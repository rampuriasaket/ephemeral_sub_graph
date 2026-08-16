"""Turns ESG's and flat-RAG's raw output into comparable numbers: recall,
precision/noise, excluded-doc hits, a structural grounding check, and cost.
"""

import re
from dataclasses import dataclass

from cost_tracker import CostMetrics
from gold_set import GoldCase

_ID_CITATION_PATTERN = re.compile(r"\b(INC\d+|PROJ-\d+|PR-\d+)\b")


def _extract_cited_ids(answer_text: str) -> set[str]:
    """Structural citation check only -- ticket/incident/PR numbers are
    reliably typed verbatim by both systems' answers, so a regex catches
    them reliably. Confluence-page citations (slugs like
    "auth-service-outage-postmortem-august-2026") are NOT reliably restated
    verbatim in prose -- both systems tend to describe them in natural
    language ("the postmortem page") instead -- so they are deliberately
    NOT checked here. That's a known MVP limitation, not an oversight: a
    proper claim-level grounding check (e.g. LLM-as-judge) is the
    documented stretch goal for closing this gap, out of scope for this
    pass per the build prompt.
    """
    return set(_ID_CITATION_PATTERN.findall(answer_text))


@dataclass
class ScoreResult:
    recall: float
    precision: float
    noise_rate: float
    excluded_hits: list[str]
    grounding: float
    ungrounded_citations: list[str]
    cost: CostMetrics | None


def score_run(
    retrieved_doc_ids: set[str],
    answer_text: str,
    gold: GoldCase,
    cost: CostMetrics | None,
) -> ScoreResult:
    expected = set(gold.expected_doc_ids)
    excluded = set(gold.excluded_doc_ids)

    hits = retrieved_doc_ids & expected
    recall = (len(hits) / len(expected)) if expected else 1.0
    precision = (len(hits) / len(retrieved_doc_ids)) if retrieved_doc_ids else 1.0
    noise_rate = 1.0 - precision

    excluded_hits = sorted(retrieved_doc_ids & excluded)

    cited_ids = _extract_cited_ids(answer_text)
    ungrounded_citations = sorted(cited_ids - retrieved_doc_ids)
    grounding = ((len(cited_ids) - len(ungrounded_citations)) / len(cited_ids)) if cited_ids else 1.0

    return ScoreResult(
        recall=recall,
        precision=precision,
        noise_rate=noise_rate,
        excluded_hits=excluded_hits,
        grounding=grounding,
        ungrounded_citations=ungrounded_citations,
        cost=cost,
    )
