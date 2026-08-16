"""One-question-one-document audit reports: for a given gold case, runs
flat-RAG / 2-hop / ESG(v2), and writes a single self-contained markdown
file with full metrics, ESG's complete turn-by-turn graph evolution log,
and the full (non-truncated) final answer from all three systems side by
side -- built for manual audit, not just aggregate scoring.

Also records every run into run_history.py and checks for a declining
trend across the case's last several runs (recall primarily, precision
secondarily -- see run_history.py). A flagged trend is surfaced in the
file itself and returned to the caller so a batch runner can pause instead
of continuing to spend on a case that's degrading.

    python compare_case_audit.py <case_number> "<question>"
"""

import sys
from pathlib import Path

import baseline_flat_rag
import llm_router
import run_history
import two_hop_rag
from gold_set import GOLD_SET
from scorer import score_run
from v2 import discovery_loop_v2
from v2.run_log import RunLog

AUDIT_DIR = Path(__file__).parent.parent / "results" / "case_audits"

_VERDICT_SYSTEM_PROMPT = """You are judging whether an experimental \
retrieval system's (ESG) final answer is WORSE, SAME, or BETTER than the \
best of two baseline systems' (flat-RAG, 2-hop) final answers to the same \
question, for the same reader.

You are given the question, the set of documents a human grader has \
confirmed are the correct/expected sources for a full answer, and (if any) \
documents known to be irrelevant distractors, plus all three systems' full \
answer text.

Judge on what a reader would actually learn or decide from the answer, \
grounded against the expected/excluded documents -- not on retrieval \
scores, verbosity, or formatting:
- BETTER: ESG's answer captures material facts grounded in the expected \
  documents that the best baseline answer misses or hedges away from \
  incorrectly (e.g. baseline says "not enough information" but the \
  expected documents do contain the answer, and ESG's answer surfaces it \
  correctly) -- WITHOUT asserting anything as settled fact that isn't \
  actually supported by the expected documents.
- SAME: both convey materially the same facts and the same degree of \
  confidence/hedging; differences are cosmetic (wording, structure, extra \
  citations that don't change what the reader learns).
- WORSE: ESG's answer states something as confident fact that the \
  expected/excluded documents don't actually support, omits material facts \
  the best baseline correctly includes, or is confidently wrong in any way \
  -- this outweighs any extra completeness ESG might otherwise offer. A \
  confidently wrong claim always makes the verdict WORSE regardless of \
  anything else ESG got right.

Be strict about confidence-calibration: correctly hedging on missing \
information is not a flaw, and it should never on its own be judged WORSE \
than a baseline that also hedges. Only judge ESG WORSE for a hedge if the \
expected documents show the answer was actually available and ESG failed \
to surface it while a baseline did.

You are also given each system's full list of actually-retrieved document \
IDs, separate from the gold expected/excluded lists. Use this to tell apart \
two different things that both look like "an answer cites something not in \
the expected set":
- TRUE FABRICATION: the cited document ID does not appear anywhere in that \
  system's own retrieved-documents list. The system invented a source it \
  never actually found. This is always a serious flaw and alone justifies \
  WORSE.
- UNLABELED-BUT-REAL: the cited ID DOES appear in that system's own \
  retrieved-documents list -- it's a real document that was actually \
  retrieved, just not one the gold set happened to list as expected. This \
  is NOT fabrication or invention, and must not be described that way. \
  Judge it on the same terms as any other citation (does what the answer \
  claims about it plausibly relate to the question); it is fine to note \
  the gold set may not capture every legitimately relevant document, but \
  that is a gold-set completeness question, not a system defect."""


def _judge_verdict(
    question: str,
    gold,
    flat_answer: str,
    two_hop_answer: str,
    esg_answer: str,
    flat_doc_ids,
    two_hop_doc_ids,
    esg_doc_ids,
) -> dict:
    user_content = (
        f"Question: {question}\n\n"
        f"Expected (correct) source documents: {', '.join(gold.expected_doc_ids) or '(none)'}\n"
        f"Known irrelevant/distractor documents: {', '.join(gold.excluded_doc_ids) or '(none)'}\n\n"
        f"=== flat-RAG ===\n"
        f"Retrieved documents: {', '.join(sorted(flat_doc_ids)) or '(none)'}\n"
        f"Answer: {flat_answer}\n\n"
        f"=== 2-hop ===\n"
        f"Retrieved documents: {', '.join(sorted(two_hop_doc_ids)) or '(none)'}\n"
        f"Answer: {two_hop_answer}\n\n"
        f"=== ESG (v2) ===\n"
        f"Retrieved documents: {', '.join(sorted(esg_doc_ids)) or '(none)'}\n"
        f"Answer: {esg_answer}\n"
    )
    result = llm_router.call_tool(
        task="verdict",
        system_prompt=_VERDICT_SYSTEM_PROMPT,
        user_content=user_content,
        tool_name="record_verdict",
        tool_description="Record the worse/same/better verdict and reasoning for ESG's answer vs. the best baseline.",
        input_schema={
            "type": "object",
            "properties": {
                # `reasoning` is deliberately listed (and required) before
                # `verdict` -- models tend to fill tool-call fields in
                # schema order, so this forces the reasoning to be worked
                # out first instead of being rationalized after the verdict
                # is already committed. Fixed 2026-08-11 after two cases
                # (#19, #30) recorded a "worse" verdict whose own reasoning
                # text argued for "same".
                "reasoning": {
                    "type": "string",
                    "description": "Work through the comparison first: what does each answer actually claim, and is it grounded in the expected/excluded documents? Conclude with 2-4 sentences.",
                },
                "verdict": {"type": "string", "enum": ["worse", "same", "better"]},
            },
            "required": ["reasoning", "verdict"],
        },
        max_tokens=4096,
    )
    if not result or result.get("verdict") not in ("worse", "same", "better"):
        # Defensive against a malformed/partial fallback response (e.g. a
        # provider overload -- 529 -- forcing a fallback model whose output
        # didn't include a usable "verdict" field) -- `if not result` alone
        # only catches a fully-empty dict, not a partially-populated one
        # missing just this field, which crashed a real run with a raw
        # KeyError instead of degrading gracefully.
        return {"verdict": "unknown", "reasoning": result.get("reasoning") or "(verdict call failed/unavailable)"}
    return result


def _slugify(text: str, max_len: int = 50) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len] or "question"


def run_case_audit(
    case_number: int,
    question: str,
    audit_dir: Path = AUDIT_DIR,
    history_path: Path = run_history.DEFAULT_HISTORY_PATH,
) -> dict:
    gold = next((g for g in GOLD_SET if g.question == question), None)
    if gold is None:
        raise SystemExit(f"Question not found in GOLD_SET: {question!r}")

    flat_result = baseline_flat_rag.run_flat_rag(question)
    flat_score = score_run(flat_result.retrieved_doc_ids, flat_result.answer_text, gold, flat_result.cost)

    two_hop_result = two_hop_rag.run_two_hop_rag(question)
    two_hop_score = score_run(two_hop_result.retrieved_doc_ids, two_hop_result.answer_text, gold, two_hop_result.cost)

    log = RunLog(question=question)
    esg_snapshot, esg_answer, esg_cost, stop_reason = discovery_loop_v2.run(question, log=log)
    esg_doc_ids = {node["doc_id"] for node in esg_snapshot["chunks"].values()}
    esg_score = score_run(esg_doc_ids, esg_answer, gold, esg_cost)

    run_history.record(question, "flat_rag", flat_score.recall, flat_score.precision, flat_result.cost.cost_usd, history_path=history_path)
    run_history.record(question, "two_hop", two_hop_score.recall, two_hop_score.precision, two_hop_result.cost.cost_usd, history_path=history_path)
    run_history.record(question, "esg_v2", esg_score.recall, esg_score.precision, esg_cost.cost_usd, history_path=history_path)

    trend = run_history.check_trend(question, "esg_v2", history_path=history_path)

    verdict = _judge_verdict(
        question,
        gold,
        flat_result.answer_text,
        two_hop_result.answer_text,
        esg_answer,
        flat_result.retrieved_doc_ids,
        two_hop_result.retrieved_doc_ids,
        esg_doc_ids,
    )

    _write_audit_file(
        case_number=case_number,
        gold=gold,
        flat_result=flat_result,
        flat_score=flat_score,
        two_hop_result=two_hop_result,
        two_hop_score=two_hop_score,
        esg_answer=esg_answer,
        esg_score=esg_score,
        esg_cost=esg_cost,
        esg_doc_ids=esg_doc_ids,
        stop_reason=stop_reason,
        run_log=log,
        trend=trend,
        verdict=verdict,
        audit_dir=audit_dir,
    )

    return {
        "question": question,
        "flat_score": flat_score,
        "two_hop_score": two_hop_score,
        "esg_score": esg_score,
        "trend": trend,
        "verdict": verdict,
        "excl_hits": {
            "flat-RAG": flat_score.excluded_hits,
            "2-hop": two_hop_score.excluded_hits,
            "ESG (v2)": esg_score.excluded_hits,
        },
    }


def _fmt_metrics_row(system: str, score, cost) -> str:
    excl_hit = "TRUE" if score.excluded_hits else "false"
    return (
        f"| {system} | {score.recall:.2f} | {score.precision:.2f} | {excl_hit} | {cost.total_tokens} "
        f"| ${cost.cost_usd:.4f} | {cost.wall_clock_seconds:.1f}s |"
    )


def _write_audit_file(
    case_number,
    gold,
    flat_result,
    flat_score,
    two_hop_result,
    two_hop_score,
    esg_answer,
    esg_score,
    esg_cost,
    esg_doc_ids,
    stop_reason,
    run_log,
    trend,
    verdict,
    audit_dir: Path = AUDIT_DIR,
):
    lines = []
    lines.append(f"# Case {case_number:02d}: {gold.question}")
    lines.append("")
    lines.append(f"**Expected docs:** {', '.join(gold.expected_doc_ids) or '(none)'}")
    lines.append(f"**Excluded docs:** {', '.join(gold.excluded_doc_ids) or '(none)'}")
    lines.append("")

    lines.append("## Verdict: ESG (v2) vs. best baseline")
    lines.append("")
    lines.append(f"**{verdict['verdict'].upper()}** -- {verdict['reasoning']}")
    lines.append("")

    lines.append("## Degradation check")
    lines.append("")
    if trend["flagged"]:
        lines.append(f"🚩 **FLAGGED** -- {trend['metric']} declining over last {len(trend['values'])} runs: {trend['values']}")
    else:
        lines.append(f"No declining trend. {trend['reason']}.")
    lines.append("")

    lines.append("## Metrics")
    lines.append("")
    lines.append("| System | Recall | Precision | Excl.hit | Tokens | Cost | Time |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(_fmt_metrics_row("flat-RAG", flat_score, flat_result.cost))
    lines.append(_fmt_metrics_row("2-hop", two_hop_score, two_hop_result.cost))
    lines.append(_fmt_metrics_row("ESG (v2)", esg_score, esg_cost))
    lines.append("")
    for label, score in (("flat-RAG", flat_score), ("2-hop", two_hop_score), ("ESG (v2)", esg_score)):
        if score.excluded_hits:
            lines.append(f"**Excl.hit ({label}):** {score.excluded_hits} -- pulled in doc(s) explicitly marked wrong for this question.")
    if flat_score.excluded_hits or two_hop_score.excluded_hits or esg_score.excluded_hits:
        lines.append("")
    lines.append(f"ESG retrieved doc_ids: {sorted(esg_doc_ids)}")
    lines.append(f"ESG stop reason: {stop_reason}")
    lines.append("")

    lines.append("## ESG (v2) -- full turn-by-turn graph evolution")
    lines.append("")
    lines.append("```")
    lines.append(run_log.render())
    lines.append("```")
    lines.append("")

    lines.append("## Final answers, side by side")
    lines.append("")
    lines.append("### flat-RAG")
    lines.append("")
    lines.append(flat_result.answer_text)
    lines.append("")
    lines.append("### 2-hop")
    lines.append("")
    lines.append(two_hop_result.answer_text)
    lines.append("")
    lines.append("### ESG (v2)")
    lines.append("")
    lines.append(esg_answer)
    lines.append("")

    audit_dir.mkdir(parents=True, exist_ok=True)
    path = audit_dir / f"case_{case_number:02d}_{_slugify(gold.question)}.md"
    path.write_text("\n".join(lines))
    print(f"Written: {path}")


def run_batch(
    cases: list[tuple[int, str]],
    audit_dir: Path = AUDIT_DIR,
    history_path: Path = run_history.DEFAULT_HISTORY_PATH,
) -> None:
    """Runs cases in order; stops immediately (does not run the rest) if
    any case's ESG trend check flags a decline. Prints exactly which case
    and why, so this can be resumed manually after review rather than
    silently burning through the remaining cases on a degrading run."""
    for case_number, question in cases:
        print(f"--- Case {case_number:02d}: {question}")
        result = run_case_audit(case_number, question, audit_dir=audit_dir, history_path=history_path)
        print(f"    verdict: {result['verdict']['verdict'].upper()}")
        for system, hits in result["excl_hits"].items():
            if hits:
                print(f"    ⚠️  Excl.hit ({system}): {hits}")
        trend = result["trend"]
        if trend["flagged"]:
            print(
                f"\n🚩 PAUSED at case {case_number:02d} ({question!r}): "
                f"{trend['metric']} declining over last {len(trend['values'])} runs: {trend['values']}"
            )
            print("Remaining cases in this batch were not run.")
            return
    print(f"\nBatch complete, {len(cases)} case(s), no degradation flagged.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Usage: python compare_case_audit.py <case_number> "<question>"')
    run_case_audit(int(sys.argv[1]), sys.argv[2])
