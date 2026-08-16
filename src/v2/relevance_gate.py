"""Batched LLM relevance gate for chunk-pop candidates. Runs once per
chunk-pop event, after the mechanical dedup check (v2/dedup.py) has
already removed exact/near-duplicate candidates -- this only judges
candidates that are structurally new.

Deliberately no embedding-similarity cutoff before this gate: retrieval
itself already bounds the candidate set (top-K), and a secondary threshold
on top would kill exactly the surface-dissimilar-but-conceptually-linked
connections this system exists to find.

Judges each candidate against the FULL discovery path from the question
down to the current parent chunk (v2/path.py), plus a mechanical
entity-overlap label per candidate (v2/acceptance.py's
shared_path_entities) -- computed by string matching, no extra LLM call.
This exists because a path-and-parent-only view can still drift: two
chunks can resemble each other locally (e.g. both about "worker pool
scaling") while the accumulated path never actually touches that topic,
and each hop's local plausibility can hide the fact that the thread as a
whole wandered off. Confirmed empirically on the "push notification"
GOLD case: an unrelated webhook-dispatcher incident kept getting admitted
through a chain of locally-plausible-looking hops even with the raw path
text shown, because nothing forced a check against what was actually
already IN that path. The overlap label makes that check explicit and
checkable instead of asking the model to infer it from prose.

Also requires a one-line reason per decision (not just the id) -- forcing
the model to articulate the concrete connection tends to surface weak
justifications before they turn into an accept, and gives every admitted
chunk a stored, auditable reason (see graph.py's ChunkNode.gate_reason).

The tool schema requires an explicit accept/reject decision for EVERY
candidate, not just a sparse list of accepted ids (changed 2026-08-11,
v3 -> v4). Confirmed empirically: the same content, path, and label,
judged via a schema that only lists accepted candidates, rejected a
clear-cut true positive (a Jira ticket whose own text cites its parent
incident's ID) 3 times in a row in real runs; switched to a schema
requiring an explicit decision per candidate, same content, and it
accepted 3 times in a row. Rejecting via omission appears to need less
justification from the model than actively including something -- an
asymmetry the schema itself was creating, independent of prompt wording.

Decoupled from vector_stores.ChunkResult (uses the small GateCandidate
struct instead) so this module is unit-testable with no vector-store or
network dependency -- inject `call_fn` in tests.

Routes through llm_router.py -- see config.LLM_TASK_MODELS["relevance_gate"]
for the current model/fallback chain (stays on Sonnet primary; this is the
mechanism hardened against precision failures earlier this build, not
swapped to a cheaper model without dedicated testing).
"""

from dataclasses import dataclass

import config
import llm_router

_GATE_TOOL = {
    "name": "judge_relevance",
    "description": "Decide accept or reject for EVERY candidate chunk, explicitly, each with a reason.",
    "input_schema": {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "chunk_id": {
                            "type": "string",
                            "description": "chunk_id of the candidate, copied verbatim.",
                        },
                        "accepted": {
                            "type": "boolean",
                            "description": "true if this candidate should be added to the graph, false otherwise.",
                        },
                        "reason": {
                            "type": "string",
                            "description": (
                                "If accepted: one sentence naming the CONCRETE connection -- a shared "
                                "entity, ticket, person, or specific narrative link -- not a generic "
                                "restatement like 'it's relevant to the question.' If rejected: one "
                                "sentence naming the specific reason (e.g. what's missing, or what makes "
                                "it a different thread than the path establishes)."
                            ),
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": (
                                "Only meaningful when accepted=true: how confident you are in the "
                                "accept decision, for audit purposes only -- it does not change the "
                                "decision itself. Use 'low' as a placeholder when accepted=false."
                            ),
                        },
                    },
                    "required": ["chunk_id", "accepted", "reason", "confidence"],
                },
                "description": (
                    "One decision object for EVERY candidate listed below -- do not omit any "
                    "candidate, whether you're accepting or rejecting it. Accept only a candidate "
                    "that both (a) has a genuine, traceable line of relevance back to the ORIGINAL "
                    "QUESTION, and (b) is coherent with the discovery PATH and its shared-entity "
                    "labels, not just the parent chunk in isolation."
                ),
            }
        },
        "required": ["decisions"],
    },
}

_SYSTEM_PROMPT = """You are judging which newly retrieved chunks are worth \
adding to an investigation graph built to answer ONE specific question.

You will be given: the original question; the discovery PATH from the \
question down to the current parent chunk (the chain of entities and \
chunks that connects them -- this is the thread so far, not just \
background); the parent chunk's own text (context for HOW this search was \
triggered, not by itself a reason to accept a candidate); and a list of \
candidates, each labeled with whether it mechanically shares any \
already-known path entity (a plain string/alias match against everything \
discovered so far) or shares none.

WHY the shared-entity label exists: judging relevance from prose alone \
drifts. Two chunks can look alike to each other -- both about "worker pool \
scaling," "delivery retries," or similar generic infra language -- while \
belonging to completely different incidents that the path never actually \
touched. Each individual hop can look locally plausible even as the \
overall thread wanders off the original question. The label turns "does \
this actually connect to what's already here" into a checkable fact \
instead of an impression. A candidate labeled as sharing NO path entity is \
not automatically wrong, but treat it as a strong signal to be STRICT \
about context continuity: require its text to make an unambiguous, direct \
case for belonging to this specific thread, not just a plausible-sounding \
topical resemblance to the parent chunk. When a shared-entity label IS \
present, weigh it as real evidence toward acceptance.

Accept a candidate only if BOTH hold:
1. It has a genuine, traceable line of relevance back to the ORIGINAL \
QUESTION -- directly, or by continuing the same underlying situation the \
path is already tracing (e.g. the path describes a symptom and the \
candidate describes that same incident's root cause, fix, or follow-up, \
even in completely different wording -- like "wanted to buy a home" / \
"mortgage rates were too high" both bearing on the same person's finances).
2. It is coherent with the FULL PATH and its shared-entity labels, not \
just the parent chunk. A candidate that merely resembles ONE node in the \
path (usually the parent) is not enough; it must extend the thread the \
whole path establishes.

When genuinely unsure, prefer rejecting rather than admitting a chunk that \
would fork the investigation onto an unrelated thread.

For every candidate you accept, give a one-sentence reason naming the \
concrete connection (the shared entity, ticket, person, or specific \
narrative link). If you can't articulate a concrete reason, that's itself \
a signal to reject instead of accepting on vibes.

Also rate your confidence in each accept decision as "high", "medium", or \
"low" -- this is recorded for audit purposes only and must NOT change the \
accept/reject decision itself. Decide accept or reject strictly on the two \
criteria above first, then rate whichever confidence level fits the \
connection you just accepted."""


@dataclass
class GateCandidate:
    chunk_id: str
    text: str
    overlap_note: str = ""


@dataclass
class GateAcceptance:
    reason: str
    confidence: str = ""


def _format_candidates(candidates: list[GateCandidate]) -> str:
    parts = []
    for c in candidates:
        label = c.overlap_note or "(no shared-entity check available)"
        parts.append(f"--- candidate chunk_id: {c.chunk_id} ---\n[{label}]\n{c.text.strip()}")
    return "\n\n".join(parts)


class RelevanceGate:
    """Stateless across a run -- safe to share one instance for every
    chunk-pop event."""

    def __init__(self, call_fn=None):
        self._call_fn = call_fn or self._llm_call

    def evaluate(
        self,
        question: str,
        path_summary: str,
        parent_text: str,
        candidates: list[GateCandidate],
    ) -> dict[str, GateAcceptance]:
        """Returns {chunk_id: GateAcceptance(reason, confidence)} for every
        accepted candidate. `confidence` is recorded for audit purposes only
        -- it is not, and must not become, a threshold on the accept/reject
        decision itself (see _SYSTEM_PROMPT)."""
        if not candidates:
            return {}
        accepted = self._call_fn(question, path_summary, parent_text, candidates)
        candidate_ids = {c.chunk_id for c in candidates}
        return {cid: acceptance for cid, acceptance in accepted.items() if cid in candidate_ids}

    def _llm_call(
        self,
        question: str,
        path_summary: str,
        parent_text: str,
        candidates: list[GateCandidate],
    ) -> dict[str, GateAcceptance]:
        user_content = (
            f"ORIGINAL QUESTION (every accepted candidate must bear on this): {question}\n\n"
            f"Discovery path so far (question -> ... -> current parent chunk):\n{path_summary}\n\n"
            f"Parent chunk's own text (context only, for how this search was triggered -- "
            f"not a standalone reason to accept a candidate):\n{parent_text.strip()}\n\n"
            f"Candidates:\n{_format_candidates(candidates)}"
        )
        result = llm_router.call_tool(
            task="relevance_gate",
            system_prompt=_SYSTEM_PROMPT,
            user_content=user_content,
            tool_name=_GATE_TOOL["name"],
            tool_description=_GATE_TOOL["description"],
            input_schema=_GATE_TOOL["input_schema"],
            max_tokens=config.RELEVANCE_GATE_MAX_TOKENS,
        )
        decisions = result.get("decisions", [])
        return {
            item["chunk_id"]: GateAcceptance(reason=item.get("reason", ""), confidence=item.get("confidence", ""))
            for item in decisions
            if isinstance(item, dict) and item.get("chunk_id") and item.get("accepted") is True
        }
