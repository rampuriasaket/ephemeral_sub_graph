"""Single shared FIFO for both entities and chunks: no priority scoring,
no tiers -- popped strictly in discovery order, so nothing is ever
deprioritized or starved.

Kept dependency-free (no graph.py, no config.py import) so it's trivially
unit-testable on its own.
"""

from collections import deque
from dataclasses import dataclass

ENTITY = "entity"
CHUNK = "chunk"


@dataclass(frozen=True)
class FrontierItem:
    kind: str  # ENTITY or CHUNK
    ref_id: str
    parent: str


class FrontierQueue:
    def __init__(self):
        self._queue: deque[FrontierItem] = deque()
        self._queued: set[tuple[str, str]] = set()
        self._visited: set[tuple[str, str]] = set()

    def push(self, kind: str, ref_id: str, parent: str) -> bool:
        """False if this (kind, ref_id) is already visited or already
        queued -- every item enters the frontier at most once per run."""
        key = (kind, ref_id)
        if key in self._visited or key in self._queued:
            return False
        self._queue.append(FrontierItem(kind, ref_id, parent))
        self._queued.add(key)
        return True

    def pop(self) -> FrontierItem:
        item = self._queue.popleft()
        key = (item.kind, item.ref_id)
        self._queued.discard(key)
        self._visited.add(key)
        return item

    def is_empty(self) -> bool:
        return not self._queue

    def count_kind(self, kind: str) -> int:
        return sum(1 for item in self._queue if item.kind == kind)

    def __len__(self) -> int:
        return len(self._queue)
