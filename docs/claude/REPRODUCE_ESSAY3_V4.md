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

`scripts/217` covers the offline logic. For the data chain, the check is to rerun the
offline stages in a fresh worktree from HEAD and diff the outputs against the committed
ones:

```
git worktree add /tmp/v4check HEAD
cd /tmp/v4check
python scripts/235_fetch_completeness_v4.py
python scripts/232_censoring_report_v4.py
python scripts/224_essay3_v4_sample_e.py
# then diff outputs/essay3_v4/e_analysis_sample.csv against the committed copy
```

`220` and `227` are slow (the classifier reads ~1,500 filings; the bootstrap draws
99,999 times) and are verified by their own internal assertions instead: `227` writes
`constants_essay3_v4.json` on its first run and **asserts against it** on every later
run, and `229` independently recomputes the HC3/CV1/CV3 SEs and coefficients and checks
them against the committed `f1_ladder.csv`.

### Result of that check (2026-09-19, HEAD 99ceb43)

Ran in a detached worktree at HEAD, offline:

| output | result |
|---|---|
| `e_analysis_sample.csv` | byte-identical |
| `e_ledger.csv` | byte-identical |
| `232_censoring.csv` | byte-identical |
| `239_v3_overlap_sensitivity.csv` | byte-identical |
| `b_scope_events.csv` | **data-identical**, bytes differ |

The one byte difference is carriage returns inside a quoted multi-line free-text
field (`incident_details`, which carries pasted breach narratives). Comparing the two
files as data — same shape (412 x 53), same columns, every column equal once CR is
stripped — they match exactly.

**Do not byte-compare `b_scope_events.csv` across checkouts.** A tracked CSV with
embedded newlines inside quoted fields is not byte-stable under git's line-ending
handling. Compare it as a dataframe, as above.
