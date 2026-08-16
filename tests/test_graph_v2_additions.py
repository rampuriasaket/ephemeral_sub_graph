import unittest

from graph import Graph
from vector_stores import ChunkResult


def _chunk(chunk_id, text, source_system="servicenow", doc_id="INC1042"):
    return ChunkResult(chunk_id=chunk_id, text=text, source_system=source_system, doc_id=doc_id, metadata={})


class TestGraphV2Additions(unittest.TestCase):
    """Additive-only: confirms the v2 helpers behave as intended, and that
    v1's upsert_chunk (refactored to call nearest_chunk_match internally)
    keeps its original dedup behavior."""

    def test_add_chunk_node_sets_discovered_via(self):
        graph = Graph()
        node = graph.add_chunk_node(_chunk("c1", "some incident text about auth-service"), turn=1, parent_label="auth-service")
        self.assertEqual(node.discovered_via, ["auth-service"])
        self.assertIn("c1", graph.chunks)

    def test_note_discovered_via_appends_once(self):
        graph = Graph()
        node = graph.add_chunk_node(_chunk("c1", "text"), turn=1, parent_label="auth-service")
        self.assertTrue(graph.note_discovered_via("c1", "INC1042"))
        self.assertFalse(graph.note_discovered_via("c1", "INC1042"))  # no duplicate
        self.assertEqual(node.discovered_via, ["auth-service", "INC1042"])

    def test_add_chunk_link_rejects_self_link_and_duplicates(self):
        graph = Graph()
        self.assertTrue(graph.add_chunk_link("c1", "c2"))
        self.assertFalse(graph.add_chunk_link("c1", "c2"))
        self.assertFalse(graph.add_chunk_link("c1", "c1"))

    def test_nearest_chunk_match_empty_graph(self):
        graph = Graph()
        best_id, best_score = graph.nearest_chunk_match([0.1, 0.2, 0.3])
        self.assertIsNone(best_id)
        self.assertEqual(best_score, 0.0)

    def test_nearest_chunk_match_finds_near_duplicate(self):
        graph = Graph()
        graph.add_chunk_node(_chunk("c1", "the auth-service returned 500 errors under load"), turn=1, parent_label="p")
        from embeddings import embed

        near_dup_embedding = embed("the auth-service returned 500 errors under load")
        best_id, best_score = graph.nearest_chunk_match(near_dup_embedding)
        self.assertEqual(best_id, "c1")
        self.assertGreater(best_score, 0.99)

    def test_upsert_chunk_still_dedups_v1_behavior(self):
        graph = Graph()
        node1, is_new1 = graph.upsert_chunk(_chunk("c1", "the auth-service returned 500 errors under load"), turn=1)
        self.assertTrue(is_new1)
        node2, is_new2 = graph.upsert_chunk(
            _chunk("c2", "the auth-service returned 500 errors under load", doc_id="INC1099"), turn=2
        )
        self.assertFalse(is_new2)
        self.assertIs(node1, node2)
        self.assertIn("servicenow:INC1099", node1.merged_refs)
        self.assertEqual(node1.discovered_via, [])  # v1 path never touches discovered_via

    def test_snapshot_includes_chunk_links(self):
        graph = Graph()
        graph.add_chunk_node(_chunk("c1", "text one"), turn=1, parent_label="p")
        graph.add_chunk_node(_chunk("c2", "text two"), turn=1, parent_label="c1")
        graph.add_chunk_link("c1", "c2")
        snapshot = graph.snapshot()
        self.assertIn("chunk_links", snapshot)
        self.assertEqual(snapshot["chunk_links"], [("c1", "c2")])


if __name__ == "__main__":
    unittest.main()
