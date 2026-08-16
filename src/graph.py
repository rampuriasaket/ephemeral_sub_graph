"""The bipartite ephemeral graph: ChunkNodes and EntityNodes, connected by
structural MentionsEdges and semantic RelationEdges. One instance per
discovery run -- built up turn by turn, thrown away at the end.
"""

from dataclasses import asdict, dataclass, field

import config
from embeddings import cosine_similarity, embed
from vector_stores import ChunkResult


@dataclass
class ChunkNode:
    id: str
    source_system: str
    doc_id: str
    text: str
    first_seen_turn: int
    status: str = ""
    merged_refs: list[str] = field(default_factory=list)
    # Every parent (entity_id or chunk_id) that independently led here.
    # Distinct from merged_refs, which records which raw source docs got
    # folded into this node on a near-dup match; discovered_via records
    # *why* this node exists in the graph at all.
    discovered_via: list[str] = field(default_factory=list)
    # The relevance gate's one-line reason for accepting this chunk,
    # whenever it was admitted via the LLM gate (chunk-pop always;
    # entity-pop as of 2026-08-11, when text-match auto-accept was removed
    # -- see v2/discovery_loop_v2.py's process_entity_pop). Empty only for
    # seed chunks (accepted unconditionally, no gate call at all).
    gate_reason: str = ""
    # The gate's own self-rated confidence ("high"/"medium"/"low") in the
    # accept decision that produced gate_reason -- recorded for audit
    # purposes only, never used as a threshold on the accept/reject
    # decision itself (see v2/relevance_gate.py's _SYSTEM_PROMPT). Empty
    # wherever gate_reason is empty, for the same reasons.
    gate_confidence: str = ""


@dataclass
class EntityNode:
    id: str
    type: str
    first_seen_turn: int
    # The single chunk_id (or "(question)") this entity was extracted
    # from. Entities have exactly one discovery path (resolver dedup means
    # a second mention never creates a second EntityNode), unlike
    # ChunkNode.discovered_via which can have several. Together with
    # discovered_via, this lets v2/path.py walk from any chunk or entity
    # back to the question.
    parent: str = ""


class Graph:
    def __init__(self):
        self.chunks: dict[str, ChunkNode] = {}
        self.entities: dict[str, EntityNode] = {}
        self.mentions_edges: set[tuple[str, str]] = set()
        self.relation_edges: set[tuple[str, str, str]] = set()
        # chunk-pop can connect two chunks directly (a chunk's own content
        # search leads to another chunk) with no entity in between.
        self.chunk_links: set[tuple[str, str]] = set()
        self._chunk_embeddings: dict[str, list[float]] = {}

    def nearest_chunk_match(self, embedding: list[float]) -> tuple[str | None, float]:
        """Highest cosine-similarity existing chunk to `embedding`, or
        (None, 0.0) if the graph has no chunks yet. Shared by upsert_chunk
        (below) and ChunkDedupPolicy (v2/dedup.py) so both agree on what
        "near-duplicate" means."""
        best_id, best_score = None, 0.0
        for existing_id, existing_embedding in self._chunk_embeddings.items():
            score = cosine_similarity(embedding, existing_embedding)
            if score > best_score:
                best_id, best_score = existing_id, score
        return best_id, best_score

    def upsert_chunk(self, chunk_result: ChunkResult, turn: int) -> tuple[ChunkNode, bool]:
        if chunk_result.chunk_id in self.chunks:
            return self.chunks[chunk_result.chunk_id], False

        new_embedding = embed(chunk_result.text)
        best_match_id, best_score = self.nearest_chunk_match(new_embedding)

        if best_match_id is not None and best_score >= config.CHUNK_DEDUP_THRESHOLD:
            node = self.chunks[best_match_id]
            ref = f"{chunk_result.source_system}:{chunk_result.doc_id}"
            if ref not in node.merged_refs:
                node.merged_refs.append(ref)
            return node, False

        node = ChunkNode(
            id=chunk_result.chunk_id,
            source_system=chunk_result.source_system,
            doc_id=chunk_result.doc_id,
            text=chunk_result.text,
            first_seen_turn=turn,
            status=chunk_result.metadata.get("status", ""),
        )
        self.chunks[node.id] = node
        self._chunk_embeddings[node.id] = new_embedding
        return node, True

    def add_chunk_node(self, chunk_result: ChunkResult, turn: int, parent_label: str) -> ChunkNode:
        """Unconditional insert -- the caller (v2/dedup.py's
        ChunkDedupPolicy, via the discovery loop) has already established
        this chunk_id is new and not a near-duplicate of anything in the
        graph. `upsert_chunk` above does its own check-and-insert in one
        step instead; this is the equivalent split into "check"
        (nearest_chunk_match, called by the policy) and "insert" (here),
        so each half is testable on its own."""
        embedding = embed(chunk_result.text)
        node = ChunkNode(
            id=chunk_result.chunk_id,
            source_system=chunk_result.source_system,
            doc_id=chunk_result.doc_id,
            text=chunk_result.text,
            first_seen_turn=turn,
            status=chunk_result.metadata.get("status", ""),
            discovered_via=[parent_label],
        )
        self.chunks[node.id] = node
        self._chunk_embeddings[node.id] = embedding
        return node

    def note_discovered_via(self, chunk_id: str, parent_label: str) -> bool:
        """v2 only. Records an additional independent path into an already-
        merged chunk (exact chunk_id convergence or embedding near-dup) --
        see esg_algorithm_v2.md section 6."""
        node = self.chunks[chunk_id]
        if parent_label in node.discovered_via:
            return False
        node.discovered_via.append(parent_label)
        return True

    def add_chunk_link(self, parent_chunk_id: str, child_chunk_id: str) -> bool:
        """v2 only. A chunk-pop can lead directly to another chunk with no
        entity in between -- this is the edge type that records that."""
        if parent_chunk_id == child_chunk_id:
            return False
        key = (parent_chunk_id, child_chunk_id)
        if key in self.chunk_links:
            return False
        self.chunk_links.add(key)
        return True

    def upsert_entity(self, canonical_id: str, type_guess: str, turn: int) -> tuple[EntityNode, bool]:
        if canonical_id in self.entities:
            return self.entities[canonical_id], False
        node = EntityNode(id=canonical_id, type=type_guess, first_seen_turn=turn)
        self.entities[canonical_id] = node
        return node, True

    def add_mentions_edge(self, chunk_node: ChunkNode, entity_node: EntityNode) -> bool:
        key = (chunk_node.id, entity_node.id)
        if key in self.mentions_edges:
            return False
        self.mentions_edges.add(key)
        return True

    def add_relation_edge(self, entity_a: str, entity_b: str, relation_type: str) -> bool:
        if entity_a == entity_b:
            return False
        a, b = sorted([entity_a, entity_b])
        key = (a, b, relation_type)
        if key in self.relation_edges:
            return False
        self.relation_edges.add(key)
        return True

    def snapshot(self) -> dict:
        return {
            "chunks": {cid: asdict(node) for cid, node in self.chunks.items()},
            "entities": {eid: asdict(node) for eid, node in self.entities.items()},
            "mentions_edges": sorted(self.mentions_edges),
            "relation_edges": sorted(self.relation_edges),
            "chunk_links": sorted(self.chunk_links),
        }
