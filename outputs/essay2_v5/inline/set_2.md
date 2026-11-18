**Table 3**

*How the Size Gradient Is Produced*

Panel A: Industry-code treatment on records

| Cell | Estimate (SE) | p | Records | Treated records | Treated parent filer entities |
|:---|---:|---:|---:|---:|---:|
| All | 1.190 (0.942) | .207 | 891 | 162 | 12 |
| Q1 (smallest) | 7.556 (2.850) | .009 | 229 | 33 | 7 |
| Q2 | 4.334 (1.522) | .005 | 224 | 13 | 2 |
| Q3 | −2.877 (2.042) | .160 | 215 | 21 | 5 |
| Q4 (largest) | −4.016 (1.456) | .006 | 223 | 95 | 7 |
| Q1 − Q4 spread | 11.571 |  |  |  |  |

Panel B: Form 499 treatment on the same records

| Cell | Estimate (SE) | p | Records | Treated records | Treated parent filer entities |
|:---|---:|---:|---:|---:|---:|
| All | 1.182 (0.952) | .214 | 891 | 188 | 15 |
| Q1 (smallest) | 5.148 (2.818) | .069 | 229 | 43 | 9 |
| Q2 | 2.862 (1.586) | .072 | 224 | 17 | 5 |
| Q3 | −3.190 (2.007) | .113 | 215 | 22 | 5 |
| Q4 (largest) | −3.791 (1.554) | .015 | 223 | 106 | 7 |
| Q1 − Q4 spread | 8.939 |  |  |  |  |

Panel C: Events instead of records, both definitions

| Cell | Industry codes: estimate (SE) | p | Treated events (parents) | Form 499: estimate (SE) | p | Treated events (parents) |
|:---|---:|---:|---:|---:|---:|---:|
| All (339 events) | 3.453 (1.879) | .067 | 105 (10) | 3.996 (1.802) | .027 | 106 (12) |
| Q1, smallest (86 events) | −13.084 (5.741) | .025 | 2 (1) | −13.084 (5.741) | .025 | 2 (1) |
| Q2 (84 events) | 8.572 (5.677) | .135 | 9 (2) | 6.345 (5.308) | .236 | 14 (4) |
| Q3 (84 events) | 11.016 (5.971) | .069 | 31 (4) | 11.016 (5.971) | .069 | 31 (4) |
| Q4, largest (85 events) | 5.552 (2.668) | .041 | 63 (5) | 6.798 (2.140) | .002 | 59 (5) |
| Q1 − Q4 spread | −18.636 |  |  | −19.882 |  |  |

Panel D: Concentration of records in events

| Measure | Value |
|:---|---:|
| Records | 891 |
| Events | 618 |
| Mean records per event | 1.44 |
| Median records per event | 1 |
| Events with more than one record | 115 |
| Records in those events | 388 |
| Records in the larger 2024 event at one parent filer entity | 31 |
| Records in the second 2024 event at that parent | 25 |
| Records in both 2024 events of that parent | 56 |

Panel E: Gradient on corrected data, 48 specifications

| Anchor date | Specifications | Q1 estimate above Q4 | Monotone decline Q1 to Q4 |
|:---|---:|---:|---:|
| Breach date | 24 | 0 | 0 |
| Notification date | 24 | 0 | 0 |
| Both anchors | 48 | 0 | 0 |

*Note.* Panels A and B reproduce the earlier specification: raw-return volatility on 891 notification records, size quartiles of log market value, and HC3 heteroskedasticity-consistent standard errors (SE), which do not account for clustering. Each cell is the treatment coefficient from a separate ordinary least squares (OLS) regression within the quartile named, with its SE in parentheses. Panel A treats a record when its Standard Industrial Classification (SIC) code is 4813, 4841, or 4899; Panel B treats it when its parent filer entity is registered on Federal Communications Commission (FCC) Form 499. The two panels use the same records, so their estimates share observations and no test of their difference is reported. Panel C repeats the comparison on 339 canonical events, with size quartiles of log total assets; treated parent filer entities are in parentheses. The Q1 − Q4 spread is the smallest-quartile estimate minus the largest. Treatment varies across few parent filer entities (the Panel C Q1 cell holds 2 treated events at 1 parent), so these SEs are too small to support a rejection. Panel D shows how records concentrate in events: 115 of the 618 events have more than one record and supply 388 records, and two 2024 events at one parent filer entity supply 56. Panel E counts, among 48 window specifications on the corrected data (24 per anchor date), those that place the Q1 estimate above Q4 (0) and those that decline steadily from Q1 to Q4 (0). Q1 is the smallest quartile.

**Table 4**

*Where the Two Treatment Definitions Disagree*

Panel A: The 30 disagreement records against the 861 agreements

| Group | Records | Organizations | Log market value M (SD) | Change M (SD) |
|:---|---:|---:|---:|---:|
| Disagree: Form 499 registrant, no industry code (missed by the codes) | 28 | 16 | 10.83 (1.18) | −1.49 (17.22) |
| Disagree: industry code, not a registrant (damaged source entries) | 2 | 2 | 12.10 (0.01) | 4.55 (1.75) |
|  ATT-SecurityBreach (SIC 4813, breach 2014-04-09, Q4) | 1 | 1 | 12.11 | 5.79 |
|  ATT-SecurityBreach2 (SIC 4813, breach 2013-10-01, Q4) | 1 | 1 | 12.09 | 3.31 |
| Agree: industry code and registrant | 160 | 41 | 11.03 (1.35) | −0.53 (11.31) |
| Agree: neither definition treats | 701 | 323 | 10.43 (1.07) | −1.89 (13.76) |
| All records | 891 |  |  |  |

Panel B: Records added to the smallest quartile

| Q1 component | Records | Events | Change M (SD) |
|:---|---:|---:|---:|
| Treated under both definitions | 33 | 20 | 0.52 (12.94) |
| Treated by codes only (dropped) | 0 | 0 | — |
| Treated by Form 499 only (added) | 10 | 6 | −8.62 (24.48) |
|  of which GoDaddy | 8 |  | −8.70 (27.75) |
|  of which Twilio | 2 |  | −8.29 (1.65) |
| Treated by neither | 186 | 142 | −2.20 (14.61) |

Panel C: Registrants the industry codes miss

| Group | Records | Organizations | Change M (SD) | Quartile placement (records) |
|:---|---:|---:|---:|---:|
| All missed registrants | 28 | 16 | −1.49 (17.22) | Q1 10; Q2–Q3 5; Q4 13 |

*Note.* Panel A divides the 891 notification records by the two treatment definitions: an industry code of 4813, 4841, or 4899 on the record, and registration of the parent filer entity on Federal Communications Commission (FCC) Form 499. The definitions disagree on 30 records. Twenty-eight are Form 499 registrant records that carry none of the three codes, at 16 organizations. The other 2 are damaged source entries coded 4813 whose organization field holds an AT&T breach label rather than a firm name, so they resolve to no parent filer entity. Records neither definition treats form the comparison group under both. Change is the change in raw-return volatility under the earlier specification, and size is log market value. Panel B splits the 229 records in the smallest size quartile (Q1). The 10 records treated under Form 499 only come from GoDaddy, a domain registrar (8), and Twilio, a communications platform (2); their mean change, −8.62, compares with −2.20 for records neither definition treats. Panel C places the 28 missed records by quartile: 10 in Q1, 13 in Q4, and 5 in Q2 or Q3. M = mean; SD = standard deviation.

**Table 5**

*Data Quality in the Matching Chain*

Panel A: Identifier collisions in the earlier chain

| Ticker on the identifier | Organizations absorbed | Examples | Records | Canonical events with these names | Identifier is a current parent filer entity |
|:---|---:|---:|---:|---:|---:|
| JNJ | 10 | Christensen O’Connor Johnson Kindness PLLC; DiGiovine, Hnilo, Jordan + Johnson Ltd; … | 15 | 0 | No |
| SBAC | 25 | American Alarm & Communications, Inc.; Centerline Communications, LLC; … | 46 | 11 | No |
| WBD | 2 | iHeart Media Inc; iHeartMedia + Entertainment, Inc. | 6 | 2 | No |
| PCG-PA | 1 | E.W. Wylie Corporation | 1 | 0 | No |
| APA | 3 | Dynapar Corporation; MNP Corporation; … | 4 | 0 | No |
| T-PC | 11 | AT&T; AT&T Inc; … | 40 | 26 | Yes |

Panel B: Reused-ticker matches

| Organization | Breach date | Ticker | Security the old rule assigned (PERMNO) | Assigned security’s ticker ended | Later owner of the ticker (PERMNO) |
|:---|---:|---:|---:|---:|---:|
| Motorola, Inc. | 2009-01-01 | MSI | MOVIE STAR INC N Y (48020) | 2008-01-28 | 22779 (MOTOROLA SOLUTIONS INC) |
| Motorola, Inc. | 2009-02-17 | MSI | MOVIE STAR INC N Y (48020) | 2008-01-28 | 22779 (MOTOROLA SOLUTIONS INC) |
| Facebook, Inc. | 2008-06-09 | META | METATEC INTERNATIONAL INC (76947) | 2002-04-25 | 21413 (LISTED FUNDS TRUST) |
| Facebook | 2013-11-24 | META | METATEC INTERNATIONAL INC (76947) | 2002-04-25 | 21413 (LISTED FUNDS TRUST) |
| Facebook | 2018-03-01 | META | METATEC INTERNATIONAL INC (76947) | 2002-04-25 | 21413 (LISTED FUNDS TRUST) |
| Facebook | 2018-09-01 | META | METATEC INTERNATIONAL INC (76947) | 2002-04-25 | 21413 (LISTED FUNDS TRUST) |
| DoorDash Inc. | 2019-05-04 | DASH | DASH INDUSTRIES INC (28557) | 1992-08-26 | 20189 (DOORDASH INC) |

Panel C: The size-measure defect

| Candidate measure | Slope | Intercept | R² | Share within 0.10 | Share within 0.25 |
|:---|---:|---:|---:|---:|---:|
| Log market value (CRSP price × shares outstanding) | 0.99 | 0.05 | .86 | .69 | .96 |
| Log total assets (earlier dataset) | 0.46 | 5.60 | .44 | .04 | .15 |

Panel D: Losses after the CRSP match

| Reason | Events | Share of 355 | Registrant events | Other events |
|:---|---:|---:|---:|---:|
| Fewer trading days than the volatility windows need | 4 | 1.1% | 2 | 2 |
| No Compustat match (size, leverage, return on assets) | 15 | 4.2% | 4 | 11 |
| Invalid disclosure date | 1 | 0.3% | 1 | 0 |
| Damaged source records | 2 | 0.6% | 0 | 2 |
| All losses | 22 | 6.2% | 7 | 15 |
| Retained | 333 | 93.8% | 104 (93.7%) | 229 (93.9%) |

*Note.* Panel A lists the 6 identifiers in the earlier matching chain that absorbed the names of unrelated organizations, so those organizations' breach records took on another firm's stock data. Organizations absorbed counts distinct organization names, records counts their breach records, and canonical events counts current events carrying one of those names; the largest collision absorbed 25 organizations and 46 records. Panel B lists the 7 events at which ticker reuse would have matched the breached firm to an earlier, unrelated holder of the same symbol whose ticker had ended years before (in 2002 for META and 1992 for DASH). The current chain blocks that match, and none of the 7 events has a stock match. Panel C regresses the earlier dataset's size variable on two candidate measures: against log market value the slope is 0.99 and R² is .86, and against log total assets the slope is 0.46 and R² is .44, so the variable measures market value. Share within is the share of records within 0.10 or 0.25 of each candidate. Panel D starts from the 355 events matched to stock data and reported by December 31, 2024 (111 registrant and 244 other events) and counts the events lost at each requirement. Retention is 93.7 percent of registrant events (104 of 111) and 93.9 percent of other events (229 of 244). PERMNO = CRSP permanent security identifier; CRSP = Center for Research in Security Prices; R² = share of variance explained.
