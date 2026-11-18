**Table 16**

*Estimates by Size Quartile*

Panel A: Cell estimates

| Size quartile | Events (registrant) | Treated parents | G | Estimate (CV3 SE) | p | BH-adjusted p |
|:---|---:|---:|---:|---:|---:|---:|
| Q1 (smallest) | 86 (2) | 1 | 13 | −0.750 (0.862) | .401 | .535 |
| Q2 | 81 (14) | 4 | 36 | −0.180 (0.442) | .686 | .686 |
| Q3 | 83 (29) | 4 | 33 | 0.528 (0.584) | .372 | .535 |
| Q4 (largest) | 83 (59) | 5 | 12 | 0.389 (0.267) | .173 | .535 |

Panel B: Equivalence and power by cell

| Size quartile | df | 90% CI | Inside ±SESOI | MDE80 | MDE80 / SESOI |
|:---|---:|---:|---:|---:|---:|
| Q1 (smallest) | 12 | [−2.288, 0.787] | No | 2.632 | 13.80 |
| Q2 | 35 | [−0.927, 0.567] | No | 1.274 | 6.68 |
| Q3 | 32 | [−0.460, 1.517] | No | 1.687 | 8.85 |
| Q4 (largest) | 11 | [−0.090, 0.868] | No | 0.821 | 4.30 |

Panel C: Procedures that understate clustering

| Size quartile | HC1 p | HC3 p | BH-adjusted HC3 p | CV1 p | Wild cluster p |
|:---|---:|---:|---:|---:|---:|
| Q1 (smallest) | .001 | .005 | .020 | .012 | .537 |
| Q2 | .527 | .580 | .580 | .561 | .601 |
| Q3 | .029 | .037 | .049 | .191 | .163 |
| Q4 (largest) | .008 | .012 | .024 | .080 | .244 |

*Note.* Each row of Panel A re-estimates the primary model M4 within one quartile of log total assets in the analytical sample (333 events in all), with the CV3 standard error (SE) clustered by parent filer entity; G is the number of parent filer entities in the cell, and each cell’s CV3 p-values use the t distribution with that cell’s G − 1 degrees of freedom (df). Registrant events cluster at the top: Q4 holds 59 of 104, and Q1 rests on 2 registrant events at 1 treated parent, so its estimate compares one firm with the rest of the cell; Q1 also drops the health-breach flag, which does not vary there. The four cells form one family of 4 tests, and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it; no cell gives a BH-adjusted CV3 p below .05 (smallest .535). Panel B asks whether any cell can rule out effects that matter. The smallest effect size of interest (SESOI) is 0.191, 0.25 times the standard deviation of the dependent variable among other events in the full sample. A cell rules out a negligible effect only if its 90 percent confidence interval (CI) lies inside ±SESOI, the equivalence test at the 5 percent level; no cell’s interval does, so no cell is ruled out as negligible. MDE80, the minimum detectable effect at 80 percent power, is (t.975 + t.80, cell df) × SE_CV3; it runs from 0.821 to 2.632, or 4.30 to 13.80 times SESOI. Panel C shows the p-values from procedures that ignore or understate clustering, to document how they over-reject when few treated clusters sit in a cell: HC1 and HC3 treat events as independent and give p below .05 in 3 of the four cells, while CV3 rejects in none. HC1 and HC3 are heteroskedasticity-consistent SEs; CV1 is the cluster-robust SE with the usual small-sample correction; the wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. Q1 to Q4 are the size quartiles, Q1 smallest.
