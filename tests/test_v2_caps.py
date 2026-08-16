import unittest

from v2.caps import RunCaps


class TestRunCaps(unittest.TestCase):
    def test_no_stop_below_cap(self):
        caps = RunCaps(base_cap=20, overflow_fraction=0.25)
        stop, _ = caps.should_stop(processed_count=19, backlog_count=0)
        self.assertFalse(stop)

    def test_hard_stop_at_cap_with_no_backlog(self):
        caps = RunCaps(base_cap=20, overflow_fraction=0.25)
        stop, reason = caps.should_stop(processed_count=20, backlog_count=0)
        self.assertTrue(stop)
        self.assertIn("20/20", reason)

    def test_one_time_bump_when_backlog_exceeds_base_cap(self):
        caps = RunCaps(base_cap=20, overflow_fraction=0.25)
        stop, _ = caps.should_stop(processed_count=20, backlog_count=21)
        self.assertFalse(stop)
        self.assertTrue(caps.bumped)
        self.assertEqual(caps.effective_cap, 25)

    def test_bump_does_not_refire(self):
        caps = RunCaps(base_cap=20, overflow_fraction=0.25)
        caps.should_stop(processed_count=20, backlog_count=21)  # bump fires, cap -> 25
        stop, reason = caps.should_stop(processed_count=25, backlog_count=30)
        self.assertTrue(stop)
        self.assertIn("one-time bump used", reason)

    def test_backlog_exactly_at_base_cap_does_not_bump(self):
        caps = RunCaps(base_cap=20, overflow_fraction=0.25)
        stop, _ = caps.should_stop(processed_count=20, backlog_count=20)
        self.assertTrue(stop)  # backlog must exceed base_cap, not just equal it


if __name__ == "__main__":
    unittest.main()
