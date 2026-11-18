**Table 1**

*Sample Construction*

Panel A: Attrition from notification records to analytical events

| Step | Removed | Remaining | Registrant events (organizations, parent filer entities) | Other events |
|:---|---:|---:|---:|---:|
| Records: Privacy Rights Clearinghouse notification records (start) | — | 1,054 | — | — |
| Records: not resolved to a public filer entity (entity resolution, Gate 1) | 296 | 758 | — | — |
| Records: duplicate records for the same filer and date removed | 234 | 524 | — | — |
| Records: removed at the Gate 2 adjacency review | 35 | 489 | — | — |
| Events: canonical events after Gate 2 | — | 489 | 118 (39, 14) | 371 |
| Events: no matched CRSP security | 128 | 361 | 111 (38, 13) | 250 |
| Events: no public notification date | 0 | 361 | 111 (38, 13) | 250 |
| Events: notified after December 31, 2024 | 6 | 355 | 111 (38, 13) | 244 |
| Events: volatility windows not computable | 4 | 351 | 109 (38, 13) | 242 |
| Events: Compustat controls incomplete | 15 | 336 | 105 (36, 12) | 231 |
| Events: disclosure gap not valid | 1 | 335 | 104 (36, 12) | 231 |
| Events: malformed records excluded (final sample) | 2 | 333 | 104 (36, 12) | 229 |

Panel B: Final sample by level

| Level | Total | Form 499 registrant | Other firm |
|:---|---:|---:|---:|
| Events | 333 | 104 | 229 |
| Organizations | 128 | 36 | 92 |
| Parent filer entities | 82 | 12 | 72 |

Panel C: Events by reporting year

| Year | Total | Registrant events | Other events | One group only |
|:---|---:|---:|---:|---:|
| 2007 | 6 | 0 | 6 | Other firms only |
| 2008 | 11 | 5 | 6 |  |
| 2009 | 3 | 3 | 0 | Registrants only |
| 2010 | 4 | 0 | 4 | Other firms only |
| 2011 | 2 | 0 | 2 | Other firms only |
| 2012 | 7 | 1 | 6 |  |
| 2013 | 14 | 1 | 13 |  |
| 2014 | 16 | 12 | 4 |  |
| 2015 | 20 | 7 | 13 |  |
| 2016 | 37 | 0 | 37 | Other firms only |
| 2017 | 44 | 12 | 32 |  |
| 2018 | 17 | 4 | 13 |  |
| 2019 | 23 | 9 | 14 |  |
| 2020 | 12 | 6 | 6 |  |
| 2021 | 19 | 9 | 10 |  |
| 2022 | 21 | 6 | 15 |  |
| 2023 | 48 | 14 | 34 |  |
| 2024 | 29 | 15 | 14 |  |
| Total | 333 | 104 | 229 |  |

*Note.* Panel A traces the sample from Privacy Rights Clearinghouse (PRC) notification records to analytical events. The first four rows count records and the remaining rows count canonical events; one breach can produce several records, so the starting 1,054 records are not 1,054 breaches. Gate 1 keeps a record only when the reporting organization resolves to a public filer entity. Gate 2 reviews records at the same parent filer entity with nearby dates and rules whether they describe one breach, so that each breach enters once. The registrant column gives Form 499 registrant events, with their organizations and parent filer entities in parentheses; an em dash (—) marks a count not tracked at that step. Panel B reports the final sample at three levels. The registrant and other parent counts sum to 84 rather than 82 because Comcast and Verizon each have events in both groups: the NBC Sports Group and Verizon Media events are other events. Panel C counts events by reporting year. The 5 years marked "one group only" hold 52 events, 3 of them registrant events, and contribute nothing to the estimate under year fixed effects. A Form 499 registrant event is an event at a firm registered on Federal Communications Commission (FCC) Form 499. The parent filer entity is the Securities and Exchange Commission (SEC) filer that owns the breached organization and is the clustering unit (G = 82). CRSP = Center for Research in Security Prices.

**Table 2**

*Descriptive Statistics by Registration*

Panel A: Dependent variable

| Variable | Form 499 registrant M (SD) | Other firm M (SD) | Difference (SE) | Welch t (df) | p |
|:---|---:|---:|---:|---:|---:|
| Change in abnormal return volatility | −0.02 (0.87) | −0.05 (0.76) | 0.04 (0.10) | 0.39 (177.49) | .700 |
| Pre-window abnormal return volatility, [−60, −11] | 1.66 (0.89) | 1.39 (0.79) | 0.27 (0.10) | 2.64 (179.07) | .009 |
| Post-window abnormal return volatility, [+1, +20] | 1.64 (1.04) | 1.33 (0.81) | 0.31 (0.12) | 2.67 (161.79) | .008 |

Panel B: Controls

| Variable | Form 499 registrant M (SD) | Other firm M (SD) | Difference (SE) | Welch t (df) | p |
|:---|---:|---:|---:|---:|---:|
| Log total assets | 11.61 (1.23) | 9.62 (1.37) | 1.99 (0.15) | 13.20 (220.12) | < .001 |
| Leverage | 0.72 (0.16) | 0.64 (0.22) | 0.08 (0.02) | 3.74 (259.57) | < .001 |
| Return on assets | 0.02 (0.05) | 0.08 (0.12) | −0.05 (0.01) | −5.63 (323.54) | < .001 |
| Health-breach flag | 0.00 (0.00) | 0.07 (0.25) | −0.07 (0.02) | −4.00 (228.00) | < .001 |
| Prior breach events | 10.03 (9.15) | 13.90 (21.12) | −3.88 (1.66) | −2.34 (330.45) | .020 |
| Disclosure gap (days) | 82.46 (159.29) | 70.33 (120.49) | 12.13 (17.53) | 0.69 (158.65) | .490 |

Panel C: Correlations of model variables

| Variable | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| (1) Change in abnormal return volatility | 1.00 |  |  |  |  |  |  |  |  |
| (2) Form 499 registrant | 0.02 | 1.00 |  |  |  |  |  |  |  |
| (3) Pre-window abnormal return volatility, [−60, −11] | −0.39 | 0.15 | 1.00 |  |  |  |  |  |  |
| (4) Disclosure gap (days) | 0.04 | 0.04 | −0.08 | 1.00 |  |  |  |  |  |
| (5) Log total assets | 0.07 | 0.57 | −0.05 | 0.11 | 1.00 |  |  |  |  |
| (6) Leverage | 0.02 | 0.18 | −0.03 | −0.02 | 0.07 | 1.00 |  |  |  |
| (7) Return on assets | 0.17 | −0.23 | −0.40 | −0.02 | −0.27 | 0.00 | 1.00 |  |  |
| (8) Health-breach flag | −0.11 | −0.15 | 0.10 | 0.09 | −0.03 | 0.13 | −0.02 | 1.00 |  |
| (9) Prior breach events | −0.01 | −0.10 | −0.19 | −0.12 | −0.25 | −0.13 | 0.48 | −0.14 | 1.00 |

*Note.* Each row compares the 104 Form 499 registrant events with the 229 other events in the analytical sample (N = 333). The dependent variable is the change in abnormal return volatility: the standard deviation (SD) of daily abnormal returns (the stock return minus the CRSP value-weighted market return), in percentage points, over trading days [+1, +20] after the agency reporting date minus the same SD over [−60, −11]; the pre-window and post-window rows report the two levels. M is the group mean. Difference is the registrant mean minus the other-firm mean, with its standard error (SE) in parentheses. The Welch t-test tests whether the two means are equal without assuming equal variances and uses Welch–Satterthwaite degrees of freedom (df), shown in parentheses; a p-value below .05 indicates that the means differ. The groups do not differ on the change (p = .700) but differ on both levels (p = .009 and .008) and on every control except the disclosure gap (p = .490). Log total assets is the natural log of Compustat total assets; leverage is total liabilities divided by total assets; return on assets is net income divided by total assets. The health-breach flag equals 1 when the breach record lists medical or health information as affected (15 events, all other events). Prior breach events counts earlier sample events at the same parent filer entity. The disclosure gap is the number of days from the breach date to the agency reporting date, with gaps of −30 to −1 days set to 0 and values capped at the 99th percentile (784.96 days). Panel C reports Pearson correlations; the largest in absolute value is between registration and log total assets (.57). CRSP = Center for Research in Security Prices.
