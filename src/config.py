"""All tunable constants for ESG in one place."""

from pathlib import Path

# --- Retrieval thresholds ---
TOP_K_PER_SEARCH = 5           # max chunks retrieved per system per query
MAX_SEARCH_DISTANCE = 1.4      # relevance cutoff (Chroma L2 distance) for
                                # entity-pop's exact/plain-text search. With
                                # only ~12-14 docs per collection, top_k alone
                                # always returns close to a third of the
                                # whole collection regardless of actual
                                # relevance. Tried tightening 1.5 -> 1.4 ->
                                # 1.3: 1.3 was a step too far -- it excluded
                                # a genuine match (bare single-word queries
                                # like "checkout" score worse even against
                                # their true best hit than longer/richer
                                # queries do). Settled on 1.4 as the best
                                # trade-off found: keeps every validated true
                                # positive tested, at the cost of one
                                # documented false positive.

SEED_SEARCH_MARGIN = 0.2       # relative cutoff for the initial broad seed
                                # search on the raw question text: keep only
                                # results within this margin of the single
                                # BEST distance found anywhere across all
                                # systems, instead of a flat threshold.
                                # Reason: the seed step has no downstream
                                # connectivity check (everything it finds is
                                # accepted), so MAX_SEARCH_DISTANCE alone
                                # isn't enough -- a generic question like
                                # "was there an incident about disk usage?"
                                # has exactly one real match (distance 1.03)
                                # but nearly the entire corpus sits at
                                # 1.2-1.5 (shared incident-report
                                # boilerplate), well inside
                                # MAX_SEARCH_DISTANCE=1.4. A genuinely broad
                                # question ("was there any outage recently?")
                                # instead has several different real matches
                                # clustered close to its own best distance --
                                # margin=0.2 empirically distinguishes both
                                # cases correctly (verified: isolates the one
                                # real disk-usage incident; keeps ~9 distinct
                                # real incidents for the broad outage
                                # question; keeps exactly the ~4-5 real
                                # auth-service docs with zero noise).

# --- Chunk matching threshold ---
# (entity-alias resolution is LLM-judged, not threshold-based -- see
# entity_resolution.py's module docstring for why)
CHUNK_DEDUP_THRESHOLD = 0.90   # chunk-level near-duplicate match

# --- Source systems ---
SOURCE_SYSTEMS = ["servicenow", "jira", "gitrepo", "confluence", "slack"]

# --- Storage ---
# __file__-relative (not cwd-relative) so this resolves to the project
# root's chroma_db/ regardless of where a script is invoked from.
# Regenerable from scratch via `python ingest.py` if it's ever missing or
# the corpus changes.
CHROMA_PERSIST_DIR = str(Path(__file__).parent.parent / "chroma_db")

# --- LLM ---
ANTHROPIC_MODEL = "claude-sonnet-5"
ENTITY_EXTRACTION_MAX_TOKENS = 1024
NARRATOR_MAX_TOKENS = 1024
FINAL_REPORT_MAX_TOKENS = 2048
# The relevance gate judges every candidate from a chunk-pop event in one
# batched call, and large batches (20+ candidates, each needing a full
# reason sentence and confidence label) can exceed a smaller budget and
# get silently cut off mid-response -- the caller has no way to tell a
# truncated response from a clean one, so every candidate in a truncated
# batch defaults to rejected without ever actually being judged. Set 3x
# higher than the original budget after confirming that failure mode
# directly (checked actual API response metadata on affected calls).
RELEVANCE_GATE_MAX_TOKENS = 768 * 3

# --- Multi-model routing (see llm_router.py) ---
# Provider identifiers used throughout llm_router.py and cost_tracker.py.
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GOOGLE = "google"

MODEL_CLAUDE_SONNET = "claude-sonnet-5"
MODEL_CLAUDE_HAIKU = "claude-haiku-4-5-20251001"
MODEL_GEMINI_FLASH_LITE = "gemini-3.5-flash-lite"

# $ per million tokens, verified against provider pricing pages 2026-08-10.
# Gemini models with "thinking" output (not gemini-3.5-flash-lite) bill
# thinking tokens at the same output rate but report them in a separate
# usage field -- llm_router.py accounts for this explicitly, see its
# module docstring.
LLM_PRICING = {
    MODEL_CLAUDE_SONNET: {"input": 2.00, "output": 10.00},
    MODEL_CLAUDE_HAIKU: {"input": 1.00, "output": 5.00},
    MODEL_GEMINI_FLASH_LITE: {"input": 0.30, "output": 2.50},
}

# Each task's fallback chain, tried in order until one call succeeds.
# Locked 2026-08-10 based on direct provider/model comparisons:
# - entity_extraction: Haiku matched Sonnet exactly on structured text in
#   testing; highest call volume, so the biggest cost lever.
# - entity_resolution: moved to Sonnet primary 2026-08-11 after a dedicated
#   comparison found a real, confirmed gap -- given a real Slack-message
#   context that triggered it, Haiku merged a generic mention ("checkout")
#   into a specific existing entity ("checkout screen") despite a sharpened
#   prompt; Sonnet correctly did not, same prompt, same input. This is the
#   step that makes a global, hard-to-undo aliasing decision (the alias
#   becomes usable by entity-pop's mechanical text-match anywhere in the
#   corpus, not just in the context it was coined in), and it's much lower
#   call volume than extraction, so the cost trade favors correctness here.
# - narrator: moved to Sonnet primary 2026-08-11 -- the cost-first choice
#   above was flagged at design time as "revisit if report quality
#   regresses," and it did: two cases showed confidently-wrong final
#   answers (asserting an issue was ongoing when the graph only supported
#   a resolved past incident; presenting an explicit gold-set distractor
#   as legitimate content) traced directly to the narrator's synthesis,
#   not to retrieval/gating (the gate had already made the right call in
#   both cases). Isolated test -- same graph state, only the narrator's
#   model forced to Sonnet -- fixed both. Narrator runs on every progress
#   update plus the final report, so this is a real, accepted cost
#   increase (~4-6x vs. Gemini Flash Lite) for calibration -- correctness
#   on confidence framing wins the trade here, same reasoning as
#   entity_resolution's move.
# - relevance_gate: stays on Sonnet primary -- this is the exact mechanism
#   hardened against precision failures during development; not swapped
#   without dedicated testing.
LLM_TASK_MODELS = {
    "entity_extraction": [
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_HAIKU),
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_SONNET),
        (PROVIDER_GOOGLE, MODEL_GEMINI_FLASH_LITE),
    ],
    "entity_resolution": [
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_SONNET),
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_HAIKU),
        (PROVIDER_GOOGLE, MODEL_GEMINI_FLASH_LITE),
    ],
    "narrator": [
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_SONNET),
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_HAIKU),
        (PROVIDER_GOOGLE, MODEL_GEMINI_FLASH_LITE),
    ],
    "relevance_gate": [
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_SONNET),
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_HAIKU),
        (PROVIDER_GOOGLE, MODEL_GEMINI_FLASH_LITE),
    ],
    # verdict: one-shot per-case judgment (compare_case_audit.py) of whether
    # ESG's final answer is worse/same/better than the best baseline answer,
    # grounded against the gold expected/excluded docs. Sonnet primary --
    # same reasoning as entity_resolution: a real judgment call, very low
    # call volume (1 per case), so correctness wins the cost trade.
    "verdict": [
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_SONNET),
        (PROVIDER_ANTHROPIC, MODEL_CLAUDE_HAIKU),
        (PROVIDER_GOOGLE, MODEL_GEMINI_FLASH_LITE),
    ],
}

# --- Discovery loop budgets and caps ---
V2_ENTITY_CAP = 20             # max entity-pops processed per run
V2_CHUNK_CAP = 20              # max chunk-pops processed per run
V2_CAP_OVERFLOW_FRACTION = 0.25  # one-time-only bump (20 -> 25) if the
                                  # frontier still holds more than the base
                                  # cap of that same kind when the cap is
                                  # first hit. Never re-fires, so this can
                                  # only delay a stop, not remove it as a
                                  # backstop.
V2_PER_SYSTEM_ENTITY_SEARCH_BUDGET = 15   # default -- not yet tuned against data
V2_PER_SYSTEM_CHUNK_SEARCH_BUDGET = 15    # default -- not yet tuned against data

# A per-entity-pop fanout threshold (gate only entities whose search results
# exceed a candidate-count threshold) was tried and abandoned during
# development: tested on a real case, precision barely moved because the
# actual noise source entered via a LOW-fanout pop (2 accepts out of 11
# candidates) -- fanout-per-pop-event doesn't predict this failure mode.
# Replaced by routing ALL entity-pop matches through the relevance gate
# unconditionally (see v2/discovery_loop_v2.py's process_entity_pop) rather
# than trying to guess which ones need it.
