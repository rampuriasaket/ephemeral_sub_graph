"""The ESG discovery algorithm: run(question) -> (snapshot, report, cost,
stop_reason).

A single FIFO queue holds both entities and chunks, popped strictly in
discovery order. Every candidate goes through mechanical
dedup-then-relevance-gate ordering before it's accepted, with separate
call budgets for entity-search and chunk-search so one mechanism can't
starve the other.

Every non-trivial policy lives in its own module (v2/frontier.py,
v2/budget.py, v2/caps.py, v2/dedup.py, v2/acceptance.py,
v2/relevance_gate.py, v2/stop_policy.py) so each is independently
unit-testable -- this file only wires them together.
"""

import concurrent.futures
import json
import sys

import config
import cost_tracker
from entity_extraction import extract_entities
from entity_resolution import EntityResolver
from graph import ChunkNode, EntityNode, Graph
from narrator import compose_final_report
from vector_stores import ChunkResult, get_vector_store, search_many_with_margin

from v2.acceptance import ENTITY_MATCH_METADATA, ENTITY_MATCH_NONE, entity_pop_accepts, shared_path_entities
from v2.budget import CallBudget
from v2.caps import RunCaps
from v2.dedup import ChunkDedupPolicy, DedupOutcome
from v2.frontier import CHUNK, ENTITY, FrontierQueue
from v2.path import build_path, format_path, path_entity_ids
from v2.relevance_gate import GateCandidate, RelevanceGate
from v2.run_log import RunLog
from v2.stop_policy import should_stop

QUESTION_PARENT_LABEL = "(question)"


def dispatch_search(query_text: str, is_id_lead: bool, budget: CallBudget) -> dict[str, list[ChunkResult]]:
    """Fire search (or exact-match) at every system still within `budget`,
    in parallel. Takes whichever CallBudget instance is active
    (entity-search or chunk-search)."""
    results: dict[str, list[ChunkResult]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.SOURCE_SYSTEMS)) as executor:
        futures = {}
        for source_system in config.SOURCE_SYSTEMS:
            if not budget.can_call(source_system):
                continue
            budget.record_call(source_system)
            store = get_vector_store(source_system)
            if is_id_lead:
                future = executor.submit(store.search_exact, query_text)
            else:
                future = executor.submit(store.search, query_text, config.TOP_K_PER_SEARCH)
            futures[future] = source_system

        for future in concurrent.futures.as_completed(futures):
            source_system = futures[future]
            try:
                results[source_system] = future.result()
            except Exception as e:
                print(f"[discovery_loop_v2] search failed for {source_system}: {e}", file=sys.stderr)
    return results


def dispatch_seed_search(question: str, budget: CallBudget) -> list[ChunkResult]:
    """Turn-0 broad search on the raw question text. Counted against the
    chunk-search budget -- it's a content search, not an entity search."""
    allowed_systems = [s for s in config.SOURCE_SYSTEMS if budget.can_call(s)]
    for source_system in allowed_systems:
        budget.record_call(source_system)
    return search_many_with_margin(allowed_systems, question, config.TOP_K_PER_SEARCH, config.SEED_SEARCH_MARGIN)


def accept_chunk(
    graph: Graph,
    resolver: EntityResolver,
    frontier: FrontierQueue,
    chunk_result: ChunkResult,
    turn: int,
    parent_label: str,
    extra_mention_entity_id: str | None = None,
    gate_reason: str = "",
    gate_confidence: str = "",
    log: RunLog | None = None,
    accept_reason: str = "",
) -> ChunkNode:
    """The shared acceptance path (esg_algorithm_v2.md section 7). Runs
    once, for whichever pop type led here, only for candidates that already
    passed their respective acceptance test and dedup check. `gate_reason`/
    `gate_confidence` are non-empty for any acceptance that went through the
    relevance gate -- as of 2026-08-11 that is EVERY acceptance, chunk-pop
    and entity-pop alike (entity-pop's text-match auto-accept was removed;
    see process_entity_pop). Only seed chunks (accepted unconditionally, no
    gate call at all) leave these empty. `accept_reason` is log-only (falls
    back to `gate_reason` when not given) -- kept separate so entity-pop can
    log its own mechanical framing without polluting the graph's stored
    `gate_reason` field, which esg_algorithm_v2.md documents as gate-only."""
    chunk_node = graph.add_chunk_node(chunk_result, turn, parent_label)
    chunk_node.gate_reason = gate_reason
    chunk_node.gate_confidence = gate_confidence

    if extra_mention_entity_id is not None:
        graph.add_mentions_edge(chunk_node, graph.entities[extra_mention_entity_id])

    new_entity_ids = []
    for raw in extract_entities(chunk_result.text):
        canonical_id, type_guess, _ = resolver.resolve(raw, context_text=chunk_result.text)
        entity_node, entity_is_new = graph.upsert_entity(canonical_id, type_guess, turn)
        graph.add_mentions_edge(chunk_node, entity_node)
        if entity_is_new:
            entity_node.parent = chunk_node.id
            frontier.push(ENTITY, canonical_id, parent=chunk_node.id)
            new_entity_ids.append(canonical_id)

    frontier.push(CHUNK, chunk_node.id, parent=parent_label)

    if log is not None:
        log.accept(chunk_result.source_system, chunk_result.doc_id, accept_reason or gate_reason, new_entity_ids)

    return chunk_node


def seed_entities(
    question: str, graph: Graph, resolver: EntityResolver, frontier: FrontierQueue, log: RunLog | None = None
) -> None:
    """Turn 0a: entities extracted from the question text itself."""
    for raw in extract_entities(question):
        canonical_id, type_guess, _ = resolver.resolve(raw, context_text=question)
        entity_node, entity_is_new = graph.upsert_entity(canonical_id, type_guess, turn=0)
        if entity_is_new:
            entity_node.parent = QUESTION_PARENT_LABEL
            if log is not None:
                log.seed_entity(canonical_id, type_guess)
        graph.add_relation_edge(question, canonical_id, "MENTIONED_IN_QUESTION")
        frontier.push(ENTITY, canonical_id, parent=QUESTION_PARENT_LABEL)


def seed_chunks(
    question: str,
    graph: Graph,
    resolver: EntityResolver,
    frontier: FrontierQueue,
    budget: CallBudget,
    question_node: EntityNode,
    log: RunLog | None = None,
) -> None:
    """Turn 0b: broad semantic search on the raw question text, accepted
    unconditionally. Each seed chunk is also pushed to the FIFO as a future
    chunk-pop.

    Gating this step (via the same relevance gate every other pop type
    uses) was tried and reverted 2026-08-11: it did eliminate excluded-doc
    pickups from seed, but on genuinely broad/vague questions with no
    concrete entity anchor (e.g. "what's been discussed in recent team
    meetings?") the gate collapsed to rejecting nearly everything rather
    than selectively keeping topical content, producing an empty "no
    information found" answer that threw away real value a baseline
    still captured. Net effect was case-dependent, not a clean win.
    Reverted rather than tuned further for now; the excluded-doc problem is
    tracked separately (Excl.hit metric) rather than solved at this
    layer."""
    for chunk_result in dispatch_seed_search(question, budget):
        chunk_node = graph.add_chunk_node(chunk_result, turn=0, parent_label=QUESTION_PARENT_LABEL)
        graph.add_mentions_edge(chunk_node, question_node)

        n_entities = 0
        for raw in extract_entities(chunk_result.text):
            canonical_id, type_guess, _ = resolver.resolve(raw, context_text=chunk_result.text)
            entity_node, entity_is_new = graph.upsert_entity(canonical_id, type_guess, turn=0)
            graph.add_mentions_edge(chunk_node, entity_node)
            graph.add_relation_edge(question, canonical_id, "MENTIONED_IN_QUESTION")
            n_entities += 1
            if entity_is_new:
                entity_node.parent = chunk_node.id
                frontier.push(ENTITY, canonical_id, parent=chunk_node.id)

        frontier.push(CHUNK, chunk_node.id, parent=QUESTION_PARENT_LABEL)
        if log is not None:
            log.seed_chunk(chunk_result.source_system, chunk_result.doc_id, n_entities)


def process_entity_pop(
    entity_id: str,
    graph: Graph,
    resolver: EntityResolver,
    frontier: FrontierQueue,
    dedup: ChunkDedupPolicy,
    gate: RelevanceGate,
    budget: CallBudget,
    question: str,
    turn: int,
    log: RunLog | None = None,
) -> None:
    """No LLM extraction call here -- the entity was already extracted and
    canonicalized when it was discovered.

    As of 2026-08-11, NO entity-pop match auto-accepts -- text matches and
    metadata-only matches alike route through the same relevance gate
    chunk-pop uses (removed the earlier text-match auto-accept entirely).
    That auto-accept path was a real, confirmed noise source: a candidate
    that mechanically contains the searched entity can still be a "hub"
    document -- e.g. a survey doc that name-checks many real service names
    in passing -- with no coherent connection to the actual investigation
    thread, and the old mechanical-only check had no way to tell the
    difference. `entity_pop_accepts()`'s mechanical text/metadata/none
    classification still runs first as a free pre-filter -- only its
    routing changed, not the classification itself: a non-match is still
    rejected for free, with no gate call spent on it.

    Text and metadata-only matches are kept as separate gate batches (not
    merged into one) so each batch's synthetic parent_text can honestly
    describe how that group of candidates was actually found -- body text
    vs. a header-field-only citation are different strength priors, and
    the gate is told which one it's looking at."""
    entity = graph.entities[entity_id]
    is_id_lead = entity.type in ("TicketID", "CommitOrPR")
    aliases = resolver.aliases_for(entity_id) | {entity_id}

    all_results = dispatch_search(entity_id, is_id_lead, budget)
    if log is not None:
        log.search_results(sum(len(v) for v in all_results.values()))

    text_matches: list[ChunkResult] = []
    metadata_only: list[ChunkResult] = []

    for chunk_results in all_results.values():
        for chunk_result in chunk_results:
            related_ids = json.loads(chunk_result.metadata.get("explicit_related_ids") or "[]")
            match_kind = entity_pop_accepts(chunk_result.text, aliases, related_ids)
            if match_kind == ENTITY_MATCH_NONE:
                if log is not None:
                    log.reject(chunk_result.source_system, chunk_result.doc_id, "does not contain the searched entity")
                continue

            dedup_result = dedup.classify(chunk_result)
            if dedup_result.outcome in (DedupOutcome.EXACT_CONVERGENCE, DedupOutcome.NEAR_DUP):
                graph.note_discovered_via(dedup_result.existing_chunk_id, entity_id)
                graph.add_mentions_edge(graph.chunks[dedup_result.existing_chunk_id], entity)
                if log is not None:
                    log.merge(
                        chunk_result.source_system,
                        chunk_result.doc_id,
                        dedup_result.existing_chunk_id,
                        dedup_result.outcome.value,
                    )
                continue

            if match_kind == ENTITY_MATCH_METADATA:
                metadata_only.append(chunk_result)
            else:
                text_matches.append(chunk_result)

    if not text_matches and not metadata_only:
        return

    path_chain = build_path(graph, ENTITY, entity_id)
    path_summary = format_path(graph, path_chain)
    path_entities = path_entity_ids(path_chain)

    if text_matches:
        # A false negative on an unambiguous ID-cited connection (PROJ-415
        # explicitly citing its parent incident INC1229) was first traced
        # to the gate lacking a way to tell a deliberate ID citation from
        # incidental keyword overlap -- an "is_id_lead" branch giving ID
        # matches a distinct, stronger label was tried here and DID NOT
        # fix it (3/3 rejections on direct retest with the real code path).
        # The actual cause turned out to be the gate's tool schema itself
        # (see v2/relevance_gate.py's module docstring): a schema
        # that only lists accepted candidates lets rejection happen by
        # silent omission, with no justification required, while
        # inclusion requires one -- an asymmetry that biased toward
        # under-accepting regardless of label wording. Fixed at the
        # schema level (v4: explicit accept/reject decision per
        # candidate), which resolved it with the PLAIN generic label too
        # (confirmed: 3/3 accepts, same content, no special ID framing) --
        # so the ID-lead branch was removed again as unneeded complexity
        # once the real fix was confirmed sufficient on its own.
        parent_text = (
            f"(entity lead '{entity_id}' -- candidates below contain this entity literally in their own "
            f"body text)"
        )
        gate_candidates = [
            GateCandidate(chunk_id=c.chunk_id, text=c.text, overlap_note=_overlap_note(c.text, path_entities, resolver))
            for c in text_matches
        ]
        accepted = gate.evaluate(question, path_summary, parent_text, gate_candidates)
        if log is not None:
            log.gate_batch(len(text_matches), len(accepted))
        for chunk_result in text_matches:
            acceptance = accepted.get(chunk_result.chunk_id)
            if acceptance is None:
                if log is not None:
                    log.reject(chunk_result.source_system, chunk_result.doc_id, "relevance gate rejected (text match)")
                continue
            accept_chunk(
                graph,
                resolver,
                frontier,
                chunk_result,
                turn,
                parent_label=entity_id,
                extra_mention_entity_id=entity_id,
                log=log,
                gate_reason=acceptance.reason,
                gate_confidence=acceptance.confidence,
            )

    if not metadata_only:
        return

    # Metadata-only matches skip the gate entirely and are accepted
    # unconditionally. This was not the original design -- these used to
    # go through the same gate as text matches above, with a hint that
    # the citation was metadata-only. Testing against confirmed genuine
    # connections (a source document explicitly citing another record as
    # related, in its own structured metadata) found the gate rejecting
    # them with factually wrong "no connection" reasoning, on clean,
    # non-truncated calls -- a real comprehension limit on this candidate
    # type specifically, not a wording problem (three different prompt
    # framings were tried and failed identically). The source document
    # has already asserted the relationship by citing it explicitly, so
    # no second LLM judgment is required. Text matches (above) remain
    # fully gated -- this exception is scoped narrowly to citations the
    # source itself declared, not incidental keyword overlap.
    for chunk_result in metadata_only:
        accept_chunk(
            graph,
            resolver,
            frontier,
            chunk_result,
            turn,
            parent_label=entity_id,
            extra_mention_entity_id=entity_id,
            log=log,
            gate_reason=f"auto-accepted: source document explicitly cites '{entity_id}' as a related ID in its own metadata (no gate call)",
            gate_confidence="n/a (auto-accepted)",
        )


def process_chunk_pop(
    chunk_id: str,
    graph: Graph,
    resolver: EntityResolver,
    frontier: FrontierQueue,
    dedup: ChunkDedupPolicy,
    gate: RelevanceGate,
    budget: CallBudget,
    question: str,
    turn: int,
    log: RunLog | None = None,
) -> None:
    """esg_algorithm_v2.md section 5. Dedup runs first and mechanically,
    against every candidate from this one search; only non-duplicate
    survivors reach the single batched LLM relevance call for this event."""
    chunk_node = graph.chunks[chunk_id]

    all_candidates = [
        chunk_result
        for chunk_results in dispatch_search(chunk_node.text, is_id_lead=False, budget=budget).values()
        for chunk_result in chunk_results
    ]
    if log is not None:
        log.search_results(len(all_candidates))

    survivors: list[ChunkResult] = []
    for candidate in all_candidates:
        dedup_result = dedup.classify(candidate)
        if dedup_result.outcome in (DedupOutcome.EXACT_CONVERGENCE, DedupOutcome.NEAR_DUP):
            graph.note_discovered_via(dedup_result.existing_chunk_id, chunk_id)
            graph.add_chunk_link(chunk_id, dedup_result.existing_chunk_id)
            if log is not None:
                log.merge(candidate.source_system, candidate.doc_id, dedup_result.existing_chunk_id, dedup_result.outcome.value)
            continue
        survivors.append(candidate)

    if not survivors:
        return

    path_chain = build_path(graph, CHUNK, chunk_id)
    path_summary = format_path(graph, path_chain)
    path_entities = path_entity_ids(path_chain)

    gate_candidates = [
        GateCandidate(
            chunk_id=c.chunk_id,
            text=c.text,
            overlap_note=_overlap_note(c.text, path_entities, resolver),
        )
        for c in survivors
    ]
    accepted = gate.evaluate(question, path_summary, chunk_node.text, gate_candidates)
    if log is not None:
        log.gate_batch(len(survivors), len(accepted))

    for candidate in survivors:
        acceptance = accepted.get(candidate.chunk_id)
        if acceptance is None:
            if log is not None:
                log.reject(candidate.source_system, candidate.doc_id, "relevance gate rejected")
            continue  # gate rejected -- never added, not discarded later
        new_node = accept_chunk(
            graph,
            resolver,
            frontier,
            candidate,
            turn,
            parent_label=chunk_id,
            gate_reason=acceptance.reason,
            gate_confidence=acceptance.confidence,
            log=log,
        )
        graph.add_chunk_link(chunk_id, new_node.id)


def _overlap_note(candidate_text: str, path_entities: list[str], resolver: EntityResolver) -> str:
    shared = shared_path_entities(candidate_text, path_entities, resolver.aliases_for)
    if shared:
        return f"shares named entities with the path so far: {', '.join(shared)}"
    return "shares NO named entity with anything in the path so far"


def run(
    question: str, log: RunLog | None = None
) -> tuple[dict, str, "cost_tracker.CostMetrics", str]:
    """Pass `log=RunLog(...)` for a turn-by-turn record (see v2/run_log.py
    and main_v2.py).

    For live progress visibility (accept/reject/merge decisions and a
    running graph-size tally, printed as they happen -- no LLM call, no
    added cost), pass `log=RunLog(question=question, echo=True)`. Plain
    `RunLog(question=question)` (echo defaults to False) still captures
    the full trace for `.write()`, just silently -- that's what
    compare_case_audit.py and multi_run_consolidation.py use."""
    cost_tracker.start_tracking()
    graph = Graph()
    resolver = EntityResolver()
    frontier = FrontierQueue()

    entity_budget = CallBudget(config.V2_PER_SYSTEM_ENTITY_SEARCH_BUDGET, config.SOURCE_SYSTEMS)
    chunk_budget = CallBudget(config.V2_PER_SYSTEM_CHUNK_SEARCH_BUDGET, config.SOURCE_SYSTEMS)
    entity_caps = RunCaps(config.V2_ENTITY_CAP, config.V2_CAP_OVERFLOW_FRACTION)
    chunk_caps = RunCaps(config.V2_CHUNK_CAP, config.V2_CAP_OVERFLOW_FRACTION)
    dedup = ChunkDedupPolicy(graph)
    gate = RelevanceGate()

    question_node, _ = graph.upsert_entity(question, "Question", turn=0)
    seed_entities(question, graph, resolver, frontier, log=log)
    seed_chunks(question, graph, resolver, frontier, chunk_budget, question_node, log=log)
    if log is not None:
        log.seed_summary(len(graph.entities), len(graph.chunks))

    entities_processed = 0
    chunks_processed = 0
    turn = 0
    stop_reason = "frontier exhausted (no more leads to follow)"

    while True:
        stop, reason = should_stop(
            frontier, entities_processed, chunks_processed, entity_caps, chunk_caps, entity_budget, chunk_budget
        )
        if stop:
            stop_reason = reason
            break

        turn += 1
        item = frontier.pop()
        if log is not None:
            log.start_turn(turn, item.kind, item.ref_id, item.parent, len(frontier))

        if item.kind == ENTITY:
            entities_processed += 1
            process_entity_pop(item.ref_id, graph, resolver, frontier, dedup, gate, entity_budget, question, turn, log=log)
        else:
            chunks_processed += 1
            process_chunk_pop(item.ref_id, graph, resolver, frontier, dedup, gate, chunk_budget, question, turn, log=log)

        if log is not None:
            log.end_turn(len(graph.chunks), len(graph.entities), len(frontier))

    final_snapshot = graph.snapshot()
    final_report = compose_final_report(question, final_snapshot, stop_reason)
    cost = cost_tracker.stop_tracking()

    if log is not None:
        log.final(stop_reason, final_snapshot, cost, final_report)

    return final_snapshot, final_report, cost, stop_reason
