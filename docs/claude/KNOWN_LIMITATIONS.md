# Known limitations — disclosed, not corrected

**The samples are frozen by decision.** `CANONICAL_V3` (489 events) and `CANONICAL_V4`
(489 events) stay exactly as committed. Every entry below is a measurement limitation that
is **disclosed rather than corrected**: nothing here has been fixed in the data, no event
has been merged or dropped, no date has been re-anchored, and no linkage has been changed.
Each entry carries its counts at every sample level and the report and line that establish
it, so a reader can check the figure rather than take it on trust.

Samples referenced throughout: `CANONICAL_V3` (489), Essay 1 regression (340), Essay 2
analytic (333), Essay 3 v4 analysis (405). Treated counts always name their level — events,
parent entities (distinct `org_name`), or parent CIKs (distinct `final_cik`).

---

## 1. One incident can appear as several events

**79 of the 489 canonical events are one incident recorded across separate state filings**,
where a sibling PRC record on the same parent CIK carries an earlier, different breach date
and a notification date within 30 days. **19 treated events, 60 control, across 26 distinct
parent CIKs.**

| sample | same-date events with no independent breach date | recoverable from a sibling record (strict) | treated | control |
|---|---:|---:|---:|---:|
| `CANONICAL_V3` | 147 | 89 | 23 | 66 |
| Essay 1 regression | 113 | 73 | 22 | 51 |
| Essay 2 analytic | 112 | 72 | 22 | 50 |
| Essay 3 v4 analysis | 125 | 79 | 22 | 57 |

Concentration matters here: Intuit contributes 20 of the 79, T-Mobile and Sprint 8, Sirius
XM 7, Fidelity National Information Services 6, Uber 5.

**Worked example — DISH Network, 2023.** Eight PRC records, all CIK 1001082, became two
canonical events. Seven collapsed into one event at breach 2023-02-22 under the Gate-2
adjacency rule (chain CH-22). The eighth, a Massachusetts filing of 2023-05-17, became a
second event because it lies 83 days after the February records — far outside the ≤3-day
adjacency window, which is the only rule that was ever applied to the question. DISH's own
SEC filings describe **one** 2023 incident: the 8-K of 2023-02-28 (Item 8.01) reports a
network outage announced on the February 23 earnings call and data extraction discovered
February 27, the Q1 10-Q repeats it, and the Q2 10-Q — which covers the quarter containing
2023-05-17 — describes no incident at all.

Folding the May record in would move Essay 1 to N 339 with 105 treated events, Essay 2 to
N 332 with 103 treated events, and Essay 3 v4 to N 404 with 108 treated events, leaving
every cluster and parent-CIK count unchanged. **That fold has not been made.**

*Source: `outputs/TIMING_MEASUREMENT_REPORT.md:552` (the 79), and the DISH duplicate check.*

---

## 2. For a third of events, the breach date is the filing date

`breach_date == reported_date` for a large minority of events, and for almost all of them
nothing in the record corroborates the breach date.

| sample | same-date events | treated | control | share | of which Massachusetts |
|---|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 151 | 48 | 103 | 30.9% | 123 |
| Essay 1 regression | 116 | 41 | 75 | 34.1% | 93 |
| Essay 2 analytic | 115 | 41 | 74 | 34.5% | 92 |
| Essay 3 v4 analysis | 128 | 42 | 86 | 31.6% | 105 |

**The Massachusetts pattern.** Across the full 1,054-record PRC file,
`breach_date == reported_date` holds for **143 of 150 Massachusetts records (95%)** against
**38 of 904 (4%)** from every other source — a 24-fold difference. Not one of the 123
Massachusetts same-date events carries an independent breach date in its description text.
The repository holds **no documentation** of what the Massachusetts breach-date field
records: `DATA_DICTIONARY_ENRICHED.csv` is auto-generated column statistics with no row for
`reported_date`, and no `docs/` file defines either field. The inference rests on the
95%-versus-4% pattern and the record texts, not on a codebook.

**What this does to Essay 1's timing variable.** Of the **124** events in the Essay 1
regression sample coded `immediate_disclosure = 1` (36.5% of 340; 45 treated events, 79
control), **8 reflect a documented gap of seven days or less** — delays of 0, 0, 2, 3, 3,
3, 3 and 7 days. 116 of the 124 (94%) have `breach_date == reported_date`, and 93 of the
124 (75%) are Massachusetts records.

**What it does to Essay 2's delay variable.** `delay_w == 0` for 117 of 333 (35.1%; 40.4%
of treated events). 112 of those 117 are same-date records with no independent breach date.
Setting those aside would move the zero-delay share to 2.3% and the median delay from 23
days to 54.

**EDGAR cannot repair it.** 29 candidate 8-K filings were fetched for the events a sibling
record could not resolve: 27 described no incident, one described an incident without a
date, and one (CrowdStrike, 2024-07-19) confirmed the existing date rather than correcting
it. **Recovery rate 0 of 29.** For most of these events the PRC filing *is* the disclosure.

*Sources: `outputs/TIMING_MEASUREMENT_REPORT.md:43` (the 95%/4% pattern), `:151` (the 124),
`:155` (the 8).*

---

## 3. The two essays anchor their event windows on different dates

- **Essay 1, `car_30d`:** anchored on **`breach_date`** — `scripts/155:42` builds `bdt`
  from `breach_date`, `155:177-178` passes it to `outcomes()`, and `155:152-159` spans the
  trading day nearest the anchor plus 30 more, 31 trading days `[0, +30]`.
- **Essay 2, the volatility windows:** anchored on **`reported_date`** — `scripts/163:131`
  builds `rdt` from `reported_date`, `163:179-180` passes it to `essay2_windows()`, with
  `PRE_LO, PRE_HI, POST_LO, POST_HI = -25, -5, 5, 25` at `163:156`.

**No committed methods document states why the two differ or defends either choice.** The
only place the difference is recorded at all is
`outputs/ESSAY2_QUERY6_REPORT.md:15-18`, as a flag.

**Windows that close before the market was told.** For events whose notification is more
than 30 trading days after the breach date, the `car_30d` window cannot reach the
notification:

| sample | events with a genuine gap | treated | control |
|---|---:|---:|---:|
| `CANONICAL_V3` | 207 | 45 | 162 |
| Essay 1 regression | **128 of 340 (38%)** | **42 of 106** | 86 |
| Essay 2 analytic | 122 | 40 | 82 |
| Essay 3 v4 analysis | 165 | 43 | 122 |

Essay 2 has the mirror problem: its pre-window `[-25,-5]` reaches back to the breach date in
**0 of its 122** genuine-gap events.

**And a mixed anchor inside Essay 1.** Because 116 of Essay 1's 340 events have
`breach_date == reported_date`, Essay 1's "breach-anchored" window is in fact anchored on
the reporting date for those events — on the *filing* date for the 93 Massachusetts ones.
224 events are anchored on an occurrence date and 116 on a reporting date, in one
specification.

*Sources: `outputs/TIMING_MEASUREMENT_REPORT.md:226` and `:669`.*

---

## 4. There is no single notification-date rule

Three departures, which compound:

1. **Two different rules inside v3.** Stage 3 takes the chain minimum
   (`scripts/152:91`, `g['reported_date'].min()`); Gate 2 keeps the earliest-*breach*
   component's date instead (`scripts/153:59`). **31 Gate-2 chained events** in
   `CANONICAL_V3` (9 treated events, 22 control; 28 in each essay sample, 8 treated) carry
   a notification date chosen by a different rule from the other 458.
2. **v4 repairs 14 of those; v3 repairs none.** Freeze exception 2 (`scripts/214:328-351`)
   re-anchors 14 events to the chain minimum. The gaps closed range from 1 day to
   **1,109 days** (GoDaddy.com LLC). **The two vintages therefore disagree**: DISH's
   February event is `2023-05-15` in v3 and `2023-02-23` in v4, which changes that event's
   disclosure delay from 82 days to 1 and its `immediate_disclosure` coding with it.
3. **The underlying field is not one quantity.** Across the DISH chain alone the seven
   source records' `reported_date` values include state attorney-general filing dates
   (Indiana 5/15, Maryland 5/16, California 5/18, Washington 5/18, Oregon 5/18), a company
   **self-report** date (5/08), and a **public-announcement** date (2023-02-23). v4's
   chain-minimum rule selected the last of those. No rule anywhere chooses among source
   types.

*Source: `outputs/TIMING_MEASUREMENT_REPORT.md:432` and `:675`.*

---

## 5. CRSP linkage attrition falls almost entirely on controls

Under `scripts/155`, treated events link to CRSP at a far higher rate than controls:

| group | events | linked by `155` (`has_crsp_data`) |
|---|---:|---:|
| **Treated** | 118 | **111 of 118 = 94.1%** |
| **Control** | 371 | **245 of 371 = 66.0%** |
| All | 489 | 356 of 489 = 72.8% |

The treated group is almost entirely large listed telecommunications carriers; the control
group contains private registrants, foreign issuers and firms with no US-listed equity at
the breach date. The consequence is that the control group in every essay is a **survivor
sample of the larger, listed controls**, and the comparison is between treated carriers and
the subset of controls that could be linked — not between treated carriers and all controls.

The v4 point-in-time linkage changes only the control side: control retention rises to 267
of 371 (72.0%) while treated retention is unchanged at 111 of 118, with 42 control events
gained and 20 lost. Of the 20 lost, 13 were correct links v4 refused; the refusals split 6
at CIK→gvkey, 9 at CUSIP→permno, and 5 at the identity gate.

*Source: `outputs/RUN_ALL_FOLLOWUP_REPORT.md:539-540`; the refusal split is
`outputs/TIMING_MEASUREMENT_REPORT.md` Part G1, which corrects the earlier Part N4
diagnosis at `RUN_ALL_FOLLOWUP_REPORT.md:825-830`.*

---

## 6. Two records have a corrupted notification date, not a corrupted breach date

The mirror image of entry 2, and it breaks Essay 2 rather than Essay 1 — for these two the
breach date is right and the **notification** date was overwritten with the breach date:

| org | event | treated? | what the record text says |
|---|---|---|---|
| **Sprint** | 2019-06-08 | treated | *"On July 3, 2019, the California Office of the Attorney General reported a data breach involving Sprint. The breach occurred between June 8 and June 22, 2019"* — so the notification date should be 2019-07-03 |
| **Roku Inc** | 2023-12-28 | control | *"reported a data breach involving Roku, Inc. on March 8, 2024. The breach likely occurred between December 28, 2023, and February 21, 2024"* — so the notification date should be 2024-03-08 |

Both appear in all four samples. Because Essay 2 anchors on `reported_date`, its volatility
windows for these two events are anchored on a date that is not a notification date.

*Source: `outputs/TIMING_MEASUREMENT_REPORT.md:118`.*

---

## What has been fixed, for contrast

So that this ledger is not read as a list of open defects: the LFS placeholder problem
*was* fixed (all 87 attributes restored, plus an executable guard that aborts
`run_all.py` before step 1 on a missing or placeholder input); the retired Essay 3 H6 keys
*were* removed from `constants_v3.json` at the rebaseline; and the HC3 significance label
*was* disqualified before it could ever read `SIGNIFICANT`. The six entries above are
different in kind — they are properties of the source records and of anchoring decisions,
and correcting any of them would change the samples, which is the thing this project has
decided not to do.
