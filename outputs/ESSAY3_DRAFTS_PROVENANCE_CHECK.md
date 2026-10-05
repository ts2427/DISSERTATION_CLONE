# Essay 3 section drafts: provenance check

Drafts checked: `drafts/e3_controls.md`, `e3_design.md`, `e3_estimation.md`, `e3_outcome.md`, `e3_sample.md`, `e3_treatment.md` (115 lines, about 4,700 words).
Read-only. Nothing in the repo was edited and no pipeline script was run. Two short read-only pandas checks were run against `outputs/essay3_v4/e_analysis_sample.csv` and `outputs/rebuild_v4/v4_212_links.csv`.

Paths below are relative to `C:\Users\mcobp\DISSERTATION_CLONE`. "v4" = `outputs/essay3_v4/`. "FACTS" = `outputs/essay3_v4/methods/METHODS_FACTS.md`.

---

## FLAGS

### (a) Superseded Essay 3 Query 2 figures: NONE FOUND

- No 338 events, 107 treated, 81 clusters, G* 23.6, CV 2.267, CV3 p .61/.87/.71, or MDE 9/29/32 pp appears in any draft.
- The only "12" attached to a treated count is `e3_treatment.md:13` ("13 parent CIKs in 12 corporate families"). That is the v4 ledger value (`e_ledger.csv`, `treated_corporate_families` = 12), not the Q2 `treated_parent_ciks` = 12.
- The validation rows for round 1, round 2 and the stratified audit come from `outputs/essay3_q2/d3_*.csv`. That is legitimate: v4 carries those rounds forward (they are in FACTS, and `ANALYSIS_PLAN_V4.md` declares the reuse). The drafts label them as earlier rounds.

### (b) Purge-list terms: NONE FOUND

- No "Rule 37.3", "September 28, 2007", "June 8, 2007", "1,054 breaches", first-stage or "faster disclosure" claims, 14.52/15.05/15.26/16.71, 648/651/653/898, 115 or 127 treated, "ten carriers", 72.7%, "immediate", BoardEx, or "turnover".
- `e3_sample.md:3` and `:5` say "1,054 breach notification records" / "1,054 records", which is the compliant form.
- Effective date is December 8, 2007 everywhere it appears (`e3_design.md:3`, `:7`; `e3_sample.md:11`, `:32`).

### (c) Wording issues

No hard violations. The rule is never called a deadline, and no hypothesis verdict uses "supported" / "not supported" / "confirmed". Items to look at:

| # | Location | Text | Issue |
|---|---|---|---|
| c1 | `e3_treatment.md:3` | "The essay measures that status through the FCC's registry…" | Self-reference as "the essay". `e3_design.md:3` uses "This study". Pick one, or drop if the rule against essay references covers self-reference. |
| c2 | `e3_treatment.md:13`, `e3_sample.md:5` | "13 parent CIKs in 12 corporate families"; "14 parent CIKs in 13 corporate families" | Level naming. The three sanctioned levels are events, parent entities, parent CIKs. The drafts call the 12/13 level "corporate families" (the ledger column name) and use "parent entity" elsewhere for the CIK-level unit (`e3_controls.md:5`, `e3_estimation.md:7`, `e3_treatment.md:9`). One term per level is needed. |
| c3 | `e3_sample.md:19-30` (Table X) | Column headers "Treated", "Control" | Level not named in the header (they are events). "Treated parent CIKs" is named. |
| c4 | `e3_outcome.md:13` | "0 treated and 1 control departure … 4 and 8 … 8 and 24"; "number 8 treated and 4 control" | These are counts of events with at least one such departure (`f5_ceo.csv` / `f6_director.csv` columns are `treated_events`, `control_events`), not counts of departures. The prose reads as departures. |
| c5 | `e3_outcome.md:19` | "an assumption the final round supports but, with 5 reference positives, cannot confirm" | "supports" / "confirm" used about an assumption, not a hypothesis verdict. Low risk; flagged because the words are on the watch list. |
| c6 | `e3_treatment.md:7` | "It confirms carrier families whose operating subsidiaries hold the registrations" | "confirms" used about adjudication, not a verdict. Low risk. |
| c7 | `e3_treatment.md:13` | "Treatment follows regulatory status and does not respond to a breach" | Reads as an exogeneity claim. Not causal language as such, but it is the sentence a reader would take as an identification argument. |
| c8 | `e3_estimation.md:17` | "…would indicate pre-existing differences between the groups rather than any response to the disclosure regime" | Placebo logic phrased as "response to" the regime. Mild causal framing in an otherwise associational section. |
| c9 | `e3_design.md:3` | "took effect December 8, 2007 (FCC, 2008)" | Citation year looks off for a rule effective in 2007. Check the reference entry. Not a number mismatch. |
| c10 | `e3_outcome.md:3` | "In a random draw of 30 filings from the sample, reference coding found an executive departure in 5 and a director-only departure in 2." | The numbers match, but the draw was 30 of the 450 filings added by the v4 rebuild (`outputs/rebuild_v4/237_validation_draw.md`), not a draw from the whole sample. `e3_outcome.md:17` describes it correctly. |
| c11 | `e3_estimation.md:13` | "The primary specification uses 99,999 bootstrap replications" | True for the p-values. `ANALYSIS_PLAN_V4.md` states the bootstrap confidence intervals are inverted at B = 9,999. Only matters if the prose later reports those intervals. |

Compliant and worth noting: `e3_design.md:5` ("places a floor under public disclosure rather than a date by which disclosure must occur"); `e3_design.md:7` and `e3_estimation.md:7` ("conditional association … rather than an effect of the rule"); `e3_estimation.md:15` ("failure to reject the null hypothesis"). No difference-in-differences or natural-experiment language. No reference to other essays or "this part".

---

## MISMATCHES (6)

| # | Location | Draft | Committed | Source |
|---|---|---|---|---|
| M1 | `e3_estimation.md:15` | MDE80 at 30 days = .096 | **.0944** (.094) | `f1_ladder.csv` row 30, `mde80_cv3`; `constants_essay3_v4.json` `F1_30_mde80_cv3` |
| M2 | `e3_estimation.md:15` | MDE80 at 90 days = .233 | **.2234** (.223) | `f1_ladder.csv` row 90; `F1_90_mde80_cv3` |
| M3 | `e3_estimation.md:15` | MDE80 at 180 days = .283 | **.2815** (.282; canonical list rounds to 28.2 pp) | `f1_ladder.csv` row 180; `F1_180_mde80_cv3` |
| M4 | `e3_outcome.md:11` | treated 180-day departure rate = 31.2% | **30.3%** (33 of 109 = .3028) | `f1_ladder.csv` row 180 `treated_mean`; `f1_se_diagnostics.csv` `treated_events` = 33 |
| M5 | `e3_outcome.md:13` | CEO departures within 90 days: "4 and 8" (treated, control) | **3** treated, 8 control | `f5_ceo.csv` window 90 `treated_events` = 3; FACTS "CEO-only / 90d / treated events" |
| M6 | `e3_sample.md:15` | "14.9% of control events" (breach+180d closes before notification) | **14.5%** (43 of 296) | FACTS "anchor diagnostic … / control"; recomputed from `e_analysis_sample.csv` `bd180_before_rd` |

Notes on the mismatches:
- M1-M3: none of .096 / .233 / .283 appears in any v4, q3, q4, appendix or defense-supplement output. They are not the Q2 values either (.0934 / .2918 / .3245). The sentence that follows ("the smallest difference the design can reliably detect exceeds the control group's departure rate") still holds on the committed values (.094 > .044, .223 > .145, .282 > .247).
- M4: 31.2% would be 34 of 109. The Q2 value was 31.8%. Neither is the v4 figure.
- M5: the conclusion (treated group below ten at every window) is unaffected.
- M6: the treated figure in the same sentence (11.9%) is correct.

## NO SOURCE (3)

| # | Location | Text | Status |
|---|---|---|---|
| N1 | `e3_estimation.md:21` | "restricts the control group to events that a conventional ticker-based match also links" | The diagnostic exists (`239_v3_overlap_sensitivity.csv`, N = 347) and the plan defines it as "events also linked in v3". Nothing in the listed outputs describes the v3 link as ticker-based. Characterization unverified. |
| N2 | `e3_outcome.md:15` | "(Claude, Anthropic [model version for the v3-era rounds]…)" and "No human coder produced reference codes" | Final round: sourced (`VALIDATION_REFERENCE_CODES_V4_README.txt`: Claude Opus 5, Tim did not hand-code). Earlier rounds: `outputs/essay3_q2/ESSAY3_STARTING_POINT.md:11` says all reference codes are Claude's, but no committed file names the model version. The bracket is an open placeholder. |
| N3 | `e3_treatment.md:3`, `:9` | 47 CFR § 64.2003 (scope) and § 64.5111 (relay service parallel provision) | Legal citations with no committed source among the listed files. Need checking against the CFR, not against outputs. |

---

## FULL LEDGER

Verdicts: MATCH (to the draft's rounding), MISMATCH, NO SOURCE, DEFINITION (design constant, not a result). "derived" = computed here from committed values.

### drafts/e3_controls.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 3 | "conditions on seven … controls" | 7 | `ANALYSIS_PLAN_V4.md` primary specification: 7 regressors besides `fcc_form499` | DEFINITION (consistent) |
| 5 | "other breach events in the 365 days before the breach date" | 365 | variable `prior_breaches_1yr`; window length not restated in a v4 output | DEFINITION |
| 9 | "no more than 550 days before it" | 550 | FACTS "covariate / fiscal-year rule"; `scripts/219_wrds_funda_v4.py:83` | DEFINITION (consistent) |
| 11 | "from 730 to 181 days before the notification date" | 730, 181 | `scripts/224_essay3_v4_sample_e.py:191` | DEFINITION (consistent) |
| 11 | "ends 180 days before notification" | 180 | same; placebo window is (t0-180d, t0] per plan | DEFINITION (consistent) |
| 13 | "from 365 days to one day before notification" | 365, 1 | `scripts/224:286` | DEFINITION (consistent) |
| 13 | "at least 150 daily returns" | 150 | `e_ledger.csv` last step label | DEFINITION (consistent) |

### drafts/e3_design.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 3 | "took effect December 8, 2007" | 2007-12-08 | `scripts/224:63` `RULE`; `scripts/245_essay3_appendix.py:311` | MATCH |
| 3 | "within seven business days" | 7 | rule text; `docs/claude/ESSAY3_HANDOFF.md:52` | DEFINITION |
| 3 | "seven further full business days" | 7 | rule text; `ESSAY3_HANDOFF.md:53` | DEFINITION |
| 7 | "Seven events … precede December 8, 2007" | 7 | `e_ledger.csv` final row `pre_rule_control` = 7; recomputed 7 | MATCH |
| 7 | "analysis sample of 405" | 405 | `constants_essay3_v4.json` `N` | MATCH |
| 7 | "all in the control group. No treated event precedes" | 0 treated | `e_ledger.csv` `pre_rule_treated` = 0 | MATCH |
| 7 | "precede December 8, 2007" | date | as above | MATCH |
| 7 | "30, 90, and 180 days after notification" | 30/90/180 | plan | DEFINITION |

### drafts/e3_estimation.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 7 | "the seven controls defined above" | 7 | plan | DEFINITION |
| 9 | "analysis sample of 405 events" | 405 | constants `N` | MATCH |
| 9 | "contains 119 parent CIKs" | 119 | constants `parent_ciks`; `f1_ladder.csv` `G` | MATCH |
| 9 | "only 13 clusters contain treated events" | 13 | `f1_ladder.csv` `G1` | MATCH |
| 9 | "coefficient of variation 2.328" | 2.328 | `f1_ladder.csv` `cluster_size_cv` | MATCH |
| 9 | "effective number of clusters … is 24.5" | 24.5 | `f1_ladder.csv` `G_star` | MATCH |
| 9 | "about a fifth of the nominal count" | 1/5 | derived: 24.5 / 119 = 20.6% | MATCH (derived) |
| 11 | "Four variance estimators" | 4 | `f1_ladder.csv` columns HC3, CV1, CV3, WCR | DEFINITION (consistent) |
| 13 | "99,999 bootstrap replications" | 99,999 | `f1_ladder.csv` `B_wcr` | MATCH (see flag c11) |
| 13 | "each sensitivity uses 9,999" | 9,999 | `f3_sensitivities.csv` `B_wcr` | MATCH |
| 15 | "80% power … 5% level" | .80, .05 | plan MDE80 formula | DEFINITION |
| 15 | "is .096 at 30 days" | .096 | `f1_ladder.csv` `mde80_cv3` = .0944 | **MISMATCH** |
| 15 | ".233 at 90 days" | .233 | .2234 | **MISMATCH** |
| 15 | ".283 at 180 days" | .283 | .2815 | **MISMATCH** |
| 15 | "control-group departure rates are .044" | .044 | `control_mean` .0439 | MATCH |
| 15 | ".145" | .145 | .1453 | MATCH |
| 15 | ".247" | .247 | .2466 | MATCH |
| 15 | "At every window, the smallest difference … exceeds the control group's departure rate" | comparison | holds on committed values | MATCH (derived) |
| 17 | "in the 180 days up to and including the notification date" | 180 | plan F4: (t0-180d, t0] | DEFINITION |
| 19 | "Nine sensitivities are estimated at each window" | 9 | `i_tests.csv`: 9 per window | MATCH |
| 19 | "for 27 in total" | 27 | FACTS "tests / sensitivities" | MATCH |
| 19 | "three recall-corrected estimates … two corner cases" | 3, 2 | `f3_sensitivities.csv` `row_type` | MATCH |
| 19 | "three primary tests and the placebo" | 3, 1 | FACTS "tests / primary H6", "tests / placebo" | MATCH |
| 19 | "comprises 31 tests" | 31 | constants `n_tests` | MATCH |
| 21 | "Three diagnostics" (leave-one-out, T-Mobile removal, restricted controls) | 3 | `f3_loco.csv`, `f1_cv3_variance_shares.csv`, `f1_se_diagnostics.csv` (noTM columns), `239_v3_overlap_sensitivity.csv` | MATCH |
| 21 | "a conventional ticker-based match" | none | none | **NO SOURCE** (N1) |

Not present in this draft (so nothing to check): coefficients, CV3 or bootstrap p-values, confidence intervals, placebo estimate, logit marginal effects, randomization-inference p-values.

### drafts/e3_outcome.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 3 | "within four business days" | 4 | Form 8-K instructions | DEFINITION |
| 3 | "random draw of 30 filings" | 30 | `238_new_document_agreement.csv` n | MATCH (see flag c10) |
| 3 | "an executive departure in 5" | 5 | same, `ref_positives`, exec departure (A) | MATCH |
| 3 | "a director-only departure in 2" | 2 | same, director-only `ref_positives` | MATCH |
| 5 | "from 730 days before to 180 days after" | 730, 180 | `e_ledger.csv` step label | DEFINITION |
| 5 | "every listed filing is present" | 0 shortfall | `outputs/rebuild_v4/235_completeness.md` (1,514 of 1,514) | MATCH |
| 11 | "30, 90, and 180 days" | windows | plan | DEFINITION |
| 11 | "3.7% of treated events" (30 days) | 3.7% | `treated_mean` .0367 | MATCH |
| 11 | "4.4% of control events" | 4.4% | `control_mean` .0439 | MATCH |
| 11 | "within 180 days, the rates are 31.2%" | 31.2% | `treated_mean` .3028 = 30.3% | **MISMATCH** |
| 11 | "and 24.7%" | 24.7% | `control_mean` .2466 | MATCH |
| 13 | "at least ten events in each group" | 10 | plan F5 gate; `f5_ceo.csv` `reason` | DEFINITION |
| 13 | "0 treated and 1 control … within 30 days" | 0, 1 | `f5_ceo.csv` window 30 | MATCH, MATCH |
| 13 | "4 and 8 within 90 days" | 4, 8 | `f5_ceo.csv` window 90: 3, 8 | **MISMATCH** (4), MATCH (8) |
| 13 | "8 and 24 within 180 days" | 8, 24 | `f5_ceo.csv` window 180 | MATCH, MATCH |
| 13 | "8 treated and 4 control within 30 days" | 8, 4 | `f6_director.csv` | MATCH, MATCH |
| 13 | "18 and 20 within 90 days" | 18, 20 | `f6_director.csv` | MATCH, MATCH |
| 13 | "21 and 56 within 180 days" | 21, 56 | `f6_director.csv` | MATCH, MATCH |
| 15 | "four blind rounds" | 4 | FACTS validation groups: round 1, round 2, recall audit, v4 new documents | MATCH |
| 15 | "Claude Opus 5 for the final round" | model | `VALIDATION_REFERENCE_CODES_V4_README.txt` | MATCH |
| 15 | "[model version for the v3-era rounds]"; "No human coder" | placeholder | none for the model version | **NO SOURCE** (N2) |
| 17 | "first round, on 80 filings" | 80 | `essay3_q2/d3_agreement.csv` A / all 80 | MATCH |
| 17 | "second round drew 30 fresh filings" | 30 | FACTS "subset random 30" (29 scored) | MATCH |
| 17 | "agreement .93, κ = .71" | .93, .71 | `d3_r2_agreement.csv` .931, .7129 | MATCH, MATCH |
| 17 | "only 5 reference positives" | 5 | same | MATCH |
| 17 | "recall estimate of .60" | .60 | same | MATCH |
| 17 | "40 filings from treated events and 40 from control" | 40, 40 | `d3_audit_recall_by_stratum.csv` (n = 40 per stratum before exclusions) | MATCH, MATCH |
| 17 | "Recall was .84 for treated filings" | .84 | .8421 | MATCH |
| 17 | "and .75 for control filings" | .75 | .7500 | MATCH |
| 17 | "with overlapping intervals" | n/a | [.604, .966] and [.476, .927] | MATCH |
| 17 | "final round drew 30 filings" | 30 | `238_new_document_agreement.csv` | MATCH |
| 17 | "agreement of .97 (κ = .87)" | .97, .87 | .9667, .8696 | MATCH, MATCH |
| 17 | "precision of 1.00 and recall of .80" | 1.00, .80 | same | MATCH, MATCH |
| 17 | "Director-only … without error in both the second and final rounds" | 1.0 | `d3_r2_agreement.csv`, `238_…agreement.csv` agreement 1.0 | MATCH |
| 19 | "precision meets or exceeds recall in every round" | comparison | all five table rows | MATCH (derived) |
| 19 | "with 5 reference positives" | 5 | `238_…agreement.csv` | MATCH |
| 25 | Table Y row 1: 80, 29, .91, .80, .96, .79 | 6 values | `d3_agreement.csv`: 80, 29, .9125, .8034, .9583, .7931 | MATCH x6 |
| 26 | row 2: 29, 5, .93, .71, 1.00 [.29, 1.00], .60 [.15, .95] | 8 values | `d3_r2_agreement.csv`: 29, 5, .931, .7129, 1.0 [.2924, 1.0], .6 [.1466, .9473] | MATCH x8 |
| 27 | row 3: 38, 19, .92, .84, 1.00 [.79, 1.00], .84 [.60, .97] | 8 values | `d3_audit_recall_by_stratum.csv` treated, PRIMARY: 38, 19, .9211, .8421, 1.0 [.794, 1.000], .8421 [.604, .966] | MATCH x8 |
| 28 | row 4: 39, 16, .87, .73, .92 [.64, 1.00], .75 [.48, .93] | 8 values | control, PRIMARY: 39, 16, .8718, .7273, .9231 [.640, .998], .75 [.476, .927] | MATCH x8 |
| 29 | row 5: 30, 5, .97, .87, 1.00 [.40, 1.00], .80 [.28, .99] | 8 values | `238_new_document_agreement.csv` PRIMARY: 30, 5, .9667, .8696, 1.0 [.3976, 1.0], .8 [.2836, .9949] | MATCH x8 |
| 31 | "Round 1 includes 7 calibration filings from T-Mobile" | 7 | `d3_agreement.csv`: 80 vs 73 "excl. T-Mobile calibration 7" | MATCH |

### drafts/e3_sample.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 3 | "1,054 breach notification records" | 1,054 | `e_ledger.csv` row 1 | MATCH |
| 5 | "Of the 1,054 records, 758 resolve" | 1,054, 758 | `e_ledger.csv` | MATCH, MATCH |
| 5 | "remaining 296 fall into six exclusion grades" | 296, 6 | FACTS "Gate 1 / records lost" = 296; six EXCLUDED/AMBIGUOUS grades | MATCH, MATCH |
| 5 | "281 records name organizations that no EDGAR registrant could be matched to" | 281 | FACTS EXCLUDED-UNRESOLVED | MATCH |
| 5 | "5 name private firms" | 5 | EXCLUDED-PRIVATE | MATCH |
| 5 | "4 … private during the breach window" | 4 | EXCLUDED-PRIVATE-WINDOW | MATCH |
| 5 | "2 predate the firm's initial public offering" | 2 | EXCLUDED-PRE-IPO | MATCH |
| 5 | "2 name firms with no U.S. listing" | 2 | EXCLUDED-NO-US-LISTING | MATCH |
| 5 | "2 remain ambiguous" | 2 | AMBIGUOUS | MATCH |
| 5 | "yields 524 firm-day events" | 524 | `e_ledger.csv` | MATCH |
| 5 | "gaps of no more than three days" | 3 | FACTS "Gate 2 / adjacency-collapse rule as coded" | DEFINITION (consistent) |
| 5 | "Of 32 adjacency chains examined, the rule collapses 28; the other 4" | 32, 28, 4 | FACTS Gate 2 (4 = 3 + 1 breach-type conflicts) | MATCH x3 |
| 5 | "reduces the count to 491" | 491 | `e_ledger.csv` | MATCH |
| 5 | "merges two further events" | 2 | `e_ledger.csv` note "re-collapse (-2)" | MATCH |
| 5 | "489 events: 118 treated and 371 control" | 489, 118, 371 | `e_ledger.csv` canonical row | MATCH x3 |
| 5 | "14 parent CIKs in 13 corporate families" | 14, 13 | `e_ledger.csv` canonical row | MATCH, MATCH |
| 7 | "The gate excludes 9 events" | 9 | FACTS "identity gate / events excluded" | MATCH |
| 7 | "6 of them T-Mobile USA events that predate the 2013 combination" | 6, 2013 | FACTS; `v4_212_links.csv` gate-excluded T-Mobile breach dates 2009-09-03 to 2012-08-28 | MATCH, MATCH |
| 7 | "For 7 events, the equity link and the outcome filer differ" | 7 | FACTS "outcome_cik / events where outcome_cik differs" | MATCH |
| 7 | "Linking retains 414 events: 111 treated and 303 control" | 414, 111, 303 | `e_ledger.csv` CRSP row | MATCH x3 |
| 9 | "no more than 550 days before it" | 550 | FACTS fiscal-year rule | DEFINITION |
| 9 | "available for 412 events" | 412 | `e_ledger.csv` | MATCH |
| 9 | "The two events lost at this step are treated: T-Mobile's November 2013 events" | 2, Nov 2013 | `e_ledger.csv` note (2013-11-01, 2013-11-26) | MATCH, MATCH |
| 9 | "narrowest margin … is 26 days" | 26 | FACTS "censoring / minimum margin" | MATCH |
| 9 | "median margin is 2,718 days" | 2,718 | FACTS "censoring / median margin" | MATCH |
| 9 | "from 730 days before to 180 days after" | 730, 180 | ledger label | DEFINITION |
| 9 | "at least 150 daily returns" | 150 | ledger label | DEFINITION |
| 9 | "405 events: 109 treated and 296 control" | 405, 109, 296 | constants | MATCH x3 |
| 9 | "Every event lost at this final step is a control event whose firm had listed too recently" | 7 control | recomputed: 7 excluded rows, all control, `prior12m_ndays_rd` 65 to 143 | MATCH (derived) |
| 11 | "spans 119 parent CIKs, 13 of which contain treated events" | 119, 13 | constants | MATCH, MATCH |
| 11 | "T-Mobile accounts for 26 of the 109 treated events (23.9%)" | 26, 109, 23.9% | FACTS "T-Mobile / …" | MATCH x3 |
| 11 | "T-Mobile and Sprint together account for 34.9%" | 34.9% | FACTS "T-Mobile + Sprint" (38 of 109) | MATCH |
| 11 | "Seven events precede the December 8, 2007 effective date … all seven are control" | 7, date, 0 treated | `e_ledger.csv` | MATCH x3 |
| 13 | "289 of the 405 events, 64 of them treated" | 289, 405, 64 | FACTS "breach type (analysis sample) / HACK" | MATCH x3 |
| 13 | "Insider incidents number 47 (22 treated)" | 47, 22 | FACTS INSD | MATCH, MATCH |
| 13 | "portable-device losses 26 (5 treated)" | 26, 5 | FACTS PORT | MATCH, MATCH |
| 13 | "unintended disclosures 18 (2 treated)" | 18, 2 | FACTS DISC | MATCH, MATCH |
| 13 | "physical losses 16 (12 treated)" | 16, 12 | FACTS PHYS | MATCH, MATCH |
| 13 | "the remaining events combine hacking with a second type" | 9 implied | derived: 405 - 396 = 9 = DISC+HACK 2, HACK+INSD 5, HACK+PORT 2 | MATCH (derived) |
| 15 | "For 11.9% of treated events" | 11.9% | FACTS anchor diagnostic, treated (13 of 109) | MATCH |
| 15 | "and 14.9% of control events" | 14.9% | FACTS anchor diagnostic, control = 14.5% (43 of 296) | **MISMATCH** |
| 15 | "a 180-day window measured from the breach date" | 180 | plan | DEFINITION |
| 21-24 | Table X rows 1-4: 1,054; 758; 524; 491 | 4 values | `e_ledger.csv` | MATCH x4 |
| 25 | Canonical: 489, 118, 371, 14, 7 | 5 values | `e_ledger.csv` | MATCH x5 |
| 26 | CRSP: 414, 111, 303, 13, 7 | 5 values | `e_ledger.csv` | MATCH x5 |
| 27-29 | three rows of 412, 109, 303, 13, 7 | 15 values | `e_ledger.csv` | MATCH x15 |
| 30 | Analysis sample: 405, 109, 296, 13, 7 | 5 values | `e_ledger.csv` | MATCH x5 |
| 32 | "December 8, 2007 effective date" | date | `scripts/224:63` | MATCH |

### drafts/e3_treatment.md

| Line | Fragment | Number | Source | Verdict |
|---|---|---|---|---|
| 3 | "(47 CFR § 64.2003)" | cite | none in listed files | DEFINITION, unverified (N3) |
| 5 | "applies two clauses" | 2 | `scripts/154_rebuild_s4_treatment.py` clause (a)/(b) | DEFINITION |
| 9 | "47 CFR § 64.5111" | cite | none in listed files | DEFINITION, unverified (N3) |
| 11 | "DISH Network is treated from July 1, 2020" | 2020-07-01 | `scripts/154_rebuild_s4_treatment.py:123-129` | MATCH |
| 11 | "The analysis sample contains no DISH event before that date" | 0 | recomputed: 2 DISH events in sample (2023-02-22, 2023-05-17), both treated | MATCH (derived) |
| 13 | "109 treated events" | 109 | constants `treated` | MATCH |
| 13 | "belonging to 13 parent CIKs" | 13 | constants `treated_parent_ciks` | MATCH |
| 13 | "in 12 corporate families" | 12 | `e_ledger.csv` final row `treated_corporate_families` | MATCH (see flag c2) |

---

## SUMMARY

| Draft | MATCH | MISMATCH | NO SOURCE | DEFINITION |
|---|---:|---:|---:|---:|
| e3_controls.md | 0 | 0 | 0 | 7 |
| e3_design.md | 5 | 0 | 0 | 3 |
| e3_estimation.md | 18 | 3 | 1 | 4 |
| e3_outcome.md | 78 | 2 | 1 | 4 |
| e3_sample.md | 94 | 1 | 0 | 5 |
| e3_treatment.md | 5 | 0 | 0 | 3 |
| **Total** | **200** | **6** | **2** | **26** |

Counting notes: each table cell and each confidence interval counts as one item. The two unverified legal citations in `e3_treatment.md` (N3) are counted under DEFINITION, not NO SOURCE.

### MISMATCH items

1. `e3_estimation.md:15` MDE80 30 days: draft .096, committed .0944.
2. `e3_estimation.md:15` MDE80 90 days: draft .233, committed .2234.
3. `e3_estimation.md:15` MDE80 180 days: draft .283, committed .2815.
4. `e3_outcome.md:11` treated 180-day departure rate: draft 31.2%, committed 30.3% (33 of 109).
5. `e3_outcome.md:13` CEO departures, treated, 90 days: draft 4, committed 3.
6. `e3_sample.md:15` control share with breach+180d before notification: draft 14.9%, committed 14.5% (43 of 296).

### NO SOURCE items

1. `e3_estimation.md:21` "conventional ticker-based match": the diagnostic is committed, the description of the earlier link as ticker-based is not.
2. `e3_outcome.md:15` model version for the earlier validation rounds: open placeholder, no committed source.
(Also unverified: 47 CFR § 64.2003 and § 64.5111 in `e3_treatment.md:3`, `:9`.)

### Flags

- (a) Superseded Query 2 figures: none.
- (b) Purge-list terms: none.
- (c) Wording: no hard violations; eleven items listed above. The ones most worth fixing are c2 (the 12/13 level is called "corporate families" while "parent entity" is used for the CIK-level unit), c4 (event counts read as departure counts), c10 (the 30-filing draw came from the 450 rebuild-added filings, not the whole sample) and c1 ("The essay").

### Aside, outside the brief

The seven events dropped at the last sample step include three "Block and Company, Inc." records (2016) with 88 to 119 daily returns. That return history fits Square/Block Inc.'s late-2015 listing, so the records may have been resolved to the wrong registrant. They are not in the analysis sample, so no draft number depends on it. Not investigated further.
