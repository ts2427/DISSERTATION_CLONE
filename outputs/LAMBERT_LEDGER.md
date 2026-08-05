# Lambert Ledger — five June questions, v3-final dispositions (8/5/2026)

Every row cites its proving artifact by name. Nothing below overstates: one row is
OPEN by design (the decision is Tim's), and row 4 reports a claim that did NOT survive.

| # | June question | June state | v3-final disposition | Proving artifact |
|---|---|---|---|---|
| 1 | Item 5.02 vs any-8-K outcome | Outcome silently measured ANY 8-K (broken date regex + stale fallback; base rates 55–59%) | Extraction rebuilt on SEC submissions item-code metadata; v3 base rates 17.4/43.4/69.9% (N=339). **OPEN sub-question:** the items field carries top-level codes only ("5.02"), never sub-items — departures cannot be distinguished from appointments/comp without new document-level pulls. Reframe (governance-disclosure incidence) vs refine (departures-only, new extraction) is **Tim's call** | scripts/156 (extraction); Data/edgar/rebuild_submissions_cache/; docs/DATA_QUALITY_DOCUMENTATION.md Failure Mode 4; constants keys H6_*; cache inspection 8/5 (this batch, task 1) |
| 2 | classify_fcc; Johnson Matthey / Aero Charter | Keyword classifier (`'att' in name`, `'charter' in name`) — "Johnson M**att**hey" and "Aero **Charter**" classified as carriers | Keyword classifier retired with the pre-audit base. v3 treatment = registry snapshot + adjudicated clause rules (scripts/154). Both firms EXCLUDED-UNRESOLVED at Gate 1 (no US public registrant; FISC precedent) — they never reach the sample | Recovered scripts/root_dev_archive-era classifier at commit 07abde7 (`fcc_keywords`); outputs/rebuild/GATE1_ENTITY_VERIFICATION_LEDGER.csv rows "Johnson Matthey, Inc.", "Aero Charter, Inc."; scripts/154 |
| 3 | CIK-resolved distinct carrier count | Unanswerable — fuzzy identity layer; treated "firms" mixed orgs, brands, and collision sinks | Fully resolved at three named levels: **13 parent CIKs / 38 orgs / 116 events** (full); **12 / 109** (CRSP); **11 / 105** (regression). Brand→parent rollups documented per entity | constants_v3.json keys treated_*; STAGE4_TREATMENT_REPORT.md (by-CIK roster); GATE1_APPLIED_LEDGER.csv |
| 4 | TOST Z_CRITICAL | Script 91e hardcoded Z=1.645 (90% CI) while its own comment and the methods text said "95% confidence interval"; methods claimed 180d equivalence within ±10pp | **Claim does not survive under either value.** On 91e's own stored inputs: 90% CI (Z=1.645) fails at 90d [−4.63,+12.03] and 180d [−1.95,+14.07]; methods-stated 95% (Z=1.96) fails harder (180d [−3.49,+15.61]). The quoted "95% CI [−9.38,+9.60]" reproduces exactly as a 90% interval on an earlier input vintage — label said 95%, math was 90%. Claim retired; v3 makes no H6 equivalence claim (MDEs 15–20pp) | scripts/91e_essay3_h6_tost_equivalence.py ll.33,59; outputs/tables/essay3_governance/reduced_form_h6_results.csv + h6_tost_equivalence_results.csv (retired run's own FAILs at 90/180d); controlled rerun 8/5 (this batch, task 2); ESSAY3_H6_APPENDIX.md l.72 (the stale claim) |
| 5 | Fresh-clone reproduction | Failed when Lambert tried it (missing inputs, unreproducible numbers) | **PASSES.** Bare clone → full canonical chain (150→159→158) → "Assertion check vs existing baseline: PASS" against committed constants_v3.json; WRDS pull path exercised live; three portability defects found and fixed by the test itself (MAX_PATH, untracked EDGAR lookup, LFS file:// quirk) | outputs/rebuild/FRESH_CLONE_RUN_LOG.txt (committed, 655708a); docs/WRDS_EXTRACT_RECIPE.md; commits 77b362d, cc7903a |

## Flags per the no-overstatement rule
- Row 1 stays OPEN until Tim decides reframe-vs-refine; nothing in the cache supports
  a departures-only sub-coding without new EDGAR document pulls (0% determinable from
  item codes).
- Row 4 is deliberately a negative disposition: the retired 180d equivalence claim is
  documented as failed, not repaired. The 30d window passes at either Z on the stored
  inputs — but v3 claims nothing from the retired chain.
