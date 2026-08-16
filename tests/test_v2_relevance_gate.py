import unittest

from v2.relevance_gate import GateAcceptance, GateCandidate, RelevanceGate


class TestRelevanceGate(unittest.TestCase):
    def test_empty_candidates_short_circuits_without_calling_llm(self):
        calls = []
        gate = RelevanceGate(call_fn=lambda *a: calls.append(a) or {})
        result = gate.evaluate("question?", "[QUESTION] -> chunk:c0", "parent text", [])
        self.assertEqual(result, {})
        self.assertEqual(calls, [])

    def test_returns_accepted_ids_with_reasons_from_call_fn(self):
        gate = RelevanceGate(
            call_fn=lambda q, p, t, c: {"chunk-a": GateAcceptance("shares INC1042 with the path", "high")}
        )
        candidates = [GateCandidate("chunk-a", "text a"), GateCandidate("chunk-b", "text b")]
        result = gate.evaluate("question?", "[QUESTION] -> chunk:c0", "parent text", candidates)
        self.assertEqual(result, {"chunk-a": GateAcceptance("shares INC1042 with the path", "high")})

    def test_ignores_ids_not_in_candidate_set(self):
        gate = RelevanceGate(
            call_fn=lambda q, p, t, c: {
                "chunk-a": GateAcceptance("real reason", "medium"),
                "hallucinated-id": GateAcceptance("fake reason", "low"),
            }
        )
        candidates = [GateCandidate("chunk-a", "text a")]
        result = gate.evaluate("question?", "[QUESTION] -> chunk:c0", "parent text", candidates)
        self.assertEqual(result, {"chunk-a": GateAcceptance("real reason", "medium")})

    def test_passes_question_path_and_parent_text_through(self):
        seen = {}

        def fake_call(question, path_summary, parent_text, candidates):
            seen["question"] = question
            seen["path_summary"] = path_summary
            seen["parent_text"] = parent_text
            return {}

        gate = RelevanceGate(call_fn=fake_call)
        gate.evaluate(
            "what broke?",
            "[QUESTION] -> entity:auth-service (Component) -> chunk:c1",
            "the parent chunk body",
            [GateCandidate("c1", "t")],
        )
        self.assertEqual(seen["question"], "what broke?")
        self.assertEqual(seen["path_summary"], "[QUESTION] -> entity:auth-service (Component) -> chunk:c1")
        self.assertEqual(seen["parent_text"], "the parent chunk body")

    def test_overlap_note_defaults_empty(self):
        candidate = GateCandidate("c1", "text")
        self.assertEqual(candidate.overlap_note, "")


if __name__ == "__main__":
    unittest.main()
