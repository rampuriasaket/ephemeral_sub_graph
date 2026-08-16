"""Shared local embedding function.

Used both to embed chunks going into ChromaDB and to embed arbitrary
strings for entity-alias / chunk-dedup similarity scoring, so both paths
stay consistent (per build_phase_1.md's assumptions section).
"""

import numpy as np
from chromadb.utils import embedding_functions

_embedding_function = embedding_functions.DefaultEmbeddingFunction()


def get_embedding_function():
    """The shared embedding function, for passing directly to Chroma collections."""
    return _embedding_function


def embed(text: str) -> list[float]:
    return _embedding_function([text])[0]


def embed_many(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return _embedding_function(list(texts))


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
