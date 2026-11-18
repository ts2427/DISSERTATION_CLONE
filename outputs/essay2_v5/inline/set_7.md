**Table 14**

*Disclosure Delay by Registration*

Panel A: Delay regressions, all events

| Outcome | Controls | Estimate (CV3 SE) | p | CV1 p | Wild cluster p | MDE80 |
|:---|---:|---:|---:|---:|---:|---:|
| Delay, days (uncapped) | Earlier controls | 25.51 (49.58) | .608 | .512 | .574 | 140.58 |
| Delay, days (uncapped) | Current controls | 29.23 (53.35) | .585 | .487 | .551 | 151.30 |
| Delay, days (capped at P99) | Earlier controls | 10.03 (39.39) | .800 | .734 | .765 | 111.69 |
| Delay, days (capped at P99) | Current controls | 13.30 (42.51) | .755 | .679 | .715 | 120.53 |
| Log(1 + delay) | Earlier controls | −0.086 (0.655) | .895 | .855 | .869 | 1.857 |
| Log(1 + delay) | Current controls | −0.107 (0.668) | .873 | .831 | .845 | 1.893 |

Panel B: Nonzero delays only

| Outcome | Controls | Estimate (CV3 SE) | p | CV1 p | N (registrant) |
|:---|---:|---:|---:|---:|---:|
| Delay, days (uncapped) | Earlier controls | 46.51 (76.94) | .547 | .418 | 216 (62) |
| Delay, days (uncapped) | Current controls | 51.11 (82.29) | .536 | .396 | 216 (62) |
| Log(delay) | Earlier controls | 0.036 (0.549) | .948 | .914 | 216 (62) |
| Log(delay) | Current controls | 0.030 (0.590) | .959 | .933 | 216 (62) |

Panel C: Quantile regressions of the uncapped delay

| Quantile | Current controls: estimate (SE) | p | Earlier controls: estimate (SE) | p |
|:---|---:|---:|---:|---:|
| 10th percentile | 0.00 (7.81) | > .999 | 0.00 (7.47) | > .999 |
| 25th percentile | 0.00 (6.68) | > .999 | 0.00 (6.62) | > .999 |
| 50th percentile | −4.14 (7.75) | .593 | −4.55 (7.35) | .536 |
| 75th percentile | 13.88 (16.41) | .398 | 13.63 (16.29) | .403 |
| 90th percentile | 16.37 (40.12) | .684 | 0.61 (45.85) | .989 |

Panel D: Distribution of the uncapped delay

| Group | Events | Zero delays | Median | 90th percentile | Maximum | M (SD) |
|:---|---:|---:|---:|---:|---:|---:|
| Form 499 registrant events | 104 | 42 | 22 | 206 | 1917 | 98.9 (252.1) |
| Other events | 229 | 75 | 24 | 199 | 961 | 71.1 (125.5) |

Panel E: Tests of spread and shape

| Test | Statistic | p | SD, registrant | SD, other |
|:---|---:|---:|---:|---:|
| Brown–Forsythe test of equal spread, all delays | 2.361 | .125 | 252.1 | 125.5 |
| Brown–Forsythe test of equal spread, nonzero delays | 3.068 | .081 | 309.9 | 140.7 |
| Kolmogorov–Smirnov test of equal distributions, nonzero delays | 0.157 | .197 | — | — |
| Log-rank test of equal timing, nonzero delays | 2.791 | .095 | — | — |

*Note.* Each row of Panel A regresses a delay outcome on the Form 499 registrant indicator and controls in the analytical sample (N = 333, G = 82 parent filer entities, 12 with registrant events). Delay is the number of days from the breach date to the agency reporting date. Delays of −30 to −1 days, where the reporting date precedes the breach date by a field-level error, are set to 0. In all, 117 events have a zero delay (42 registrant, 75 other), because the source records the breach and its report on the same day or because a small negative delay was set to 0. The uncapped rows use the delay as recorded; the capped rows cap it at the in-sample 99th percentile (P99), 784.96 days, the disclosure gap of Table 2. The unadjusted difference in mean uncapped delay is 27.8 days, while Table 2 reports the capped gap of 12.13 days. The log rows use log(1 + delay) in Panel A and log(delay) on nonzero delays in Panel B. Current controls are the M4 controls with the pre-window volatility of the current outcome; earlier controls use the pre-window volatility of the earlier raw-return outcome. CV3 is the cluster jackknife standard error (SE) by parent filer entity, with p-values from the t distribution with G − 1 degrees of freedom; CV1 is the cluster-robust SE with the usual small-sample correction; the wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. MDE80 is the minimum detectable effect at 80 percent power, (t.975 + t.80) × SE_CV3, in the units of the outcome. No row gives p below .05. Panel B drops the zero delays (216 events, 62 registrant). Panel C reports quantile regressions of the uncapped delay at five quantiles with SEs in parentheses. Below the median the estimates carry no information: more than a quarter of the delays in each group are zero, so both groups’ 10th and 25th percentiles are 0 and the estimate there is 0 by construction. Panel D describes the uncapped delay by group. Panel E tests whether the two groups’ delays differ in spread or shape: the Brown–Forsythe test compares spread using deviations from each group’s median, the Kolmogorov–Smirnov test compares whole distributions, and the log-rank test compares the time to report as a survival curve; none gives p below .05. SD is the standard deviation and M the mean.

**Table 15**

*Trading-Cost Measures*

| Measure (change, post minus pre) | Estimate (CV3 SE) | p | BH-adjusted p | CV1 p | Correlation with the volatility change |
|:---|---:|---:|---:|---:|---:|
| Closing percent quoted spread (CPQS) | 0.00001 (0.00003) | .779 | .794 | .715 | 0.11 |
| EDGE spread estimator | 0.003 (0.005) | .485 | .794 | .310 | −0.02 |
| Log open-to-close Amihud illiquidity (OCAM) | 0.037 (0.142) | .794 | .794 | .696 | 0.10 |

*Note.* Each row regresses the change in one trading-cost measure, its mean over trading days [+1, +20] after the agency reporting date minus its mean over [−60, −11], on the Form 499 registrant indicator, the M4 controls and fixed effects for the calendar month of the reporting date, in the analytical sample (N = 333, 104 registrant events, G = 82 parent filer entities, 12 with registrant events). CPQS is the closing percent quoted spread, (ask − bid) divided by the quote midpoint, from valid uncrossed closing quotes, with values above 0.5 set to missing (Chung & Zhang, 2014); it is shown to five decimals because it is a fraction. EDGE is the efficient estimator of the bid–ask spread from open, high, low and close prices (Ardia et al., 2024). OCAM is the open-to-close Amihud illiquidity measure, the absolute open-to-close return divided by dollar volume (Barardehi et al., 2021); its window means are winsorized at the 1st and 99th percentiles within each window and then logged. OCAM is biased toward zero in large stocks, where dollar volume is high. Each window needs trading on at least 80 percent of its days. CV3 is the cluster jackknife standard error (SE) by parent filer entity, with p-values from the t distribution with G − 1 degrees of freedom; CV1 is the cluster-robust SE with the usual small-sample correction. The three measures form one family of 3 tests, and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it; no measure gives p below .05 before or after the adjustment. The last column is the Pearson correlation across events between the change in the measure and the change in abnormal return volatility; all three are small (at most .11 in absolute value), so trading costs and volatility move largely independently around the reporting date.
