# Essay 3 Appendix

Analysis sample N = 405 events (109 treated, 296 control; G = 119 parent CIKs, G1 = 13 treated clusters, 12 treated parent entities). Tables are numbered in the order the Results section first mentions them. Every cell is read from a committed CSV under `outputs/essay3_q4/` or `outputs/essay3_q3/` and then formatted; nothing here is estimated. Built by `scripts/245_essay3_appendix.py`.

Conventions: coefficients, standard errors, confidence intervals and minimum detectable effects are in percentage points to two decimals; rates are percent to one decimal; p, kappa, precision and recall carry three decimals with no leading zero; counts use thousands separators; the minus sign is U+2212.

## SAMPLE AND TREATMENT

**Table 1**

*Sample Construction From Notification Records to the Analysis Sample*

**Panel A: Attrition ledger**

| Step | N | Treated events | Control events | Treated parent CIKs | Pre-rule treated | Pre-rule control |
|---|---|---|---|---|---|---|
| PRC notification records (master_breach_dataset.xlsx) | 1,054 |  |  |  |  |  |
| Gate 1: signed parent CIK | 758 |  |  |  |  |  |
| Stage 3: CIK+date firm-day events | 524 |  |  |  |  |  |
| Gate 2 adjacency collapse | 491 |  |  |  |  |  |
| Stage 4/5 canonical events (CANONICAL_V4) | 489 | 118 | 371 | 14 | 0 | 7 |
| CRSP data (has_crsp_data) | 414 | 111 | 303 | 13 | 0 | 7 |
|     Identity-gate rejections | 9 | 6 | 3 |  |  |  |
|     No acceptable security link | 66 | 1 | 65 |  |  |  |
| Compustat covariates (size, leverage, ROA) = Query 2 scope | 412 | 109 | 303 | 13 | 0 | 7 |
| Fully observed outcome window (pre-specified censoring rule) | 412 | 109 | 303 | 13 | 0 | 7 |
| Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK) | 412 | 109 | 303 | 13 | 0 | 7 |
| Prior 12-month market-adjusted return available (>=150 daily returns) | 405 | 109 | 296 | 13 | 0 | 7 |

**Panel B: Record resolution grades**

| Final resolution grade | Records |
|---|---|
| Verified | 473 |
| No matching registrant or unresolved | 281 |
| Verified at Gate 1 | 264 |
| Verified by reasoning | 19 |
| Private company | 5 |
| Private during the breach window | 4 |
| Adjudicated | 2 |
| No U.S. listing | 2 |
| Unresolved ambiguity | 2 |
| Pre-IPO | 2 |
| Total | 1,054 |

*Note.* Panel A rows above the canonical-event line are at the record level, where treatment is undefined; rows from the canonical event set down are at the event level. Parent CIKs are the clustering unit. Records per event have a mean of 1.55 and a maximum of 31 (Cencora, Inc., February 2024). Pre-rule is defined relative to the December 8, 2007 effective date of 47 C.F.R. § 64.2011. The two indented sub-rows decompose the 75 events lost at the security-link step. Sources: outputs/essay3_q4/table01.csv (Panel A, from outputs/essay3_v4/e_ledger.csv and outputs/rebuild_v4/v4_212_identity_review.csv); Data/processed/rebuild/stage2_signed.csv (Panel B); outputs/essay3_appendix/descriptive_counts.csv (records per event).

**Table 2**

*Treated Parent CIKs and Cluster Structure*

**Panel A: Treated parent CIKs**

| CIK | Name | Clause 1 events | Clause 2 events | Total treated | Control events on same CIK |
|---|---|---|---|---|---|
| 1,283,699 | T-Mobile USA, Inc. | 26 | 0 | 26 | 0 |
| 732,717 | AT&T | 15 | 9 | 24 | 2 |
| 101,830 | Sprint Corporation | 11 | 1 | 12 | 0 |
| 732,712 | Verizon | 10 | 0 | 10 | 1 |
| 1,166,691 | Comcast Cable Communications LLC | 1 | 8 | 9 | 3 |
| 1,091,667 | Charter Communications, Inc. | 0 | 8 | 8 | 0 |
| 18,926 | CenturyLink | 0 | 5 | 5 | 0 |
| 20,520 | Frontier Communications Parent, Inc. | 0 | 4 | 4 | 0 |
| 1,609,711 | GoDaddy.com, LLC | 3 | 0 | 3 | 0 |
| 1,001,082 | DISH Network, LLC | 0 | 2 | 2 | 0 |
| 1,447,669 | Twilio | 2 | 0 | 2 | 0 |
| 1,632,127 | Cable One, Inc. | 2 | 0 | 2 | 0 |
| 1,702,780 | Altice USA | 0 | 2 | 2 | 0 |
| Total |  | 70 | 39 | 109 | 6 |

**Panel B: Cluster structure**

| Cluster statistic | Value |
|---|---|
| Parent CIKs (G) | 119 |
| Treated clusters (G1) | 13 |
| Effective clusters (G*) | 24.5 |
| Cluster-size coefficient of variation | 2.328 |
| Singleton clusters | 61 |
| Largest cluster | Intuit, Inc. (CIK 896878): 78 events (19.3%) |
| Mixed clusters (hold treated and control events) | AT&T; Verizon; Comcast Cable Communications LLC |
| T-Mobile share of treated events | 26 of 109 (23.9%) |
| T-Mobile and Sprint share of treated events | 38 of 109 (34.9%) |

*Note.* Sample level is events within parent CIKs; inference clusters on parent CIK. Clause 1 is a direct Form 499 registry match; clause 2 is an adjudicated holding or parent-brand relationship. Eight CIKs carry clause 1 events and eight carry clause 2 events; three carry both (at&T, Sprint, Comcast), so the two counts reconcile to 13 CIKs. T-Mobile (1283699) and Sprint (101830) are separate parent CIKs and are clustered separately; they are one corporate family only in the entity count (12). Twilio and GoDaddy enter by direct registry match, not by the network-operator criterion. Both DISH events postdate July 1, 2020, the Boost Mobile divestiture that the date-conditional rule turns on. G* is the effective number of clusters. Sources: outputs/essay3_q4/table02.csv; outputs/essay3_v4/f1_ladder.csv; outputs/essay3_appendix/descriptive_counts.csv (singleton and largest-cluster rows).

**Table 3**

*Breach Type by Treatment Group*

| PRC breach type | Treated n | Treated % | Control n | Control % |
|---|---|---|---|---|
| HACK | 64 | 58.7 | 225 | 76.0 |
| INSD | 22 | 20.2 | 25 | 8.4 |
| PHYS | 12 | 11.0 | 4 | 1.4 |
| PORT | 5 | 4.6 | 21 | 7.1 |
| HACK+INSD | 3 | 2.8 | 2 | 0.7 |
| DISC | 2 | 1.8 | 16 | 5.4 |
| HACK+PORT | 1 | 0.9 | 1 | 0.3 |
| DISC+HACK | 0 | 0.0 | 2 | 0.7 |
| Total | 109 | 100.0 | 296 | 100.0 |

*Note.* Sample level is events (109 treated, 296 control). Breach types are the Privacy Rights Clearinghouse's own labels, carried through unchanged: HACK = HACK = Hacking or malware; INSD = Insider; PHYS = Physical records; PORT = Portable device; DISC = Unintended disclosure; HACK+INSD = Hacking and insider; HACK+PORT = Hacking and portable device; DISC+HACK = Unintended disclosure and hacking. Combined codes arise where an event collapses source records of more than one type. Column percentages sum to 100 within group. No test is performed. Source: outputs/essay3_q4/table03.csv.

**Table 4**

*Covariate Balance, Common Support, and Date Anchors*

**Panel A: Covariates**

| Covariate | Treated M (SD) | Control M (SD) | Standardized difference |
|---|---|---|---|
| Prior breaches, 1 year | 1.6605 (2.0959) | 4.1554 (7.3735) | −0.460 |
| Health information | 0.0183 (0.1348) | 0.0811 (0.2734) | −0.291 |
| Firm size (log total assets) | 11.5762 (1.2124) | 9.6945 (1.3849) | 1.446 |
| Leverage | 0.7251 (0.1630) | 0.6278 (0.2320) | 0.485 |
| Return on assets | 0.0222 (0.0471) | 0.0717 (0.1158) | −0.560 |
| Baseline departure rate (per year) | 1.0228 (0.8919) | 0.9349 (1.0550) | 0.090 |
| Prior 12-month market-adjusted return | −0.0222 (0.3152) | 0.0246 (0.2523) | −0.164 |

**Panel B: Common support**

| Common support, log total assets | Value |
|---|---|
| Treated range | [7.7421, 13.2206] |
| Control range | [6.4420, 12.8096] |
| Control events inside the treated range | 287 of 296 (97.0%) |
| Treated events inside the control range | 93 of 109 (85.3%) |

**Panel C: Date anchors**

| Anchor statistic | Treated | Control |
|---|---|---|
| Breach date equals notification date | 38.5% (42) | 29.1% (86) |
| Notification lag, median days | 22 | 27 |
| Notification lag, IQR days | [0, 94] | [0, 102] |
| Breach-anchored 180-day window closes before notification | 11.9% (13) | 14.5% (43) |

*Note.* Sample level is events (109 treated, 296 control). The standardized difference is the treated mean minus the control mean divided by the pooled standard deviation; the 0.1 benchmark follows Austin (2009). No balance tests are reported, because they would add unplanned hypothesis tests to the ledger. Panel B shows that common support is substantial: the imbalance in firm size is a shift in means, not a failure of overlap. Sources: outputs/essay3_q4/table04.csv, from outputs/essay3_q3/descriptives.csv; outputs/essay3_appendix/descriptive_counts.csv (Panel B).

## MEASUREMENT

**Table 5**

*Classifier Validation*

**Panel A: Four validation rounds**

| Round | N scored | Field | κ | Precision [95% CI] | Recall [95% CI] |
|---|---|---|---|---|---|
| Round 1 (earlier classifier version) | 80 | Executive departure | .803 | .958 | .793 |
| Round 1 (earlier classifier version) | 80 | Chief executive departure | .707 | .800 | .667 |
| Round 1 (earlier classifier version) | 80 | Director-only departure | .858 | 1.000 | .786 |
| Round 2 (out-of-sample) | 29 | Executive departure | .713 | 1.000 [.292, 1.000] | .600 [.147, .947] |
| Round 2 (out-of-sample) | 30 | Chief executive departure |  |  |  |
| Round 2 (out-of-sample) | 30 | Director-only departure | 1.000 | 1.000 [.664, 1.000] | 1.000 [.664, 1.000] |
| Stratified recall audit | 77 | Executive departure | .787 | .966 [.822, .999] | .800 [.631, .916] |
| Stratified recall audit | 79 | Chief executive departure | .530 | .571 [.184, .901] | .571 [.184, .901] |
| Stratified recall audit | 80 | Director-only departure | .746 | .818 [.482, .977] | .750 [.428, .945] |
| Final round (new documents) | 30 | Executive departure | .870 | 1.000 [.398, 1.000] | .800 [.284, .995] |
| Final round (new documents) | 30 | Chief executive departure | .000 | .000 [.000, .975] |  |
| Final round (new documents) | 30 | Director-only departure | 1.000 | 1.000 [.158, 1.000] | 1.000 [.158, 1.000] |

**Panel B: Stratified recall audit, by treatment group**

| Stratum | Reference departures | TP | FP | FN | Precision [95% CI] | Recall [95% CI] |
|---|---|---|---|---|---|---|
| Treated | 19 | 16 | 0 | 3 | 1.000 [.794, 1.000] | .842 [.604, .966] |
| Control | 16 | 12 | 1 | 4 | .923 [.640, .998] | .750 [.476, .927] |

*Note.* Sample level is filings. κ = Cohen's kappa; TP, FP, FN = true positives, false positives, false negatives. Reference codes were produced blind to the classifier: in rounds 1, 2 and the stratified audit the classifier's answers were sealed in a committed file before coding; in the final round the classifier had never been run on those documents and the reference codes were committed first. Round 1 scored an earlier classifier version. Confidence intervals are Clopper-Pearson. Unresolved rows are excluded under the primary scoring; the alternative scoring that forces them positive is in the source CSV. An empty cell means the field had no reference positives and no classifier positives, so the statistic is undefined. Sources: outputs/essay3_q4/table05.csv; outputs/essay3_q2/d3_audit_recall_by_stratum.csv.

## OUTCOMES

**Table 6**

*Item 5.02 Filings and Disclosed Departures by Window*

**Panel A: Rates by window and group**

| Window (days) | Group | N | Any Item 5.02 filing | Executive departure | Chief executive departure | Director-only departure |
|---|---|---|---|---|---|---|
| 30 | Treated | 109 | 26 (23.9%) | 4 (3.7%) | 0 (0.0%) | 8 (7.3%) |
| 30 | Control | 296 | 40 (13.5%) | 13 (4.4%) | 1 (0.3%) | 4 (1.4%) |
| 90 | Treated | 109 | 56 (51.4%) | 11 (10.1%) | 3 (2.8%) | 18 (16.5%) |
| 90 | Control | 296 | 123 (41.6%) | 43 (14.5%) | 8 (2.7%) | 20 (6.8%) |
| 180 | Treated | 109 | 82 (75.2%) | 33 (30.3%) | 8 (7.3%) | 21 (19.3%) |
| 180 | Control | 296 | 197 (66.6%) | 73 (24.7%) | 24 (8.1%) | 56 (18.9%) |

**Panel B: Crosswalk**

| Window (days) | Group | Filing, no executive departure | Over all events | Over events with a filing |
|---|---|---|---|---|
| 30 | Treated | 22 | 20.2% (22 of 109) | 84.6% (22 of 26) |
| 30 | Control | 27 | 9.1% (27 of 296) | 67.5% (27 of 40) |
| 30 | Pooled | 49 | 12.1% (49 of 405) | 74.2% (49 of 66) |
| 90 | Treated | 45 | 41.3% (45 of 109) | 80.4% (45 of 56) |
| 90 | Control | 80 | 27.0% (80 of 296) | 65.0% (80 of 123) |
| 90 | Pooled | 125 | 30.9% (125 of 405) | 69.8% (125 of 179) |
| 180 | Treated | 49 | 45.0% (49 of 109) | 59.8% (49 of 82) |
| 180 | Control | 124 | 41.9% (124 of 296) | 62.9% (124 of 197) |
| 180 | Pooled | 173 | 42.7% (173 of 405) | 62.0% (173 of 279) |

*Note.* Sample level is events (109 treated, 296 control). The notification anchor is used throughout; a window is (t0, t0 + w] and excludes a filing dated on t0 itself. An Item 5.02 filing is not a departure: Item 5.02 also covers appointments, elections and compensatory arrangements, and Panel B shows how often a filing in the window reports no executive departure at all. The chief executive model requires at least 10 events in each group and is therefore not estimated at any window; the counts are reported for description only. Sources: outputs/essay3_q4/table06.csv; outputs/essay3_q4/_d5_crosswalk.csv.

## ESTIMATES

**Table 7**

*Primary Estimates: Inference Ladder, Minimum Detectable Effects, Logit Check, and Controls*

**Panel A: Inference ladder, minimum detectable effects**

| Window (days) | Estimator | β (pp) | SE (pp) | p | 95% CI (pp) |
|---|---|---|---|---|---|
| 30 | HC3 (disqualified; reported per the analysis plan) | 0.40 | 2.54 | .876 |  |
|  | CV1 | 0.40 | 2.47 | .873 |  |
|  | CV3 | 0.40 | 3.34 | .906 | [−6.23, 7.02] |
|  | Wild cluster restricted bootstrap | 0.40 |  | .889 | [−5.53, 5.78] |
|  | Control departure rate | 4.39 |  |  |  |
|  | MDE (80% power, two-sided 5%) | 9.44 |  |  |  |
|  | MDE ÷ control rate | 2.15 |  |  |  |
| 90 | HC3 (disqualified; reported per the analysis plan) | −4.10 | 4.33 | .344 |  |
|  | CV1 | −4.10 | 4.99 | .413 |  |
|  | CV3 | −4.10 | 7.91 | .605 | [−19.76, 11.56] |
|  | Wild cluster restricted bootstrap | −4.10 |  | .514 | [−15.96, 8.05] |
|  | Control departure rate | 14.53 |  |  |  |
|  | MDE (80% power, two-sided 5%) | 22.34 |  |  |  |
|  | MDE ÷ control rate | 1.54 |  |  |  |
| 180 | HC3 (disqualified; reported per the analysis plan) | 2.33 | 6.10 | .703 |  |
|  | CV1 | 2.33 | 7.82 | .767 |  |
|  | CV3 | 2.33 | 9.96 | .816 | [−17.40, 22.06] |
|  | Wild cluster restricted bootstrap | 2.33 |  | .790 | [−15.76, 20.11] |
|  | Control departure rate | 24.66 |  |  |  |
|  | MDE (80% power, two-sided 5%) | 28.15 |  |  |  |
|  | MDE ÷ control rate | 1.14 |  |  |  |

**Panel B: Logit average marginal effects**

| Window (days) | AME (pp) | SE (pp) | Convergence |
|---|---|---|---|
| 30 | did not converge | did not converge | 35 iterations; ConvergenceWarning |
| 90 | −4.20 | 4.68 | converged in 6 iterations |
| 180 | 1.97 | 7.75 | converged in 5 iterations |

**Panel C: All terms, CV3**

| Window (days) | Term | β (pp) | CV3 SE (pp) | p |
|---|---|---|---|---|
| 30 | (Intercept) | 5.85 | 12.41 | .638 |
| 30 | Form 499 filer (treatment) | 0.40 | 3.34 | .906 |
| 30 | Prior breaches, 1 year | 0.22 | 0.56 | .692 |
| 30 | Health information | −3.81 | 1.94 | .052 |
| 30 | Firm size (log total assets) | −0.37 | 1.12 | .742 |
| 30 | Leverage | 1.99 | 5.36 | .711 |
| 30 | Return on assets | 5.90 | 16.29 | .718 |
| 30 | Baseline departure rate (per year) | −0.16 | 1.13 | .887 |
| 30 | Prior 12-month market-adjusted return | −0.10 | 5.16 | .984 |
| 90 | (Intercept) | 3.77 | 21.11 | .859 |
| 90 | Form 499 filer (treatment) | −4.10 | 7.91 | .605 |
| 90 | Prior breaches, 1 year | 0.25 | 0.57 | .660 |
| 90 | Health information | −2.44 | 7.41 | .742 |
| 90 | Firm size (log total assets) | 0.01 | 2.09 | .995 |
| 90 | Leverage | 7.46 | 14.28 | .602 |
| 90 | Return on assets | 28.83 | 50.96 | .573 |
| 90 | Baseline departure rate (per year) | 3.53 | 4.13 | .395 |
| 90 | Prior 12-month market-adjusted return | −10.78 | 9.18 | .243 |
| 180 | (Intercept) | −0.93 | 29.54 | .975 |
| 180 | Form 499 filer (treatment) | 2.33 | 9.96 | .816 |
| 180 | Prior breaches, 1 year | 0.72 | 1.16 | .537 |
| 180 | Health information | −3.72 | 9.86 | .706 |
| 180 | Firm size (log total assets) | 2.55 | 2.67 | .342 |
| 180 | Leverage | −1.92 | 19.54 | .922 |
| 180 | Return on assets | 3.51 | 41.05 | .932 |
| 180 | Baseline departure rate (per year) | −0.60 | 4.14 | .884 |
| 180 | Prior 12-month market-adjusted return | −10.14 | 10.69 | .345 |

*Note.* N = 405 events; G = 119 parent CIKs. Standard errors are clustered by parent CIK. β, SE, CI and MDE are in percentage points. HC3 ignores within-cluster correlation and is disqualified as an inferential rung; it is shown because the analysis plan specified the full ladder, and its p must never be read as significance. CV3 uses the t distribution with G − 1 = 118 degrees of freedom. The wild cluster restricted bootstrap uses B = 99,999 for p and B = 9,999 for confidence-interval inversion; it yields no standard error. The 30-day logit failed to converge (35 iterations, ConvergenceWarning), so its average marginal effect is not reported; there was no separation and no dropped observation at any window. Panel C coefficients are descriptive: they are not hypothesis tests and are outside the 31-test ledger. Sources: outputs/essay3_q4/table07.csv; b_control_coefficients.csv; c_logit_diagnostics.csv; outputs/essay3_v4/f1_ladder.csv.

**Table 8**

*Pre-Disclosure Placebo*

| Estimator | β (pp) or rate (%) | SE (pp) | p | 95% CI (pp) / n |
|---|---|---|---|---|
| HC3 (disqualified; reported per the analysis plan) | −8.62 | 5.60 | .124 |  |
| CV1 | −8.62 | 6.49 | .187 |  |
| CV3 | −8.62 | 8.49 | .312 | [−25.43, 8.18] |
| Wild cluster restricted bootstrap | −8.62 |  | .231 | [−23.24, 5.92] |
| Treated departure rate in the placebo window | 22.9 |  |  | 25 of 109 events |
| Control departure rate in the placebo window | 23.6 |  |  | 70 of 296 events |

*Note.* N = 405 events; G = 119 parent CIKs. The placebo outcome is an executive departure in (t0 − 180d, t0], the 180 days ending at notification. The interval is closed at t0, so a departure dated on the notification date falls in the placebo window and not in any outcome window. β, SE and CI are in percentage points. HC3 is disqualified as above. Sources: outputs/essay3_q4/table08.csv, from outputs/essay3_v4/f4_placebo.csv.

**Table 9**

*Sensitivity Analyses*

**Panel A: All 27 sensitivity specifications**

| Sensitivity | Window (days) | β (pp) | CV3 SE (pp) | CV3 p | Bootstrap p | BH-adjusted p | N |
|---|---|---|---|---|---|---|---|
| year FE (reported year) | 30 | 0.78 | 3.02 | .796 | .744 | .986 | 405 |
| year FE (reported year) | 90 | −1.65 | 7.05 | .815 | .750 | .986 | 405 |
| year FE (reported year) | 180 | 5.57 | 8.61 | .519 | .461 | .986 | 405 |
| two-digit SIC FE | 30 | 3.95 | 3.41 | .248 | .155 | .986 | 405 |
| two-digit SIC FE | 90 | 4.17 | 7.88 | .597 | .484 | .986 | 405 |
| two-digit SIC FE | 180 | 11.09 | 13.89 | .426 | .395 | .986 | 405 |
| breach_date anchor | 30 | −2.08 | 3.95 | .600 | .554 | .986 | 405 |
| breach_date anchor | 90 | −7.17 | 6.79 | .293 | .222 | .986 | 405 |
| breach_date anchor | 180 | −5.06 | 10.58 | .633 | .592 | .986 | 405 |
| excluding pre-announced departures | 30 | 1.71 | 3.03 | .572 | .527 | .986 | 405 |
| excluding pre-announced departures | 90 | −0.46 | 6.67 | .945 | .929 | .986 | 405 |
| excluding pre-announced departures | 180 | 5.64 | 10.04 | .576 | .545 | .986 | 405 |
| excluding the F2 baseline control | 30 | 0.38 | 3.17 | .905 | .893 | .986 | 405 |
| excluding the F2 baseline control | 90 | −3.70 | 8.00 | .645 | .605 | .986 | 405 |
| excluding the F2 baseline control | 180 | 2.26 | 9.75 | .817 | .801 | .986 | 405 |
| restatement-dated outcome (rs) | 30 | 3.42 | 5.89 | .562 | .666 | .986 | 405 |
| restatement-dated outcome (rs) | 90 | −1.07 | 9.66 | .912 | .894 | .986 | 405 |
| restatement-dated outcome (rs) | 180 | 0.30 | 14.80 | .984 | .984 | .986 | 405 |
| recall-corrected, audit point estimates (r_T=0.842, r_C=0.750) | 30 | 0.07 | 4.30 | .986 | .984 | .986 | 405 |
| recall-corrected, audit point estimates (r_T=0.842, r_C=0.750) | 90 | −6.82 | 10.34 | .511 | .404 | .986 | 405 |
| recall-corrected, audit point estimates (r_T=0.842, r_C=0.750) | 180 | −1.03 | 12.49 | .935 | .927 | .986 | 405 |
| recall-corrected, treated recall at CI low / control at CI high (r_T=0.604, r_C=0.927) [bounding exercise] | 30 | 2.22 | 4.37 | .613 | .574 | .986 | 405 |
| recall-corrected, treated recall at CI high / control at CI low (r_T=0.966, r_C=0.476) [bounding exercise] | 30 | −2.48 | 6.11 | .685 | .633 | .986 | 405 |
| recall-corrected, treated recall at CI low / control at CI high (r_T=0.604, r_C=0.927) [bounding exercise] | 90 | 0.96 | 9.61 | .921 | .902 | .986 | 405 |
| recall-corrected, treated recall at CI high / control at CI low (r_T=0.966, r_C=0.476) [bounding exercise] | 90 | −18.54 | 15.52 | .235 | .125 | .986 | 405 |
| recall-corrected, treated recall at CI low / control at CI high (r_T=0.604, r_C=0.927) [bounding exercise] | 180 | 18.83 | 14.23 | .188 | .168 | .986 | 405 |
| recall-corrected, treated recall at CI high / control at CI low (r_T=0.966, r_C=0.476) [bounding exercise] | 180 | −25.27 | 15.84 | .113 | .071 | .986 | 405 |

**Panel B: Two-digit SIC cells**

| Two-digit SIC cell | Events | Treated | Control |
|---|---|---|---|
| 48 (communications) | 144 | 104 | 40 |
| 73 (business services) | 146 | 5 | 141 |
| 34 cells, no treated events | 115 | 0 | 115 |
| Total | 405 | 109 | 296 |

*Note.* Sample level is events; every row retains all N = 405, so no specification drops a fixed-effect singleton or a missing SIC cell. β and SE are in percentage points. Benjamini-Hochberg is applied within the 27-test sensitivity family. HC3 does not appear: it is disqualified, and its standard error is not finite for the SIC fixed-effects rows, whose design is rank-deficient. The recall-corrected rows divide the outcome by the measured stratum recall; that correction is uncapped and corrects missed departures only, with no adjustment for false positives, and the two CI-endpoint rows are bounding exercises rather than estimates. The complete test ledger is 31 tests (3 primary, 1 placebo, 27 sensitivities); the chief executive family contributes 0 tests because its 10-event gate failed at every window. The full 36-cell SIC list is in outputs/essay3_v4/f3_sic2_cells.csv. Sources: outputs/essay3_q4/table09.csv; outputs/essay3_v4/i_tests.csv.

## ROBUSTNESS

**Table 10**

*Cluster Concentration*

**Panel A: Leave-one-cluster-out**

| Window (days) | Full-sample β (pp) | Range across deletions (pp) | Sign reversals | Reversing clusters (β without) | T-Mobile deleted (pp) | Sprint deleted (pp) |
|---|---|---|---|---|---|---|
| 30 | 0.40 | [−1.64, 2.00] | 3 | T-Mobile USA, Inc. (−1.64); Sprint Nextel (−0.25); Sirius XM Radio Inc. (−0.13) | −1.64 | −0.25 |
| 90 | −4.10 | [−6.87, 2.04] | 1 | Fidelity National Information Services, Inc. (2.04) | −6.87 | −4.24 |
| 180 | 2.33 | [−3.49, 6.23] | 1 | T-Mobile USA, Inc. (−3.49) | −3.49 | 1.66 |

**Panel B: Top ten clusters by share of CV3 jackknife variance**

| Window (days) | CIK | Cluster | Group | Events | Share of CV3 jackknife variance (%) | β without (pp) |
|---|---|---|---|---|---|---|
| 30 | 1,283,699 | T-Mobile USA, Inc. | Treated | 26 | 36.9 | −1.64 |
| 30 | 1,136,893 | Fidelity National Information Services, Inc. | Control | 12 | 22.7 | 2.00 |
| 30 | 1,889,539 | Corebridge Financial, Inc. | Control | 1 | 18.3 | 1.83 |
| 30 | 732,717 | AT&T | Treated | 26 | 4.2 | 1.09 |
| 30 | 101,830 | Sprint Nextel | Treated | 12 | 3.7 | −0.25 |
| 30 | 908,937 | Sirius XM Radio Inc. | Control | 15 | 2.4 | −0.13 |
| 30 | 320,193 | Apple Inc. | Control | 7 | 2.3 | 0.90 |
| 30 | 1,091,667 | Charter Communications, Inc. | Treated | 8 | 1.4 | 0.80 |
| 30 | 1,108,524 | Salesforce.com | Control | 1 | 1.1 | 0.04 |
| 30 | 1,137,789 | Seagate US LLC | Control | 3 | 1.0 | 0.73 |
| 90 | 1,136,893 | Fidelity National Information Services, Inc. | Control | 12 | 59.2 | 2.04 |
| 90 | 1,283,699 | T-Mobile USA, Inc. | Treated | 26 | 12.3 | −6.87 |
| 90 | 732,717 | AT&T | Treated | 26 | 5.9 | −2.15 |
| 90 | 908,937 | Sirius XM Radio Inc. | Control | 15 | 4.1 | −5.68 |
| 90 | 1,889,539 | Corebridge Financial, Inc. | Control | 1 | 2.4 | −2.85 |
| 90 | 20,520 | Frontier Communications | Treated | 4 | 1.9 | −5.17 |
| 90 | 1,001,082 | DISH Network, LLC | Treated | 2 | 1.7 | −5.11 |
| 90 | 1,041,061 | Yum! Brands, Inc. | Control | 1 | 1.3 | −3.18 |
| 90 | 789,019 | Microsoft Corporation | Control | 5 | 0.9 | −4.84 |
| 90 | 1,609,711 | GoDaddy.com LLC | Treated | 3 | 0.9 | −3.32 |
| 180 | 1,283,699 | T-Mobile USA, Inc. | Treated | 26 | 33.9 | −3.49 |
| 180 | 1,166,691 | Comcast | Treated | 12 | 15.2 | 6.23 |
| 180 | 1,136,893 | Fidelity National Information Services, Inc. | Control | 12 | 9.8 | 5.47 |
| 180 | 732,717 | AT&T | Treated | 26 | 9.4 | 5.41 |
| 180 | 1,001,082 | DISH Network, LLC | Treated | 2 | 4.3 | 0.25 |
| 180 | 908,937 | Sirius XM Radio Inc. | Control | 15 | 4.0 | 0.34 |
| 180 | 1,105,705 | Time Warner Inc. | Control | 8 | 2.7 | 0.68 |
| 180 | 1,091,667 | Charter Communications, Inc. | Treated | 8 | 2.3 | 3.86 |
| 180 | 732,712 | Verizon | Treated | 11 | 2.3 | 0.81 |
| 180 | 1,543,151 | Uber Technologies, Inc. | Control | 3 | 1.7 | 3.63 |

**Panel C: CCM-based overlap restriction**

| Window (days) | Sample | N | G | β (pp) | CV3 p | Bootstrap p |
|---|---|---|---|---|---|---|
| 30 | CCM-based overlap restriction | 347 | 83 | 1.77 | .585 | .466 |
| 30 | Full sample | 405 |  | 0.40 | .906 | .889 |
| 90 | CCM-based overlap restriction | 347 | 83 | −3.45 | .731 | .621 |
| 90 | Full sample | 405 |  | −4.10 | .605 | .514 |
| 180 | CCM-based overlap restriction | 347 | 83 | 2.08 | .852 | .818 |
| 180 | Full sample | 405 |  | 2.33 | .816 | .790 |

*Note.* Sample level is events within parent CIKs; G = 119 clusters. β is in percentage points. A sign reversal is a cluster whose deletion changes the sign of β. Panel C restricts to events that were also linked by the earlier ccm-based security link, which v4 replaced with a rebuilt CUSIP-to-permno link; it is a ccm-based overlap restriction and is not a ticker match. All 58 events removed in Panel C are control events across 37 parent CIKs; no treated event turns on the linker rebuild. Sources: outputs/essay3_q4/table10.csv; outputs/essay3_v4/f1_cv3_variance_shares.csv; outputs/essay3_v4/239_v3_overlap_sensitivity.csv.

## CASE EVIDENCE

**Table 11**

*T-Mobile Events and Executive Departures*

**Panel A: The 26 T-Mobile events**

| Breach date | Notification date | Treatment clause | Placebo | 30 days | 90 days | 180 days |
|---|---|---|---|---|---|---|
| 2014-01-02 | 2014-01-02 | 1 | N | N | N | N |
| 2015-09-14 | 2015-10-01 | 1 | N | N | N | Y |
| 2015-10-01 | 2015-10-01 | 1 | N | N | N | Y |
| 2015-11-04 | 2015-11-04 | 1 | N | N | N | Y |
| 2017-04-01 | 2017-06-09 | 1 | N | N | N | N |
| 2017-08-24 | 2017-09-14 | 1 | N | N | N | N |
| 2017-09-16 | 2017-10-02 | 1 | N | N | N | N |
| 2018-08-20 | 2018-08-23 | 1 | Y | N | N | N |
| 2019-11-26 | 2020-03-02 | 1 | Y | N | N | N |
| 2020-04-02 | 2020-04-02 | 1 | Y | N | N | N |
| 2020-04-15 | 2020-04-15 | 1 | Y | N | N | N |
| 2020-08-27 | 2020-12-08 | 1 | N | N | N | N |
| 2020-08-31 | 2020-10-09 | 1 | N | N | N | N |
| 2021-01-18 | 2021-02-09 | 1 | N | N | N | N |
| 2021-02-12 | 2021-03-16 | 1 | N | N | N | N |
| 2021-02-20 | 2021-03-31 | 1 | N | N | N | Y |
| 2021-03-01 | 2021-08-16 | 1 | N | N | Y | Y |
| 2021-03-31 | 2021-03-31 | 1 | N | N | N | Y |
| 2021-08-13 | 2021-08-16 | 1 | N | N | Y | Y |
| 2021-08-17 | 2021-08-19 | 1 | N | Y | Y | Y |
| 2021-08-26 | 2021-08-26 | 1 | N | Y | Y | Y |
| 2022-03-08 | 2022-03-08 | 1 | Y | N | N | N |
| 2022-11-25 | 2023-01-19 | 1 | N | Y | Y | Y |
| 2023-02-01 | 2023-04-28 | 1 | Y | N | N | Y |
| 2023-02-24 | 2023-04-28 | 1 | Y | N | N | Y |
| 2023-04-28 | 2023-04-28 | 1 | Y | N | N | Y |

**Panel B: The departures**

| Name | Title as stated in the filing | Filing date | Accession | Window placement | Outcome-window events (180 days) | Placebo-window events |
|---|---|---|---|---|---|---|
| Gary A. King | Executive Vice President and Chief Information Officer | 2016-02-19 | 0001193125-16-470124 | Outcome window | 3 | 0 |
| David A. Miller | Executive Vice President, General Counsel and Secretary | 2021-09-16 | 0001193125-21-275230 | Outcome window | 6 | 1 |
| Neville Ray | President, Technology | 2023-02-13 | 0001193125-23-035719 | Outcome window | 1 | 3 |
| Peter Ewens | Executive Vice President, Corporate Strategy & Development | 2023-09-08 | 0001193125-23-231377 | Outcome window | 3 | 0 |
| John Legere | Chief Executive Officer | 2019-11-18 | 0001193125-19-294093 | Placebo window | 0 | 3 |
| J. Braxton Carter | Executive Vice President and Chief Financial Officer | 2019-11-18 | 0001193125-19-294093 | Placebo window | 0 | 3 |

*Note.* Sample level is events in Panel A (all 26 T-Mobile events in the analysis sample, CIK 1283699) and persons in Panel B. Y/N marks whether at least one executive departure falls in that window. The 13 events with a 180-day departure resolve to only four distinct departures, because several breach records fall within 180 days of the same filing. The two event columns count, for each person, how many of the 26 events place that person's departure in the 180-day outcome window and how many place it in the placebo window; they are counted per person, and a person can appear in both. Legere and Carter fall in the placebo window of the 2019-11-26 event: their 8-K was filed 2019-11-18, eight days before that breach date and 105 days before the 2020-03-02 notification, so neither can be a response to either. Titles and context are taken verbatim from the filings; no filing links any departure to a breach. Sources: outputs/essay3_q4/table11.csv; outputs/essay3_q4/tmobile_502_text.md.

---

## ASSERTIONS

- T1 Panel B totals 1,054 **PASS**
- T1 Panel B every label is a GRADE_LABEL value **PASS**
- T1 Panel B no label is a raw final_grade code **PASS**
- T1 ledger closes (N never rises) **PASS**
- T1 treated + control == N at every populated step **PASS**
- T2 treated total == 109 **PASS**
- T2 clause totals == 70 / 39 **PASS**
- T3 totals == 109 / 296 **PASS**
- T6  30d treated + control == pooled on every count **PASS**
- T6  90d treated + control == pooled on every count **PASS**
- T6 180d treated + control == pooled on every count **PASS**
- T7 Panel A CV3 rows equal f1_ladder.csv **PASS**
- T9 Panel A has 27 rows **PASS**
- T9 Panel B events total 405 **PASS**
- T11 Panel A has 26 rows **PASS**
- T11 Panel B every title is verbatim in tmobile_502_text.md **PASS**
- T11 Panel B no title uses an abbreviation **PASS**
- T11 abbreviation regex is live (fires on 'EVP', quiet on the spelled-out title) **PASS**
- T11 Panel B title check has teeth (an abbreviated title is rejected) **PASS**
- T11 Panel B outcome-window column sums to 13 **PASS**
- T11 Panel B outcome-window sum equals Panel A 180-day Y count **PASS**
- Tables numbered 1-11 in order **PASS**
- No cell contains inf, nan, or a hyphen used as a minus sign **PASS**
- Note text contains no banned string (47 CFR, bare 'se', or a grade code) **PASS**

## NOT REGENERABLE

- none

## TEXT-TO-TABLE CHECK

163 figures checked; 0 MISMATCH. Full listing in `text_figures_check.csv`.

