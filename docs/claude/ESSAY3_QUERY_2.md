# Essay 3 — Query 2: Build Executive Turnover, Then Re-estimate H6

Companions (commit these to `claude/` before running; the directory does not exist yet):
`claude/ESSAY3_PRE_RERUN_AUDIT.md`, `claude/ESSAY3_QUERY_1.md`, `claude/ESSAY3_QUERY_2.md` (this file).
Prior report: `outputs/ESSAY3_QUERY1_REPORT.md` (commit 74c7a3d).

> Placement note (2026-09-11): per Tim, the companions live in `docs/claude/` (root stays clean), and nothing is committed until Tim explicitly says so. `ESSAY3_PRE_RERUN_AUDIT.md` was not supplied.

This query runs in two stages with a hard stop between them. **Stage 1** builds the outcome and a blind validation sheet, then stops. Tim hand-codes the sheet. **Stage 2** estimates only after the classifier is frozen and validated.

---

## PART 0 — Standing rules

All Query 1 rules carry forward:
- Report what you find.
- Print already-emitted values verbatim with file and line.
- Label new computations NEW.
- Do not edit existing scripts or prose unless a Part below says so.
- New scripts get the next free number with an `essay3_q2_` prefix.
- Output `outputs/ESSAY3_QUERY2_REPORT.md`, committed with `git add -f`.

Additional rules:
- **No estimation of H6 on the new outcome until Part D is complete and the classifier commit hash is recorded.** No classifier change after Tim's codes are seen, except through the revision rule in D3.
- **Every sentence citing a treated N names its sample level.** "Organizations" means parent entities (parent CIKs), not distinct `org_name` strings. Report name-string counts only if labeled as such.
- **Do not rebaseline `constants_v3.json`.** Report what would change; Tim decides.

## Decisions locked for this run

| # | Decision | Setting |
|---|---|---|
| L1 | Outcome | **Primary:** departure of an executive officer reported under Item 5.02(b) (principal executive officer, president, principal financial officer, principal accounting officer, principal operating officer, or named executive officer). **Secondary:** CEO (principal executive officer) departure only. **Reported separately, not an outcome:** director-only departures. Appointments, elections, and compensation items are not turnover. |
| L2 | Event anchor | **Primary t0 = `reported_date`** (public notification). Sensitivity: `breach_date` (occurrence). |
| L3 | Mediator | `immediate_disclosure` is removed from the H6 model. No mediation analysis. |
| L4 | Equivalence | No TOST and no equivalence claim. Report CIs and MDEs. |
| L5 | Validation | Tim hand-codes blind; agreement is reported whatever it is. |

---

# STAGE 1

## PART A — Chain and treatment reconciliation (quick, blocking for Part H)

### A1. Which chain does each essay's authoritative output come from?
For Essay 1 (`outputs/ESSAY1_APPENDIX_TABLES_FORM499.md`, `outputs/SAMPLE_ATTRITION_LEDGER.md`), Essay 2 (`ESSAY2_APPENDIX_TABLES_FORM499.md`, `ESSAY2_SAMPLE_ATTRITION_LEDGER.md`), and Essay 3 (v3 constants), state:
- the chain (7/28 or v3);
- the regression N;
- treated events, parent entities, and parent CIKs.

Query 1 found the Essay 1 regression sample equal to Essay 3's 340 within v3. The project instructions carry Essay 1 as 1,054 → 784 → 779 → 672 → 648 with 115 treated. Which is Essay 1's authoritative appendix built on? Print the first lines of each ledger verbatim.

### A2. DISH
Essay 2's settled state lists DISH as excluded by the project's adjudication. Query 1 D2 lists DISH Network, LLC (CIK 1001082) as treated with 2 events at the Essay 3 regression level, added by the 9/4 top-up. Quote the adjudication record for DISH. Is DISH treated, excluded, or treated in one essay and excluded in another? Report every essay's DISH status.

### A3. Effect of the DISH top-up on every essay
For each essay's committed constants: which values change on today's CANONICAL_V3, and by how much. Print old and new side by side. No rebaselining.

### A4. Does anything outside the legacy Essay 3 chain read script 46 or script 53 outputs?
List every consumer of `Data/enrichment/executive_changes*.csv` and `…DEDUPLICATED_ENRICHED.csv`, especially any Essay 1 or Essay 2 script. This decides whether Part H can retire them.

## PART B — Fetch the filing text

### B1. Scope
For every parent CIK in the Essay 3 regression sample, collect every 8-K or 8-K/A whose `items` lists 5.02 and whose filing date falls in `[min(breach_date, reported_date) − 365d, reported_date + 180d]`. The pre-window supports the placebo in F4 and the baseline rate in F2.

Fetch each primary document from the addresses already in the v3 cache. For any filing the classifier later codes as a CEO departure, also fetch the EX-99 exhibits via `{accession}-index.json`.

### B2. Storage
Save under `Data/edgar/item5_02_text/`, **tracked** (not gitignored, not LFS unless over the size limit). Reuse the 35 T-Mobile and 50 calibration documents already on disk. Log the counts: filings in scope, fetched, reused, failed.

## PART C — Classifier (deterministic rules, no ML)

### C1. Parse
Strip the Item 5.02 caption ("Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers") and any repeated boilerplate. Isolate the Item 5.02 section. Where the filing labels sub-items ((b), (c), (d), (e)), use the labels. Where it does not, classify from the text.

### C2. Code one row per filing, with one sub-row per person named
- Person and title as stated.
- Role class: CEO / president / CFO / COO / PAO / other NEO or executive officer / director only.
- Action: departure / appointment / election / compensation only.
- **Dates:**
  - the filing date;
  - the notice date stated in the text ("On [date], X notified…");
  - the stated effective date.
  - The outcome date is the **filing date**. The others are recorded.
- **Context flags** (from text; descriptive only): retirement, health, transaction or merger, termination or "without cause", severance or release, "no disagreement", **pre-announced** (the text references an announcement, agreement, or notice dated before t0).

### C3. Outcome variables
At 30, 90, and 180 days after t0, on both anchors:
- `exec_departure_{w}` (L1 primary);
- `ceo_departure_{w}` (L1 secondary);
- `director_departure_{w}` (descriptive);
- `any_502_{w}` (the old v3 outcome, kept for the crosswalk).

Also record `days_to_first_exec_departure`.

### C4. Crosswalk
Print the base rates, treated and control, for all four outcomes at each window, next to v3's any-5.02 rates. How many any-5.02 events are not executive departures?

### C5. Freeze
Commit the classifier. Record its hash in the report.

## PART D — Blind validation sheet, then STOP

### D1. The sheet
Use the 50 documents in `outputs/rebuild/calibration_5_02/` plus 30 filings drawn at random (stated seed) from the Part B set that are not in the calibration 50. Randomize the order.

For each filing, give: the URL, the Item 5.02 section text with the caption stripped, and blank columns for Tim to fill:
- executive officer departure (Y/N);
- CEO departure (Y/N);
- director-only departure (Y/N);
- person and role;
- pre-announced (Y/N/unclear).

The classifier output goes in a separate file that Tim does not open until he has finished coding.

Write the sheet to `outputs/essay3_q2/VALIDATION_SHEET.xlsx` and the hidden answers to `outputs/essay3_q2/validation_classifier_HIDDEN.csv`.

### D2. STOP
End Stage 1 here. Report Parts A–C and confirm the sheet exists.

### D3. After Tim codes (start of Stage 2)
- Report agreement and Cohen's kappa for each coded field.
- List every disagreement with the text excerpt.
- **Revision rule:** if the classifier is revised, it must be revalidated on a fresh random draw of 30 that Tim also codes blind. Report both rounds.

---

# STAGE 2 (only after D3)

## PART E — Sample

### E1. Outcome-data requirement
An event enters only if its resolved CIK filed at least one 8-K of any kind in `[t0 − 730d, t0 + 180d]`.
- Resolve the four structural zeros from Query 1: Nokia 924613, Disney 926480, Aon 1808065 ×2. Is each a CIK-vintage mismatch? Name the correct filer CIK if one exists. Fix the mismatch or exclude the event, and state which.
- Report how many events this requirement removes, treated and control.

### E2. Ledger
Rebuild the Essay 3 attrition ledger from 1,054 records, with the outcome-data requirement as its own line and a closing check.

Report treated events, parent entities, and parent CIKs at every level. Report pre-rule counts under the December 8, 2007 effective date, treated and control.

### E3. Anchor diagnostic
Report the share of events whose occurrence-anchored 180-day window ends before `reported_date`, treated and control. These are windows in which every departure predates public disclosure.

## PART F — Estimation

### F1. Primary
`exec_departure_{30,90,180}` on `fcc_form499` plus `prior_breaches_1yr, health_breach, firm_size_log, leverage, roa`, the baseline rate from F2, and **prior 12-month market-adjusted stock return** ending t0 − 1 (from the committed CRSP daily file; the standard performance control in the turnover literature, pre-specified here). Notification anchor.

Estimate by LPM, reported as an inference ladder, as in Essay 2:
- HC3;
- CV1;
- CV3;
- restricted wild cluster bootstrap (Rademacher, B = 99,999, CI by inversion).

Cluster on parent CIK. Report G, treated clusters G₁, effective clusters G* (full CSS formula on treatment partial leverage), and cluster-size CV.

A logit AME serves as corroboration. Compute the MDE at 80% power from the CV3 standard error.

### F2. Baseline departure rate (pre-specified control)
The firm's own executive-departure count in `[t0 − 730d, t0 − 181d]`, scaled per year. This addresses the mechanical concern that large firms with more NEOs file more departures. Report its distribution, treated and control.

### F3. Sensitivities (each as a single row against the primary)
- Year fixed effects.
- Two-digit SIC fixed effects (report the cell composition; Query 1 found 101 of the 106 treated events in SIC 48 alongside 24 controls).
- The `breach_date` anchor.
- Excluding pre-announced departures.
- Excluding the F2 control.
- Leave-one-parent-CIK-out: report the range and the number of sign flips, and **name the T-Mobile and Sprint deletions specifically**.

### F4. Placebo
The same primary specification with the outcome measured in `(t0 − 180d, t0]`, before public notification.

### F5. CEO-only
Report event counts, treated and control, at each window. Estimate the LPM with CV3 only if both groups have at least 10 events at that window; otherwise report the counts alone and state why.

### F6. Director-only
Descriptive counts only.

## PART G — T-Mobile (the case thread)

Everything in this Part is **print, do not interpret**. It runs on CIK 1283699 (T-Mobile US; MetroPCS before 2013-04-29) and, where marked, on Sprint (CIK 101830), since Sprint's events are treated in their own right and two post-merger Sprint events sit on the T-Mobile CIK. **G1–G5 are data collection and run in Stage 1. G6 runs in Stage 2.**

### G1. Weight of T-Mobile in the treated set
At every sample level, give T-Mobile's events as a share of treated events. Give the same for T-Mobile plus Sprint combined. Query 1 D2 gives 26 of 106 at the Essay 3 regression level for T-Mobile alone. Confirm this on the Stage 2 sample.

### G2. How each T-Mobile breach reached the public
For each T-Mobile event, list:
- every 8-K in `[reported_date − 30d, reported_date + 30d]`, with the items listed;
- for any 8-K listing 7.01, 8.01, or 1.05, the text passage describing the incident (e.g., the January 2023 incident);
- whether the PRC source record is a state-AG filing, a press release, or other (from `stage2_signed`).

The result is one row per event: disclosure channel, the 8-K accession where one exists, and the days between the 8-K and `reported_date`.

### G3. Who controls the board (DEF 14A, every proxy 2013–2025)
Pull every DEF 14A for CIK 1283699. From each, print:
- **Controlled-company status.** Any "controlled company" statement, the majority holder named, and the stated ownership percentage.
- **Director roster.** Each director, whether independent, and whether affiliated with Deutsche Telekom, SoftBank, or another holder, as the proxy states it.
- **Committees.** Any committee whose charter or description mentions cybersecurity, privacy, or information security, with the first proxy in which each such mention appears.
- **CD&A.** Every passage mentioning "cyber," "breach," "security incident," "data," or "privacy," and any statement that an incident affected any executive's bonus, PRSU, or other pay.

### G4. What T-Mobile told investors about the breaches (10-K and 10-Q)
For every 10-K and 10-Q filed from 2013 onward:
- risk-factor and legal-proceedings passages mentioning a cyberattack, a breach, or a named incident;
- any stated charge, settlement, reserve, or committed security spending tied to an incident, with amount and filing;
- **10-K Item 1C (fiscal 2023 onward):** the named CISO or equivalent role, whom that role reports to, and the board committee assigned oversight. Item 1C is the only filing route that can name security leadership, and it partly fills the 5.02 blind spot.

### G5. Sprint's Item 5.02 record
Run Query 1 E2, with the Part C codes and flags, for Sprint (CIK 101830) events in the Essay 3 sample, through the April 1, 2020 merger close.

### G6. Case table on the notification anchor (Stage 2)
Rerun Query 1 E2 for T-Mobile on the **notification anchor**, with the Part C codes and flags. For each executive departure in any window, give:
- the text excerpt;
- the context flags;
- whether the person was a controlled-holder affiliate (from G3);
- for the King (2016-02-19) and Legere-to-Sievert (2020-04-01) filings, the EX-99 press-release excerpt.

For the 2019-11-26 event, state the dates of the Sievert employment agreement and of any earlier public announcement of the CEO succession, relative to that event's `reported_date`. Part B's pre-window should capture the announcement filing.

Put G2, G3 (summarized by proxy year), G4, and G6 on **one dated timeline** (`outputs/essay3_q2/tmobile_timeline.csv`): breaches, public disclosures, executive and director departures, committee changes, compensation statements, charges, and settlements.

### G7. What this Part does not do
- No T-Mobile-only regression.
- No selection of T-Mobile events for narrative fit; every event is reported.
- No web sources. EDGAR and the committed pipeline data only. Regulatory actions (FCC consent decrees) come from Tim's own sources, not this query.

## PART H — Pipeline hygiene (only after A4 confirms no non-Essay-3 dependency)

- Remove the legacy Essay 3 scripts from `run_all.py` (91, 91b, 91c, 91e, 91f, 91g, 91h, 91j, 91k, 91m, 91_mediation, the Essay 3 portions of 97 and 102, and 96's hardcoded turnover constant). Also remove script 46 if A4 allows.
- Record each removal in `outputs/RETIREMENT_LEDGER.md`: script, reason, last output, and the commit that retired it.
- Remove 91m from `critical_keys`. Remove the run_all:355 label "confirms FCC effect is economically negligible".
- Mark every hardcoded 16.71 and 14.52 string (161, the legacy appendix builders) as retired. The v3 exhibit must not print a first stage that has no computed source.
- Add the new Essay 3 scripts to `run_all.py` in chain order, with assertions against their own emitted outputs.

## PART I — Tests

Count every hypothesis test in the new Essay 3 code. Apply Benjamini–Hochberg within these families: primary H6 (3), sensitivities, placebo, CEO-only. Report adjusted values beside raw values.

---

## Report back

**Stage 1:** A, then B, then C, then G1–G5, and confirm D1. Stop.

**Stage 2:** D3 first. Then F1, F4, E, F2–F3, F5–F6, G6 and the timeline, H, I.

Close Stage 2 with three sentences:
1. At each window, is executive departure higher for treated events, under the CV3 and wild-bootstrap rungs, and what is the MDE?
2. Does the pre-disclosure placebo show the same treated–control gap?
3. How many T-Mobile executive departures within 180 days of notification carry a pre-announced, retirement, or transaction flag, out of how many total?
