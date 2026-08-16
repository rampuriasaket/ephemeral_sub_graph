import tempfile
import unittest
from pathlib import Path

import run_history


class TestIsDeclining(unittest.TestCase):
    def test_too_few_points_not_flagged(self):
        self.assertFalse(run_history._is_declining([1.0, 0.5]))

    def test_clean_decline_flagged(self):
        self.assertTrue(run_history._is_declining([1.0, 0.8, 0.6, 0.4]))

    def test_one_noise_blip_tolerated(self):
        self.assertTrue(run_history._is_declining([1.0, 0.6, 0.7, 0.4]))

    def test_two_blips_not_flagged(self):
        self.assertFalse(run_history._is_declining([1.0, 0.6, 0.9, 0.5, 0.8]))

    def test_flat_not_flagged(self):
        self.assertFalse(run_history._is_declining([0.8, 0.8, 0.8, 0.8]))

    def test_improving_not_flagged(self):
        self.assertFalse(run_history._is_declining([0.5, 0.6, 0.8, 1.0]))

    def test_last_equal_to_first_not_flagged(self):
        # dips in the middle but recovers back to the start -- not a trend
        self.assertFalse(run_history._is_declining([0.8, 0.4, 0.8]))


class TestRecordAndCheckTrend(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.history_path = Path(self.tmpdir.name) / "history.json"

    def tearDown(self):
        self.tmpdir.cleanup()

    def _record_sequence(self, question, system, recalls, precisions=None):
        precisions = precisions or [1.0] * len(recalls)
        for r, p in zip(recalls, precisions):
            run_history.record(question, system, r, p, cost_usd=0.01, history_path=self.history_path)

    def test_not_enough_history_not_flagged(self):
        self._record_sequence("q1", "esg_v2", [1.0, 0.8])
        result = run_history.check_trend("q1", "esg_v2", history_path=self.history_path)
        self.assertFalse(result["flagged"])
        self.assertEqual(result["reason"], "not enough history yet")

    def test_declining_recall_flagged(self):
        self._record_sequence("q1", "esg_v2", [1.0, 0.8, 0.6, 0.4])
        result = run_history.check_trend("q1", "esg_v2", history_path=self.history_path)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["metric"], "recall")
        self.assertEqual(result["values"], [1.0, 0.8, 0.6, 0.4])

    def test_stable_recall_not_flagged(self):
        self._record_sequence("q1", "esg_v2", [1.0, 1.0, 1.0, 1.0])
        result = run_history.check_trend("q1", "esg_v2", history_path=self.history_path)
        self.assertFalse(result["flagged"])

    def test_declining_precision_flagged_when_recall_stable(self):
        self._record_sequence("q1", "esg_v2", [1.0, 1.0, 1.0, 1.0], precisions=[1.0, 0.8, 0.6, 0.4])
        result = run_history.check_trend("q1", "esg_v2", history_path=self.history_path)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["metric"], "precision")

    def test_recall_decline_takes_priority_over_precision(self):
        self._record_sequence("q1", "esg_v2", [1.0, 0.8, 0.6, 0.4], precisions=[1.0, 0.8, 0.6, 0.4])
        result = run_history.check_trend("q1", "esg_v2", history_path=self.history_path)
        self.assertEqual(result["metric"], "recall")

    def test_window_limits_to_recent_runs(self):
        # 6 runs recorded, oldest shows a big drop, but window=5 should
        # only look at the most recent 5, which are stable.
        self._record_sequence("q1", "esg_v2", [1.0, 0.2, 0.9, 0.9, 0.9, 0.9])
        result = run_history.check_trend("q1", "esg_v2", window=5, history_path=self.history_path)
        self.assertFalse(result["flagged"])

    def test_different_questions_tracked_independently(self):
        self._record_sequence("q1", "esg_v2", [1.0, 0.8, 0.6, 0.4])
        self._record_sequence("q2", "esg_v2", [1.0, 1.0, 1.0, 1.0])
        self.assertTrue(run_history.check_trend("q1", "esg_v2", history_path=self.history_path)["flagged"])
        self.assertFalse(run_history.check_trend("q2", "esg_v2", history_path=self.history_path)["flagged"])

    def test_different_systems_tracked_independently(self):
        self._record_sequence("q1", "esg_v2", [1.0, 0.8, 0.6, 0.4])
        self._record_sequence("q1", "flat_rag", [1.0, 1.0, 1.0, 1.0])
        self.assertTrue(run_history.check_trend("q1", "esg_v2", history_path=self.history_path)["flagged"])
        self.assertFalse(run_history.check_trend("q1", "flat_rag", history_path=self.history_path)["flagged"])

    def test_history_persists_across_separate_load_calls(self):
        run_history.record("q1", "esg_v2", 1.0, 1.0, 0.01, history_path=self.history_path)
        run_history.record("q1", "esg_v2", 0.5, 1.0, 0.01, history_path=self.history_path)
        history = run_history._load(self.history_path)
        self.assertEqual(len(history["q1::esg_v2"]), 2)


if __name__ == "__main__":
    unittest.main()
