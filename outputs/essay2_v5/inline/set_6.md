**Table 13**

*Volatility Around the Agency Reporting Date*

Panel A: The pre-specified family of four tests

| Test | Estimate (SE) | p | BH-adjusted p | N | Clusters | SE |
|:---|---:|---:|---:|---:|---:|---:|
| Elevation on earnings dates (mean) | 0.775 (0.055) | < .001 | < .001 | 5,094 | 79 | CV1, security |
| Elevation on breach reporting dates (mean) | −0.106 (0.054) | .052 | .052 | 333 | 82 | CV1, parent |
| Breach minus earnings (contrast) | −0.881 (0.083) | < .001 | < .001 | 5,427 | 83 | CV1, security |
| Form 499 registrant on breach elevation (pre-specified) | 0.433 (0.192) | .027 | .036 | 333 | 82 | CV3, parent |
| Bridge: registrant on elevation, committed market-model definition | 0.472 (0.200) | .021 | — | 331 | 81 | CV3, parent |

Panel B: Inference for the registrant coefficient

| Procedure | SE | df | p | 95% CI |
|:---|---:|---:|---:|---:|
| OLS, classical | 0.122 | 324 | < .001 | [0.192, 0.674] |
| HC1 | 0.137 | 324 | .002 | [0.164, 0.702] |
| HC3 | 0.141 | 324 | .002 | [0.156, 0.709] |
| CV1, parent filer entity | 0.159 | 81 | .008 | [0.116, 0.750] |
| CV3, parent filer entity (primary) | 0.192 | 81 | .027 | [0.050, 0.815] |
| Wild cluster, restricted, Rademacher weights (B=99,999) | — | — | .009 | [0.104, 0.777] |
| Wild cluster, unrestricted, Rademacher weights (B=99,999) | — | — | .545 | — |
| Wild cluster, restricted, Webb weights (B=9,999) | — | — | .011 | — |

Panel C: Adding controls in steps

| Controls | Estimate (CV3 SE) | p | Share of the movement |
|:---|---:|---:|---:|
| Registrant indicator only | 0.125 (0.113) | .275 | .00 |
| + baseline-window SD | 0.253 (0.204) | .218 | .42 |
| + baseline-window SD and log total assets | 0.375 (0.171) | .031 | .81 |
| All controls (pre-specified) | 0.433 (0.192) | .027 | 1.00 |

Panel D: Placebo dates

| Outcome | Actual estimate | Placebo mean (SD) | Draws at least as large | Draws with p < .05 | Draws |
|:---|---:|---:|---:|---:|---:|
| Change in abnormal return volatility (primary) | 0.137 | −0.058 (0.134) | 64 | 0 | 200 |
| Announcement elevation | 0.433 | 0.024 (0.132) | 0 | 1 | 200 |

Panel E: Earnings-announcement benchmark

| Outcome | Mean (SE) | p | Dates | Securities |
|:---|---:|---:|---:|---:|
| Change in volatility, earnings dates | 0.164 (0.028) | < .001 | 5,071 | 79 |
| Elevation, earnings dates | 0.775 (0.055) | < .001 | 5,094 | 79 |
| Change in volatility, breach reporting dates (sample mean) | −0.042 | — | 333 | 83 |

Panel F: Leaving out one treated parent filer entity

| Treated parent removed | Events removed (registrant) | Estimate (CV3 SE) | p | N |
|:---|---:|---:|---:|---:|
| Sprint Corporation | 9 (9) | 0.329 (0.153) | .035 | 324 |
| Twilio | 2 (2) | 0.381 (0.190) | .049 | 331 |
| DISH Network, LLC | 2 (2) | 0.403 (0.194) | .041 | 331 |
| GoDaddy.com, LLC | 3 (3) | 0.410 (0.198) | .042 | 330 |
| Verizon | 11 (10) | 0.420 (0.204) | .043 | 322 |
| Charter Communications, Inc. | 8 (8) | 0.423 (0.205) | .043 | 325 |
| T-Mobile USA, Inc. | 26 (26) | 0.435 (0.242) | .076 | 307 |
| Cable One, Inc. | 2 (2) | 0.450 (0.207) | .032 | 331 |
| Frontier Communications Parent, Inc. | 4 (4) | 0.458 (0.210) | .032 | 329 |
| Comcast Cable Communications LLC | 12 (9) | 0.465 (0.214) | .033 | 321 |
| CenturyLink | 5 (5) | 0.467 (0.208) | .028 | 328 |
| AT&T | 24 (24) | 0.506 (0.203) | .015 | 309 |

Panel G: Sensitivities

| Specification | Estimate (CV3 SE) | p | CV1 p | N |
|:---|---:|---:|---:|---:|
| Pre-specified model | 0.433 (0.192) | .027 | .008 | 333 |
| + breach severity (log records and attack-vector fixed effects) | 0.444 (0.207) | .035 | .009 | 333 |
| + flexible size (size-quartile fixed effects and size squared) | 0.489 (0.211) | .023 | .006 | 333 |
| + severity and flexible size | 0.490 (0.223) | .031 | .007 | 333 |
| Common support (other events within the registrant size range) | 0.416 (0.191) | .032 | .010 | 327 |

*Note.* Each estimate in Panels A, B, C, F and G is the coefficient on the Form 499 registrant indicator in a regression of announcement elevation on registration, the baseline-window volatility and the M4 controls, on the analytical sample (N = 333, G = 82 parent filer entities, 12 with registrant events) unless a row shows otherwise. Announcement elevation is the standard deviation (SD) of daily market-adjusted abnormal returns, RET − vwretd, over the nine trading days [−4, +4] centered on the agency reporting date (day 0) minus the same SD over the three weeks before, trading days [−25, −5]; each window must have returns on 8 of 9 and 17 of 21 days. Panel A is the pre-specified family of 4 tests: mean elevation on the sample securities’ earnings-announcement dates, mean elevation on breach reporting dates, their contrast, and the registrant coefficient. The BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within that family. The registrant coefficient is 0.433 (CV3 p = .027, BH-adjusted p = .036), and it clears .05 after the adjustment; the bridge row gives the registrant coefficient under the committed market-model definition of elevation. CV3 is the cluster jackknife standard error (SE) by parent filer entity, with t distribution p-values on G − 1 degrees of freedom; CV1 is the cluster-robust SE with the usual small-sample correction. Panel B repeats the registrant test under each inference procedure, defined as in Table 10; every procedure gives p below .05 except the unrestricted wild cluster bootstrap (p = .545). Panel C adds controls in steps; Share of the movement is how far each step moves the coefficient from the registrant-only value toward the full-model value, as a share of the whole distance: the baseline-window SD closes .42 of it and log total assets brings the total to .81. Panel D is the placebo test: in each of 200 draws (seed 499), every security in the sample gets a random date that lies at least 120 trading days from any of its breach notifications and at least 30 from any of its earnings dates, and the regression is re-estimated on those quiet days; the columns count the draws whose coefficient is at least as large in absolute value as the actual one and the draws with CV3 p below .05. No placebo draw matches the actual elevation coefficient (0 of 200). Compared with their own quiet days, registrant events show elevation 0.008 higher on breach reporting dates and other events −0.140, so the registrant difference comes from other events’ volatility falling below its quiet-day level. Panel E is the earnings-announcement benchmark: the mean of each outcome over the sample securities’ quarterly earnings dates, with SEs clustered by security. Panel F removes one treated parent filer entity at a time; the CV3 p-value stays below .05 for 11 of 12 removals and not when T-Mobile USA, Inc. is removed (p = .076). Panel G adds the four sensitivities to the pre-specified model: breach severity, flexible size, both, and a common-support sample; each keeps CV3 p below .05. RET is the daily stock return and vwretd the value-weighted market return, both from the Center for Research in Security Prices (CRSP); OLS is ordinary least squares.
