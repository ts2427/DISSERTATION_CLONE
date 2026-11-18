**Table 17**

*Specification Curve*

Panel A: Estimates by decision and option

| Decision | Option | Number | Median estimate | Range | CV3 p < .05 | CV1 p < .05 |
|:---|---:|---:|---:|---:|---:|---:|
| All specifications |  | 144 | 0.194 | 0.037 to 0.364 | 0 | 0 |
| Pre-window | [−60, −11] | 48 | 0.168 | 0.037 to 0.240 | 0 | 0 |
| Pre-window | [−45, −11] | 48 | 0.190 | 0.042 to 0.270 | 0 | 0 |
| Pre-window | [−25, −5] | 48 | 0.296 | 0.125 to 0.364 | 0 | 0 |
| Post-window | [+1, +5] | 36 | 0.227 | 0.178 to 0.364 | 0 | 0 |
| Post-window | [+1, +10] | 36 | 0.219 | 0.163 to 0.363 | 0 | 0 |
| Post-window | [+1, +20] | 36 | 0.181 | 0.107 to 0.301 | 0 | 0 |
| Post-window | [+5, +25] | 36 | 0.085 | 0.037 to 0.208 | 0 | 0 |
| Return benchmark | Market-adjusted | 48 | 0.178 | 0.037 to 0.350 | 0 | 0 |
| Return benchmark | Market model | 48 | 0.189 | 0.050 to 0.337 | 0 | 0 |
| Return benchmark | Fama–French three-factor | 48 | 0.218 | 0.065 to 0.364 | 0 | 0 |
| Return type | Simple | 72 | 0.195 | 0.049 to 0.363 | 0 | 0 |
| Return type | Log | 72 | 0.193 | 0.037 to 0.364 | 0 | 0 |
| Winsorizing | None | 72 | 0.209 | 0.054 to 0.364 | 0 | 0 |
| Winsorizing | 1st and 99th percentiles | 72 | 0.185 | 0.037 to 0.362 | 0 | 0 |

Panel B: Permutation test of the curve

| Statistic | Observed | Mean under the null | Permutation p | Percentile of the observed value |
|:---|---:|---:|---:|---:|
| Median estimate (two-sided) | 0.194 | 0.008 | .331 | 67.0 |
| Estimates sharing the dominant sign | 144 | 119.409 | .284 | 85.9 |
| Significant in the dominant direction (CV1) | 0 | 12.418 | > .999 | 30.1 |

*Note.* Each specification re-estimates the registrant coefficient of the primary model M4 (N = 333, G = 82) under one combination of five decisions: the pre-window, the post-window, the return benchmark, simple or log returns, and whether the outcome is winsorized at the 1st and 99th percentiles, for 3 × 4 × 3 × 2 × 2 = 144 specifications. Panel A summarizes the estimates for each option, pooling the specifications that use it, and counts those with p below .05 under CV3, the cluster jackknife standard error by parent filer entity, and under CV1, the cluster-robust standard error with the usual small-sample correction. All 144 estimates are positive, none is significant under either procedure, and the median estimate is 0.194. Panel B tests the whole curve by permutation (Simonsohn et al., 2020): in each of 1,000 draws, registration is reassigned at random to 12 of the 82 parent filer entities, and all 144 specifications are re-estimated. Each permutation p is the share of draws at least as extreme as the observed curve, for the median estimate, the count of estimates sharing the dominant sign, and the count significant in that direction under CV1; none is below .05. A curve of a single sign is common under the null here because every specification uses the same events, so the estimates move together: .283 of the null draws produce one.

**Table 18**

*Sensitivity of the Main Estimate*

Panel A: Leaving out one parent filer entity

| Check | Estimate (CV3 SE) | p | N |
|:---|---:|---:|---:|
| Full sample (primary) | 0.137 (0.193) | .481 | 333 |
| Without Sprint Corp (9 events), smallest | 0.029 |  | 324 |
| Without Intuit Inc. (76 events), largest | 0.213 |  | 257 |
| Share of the estimate removed by dropping Sprint Corp | 0.789 |  |  |

Panel B: Influential and pre-rule events

| Check | Estimate (CV3 SE) | p | N |
|:---|---:|---:|---:|
| Drop events with Cook’s distance above 4/N | 0.100 (0.123) | .420 | 315 |
| Drop events reported before the rule took effect | 0.130 (0.195) | .507 | 327 |

Panel C: Fixed effects and effective samples

| Fixed effects | Estimate (CV3 SE) | p | N | Mixed strata | Effective events (registrant) | Singletons dropped |
|:---|---:|---:|---:|---:|---:|---:|
| Year | 0.181 (0.227) | .427 | 333 | 13 of 18 | 281 (101) | 0 |
| Industry (two-digit SIC) | 0.293 (0.253) | .251 | 326 | 2 of 25 | 251 (104) | 7 |
| Year and industry | 0.249 (0.333) | .456 | 326 | 12 of 88 | 109 (64) | 7 |

Panel D: Revised dates

| Dates | Estimate (CV3 SE) | p | N (registrant) | Events changed |
|:---|---:|---:|---:|---:|
| Dates as used (primary) | 0.137 (0.193) | .481 | 333 (104) | 0 |
| Revised source reporting dates | 0.112 (0.188) | .552 | 333 (104) | 12 |
| Sprint’s corrected breach date (event added) | 0.137 (0.193) | .481 | 334 (105) | 1 |

*Note.* Each row re-estimates the registrant coefficient of the primary model M4 (N = 333, G = 82) with one change, with CV3 standard errors by parent filer entity. Panel A drops one parent filer entity at a time (82 re-estimates) and reports the smallest and largest estimates: dropping Sprint Corp (9 events) lowers the estimate to 0.029, removing 78.9 percent of it, and dropping Intuit Inc. (76 events) raises it to 0.213. Panel B drops the 18 events whose Cook's distance, a measure of how much all fitted values move when one observation is deleted, exceeds 4/N, and separately the 6 events reported before the rule took effect on December 8, 2007, none of them registrant events. Panel C adds fixed effects for reporting year, two-digit Standard Industrial Classification (SIC) industry, or both. A mixed stratum is a year, industry, or year-by-industry cell holding both registrant and other events; with fixed effects the coefficient is identified only within mixed strata, so events in single-group strata carry no weight (Aronow & Samii, 2016). Effective events counts the events in mixed strata, with registrant events in parentheses: year fixed effects leave 281, and both sets leave 109 events in 12 mixed cells. Industries with a single event drop as singletons (7 events). Panel D uses the revised reporting dates the source later published for 12 events and then corrects Sprint's breach date, which adds 1 event. No row gives a p-value below .05.

**Table 19**

*Test Program Summary*

| Family | Tests | BH family size | p < .05 |
|:---|---:|---:|---:|
| Disclosure delay | 11 | 11 | 0 |
| Disclosure delay, nonzero | 5 | 5 | 0 |
| Records per event and firm size | 2 | — | 0 |
| Industry-code-only group comparisons | 4 | — | 2 |
| Positive control (earnings decline) | 1 | — | 0 |
| Post-window length (dynamic path) | 3 | 3 | 0 |
| Announcement window | 4 | 4 | 3 |
| Size quartiles | 4 | 4 | 0 |
| Fixed effects | 3 | — | 0 |
| Pre-rule exclusion | 1 | — | 0 |
| Cook’s distance exclusion | 1 | — | 0 |
| Specification-curve permutation | 3 | — | 0 |
| Trading costs | 3 | 3 | 0 |
| All tests | 45 |  | 5 |

*Note.* Each row is one family of tests in the analysis program, which holds 45 tests. A family is a set of tests addressing one question. Within each family of more than one test, p-values are adjusted by the Benjamini–Hochberg (BH) false-discovery-rate procedure; single checks and joint tests use their own reference distributions. The last column counts tests with p below .05, using the CV3 cluster jackknife standard error where the test has one. Five tests give p below .05. Three are in the announcement-window family, and two of them are calibration checks expected to reject on earnings dates (the earnings elevation and the breach-minus-earnings contrast). The other two are composition checks, which compare the size and pre-breach volatility of events that industry codes treat but Form 499 does not with registrant events the codes also treat (p = .003 and p < .001); neither tests registration. One test of registration rejects: the registrant coefficient on announcement elevation (p = .027, BH-adjusted p = .036). If every null hypothesis were true, about 45 × .05 = 2.25 tests would give p below .05 by chance.
