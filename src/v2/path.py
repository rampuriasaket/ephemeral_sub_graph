"""Walks from any chunk or entity back to the question, using
ChunkNode.discovered_via[0] and EntityNode.parent (both v2-only fields on
graph.py's shared node types -- see their docstrings).

Exists because a relevance-gate judgment scoped to just "the question" and
"the immediate parent chunk" can't tell a candidate that continues the
actual thread from one that merely resembles the parent chunk in isolation
-- two chunks can look alike to each other (e.g. both about worker-pool
scaling) while the accumulated path from the question never touches that
topic at all. Feeding the full path into the gate gives it that context.

Kept dependency-free (duck-typed on graph.chunks / graph.entities) so it's
unit-testable with a bare fake graph, no real Graph instance needed.
"""

from dataclasses import dataclass

QUESTION = "question"
ENTITY = "entity"
CHUNK = "chunk"

QUESTION_PARENT_LABEL = "(question)"


@dataclass(frozen=True)
class PathNode:
    kind: str  # QUESTION, ENTITY, or CHUNK
    ref_id: str


def _parent_of(graph, kind: str, ref_id: str) -> str | None:
    if kind == CHUNK:
        node = graph.chunks.get(ref_id)
        if node is None or not node.discovered_via:
            return None
        return node.discovered_via[0]
    if kind == ENTITY:
        node = graph.entities.get(ref_id)
        if node is None or not node.parent:
            return None
        return node.parent
    return None


def build_path(graph, start_kind: str, start_id: str, max_hops: int = 25) -> list[PathNode]:
    """Root-first chain ending at (start_kind, start_id) inclusive. Stops at
    the question sentinel, an unknown/missing parent, or max_hops (a
    defensive cap -- FrontierQueue's visit-once guarantee should make a
    cycle impossible, but a path walker should never spin forever if that
    invariant is ever violated)."""
    chain = [PathNode(start_kind, start_id)]
    kind, ref_id = start_kind, start_id

    for _ in range(max_hops):
        parent = _parent_of(graph, kind, ref_id)
        if parent is None or parent == QUESTION_PARENT_LABEL:
            chain.append(PathNode(QUESTION, QUESTION_PARENT_LABEL))
            break
        parent_kind = ENTITY if parent in graph.entities else CHUNK
        chain.append(PathNode(parent_kind, parent))
        kind, ref_id = parent_kind, parent
    else:
        chain.append(PathNode(QUESTION, "(path truncated at max_hops)"))

    chain.reverse()
    return chain


def format_path(graph, chain: list[PathNode]) -> str:
    """Human/LLM-readable breadcrumb, e.g.:
    [QUESTION] -> entity:image uploads (Component) -> chunk:servicenow:INC1155:0
    -> entity:image-processing-service (Component) -> chunk:gitrepo:PR-545:0
    """
    parts = []
    for node in chain:
        if node.kind == QUESTION:
            parts.append("[QUESTION]")
        elif node.kind == ENTITY:
            entity = graph.entities.get(node.ref_id)
            type_note = f" ({entity.type})" if entity else ""
            parts.append(f"entity:{node.ref_id}{type_note}")
        else:
            chunk = graph.chunks.get(node.ref_id)
            doc_note = f" [{chunk.source_system}:{chunk.doc_id}]" if chunk else ""
            parts.append(f"chunk:{node.ref_id}{doc_note}")
    return " -> ".join(parts)


def path_entity_ids(chain: list[PathNode]) -> list[str]:
    """The canonical entity ids that appear as ancestors in this path --
    the set a chunk-pop candidate's overlap gets checked against (see
    v2/acceptance.py's shared_path_entities). Deliberately ancestors only,
    not the popped chunk's own (not-yet-discovered) children."""
    return [node.ref_id for node in chain if node.kind == ENTITY]
