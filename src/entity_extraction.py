"""LLM-backed entity extraction, kept behind a single interface so the
model/provider can be swapped later without touching the rest of the code.

Routes through llm_router.py -- see config.LLM_TASK_MODELS["entity_extraction"]
for the current model/fallback chain.
"""

from dataclasses import dataclass

import config
import llm_router

ENTITY_TYPES = ["Component", "TicketID", "CommitOrPR", "Person", "Team", "Other"]

_EXTRACTION_TOOL = {
    "name": "record_entities",
    "description": "Record the distinct entities mentioned in a chunk of text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "mention": {
                            "type": "string",
                            "description": "The entity exactly as it appears in the text (surface form, not normalized).",
                        },
                        "type": {
                            "type": "string",
                            "enum": ENTITY_TYPES,
                            "description": "Rough type guess for this mention.",
                        },
                    },
                    "required": ["mention", "type"],
                },
            }
        },
        "required": ["entities"],
    },
}

_SYSTEM_PROMPT = """You extract distinct named entities from a single chunk of \
engineering-system text (an incident, ticket, pull request, or wiki page). \
List every distinct component/service name, ticket/incident ID (e.g. INC1042, \
PROJ-201), PR/commit reference (e.g. PR-455), person name, and team name \
mentioned in the text. Use the exact surface form as it appears in the text \
-- do not normalize, rename, or invent entities that are not present in the \
text. If the same entity is mentioned multiple times, list it once.

Skip generic role, queue, or department labels that are not themselves a \
specific, uniquely-identifying name -- e.g. "Support", "Engineering", "the \
team", "on-call" describe a broad function, not a specific entity, even \
when capitalized or used as a field value (assignee, owner, queue). Only \
extract a team/group name when it is specific enough to identify one \
particular team (e.g. "Data Platform team", "checkout-service on-call"). \
This matters because every extracted entity becomes searchable across the \
entire corpus -- a generic word extracted as an entity will spuriously \
match unrelated documents that happen to share that common word."""


@dataclass
class RawEntity:
    mention: str
    type_guess: str


def extract_entities(text: str) -> list[RawEntity]:
    if not text.strip():
        return []

    result = llm_router.call_tool(
        task="entity_extraction",
        system_prompt=_SYSTEM_PROMPT,
        user_content=text,
        tool_name=_EXTRACTION_TOOL["name"],
        tool_description=_EXTRACTION_TOOL["description"],
        input_schema=_EXTRACTION_TOOL["input_schema"],
        max_tokens=config.ENTITY_EXTRACTION_MAX_TOKENS,
    )
    raw_entities = result.get("entities", [])
    return [
        RawEntity(mention=e["mention"].strip(), type_guess=e.get("type", "Other"))
        for e in raw_entities
        if isinstance(e, dict) and e.get("mention", "").strip()
    ]
