"""Composes human-readable narrative from the ephemeral graph: a short
incremental summary after each turn, and a polished final written report
once the graph stabilizes.

Added per an explicit scope decision (see the "scope amendment" Addendum in
build_phase_1.md) that pulled part of Phase 4 (Streaming/Explanation)
forward into this build, ahead of the original "no final LLM synthesis
pass" exclusion.

Routes through llm_router.py -- see config.LLM_TASK_MODELS["narrator"] for
the current model/fallback chain.
"""

import config
import llm_router


def _format_snapshot(snapshot: dict, max_chunk_chars: int = 2000) -> str:
    # Chunks in this dataset run 260-1150 chars; 2000 is a generous cap that
    # in practice never truncates mid-sentence and gives the model the full
    # source text rather than a partial excerpt it might mistake for a real
    # gap in the underlying document.
    lines = ["ENTITIES:"]
    for entity_id, node in snapshot["entities"].items():
        lines.append(f"- {entity_id} (type: {node['type']}, first seen turn {node['first_seen_turn']})")

    lines.append("")
    lines.append("CHUNKS (source documents found so far):")
    for chunk_id, node in snapshot["chunks"].items():
        excerpt = node["text"][:max_chunk_chars].replace("\n", " ")
        status_note = f", status: {node['status']}" if node["status"] else ""
        merged_note = f" [also seen via: {', '.join(node['merged_refs'])}]" if node["merged_refs"] else ""
        lines.append(f"- {chunk_id} ({node['source_system']}, doc {node['doc_id']}{status_note}){merged_note}: {excerpt}")

    lines.append("")
    lines.append("MENTIONS (chunk -> entity):")
    for chunk_id, entity_id in snapshot["mentions_edges"]:
        lines.append(f"- {chunk_id} mentions {entity_id}")

    lines.append("")
    lines.append("RELATIONS (entity <-> entity, co-occurrence):")
    for a, b, rel in snapshot["relation_edges"]:
        lines.append(f"- {a} {rel} {b}")

    return "\n".join(lines)


_PROGRESS_SYSTEM_PROMPT = """You are narrating the live construction of an \
investigation graph, one turn at a time, for an engineer watching it build. \
Given the original question and the current state of the graph (entities, \
source chunks, and how they connect), write a SHORT (2-4 sentence) plain- \
English update on the current understanding of what happened and what's \
still unclear. Only use information present in the graph data below -- do \
not invent facts, IDs, root causes, or connections that are not explicitly \
present. If the picture is still too thin to say anything meaningful, say \
so briefly rather than speculating."""

_FINAL_REPORT_SYSTEM_PROMPT = """You are writing the final report for an \
investigation graph that has just stabilized. Given the original question, \
the full graph (entities, source chunks, and how they connect), and why the \
search stopped, write a clear, well-organized written answer to the \
question. The graph may include chunks that were retrieved during the \
search but turn out to be unrelated to this specific question -- ignore \
those entirely rather than mentioning them; only discuss material that \
actually bears on answering the question asked. Structure the answer as a \
short direct answer, then a walkthrough of the supporting evidence citing \
the specific ticket/incident/PR/page IDs that are directly relevant to the \
question. Only use information present in the graph data below -- do not \
invent facts, IDs, root causes, or connections that are not explicitly \
present, and do not state something as settled fact unless the graph data \
directly supports it. If the graph doesn't fully answer the question, say \
plainly what's missing rather than asserting an uncertain conclusion with \
confidence."""


def _is_effectively_empty(snapshot: dict) -> bool:
    # The question node itself is always present, so "empty" means nothing
    # BEYOND that root node -- no chunks, and no other entities.
    return not snapshot["chunks"] and len(snapshot["entities"]) <= 1


def summarize_progress(question: str, snapshot: dict, turn: int) -> str:
    if _is_effectively_empty(snapshot):
        return "Nothing found yet."

    user_content = (
        f"Original question: {question}\n\n"
        f"Turn: {turn}\n\n"
        f"Current graph state:\n{_format_snapshot(snapshot)}"
    )
    text = llm_router.call_text(
        task="narrator",
        system_prompt=_PROGRESS_SYSTEM_PROMPT,
        user_content=user_content,
        max_tokens=config.NARRATOR_MAX_TOKENS,
    )
    return text or "(narrative unavailable this turn)"


def compose_final_report(question: str, snapshot: dict, stop_reason: str) -> str:
    if _is_effectively_empty(snapshot):
        return "No connected information was found for this question."

    user_content = (
        f"Original question: {question}\n\n"
        f"Search stopped because: {stop_reason}\n\n"
        f"Final graph state:\n{_format_snapshot(snapshot)}"
    )
    text = llm_router.call_text(
        task="narrator",
        system_prompt=_FINAL_REPORT_SYSTEM_PROMPT,
        user_content=user_content,
        max_tokens=config.FINAL_REPORT_MAX_TOKENS,
    )
    return text or "(final report unavailable)"
