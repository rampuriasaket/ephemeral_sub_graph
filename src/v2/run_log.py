"""Turn-by-turn, human-readable record of one discovery run.

Built entirely from mechanical state already available at each decision
point (what was popped, what a search returned, why something was
accepted/rejected/merged) plus the relevance gate's own one-line reason
(already generated for free as part of acceptance -- see
v2/relevance_gate.py). Deliberately adds NO new LLM calls: this is a
formatting/bookkeeping layer over decisions the loop is already making,
not a second narration pass. If a prose, LLM-written narrative (like
narrator.py's summarize_progress, currently unused) is wanted later, it's
a separate, explicit cost decision -- not bundled in here.

Usage: construct one RunLog per run, pass it into discovery_loop_v2.run()
as `log=`, then call .render() (or .write(path)) once the run finishes.
Every method is a no-op-safe append -- callers that don't want logging
just don't pass a RunLog at all (discovery_loop_v2's functions all default
log=None and skip every call site).

Pass `echo=True` to also print each accept/reject/merge/gate-batch line to
stdout as it happens, not just capture it for the eventual .write() -- for
main_v2.py's single-question CLI, where a multi-minute silent run is worse
than some noise. Batch callers (multi_run_consolidation.py,
compare_case_audit.py) don't pass it, so their output is unaffected. The
final assessment (`final()`) is deliberately never echoed -- main_v2.py
already prints its own stop-reason/cost/report summary after run()
returns, so echoing it too would just duplicate that output.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RunLog:
    question: str
    echo: bool = False
    lines: list[str] = field(default_factory=list)
    _start_time: float = field(default_factory=time.time, repr=False)

    def _emit(self, line: str) -> None:
        self.lines.append(line)
        if self.echo:
            print(line)

    def __post_init__(self):
        self._emit("=" * 72)
        self._emit("ESG v2 discovery run")
        self._emit(f"Question: {self.question}")
        self._emit(time.strftime("Started: %Y-%m-%d %H:%M:%S"))
        self._emit("=" * 72)

    # --- Turn 0: seeding ---

    def seed_entity(self, entity_id: str, type_guess: str) -> None:
        self._emit(f"[seed] entity from question text: '{entity_id}' ({type_guess})")

    def seed_chunk(self, source_system: str, doc_id: str, n_entities: int) -> None:
        self._emit(
            f"[seed] chunk accepted unconditionally: {source_system}:{doc_id} "
            f"({n_entities} entities extracted)"
        )

    def seed_summary(self, n_entities: int, n_chunks: int) -> None:
        self._emit(f"[seed] done -- {n_entities} entities, {n_chunks} chunks queued for turn 1+")
        self._emit("")

    # --- per-turn pop events ---

    def start_turn(self, turn: int, kind: str, ref_id: str, parent: str, frontier_remaining: int) -> None:
        self._emit(f"--- Turn {turn}: pop {kind} '{ref_id}' (discovered via: {parent}) ---")
        self._emit(f"    frontier had {frontier_remaining} other item(s) waiting")

    def search_results(self, n_candidates: int) -> None:
        if n_candidates == 0:
            self._emit("    search returned nothing")
        else:
            self._emit(f"    search returned {n_candidates} candidate(s)")

    def reject(self, source_system: str, doc_id: str, reason: str) -> None:
        self._emit(f"    x  rejected {source_system}:{doc_id} -- {reason}")

    def merge(self, source_system: str, doc_id: str, existing_doc_id: str, outcome: str) -> None:
        self._emit(
            f"    ~  {source_system}:{doc_id} merged into existing {existing_doc_id} ({outcome}, no new node)"
        )

    def accept(self, source_system: str, doc_id: str, reason: str, new_entities: list[str]) -> None:
        self._emit(f"    +  accepted {source_system}:{doc_id} -- {reason}")
        if new_entities:
            self._emit(f"       new entities queued: {', '.join(new_entities)}")

    def gate_batch(self, n_survivors: int, n_accepted: int) -> None:
        self._emit(
            f"    relevance gate judged {n_survivors} non-duplicate candidate(s): "
            f"{n_accepted} accepted, {n_survivors - n_accepted} rejected"
        )

    def end_turn(self, n_chunks: int | None = None, n_entities: int | None = None, frontier_remaining: int | None = None) -> None:
        if n_chunks is not None:
            self._emit(f"    -> graph so far: {n_chunks} chunks, {n_entities} entities -- frontier: {frontier_remaining} left")
        self._emit("")

    # --- final assessment ---

    def final(self, stop_reason: str, snapshot: dict, cost, report: str) -> None:
        # Not echoed -- main_v2.py prints its own stop-reason/cost/report
        # summary after run() returns, so echoing here would duplicate it.
        self.lines.append("=" * 72)
        self.lines.append("FINAL ASSESSMENT")
        self.lines.append("=" * 72)
        self.lines.append(f"Stop reason: {stop_reason}")
        self.lines.append(
            f"Graph: {len(snapshot['chunks'])} chunks, {len(snapshot['entities'])} entities, "
            f"{len(snapshot['mentions_edges'])} mentions edges, {len(snapshot['relation_edges'])} relation edges, "
            f"{len(snapshot.get('chunk_links', []))} chunk links"
        )
        systems = sorted({node["source_system"] for node in snapshot["chunks"].values()})
        self.lines.append(f"Systems contributed: {', '.join(systems) if systems else '(none)'}")
        if cost is not None:
            self.lines.append(
                f"Cost: {cost.llm_calls} LLM calls, {cost.retrieval_calls} retrieval calls, "
                f"{cost.total_tokens} tokens ({cost.input_tokens} in / {cost.output_tokens} out), "
                f"{cost.wall_clock_seconds:.1f}s wall clock"
            )
        self.lines.append("")
        self.lines.append("--- Final report ---")
        self.lines.append(report)

    # --- output ---

    def render(self) -> str:
        return "\n".join(self.lines)

    def write(self, path: "str | Path") -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render())
        return path
