import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from v2.run_log import RunLog


@dataclass
class FakeCost:
    llm_calls: int
    retrieval_calls: int
    input_tokens: int
    output_tokens: int
    wall_clock_seconds: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class TestRunLog(unittest.TestCase):
    def test_header_includes_question(self):
        log = RunLog(question="why did it break?")
        self.assertIn("why did it break?", log.render())

    def test_seed_entity_and_chunk_lines(self):
        log = RunLog(question="q")
        log.seed_entity("auth-service", "Component")
        log.seed_chunk("servicenow", "INC1042", 3)
        text = log.render()
        self.assertIn("auth-service", text)
        self.assertIn("Component", text)
        self.assertIn("servicenow:INC1042", text)
        self.assertIn("3 entities extracted", text)

    def test_turn_lifecycle(self):
        log = RunLog(question="q")
        log.start_turn(1, "entity", "auth-service", "(question)", frontier_remaining=4)
        log.search_results(2)
        log.reject("jira", "PROJ-999", "does not contain the searched entity")
        log.accept("servicenow", "INC1042", "contains searched entity 'auth-service'", ["Priya Nair"])
        log.end_turn()
        text = log.render()
        self.assertIn("Turn 1: pop entity 'auth-service'", text)
        self.assertIn("frontier had 4 other item(s) waiting", text)
        self.assertIn("returned 2 candidate(s)", text)
        self.assertIn("x  rejected jira:PROJ-999", text)
        self.assertIn("+  accepted servicenow:INC1042", text)
        self.assertIn("new entities queued: Priya Nair", text)

    def test_merge_and_gate_batch_lines(self):
        log = RunLog(question="q")
        log.merge("jira", "PROJ-201", "servicenow:INC1042:0", "near_dup")
        log.gate_batch(n_survivors=3, n_accepted=1)
        text = log.render()
        self.assertIn("merged into existing servicenow:INC1042:0 (near_dup", text)
        self.assertIn("3 non-duplicate candidate(s): 1 accepted, 2 rejected", text)

    def test_final_includes_stop_reason_graph_cost_and_report(self):
        log = RunLog(question="q")
        snapshot = {
            "entities": {"a": {}, "b": {}},
            "chunks": {
                "c1": {"source_system": "servicenow"},
                "c2": {"source_system": "jira"},
            },
            "mentions_edges": [("c1", "a")],
            "relation_edges": [],
            "chunk_links": [],
        }
        cost = FakeCost(llm_calls=5, retrieval_calls=10, input_tokens=100, output_tokens=20, wall_clock_seconds=12.3)
        log.final("frontier exhausted", snapshot, cost, "The answer is X.")
        text = log.render()
        self.assertIn("Stop reason: frontier exhausted", text)
        self.assertIn("2 chunks, 2 entities", text)
        self.assertIn("jira, servicenow", text)
        self.assertIn("5 LLM calls", text)
        self.assertIn("120 tokens", text)
        self.assertIn("The answer is X.", text)

    def test_final_handles_missing_cost(self):
        log = RunLog(question="q")
        snapshot = {"entities": {}, "chunks": {}, "mentions_edges": [], "relation_edges": [], "chunk_links": []}
        log.final("frontier exhausted", snapshot, None, "no info found")
        # should not raise, cost line simply omitted
        self.assertIn("no info found", log.render())

    def test_write_creates_file_and_parent_dirs(self):
        log = RunLog(question="q")
        log.final("frontier exhausted", {"entities": {}, "chunks": {}, "mentions_edges": [], "relation_edges": []}, None, "done")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "run.log"
            written = log.write(path)
            self.assertTrue(written.exists())
            self.assertIn("done", written.read_text())


if __name__ == "__main__":
    unittest.main()
