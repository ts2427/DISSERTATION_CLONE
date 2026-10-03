# Repo inventory — summary

Branch `repo-cleanup` at `76167e8` (cut from `main` 76167e8). Every file on disk under the repo root, excluding `.git/`, `venv/` and `.venv/` (a second virtualenv, 16k files). Full rows: `outputs/REPO_INVENTORY.csv`.

## Totals

| set | files | MB | LFS |
|---|---|---|---|
| all on disk | 5,566 | 2,904.8 | 113 |
| tracked | 3,862 | 2,362.0 | 113 |
| untracked (not ignored) | 683 | 134.9 | |
| ignored | 1,021 | 407.8 | |

## Directory tree (two levels)

| directory | files | tracked | MB |
|---|---|---|---|
| `(root)` | 367.0 | 9.0 | 62.8 |
| `.claude/worktrees` | 676.0 | 0.0 | 132.8 |
| `.devcontainer/` | 1.0 | 1.0 | 0.0 |
| `.vscode/` | 1.0 | 1.0 | 0.0 |
| `Dashboard/` | 2.0 | 2.0 | 0.0 |
| `Dashboard/__pycache__` | 3.0 | 0.0 | 0.0 |
| `Dashboard/pages` | 27.0 | 15.0 | 0.4 |
| `Data/` | 8.0 | 7.0 | 14.8 |
| `Data/Articles` | 149.0 | 75.0 | 102.5 |
| `Data/Articles_Notes` | 314.0 | 0.0 | 2.1 |
| `Data/JSON Files` | 19.0 | 19.0 | 1817.6 |
| `Data/audit_analytics` | 4.0 | 4.0 | 0.3 |
| `Data/edgar` | 2376.0 | 2363.0 | 280.4 |
| `Data/enrichment` | 9.0 | 9.0 | 0.5 |
| `Data/fcc` | 3.0 | 3.0 | 0.1 |
| `Data/processed` | 44.0 | 33.0 | 267.7 |
| `Data/raw` | 1.0 | 1.0 | 0.0 |
| `Data/wrds` | 15.0 | 14.0 | 84.7 |
| `Data/wrds_v4` | 19.0 | 18.0 | 39.8 |
| `Data/yfinance` | 1.0 | 0.0 | 37.3 |
| `Notebooks/` | 4.0 | 4.0 | 0.1 |
| `__pycache__/` | 2.0 | 0.0 | 0.1 |
| `article_monitors/` | 17.0 | 17.0 | 0.5 |
| `docs/` | 4.0 | 3.0 | 0.0 |
| `docs/claude` | 11.0 | 11.0 | 0.2 |
| `drafts/` | 6.0 | 0.0 | 0.0 |
| `outputs/` | 165.0 | 82.0 | 6.0 |
| `outputs/audit` | 10.0 | 10.0 | 0.0 |
| `outputs/defense_prep` | 18.0 | 12.0 | 0.1 |
| `outputs/defense_supplement` | 10.0 | 6.0 | 0.3 |
| `outputs/economic_significance` | 5.0 | 5.0 | 0.3 |
| `outputs/essay2` | 12.0 | 12.0 | 0.7 |
| `outputs/essay2_expanded` | 5.0 | 5.0 | 0.3 |
| `outputs/essay2_final` | 11.0 | 11.0 | 0.5 |
| `outputs/essay3` | 4.0 | 4.0 | 0.3 |
| `outputs/essay3_appendix` | 5.0 | 5.0 | 0.1 |
| `outputs/essay3_figures` | 2.0 | 2.0 | 0.1 |
| `outputs/essay3_q1` | 42.0 | 42.0 | 1.5 |
| `outputs/essay3_q2` | 124.0 | 118.0 | 9.1 |
| `outputs/essay3_q3` | 10.0 | 9.0 | 0.1 |
| `outputs/essay3_q4` | 18.0 | 16.0 | 0.1 |
| `outputs/essay3_revised` | 7.0 | 7.0 | 0.4 |
| `outputs/essay3_v4` | 52.0 | 52.0 | 6.3 |
| `outputs/figures` | 29.0 | 29.0 | 8.0 |
| `outputs/heterogeneous_analysis` | 3.0 | 3.0 | 0.3 |
| `outputs/logs` | 69.0 | 34.0 | 7.4 |
| `outputs/ml_models` | 21.0 | 21.0 | 3.0 |
| `outputs/rebuild` | 92.0 | 82.0 | 2.1 |
| `outputs/rebuild_v4` | 54.0 | 54.0 | 2.4 |
| `outputs/recovered` | 1.0 | 0.0 | 0.0 |
| `outputs/retired_originals_20260902` | 9.0 | 9.0 | 0.1 |
| `outputs/robustness` | 25.0 | 25.0 | 1.2 |
| `outputs/scm_crsp_comprehensive` | 2.0 | 2.0 | 0.0 |
| `outputs/scm_crsp_with_sprint` | 2.0 | 2.0 | 0.0 |
| `outputs/scm_firm_by_firm` | 16.0 | 15.0 | 1.1 |
| `outputs/tables` | 225.0 | 218.0 | 2.5 |
| `outputs/validation` | 4.0 | 4.0 | 0.3 |
| `scripts/` | 324.0 | 312.0 | 3.7 |
| `scripts/__pycache__` | 62.0 | 0.0 | 1.6 |
| `scripts/archive` | 12.0 | 12.0 | 0.1 |
| `scripts/ml_models` | 4.0 | 4.0 | 0.0 |
| `scripts/root_dev_archive` | 18.0 | 18.0 | 0.1 |
| `tests/` | 2.0 | 2.0 | 0.0 |
| `tests/integration` | 1.0 | 1.0 | 0.0 |
| `tests/unit` | 3.0 | 3.0 | 0.0 |
| `validation/nlp_validation` | 2.0 | 2.0 | 0.0 |
| `validation/scripts` | 3.0 | 3.0 | 0.0 |

## By extension

| extension | files | MB |
|---|---|---|
| `.json` | 320.0 | 1893.4 |
| `.csv` | 784.0 | 430.9 |
| `.pdf` | 148.0 | 190.5 |
| `.htm` | 1992.0 | 69.6 |
| `.txt` | 523.0 | 68.5 |
| `.xml` | 1.0 | 63.8 |
| `.pkl` | 17.0 | 60.6 |
| `.png` | 141.0 | 29.8 |
| `.pptx` | 8.0 | 25.7 |
| `.docx` | 89.0 | 23.5 |
| `.xlsx` | 23.0 | 15.5 |
| `.gz` | 136.0 | 12.4 |
| `.py` | 600.0 | 6.7 |
| `.md` | 590.0 | 6.7 |
| `.log` | 64.0 | 3.4 |
| `.pyc` | 79.0 | 1.9 |
| `.lock` | 2.0 | 1.2 |
| `.html` | 12.0 | 0.4 |
| `.eps` | 2.0 | 0.1 |
| `(none)` | 13.0 | 0.0 |
| `.ini` | 4.0 | 0.0 |
| `.npy` | 2.0 | 0.0 |
| `.psv` | 5.0 | 0.0 |
| `.sh` | 1.0 | 0.0 |
| `.tex` | 8.0 | 0.0 |
| `.toml` | 2.0 | 0.0 |

## 25 largest files

| path | MB | tracked | LFS | category |
|---|---|---|---|---|
| `Data/JSON Files/nvdcve-2.0-2024.json` | 197.6 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2023.json` | 187.5 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2022.json` | 176.0 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2021.json` | 174.7 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2020.json` | 146.5 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2025.json` | 134.7 | yes | yes | ARCHIVE |
| `Data/processed/chronology_cleaned_full.csv` | 125.0 | no | no | IGNORED |
| `Data/JSON Files/nvdcve-2.0-2019.json` | 111.4 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2018.json` | 98.7 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2017.json` | 93.9 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2016.json` | 66.1 | yes | yes | ARCHIVE |
| `Data/edgar/form499_registry.xml` | 63.8 | yes | yes | KEEP-RUN |
| `Data/JSON Files/nvdcve-2.0-2013.json` | 57.9 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2014.json` | 53.1 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2015.json` | 52.5 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2012.json` | 52.3 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2010.json` | 45.7 | yes | yes | ARCHIVE |
| `Data/wrds/crsp_daily_returns.csv` | 45.7 | yes | yes | KEEP-RUN |
| `Data/JSON Files/nvdcve-2.0-2011.json` | 45.3 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2008.json` | 43.6 | yes | yes | ARCHIVE |
| `Data/JSON Files/nvdcve-2.0-2009.json` | 42.3 | yes | yes | ARCHIVE |
| `Data/edgar/cik-lookup-data.txt` | 40.9 | yes | yes | KEEP-RUN |
| `Data/JSON Files/nvdcve-2.0-2007.json` | 37.7 | yes | yes | ARCHIVE |
| `Data/yfinance/prices_cache.pkl` | 37.3 | no | no | IGNORED |
| `Data/wrds_v4/crsp_dsf.csv` | 36.5 | yes | yes | KEEP-RUN |

## Untracked and ignored files (reported only; this query never deletes them)

Grouped by directory. Candidates Tim may want in the repo are flagged.

| directory | untracked | ignored | MB | examples |
|---|---|---|---|---|
| `.` | 0 | 358 | 62.1 | `TSpivey Dissertation Proposal.pptx`, `Essay 1 (6) (1) (1).docx`, `Essay 1 (6) (1) (1)_UPDATED.docx` |
| `.claude/worktrees/agent-aad33f2c4403479f4` | 20 | 0 | 0.9 | `uv.lock`, `cik_research_framework.json`, `run_all.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/.claude` | 1 | 0 | 0.0 | `settings.local.json` |
| `.claude/worktrees/agent-aad33f2c4403479f4/.devcontainer` | 1 | 0 | 0.0 | `devcontainer.json` |
| `.claude/worktrees/agent-aad33f2c4403479f4/.vscode` | 1 | 0 | 0.0 | `settings.json` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Dashboard` | 2 | 0 | 0.0 | `app.py`, `utils.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Dashboard/pages` | 15 | 0 | 0.2 | `5_Essay2_InformationAsymmetry.py`, `4_Essay1_MarketReactions.py`, `9_Conclusion.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data` | 1 | 0 | 0.2 | `DataBreaches.xlsx` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/Articles` | 75 | 0 | 95.2 | `Cybersecurity Intelligence Through Textual Data Analysis A Framework Using Machine Learning and Terrorism Datasets.pdf`, `Cybersecurity risk and corporate innovation.pdf`, `Disclosure, Liquidity, and the Cost of Capital.pdf` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/JSON Files` | 19 | 0 | 0.0 | `nvdcve-2.0-2023.json`, `nvdcve-2.0-2025.json`, `nvdcve-2.0-2022.json` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/audit_analytics` | 4 | 0 | 0.0 | `sox_404_data.csv`, `restatements.csv`, `restatements_sample.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/enrichment` | 7 | 0 | 0.0 | `industry_adjusted_returns.csv`, `breach_severity_classification.csv`, `executive_changes.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/fcc` | 3 | 0 | 0.0 | `companies_to_match_DEDUPLICATED.csv`, `companies_to_match.csv`, `fcc_data_template.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/processed` | 17 | 0 | 15.2 | `FINAL_DISSERTATION_DATASET_ENRICHED.csv`, `data_prepared_for_scm.csv`, `FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/raw` | 1 | 0 | 0.0 | `.gitkeep` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Data/wrds` | 5 | 0 | 0.0 | `crsp_daily_returns.csv`, `compustat_fundamentals.csv`, `compustat_annual.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/Notebooks` | 4 | 0 | 0.1 | `02_essay2_event_study.py`, `01_descriptive_statistics.py`, `03_essay3_information_asymmetry.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/article_monitors` | 8 | 0 | 0.2 | `monitor_2026-06-08.md`, `monitor_2026-07-27.md`, `monitor_2026-07-20.md` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs` | 10 | 0 | 0.2 | `reasoning_pass_254_results.json`, `ESSAY1_APPENDIX_TABLES.md`, `scm_mahalanobis_results.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/audit` | 10 | 0 | 0.0 | `README.md`, `audit_comprehensive.csv`, `audit_data_quality.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/defense_prep` | 11 | 0 | 0.1 | `h2_firm_level_data.csv`, `cik_1001082_full_detail.csv`, `ri_placebo_distribution.npy` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/economic_significance` | 5 | 0 | 0.3 | `Economic_Impact_Breakdown.png`, `FCC_Cost_by_Firm_Size.png`, `Governance_Cost_Components.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2/figures` | 3 | 0 | 0.7 | `fig1_correlation_heatmap.png`, `FIGURE_CAR_BY_TIMING.png`, `FIGURE_CAR_BY_FCC.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2/tables` | 9 | 0 | 0.0 | `table6_regression_full_output.txt`, `table5_correlations.csv`, `TABLE_MAIN_REGRESSIONS.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2_expanded/figures` | 2 | 0 | 0.2 | `fig_car_by_fcc.png`, `fig_car_by_timing.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2_expanded/tables` | 3 | 0 | 0.0 | `regression_full_output.txt`, `table1_descriptives.csv`, `table_sample_comparison.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2_final/figures` | 3 | 0 | 0.5 | `FIGURE1_fcc_comparison.png`, `FIGURE3_coefficient_comparison.png`, `FIGURE2_breach_severity.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay2_final/tables` | 8 | 0 | 0.0 | `FULL_REGRESSION_OUTPUT.txt`, `H1_Comprehensive_Power_Analysis.txt`, `H1_Power_Analysis_Summary.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay3/figures` | 2 | 0 | 0.3 | `fig_volatility_by_timing.png`, `fig_interaction.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay3/tables` | 2 | 0 | 0.0 | `regression_full_output.txt`, `table1_descriptive_stats.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay3_figures` | 2 | 0 | 0.1 | `Figure2_Turnover_by_Timing_Regulatory.png`, `Figure1_Turnover_by_Window.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay3_revised/figures` | 2 | 0 | 0.3 | `FIGURE1_volatility_comparisons.png`, `FIGURE3_coefficient_comparison.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/essay3_revised/tables` | 5 | 0 | 0.0 | `FULL_REGRESSION_OUTPUT.txt`, `TABLE1_descriptives.csv`, `TABLE2_composition.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/figures` | 26 | 0 | 7.6 | `CONCEPTUAL_05_INTEGRATED_FLOW.png`, `CONCEPTUAL_03_THREE_ESSAY_MODELS.png`, `CONCEPTUAL_04_POLICY_OPTIONS.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/heterogeneous_analysis` | 3 | 0 | 0.3 | `Essay3_Heterogeneous_Turnover.png`, `Essay2_Heterogeneous_Volatility.png`, `Essay1_FCC_Effect_by_Size.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/logs` | 34 | 0 | 1.7 | `analysis_log_20260303_104345.txt`, `analysis_log_20260303_104950.txt`, `analysis_log_20260303_104116.txt` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/ml_models` | 17 | 0 | 1.3 | `pred_vs_actual_random_forest.png`, `ols_vs_ml_importance_comparison.png`, `predictions_vs_actual_car30d.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/ml_models/trained_models` | 4 | 0 | 1.6 | `rf_essay3_volatility.pkl`, `rf_essay2_car30d.pkl`, `gb_essay2_car30d.pkl` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/robustness/figures` | 4 | 0 | 0.7 | `R04_standard_errors.png`, `R03_sample_restrictions.png`, `R02_timing_thresholds.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/robustness/tables` | 21 | 0 | 0.5 | `FIGURE_B3_sample_restrictions.png`, `FIGURE_B2_timing_thresholds.png`, `FIGURE_B4_standard_errors.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/scm_crsp_comprehensive` | 2 | 0 | 0.0 | `firm_effects_with_controls.csv`, `scm_crsp_firm_results.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/scm_crsp_with_sprint` | 2 | 0 | 0.0 | `scm_crsp_sprint_proxy_results.csv`, `consolidated_by_company.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/scm_firm_by_firm` | 15 | 0 | 1.1 | `scm_firm_effects_distribution.png`, `scm_permutation_distribution.csv`, `scm_aggregate_gaps_over_time.png` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/tables` | 46 | 0 | 0.1 | `TABLE1_COMBINED.txt`, `table4_essay3_regressions.tex`, `TABLE1_PANEL_D_by_timing.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/tables/essay2` | 22 | 0 | 0.7 | `DIAGNOSTICS_residual_plots_model1.png`, `DIAGNOSTICS_VIF_summary.txt`, `H1_TOST_Equivalence_Test.txt` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/tables/essay3` | 9 | 0 | 0.0 | `Mediation_Summary_Essay3.txt`, `TABLE2_volatility_changes.txt`, `FCC_Causal_ID_Summary_Volatility.txt` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/tables/essay3_governance` | 22 | 0 | 0.0 | `H6_TOST_Equivalence_Test.txt`, `h6_reduced_form_all_coefficients.csv`, `h6_firm_size_heterogeneity_full.csv` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/tables/robustness` | 3 | 0 | 0.0 | `TABLE_Falsification_Tests.txt`, `TABLE_Low_R2_Sensitivity.txt`, `TABLE_Market_Model_Sensitivity.txt` |
| `.claude/worktrees/agent-aad33f2c4403479f4/outputs/validation` | 4 | 0 | 0.3 | `feature_importance_combined.png`, `feature_importance_by_category.png`, `dissertation_robustness_section.txt` |
| `.claude/worktrees/agent-aad33f2c4403479f4/scripts` | 154 | 0 | 1.5 | `80_essay1_car_regressions.py`, `update_proposal_documents.py`, `create_conceptual_models.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/scripts/archive` | 12 | 0 | 0.1 | `25_essay2_EXPANDED_sample.py`, `26_essay3_information_asymmetry.py`, `22_essay2_comprehensive_analysis.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/scripts/ml_models` | 4 | 0 | 0.0 | `breach_impact_model.py`, `feature_importance.py`, `model_evaluation.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/tests` | 2 | 0 | 0.0 | `conftest.py`, `__init__.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/tests/integration` | 1 | 0 | 0.0 | `__init__.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/tests/unit` | 3 | 0 | 0.0 | `test_nlp_classifier.py`, `test_data_validation.py`, `__init__.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/validation/nlp_validation` | 2 | 0 | 0.0 | `nlp_classifier.py`, `__init__.py` |
| `.claude/worktrees/agent-aad33f2c4403479f4/validation/scripts` | 3 | 0 | 0.0 | `02_generate_validation_report.py`, `01_run_nlp_validation.py`, `00_sample_breaches_for_validation.py` |
| `Dashboard/__pycache__` | 0 | 3 | 0.0 | `app.cpython-313.pyc`, `utils.cpython-313.pyc`, `utils.cpython-310.pyc` |
| `Dashboard/pages/__pycache__` | 0 | 12 | 0.2 | `4_Essay1_MarketReactions.cpython-313.pyc`, `5_Essay2_InformationAsymmetry.cpython-313.pyc`, `8_Conclusion.cpython-313.pyc` |
| `Data` | 0 | 1 | 11.9 | `Data_Breach_Chronology_Test.xlsx` |
| `Data/Articles` | 0 | 74 | 7.2 | `Data Breach Reporting Requirements effective March 13 2024.txt`, `The Economics of Privacy.txt`, `Bridging the human factor gap Fortifying employees through training, culture, and behavioral intervention.txt` |
| `Data/Articles_Notes` | 0 | 314 | 2.1 | `ARTICLE_03_Cross_Cultural_Transparency_COMPREHENSIVE.md`, `ARTICLE_02_2011_Cost_Data_Breach_COMPREHENSIVE.md`, `ARTICLE_04_Absorptive_Capacity_Scale_COMPREHENSIVE.md` |
| `Data/edgar` | 0 | 11 | 11.6 | `xbrl_facts_cache.pkl`, `company_tickers_exchange.json`, `wayback_ticker_snapshots.pkl` |
| `Data/edgar/8k_item5_02_cache` | 0 | 2 | 9.1 | `submissions_cache.pkl`, `cache_index.pkl` |
| `Data/processed` | 0 | 10 | 230.2 | `chronology_cleaned_full.csv`, `chronology_bso_FINAL.csv`, `chronology_bso_with_stock.csv` |
| `Data/processed/rebuild` | 0 | 1 | 0.0 | `CANONICAL_V3_LINEAGE.md` |
| `Data/wrds` | 0 | 1 | 25.6 | `crsp_quotes_topup.csv` |
| `Data/wrds_v4/_aborted_run_1` | 1 | 0 | 0.1 | `comp_company.csv` |
| `Data/yfinance` | 0 | 1 | 37.3 | `prices_cache.pkl` |
| `__pycache__` | 0 | 2 | 0.1 | `run_all.cpython-313.pyc`, `run_all.cpython-310.pyc` |
| `docs` | 0 | 1 | 0.0 | `entity_resolution_audit.md` |
| `drafts` | 0 | 6 | 0.0 | `e3_outcome.md`, `e3_sample.md`, `e3_estimation.md` |
| `outputs` | 1 | 82 | 4.7 | `REPO_INVENTORY.csv`, `172_att_exclusion_rerun.log`, `MATCH_SOURCE_BUNDLE_FINAL.md` |
| `outputs/defense_prep` | 0 | 6 | 0.0 | `h2_firm_level_model_summary.txt`, `task2_deduplication_summary.txt`, `h2_robustness_comprehensive_summary.txt` |
| `outputs/defense_supplement` | 0 | 4 | 0.1 | `deck_exhibits.log`, `e1_notification_anchored.log`, `e3_randomization_inference.log` |
| `outputs/essay3_q2` | 2 | 4 | 0.1 | `crsp_drop_controls_worksheet.csv`, `201_stdout.txt`, `crsp_drop_nominations.csv` |
| `outputs/essay3_q3` | 1 | 0 | 0.1 | `242_pull.log` |
| `outputs/essay3_q4` | 2 | 0 | 0.0 | `243_readouts.log`, `244_tables.log` |
| `outputs/logs` | 0 | 35 | 5.6 | `analysis_log_20260728_150354.txt`, `analysis_log_20260728_135904.txt`, `analysis_log_20260728_134917.txt` |
| `outputs/rebuild` | 0 | 10 | 0.1 | `INTEXT_TABLES_4_5.docx`, `GATE1_SUMMARY.md`, `GATE2_ADJACENCY_SHEET.md` |
| `outputs/recovered` | 0 | 1 | 0.0 | `20_final_comprehensive_merge_FROM_07abde7.py` |
| `outputs/scm_firm_by_firm` | 0 | 1 | 0.0 | `SCM_RESULTS_SUMMARY.txt` |
| `outputs/tables` | 0 | 4 | 0.0 | `TABLE_B7_Alternative_Explanations.docx`, `essay1_null_sensitivity_analysis.txt`, `FE_H1_H4_RESULTS.txt` |
| `outputs/tables/essay3_governance` | 0 | 3 | 0.0 | `H6_CANONICAL_SUMMARY.txt`, `CFO_Turnover_Placebo_Test.txt`, `H6_Cox_Model_Results.txt` |
| `scripts` | 0 | 12 | 0.1 | `134_chronology_through_pipeline.py`, `136_exhaustive_sweep.py`, `132_fill_chronology_blanks.py` |
| `scripts/__pycache__` | 0 | 62 | 1.6 | `217_v4_offline_tests.cpython-313.pyc`, `163_essay2_rerun_form499.cpython-313.pyc`, `220_essay3_v4_classifier_v2.cpython-313.pyc` |

Flagged for a decision: `Data/wrds/crsp_quotes_topup.csv`, `outputs/rebuild/INTEXT_TABLES_4_5.docx` (`crsp_quotes_topup.csv` is CRSP-licensed and must stay out of the public repo; `INTEXT_TABLES_4_5.docx` is written by live step 160 and ignored by `*.docx`).
