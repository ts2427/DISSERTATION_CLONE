# Reviewer guide — reproducing the dissertation pipeline

One page for a committee member reviewing the code and data pipeline. Results are never restated here; every number lives in a committed file listed below.

## What the two references represent

- **`defense-final`** (tag, `902a8ea`): the verified state of every result. Nothing about the results changes after this tag.
- **`main`**: the same pipeline and outputs after a repository cleanup (tag `repo-clean`). Superseded material moved to `archive/`, documentation was added, and `requirements.txt` was pinned. No script logic or output changed.

Review either one. Use `defense-final` if you want exactly what was defended.

## Setup (tested from scratch, Windows 11, Python 3.13.2)

```bash
git clone -c core.longpaths=true https://github.com/ts2427/DISSERTATION_CLONE.git
cd DISSERTATION_CLONE
git checkout defense-final          # or stay on main
git lfs pull                        # large inputs are stored with Git LFS

python -m venv C:\venvs\diss        # keep the venv path SHORT on Windows (see note)
C:\venvs\diss\Scripts\activate
pip install -r requirements.txt     # pinned versions on main (see note)
python run_all.py
```

**Run time:** about 10 minutes end to end on a laptop (583 s in the fresh-environment test; 66 steps). **Exit code 0 means clean.** The final summary lists failed steps; there should be none.

**Notes from the fresh-environment test.**
- **Short venv path.** A venv under a long directory path fails `pip install` on Windows. One of statsmodels' test files then exceeds the 260-character path limit, the install aborts partway, and `lifelines` never installs. Put the venv somewhere short, or enable Windows long paths.
- **Install from `main`'s `requirements.txt`.** The file at `defense-final` lacked `python-docx` (step 160 needs it) and set minimum versions only. Newer releases reproduce every primary result, but they move one corroborating, non-converging Essay 3 logit and some floating-point digits and figure pixels. `main` pins the exact versions that produced the committed outputs. With those, the outputs reproduce byte for byte.

## The one declared skip: step 170

`scripts/170_essay2_scope_and_bounds.py` needs `Data/wrds/crsp_quotes_topup.csv`, a CRSP intraday-quote extract that the WRDS licence does not allow us to redistribute. `run_all.py` reports the step as **SKIPPED (declared), not failed**. Its committed outputs come from the licensed run, and they are documented in `docs/claude/REPRODUCE_ESSAY2.md`. Everything else runs from the repository. `docs/WRDS_EXTRACT_RECIPE.md` explains how to re-pull the licensed extracts with your own WRDS credentials.

## Where the results live

| | constants (assertion baseline) | tables | sample ledger |
|---|---|---|---|
| **Essay 1** | `outputs/rebuild/constants_v3.json` | `outputs/rebuild/appendix_v3/table_1..16.csv` | `outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md` |
| **Essay 2** | (inference in the tables) | `outputs/tables/essay2_v2/` (`t26` inference ladder, `t28` design resolution, `t50` announcement contrast, `t53` test ledger) | `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` |
| **Essay 3** | `outputs/essay3_v4/constants_essay3_v4.json` | `outputs/essay3_v4/`, appendix in `outputs/essay3_appendix/` | `outputs/essay3_v4/e_ledger.csv` |
| **Defense supplement** | `outputs/defense_supplement/constants_defense_supplement.json` | `outputs/defense_supplement/` | — |

Each chain **asserts its results against its committed constants file** on every run, so if an estimate changes silently, the run fails.

## The audit trail

- `outputs/RETIREMENT_LEDGER.md`: everything retired, fixed or removed, with dates, reasons and before/after values.
- `docs/claude/KNOWN_LIMITATIONS.md`: disclosed limitations of the samples and measures.
- `docs/claude/V3_FREEZE_EXCEPTIONS.md`: authorised departures from the frozen baseline.
- `archive/ARCHIVE_MAP.csv`: old path to new path for every archived file. Documents dated before 2026-10-03 cite pre-archive paths.
- `docs/claude/POST_DEFENSE.md`: the change rule after the freeze.

## How to verify reproducibility

1. **The run itself.** `python run_all.py` exits 0, with step 170 the only declared skip, and every assertion baseline reports `PASS`.
2. **The freeze gate.** `scripts/210_verify_v3_frozen.py`, which also runs inside `run_all.py`, compares every baseline file against `outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv` by content hash and git blob id. It ends `RESULT: PASS - v3 baseline intact`. Any changed, deleted or unexpected file fails it.
3. **Byte comparison.** After a run, `git status` and `git diff --ignore-cr-at-eol --stat` should show nothing beyond the following:
   - run logs and timestamp lines;
   - `.docx` files rebuilt with identical text;
   - one line of `outputs/ESSAY2_QUERY6_REPORT.md` that needs the licensed quote file.

   Every essay and supplement output should be byte-identical apart from line endings.
