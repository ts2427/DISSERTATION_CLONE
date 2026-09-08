# Essay 2 Sample Attrition Ledger (computed live)

Chain from the 1,054 PRC notification records to the Essay 2 regression
sample, every step its own line. Pre-rule = breach_date before the
December 8, 2007 effective date of 47 CFR 64.2011 (the only cutoff used;
there is no September 28, 2007 date and no "Rule 37.3").

## Record-level steps (treatment is assigned at Stage 4, on events â€”
treated counts are not defined for record-level rows)

| Step | N | Removed | Reason |
|---|---|---|---|
| PRC universe | 1,054 | â€” | notification RECORDS, not breaches (records vs events is a methodological finding) |
| Entity resolution + Gate 1 | 758 | 296 | no verified public-registrant identity (EXCLUDED-UNRESOLVED 281, private 9, no US listing 2, ambiguous 2, pre-IPO 2) |
| CIK+date deduplication | 524 | 234 | records collapsed into firm-day EVENTS (unit changes here) |
| Gate 2 adjacency verdicts | 489 | 35 | near-duplicate refiling chains collapsed (signed) |

## Event-level steps (Essay 2)

| Level | Unit | N | Treated | Treated orgs | Treated parent CIKs | Control | Pre-rule (<2007-12-08) | Pre-rule treated | Note |
|---|---|---|---|---|---|---|---|---|---|
| Canonical events (post-Gate 2) | events | 489 | 118 | 39 | 14 | 371 | 7 | 0 | CANONICAL_V3 |
| CRSP security matched | events | 361 | 111 | 38 | 13 | 250 | 6 | 0 | permno resolved (stage-5 identity layer) |
| Public notification date present | events | 361 | 111 | 38 | 13 | 250 | 6 | 0 | reported_date parseable (Essay 2 anchors on notification) |
| Notification on/before 2024-12-31 | events | 355 | 111 | 38 | 13 | 244 | 6 | 0 | 6 events notified in 2025 dropped at the WRDS extract boundary (OWN LINE; stated sample period 2006-2024) |
| Volatility windows computable | events | 351 | 109 | 38 | 13 | 242 | 6 | 0 | >= 15 daily returns in each 21-trading-day window (OWN LINE per directive; pre/post split below) |
| Compustat covariates complete | events | 336 | 105 | 36 | 12 | 231 | 6 | 0 | prior-FY size, leverage, ROA |
| Disclosure delay valid | events | 335 | 104 | 36 | 12 | 231 | 6 | 0 | delay regressor present (wrong-field/unparseable dates are missing by the 8/17 signed fixes) |
| Malformed-record exclusion (FINAL) | events | 333 | 104 | 36 | 12 | 229 | 6 | 0 | ATT-SecurityBreach artifact records (control-coded, AT&T-identity returns) excluded (OWN LINE, 9/2 signed) |

**Final Essay 2 regression sample: N = 333 (104 treated / 36 orgs / 12 parent CIKs; 229 control; 6 pre-rule events of which 0 treated).**

Framing is post-2007 cross-sectional (no DiD, no natural experiment).
Essay 1 v3 comparison: its regression sample reproduces at 340 (106
treated) from the 356 events with a breach-anchored car_30d
(has_crsp_data); the committed constants_v3.json still carries 338/104
pending Essay 1's own signed regeneration (dual-print below). Essay 2
instead keys on the 368 permno-matched events and applies its own
notification-anchored window requirement and the delay-regressor
requirement â€” the two samples overlap heavily but are not nested.

## Decomposition of the 4 volatility-window losses (355 -> 351)

Windows are NOTIFICATION-anchored (reported_date mapped to the nearest
trading day within +/-7 calendar days): trading days [-25,-5] pre and
[+5,+25] post, 21 trading days each, minimum 15 valid daily returns per window.

| Failure | N | Treated | Reason |
|---|---|---|---|
| No trading day within +/-7 calendar days of notification | 1 | 1 | security not trading around the notification date (delisted or gap in coverage) |
| Insufficient PRE-window returns (< 15) | 0 | 0 | recently listed or thinly traded before notification |
| Insufficient POST-window returns (< 15) | 3 | 1 | delisted or halted shortly after notification |
| Both windows insufficient | 0 | 0 | too few returns on both sides |
| **Total** | **4** | **2** | |

## Composition of the 128 events failing CRSP security match (489 -> 361)

7 treated (4 orgs, 2 parent CIKs) and 121 control. These are Gate-1-verified public registrants whose stage-5 identity layer resolves no PERMNO at the breach date (no listed common equity on CRSP then: OTC/foreign-listed, pre-IPO at breach, or post-delisting).

| Organization type | N | Treated |
|---|---|---|
| BSO | 128 | 7 |

## By-year: canonical events (breach year) and final regression sample (notification year)

| Year | Canonical N | Canonical treated | Final N | Final treated |
|---|---|---|---|---|
| 2006 | 3 | 0 | 0 | 0 |
| 2007 | 5 | 0 | 6 | 0 |
| 2008 | 14 | 5 | 11 | 5 |
| 2009 | 12 | 6 | 3 | 3 |
| 2010 | 5 | 0 | 4 | 0 |
| 2011 | 3 | 1 | 2 | 0 |
| 2012 | 13 | 4 | 7 | 1 |
| 2013 | 28 | 6 | 14 | 1 |
| 2014 | 28 | 13 | 16 | 12 |
| 2015 | 19 | 4 | 20 | 7 |
| 2016 | 57 | 1 | 37 | 0 |
| 2017 | 55 | 11 | 44 | 12 |
| 2018 | 26 | 4 | 17 | 4 |
| 2019 | 41 | 14 | 23 | 9 |
| 2020 | 25 | 5 | 12 | 6 |
| 2021 | 21 | 9 | 19 | 9 |
| 2022 | 32 | 11 | 21 | 6 |
| 2023 | 67 | 12 | 48 | 14 |
| 2024 | 28 | 12 | 29 | 15 |
| 2025 | 7 | 0 | 0 | 0 |
| **Total** | **489** | **118** | **333** | **104** |

Final-sample date span: notifications 2007-01-10 to 2024-11-08; breach dates 2006-12-01 to 2024-10-04. Any final-sample year outside 2006-2024 in the table above contradicts the stated sample period and must be resolved in the text, not silently.

**DUAL-PRINT (documented divergence, 9/4):** fresh Essay 1 recipe = 340/106 (DISH events entered via the scripts/179 top-up); committed constants_v3.json = 338/104 (STALE, Essay 1 regeneration pending its own signed pass). Neither number is silently adopted for the other essay.

## Cross-essay pre-rule check (Essay 1 v3 regression sample, script-158 recipe)

| Anchor | Pre-rule (<2007-12-08) | Pre-rule treated |
|---|---|---|
| breach_date | 6 | 0 |
| reported_date | 6 | 0 |

Computed live on the reproduced Essay 1 sample (N=340, 106 treated; constants_v3.json remains at 338/104, see the dual-print above). The audit-era "10 pre-rule / 1 treated" figure (DATA_QUALITY_DOCUMENTATION.md, DEAD_DATE_PURGE_INVENTORY.md, STALE_RESULTS_MANIFEST.txt, outputs/SAMPLE_ATTRITION_LEDGER.md) was computed on the PRE-REBUILD regression sample and does not describe any v3 sample; whichever row above matches the prose is the citable number, and every pre/post statement must name both its cutoff and its anchor.
