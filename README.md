# Data Breach Disclosure Timing and Market Reactions

**Author:** Timothy D. Spivey
**Institution:** University of South Alabama
**Year:** 2026

Code, data-construction pipeline, and committed outputs for a three-essay dissertation on how the timing of data breach disclosure, and a firm's regulatory status under it, relate to market reactions, information asymmetry, and governance response.

---

## Read this first

**This README carries no results.** Every figure in this project lives in a committed artifact with a generating script, and numbers are cited from those files, never from prose. The pointers below say where each result lives; they do not restate it.

**What the three essays find.** All three report null results. None of them supports its hypothesis, and the design does not license causal claims:

- The regulatory setting is **47 CFR 64.2011** (effective December 8, 2007). Its clock runs to law enforcement, and public disclosure is embargoed afterward; it sets no customer-notification deadline. See `docs/fcc_premise_verification.md`.
- There are no treated events before the rule took effect, so a difference-in-differences design is not identified. The essays are **post-2007 cross-sectional**.
- Do not describe this project as a natural experiment, a quasi-experiment, or causal evidence.

**Treatment** is FCC Form 499 registration status, established by a documented two-clause rule with adjudications. It is never SIC code.

**Inference frame.** Cluster-jackknife (CV3) standard errors on parent CIK, with a restricted wild cluster bootstrap. HC3 is reported for comparison only and is **disqualified**: it ignores within-parent clustering. No HC3 p-value should be read as significance anywhere in this project.

**Equivalence claims are retired.** No TOST result is current.

---

## Setup

```bash
# Clone. core.longpaths is required on Windows or checkout will fail.
git clone -c core.longpaths=true https://github.com/ts2427/DISSERTATION_CLONE.git
cd DISSERTATION_CLONE

python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

### Git LFS — read before running anything

Several inputs and committed outputs are stored with Git LFS. The Essay 3 chain's inputs are configured correctly and arrive as real files in a clean clone.

**Many legacy files are not.** Their pointers were committed, but the `filter=lfs` rule for their paths was removed from `.gitattributes` in an earlier commit, so a clean clone writes a small placeholder file instead of the data, **with no error**. The objects themselves are intact on GitHub; only the rule is missing. Affected paths are concentrated under `Data/JSON Files/`, `Data/enrichment/`, `Data/audit_analytics/` and several `outputs/` table directories, which means **Essays 1 and 2 are not fully reproducible from a clean clone today**.

To tell a placeholder from real data:

```bash
head -c 60 <file>   # a placeholder begins: version https://git-lfs.github.com/spec/v1
```

Restoring the rule by directory is a planned task, tracked in `outputs/PENDING_REBASELINE.md`.

### Data not in Git

Licensed and bulk inputs (CRSP, Compustat, and other WRDS extracts) are not redistributed here. See `docs/WRDS_EXTRACT_RECIPE.md` for how each extract was pulled and how to reproduce it with your own WRDS credentials. Public EDGAR inputs used by the Essay 3 chain, including the Item 5.02 filing texts, are committed.

---

## Running the analysis

```bash
python run_all.py          # full pipeline; see the docstring for stage order and gating
```

`run_all.py` is the authority on stage order, which scripts are current, and which are retired. Read its docstring before running anything.

**Essay 3 has its own chain** and must not be run through `run_all.py` or `scripts/158`:

```
scripts/187 -> 195 -> 199 -> 202 -> 190 -> 191 -> 203 -> 204
```

`scripts/195` is the frozen final classifier; do not edit it. `scripts/202` asserts its results against a committed baseline, so a silent change in the estimates fails the run. Start from `outputs/essay3_q2/ESSAY3_STARTING_POINT.md`.

---

## Where the current results live

### Essay 1 — market reaction
- `outputs/rebuild/constants_v3.json` — the assertion baseline; the authoritative source for every Essay 1 figure
- `outputs/rebuild/CONSTANTS_BLOCK_V3.md` — the same constants, annotated
- `outputs/rebuild/appendix_v3/` — appendix tables, live-computed (written by `scripts/158`; Word build in `scripts/160`)
- `outputs/rebuild/GATE1_SUMMARY.md`, `GATE1_APPLICATION_REPORT.md` — entity verification

### Essay 2 — information asymmetry
- `outputs/ESSAY2_QUERY4_REPORT.md`, `ESSAY2_QUERY5_REPORT.md`, `ESSAY2_QUERY6_REPORT.md`, `ESSAY2_QUERY7_REPORT.md` — the analysis record, in order
- `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` — sample chain
- `outputs/ESSAY2_MECHANICAL_RULES.md` — the rules applied to the sample
- `outputs/ESSAY2_ANNOUNCEMENT_CONTRAST.md` — the announcement-window contrast
- `outputs/tables/essay2_appendix/` — appendix tables (`manifest.csv` lists them; Word build in `scripts/178`)

### Essay 3 — governance response
- `outputs/ESSAY3_QUERY2_REPORT.md` — the current analysis, end to end: sample ledger, estimation, validation, T-Mobile case
- `outputs/essay3_q2/ESSAY3_STARTING_POINT.md` — one-page orientation; start here
- `outputs/essay3_q2/constants_essay3_q2.json` — Essay 3's assertion baseline, separate from `constants_v3.json`
- `outputs/essay3_q2/` — all estimation, validation and case outputs
- `outputs/ESSAY3_QUERY1_REPORT.md` — the discovery pass that preceded the rebuild
- `docs/claude/ESSAY3_POST_RERUN_STATE.md`, `docs/claude/ESSAY3_HANDOFF.md` — the settled state and handoff

---

## Retired material — do not cite

Superseded results remain in the repository for provenance. Several carry a `TOMBSTONE — RETIRED` header; treat any file so marked as history.

- `outputs/RETIREMENT_LEDGER.md` — what was retired, why, and what replaced it
- `outputs/STALE_RESULTS_MANIFEST.txt` — superseded output files
- `outputs/PENDING_REBASELINE.md` — known gaps and planned maintenance

Claims that appear in older drafts and are **no longer supported**: any first-stage effect of the rule on disclosure timing; any mediation result; any equivalence or TOST claim; Cox hazard results; BoardEx-based turnover measurement; SIC-code treatment; and any Item 5.02 filing rate described as executive turnover.

---

## Reproducibility

The Essay 3 chain is verified reproducible from a clean clone: scripts 195 through 204 run end to end and every emitted file matches the committed version.

Two failures found during that verification are worth knowing about, because both produced wrong output **without raising an error**:

1. A `.gitignore` rule silently excluded pipeline inputs, so the classifier coded a subset of its filings, exited normally, and emitted different rates.
2. A missing LFS rule delivered placeholder files in place of data.

The lesson is recorded in `docs/DATA_QUALITY_DOCUMENTATION.md`: verify a pipeline by comparing emitted outputs against committed ones from a clean clone, not by checking that scripts exit cleanly.

---

## Repository layout

```
run_all.py           Pipeline entry point and stage authority
scripts/             Data construction, estimation, validation
Notebooks/           Exploratory analysis
Data/                Inputs (see Git LFS and Data sections above)
outputs/             Committed results, tables, reports, ledgers
docs/                Methods documentation, data quality, audit records
tests/               Unit and integration tests
validation/          Validation artifacts
Dashboard/           Streamlit app (see note below)
```

Working notes and query documents live in `docs/claude/`.

**Note on `.gitignore`:** `*.md`, `*.txt`, `*.xlsx` and `*.docx` are ignored repository-wide, so deliverables in those formats need `git add -f` unless they sit in a directory with a negated rule (`docs/claude/`, `outputs/essay3_q2/`). Check for missing work with `git status --porcelain --ignored=matching -- <dir>`.

---

## Dashboard

```bash
streamlit run Dashboard/app.py
```

**The dashboard has not been updated to the current chain.** It still presents the retired natural-experiment framing and pre-rebuild results. Do not use it to read current findings.

---

## Citation

```
Spivey, T. D. (2026). Data breach disclosure timing and market reactions.
Dissertation, University of South Alabama.
```

## Contact

Timothy Spivey — ts2427@jagmail.southalabama.edu

## License

Provided as-is for academic use.
