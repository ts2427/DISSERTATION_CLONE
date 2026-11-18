**Table 9**

*Hierarchical Model for H1*

| Variable | M1 | M2 | M3 | M4 |
|:---|---:|---:|---:|---:|
| Form 499 registrant |  |  | 0.139 (0.174) | 0.137 (0.193) |
|  p |  |  | .426 | .481 |
| Pre-window abnormal return volatility | −0.377 (0.112) | −0.359 (0.119) | −0.373 (0.116) | −0.368 (0.115) |
|  p | .001 | .003 | .002 | .002 |
| Disclosure gap (days) | 0.00006 (0.00024) | 0.00003 (0.00025) | 0.00003 (0.00027) | 0.00001 (0.00026) |
|  p | .813 | .895 | .901 | .982 |
| Log total assets |  | 0.031 (0.061) | 0.008 (0.062) | 0.000 (0.042) |
|  p |  | .610 | .895 | .997 |
| Leverage |  | 0.025 (0.196) | −0.021 (0.209) | −0.041 (0.226) |
|  p |  | .900 | .922 | .855 |
| Return on assets |  | 0.299 (0.681) | 0.297 (0.710) | 0.733 (0.608) |
|  p |  | .661 | .677 | .232 |
| Health-breach flag |  |  |  | −0.311 (0.217) |
|  p |  |  |  | .155 |
| Prior breach events |  |  |  | −0.006 (0.010) |
|  p |  |  |  | .551 |
| Intercept | 0.510 (0.164) | 0.131 (0.753) | 0.374 (0.762) | 0.529 (0.514) |
|  p | .003 | .862 | .625 | .307 |
| N | 333 | 333 | 333 | 333 |
| R² | .155 | .159 | .163 | .180 |
| Adjusted R² | .150 | .146 | .148 | .160 |

*Note.* Each column is an ordinary least squares (OLS) regression on the analytical sample (N = 333 events, 104 Form 499 registrant events). The dependent variable is the change in abnormal return volatility, defined in Table 2. M1 includes the pre-window volatility level and the disclosure gap; M2 adds log total assets, leverage, and return on assets; M3 adds the Form 499 registrant indicator, the test of H1; M4 adds the health-breach flag and prior breach events and is the primary model. Each cell shows the coefficient, its CV3 standard error in parentheses, and its p-value below. CV3 is the cluster jackknife standard error, clustered by parent filer entity (G = 82, 12 with registrant events); it re-estimates the model leaving out one parent at a time, and its p-values use the t distribution with 81 degrees of freedom. With the pre-window level as a regressor, each model is an analysis of covariance: the registrant coefficient compares post-window volatility across groups at the same pre-window level. Because the dependent variable contains the pre-window level, R² is not the share of post-disclosure volatility explained. In M4 the registrant coefficient is 0.137 (p = .481), and adding the indicator in M3 raises R² from .159 to .163. Disclosure-gap coefficients are per day.

**Table 10**

*Inference for the Registrant Coefficient*

Panel A: Inference ladder, clustering by parent filer entity

| Procedure | SE | df | p | 95% CI |
|:---|---:|---:|---:|---:|
| OLS, classical | 0.113 | 324 | .228 | [−0.086, 0.359] |
| HC1 | 0.112 | 324 | .225 | [−0.084, 0.358] |
| HC3 | 0.114 | 324 | .231 | [−0.087, 0.361] |
| CV1, parent filer entity | 0.161 | 81 | .398 | [−0.183, 0.457] |
| CV3, parent filer entity (primary) | 0.193 | 81 | .481 | [−0.248, 0.521] |
| Wild cluster, restricted, Rademacher weights (B=99,999) | — | — | .426 | [−0.198, 0.470] |
| Wild cluster, unrestricted, Rademacher weights (B=99,999) | — | — | .556 | — |
| Wild cluster, restricted, Webb weights (B=9,999) | — | — | .419 | — |

Panel B: Clustering by industry

| Procedure | SE | p |
|:---|---:|---:|
| CV1, two-digit SIC industry | 0.127 | .292 |
| CV3, two-digit SIC industry | 0.315 | .669 |

*Note.* Each row of Panel A reports a different standard error (SE) and test for the Form 499 registrant coefficient of the primary model M4 (0.137; N = 333). OLS assumes independent errors with equal variance. HC1 and HC3 allow the variance to differ across events but treat events as independent; HC3 inflates each residual by its leverage. CV1 clusters by parent filer entity with the usual small-sample correction. CV3, the primary procedure, is the cluster jackknife, which re-estimates the model leaving out one parent filer entity at a time; its p-values use the t distribution with 81 degrees of freedom. The three wild cluster bootstrap rows reweight parent-level residuals to simulate the distribution of the test statistic: the restricted version imposes a zero coefficient and the unrestricted version does not. Rademacher weights flip each parent's residuals with probability one half (99,999 draws); Webb weights draw from six points, which suits few clusters (9,999 draws); the seed is 499. Procedures that ignore clustering understate the SE when treatment varies across few parents: the HC1 SE (0.112) is 42 percent smaller than the CV3 SE (0.193). No procedure gives a p-value below .05. G is the number of parent filer entities (82), G1 the number with registrant events (12), and G* the effective number of clusters, 23.4, which adjusts G for unequal cluster sizes and the concentration of treatment (Carter et al., 2017); the coefficient of variation of cluster size is 2.25. An em dash (—) marks a procedure that produces no confidence interval. Panel B clusters by two-digit Standard Industrial Classification (SIC) industry (25 clusters).

**Table 11**

*Design Resolution: Equivalence and Power*

Panel A: Thresholds

| Quantity | Daily, pp | Annualized, pp |
|:---|---:|---:|
| Smallest effect size of interest (SESOI) | 0.191 | 3.03 |
| Equivalence bound from the announcement-return literature | 0.132 | 2.10 |
| Minimum detectable effect, CV3 (MDE80) | 0.548 | 8.69 |
| Minimum detectable effect, HC3 | 0.319 | 5.06 |
| MDE80 floor as treated parents grow without limit | 0.207 | 3.29 |

Panel B: Tests and design

| Quantity | Value |
|:---|---:|
| Registrant coefficient (CV3) | 0.137 |
| 90% confidence interval | [−0.185, 0.458] |
| 90% interval inside ±SESOI | No |
| TOST p, lower test (effect below −SESOI) | .047 |
| TOST p, upper test (effect above +SESOI) | .390 |
| TOST p against the literature bound | .509 |
| MDE80 as a multiple of SESOI | 2.87 |
| Treated parents needed for MDE80 of 5 pp annualized | 55 |
| Share of events that are registrant events | 0.312 |

*Note.* The table asks whether the primary estimate (M4; N = 333, G = 82) is precise enough to rule out effects that matter. Values are in percentage points (pp) of daily abnormal return volatility; annualized values multiply by √252. The smallest effect size of interest (SESOI) is 0.25 times the standard deviation of the dependent variable among other events (0.763), or 0.191 pp daily (3.03 pp annualized); no comparable volatility effect is reported in the literature, so the bound rests on the outcome's own spread. TOST (two one-sided tests) tests whether the effect is small enough to treat as practically zero: it runs one test that the effect is above −SESOI and one that it is below +SESOI, using the CV3 standard error and the t distribution with 81 degrees of freedom, and reports the larger p-value. The lower test rejects (p = .047), so effects below −SESOI are ruled out; the upper test does not (p = .390), so a positive effect as large as SESOI cannot be excluded. The 90 percent confidence interval, [−0.185, 0.458], corresponds to TOST at the 5 percent level and does not lie inside ±SESOI. The literature bound is ±2.10 pp, the two-day breach penalty reported by Cavusoglu et al. (2004), divided by √252 to 0.132 pp daily; its TOST p is .509. MDE80 is the minimum detectable effect, the smallest true effect the regression would detect approximately four times in five at the 5 percent level, computed as 2.84 times the CV3 standard error; it is 2.87 times SESOI. The HC3 row shows the MDE80 that heteroskedasticity-consistent standard errors would imply, 41 percent lower. An MDE80 of 5 pp annualized would require 55 treated parent filer entities, and as treated parents increase without limit the MDE80 falls only to 0.207 pp daily (3.29 pp annualized).
