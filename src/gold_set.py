"""Hand-labeled gold set for scoring ESG against flat-RAG and two-hop.

Every doc_id below was checked directly against the ingested Chroma
collections, not guessed from memory. expected_doc_ids are real
*documents* (chunk doc_ids), not entity names -- a soft-link entity like
"inventory-service" that has no document of its own belongs in
expected_facts, not here.
"""

from dataclasses import dataclass, field


@dataclass
class GoldCase:
    question: str
    expected_doc_ids: list[str]
    excluded_doc_ids: list[str] = field(default_factory=list)
    expected_facts: list[str] = field(default_factory=list)


GOLD_SET: list[GoldCase] = [
    # --- The three original test questions from build_phase_1.md ---
    GoldCase(
        question="why did auth-service go down?",
        expected_doc_ids=[
            "INC1042",
            "PROJ-201",
            "PR-455",
            "auth-service-outage-postmortem-august-2026",
            "eng-platform-2026-08-08",  # added 2026-08-12, staleness audit: same
            # incident, Slack thread added in the 5-system expansion after this
            # case was originally written -- cross-validated, already the
            # expected 5th doc on case 20 ("What happened with the login
            # outage?") which asks about this identical incident.
        ],
        excluded_doc_ids=[
            "new-hire-onboarding-engineering-wiki-home",
            "incident-response-process-standard-operating-procedure",
        ],
        expected_facts=[
            "root cause was an expired JWT signing key that was not rotated ahead of its expiry window",
            "the key was rotated manually to restore service",
            "PR-455 added automated expiry alerting",
        ],
    ),
    GoldCase(
        question="what's going on with the payment gateway timeouts?",
        expected_doc_ids=[
            "INC1055",
            "PROJ-215",
            "payment-gateway-troubleshooting-guide",
            "INC1101",  # added 2026-08-14, second correction pass: corpus-exhaustive
            "PR-601",  # check (all 154 docs x 3 runs) found these legitimately
            "PR-745",  # retrieved and grounded on this question across all 3 runs,
            "PROJ-301",  # never on excluded_doc_ids -- same correction criterion as
            "checkout-idempotency-design-doc",  # cases 01/06/09/11/12 (corpus
            "incident-response-2026-08-09",  # content, not observed-output-driven).
            # See results/followup.md.
        ],
        excluded_doc_ids=[],  # no PR exists for this -- a fabricated one would fail the grounding check instead
        expected_facts=[
            "root cause is unconfirmed, connection pool exhaustion is only suspected",
            "no fix has been merged yet",
        ],
    ),
    GoldCase(
        question="checkout latency during the flash sale",
        expected_doc_ids=["INC1082", "PROJ-260"],
        excluded_doc_ids=["new-hire-onboarding-engineering-wiki-home"],
        expected_facts=[
            "checkout p95 latency rose from approximately 400ms to over 6 seconds",
            "early findings point to lock contention in inventory-service during concurrent stock-decrement operations",
        ],
    ),
    # --- Soft, non-ID-based connection ---
    GoldCase(
        question=(
            "I am hearing some partners complaining about delays in push "
            "notification to their apps. what do we know?"
        ),
        expected_doc_ids=[
            "INC1070",
            "PROJ-244",
            "PR-481",
            "notification-service-architecture",
        ],
        excluded_doc_ids=["new-hire-onboarding-engineering-wiki-home"],
        expected_facts=[
            "notification-worker consumers are falling behind incoming message volume",
            "no message loss, only delay",
            "a draft PR (PR-481) increasing worker concurrency is not yet merged",
        ],
    ),
    # --- Should find almost nothing (no related tickets/docs at all) ---
    GoldCase(
        question="what's the latest on the TLS certificate expiring for the billing API?",
        expected_doc_ids=["INC1090"],
        excluded_doc_ids=["api-rate-limiting-guide"],  # plausible false-positive: both mention "API"
        expected_facts=[
            "certificate expires in 14 days",
            "no customer impact",
            "no related tickets or documentation exist yet",
        ],
    ),
    # --- Zero-shared-ID connections: candidate docs are linked only by a
    # shared component name / narrative, never by a ticket ID pointing from
    # one to the other. Whether these land as GOLD (only ESG gets full
    # recall) or turn out reachable by 1-hop semantic search anyway is an
    # empirical question -- deliberately not pre-labeled here, see
    # compare_tiers.py for how tier membership gets computed from measured
    # recall, not asserted in advance. ---
    GoldCase(
        question="order-service keeps having connection pool issues, what's actually being done about it?",
        expected_doc_ids=[
            "INC0980",
            "order-service-on-call-runbook",
            "PR-508",
            "order-platform-2026-08-07",  # added 2026-08-12, staleness audit:
            # same incident/topic, Slack thread added in the 5-system
            # expansion after this case was originally written --
            # cross-validated, already the expected 4th doc on case 22
            # ("Did the order-service pool issue come back?"), same
            # underlying pattern.
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "INC0980 (May 2026) was caused by a long-running batch reconciliation job holding database connections open",
            "the fix applied at the time was a manual, undocumented connection-pool-ceiling increase, not a permanent code fix",
            "PR-508 is an open draft proposing a permanent fix via connection pool size tuning, not yet merged and not linked to any tracked ticket",
        ],
    ),
    GoldCase(
        question="are there known issues with image uploads or thumbnail generation under load?",
        expected_doc_ids=["INC1155", "PR-545"],
        excluded_doc_ids=[],
        expected_facts=[
            "the resize worker has failed intermittently more than once during burst upload load, most recently INC1155",
            "each time it was resolved with a manual restart of the resize worker pool",
            "PR-545 adds retry-with-jitter as a proactive hardening fix, not tied to a specific incident ticket",
        ],
    ),
    GoldCase(
        question="partners have mentioned delayed webhook deliveries during traffic spikes, what's the status?",
        expected_doc_ids=["INC1160", "PROJ-320"],
        excluded_doc_ids=[],
        expected_facts=[
            "webhook-dispatcher-service has fallen behind more than once during a spike, most recently INC1160, delaying deliveries up to 20 minutes with no data loss",
            "the only mitigation today is manually scaling the worker pool",
            "PROJ-320 is a backlog task to build proper backpressure/dead-letter-queue handling, not yet scheduled or linked to a specific incident",
        ],
    ),
    # NOTE: originally INC1165 -- renumbered to INC1166 when the corpus was
    # regenerated for the 5-system expansion, since the new corpus reused
    # INC1165 for an unrelated incident (transactional email delivery
    # rate drop). Content otherwise unchanged.
    GoldCase(
        question="some users are reporting random logouts, do we know why?",
        expected_doc_ids=["INC1166", "PR-550"],
        excluded_doc_ids=[],
        expected_facts=[
            "root cause was session-store evicting active sessions early under memory pressure",
            "resolved by a manual cache flush and rebalance; this has happened before as a one-off each time",
            "PR-550 adds proactive memory-pressure alerting and eviction tuning to catch this before it affects users",
        ],
    ),
    GoldCase(
        question="did a recent feature flag change cause errors for customers?",
        expected_doc_ids=["INC1170", "PR-555"],
        excluded_doc_ids=[],
        expected_facts=[
            "a stale cached flag value in feature-flag-service's client cache caused HTTP 500s after a flag was disabled",
            "resolved via a manual cluster-wide cache flush",
            "PR-555 adds a TTL plus an explicit invalidation hook so a flag change propagates immediately, not tied to a specific ticket",
        ],
    ),
    GoldCase(
        question="are transactional emails like password resets being delayed right now?",
        expected_doc_ids=[
            "INC1175",
            "email-delivery-service-operational-runbook",
            "INC1165",  # added 2026-08-12, staleness audit: a second, genuinely
            "PROJ-340",  # relevant transactional-email issue -- unlike INC1175
            "eng-notifications-2026-08-08",  # (resolved, provider-side, same
            # day), INC1165 is explicitly UNRESOLVED/still under investigation
            # at the time of writing, and its own ticket names "password
            # resets" as an affected type. Given the question asks about
            # "right now," the currently-open issue plausibly belongs in a
            # complete answer more than the already-closed one alone --
            # moderate-high confidence, not a mechanical cross-reference like
            # the case 01/06 additions.
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "INC1175 traced a roughly 30 minute delay to a queue backlog on the third-party provider's side, not our own service",
            "the runbook says to check the provider-side queue-depth dashboard first, since this has happened before and usually resolves on its own",
            "separately, INC1165/PROJ-340 tracks an unresolved ~15% drop in transactional email delivery rate, still under investigation, not yet confirmed as a provider or internal issue",
        ],
    ),
    GoldCase(
        question="why did legitimate customers get rate-limited recently?",
        expected_doc_ids=["INC1180", "PR-560"],
        # 2026-08-12: INC1151/PROJ-330/PR-625/partner-eng-2026-08-09/
        # api-rate-limiting-guide were added then reverted same day. Only
        # "moderate confidence" in the original audit -- different specific
        # cause (partner-tier misprovisioning vs. a global config push) and
        # a narrower affected population (partner accounts vs. general
        # customers). A validation run's recall drop lined up with that
        # weaker confidence rather than looking like ordinary retrieval
        # noise, so reverted pending stronger evidence.
        excluded_doc_ids=[],
        expected_facts=[
            "a rate-limiter-service threshold change was pushed globally to all traffic at once and incorrectly throttled legitimate users",
            "resolved via a config rollback",
            "PR-560 adds a canary/gradual-rollout stage for future config changes to prevent a repeat",
        ],
    ),
    # --- Known-noise exclusion under a deliberately broad/vague question ---
    GoldCase(
        question="is there anything engineers should be aware of right now?",
        expected_doc_ids=[
            "INC1061",
            "eng-onboarding-2026-08-16",  # added 2026-08-14, second correction pass
            # -- see results/followup.md.
        ],
        excluded_doc_ids=[
            "new-hire-onboarding-engineering-wiki-home",
            "incident-response-process-standard-operating-procedure",
            "engineering-all-hands-notes-august-2026",  # renamed from ...july-2026 on corpus regen
            "PR-512",
            "PR-490",
        ],
        expected_facts=[],  # this case is about precision/exclusion, not fact recall -- deliberately left thin
    ),
    # =====================================================================
    # 5-system corpus expansion (added Slack). Every doc_id below was
    # checked directly against the ingested Chroma collections, same
    # discipline as the original set above. A case marked (retained)
    # already exists above and has no new entry here.
    # =====================================================================
    # --- Full chains, 5 systems ---
    GoldCase(
        question="Why were customers seeing double discounts at checkout?",
        expected_doc_ids=[
            "INC1201",
            "PROJ-401",
            "PR-701",
            "coupon-discount-validation-rules",
            "eng-checkout-2026-08-10",
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "root cause was coupon validation only checking for duplicate codes, not multiple distinct codes on the same order",
            "fixed by enforcing a single-coupon-per-order rule at validation, checked at cart-finalization time",
            "affected orders were being reviewed by finance separately",
        ],
    ),
    GoldCase(
        question="Why did the analytics dashboard show revenue below actual?",
        expected_doc_ids=["INC1208", "PROJ-405", "PR-705", "eng-data-2026-08-11"],
        excluded_doc_ids=[],
        expected_facts=[
            "dashboard revenue was ~20% below the payment processor's own numbers",
            "root cause was a join condition silently excluding orders that used a coupon code",
            "fixed by correcting the join logic; no indication of how long the bug had existed",
        ],
    ),
    GoldCase(
        question="Why weren't Gmail users getting password reset emails?",
        expected_doc_ids=["INC1215", "PROJ-410", "PR-710", "email-deliverability-runbook"],
        excluded_doc_ids=[],
        expected_facts=[
            "a recent sender-domain authentication change had not updated the DKIM record Gmail validates strictly against",
            "other providers are more lenient, so only Gmail users were affected",
            "fixed via a DNS record update plus a code change referencing the new record",
        ],
    ),
    GoldCase(
        question="Why is bulk export timing out for large accounts?",
        expected_doc_ids=["INC1250", "PROJ-430", "PR-715", "bulk-export-architecture", "eng-platform-2026-08-16"],
        excluded_doc_ids=[],
        expected_facts=[
            "export ran as a single synchronous request with no pagination, so large accounts exceeded the request timeout entirely rather than just running slowly",
            "fixed by reworking export to stream results in chunks",
        ],
    ),
    # --- Soft/non-ID connections (new deliberate pairs) ---
    GoldCase(
        question="Why is the iOS app crashing on the checkout screen?",
        expected_doc_ids=["INC1122", "mobile-eng-2026-08-05"],
        excluded_doc_ids=[],
        expected_facts=[
            "crash reports cluster around the checkout screen, with memory pressure building over the course of a session",
            "no Jira story has been opened yet -- mobile team is investigating informally",
            "suspected cause is the SDK's image cache not releasing thumbnails properly, not yet confirmed",
        ],
    ),
    GoldCase(
        question="Why don't the warehouse inventory counts match the system?",
        expected_doc_ids=["INC1137", "ops-warehouse-2026-08-02"],
        excluded_doc_ids=[],
        expected_facts=[
            "a routine warehouse audit found a discrepancy between system-recorded and physical counts for several SKUs",
            "not yet triaged, no related ticket exists, and it isn't yet clear whether it's a sync-job bug or a physical process issue",
        ],
    ),
    # --- Soft/non-ID connections that echo the ORIGINAL corpus ---
    GoldCase(
        question="What happened with the login outage?",
        expected_doc_ids=[
            "INC1042",
            "PROJ-201",
            "PR-455",
            "auth-service-outage-postmortem-august-2026",
            "eng-platform-2026-08-08",
            "INC1115",  # added 2026-08-14, second correction pass -- same docs
            "PR-611",  # legitimately retrieved on the near-duplicate case 01
            "PROJ-312",  # ("why did auth-service go down?") but missed here since
            "session-management-runbook",  # the first pass didn't check this twin
            # question. See results/followup.md.
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "root cause was an expired JWT signing key that was not rotated ahead of its expiry window",
            "the Slack thread references the outage and the on-call paging that shipped afterward without citing any ticket ID",
        ],
    ),
    GoldCase(
        question="Are customers stacking discount codes somehow?",
        expected_doc_ids=[
            "INC1201",
            "PROJ-401",
            "PR-701",
            "coupon-discount-validation-rules",
            "customer-support-eng-2026-08-10",
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "yes -- coupon validation only checked for duplicate codes, not multiple distinct codes on one order",
            "the support-eng Slack thread independently flags the same pattern from customer-facing tickets, with no ticket ID referenced",
        ],
    ),
    GoldCase(
        question="Did the order-service pool issue come back?",
        expected_doc_ids=[
            "INC0980",
            "order-service-on-call-runbook",
            "PR-508",
            "order-platform-2026-08-07",
            "q3-2026-infra-cost-review-meeting-notes",  # added 2026-08-14, second
            # correction pass -- same doc legitimately retrieved on the
            # near-duplicate case 06, missed here since the first pass didn't
            # check this twin question. See results/followup.md.
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "INC0980 (May 2026) was caused by a long-running batch job holding database connections open, mitigated manually, never permanently fixed",
            "the Slack thread reports the same pool-exhaustion pattern recurring, referencing no ticket ID, and confirms PR-508's fix still hasn't shipped",
        ],
    ),
    # --- Inconclusive / no-real-answer ---
    GoldCase(
        question="Why are we seeing sporadic 502s from the API gateway?",
        expected_doc_ids=["INC1243", "PROJ-425", "eng-infra-2026-08-15"],
        excluded_doc_ids=[],
        expected_facts=[
            "low-frequency 502s (~0.05% of requests) with no consistent pattern by endpoint, time, or upstream service",
            "root cause is not yet identified -- attempts to reproduce on demand have been unsuccessful",
            "no fix exists; a good answer must not invent one",
        ],
    ),
    GoldCase(
        question="What's causing the intermittent Redis latency spikes?",
        expected_doc_ids=["INC1158", "PROJ-335"],
        excluded_doc_ids=[],
        expected_facts=[
            "multiple otherwise-unrelated services see Redis latency spike to 2-3x baseline at irregular intervals",
            "connection pool sizing has been checked and ruled out; escalated to infra to check for a network-level cause",
            "no root cause identified and no fix in progress; a good answer must not invent one",
        ],
    ),
    # --- Cross-system, no shared ID (new pair, links to pre-existing data) ---
    GoldCase(
        question="Is partner API traffic being rate-limited correctly?",
        expected_doc_ids=[
            "INC1151",
            "PROJ-330",
            "PR-625",
            "api-rate-limiting-guide",
            "partner-eng-2026-08-09",  # added 2026-08-12, staleness audit:
            # same incident, Slack thread -- same pattern as cases 01/06/20/22.
            "PROJ-255",  # added 2026-08-14, second correction pass -- legitimately
            "partner-integration-best-practices",  # retrieved and grounded on
            # this question across all 3 runs, never on excluded_doc_ids.
            # See results/followup.md.
        ],
        excluded_doc_ids=[],
        expected_facts=[
            "a newly onboarded partner integration was defaulting to the standard rate-limit tier (100 req/min) instead of partner tier (500 req/min)",
            "fixed by correcting the default and re-provisioning the account",
            "the API Rate Limiting Guide documents the same tier thresholds but is linked only by shared fact, not by any ticket ID pointing to INC1151/PROJ-330",
        ],
    ),
    # --- Open/partial, no fix yet ---
    GoldCase(
        question="Why is customer support queue time increasing?",
        expected_doc_ids=["INC1236", "PROJ-420", "support-eng-2026-08-14"],
        excluded_doc_ids=[],
        expected_facts=[
            "average time-to-first-response has climbed steadily over the past week with no clear staffing or volume explanation",
            "engineering is checking whether the support tool's ticket-routing integration has slowed down -- no conclusion yet, no fix exists",
        ],
    ),
    GoldCase(
        question="Why did the third-party analytics script slow the page down?",
        expected_doc_ids=["INC1229", "PROJ-415"],
        excluded_doc_ids=[],
        expected_facts=[
            "page load time regressed correlating with a new third-party analytics script that blocks rendering under slow network conditions",
            "confirmed render-blocking; still evaluating whether it can be deferred or async-loaded without breaking functionality -- no fix merged yet",
        ],
    ),
    GoldCase(
        question="What's happening with the mobile push notification opt-in rate?",
        expected_doc_ids=["INC1257", "mobile-notification-permission-best-practices", "mobile-eng-2026-08-17"],
        excluded_doc_ids=[],
        expected_facts=[
            "opt-in rate for new installs dropped noticeably starting a few days ago",
            "product team suspects a recent permission-prompt timing change, but engineering has not yet confirmed this",
            "no fix exists yet -- a good answer must not present the timing theory as confirmed",
        ],
    ),
    # --- Precision / noise stress ---
    GoldCase(
        question="What's been discussed in recent team meetings?",
        expected_doc_ids=[
            "q3-design-review-notes",
            "eng-onboarding-2026-08-16",  # added 2026-08-14, second correction pass
            "eng-database-2026-08-13",  # -- legitimately retrieved and grounded on
            "eng-general-2026-08-14",  # this question across all 3 runs, never on
            # excluded_doc_ids (distinct from the confirmed distractor hits
            # already documented in Section 5.1). See results/followup.md.
        ],
        excluded_doc_ids=[
            "team-offsite-planning-fall-2026",
            "vendor-contract-renewals-q3",
            "engineering-all-hands-notes-august-2026",
            "standup-notes-2026-08-06",
            "standup-notes-2026-08-13",
        ],
        expected_facts=[],  # precision/exclusion case, deliberately thin -- same pattern as "anything engineers should know"
    ),
    GoldCase(
        question="Anything I should know about upcoming team events or offsites?",
        expected_doc_ids=[
            "team-offsite-planning-fall-2026",
            "social-committee-2026-08-01",
            "social-committee-2026-08-15",
        ],
        excluded_doc_ids=["vendor-contract-renewals-q3", "q3-design-review-notes"],
        expected_facts=[],  # precision case -- must not pull in unrelated incidents/bugs just because they're recent
    ),
    # --- Cases 31-35: added after finding the original 30 had zero
    # questions naming an identifier whose only connection to an expected
    # document is a citation in that document's structured metadata
    # (explicit_related_ids), never in its own embedded text -- a
    # genuinely different retrieval scenario than the rest of the gold
    # set exercises. Every expected_doc_id below was confirmed directly
    # against the corpus: the "hidden" doc genuinely does not contain the
    # named ID anywhere in its own embedded text, only in metadata.
    GoldCase(
        question="What's the latest on PROJ-305?",
        expected_doc_ids=["PROJ-305", "eng-search-2026-08-05", "PR-605"],
        excluded_doc_ids=[],
        expected_facts=[
            "PROJ-305 is a bug: autocomplete showing stale product names because it reads from a separate, slower-refreshing cache than the main search index",
            "PR-605 is the fix -- repoints autocomplete at the primary search index",
            "the eng-search Slack thread is where the issue was first noticed and diagnosed, same category of staleness as the earlier PROJ-230 fix but a different, never-repointed cache",
        ],
    ),
    GoldCase(
        question="Is there any update on PROJ-318?",
        expected_doc_ids=["PROJ-318", "INC1130"],
        excluded_doc_ids=[],
        expected_facts=[
            "PROJ-318 investigates carrier API rate limiting as the cause of INC1130 (shipping label generation failing intermittently during peak order volume)",
            "429 rate-limit responses from the external carrier API track tightly with peak-hour order volume",
            "no fix merged yet -- still deciding between client-side backoff and requesting a higher limit from the carrier",
        ],
    ),
    GoldCase(
        question="What was PROJ-275 about?",
        expected_doc_ids=["PROJ-275", "PR-495"],
        excluded_doc_ids=[],
        expected_facts=[
            "PROJ-275 is a cosmetic typo fix in the order confirmation email footer, flagged by customer support, not tied to any incident",
            "PR-495 is the fix, merged and deployed with the next scheduled release",
        ],
    ),
    GoldCase(
        question="Can you give me context on PROJ-355?",
        expected_doc_ids=["PROJ-355", "PR-645"],
        excluded_doc_ids=[],
        expected_facts=[
            "PROJ-355 is a cosmetic CSS fix for a misaligned Save button on the account settings page at certain viewport widths, flagged by the design team",
            "PR-645 is the fix, merged with the next release",
        ],
    ),
    GoldCase(
        question="What's the story behind PROJ-445?",
        expected_doc_ids=["PROJ-445", "PR-740"],
        excluded_doc_ids=[],
        expected_facts=[
            "PROJ-445 is a small, proactive robustness improvement to the automated SSL certificate renewal script, not tied to any incident",
            "PR-740 is the routine fix, merged",
        ],
    ),
]
