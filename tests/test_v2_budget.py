import unittest

from v2.budget import CallBudget


class TestCallBudget(unittest.TestCase):
    def test_can_call_within_budget(self):
        b = CallBudget(2, ["servicenow", "jira"])
        self.assertTrue(b.can_call("servicenow"))

    def test_record_call_increments_and_blocks_at_limit(self):
        b = CallBudget(1, ["servicenow"])
        self.assertTrue(b.can_call("servicenow"))
        b.record_call("servicenow")
        self.assertFalse(b.can_call("servicenow"))
        self.assertEqual(b.calls_made("servicenow"), 1)

    def test_systems_tracked_independently(self):
        b = CallBudget(1, ["servicenow", "jira"])
        b.record_call("servicenow")
        self.assertFalse(b.can_call("servicenow"))
        self.assertTrue(b.can_call("jira"))

    def test_exhausted_requires_every_system_out(self):
        b = CallBudget(1, ["servicenow", "jira"])
        b.record_call("servicenow")
        self.assertFalse(b.exhausted())
        b.record_call("jira")
        self.assertTrue(b.exhausted())

    def test_unknown_system_defaults_to_zero_calls(self):
        b = CallBudget(1, ["servicenow"])
        self.assertEqual(b.calls_made("gitrepo"), 0)


if __name__ == "__main__":
    unittest.main()
