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

## 7. Two CIKs, one firm: Aon is clustered as two firms in Essays 1 and 2

Essays 1 and 2 cluster on `CANONICAL_V3.final_cik` — `158:300` passes
`cov_kwds={'groups': reg['final_cik']}` and reports "clustering by parent CIK", and
`scripts/165` declares "Cluster level: PARENT CIK (final_cik)" and asserts
`fin['final_cik'].nunique() == 82`. In `CANONICAL_V3`, `final_cik` is the CIK the event
was *recorded* under, which for a subsidiary or a pre-succession registrant is not the
listed parent. **Within these two samples exactly one firm is therefore counted twice:**

| firm | CIK | event | treated? |
|---|---|---|---|
| Aon | **315293** (`Aon plc`, ticker AON) | `Aon Corporation` 2020-12-17 | control |
| Aon | **1808065** (`Aon plc`, no ticker, filings from 2020-04) | `Aon Corporation PLC` 2020-12-29 | control |
| Aon | **1808065** | `Aon PLC` 2022-02-25 | control |

`CANONICAL_V4` joins these two CIKs on a verified succession filing
(`link_basis = successor_filing`, `orig_cik = 1808065`, `final_cik = 315293`). All three
events are **control**, so no treated cluster is affected.

**Cluster counts if Aon were merged:**

| sample | N | clusters now | clusters merged |
|---|---:|---:|---:|
| Essay 1 regression | 340 | **83** | **82** |
| Essay 2 final | 333 | **82** | **81** |
| Essay 1 CRSP (for reference) | 356 | 88 | 86 |

The Essay 1 CRSP sample loses two because Google/Alphabet (1288776 → 1652044) also appears
under both CIKs there; that pair does not survive into the 340, and Seagate
(1137785 → 1137789) splits in `CANONICAL_V3` but only the parent reaches either sample.

**This is the complete list.** Every CIK pair the `CANONICAL_V4` re-parenting map joins was
checked against both samples, and a second pass over organisation-name agreement found no
further case. Two name matches were adjudicated and are **not** errors:

- **Hewlett-Packard** — CIK 47217 (`Hewlett-Packard Company`, 5 events 2007-07-01 to
  2010-02-09) and CIK 1645590 (`Hewlett Packard Enterprise Company`, 2 events 2023-12-12 to
  2025-02-05). Separate firms after the 2015 split, with non-overlapping event windows.
- **Sprint / T-Mobile** — CIK 101830 (Sprint-era equity, 12 events) and CIK 1283699
  (T-Mobile, 34 events). A deliberate point-in-time separation: Sprint traded on its own
  until the 2020 merger, and Gate 1 rule F pins the Sprint-era events to the Sprint equity
  (*"Gate1-F: Sprint-era equity (SEC-verified: SPRINT LLC fka SPRINT CORP/NEXTEL,
  10-Ks 2014-2019)"*).

**Essay 3 is unaffected.** Its chain reads `CANONICAL_V4`, whose `final_cik` is already the
re-parented registrant — 27 of its rows have `final_cik != orig_cik`. Its analysis sample
(N=405) spans 119 clusters and contains **zero** firms under more than one `final_cik`.

The samples are frozen, so this is disclosed and not corrected. The direction of the bias
is known: splitting one firm into two clusters overstates the number of independent
clusters by one, which makes clustered standard errors slightly **too small**. With
82 or 83 clusters, one spurious cluster is immaterial to any verdict, and Essay 2's
inference of record rests on CV3 and the wild cluster bootstrap rather than on the cluster
count alone.

---

## 8. One breach date postdates its own notification by three and a half years

`CANONICAL_V3` carries a `breach_date` of **2012-08-01** for a Sprint Nextel event whose
own record text places the breach in **December 2008 to January 2009** and whose
notification date is **2009-03-30**:

> *"The New Hampshire Department of Justice reported a data breach involving Sprint Nextel
> on March 30, 2009. The breach occurred between December 2008 and January 2009, affecting
> 4 residents of New Hampshire. The compromised information includes customers' names,
> addresses, wireless phone numbers, Sprint account numbers, security question answers, and
> points of contact, but did not include Social Security numbers or payment information."*

The row's own `end_breach_date` is **2009-01-01**, the end of the window the text
describes. A breach date of 2012-08-01 is impossible: it falls three years and five months
*after* the breach was reported. This is the same wrong-field class as entry 2, but it
lands on the breach date rather than the notification date.

**Which samples contain it:**

| sample | contains it? | why |
|---|---|---|
| Essay 1 CRSP (356) | **yes** | `has_crsp_data = 1`, permno 39087, and it carries `car_30d = 12.0426` — a 30-day CAR computed on the wrong anchor |
| **Essay 1 regression (340)** | **no** | dropped by the control filter, for a missing `immediate_disclosure` |
| **Essay 2 (333)** | **no** | not in the final sample |
| Essay 3 v4 (405) | yes, **at the corrected date** | treated; enters as 2009-01-01 |

So it reaches no regression of record. It does sit inside the 356-event CRSP sample, which
the descriptive and Table 16 panels are drawn from, carrying a CAR measured on a date the
record contradicts.

**v4 corrects it.** `scripts/214`'s `fix_sprint` rewrites the `breach_date` to the row's
own `end_breach_date`, giving 2009-01-01, and only after asserting that its recomputation
of `prior_breaches_1yr` reproduces v3's stored column exactly under the original dates —
so the rule is v3's, not a new one. The correction also moves the *other* Sprint Nextel
event (2009-02-01, "late February 2009", reported 2009-06-12 — a genuinely separate PRC
record and a correct date) from `prior_breaches_1yr = 0` to `1`, because the first event
now correctly precedes it within 365 days.

`CANONICAL_V3` is frozen, so v3 keeps the wrong date and Essay 3 uses the corrected one.

---

## What has been fixed, for contrast

So that this ledger is not read as a list of open defects: the LFS placeholder problem
*was* fixed (all 87 attributes restored, plus an executable guard that aborts
`run_all.py` before step 1 on a missing or placeholder input); the retired Essay 3 H6 keys
*were* removed from `constants_v3.json` at the rebaseline; and the HC3 significance label
*was* disqualified before it could ever read `SIGNIFICANT`; and the v4 linker's second
pass *was* staged in `run_all.py`, so the v4 linkage is now derived from the canonical data
rather than read from a committed artefact. The eight entries above are different in kind —
they are properties of the source records and of anchoring decisions, and correcting any of
them would change the samples, which is the thing this project has decided not to do.
