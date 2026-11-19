# Deck graphics data (G1–G9): committed values for the new defense charts

Written 2026-11-19. Read-only on results: no canonical file, results script or committed output changed.
Every value below comes from a committed file, named with its key or row. The per-item CSVs in this folder carry a `source` column on every row.
Treated counts name their level (events, organizations or parent CIKs).

One new script, `scripts/275_defaud_graphics_ri.py` (G8), re-runs script 250's draw loop and asserts that the committed headline values reproduce.
To keep script 210 passing, its script allowlist bound moved from 274 to 275. The matching test in `scripts/217` was updated (275 allowed, 276 outside).

| Item | CSV | Source |
|:---|:---|:---|
| G1 | g1_caar_breach.csv | outputs/defense_supplement/deck_exhibits.csv, exhibit E1_caar |
| G2 | g2_essay1_funnel.csv | outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md (scripts/247) |
| G3 | g3_tmobile_2021-08-17.csv | deck_exhibits.csv, exhibit E1_tmobile |
| G4 | g4_sic_coverage.csv | outputs/essay2_v5/appendix/14_sic_conventions_vs_form499.csv (scripts/269) |
| G5 | g5_size_gradient.csv | appendix/05A_four_panel_decomposition.csv; appendix/27A_size_quartiles.csv, 27B, v5_t18c |
| G6 | g6_lopo.csv | v5_t14b_leave_one_parent_out.csv (= appendix/30A); appendix/24F_announcement_lotpo.csv (= v5_t18d) |
| G7 | g7_filings_vs_departures.csv | outputs/essay3_q4/table06.csv (scripts/244) |
| G8 | g8_ri_histograms.csv (+ .log) | scripts/275, a re-run of scripts/250 C1 with seed 250 |
| G9 | g9_confusion_matrix.csv | outputs/essay3_q2/d3_audit_agreement.csv (scripts/201) |

## Essay 1

### G1. CAAR paths, day −10 to +30 around the breach date
Source: deck_exhibits.csv, exhibit `E1_caar`, keys `{treated|control}_day{t}_caar` and `_aar`; N per group per day is in the `n` column.
- Sample: the E1 regression sample of 340 events.
- Treated: 106 Form 499 registrant events (event level) on every day.
- Control: 234 events on days −10 to +6 and 233 on days +7 to +30, because one control event loses its return series.
- CAAR is the cumulative sum, from day −10, of the cross-event mean abnormal return (AR).

| Day | Treated CAAR | Control CAAR |
|---:|---:|---:|
| −10 | 0.3716 | 0.0015 |
| −1 | 0.5275 | −0.4092 |
| 0 | 0.5417 | −0.4251 |
| +5 | −0.1723 | −0.7344 |
| +10 | −0.2359 | −0.7434 |
| +20 | −0.4947 | −0.5705 |
| +30 | −0.4050 | −0.3935 |

Summary keys in the same exhibit:
- CAAR(+30) − CAAR(−1): treated −0.9325, control 0.0157. This cross-checks against appendix_v3/table_3.csv (−0.933 and 0.014).
- CAR[0,+1]: −0.0785 / −0.2292.
- CAR[0,+5]: −0.6999 / −0.3252.

**Notification-anchored daily path: NO-SOURCE.** outputs/defense_supplement/e1_notification_anchored.csv holds only window regressions and means.
- Its D3 window means (treated, 104 events / control) are NCAR[0,+1] −0.4540 / −0.0025, NCAR[0,+5] −1.1320 / −0.1811 and NCAR[0,+30] −0.3367 / 0.7220.
- At [0,+30] the control count is 231.

### G2. Essay 1 sample funnel
Source: ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md, sections "The chain" and "Treated counts at each level". Treated counts are events / organizations / parent CIKs.

| Step | Dropped | Remaining | Treated (events / orgs / parent CIKs) | Reason for drop |
|:---|---:|---:|:---|:---|
| Privacy Rights Clearinghouse (PRC) notification records | — | 1,054 records | NO-SOURCE | — |
| Gate 1: entity resolution | 296 | 758 records | NO-SOURCE | No parent CIK assignable |
| Stage 3: firm-day deduplication | 234 | 524 events | NO-SOURCE | Same parent CIK and breach date merge into one event |
| Gate 2: rolling-campaign rule | 35 | 489 events | 118 / 39 / 14 | Chained to an earlier event of the same parent |
| Stage 5: CRSP security link | 133 | 356 | 111 / 38 / 13 | No CRSP security on the breach date |
| Stage 6: complete covariates | 16 | **340** | **106 / 36 / 12** | A regression variable is missing (15 lack size, leverage and ROA; 1 lacks immediate_disclosure) |

### G3. T-Mobile worked example (day 0 = 2021-08-17, reported 2021-08-19)
Source: deck_exhibits.csv, exhibit `E1_tmobile`, keys `ar_dayNN_<date>` and `cum_dayNN`. AR = (ret − vwretd) × 100, and CAR is cumulated from day 0. Days −5 to −1 are **NO-SOURCE**: the exhibit starts at day 0.

| Day | AR | CAR |
|---:|---:|---:|
| 0 | 0.7395 | 0.7395 |
| +1 | 0.2887 | 1.0282 |
| +2 | 0.9840 | 2.0122 |
| +5 | −0.4513 | 0.8090 |
| +6 | −2.1119 | −1.3029 |
| +10 | −0.5318 | −3.9826 |
| +20 | −2.2868 | −10.7195 (trough) |
| +30 | 1.4241 | −7.2380 |

Other values in the exhibit:
- `car_30d` = −7.238 pp
- `mcap` = $175.63B (as of 2021-08-16)
- `dollar_car_30d` = −$12.71B

## Essay 2 (v5)

### G4. Industry-code coverage (inline Table 7)
Source: appendix/14_sic_conventions_vs_form499.csv, one row per convention. The same values are in constants_essay2.json under `values.sic_*`.
- Testable events: 346 canonical events with a Compustat SIC code, of which 107 are registrant events and 239 control events.
- Treated parent CIKs: 12.
- Two columns are arithmetic on committed columns rather than committed directly: treated events captured = 107 − FN, and control events included = FP.

| Convention (row key) | Treated parent CIKs captured (of 12) | Non-registrant parents included | Treated events captured (of 107) | Control events included (of 239) | Event agreement |
|:---|---:|---:|---:|---:|---:|
| Taken from published practice, 4812 + 4813 (`published_regulated_dummy_4812_4813`) | **6** | 0 | 81 | 3 | 91.6% |
| Earlier specification, 4813 + 4841 + 4899 (`prior_spec_4813_4841_4899`) | 9 | 1 | 44 | 6 | 80.1% |
| Tuned to the registry, 4812 + 4813 + 4841 + 4899 (`tuned_4812_4813_4841_4899`) | 10 | 1 | 102 | 9 | 96.0% |
| Full range, 4800–4899 (`full_range_4800_4899`) | 10 | 4 | 102 | 28 | 90.5% |

**"6 of 12" holds** in the published-practice row: `parents_identified` = 6 and `parents_missed` = 6. It agrees with constants `sic_published_parents_identified` = 6 and `sic_treated_parents_testable` = 12.
- The 6 parents missed (from appendix/15_sic_convention_errors.csv) are Cable One, Charter, Comcast (including NBCUniversal), DISH, GoDaddy and Twilio.

Generators for Tables 3–8: every source has a committed generator.
- scripts/269 writes appendix files 01, 05A/B, 06A/B, 07, 08A/B, 10A–C and 11–17.
- appendix/09 is copied from outputs/tables/essay2_v2/t31_gradient_grid.csv, which scripts/166 writes.
- missed_registrants_by_firm.csv and parent_filer_names.csv come from gated modes of scripts/274.
- The one open item is the literature citation for the published-practice convention in Table 7, which remains NO-SOURCE.

### G5. Size gradient by quartile
**(a) Record level, earlier specification.** Source: appendix/05A_four_panel_decomposition.csv, panels `i_industry_codes_records` (SIC) and `ii_form499_repaired` (Form 499).
- DV: raw-return volatility, on 891 records in market-value quartiles.
- Standard errors are HC3 only; CV3 is NO-SOURCE.

| Quartile | SIC coef (HC3 p) | Form 499 coef (HC3 p) | N | Treated records, SIC / Form 499 | Treated parents, SIC / Form 499 |
|:---|---:|---:|---:|---:|---:|
| Q1 | 7.556 (.009) | 5.148 (.069) | 229 | 33 / 43 | 7 / 9 |
| Q2 | 4.334 (.005) | 2.862 (.072) | 224 | 13 / 17 | 2 / 5 |
| Q3 | −2.877 (.160) | −3.190 (.113) | 215 | 21 / 22 | 5 / 5 |
| Q4 | −4.016 (.006) | −3.791 (.015) | 223 | 95 / 106 | 7 / 7 |

**(b) Event level, the version that reverses the pattern.** Source: same file, panels `iii_dedup_sic` and `iv_dedup_form499`.
- Sample: 339 canonical events in log-total-assets quartiles.
- Standard errors are HC3 only.

| Quartile | SIC coef (HC3 p) | Form 499 coef (HC3 p) | N | Treated events, SIC / Form 499 | Treated parents, SIC / Form 499 |
|:---|---:|---:|---:|---:|---:|
| Q1 | −13.084 (.025) | −13.084 (.025) | 86 | 2 / 2 | 1 / 1 |
| Q2 | 8.572 (.135) | 6.345 (.236) | 84 | 9 / 14 | 2 / 4 |
| Q3 | 11.016 (.069) | 11.016 (.069) | 84 | 31 / 31 | 4 / 4 |
| Q4 | 5.552 (.041) | 6.798 (.002) | 85 | 63 / 59 | 5 / 5 |

**(c) v5 market-adjusted volatility change, Form 499 definition.** Source: appendix/27A_size_quartiles.csv (= v5_t12). The ladder is in 27B and the 90% CIs in v5_t18c.

| Quartile | Coef | HC3 p | CV3 p | CV3 95% CI | N | Treated events | Treated parents |
|:---|---:|---:|---:|:---|---:|---:|---:|
| Q1 | −0.750 | .005 | .401 | [−2.629, 1.129] | 86 | 2 | 1 |
| Q2 | −0.180 | .580 | .686 | [−1.078, 0.717] | 81 | 14 | 4 |
| Q3 | 0.528 | .037 | .372 | [−0.661, 1.717] | 83 | 29 | 4 |
| Q4 | 0.389 | .012 | .173 | [−0.198, 0.976] | 83 | 59 | 5 |

NO-SOURCE:
- SIC-definition quartile coefficients on the v5 DV.
- CV3 for panels (a) and (b).
- A committed Essay 2 "Stage 2 item E3": none was found. The v5 CV3 quartiles in (c) are the committed equivalent.

### G6. Leave one parent out
**Volatility.** Source: v5_t14b_leave_one_parent_out.csv (= appendix/30A). It has 82 rows, with a `treated_parent` flag.
- The full-sample coefficient is 0.137 (constants `primary_coef`).
- The file holds coefficients only, so SE and p per deletion are NO-SOURCE.
- The overall maximum is a control parent, Intuit Inc., at 0.213.

Coefficient after removing each treated parent (CIK in parentheses):
- Sprint Corp (101830): 0.029 (the minimum)
- DISH (1001082): 0.087
- Comcast (1166691): 0.118
- T-Mobile (1283699): 0.119
- Verizon (732712): 0.128
- GoDaddy (1609711): 0.133
- Charter (1091667): 0.157
- Frontier (20520): 0.158
- Lumen/CenturyLink (18926): 0.159
- Twilio (1447669): 0.161
- Cable One (1632127): 0.171
- AT&T (732717): 0.211

**Announcement elevation.** Source: appendix/24F_announcement_lotpo.csv (= v5_t18d, checked row by row).
- The full-sample coefficient is 0.433, CV3 p = .027.
- Every removal has G = 81 and G1 = 11.

| Treated parent removed | Events (registrant) | Coef | CV3 p | N |
|:---|---:|---:|---:|---:|
| Sprint | 9 (9) | 0.329 | .035 | 324 |
| Twilio | 2 (2) | 0.381 | .049 | 331 |
| DISH | 2 (2) | 0.403 | .041 | 331 |
| GoDaddy | 3 (3) | 0.410 | .042 | 330 |
| Verizon | 11 (10) | 0.420 | .043 | 322 |
| Charter | 8 (8) | 0.423 | .043 | 325 |
| T-Mobile | 26 (26) | 0.435 | .076 | 307 |
| Cable One | 2 (2) | 0.450 | .032 | 331 |
| Frontier | 4 (4) | 0.458 | .032 | 329 |
| Comcast | 12 (9) | 0.465 | .033 | 321 |
| CenturyLink/Lumen | 5 (5) | 0.467 | .028 | 328 |
| AT&T | 24 (24) | 0.506 | .015 | 309 |

No committed Essay 2 "Stage 2 item E1" was found. v5_t18d / 24F is the committed leave-one-treated-parent-out.

## Essay 3 (v4)

### G7. Item 5.02 filings and executive departures
Source: outputs/essay3_q4/table06.csv. The appendix is ESSAY3_APPENDIX_TABLES.md, Panel A.
- Sample: 405 events.
- Treated: 109 Form 499 registrant events (event level), at 13 of the 119 parent CIKs.
- Control: 296 events.

| Window | Group | Events | Any Item 5.02 filing | Executive departure | table06 line |
|---:|:---|---:|---:|---:|---:|
| 30 | treated | 109 | 26 | 4 | 2 |
| 30 | control | 296 | 40 | 13 | 3 |
| 30 | total | 405 | 66 | 17 | 4 |
| 90 | treated | 109 | 56 | 11 | 5 |
| 90 | control | 296 | 123 | 43 | 6 |
| 90 | total | 405 | 179 | 54 | 7 |
| 180 | treated | 109 | 82 | 33 | 8 |
| 180 | control | 296 | **197** | **73** | 9 |
| 180 | total | 405 | 279 | 106 | 10 |

**Confirmed: 197 and 73 of 296 control events at 180 days** (line 9). These are also MATCH in DECK_PROVENANCE.csv rows 188, 189 and 192.

### G8. Randomization-inference distributions (C1, all 119 parents eligible, 9,999 draws, seed 250)
Source: g8_ri_histograms.csv, written by scripts/275, which re-runs scripts/250's own code and C1 draw loop.
- Each window has 40 equal-width bins between the minimum and maximum draw. Every row carries `obs_bin`, `coef_obs` and `ri_p_coef`.
- Before writing, scripts/275 asserted against outputs/defense_supplement/e3_randomization_inference.csv. All three windows PASS: RI p, observed coefficient and draw SD each match the committed value.

| Window | Observed coef | RI p (coef) | Draw coef SD |
|---:|---:|---:|---:|
| 30 | +0.003951 | .9037 | 0.037802 |
| 90 | −0.040982 | .5961 | 0.075306 |
| 180 | +0.023253 | .8455 | 0.112726 |

The re-run also passes 250's own reproduction assert against f1_ladder/f4_placebo, logged in g8_ri_histograms.log. No draws are written.

### G9. Classifier confusion matrix, executive-departure field (slide B7)
Source: outputs/essay3_q2/d3_audit_agreement.csv, row `exec departure (A)`, `PRIMARY (verified)`.
- `ref_Y` is the hand-verified reference label (truth) and `clf_Y` is the classifier label (scripts/201, line 89).
- TN = n − TP − FP − FN, because the file has no TN column. The derived TN reproduces the committed agreement (.8961) and kappa (.7874).

| | Reference: departure | Reference: none |
|:---|---:|---:|
| Classifier: departure | TP 28 | FP 1 |
| Classifier: none | FN 7 | TN 41 |

- n = 77, with 3 unclear cases excluded.
- Precision .966 [.822, .999], recall .800 [.631, .916].
- These match DECK_PROVENANCE.csv rows 367–372.
- Caveat: this is the audit of the Query 2-era (v2) classifier, not the v4 scoring in outputs/essay3_v4/238_scoring.md.

## NO-SOURCE summary
1. G1: notification-anchored daily CAAR path (only window means are committed).
2. G2: treated counts at the 1,054, 758 and 524 steps.
3. G3: T-Mobile ARs for days −5 to −1.
4. G4: literature citation for the published-practice convention (already open).
5. G5: SIC-definition quartile coefficients on the v5 DV, and CV3 for the record-level and event-level four-panel quartiles.
6. G6: SE and p per deletion for volatility leave-one-parent-out.
