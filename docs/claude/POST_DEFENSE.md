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
