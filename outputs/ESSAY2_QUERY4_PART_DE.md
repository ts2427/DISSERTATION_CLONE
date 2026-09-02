# Essay 2 Query 4 — Parts D & E (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PART D/E: INFERENCE (N=331, G=81 parent-CIK clusters, G1=11 treated clusters — the matched pair)
==========================================================================================

## D2 — Cluster diagnostics (summclust-style, top 10 by partial leverage of the treatment dummy):
 cluster  size  leverage  partial_leverage_share  jackknife_coef
 1283699    26    0.0536                  0.0998          0.1274
 1136893    12    0.0573                  0.0718          0.0983
 1632127     2    0.0112                  0.0614          0.1831
 1166691    12    0.0215                  0.0534          0.1062
   20520     4    0.0116                  0.0520          0.1361
  732717    24    0.0712                  0.0460          0.2583
  320193     7    0.0273                  0.0459          0.1334
  101830     9    0.0167                  0.0411          0.0004
 1447669     2    0.0127                  0.0405          0.1752
 1609711     3    0.0218                  0.0401          0.1449

  CV of cluster sizes: 2.25 | effective clusters G* (Carter-Schnepel-Steigerwald, treatment partial leverage): 23.4 of G=81
  Cluster-deleted (jackknife) treatment coefficients: full-sample +0.1486; range across deletions [+0.0004, +0.2583]; largest single-cluster move = deleting 101830 -> +0.0004. Sign flips under deletion: 0 of 81. No deletion moves the estimate anywhere near significance — the direct answer to "is the null one firm?" And the most economical sentence available: deleting Sprint removes 100% of the (already null) point estimate — what little positive point estimate exists is almost entirely one carrier. That does not weaken the null; it deepens it.

## D5 — THE INFERENCE LADDER (treatment coefficient +0.1486 daily pp; G=81, G1=11):
                                                    procedure     se   ci_lo  ci_hi      p                                                           bias
                                HC3 (heteroskedasticity-only) 0.1321 -0.1112 0.4084 0.2613 ignores within-parent correlation -> SE too SMALL, p too small
                              CV1 cluster (parent CIK), t(80) 0.2021 -0.2535 0.5507 0.4643        downward-biased SE with few/unbalanced treated clusters
                                         CV3 jackknife, t(80) 0.2401 -0.3291 0.6263 0.5377           conservative; MNW-recommended corroborating interval
WCR wild cluster bootstrap (restricted, Rademacher, B=99,999)    NaN -0.2851 0.5731 0.5142   under-rejects with very few treated clusters (G1=11 is safe)
          WCU wild cluster bootstrap (unrestricted, B=99,999)    NaN     NaN    NaN 0.5870 over-rejects with few treated clusters — opposite failure mode
                        WCR, Webb six-point weights (B=9,999)    NaN     NaN    NaN 0.5196             robustness row; 2^G limit is on total G=81, not G1

  Reading: HC3 ignores within-parent correlation, so its p=.228 is a LOWER BOUND on the honest p-value; the p only moves one way as inference honors the design. WCR and WCU agree (p=0.514 vs 0.587); their failure modes run in opposite directions, so agreement is evidence neither pathology operates. MacKinnon-Webb rule-of-thumb danger zone ("G1=1 and G<500, or G1=2 and G<45, or G1=3 and G<20") does not trigger at G1=11 — quote in a footnote. Bootstrap implemented is the standard restricted WCR (boottest default), stated; WCR-S refinement not separately run.
  D6: randomization inference NOT run — the randomization hypothesis (exchangeability of carriers and non-carriers under the sharp null) is false here; permutation would over-reject under variance mismatch. Young (2019) not cited (Data Colada #99: HC1-vs-HC3 artifact). D7: Conley-Taber considered and rejected (requires small fixed N1 with N0->inf and an assignment condition unmet; Ferman & Pinto 2019); synthetic control unavailable (no treated pre-period, see E4).

==========================================================================================
## E — Design resolution (no observed power anywhere; Hoenig & Heisey 2001)
==========================================================================================
  E2: MDE (CV3 SE, t multipliers at df=G-1=80): (1.990 + 0.846) x 0.2401 = 0.6808 daily pp = 10.81pp annualized. (The HC3-based MDE 0.3698 understates this by 45% — the CV3 figure is the honest one.) Bloom (1995) imbalance factor at 31/69 allocation: 1.083 — imbalance inflates the MDE by only ~8% and is NOT the source of the null. This is a descriptive statement of design resolution, not a power calculation.

  E3: treated parent firms required for 80% power (cluster-mean approximation holding the control group and variance structure fixed — approximation stated):
 target_annualized_pp  target_daily_pp required_treated_parents  available
                    1            0.063                    >4000         11
                    2            0.126                    >4000         11
                    3            0.189                    >4000         11
                    4            0.252                     2136         11
                    5            0.315                      118         11

  E5: SESOI derived on distributional grounds (no commensurable literature magnitude exists — the 4.2pp anchor is retired, Part I1): m = 0.25 x control-group SD of the volatility change = 0.25 x 1.1012 = 0.2753 daily pp (4.37pp annualized) — a quarter-SD shift in the outcome distribution, below which a regulatory effect on uncertainty is of no practical import. Rainey (2014) equal-tailed 90% CI (CV3): [-0.2509, +0.5481] — NOT contained in (-m, +m), so a negligible effect CANNOT be affirmed at that SESOI.
  The FAILED converted-CAR TOST is reported, not omitted: against ±2.10pp-annualized (0.1323 daily), TOST p = 0.5270 on CV3 — equivalence not established at that (non-native) bound.
  E5 preserved distinction: MDE (0.6808) is not SESOI (0.2753); 80% power against an effect does not imply it can be equivalence-bounded beneath it (5%/20% error asymmetry).

  E6: verdict vocabulary — meaningful / negligible / INCONCLUSIVE. On the ladder above the estimate is: not significant under any procedure; not equivalence-bounded at the quarter-SD SESOI: INCONCLUSIVE — an underpowered null, stated as such. Abadie (2020 AER:Insights): failure to reject may be highly informative; the small-effect prior belongs in hypothesis development (the rule is a disclosure floor, not a ceiling — Part A).

Part D contributes ONE hypothesis (the main effect) under multiple inference procedures — procedures are not multiplied as tests. Part E contributes the equivalence test (one TOST family: 2 one-sided components + the Rainey CI restatement).
