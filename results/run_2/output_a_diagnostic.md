# Output A -- internal diagnostic report (run_2 only)

**Single-run data.** Stability fields (STABLE/UNSTABLE, mean+/-spread) require run_2 and run_3 to be meaningful -- not faked here, left as 'N/A (single run)' throughout. Re-run this generator once run_2/run_3 exist to fill them in.

## Aggregate summary

Verdict tally (run_2): better: 19, same: 15, worse: 1
Verdict stability: N/A (single run) -- requires run_2/run_3.

**Excl.hit occurrences (6 total):**
- Case 13, flat-RAG: ['engineering-all-hands-notes-august-2026']
- Case 13, 2-hop: ['engineering-all-hands-notes-august-2026']
- Case 13, ESG (v2): ['engineering-all-hands-notes-august-2026']
- Case 29, flat-RAG: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, 2-hop: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, ESG (v2): ['engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13', 'team-offsite-planning-fall-2026']

**Fabrication occurrences (13 total):**
- Case 01, flat-RAG: cited but not retrieved: ['PROJ-201', 'PROJ-312']
- Case 09, flat-RAG: cited but not retrieved: ['PR-611', 'PROJ-312']
- Case 12, flat-RAG: cited but not retrieved: ['PROJ-255']
- Case 12, ESG (v2): cited but not retrieved: ['PROJ-255']
- Case 14, flat-RAG: cited but not retrieved: ['PR-701', 'PROJ-401']
- Case 15, flat-RAG: cited but not retrieved: ['PR-705', 'PROJ-405']
- Case 16, flat-RAG: cited but not retrieved: ['PR-710', 'PROJ-410']
- Case 17, flat-RAG: cited but not retrieved: ['PR-715']
- Case 20, flat-RAG: cited but not retrieved: ['PR-455', 'PR-611', 'PROJ-201', 'PROJ-312']
- Case 21, flat-RAG: cited but not retrieved: ['PR-701', 'PROJ-401']
- Case 25, flat-RAG: cited but not retrieved: ['PROJ-255']
- Case 31, flat-RAG: cited but not retrieved: ['PROJ-230']
- Case 31, ESG (v2): cited but not retrieved: ['PR-470', 'PROJ-230']

---

## Case 01: why did auth-service go down?
Expected docs: ['INC1042', 'PROJ-201', 'PR-455', 'auth-service-outage-postmortem-august-2026', 'eng-platform-2026-08-08']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home', 'incident-response-process-standard-operating-procedure']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.60 | 0.60 | false | TRUE | 2231 | $0.0100 | 8.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.50 | false | false | 3046 | $0.0120 | 9.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.45 | false | false | 125898 | $0.3625 | 181.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify the root cause: expired JWT signing key not rotated, due to manual calendar-reminder process, fixed via PR-455/PROJ-201, and correctly distinguish the unrelated INC1115 TTL issue. ESG additionally cites eng-platform-2026-08-08 (an expected document that flat-RAG missed and 2-hop also missed retrieving/citing), adding the corroborating Slack detail about calendar reminders, which is grounded in the expected doc set. ESG also correctly notes INC1166/PR-550 as not relevant, showing good discrimination without fabricating relevance. This is essentially the same core content as 2-hop but with the additional expected document (eng-platform-2026-08-08) properly incorporated, which neither baseline used. This is a genuine improvement using an expected document, not overreach.
Stability: N/A (single run)

## Case 02: what's going on with the payment gateway timeouts?
Expected docs: ['INC1055', 'PROJ-215', 'payment-gateway-troubleshooting-guide', 'INC1101', 'PR-601', 'PR-745', 'PROJ-301', 'checkout-idempotency-design-doc', 'incident-response-2026-08-09']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 1802 | $0.0097 | 8.2s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 1918 | $0.0106 | 11.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 121304 | $0.3216 | 207.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines correctly cover the core INC1055/PROJ-215/troubleshooting-guide facts, hedging appropriately on the unconfirmed root cause. ESG covers all that plus the additional expected documents (INC1101, PR-601, PR-745, PROJ-301, checkout-idempotency-design-doc, incident-response-2026-08-09), correctly explaining the related-but-distinct double-charging issue and its resolution via idempotency fix, while clearly distinguishing it from the still-unresolved timeout root cause. This adds materially relevant, correctly grounded context that the baselines omit entirely, without overstating confidence on the unresolved parts. No fabrication is apparent - all cited documents are in ESG's retrieved list and align with the expected document set.
Stability: N/A (single run)

## Case 03: checkout latency during the flash sale
Expected docs: ['INC1082', 'PROJ-260']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 1256 | $0.0073 | 7.4s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1149 | $0.0060 | 7.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 40582 | $0.1078 | 71.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers rely on the same two expected documents (INC1082, PROJ-260) and convey materially identical facts: latency rose from ~400ms baseline to 6s+ under peak load, lock contention in inventory-service is the leading but unconfirmed hypothesis, checkout-service also showed elevated thread waits, no fix yet, investigation ongoing. ESG's answer is essentially equivalent in content and hedging to flat-RAG and 2-hop, just reformatted with headers. No new material facts are added, and no fabrications are present. This is a cosmetic difference only.
Stability: N/A (single run)

## Case 04: I am hearing some partners complaining about delays in push notification to their apps. what do we know?
Expected docs: ['INC1070', 'PROJ-244', 'PR-481', 'notification-service-architecture']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 0.50 | false | false | 1794 | $0.0099 | 9.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 0.50 | false | false | 1855 | $0.0103 | 13.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.67 | false | false | 79839 | $0.2085 | 141.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved and incorporated PROJ-244 and PR-481, both expected gold documents that neither baseline retrieved or cited. This adds material, grounded detail: the queue depth tripled over 48 hours without traffic increase (pointing to a consumer throughput regression, not just load growth), the identity of who opened the fix (Chen Liu), and the specific reason the fix isn't ready to merge (needs load testing to avoid downstream rate-limit errors). These are concrete, useful facts that directly answer the "what do we know" question and are grounded in the expected documents. ESG maintains the same appropriate hedging on missing info (no ETA, no partner-specific impact data) as the baselines, and does not overstate confidence anywhere. No fabrication is evident. This is a clear improvement in completeness without sacrificing calibration.
Stability: N/A (single run)

## Case 05: what's the latest on the TLS certificate expiring for the billing API?
Expected docs: ['INC1090']
Excluded docs: ['api-rate-limiting-guide']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 697 | $0.0041 | 5.1s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 577 | $0.0027 | 5.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 13866 | $0.0366 | 25.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers rely solely on INC1090 and convey the same core facts: TLS cert for api.internal-billing due to expire in 14 days, routine/low-urgency, no customer impact, no follow-up tickets, expected to be handled by on-call engineer. All three correctly hedge that no resolution/renewal confirmation exists. ESG is slightly more verbose with extra headers but adds no new grounded facts beyond the baselines, and doesn't fabricate anything. Differences are cosmetic/structural only.
Stability: N/A (single run)

## Case 06: order-service keeps having connection pool issues, what's actually being done about it?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.75 | 1.00 | false | false | 1674 | $0.0086 | 10.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.75 | 1.00 | false | false | 1593 | $0.0075 | 7.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.80 | false | false | 79394 | $0.2365 | 120.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved and incorporated order-platform-2026-08-07, one of the expected documents that both baselines missed. This gives a materially important update: the issue recurred in August 2026, and the draft PR "hasn't gone anywhere yet" despite a suggestion to revive it. This is new, grounded information not present in either baseline answer, directly answering "what's actually being done about it" more completely and currently. ESG also appropriately hedges on the extra infra-cost document as "unconfirmed" and clearly flags what's missing. No fabrication is evident since cited documents align with retrieved list. This makes ESG's answer strictly more complete and equally well-calibrated compared to the baselines.
Stability: N/A (single run)

## Case 07: are there known issues with image uploads or thumbnail generation under load?
Expected docs: ['INC1155', 'PR-545']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 964 | $0.0058 | 8.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 893 | $0.0048 | 5.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 31521 | $0.0826 | 49.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1155 and correctly describe the recurring thumbnail generation failure under burst load, but note there is no fix/RCA documented. ESG retrieved both expected documents (INC1155 and PR-545), and additionally surfaces that PR-545 introduced a retry-with-jitter fix attempting to address the issue, while appropriately hedging that it's not confirmed to be deployed/verified or explicitly linked to INC1155. This adds material, correctly-grounded information beyond what the baselines provide, without overstating confidence.
Stability: N/A (single run)

## Case 08: partners have mentioned delayed webhook deliveries during traffic spikes, what's the status?
Expected docs: ['INC1160', 'PROJ-320']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 864 | $0.0049 | 6.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 1011 | $0.0061 | 7.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 33440 | $0.0859 | 51.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1160 and PROJ-320) and used them correctly: it explains the incident resolution and, crucially, surfaces that a permanent fix (backpressure/DLQ) is proposed in PROJ-320 but not yet scheduled. This directly answers the follow-up question that both baselines explicitly say they cannot answer ("I don't have documents indicating whether a permanent fix has been implemented"). ESG's claims about PROJ-320 status (backlog, unscheduled) are grounded in the expected document. This is materially more complete and accurate than either baseline, which both hedge on exactly the information ESG correctly surfaces.
Stability: N/A (single run)

## Case 09: some users are reporting random logouts, do we know why?
Expected docs: ['INC1166', 'PR-550']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 2148 | $0.0125 | 15.2s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.20 | false | false | 3723 | $0.0146 | 12.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.20 | false | false | 125410 | $0.3317 | 199.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the same two root causes (INC1166 session-store eviction under memory pressure, fixed/mitigated by PR-550; and INC1115 TTL config regression, fixed by PR-611) and appropriately hedge that the documents don't specify which matches the current reports. ESG's answer is grounded in the expected documents (INC1166, PR-550) plus additional real retrieved documents (INC1115, PR-611, etc.) that provide useful context without contradicting the expected set. It doesn't fabricate anything - all cited docs appear in its retrieved list. ESG adds a helpful clarifying section on INC1042/PROJ-201/PR-455 explicicitly ruling it out as unrelated, which is accurate framing rather than fabrication. This is materially the same level of hedging and correctness as flat-RAG and 2-hop, just with slightly more structure/detail. No confident wrong claims. Overall it's essentially equivalent in substance to the 2-hop baseline (same retrieved set, same core conclusions), with flat-RAG being slightly less complete (missing INC1115/PR-611 detail is present in flat-RAG actually, so flat-RAG covers similar ground too). Since ESG matches or slightly exceeds in organization but not in new factual content beyond what 2-hop already provides, this is same performance.
Stability: N/A (single run)

## Case 10: did a recent feature flag change cause errors for customers?
Expected docs: ['INC1170', 'PR-555']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 734 | $0.0036 | 5.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 752 | $0.0035 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 32225 | $0.0863 | 55.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines correctly answer the core question using INC1170, describing root cause and resolution accurately. ESG includes the same INC1170 information plus PR-555, which is part of the expected document set that baselines missed. ESG's discussion of PR-555 is appropriately hedged (notes it's "not formally linked to a specific ticket" but related in substance), which is a calibrated, non-fabricated addition. This gives readers a fuller picture (that a follow-up fix was merged) without overstating certainty. No confident false claims are present. Thus ESG is more complete than either baseline while maintaining appropriate hedging.
Stability: N/A (single run)

## Case 11: are transactional emails like password resets being delayed right now?
Expected docs: ['INC1175', 'email-delivery-service-operational-runbook', 'INC1165', 'PROJ-340', 'eng-notifications-2026-08-08']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | false | 807 | $0.0049 | 5.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.20 | 1.00 | false | false | 823 | $0.0048 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.56 | false | false | 94405 | $0.2754 | 140.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected documents include INC1175, email-delivery-service-operational-runbook, INC1165, PROJ-340, and eng-notifications-2026-08-08 — indicating the gold answer should cover both the resolved delay incident AND the still-open/investigating delivery-rate drop (INC1165/PROJ-340/eng-notifications-2026-08-08). Both baselines only retrieved INC1175 and thus only report the resolved incident, completely missing the still-open INC1165/PROJ-340 investigation, which is central to answering "is this delayed right now" — the correct nuanced answer is that the specific delay is resolved but a related unresolved issue (15% delivery drop) was still open with no fix as of the last update. ESG's answer surfaces exactly this: it cites INC1175 (resolved), the operational runbook, and critically INC1165/PROJ-340/eng-notifications-2026-08-08 showing the open investigation, giving a much more complete and accurate picture. ESG also appropriately hedges about not having timestamped "right now" confirmation, matching the caveating style of the baselines while providing substantially more grounded detail. The additional documents ESG references (INC1215, PROJ-410, PR-710, email-deliverability-runbook) are in its own retrieved list, so they are legitimately retrieved (not fabricated), and are used to add relevant context about a related Gmail-specific issue, appropriately caveated as distinct from the main question. This makes ESG's answer clearly better than either baseline, which entirely miss the material fact that a related delivery-rate problem was still unresolved.
Stability: N/A (single run)

## Case 12: why did legitimate customers get rate-limited recently?
Expected docs: ['INC1180', 'PR-560']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 1675 | $0.0077 | 7.9s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.40 | false | false | 2243 | $0.0113 | 10.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.50 | false | TRUE | 55812 | $0.1461 | 89.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the two causes grounded in INC1180 and PR-560 (bad global config rollout without canary) plus the partner tier misprovisioning issue from partner-eng-2026-08-09. ESG's answer is consistent with the expected documents, provides accurate detail (quotes from INC1180/PR-560, correct attribution), and appropriately notes PROJ-255 as secondary/background rather than a cause, similar to 2-hop's treatment. It doesn't fabricate anything - its retrieved list includes the documents it cites. It also adds a helpful "Gaps" section correctly noting missing details (ticket number for checklist) without overclaiming. This closely matches the quality of the 2-hop answer, which was itself equivalent to flat-RAG in content. No confident wrong claims are present. Differences between ESG and the baselines are essentially cosmetic/structural (headers, organization) with the same core facts and same hedging where appropriate.
Stability: N/A (single run)

## Case 13: is there anything engineers should be aware of right now?
Expected docs: ['INC1061', 'eng-onboarding-2026-08-16']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home', 'incident-response-process-standard-operating-procedure', 'engineering-all-hands-notes-august-2026', 'PR-512', 'PR-490']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.00 | 0.00 | TRUE | false | 707 | $0.0037 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.00 | 0.00 | TRUE | false | 722 | $0.0035 | 4.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.50 | 0.50 | TRUE | false | 14889 | $0.0461 | 29.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- The expected sources include INC1061, which likely contains an actual current incident relevant to engineers, but none of the three systems retrieved INC1061 - all three retrieved only eng-onboarding-2026-08-16 and engineering-all-hands-notes-august-2026. All three systems therefore missed the key expected document and gave essentially the same hedged "no current issue found" answer. ESG's answer is more verbose but conveys the same substantive conclusion and same degree of hedging as the baselines - none of them surface the actual incident information that INC1061 likely contains. Since ESG didn't retrieve INC1061 either, it can't be credited with surfacing missing information; it's just as incomplete as the baselines, just with extra narrative framicing (e.g., "investigation graph", "search exhausted its available leads") that doesn't add real information. This is a tie in substance.
Stability: N/A (single run)

## Case 14: Why were customers seeing double discounts at checkout?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'eng-checkout-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 664 | $0.0032 | 3.6s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1679 | $0.0068 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 68767 | $0.1820 | 118.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Both 2-hop and ESG retrieved all five expected documents and give materially the same core explanation: validation only checked for duplicate identical codes, not distinct codes, allowing stacking; fixed via PROJ-401/PR-701, moved validation to cart-finalization time. ESG additionally cites customer-support-eng-2026-08-10 (not in expected set but plausibly a real, relevant retrieved doc, not fabricated) as corroborating evidence, and includes a "Gaps" section that appropriately hedges on details not in the documents. This matches the level of detail and grounding of the 2-hop answer, with essentially the same facts, same confidence. No fabrications or incorrect assertions apparent. The differences are largely additional formatting/corroboration, not a difference in what a reader learns. Thus this is materially the same as the best baseline (2-hop).
Stability: N/A (single run)

## Case 15: Why did the analytics dashboard show revenue below actual?
Expected docs: ['INC1208', 'PROJ-405', 'PR-705', 'eng-data-2026-08-11']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 547 | $0.0024 | 4.5s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1235 | $0.0044 | 5.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 53049 | $0.1391 | 90.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the root cause: a join condition bug excluding coupon orders from revenue aggregation, causing ~20% undercount, fixed in PR-705/PROJ-405. Flat-RAG only cites INC1208 but gets the core fact right, though lacks the detail about the null field mechanism and verification. 2-hop and ESG both retrieve all four expected documents and add mechanism detail (null field), attribution (Sam Okafor, Layla Haddad), and verification. ESG additionally notes the gap about unknown duration of the bug, which is accurately grounded in eng-data-2026-08-11 ("no clear sense of how long it's been wrong"), matching 2-hop's mention of "no clear indication of how long it had been happening." Both 2-hop and ESG are essentially equivalent in content and confidence; ESG is slightly more organized but not materially different in facts conveyed. No fabrications detected in ESG - all citations correspond to retrieved documents in the expected set. Since ESG matches 2-hop (the better baseline) in substance, this is a SAME verdict.
Stability: N/A (single run)

## Case 16: Why weren't Gmail users getting password reset emails?
Expected docs: ['INC1215', 'PROJ-410', 'PR-710', 'email-deliverability-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 586 | $0.0027 | 3.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1492 | $0.0064 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 45928 | $0.1239 | 77.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All four expected documents were retrieved by both 2-hop and ESG, while flat-RAG only had INC1215. ESG's answer covers the same root cause, fix, and runbook context as 2-hop, correctly attributing details to each document (INC1215, PROJ-410, PR-710, email-deliverability-runbook) and correctly notes the broader delivery-rate investigation was separate and unresolved without conflating it. This matches 2-hop's coverage and calibration closely - both are grounded in the same four documents with the same degree of hedging on the unresolved broader issue. ESG provides slightly more granular quotes but conveys materially the same facts and confidence level as 2-hop, which is the best baseline. No fabrications or overreach detected relative to the expected documents.
Stability: N/A (single run)

## Case 17: Why is bulk export timing out for large accounts?
Expected docs: ['INC1250', 'PROJ-430', 'PR-715', 'bulk-export-architecture', 'eng-platform-2026-08-16']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.40 | 1.00 | false | TRUE | 811 | $0.0035 | 3.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 1264 | $0.0051 | 6.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 56950 | $0.1516 | 89.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three systems correctly identify the root cause (synchronous, in-memory, non-paginated export) and fix (PR-715 streaming). The 2-hop answer additionally includes the architecture doc guidance. ESG's answer includes all five expected documents (INC1250, PROJ-430, PR-715, bulk-export-architecture, eng-platform-2026-08-16), fully covering the expected source set, including the Slack thread which neither baseline cited. ESG's claims are well-grounded with direct quotes matching the described document content, and it doesn't assert anything unsupported. This makes ESG's answer more complete than both baselines while maintaining accuracy.
Stability: N/A (single run)

## Case 18: Why is the iOS app crashing on the checkout screen?
Expected docs: ['INC1122', 'mobile-eng-2026-08-05']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 722 | $0.0046 | 5.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 641 | $0.0035 | 6.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 30511 | $0.0809 | 55.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1122 and correctly note the symptom (memory pressure) but hedge heavily that root cause is unknown. ESG retrieved the additional expected document (mobile-eng-2026-08-05) and surfaces the actual working hypothesis discussed there (SDK image cache not releasing thumbnails), while correctly caveating that this is unconfirmed and not yet formalized. This is materially more informative and still properly hedged/calibrated - it doesn't claim the leak is confirmed, just that it's the leading hypothesis per the Slack thread, which matches the expected documents. This is a clear improvement over baselines that missed the second expected document entirely.
Stability: N/A (single run)

## Case 19: Why don't the warehouse inventory counts match the system?
Expected docs: ['INC1137', 'ops-warehouse-2026-08-02']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 564 | $0.0031 | 5.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 547 | $0.0027 | 6.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 23117 | $0.0745 | 41.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1137 and correctly hedge that root cause is unknown, but they miss the additional context available in ops-warehouse-2026-08-02 (the expected second document), which contains the ops team's speculation about a sync-job bug, the recurrence pattern, and the origin story of the ticket. ESG retrieved both expected documents and surfaces this additional grounded context while still correctly hedging that the root cause is unconfirmed and speculative. ESG does not overstate confidence - it clearly labels the sync-job theory as speculative/unconfirmed, matching the source material. This gives the reader materially more useful, correctly-hedged information than either baseline.
Stability: N/A (single run)

## Case 20: What happened with the login outage?
Expected docs: ['INC1042', 'PROJ-201', 'PR-455', 'auth-service-outage-postmortem-august-2026', 'eng-platform-2026-08-08', 'INC1115', 'PR-611', 'PROJ-312', 'session-management-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 0.75 | false | TRUE | 1809 | $0.0084 | 7.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.90 | false | false | 3733 | $0.0152 | 15.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.82 | false | false | 122253 | $0.3285 | 203.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify INC1042 as "the login outage" per the Slack thread framing, and all three correctly note the two other distinct incidents (INC1115, INC1166) as separate issues. The 2-hop answer is the most complete baseline, including postmortem details (2.5hr duration, 60% failure rate, manual calendar-reminder root cause), PR-455 details, and action items. ESG's answer covers essentially the same ground as 2-hop: INC1042 details, postmortem stats (2.5hr, 60% failure), PROJ-201/PR-455 follow-up, and the two separate incidents INC1115/INC1166 with their respective PROJ-312/PR-611 and PR-550 fixes. ESG additionally cites PR-550 for INC1166 remediation, which is a retrieved (not fabricated) document per its own retrieved list, adding useful detail not in 2-hop's answer. Both ESG and 2-hop hedge appropriately about ambiguity while landing on INC1042 as the best answer. The content and confidence calibration are materially equivalent, with ESG being slightly more explicit about the three-incident structure and including PR-550, which is a minor completeness addition but not a decisive difference. Overall this is essentially the same level of quality as the best baseline (2-hop), just reformatted with slightly more explicit structure.
Stability: N/A (single run)

## Case 21: Are customers stacking discount codes somehow?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'customer-support-eng-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 741 | $0.0040 | 4.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.80 | false | false | 1696 | $0.0070 | 6.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 65174 | $0.1751 | 109.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly confirm the coupon stacking bug, root cause, and fix (INC1201, PROJ-401, PR-701). The 2-hop answer adds detail from eng-checkout-2026-08-10 about how it was found and the cart-finalization fix. ESG covers all of that plus incorporates customer-support-eng-2026-08-10, which is part of the expected document set that neither baseline used. This is materially important because the question asks "are customers stacking discount codes somehow" (present tense), and the support thread indicates ongoing/recent reports of this happening, which is directly relevant context. ESG correctly hedges that it's unclear whether this is a recurrence or unrelated, without overclaiming. This gives the reader a more complete and accurate picture grounded in the expected documents, an addition the best baseline (2-hop) omits entirely.
Stability: N/A (single run)

## Case 22: Did the order-service pool issue come back?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07', 'q3-2026-infra-cost-review-meeting-notes']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.80 | 1.00 | false | false | 1917 | $0.0093 | 10.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 1855 | $0.0084 | 7.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 77045 | $0.2011 | 119.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers converge on the same core conclusion: yes, the issue appears to have recurred based on the informal Slack thread, with no permanent fix ever merged, and no formal new incident ticket confirming it. ESG additionally incorporates the q3-2026-infra-cost-review-meeting-notes document (part of the expected set that both baselines missed), correctly noting the infra cost increase tentatively attributed to pool sizing changes, while appropriately hedging that this doesn't confirm a new incident on its own. This is a legitimate additional piece of grounded evidence that improves completeness without overstating confidence. ESG maintains the same calibrated hedging as the baselines regarding lack of a formal incident ticket. No fabrications are apparent - all cited documents are in ESG's retrieved list and appear consistent with the expected set. This makes ESG modestly better due to fuller use of the expected document set while preserving appropriate uncertainty.
Stability: N/A (single run)

## Case 23: Why are we seeing sporadic 502s from the API gateway?
Expected docs: ['INC1243', 'PROJ-425', 'eng-infra-2026-08-15']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 794 | $0.0041 | 5.2s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 822 | $0.0041 | 13.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 38371 | $0.0999 | 59.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three systems correctly conclude the root cause is unknown/unresolved, avoiding fabrication. However, ESG additionally retrieves and incorporates eng-infra-2026-08-15, one of the three expected documents that both baselines missed entirely. ESG's answer surfaces the corroborating Slack thread detail (infra-team reports, plan to enable verbose logging) which is part of the expected evidence set and adds legitimate, grounded detail without overstating confidence about the root cause. This makes ESG's answer more complete relative to the expected documents while maintaining the same appropriate hedge on the unresolved root cause.
Stability: N/A (single run)

## Case 24: What's causing the intermittent Redis latency spikes?
Expected docs: ['INC1158', 'PROJ-335']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 862 | $0.0045 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 900 | $0.0046 | 9.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 26594 | $0.0694 | 42.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify that no root cause has been confirmed in the expected documents, correctly note connection pool sizing was ruled out, and escalation to infra for network-level investigation. ESG's answer is materially the same as the baselines in facts and hedging, just with more formatting/detail (e.g., status labels, "search frontier exhausted"). No fabrications noted - all citations are within the expected set. Differences are cosmetic/structural, not substantive.
Stability: N/A (single run)

## Case 25: Is partner API traffic being rate-limited correctly?
Expected docs: ['INC1151', 'PROJ-330', 'PR-625', 'api-rate-limiting-guide', 'partner-eng-2026-08-09', 'PROJ-255', 'partner-integration-best-practices']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.14 | 1.00 | false | TRUE | 1126 | $0.0082 | 9.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.29 | 1.00 | false | false | 1381 | $0.0086 | 8.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 94098 | $0.2458 | 156.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved and synthesized all seven expected documents (INC1151, PROJ-330, PR-625, api-rate-limiting-guide, partner-eng-2026-08-09, PROJ-255, partner-integration-best-practices), while both baselines missed the majority of the expected set (flat-RAG had only 1, 2-hop had only 2). ESG's answer correctly identifies two distinct issues: a documentation mismatch (PROJ-255, resolved without code change) and a real incorrect-rate-limiting incident (INC1151/PROJ-330, fixed via PR-625), and appropriately hedges on whether a systemic provisioning-checklist fix was implemented, which matches the "agreed, separate ticket" language implied by the gold documents. This is far more complete and still properly calibrated (it doesn't overclaim resolution beyond what's evidenced) compared to the baselines, which only had partial information and could not surface the INC1151/PROJ-330/PR-625 incident at all. ESG's citations correspond to its own retrieved list, so no fabrication concerns. This is a clear improvement in grounded completeness over the best baseline.
Stability: N/A (single run)

## Case 26: Why is customer support queue time increasing?
Expected docs: ['INC1236', 'PROJ-420', 'support-eng-2026-08-14']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 561 | $0.0033 | 4.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 750 | $0.0049 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.60 | false | false | 66278 | $0.2072 | 108.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected sources (INC1236, PROJ-420, support-eng-2026-08-14) together reveal that support leadership/engineering suspect the ticket-routing integration tool is slowing down, though root cause is unconfirmed. Both baselines only retrieved INC1236 and thus missed PROJ-420 and the Slack thread, so they hedge maximally and never surface the "ticket-routing integration" hypothesis, incorrectly stating no further info exists. ESG retrieved all three expected documents and correctly surfaces the leading hypothesis (routing-tool slowdown) while still appropriately hedging that root cause is unconfirmed, matching the actual confirmed status in the expected docs. ESG also brings in INC1222/eng-database-2026-08-13 as a possibly-related but explicitly unconfirmed signal, clearly labeling it as speculative and not conflating it with confirmed fact. This is a case where the expected documents did contain more info (the routing-tool hypothesis) that the baselines failed to surface but ESG did, without asserting unsupported claims as fact.
Stability: N/A (single run)

## Case 27: Why did the third-party analytics script slow the page down?
Expected docs: ['INC1229', 'PROJ-415']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 660 | $0.0043 | 6.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 528 | $0.0027 | 4.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 21773 | $0.0592 | 38.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected sources are INC1229 and PROJ-415. Both baselines only retrieved INC1229 and explicitly note they lack the root-cause mechanism, correctly hedging but missing the actual answer. ESG retrieved both expected documents and surfaced the key fact (confirmed by Layla Haddad's comment in PROJ-415) that the script was loaded synchronously/render-blocking, which explains the "why" the question asks. This is a material fact grounded in the expected documents that both baselines missed. ESG also appropriately notes remaining gaps (no confirmed fix, no quantitative data) without overstating confidence. No fabrication is evident since PROJ-415 is in the expected set and ESG's claims align with it.
Stability: N/A (single run)

## Case 28: What's happening with the mobile push notification opt-in rate?
Expected docs: ['INC1257', 'mobile-notification-permission-best-practices', 'mobile-eng-2026-08-17']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 575 | $0.0033 | 5.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 576 | $0.0031 | 5.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 35316 | $0.1076 | 59.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved all three expected documents and synthesized them accurately: it captures the INC1257 core facts (drop in opt-in rate, unconfirmed permission-prompt-timing theory), and adds corroborating detail from the mobile-eng Slack thread (independent observation, A/B test proposal) and the best-practices doc (industry guidance on prompt timing affecting opt-in rates). This is materially more complete than both baselines, which only retrieved INC1257 and explicitly stated they lacked further detail. ESG appropriately hedges on what remains unconfirmed (root cause, resolution) without asserting anything unsupported. No fabrication is evident since all cited documents are in ESG's retrieved list and align with the expected set.
Stability: N/A (single run)

## Case 29: What's been discussed in recent team meetings?
Expected docs: ['q3-design-review-notes', 'eng-onboarding-2026-08-16', 'eng-database-2026-08-13', 'eng-general-2026-08-14']
Excluded docs: ['team-offsite-planning-fall-2026', 'vendor-contract-renewals-q3', 'engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.00 | 0.00 | TRUE | false | 1709 | $0.0094 | 11.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.00 | 0.00 | TRUE | false | 1641 | $0.0084 | 12.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.75 | 0.30 | TRUE | false | 89210 | $0.2587 | 136.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **WORSE** -- The expected documents are q3-design-review-notes, eng-onboarding-2026-08-16, eng-database-2026-08-13, eng-general-2026-08-14. Neither baseline nor ESG retrieved q3-design-review-notes, so all miss that piece. Both baselines cover eng-database, eng-general, eng-onboarding correctly, and appropriately hedge that there's no formal "team meeting" notes, listing Slack threads instead - this is accurate given the retrieved set.

ESG covers the same three expected docs (eng-database-2026-08-13, eng-general-2026-08-14, eng-onboarding-2026-08-16) plus additional context. However, ESG introduces engineering-all-hands-notes-august-2026, standup-notes-2026-08-13, and INC1222 - the first two are explicitly listed as distractors in the known irrelevant list. ESG confidently asserts a connection between eng-database-2026-08-13 and INC1222, claiming the discussion "escalated into a formal incident" - this is a confident causal/temporal claim not established by the expected documents (INC1222 isn't even in the expected or excluded list, it's an outside document not vetted by the grader). This is a fairly strong claim of correlation/causation that isn't verified against gold documents, and engineering-all-hands-notes-august-2026 being included as a distractor also gets discussed as if relevant content, potentially misleading the reader about what recent meeting notes contain by treating it as material.

While ESG's inclusion of standup-notes-2026-08-13 (a distractor) is just listed as "routine standup" with no false claims - fairly benign. But INC1222 linkage is a stronger, speculative claim presented with confidence ("This concern appears to have escalated..." "matches directly with the discussion") that isn't supported by the expected document set, since INC1222 is outside the expected documents. This introduces unsupported/unverified conclusions beyond what's grounded, making the answer less calibrated than the baselines, which stick closely to what's actually in the documents and appropriately hedge.

Given the strict criteria that confidently asserting connections not supported by expected documents counts as WORSE regardless of other completeness, and ESG does state this incident-escalation narrative with some confidence ("appears to have escalated", "matches directly"), this constitutes an overreach not grounded in the expected/excluded document set.
Stability: N/A (single run)

## Case 30: Anything I should know about upcoming team events or offsites?
Expected docs: ['team-offsite-planning-fall-2026', 'social-committee-2026-08-01', 'social-committee-2026-08-15']
Excluded docs: ['vendor-contract-renewals-q3', 'q3-design-review-notes']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 741 | $0.0041 | 6.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 823 | $0.0047 | 6.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 22173 | $0.0610 | 33.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the two key expected documents (team-offsite-planning-fall-2026 and social-committee-2026-08-01) and gave essentially the same substantive content: early-stage planning, no finalized dates/venues. ESG additionally retrieved social-committee-2026-08-15, which is in the expected set, but ESG correctly identifies it as unrelated (birthday shoutout, not an event/offsite) and excludes it from the substantive answer -- this is accurate handling rather than a miss, though it means the "team offsite" content of that document (if any) wasn't surfaced. Since the gold set lists it as expected, presumably it contains something relevant, but ESG's characterization matches the actual content it retrieved (a birthday shoutout) and correctly judged it not relevant to offsites/team events. This appears to be a case where the gold label may include a doc that turns out not to add extra material info, or the system correctly assessed its content. Either way, ESG doesn't fabricate anything, doesn't hedge incorrectly, and provides the same core information as both baselines, with slightly more transparency about the extra document. This is materially the same as the baselines with minor additional transparency -- not clearly better or worse.
Stability: N/A (single run)

## Case 31: What's the latest on PROJ-305?
Expected docs: ['PROJ-305', 'eng-search-2026-08-05', 'PR-605']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | TRUE | 2698 | $0.0087 | 6.1s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 3882 | $0.0106 | 5.3s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.23 | false | TRUE | 103774 | $0.2682 | 126.8s | reached processing cap (20/20) |

Verdict run 1: **BETTER** -- All three answers converge on the same core facts: PROJ-305 tracked stale autocomplete cache, fixed via PR-605, merged and verified in staging, related to INC1108. Both flat-RAG and ESG retrieved and cited eng-search-2026-08-05 (the Slack discussion) among expected docs, though flat-RAG's answer text doesn't explicitly mention or quote it, while ESG explicitly cites and summarizes the slack:eng-search-2026-08-05 content, adding the discussion between Layla Haddad and Omar Farouk that led to the PR-605 plan. This makes ESG's answer more complete relative to the full expected document set. No fabrication is evident: all cited docs appear in ESG's retrieved list. The extra detail is grounded and factually consistent with the other documents, not contradicted. Thus ESG's answer is slightly more complete but not fundamentally different in facts or confidence.
Stability: N/A (single run)

## Case 32: Is there any update on PROJ-318?
Expected docs: ['PROJ-318', 'INC1130']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1535 | $0.0055 | 4.3s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 2252 | $0.0069 | 4.7s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 143069 | $0.4277 | 205.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers convey the same core facts: PROJ-318 is investigating carrier API rate limiting (429s) tied to peak-hour volume, no fix merged yet, decision pending between client-side backoff vs requesting higher rate limit, corroborated by INC1130. ESG adds a bit more framing ("What's Missing" section, status labels) but doesn't introduce new unsupported claims beyond what's in the retrieved documents (PROJ-318, INC1130), and the additional context about PR-740 being unrelated is accurate hedging, not fabrication. This is materially the same information as the baselines, just with slightly more structure/detail. No confident wrong claims in ESG. Differences are cosmetic/formatting rather than substantive.
Stability: N/A (single run)

## Case 33: What was PROJ-275 about?
Expected docs: ['PROJ-275', 'PR-495']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1353 | $0.0038 | 2.9s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.18 | false | false | 1963 | $0.0052 | 3.4s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 136942 | $0.3985 | 189.0s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers correctly identify PROJ-275 as the email footer typo fix, resolved via PR-495 by Yuki Tanaka and approved by Priya Nair, deployed in next release. ESG adds slightly more detail (reviewer comment, explicit note that it's unrelated to other tickets/incidents) but this is grounded in the retrieved PROJ-275 and PR-495 docs and doesn't introduce fabrication. The core facts are the same across all three; ESG's extra context is accurate and sourced, not materially different in confidence or correctness. This is essentially cosmetic/additional detail, not a substantive difference in what a reader learns.
Stability: N/A (single run)

## Case 34: Can you give me context on PROJ-355?
Expected docs: ['PROJ-355', 'PR-645']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | false | 1557 | $0.0051 | 3.6s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.25 | false | false | 1565 | $0.0049 | 3.4s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.25 | false | false | 99112 | $0.2879 | 143.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers convey the same core facts: PROJ-355 is a minor cosmetic bug fix (misaligned Save button), resolved via PR-645 by Layla Haddad, reviewed/approved by Yuki Tanaka, merged in next release. ESG adds slightly more structure, explicit status (Done/Merged), and explicitly notes the other retrieved documents are unrelated, which is a helpful clarification but not a material fact difference. No fabrications, no contradictions with expected/excluded docs. Differences are essentially cosmetic/organizational.
Stability: N/A (single run)

## Case 35: What's the story behind PROJ-445?
Expected docs: ['PROJ-445', 'PR-740']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | false | 1139 | $0.0060 | 6.3s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.33 | false | false | 1362 | $0.0056 | 4.5s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.33 | false | false | 69750 | $0.2190 | 112.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers converge on the same core facts: PROJ-445 was a routine, non-incident-related SSL cert renewal robustness improvement, implemented via PR-740, approved by Tomas Berg, merged, closed with Omar Farouk's comment. ESG adds explicit clarification that other retrieved entities (PROJ-440, PROJ-425/INC1243) are unrelated, which is consistent with flat-RAG's and 2-hop's own notes. No fabrication is evident, and no confident claims go beyond what's supported by PROJ-445/PR-740. The differences between ESG and the baselines are essentially cosmetic/organizational (formatting, extra headers) rather than substantive - all three correctly hedge about lack of deeper history and correctly note the ticket is self-contained and unrelated to incidents.
Stability: N/A (single run)
