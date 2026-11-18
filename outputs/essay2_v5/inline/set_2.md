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
| Records in the 2024-02-21 event of parent CIK 1140859 | 31 |
| Records in the 2024-04-10 event of parent CIK 1140859 | 25 |
| Records in both 2024 events of parent CIK 1140859 | 56 |

Panel E: Gradient on corrected data, 48 specifications

| Anchor date | Specifications | Q1 estimate above Q4 | Monotone decline Q1 to Q4 |
|:---|---:|---:|---:|
| Breach date | 24 | 0 | 0 |
| Notification date | 24 | 0 | 0 |
| Both anchors | 48 | 0 | 0 |

*Note.* Record-level panels use the earlier specification: raw-return volatility on notification records, size measured by market value. Panels A and B: 891 notification records; treatment by industry code (SIC 4813, 4841 or 4899 on the record) in Panel A and by Form 499 registration of the parent filer entity in Panel B; quartiles of log market value. Panel C: the same comparison on 339 canonical events (records collapsed to events), with the earlier breach-date-anchored raw-return outcome; its quartiles are of log total assets from the canonical event file. Estimates are the treatment coefficient from OLS of the change in raw-return volatility on treatment and the earlier specification’s controls (pre-period volatility, size, leverage, return on assets, disclosure gap, prior breaches, health-breach flag), within each cell; SEs are HC3 heteroskedasticity-consistent, not clustered. Q1 − Q4 spread = Q1 estimate minus Q4 estimate. Panel D counts records per event in the Panel A–B records. Panel E summarizes the gradient on corrected data across 48 window specifications (24 per anchor date); the full grid, one row per specification, is in the committed CSV outputs/tables/essay2_v2/t31_gradient_grid.csv. Treated parents in Panel C are parent filer entities. SIC = Standard Industrial Classification; Q1–Q4 = size quartiles, Q1 smallest; SE = standard error; OLS = ordinary least squares; HC3 = heteroskedasticity-consistent covariance, type 3; CIK = SEC Central Index Key.

**Table 4**

*Where the Two Definitions Disagree*

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
|  of which GoDaddy (parent CIK 1609711) | 8 |  | −8.70 (27.75) |
|  of which Twilio (parent CIK 1447669) | 2 |  | −8.29 (1.65) |
| Treated by neither | 186 | 142 | −2.20 (14.61) |

Panel C: Registrants the industry codes miss

| Group | Records | Organizations | Change M (SD) | Quartile placement (records) |
|:---|---:|---:|---:|---:|
| All missed registrants | 28 | 16 | −1.49 (17.22) | Q1 10; Q2–Q3 5; Q4 13 |

*Note.* Record-level panels use the earlier specification: raw-return volatility on notification records, size measured by market value. All panels use the 891 notification records; industry-code treatment = SIC 4813, 4841 or 4899 on the record; Form 499 treatment = Form 499 registration of the parent filer entity. Change = change in raw-return volatility. Panel B covers the 229 records in the smallest size quartile (Q1). In Panel C, Q2–Q3 placement is the 28 records less those in Q1 and Q4; the firm names and SIC codes of the 28 records are in the committed CSV outputs/essay2_v5/missed_registrants_by_firm.csv. The pre-repair sensitivity group and the Welch contrasts for the damaged entries are in the committed appendix CSVs. SIC = Standard Industrial Classification; CIK = SEC Central Index Key; Q1–Q4 = size quartiles of log market value, Q1 smallest; M = mean; SD = standard deviation.

**Table 5**

*Data Quality*

Panel A: Identifier collisions in the earlier chain

| Legacy CIK | Ticker on the CIK | Organizations absorbed | Examples | Records | Canonical events with these names | CIK is a canonical parent |
|:---|---:|---:|---:|---:|---:|---:|
| 200406 | JNJ | 10 | Christensen O’Connor Johnson Kindness PLLC; DiGiovine, Hnilo, Jordan + Johnson Ltd; … | 15 | 0 | No |
| 1034054 | SBAC | 25 | American Alarm & Communications, Inc.; Centerline Communications, LLC; … | 46 | 11 | No |
| 1437107 | WBD | 2 | iHeart Media Inc; iHeartMedia + Entertainment, Inc. | 6 | 2 | No |
| 1004980 | PCG-PA | 1 | E.W. Wylie Corporation | 1 | 0 | No |
| 1841666 | APA | 3 | Dynapar Corporation; MNP Corporation; … | 4 | 0 | No |
| 732717 | T-PC | 11 | AT&T; AT&T Inc; … | 40 | 26 | Yes |

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

| Candidate measure | Records | Slope | Intercept | R² | Share within 0.10 | Share within 0.25 |
|:---|---:|---:|---:|---:|---:|---:|
| Log market value (CRSP price × shares outstanding) | 674 | 0.99 | 0.05 | .86 | .69 | .96 |
| Log total assets (earlier dataset) | 898 | 0.46 | 5.60 | .44 | .04 | .15 |

Panel D: Losses after the CRSP match

| Reason | Events | Share of 355 | Registrant events | Other events |
|:---|---:|---:|---:|---:|
| Fewer trading days than the volatility windows need | 4 | 1.1% | 2 | 2 |
| No Compustat match (size, leverage, return on assets) | 15 | 4.2% | 4 | 11 |
| Invalid disclosure date | 1 | 0.3% | 1 | 0 |
| Damaged source records | 2 | 0.6% | 0 | 2 |
| All losses | 22 | 6.2% | 7 | 15 |
| Retained | 333 | 93.8% | 104 (93.7%) | 229 (93.9%) |

*Note.* Record-level panels use the earlier specification: raw-return volatility on notification records, size measured by market value. Panel A lists the 6 legacy identifiers (SEC Central Index Keys) to which the earlier chain attached unrelated organizations; examples show the first two names, and every name is in the committed CSV. Panel B lists the canonical events that the earlier fallback rule would have matched to an earlier, unrelated owner of the same ticker; the current chain blocks the rule and none of the 7 has a CRSP match. Panel C regresses the earlier dataset’s size variable on each candidate measure; share within = share of records whose absolute gap to the candidate is at most 0.10 or 0.25. Panel D starts from the 355 CRSP-matched events notified by December 31, 2024 (111 registrant, 244 other); retained shares are within group. CIK = SEC Central Index Key; CRSP = Center for Research in Security Prices; PERMNO = CRSP permanent security identifier.
