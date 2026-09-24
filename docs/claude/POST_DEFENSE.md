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
| 2026-09-24 | **1** | The methods section claims *industry fixed effects*. The SIC-FE sensitivity did not implement them: it grouped on the PRC extract's **inherited** `sic`, taken as the mode per parent CIK. That column disagrees with the resolved parent's actual industry for **87 of 405** analysis events, and every one of those 87 is a **control** event (all 109 treated events agree). The inherited values are visibly placeholders — 3400, 6200, 2000, 5000, 1000 recur across unrelated firms — and several trace to the ticker-sink mis-assignments already documented (Oceaneering carrying `AIG`/6200 against a true SIC of 13; Brown-Forman carrying `BRO`/6200 against 20; EMC carrying `AES`/4900 against 35; Nuance and Microsoft carrying `SBAC`/6500 against 73). Since treatment is identified almost entirely off one SIC cell's controls, a control-side industry mislabel changes which controls sit in the treated firms' comparison cell, so the sentence "industry fixed effects" is not supported by what the code did. **Scope: the SIC-FE sensitivity only.** The primary specification, the placebo and the other 24 sensitivity rows do not read `sic2` and are not re-estimated; their outputs must remain byte-identical. | `2d0ee01` (log), `7d78990` (change). **`scripts/227` was subsequently re-run WHOLE** so the three SIC-FE WCR p-values come from the canonical seeded bootstrap stream rather than a restarted one; only those three `p_wcr` values moved, by thousandths (30d .1742->.1749, 90d .3898->.3878, 180d .2563->.2658). Coefficients, CV3 p and BH p are unchanged, and the 24 non-SIC sensitivity rows plus f1_ladder, f4_placebo, f1_cluster_diagnostics, f3_loco, f5_ceo and constants_essay3_v4.json are all byte-identical to the pre-exception commit `fe486f0`. |
