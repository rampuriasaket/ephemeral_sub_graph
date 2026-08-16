"""Overall stop signal for the v2 loop -- four independent conditions, any
one of which ends the run. Kept as a standalone function (not inlined into
the loop) so each condition is testable on its own via small stubs, without
spinning up a real FrontierQueue/RunCaps/CallBudget.

Duck-typed on purpose:
  frontier:      .is_empty() -> bool, .count_kind(kind) -> int
  entity_caps / chunk_caps: .should_stop(processed, backlog) -> (bool, str)
  entity_budget / chunk_budget: .exhausted() -> bool
"""

ENTITY = "entity"
CHUNK = "chunk"


def should_stop(
    frontier,
    entities_processed: int,
    chunks_processed: int,
    entity_caps,
    chunk_caps,
    entity_budget,
    chunk_budget,
) -> tuple[bool, str]:
    if frontier.is_empty():
        return True, "frontier exhausted (no more leads to follow)"

    stop, reason = entity_caps.should_stop(entities_processed, frontier.count_kind(ENTITY))
    if stop:
        return True, reason

    stop, reason = chunk_caps.should_stop(chunks_processed, frontier.count_kind(CHUNK))
    if stop:
        return True, reason

    if entity_budget.exhausted() and chunk_budget.exhausted():
        return True, "per-system call budgets exhausted for every source (entity + chunk)"

    return False, "continuing"
