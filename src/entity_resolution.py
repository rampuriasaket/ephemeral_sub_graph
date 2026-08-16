"""Maintains a growing canonical entity registry for one discovery run.

Ticket/PR IDs resolve via exact/near-exact string match -- they're already
unique tokens, no need for fuzzy matching there.

Everything else (components, people, teams) is resolved by asking the LLM
whether a new mention refers to the same real-world entity as something
already in the registry. A diagnostic run against the seeded alias-stress
test cases showed the originally spec'd hybrid
`0.6*jaro_winkler + 0.4*cosine` formula could not separate "should merge"
aliases (e.g. "RecEngine" / "recommendation-engine", hybrid ~0.64) from
"should NOT merge" near-misses (e.g. "billing-service" / "billing-service-v2",
hybrid ~0.92) at any single threshold -- the score ranges interleave. See the
Addendum in build_phase_1.md. An LLM judgment, given the mention's source
context and the entity's known aliases, handles both directions far more
reliably than string/embedding similarity on short, decontextualized tokens.
"""

import re

import llm_router
from entity_extraction import RawEntity

_ID_PATTERN = re.compile(r"^(INC\d+|PROJ-\d+|PR-\d+)$", re.IGNORECASE)


def _looks_like_id(mention: str) -> bool:
    return bool(_ID_PATTERN.match(mention.strip()))


_RESOLVE_TOOL = {
    "name": "resolve_entity",
    "description": "Decide whether a newly mentioned entity is the same real-world thing as one already known.",
    "input_schema": {
        "type": "object",
        "properties": {
            "matches_existing": {
                "type": "boolean",
                "description": "True if the new mention refers to the same real-world entity as one of the existing canonical entities listed.",
            },
            "matched_canonical_id": {
                "type": ["string", "null"],
                "description": "The exact canonical_id string (copied verbatim) from the existing list that this mention matches, if matches_existing is true. Null otherwise.",
            },
        },
        "required": ["matches_existing", "matched_canonical_id"],
    },
}

_SYSTEM_PROMPT = """You maintain a canonical entity registry for a knowledge \
graph built from engineering systems (incidents, tickets, pull requests, \
wiki pages). Given a newly mentioned entity (with the text it appeared in, \
for context) and a list of already-known canonical entities (with their type \
and any aliases already recorded for them), decide whether the new mention \
refers to the SAME real-world component, service, person, or team as one of \
the existing entities.

Treat mentions as the SAME entity if they are an abbreviation, nickname, \
alias, initials, or a differently-cased/hyphenated/spaced form of the same \
thing -- e.g. "RecEngine" and "recommendation-engine"; "F. Al-Sayed" and \
"Fatima Al-Sayed"; "the authentication service" and "auth-service".

Treat mentions as DIFFERENT entities if they are related but distinct -- e.g. \
a service and a specifically-named client/wrapper library for it \
("inventory-service" vs "inventory-service-client"), two versions of a \
service meant to coexist during a migration ("billing-service" vs \
"billing-service-v2"), or two components that merely share a naming prefix \
("notification-worker" vs "notification-queue-config").

Before merging, also check: is the NEW mention actually a specific, \
uniquely-identifying name on its own -- or a generic/common word describing \
a broader feature area, workflow, or concept (e.g. "checkout", "search", \
"billing", "login", "notifications")? A generic descriptor is essentially \
never the same entity as a specific named component/service/incident that \
relates to it, even when the specific one's name contains the generic word \
(e.g. "checkout" is not "checkout-service" or "checkout screen"). This \
applies regardless of domain or which system the mention came from -- the \
test is about specificity, not any particular word list. Only merge when \
BOTH mentions are functioning as specific, identifying names for the same \
real-world thing.

When genuinely unsure, prefer treating them as different rather than \
merging unrelated entities together.

If there are no existing entities of a plausibly compatible type, or none \
plausibly match, return matches_existing=false."""


def _format_existing(entities: list[tuple[str, str, set[str]]]) -> str:
    if not entities:
        return "(none yet)"
    lines = []
    for canonical_id, type_guess, aliases in entities:
        alias_note = f", also known as: {', '.join(sorted(aliases))}" if aliases else ""
        lines.append(f"- {canonical_id} (type: {type_guess}{alias_note})")
    return "\n".join(lines)


class EntityResolver:
    """One instance per discovery run -- in-memory only, thrown away with the graph."""

    def __init__(self):
        self._canonical_types: dict[str, str] = {}
        self._aliases: dict[str, set[str]] = {}
        self._mention_cache: dict[str, tuple[str, str]] = {}

    def resolve(self, raw_entity: RawEntity, context_text: str = "") -> tuple[str, str, bool]:
        """Resolve a RawEntity to a canonical entity. Returns (canonical_id, type, is_new)."""
        mention = raw_entity.mention.strip()
        cache_key = mention.lower()

        if _looks_like_id(mention):
            normalized = mention.upper()
            if normalized in self._canonical_types:
                return normalized, self._canonical_types[normalized], False
            self._register_new(normalized, raw_entity.type_guess)
            return normalized, raw_entity.type_guess, True

        if cache_key in self._mention_cache:
            canonical_id, type_guess = self._mention_cache[cache_key]
            return canonical_id, type_guess, False

        existing = [
            (cid, t, self._aliases.get(cid, set()))
            for cid, t in self._canonical_types.items()
            if not _looks_like_id(cid)
        ]

        matched_id = self._llm_resolve(mention, raw_entity.type_guess, context_text, existing) if existing else None

        if matched_id is not None:
            self._aliases.setdefault(matched_id, set()).add(mention)
            type_guess = self._canonical_types[matched_id]
            self._mention_cache[cache_key] = (matched_id, type_guess)
            return matched_id, type_guess, False

        self._register_new(mention, raw_entity.type_guess)
        return mention, raw_entity.type_guess, True

    def _register_new(self, canonical_id: str, type_guess: str) -> None:
        self._canonical_types[canonical_id] = type_guess
        self._aliases.setdefault(canonical_id, set())
        self._mention_cache[canonical_id.lower()] = (canonical_id, type_guess)

    def _find_canonical(self, candidate: str) -> str | None:
        if candidate in self._canonical_types:
            return candidate
        for cid in self._canonical_types:
            if cid.lower() == candidate.lower():
                return cid
        return None

    def _llm_resolve(
        self,
        mention: str,
        type_guess: str,
        context_text: str,
        existing: list[tuple[str, str, set[str]]],
    ) -> str | None:
        user_content = (
            f'New mention: "{mention}" (rough type guess: {type_guess})\n\n'
            f"Text it appeared in:\n{context_text.strip() or '(no context provided)'}\n\n"
            f"Existing canonical entities:\n{_format_existing(existing)}"
        )
        result = llm_router.call_tool(
            task="entity_resolution",
            system_prompt=_SYSTEM_PROMPT,
            user_content=user_content,
            tool_name=_RESOLVE_TOOL["name"],
            tool_description=_RESOLVE_TOOL["description"],
            input_schema=_RESOLVE_TOOL["input_schema"],
            max_tokens=256,
        )
        if result.get("matches_existing"):
            return self._find_canonical(result.get("matched_canonical_id") or "")
        return None

    def snapshot(self) -> dict[str, str]:
        return dict(self._canonical_types)

    def aliases_for(self, canonical_id: str) -> set[str]:
        return set(self._aliases.get(canonical_id, set()))
