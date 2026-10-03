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
- There are no treated events before the rule took effect, so a difference-in-differences design is not identified. The essays are **post-2007 cross-sectional** and descriptive.
- Do not describe this project as a natural experiment, a quasi-experiment, or causal evidence.

**Treatment** is FCC Form 499 registration status, established by a documented two-clause rule with adjudications. It is never SIC code.

**Reviewing the pipeline?** Start with [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md): one page on setup, the expected run, where every result lives, and how to verify it.

**Inference frame.** Cluster-jackknife (CV3) standard errors on parent CIK, with a restricted wild cluster bootstrap. HC3 is reported for comparison only and is **disqualified**: it ignores within-parent clustering. No HC3 p-value should be read as significance anywhere in this project.

---

## Verified states (tags)

- **`defense-final`** (`902a8ea`) — the verified state of every result. A clean clone of this tag runs `run_all.py` to exit 0 (one declared skip, `scripts/170`, which needs a licensed quote file), the freeze gate `scripts/210` passes, and every essay and supplement output reproduces byte for byte. Every file ever committed, including everything later archived or removed, is intact at this tag.
- **`repo-clean`** (`0184898`) — the same results after the repository cleanup: superseded material moved to `archive/`, nothing in the pipeline changed, verified again from a clean clone.
- **`main`** — `repo-clean` plus the reviewer guide and a pinned `requirements.txt`. Same pipeline, same outputs. Use `main`'s `requirements.txt` even when checking out `defense-final` (see Setup).

---

## Setup

```bash
# Clone. core.longpaths is required on Windows or checkout will fail.
git clone -c core.longpaths=true https://github.com/ts2427/DISSERTATION_CLONE.git
cd DISSERTATION_CLONE
git lfs pull

python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

**The environment is defined by `requirements.txt`**, which pins the exact package versions that produced the committed outputs (tested on Python 3.13.2). Two lessons from a from-scratch test on 2026-10-03:

- **Use exact pins.** With minimum versions only (the file at `defense-final`), a fresh install pulls newer releases. Those reproduce every primary result but move a few non-primary digits and figure pixels. The `defense-final` file also lacked `python-docx`. With `main`'s pinned file, a brand-new environment reproduces every output byte for byte.
- **Keep the virtual environment's path short on Windows.** Under a long directory path, `pip install` fails partway when a file inside statsmodels exceeds Windows' 260-character limit. Packages after it, such as `lifelines`, never install. Either use a short path or enable Windows long paths.

### Git LFS

Large inputs and outputs are stored with Git LFS. `run_all.py` checks every input a live step reads before step 1 and stops if any is an LFS placeholder rather than data. To tell a placeholder from real data by hand:

```bash
head -c 60 <file>   # a placeholder begins: version https://git-lfs.github.com/spec/v1
```

### Data not in Git

Licensed and bulk inputs (CRSP, Compustat, and other WRDS extracts) beyond the committed extracts are not redistributed here. See `docs/WRDS_EXTRACT_RECIPE.md` for how each extract was pulled and how to reproduce it with your own WRDS credentials. Public EDGAR inputs, including the Item 5.02 filing texts, are committed. The literature PDFs are kept outside the repository and are not tracked (`Data/Articles/` is ignored).

---

## Running the analysis

```bash
python run_all.py          # full pipeline, all three essays and the defense supplement
```

**Expected result:** about 10 minutes on a laptop, exit code 0, and one declared skip. The skip is `scripts/170`, which needs a licensed CRSP quote file that is not redistributed; its committed outputs come from the licensed run (`docs/claude/REPRODUCE_ESSAY2.md`). Any other failed step means the run is not clean.

`run_all.py` is the authority on stage order, which scripts are current, and which are retired. Read its docstring before running anything. It runs the Essay 1 chain (`scripts/150`-`160`, `247`), the Essay 3 v4 chain (`scripts/212`-`246`, with the freeze gate `210`), the Essay 2 chain (`scripts/163`-`182`) and the defense supplement (`scripts/249`-`253`). Every chain asserts its results against a committed baseline, so a silent change in an estimate fails the run.

---

## Where the current results live

### Essay 1 — market reaction
- `outputs/rebuild/constants_v3.json` — the assertion baseline; the authoritative source for every Essay 1 figure
- `outputs/rebuild/CONSTANTS_BLOCK_V3.md` — the same constants, annotated
- `outputs/rebuild/appendix_v3/` — appendix tables, live-computed (written by `scripts/158`; Word build in `scripts/160`)
- `outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md` — sample chain

### Essay 2 — information asymmetry
- `outputs/tables/essay2_v2/` — the live tables (inference ladder `t26`, design resolution `t28`, announcement contrast `t50`, test ledger `t53`)
- `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` — sample chain
- `outputs/ESSAY2_ANNOUNCEMENT_CONTRAST.md` — the announcement-window contrast
- `outputs/ESSAY2_QUERY4_REPORT.md` through `ESSAY2_QUERY7_REPORT.md` — the analysis record, in order

### Essay 3 — governance response
- `outputs/essay3_v4/constants_essay3_v4.json` — the assertion baseline
- `outputs/essay3_v4/` — estimation, validation and case outputs; `outputs/essay3_appendix/` — the rendered appendix
- `docs/claude/ESSAY3_V4_STATE.md` — the settled state

### Defense supplement
- `outputs/defense_supplement/` — supplementary estimates on the frozen samples (`constants_defense_supplement.json` is its baseline)

---

## Audit trail

- `outputs/RETIREMENT_LEDGER.md` — what was retired, fixed or removed, when, and why
- `docs/claude/KNOWN_LIMITATIONS.md` — disclosed limitations of the samples and measures
- `docs/claude/POST_DEFENSE.md` — the change rule after the freeze
- `docs/claude/V3_FREEZE_EXCEPTIONS.md` and `outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv` — the freeze gate's record
- `docs/claude/REPRODUCE_ESSAY2.md`, `docs/claude/REPRODUCE_ESSAY3_V4.md` — reproduction notes and declared exceptions
- `docs/DATA_QUALITY_DOCUMENTATION.md` — the data-construction failure modes

### Archived material

Superseded scripts, pre-rebuild outputs, old dashboards and notebooks are in `archive/`, each at its original relative path. **Paths cited in documents dated before the cleanup (2026-10-03) refer to pre-archive locations; they resolve through `archive/ARCHIVE_MAP.csv` (old_path, new_path).** Nothing in `archive/` is read by the pipeline; treat it as history, not as current results.

Claims that appear in older drafts and are **no longer supported**: any first-stage effect of the rule on disclosure timing; any mediation result; any equivalence claim from those drafts (current TOST p-values are in the constants files and the defense supplement); Cox hazard results; BoardEx-based turnover measurement; SIC-code treatment; and any Item 5.02 filing rate described as executive turnover.

---

## Reproducibility

A clean clone runs end to end and reproduces every committed essay and supplement output (verified at `defense-final` and again at `repo-clean`). Two failures found in earlier verification are worth knowing about, because both produced wrong output **without raising an error**:

1. A `.gitignore` rule silently excluded pipeline inputs, so a classifier coded a subset of its filings, exited normally, and emitted different rates.
2. A missing LFS rule delivered placeholder files in place of data.

The lesson is recorded in `docs/DATA_QUALITY_DOCUMENTATION.md`: verify a pipeline by comparing emitted outputs against committed ones from a clean clone, not by checking that scripts exit cleanly.

---

## Repository layout

```
run_all.py           Pipeline entry point and stage authority
requirements.txt     The environment (pinned)
REVIEWER_GUIDE.md    One-page guide for reviewing and reproducing the pipeline
scripts/             Data construction, estimation, validation (live steps listed in run_all.py)
Data/                Inputs (see Git LFS and Data sections above)
outputs/             Committed results, tables, reports, ledgers
docs/                Methods documentation, data quality, audit records
archive/             Superseded material at its original paths (archive/ARCHIVE_MAP.csv)
Dashboard/           Streamlit app reading the committed outputs (see Dashboard below)
```

Working notes and query documents live in `docs/claude/`.

**Note on `.gitignore`:** `*.txt`, `*.xlsx` and `*.docx` are ignored repository-wide, and `*.md` everywhere except `outputs/`, `docs/`, `README.md` and the negated directories. A deliverable in an ignored format needs `git add -f`. Check for missing work with `git status --porcelain --ignored=matching -- <dir>`.

---

## Dashboard

```bash
streamlit run Dashboard/app.py
```

A local Streamlit app that presents the three essays as they stand at `defense-final`: an overview and the data chain, one page per essay, robustness and the defense supplement, and the limitations and audit trail. **It computes nothing and types no results.** Every number is read at run time from a committed output (constants files, appendix and essay tables, the defense supplement), and the file is named under each chart. It reads no raw CRSP or Compustat rows. Rebuilt 2026-10-03; the previous dashboard, with its retired framing and pre-rebuild numbers, is in `archive/Dashboard/`.

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
