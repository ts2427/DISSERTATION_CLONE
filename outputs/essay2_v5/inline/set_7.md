**Table 14**

*Disclosure Delay by Registration*

Panel A: Delay regressions, all events

| Outcome | Estimate (CV3 SE) | p | CV1 p | Wild cluster p | MDE80 |
|:---|---:|---:|---:|---:|---:|
| Delay, days (uncapped) | 29.23 (53.35) | .585 | .487 | .551 | 151.30 |
| Delay, days (capped at P99) | 13.30 (42.51) | .755 | .679 | .715 | 120.53 |
| Log(1 + delay) | −0.107 (0.668) | .873 | .831 | .845 | 1.893 |

Panel B: Nonzero delays only

| Outcome | Estimate (CV3 SE) | p | CV1 p | N (registrant) |
|:---|---:|---:|---:|---:|
| Delay, days (uncapped) | 51.11 (82.29) | .536 | .396 | 216 (62) |
| Log(delay) | 0.030 (0.590) | .959 | .933 | 216 (62) |

Panel C: Quantile regressions of the uncapped delay

| Quantile | Estimate (SE) | p |
|:---|---:|---:|
| 10th percentile | 0.00 (7.81) | > .999 |
| 25th percentile | 0.00 (6.68) | > .999 |
| 50th percentile | −4.14 (7.75) | .593 |
| 75th percentile | 13.88 (16.41) | .398 |
| 90th percentile | 16.37 (40.12) | .684 |

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

*Note.* Delay is the number of days from the breach date to the agency reporting date, with delays of −30 to −1 days, which arise from field-level errors, set to 0. Each row of Panel A regresses a delay outcome on the Form 499 registrant indicator and controls (N = 333, G = 82), with CV3 standard errors by parent filer entity. In all, 117 events have a zero delay (42 registrant, 75 other), because the source records the breach and its report on the same day or a small negative delay was set to 0. Uncapped rows use the delay as recorded; capped rows cap it at the 99th percentile (784.96 days), the disclosure gap of Table 2. The unadjusted difference in mean uncapped delay is 27.8 days; the capped difference in Table 2 is 12.13 days. Log rows use log(1 + delay) in Panel A and log(delay) on nonzero delays in Panel B, which drops the zero delays (216 events, 62 registrant). MDE80 is the minimum detectable effect at 80 percent power, in the units of the outcome. Panel C reports quantile regressions of the uncapped delay; at the 10th and 25th percentiles both groups' delays are 0, so those estimates are 0 by construction and carry no information. Panel D describes the uncapped delay by group. Panel E tests whether the groups' delays differ in spread or shape: the Brown–Forsythe test compares spread around each group's median, the Kolmogorov–Smirnov test compares whole distributions, and the log-rank test compares time to report. No test in the table gives a p-value below .05. CV1 and the wild cluster bootstrap are defined in Table 10.

**Table 15**

*Trading-Cost Measures*

| Measure (change, post minus pre) | Estimate (CV3 SE) | p | BH-adjusted p | CV1 p | Correlation with the volatility change |
|:---|---:|---:|---:|---:|---:|
| Closing percent quoted spread (CPQS) | 0.00001 (0.00003) | .779 | .794 | .715 | 0.11 |
| EDGE spread estimator | 0.003 (0.005) | .485 | .794 | .310 | −0.02 |
| Log open-to-close Amihud illiquidity (OCAM) | 0.037 (0.142) | .794 | .794 | .696 | 0.10 |

*Note.* Each row regresses the change in one trading-cost measure, its mean over trading days [+1, +20] after the agency reporting date minus its mean over [−60, −11], on the Form 499 registrant indicator, the M4 controls, and calendar-month fixed effects (N = 333, G = 82), with CV3 standard errors by parent filer entity. CPQS is the closing percent quoted spread, the ask minus the bid divided by the quote midpoint, from valid uncrossed closing quotes, with values above 0.5 set to missing (Chung & Zhang, 2014); it is a fraction and is shown to five decimals. EDGE is the efficient bid–ask spread estimator from open, high, low, and close prices (Ardia et al., 2024). OCAM is the open-to-close Amihud illiquidity measure, the absolute open-to-close return divided by dollar volume (Barardehi et al., 2021); its window means are winsorized at the 1st and 99th percentiles and logged. OCAM is biased toward zero in large stocks, where dollar volume is high. Each window needs trading on at least 80 percent of its days. The three measures form one family, and the BH-adjusted p applies the Benjamini–Hochberg adjustment within it; no measure gives p below .05 before or after adjustment. The last column is the Pearson correlation between the change in each measure and the change in abnormal return volatility; none exceeds .11 in absolute value, so trading costs and volatility move largely independently around the reporting date.
