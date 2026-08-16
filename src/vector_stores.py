"""Uniform search() wrapper over the local ChromaDB collections.

The discovery loop should never need to know which system it's talking to
beyond a name string -- every VectorStore exposes the same interface.
"""

import concurrent.futures
import json
from dataclasses import dataclass, field

import chromadb

import config
import cost_tracker
from embeddings import get_embedding_function

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return _client


@dataclass
class ChunkResult:
    chunk_id: str
    text: str
    source_system: str
    doc_id: str
    metadata: dict = field(default_factory=dict)


class VectorStore:
    def __init__(self, source_system: str):
        self.source_system = source_system
        self._collection = _get_client().get_collection(
            name=source_system,
            embedding_function=get_embedding_function(),
        )

    def search(self, query_text: str, top_k: int = config.TOP_K_PER_SEARCH) -> list[ChunkResult]:
        cost_tracker.record_retrieval_call()
        result = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        if not result["ids"] or not result["ids"][0]:
            return []

        chunks = []
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            if distance > config.MAX_SEARCH_DISTANCE:
                continue  # not actually relevant -- just top-k padding
            chunks.append(
                ChunkResult(
                    chunk_id=chunk_id,
                    text=text,
                    source_system=metadata.get("source_system", self.source_system),
                    doc_id=metadata.get("doc_id", ""),
                    metadata=dict(metadata),
                )
            )
        return chunks

    def search_with_distances(
        self, query_text: str, top_k: int = config.TOP_K_PER_SEARCH
    ) -> list[tuple[ChunkResult, float]]:
        """Like search(), but returns (chunk, distance) pairs with no
        absolute distance filtering -- for callers that want to apply their
        own relative/margin-based cutoff instead of MAX_SEARCH_DISTANCE.
        A flat threshold can't tell "a broad query with several genuinely
        different real matches at similar distances" apart from "a generic
        query where only the single best result is real and everything else
        is corpus-wide boilerplate noise" -- a cutoff relative to the best
        distance actually found can.
        """
        cost_tracker.record_retrieval_call()
        result = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        if not result["ids"] or not result["ids"][0]:
            return []

        pairs = []
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            chunk = ChunkResult(
                chunk_id=chunk_id,
                text=text,
                source_system=metadata.get("source_system", self.source_system),
                doc_id=metadata.get("doc_id", ""),
                metadata=dict(metadata),
            )
            pairs.append((chunk, distance))
        return pairs

    def search_exact(self, literal_string: str) -> list[ChunkResult]:
        """Literal match, for ID-type leads (ticket/PR numbers) -- either
        the ID appears in the chunk's own embedded text, OR the chunk cites
        it via a structured header field (RELATED WORK, LINKED TICKET,
        etc.), captured at ingest time as `explicit_related_ids` metadata.

        The metadata check matters because header fields other than
        doc_id/title are deliberately excluded from embedded text (see
        ingest.py -- avoids boilerplate wrecking the calibrated
        MAX_SEARCH_DISTANCE). That's fine when the ID also appears in the
        body text, but some chunks (e.g. informal Slack threads that cite a
        ticket only in their RELATED field, never typing the ID out in the
        conversation itself) cite an ID *only* in that excluded metadata --
        without this check, such a chunk is permanently unreachable by
        exact-ID search. Confirmed 2026-08, see results/regression_full_8.md.

        An ID like "INC1042" has no useful semantic content -- embedding
        search on a bare ID matches other documents' generic boilerplate
        shape rather than actual cross-references, which is why this stays
        a literal/exact check rather than a nearest-neighbor one.
        """
        cost_tracker.record_retrieval_call()
        # Text match: unchanged from the original implementation -- Chroma's
        # own $contains, not a hand-rolled Python substring check. Those two
        # are NOT equivalent (confirmed 2026-08: a naive `literal_string in
        # text` client-side check matched far more loosely, pulling in
        # unrelated docs a plain-language entity string happened to be a
        # substring of). Do not "simplify" this into one client-side loop.
        text_result = self._collection.get(
            where_document={"$contains": literal_string},
            include=["documents", "metadatas"],
        )

        chunks = []
        matched_ids = set()
        for chunk_id, text, metadata in zip(text_result["ids"], text_result["documents"], text_result["metadatas"]):
            chunks.append(
                ChunkResult(
                    chunk_id=chunk_id,
                    text=text,
                    source_system=metadata.get("source_system", self.source_system),
                    doc_id=metadata.get("doc_id", ""),
                    metadata=dict(metadata),
                )
            )
            matched_ids.add(chunk_id)

        # Metadata match: additive only, never removes/replaces a text-match
        # result. Separate collection scan (not combined into the query
        # above) so the text-match path's behavior is provably unchanged.
        cost_tracker.record_retrieval_call()
        all_chunks = self._collection.get(include=["documents", "metadatas"])
        for chunk_id, text, metadata in zip(all_chunks["ids"], all_chunks["documents"], all_chunks["metadatas"]):
            if chunk_id in matched_ids:
                continue
            related_ids = json.loads(metadata.get("explicit_related_ids") or "[]")
            if literal_string not in related_ids:
                continue
            chunks.append(
                ChunkResult(
                    chunk_id=chunk_id,
                    text=text,
                    source_system=metadata.get("source_system", self.source_system),
                    doc_id=metadata.get("doc_id", ""),
                    metadata=dict(metadata),
                )
            )
            matched_ids.add(chunk_id)

        return chunks


_stores: dict[str, VectorStore] = {}


def get_vector_store(source_system: str) -> VectorStore:
    if source_system not in _stores:
        _stores[source_system] = VectorStore(source_system)
    return _stores[source_system]


def all_vector_stores() -> dict[str, VectorStore]:
    return {s: get_vector_store(s) for s in config.SOURCE_SYSTEMS}


def search_many_with_margin(
    source_systems: list[str],
    query_text: str,
    top_k: int = config.TOP_K_PER_SEARCH,
    margin: float = config.SEED_SEARCH_MARGIN,
) -> list[ChunkResult]:
    """Search the given systems in parallel and keep only results within
    `margin` of the single best distance found anywhere -- the retrieval
    strategy for question-level (not entity-level) queries. Used by ESG's
    own seed search, and by both baselines (flat-RAG, two-hop), so all
    systems start from identical retrieval quality and a comparison between
    them isolates the traversal/graph mechanism, not a difference in
    retrieval.
    """
    all_pairs: list[tuple[ChunkResult, float]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(len(source_systems), 1)) as executor:
        futures = {
            executor.submit(get_vector_store(s).search_with_distances, query_text, top_k): s
            for s in source_systems
        }
        for future in concurrent.futures.as_completed(futures):
            all_pairs.extend(future.result())

    if not all_pairs:
        return []
    best_distance = min(dist for _, dist in all_pairs)
    cutoff = best_distance + margin
    return [chunk for chunk, dist in all_pairs if dist <= cutoff]
