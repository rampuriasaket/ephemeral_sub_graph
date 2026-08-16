import unittest

from v2.acceptance import (
    ENTITY_MATCH_METADATA,
    ENTITY_MATCH_NONE,
    ENTITY_MATCH_TEXT,
    entity_pop_accepts,
    shared_path_entities,
)


class TestEntityPopAccepts(unittest.TestCase):
    def test_accepts_exact_substring(self):
        self.assertEqual(entity_pop_accepts("This mentions INC1042 directly.", {"INC1042"}), ENTITY_MATCH_TEXT)

    def test_accepts_case_insensitive(self):
        self.assertEqual(entity_pop_accepts("the Auth-Service is down", {"auth-service"}), ENTITY_MATCH_TEXT)

    def test_accepts_via_alias(self):
        self.assertEqual(
            entity_pop_accepts("RecEngine had a memory leak", {"recommendation-engine", "RecEngine"}), ENTITY_MATCH_TEXT
        )

    def test_rejects_no_match(self):
        self.assertEqual(entity_pop_accepts("unrelated content about billing", {"auth-service"}), ENTITY_MATCH_NONE)

    def test_empty_aliases_rejects(self):
        self.assertEqual(entity_pop_accepts("any text", set()), ENTITY_MATCH_NONE)

    def test_ignores_blank_alias_entries(self):
        self.assertEqual(entity_pop_accepts("any text", {""}), ENTITY_MATCH_NONE)

    def test_metadata_only_match_returns_metadata_not_text(self):
        # the Slack-thread gap: RELATED field is excluded from embedded
        # text, so the ID only shows up in explicit_related_ids metadata --
        # this must be distinguishable from a text match, not conflated
        # with it (see acceptance.py's docstring for why).
        self.assertEqual(
            entity_pop_accepts(
                "finance pinged about orders with way bigger discounts", {"INC1201"}, ["INC1201", "PROJ-401"]
            ),
            ENTITY_MATCH_METADATA,
        )

    def test_related_ids_none_or_missing_id_still_rejects(self):
        self.assertEqual(entity_pop_accepts("unrelated text", {"INC1201"}, None), ENTITY_MATCH_NONE)
        self.assertEqual(entity_pop_accepts("unrelated text", {"INC1201"}, ["PROJ-999"]), ENTITY_MATCH_NONE)

    def test_text_match_wins_over_metadata_when_both_present(self):
        self.assertEqual(entity_pop_accepts("mentions INC1042 directly", {"INC1042"}, ["INC1042"]), ENTITY_MATCH_TEXT)


class TestSharedPathEntities(unittest.TestCase):
    def _no_aliases(self, entity_id):
        return set()

    def test_finds_direct_mentions(self):
        shared = shared_path_entities(
            "the resize worker in image-processing-service failed",
            ["image-processing-service", "webhook-dispatcher-service"],
            self._no_aliases,
        )
        self.assertEqual(shared, ["image-processing-service"])

    def test_finds_via_alias(self):
        shared = shared_path_entities(
            "RecEngine crashed under load",
            ["recommendation-engine"],
            lambda eid: {"RecEngine"} if eid == "recommendation-engine" else set(),
        )
        self.assertEqual(shared, ["recommendation-engine"])

    def test_no_overlap_returns_empty(self):
        shared = shared_path_entities(
            "webhook-dispatcher-service needs backpressure handling",
            ["image-processing-service", "resize worker"],
            self._no_aliases,
        )
        self.assertEqual(shared, [])

    def test_empty_path_entities_returns_empty(self):
        shared = shared_path_entities("any text", [], self._no_aliases)
        self.assertEqual(shared, [])

    def test_preserves_path_entity_order(self):
        shared = shared_path_entities(
            "mentions both b and a here",
            ["a", "b"],
            self._no_aliases,
        )
        self.assertEqual(shared, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
