# Reproducing Essay 3, v4

What a fresh clone can rebuild, in what order, and what it cannot.

## What is NOT rerun from a clean clone

Two stages need credentials or the network and are **not** part of the
reproduction. Their outputs are committed and are treated as inputs.

| stage | why | committed output |
|---|---|---|
| `211` WRDS pull, `219` Compustat pull | WRDS subscription | `Data/wrds_v4/*.csv` (LFS) |
| `213` EDGAR verification, `231` SEC fetch | SEC network, declared User-Agent | `Data/edgar/ex21_cache_v4/`, `Data/edgar/submissions_cache_v4/`, `Data/edgar/item5_02_text/`, `outputs/rebuild_v4/213_verification_log.csv` |

Everything else reruns offline from those bytes.

## Order

Run order and numeric order diverge in two places; follow this list, not the numbers.

```
# --- linking ---------------------------------------------------------------
python scripts/212_pit_linker_v4.py                    # v3 pass -> Stage 3 worklist
python scripts/214_corrections_v4.py                   # -> CANONICAL_V4
python scripts/212_pit_linker_v4.py --canonical Data/processed/rebuild_v4/CANONICAL_V4.csv \
                                    --out-prefix v4_   # v4 pass
python scripts/215_ledger_v4.py

# --- Stage 6 inputs --------------------------------------------------------
python scripts/219_wrds_funda_v4.py --assemble-only    # offline: covariates from the committed pull
python scripts/234_outcome_cik_v4.py                   # outcome_cik by rule
python scripts/233_resolve_reconciliation.py           # PREREQUISITE of 224; must be all 'agree'
python scripts/230_outcome_gap_v4.py
python scripts/235_fetch_completeness_v4.py            # also writes the b_* scope files
python scripts/237_validation_draw_v4.py               # needs the v3-frozen ref

# --- Essay 3 ---------------------------------------------------------------
python scripts/220_essay3_v4_classifier_v2.py          # slow (~1500 filings)
python scripts/238_score_new_documents_v4.py
python scripts/232_censoring_report_v4.py              # MUST precede 224
python scripts/224_essay3_v4_sample_e.py
python scripts/227_essay3_v4_estimation.py             # slow (wild bootstrap B=99,999)
python scripts/229_essay3_v4_se_diagnostics.py
python scripts/228_essay3_v4_tmobile_case_timeline.py
python scripts/239_v3_vs_v4_sidebyside.py

# --- gates -----------------------------------------------------------------
python scripts/217_v4_offline_tests.py                 # must be all-pass
python scripts/210_verify_v3_frozen.py                 # must be PASS
```

**Two ordering traps.** `232` must run before `224`, because 224's ledger reads the
censoring result. `233` must run before `224`, which aborts unless every reconciliation
row says `agree`.

## What must not change

- **v3 is frozen.** `scripts/210` is the gate; run it *after staging*, not before, or it
  cannot see newly added files.
- **The classifier is frozen.** `scripts/220` is byte-identical to v3's `scripts/195`.
  No result may retune it.
- **The reference codes and the draw are frozen**, and were committed before the
  classifier was ever run on those documents. See `outputs/rebuild_v4/231_validation_draws.md`
  for the sha256 of each, including the two superseded draws and why they were retired.
- **The analysis plan is frozen.** `outputs/essay3_v4/ANALYSIS_PLAN_V4.md`, committed
  before `227` ran. No specification change is permitted after that commit.

## Inputs that are deliberately v3's

Three places read a v3 artefact on purpose. Each is an input-reading choice, documented
where it occurs, not a silent fallback.

| input | used by | why |
|---|---|---|
| `outputs/essay3_q2/d3_audit_recall_by_stratum.csv` | `227` recall-correction sensitivities | v4 has no recall audit of its own; the classifier is byte-identical, so measured recall is a property of the classifier. **Assumes** recall measured on v3-era documents transfers. |
| six T-Mobile case files (`g3_director_roster`, `b_exhibits_log`, `g2_*`, `g3_*`, `g34_*`, `g4_*`) | `228` | produced by `scripts/191`, never copied into the 220s; they describe one firm's governance and do not vary with the event set |
| `outputs/essay3_q2/constants_essay3_q2.json` | `239` | the v3 side of the comparison |

## The trap that the loader exists to close

`CANONICAL_V4` still carries `has_crsp_data`, `permno` and four covariates **inherited
from v3**. Reading them would score the v3 sample under v4 labels — Nokia is the tell:
that file says `has_crsp_data=1, permno=87128` while v4 does not link it at all.

Every Essay 3 v4 script therefore loads through `scripts/236_essay3_v4_loader.py`, which
drops those columns and re-attaches v4's own. `scripts/217` asserts that none of
`220`–`229` or `232` opens `CANONICAL_V4` directly.

## Clean-clone check

A **worktree is not a clean-clone test.** It shares `.git` and the LFS object store, so
it cannot catch a missing LFS object or a missing ref — two of the failures that
actually occur. Test from a real clone:

```
git clone --branch rebuild-v4 <repo URL> v4clone
cd v4clone
git lfs pull                                   # ALL of it, not a subset
git fetch origin refs/tags/v3-frozen:refs/tags/v3-frozen   # if the clone is shallow
python scripts/235_fetch_completeness_v4.py
python scripts/232_censoring_report_v4.py
python scripts/224_essay3_v4_sample_e.py
python scripts/239_v3_vs_v4_sidebyside.py
python scripts/217_v4_offline_tests.py
python scripts/210_verify_v3_frozen.py
```

Two things a shallow clone breaks, both of which look like code failures and are not:

- **A partial `git lfs pull` leaves `Data/edgar/cik-lookup-data.txt` a pointer**, and the
  two SEC name-index tests fail. Pull everything.
- **`--depth 1` has no `v3-frozen` tag**, so `scripts/210` cannot resolve its baseline and
  `scripts/237` cannot define the validation pool. Fetch the tag explicitly.

### Result (2026-09-19, HEAD f1c0ee0, fresh clone from GitHub)

`CANONICAL_V4.csv` byte-identical to the source tree, and every regenerated output
byte-identical to its committed copy:

`b_scope_events.csv`, `b_scope_filings.csv`, `b_event_filing_pairs.csv`,
`232_censoring.csv`, `e_analysis_sample.csv`, `e_ledger.csv`,
`239_v3_overlap_sensitivity.csv`, `239_v3_vs_v4_constants.csv` — **8/8 identical.**

`scripts/217` 62/62, `scripts/210` PASS.

**What made this possible.** Before the `-text` rules, `core.autocrlf` rewrote CRLF to LF
on commit for every pandas-written CSV, so the on-disk bytes of 20+ v4 CSVs — including
`CANONICAL_V4.csv` — differed from their own blobs. A clone received different *input*
bytes than the tree the outputs were produced in, and byte comparison could never
succeed. `.gitattributes` now carries `-text` for `outputs/essay3_v4/**/*.csv`,
`outputs/rebuild_v4/**/*.csv` and `Data/processed/rebuild_v4/**/*.csv`, scoped to v4
because v3 blobs must not be renormalised — `scripts/210` compares them byte for byte.

`220` and `227` are slow (the classifier reads ~1,500 filings; the bootstrap draws
99,999 times) and are verified by their own internal assertions instead: `227` writes
`constants_essay3_v4.json` on its first run and **asserts against it** on every later
run, and `229` independently recomputes the HC3/CV1/CV3 SEs and coefficients and checks
them against the committed `f1_ladder.csv`.

## Classifier validation: hand-coding steps with committed outputs (2026-10-02)

The validation pipeline behind the classifier precision, recall and kappa figures
(`outputs/essay3_q2/d3_*.csv`) has two kinds of step.

**Sheet builders, never rerun.** `scripts/189`, `196` and `200` each drew a blind
validation sample once and wrote the coding sheets and hidden-code files. Re-running them
would draw a new sample. Their outputs are committed static inputs.

**Scorers.** These score the committed sheets against the committed reference codes
(`VALIDATION_REFERENCE_CODES_{R1,R2,AUDIT}.psv`, cross-checked cell by cell against the
`*_CLAUDE_RATER.xlsx` workbooks). Checked on 2026-10-02 in an isolated worktree with the
network disabled. All four run offline from committed inputs, and every input is git-tracked.

| script | in `run_all.py`? | result |
|---|---|---|
| `194_essay3_q2_validation_agreement.py` | **yes** | CSVs byte-identical. Its committed log predated a `hand:` → `ref :` relabel (17 lines, values unchanged); the regenerated log is committed, and the step is now byte-identical. |
| `198_essay3_q2_differential_recall.py` | **yes** | CSVs and log byte-identical. |
| `197_essay3_q2_validation_r2_flag_changes.py` | no | Every CSV and its log byte-identical. It also rewrites `ADJUDICATION.xlsx`. |
| `201_essay3_q2_recall_audit_scoring.py` | no | Every CSV and its log byte-identical. It also rewrites `ADJUDICATION.xlsx` (adds tab `audit_v2`) and must follow 197. |

**Why 197 and 201 stay out of `run_all.py`.** No input is missing. The exception is the
one output, `ADJUDICATION.xlsx`, which openpyxl cannot reproduce byte for byte: it stamps
the write time into `docProps/core.xml` and serialises XML whitespace differently across
versions. The regenerated workbook has the same five tabs with identical cells, compared
with pandas, but differs in bytes (32,974 vs 32,917 committed). To reproduce by hand, run
`194`, `197`, `198`, `201` in that order (201 reads the workbook 197 writes), then compare
`ADJUDICATION.xlsx` by content, not bytes. The v4 counterparts (`221`-`226`) were not
part of this check.
