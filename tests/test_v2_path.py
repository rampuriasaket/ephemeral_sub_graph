import unittest

from graph import ChunkNode, EntityNode
from v2.path import CHUNK, ENTITY, QUESTION, QUESTION_PARENT_LABEL, build_path, format_path, path_entity_ids


class FakeGraph:
    def __init__(self):
        self.chunks = {}
        self.entities = {}


def _chunk(id_, discovered_via, source_system="servicenow", doc_id="INC1"):
    return ChunkNode(
        id=id_,
        source_system=source_system,
        doc_id=doc_id,
        text="text",
        first_seen_turn=0,
        discovered_via=list(discovered_via),
    )


def _entity(id_, parent, type_="Component"):
    return EntityNode(id=id_, type=type_, first_seen_turn=0, parent=parent)


class TestBuildPath(unittest.TestCase):
    def test_direct_seed_chunk(self):
        graph = FakeGraph()
        graph.chunks["c1"] = _chunk("c1", [QUESTION_PARENT_LABEL])
        chain = build_path(graph, CHUNK, "c1")
        self.assertEqual([(n.kind, n.ref_id) for n in chain], [(QUESTION, QUESTION_PARENT_LABEL), (CHUNK, "c1")])

    def test_multi_hop_chain(self):
        graph = FakeGraph()
        graph.entities["image uploads"] = _entity("image uploads", QUESTION_PARENT_LABEL)
        graph.chunks["c1"] = _chunk("c1", [QUESTION_PARENT_LABEL])
        graph.entities["image-processing-service"] = _entity("image-processing-service", "c1")
        graph.chunks["c2"] = _chunk("c2", ["image-processing-service"])

        chain = build_path(graph, CHUNK, "c2")
        self.assertEqual(
            [(n.kind, n.ref_id) for n in chain],
            [
                (QUESTION, QUESTION_PARENT_LABEL),
                (CHUNK, "c1"),
                (ENTITY, "image-processing-service"),
                (CHUNK, "c2"),
            ],
        )

    def test_entity_start_point(self):
        graph = FakeGraph()
        graph.chunks["c1"] = _chunk("c1", [QUESTION_PARENT_LABEL])
        graph.entities["auth-service"] = _entity("auth-service", "c1")
        chain = build_path(graph, ENTITY, "auth-service")
        self.assertEqual(chain[-1].ref_id, "auth-service")
        self.assertEqual(chain[0].kind, QUESTION)

    def test_missing_parent_stops_gracefully(self):
        graph = FakeGraph()
        graph.chunks["orphan"] = _chunk("orphan", [])  # discovered_via empty -- shouldn't happen, but shouldn't crash
        chain = build_path(graph, CHUNK, "orphan")
        self.assertEqual([(n.kind, n.ref_id) for n in chain], [(QUESTION, QUESTION_PARENT_LABEL), (CHUNK, "orphan")])

    def test_cycle_is_bounded_by_max_hops(self):
        graph = FakeGraph()
        graph.chunks["a"] = _chunk("a", ["b"])
        graph.chunks["b"] = _chunk("b", ["a"])  # pathological cycle, shouldn't happen in practice
        chain = build_path(graph, CHUNK, "a", max_hops=5)
        self.assertLessEqual(len(chain), 7)  # doesn't spin forever


class TestFormatPath(unittest.TestCase):
    def test_format_includes_kinds_and_metadata(self):
        graph = FakeGraph()
        graph.entities["image-processing-service"] = _entity("image-processing-service", QUESTION_PARENT_LABEL)
        graph.chunks["c2"] = _chunk("c2", ["image-processing-service"], source_system="gitrepo", doc_id="PR-545")
        chain = build_path(graph, CHUNK, "c2")
        text = format_path(graph, chain)
        self.assertIn("[QUESTION]", text)
        self.assertIn("entity:image-processing-service (Component)", text)
        self.assertIn("chunk:c2 [gitrepo:PR-545]", text)


class TestPathEntityIds(unittest.TestCase):
    def test_extracts_only_entity_nodes_in_order(self):
        graph = FakeGraph()
        graph.entities["image uploads"] = _entity("image uploads", QUESTION_PARENT_LABEL)
        graph.chunks["c1"] = _chunk("c1", [QUESTION_PARENT_LABEL])
        graph.entities["image-processing-service"] = _entity("image-processing-service", "c1")
        graph.chunks["c2"] = _chunk("c2", ["image-processing-service"])

        chain = build_path(graph, CHUNK, "c2")
        self.assertEqual(path_entity_ids(chain), ["image-processing-service"])

    def test_no_entities_in_path_returns_empty(self):
        graph = FakeGraph()
        graph.chunks["c1"] = _chunk("c1", [QUESTION_PARENT_LABEL])
        chain = build_path(graph, CHUNK, "c1")
        self.assertEqual(path_entity_ids(chain), [])


if __name__ == "__main__":
    unittest.main()
