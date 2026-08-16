"""Lightweight cost accounting, shared by ESG and the flat-RAG baseline so
the comparison's cost numbers come from one measurement, not two separately
hand-rolled counters.

record_llm_call takes explicit (input_tokens, output_tokens, cost_usd,
provider, model) rather than a provider-specific usage object -- this
became necessary once calls could be served by either Anthropic or Google
(see llm_router.py), whose usage objects have different shapes. Every LLM
call site (via llm_router.py, or directly for the flat-RAG/2-hop baselines,
which intentionally stay on a fixed model for a controlled comparison) is
responsible for computing its own token counts and cost before reporting in.

Uses a single "current tracker" active for the duration of one run
(discovery_loop.run() or baseline_flat_rag.run_flat_rag()). Thread-safe,
since discovery_loop dispatches parallel searches across threads.
"""

import threading
import time


class CostMetrics:
    def __init__(self):
        self.retrieval_calls = 0
        self.llm_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0
        self.calls_by_model: dict[str, int] = {}
        self.fallback_count = 0  # how many calls needed a non-primary model
        self.wall_clock_seconds = 0.0
        self._start_time = time.time()
        self._lock = threading.Lock()

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def record_llm_call(
        self,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        provider: str,
        model: str,
        fell_back: bool = False,
    ) -> None:
        with self._lock:
            self.llm_calls += 1
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            self.cost_usd += cost_usd
            self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1
            if fell_back:
                self.fallback_count += 1

    def record_retrieval_call(self) -> None:
        with self._lock:
            self.retrieval_calls += 1

    def finalize(self) -> "CostMetrics":
        self.wall_clock_seconds = time.time() - self._start_time
        return self

    def __repr__(self) -> str:
        model_breakdown = ", ".join(f"{m}: {c}" for m, c in sorted(self.calls_by_model.items()))
        return (
            f"CostMetrics(retrieval_calls={self.retrieval_calls}, llm_calls={self.llm_calls}, "
            f"input_tokens={self.input_tokens}, output_tokens={self.output_tokens}, "
            f"cost_usd={self.cost_usd:.6f}, fallback_count={self.fallback_count}, "
            f"calls_by_model=[{model_breakdown}], wall_clock_seconds={self.wall_clock_seconds:.2f})"
        )


_current: CostMetrics | None = None
_current_lock = threading.Lock()


def start_tracking() -> CostMetrics:
    """Begin a new tracking scope. Call once at the start of a run."""
    global _current
    metrics = CostMetrics()
    with _current_lock:
        _current = metrics
    return metrics


def stop_tracking() -> CostMetrics:
    """End the current tracking scope, finalize wall-clock time, return it."""
    global _current
    with _current_lock:
        metrics = _current
        _current = None
    if metrics is not None:
        metrics.finalize()
    return metrics


def record_llm_call(
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    provider: str,
    model: str,
    fell_back: bool = False,
) -> None:
    if _current is not None:
        _current.record_llm_call(input_tokens, output_tokens, cost_usd, provider, model, fell_back)


def record_retrieval_call() -> None:
    if _current is not None:
        _current.record_retrieval_call()
