# Enforcement-timing exploration — Essay 3 (EXPLORATORY, POST-HOC)

> **STATUS: EXPLORATORY. POST-HOC. DESCRIPTIVE ONLY.**
> This document was generated *after* the Essay 3 Query 2 results were known. It is
> **not** part of the essay's test inventory. It adds **no** hypothesis test, **no**
> p-value, and **no** entry to any Benjamini-Hochberg family. Nothing here was
> pre-registered. It must be labelled exploratory and post-hoc wherever it is written
> up, and it must not be described as evidence for or against H6.
>
> No committed output was modified to produce this file. `run_all` and script 158 were
> not run. All inputs were read only.

## Provenance

- Repository HEAD at generation: `e65d4b1`
- Sample: `outputs/essay3_q2/e_analysis_sample.csv`, `in_analysis_sample == 1`
  (N = 338; 107 treated events; 12 treated parent CIKs; G = 81).
- Departure events: `outputs/essay3_q2/c2_departure_events.csv` (classifier v2,
  `scripts/195_essay3_q2_classifier_v2.py`, commit `6f7be7a`), one departure per person
  per parent CIK, dated to its earliest disclosing filing.
- Titles: `outputs/essay3_q2/c2_person_rows.csv` (`action == "departure"`).
- Filing scope and coverage windows: `outputs/essay3_q2/b_scope_filings.csv`,
  `b_scope_events.csv`, built by `scripts/187_essay3_q2_fetch_502_text.py`.

## Motivating question (stated before the tables, answered by none of them)

Stakeholder salience theory (Mitchell, Agle, and Wood 1997) holds that a stakeholder
holding power and legitimacy becomes *definitive* only when urgency is added. The
enforcement literature suggests dismissals follow the sanction rather than the
underlying event. That motivates asking whether treated-firm executive departures
cluster near **FCC enforcement actions** rather than near **breach notifications**.

**This repository cannot answer that question.** Part 3 explains why. Parts 1 and 2
report only what the repository does contain: departure timing relative to
notification, and the coverage limits that bound what could have been observed.

---

## Part 1 — Timeline: notifications and v2 executive departures, 12 treated parent CIKs

108 executive departure events and 107 breach notifications, 215 rows, sorted by CIK then date.

Column notes:

- `kind` — `NOTIFICATION` is a treated breach event (its `breach_date` is shown in the
  detail column); `DEPARTURE` is a v2 executive-departure event.
- `days_since_prior_notif` — days from the most recent *preceding* notification for the
  same CIK. Blank means the departure precedes every notification for that CIK. This is
  a descriptive gap, **not** an outcome variable and **not** a test.
- Departures **outside** every outcome window are included, as requested. Of the
  108 executive departures, 3 fall within 30 days of a prior notification, 8 within 90 days, and 20 within 180 days; 88 fall outside all 180-day windows or precede every notification.
- `role` is the classifier's role class; `title` is the title string as parsed from the
  filing, truncated to 70 characters.
- `restated-only` marks a departure whose every mention was a restatement of an earlier
  announcement; `vacancy-only` marks a vacancy-phrasing mention. Both are classifier
  flags carried through for transparency.
- `director_only` is **not** shown: it defaults to 1 for every `grp == "exec"` row and is
  meaningful only for director rows (`scripts/195`, lines 620-625).
- Director departures are excluded from this table. There are 70 director-departure
  events across these 12 CIKs; Essay 3 treats directors as descriptive only.

| CIK | Organization | Date | Kind | Person | Title / detail | Role | First disclosing filing | Form | days_since_prior_notif | Flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 18926 | CenturyLink | 2013-03-25 | DEPARTURE | James E. Ousley | Chief Executive Officer | CEO | 0001193125-13-124519 | 8-K |  | CEO |
| 18926 | CenturyLink | 2014-05-28 | NOTIFICATION |  | breach_date 2013-12-27 |  |  |  |  |  |
| 18926 | CenturyLink | 2015-06-02 | DEPARTURE | Karen A. Puckett | President | president | 0001193125-15-210785 | 8-K | 370 |  |
| 18926 | CenturyLink | 2017-02-20 | NOTIFICATION |  | breach_date 2017-01-30 |  |  |  |  |  |
| 18926 | CenturyLink | 2017-02-28 | NOTIFICATION |  | breach_date 2017-02-28 |  |  |  |  |  |
| 18926 | CenturyLink | 2018-09-24 | DEPARTURE | Sunit S. Patel | Executive Vice President and Chief Financial Officer | CFO | 0001193125-18-281219 | 8-K | 573 |  |
| 18926 | CenturyLink | 2018-11-07 | DEPARTURE | Amir Hussain | Executive Vice President and Chief Technology Officer | other_exec | 0001193125-18-319718 | 8-K | 617 |  |
| 18926 | CenturyLink | 2020-09-25 | NOTIFICATION |  | breach_date 2020-08-20 |  |  |  |  |  |
| 18926 | CenturyLink | 2021-01-20 | DEPARTURE | Eric J. Mortensen | Senior Vice President Controller | PAO | 0001193125-21-011905 | 8-K | 117 |  |
| 18926 | CenturyLink | 2022-03-28 | DEPARTURE | Indraneel Dev | Executive Vice President and Chief Financial Officer of the Company an | CFO | 0001193125-22-085992 | 8-K | 549 |  |
| 18926 | CenturyLink | 2022-04-21 | NOTIFICATION |  | breach_date 2022-03-15 |  |  |  |  |  |
| 18926 | CenturyLink | 2022-09-13 | DEPARTURE | Jeffrey K. Storey | President and Chief Executive Officer of the Company and its principal | CEO | 0001193125-22-243230 | 8-K | 145 | CEO |
| 20520 | Frontier Communications | 2020-02-26 | DEPARTURE | Daniel McCarthy | Chief Executive Officer in December 2019, succeeding CEO | CEO | 0001193125-20-050127 | 8-K |  | CEO restated-only |
| 20520 | Frontier Communications | 2020-12-15 | DEPARTURE | Bernard L. Han | President and Chief Executive Officer | CEO | 0001140361-20-028400 | 8-K |  | CEO |
| 20520 | Frontier Communications | 2021-04-30 | DEPARTURE | John G. Stratton | Executive Chairman | other_exec | 0001140361-21-015200 | 8-K12G3 |  |  |
| 20520 | Frontier Communications | 2021-06-02 | DEPARTURE | Sheldon Bruha | Executive Vice President Chief Financial Officer | CFO | 0001193125-21-179930 | 8-K |  |  |
| 20520 | Frontier Communications | 2021-07-30 | DEPARTURE | Ken Arndt | Executive Vice President and Chief Customer Operations Officer | other_exec | 0000020520-21-000008 | 8-K |  |  |
| 20520 | Frontier Communications | 2021-07-30 | DEPARTURE | nan | Executive Vice President and Chief Digital and Information Officer | other_exec | 0000020520-21-000008 | 8-K |  |  |
| 20520 | Frontier Communications | 2022-05-04 | NOTIFICATION |  | breach_date 2022-02-24 |  |  |  |  |  |
| 20520 | Frontier Communications | 2022-06-24 | DEPARTURE | Donald W. Daniels | Senior Vice President Chief Accounting Officer | PAO | 0001140361-22-023997 | 8-K | 51 |  |
| 20520 | Frontier Communications | 2024-06-06 | NOTIFICATION |  | breach_date 2024-04-13 |  |  |  |  |  |
| 20520 | Frontier Communications | 2024-06-10 | NOTIFICATION |  | breach_date 2024-06-10 |  |  |  |  |  |
| 20520 | Frontier Communications | 2024-06-12 | NOTIFICATION |  | breach_date 2023-12-18 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2007-10-12 | DEPARTURE | Gary Forsee | president and chief executive officer | CEO | 0000101830-07-000036 | 8-K |  | CEO |
| 101830 | Sprint Nextel | 2008-01-24 | DEPARTURE | Timothy E. Kelly | Chief Marketing Officer | other_exec | 0000101830-08-000006 | 8-K |  |  |
| 101830 | Sprint Nextel | 2008-10-07 | DEPARTURE | William Arendt | principal accounting officer | PAO | 0000101830-08-000028 | 8-K |  |  |
| 101830 | Sprint Nextel | 2008-11-28 | DEPARTURE | Barry J. West | Chief Technology Officer and President | president | 0000950123-08-016627 | 8-K |  |  |
| 101830 | Sprint Nextel | 2009-03-03 | DEPARTURE | Christopher J. Gregoire | principal accounting officer of the Company effective March 3 | PAO | 0000101830-09-000005 | 8-K |  |  |
| 101830 | Sprint Nextel | 2009-03-30 | NOTIFICATION |  | breach_date 2012-08-01 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2009-06-12 | NOTIFICATION |  | breach_date 2009-02-01 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2009-10-16 | DEPARTURE | Charles L. Hall | Senior Vice President, Controller and Principal Accounting Officer | PAO | 0000101830-09-000014 | 8-K | 126 |  |
| 101830 | Sprint Nextel | 2010-07-21 | DEPARTURE | Daniel H. Schulman | President | president | 0000101830-10-000015 | 8-K | 404 |  |
| 101830 | Sprint Nextel | 2011-02-28 | DEPARTURE | Robert H. Brust | CFO | CFO | 0000101830-11-000010 | 8-K | 626 |  |
| 101830 | Sprint Nextel | 2014-03-12 | DEPARTURE | Steven L. Elfman | President | president | 0000101830-14-000021 | 8-K | 1734 |  |
| 101830 | Sprint Nextel | 2014-08-06 | DEPARTURE | Marcelo Claure | executive officer | other_exec | 0001193125-14-297076 | 8-K | 1881 |  |
| 101830 | Sprint Nextel | 2014-08-06 | DEPARTURE | Daniel R. Hesse | President and CEO, and as a member of the Board of Directors | CEO | 0001193125-14-297076 | 8-K | 1881 | CEO |
| 101830 | Sprint Nextel | 2014-11-12 | DEPARTURE | Robert L. Johnson | Chief Experience Officer | other_exec | 0000101830-14-000081 | 8-K | 1979 |  |
| 101830 | Sprint Nextel | 2014-11-12 | DEPARTURE | Overland Park | President, Retail, Chief Service and IT Officer | president | 0000101830-14-000081 | 8-K | 1979 |  |
| 101830 | Sprint Nextel | 2015-08-03 | DEPARTURE | Joseph Euteneuer | Chief Financial Officer | CFO | 0001193125-15-275046 | 8-K | 2243 |  |
| 101830 | Sprint Nextel | 2015-10-15 | DEPARTURE | Michael Schwartz | Senior Vice President | other_exec | 0000101830-15-000030 | 8-K | 2316 |  |
| 101830 | Sprint Nextel | 2017-09-20 | NOTIFICATION |  | breach_date 2017-05-01 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2017-09-20 | NOTIFICATION |  | breach_date 2017-05-07 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2018-01-04 | DEPARTURE | Marcelo Claure | President | president | 0000101830-18-000003 | 8-K | 106 | CEO |
| 101830 | Sprint Nextel | 2018-01-04 | DEPARTURE | Tarek Robbiati | Chief Financial Officer | CFO | 0000101830-18-000003 | 8-K | 106 |  |
| 101830 | Sprint Nextel | 2018-03-30 | NOTIFICATION |  | breach_date 2018-03-02 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2019-05-09 | NOTIFICATION |  | breach_date 2019-03-14 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2019-05-09 | NOTIFICATION |  | breach_date 2019-05-09 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2019-06-08 | NOTIFICATION |  | breach_date 2019-06-08 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2019-07-11 | NOTIFICATION |  | breach_date 2019-06-02 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2019-07-11 | NOTIFICATION |  | breach_date 2019-06-22 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2020-03-31 | NOTIFICATION |  | breach_date 2019-08-13 |  |  |  |  |  |
| 101830 | Sprint Nextel | 2020-04-01 | DEPARTURE | Paul Schieber | Vice President Controller | PAO | 0001193125-20-093630 | 8-K | 1 |  |
| 101830 | Sprint Nextel | 2020-04-09 | NOTIFICATION |  | breach_date 2015-08-17 |  |  |  |  |  |
| 732712 | Verizon | 2006-12-12 | DEPARTURE | Babbio Jr | President Lawrence T. Babbio Jr. has notified the Board of Directors | president | 0001193125-06-251425 | 8-K |  |  |
| 732712 | Verizon | 2008-06-27 | NOTIFICATION |  | breach_date 2008-06-27 |  |  |  |  |  |
| 732712 | Verizon | 2008-10-01 | DEPARTURE | William P. Barr | Executive Vice President General Counsel | other_exec | 0001193125-08-204660 | 8-K | 96 |  |
| 732712 | Verizon | 2014-02-25 | NOTIFICATION |  | breach_date 2014-01-20 |  |  |  |  |  |
| 732712 | Verizon | 2014-02-26 | NOTIFICATION |  | breach_date 2014-02-26 |  |  |  |  |  |
| 732712 | Verizon | 2015-02-18 | DEPARTURE | Daniel S. Mead | Executive Vice President President | president | 0001193125-15-051424 | 8-K | 357 |  |
| 732712 | Verizon | 2015-05-13 | DEPARTURE | Mr. Lowell | Chief Executive Officer | CEO | 0001193125-15-185255 | 8-K | 441 | CEO |
| 732712 | Verizon | 2016-09-01 | DEPARTURE | Francis J. Shammo | Chief Financial Officer | CFO | 0001193125-16-699639 | 8-K | 918 |  |
| 732712 | Verizon | 2017-07-20 | NOTIFICATION |  | breach_date 2016-08-10 |  |  |  |  |  |
| 732712 | Verizon | 2017-07-20 | NOTIFICATION |  | breach_date 2017-07-20 |  |  |  |  |  |
| 732712 | Verizon | 2017-10-04 | DEPARTURE | Lowell C. McAdam | Chief Executive Officer | CEO | 0001193125-17-303383 | 8-K | 76 | CEO |
| 732712 | Verizon | 2018-06-08 | DEPARTURE | John G. Stratton | Executive Vice President President | president | 0001193125-18-187324 | 8-K | 323 |  |
| 732712 | Verizon | 2019-05-31 | NOTIFICATION |  | breach_date 2019-04-24 |  |  |  |  |  |
| 732712 | Verizon | 2019-06-03 | NOTIFICATION |  | breach_date 2019-06-03 |  |  |  |  |  |
| 732712 | Verizon | 2021-09-01 | DEPARTURE | Mr. Guru | executive officer | other_exec | 0001193125-21-262922 | 8-K | 821 |  |
| 732712 | Verizon | 2022-05-16 | DEPARTURE | Hans Vestberg | Chief Executive Officer | CEO | 0001193125-22-151826 | 8-K | 1078 | CEO |
| 732712 | Verizon | 2022-06-06 | DEPARTURE | Tami A. Erwin | Executive Vice President and Group CEO | CEO | 0001193125-22-168378 | 8-K | 1099 | CEO |
| 732712 | Verizon | 2022-08-25 | DEPARTURE | Verizon Consumer | Executive Vice President and Group CEO | CEO | 0001193125-22-230055 | 8-K | 1179 | CEO |
| 732712 | Verizon | 2023-03-03 | DEPARTURE | Matthew D. Ellis | Verizon’s Executive Vice President and Chief Financial Officer | CFO | 0001193125-23-058988 | 8-K | 1369 |  |
| 732712 | Verizon | 2023-03-03 | DEPARTURE | Kyle Malady | Executive Vice President and President | president | 0001193125-23-058988 | 8-K | 1369 |  |
| 732712 | Verizon | 2023-03-03 | DEPARTURE | Anthony T. Skiadas | Verizon’s Senior Vice President and Controller | PAO | 0001193125-23-058988 | 8-K | 1369 |  |
| 732712 | Verizon | 2023-05-11 | NOTIFICATION |  | breach_date 2023-05-11 |  |  |  |  |  |
| 732712 | Verizon | 2024-02-05 | NOTIFICATION |  | breach_date 2023-09-21 |  |  |  |  |  |
| 732712 | Verizon | 2024-02-06 | NOTIFICATION |  | breach_date 2024-02-06 |  |  |  |  |  |
| 732712 | Verizon | 2024-05-23 | DEPARTURE | Craig L. Silliman | Executive Vice President and President | president | 0001193125-24-146021 | 8-K | 107 |  |
| 732717 | AT&T | 2007-04-30 | DEPARTURE | Edward E. Whitacre, Jr. | Board of Directors and as Chief Executive Officer and President | CEO | 0000732717-07-000028 | 8-K |  | CEO |
| 732717 | AT&T | 2007-10-16 | DEPARTURE | Stan Sigman | President and Chief Executive Officer | CEO | 0000732717-07-000084 | 8-K |  | CEO |
| 732717 | AT&T | 2008-05-23 | NOTIFICATION |  | breach_date 2008-05-23 |  |  |  |  |  |
| 732717 | AT&T | 2011-03-07 | DEPARTURE | Richard G. Lindner | Executive Vice President and Chief Financial Officer | CFO | 0000732717-11-000016 | 8-K | 1018 |  |
| 732717 | AT&T | 2012-02-13 | NOTIFICATION |  | breach_date 2012-01-01 |  |  |  |  |  |
| 732717 | AT&T | 2014-06-05 | NOTIFICATION |  | breach_date 2014-04-09 |  |  |  |  |  |
| 732717 | AT&T | 2014-06-11 | NOTIFICATION |  | breach_date 2013-11-05 |  |  |  |  |  |
| 732717 | AT&T | 2014-06-13 | NOTIFICATION |  | breach_date 2014-04-01 |  |  |  |  |  |
| 732717 | AT&T | 2014-10-01 | NOTIFICATION |  | breach_date 2014-08-11 |  |  |  |  |  |
| 732717 | AT&T | 2014-10-09 | NOTIFICATION |  | breach_date 2014-10-09 |  |  |  |  |  |
| 732717 | AT&T | 2015-04-20 | NOTIFICATION |  | breach_date 2014-02-01 |  |  |  |  |  |
| 732717 | AT&T | 2015-04-20 | NOTIFICATION |  | breach_date 2014-06-05 |  |  |  |  |  |
| 732717 | AT&T | 2015-04-20 | NOTIFICATION |  | breach_date 2014-06-11 |  |  |  |  |  |
| 732717 | AT&T | 2015-04-21 | NOTIFICATION |  | breach_date 2013-01-01 |  |  |  |  |  |
| 732717 | AT&T | 2015-08-20 | DEPARTURE | Wayne Watts | Executive Vice President and General Counsel | other_exec | 0000732717-15-000089 | 8-K | 121 |  |
| 732717 | AT&T | 2016-12-08 | DEPARTURE | nan | Vice Chairman | other_exec | 0000732717-16-000251 | 8-K | 597 |  |
| 732717 | AT&T | 2016-12-16 | DEPARTURE | nan | Vice Chairman | other_exec | 0000732717-16-000257 | 8-K | 605 |  |
| 732717 | AT&T | 2017-05-19 | NOTIFICATION |  | breach_date 2017-01-01 |  |  |  |  |  |
| 732717 | AT&T | 2017-05-19 | NOTIFICATION |  | breach_date 2017-01-25 |  |  |  |  |  |
| 732717 | AT&T | 2017-09-14 | NOTIFICATION |  | breach_date 2017-02-01 |  |  |  |  |  |
| 732717 | AT&T | 2018-08-17 | NOTIFICATION |  | breach_date 2018-08-17 |  |  |  |  |  |
| 732717 | AT&T | 2018-08-21 | NOTIFICATION |  | breach_date 2018-08-21 |  |  |  |  |  |
| 732717 | AT&T | 2019-12-17 | DEPARTURE | John Stankey | president chief operating officer | COO | 0001193125-19-316283 | 8-K | 483 |  |
| 732717 | AT&T | 2020-04-28 | DEPARTURE | Randall Stephenson | Executive Chairman of the Board | other_exec | 0001193125-20-123202 | 8-K | 616 |  |
| 732717 | AT&T | 2020-11-17 | DEPARTURE | John Stephens | Executive Vice President and Chief Financial Officer | CFO | 0001193125-20-296128 | 8-K | 819 |  |
| 732717 | AT&T | 2023-02-02 | DEPARTURE | Debra L. Dial | Senior Vice President - Chief Accounting Officer and Controller | PAO | 0001193125-23-022845 | 8-K | 1626 |  |
| 732717 | AT&T | 2023-02-24 | NOTIFICATION |  | breach_date 2022-08-30 |  |  |  |  |  |
| 732717 | AT&T | 2023-03-01 | NOTIFICATION |  | breach_date 2023-03-01 |  |  |  |  |  |
| 732717 | AT&T | 2024-03-30 | NOTIFICATION |  | breach_date 2022-06-01 |  |  |  |  |  |
| 732717 | AT&T | 2024-04-01 | NOTIFICATION |  | breach_date 2019-01-01 |  |  |  |  |  |
| 732717 | AT&T | 2024-04-09 | NOTIFICATION |  | breach_date 2024-03-17 |  |  |  |  |  |
| 732717 | AT&T | 2024-04-09 | NOTIFICATION |  | breach_date 2024-03-26 |  |  |  |  |  |
| 732717 | AT&T | 2024-04-09 | NOTIFICATION |  | breach_date 2024-04-09 |  |  |  |  |  |
| 732717 | AT&T | 2024-04-10 | NOTIFICATION |  | breach_date 2024-04-14 |  |  |  |  |  |
| 1001082 | DISH Network, LLC | 2023-05-15 | NOTIFICATION |  | breach_date 2023-02-22 |  |  |  |  |  |
| 1001082 | DISH Network, LLC | 2023-05-17 | NOTIFICATION |  | breach_date 2023-05-17 |  |  |  |  |  |
| 1001082 | DISH Network, LLC | 2023-06-23 | DEPARTURE | Mr. Narayan | Executive Vice President and Chief Operating Officer | COO | 0001001082-23-000031 | 8-K | 37 |  |
| 1001082 | DISH Network, LLC | 2023-08-08 | DEPARTURE | Erik Carlson | Chief Executive Officer | CEO | 0001104659-23-088620 | 8-K | 83 | CEO |
| 1091667 | Charter Communications, Inc. | 2007-03-14 | DEPARTURE | Sue Ann | Executive Vice President | other_exec | 0001091667-07-000050 | 8-K |  |  |
| 1091667 | Charter Communications, Inc. | 2008-03-11 | DEPARTURE | Jeffrey T. Fisher | Executive Vice President Chief Financial Officer | CFO | 0001091667-08-000035 | 8-K |  |  |
| 1091667 | Charter Communications, Inc. | 2008-06-23 | DEPARTURE | Robert A. Quigley | Executive Vice President Chief Marketing Officer | other_exec | 0001091667-08-000129 | 8-K |  |  |
| 1091667 | Charter Communications, Inc. | 2008-08-05 | NOTIFICATION |  | breach_date 2008-07-14 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2008-08-11 | NOTIFICATION |  | breach_date 2008-08-11 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2011-10-11 | DEPARTURE | Michael J. Lovett | Chief Executive Officer and President | CEO | 0001091667-11-000130 | 8-K | 1156 | CEO |
| 1091667 | Charter Communications, Inc. | 2012-06-11 | DEPARTURE | Steve Apodaca | President | president | 0001091667-12-000100 | 8-K | 1400 |  |
| 1091667 | Charter Communications, Inc. | 2013-04-26 | NOTIFICATION |  | breach_date 2013-04-26 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2014-01-21 | NOTIFICATION |  | breach_date 2014-01-21 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2014-09-30 | NOTIFICATION |  | breach_date 2014-09-30 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2022-09-21 | DEPARTURE | Richard J. DiGeronimo | President | president | 0001091667-22-000104 | 8-K | 2913 |  |
| 1091667 | Charter Communications, Inc. | 2022-09-21 | DEPARTURE | Thomas M. Rutledge | Executive Chairman | other_exec | 0001091667-22-000104 | 8-K | 2913 |  |
| 1091667 | Charter Communications, Inc. | 2022-09-21 | DEPARTURE | Christopher L. Winfrey | President and Chief Executive Officer | CEO | 0001091667-22-000104 | 8-K | 2913 | CEO |
| 1091667 | Charter Communications, Inc. | 2023-01-01 | NOTIFICATION |  | breach_date 2023-01-01 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2023-02-10 | NOTIFICATION |  | breach_date 2022-12-21 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2023-09-01 | NOTIFICATION |  | breach_date 2023-09-01 |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. | 2023-10-25 | DEPARTURE | Eric L. Zinterhofer | Executive Chairman | other_exec | 0001091667-23-000137 | 8-K | 54 |  |
| 1166691 | Comcast | 2006-11-28 | DEPARTURE | Mr. Alchin | Chief Financial Officer | CFO | 0000950103-06-002700 | 8-K |  |  |
| 1166691 | Comcast | 2006-11-28 | DEPARTURE | Mr. John | Executive Vice President, Co-Chief Financial Officer and Treasurer | CFO | 0000950103-06-002700 | 8-K |  |  |
| 1166691 | Comcast | 2006-11-28 | DEPARTURE | Mr. Lawrence | Executive Vice President and Co-Chief Financial Officer | CFO | 0000950103-06-002700 | 8-K |  |  |
| 1166691 | Comcast | 2006-11-28 | DEPARTURE | Mr. Smith | executive officer | other_exec | 0000950103-06-002700 | 8-K |  |  |
| 1166691 | Comcast | 2008-01-29 | NOTIFICATION |  | breach_date 2008-01-29 |  |  |  |  |  |
| 1166691 | Comcast | 2009-05-11 | NOTIFICATION |  | breach_date 2009-05-11 |  |  |  |  |  |
| 1166691 | Comcast | 2009-06-22 | NOTIFICATION |  | breach_date 2009-06-22 |  |  |  |  |  |
| 1166691 | Comcast | 2011-01-31 | DEPARTURE | Stephen B. Burke | Chief Operating Officer | COO | 0000950103-11-000353 | 8-K | 588 |  |
| 1166691 | Comcast | 2011-09-22 | DEPARTURE | Johnathan Rodgers | President and Chief Executive Officer | CEO | 0001193125-11-254480 | 8-K | 822 | CEO |
| 1166691 | Comcast | 2014-02-14 | DEPARTURE | Edward D. Breen | director | director | 0000950103-14-001112 | 8-K | 1698 | CEO |
| 1166691 | Comcast | 2014-09-29 | NOTIFICATION |  | breach_date 2014-09-29 |  |  |  |  |  |
| 1166691 | Comcast | 2022-04-21 | NOTIFICATION |  | breach_date 2022-01-04 |  |  |  |  |  |
| 1166691 | Comcast | 2022-10-12 | DEPARTURE | Brian L. Roberts | Chief Executive Officer, but will no longer serve as President | CEO | 0000950103-22-017696 | 8-K | 174 | CEO |
| 1166691 | Comcast | 2023-01-06 | DEPARTURE | Michael J. Cavanagh | the Chief Financial Officer of the Company | CFO | 0000950103-23-000208 | 8-K | 260 |  |
| 1166691 | Comcast | 2023-12-18 | NOTIFICATION |  | breach_date 2023-10-16 |  |  |  |  |  |
| 1166691 | Comcast | 2024-01-26 | NOTIFICATION |  | breach_date 2024-01-26 |  |  |  |  |  |
| 1166691 | Comcast | 2024-10-03 | NOTIFICATION |  | breach_date 2024-02-14 |  |  |  |  |  |
| 1166691 | Comcast | 2024-10-04 | NOTIFICATION |  | breach_date 2024-10-04 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2013-05-02 | DEPARTURE | Braxton Carter | Chief Accounting Officer | PAO | 0001193125-13-193449 | 8-K |  |  |
| 1283699 | T-Mobile USA, Inc. | 2013-05-02 | DEPARTURE | Malcolm M. Lorang | executive officer | other_exec | 0001193125-13-193449 | 8-K |  |  |
| 1283699 | T-Mobile USA, Inc. | 2014-01-02 | NOTIFICATION |  | breach_date 2014-01-02 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2015-02-18 | DEPARTURE | Mr. Alling | officer | other_exec | 0001193125-15-052763 | 8-K | 412 |  |
| 1283699 | T-Mobile USA, Inc. | 2015-10-01 | NOTIFICATION |  | breach_date 2015-09-14 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2015-10-01 | NOTIFICATION |  | breach_date 2015-10-01 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2015-11-04 | NOTIFICATION |  | breach_date 2015-11-04 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2016-02-19 | DEPARTURE | Gary A. King | Executive Vice President Chief Information Officer | other_exec | 0001193125-16-470124 | 8-K | 107 |  |
| 1283699 | T-Mobile USA, Inc. | 2017-06-09 | NOTIFICATION |  | breach_date 2017-04-01 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2017-09-14 | NOTIFICATION |  | breach_date 2017-08-24 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2017-10-02 | NOTIFICATION |  | breach_date 2017-09-16 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2018-04-30 | DEPARTURE | John J. Legere | President upon ratification by the T-Mobile board of directors | president | 0001104659-18-028086 | 8-K | 210 |  |
| 1283699 | T-Mobile USA, Inc. | 2018-04-30 | DEPARTURE | Michael Sievert | Chief Operating Officer | COO | 0001104659-18-028086 | 8-K | 210 |  |
| 1283699 | T-Mobile USA, Inc. | 2018-08-23 | NOTIFICATION |  | breach_date 2018-08-20 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2019-11-18 | DEPARTURE | Braxton Carter | Executive Vice President Chief Financial Officer | CFO | 0001193125-19-294093 | 8-K | 452 |  |
| 1283699 | T-Mobile USA, Inc. | 2019-11-18 | DEPARTURE | John J. Legere | CEO, will cease to serve as CEO | CEO | 0001193125-19-294093 | 8-K | 452 | CEO |
| 1283699 | T-Mobile USA, Inc. | 2020-02-19 | DEPARTURE | David Carey | Executive Vice President | other_exec | 0001193125-20-041926 | 8-K | 545 |  |
| 1283699 | T-Mobile USA, Inc. | 2020-03-02 | NOTIFICATION |  | breach_date 2019-11-26 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2020-04-02 | NOTIFICATION |  | breach_date 2020-04-02 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2020-04-15 | NOTIFICATION |  | breach_date 2020-04-15 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2020-10-09 | NOTIFICATION |  | breach_date 2020-08-31 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2020-12-08 | NOTIFICATION |  | breach_date 2020-08-27 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-02-09 | NOTIFICATION |  | breach_date 2021-01-18 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-03-16 | NOTIFICATION |  | breach_date 2021-02-12 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-03-31 | NOTIFICATION |  | breach_date 2021-02-20 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-03-31 | NOTIFICATION |  | breach_date 2021-03-31 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-08-16 | NOTIFICATION |  | breach_date 2021-03-01 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-08-16 | NOTIFICATION |  | breach_date 2021-08-13 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-08-19 | NOTIFICATION |  | breach_date 2021-08-17 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-08-26 | NOTIFICATION |  | breach_date 2021-08-26 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2021-09-16 | DEPARTURE | David A. Miller | Executive Vice President, General Counsel and Secretary | other_exec | 0001193125-21-275230 | 8-K | 21 |  |
| 1283699 | T-Mobile USA, Inc. | 2022-03-08 | NOTIFICATION |  | breach_date 2022-03-08 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2023-01-19 | NOTIFICATION |  | breach_date 2022-11-25 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2023-02-13 | DEPARTURE | Neville Ray | President | president | 0001193125-23-035719 | 8-K | 25 |  |
| 1283699 | T-Mobile USA, Inc. | 2023-04-28 | NOTIFICATION |  | breach_date 2023-02-01 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2023-04-28 | NOTIFICATION |  | breach_date 2023-02-24 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2023-04-28 | NOTIFICATION |  | breach_date 2023-04-28 |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. | 2023-09-08 | DEPARTURE | Peter Ewens | Executive Vice President | other_exec | 0001193125-23-231377 | 8-K | 133 |  |
| 1447669 | Twilio | 2021-02-22 | DEPARTURE | Karyn Smith | General Counsel | other_exec | 0001193125-21-049966 | 8-K |  |  |
| 1447669 | Twilio | 2021-05-05 | DEPARTURE | Chee Chew | Chief Product Officer | other_exec | 0001447669-21-000122 | 8-K |  |  |
| 1447669 | Twilio | 2021-10-27 | DEPARTURE | George Hu | Chief Operating Officer | COO | 0001447669-21-000263 | 8-K |  |  |
| 1447669 | Twilio | 2022-05-04 | DEPARTURE | Marc D. Boroditsky | Chief Revenue Officer | other_exec | 0001447669-22-000094 | 8-K |  |  |
| 1447669 | Twilio | 2022-08-04 | NOTIFICATION |  | breach_date 2022-08-04 |  |  |  |  |  |
| 1447669 | Twilio | 2023-02-13 | DEPARTURE | Elena Donio | President | president | 0001193125-23-034646 | 8-K | 193 | CEO |
| 1447669 | Twilio | 2023-02-13 | DEPARTURE | Khozema Shipchandler | Chief Operating Officer, principal financial and accounting officer | COO | 0001193125-23-034646 | 8-K | 193 | CEO |
| 1447669 | Twilio | 2023-02-15 | DEPARTURE | Eyal Manor | Chief Product Officer | other_exec | 0001447669-23-000025 | 8-K | 195 |  |
| 1447669 | Twilio | 2024-01-08 | DEPARTURE | Jeff Lawson | CEO and Director | CEO | 0001193125-24-004000 | 8-K | 522 | CEO |
| 1447669 | Twilio | 2024-04-01 | NOTIFICATION |  | breach_date 2024-04-01 |  |  |  |  |  |
| 1609711 | GoDaddy.com LLC | 2019-02-14 | DEPARTURE | Steven Aldrich | Chief Product Officer | other_exec | 0001609711-19-000008 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2019-02-14 | DEPARTURE | Arne M. Josefsberg | Executive Vice President, Chief Infrastructure Officer | other_exec | 0001609711-19-000008 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2019-07-16 | DEPARTURE | Rebecca Morrow | Chief Accounting Officer | PAO | 0001609711-19-000176 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2019-08-02 | DEPARTURE | Scott W. Wagner | Chief Executive Officer | CEO | 0001609711-19-000190 | 8-K |  | CEO |
| 1609711 | GoDaddy.com LLC | 2020-11-04 | DEPARTURE | Andrew Low Ah | Officer | other_exec | 0001609711-20-000141 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2021-02-11 | DEPARTURE | Nima J. Kelly | Chief Legal Officer, Executive Vice President and Secretary | other_exec | 0001609711-21-000008 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2021-02-11 | DEPARTURE | Raymond E. Winborne | Chief Financial Officer and principal financial officer | CFO | 0001609711-21-000008 | 8-K |  |  |
| 1609711 | GoDaddy.com LLC | 2021-11-07 | NOTIFICATION |  | breach_date 2021-09-06 |  |  |  |  |  |
| 1609711 | GoDaddy.com LLC | 2022-06-01 | NOTIFICATION |  | breach_date 2022-03-14 |  |  |  |  |  |
| 1609711 | GoDaddy.com LLC | 2023-05-17 | NOTIFICATION |  | breach_date 2019-10-16 |  |  |  |  |  |
| 1609711 | GoDaddy.com LLC | 2023-10-06 | DEPARTURE | Michele Lau | Chief Legal Officer and Corporate Secretary | other_exec | 0001609711-23-000153 | 8-K | 142 |  |
| 1632127 | Cable One, Inc. | 2017-10-05 | DEPARTURE | Alan H. Silverman | Senior Vice President General Counsel Secretary | other_exec | 0000950157-17-001405 | 8-K |  |  |
| 1632127 | Cable One, Inc. | 2017-11-08 | DEPARTURE | Thomas O. Might | Executive Chairman | other_exec | 0001437749-17-018584 | 8-K |  |  |
| 1632127 | Cable One, Inc. | 2018-04-02 | DEPARTURE | Kevin P. Coyle | Senior Vice President Chief Financial Officer | CFO | 0001437749-18-006058 | 8-K |  |  |
| 1632127 | Cable One, Inc. | 2019-08-08 | NOTIFICATION |  | breach_date 2019-03-01 |  |  |  |  |  |
| 1632127 | Cable One, Inc. | 2019-08-08 | NOTIFICATION |  | breach_date 2019-08-08 |  |  |  |  |  |

---

## Part 2 — Coverage limits of the filing text store

### Correction to the assumed window

The store is **not** a flat `[t0 - 730d, t0 + 180d]` per event. `scripts/187`
(lines 71-74) builds two nested windows, both anchored on the breach and reported
dates rather than on a single `t0`:

| Window | Lower bound | Upper bound | Purpose |
|---|---|---|---|
| Spec scope | `min(breach_date, reported_date) - 365d` | `reported_date + 180d` | Query 2 B1 verbatim; validation and dev draws come from here only |
| Extended | `min(breach_date, reported_date) - 730d` | `max(breach_date, reported_date) + 180d` | `-730d` feeds the F2 baseline `[t0-730, t0-181]`; the upper extension handles breach dates later than reported dates |

So `-730d` is the **extended pre-window only**, and the post-window is `+180d` from the
reported date (or the later of the two dates in the extended window), not from a single
anchor. Coverage below is reported on the **extended** window, the more generous of the two.

### Two further limits, both material

1. **Only 8-K filings carrying Item 5.02 are in the store.** `scripts/187` (line 87)
   keeps a filing only if `form.startswith("8-K")` and `"5.02" in items`. A departure
   disclosed solely in a 10-K, a proxy statement, or an 8-K that omits the 5.02 item tag
   is invisible to the classifier even inside a covered date range.
2. **Coverage is a union of per-event windows, not one continuous span.** Firms with
   widely separated breach events have interior gaps in which no filing was fetched.

### Per-CIK coverage

| CIK | Organization | Scope events (drove fetching) | Analysis-sample events (Part 1) | 8-K 5.02 filings | Covered segments (extended window) | Last date covered | Last notification |
|---|---|---|---|---|---|---|---|
| 18926 | CenturyLink | 5 | 5 | 19 | 2011-12-28 to 2014-11-24; 2015-01-31 to 2017-08-27; 2018-08-21 to 2022-10-18 | 2022-10-18 | 2022-04-21 |
| 20520 | Frontier Communications | 4 | 4 | 11 | 2020-02-25 to 2024-12-09 | 2024-12-09 | 2024-06-12 |
| 101830 | Sprint Nextel | 12 | 12 | 86 | 2007-02-02 to 2013-01-28; 2013-08-17 to 2020-10-06 | 2020-10-06 | 2020-04-09 |
| 732712 | Verizon | 11 | 10 | 59 | 2006-06-28 to 2008-12-24; 2012-01-21 to 2020-04-04; 2021-05-11 to 2024-08-04 | 2024-08-04 | 2024-02-06 |
| 732717 | AT&T | 26 | 24 | 50 | 2006-05-24 to 2008-11-19; 2010-01-01 to 2024-10-11 | 2024-10-11 | 2024-04-10 |
| 1001082 | DISH Network, LLC | 2 | 2 | 8 | 2021-02-22 to 2023-11-13 | 2023-11-13 | 2023-05-17 |
| 1091667 | Charter Communications, Inc. | 8 | 8 | 36 | 2006-07-15 to 2009-02-07; 2011-04-27 to 2015-03-29; 2020-12-21 to 2024-02-28 | 2024-02-28 | 2023-09-01 |
| 1166691 | Comcast | 12 | 9 | 29 | 2006-01-29 to 2009-12-19; 2010-08-25 to 2015-03-28; 2020-01-05 to 2025-04-02 | 2025-04-02 | 2024-10-04 |
| 1283699 | T-Mobile USA, Inc. | 26 | 26 | 49 | 2012-01-03 to 2023-10-25 | 2023-10-25 | 2023-04-28 |
| 1447669 | Twilio | 2 | 2 | 19 | 2020-08-04 to 2024-09-28 | 2024-09-28 | 2024-04-01 |
| 1609711 | GoDaddy.com LLC | 3 | 3 | 24 | 2017-10-16 to 2023-11-13 | 2023-11-13 | 2023-05-17 |
| 1632127 | Cable One, Inc. | 2 | 2 | 9 | 2017-03-01 to 2020-02-04 | 2020-02-04 | 2019-08-08 |

**The two event columns differ, and the reason is not an attrition step.** Across these
12 CIKs the scope file holds 113 events while Part 1 lists 107. The gap is 6, and
every one of those events is flagged `fcc_form499 == 0` — an *untreated* breach event at
a firm whose parent is Form 499 registered. None is dropped by `in_analysis_sample`
(zero such exclusions at these CIKs). The arithmetic closes exactly:
113 - 6 = 107.

This is date-conditional treatment: a Form 499 parent can have breach events that
predate its treatment start, and those events are correctly untreated. The affected
CIKs are 732712 (Verizon, 1 event), 732717 (AT&T, 2 events), 1166691 (Comcast, 3 events).

Coverage is reported on the **scope** count because that is what actually determined
which filings were downloaded — the untreated events still widened the covered date
ranges, which works in favour of observability. Do not read the scope column as a
sample size. Neither column is an outcome.

### Periods with no filing coverage at all

After the dates below, **no filing was fetched for that CIK**, so a departure occurring
later would be invisible to the classifier regardless of whether it occurred. This is a
censoring statement about the measurement instrument, not a finding about departures.

| CIK | Organization | No coverage after | Interior gaps with no coverage |
|---|---|---|---|
| 18926 | CenturyLink | 2022-10-18 | 2014-11-24 to 2015-01-31; 2017-08-27 to 2018-08-21 |
| 20520 | Frontier Communications | 2024-12-09 | none |
| 101830 | Sprint Nextel | 2020-10-06 | 2013-01-28 to 2013-08-17 |
| 732712 | Verizon | 2024-08-04 | 2008-12-24 to 2012-01-21; 2020-04-04 to 2021-05-11 |
| 732717 | AT&T | 2024-10-11 | 2008-11-19 to 2010-01-01 |
| 1001082 | DISH Network, LLC | 2023-11-13 | none |
| 1091667 | Charter Communications, Inc. | 2024-02-28 | 2009-02-07 to 2011-04-27; 2015-03-29 to 2020-12-21 |
| 1166691 | Comcast | 2025-04-02 | 2009-12-19 to 2010-08-25; 2015-03-28 to 2020-01-05 |
| 1283699 | T-Mobile USA, Inc. | 2023-10-25 | none |
| 1447669 | Twilio | 2024-09-28 | none |
| 1609711 | GoDaddy.com LLC | 2023-11-13 | none |
| 1632127 | Cable One, Inc. | 2020-02-04 | none |

Every treated CIK is censored at its own last covered date, the earliest being
**2020-02-04** (1632127, Cable One, Inc.) and the latest
**2025-04-02** (1166691, Comcast). 6 of the 12 CIKs
(18926, 101830, 732712, 732717, 1091667, 1166691) additionally have interior gaps, some
multi-year. Any enforcement-timing analysis restricted to this store inherits all of it.

---

## Part 3 — What the repository cannot answer

### Confirmed: no FCC enforcement data exists in the pipeline

Searched the repository for enforcement datasets by filename and by content. Findings:

- `Data/fcc/fcc_data_template.csv` is an empty two-line **template** (header plus a
  placeholder row reading `YYYY-MM-DD, Company Name, FCC Registration Number, ...`).
  It contains no records.
- `outputs/defense_prep/canonical_fcc_firm_list*.csv` and
  `outputs/essay3_q2` treatment fields are **Form 499 registration** rosters — they
  establish who the rule can reach, not who was sanctioned.
- `outputs/audit/audit_fcc_analysis.csv` holds counts of `fcc_reportable`, again a
  treatment-assignment quantity.
- `outputs/essay3_q2/g4_charges_settlements.csv` holds sentences parsed from filings
  about charges and settlements (largely the Deutsche Telekom business-combination
  terms and breach-related litigation). It is filing text, not an enforcement docket,
  and carries no agency, no docket number, and no action date.

### `Data/enrichment/regulatory_enforcement.csv` is synthetic — do not use it

One file appears to hold enforcement data. It does not. `Data/enrichment/
regulatory_enforcement.csv` has 1,054 rows and 6 flagged `enforcement_type == "FCC"`.
Its generator, `scripts/47_regulatory_enforcement.py`, **fabricates these values**:

```python
# lines 51-66, scripts/47_regulatory_enforcement.py
if fcc_regulated and affected > 100000:
    import random
    random.seed(int(cik) if cik else idx)  # Reproducible
    if affected > 1000000:
        has_enforcement = 1 if random.random() < 0.3 else 0
    ...
    if has_enforcement:
        enforcement_type = 'FCC'
        penalty_amount = min(affected * 0.001, 10000000)
```

The flag is a seeded coin flip on breach size; the penalty is breach size times 0.001.
The script states its own status at line 118: *"NOTE: This uses heuristic enforcement
detection / For final analysis, verify against actual FCC/FTC enforcement databases."*
The file has **no date column and no docket column**, so even taken at face value it
could not date an enforcement action.

Its `breach_id` runs 0-1053, indexing the retired 1,054-row chain. `CANONICAL_V3.csv`
(489 rows) has no `breach_id`, so these rows cannot be joined to the current sample
without a crosswalk that does not exist in the repository.

**Containment, as verified:** no `enforcement`- or `penalty`-named column appears in
`CANONICAL_V3.csv` or in `e_analysis_sample.csv`, and no Essay 3 script (195-204) reads
the file. However, `scripts/53_merge_CONFIRMED_enrichments.py` and
`scripts/80_essay1_car_regressions.py` do read it, and **both are staged in `run_all.py`**
(lines 368 and 467; script 80 is labelled `[REFERENCE - SIC-BASED]`). Whether this
synthetic column reaches any current Essay 1 result was **not** established here and is
flagged for a separate check. It is out of scope for this exploratory note.

### What would have to be supplied manually

To test whether departures cluster near enforcement rather than near notification, the
following must be hand-collected from FCC primary sources and supplied as a dated file.
No web search was performed for this note, as instructed; the table below is the
specification of what is missing, with every value left blank.

Required, for each of the 12 treated parent CIKs, for every FCC **enforcement action,
consent decree, notice of apparent liability (NAL), or forfeiture order** during the
sample period (2006-12-01 to 2024-12-20):

| CIK | Organization | Action date | Action type | Docket / file no. | Release no. | Amount | Source URL |
|---|---|---|---|---|---|---|---|
| 18926 | CenturyLink |  |  |  |  |  |  |
| 20520 | Frontier Communications |  |  |  |  |  |  |
| 101830 | Sprint Nextel |  |  |  |  |  |  |
| 732712 | Verizon |  |  |  |  |  |  |
| 732717 | AT&T |  |  |  |  |  |  |
| 1001082 | DISH Network, LLC |  |  |  |  |  |  |
| 1091667 | Charter Communications, Inc. |  |  |  |  |  |  |
| 1166691 | Comcast |  |  |  |  |  |  |
| 1283699 | T-Mobile USA, Inc. |  |  |  |  |  |  |
| 1447669 | Twilio |  |  |  |  |  |  |
| 1609711 | GoDaddy.com LLC |  |  |  |  |  |  |
| 1632127 | Cable One, Inc. |  |  |  |  |  |  |

Notes on collection, so the result is analysable:

1. **Action type must be distinguished.** An NAL is a proposed penalty; a forfeiture
   order is the final one; a consent decree settles without a liability finding. They
   carry different dates and different salience, and collapsing them would destroy the
   timing question.
2. **The date must be the public release date**, to be comparable with the notification
   anchor the essay already uses.
3. **Corporate-family mapping is required.** Treatment here is assigned at the parent
   CIK after Form 499 clause (a)/(b) adjudication; FCC actions name carrier subsidiaries
   (for example Sprint Spectrum LLC, Verizon-NY, AT&T Enterprises LLC). Actions must be
   rolled up to the same parent CIK using the same rule, or treatment and enforcement
   will not align.
4. **Coverage from Part 2 still binds.** Even with enforcement dates in hand, a
   departure can only be observed where the filing store covers it. An enforcement
   action after a CIK's last covered date has no observable departure window at all.
5. Any analysis built on this would be a **new, exploratory, post-hoc** exercise and
   would need its own labelling. It would not join the existing test inventory or any
   BH family without a separate pre-specification.
