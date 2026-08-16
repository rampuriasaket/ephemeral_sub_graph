"""CLI entrypoint for v2, run on demand, one question at a time.

    python main_v2.py "why did auth-service go down?"

Prints every pop/search/accept/reject/merge decision live as it happens
(no LLM call, no added cost -- just visibility into an otherwise-silent
multi-minute run), then the final answer. The same trace is also written
in full to results/runs/<timestamp>-<question-slug>.log -- see
v2/run_log.py for exactly what it captures. No graph_view browser
visualization yet; that's v1-only for now (see discovery_loop_v2.run's
docstring).
"""

import re
import sys
import time
from pathlib import Path

from v2 import discovery_loop_v2
from v2.run_log import RunLog

RUNS_DIR = Path(__file__).parent.parent / "results" / "runs"


def _slugify(text: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len] or "question"


def main():
    if len(sys.argv) < 2:
        print('Usage: python main_v2.py "<question>"')
        sys.exit(1)

    question = sys.argv[1]
    print(f'Question: "{question}"')
    print("Running v2 discovery loop...")

    log = RunLog(question=question, echo=True)
    snapshot, report, cost, stop_reason = discovery_loop_v2.run(question, log=log)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = log.write(RUNS_DIR / f"{timestamp}-{_slugify(question)}.log")

    print(f"\nStop reason: {stop_reason}")
    print(f"Graph: {len(snapshot['chunks'])} chunks, {len(snapshot['entities'])} entities")
    print(
        f"Cost: {cost.llm_calls} LLM calls, {cost.retrieval_calls} retrieval calls, "
        f"{cost.total_tokens} tokens, {cost.wall_clock_seconds:.1f}s"
    )
    print(f"Detailed log written to: {log_path}")
    print("\n=== FINAL REPORT ===")
    print(report)


if __name__ == "__main__":
    main()
