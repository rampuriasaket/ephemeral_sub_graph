import unittest

from v2.stop_policy import should_stop


class StubFrontier:
    def __init__(self, empty=False, entity_backlog=0, chunk_backlog=0):
        self._empty = empty
        self._counts = {"entity": entity_backlog, "chunk": chunk_backlog}

    def is_empty(self):
        return self._empty

    def count_kind(self, kind):
        return self._counts[kind]


class StubCaps:
    def __init__(self, stop=False, reason=""):
        self._stop = stop
        self._reason = reason

    def should_stop(self, processed, backlog):
        return self._stop, self._reason


class StubBudget:
    def __init__(self, exhausted):
        self._exhausted = exhausted

    def exhausted(self):
        return self._exhausted


class TestShouldStop(unittest.TestCase):
    def test_frontier_empty_stops_first(self):
        stop, reason = should_stop(
            StubFrontier(empty=True), 0, 0, StubCaps(), StubCaps(), StubBudget(False), StubBudget(False)
        )
        self.assertTrue(stop)
        self.assertIn("frontier exhausted", reason)

    def test_entity_cap_stop(self):
        stop, reason = should_stop(
            StubFrontier(), 20, 0, StubCaps(True, "entity cap"), StubCaps(), StubBudget(False), StubBudget(False)
        )
        self.assertTrue(stop)
        self.assertEqual(reason, "entity cap")

    def test_chunk_cap_stop(self):
        stop, reason = should_stop(
            StubFrontier(), 0, 20, StubCaps(), StubCaps(True, "chunk cap"), StubBudget(False), StubBudget(False)
        )
        self.assertTrue(stop)
        self.assertEqual(reason, "chunk cap")

    def test_both_budgets_exhausted_stops(self):
        stop, reason = should_stop(
            StubFrontier(), 0, 0, StubCaps(), StubCaps(), StubBudget(True), StubBudget(True)
        )
        self.assertTrue(stop)
        self.assertIn("budgets exhausted", reason)

    def test_only_one_budget_exhausted_continues(self):
        stop, _ = should_stop(
            StubFrontier(), 0, 0, StubCaps(), StubCaps(), StubBudget(True), StubBudget(False)
        )
        self.assertFalse(stop)

    def test_nothing_trips_continues(self):
        stop, reason = should_stop(
            StubFrontier(), 0, 0, StubCaps(), StubCaps(), StubBudget(False), StubBudget(False)
        )
        self.assertFalse(stop)
        self.assertEqual(reason, "continuing")


if __name__ == "__main__":
    unittest.main()
