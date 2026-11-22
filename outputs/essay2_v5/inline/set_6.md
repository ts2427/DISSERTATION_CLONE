**Table 13**

*Volatility Around the Agency Reporting Date*

Panel A: The exploratory family of four tests

| Test | Estimate (SE) | p | BH-adjusted p | N | Clusters | SE |
|:---|---:|---:|---:|---:|---:|---:|
| Elevation on earnings dates (mean) | 0.775 (0.055) | < .001 | < .001 | 5,094 | 79 | CV1, security |
| Elevation on breach reporting dates (mean) | −0.106 (0.054) | .052 | .052 | 333 | 82 | CV1, parent |
| Breach minus earnings (contrast) | −0.881 (0.083) | < .001 | < .001 | 5,427 | 83 | CV1, security |
| Form 499 registrant on breach elevation (exploratory) | 0.433 (0.192) | .027 | .036 | 333 | 82 | CV3, parent |

Panel B: Inference for the registrant coefficient

| Procedure | SE | df | p | 95% CI |
|:---|---:|---:|---:|---:|
| OLS, classical | 0.122 | 324 | < .001 | [0.192, 0.674] |
| HC1 | 0.137 | 324 | .002 | [0.164, 0.702] |
| HC3 | 0.141 | 324 | .002 | [0.156, 0.709] |
| CV1, parent filer entity | 0.159 | 81 | .008 | [0.116, 0.750] |
| CV3, parent filer entity (primary) | 0.192 | 81 | .027 | [0.050, 0.815] |
| Wild cluster, restricted, Rademacher weights (B=99,999) | — | — | .009 | [0.104, 0.777] |
| Wild cluster, unrestricted, Rademacher weights (B=99,999) | — | — | .006 | — |
| Wild cluster, restricted, Webb weights (B=9,999) | — | — | .011 | — |

Panel C: Adding controls in steps

| Controls | Estimate (CV3 SE) | p | Share of the movement |
|:---|---:|---:|---:|
| Registrant indicator only | 0.125 (0.113) | .275 | .00 |
| + baseline-window SD | 0.253 (0.204) | .218 | .42 |
| + baseline-window SD and log total assets | 0.375 (0.171) | .031 | .81 |
| All controls (exploratory) | 0.433 (0.192) | .027 | 1.00 |

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
| Sprint Corp | 9 (9) | 0.329 (0.153) | .035 | 324 |
| Twilio Inc | 2 (2) | 0.381 (0.190) | .049 | 331 |
| DISH Network Corp | 2 (2) | 0.403 (0.194) | .041 | 331 |
| GoDaddy Inc | 3 (3) | 0.410 (0.198) | .042 | 330 |
| Verizon Communications Inc | 11 (10) | 0.420 (0.204) | .043 | 322 |
| Charter Communications Inc | 8 (8) | 0.423 (0.205) | .043 | 325 |
| T-Mobile US Inc | 26 (26) | 0.435 (0.242) | .076 | 307 |
| Cable One Inc | 2 (2) | 0.450 (0.207) | .032 | 331 |
| Frontier Communications Parent Inc | 4 (4) | 0.458 (0.210) | .032 | 329 |
| Comcast Corp | 12 (9) | 0.465 (0.214) | .033 | 321 |
| Lumen Technologies Inc (formerly CenturyLink) | 5 (5) | 0.467 (0.208) | .028 | 328 |
| AT&T Inc | 24 (24) | 0.506 (0.203) | .015 | 309 |

Panel G: Sensitivities

| Specification | Estimate (CV3 SE) | p | CV1 p | N |
|:---|---:|---:|---:|---:|
| Exploratory model | 0.433 (0.192) | .027 | .008 | 333 |
| + breach severity (log records and attack-vector fixed effects) | 0.444 (0.207) | .035 | .009 | 333 |
| + flexible size (size-quartile fixed effects and size squared) | 0.489 (0.211) | .023 | .006 | 333 |
| + severity and flexible size | 0.490 (0.223) | .031 | .007 | 333 |
| Common support (other events within the registrant size range) | 0.416 (0.191) | .032 | .010 | 327 |

*Note.* Announcement elevation is the standard deviation (SD) of daily market-adjusted returns over the nine trading days [−4, +4] centered on the agency reporting date minus the SD over the three weeks before, [−25, −5]; each window needs returns on 8 of 9 and 17 of 21 days. Unless a row shows otherwise, each estimate is the Form 499 registrant coefficient from a regression of elevation on registration, baseline-window volatility, and the M4 controls (N = 333, G = 82). Panel A is the exploratory family of 4 tests: mean elevation on earnings-announcement dates, mean elevation on breach reporting dates, their contrast, and the registrant coefficient; the BH-adjusted p applies the Benjamini–Hochberg adjustment within that family. The two earnings tests are calibration checks expected to reject. The registrant coefficient is 0.433 (CV3 p = .027, BH-adjusted p = .036). Panel B repeats the test under each procedure in Table 10; every procedure gives p below .05. Panel C adds controls in steps; the baseline-window SD closes .42 of the distance from the unadjusted to the full-model coefficient, and log total assets brings the total to .81. Panel D is the placebo test: in each of 200 draws (seed 499), every security receives a random quiet date at least 120 trading days from any breach notification and 30 from any earnings date, and no draw matches the actual coefficient (0 of 200). Relative to their own quiet days, registrant events show elevation 0.008 higher on breach dates and other events 0.140 lower, so the difference comes from other events. Panel E reports the earnings-announcement benchmark, with SEs clustered by security. Panel F removes one treated parent filer entity at a time; the CV3 p stays below .05 in 11 of 12 removals but not when T-Mobile is removed (p = .076). Panel G adds the four sensitivities (breach severity, flexible size, both, and a common-support sample), each with CV3 p below .05.
