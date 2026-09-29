# TOMBSTONE — `outputs/tables/essay2_appendix/`

**2026-09-29 (Run-All Follow-Up, Part L). The 41 CSV files in this directory have no
committed generator. Do not cite them.**

Nothing here is deleted. The files stay on disk and in git history so the Essay 2
appendix that was built from them remains inspectable. What is withdrawn is their
standing as evidence.

## What is wrong with them

**No script in this repository writes them.** The only script that names this directory
is `scripts/178_essay2_appendix_docx.py`, and 178 only *renders* these CSVs into
`ESSAY2_APPENDIX.docx` — which is itself gitignored. The code that produced the numbers
was a scratchpad file (`emit_appendix.py`) that was never committed.

The consequence: **a figure in this directory cannot be traced to the data or the
specification that produced it, and cannot be regenerated from a clean clone.** Neither
can it be checked — there is nothing to re-run and compare against.

## They are not stale copies of the live tables

This is the part that is easy to get wrong, so it is stated explicitly.

| | files | written by |
|---|---|---|
| `outputs/tables/essay2_appendix/` (this directory) | **41** | nothing committed |
| `outputs/tables/essay2_v2/` | **61** | `scripts/163` and `scripts/164`, both live in `run_all.py` |

**The two sets share zero filenames.** Not one. This directory holds names like
`channel_announcement_buildup.csv` and `cluster_deletion_prerule.csv`; the live directory
holds `t1_final_sample.csv` through `t52_spec_curve_permutation.csv`.

So this is **a different set of tables, not an out-of-date copy of the live ones**. You
cannot repair a citation to a file here by pointing it at the same filename in
`essay2_v2/` — there is no same filename. A reader who assumed these were simply older
versions of the live tables would be wrong twice: wrong that a current equivalent exists,
and wrong that the number could be refreshed by re-running the pipeline.

## What to cite instead

- **Essay 2 tables:** `outputs/tables/essay2_v2/`, written by `scripts/163` and
  `scripts/164`. Since 2026-09-29 script 163 asserts its canonical sample on the way out
  (N = 333, 104 treated, 82 clusters, 12 treated parent filer entities), and `scripts/165`
  asserts the same three on the way in.
- **The inferential frame:** `scripts/165`. CV1, CV3 and the wild cluster bootstrap. HC3
  is reported for comparison only and is disqualified as a significance test.
- **The attrition chain:** `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md`, computed live by
  163 Phase A.

`manifest.csv` in this directory lists the 41 files. It is a manifest of what exists here,
not a provenance record: it does not name a generator either.

## Status

| | |
|---|---|
| Deleted? | **No.** Kept for provenance. |
| Citable? | **No.** |
| Regenerable from a clean clone? | **No.** |
| Recorded in | `outputs/RETIREMENT_LEDGER.md`, Part L |
