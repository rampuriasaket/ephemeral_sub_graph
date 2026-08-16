# Output A -- internal diagnostic report (run_3 only)

**Single-run data.** Stability fields (STABLE/UNSTABLE, mean+/-spread) require run_2 and run_3 to be meaningful -- not faked here, left as 'N/A (single run)' throughout. Re-run this generator once run_2/run_3 exist to fill them in.

## Aggregate summary

Verdict tally (run_3): better: 18, same: 16, worse: 1
Verdict stability: N/A (single run) -- requires run_2/run_3.

**Excl.hit occurrences (6 total):**
- Case 13, flat-RAG: ['engineering-all-hands-notes-august-2026']
- Case 13, 2-hop: ['engineering-all-hands-notes-august-2026']
- Case 13, ESG (v2): ['engineering-all-hands-notes-august-2026']
- Case 29, flat-RAG: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, 2-hop: ['standup-notes-2026-08-06', 'team-offsite-planning-fall-2026']
- Case 29, ESG (v2): ['engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13', 'team-offsite-planning-fall-2026']

**Fabrication occurrences (15 total):**
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
- Case 31, flat-RAG: cited but not retrieved: ['PR-470', 'PROJ-230']
- Case 31, ESG (v2): cited but not retrieved: ['PR-470', 'PROJ-230']
- Case 35, flat-RAG: cited but not retrieved: ['INC1243']

---

## Case 01: why did auth-service go down?
Expected docs: ['INC1042', 'PROJ-201', 'PR-455', 'auth-service-outage-postmortem-august-2026', 'eng-platform-2026-08-08']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home', 'incident-response-process-standard-operating-procedure']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.60 | 0.60 | false | TRUE | 2380 | $0.0115 | 10.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.50 | false | false | 2886 | $0.0104 | 7.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.56 | false | false | 100839 | $0.2956 | 149.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify the root cause (expired JWT signing key, manual calendar-reminder rotation process) and the fix (PR-455/PROJ-201), and all correctly note INC1115 as a separate unrelated issue. ESG additionally retrieves and cites eng-platform-2026-08-08 (an expected document that neither baseline retrieved or cited), using it to corroborate the calendar-reminder root cause with a Slack quote from Tomas Berg. This adds a materially grounded detail from an expected source that both baselines missed entirely. ESG's claims are all consistent with the expected documents (INC1042, PROJ-201, PR-455, postmortem, eng-platform-2026-08-08) and it doesn't fabricate anything - PROJ-312 and session-management-runbook are in ESG's own retrieved list, so they are unlabeled-but-real, not fabricated. ESG's answer is thus more complete than flat-RAG and roughly equivalent to 2-hop but with the added eng-platform-2026-08-08 grounding, making it strictly more complete without introducing errors.
Stability: N/A (single run)

## Case 02: what's going on with the payment gateway timeouts?
Expected docs: ['INC1055', 'PROJ-215', 'payment-gateway-troubleshooting-guide', 'INC1101', 'PR-601', 'PR-745', 'PROJ-301', 'checkout-idempotency-design-doc', 'incident-response-2026-08-09']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 1740 | $0.0090 | 8.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 1772 | $0.0091 | 7.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.89 | 1.00 | false | false | 114754 | $0.3013 | 176.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines correctly cover INC1055/PROJ-215/troubleshooting guide with appropriate hedging on unconfirmed root cause. ESG covers the same core content but additionally surfaces the related, expected documents (INC1101, PR-601, PR-745/PROJ-301, checkout-idempotency-design-doc, incident-response-2026-08-09) that the baselines missed entirely despite being in the expected set. ESG correctly distinguishes the still-open timeout issue from the resolved double-charging consequence, and clearly flags what remains unknown. This gives the reader materially more grounded information without overstating confidence on the unresolved parts. No evidence of fabrication - all cited docs are in ESG's retrieved list.
Stability: N/A (single run)

## Case 03: checkout latency during the flash sale
Expected docs: ['INC1082', 'PROJ-260']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 1200 | $0.0067 | 6.5s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1218 | $0.0067 | 6.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 42354 | $0.1126 | 71.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the same two expected documents and convey materially identical facts: the latency spike details, the unconfirmed lock-contention hypothesis, the elevated thread wait times in checkout-service, and the lack of a confirmed root cause or fix. ESG's answer is essentially the same content, just reorganized with more granular sourcing labels (e.g., "servicenow:INC1082:0"). No new material facts are added, and no incorrect claims are introduced. The differences are purely cosmetic/formatting (headers, "Short Answer" vs prose, explicit quote blocks).
Stability: N/A (single run)

## Case 04: I am hearing some partners complaining about delays in push notification to their apps. what do we know?
Expected docs: ['INC1070', 'PROJ-244', 'PR-481', 'notification-service-architecture']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 0.50 | false | false | 1796 | $0.0099 | 9.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 0.50 | false | false | 1797 | $0.0097 | 10.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.57 | false | false | 92079 | $0.2402 | 152.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify INC1070 as the active delay incident and correctly distinguish the unrelated INC1257 opt-in issue. However, ESG additionally surfaces PROJ-244 (the Jira ticket tracking root-cause investigation, including the finding that queue depth tripled without corresponding traffic increase, pointing to a throughput regression rather than pure load growth) and PR-481 (the specific draft PR details, including that it needs load testing to avoid rate-limit issues with the push-notification-provider). These are part of the expected document set and add materially useful, correctly-grounded detail (ticket IDs, owner, specific root-cause hypothesis) that both baselines explicitly flag as "missing" (they note no Jira story ID/PR ID is available). ESG also maintains appropriate hedging on what remains unknown (no confirmed root cause beyond hypothesis, no ETA, no explicit partner-incident link). No fabricated claims are evident; all citations align with ESG's retrieved list and the expected gold set. Thus ESG provides strictly more grounded, accurate information than either baseline without overstating confidence.
Stability: N/A (single run)

## Case 05: what's the latest on the TLS certificate expiring for the billing API?
Expected docs: ['INC1090']
Excluded docs: ['api-rate-limiting-guide']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 641 | $0.0036 | 5.1s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 648 | $0.0034 | 5.3s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 13886 | $0.0368 | 24.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers are grounded in INC1090 and convey the same core facts: TLS cert for api.internal-billing expiring in 14 days, low-urgency, no customer impact, no follow-up documented. All three correctly hedge that resolution/renewal status is unknown. ESG adds slightly more structure and explicit note about "status: New" and "search frontier exhausted" but this doesn't add new material facts beyond the baselines. No fabrications, no confidently wrong claims. Differences are cosmetic/formatting only.
Stability: N/A (single run)

## Case 06: order-service keeps having connection pool issues, what's actually being done about it?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.75 | 1.00 | false | false | 1674 | $0.0086 | 10.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.75 | 1.00 | false | false | 1593 | $0.0075 | 7.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.80 | false | false | 83450 | $0.2460 | 127.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify the core facts from INC0980, the runbook, and PR-508: manual mitigation only, no permanent fix merged, PR-508 stalled/exploratory. ESG additionally surfaces the order-platform-2026-08-07 Slack thread, which is part of the expected document set that both baselines missed entirely. This document adds materially important information: the problem recurred in August 2026, and there's explicit confirmation from Diego that the fix "just the manual bump" and the PR "not gone anywhere yet," plus Aisha's suggestion to revive the PR. This directly answers the question's implicit premise ("keeps having connection pool issues" - plural occurrences) which neither baseline addresses since they only found the single INC0980 incident. ESG's answer is grounded in the expected documents and doesn't overstate anything - it appropriately hedges on whether the PR was ever revived after August. The extra citation of q3-2026-infra-cost-review-meeting-notes is not in the expected set but is retrieved (not fabricated) and is treated appropriately as tangential/consistent context, not overstated as remediation. ESG's answer is more complete and accurate relative to the expected documents, capturing the recurrence pattern that better matches the question's framing of an ongoing/recurring issue.
Stability: N/A (single run)

## Case 07: are there known issues with image uploads or thumbnail generation under load?
Expected docs: ['INC1155', 'PR-545']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 1028 | $0.0064 | 7.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 942 | $0.0053 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 29619 | $0.0785 | 42.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines correctly surface INC1155 with accurate details but explicitly state they lack any corroborating fix/follow-up ticket. ESG additionally retrieves and incorporates PR-545, which per the expected document set is a required source, and correctly reports it as a hardening fix (retry-with-jitter) addressing the recurring resize-worker burst issue, while appropriately hedging on whether it was deployed in direct response to INC1155 or fully resolved the issue. This gives the reader the more complete, still well-calibrated picture that matches the expected documents (INC1155 + PR-545), which neither baseline achieved.
Stability: N/A (single run)

## Case 08: partners have mentioned delayed webhook deliveries during traffic spikes, what's the status?
Expected docs: ['INC1160', 'PROJ-320']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 870 | $0.0049 | 6.7s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 1039 | $0.0063 | 7.9s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 33572 | $0.0872 | 50.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1160 and correctly noted they lacked information about a follow-up fix ticket, hedging appropriately. ESG retrieved both expected documents (INC1160 and PROJ-320) and surfaced the material fact that a follow-up fix (PROJ-320) exists in the backlog but is unscheduled, which is exactly the gap the baselines flagged as missing. This is a case where the expected documents actually contain the answer (PROJ-320) and ESG correctly surfaced it while still appropriately hedging on the exact timeline. ESG's claims appear well-grounded in the expected documents and it does not overstate certainty beyond what's supported.
Stability: N/A (single run)

## Case 09: some users are reporting random logouts, do we know why?
Expected docs: ['INC1166', 'PR-550']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 2110 | $0.0121 | 13.6s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.20 | false | false | 3862 | $0.0160 | 14.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.33 | false | TRUE | 91565 | $0.2435 | 139.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the two root causes (INC1166 session-store eviction, INC1115/PROJ-312 TTL regression) and appropriately hedge about which applies to current reports. ESG's answer says "Both have been fixed" - which is slightly overconfident regarding INC1166/PR-550, since the incident notes say prior mitigations were one-off and PR-550 adds alerting/tuning as "closest thing to a durable fix" but ESG's short answer summary states "Both have been fixed, though one fix is a permanent guard and the other is a manual/reactive mitigation" - this is a bit garbled/contradictory (says both fixed, then says one is manual/reactive, which contradicts "fixed"). But then in supporting evidence it clarifies PR-550 as the fix for INC1166's cause and PR-611 for INC1115. This matches flat-RAG and 2-hop's characterization closely. All three convey the same core facts and hedge similarly about not knowing the current symptom. ESG explicitly also notes the JWT rotation is ruled out, an extra detail not harmful. Overall ESG's answer is basically same substance as 2-hop's answer, just reorganized. No fabrication - PR-611, PROJ-312 are in retrieved list and relevant. This is materially the same as the 2-hop answer (which was the more complete baseline), with same hedging degree, just different structure/formatting.
Stability: N/A (single run)

## Case 10: did a recent feature flag change cause errors for customers?
Expected docs: ['INC1170', 'PR-555']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 749 | $0.0038 | 5.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 743 | $0.0034 | 3.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 32247 | $0.0864 | 56.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1170 and correctly describe the incident. ESG additionally retrieved PR-555 (one of the two expected documents) and incorporates it accurately, noting the follow-up fix while appropriately hedging about the lack of a formal ticket link between PR-555 and INC1170. This is a more complete answer grounded in the full expected document set, without asserting unsupported claims. The added caveats show good calibration rather than overclaiming.
Stability: N/A (single run)

## Case 11: are transactional emails like password resets being delayed right now?
Expected docs: ['INC1175', 'email-delivery-service-operational-runbook', 'INC1165', 'PROJ-340', 'eng-notifications-2026-08-08']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | false | 851 | $0.0053 | 5.9s | single-pass (no traversal) |
| 2-hop | 1 | 0.20 | 1.00 | false | false | 774 | $0.0043 | 5.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.56 | false | false | 99908 | $0.2943 | 156.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1175 and correctly reported it as a resolved past incident, hedging on whether current delays are occurring, but they miss the additional open thread (INC1165/PROJ-340/eng-notifications-2026-08-08) which is part of the expected document set and directly relevant to "right now" status. ESG retrieved and synthesized all the expected documents (INC1175, email-delivery-service-operational-runbook, INC1165, PROJ-340, eng-notifications-2026-08-08) plus some extras (INC1215, PR-710, PROJ-410, email-deliverability-runbook) that appear to be real retrieved/related documents, not fabrications. ESG correctly distinguishes between the resolved delay incident and the separate still-open delivery-rate-drop issue, giving a more complete and accurate picture without asserting anything unsupported — it still hedges appropriately about lack of timestamp certainty. This is a materially more complete and correctly-grounded answer than either baseline, which is missing the important open incident entirely.
Stability: N/A (single run)

## Case 12: why did legitimate customers get rate-limited recently?
Expected docs: ['INC1180', 'PR-560']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 2037 | $0.0113 | 9.9s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.40 | false | false | 2246 | $0.0113 | 12.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.50 | false | TRUE | 53945 | $0.1426 | 86.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the two causes grounded in INC1180 and PR-560 (global config push without canary, and partner tier misprovisioning). ESG cites PROJ-255, which was not in its own retrieved-documents list (only INC1180, PR-560, api-rate-limiting-guide, partner-eng-2026-08-09 were retrieved) — this is a true fabrication of a citation not actually retrieved by ESG. However, this mirrors the 2-hop baseline which did retrieve PROJ-255 legitimately. ESG's content otherwise matches flat-RAG and 2-hop closely in substance, hedging appropriately about gaps. The core facts about why customers were rate-limited (both causes) are correctly conveyed, materially the same as best baseline (2-hop). The PROJ-255 citation issue is a minor flaw since flat-RAG also references PROJ-255 in its answer without retrieving it as a separate ID (it's mentioned inside the api-rate-limiting-guide summary, not cited as its own doc) - so ESG's citing PROJ-255 as a distinct document it did not retrieve is a fabrication, but the informational content is still consistent with what the expected documents support (the guide document likely mentions PROJ-255 as the ticket number). This is a minor labeling issue rather than a substantive factual error. Overall, ESG's answer conveys the same material facts as the best baseline (2-hop), with equivalent hedging and detail.
Stability: N/A (single run)

## Case 13: is there anything engineers should be aware of right now?
Expected docs: ['INC1061', 'eng-onboarding-2026-08-16']
Excluded docs: ['new-hire-onboarding-engineering-wiki-home', 'incident-response-process-standard-operating-procedure', 'engineering-all-hands-notes-august-2026', 'PR-512', 'PR-490']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.00 | 0.00 | TRUE | false | 707 | $0.0037 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.00 | 0.00 | TRUE | false | 722 | $0.0035 | 4.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.50 | 0.50 | TRUE | false | 14955 | $0.0468 | 30.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- The expected sources include INC1061, which none of the three systems actually retrieved (all retrieved only eng-onboarding-2026-08-16 and engineering-all-hands-notes-august-2026). Since none of the systems surfaced INC1061, all three miss the actual answer content. All three answers are essentially the same: they correctly report that the retrieved documents contain no actionable incident info, and hedge that they cannot confirm one way or the other. ESG's answer is slightly more elaborate in structure ("What's Missing" section) but conveys the same substantive information and same degree of hedging as flat-RAG and 2-hop. No system fabricates anything, and none surfaces INC1061. Differences are cosmetic/formatting only.
Stability: N/A (single run)

## Case 14: Why were customers seeing double discounts at checkout?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'eng-checkout-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 645 | $0.0030 | 3.4s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1741 | $0.0074 | 8.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 65030 | $0.1721 | 105.3s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- Both 2-hop and ESG correctly identify the root cause (validation only checked same-code duplication, not any-code) and cite all five expected documents. ESG additionally retrieved and cited customer-support-eng-2026-08-10, a real document from its own retrieval list, adding corroborating detail (customer support tickets mentioning two promo codes) that is plausible and not fabricated. ESG's answer is essentially equivalent in core content to 2-hop, with an extra legitimately-retrieved supporting document, and both correctly hedge about the finance remediation details not being available. No confident-wrong claims in either. This is a marginal improvement in completeness but materially the same core answer.
Stability: N/A (single run)

## Case 15: Why did the analytics dashboard show revenue below actual?
Expected docs: ['INC1208', 'PROJ-405', 'PR-705', 'eng-data-2026-08-11']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 533 | $0.0022 | 3.0s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1278 | $0.0048 | 5.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 51351 | $0.1365 | 85.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- ESG retrieves all four expected documents and provides a thorough, accurate answer covering the root cause (join condition bug excluding coupon orders), the fix (PR-705), verification, and correctly notes the uncertainty about how long the bug existed - matching 2-hop's level of detail and hedging. Both ESG and 2-hop are materially equivalent in content, correctly grounded in the expected documents, with no fabrications. ESG is slightly more structured but conveys the same facts as 2-hop, which is the better of the two baselines (flat-RAG missed PR-705, PROJ-405 details and the slack thread nuance). Differences between ESG and 2-hop are cosmetic/organizational only.
Stability: N/A (single run)

## Case 16: Why weren't Gmail users getting password reset emails?
Expected docs: ['INC1215', 'PROJ-410', 'PR-710', 'email-deliverability-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.25 | 1.00 | false | TRUE | 586 | $0.0027 | 3.2s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 1415 | $0.0056 | 7.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 44158 | $0.1206 | 76.7s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All four expected documents were retrieved by both 2-hop and ESG, and both give the same core explanation: DKIM record not updated after domain change, Gmail's stricter validation silently filtered the emails, fixed via PR-710. ESG adds slightly more detail (quotes from Marcus Webb, explicit distinction between the resolved Gmail issue and the still-open broader deliverability investigation mentioned in the runbook), which is a nuance the 2-hop answer doesn't explicitly clarify (2-hop doesn't mention the runbook's note about the separate broader issue). This clarification is grounded in the runbook document and adds useful precision without overstating claims. Both answers are consistent with expected documents and hedge similarly where warranted. ESG's answer is essentially equivalent in core content to 2-hop, with marginally better organization and a correct nuance about the broader unresolved issue, but this is not a major material addition - it's largely cosmetic/organizational. No fabrications noted in either domain. Overall, ESG is at least as good as 2-hop, arguably marginally better due to the clearer distinction of the still-open broader issue, but this doesn't rise to a major factual advantage since flat-RAG also mentioned that ambiguity vaguely. Given the two are materially the same in substance with ESG offering slightly better clarity without introducing errors, I'd call this same.
Stability: N/A (single run)

## Case 17: Why is bulk export timing out for large accounts?
Expected docs: ['INC1250', 'PROJ-430', 'PR-715', 'bulk-export-architecture', 'eng-platform-2026-08-16']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.40 | 1.00 | false | TRUE | 819 | $0.0036 | 3.5s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 1231 | $0.0047 | 5.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 57033 | $0.1524 | 92.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly identify the root cause (synchronous, in-memory, non-streaming export exceeding timeout) and fix (PR-715 streaming chunks). Flat-RAG misses PR-715, bulk-export-architecture, and eng-platform-2026-08-16, giving the shallowest account. 2-hop adds PR-715 and bulk-export-architecture, giving a more complete picture including the broader architectural lesson. ESG retrieves all five expected documents and accurately summarizes each, including the Slack thread corroboration and the architecture doc's broader guidance, without introducing unsupported claims. This is the most complete and fully grounded answer, matching all expected documents with no fabrication.
Stability: N/A (single run)

## Case 18: Why is the iOS app crashing on the checkout screen?
Expected docs: ['INC1122', 'mobile-eng-2026-08-05']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 801 | $0.0054 | 6.4s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 616 | $0.0033 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 32224 | $0.0849 | 56.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1122 and mobile-eng-2026-08-05), while both baselines only retrieved INC1122 and missed the Slack thread. This allowed ESG to surface the additional material fact that Sam Okafor's profiling pointed to a specific hypothesis (SDK image cache not releasing thumbnails) as the leading suspect for the memory leak, while still correctly hedging that this is unconfirmed. ESG's claims are properly grounded in the retrieved documents and appropriately caveated as a working hypothesis, not asserted as settled fact. This gives the reader materially more useful information without overstating confidence, whereas both baselines stop at "memory pressure" without identifying the suspected source.
Stability: N/A (single run)

## Case 19: Why don't the warehouse inventory counts match the system?
Expected docs: ['INC1137', 'ops-warehouse-2026-08-02']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 564 | $0.0031 | 5.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 547 | $0.0027 | 6.0s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 25046 | $0.0802 | 45.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1137 and ops-warehouse-2026-08-02) while both baselines only retrieved INC1137. ESG correctly surfaces the additional context from the Slack thread—recurring discrepancies on aisle 12, and the team's hypothesis (explicitly flagged as unconfirmed) that a nightly sync job might be skipping items—while still correctly hedging that no root cause was confirmed. This is materially more informative than the baselines, which only state that the cause is unknown, without surfacing the suspected sync-job hypothesis or the recurring aisle 12 pattern that the expected documents contain. ESG does not overstate confidence; it clearly labels the sync-job theory as speculation and unverified. This makes ESG strictly better than either baseline, which missed the second expected document entirely.
Stability: N/A (single run)

## Case 20: What happened with the login outage?
Expected docs: ['INC1042', 'PROJ-201', 'PR-455', 'auth-service-outage-postmortem-august-2026', 'eng-platform-2026-08-08', 'INC1115', 'PR-611', 'PROJ-312', 'session-management-runbook']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 0.75 | false | TRUE | 2178 | $0.0121 | 11.2s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 0.90 | false | false | 3839 | $0.0163 | 13.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.82 | false | false | 120369 | $0.3252 | 197.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify INC1042 as the core "login outage" (expired JWT signing key, 401s, fixed via manual rotation, PROJ-201/PR-455 follow-up), and correctly note INC1115 and INC1166 as separate but related incidents. The 2-hop answer covers all the expected documents (INC1042, PROJ-201, PR-455, postmortem, eng-platform slack, INC1115, PR-611, PROJ-312, session-management-runbook) with accurate details (60% failure rate, 2.5 hour window, calendar reminder root cause, runbook update). ESG's answer covers the same expected documents plus an additional real (retrieved) document PR-550 for INC1166's follow-up fix, which is not fabrication since it appears in ESG's retrieved list. ESG's content is essentially equivalent to 2-hop's in substance and confidence level - both correctly identify INC1042 as the primary incident, both hedge appropriately about the ambiguity of the term "login outage," and both provide the same key facts. ESG adds slightly more detail on INC1166's resolution (PR-550) which is grounded in its own retrieval, not a fabrication. No confident wrong claims in either. The differences are essentially cosmetic/additive rather than substantively better or worse.
Stability: N/A (single run)

## Case 21: Are customers stacking discount codes somehow?
Expected docs: ['INC1201', 'PROJ-401', 'PR-701', 'coupon-discount-validation-rules', 'customer-support-eng-2026-08-10']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.20 | 1.00 | false | TRUE | 689 | $0.0035 | 4.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 0.80 | false | false | 1642 | $0.0065 | 7.1s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 0.83 | false | false | 64978 | $0.1731 | 108.1s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly confirm stacking occurred and describe the same root cause and fix. Flat-RAG is the thinnest, missing the "multiple distinct codes" nuance's supporting detail and citing only INC1201. 2-hop covers INC1201, PROJ-401, PR-701, coupon-discount-validation-rules, and eng-checkout-2026-08-10, essentially matching the expected set except for customer-support-eng-2026-08-10. ESG retrieves and cites all five expected documents, including customer-support-eng-2026-08-10, which corroborates that real customers were seeing the stacking behavior via support tickets — a material fact the baselines omit. ESG also appropriately hedges on unresolved gaps (Finance review outcome, whether support flag was linked to the incident) without asserting unsupported facts. This makes ESG more complete than both baselines while maintaining calibrated hedging, so it is better.
Stability: N/A (single run)

## Case 22: Did the order-service pool issue come back?
Expected docs: ['INC0980', 'order-service-on-call-runbook', 'PR-508', 'order-platform-2026-08-07', 'q3-2026-infra-cost-review-meeting-notes']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.80 | 1.00 | false | false | 2242 | $0.0125 | 12.0s | single-pass (no traversal) |
| 2-hop | 1 | 0.80 | 1.00 | false | false | 1911 | $0.0090 | 9.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 76969 | $0.2006 | 114.2s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three answers correctly conclude "yes, it recurred" with appropriate hedging about lack of a formal ticket. ESG additionally retrieves and incorporates q3-2026-infra-cost-review-meeting-notes, which is part of the expected document set that both baselines missed. ESG correctly notes this document's relevance (cost increase tentatively attributed to pool sizing changes) while appropriately labeling it as tangential and not overclaiming its significance. This gives ESG more complete coverage of the expected documents without introducing any unsupported claims. The core narrative and hedging about gaps is materially the same across all three, but ESG is more complete.
Stability: N/A (single run)

## Case 23: Why are we seeing sporadic 502s from the API gateway?
Expected docs: ['INC1243', 'PROJ-425', 'eng-infra-2026-08-15']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 780 | $0.0040 | 5.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 873 | $0.0046 | 6.4s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 38391 | $0.1001 | 59.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- All three systems correctly conclude the root cause is unknown, with consistent hedging. ESG additionally retrieves and incorporates eng-infra-2026-08-15, the third expected document, which corroborates the same facts (Slack thread showing the team independently noticed the issue and plans to capture more detail live). This adds grounded completeness without introducing unsupported claims. ESG's answer is thus more complete while maintaining the same calibrated hedge as the baselines, making it strictly better.
Stability: N/A (single run)

## Case 24: What's causing the intermittent Redis latency spikes?
Expected docs: ['INC1158', 'PROJ-335']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 1.00 | false | false | 822 | $0.0041 | 5.6s | single-pass (no traversal) |
| 2-hop | 1 | 1.00 | 1.00 | false | false | 815 | $0.0037 | 5.5s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 24881 | $0.0657 | 37.0s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly convey the same core facts: root cause not identified, connection pooling ruled out, application layer cleared, escalated to infra team for network-level investigation, no fix in progress. All three hedge appropriately given the expected documents don't contain a resolution. ESG's answer is more verbose with extra structure but doesn't add new factual content beyond what flat-RAG and 2-hop already state, nor does it fabricate anything. Differences are cosmetic/formatting only.
Stability: N/A (single run)

## Case 25: Is partner API traffic being rate-limited correctly?
Expected docs: ['INC1151', 'PROJ-330', 'PR-625', 'api-rate-limiting-guide', 'partner-eng-2026-08-09', 'PROJ-255', 'partner-integration-best-practices']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.14 | 1.00 | false | TRUE | 924 | $0.0061 | 7.2s | single-pass (no traversal) |
| 2-hop | 1 | 0.29 | 1.00 | false | false | 1407 | $0.0089 | 9.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 88263 | $0.2314 | 136.5s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- The gold expected set includes INC1151, PROJ-330, PR-625, api-rate-limiting-guide, partner-eng-2026-08-09, PROJ-255, and partner-integration-best-practices. Both flat-RAG and 2-hop retrieved only a subset (1 and 2 docs respectively) and thus missed the entire incident/root-cause narrative about partner accounts defaulting to standard tier, the recurring provisioning bug, and the fix in PR-625. Their conclusions are limited to "documentation is accurate but we can't confirm real-time enforcement," which is an incomplete picture — it misses that there IS documented evidence of incorrect rate-limiting occurring (INC1151, PROJ-330) and a recurring failure mode.

ESG retrieved nearly the full expected set (6 of 7 expected docs, missing none critically) and synthesized a much more complete and accurate answer: it correctly notes the documented limits are correct, but explains a real, recurring incorrect-enforcement issue (new partner accounts defaulting to standard tier) grounded in INC1151, PROJ-330, PR-625, the Slack thread, and the best-practices doc. It also appropriately hedges about whether the provisioning checklist was implemented and about real-time monitoring data. This is well-grounded in the expected documents and provides significantly more material fact content than either baseline, without asserting unsupported claims. This is a clear case of ESG surfacing available answer content that the baselines missed due to incomplete retrieval.
Stability: N/A (single run)

## Case 26: Why is customer support queue time increasing?
Expected docs: ['INC1236', 'PROJ-420', 'support-eng-2026-08-14']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 582 | $0.0035 | 4.6s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 734 | $0.0047 | 6.2s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 42861 | $0.1311 | 70.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved all three expected documents (INC1236, PROJ-420, support-eng-2026-08-14) while both baselines only retrieved INC1236. ESG correctly surfaces additional material facts that the baselines missed entirely: PROJ-420 shows an active engineering investigation pointing to a suspected slowdown in the support tool's ticket-routing integration, and the Slack thread corroborates this hypothesis while ruling out volume as a cause. ESG appropriately hedges that this is not confirmed as the root cause, avoiding overclaiming, while still giving the reader the leading hypothesis and ruling out demand surge - both material facts unavailable to the baselines. This is a clear case where the baselines' "not enough information" hedge was overly conservative given the expected documents actually contained additional useful investigative context that ESG correctly found and calibrated confidence around.
Stability: N/A (single run)

## Case 27: Why did the third-party analytics script slow the page down?
Expected docs: ['INC1229', 'PROJ-415']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.50 | 1.00 | false | false | 688 | $0.0046 | 6.2s | single-pass (no traversal) |
| 2-hop | 1 | 0.50 | 1.00 | false | false | 624 | $0.0037 | 5.6s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 23508 | $0.0632 | 38.9s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- ESG retrieved both expected documents (INC1229 and PROJ-415), while both baselines only retrieved INC1229 and explicitly hedged that they couldn't determine why the script blocked rendering. ESG surfaces the additional confirmed detail from PROJ-415 (Layla Haddad's comment confirming render-blocking loading as the mechanism and the proposed defer/async fix), which is grounded in the expected document set and directly answers the "why" that the baselines said was missing. ESG still appropriately hedges on remaining gaps (exact technical implementation, resolution outcome). This is a clear case of ESG surfacing material facts from the expected documents that both baselines missed.
Stability: N/A (single run)

## Case 28: What's happening with the mobile push notification opt-in rate?
Expected docs: ['INC1257', 'mobile-notification-permission-best-practices', 'mobile-eng-2026-08-17']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.33 | 1.00 | false | false | 575 | $0.0033 | 5.8s | single-pass (no traversal) |
| 2-hop | 1 | 0.33 | 1.00 | false | false | 576 | $0.0031 | 5.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 1.00 | 1.00 | false | false | 36984 | $0.1101 | 61.8s | frontier exhausted (no more leads to follow) |

Verdict run 1: **BETTER** -- Both baselines only retrieved INC1257 and correctly hedged that no further detail (cause confirmation, magnitude, etc.) was available. ESG retrieved the additional expected documents (mobile-eng-2026-08-17 and mobile-notification-permission-best-practices) and used them to add legitimate, grounded detail: the Slack thread corroborating the timing-change theory and proposed A/B test, and the best-practices doc explaining why prompt timing affects opt-in and that it was written in response to this incident. ESG still correctly hedges that the root cause is unconfirmed and that quantitative details are missing, matching the calibration of the baselines while surfacing more grounded facts from the expected sources that the baselines missed entirely (due to retrieval limitations). No fabrication apparent since all cited documents are in ESG's retrieved list and content matches expected sources.
Stability: N/A (single run)

## Case 29: What's been discussed in recent team meetings?
Expected docs: ['q3-design-review-notes', 'eng-onboarding-2026-08-16', 'eng-database-2026-08-13', 'eng-general-2026-08-14']
Excluded docs: ['team-offsite-planning-fall-2026', 'vendor-contract-renewals-q3', 'engineering-all-hands-notes-august-2026', 'standup-notes-2026-08-06', 'standup-notes-2026-08-13']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.00 | 0.00 | TRUE | false | 1709 | $0.0094 | 11.1s | single-pass (no traversal) |
| 2-hop | 1 | 0.00 | 0.00 | TRUE | false | 1641 | $0.0084 | 12.7s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.75 | 0.30 | TRUE | false | 82508 | $0.2429 | 128.4s | frontier exhausted (no more leads to follow) |

Verdict run 1: **WORSE** -- The expected sources include q3-design-review-notes, eng-onboarding-2026-08-16, eng-database-2026-08-13, eng-general-2026-08-14. Neither flat-RAG nor 2-hop retrieved q3-design-review-notes at all, and both missed it entirely, framing their answer around Slack threads and offsite planning, explicitly stating no "team meeting" notes exist — this is a miss since q3-design-review-notes presumably is an actual meeting notes doc that should have been surfaced.

ESG also does not cite q3-design-review-notes directly, but it does retrieve engineering-all-hands-notes-august-2026 (a distractor per the gold labels) and standup-notes-2026-08-13, which references "design review prep" — closer to touching on the design review topic than flat-RAG/2-hop, though it never actually reaches or cites the q3-design-review-notes document itself. So all three miss the same expected document.

ESG additionally introduces INC1222 and engineering-all-hands-notes-august-2026, which are actually retrieved by ESG (so not fabricated), but engineering-all-hands-notes-august-2026 is explicitly listed as a distractor/irrelevant document in the gold set. ESG treats it as legitimate content ("monthly all-hands covering roadmap...") which incorporates a known irrelevant document into the confident answer, potentially misleading the reader. However, since it was actually retrieved, it's not a fabrication â€“ it's an unlabeled-but-real citation, though the gold explicitly marks it as a distractor, meaning it's likely not relevant to the "recent team meetings" topic, yet ESG presents it as a real part of the answer, alongside the invented "INC1222" incident narrative that isn't part of expected sources either.

Given that all three miss q3-design-review-notes, and ESG uses a distractor document confidently as being relevant to the discussion, while also adding a somewhat speculative incident narrative not in expected docs, ESG doesn't clearly improve accuracy over baselines. It's roughly the same overall in terms of key facts (all miss key expected the design review notes), but ESG introduces additional content from a known distractor with confidence, which could mislead the reader about what's relevant. This is a modest downgrade relative to flat-RAG/2-hop's cleaner (if incomplete) hedged answer.
Stability: N/A (single run)

## Case 30: Anything I should know about upcoming team events or offsites?
Expected docs: ['team-offsite-planning-fall-2026', 'social-committee-2026-08-01', 'social-committee-2026-08-15']
Excluded docs: ['vendor-contract-renewals-q3', 'q3-design-review-notes']

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 0.67 | 1.00 | false | false | 741 | $0.0041 | 6.3s | single-pass (no traversal) |
| 2-hop | 1 | 0.67 | 1.00 | false | false | 823 | $0.0047 | 6.8s | single-pass, one follow-up hop |
| ESG (v2) | 1 | 0.67 | 1.00 | false | false | 13559 | $0.0399 | 27.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three systems retrieved the same two documents (social-committee-2026-08-01 and team-offsite-planning-fall-2026) and missed the third expected document (social-committee-2026-08-15), which likely contains a follow-up update. None of the systems surfaced content from that missing document, so all are equally incomplete in that respect. The content and hedging in ESG's answer is materially the same as the baselines - same facts about the offsite and holiday party, same acknowledgment of missing details. ESG is slightly more verbose with added formatting but doesn't add or omit material facts relative to the baselines, nor does it fabricate anything the retrieved docs list doesn't include.
Stability: N/A (single run)

## Case 31: What's the latest on PROJ-305?
Expected docs: ['PROJ-305', 'eng-search-2026-08-05', 'PR-605']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | TRUE | 2741 | $0.0092 | 6.5s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 4007 | $0.0119 | 6.5s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.21 | false | TRUE | 115263 | $0.3037 | 142.8s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers converge on the same core facts: PROJ-305 addressed autocomplete's stale separate cache, fixed via PR-605 (repointing to primary index), status resolved/done/merged and verified in staging, corroborated by INC1108 and the eng-search-2026-08-05 Slack thread. ESG's answer is essentially the same content as flat-RAG and 2-hop, just reorganized with more headers and slightly more detail on PROJ-230/PR-470 context (which 2-hop also includes). No new material facts are added beyond what 2-hop already covers, and no confident errors are introduced. Differences are cosmetic/structural only.
Stability: N/A (single run)

## Case 32: Is there any update on PROJ-318?
Expected docs: ['PROJ-318', 'INC1130']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1520 | $0.0053 | 4.2s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.17 | false | false | 2308 | $0.0075 | 5.6s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 132810 | $0.3904 | 189.1s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers convey the same core facts: PROJ-318 root cause identified (429 rate limiting during peak volume), tied to INC1130, no fix merged yet, team deciding between client-side backoff vs requesting higher carrier limit. ESG's answer is essentially the same content as flat-RAG and 2-hop, just with different formatting (headers, bolded status "In Progress"). No new material facts are added, and no incorrect claims are introduced. The extra retrieved documents (INC1236, INC1243, PR-740, etc.) are not used to add any unsupported claims. This is a cosmetic difference in presentation only.
Stability: N/A (single run)

## Case 33: What was PROJ-275 about?
Expected docs: ['PROJ-275', 'PR-495']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.29 | false | false | 1335 | $0.0036 | 2.6s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.18 | false | false | 1914 | $0.0047 | 2.6s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.17 | false | false | 141379 | $0.4078 | 192.8s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers correctly identify PROJ-275 as a typo fix in the order confirmation email footer, fixed via PR-495, noted by Yuki Tanaka, merged and deployed with next release. ESG adds a bit more detail (reviewer Priya Nair's comment, PR title) and clarifies unrelated retrieved docs, but this is essentially the same core fact set as flat-RAG and 2-hop. No fabrication, no hedging issues, no material omissions. Differences are cosmetic/additional detail without changing the substance.
Stability: N/A (single run)

## Case 34: Can you give me context on PROJ-355?
Expected docs: ['PROJ-355', 'PR-645']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.25 | false | false | 1712 | $0.0067 | 5.8s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.25 | false | false | 1690 | $0.0062 | 4.6s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.14 | false | false | 134353 | $0.3905 | 191.7s | reached processing cap (20/20) |

Verdict run 1: **SAME** -- All three answers correctly identify PROJ-355 as a minor cosmetic CSS fix resolved via PR-645, with the same key facts (Layla Haddad, Yuki Tanaka's review, merged into next release). ESG adds explicit clarification that other retrieved documents (PROJ-330, INC1151, PR-625, etc.) are unrelated, which is a helpful but not materially different addition - it doesn't add new facts about PROJ-355 itself beyond what flat-RAG/2-hop already state. All three are grounded in the expected documents (PROJ-355, PR-645) with no fabrication. The core content and confidence level are essentially the same across all three; ESG's extra note about irrelevant tickets is cosmetic/organizational rather than materially informative.
Stability: N/A (single run)

## Case 35: What's the story behind PROJ-445?
Expected docs: ['PROJ-445', 'PR-740']
Excluded docs: []

| System | Run | Recall | Precision | Excl.hit | Fabrication | Tokens | Cost | Time | Stop reason |
|---|---|---|---|---|---|---|---|---|---|
| flat-RAG | 1 | 1.00 | 0.50 | false | TRUE | 1048 | $0.0051 | 4.8s | single-pass + question-ID exact match |
| 2-hop | 1 | 1.00 | 0.33 | false | false | 1395 | $0.0059 | 4.8s | single-pass, one follow-up hop + question-ID exact match |
| ESG (v2) | 1 | 1.00 | 0.33 | false | false | 71582 | $0.2234 | 116.6s | frontier exhausted (no more leads to follow) |

Verdict run 1: **SAME** -- All three answers correctly identify the core story: PROJ-445 is a routine maintenance ticket for SSL cert renewal script robustness, implemented via PR-740, unrelated to any incident, approved by Tomas Berg, merged per Omar Farouk's comment. ESG adds extra context (status "Done", PROJ-440 backlog item, explicit "What's Missing" section noting no prior history is available) but does not introduce any confidently wrong claims beyond what's supported by the retrieved documents. The additional detail about INC1243/PROJ-425/eng-infra thread being a separate unresolved investigation is consistent with the 2-hop baseline's mention as well. ESG's answer is essentially equivalent in factual content to the 2-hop baseline (which is the stronger baseline), with the same hedging about no further connection found. The differences are additional structure/detail but not materially different facts or confidence levels.
Stability: N/A (single run)
