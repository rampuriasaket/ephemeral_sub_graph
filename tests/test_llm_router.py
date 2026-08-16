import unittest

import cost_tracker
import llm_router


class TestToGeminiSchema(unittest.TestCase):
    def test_simple_string_field(self):
        schema = llm_router._to_gemini_schema({"type": "string", "description": "a name"})
        self.assertEqual(schema.type, "STRING")
        self.assertEqual(schema.description, "a name")

    def test_object_with_properties_and_required(self):
        schema = llm_router._to_gemini_schema(
            {
                "type": "object",
                "properties": {"mention": {"type": "string"}, "type": {"type": "string", "enum": ["A", "B"]}},
                "required": ["mention", "type"],
            }
        )
        self.assertEqual(schema.type, "OBJECT")
        self.assertEqual(set(schema.properties.keys()), {"mention", "type"})
        self.assertEqual(schema.properties["type"].enum, ["A", "B"])
        self.assertEqual(schema.required, ["mention", "type"])

    def test_array_with_items(self):
        schema = llm_router._to_gemini_schema({"type": "array", "items": {"type": "string"}})
        self.assertEqual(schema.type, "ARRAY")
        self.assertEqual(schema.items.type, "STRING")

    def test_union_type_with_null_becomes_nullable(self):
        # entity_resolution.py's matched_canonical_id: ["string", "null"]
        schema = llm_router._to_gemini_schema({"type": ["string", "null"], "description": "x"})
        self.assertEqual(schema.type, "STRING")
        self.assertTrue(schema.nullable)

    def test_nested_object_in_array(self):
        # the exact shape of relevance_gate.py's _GATE_TOOL "accepted" field
        schema = llm_router._to_gemini_schema(
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"chunk_id": {"type": "string"}, "reason": {"type": "string"}},
                    "required": ["chunk_id", "reason"],
                },
            }
        )
        self.assertEqual(schema.type, "ARRAY")
        self.assertEqual(schema.items.type, "OBJECT")
        self.assertEqual(set(schema.items.properties.keys()), {"chunk_id", "reason"})


class TestCost(unittest.TestCase):
    def test_known_model_computes_correctly(self):
        cost = llm_router._cost("claude-haiku-4-5-20251001", input_tokens=1_000_000, output_tokens=1_000_000)
        self.assertAlmostEqual(cost, 1.00 + 5.00)

    def test_unknown_model_returns_zero_not_error(self):
        self.assertEqual(llm_router._cost("some-future-model", 1000, 1000), 0.0)


class FakeUsage:
    def __init__(self, candidates=0, thoughts=None):
        self.candidates_token_count = candidates
        self.thoughts_token_count = thoughts


class TestGeminiOutputTokens(unittest.TestCase):
    def test_no_thinking_tokens(self):
        self.assertEqual(llm_router._gemini_output_tokens(FakeUsage(candidates=5, thoughts=None)), 5)

    def test_sums_thinking_tokens_when_present(self):
        # exactly the bug found this session: a thinking model reports
        # thoughts_token_count separately from candidates_token_count, and
        # both are billed as output.
        self.assertEqual(llm_router._gemini_output_tokens(FakeUsage(candidates=2, thoughts=68)), 70)


class TestWalkChain(unittest.TestCase):
    def setUp(self):
        cost_tracker.start_tracking()

    def tearDown(self):
        cost_tracker.stop_tracking()

    def test_primary_success_no_fallback(self):
        calls = []

        def attempt(provider, model):
            calls.append((provider, model))
            return {"ok": True}, 10, 5

        chain = [("anthropic", "model-a"), ("google", "model-b")]
        result = llm_router._walk_chain(chain, "test_task", attempt, empty_result={})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(calls, [("anthropic", "model-a")])  # never tried the second

    def test_falls_back_to_second_model_on_failure(self):
        attempted = []

        def attempt(provider, model):
            attempted.append(model)
            if model == "model-a":
                raise RuntimeError("simulated outage")
            return {"ok": True}, 10, 5

        chain = [("anthropic", "model-a"), ("google", "model-b")]
        result = llm_router._walk_chain(chain, "test_task", attempt, empty_result={})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(attempted, ["model-a", "model-b"])

    def test_all_models_fail_returns_empty_result(self):
        def attempt(provider, model):
            raise RuntimeError("simulated outage")

        chain = [("anthropic", "model-a"), ("google", "model-b")]
        result = llm_router._walk_chain(chain, "test_task", attempt, empty_result="fallback-value")

        self.assertEqual(result, "fallback-value")

    def test_records_cost_and_fallback_flag(self):
        def attempt(provider, model):
            if model == "model-a":
                raise RuntimeError("down")
            return {}, 1_000_000, 1_000_000  # 1M in, 1M out -- easy to check cost math

        # use a real priced model so _cost() inside _walk_chain resolves to something non-zero
        chain = [("anthropic", "model-a"), ("anthropic", "claude-haiku-4-5-20251001")]
        llm_router._walk_chain(chain, "test_task", attempt, empty_result={})

        metrics = cost_tracker._current
        self.assertEqual(metrics.llm_calls, 1)
        self.assertEqual(metrics.fallback_count, 1)  # succeeded on the 2nd model in the chain
        self.assertAlmostEqual(metrics.cost_usd, 1.00 + 5.00)  # haiku pricing


if __name__ == "__main__":
    unittest.main()
