# Essay 3 v4 — post-freeze change rule

Tagged `essay3-v4-final`. The Essay 3 pipeline is frozen at that tag.

## The rule

The pipeline changes for **two** reasons, and nothing else:

1. **A committed output is factually wrong AND the error changes essay text.** Both
   halves are required. An output that is wrong but changes no sentence in the essay is
   recorded here, not fixed.
2. **A committee request.**

Any change made under either reason is recorded in the log at the bottom of this file
with the reason, the commit, and what essay text it moved.

## Why the rule is this narrow

The work that gives these results their standing is ordering: the classifier frozen
before its draw, the reference codes committed before the classifier ever ran on them,
the analysis plan committed before estimation. Each of those is provable only because
git history fixes the order. Re-running a stage after the fact does not just risk a
different number — it retrospectively weakens what the ordering demonstrates, and no
later commit can restore it.

So the default is: **do not touch it.** Read the number from the artefact instead.

## What is explicitly NOT a reason to change the pipeline

Everything here is either already true of the outputs, already documented, or is a
preference that costs more than it is worth.

- **A number reads oddly, or differs from v3.** v3 and v4 differ in sample and clustering
  by construction. Read `outputs/essay3_v4/239_v3_vs_v4_constants.csv`; the verdicts are
  in `239_verdict_table.csv` and none of them differ.
- **A point estimate is unstable to one cluster deletion.** That is a finding, not a
  defect. `f3_loco.csv`.
- **The estimates are null and underpowered.** Also a finding. The MDE exceeds the
  control base rate at two of three windows; that belongs in the results section, not in
  a new specification.
- **A different specification "would be better".** The plan is frozen
  (`ANALYSIS_PLAN_V4.md`, sha recorded). A new specification is a new study, not a fix.
- **Wanting more validation documents, a redraw, or another verification pass.** The draw
  and its two superseded predecessors are recorded in
  `outputs/rebuild_v4/231_validation_draws.md`. Redrawing now is not blind.
- **Four validation rows remain unsettled.** They are reported as bounds
  (`238_new_document_bounds.csv`). Bounds are the honest answer; resolving them post hoc
  is not.
- **CEO-only was not estimated.** Its ≥10-per-group gate was pre-specified and failed.
  Relaxing it now is a specification change.
- **`pre_announced` agreement on the full pool is mechanical.** Already labelled as such
  in `238_scoring.md`. Do not re-engineer the draw to make the number prettier.
- **The recall correction uses v3's audit.** Declared in the plan before estimation, with
  its assumption stated. Running a v4 audit now would require a fresh blind round.
- **`228` reads six v3 T-Mobile case files.** Declared; they describe one firm's
  governance and do not vary with the event set.
- **Cosmetic changes**: log wording, column order, file names, formatting, docstrings.
- **Re-running a stage to "confirm" it.** `227` asserts against the constants it first
  wrote and `229` independently recomputes the SEs; both already pass. A re-run that
  changes nothing still rewrites timestamps and muddies the history.
- **Merging `rebuild-v4` into `main`.** Not part of this work.

## If a change does qualify

1. Say which of the two reasons applies, and for (1) name the essay sentence that moves.
2. Make the smallest change that fixes it.
3. `scripts/217` all-pass and `scripts/210` PASS **run after staging**.
4. `scripts/240_methods_toolkit_v4.py check` must still pass.
5. Re-run only what the change actually invalidates, in the order in
   `REPRODUCE_ESSAY3_V4.md`.
6. Append to the log below and re-tag with a new suffixed tag. **Do not move
   `essay3-v4-final`** — the tag is the evidence of what was frozen and when.

## Exception 2026-09-24 — what was decided before touching code

- **Source.** `Data/wrds_v4/comp_funda.csv` carries **no `sich`** (the 219 pull requested
  only `at, lt, ni, sale, cogs, xsga` plus keys), so the point-in-time Compustat SIC is
  not available without a new WRDS pull. The header SIC already on disk is used instead:
  **`Data/wrds_v4/comp_company.csv`, column `sic`**, keyed on `final_cik`.
- **Coverage.** 400 of the 405 analysis events have one. The 5 without (all control) get
  their own `sic2 = 'unclassified'` cell. **No fallback to the inherited `sic`.**
- **Known limitation, recorded now rather than discovered later.** A header SIC is
  current-state, not point-in-time, so a firm that changed industry classification after
  its breach is labelled by its later industry. That is a weaker instrument than `sich`
  would be, and it is accepted here rather than triggering a new pull.
- **`scripts/199` is NOT edited.** It is v3 and outside `scripts/210`'s allowlist; the v3
  vintage keeps the inherited-SIC behaviour it always had.

## Exception 2026-09-24 (second) — the Gate-2 notification anchor

**Defect origin: `scripts/153:59` — v3, frozen, and left unchanged.** Gate 2 collapses
adjacent firm-day events by sorting on breach date and keeping `m.index[0]`; it rewrites
`name_variants`, `n_source_records`, `breach_type`, `multi_type`, `total_affected_max`,
`multi_filing` and `chain_note` on the surviving row, but **not `reported_date`**. So the
kept event inherits the notification date of the earliest-*breach* component rather than
the chain minimum — inconsistent with Stage 3, where `152:91` takes
`g['reported_date'].min()`.

`scripts/153` and its outputs (`stage4_input.csv`, `CANONICAL_V3.csv`) are in the v3
freeze manifest and outside `scripts/210`'s allowlist. Editing or re-running it would
change v3's canonical event table, which no Essay 3 v4 exception authorises. **The v3
vintage therefore keeps its original anchor**, consistent with exception 1 leaving
`scripts/199` on the inherited SIC.

**Fix site: `scripts/214`**, as correction-ledger entries with old/new/evidence for each
of the 12 events, alongside the Sprint, Carnival and CIK corrections already there. The
correction becomes visible in `214_corrections.csv` rather than silent inside a v3
collapse.

**Reason 1.** Essay text moved: the methods define the notification date as the earliest
reported date among an event's records. 12 analysis events (3 treated, 9 control) are
anchored later than their earliest notification, every one of them Gate-2 chained, with
gaps from 1 to 1,109 days. Two treated outcomes depend on it — **DISH Network 90d** and
**GoDaddy 180d** — and in both the later anchor is the one that records a departure, so
the defect runs in the direction of finding more treated turnover.

**Scope.** `reported_date` feeds the outcome windows, so everything downstream of it is
re-run: 234 (outcome_cik windows), 233, 230, 235, 232, 224, 227. Constants are updated
only through 227's own write.

## Exception 2026-09-25 (third) — the health-information indicator

**Defect origin: `scripts/152:93` and `scripts/153:62–71` — v3, frozen, and left
unchanged.** `health_breach` is derived at `scripts/156:144–146`:

```python
ia = ev['information_affected'].astype(str).str.contains('medical|health', case=False, na=False)
ot = ev['organization_type'].astype(str).str.upper().eq('MED')
ev['health_breach'] = (ia | ot).astype(int)
```

That reads **one** `information_affected` per event. Stage 3 picks it at `152:93` as the
value of the single source record with the **longest string**
(`g.loc[g['information_affected'].astype(str).str.len().idxmax(), ...]`) — not a union
across the firm-day's records. Gate 2 then collapses adjacent firm-day events at
`153:62–71`, rewriting `name_variants`, `n_source_records`, `breach_type`, `multi_type`,
`total_affected_max`, `multi_filing` and `chain_note` on the survivor, but **not**
`information_affected`. So an event whose health mention sits in a shorter record of the
same firm-day, or in another chain component, is coded 0.

`scripts/152`, `scripts/153` and their outputs are in the v3 freeze manifest and outside
`scripts/210`'s allowlist. **The v3 vintage keeps its original values**, consistent with
exception 1 leaving `scripts/199` on the inherited SIC and exception 2 leaving
`scripts/153`'s anchor alone.

**Fix site: `scripts/214`**, as correction-ledger entries with old/new/evidence, applied
to all 489 canonical events under the same regex, case-insensitive, over **every** source
record of the event.

**Reason 1.** Essay text moved: the methods define the indicator as any record describing
health data. **Five of the 405** analysis events mention health in a source record but
carry `health_breach = 0`:

| event | treated | why it was missed |
|---|---|---|
| DISH Network, LLC 2023-02-22 | **treated** | Gate-2 chain CH-22; mention is in the 2023-02-23 component |
| Altice USA 2024-02-29 | **treated** | Gate-2 chain CH-32; mention is in the 2024-03-01 component |
| ABM Industries 2018-01-08 | control | same firm-day; health record len 1074 lost to a 1241-char record |
| Wabtec Corporation 2022-03-15 | control | same firm-day; health record len 1286 lost to a 1295-char record |
| Okta, Inc. 2023-09-23 | control | same firm-day; three health records len 1002 lost to a 1127-char record |

A sixth event, **IMA Financial Group 2022-10-18** (control, Gate-2 chain CH-31, mention in
the 2022-10-19 component), is in the 489 but not in the 405; it is corrected too, and
recorded here.

The error is strictly one-directional. Of the 24 events currently flagged 1, **all 24**
survive an `"Affected":"Yes"`-only reading of the CCPA-style JSON in
`information_affected` — none is flagged by text inside a category marked `"No"`, and none
falls back to an unparseable blob. So the indicator under-counts and never over-counts.

**Why it matters beyond five rows.** `health_breach = 1` currently has **zero treated
events** in every sample — 489, 405, and Essay 2's N = 333. DISH and Altice are the only
treated events anywhere in the chain whose source records mention health, so the empty
treated cell is an artefact of this defect, not a property of the data.

**Scope.** `health_breach` is a control in the F1 primary, the placebo, F2 and every
sensitivity (`227:80` `BASE`), so `224`, `227` and `229` are re-run in full. It is **not**
an outcome, an anchor, a treatment or a window input, so nothing upstream of `224` moves
and no other column may change. Constants are updated only through `227`'s own write.

**Known limitation, recorded now.** The regex is a raw substring test over a serialised
JSON blob, so it is not category-aware: a future extract in which health appears only
under `"Affected":"No"` would be flagged. That is unchanged by this exception — it is the
v3 rule, applied to more records rather than to one — and it does not bite in this data.

**Not touched.** Essay 1 uses the same column as **H4** (`158:80`, `labels[...] =
'H4_health'`), as a subgroup split (`158:231`) and as a robustness restriction
(`158:287`); Essay 2 uses it as a control in ten scripts. Both sit outside the Essay 3
freeze and outside this exception. Flagged, not measured, not changed.

## Where to read things instead of changing them

| Question | File |
|---|---|
| Settled state, with pointers | `docs/claude/ESSAY3_V4_STATE.md` |
| Every methods number, prose-formatted | `outputs/essay3_v4/methods/METHODS_FACTS.md` |
| How to reproduce, and the traps | `docs/claude/REPRODUCE_ESSAY3_V4.md` |
| What was pre-specified | `outputs/essay3_v4/ANALYSIS_PLAN_V4.md` |
| Draw and verification history | `outputs/rebuild_v4/231_validation_draws.md` |

## Change log

*(empty at the freeze; append one row per qualifying change)*

| Date | Reason (1 or 2) | Essay text moved | Commit |
|---|---|---|---|
| 2026-09-25 | **1** | The methods define the health indicator as **any record** describing health data. `health_breach` (`156:144`) instead reads ONE `information_affected` per event: Stage 3 (`152:93`) keeps the single source record with the longest string, and Gate 2 (`153:62-71`) does not re-aggregate it across chained components. **5 of 405** analysis events mention health in a source record but carry 0 - treated: DISH Network 2023-02-22 (chain CH-22), Altice USA 2024-02-29 (CH-32); control: ABM Industries 2018-01-08, Wabtec 2022-03-15, Okta 2023-09-23 (all three lost inside their own firm-day, Wabtec by 9 characters). A sixth, IMA Financial 2022-10-18 (control, CH-31), is in the 489 but not the 405 and is corrected too. The error is one-directional: all 24 currently-flagged events survive an `"Affected":"Yes"`-only reading, so the indicator under-counts and never over-counts. The treated health cell is empty (0 of 109) for this reason alone. Fixed in `scripts/214` as ledger entries; v3 left frozen. | PENDING (log commit); change commit and constants to follow. |
| 2026-09-24 | **1** | The methods define the notification date as the earliest reported date among an event's records. Gate 2 (`153:59`, v3, frozen) instead keeps the earliest-*breach* component's `reported_date`, unlike Stage 3 (`152:91`, which takes the minimum). 12 analysis events (3 treated, 9 control) are anchored later than their earliest notification, gaps 1 to 1,109 days, all Gate-2 chained. Two treated outcomes turn on it — DISH 90d and GoDaddy 180d — both in the direction of recording a departure. Fixed in `scripts/214` as ledger entries; v3 left frozen. | `bfeb08c` (log), see following commit (change). **Constants moved** (51 of 94): F1_30 coef .0031->.0032, CV3 p .9272->.9252; F1_90 coef -.0252->-.0390, CV3 p .7603->.6263; F1_180 coef .0383->.0227, CV3 p .7026->.8211; F4 placebo coef -.0833->-.0837, CV3 p .3191->.3257. Sensitivity-family min BH p .9912->.9942. **No verdict changed** — all four remain NULL. Re-run: 214, 234, 233, 230, 235, **220**, 232, 224, 227, 229, 228, 239. Constants were written by 227 itself, after retiring the superseded baseline so its assertion could not block the legitimate change. |
| 2026-09-24 | **1** | The methods section claims *industry fixed effects*. The SIC-FE sensitivity did not implement them: it grouped on the PRC extract's **inherited** `sic`, taken as the mode per parent CIK. That column disagrees with the resolved parent's actual industry for **87 of 405** analysis events, and every one of those 87 is a **control** event (all 109 treated events agree). The inherited values are visibly placeholders — 3400, 6200, 2000, 5000, 1000 recur across unrelated firms — and several trace to the ticker-sink mis-assignments already documented (Oceaneering carrying `AIG`/6200 against a true SIC of 13; Brown-Forman carrying `BRO`/6200 against 20; EMC carrying `AES`/4900 against 35; Nuance and Microsoft carrying `SBAC`/6500 against 73). Since treatment is identified almost entirely off one SIC cell's controls, a control-side industry mislabel changes which controls sit in the treated firms' comparison cell, so the sentence "industry fixed effects" is not supported by what the code did. **Scope: the SIC-FE sensitivity only.** The primary specification, the placebo and the other 24 sensitivity rows do not read `sic2` and are not re-estimated; their outputs must remain byte-identical. | `2d0ee01` (log), `7d78990` (change). **`scripts/227` was subsequently re-run WHOLE** so the three SIC-FE WCR p-values come from the canonical seeded bootstrap stream rather than a restarted one; only those three `p_wcr` values moved, by thousandths (30d .1742->.1749, 90d .3898->.3878, 180d .2563->.2658). Coefficients, CV3 p and BH p are unchanged, and the 24 non-SIC sensitivity rows plus f1_ladder, f4_placebo, f1_cluster_diagnostics, f3_loco, f5_ceo and constants_essay3_v4.json are all byte-identical to the pre-exception commit `fe486f0`. |
