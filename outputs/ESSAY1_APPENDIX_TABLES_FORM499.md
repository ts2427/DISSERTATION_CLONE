TOMBSTONE — RETIRED 2026-09-11. DO NOT CITE.

This file is the 7/28 audit-era Essay 1 appendix (pre-rebuild chain: 779 / 672 / 648, treated 127 / 118 / 115).
Every number in it is SUPERSEDED. That chain was replaced on 8/17-8/30/2026 by the canonical v3 rebuild:
  1,054 records -> 758 (Gate 1 entity verification) -> 524 (CIK+date dedup) -> 489 canonical events;
  Essay 1: CRSP 354 / regression 338 (104 treated, 11 parent filer CIKs).

Authoritative artifact: **constants_v3.json** (outputs/rebuild/constants_v3.json), with the live-computed Essay 1
appendix in outputs/rebuild/appendix_v3/ (scripts/158; Word build scripts/160). See also outputs/SAMPLE_ATTRITION_LEDGER.md (retired) and
outputs/PENDING_REBASELINE.md.

Committed 2026-09-11 for the record only, so the retired figures have a git history and can be cited as history.

---

# ESSAY 1 APPENDIX TABLES — FORM 499 CORRECTED (regenerated from final pipeline dataset)

Sample: 779 incidents. Treatment: fcc_form499.

TREATED COUNTS EXIST AT THREE LEVELS — every essay sentence citing a treated N must name its sample:
- Full sample: 127 treated of 779
- CRSP sample: 118 treated of 672 (37 organizations, 12 parent filer CIKs)
- Regression sample: 115 treated of 648 (35 organizations, 11 parent filer CIKs)

All values computed by the generator script — no hardcoded results.

## Table 1

Summary statistics. Panel A: full sample (N=779). Panel B: CRSP-matched sample (N=672; 118 treated incidents across 37 firms). Treatment: FCC Form 499 filer registry (primary-source verified, two-clause rule).

| Panel | Variable | N | Mean | SD | Min | Median | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A: Full sample | car_30d | 672 | -0.3961 | 8.9316 | -42.5551 | 0.18 | 34.0505 |
| A: Full sample | car_5d | 672 | -0.0799 | 4.1974 | -26.4131 | -0.0484 | 14.2089 |
| A: Full sample | firm_size_log | 713 | 10.4694 | 1.2757 | 5.0063 | 10.3786 | 14.7407 |
| A: Full sample | leverage | 716 | 0.7188 | 0.2444 | 0.1204 | 0.6853 | 2.5183 |
| A: Full sample | roa | 716 | 0.01 | 0.0358 | -0.3346 | 0.0072 | 0.2077 |
| A: Full sample | disclosure_delay_days | 779 | 119.5096 | 225.0441 | -1220 | 55.0 | 2153 |
| A: Full sample | records_affected_numeric | 779 | 3337544.1142 | 41454972.9628 | 0 | 19.0 | 1000000000 |
| A: Full sample | Form 499 treated (count) | 779 | 127.0 | - | - | - | - |
| A: Full sample | Immediate disclosure (count) | 779 | 190.0 | - | - | - | - |
| A: Full sample | Health breach (count) | 779 | 48.0 | - | - | - | - |
| A: Full sample | Prior breach 1yr (count) | 779 | 94.0 | - | - | - | - |
| B: CRSP sample | car_30d | 672 | -0.3961 | 8.9316 | -42.5551 | 0.18 | 34.0505 |
| B: CRSP sample | car_5d | 672 | -0.0799 | 4.1974 | -26.4131 | -0.0484 | 14.2089 |
| B: CRSP sample | firm_size_log | 648 | 10.5254 | 1.2416 | 5.6397 | 10.398 | 14.7407 |
| B: CRSP sample | leverage | 650 | 0.7221 | 0.2392 | 0.139 | 0.6927 | 2.5183 |
| B: CRSP sample | roa | 650 | 0.0108 | 0.0357 | -0.3346 | 0.007 | 0.2077 |
| B: CRSP sample | disclosure_delay_days | 672 | 126.8839 | 229.9708 | -4 | 57.0 | 2153 |
| B: CRSP sample | records_affected_numeric | 672 | 3548705.0982 | 44373771.9034 | 0 | 23.5 | 1000000000 |
| B: CRSP sample | Form 499 treated (count) | 672 | 118.0 | - | - | - | - |
| B: CRSP sample | Immediate disclosure (count) | 672 | 155.0 | - | - | - | - |
| B: CRSP sample | Health breach (count) | 672 | 40.0 | - | - | - | - |
| B: CRSP sample | Prior breach 1yr (count) | 672 | 80.0 | - | - | - | - |
| B: CRSP sample | Form 499 treated organizations (unique org_name) | - | 37.0 | - | - | - | - |
| B: CRSP sample | Form 499 treated parent filers (unique CIK) | - | 12.0 | - | - | - | - |

## Table 2

Mean 30-day CAR by subgroup, regression sample (N=648); every two-group split sums to 648. History split: prior_breaches_1yr > 0 vs = 0 (the variable is a 12-month COUNT; the H3 regression uses the count itself, not this dummy). Supersedes the 7/24 table (retired SIC-based flag, 125 treated, and a ==1/==0 history split that silently dropped 131 multi-prior observations).

| Comparison | Group | Mean CAR | SE | CI Lower | CI Upper | N |
| --- | --- | --- | --- | --- | --- | --- |
| Form 499 status | Form 499 filer | -0.5337 | 0.6071 | -1.7237 | 0.6563 | 115 |
| Form 499 status | Non-filer | -0.2258 | 0.4004 | -1.0106 | 0.559 | 533 |
| Form 499 status | Difference (Welch t) | -0.3079 | - | - | - | t=-0.42, p=0.672 |
| Disclosure speed | Immediate (<=7d) | 0.1147 | 0.7237 | -1.3037 | 1.5331 | 146 |
| Disclosure speed | Delayed (>7d) | -0.3954 | 0.3947 | -1.1691 | 0.3783 | 502 |
| Disclosure speed | Difference (Welch t) | 0.5101 | - | - | - | t=0.62, p=0.537 |
| Breach type | Health | -0.9399 | 1.5363 | -3.9511 | 2.0712 | 38 |
| Breach type | Non-health | -0.2394 | 0.3556 | -0.9363 | 0.4576 | 610 |
| Breach type | Difference (Welch t) | -0.7006 | - | - | - | t=-0.44, p=0.659 |
| History | Any prior breach, 1yr (count>0) | -0.0296 | 0.4866 | -0.9834 | 0.9242 | 208 |
| History | No prior breach, 1yr | -0.399 | 0.4556 | -1.292 | 0.4939 | 440 |
| History | Difference (Welch t) | 0.3694 | - | - | - | t=0.55, p=0.580 |

## Table 3

Main regression: 30-day CAR on H1-H4 variables, HC3 robust SEs, N=648. H2 row is the Form 499 corrected estimate (the SIC-based -2.21, p=.017 is retired as a misclassification artifact).

| Variable | Coefficient | SE | t-stat | P-value | CI Lower | CI Upper |
| --- | --- | --- | --- | --- | --- | --- |
| const | -3.7238 | 3.4545 | -1.078 | 0.2811 | -10.4944 | 3.0469 |
| fcc_form499 | -0.4234 | 0.7544 | -0.561 | 0.5747 | -1.9021 | 1.0553 |
| immediate_disclosure | 0.614 | 0.8728 | 0.704 | 0.4817 | -1.0967 | 2.3247 |
| prior_breaches_1yr | 0.0315 | 0.0683 | 0.461 | 0.6448 | -0.1024 | 0.1654 |
| health_breach | -0.3901 | 1.6341 | -0.239 | 0.8113 | -3.593 | 2.8127 |
| firm_size_log | 0.1761 | 0.2856 | 0.616 | 0.5376 | -0.3838 | 0.7359 |
| leverage | 1.7359 | 1.3682 | 1.269 | 0.2045 | -0.9456 | 4.4174 |
| roa | 23.021 | 8.7923 | 2.618 | 0.0088 | 5.7884 | 40.2536 |

## Table 4

H1 robustness: immediate-disclosure coefficient under sample restrictions (HC3). "Prior breach history" subsample = prior_breaches_1yr > 0 (N=208), the same definition as Table 2's history split.

| Restriction | Timing Coefficient | SE | P-value | N |
| --- | --- | --- | --- | --- |
| Full sample | 0.614 | 0.8728 | 0.4817 | 648 |
| Exclude largest decile | 0.4118 | 0.9375 | 0.6605 | 583 |
| Exclude smallest decile | 0.2306 | 0.8705 | 0.791 | 583 |
| Exclude outliers (3 SD) | 0.2604 | 0.7858 | 0.7404 | 637 |
| Form 499 filers only | -1.1304 | 1.5173 | 0.4563 | 115 |
| Non-filers only | 1.1037 | 1.0614 | 0.2984 | 533 |
| Non-health breaches | 0.41 | 0.8995 | 0.6485 | 610 |
| Prior breach history | 0.4623 | 1.0248 | 0.652 | 208 |

## Table 5

H1/H2 robustness to standard-error estimation method (N=648). Caveat for firm-clustered row: treated observations span only 12 parent filer CIK clusters (37 organizations roll up to 12 filers); cluster-robust inference with few treated clusters is conservative territory — HC3 remains the primary specification.

| Method | Timing Coef | Timing SE | Timing p | FCC Coef | FCC SE | FCC p |
| --- | --- | --- | --- | --- | --- | --- |
| OLS (classical) | 0.614 | 0.871 | 0.4811 | -0.4234 | 0.9405 | 0.6527 |
| HC1 | 0.614 | 0.8656 | 0.4781 | -0.4234 | 0.7476 | 0.5712 |
| HC2 | 0.614 | 0.8664 | 0.4785 | -0.4234 | 0.7486 | 0.5717 |
| HC3 | 0.614 | 0.8728 | 0.4817 | -0.4234 | 0.7544 | 0.5747 |
| Firm-clustered (CIK) | 0.614 | 0.9573 | 0.5213 | -0.4234 | 0.7226 | 0.5579 |
| Date-clustered | 0.614 | 0.9457 | 0.5161 | -0.4234 | 0.7652 | 0.5801 |

## Table 6

H1 heterogeneity: timing coefficient by firm-size quartile (HC3).

| Size Quartile | Timing Coefficient | SE | P-value | N |
| --- | --- | --- | --- | --- |
| Q1 | 1.434 | 2.7335 | 0.5999 | 162 |
| Q2 | -1.0192 | 1.2387 | 0.4106 | 162 |
| Q3 | -0.7318 | 1.9672 | 0.7099 | 162 |
| Q4 | 1.3031 | 1.3526 | 0.3354 | 162 |

## Table 7

H2 heterogeneity: Form 499 coefficient by firm-size quartile, with corrected treated counts per quartile. Treated incidents sum to 115 (the regression sample). The organization and parent-CIK columns count UNIQUE entities within each quartile and double-count across quartiles, because the same organization appears in different size quartiles across incidents (firm size varies over time); they therefore sum to more than the sample-wide totals of 35 organizations / 11 parent CIKs in the regression sample (37 / 12 in the CRSP sample).

| Size Quartile | FCC Coefficient | SE | P-value | N | Treated N | Treated Orgs | Treated Parent CIKs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | -0.0742 | 2.5393 | 0.9767 | 162 | 23 | 13 | 8 |
| Q2 | 0.5873 | 3.4559 | 0.8651 | 162 | 11 | 7 | 2 |
| Q3 | 2.052 | 1.9973 | 0.3042 | 162 | 23 | 11 | 3 |
| Q4 | -0.2336 | 1.0917 | 0.8306 | 162 | 58 | 16 | 4 |

## Table 8

H2 specification robustness under the descriptive framing (no causal claim). REPLACES the retired 7/24 "causal identification" table, whose values were hardcoded SIC-era placeholders (industry FE -1.94; falsification 0.23; matching -1.64) never computed by its script. The pre-breach falsification row is retired pending recomputation from CRSP daily data on final membership. Interpretation caveat for the industry-FE rows: Form 499 treatment is nearly collinear with telecom SIC codes (118 treated incidents, 12 parent filers), so within-industry estimates rest on minimal variation; the coefficient instability across FE specifications (all p>.14) reflects that thinness, not a detectable effect. The baseline HC3 and matched estimates are the informative rows.

| Specification | FCC Coefficient | SE | P-value | N |
| --- | --- | --- | --- | --- |
| Baseline (HC3) | -0.4234 | 0.7544 | 0.5747 | 648 |
| + Industry FE (SIC3) | 3.2643 | 2.2623 | 0.1491 | 648 |
| + Year FE | -1.0911 | 0.8387 | 0.1933 | 648 |
| + Industry and Year FE | 2.304 | 2.2381 | 0.3033 | 648 |
| PS matched (1:1 NN, no replacement) | -0.6553 | 0.983 | 0.5063 | 115 pairs |

## Table 9

H2 robustness to alternative explanations: market concentration and breach severity.

| Added Control | FCC Coefficient | FCC SE | FCC P-value | Control Coefficient | Control P-value | N |
| --- | --- | --- | --- | --- | --- | --- |
| HHI industry concentration | -0.4283 | 0.7571 | 0.5716 | -1.3e-05 | 0.918 | 648 |
| Breach severity (records affected) | -0.4682 | 0.757 | 0.5363 | 0.0 | 0.3171 | 648 |

## Table 10

Factor-model robustness on the common factor subsample (event-month factor controls added to the baseline spec; same construction as the pipeline reference scripts, treatment corrected to Form 499). Supersedes the hardcoded SIC-era table (-2.47/-2.12/-2.14/-2.22).

| Model | FCC Coefficient | SE | P-value | Timing Coefficient | Timing P-value | N |
| --- | --- | --- | --- | --- | --- | --- |
| Market-adjusted (baseline, factor subsample) | -0.4234 | 0.7544 | 0.5747 | 0.614 | 0.4817 | 648 |
| FF3 controls | -0.261 | 0.7742 | 0.736 | 0.6476 | 0.4612 | 648 |
| Carhart 4-factor controls | -0.1941 | 0.7821 | 0.804 | 0.6813 | 0.4379 | 648 |
| FF5 controls | -0.2549 | 0.7815 | 0.7442 | 0.6874 | 0.4336 | 648 |

## Table 11

Abnormal trading volume (log turnover, event [-5,+25] vs estimation [-240,-60]) regressed on the baseline spec, N=640. Computed live; supersedes the hardcoded 7/24 values.

| Variable | Coefficient | SE | P-value |
| --- | --- | --- | --- |
| fcc_form499 | -0.0456 | 0.0335 | 0.1741 |
| immediate_disclosure | 0.0235 | 0.0349 | 0.501 |
| prior_breaches_1yr | -0.0051 | 0.0026 | 0.0549 |
| health_breach | -0.0029 | 0.0555 | 0.958 |
| firm_size_log | 0.0219 | 0.0144 | 0.1265 |
| leverage | -0.0288 | 0.0596 | 0.6288 |
| roa | -0.0959 | 0.534 | 0.8575 |

## Table 12

Random forest (500 trees, seed 42) feature importance for 30-day CAR, N=648. Computed live; supersedes hardcoded 7/24 values.

| Rank | Feature | Importance |
| --- | --- | --- |
| 1 | roa | 0.3361 |
| 2 | firm_size_log | 0.3213 |
| 3 | leverage | 0.2279 |
| 4 | prior_breaches_1yr | 0.0576 |
| 5 | immediate_disclosure | 0.0272 |
| 6 | health_breach | 0.0171 |
| 7 | fcc_form499 | 0.0128 |

## Table 13

Pre-announcement market-adjusted cumulative abnormal returns (leakage test), 647 of the 648 regression-sample events; the remaining 1 lack sufficient pre-event CRSP trading history (>=35 trading days before the event). Event day = first trading day on/after breach_date (within 5 calendar days). Computed live; supersedes hardcoded 7/24 values.

| Window | Mean Cumulative AR (pp) | SE | t-stat | P-value | N |
| --- | --- | --- | --- | --- | --- |
| Day -30 to -21 | -0.0444 | 0.2118 | -0.209 | 0.8342 | 647 |
| Day -20 to -11 | 0.1733 | 0.2203 | 0.787 | 0.4318 | 647 |
| Day -10 to -2 | 0.0554 | 0.2057 | 0.269 | 0.7879 | 647 |

## Table 14

Equivalence testing (TOST, pre-specified bound ±2.1pp), N=648. H1-H3: bounded nulls. H4: inconclusive (CI exceeds bound). This table is new to the appendix; it carries the corrected essays' central claims.

| Hypothesis | Coefficient (pp) | SE | p (test of zero) | MDE 80% (pp) | TOST p (±2.10pp) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| H1 Immediate disclosure | 0.614 | 0.8728 | 0.4817 | 2.4439 | 0.0446 | Bounded null |
| H2 FCC regulation (Form 499) | -0.4234 | 0.7544 | 0.5747 | 2.1124 | 0.0133 | Bounded null |
| H3 Prior breaches | 0.0315 | 0.0683 | 0.6448 | 0.1913 | 0.0 | Bounded null |
| H4 Health breach | -0.3901 | 1.6341 | 0.8113 | 4.5756 | 0.1479 | Inconclusive |

