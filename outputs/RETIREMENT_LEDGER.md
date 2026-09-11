# Retirement Ledger — Essay 3 (Query 2, Part H; 2026-09-11)

The scripts below are removed from `run_all.py`, and the hardcoded values are marked retired. Nothing is deleted: every script and output stays on disk and in git history.

- **Retiring commit:** the Essay 3 Query 2 Stage 2 commit, which follows `8e18c4e`. Record its hash here once it exists: `git log --oneline -- outputs/RETIREMENT_LEDGER.md`.
- **Replacement:** the Query 2 chain, scripts 187 → 195 (frozen v2 classifier, `6f7be7a`) → 199 → 202 → 190/191 → 203. Results are in `outputs/ESSAY3_QUERY2_REPORT.md` and the assertion baseline is `outputs/essay3_q2/constants_essay3_q2.json`.

**Why these went.** The legacy Essay 3 chain has two problems:
- **Outcome.** It uses any Item 5.02 filing as the outcome, but Item 5.02 also covers appointments, elections and pay.
- **Treatment and sample.** It uses the SIC-era or 7/28-era treatment and the N = 646/651 samples. Both predate the v3 rebuild.

Query 1 (`outputs/ESSAY3_QUERY1_REPORT.md`) found that the essay prose describes a dependent variable that was never computed.

## Scripts removed from run_all.py

"Last commit" is the last commit touching the script. "Last committed output" is the last commit touching that output file.

| Script | Reason | Last commit | Main output(s) | Last committed output |
|---|---|---|---|---|
| 91m_essay3_h6_form499_corrected | 7/28-chain H6 on the any-5.02 outcome. Its MDE/TOST framing was retired (decision L4). | aa2ed2d (2026-07-28) | `outputs/h6_form499_corrected_regression_results.txt`, `h6_form499_corrected_ame_by_window.csv`, `h6_form499_corrected_power_analysis.csv` | none (untracked on disk) |
| 91_essay3_governance_regressions | SIC-era logit by window; includes the immediate_disclosure mediator (decision L3) | d3ef2fe (2026-06-30) | TABLE2_turnover_summary.csv, TABLE4_ownership_results.txt, with_mediator_model_coefficients.csv | — |
| 91b_essay3_reduced_form_mediation | Reduced form plus mediator first stage; source of the 14.52pp first stage | d3ef2fe (2026-06-30) | `essay3_governance/reduced_form_h6_results.csv`, `mediator_first_stage_results.csv` | aa2ed2d / afa618a |
| 91c_essay3_mediation_bootstrap | Mediation (decision L3: none) | d3ef2fe (2026-06-30) | `essay3_governance/mediation_bootstrap_indirect_effects.csv` | aa2ed2d |
| 91e_essay3_h6_tost_equivalence | TOST (decision L4: none). The run_all label "confirms FCC effect is economically negligible" is withdrawn. | 5abe766 (2026-07-22) | `essay3_governance/h6_tost_equivalence_results.csv`, `H6_TOST_Equivalence_Test.txt` | aa2ed2d |
| 91f_essay3_h6_firm_size_heterogeneity | Quartile heterogeneity on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/h6_firm_size_heterogeneity_full.csv` | aa2ed2d |
| 91g_extract_reduced_form_controls | Controls table from the legacy reduced form | 5abe766 (2026-07-22) | `essay3_governance/h6_reduced_form_all_coefficients.csv` | aa2ed2d |
| 91h_essay3_cox_hazards | Cox HR 1.43 (post hoc; outcome includes appointments and pay). Robustness only; now retired with its chain. | aa2ed2d (2026-07-28) | `cox_model_all_turnover.csv`, `H6_Cox_Model_Results.txt` | aa2ed2d |
| 91j_essay3_ols_lpm_and_negbin | LPM and negative binomial on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/ols_lpm_h6_results.csv`, `negative_binomial_h6_results.csv` | aa2ed2d |
| 91k_essay3_robustness_checks | Threshold and restricted-sample checks on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/robustness_check{1,2,3}_*.csv` | 5abe766 |
| 102_extended_governance_windows | Entirely Essay 3: 30/90/180-day windows on the any-5.02 outcome with the SIC treatment | faae3ee (2026-06-30) | `outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv` | aa2ed2d |
| 91_essay3_mediation_analysis | Volatility → turnover mediation (decision L3) | d3ef2fe (2026-06-30) | TABLE_Mediation_Effects_Essay3.txt, Mediation_Summary_Essay3.txt | — |

These edits were also made in `run_all.py`:
- The 91m entry is removed from `critical_keys`.
- The legacy Essay 3 files are commented out of `verify_outputs` `critical_files`, and the Query 2 outputs are added.
- The docstring and the final banner now mark 16.71pp, 14.52pp and the 7/28 H6 figures as RETIRED.
- The Query 2 chain is added as its own category.
- `LONG_RUNNING_SCRIPTS` has entries for 187, 191 and 202.

**Script 46 stays in run_all.** Script 53 merges its committed output for the legacy Essay 1/2 scripts. Removing 46 is in Tim's parking lot, pending a check that `executive_changes.csv` is committed and that 53 runs without 46.

## Hardcoded values retired in scripts that stay

| Script | Location | Value | Action |
|---|---|---|---|
| 96_economic_significance | Section 3 (`turnover_prob_increase`), report text part C | 0.053 (+5.3pp) | Set to NaN; every turnover-cost figure now prints nan. The text is marked retired. |
| 97_heterogeneous_mechanisms | Section 5 (Table E) | LPM of executive_change_30d by size quartile | Gated off with `RETIRED_ESSAY3 = True` (the loop runs over an empty list) |
| 97_heterogeneous_mechanisms | Figure 3 | `fcc_turnover = [19.23, -20.08, -29.96, 11.72]`, `timing_turnover = [-22.53, -20.58, -20.27, 5.79]` | Gated off. The existing `Essay3_Heterogeneous_Turnover.png` on disk is a legacy artifact. |
| 161_old_vs_new_exhibit | line 68 | '+16.71pp descriptive' | Marked "[RETIRED 2026-09-11: no computed source; ESSAY3_QUERY1_REPORT C1]" |
| build_essay3_appendix_all_tables | lines 130, 162 | +14.52pp | Marked retired |
| create_essay3_appendix_word | line 253 | +14.52pp | Marked retired |
| create_essay3_appendix_docx | lines 197, 211 | 14.52 | Marked retired |
| create_essay3_appendix_sequential | lines 183, 193 | 14.52 | Marked retired |

**Not run.** Per the standing rules, neither `run_all.py` nor script 158 was run. Every edited script was checked with `py_compile`.

---

# Addendum — 2026-09-11 (repo hygiene, after the README rewrite)

## Script archived

| Script | Moved to | Reason |
|---|---|---|
| `scripts/update_readme.py` | `scripts/root_dev_archive/update_readme.py` | A one-off that rewrote `README.md` in place through a hardcoded absolute path (`C:\Users\mcobp\DISSERTATION_CLONE\README.md`), string-replacing audit-era H1 values (`0.57%` → `0.649%`, `p=0.539` → `p=0.443`). Those values match neither the old README nor the current one, and the README now carries no numbers at all. It was never in `run_all.py`, and nothing references it. Moved with `git mv`, so its history is preserved. |

## Stale pointers corrected

The line `outputs/tables/appendix_v3/` names a directory that has never existed. The Essay 1 appendix tables are in **`outputs/rebuild/appendix_v3/`**, written by `scripts/158` (Word build `scripts/160`).

- Corrected in 18 committed files: `outputs/SAMPLE_ATTRITION_LEDGER.md`, `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md` and `outputs/ESSAY3_QUERY2_REPORT.md`, plus the 15 audit-era files that carry the same boilerplate tombstone block.
- `scripts/141_essay1_appendix_tables_form499.py` no longer exists. The two documents that still described it as live — `docs/DATA_QUALITY_DOCUMENTATION.md` and `outputs/STALE_RESULTS_MANIFEST.txt` — now say so and name the current generator.

None of these files is read by code: every reference is either the generator that writes it, a filename inside another script's printed output, or a line of banner text. None is a Git LFS pointer. The edits change documentation only.
