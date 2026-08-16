"""Mechanical (no-LLM) entity-text matching, used in two places:

1. entity-pop's acceptance test (esg_algorithm_v2.md section 4): a
   candidate is accepted only if it actually contains the entity that was
   searched for -- containing the searched entity is already a stronger
   signal than the chunk-pop relevance gate exists to provide.

2. chunk-pop's path-overlap hint (v2/relevance_gate.py): before the LLM
   relevance gate judges a chunk-pop candidate, we mechanically check which
   already-known path entities the candidate's own text mentions, and hand
   that to the gate as a labeled fact instead of asking it to eyeball
   vocabulary similarity alone. Zero overlap doesn't force a reject (a
   candidate can still earn acceptance on a genuine textual case -- see
   esg_algorithm_v2.md's "wanted to buy a home" / "mortgage rates" example)
   but it's a strong, checkable signal the gate is told to weigh.
"""


ENTITY_MATCH_TEXT = "text"
ENTITY_MATCH_METADATA = "metadata"
ENTITY_MATCH_NONE = "none"


def entity_pop_accepts(chunk_text: str, entity_aliases: set[str], related_ids: list[str] | None = None) -> str:
    """Returns ENTITY_MATCH_TEXT, ENTITY_MATCH_METADATA, or ENTITY_MATCH_NONE
    -- these are NOT equally strong signals, so the caller must not treat
    them the same way. A literal mention in the chunk's own text is the
    strongest possible signal (auto-accept). A metadata-only match (the ID
    only appears in `related_ids` -- the candidate's own explicit_related_ids,
    i.e. IDs it cites via a structured header field like RELATED WORK/LINKED
    TICKET, excluded from embedded text by design, see vector_stores.py's
    search_exact) is real but weaker: confirmed 2026-08 that these header
    citations are dense enough across the corpus that auto-accepting them
    the same way as text matches causes runaway cascading acceptance into
    genuinely unrelated documents (see results/regression_full_8.md and the
    chat that found it) -- metadata-only matches should go through the
    relevance gate for confirmation, not skip it. related_ids only ever
    contains ID-shaped tokens (see ingest.py's ID_PATTERN), so this check is
    a no-op for non-ID entity types (Component/Person/Team)."""
    lowered = chunk_text.lower()
    if any(alias.lower() in lowered for alias in entity_aliases if alias):
        return ENTITY_MATCH_TEXT
    if related_ids and any(alias in related_ids for alias in entity_aliases if alias):
        return ENTITY_MATCH_METADATA
    return ENTITY_MATCH_NONE


def shared_path_entities(chunk_text: str, path_entity_ids: list[str], alias_lookup) -> list[str]:
    """Which of `path_entity_ids` does `chunk_text` mention (by canonical id
    or any known alias)? `alias_lookup(entity_id) -> set[str]` is injected
    so this stays decoupled from EntityResolver for testing."""
    lowered = chunk_text.lower()
    shared = []
    for entity_id in path_entity_ids:
        aliases = alias_lookup(entity_id) | {entity_id}
        if any(alias.lower() in lowered for alias in aliases if alias):
            shared.append(entity_id)
    return shared
