"""Per-system call budget, one instance per lane: entity-search calls and
chunk-content-search calls are tracked separately, so one mechanism's cost
can't silently starve the other's budget. The discovery loop creates two
CallBudget instances -- one for entity-pop searches, one for chunk-pop
searches -- rather than this class knowing about lanes itself, keeping
each instance simple and independently testable.
"""


class CallBudget:
    def __init__(self, per_system_budget: int, systems: list[str]):
        self.per_system_budget = per_system_budget
        self._calls: dict[str, int] = {s: 0 for s in systems}

    def can_call(self, source_system: str) -> bool:
        return self._calls.get(source_system, 0) < self.per_system_budget

    def record_call(self, source_system: str) -> None:
        self._calls[source_system] = self._calls.get(source_system, 0) + 1

    def calls_made(self, source_system: str) -> int:
        return self._calls.get(source_system, 0)

    def exhausted(self) -> bool:
        """True once every system tracked by this budget has hit its limit."""
        return all(count >= self.per_system_budget for count in self._calls.values())
