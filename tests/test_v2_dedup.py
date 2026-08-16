import unittest
from dataclasses import dataclass

from v2.dedup import ChunkDedupPolicy, DedupOutcome


@dataclass
class FakeChunkResult:
    chunk_id: str
    text: str


class FakeGraph:
    """Just enough surface for ChunkDedupPolicy: .chunks and
    .nearest_chunk_match(embedding)."""

    def __init__(self, existing_chunk_ids=(), nearest_match=(None, 0.0)):
        self.chunks = {cid: object() for cid in existing_chunk_ids}
        self._nearest_match = nearest_match

    def nearest_chunk_match(self, embedding):
        return self._nearest_match


class TestChunkDedupPolicy(unittest.TestCase):
    def test_exact_chunk_id_match_is_convergence(self):
        graph = FakeGraph(existing_chunk_ids=["servicenow:INC1042:0"])
        policy = ChunkDedupPolicy(graph, embed_fn=lambda text: [0.0])
        result = policy.classify(FakeChunkResult("servicenow:INC1042:0", "text"))
        self.assertEqual(result.outcome, DedupOutcome.EXACT_CONVERGENCE)
        self.assertEqual(result.existing_chunk_id, "servicenow:INC1042:0")

    def test_exact_match_skips_embedding_call(self):
        graph = FakeGraph(existing_chunk_ids=["a"])
        calls = []
        policy = ChunkDedupPolicy(graph, embed_fn=lambda text: calls.append(text) or [0.0])
        policy.classify(FakeChunkResult("a", "text"))
        self.assertEqual(calls, [])  # exact match short-circuits before embedding

    def test_near_dup_above_threshold(self):
        graph = FakeGraph(nearest_match=("existing-chunk", 0.95))
        policy = ChunkDedupPolicy(graph, threshold=0.90, embed_fn=lambda text: [0.0])
        result = policy.classify(FakeChunkResult("new-chunk", "text"))
        self.assertEqual(result.outcome, DedupOutcome.NEAR_DUP)
        self.assertEqual(result.existing_chunk_id, "existing-chunk")
        self.assertAlmostEqual(result.score, 0.95)

    def test_below_threshold_is_new(self):
        graph = FakeGraph(nearest_match=("existing-chunk", 0.40))
        policy = ChunkDedupPolicy(graph, threshold=0.90, embed_fn=lambda text: [0.0])
        result = policy.classify(FakeChunkResult("new-chunk", "text"))
        self.assertEqual(result.outcome, DedupOutcome.NEW)
        self.assertIsNone(result.existing_chunk_id)

    def test_no_existing_chunks_is_new(self):
        graph = FakeGraph(nearest_match=(None, 0.0))
        policy = ChunkDedupPolicy(graph, embed_fn=lambda text: [0.0])
        result = policy.classify(FakeChunkResult("first-chunk", "text"))
        self.assertEqual(result.outcome, DedupOutcome.NEW)


if __name__ == "__main__":
    unittest.main()
