# Essay 3 — Appendix Tables, Supplement (Tables 12–15)

Written by `scripts/256_essay3_appendix_supplement.py` from committed outputs. These tables follow Appendix Tables 1–11 (`ESSAY3_APPENDIX_TABLES.md`, written by `scripts/245`), which are unchanged. Analysis sample throughout: N = 405 events (109 treated events at 13 treated parent CIKs; 296 control events; 119 parent-CIK clusters).

## Note to Table 5 (Classifier Validation)

The recall audit in Table 5 (source: `outputs/essay3_q2/d3_audit_recall_by_stratum.csv`, written by `scripts/201`) scored classifier v2, `scripts/195` at commit `6f7be7a` (blob `ec32364`). That is the classifier the v4 chain uses: the v4 constants name it, and the 15 classifier functions in `scripts/220` are identical to those in `scripts/195`. The audit file sits in the earlier build's folder because the audit was drawn and scored once, before the v4 relink; the relink changed the sample, not the classifier.

**Table 12**

*Randomization Inference: Reassigning Treatment Across Parent CIKs*

**Panel A: Randomization p-values**

| Outcome window | Reassignment pool | Eligible parent CIKs | Coefficient (pp) | CV3 t | RI p (coefficient) | RI p (CV3 t) |
|---|---|---|---|---|---|---|
| 30 days | All parent CIKs | 119 | +0.4 | +0.12 | .904 | .880 |
| 90 days | All parent CIKs | 119 | −4.1 | −0.52 | .596 | .587 |
| 180 days | All parent CIKs | 119 | +2.3 | +0.23 | .846 | .810 |
| Placebo (180 days before) | All parent CIKs | 119 | −8.6 | −1.02 | .408 | .287 |
| 30 days | Size-matched parent CIKs | 57 | +0.4 | +0.12 | .929 | .921 |
| 90 days | Size-matched parent CIKs | 57 | −4.1 | −0.52 | .546 | .587 |
| 180 days | Size-matched parent CIKs | 57 | +2.3 | +0.23 | .832 | .806 |
| Placebo (180 days before) | Size-matched parent CIKs | 57 | −8.6 | −1.02 | .323 | .270 |

**Panel B: Treated events per draw**

| Reassignment pool | Minimum | 5th pct. | 25th pct. | Median | 75th pct. | 95th pct. | Maximum | Mean | Share of draws with ≥ 109 treated events |
|---|---|---|---|---|---|---|---|---|---|
| All parent CIKs | 14 | 20 | 26 | 35 | 50 | 110 | 170 | 44.3 | 5.6% |
| Size-matched parent CIKs | 29 | 37 | 48 | 59 | 71 | 90 | 127 | 60.8 | 0.4% |

*Note.* Each draw selects 13 of the eligible parent CIKs at random, treats all of their events, and re-estimates the specification of Table 7; 9,999 draws, seed 250. The randomization p-value is the share of draws whose statistic is at least as large in absolute value as the observed one, computed for the coefficient and for the CV3 t-statistic. The size-matched pool keeps parent CIKs whose event count lies within the range of the observed treated parents. The observed design has 109 treated events; the 13 treated parent CIKs hold 115 events in total because some have untreated events, and each draw treats every event of a selected parent. Treated events are concentrated in a few large parents, so few draws reach the observed treated-event count (Panel B); the CV3 t-statistic accounts for that, the raw coefficient does not. Coefficients are percentage points. Source: `outputs/defense_supplement/e3_randomization_inference.csv` (`scripts/250`).

**Table 13**

*Chief Executive Departures by Window: Counts Only*

| Window | Treated events with a CEO departure (of 109) | Control events with a CEO departure (of 296) | Treated rate | Control rate |
|---|---|---|---|---|
| 30 days | 0 | 1 | 0.0% | 0.3% |
| 90 days | 3 | 8 | 2.8% | 2.7% |
| 180 days | 8 | 24 | 7.3% | 8.1% |

*Note.* Not estimated. The estimation script fits a chief-executive model only when each group has at least ten chief-executive departures in the window, and no window meets that (committed reason: "fewer than 10 CEO departures in at least one group; counts only"). The chief-executive field also validates poorly (Table 5), which is a second reason to report counts rather than estimates. Rates are counts divided by group size. Source: `outputs/essay3_v4/f5_ceo.csv` (`scripts/227`).

**Table 14**

*Director-Only Departures by Window: Descriptive Counts*

| Window | Treated events with a director-only departure (of 109) | Control events with a director-only departure (of 296) | Treated rate | Control rate |
|---|---|---|---|---|
| 30 days | 8 | 4 | 7.3% | 1.4% |
| 90 days | 18 | 20 | 16.5% | 6.8% |
| 180 days | 21 | 56 | 19.3% | 18.9% |

*Note.* Descriptive only; no model is fitted and no test is reported. A director-only departure is an Item 5.02 departure of a board member who is not also an executive officer; it is outside the outcome of H6. Rates are counts divided by group size. Source: `outputs/essay3_v4/f6_director.csv` (`scripts/227`).

**Table 15**

*T-Mobile: Executive Departures Disclosed Within the Outcome Windows, and the Placebo-Window Succession Filing*

| Executive | Filing date | Accession number | Window | T-Mobile events with this departure in window | Days from notification | Stated context (verbatim, Item 5.02) |
|---|---|---|---|---|---|---|
| Gary A. King | 2016-02-19 | 0001193125-16-470124 | Outcome (within 180 days after notification) | 3 | 107–141 | "On February 16, 2016, T-Mobile US, Inc. (the “Company”) and Gary A. King, Executive Vice President and Chief Information Officer, agreed that Mr. King will terminate his employment with the Company effective on March 18, 2016. Mr. King will receive a payment in the amount of one year of base salary in exchange for a release and covenant of future cooperation." |
| David A. Miller | 2021-09-16 | 0001193125-21-275230 | Outcome (within 180 days after notification) | 6 | 21–169 | "On September 10, 2021, David A. Miller, Executive Vice President, General Counsel and Secretary of T-Mobile US, Inc. (the “Company”) notified the Company that he will retire from the Company effective April 1, 2022. Mr. Miller will transition out of his current position as the Company’s Executive Vice President, General Counsel and Secretary effective October 11, 2021, but remain with the Company as Executive Vice President and Strategic Advisor until his retirement date." |
| Neville Ray | 2023-02-13 | 0001193125-23-035719 | Outcome (within 180 days after notification) | 1 | 25 | "On February 13, 2023, T-Mobile US, Inc. (the “Company”) entered into a letter agreement (the “Ray Letter Agreement”) with Neville Ray, the Company’s President, Technology setting forth certain benefits Mr. Ray will be entitled to receive from the Company upon his retirement. The Company and Mr. Ray have agreed that Mr. Ray’s retirement date will be on or about October 1, 2023. When Mr. Ray retires on that date, he will be entitled to receive the following (subject to his timely execution and non-revocation of a release of claims in favor of the Company):" |
| Peter Ewens | 2023-09-08 | 0001193125-23-231377 | Outcome (within 180 days after notification) | 3 | 133 | "On September 6, 2023, T-Mobile US, Inc. (the “Company”) entered into a letter agreement (the “Ewens Letter Agreement”) with Peter Ewens, the Company’s Executive Vice President, Corporate Strategy & Development, setting forth certain benefits Mr. Ewens will be entitled to receive from the Company upon his retirement on February 1, 2024. When Mr. Ewens retires, he will be entitled to receive the following (subject to his timely execution and non-revocation of a release of claims in favor of the Company and continued compliance with certain restrictive covenants):" |
| John Legere (chief executive); J. Braxton Carter | 2019-11-18 | 0001193125-19-294093 | PLACEBO (before notification) | — | — | "On November 18, 2019, the Board of Directors (the “Board”) of T-Mobile US, Inc. (“T-Mobile” or the “Company”), following a multi-year, comprehensive leadership succession planning process, announced that G. Michael Sievert, age 50, has been appointed as Chief Executive Officer (“CEO”) of T-Mobile, effective as of May 1, 2020. John Legere, the current CEO, will cease to serve as CEO of T-Mobile effective as of April 30, 2020, upon the conclusion of his current employment agreement with T-Mobile. Mr. Legere will continue to serve as CEO of T-Mobile and as a member of the Board through such date, and will continue to serve as a member of the Board thereafter. In connection with Mr. Sievert’s appointment as CEO, on and effective as of November 15, 2019, T-Mobile entered into an employment agreement (the “Sievert Employment Agreement”) with Mr. Sievert, which supersedes and replaces the prior compensation term sheet between T-Mobile and Mr. Sievert, dated as of January 1, 2017, as amended. Information regarding Mr. Sievert’s business experience, qualifications and other biographical data, including his experience over the past five years, is incorporated by reference to T-Mobile’s Definitive Proxy Statement relating to T-Mobile’s 2019 Annual Meeting of Stockholders, filed on Schedule 14A with the Securities and Exchange Commission (the “SEC”) on April 26, 2019." |

*Note.* T-Mobile US (parent CIK 1283699) contributes 26 events to the analysis sample. Four executive departures fall within 180 days after a T-Mobile notification date; one departure can fall in the windows of several events, so the events column counts how many T-Mobile events have it in window and the days column gives the range. The stated context is the first paragraph of each filing's Item 5.02 section that names the executive, quoted exactly; no classifier context flag is reported. The 2019 filing announces the chief-executive succession and amends the chief financial officer's agreement; it precedes the notification date of the nearest T-Mobile event and so falls in the placebo window, not an outcome window. No filing links a departure to a breach, and none is interpreted here. Sources: `outputs/essay3_v4/g6_case_table.csv` (`scripts/228`); `outputs/essay3_q4/tmobile_502_text.md` (verbatim filing text).
