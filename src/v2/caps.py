"""Hard per-kind processing cap with a single one-time bump (locked
2026-08-09, see esg_algorithm_v2.md section 8's "Proposed, not yet
confirmed" item -- now confirmed).

Mechanism: allow up to `base_cap` items of a kind to be processed. If the
cap is hit while the frontier still holds MORE than `base_cap` items of that
same kind -- real backlog, not noise -- grant one extension to
`base_cap * (1 + overflow_fraction)` and continue. The bump can only fire
once per instance, so this stays a hard backstop: it can delay a stop, never
remove it. If it re-fired indefinitely on every hit, it would stop being a
cap at all.
"""


class RunCaps:
    def __init__(self, base_cap: int, overflow_fraction: float):
        self.base_cap = base_cap
        self.overflow_fraction = overflow_fraction
        self.effective_cap = base_cap
        self.bumped = False

    def should_stop(self, processed_count: int, backlog_count: int) -> tuple[bool, str]:
        if processed_count < self.effective_cap:
            return False, ""

        if not self.bumped and backlog_count > self.base_cap:
            self.bumped = True
            self.effective_cap = int(self.base_cap * (1 + self.overflow_fraction))
            return False, ""

        return True, (
            f"reached processing cap ({processed_count}/{self.effective_cap}"
            f"{', one-time bump used' if self.bumped else ''})"
        )
