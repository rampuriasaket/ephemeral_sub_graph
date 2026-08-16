# Output A -- internal diagnostic report (run_1 only)

**Single-run data.** Stability fields (STABLE/UNSTABLE, mean+/-spread) require run_2 and run_3 to be meaningful -- not faked here, left as 'N/A (single run)' throughout. Re-run this generator once run_2/run_3 exist to fill them in.

## Aggregate summary

Verdict tally (run_1): better: 17, same: 17, unknown: 1
Verdict stability: N/A (single run) -- requires run_2/run_3.

**Excl.hit occurrences (6 total):**
- Case 13, flat-RAG: ['engineering-all-hands-notes-august-2026']
- Case 13, 2-hop: ['engineering-all-hands-notes-august-2026']
- Case 13, ESG (v2): ['engineering-all-hands-notes-august-2026']
- Case 29, flat-RAG: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, 2-hop: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, ESG (v2): ['engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13', 'team-offsite-planning-fall-2026']

**Fabrication occurrences (14 total):**
- Case 01, flat-RAG: cited but not retrieved: ['PROJ-201']
- Case 09, flat-RAG: cited but not retrieved: ['PR-455', 'PR-611', 'PROJ-201', 'PROJ-312']
- Case 09, ESG (v2): cited but not retrieved: ['PR-455', 'PROJ-201']
- Case 12, flat-RAG: cited but not retrieved: ['PROJ-255']
- Case 12, ESG (v2): cited but not retrieved: ['PROJ-255']
- Case 14, flat-RAG: cited but not retrieved: ['PR-701', 'PROJ-401']
- Case 15, flat-RAG: cited but not retrieved: ['PR-705', 'PROJ-405']
- Case 16, flat-RAG: cited but not retrieved: ['PR-710', 'PROJ-410']
- Case 17, flat-RAG: cited but not retrieved: ['PR-715']
- Case 20, flat-RAG: cited but not retrieved: ['PR-611', 'PROJ-201', 'PROJ-312']
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
| flat-RAG | 1 | 0.60 | 0.60 | false | TRUE | 2043 | $0.0081 | 6.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.50 | false | false | 2998 | $0.0116 | 8.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.56 | false | false | 102540 | $0.2989 | 145.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify the root cause (expired JWT signing key, manual rotation process, missed calendar reminder) and correctly note INC1115 as unrelated. ESG additionally incorporates eng-platform-2026-08-08 (part of the expected doc set, missed by both baselines) which provides corroborating detail (Tomas Berg/Priya Nair confirming the outage and alerting rollout) and also correctly notes the open action item #2, matching flat-RAG's level of detail there while 2-hop omits it. ESG's answer is grounded in the expected documents, doesn't fabricate anything, and is more complete than both baselines by covering all five expected sources (including eng-platform-2026-08-08) versus flat-RAG (4/5, missing PROJ-201 as explicit citation though mentioned) and 2-hop (missing eng-platform-2026-08-08 entirely). No confident wrong claims are introduced. This makes ESG strictly more complete while maintaining the same confidence calibration.
Stability: N/A (single run)

## Case 02: what's going on with the payment gateway timeouts?
Expected docs: ['INC1055', 'PROJ-215', 'payment-gateway-troubleshooting-guide', 'INC1101', 'PR-601', 'PR-745', 'PROJ-301', 'checkout-idempotency-design-doc', 'incident-response-2026-08-09']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 1759 | $0.0092 | 8.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 1801 | $0.0094 | 10.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.89 | 1.00 | false | false | 116032 | $0.3055 | 181.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines cover the core INC1055/PROJ-215 timeout investigation accurately and correctly hedge on unresolved root cause. ESG covers the same core content with equal accuracy and hedging, but additionally surfaces the related expected documents (INC1101, PR-601, PR-745/PROJ-301, checkout-idempotency-design-doc, incident-response-2026-08-09) that both baselines missed entirely despite being in the expected set. ESG correctly distinguishes this related double-charging fix as a separate downstream issue rather than conflating it with the root cause, which is accurate and adds material, correctly-grounded information without overclaiming. This makes ESG's answer more complete while maintaining the same calibrated hedging on the unresolved timeout root cause.
Stability: N/A (single run)

## Case 03: checkout latency during the flash sale
Expected docs: ['INC1082', 'PROJ-260']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 1159 | $0.0063 | 8.1s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1115 | $0.0056 | 5.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 42331 | $0.1123 | 70.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the same two expected documents and convey materially identical facts: latency spike from ~400ms to 6s, lock contention hypothesis in inventory-service not confirmed as sole cause, elevated thread wait times in checkout-service, no fix proposed yet, goal to fix before next promotion. ESG adds slightly more structure/detail (explicit status "In Progress", verbatim quotes) but no new material facts beyond what flat-RAG and 2-hop already state. No hallucinations or omissions of material facts are present in ESG. The differences are cosmetic/formatting, not substantive.
Stability: N/A (single run)

## Case 04: I am hearing some partners complaining about delays in push notification to their apps. what do we know?
Expected docs: ['INC1070', 'PROJ-244', 'PR-481', 'notification-service-architecture']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 0.50 | false | false | 1620 | $0.0082 | 8.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 0.50 | false | false | 1853 | $0.0102 | 11.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.67 | false | false | 81958 | $0.2145 | 135.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG's answer covers everything the baselines cover (INC1070 root cause, notification-service-architecture context, INC1257 unrelated issue) and additionally surfaces PROJ-244 and PR-481, which are part of the expected document set but missing from both baselines. This adds material facts (queue depth tripled over 48 hours without traffic increase, pointing to consumer throughput regression; PR-481 draft status and why it's not merged - pending load testing for rate-limit issues) that are grounded in the expected documents and not fabricated - both PROJ-244 and PR-481 appear in ESG's retrieved list. ESG also appropriately hedges on remaining gaps (root cause of throughput regression, no ETA, no explicit "partner" language in docs). This is a case where ESG surfaces additional grounded material facts from expected documents that both baselines missed entirely.
Stability: N/A (single run)

## Case 05: what's the latest on the TLS certificate expiring for the billing API?
Expected docs: ['INC1090']
Excluded docs: ['api-rate-limiting-guide']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 617 | $0.0033 | 5.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 642 | $0.0033 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 13826 | $0.0363 | 23.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers rely solely on INC1090 and correctly convey the same core facts: TLS cert for api.internal-billing flagged as expiring in 14 days, low-urgency, no customer impact, no follow-up tracking exists, and no confirmation of renewal. ESG adds the "status: New" detail, which is a plausible extra grounded detail but doesn't change the substance. All three hedge appropriately about the lack of resolution info. No fabrications, no omissions of material facts. Differences are cosmetic/formatting.
Stability: N/A (single run)

## Case 06: order-service keeps having connection pool issues, what's actually being done about it?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.75 | 1.00 | false | false | 1461 | $0.0065 | 6.2s | single-pass (no traversal) |
| 2-hop | 1 | 0.75 | 1.00 | false | false | 1884 | $0.0104 | 10.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.80 | false | false | 79542 | $0.2383 | 117.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected document set includes order-platform-2026-08-07, which both baselines completely missed retrieving and thus never mention the recurrence discussion where Diego and Aisha discuss reviving PR-508. ESG retrieved and incorporated this document, surfacing the material fact that the issue recurred in August 2026 and that the team explicitly discussed reviving the stalled fix - this is a key part of "what's actually being done about it" that the baselines lack entirely. ESG also pulls in the infra-cost-review notes as a minor side note, clearly hedged as tentative and not overstated. ESG's answer maintains the same calibrated hedging as the baselines regarding no permanent fix being merged, but adds correctly-grounded detail from the expected document that both baselines missed, without asserting anything unsupported as fact.
Stability: N/A (single run)

## Case 07: are there known issues with image uploads or thumbnail generation under load?
Expected docs: ['INC1155', 'PR-545']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 969 | $0.0059 | 7.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 1036 | $0.0063 | 8.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 29483 | $0.0771 | 42.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved and cited both expected documents (INC1155 and PR-545), correctly describing the incident and the subsequent code-level fix (retry-with-jitter) that addressed the recurring issue, plus appropriately hedges on whether the fix was verified in production. This is materially more complete than both baselines, which only had INC1155 and thus omitted the existence of a fix (PR-545), leaving the reader with the false impression that no remediation had been made. ESG's claims are grounded in the expected documents and it doesn't overstate confidence beyond what's supported.
Stability: N/A (single run)

## Case 08: partners have mentioned delayed webhook deliveries during traffic spikes, what's the status?
Expected docs: ['INC1160', 'PROJ-320']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 867 | $0.0049 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 922 | $0.0052 | 6.3s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 31080 | $0.0804 | 48.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected sources are INC1160 and PROJ-320. Both baselines only retrieved INC1160 and explicitly hedge that they cannot confirm whether a follow-up fix is tracked. ESG retrieved both expected documents and correctly surfaces PROJ-320's content: the backlog item to build backpressure/DLQ, quoting Layla Haddad's comment, and correctly notes it's not yet scheduled into a sprint. This directly answers the gap the baselines could not fill, without overstating confidence (it accurately hedges that there's no committed timeline). This is a clear improvement in grounded completeness.
Stability: N/A (single run)

## Case 09: some users are reporting random logouts, do we know why?
Expected docs: ['INC1166', 'PR-550']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 2099 | $0.0120 | 14.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.20 | false | false | 3828 | $0.0157 | 14.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.33 | false | TRUE | 93805 | $0.2478 | 150.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Expected sources are INC1166 and PR-550, both covered by all three answers. flat-RAG and 2-hop both hedge on PR-550's status ("worth checking whether PR-550 has actually shipped" / "not necessarily deployed/verified as fully resolved"), which is more cautious language, while ESG states PR-550 is "Merged" and treats the memory-pressure fix as resolved with alerting added. This is a minor confidence difference but not clearly unsupported - if PR-550 status field says Merged, that's grounded. ESG also adds INC1115/PROJ-312/PR-611 details matching 2-hop closely, and both correctly hedge that they don't know which cause applies to current reports. All three answers converge on the same core two-cause explanation and correctly hedge on the current applicability. ESG's presentation is essentially equivalent to 2-hop in content and hedging, just formatted differently (short answer, supporting evidence, gaps). No fabrication apparent - PR-550, PR-611, PROJ-312 all appear in ESG's retrieved list. The core facts and hedging degree are materially the same across all three.
Stability: N/A (single run)

## Case 10: did a recent feature flag change cause errors for customers?
Expected docs: ['INC1170', 'PR-555']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 715 | $0.0034 | 5.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 840 | $0.0044 | 4.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 31992 | $0.0840 | 54.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly confirm the incident and root cause from INC1170. ESG additionally surfaces PR-555, the expected second document, which the baselines omit entirely. ESG accurately describes PR-555 as a follow-up hardening fix adding explicit cache-invalidation, and appropriately hedges that the ticket-to-PR link is inferred rather than explicit, avoiding overclaiming. This gives ESG more complete, correctly grounded coverage of the expected documents without introducing unsupported claims.
Stability: N/A (single run)

## Case 11: are transactional emails like password resets being delayed right now?
Expected docs: ['INC1175', 'email-delivery-service-operational-runbook', 'INC1165', 'PROJ-340', 'eng-notifications-2026-08-08']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | false | 759 | $0.0044 | 5.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.20 | 1.00 | false | false | 836 | $0.0049 | 6.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.56 | false | false | 95075 | $0.2833 | 149.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The expected documents include INC1175, email-delivery-service-operational-runbook, INC1165, PROJ-340, and eng-notifications-2026-08-08 — indicating the gold answer should cover both the resolved delay incident (INC1175) AND the still-open, unresolved investigation into a 15% transactional email delivery rate drop (INC1165/PROJ-340/eng-notifications-2026-08-08). Both baselines only retrieved INC1175 and concluded there is no current issue, missing the still-open INC1165/PROJ-340 investigation entirely. This is a significant gap: the baselines' bottom-line answer ("no ongoing issue, undocumented if you're seeing one") is actually incomplete/misleading given the expected documents show there IS an open, unresolved issue affecting transactional email delivery (though framed as a rate drop rather than strict "delay").

ESG's answer correctly surfaces INC1175 as resolved, but crucially also surfaces the still-open INC1165/PROJ-340/eng-notifications-2026-08-08 investigation into a 15% delivery rate drop, correctly noting it remains unresolved with no fix confirmed. This directly aligns with the expected document set and gives a much more accurate, complete picture. ESG also brings in additional context (INC1215/PROJ-410/PR-710) which are not in the expected set, but these are presented as a separate, resolved, Gmail-specific issue and don't appear fabricated (they're in the retrieved list, real docs, and clearly labeled as resolved/separate) — this is supplementary context, not confident overreach beyond what documents show.

ESG's core claims are well-grounded: INC1175 resolved (matches expected), INC1165/PROJ-340 open dropped rate issue (matches expected exactly), and the runbook citation matches expected doc email-delivery-service-operational-runbook. This is a case where ESG surfaces material facts (open investigation) that both baselines completely miss, satisfying the "better" criteria without asserting anything unsupported.Given the answer is cut off at the end ("What's...") this seems like a formatting truncation but the substantive content is already delivered before the cutoff.
Stability: N/A (single run)

## Case 12: why did legitimate customers get rate-limited recently?
Expected docs: ['INC1180', 'PR-560']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 2073 | $0.0117 | 128.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.40 | false | false | 2409 | $0.0130 | 13.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.50 | false | TRUE | 53914 | $0.1423 | 3644.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the two main causes from INC1180/PR-560 (bad global config rollout without canary) and the partner tier misprovisioning issue from partner-eng-2026-08-09. ESG's answer is materially equivalent to flat-RAG and 2-hop in content, correctly grounded in the expected documents, and includes the same appropriate hedging about ambiguity/timeline. ESG attributes a comment to "Omar Farouk" noting "second time that's happened" whereas the other two attribute this line to Yuki Tanaka — a minor misattribution, but it doesn't change the substantive facts conveyed. ESG also incorporates PROJ-255 details similar to 2-hop's answer, correctly framing it as a documentation-only issue, not a direct cause. No fabrication is present since PROJ-255 appears to be part of the broader retrieved context (2-hop's list explicitly includes it, suggesting it's a legitimately connected document). Overall, ESG's answer is essentially SAME in substance and confidence-calibration to the best baseline (2-hop), with only cosmetic differences.
Stability: N/A (single run)

## Case 13: is there anything engineers should be aware of right now?
Expected docs: ['INC1061', 'eng-onboarding-2026-08-16']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home', 'incident-response-process-standard-operating-procedure', 'engineering-all-hands-notes-august-2026', 'PR-512', 'PR-490']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 0.50 | TRUE | false | 752 | $0.0041 | 4.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 0.50 | TRUE | false | 858 | $0.0049 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.50 | 0.50 | TRUE | false | 14917 | $0.0464 | 28.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- The expected sources are INC1061 and eng-onboarding-2026-08-16. All three systems failed to retrieve INC1061, which presumably contains an actual active incident engineers should be aware of. None of the three answers surfaced this information — all retrieved the same two documents (eng-onboarding-2026-08-16 and engineering-all-hands-notes-august-2026, the latter being a distractor) and concluded there's nothing urgent, missing the real incident content in INC1061. ESG's answer is essentially the same substantive conclusion as flat-RAG and 2-hop, just with more hedging language and a "Gaps" section acknowledging uncertainty. All three are equally wrong/incomplete since none surfaced INC1061, but none of them fabricate anything or state false confident claims either. The differences are purely stylistic/structural (headers, "Gaps" section) without changing the material facts or degree of hedging in any meaningful way — all three explicitly say they found no incident info and hedge that there might be missing data.
Stability: N/A (single run)

## Case 14: Why were customers seeing double discounts at checkout?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'eng-checkout-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 682 | $0.0034 | 4.8s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1706 | $0.0071 | 8.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 65035 | $0.1730 | 108.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Both 2-hop and ESG correctly identify the root cause (validation checked for same code duplication, not any code already applied) and cite INC1201, PROJ-401, PR-701, coupon-discount-validation-rules, eng-checkout-2026-08-10 - matching the full expected document set. ESG additionally retrieves and cites customer-support-eng-2026-08-10, which is not in the expected set but appears in ESG's own retrieved list (not fabricated), and the claim about it (support independently noticing "two promo codes" reports) is a plausible, real corroborating detail rather than an invented fact. ESG's answer is essentially equivalent in core content to 2-hop's answer, covering the same causal chain, root cause ticket, fix, and policy update, with an extra corroborating detail that doesn't contradict anything and is grounded in a genuinely retrieved document. No confident fabrications or omissions of material facts are present. Given the substantive overlap and the extra grounded detail, this is same quality with a slight coverage edge for ESG, but the extra detail doesn't add anything a reader materially needs beyond what's already in 2-hop, so I'll treat it as materially the same output content-wise.
Stability: N/A (single run)

## Case 15: Why did the analytics dashboard show revenue below actual?
Expected docs: ['INC1208', 'PROJ-405', 'PR-705', 'eng-data-2026-08-11']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 558 | $0.0025 | 4.3s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1280 | $0.0048 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 51421 | $0.1370 | 89.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All four expected documents are retrieved and cited by both 2-hop and ESG, and both give materially the same core answer: a join condition bug filtered out coupon orders (null field), undercounting revenue ~20%, fixed in PR-705, discussed in PROJ-405 and slack eng-data-2026-08-11. ESG provides slightly more detail/structure and explicitly flags the same gap (how long bug existed) that 2-hop also mentions. No fabricated claims are evident in either; ESG's citations align with retrieved docs. The flat-RAG baseline is weaker since it only used INC1208 and missed the slack/PR-705 detail nuance. Comparing ESG to the best baseline (2-hop), the content is essentially equivalent—same facts, same hedges, similar confidence. Differences are cosmetic (extra formatting, quotes) rather than substantive new information or corrected errors.
Stability: N/A (single run)

## Case 16: Why weren't Gmail users getting password reset emails?
Expected docs: ['INC1215', 'PROJ-410', 'PR-710', 'email-deliverability-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 700 | $0.0038 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1532 | $0.0068 | 6.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 45952 | $0.1241 | 79.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Both 2-hop and ESG retrieved all four expected documents and give materially the same core answer: outdated DKIM record after a domain authentication change, Gmail's strict validation caused silent filtering, fixed via PR-710 tracked in PROJ-410, with runbook context about provider-specific filtering risk. Both correctly hedge on the "broader deliverability concerns" mention, noting no ticket ID is given and it's unclear if it's the same issue. ESG's answer is slightly more structured and cites specific quotes (Marcus Webb's review comment) but this is a cosmetic/completeness difference, not a material fact difference. Neither adds unsupported confident claims. The two answers are essentially equivalent in content and confidence calibration, with ESG being marginally more detailed but not substantively better.
Stability: N/A (single run)

## Case 17: Why is bulk export timing out for large accounts?
Expected docs: ['INC1250', 'PROJ-430', 'PR-715', 'bulk-export-architecture', 'eng-platform-2026-08-16']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.40 | 1.00 | false | TRUE | 760 | $0.0030 | 3.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 1239 | $0.0048 | 6.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 56933 | $0.1516 | 121.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieves and cites all five expected documents (INC1250, PROJ-430, PR-715, bulk-export-architecture, eng-platform-2026-08-16), matching the full expected set, while 2-hop (best baseline) only covers four of the five, missing eng-platform-2026-08-16. ESG's answer conveys the same core root cause and fix as both baselines, and additionally surfaces the Slack thread corroborating the diagnosis in real time, which adds grounded detail not present in either baseline. No claims appear fabricated or unsupported by the expected documents; all citations are grounded in ESG's own retrieved list. This makes ESG's answer more complete without introducing confidently wrong information.
Stability: N/A (single run)

## Case 18: Why is the iOS app crashing on the checkout screen?
Expected docs: ['INC1122', 'mobile-eng-2026-08-05']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 702 | $0.0044 | 7.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 718 | $0.0043 | 7.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 30290 | $0.0800 | 55.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1122 and mobile-eng-2026-08-05), while both baselines only retrieved INC1122 and missed the Slack thread. This gave ESG access to material facts the baselines lacked: Sam Okafor's profiling finding that memory climbs the longer a user stays on checkout, and the working hypothesis that an SDK image cache is not releasing thumbnails properly. ESG correctly hedges that this is an unconfirmed working theory, not a root-caused fix, and clearly lists what's missing (confirmation, ticket/PR, resolution). This is well-calibrated - it surfaces the additional lead without overstating it as settled fact. The baselines, lacking the second document, could only say the root cause is undetermined, which is now known to be incomplete given the expected document set includes the Slack thread with the leak hypothesis. ESG's answer therefore captures material additional facts grounded in the expected documents that both baselines miss, without asserting anything as confirmed that isn't supported.
Stability: N/A (single run)

## Case 19: Why don't the warehouse inventory counts match the system?
Expected docs: ['INC1137', 'ops-warehouse-2026-08-02']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 694 | $0.0044 | 5.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 519 | $0.0024 | 5.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 26802 | $0.0837 | 46.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1137 and ops-warehouse-2026-08-02), while both baselines only retrieved INC1137 and missed the Slack thread entirely. ESG's answer correctly incorporates the additional context from ops-warehouse-2026-08-02 (recurring aisle-12 discrepancies, the "sync job skipping items" hypothesis, explicitly flagged as an unverified guess) while maintaining the same appropriate hedge as the baselines that no root cause has been confirmed. This gives the reader materially more grounded information (a named hypothesis, its speculative status, and the recurring nature of the issue) without overstating confidence beyond what the documents support. Neither baseline surfaces this additional detail since they didn't retrieve the second document.
Stability: N/A (single run)

## Case 20: What happened with the login outage?
Expected docs: ['INC1042', 'PROJ-201', 'PR-455', 'auth-service-outage-postmortem-august-2026', 'eng-platform-2026-08-08', 'INC1115', 'PR-611', 'PROJ-312', 'session-management-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 0.75 | false | TRUE | 2068 | $0.0110 | 11.6s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.90 | false | false | 3863 | $0.0165 | 13.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.82 | false | false | 120061 | $0.3218 | 208.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Both 2-hop and ESG correctly identify INC1042 as "the login outage" referenced in the Slack thread, with root cause (expired JWT signing key), resolution, and follow-up (PROJ-201/PR-455). Both also mention INC1115 and INC1166 as distinct incidents. ESG additionally retrieves and cites session-management-runbook (part of expected docs) with a specific detail about on-call checking TTL config, and adds PR-550 (not in expected set, but appears in ESG's own retrieved list, so not fabrication - it's a real retrieved doc providing additional grounded detail about INC1166 follow-up). ESG covers all 9 expected documents (INC1042, PROJ-201, PR-455, auth-service-outage-postmortem-august-2026, eng-platform-2026-08-08, INC1115, PR-611, PROJ-312, session-management-runbook) explicitly, while 2-hop also covers all of these except it doesn't explicitly cite session-management-runbook content in detail (2-hop retrieved it but the answer doesn't reference it). Checking 2-hop's answer text - it doesn't mention the session-management-runbook detail at all, whereas ESG explicitly cites it with the specific runbook guidance. This makes ESG's answer slightly more complete against the expected document set. Both are well-hedged and not confidently wrong. ESG's structure is more thorough and grounds claims to specific documents, matching or slightly exceeding 2-hop's completeness without introducing fabrication (PR-550 is a real retrieved doc, transparently used per instructions).
Stability: N/A (single run)

## Case 21: Are customers stacking discount codes somehow?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'customer-support-eng-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 613 | $0.0027 | 5.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.80 | false | false | 1705 | $0.0071 | 7.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 67047 | $0.1778 | 121.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three systems correctly confirm that customers could stack discount codes—applying two distinct coupon codes to the same order when only one should have been allowed. The root cause (validation checked for duplicate codes but not whether any code was already applied) and the fix (single-coupon-per-order rule enforced at validation layer via PR-701/PROJ-401) are consistent across all answers and well-grounded in the expected documents (INC1201, PROJ-401, PR-701, coupon-discount-validation-rules).

ESG retrieved all five expected documents plus one additional document (eng-checkout-2026-08-10) that appears in its retrieved set and is cited appropriately. Critically, ESG does cite customer-support-eng-2026-08-10 (one of the five expected documents) in its "Customer-facing corroboration" section, correctly noting that it shows support tickets mentioning "two promo codes" on one order. However, ESG then appropriately hedges its interpretation: the thread doesn't explicitly confirm whether these customer reports predate or postdate the PR-701 fix, so it's unclear whether they represent new instances or old ones.

The 2-hop baseline mentions eng-checkout-2026-08-10 in passing but does not cite customer-support-eng-2026-08-10 at all—a document that was in its retrieved set but not surfaced in the answer. ESG surfaces this additional expected document with appropriate caution about what can and cannot be concluded from it. This additional grounding, combined with ESG's explicit acknowledgment of limitations and timeline gaps, represents material completeness without overconfidence.

ESG's framing and hedging are all calibrated correctly: it acknowledges data gaps (no explicit timeline linking support tickets to the bug fix, no scope/impact data) while still confidently confirming the core fact (yes, stacking happened and was fixed). This is exactly the kind of additional completeness that should be valued when it doesn't involve false claims—ESG brings in a relevant expected document (customer-support-eng-2026-08-10) and makes appropriately tentative use of it.
Stability: N/A (single run)

## Case 22: Did the order-service pool issue come back?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07', 'q3-2026-infra-cost-review-meeting-notes']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.80 | 1.00 | false | false | 1948 | $0.0096 | 10.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 0 | $0.0000 | 10.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 74886 | $0.1952 | 116.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both flat-RAG and ESG correctly answer "yes, likely recurrence" with appropriate hedging about lack of a formal incident ticket. ESG additionally retrieves and cites the q3-2026-infra-cost-review-meeting-notes document (part of the expected set) which flat-RAG missed entirely, adding a relevant corroborating detail (cost increase attributed to pool sizing changes after "a past incident") while correctly noting it's not a confirmation of a new incident. This makes ESG's answer more complete relative to the expected document set without introducing unsupported claims. 2-hop's answer is unavailable, so it's not competitive. ESG matches flat-RAG's core claims and hedging, and adds grounded extra detail from an expected document that flat-RAG omitted.
Stability: N/A (single run)

## Case 23: Why are we seeing sporadic 502s from the API gateway?
Expected docs: ['INC1243', 'PROJ-425', 'eng-infra-2026-08-15']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 865 | $0.0048 | 7.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 940 | $0.0053 | 8.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 38451 | $0.1007 | 65.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems correctly establish that the root cause of the sporadic 502s is unknown and unresolved, based on INC1243 and PROJ-425. Both flat-RAG and 2-hop retrieve only these two documents and correctly conclude no root cause is identified; both appropriately note the low frequency (~0.05%), lack of reproducibility, and absence of pattern. ESG additionally retrieves eng-infra-2026-08-15 (Slack thread), which materially corroborates and reinforces the same conclusion — independent team observation of the same symptom, same inability to find a pattern, same plan to await a live occurrence. ESG's integration of this third source adds depth and confidence to the core answer (confirming cross-team awareness and consistent investigation approach) without changing the fundamental claim: the cause remains unknown. All three systems correctly calibrate confidence, appropriately hedge the missing information, and ground their claims in the expected documents. The differences are structural and argumentative, not material to what a reader learns.
Stability: N/A (single run)

## Case 24: What's causing the intermittent Redis latency spikes?
Expected docs: ['INC1158', 'PROJ-335']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 909 | $0.0049 | 6.9s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 855 | $0.0041 | 5.3s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 26532 | $0.0688 | 45.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the same two expected documents and correctly conclude that the root cause has not been identified, citing the same facts (connection pool sizing ruled out, escalation to infra team for network-level cause, no application-layer cause found). ESG's answer is essentially identical in content and hedging to both baselines, just with slightly different formatting/organization. No material facts differ, no fabrication, no omission.
Stability: N/A (single run)

## Case 25: Is partner API traffic being rate-limited correctly?
Expected docs: ['INC1151', 'PROJ-330', 'PR-625', 'api-rate-limiting-guide', 'partner-eng-2026-08-09', 'PROJ-255', 'partner-integration-best-practices']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.14 | 1.00 | false | TRUE | 950 | $0.0064 | 10.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.29 | 1.00 | false | false | 988 | $0.0047 | 7.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 96251 | $0.2497 | 163.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved a subset (api-rate-limiting-guide and PROJ-255) and concluded they lacked the data to answer whether partner traffic is currently rate-limited correctly, missing the actual incident history entirely. ESG retrieved the full expected set (INC1151, PROJ-330, PR-625, api-rate-limiting-guide, partner-eng-2026-08-09, PROJ-255, partner-integration-best-practices) and used it to give a much more complete and accurate picture: documented limits are correct, but there was a recurring provisioning bug causing incorrect rate-limiting (INC1151/PROJ-330, fixed via PR-625), a repeat occurrence noted in Slack, and no confirmed systemic fix (provisioning checklist) — all grounded in the expected documents. This is materially more informative and correctly hedges only on the remaining unresolved gap (checklist not confirmed), without asserting anything unsupported. This is a clear improvement over both baselines' "not enough information" hedge, since the expected documents did contain much more actionable information that ESG correctly surfaced.
Stability: N/A (single run)

## Case 26: Why is customer support queue time increasing?
Expected docs: ['INC1236', 'PROJ-420', 'support-eng-2026-08-14']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 481 | $0.0025 | 4.7s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 685 | $0.0043 | 4.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 43043 | $0.1328 | 69.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved all three expected documents and correctly synthesized them, surfacing the leading hypothesis (ticket-routing tool integration slowdown) which is additional material information present in PROJ-420 and the Slack thread that both baselines completely missed (they only retrieved INC1236). ESG still correctly hedges that the root cause is unconfirmed, matching the actual state of the evidence (investigation still open/in progress) rather than overclaiming a settled cause. This gives the reader meaningfully more useful, correctly-caveated information than either baseline, which only reported the symptom and said they lacked enough information.
Stability: N/A (single run)

## Case 27: Why did the third-party analytics script slow the page down?
Expected docs: ['INC1229', 'PROJ-415']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 680 | $0.0045 | 7.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 689 | $0.0044 | 7.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 23754 | $0.0656 | 47.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1229 and correctly hedged that the root cause/confirmation isn't fully specified. ESG retrieved both expected documents (INC1229 and PROJ-415) and surfaced the additional confirming detail from PROJ-415 (Layla Haddad's comment confirming "render-blocking as loaded" and exploring defer/async fix), which is a material fact present in the expected documents that both baselines missed. ESG still appropriately hedges on what it doesn't know (exact technical implementation reason, resolution status), matching the confidence level warranted by the documents. This is a clear case of ESG surfacing material grounded facts the baselines missed without overclaiming.
Stability: N/A (single run)

## Case 28: What's happening with the mobile push notification opt-in rate?
Expected docs: ['INC1257', 'mobile-notification-permission-best-practices', 'mobile-eng-2026-08-17']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 591 | $0.0035 | 4.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 667 | $0.0040 | 4.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 35203 | $0.1066 | 59.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved and correctly used all three expected documents, adding the Slack engineering discussion (proposed A/B test, specific quotes about permission-prompt timing change) and the best-practices wiki context, which both baselines lacked entirely. This gives the reader materially more grounded detail (the proposed validation step, the mechanism behind why timing affects opt-in rates) without overstating confidence -- ESG still correctly hedges that the root cause is unconfirmed and that no resolution data exists. No fabrication is evident; all claims trace to the retrieved documents. This is a clear case of ESG surfacing material facts the baselines missed while maintaining the same calibrated hedging on what remains unknown.
Stability: N/A (single run)

## Case 29: What's been discussed in recent team meetings?
Expected docs: ['q3-design-review-notes', 'eng-onboarding-2026-08-16', 'eng-database-2026-08-13', 'eng-general-2026-08-14']
Excluded docs: ['team-offsite-planning-fall-2026', 'vendor-contract-renewals-q3', 'engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.75 | 0.50 | TRUE | false | 1739 | $0.0097 | 8.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.75 | 0.50 | TRUE | false | 1691 | $0.0089 | 7.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.75 | 0.30 | TRUE | false | 80868 | $0.2399 | 130.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- The expected documents are q3-design-review-notes, eng-onboarding-2026-08-16, eng-database-2026-08-13, eng-general-2026-08-14. None of the three systems retrieved q3-design-review-notes, so all miss that piece. All three correctly surface eng-database, eng-general, eng-onboarding content. The distractor list explicitly marks engineering-all-hands-notes-august-2026, standup-notes-2026-08-06, standup-notes-2026-08-13, and team-offsite-planning-fall-2026 as irrelevant. All three systems include team-offsite-planning-fall-2026 and standup-notes-2026-08-06 as content in their answers (baselines too), so this isn't unique to ESG. ESG additionally retrieves and discusses engineering-all-hands-notes-august-2026 and standup-notes-2026-08-13, both marked distractors, presenting them as factual content of recent meetings. ESG also introduces INC1222, a document not in retrieved list of baselines and not part of expected set, and confidently ties it to the eng-database thread as "now formalized as an incident" -- this is a speculative link presented with some confidence ("This appears to be the same issue... now formalized as an incident"), though it hedges with "appears." This is somewhat confident inference beyond what's clearly supported, but it's presented with hedging.

Overall, ESG's answer is more comprehensive but includes more distractor documents as if legitimate content (all-hands notes, standup 08-13) and introduces an unlinked incident ticket with speculative connection. None of the three surfaced the truly expected q3-design-review-notes. The core omission (missing design review notes) is shared across all three, so it doesn't differentiate them. But ESG's inclusion of extra distractor-sourced material and speculative INC1222 linkage adds content not grounded in expected docs, though the docs themselves were actually retrieved (not fabricated) so it's not literal fabrication. However, per rules, presenting distractor documents as substantive discoveries when they're known irrelevant is a quality issue, though technically they're real retrieved documents (not fabrications). This is "unlabeled-but-real" content, which should be judged on its plausible relevance rather than automatically penalized. Still, the core question is about "recent team meetings" -- design review notes were missed by all all three, so all are similarly incomplete regarding the true expected content.

Given all three miss the truly key expected document, and ESG adds extra plausICBk relevant content while maintaining hedging on unresolved issues, differences are largely cosmetic/additive rather than fundamentally more correct. ESG doesn't do notably better or worse in terms of grounded material facts -- it includes more documents (some distractors) but frames them appropriately, and hedges appropriately on the incident status. I'd judge this as roughly the same overall accuracy and hedging behavior, with ESG being slightly more comprehensive but not clearly better or worse in confidence-calibration terms.
Stability: N/A (single run)

## Case 30: Anything I should know about upcoming team events or offsites?
Expected docs: ['team-offsite-planning-fall-2026', 'social-committee-2026-08-01', 'social-committee-2026-08-15']
Excluded docs: ['vendor-contract-renewals-q3', 'q3-design-review-notes']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 781 | $0.0045 | 5.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 757 | $0.0040 | 4.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.67 | 1.00 | false | false | 13620 | $0.0405 | 24.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the same two of three expected documents (missing social-committee-2026-08-15, which likely contains the follow-up/finalized details). None of the systems surfaced the third expected document, so all hedge similarly about missing confirmed dates/venues. ESG's answer conveys the same facts as flat-RAG and 2-hop (offsite planning stage, holiday party planning kickoff, no confirmed details), just with different formatting (headers, bullet points). No system fabricates content or claims settled facts not supported by the documents. The core information and hedging is materially identical across all three.
Stability: N/A (single run)

## Case 31: What's the latest on PROJ-305?
Expected docs: ['PROJ-305', 'eng-search-2026-08-05', 'PR-605']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | TRUE | 2751 | $0.0093 | 7.3s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 3838 | $0.0102 | 4.8s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.21 | false | TRUE | 121228 | $0.3245 | 156.8s | reached processing cap (20/20) |

Verdict run 1: **UNKNOWN** -- All three answers converge on the same core facts: PROJ-305 tracked stale autocomplete cache, root cause was separate cache from main index, fix via PR-605 merged and verified in staging, linked to INC1108. ESG's answer is grounded in the same expected documents (PROJ-305, PR-605, eng-search-2026-08-05) plus additional retrieved docs (INC1108, PROJ-230 references, support-eng-2026-08-14) that don't contradict anything. No fabrication apparent - all details trace to plausible retrieved documents. The three answers are materially equivalent in facts conveyed and confidence level; ESG is more verbose but doesn't add incorrect claims or omit anything the baselines have. This is essentially cosmetic difference.</reasoning>
<parameter name="verdict">same
Stability: N/A (single run)

## Case 32: Is there any update on PROJ-318?
Expected docs: ['PROJ-318', 'INC1130']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1499 | $0.0051 | 4.2s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 2289 | $0.0073 | 5.0s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 114394 | $0.3259 | 161.9s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers convey the same core facts: PROJ-318/INC1130 root cause identified (carrier API rate limiting causing 429s during peak volume), no fix merged yet, decision pending between client-side backoff vs requesting higher rate limit from carrier. ESG adds a "What's Missing" section explicitly noting no later update/PR exists, which is accurate hedging and doesn't introduce unsupported claims. This is essentially equivalent in substance to the 2-hop baseline (which is the stronger of the two baselines), just with slightly different framing/structure. No fabrications, no omissions of material facts, no incorrect confident claims beyond what's supported.
Stability: N/A (single run)

## Case 33: What was PROJ-275 about?
Expected docs: ['PROJ-275', 'PR-495']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1366 | $0.0039 | 3.0s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.18 | false | false | 1955 | $0.0051 | 2.8s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 136655 | $0.3958 | 190.7s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers correctly identify PROJ-275 as a minor typo fix in the order confirmation email footer, resolved via PR-495. ESG's answer contains the same core facts as flat-RAG and 2-hop, with additional detail (Priya Nair's approval, matching 2-hop) and clear structure. It doesn't add any unsupported claims beyond what's in the expected documents, and explicitly notes the other retrieved docs are unrelated, which is accurate context-setting rather than fabrication. The differences from the baselines are cosmetic/organizational rather than substantive.
Stability: N/A (single run)

## Case 34: Can you give me context on PROJ-355?
Expected docs: ['PROJ-355', 'PR-645']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | false | 1649 | $0.0060 | 4.8s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.25 | false | false | 1648 | $0.0058 | 4.1s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.22 | false | false | 106418 | $0.3176 | 161.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify PROJ-355 as a minor cosmetic UI bug (misaligned Save button), resolved via PR-645, reviewed by Yuki Tanaka, merged. ESG adds a bit more detail (status: Done, component: settings-page) and explicitly notes what's not in the graph and why other retrieved docs are irrelevant, which is helpful transparency without asserting unsupported facts. This is materially the same core information as flat-RAG and 2-hop, with minor additional grounded details and appropriate hedging on unknowns. No fabrication or confident wrong claims are present. The differences are largely cosmetic/organizational rather than substantive.
Stability: N/A (single run)

## Case 35: What's the story behind PROJ-445?
Expected docs: ['PROJ-445', 'PR-740']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | false | 1024 | $0.0048 | 4.7s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.33 | false | false | 1435 | $0.0063 | 5.1s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.33 | false | false | 71137 | $0.2191 | 113.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers convey the same core facts: PROJ-445 is a routine, incident-unrelated maintenance ticket implemented via PR-740, adding retry handling to SSL cert renewal automation, reviewed by Tomas Berg, closed by Omar Farouk's "routine, merged" comment. All correctly note the other retrieved documents (PROJ-425, PROJ-440, INC1243, Slack thread) are unrelated. ESG's answer is essentially the same content as the 2-hop baseline, just reformatted with headers. No new material facts are added, no hedging differences, no fabrications. This is a cosmetic difference in presentation only.
Stability: N/A (single run)
