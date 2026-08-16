# Ephemeral Subgraph Generation (ESG)

Root-cause and status questions in a real engineering org are rarely answered by one system.
"Why did auth-service go down, and is it related to anything we changed recently?" usually means
manually checking an incident tracker, a ticketing system, a code host, a documentation wiki, and
team chat, by hand, noticing when one system's record references an identifier from another.

**Ephemeral Subgraph Generation (ESG)** answers a question like that by building a small,
correct knowledge graph *for that one question, on the fly*, and discarding it once answered.
Given a question, it seeds itself from the question text, then repeatedly pops the next
discovered entity or chunk off a queue, searches for it across every connected system
(ServiceNow, Jira, a Git host, Confluence, Slack, in this project's corpus), passes genuine
candidates through an LLM relevance gate, and stops once a bounded exit condition is met. Nothing
is persisted across questions — no ontology to maintain, no staleness, no standing index.

Evaluated against two cheaper baselines (single-shot retrieval, and a fixed two-hop
identifier-chasing method) across a 35-question gold set, three independent runs each. Full
results are in `results/` (see "Where things are," below). For a plain-English explanation of
the traversal strategy itself, see [`ALGORITHM.md`](ALGORITHM.md).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your own keys
```

`.env` needs:
```
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

The vector database (`chroma_db/`) is already built and committed, so you can ask a question
immediately after setup with no ingestion step. If you ever need to rebuild it from the raw
corpus in `data/` (e.g. after editing the corpus), run this from the project root:

```bash
python src/ingest.py
```

All commands below are run from the project root, not from inside `src/` — every script resolves
`data/`, `chroma_db/`, and `results/` relative to its own location, one level up from `src/`.

## Ask a single question

```bash
python src/main_v2.py "why did auth-service go down?"
```

Prints one status line per turn as it goes (what was searched, what got accepted or rejected and
why, a running chunk/entity count) followed by the final answer. Also writes the full trace to
`results/runs/<timestamp>-<question-slug>.log`.

**Sample questions to try** (pulled verbatim from `src/gold_set.py`'s 35-question evaluation
set, so they're guaranteed to have real, checkable answers in `data/`, not made up):

```bash
python src/main_v2.py "why did auth-service go down?"
python src/main_v2.py "are transactional emails like password resets being delayed right now?"
python src/main_v2.py "what's the latest on the TLS certificate expiring for the billing API?"
python src/main_v2.py "Why weren't Gmail users getting password reset emails?"
python src/main_v2.py "did a recent feature flag change cause errors for customers?"
```

## Run the full evaluation

Runs all 35 gold-set questions against all 3 systems (flat-RAG, two-hop, and ESG):

```bash
python src/multi_run_consolidation.py 1
```

The argument is a run number — it writes structured per-case JSON plus two summary reports to
`results/run_<N>/` (`output_a_diagnostic.md`, full per-case detail; `output_b_paper_table.md`,
the aggregated table). ESG's LLM-driven steps are stochastic, so a single run is a legitimate data
point but not a stable one on its own — `results/run_1/2/3` already contain three independent runs
for exactly this reason.

This is a real evaluation (105 system-runs: 35 questions × 3 systems) and will make that many LLM
calls — expect it to take a few hours and cost around $20, most of it from ESG's own traversal
(see `results/run_1/output_b_paper_table.md` for actual cost/time figures).

For a single-case deep-dive with full turn-by-turn gate reasoning captured (useful for debugging
one question in detail, rather than a full 35-question pass) — takes a gold-set case number and
its exact question text:

```bash
python src/compare_case_audit.py 1 "why did auth-service go down?"
```

Writes a detailed markdown audit to `results/case_audits/`, including every gate accept/reject
decision and its stated reasoning.

## Run the tests

`tests/` lives alongside `src/`, so point Python at `src/` for imports to resolve:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

97 tests, no API keys or network access needed — pure unit tests over the traversal logic
(dedup, budget/cap enforcement, path building, relevance gate plumbing, run logging).

## Where things are

- `src/` — all code.
  - `src/v2/` — the ESG traversal algorithm itself (frontier queue, entity/chunk discovery,
    dedup, relevance gate, exit conditions).
  - `src/config.py` — every tunable knob lives here, nothing hardcoded elsewhere: search
    caps and per-system budgets (how much a run does before it stops), retrieval thresholds,
    model routing per task, and which corpus systems are searched. Each is commented in place
    with what it controls and, where relevant, why that value was chosen.
  - `src/gold_set.py` — the 35-question evaluation set (question, expected docs, excluded docs).
  - `src/baseline_flat_rag.py`, `src/two_hop_rag.py` — the two comparison systems.
  - `src/scorer.py` — recall, precision, excluded-hit, and fabrication scoring, used during
    evaluation runs.
  - `src/fabrication_scorer_v2.py` — a more precise fabrication check for re-analyzing already-run
    results: a cited ID counts as fabricated only if it's absent from both the retrieved-doc-ID
    list *and* the body text of every retrieved chunk, catching legitimate cross-references
    `scorer.py` alone would flag as false positives.
- `tests/` — unit tests, sibling to `src/` (see "Run the tests" above for why `PYTHONPATH=src`
  is needed).
- `data/` — the synthetic 5-system corpus (ServiceNow, Jira, Git, Confluence, Slack).
- `chroma_db/` — the built vector store over that corpus.
- `results/` — the three independent full evaluation runs (`run_1/2/3`) behind the headline
  numbers: structured per-case JSON plus each run's `output_a_diagnostic.md` (full detail) and
  `output_b_paper_table.md` (aggregated table).
- `ALGORITHM.md` — plain-English explanation of the traversal strategy: how the queue, the
  entity/chunk search, the relevance gate, and the exit conditions fit together, and why a few
  of the less obvious design choices are the way they are.
