"""Chunk convergence/dedup, cheapest check first, no LLM involved
(esg_algorithm_v2.md section 6):

1. Exact chunk_id match -> EXACT_CONVERGENCE (the same chunk reached via two
   independent parents -- a real edge, not a compromise).
2. Embedding near-dup (>= threshold) -> NEAR_DUP (a different chunk_id,
   near-identical content -- merge, don't double-add).
3. Neither -> NEW.

`graph` only needs `.chunks: dict[str, ChunkNode]` and
`.nearest_chunk_match(embedding) -> (id | None, score)` -- see graph.py.
`embed_fn` is injectable so this is testable without a real embeddings call.
"""

from dataclasses import dataclass
from enum import Enum

import config
from embeddings import embed


class DedupOutcome(Enum):
    EXACT_CONVERGENCE = "exact_convergence"
    NEAR_DUP = "near_dup"
    NEW = "new"


@dataclass
class DedupResult:
    outcome: DedupOutcome
    existing_chunk_id: str | None = None
    score: float | None = None


class ChunkDedupPolicy:
    def __init__(self, graph, threshold: float | None = None, embed_fn=None):
        self.graph = graph
        self.threshold = config.CHUNK_DEDUP_THRESHOLD if threshold is None else threshold
        self._embed_fn = embed_fn or embed

    def classify(self, chunk_result) -> DedupResult:
        if chunk_result.chunk_id in self.graph.chunks:
            return DedupResult(DedupOutcome.EXACT_CONVERGENCE, chunk_result.chunk_id, 1.0)

        embedding = self._embed_fn(chunk_result.text)
        best_id, best_score = self.graph.nearest_chunk_match(embedding)
        if best_id is not None and best_score >= self.threshold:
            return DedupResult(DedupOutcome.NEAR_DUP, best_id, best_score)
        return DedupResult(DedupOutcome.NEW, None, best_score if best_id else None)
