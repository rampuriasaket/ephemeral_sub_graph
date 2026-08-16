"""v2 of scorer.py's fabrication check. scorer.py (v1) is untouched -- this
is a standalone copy, not a replacement.

Bug fixed: v1 flags a cited ID as fabricated whenever it's absent from
`retrieved_doc_ids`, even when the ID is mentioned inside the body text of a
chunk that WAS retrieved (e.g. a Jira ticket's own text naming a related-but-
separate ticket ID). Confirmed false-positive mechanism on cases 9 and 12,
all 3 runs (5 flags total).

v2's rule: a cited ID is fabricated only if it appears in neither
`retrieved_doc_ids` NOR the body text of any retrieved chunk.
"""

import re
from dataclasses import dataclass

import config
from cost_tracker import CostMetrics
from gold_set import GoldCase
from vector_stores import get_vector_store

_ID_CITATION_PATTERN = re.compile(r"\b(INC\d+|PROJ-\d+|PR-\d+)\b")


def _extract_cited_ids(answer_text: str) -> set[str]:
    return set(_ID_CITATION_PATTERN.findall(answer_text))


@dataclass
class ScoreResultV2:
    recall: float
    precision: float
    noise_rate: float
    excluded_hits: list[str]
    grounding: float
    ungrounded_citations: list[str]
    text_grounded_citations: list[str]  # cited, not in retrieved_doc_ids, but named inside retrieved chunk text
    cost: CostMetrics | None


_doc_text_cache: dict[str, str] = {}


def _all_doc_text() -> dict[str, str]:
    """doc_id -> concatenated body text of every chunk belonging to that doc,
    read once from the persisted Chroma stores (no LLM calls). Corpus is
    unchanged since the 3 runs, so this reflects what was actually
    retrievable at run time.
    """
    global _doc_text_cache
    if _doc_text_cache:
        return _doc_text_cache
    texts: dict[str, list[str]] = {}
    for system in config.SOURCE_SYSTEMS:
        store = get_vector_store(system)
        raw = store._collection.get(include=["documents", "metadatas"])
        for text, metadata in zip(raw["documents"], raw["metadatas"]):
            doc_id = metadata.get("doc_id", "")
            if doc_id:
                texts.setdefault(doc_id, []).append(text)
    _doc_text_cache = {doc_id: "\n".join(chunks) for doc_id, chunks in texts.items()}
    return _doc_text_cache


def score_run(
    retrieved_doc_ids: set[str],
    answer_text: str,
    gold: GoldCase,
    cost: CostMetrics | None,
) -> ScoreResultV2:
    expected = set(gold.expected_doc_ids)
    excluded = set(gold.excluded_doc_ids)

    hits = retrieved_doc_ids & expected
    recall = (len(hits) / len(expected)) if expected else 1.0
    precision = (len(hits) / len(retrieved_doc_ids)) if retrieved_doc_ids else 1.0
    noise_rate = 1.0 - precision

    excluded_hits = sorted(retrieved_doc_ids & excluded)

    cited_ids = _extract_cited_ids(answer_text)
    not_in_retrieved = cited_ids - retrieved_doc_ids

    all_text = _all_doc_text()
    retrieved_text = "\n".join(all_text.get(doc_id, "") for doc_id in retrieved_doc_ids)

    ungrounded_citations = sorted(cid for cid in not_in_retrieved if cid not in retrieved_text)
    text_grounded_citations = sorted(cid for cid in not_in_retrieved if cid in retrieved_text)

    grounding = ((len(cited_ids) - len(ungrounded_citations)) / len(cited_ids)) if cited_ids else 1.0

    return ScoreResultV2(
        recall=recall,
        precision=precision,
        noise_rate=noise_rate,
        excluded_hits=excluded_hits,
        grounding=grounding,
        ungrounded_citations=ungrounded_citations,
        text_grounded_citations=text_grounded_citations,
        cost=cost,
    )
