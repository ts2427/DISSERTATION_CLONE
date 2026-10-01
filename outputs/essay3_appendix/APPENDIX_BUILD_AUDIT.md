# Essay 3 appendix - build audit

Produced by `scripts/245_essay3_appendix.py` alongside `ESSAY3_APPENDIX_TABLES.md` and `.docx`. Kept separate from the appendix so that the appendix contains only the title, Tables 1-11 and their notes, and so that grepping the appendix for a banned string cannot match an assertion name.

## ASSERTIONS

- T1 Panel A every ledger step has a reader-facing label **PASS**
- T1 Panel B totals 1,054 **PASS**
- T1 Panel B every label is a GRADE_LABEL value **PASS**
- T1 Panel B no label is a raw final_grade code **PASS**
- T1 ledger closes (N never rises) **PASS**
- T1 treated + control == N at every populated step **PASS**
- T2 treated total == 109 **PASS**
- T2 clause totals == 70 / 39 **PASS**
- T3 totals == 109 / 296 **PASS**
- T6  30d treated + control == pooled on every count **PASS**
- T6  90d treated + control == pooled on every count **PASS**
- T6 180d treated + control == pooled on every count **PASS**
- T7 Panel A CV3 rows equal f1_ladder.csv **PASS**
- T9 Panel A has 27 rows **PASS**
- T9 Panel B events total 405 **PASS**
- T11 Panel A has 26 rows **PASS**
- T11 Panel B every title is verbatim in tmobile_502_text.md **PASS**
- T11 Panel B no title uses an abbreviation **PASS**
- T11 abbreviation regex is live (fires on 'EVP', quiet on the spelled-out title) **PASS**
- T11 Panel B title check has teeth (an abbreviated title is rejected) **PASS**
- T11 Panel B outcome-window column sums to 13 **PASS**
- T11 Panel B outcome-window sum equals Panel A 180-day Y count **PASS**
- Tables numbered 1-11 in order **PASS**
- No cell contains inf, nan, or a hyphen used as a minus sign **PASS**
- Note text contains no banned string (47 CFR, bare 'se', or a grade code) **PASS**

36 assertion(s): 36 PASS, 0 FAIL.

## TABLE 1 STEP LABELS

The reader-facing label shown in Table 1 Panel A, and the pipeline step name it comes from in the committed ledger.

| Appendix label | Committed ledger step |
|---|---|
| PRC notification records | PRC notification records (master_breach_dataset.xlsx) |
| Records assigned a parent CIK | Gate 1: signed parent CIK |
| Firm-day events | Stage 3: CIK+date firm-day events |
| After the rolling-campaign rule | Gate 2 adjacency collapse |
| Canonical breach events | Stage 4/5 canonical events (CANONICAL_V4) |
| Security link to CRSP | CRSP data (has_crsp_data) |
| Compustat covariates within 550 days | Compustat covariates (size, leverage, ROA) = Query 2 scope |
| Censoring rule | Fully observed outcome window (pre-specified censoring rule) |
| Form 8-K activity requirement | Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK) |
| At least 150 daily returns (analysis sample) | Prior 12-month market-adjusted return available (>=150 daily returns) |

## TABLE SOURCES

The provenance sentence that each table's note used to carry. The appendix itself states findings only; build information lives here.

- **Table 1** outputs/essay3_q4/table01.csv (Panel A, from outputs/essay3_v4/e_ledger.csv and outputs/rebuild_v4/v4_212_identity_review.csv); Data/processed/rebuild/stage2_signed.csv (Panel B); outputs/essay3_appendix/descriptive_counts.csv (records per event)
- **Table 2** outputs/essay3_q4/table02.csv; outputs/essay3_v4/f1_ladder.csv; outputs/essay3_appendix/descriptive_counts.csv (singleton and largest-cluster rows)
- **Table 3** outputs/essay3_q4/table03.csv
- **Table 4** outputs/essay3_q4/table04.csv, from outputs/essay3_q3/descriptives.csv; outputs/essay3_appendix/descriptive_counts.csv (Panel B)
- **Table 5** outputs/essay3_q4/table05.csv; outputs/essay3_q2/d3_audit_recall_by_stratum.csv
- **Table 6** outputs/essay3_q4/table06.csv; outputs/essay3_q4/_d5_crosswalk.csv
- **Table 7** outputs/essay3_q4/table07.csv; b_control_coefficients.csv; c_logit_diagnostics.csv; outputs/essay3_v4/f1_ladder.csv
- **Table 8** outputs/essay3_q4/table08.csv, from outputs/essay3_v4/f4_placebo.csv
- **Table 9** outputs/essay3_q4/table09.csv; outputs/essay3_v4/i_tests.csv; The full 36-cell SIC list is in outputs/essay3_v4/f3_sic2_cells.csv
- **Table 10** outputs/essay3_q4/table10.csv; outputs/essay3_v4/f1_cv3_variance_shares.csv; outputs/essay3_v4/239_v3_overlap_sensitivity.csv
- **Table 11** outputs/essay3_q4/table11.csv; outputs/essay3_q4/tmobile_502_text.md

## NOT REGENERABLE

- none

## TEXT-TO-TABLE CHECK

163 figures checked; 0 MISMATCH. Full listing in `text_figures_check.csv`.

