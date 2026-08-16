"""The simplest reasonable alternative to ESG: single-shot retrieval +
answer. No graph, no traversal, no entity resolution, no multi-turn
follow-up, no connectivity rule. Uses the SAME retrieval (
vector_stores.search_many_with_margin) and the same "don't guess"
grounding philosophy as ESG's own narrator, so a comparison between the two
isolates the traversal/graph mechanism specifically -- not a difference in
retrieval quality or prompt style.

One deliberate exception to "single semantic pass, no cross-referencing":
any ID-shaped token (INC123, PROJ-123, PR-123) literally present in the
question is also looked up via exact match (search_exact -- the same
body-text + metadata lookup ESG's entity-pop uses), so a document whose
only connection to a directly-named ID is a citation in a structured
field excluded from embedded text (see ingest.py's RELATED_FIELDS) isn't
structurally unreachable just because it names the ID nowhere in its own
body text. Everything else about flat-RAG is unchanged.
"""

import concurrent.futures
import re
import sys
from dataclasses import dataclass, field

from anthropic import Anthropic
from dotenv import load_dotenv

import config
import cost_tracker
from vector_stores import ChunkResult, get_vector_store, search_many_with_margin

load_dotenv()

_ID_PATTERN = re.compile(r"\b(INC\d+|PROJ-\d+|PR-\d+)\b")

_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


@dataclass
class BaselineResult:
    question: str
    retrieved_doc_ids: set[str] = field(default_factory=set)
    chunks: list[ChunkResult] = field(default_factory=list)
    answer_text: str = ""
    cost: "cost_tracker.CostMetrics | None" = None


def _exact_search_question_ids(question: str) -> list[ChunkResult]:
    """Exact-match lookup for every ID-shaped token literally present in
    the question, across all systems in parallel. Additive to the
    semantic pass -- see module docstring."""
    ids = set(_ID_PATTERN.findall(question))
    if not ids:
        return []

    results: list[ChunkResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.SOURCE_SYSTEMS) * len(ids)) as executor:
        futures = {}
        for doc_id in ids:
            for source_system in config.SOURCE_SYSTEMS:
                future = executor.submit(get_vector_store(source_system).search_exact, doc_id)
                futures[future] = source_system
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"[baseline_flat_rag] exact search failed: {e}", file=sys.stderr)
    return results


_ANSWER_SYSTEM_PROMPT = """You answer questions using only the documents \
provided below -- the same set of documents, retrieved once, is all you \
have to work with (no follow-up search is possible). Only use information \
present in these documents -- do not invent facts, IDs, root causes, or \
connections that are not explicitly present. Cite the specific ticket/\
incident/PR/page IDs you're relying on. If the documents don't fully \
answer the question, say plainly what's missing rather than filling the \
gap with a guess."""


def run_flat_rag(question: str) -> BaselineResult:
    cost = cost_tracker.start_tracking()

    chunks = search_many_with_margin(
        config.SOURCE_SYSTEMS, question, config.TOP_K_PER_SEARCH, config.SEED_SEARCH_MARGIN
    )

    seen_chunk_ids = {c.chunk_id for c in chunks}
    for chunk in _exact_search_question_ids(question):
        if chunk.chunk_id not in seen_chunk_ids:
            seen_chunk_ids.add(chunk.chunk_id)
            chunks.append(chunk)

    retrieved_doc_ids = {c.doc_id for c in chunks}

    if not chunks:
        cost_tracker.stop_tracking()
        return BaselineResult(
            question=question,
            retrieved_doc_ids=set(),
            chunks=[],
            answer_text="No relevant documents found.",
            cost=cost,
        )

    documents_block = "\n\n".join(f"[{c.source_system}:{c.doc_id}]\n{c.text}" for c in chunks)
    user_content = f"Question: {question}\n\nDocuments:\n{documents_block}"

    try:
        response = _get_client().messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.FINAL_REPORT_MAX_TOKENS,
            system=_ANSWER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        rates = config.LLM_PRICING[config.ANTHROPIC_MODEL]
        call_cost = (response.usage.input_tokens * rates["input"] + response.usage.output_tokens * rates["output"]) / 1_000_000
        cost_tracker.record_llm_call(
            response.usage.input_tokens, response.usage.output_tokens, call_cost, config.PROVIDER_ANTHROPIC, config.ANTHROPIC_MODEL
        )
        answer_text = "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception as e:
        print(f"[baseline_flat_rag] LLM call failed: {e}", file=sys.stderr)
        answer_text = "(answer unavailable)"

    cost = cost_tracker.stop_tracking()
    return BaselineResult(
        question=question,
        retrieved_doc_ids=retrieved_doc_ids,
        chunks=chunks,
        answer_text=answer_text,
        cost=cost,
    )
