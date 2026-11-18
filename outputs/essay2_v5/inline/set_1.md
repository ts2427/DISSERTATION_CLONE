**Table 1**

*Sample Construction*

Panel A: Attrition from notification records to analytical events

| Step | Removed | Remaining | Registrant events | Registrant organizations | Registrant parent filer entities | Other events |
|:---|---:|---:|---:|---:|---:|---:|
| Records: Privacy Rights Clearinghouse notification records (start) | — | 1,054 | — | — | — | — |
| Records: not resolved to a public filer entity (entity resolution, Gate 1) | 296 | 758 | — | — | — | — |
| Records: duplicate records for the same filer and date removed | 234 | 524 | — | — | — | — |
| Records: removed at the Gate 2 adjacency review | 35 | 489 | — | — | — | — |
| Events: canonical events after Gate 2 | — | 489 | 118 | 39 | 14 | 371 |
| Events: no matched CRSP security | 128 | 361 | 111 | 38 | 13 | 250 |
| Events: no public notification date | 0 | 361 | 111 | 38 | 13 | 250 |
| Events: notified after December 31, 2024 | 6 | 355 | 111 | 38 | 13 | 244 |
| Events: volatility windows not computable | 4 | 351 | 109 | 38 | 13 | 242 |
| Events: Compustat controls incomplete | 15 | 336 | 105 | 36 | 12 | 231 |
| Events: disclosure gap not valid | 1 | 335 | 104 | 36 | 12 | 231 |
| Events: malformed records excluded (final sample) | 2 | 333 | 104 | 36 | 12 | 229 |

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

*Note.* The starting units are Privacy Rights Clearinghouse (PRC) notification records, not breaches; a breach can generate several records, and the record-level steps reduce records to events. Final sample: 333 events (104 Form 499 registrant events, 229 other), 128 organizations, and 82 parent filer entities (G = 82; 12 with registrant events). Of these, 2 parent filer entities (Comcast and Verizon) have both registrant and other events, so the registrant and other parent counts in Panel B sum to 84, not 82. Reporting dates run from 2007-01-10 to 2024-11-08. An em dash (—) marks a count the ledger does not track at that step. In Panel C, "one group only" marks years whose events are all registrant or all other events. Form 499 registrant = event at a firm registered with the Federal Communications Commission on FCC Form 499. Gate 1 = entity-resolution screen; Gate 2 = adjacency review of near-duplicate events. CRSP = Center for Research in Security Prices.

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

*Note.* Sample: 333 events (104 Form 499 registrant events, 229 other-firm events). Dependent variable: abnormal return volatility = SD of daily (RET − vwretd) in percentage points; change = post-window [+1, +20] minus pre-window [−60, −11], in trading days around the agency reporting date; the pre- and post-window rows give the two levels. Difference = Form 499 registrant mean minus other-firm mean; Welch t and p are from the unequal-variance two-sample t test, with Welch–Satterthwaite df. Correlations are Pearson, lower triangle, over all 333 events; column numbers refer to the numbered rows. Percentiles, minima and maxima are in the committed appendix CSV. Log total assets = natural log of Compustat total assets; leverage = total liabilities / total assets; return on assets = net income / total assets; health-breach flag = 1 when the record lists medical or health information as affected or the organization is a medical organization; prior breach events = earlier sample events at the same parent filer entity; disclosure gap = days from the breach date to the reporting date (negative gaps set to 0), top-coded at the 99th percentile. M = mean; SD = standard deviation; SE = standard error; df = degrees of freedom; Form 499 registrant = event at a firm registered with the Federal Communications Commission on FCC Form 499.
