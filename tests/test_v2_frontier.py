import unittest

from v2.frontier import CHUNK, ENTITY, FrontierQueue


class TestFrontierQueue(unittest.TestCase):
    def test_fifo_order(self):
        q = FrontierQueue()
        q.push(ENTITY, "a", parent="(question)")
        q.push(CHUNK, "c1", parent="a")
        q.push(ENTITY, "b", parent="c1")
        self.assertEqual([q.pop().ref_id for _ in range(3)], ["a", "c1", "b"])

    def test_push_rejects_duplicate_while_queued(self):
        q = FrontierQueue()
        self.assertTrue(q.push(ENTITY, "a", parent="(question)"))
        self.assertFalse(q.push(ENTITY, "a", parent="somewhere-else"))
        self.assertEqual(len(q), 1)

    def test_push_rejects_duplicate_after_visited(self):
        q = FrontierQueue()
        q.push(ENTITY, "a", parent="(question)")
        q.pop()
        self.assertFalse(q.push(ENTITY, "a", parent="somewhere-else"))
        self.assertTrue(q.is_empty())

    def test_same_ref_id_different_kind_is_distinct(self):
        q = FrontierQueue()
        q.push(ENTITY, "x", parent="(question)")
        self.assertTrue(q.push(CHUNK, "x", parent="(question)"))
        self.assertEqual(len(q), 2)

    def test_count_kind(self):
        q = FrontierQueue()
        q.push(ENTITY, "a", parent="(question)")
        q.push(ENTITY, "b", parent="(question)")
        q.push(CHUNK, "c1", parent="(question)")
        self.assertEqual(q.count_kind(ENTITY), 2)
        self.assertEqual(q.count_kind(CHUNK), 1)

    def test_pop_records_parent(self):
        q = FrontierQueue()
        q.push(ENTITY, "a", parent="INC1042")
        item = q.pop()
        self.assertEqual(item.parent, "INC1042")


if __name__ == "__main__":
    unittest.main()
