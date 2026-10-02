# Timing Measurement — same-date records, event anchors, and the notification-date rule

**Stage 1, read-only.** Nothing was estimated, edited or pulled. `run_all.py` and
`scripts/158` were not executed. No dataset, script, constants file or prose was changed.
EDGAR was reached only through the sanctioned fetch tool.

Every count below is NEW unless marked "not recomputed", and every computation names the
scratchpad script that produced it. Treated counts name their level: events, parent
entities (distinct `org_name`), parent CIKs (distinct `final_cik`).

---

# PART A — anatomy of the same-date records

## A1. How many, and from where

*NEW — `tm_common.py`, `tm_partA3.py`.* This dataset has **no source column**: the
reporting authority exists only inside the `incident_details` prose, and is parsed from
the first 200 characters.

| sample | N | same-date | treated | control | share |
|---|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 489 | 151 | 48 | 103 | 30.9% |
| Essay 1 regression | 340 | 116 | 41 | 75 | 34.1% |
| Essay 2 analytic | 333 | 115 | 41 | 74 | 34.5% |
| Essay 3 v4 analysis | 405 | 128 | 42 | 86 | 31.6% |

Sources with **at least 5** such records (`CANONICAL_V3`):

| source | same-date events | treated | control |
|---|---:|---:|---:|
| **Massachusetts** | **123** | 37 | 86 |
| (no state named — curated one-line records) | 9 | 4 | 5 |
| New Hampshire | 6 | 1 | 5 |

Below 5, all in `CANONICAL_V3`: Texas 3, California 3, Indiana 2, and one each from US HHS,
Maryland, Washington, Wisconsin, Maine.

In Essay 1's 116: Massachusetts 93 (31 treated), no-state-named 9, then singletons.
In Essay 3 v4's 128: Massachusetts 105 (32 treated).

**The Massachusetts concentration is not a coincidence of sampling.** Across the full
1,054-record PRC file, `breach_date == reported_date` holds for **143 of 150 Massachusetts
records (95%)** against **38 of 904 (4%)** everywhere else — a 24-fold difference.

*One parsing caveat, stated rather than buried:* the single "Washington" same-date record
is **ServiceNow**, whose text names "Vancouver and Washington DC releases" — a product
name, not a reporting authority. It is a false positive of the source parser. It does not
change any count other than that one row's label.

## A2. Is the Massachusetts field documented anywhere in the repository?

**No. The repository holds no documentation of what any PRC field records, and none for
the Massachusetts source.**

- `Data/processed/DATA_DICTIONARY_ENRICHED.csv` is **auto-generated column statistics** —
  name, dtype, non-null count, "549 unique values". It carries no semantics, and it has no
  row for `reported_date` at all.
- No `.md` under `docs/` defines `breach_date` or `reported_date`. A repo-wide search for
  definitional phrasing ("breach date is", "the date the breach", "notification date")
  returns nothing in `docs/`.
- Massachusetts appears in exactly three committed `.md` files, none of them documentation
  of the field: `ADJUDICATION_EVIDENCE_SHEET.md`, `GATE2_ADJACENCY_SHEET.md`, and
  `ESSAY2_QUERY6_REPORT.md`.

So the claim that the Massachusetts breach-date field carries the filing date rests on the
**95%-versus-4% pattern above and the record texts themselves**, not on source
documentation. That is weaker evidence than a codebook would be, and it should be
described that way.

**Already emitted, not recomputed** — `outputs/ESSAY2_QUERY6_REPORT.md:15-22` reached the
same problem from Essay 2's own focal case:

> Essay 2 anchors on the notification date, so the anchor is
> ALREADY 8/16 — no correction required. Essay 1's car_30d anchors on the
> 8/13 occurrence date (breach-anchored convention; the Part-F flag
> applies). STRUCTURE NOTE for the intro: the incident appears as THREE
> canonical events (8/13 Wisconsin, 8/17 Maryland, 8/26 Massachusetts
> filings carrying different stated breach dates), kept distinct by the
> signed 3-day adjacency rule — the records-vs-events problem in
> miniature, from the essay's own focal case.

## A3. The non-Massachusetts same-date records, classified

*NEW — `tm_partA3.py`.* **The rule**, applied in order, with dates extracted from the
description prose and compared against the record's own fields:

1. **GENUINE_SAME_DAY** — the text says the incident happened on the reporting date.
2. **BREACH_DATE_UNKNOWN** — the text states the breach date is unknown or unavailable.
3. **REPORTED_DATE_CORRUPTED** — the text gives a report date *later* than the field's
   `reported_date` while an incident date matching the field's `breach_date` also appears.
   Here the breach date is real and the **notification** date is what was overwritten.
4. **NO_INDEPENDENT_DATE** — only the reporting date, or no date at all; nothing
   corroborates the breach date.

`CANONICAL_V3`, 151 same-date events:

| class | events | treated | control | Massachusetts |
|---|---:|---:|---:|---:|
| GENUINE_SAME_DAY | 1 | 0 | 1 | 0 |
| BREACH_DATE_UNKNOWN | 1 | 1 | 0 | 0 |
| REPORTED_DATE_CORRUPTED | 2 | 1 | 1 | 0 |
| **NO_INDEPENDENT_DATE** | **147** | 46 | 101 | **123** |

Essay 1 (116): 113 NO_INDEPENDENT_DATE (39 treated / 74 control, 93 Massachusetts), 1
BREACH_DATE_UNKNOWN, 2 REPORTED_DATE_CORRUPTED. Essay 2 (115): 112 / 1 / 2. Essay 3 v4
(128): 125 / 1 / 2.

**Not one of the 123 Massachusetts same-date records carries an independent breach date in
its text.** All 123 classify as NO_INDEPENDENT_DATE.

The individually identified non-Massachusetts cases:

- **GENUINE_SAME_DAY (1).** Twitter 2013-02-01 (control) — *"The breach occurred the same
  day, affecting approximately 250,000 users"*.
- **BREACH_DATE_UNKNOWN (1).** Charter Communications 2023-09-01 (treated) — *"although
  the specific breach date is not available"*.
- **REPORTED_DATE_CORRUPTED (2).** Sprint 2019-06-08 (treated) — *"On July 3, 2019, the
  California Office of the Attorney General reported … The breach occurred between June 8
  and June 22, 2019"*; Roku 2023-12-28 (control) — *"reported … on March 8, 2024. The
  breach likely occurred between December 28, 2023, and February 21, 2024"*. **For these
  two the breach date is correct and the notification date is wrong** — the mirror image of
  the Massachusetts problem, and it breaks Essay 2 (notification-anchored) rather than
  Essay 1.
- **NO_INDEPENDENT_DATE (24).** Frontier, HP ×1, IBM, Apple ×2, Verizon, AT&T ×2, Adobe,
  Charter, Salesforce, Global Payments, Comcast, T-Mobile, Fox, Duke Energy, ServiceNow,
  Twilio ×2, CrowdStrike, Uber ×2, Snowflake, Okta.

**Ambiguous cases, as asked.** Nine of the 24 are the "(no state named)" curated records —
Charter, Twilio ×2, CrowdStrike, Snowflake, Adobe, AT&T Services, Apple ×2 — one-line
summaries with **no date anywhere in the text**, so the rule cannot distinguish "incident
occurred that day" from "no breach date known". They are counted as NO_INDEPENDENT_DATE
because nothing corroborates the field, but they are a different kind of record from a
state filing and only a source document can settle them. One of the nine was settled by
Part B2: **CrowdStrike's 2024-07-19 is genuine** (its own 8-K says so).

*Two regex bugs found and fixed in this part, recorded because they changed counts:* the
first version of rule 3 used `[^.]{0,40}`, which cannot cross the period in "Roku, Inc."
and is too narrow for "On July 3, 2019, the California Office …"; and the date extractor
could not read "between June 8 and June 22, 2019", where the year is given once. Both were
hiding REPORTED_DATE_CORRUPTED records inside NO_INDEPENDENT_DATE.

## A4. Essay 1: what `immediate_disclosure = 1` survives

*NEW — `tm_partA45.py`.* As it stands: **124 of 340** events (36.5%), 45 treated / 79
control. Setting a breach date to unknown makes the timing variable missing, and
`immediate_disclosure` is a required control, so the event leaves the regression.

| | events dropped | N surviving | `immediate = 1` surviving | treated | control | share of survivors |
|---|---:|---:|---:|---:|---:|---:|
| as it stands | — | 340 | **124** | 45 | 79 | 36.5% |
| **Treatment 1** — Massachusetts same-date unknown | 93 (31 T / 62 C) | 247 | **31** | 14 | 17 | 12.6% |
| **Treatment 2** — no independent breach date unknown | 113 (39 T / 74 C) | 227 | **11** | 6 | 5 | 4.8% |

**What the 11 survivors of Treatment 2 actually are:** 8 events with a genuine 1–7 day gap
(delays of 0, 0, 2, 3, 3, 3, 3, 7 days) and 3 same-date events of the other A3 classes
(the 2 REPORTED_DATE_CORRUPTED and the 1 BREACH_DATE_UNKNOWN).

So of the 124 events the variable currently calls immediate disclosure, **8 reflect a
documented gap of seven days or less**. The rest rest on a date equality.

## A5. Essay 2: `delay_w` under the same treatments

*NEW — `tm_partA45.py` (recomputed; the first version of the helper mis-aligned the
treated/control masks and printed only the pooled row).*

| | group | n | mean | median | share = 0 |
|---|---|---:|---:|---:|---:|
| as it stands | all | 333 | 74.12 | 23.0 | **35.1%** |
| | treated | 104 | 82.46 | 22.0 | 40.4% |
| | control | 229 | 70.33 | 24.0 | 32.8% |
| **Treatment 1** | all | 241 | 102.41 | 45.0 | **10.4%** |
| | treated | 73 | 117.48 | 55.0 | 15.1% |
| | control | 168 | 95.86 | 41.5 | 8.3% |
| **Treatment 2** | all | 221 | 111.68 | 54.0 | **2.3%** |
| | treated | 65 | 131.94 | 63.0 | 4.6% |
| | control | 156 | 103.24 | 49.0 | 1.3% |

112 of the 117 events with `delay_w == 0` are same-date records with no independent breach
date. The zero-delay mass that Essay 2's "the rule is a floor that does not bind" reading
rests on is **almost entirely a date-equality artefact**: 35.1% → 2.3% once those records
are set aside, and the median delay roughly doubles, from 23 days to 54.

---

# PART C — the event-window anchor

## C1. What each essay anchors on

**The two essays use different anchors, and neither file says why.**

- **Essay 1, `car_30d`: the breach date.** `scripts/155:42` builds
  `ev['bdt'] = pd.to_datetime(ev['breach_date'])`; `155:177-178` calls
  `outcomes(permno, r['bdt'])`. The window is built at `155:152-159`: the trading day
  nearest the anchor, then 30 further trading days — 31 trading days, `[0, +30]`.
- **Essay 2, the volatility windows: the notification date.** `scripts/163:131` builds
  `ev['rdt'] = pd.to_datetime(ev['reported_date'])`; `163:179-180` calls
  `essay2_windows(p, a) for p, a in zip(ev['permno'], ev['rdt'])`. The windows are
  `PRE_LO, PRE_HI, POST_LO, POST_HI, MIN_OBS = -25, -5, 5, 25, 15` at `163:156`.

**Is the anchor and its rationale described in any methods document?** Only in one place,
and as a flag rather than a rationale — `outputs/ESSAY2_QUERY6_REPORT.md:15-18`, quoted in
A2 above: *"Essay 2 anchors on the notification date … Essay 1's car_30d anchors on the
8/13 occurrence date (breach-anchored convention; the Part-F flag applies)."* No committed
methods document states why the two differ or defends either choice.

**The consequence of A1 for Essay 1.** For the 116 same-date events in its sample,
`breach_date == reported_date`, so Essay 1's "breach-anchored" window is in fact anchored
on the notification date — on the *filing* date for the 93 Massachusetts ones. Essay 1
therefore runs a **mixed-anchor regression**: 224 events anchored on an occurrence date and
116 on a reporting date, in one specification, undocumented.

## C2. Does the `car_30d` window reach the notification date?

*NEW — `tm_partC.py`.* "Genuine gap" = notification more than 30 **trading** days after the
breach date.

| sample | n | genuine gap | window closes before the notification | treated | control |
|---|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 489 | 207 | **207** | 45 | 162 |
| Essay 1 regression | 340 | 128 | **128** | 42 | 86 |
| Essay 2 analytic | 333 | 122 | **122** | 40 | 82 |
| Essay 3 v4 analysis | 405 | 165 | **165** | 43 | 122 |

For every one of them the answer is no, by construction: the window spans 31 trading days
from the breach anchor and the notification lies beyond it. **128 of Essay 1's 340 events —
38%, including 42 of its 106 treated events — have a `car_30d` window that closes before
the market was told.**

Trading-day gap distribution: Essay 1 median 17, mean 59.4, p90 145, max 1,320; 118 events
at a gap of ≤ 0 (the 116 same-date events plus 2 where the notification precedes the breach
date, which `156:115-131` handles as wrong-field records).

**Essay 2 inverts the question** — its anchor *is* the notification, so the test is whether
its pre-window `[-25,-5]` reaches back to the breach. Wherever the gap exceeds 30 trading
days it cannot: **0 of 122**. Essay 2's pre-window contains the breach date only when the
gap happens to fall between 5 and 25 trading days.

## C3. The earliest public disclosure date available in the repository

*NEW — `tm_partC3.py`.* Sources: PRC `reported_date`; the cached EDGAR submission indexes
(`Data/edgar/rebuild_submissions_cache/`, 162 CIKs); and
`outputs/rebuild/stage7_disclosure_date_verification.csv` (335 rows, written by
`scripts/157:85` — the first 8-K within +90 days of the breach, for treated events plus
control CIKs with 3 or more events, so **not full coverage**).

A first pass counted *any* EDGAR form in the window and returned 204 of 340 for Essay 1.
That number is wrong for this purpose — it includes Form 4s, 13G/As and 10-Qs, which
disclose nothing about a breach. Restricted to **8-K**:

| sample | n | any 8-K before `reported_date` | treated | with item 1.05 / 7.01 / 8.01 | treated | control |
|---|---:|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 489 | 220 | 58 | **168** | 47 | 121 |
| Essay 1 regression | 340 | 169 | 56 | **131** | 45 | 86 |
| Essay 2 analytic | 333 | 163 | 54 | **125** | 43 | 82 |
| Essay 3 v4 analysis | 405 | 200 | 57 | **153** | 44 | 109 |

Gap, `reported_date` minus the first intervening 8-K, calendar days — Essay 1: median 56,
mean 141.7, p90 336, max 1,888. Restricted to the three item codes: median 62, mean 155.2.

**Caveat.** An 8-K in the window is not proof it discussed the breach; the item codes
narrow it but do not confirm it. These are **upper bounds** on how many events had an
earlier disclosure available. Part B2 tested that assumption directly on 29 such filings
and found the precision very low.

---

# PART B — can true breach dates be recovered?

## B1. From a sibling PRC record

*NEW — `tm_partB1.py`.* The query specifies a ±120-day window on the notification date.
That window is loose enough to pair a *different* incident at the same firm: it matches
AT&T's 2024-04-09 event to a 2019-01-01 breach, a shift of 1,925 days, and Home Box Office
across 446 days. So two criteria are reported — the literal 120-day one, and a strict
**same-wave** one (notification dates within 30 days), which is what the DISH pattern
actually looks like (DISH's own pair is 1 day apart on notification, 84 days apart on
breach date).

| sample | same-date, no independent date | recoverable, 120d | treated | control | **recoverable, strict 30d** | treated | control |
|---|---:|---:|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 147 | 105 | 29 | 76 | **89** | 23 | 66 |
| Essay 1 regression | 113 | 83 | 26 | 57 | **73** | 22 | 51 |
| Essay 2 analytic | 112 | 82 | 26 | 56 | **72** | 22 | 50 |
| Essay 3 v4 analysis | 125 | 90 | 26 | 64 | **79** | 22 | 57 |

The DISH pair appears in the strict set: event 2023-05-17 (Massachusetts) ← sibling breach
2023-02-22 (California), notification dates 1 day apart, shift 84 days. Other strict
matches include Cricket Wireless (shift 4 days), CenturyLink (29), Charter (28), Cisco
(18), Crown Castle (19), HP (4), and long runs for Intuit, Sirius XM, Fidelity National
Information Services, Uber, T-Mobile and Verizon. Full list in the scratchpad
(`b1_recoveries.csv`); 26 distinct parent CIKs are involved.

## B2. From EDGAR

*NEW — `tm_partB2_screen.py`, `tm_partB2_screen2.py`, then 29 fetches.*

Screening first, so fetches were not spent on documents that cannot carry an incident
date. A 180-day lookback taking the earliest qualifying 8-K returned earnings releases and
debt offerings, so it was tightened to: 8-K filed within 45 days before the notification
(or 7 days after), carrying item 1.05, 8.01 or 7.01, nearest the notification date first.

| sample | unrecovered after B1 (strict) | plausible filing | treated | no plausible filing |
|---|---:|---:|---:|---:|
| `CANONICAL_V3` | 58 | 30 | 11 | 28 |
| Essay 1 regression | 40 | 23 | 9 | 17 |
| Essay 2 analytic | 40 | 23 | 9 | 17 |
| Essay 3 v4 analysis | 46 | 26 | 10 | 20 |

**29 distinct filings fetched — all of them, under the 60-fetch cap, so no sampling was
needed and no seed applies.** Outcome:

| | count |
|---|---:|
| incident described **with** a date | **1** |
| incident described **without** any incident date | 1 |
| no incident described at all | 27 |
| **breach dates recovered** | **0** |

- **CrowdStrike** (8-K filed 2024-07-22, item 8.01): *"On July 19, 2024, CrowdStrike
  Holdings, Inc. … released a sensor configuration update for our Falcon sensor software
  that resulted in outages"*, and *"Certain Windows systems that were online when the
  update was released at 4:09 UTC on July 19 were affected."* This **confirms** the PRC
  breach date of 2024-07-19 rather than correcting it — a reclassification from
  NO_INDEPENDENT_DATE to genuine same-day, not a recovery.
- **Global Payments** (8-K filed 2012-06-12, item 8.01) references *"unauthorized access
  into a portion of its processing system"* but gives **no intrusion date**.
- The other 27 were debt offerings (AT&T, Altice, Comcast ×2, HP ×2, Verizon), M&A
  (Charter ×3, Paramount, Intuit/Credit Karma, HBO/Time Warner), earnings (Intuit ×2, Uber,
  Fiserv, Twilio), executive changes (Salesforce, Fox, Uber, Intuit), an FCPA settlement
  (IBM), a service-plan announcement (T-Mobile), a securitisation facility (Sinclair), a
  UK contract judgment (HP) and a stock-description update (Apple).

**Recovery rate from EDGAR: 0 of 29 (0%).** The reason is structural, not a screening
failure: most of these breaches affected a few hundred to a few thousand individuals and
were never 8-K material. For them **the PRC filing is the disclosure**, and there is no
second source to check it against.

## B3. What remains

After B1 (strict) and B2, the same-date events with no recoverable breach date are
**57 of 147 in `CANONICAL_V3`** (one of the 58 being CrowdStrike, now confirmed genuine),
**40 of 113 in Essay 1's regression sample**, **40 of 112 in Essay 2's**, and **46 of 125
in Essay 3 v4's** — and for those events no source in or reachable from this repository
establishes when the breach occurred.

---

# PART D — what "notification date" means

## D1. The definition, v3 and v4

**v3, Stage 3 (`scripts/152:91`)** — the firm-day collapse takes the minimum:

```python
'reported_date': g['reported_date'].min(),
```

**v3, Gate 2 (`scripts/153`)** — the chain collapse does **not** re-take the minimum. It
keeps `m.index[0]`, the earliest-*breach* component, rewriting `name_variants`,
`n_source_records`, `breach_type`, `multi_type`, `total_affected_max`, `multi_filing` and
`chain_note`, but not `reported_date` (`153:59-68`).

**Derived (`scripts/156:109-136`)**:

```python
ev['reported_dt'] = pd.to_datetime(ev['reported_date'], errors='coerce')
ev['disclosure_delay_days'] = (ev['reported_dt'] - ev['bdt']).dt.days
...
ev['immediate_disclosure'] = (ev['disclosure_delay_days'] <= 7).astype(float)
```
with the signed 8/17/2026 fixes: a delay below −30 days is a wrong-field record and is set
missing (`156:115-121`); a delay between −30 and 0 is field imprecision recoded to 0
(`156:125-131`); `immediate_disclosure` is missing wherever the delay is missing.

**v4 (`scripts/214:351`)**, under freeze exception 2:

```python
def fix_gate2_anchor(ev, rows, v3_breach):
    """reported_date := min(reported_date) across every source record of the chain."""
```

## D2. Freeze exception 2, and every re-anchored event

Quoted from `scripts/214:328-342`:

> FREEZE EXCEPTION 2026-09-24 (second), reason 1, logged in docs/claude/POST_DEFENSE.md
> BEFORE this change.
>
> Defect origin: scripts/153:59, which is v3 and FROZEN. Gate 2 collapses adjacent
> firm-day events by sorting on breach date and keeping m.index[0]. It rewrites
> name_variants, n_source_records, breach_type, multi_type, total_affected_max,
> multi_filing and chain_note on the surviving row - but NOT reported_date. The kept
> event therefore inherits the notification date of the earliest-BREACH component
> rather than the chain minimum, unlike Stage 3, where 152:91 takes
> g['reported_date'].min().
>
> scripts/153 and its outputs are in the v3 freeze manifest, so the defect is repaired
> HERE instead, as ordinary correction-ledger entries. The v3 vintage keeps its
> original anchor.

**v3 re-anchored nothing. v4 re-anchored 14 events**, from
`outputs/rebuild_v4/214_corrections.csv`:

| org | event breach | old `reported_date` | new | gap closed |
|---|---|---|---|---:|
| Frontier Communications Parent | 2024-04-13 | 2024-06-06 | 2024-06-05 | 1 d |
| Gray Television | 2016-08-08 | 2016-08-31 | 2016-08-30 | 1 d |
| Fidelity National Information Services | 2023-05-27 | 2023-08-11 | 2023-08-10 | 1 d |
| Intuit, Inc. | 2019-02-21 | 2019-03-12 | 2019-02-22 | 18 d |
| Intuit, Inc. | 2017-04-02 | 2017-04-17 | 2017-04-04 | 13 d |
| Intuit, Inc. | 2017-07-30 | 2017-08-15 | 2017-08-01 | 14 d |
| Intuit Inc | 2016-02-29 | 2016-03-16 | 2016-03-03 | 13 d |
| Intuit, Inc. | 2016-03-07 | 2016-04-01 | 2016-03-08 | 24 d |
| Intuit Inc. | 2017-02-28 | 2017-03-17 | 2017-03-02 | 15 d |
| Intuit Inc | 2016-03-29 | 2016-10-17 | 2016-06-13 | 126 d |
| IMA Financial Group | 2022-10-18 | 2023-07-06 | 2023-04-22 | 75 d |
| Sierra Pacific Industries | 2022-06-10 | 2023-01-11 | 2022-08-09 | 155 d |
| **DISH Network, LLC** | 2023-02-22 | 2023-05-15 | **2023-02-23** | **81 d** |
| GoDaddy.com LLC | 2019-10-16 | 2023-05-17 | 2020-05-03 | **1,109 d** |

Two further date corrections in the same ledger: **Carnival Corporation & PLC** 2019-04-01,
`reported_date` `2020-03` → missing (a month-truncated value the pipeline had completed to
`-01`); and **Sprint Nextel**, `breach_date` 2012-08-01 → 2009-01-01, the only breach date
v4 moves.

## D3. Is one rule applied to every event?

**No.** Three distinct departures, and they compound:

1. **Within v3, two different rules.** Stage 3 takes the chain minimum (`152:91`); Gate 2
   takes the earliest-breach component's date (`153:59`). **31 Gate-2 chained events** in
   `CANONICAL_V3` (9 treated, 22 control; 28 in each essay sample, 8 treated) carry a
   notification date chosen by a different rule from the other 458. v4 fixes 14 of them;
   v3 fixes none.
2. **The underlying field is not one quantity.** Across the DISH chain alone the seven
   source records' `reported_date` values are a state-AG filing date (Indiana 5/15,
   Maryland 5/16, California 5/18, Washington 5/18, Oregon 5/18), a **company self-report**
   date (DISH Security Team 5/08), and a **public-announcement** date (the curated record,
   2023-02-23). v4's "chain minimum" rule selected the last of those. No rule anywhere
   chooses among source types, so "notification date" means whichever of these happens to
   be smallest.
3. **For 151 events it is not a notification date at all** but a copy of the breach date
   (A1), or, in 2 cases, the reverse (A3's REPORTED_DATE_CORRUPTED).

---

# PART E — the specifications, counts only

*NEW — `tm_partE.py`, `tm_partE_cells.py`.* Specs 2, 3 and 4 remove events because the
timing variable each essay requires becomes missing. **Spec 5 removes nothing** — it
re-anchors, so its sample equals spec 1's; what changes is which 31 trading days are read.

| sample | spec | N | treated events | control | treated parent CIKs | treated parent entities |
|---|---|---:|---:|---:|---:|---:|
| `CANONICAL_V3` | 1 as it stands | 489 | 118 | 371 | 14 | 39 |
| | 2 MA same-date unknown | 366 | 81 | 285 | 14 | 33 |
| | 3 no independent date unknown | 342 | 72 | 270 | 13 | 31 |
| | 4 spec 3 + B1/B2 recoveries | 431 | 95 | 336 | 13 | 34 |
| | 5 re-anchored on first disclosure | 489 | 118 | 371 | 14 | 39 |
| Essay 1 regression | 1 | 340 | 106 | 234 | 12 | 36 |
| | 2 | 247 | 75 | 172 | 12 | 31 |
| | 3 | **227** | **67** | 160 | 11 | 29 |
| | 4 | 300 | 89 | 211 | 11 | 32 |
| | 5 | 340 | 106 | 234 | 12 | 36 |
| Essay 2 analytic | 1 | 333 | 104 | 229 | 12 | 36 |
| | 2 | 241 | 73 | 168 | 12 | 31 |
| | 3 | **221** | **65** | 156 | 11 | 29 |
| | 4 | 293 | 87 | 206 | 11 | 32 |
| | 5 | 333 | 104 | 229 | 12 | 36 |
| Essay 3 v4 analysis | 1 | 405 | 109 | 296 | 13 | 38 |
| | 2 | 300 | 77 | 223 | 13 | 32 |
| | 3 | **280** | **69** | 211 | 12 | 30 |
| | 4 | 359 | 91 | 268 | 12 | 33 |
| | 5 | 405 | 109 | 296 | 13 | 38 |

## Cells falling below 10 treated events

| cell | spec 1 | spec 2 | spec 3 | spec 4 |
|---|---:|---:|---:|---:|
| full sample, treated events (Essay 1) | 106 | 75 | 67 | 89 |
| firm-size **Q1** treated | **2** | **1** | **1** | **2** |
| firm-size **Q2** treated | 14 | 10 | **7** | **9** |
| firm-size Q3 treated | 31 | 23 | 23 | 31 |
| firm-size Q4 treated | 59 | 41 | 36 | 47 |
| `health_breach = 1` treated | **0** | **0** | **0** | **0** |
| pre-rule treated | **0** | **0** | **0** | **0** |
| treated parent CIKs | 12 | 12 | 11 | 11 |

**Three of these cells are already below 10 as it stands**, and no specification causes
that: firm-size **Q1** (2 treated), **`health_breach = 1`** (0 treated in v3; 2 in Essay 3
v4 after freeze exception 3, falling to 1 under specs 2–4), and **pre-rule** (0 treated —
the structural fact that makes the design cross-sectional).

**The one cell the specifications newly break is firm-size Q2**, which falls from 14
treated to **7 under spec 3** and **9 under spec 4**. Since the quartile panels are what
Essay 2's spec grid estimates, specs 3 and 4 put two of its four size cells below 10
treated events. Specs 1 and 2 leave Q2 at 14 and 10.

No specification takes the full-sample treated count below 10 in any essay, and treated
parent CIKs stay at 11–14 throughout — but 11 treated clusters is already the binding
constraint on the CV3 and bootstrap inference, not the event count.

---

# PART F — the DISH fold, and the other duplicates

## F1. What would have to change (no edits made)

**In v3 — every one of these files is inside the freeze manifest, so this needs a v3 freeze
exception, which the Stage 2 ruling routes through `docs/claude/V3_FREEZE_EXCEPTIONS.md`
with a pinned old and new hash per file:**

| step / file | why it changes |
|---|---|
| `scripts/152_rebuild_s3_dedup.py:110-125` | the ≤3-day adjacency window is what keeps the two events apart; folding needs either a wider window or a signed manual chain |
| `outputs/rebuild/GATE2_ADJACENCY_SHEET.csv` / `.md` | CH-22 gains a third member, or a new chain is declared |
| `scripts/153_rebuild_gate2_apply.py` | the signed collapse list and `chain_note` |
| `Data/processed/rebuild/stage3_events.csv` | unchanged in row count (3 firm-days) but the chain assignment changes |
| `Data/processed/rebuild/CANONICAL_V3.csv` (`scripts/156`) | 489 → 488 events |
| `Data/processed/rebuild/stage5_outcomes.csv` (`scripts/155`) | one fewer event, one fewer `car_30d` |
| **`scripts/155` I2 tripwire** | asserts 489 / 356 / 111 — **would fire** |
| **`scripts/156` I2 tripwire** | asserts 489 / 118 / 356 / 14 — **would fire** |
| `outputs/rebuild/constants_v3.json` (`scripts/158`) | the rebaseline |
| `outputs/rebuild/appendix_v3/*` (`158`, `160`) | 16 tables |
| `scripts/163`, `scripts/165` I2 tripwires | assert N = 333 / 104 / 82 — **would fire** |
| `outputs/tables/essay2_v2/*` (61 files) | the Essay 2 chain |
| `scripts/247` + `outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md` | every chain count |
| `outputs/rebuild/stage7_*` (`scripts/157`) | verification outputs |

**In v4 — the fix site is `scripts/214`, as with every other repair, so v3 stays frozen:**

| step / file | why |
|---|---|
| `scripts/214_corrections_v4.py` | a new correction-ledger entry folding the event |
| `outputs/rebuild_v4/214_corrections.csv` / `.md` | the ledger row |
| `Data/processed/rebuild_v4/CANONICAL_V4.csv` | 489 → 488 |
| `scripts/219`, `234`, `230`, `235` | covariates, outcome CIK, fetch scope |
| `scripts/220` scope, `224` sample E, `227` estimation, `229` SEs | 405 → 404, 109 → 108 treated events |
| `outputs/essay3_v4/constants_essay3_v4.json` | the assertion baseline |
| `scripts/239`, `242`, `243`, `244`, `246`, `245` | side-by-side, pulls, tables, appendix |

**The freeze exception it would require: a fourth one.** `docs/claude/POST_DEFENSE.md`
currently records three (2026-09-24, 2026-09-24 second, 2026-09-25 third). This fold is the
same shape as the second: the defect originates in frozen v3 code (`152`'s adjacency
window), so it would be logged **before** any code change and applied in `214`.

## F2. The other duplicates

*NEW — `tm_partFG.py`.* Of the **89** strict B1 matches in `CANONICAL_V3`:

- **79 are the DISH pattern** — the sibling record is itself a separate canonical event, so
  one incident has been split into two events. **19 treated, 60 control, across 26 distinct
  parent CIKs.**
- 10 are not duplicates: the sibling record is already inside the same event's collapsed
  set.

The pattern is concentrated: **Intuit 20 events, Sirius XM 7, Uber 5, Fidelity National
Information Services 6, T-Mobile/Sprint 8, Verizon 4, AT&T 3**, with notification gaps as
small as 0 days. DISH is one case of 79, not a special one.

This is the same phenomenon `ESSAY2_QUERY6_REPORT.md:18-22` flagged for the T-Mobile
August 2021 incident — three canonical events from one incident — described there as *"the
records-vs-events problem in miniature, from the essay's own focal case."* It is not in
miniature: on the strict criterion it touches 79 of 489 events.

---

# PART G — the Compustat/CRSP top-up

## G1. Why v4 refused each of the 20, resolved per event

*NEW — `tm_partG1.py`.* **This corrects the Part N4 finding in
`outputs/RUN_ALL_FOLLOWUP_REPORT.md:825-830`.** N4 said 6 events had no gvkey and *"14 have
a gvkey but no CUSIP"* in the committed `comp_security` extract, and that **none** of the
20 was an identity-gate rejection. Walking the path against the committed extracts shows
both halves of that are wrong: the CUSIPs are present, and five refusals **are** at the
gate.

| org | event | CIK | permno 155 assigned | gvkey | stage that fails | what is missing |
|---|---|---|---|---|---|---|
| Aon Corporation PLC | 2020-12-29 | 1808065 | 61735 | — | 1 CIK→gvkey | CIK absent from `comp_company` |
| Aon PLC | 2022-02-25 | 1808065 | 61735 | — | 1 CIK→gvkey | same |
| Google, Inc. | 2008-06-27 | 1288776 | 90319 | — | 1 CIK→gvkey | same |
| Paramount | 2023-01-01 | 813828 | 76226 | — | 1 CIK→gvkey | same |
| Paramount Global | 2023-08-10 | 813828 | 76226 | — | 1 CIK→gvkey | same |
| The Walt Disney Company | 2008-07-29 | 926480 | 26403 | — | 1 CIK→gvkey | same |
| Honeywell International Inc. | 2021-02-16 | 773840 | 10145 | 1300 | 3 CUSIP→permno | **no `crsp_stocknames` row** for CUSIPs 43851613 / 43851620 / 43856Q10 |
| Honeywell International, Inc. | 2023-05-27 | 773840 | 10145 | 1300 | 3 | same |
| Honeywell International Inc. | 2023-06-03 | 773840 | 10145 | 1300 | 3 | same |
| Carnival Corporation | 2020-12-25 | 815097 | 75154 | 13498 | 3 | resolves to permno **89728** (the UK twin) — Compustat's primary issue is the G-prefix CUSIP `G2004J103` |
| Carnival Corporation | 2021-03-19 | 815097 | 75154 | 13498 | 3 | same |
| Yahoo! Voices | 2012-07-11 | 1011006 | 83435 | 62634 | 3 | resolves to permno **16752** (Altaba, the successor) |
| Yahoo! Inc. | 2013-08-01 | 1011006 | 83435 | 62634 | 3 | same |
| Yahoo | 2014-12-01 | 1011006 | 83435 | 62634 | 3 | same |
| Yahoo Inc. | 2016-08-13 | 1011006 | 83435 | 62634 | 3 | same |
| Aon Corporation | 2020-12-17 | 315293 | 61735 | 3221 | **5 identity gate** | nothing — the path reaches permno 61735, valid at the date |
| CyrusOne, Inc. | 2017-10-18 | 1553023 | 13752 | 16116 | **5 identity gate** | nothing |
| Essex Property Trust, Inc. | 2013-08-13 | 920522 | 80681 | 30293 | **5 identity gate** | nothing |
| Nokia Inc. | 2013-07-22 | 924613 | 87128 | 23671 | **5 identity gate** | nothing |
| Seagate Technology LLC | 2017-07-08 | 1137789 | 89641 | 150937 | **5 identity gate** | nothing |

**Counts: 6 fail at CIK→gvkey, 9 at CUSIP→permno, 5 at the identity gate.** Only **9** of
the 13 correct-but-refused links are a data-coverage problem; **4** of them (Essex, Nokia,
Seagate, CyrusOne) resolve correctly all the way to the right permno at the right date and
are refused by the gate itself.

## The WRDS queries that would supply what is missing (nothing pulled)

**(a) The 6 CIK→gvkey failures** — four CIKs: 1808065 (Aon PLC), 1288776 (Google), 813828
(Paramount), 926480 (Disney).

```sql
SELECT gvkey, conm, cik, sic, naics, fic, costat, ipodate
FROM   comp.company
WHERE  cik IN ('0001808065','0001288776','0000813828','0000926480');
```
Library `comp`, table `company`, key `cik` (zero-padded to 10 characters, as it is stored).
Append to `Data/wrds_v4/comp_company_topup_<UTC timestamp>.csv`, matching the existing
top-up naming.

**(b) The 3 Honeywell failures** — the gap is in CRSP, not Compustat, so the top-up is on
`crsp.stocknames` keyed by permno rather than by CUSIP:

```sql
SELECT permno, permco, namedt, nameenddt, cusip, ncusip, ticker, comnam, shrcd, exchcd
FROM   crsp.stocknames
WHERE  permno = 10145;
```
That returns Honeywell's full name history and the NCUSIP series the CUSIP join needs. The
companion Compustat side, to see every issue rather than only the primary:

```sql
SELECT gvkey, iid, tic, cusip, isin, sedol, excntry, secstat, tpci, dldtei
FROM   comp.security
WHERE  gvkey = '001300';
```

**(c) Carnival and Yahoo need no pull.** Both already resolve — to permno 89728 and 16752
respectively. These are **issue-selection** decisions, not coverage: Compustat's primary
issue for Carnival is the Panama-domiciled twin (`G2004J103`) while 155 used the US-listed
CCL (75154), and Yahoo's gvkey now carries Altaba's CUSIP. Pulling more rows will not
resolve either; a rule choosing among issues will — for example, preferring `iid = '01'`
with `excntry = 'USA'` and a non-`G` CUSIP, and requiring the CRSP name interval to cover
the event date, which would reject Altaba for the 2012–2016 Yahoo events.

**(d) The 5 identity-gate refusals need no pull either.** They are a rule question: the
gate at `212:39-44` accepts `cusip_header` only when the CRSP `comnam` valid at the breach
date token-matches the PRC organisation or EDGAR name. "ESSEX PROPERTY TRUST INC",
"NOKIA CORP", "SEAGATE TECHNOLOGY PLC" and "CYRUSONE INC" all token-match their PRC
strings, so the refusal is worth re-reading before any data is bought.

---

# Close

**1.** In Essay 1's regression sample, **8** of the 124 events coded
`immediate_disclosure = 1` reflect a documented disclosure within seven days (delays of 0,
0, 2, 3, 3, 3, 3 and 7 days), while **113** are same-date records with no independent
breach date — 93 of them Massachusetts filings — and the remaining 3 are same-date records
of the other classes.

**2.** **73 of Essay 1's 113** same-date events without an independent breach date can be
given a recovered date (89 of 147 in `CANONICAL_V3`, 72 of 112 in Essay 2, 79 of 125 in
Essay 3 v4), every one of them from a sibling PRC record under the strict same-wave
criterion, and **none** from EDGAR — 29 filings were fetched and 0 yielded an incident
date.

**3.** **128 of Essay 1's 340 events — 38%, including 42 of its 106 treated events — have a
`car_30d` window that closes before the notification date** (207 of 489 in `CANONICAL_V3`,
165 of 405 in Essay 3 v4), and for Essay 2 the mirror holds: its pre-window reaches back to
the breach date in 0 of the 122 genuine-gap cases.

**4.** **No.** v3 applies the chain minimum at Stage 3 but the earliest-breach component's
date at Gate 2, so **31 events** in `CANONICAL_V3` (9 treated / 22 control; 28 in each
essay sample) depart from the documented rule — v4 repairs 14 of them and v3 none — and
beneath that the field itself mixes state-filing, self-report and public-announcement
dates with no rule choosing among them, while for 151 events it is simply a copy of the
breach date.

**5.** **Yes, one.** Firm-size **Q2** falls from 14 treated events to **7 under
specification 3** and **9 under specification 4**, which puts it below 10 in the quartile
panels Essay 2's spec grid estimates; firm-size Q1 (2 treated), `health_breach = 1` (0 in
v3) and the pre-rule cell (0 treated) are already below 10 as the samples stand, under
every specification including the status quo.
