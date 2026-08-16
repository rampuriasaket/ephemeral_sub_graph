"""Persistent, append-only history of every case run's key metrics, plus a
trend check across a case's recent runs.

Exists because a single before/after comparison isn't reliable evidence of
a real regression -- confirmed empirically this build (see
results/regression_full_8.md's case #2: three consecutive runs of the
identical question, identical code, came back at precision 0.12, 0.11,
then completely clean). This lets a batch runner look at a *trend* across
a case's last several runs instead of reacting to any single one.
"""

import json
import time
from pathlib import Path

DEFAULT_HISTORY_PATH = Path(__file__).parent.parent / "results" / "run_history.json"
WINDOW = 5


def _load(history_path: Path) -> dict[str, list[dict]]:
    if not history_path.exists():
        return {}
    return json.loads(history_path.read_text())


def _save(history: dict[str, list[dict]], history_path: Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2))


def _key(question: str, system: str) -> str:
    return f"{question}::{system}"


def record(
    question: str,
    system: str,
    recall: float,
    precision: float,
    cost_usd: float,
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> None:
    history = _load(history_path)
    history.setdefault(_key(question, system), []).append(
        {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "recall": recall,
            "precision": precision,
            "cost_usd": cost_usd,
        }
    )
    _save(history, history_path)


def _is_declining(values: list[float]) -> bool:
    """True if `values` (chronological) show a declining trend: the last
    value is below the first, and at most one step in the sequence goes
    up (one noise blip tolerated; a consistent decline otherwise)."""
    if len(values) < 3:
        return False
    if values[-1] >= values[0]:
        return False
    increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
    return increases <= 1


def check_trend(
    question: str,
    system: str = "esg_v2",
    window: int = WINDOW,
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> dict:
    """Recall is checked first (primary signal, per the project's own
    "recall must not diminish" bar) -- only checks precision if recall
    isn't the one declining, so a flagged trend always names one clear
    culprit metric, not both at once."""
    history = _load(history_path)
    runs = history.get(_key(question, system), [])[-window:]

    if len(runs) < 3:
        return {"flagged": False, "metric": None, "values": [], "reason": "not enough history yet"}

    recalls = [r["recall"] for r in runs]
    precisions = [r["precision"] for r in runs]

    if _is_declining(recalls):
        return {
            "flagged": True,
            "metric": "recall",
            "values": recalls,
            "reason": f"recall declining over last {len(runs)} runs: {recalls}",
        }
    if _is_declining(precisions):
        return {
            "flagged": True,
            "metric": "precision",
            "values": precisions,
            "reason": f"precision declining over last {len(runs)} runs: {precisions}",
        }
    return {"flagged": False, "metric": None, "values": recalls, "reason": "no declining trend"}
