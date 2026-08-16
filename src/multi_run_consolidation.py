"""Multi-run consolidation per results/multi_run_consolidation_prompt.md.

Runs every gold case through all 3 systems for ONE run (run_N), stores
structured per-case JSON (the reproducibility record), and generates
Output A (internal diagnostic, full per-run detail) and Output B
(paper-ready aggregated table). For a single run, cross-run stability
fields are honestly marked as not-yet-available rather than faked.

    python multi_run_consolidation.py <run_number>
"""

import json
import sys
from pathlib import Path

import baseline_flat_rag
import two_hop_rag
from compare_case_audit import _judge_verdict
from gold_set import GOLD_SET
from scorer import score_run
from v2 import discovery_loop_v2


def _system_record(name: str, score, cost, retrieved_doc_ids, stop_reason: str) -> dict:
    return {
        "system": name,
        "recall": score.recall,
        "precision": score.precision,
        "excl_hit": bool(score.excluded_hits),
        "excl_hit_docs": score.excluded_hits,
        "fabrication": bool(score.ungrounded_citations),
        "fabrication_docs": score.ungrounded_citations,
        "retrieved_doc_ids": sorted(retrieved_doc_ids),
        "retrieval_calls": cost.retrieval_calls,
        "llm_calls": cost.llm_calls,
        "tokens": cost.total_tokens,
        "cost_usd": cost.cost_usd,
        "time_sec": cost.wall_clock_seconds,
        "stop_reason": stop_reason,
    }


def run_one_case(case_number: int, question: str, run_dir: Path) -> dict:
    gold = next(g for g in GOLD_SET if g.question == question)

    flat_result = baseline_flat_rag.run_flat_rag(question)
    flat_score = score_run(flat_result.retrieved_doc_ids, flat_result.answer_text, gold, flat_result.cost)

    two_hop_result = two_hop_rag.run_two_hop_rag(question)
    two_hop_score = score_run(two_hop_result.retrieved_doc_ids, two_hop_result.answer_text, gold, two_hop_result.cost)

    esg_snapshot, esg_answer, esg_cost, stop_reason = discovery_loop_v2.run(question)
    esg_doc_ids = {node["doc_id"] for node in esg_snapshot["chunks"].values()}
    esg_score = score_run(esg_doc_ids, esg_answer, gold, esg_cost)

    verdict = _judge_verdict(
        question, gold, flat_result.answer_text, two_hop_result.answer_text, esg_answer,
        flat_result.retrieved_doc_ids, two_hop_result.retrieved_doc_ids, esg_doc_ids,
    )

    record = {
        "case_number": case_number,
        "question": question,
        "expected_doc_ids": gold.expected_doc_ids,
        "excluded_doc_ids": gold.excluded_doc_ids,
        "systems": [
            _system_record("flat-RAG", flat_score, flat_result.cost, flat_result.retrieved_doc_ids, "single-pass (no traversal)"),
            _system_record("2-hop", two_hop_score, two_hop_result.cost, two_hop_result.retrieved_doc_ids, "single-pass, one follow-up hop"),
            _system_record("ESG (v2)", esg_score, esg_cost, esg_doc_ids, stop_reason),
        ],
        "answers": {
            "flat-RAG": flat_result.answer_text,
            "2-hop": two_hop_result.answer_text,
            "ESG (v2)": esg_answer,
        },
        "verdict": verdict["verdict"],
        "verdict_reasoning": verdict["reasoning"],
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"case_{case_number:02d}.json").write_text(json.dumps(record, indent=2))
    print(f"--- Case {case_number:02d}: {question}")
    print(f"    verdict: {verdict['verdict'].upper()}"
          + (" | EXCL.HIT" if any(s["excl_hit"] for s in record["systems"]) else "")
          + (" | FABRICATION" if any(s["fabrication"] for s in record["systems"]) else ""))
    return record


def run_all(run_number: int) -> list[dict]:
    run_dir = Path(__file__).parent.parent / "results" / f"run_{run_number}"
    records = []
    for i, gold in enumerate(GOLD_SET, 1):
        record = run_one_case(i, gold.question, run_dir)
        records.append(record)
    return records


def _fmt_pct(x: float) -> str:
    return f"{x:.2f}"


def write_output_a(records: list[dict], run_number: int) -> Path:
    run_dir = Path(__file__).parent.parent / "results" / f"run_{run_number}"
    lines = []
    lines.append(f"# Output A -- internal diagnostic report (run_{run_number} only)")
    lines.append("")
    lines.append(
        "**Single-run data.** Stability fields (STABLE/UNSTABLE, mean+/-spread) "
        "require run_2 and run_3 to be meaningful -- not faked here, left as "
        "'N/A (single run)' throughout. Re-run this generator once run_2/run_3 "
        "exist to fill them in."
    )
    lines.append("")

    excl_hits = [(r["case_number"], s["system"], s["excl_hit_docs"]) for r in records for s in r["systems"] if s["excl_hit"]]
    fabrications = [(r["case_number"], s["system"], s["fabrication_docs"]) for r in records for s in r["systems"] if s["fabrication"]]
    verdict_tally = {}
    for r in records:
        verdict_tally[r["verdict"]] = verdict_tally.get(r["verdict"], 0) + 1

    lines.append("## Aggregate summary")
    lines.append("")
    lines.append(f"Verdict tally (run_{run_number}): " + ", ".join(f"{v}: {c}" for v, c in sorted(verdict_tally.items())))
    lines.append("Verdict stability: N/A (single run) -- requires run_2/run_3.")
    lines.append("")
    lines.append(f"**Excl.hit occurrences ({len(excl_hits)} total):**")
    if excl_hits:
        for case_num, system, docs in excl_hits:
            lines.append(f"- Case {case_num:02d}, {system}: {docs}")
    else:
        lines.append("- None found.")
    lines.append("")
    lines.append(f"**Fabrication occurrences ({len(fabrications)} total):**")
    if fabrications:
        for case_num, system, docs in fabrications:
            lines.append(f"- Case {case_num:02d}, {system}: cited but not retrieved: {docs}")
    else:
        lines.append("- None found.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for r in records:
        lines.append(f"## Case {r['case_number']:02d}: {r['question']}")
        lines.append(f"Expected docs: {r['expected_doc_ids']}")
        lines.append(f"Excluded docs: {r['excluded_doc_ids']}")
        lines.append("")
        lines.append("| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for s in r["systems"]:
            lines.append(
                f"| {s['system']} | 1 | {_fmt_pct(s['recall'])} | {_fmt_pct(s['precision'])} | "
                f"{'TRUE' if s['excl_hit'] else 'false'} | {'TRUE' if s['fabrication'] else 'false'} | "
                f"{s['tokens']} | ${s['cost_usd']:.4f} | {s['time_sec']:.1f}s | {s['stop_reason']} |"
            )
        lines.append("")
        lines.append(f"Verdict run 1: **{r['verdict'].upper()}** -- {r['verdict_reasoning']}")
        lines.append("Stability: N/A (single run)")
        lines.append("")

    path = run_dir / "output_a_diagnostic.md"
    path.write_text("\n".join(lines))
    return path


def write_output_b(records: list[dict], run_number: int) -> Path:
    run_dir = Path(__file__).parent.parent / "results" / f"run_{run_number}"
    systems = ["flat-RAG", "2-hop", "ESG (v2)"]
    lines = []
    lines.append(f"# Output B -- paper-ready summary table (run_{run_number} only, not yet averaged over 3 runs)")
    lines.append("")
    lines.append(
        "**Note:** this is a single run. The build spec calls for averaging "
        "over 3 runs per system; that requires run_2/run_3. Reported here as "
        "run_1 point values, not means -- do not present as a stable mean in "
        "the paper without run_2/run_3."
    )
    lines.append("")
    lines.append("| System | Recall | Precision | Tokens | Cost | Time (s) | Excl.hit rate | Fabrication rate |")
    lines.append("|---|---|---|---|---|---|---|---|")

    total_cost = 0.0
    total_time = 0.0
    for sysname in systems:
        rows = [s for r in records for s in r["systems"] if s["system"] == sysname]
        n = len(rows)
        mean_recall = sum(x["recall"] for x in rows) / n
        mean_precision = sum(x["precision"] for x in rows) / n
        mean_tokens = sum(x["tokens"] for x in rows) / n
        mean_cost = sum(x["cost_usd"] for x in rows) / n
        mean_time = sum(x["time_sec"] for x in rows) / n
        excl_rate = sum(1 for x in rows if x["excl_hit"]) / n
        fab_rate = sum(1 for x in rows if x["fabrication"]) / n
        total_cost += sum(x["cost_usd"] for x in rows)
        total_time += sum(x["time_sec"] for x in rows)
        lines.append(
            f"| {sysname} | {mean_recall:.2f} | {mean_precision:.2f} | {mean_tokens:.0f} | "
            f"${mean_cost:.4f} | {mean_time:.1f} | {excl_rate:.0%} | {fab_rate:.0%} |"
        )

    lines.append("")
    lines.append(f"Total experiment cost (run_{run_number}, {len(records)} questions x 3 systems): ${total_cost:.2f}")
    lines.append(f"Total wall-clock time (run_{run_number}, sum across all calls): {total_time:.0f}s (~{total_time/60:.1f} min)")

    path = run_dir / "output_b_paper_table.md"
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    run_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    records = run_all(run_number)
    a_path = write_output_a(records, run_number)
    b_path = write_output_b(records, run_number)
    print(f"\nWritten: {a_path}")
    print(f"Written: {b_path}")
