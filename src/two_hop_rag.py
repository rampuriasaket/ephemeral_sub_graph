"""A cheaper alternative to ESG: retrieve once, extract ID-shaped citations
(ticket/incident/PR numbers) literally present in the hop-1 text, fetch
those specific documents by exact substring match as a second round, then
answer using hop1 union hop2. No entity extraction, no entity resolution,
no further follow-up from whatever hop 2 turns up.

Deliberately hard-capped at exactly 2 rounds, and deliberately blind to
free-text component names -- it only ever chases literal ID-shaped tokens
(INC\\d+, PROJ-\\d+, PR-\\d+). The moment you generalize this to also
extract and search on component names, you've stopped building a cheaper
alternative to ESG and started rebuilding ESG's own entity-extraction +
traversal loop. That boundary is the point: this baseline exists to show
what a "just add one more retrieval round" fix actually buys you, and where
it structurally can't go no matter how many rounds you bolt on, since a
document with no ID trail pointing to it is invisible to ID-citation
chasing regardless of hop count.

The set of IDs chased in hop 2 includes any ID-shaped token literally
present in the QUESTION itself, not only ones that happen to surface in
hop-1's results -- without this, an ID named directly in the question was
never chased at all unless some hop-1 result coincidentally also
mentioned it, an avoidable gap rather than a deliberate part of what "one
extra ID-chasing round" is meant to test.
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

_client = None

_ID_PATTERN = re.compile(r"\b(INC\d+|PROJ-\d+|PR-\d+)\b")


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


@dataclass
class TwoHopResult:
    question: str
    retrieved_doc_ids: set[str] = field(default_factory=set)
    chunks: list[ChunkResult] = field(default_factory=list)
    answer_text: str = ""
    cost: "cost_tracker.CostMetrics | None" = None


_ANSWER_SYSTEM_PROMPT = """You answer questions using only the documents \
provided below -- retrieved in two rounds (an initial search, plus a \
follow-up fetch of any ticket/incident/PR IDs cited in the first round's \
results). No further follow-up search is possible beyond that. Only use \
information present in these documents -- do not invent facts, IDs, root \
causes, or connections that are not explicitly present. Cite the specific \
ticket/incident/PR/page IDs you're relying on. If the documents don't \
fully answer the question, say plainly what's missing rather than filling \
the gap with a guess."""


def _fetch_by_id(doc_id: str) -> list[ChunkResult]:
    results: list[ChunkResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.SOURCE_SYSTEMS)) as executor:
        futures = {
            executor.submit(get_vector_store(s).search_exact, doc_id): s for s in config.SOURCE_SYSTEMS
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"[two_hop_rag] hop-2 fetch failed for {doc_id}: {e}", file=sys.stderr)
    return results


def run_two_hop_rag(question: str) -> TwoHopResult:
    cost = cost_tracker.start_tracking()

    hop1_chunks = search_many_with_margin(
        config.SOURCE_SYSTEMS, question, config.TOP_K_PER_SEARCH, config.SEED_SEARCH_MARGIN
    )
    hop1_doc_ids = {c.doc_id for c in hop1_chunks}

    cited_ids = set(_ID_PATTERN.findall(question))
    for c in hop1_chunks:
        cited_ids.update(_ID_PATTERN.findall(c.text))
    new_ids = cited_ids - hop1_doc_ids

    hop2_chunks: list[ChunkResult] = []
    seen_chunk_ids = {c.chunk_id for c in hop1_chunks}
    for doc_id in new_ids:
        for chunk in _fetch_by_id(doc_id):
            if chunk.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk.chunk_id)
                hop2_chunks.append(chunk)

    chunks = hop1_chunks + hop2_chunks
    retrieved_doc_ids = {c.doc_id for c in chunks}

    if not chunks:
        cost_tracker.stop_tracking()
        return TwoHopResult(
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
        print(f"[two_hop_rag] LLM call failed: {e}", file=sys.stderr)
        answer_text = "(answer unavailable)"

    cost = cost_tracker.stop_tracking()
    return TwoHopResult(
        question=question,
        retrieved_doc_ids=retrieved_doc_ids,
        chunks=chunks,
        answer_text=answer_text,
        cost=cost,
    )
