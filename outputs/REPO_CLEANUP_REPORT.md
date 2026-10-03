# Repo cleanup — Stage 1 report (read-only)

Branch `repo-cleanup` at `76167e8`, cut from `main` (76167e8). Nothing moved, deleted or edited. `defense-final` (902a8ea) untouched. Inventory: `outputs/REPO_INVENTORY.csv`; summary: `outputs/REPO_INVENTORY_SUMMARY.md`.

## How the classification was made

- **Live steps**: the 65 uncommented `run_all.py` tuples, plus 8 helper modules they load (found by AST: `spec_from_file_location`, `Path("scripts/...")`, runpy), plus 254.
- **read/written by a live step**: AST string literals of every live script and helper matched against each file (full path, path suffix, directory prefix of two or more levels, glob, or a bare filename whose parent directory the script names). Patterns whose filename part is all wildcard (f-string `*/*`) are ignored. **written** = the file was rewritten during the verified clean-clone run at 902a8ea (mtime after its start); the writer is the matching script. The gates 210 and 217 are excluded from the read test because they read every baseline file by scope. This is a static heuristic: Stage 2 D5 (fresh-clone run) is the real test.
- **B1 rule as applied**: an ARCHIVE candidate referenced by a kept *script* (not `run_all.py`, whose remaining mentions are comments and its printed summary) moves to ASK; one cited only by kept *docs* stays ARCHIVE and is listed under B2 so the citation can be repointed to `archive/`; any reference moves a REMOVE-LEGACY candidate to ASK. Read literally ("any hit to ASK"), B1 sent 717 files to ASK - mostly retired scripts named in RETIREMENT_LEDGER.md - and left B2 empty by construction, so this reading was used instead.

## Counts per category (tracked files)

| category | files | MB | LFS objects |
|---|---|---|---|
| KEEP-RUN | 2,764 | 389.1 | 24 |
| KEEP-CITED | 172 | 8.4 | 0 |
| KEEP-AUDIT | 21 | 0.4 | 0 |
| KEEP-COMMITTEE | 27 | 2.5 | 1 |
| ARCHIVE | 716 | 1,860.4 | 88 |
| REMOVE-LEGACY | 0 | 0.0 | 0 |
| ASK | 162 | 101.3 | 0 |
| **total** | **3,862** | **2,362.0** | **113** |

## ASK (162 files, 101.3 MB)

### `./` (3 files, 0.6 MB)

*Reason:* tooling / environment config not used by run_all.py

`pyproject.toml`, `pytest.ini`, `uv.lock`

### `.devcontainer/` (1 files, 0.0 MB)

*Reason:* tooling / environment config not used by run_all.py

`devcontainer.json`

### `.vscode/` (1 files, 0.0 MB)

*Reason:* tooling / environment config not used by run_all.py

`settings.json`

### `Dashboard/` (1 files, 0.0 MB)

*Reason:* listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table

`app.py`

### `Dashboard/pages/` (7 files, 0.1 MB)

*Reason:* listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table

`0_Research_Story.py`, `1_Natural_Experiment.py`, `3_Data_Landscape.py`, `5_Essay2_InformationAsymmetry.py`, `6_Essay3_GovernanceResponse.py`, `8_Key_Findings.py`, `9_Conclusion.py`

### `Data/Articles/` (75 files, 95.2 MB)

*Reason:* literature PDFs (source reading, possibly copyrighted): keep, archive, or untrack?

`2010_Annual_Study_Data_Breach.pdf`, `2011_US_CODB_FINAL_5.pdf`, `A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets.pdf`, `A cross-cultural analysis of transparency the interplay of law, privacy policies, and user perceptions.pdf`, `A measure of absorptive capacity Scale development and validation.pdf`, `Advancing cybersecurity and privacy with artificial intelligence current trends and future research directions.pdf`, `Bridging the human factor gap Fortifying employees through training, culture, and behavioral intervention.pdf`, `Common risk factors in the returns on stocks and bonds.pdf`, `Corporate Financing and Investment Decisions When Firms Have Informationthat Investors Do Not Have.pdf`, `Corporate communication and likelihood of data breaches.pdf`, `Corporate cybersecurity risk and data breaches A systematic review of empirical research.pdf`, `Corporate governance, chief executive officer compensation, and firm performance.pdf`, `Crisis response and crisis timing strategies, two sides of the same coin.pdf`, `Cybersecurity Intelligence Through Textual Data Analysis A Framework Using Machine Learning and Terrorism Datasets.pdf`, `Cybersecurity Risks and Incidents Disclosure  A Literature Review.pdf`, `Cybersecurity risk and corporate innovation.pdf`, `Data Breach Announcements and Stock Market Reactions A Matter of Timing (1).pdf`, `Data Breach Reporting Requirements effective March 13 2024.pdf`, `Data breach disclosures and stock price crash risk Evidence from data breach notification laws.pdf`, `Digital Battlegrounds The Power Dynamics and Governance of Contemporary Platforms.pdf`, `Digital platform ecosystem governance of private companies Building blocks and a research agenda based on a multidisciplinary, systematic literature review.pdf`, `Disclosure, Liquidity, and the Cost of Capital.pdf`, `Do Managers Withhold Bad News.pdf`, `Do security breaches matter The shareholder puzzle.pdf`, `Does Information Asymmetry Affect Firm Disclosure Evidence from Mergers and Acquisitions of Financial Institutions.pdf`, `Dynamic Capabilities and Strategic Management.pdf`, `Empirical evidence on disclosing cyber breaches in an 8-K report Initial exploratory evidence.pdf`, `Equivalence Testing for Psychological Research a Tutorial.pdf`, `Estimating Standard Errors in Finance Panel Data Sets Comparing Approaches.pdf`, `Estimating the market impact of security breach announcements on firm values.pdf`, `FCC Updates Data Breach Notification Rules.pdf`, `Governing digital platform ecosystems for social options.pdf`, `Greedy Function Approximation A Gradient Boosting Machine.pdf`, `HACKED Understanding the stock market response to cyberattacks.pdf`, `Handling Censoring and Censored Data in Survival Analysis A Standalone Systematic Literature Review.pdf`, `Hard-to-Value Stocks, Behavioral Biases, and Informed Trading.pdf`, `How Crisis Management Strategies Address Stakeholders' Sociocognitive Concerns and Organizations' Social Evaluations.pdf`, `Hybrid governance of digital platforms Exploring complementarities and tensions in the governance of peer relationships.pdf`, `Hype and heavy tails A closer look at data breaches.pdf`, `Information Processing as an Integrating Concept in Organizational Design (1).pdf`, `Insider threat paradox in security policies.pdf`, `Institutionalized Organizations Formal Structure as Myth and Ceremony (1).pdf`, `Is there a cost to privacy breaches An event study.pdf`, `Job Market Signaling.pdf`, `Mandatory IFRS reporting and changes in enforcement.pdf`, `NECESSITY AS THE MOTHER OF 'GREEN' INVENTIONS INSTITUTIONAL PRESSURES AND ENVIRONMENTAL INNOVATIONS (1).pdf`, `Protecting Organization Reputations During a Crisis The Development and Application of Situational Crisis Communication Theory.pdf`, `Random Forests.pdf`, `Reluctant Disclosure and Transparency Evidence from Environmental Disclosures.pdf`, `Risk management, firm reputation, and the impact of successful cyberattacks on target firms.pdf`, `Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties.pdf`, `Stock market effects of major cyber-attacks evidence for breached and cybersecurity listed firms..pdf`, `Stock-market disruptions and corporate disclosure policies.pdf`, `Taking account of time The application of event history analysis to leadership research.pdf`, `The Dynamics of Stock Market Responses Following the Cyber-Attacks News Evidence from Event Study.pdf`, `The Economics of Privacy.pdf`, `The Effect of Internet Security Breach Announcements on Market Value Capital Market Reactions for Breached Firms and Internet Security Developers.pdf`, `The Informativeness of Sentiment Types in Risk Factor Disclosures Evidence from Firms with Cybersecurity Breaches.pdf`, `The Iron Cage Revisited Institutional Isomorphism and Collective Rationality in Organizational Fields (1).pdf`, `The Market for Lemons Quality Uncertainty and the Market Mechanism.pdf`, `The Politics of Risk in the Digital Services Act.pdf`, `The Stakeholder Theory of the Corporation Concepts, Evidence, and Implications.pdf`, `The economic cost of publicly announced information security breaches empirical evidence from the stock market.pdf`, `The impact of cyber threats on environmental, social, and governance performance.pdf`, `The unintended cost of data breach notification laws Evidence from managerial bad news hoarding.pdf`, `Theory of the firm Managerial behavior, agency costs and ownership structure.pdf`, `Time Dependence in the Cox Proportional Hazard Model as a Theory Development Opportunity A Step-by-Step Guide.pdf`, `Time to break up The case for tailor-made digital platform regulation based on platform-governance standard types.pdf`, `Toward a theory of stakeholder identification and salience Defining the principle of who and what really counts.pdf`, `Transient Customer Response to Data Breaches of Their Information.pdf`, `Understanding Data Breach from a Global Perspective Incident Visualization and Data Protection Law Review.pdf`, `Using Daily Stock Returns The Case of Event Studies.pdf`, `Why Firms Voluntarily Disclose Bad News.pdf`, `cost-of-a-data-breach-2025-full-report.pdf`, `desktop.ini`

### `Data/processed/` (2 files, 3.2 MB)

- `FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv` - was ARCHIVE; referenced by kept code: scripts/186_essay3_q2_chain_reconciliation.py
- `FINAL_DISSERTATION_DATASET_WITH_CVSS.csv` - was REMOVE-LEGACY; referenced by kept doc: outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv, run_all.py

### `outputs/` (4 files, 0.0 MB)

- `ESSAY1_APPENDIX_TABLES_FORM499.md` - was ARCHIVE; referenced by kept code: scripts/186_essay3_q2_chain_reconciliation.py
- `PENDING_REBASELINE.md` - was ARCHIVE; referenced by kept code: scripts/193_essay3_q2_pending_rebaseline.py
- `SAMPLE_ATTRITION_LEDGER.md` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py, scripts/193_essay3_q2_pending_rebaseline.py, scripts/186_essay3_q2_chain_reconciliation.py
- `STALE_RESULTS_MANIFEST.txt` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py

### `outputs/logs/` (34 files, 1.7 MB)

*Reason:* was REMOVE-LEGACY; referenced by kept doc: outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv

`analysis_log_20260125_113431.txt`, `analysis_log_20260125_114613.txt`, `analysis_log_20260125_115139.txt`, `analysis_log_20260125_122005.txt`, `analysis_log_20260125_140027.txt`, `analysis_log_20260125_140404.txt`, `analysis_log_20260125_140549.txt`, `analysis_log_20260125_144204.txt`, `analysis_log_20260125_151726.txt`, `analysis_log_20260125_172819.txt`, `analysis_log_20260213_140323.txt`, `analysis_log_20260213_140411.txt`, `analysis_log_20260213_143000.txt`, `analysis_log_20260213_151513.txt`, `analysis_log_20260213_151613.txt`, `analysis_log_20260216_190159.txt`, `analysis_log_20260216_190309.txt`, `analysis_log_20260217_171010.txt`, `analysis_log_20260217_173049.txt`, `analysis_log_20260217_173151.txt`, `analysis_log_20260217_173316.txt`, `analysis_log_20260217_174115.txt`, `analysis_log_20260217_174713.txt`, `analysis_log_20260217_175412.txt`, `analysis_log_20260217_175931.txt`, `analysis_log_20260217_180657.txt`, `analysis_log_20260218_095337.txt`, `analysis_log_20260221_164058.txt`, `analysis_log_20260221_173650.txt`, `analysis_log_20260227_115733.txt`, `analysis_log_20260228_215032.txt`, `analysis_log_20260303_104116.txt`, `analysis_log_20260303_104345.txt`, `analysis_log_20260303_104950.txt`

### `outputs/retired_originals_20260902/` (1 files, 0.0 MB)

*Reason:* was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py, scripts/193_essay3_q2_pending_rebaseline.py, scripts/186_essay3_q2_chain_reconciliation.py

`SAMPLE_ATTRITION_LEDGER.md`

### `outputs/tables/essay2_appendix/` (11 files, 0.0 MB)

- `delay_quantiles.csv` - was ARCHIVE; referenced by kept code: scripts/164_essay2_rule_delay_classification.py
- `descriptives_by_treatment.csv` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py, scripts/252_defsup_deck_exhibits.py
- `design_resolution.csv` - was ARCHIVE; referenced by kept code: scripts/249_defsup_e2_delay_ladder.py, scripts/252_defsup_deck_exhibits.py, scripts/165_essay2_inference_ladder.py
- `dv_correlations.csv` - was ARCHIVE; referenced by kept code: scripts/166_essay2_spec_grid.py
- `events_by_year.csv` - was ARCHIVE; referenced by kept code: scripts/164_essay2_rule_delay_classification.py
- `fixed_effects.csv` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py
- `gradient_grid.csv` - was ARCHIVE; referenced by kept code: scripts/166_essay2_spec_grid.py
- `inference_ladder.csv` - was ARCHIVE; referenced by kept code: scripts/249_defsup_e2_delay_ladder.py, scripts/252_defsup_deck_exhibits.py, scripts/165_essay2_inference_ladder.py
- `nested_models.csv` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py
- `records_per_event.csv` - was ARCHIVE; referenced by kept code: scripts/164_essay2_rule_delay_classification.py
- `size_quartiles.csv` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py

### `scripts/` (11 files, 0.2 MB)

- `105_complexity_index_heterogeneity.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `106_information_environment_composite.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `80_essay1_car_regressions.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `99_cvss_complexity_heterogeneity.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `99_cvss_complexity_heterogeneity_BROKEN_June22.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `99_cvss_complexity_heterogeneity_essay2.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `create_regression_formulas_document.py` - was ARCHIVE; referenced by kept code: scripts/163_essay2_rerun_form499.py
- `create_regression_tables_word.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `h1_comprehensive_power_analysis.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `update_existing_proposal.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table
- `update_proposal_documents.py` - listed in t24_a4_deadline_scan.csv: scripts/164 A4 scans scripts/*.py and Dashboard/**/*.py, so moving this file would change a cited Essay 2 table

### `tests/` (2 files, 0.0 MB)

*Reason:* test / NLP-validation harness of the pre-rebuild classifier; not run by run_all.py

`__init__.py`, `conftest.py`

### `tests/integration/` (1 files, 0.0 MB)

*Reason:* test / NLP-validation harness of the pre-rebuild classifier; not run by run_all.py

`__init__.py`

### `tests/unit/` (3 files, 0.0 MB)

*Reason:* test / NLP-validation harness of the pre-rebuild classifier; not run by run_all.py

`__init__.py`, `test_data_validation.py`, `test_nlp_classifier.py`

### `validation/nlp_validation/` (2 files, 0.0 MB)

*Reason:* test / NLP-validation harness of the pre-rebuild classifier; not run by run_all.py

`__init__.py`, `nlp_classifier.py`

### `validation/scripts/` (3 files, 0.0 MB)

*Reason:* test / NLP-validation harness of the pre-rebuild classifier; not run by run_all.py

`00_sample_breaches_for_validation.py`, `01_run_nlp_validation.py`, `02_generate_validation_report.py`


## REMOVE-LEGACY (0 files, 0.0 MB)

None.

## ARCHIVE (to be moved to archive/ with the same relative path) (716 files, 1860.4 MB)

### `Dashboard/` (1 files, 0.0 MB)

*Reason:* pre-audit dashboard / notebook (stale numbers)

`utils.py`

### `Dashboard/pages/` (8 files, 0.1 MB)

*Reason:* pre-audit dashboard / notebook (stale numbers)

`10_Raw_Data_Explorer.py`, `11_Data_Dictionary.py`, `2_Sample_Validation.py`, `4_Essay1_MarketReactions.py`, `7_Economic_Significance.py`, `7_Robustness_Checks.py`, `8_Heterogeneity_Complete.py`, `8_Heterogeneous_Mechanisms.py`

### `Data/` (5 files, 1.4 MB)

*Reason:* pre-rebuild / superseded output or dataset

`F-F_Momentum_Factor_daily.csv`, `F-F_Research_Data_5_Factors_2x3_daily.csv`, `ex21_extraction_template.csv`, `ex21_subsidiaries_extracted.csv`, `validation_set_40_records.csv`

### `Data/JSON Files/` (19 files, 1817.6 MB)

*Reason:* pre-rebuild / superseded output or dataset

`nvdcve-2.0-2007.json` (LFS), `nvdcve-2.0-2008.json` (LFS), `nvdcve-2.0-2009.json` (LFS), `nvdcve-2.0-2010.json` (LFS), `nvdcve-2.0-2011.json` (LFS), `nvdcve-2.0-2012.json` (LFS), `nvdcve-2.0-2013.json` (LFS), `nvdcve-2.0-2014.json` (LFS), `nvdcve-2.0-2015.json` (LFS), `nvdcve-2.0-2016.json` (LFS), `nvdcve-2.0-2017.json` (LFS), `nvdcve-2.0-2018.json` (LFS), `nvdcve-2.0-2019.json` (LFS), `nvdcve-2.0-2020.json` (LFS), `nvdcve-2.0-2021.json` (LFS), `nvdcve-2.0-2022.json` (LFS), `nvdcve-2.0-2023.json` (LFS), `nvdcve-2.0-2024.json` (LFS), `nvdcve-2.0-2025.json` (LFS)

### `Data/audit_analytics/` (4 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`restatements.csv` (LFS), `restatements_sample.csv` (LFS), `sox_404_data.csv` (LFS), `sox_sample.csv` (LFS)

### `Data/enrichment/` (9 files, 0.5 MB)

*Reason:* pre-rebuild / superseded output or dataset

`README.md`, `breach_severity_classification.csv` (LFS), `executive_changes.csv`, `executive_changes_item5_02.csv`, `industry_adjusted_returns.csv` (LFS), `media_coverage.csv` (LFS), `organization_breach_summary.csv` (LFS), `prior_breach_history.csv` (LFS), `regulatory_enforcement.csv` (LFS)

### `Data/fcc/` (3 files, 0.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`companies_to_match.csv` (LFS), `companies_to_match_DEDUPLICATED.csv`, `fcc_data_template.csv` (LFS)

### `Data/processed/` (16 files, 19.6 MB)

*Reason:* pre-rebuild / superseded output or dataset

`DATA_DICTIONARY_ENRICHED.csv` (LFS), `FINAL_DATASET_DEDUPLICATED_784.csv`, `FINAL_DATASET_DEDUP_V2_CANDIDATE.csv`, `FINAL_DISSERTATION_DATASET.xlsx`, `FINAL_DISSERTATION_DATASET_CONSOLIDATED_WITH_CAR.csv`, `FINAL_DISSERTATION_DATASET_CORRECTED_CONSOLIDATED.csv`, `FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv`, `FINAL_DISSERTATION_DATASET_ENRICHED.xlsx`, `FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv`, `FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv`, `FINAL_DISSERTATION_DATASET_WITH_CORRECTED_CIK.csv`, `FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv`, `FINAL_DISSERTATION_DATASET_WITH_RESOLVED_CIK.csv`, `company_vendor_matching.xlsx`, `data_prepared_for_scm.csv`, `final_analysis_dataset.xlsx`

### `Notebooks/` (4 files, 0.1 MB)

*Reason:* pre-audit dashboard / notebook (stale numbers)

`01_descriptive_statistics.py`, `02_essay2_event_study.py`, `03_essay3_information_asymmetry.py`, `04_enrichment_analysis.py`

### `article_monitors/` (17 files, 0.5 MB)

*Reason:* literature-monitor notes (process record, not a result)

`monitor_2026-06-08.md`, `monitor_2026-06-15.md`, `monitor_2026-06-22.md`, `monitor_2026-06-29.md`, `monitor_2026-07-06.md`, `monitor_2026-07-13.md`, `monitor_2026-07-20.md`, `monitor_2026-07-27.md`, `monitor_2026-08-03.md`, `monitor_2026-08-10.md`, `monitor_2026-08-17.md`, `monitor_2026-08-24.md`, `monitor_2026-08-31.md`, `monitor_2026-09-07.md`, `monitor_2026-09-14.md`, `monitor_2026-09-21.md`, `monitor_2026-09-28.md`

### `outputs/` (50 files, 0.5 MB)

*Reason:* pre-rebuild / superseded output or dataset

`AUDIT_SCM_PVALUE_RESOLUTION.txt`, `CANONICAL_RESULTS_SUMMARY_20260722.txt`, `DATA_INTEGRITY_FIX_H2_SUMMARY.txt`, `ESSAY1_AUDIT_FINAL_INDEX.txt`, `ESSAY1_AUDIT_README.txt`, `ESSAY1_DATA_EXTRACTION_AUDIT.txt`, `ESSAY1_OUTPUT_FILES_MAP.txt`, `ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt`, `H1_timing_fcc_interaction_results.csv`, `PRC_MISSING_RECORDS_VERIFICATION_WORKSHEET.csv`, `adjudication_evidence_sheet.csv`, `all_unmatched_org_names.csv`, `calendar_month_clustering_results.csv`, `cik_corrections_detailed.csv`, `corrected_longrun_analysis_results.csv`, `essay1_results_supplements.csv`, `exact_and_subsidiary_matches.csv`, `exact_match_validation_results.csv`, `exact_matcher_validation_scores.csv`, `extended_bhar_60d_90d_results.csv`, `factor_model_robustness_market.csv`, `factor_model_robustness_results.csv`, `form499_classification_final.csv`, `form499_matched_records.csv`, `form499_unmatched_with_candidates.csv`, `full_dataset_resolution_summary.csv`, `h1_h4_form499_corrected_summary.csv`, `h1h4_abnormal_volume_results.csv`, `h2_form499_corrected_regression_summary.csv`, `h2_form499_regression_summary.csv`, `h5_form499_corrected_heterogeneity.csv`, `h6_form499_corrected_ame_by_window.csv`, `h6_form499_corrected_power_analysis.csv`, `longrun_bhar_extended_results.csv`, `longrun_bhar_results.csv`, `overlap_audit_summary.csv`, `preannouncement_648_results.csv`, `residual_duplicate_adjacent_candidates.csv`, `residual_duplicate_groups.csv`, `scm_breach_event_nn_results.csv`, `scm_firm_level_nn_results.csv`, `scm_mahalanobis_firm_level.csv`, `scm_mahalanobis_results.csv`, `scm_mahalanobis_summary.csv`, `scm_summary_nn_results.csv`, `sec_2023_rule_preliminary.csv`, `table4_computed_values.csv`, `table5_computed_values.csv`, `table7_computed_values.csv`, `validation_set_complete_resolution.csv`

### `outputs/audit/` (10 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`README.md`, `audit_comprehensive.csv` (LFS), `audit_data_quality.csv` (LFS), `audit_dataset_size.csv` (LFS), `audit_essay2_sample.csv` (LFS), `audit_essay3_sample.csv` (LFS), `audit_fcc_analysis.csv` (LFS), `audit_market_reactions_car.csv` (LFS), `audit_sample_characteristics.csv` (LFS), `audit_volatility_analysis.csv` (LFS)

### `outputs/defense_prep/` (12 files, 0.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`boost_mobile_all_observations.csv`, `canonical_fcc_firm_list.csv`, `canonical_fcc_firm_list_corrected.csv`, `cik_1001082_detailed_forensics.csv`, `cik_1001082_full_detail.csv`, `fcc_firm_roster_regression_sample.csv`, `h2_firm_level_data.csv`, `h2_leave_one_out_648_run.log`, `h2_leave_one_out_sensitivity.csv`, `near_duplicate_pairs_7day.csv`, `ri_placebo_distribution.npy`, `task5_scm_vs_ols_summary.txt`

### `outputs/economic_significance/` (5 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`Economic_Impact_Breakdown.png`, `FCC_Cost_by_Firm_Size.png`, `Governance_Cost_Components.png`, `economic_impact_summary.csv`, `economic_significance_report.txt`

### `outputs/essay2/figures/` (3 files, 0.7 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FIGURE_CAR_BY_FCC.png`, `FIGURE_CAR_BY_TIMING.png`, `fig1_correlation_heatmap.png`

### `outputs/essay2/tables/` (9 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`TABLE_MAIN_REGRESSIONS.csv` (LFS), `TABLE_ROBUSTNESS.csv` (LFS), `TABLE_SUBSAMPLES.csv` (LFS), `table1_descriptive_stats.csv` (LFS), `table2_sample_composition.csv` (LFS), `table3_univariate_disclosure.csv` (LFS), `table4_univariate_fcc.csv` (LFS), `table5_correlations.csv` (LFS), `table6_regression_full_output.txt`

### `outputs/essay2_expanded/figures/` (2 files, 0.2 MB)

*Reason:* pre-rebuild / superseded output or dataset

`fig_car_by_fcc.png`, `fig_car_by_timing.png`

### `outputs/essay2_expanded/tables/` (3 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`regression_full_output.txt`, `table1_descriptives.csv` (LFS), `table_sample_comparison.csv` (LFS)

### `outputs/essay2_final/figures/` (3 files, 0.5 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FIGURE1_fcc_comparison.png`, `FIGURE2_breach_severity.png`, `FIGURE3_coefficient_comparison.png`

### `outputs/essay2_final/tables/` (8 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FULL_REGRESSION_OUTPUT.txt`, `H1_Comprehensive_Power_Analysis.txt`, `H1_Power_Analysis_Summary.csv` (LFS), `TABLE1_descriptives.csv` (LFS), `TABLE2_composition.csv` (LFS), `TABLE3_heterogeneity.csv` (LFS), `TABLE4_univariate.csv` (LFS), `TABLE7_comparison.csv` (LFS)

### `outputs/essay3/figures/` (2 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`fig_interaction.png`, `fig_volatility_by_timing.png`

### `outputs/essay3/tables/` (2 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`regression_full_output.txt`, `table1_descriptive_stats.csv` (LFS)

### `outputs/essay3_figures/` (2 files, 0.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`Figure1_Turnover_by_Window.png`, `Figure2_Turnover_by_Timing_Regulatory.png`

### `outputs/essay3_q1/` (14 files, 0.4 MB)

*Reason:* pre-rebuild / superseded output or dataset

`183_discovery.log`, `184_tmobile_text.log`, `b3_window_8k_filings.csv`, `c4_first_stage_reconciliation.csv`, `d1_attrition_ledger.csv`, `d2_treated_orgs_essay3.csv`, `e1_tmobile_events.csv`, `e2_tmobile_502_filings.csv`, `e2_tmobile_502_handcoded.csv`, `e2_tmobile_502_text.csv`, `e2_tmobile_events_x_filings.csv`, `e3_security_title_scan.csv`, `g_constants_reconciliation.csv`, `g_h6_reestimation.csv`

### `outputs/essay3_revised/figures/` (2 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FIGURE1_volatility_comparisons.png`, `FIGURE3_coefficient_comparison.png`

### `outputs/essay3_revised/tables/` (5 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FULL_REGRESSION_OUTPUT.txt`, `TABLE1_descriptives.csv` (LFS), `TABLE2_composition.csv` (LFS), `TABLE3_univariate.csv` (LFS), `TABLE5_hypothesis_tests.csv` (LFS)

### `outputs/figures/` (26 files, 7.6 MB)

*Reason:* pre-rebuild / superseded output or dataset

`CONCEPTUAL_01_LITERATURE_GENEALOGY.png`, `CONCEPTUAL_02_OVERARCHING_MECHANISM.png`, `CONCEPTUAL_03_THREE_ESSAY_MODELS.png`, `CONCEPTUAL_04_POLICY_OPTIONS.png`, `CONCEPTUAL_05_INTEGRATED_FLOW.png`, `FIGURE_PARALLEL_TRENDS.eps`, `FIGURE_PARALLEL_TRENDS.png`, `GRAPH_Dissertation_Ecosystem.png`, `GRAPH_FCC_Turnover_Mechanism.png`, `GRAPH_Temporal_Decay_FCC_Effect.png`, `REGRESSION_Essay1_MarketReturns.png`, `REGRESSION_Essay2_Mechanisms.png`, `REGRESSION_Essay2_Volatility.png`, `REGRESSION_Essay3_Governance.png`, `REGRESSION_Overall_FCC_Comparison.png`, `correlation_matrix.png`, `enrichment_executive_turnover.png`, `enrichment_prior_breaches.png`, `enrichment_regulatory.png`, `enrichment_severity.png`, `fig1_breach_timeline.png`, `fig2_car_distribution.png`, `fig3_enrichment_highlights.png`, `fig4_heterogeneity_analysis.png`, `fig5_volatility_analysis.png`, `fig_timing_distribution.png`

### `outputs/heterogeneous_analysis/` (3 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`Essay1_FCC_Effect_by_Size.png`, `Essay2_Heterogeneous_Volatility.png`, `Essay3_Heterogeneous_Turnover.png`

### `outputs/ml_models/` (17 files, 1.4 MB)

*Reason:* pre-rebuild / superseded output or dataset

`feature_importance_car30d.csv`, `feature_importance_car30d.png`, `feature_importance_essay2_rf.csv` (LFS), `feature_importance_essay3_rf.csv` (LFS), `feature_importance_random_forest_(essay_2).png`, `feature_importance_random_forest_(essay_3).png`, `feature_importance_volatility.csv`, `feature_importance_volatility.png`, `ml_model_results.json`, `ml_model_summary.csv`, `ols_vs_ml_essay2_comparison.csv` (LFS), `ols_vs_ml_essay3_comparison.csv` (LFS), `ols_vs_ml_importance_comparison.png`, `pred_vs_actual_random_forest.png`, `predictions_vs_actual_car30d.png`, `robustness_section_template_essay2.txt`, `robustness_section_template_essay3.txt`

### `outputs/ml_models/trained_models/` (4 files, 1.6 MB)

*Reason:* pre-rebuild / superseded output or dataset

`gb_essay2_car30d.pkl`, `gb_essay3_volatility.pkl`, `rf_essay2_car30d.pkl`, `rf_essay3_volatility.pkl`

### `outputs/retired_originals_20260902/` (8 files, 0.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`AUDIT_SCM_PVALUE_RESOLUTION.txt`, `DATA_INTEGRITY_FIX_H2_SUMMARY.txt`, `ESSAY1_AUDIT_FINAL_INDEX.txt`, `ESSAY1_AUDIT_README.txt`, `ESSAY1_DATA_EXTRACTION_AUDIT.txt`, `ESSAY1_OUTPUT_FILES_MAP.txt`, `ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt`, `task5_scm_vs_ols_summary.txt`

### `outputs/robustness/figures/` (4 files, 0.7 MB)

*Reason:* pre-rebuild / superseded output or dataset

`R02_timing_thresholds.png`, `R03_sample_restrictions.png`, `R04_standard_errors.png`, `R05_fixed_effects.png`

### `outputs/robustness/tables/` (21 files, 0.5 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FIGURE_B2_timing_thresholds.png`, `FIGURE_B3_sample_restrictions.png`, `FIGURE_B4_standard_errors.png`, `R01_alternative_windows_full.csv`, `R01_alternative_windows_summary.csv`, `R02_timing_thresholds_full.csv`, `R02_timing_thresholds_summary.csv`, `R03_sample_restrictions_full.csv`, `R03_sample_restrictions_summary.csv`, `R04_standard_errors_full.csv`, `R04_standard_errors_summary.csv`, `R05_fixed_effects_summary.csv`, `TABLE_B1_alternative_windows.csv` (LFS), `TABLE_B1_detailed_results.csv` (LFS), `TABLE_B2_detailed_results.csv` (LFS), `TABLE_B2_timing_thresholds.csv` (LFS), `TABLE_B3_detailed_results.csv` (LFS), `TABLE_B3_sample_restrictions.csv` (LFS), `TABLE_B4_all_variables.csv` (LFS), `TABLE_B4_detailed_results.csv` (LFS), `TABLE_B4_standard_errors.csv` (LFS)

### `outputs/scm_crsp_comprehensive/` (2 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`firm_effects_with_controls.csv`, `scm_crsp_firm_results.csv`

### `outputs/scm_crsp_with_sprint/` (2 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`consolidated_by_company.csv`, `scm_crsp_sprint_proxy_results.csv`

### `outputs/scm_firm_by_firm/` (15 files, 1.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`TABLE_SCM_AGGREGATE_RESULTS.csv`, `TABLE_SCM_GAPS_BY_YEAR.csv`, `TABLE_SCM_TOP_20_FIRMS.csv`, `scm_aggregate_effect.png`, `scm_aggregate_gaps_over_time.png`, `scm_aggregate_statistics.csv`, `scm_all_firm_gaps.csv`, `scm_effect_distribution.png`, `scm_firm_effects_distribution.png`, `scm_firm_level_effects.png`, `scm_firm_summary_results.csv`, `scm_permutation_distribution.csv`, `scm_permutation_distribution.png`, `scm_permutation_test_distribution.png`, `scm_statistical_inference.csv`

### `outputs/tables/` (58 files, 0.1 MB)

*Reason:* pre-rebuild / superseded output or dataset

`CENCORA_SENSITIVITY_H3_PRIOR_BREACHES.csv`, `CENCORA_SENSITIVITY_H4_HEALTH_BREACH.csv`, `DEDUP_SENSITIVITY_H2_FCC_EFFECT.csv`, `ESSAY2_ALTERNATIVE_VOLATILITY_MEASURES.csv`, `ESSAY2_ALTERNATIVE_VOLATILITY_MEASURES_RECONCILED.csv`, `ESSAY2_GOVERNANCE_VOLATILITY_RECONCILED.csv`, `ESSAY2_GOVERNANCE_VOLATILITY_RESULTS.csv`, `ESSAY2_INFO_ENVIRONMENT_VOLATILITY_RECONCILED.csv`, `ESSAY2_INFO_ENVIRONMENT_VOLATILITY_RESULTS.csv`, `ESSAY2_MEDIA_COVERAGE_VOLATILITY_RECONCILED.csv`, `ESSAY2_MEDIA_COVERAGE_VOLATILITY_RESULTS.csv`, `H6_ENFORCEMENT_ANALYSIS.txt`, `Heterogeneity_Analysis_By_Size.txt`, `SAMPLE_COMPOSITION_COMPARISON.csv`, `TABLE1_COMBINED.txt`, `TABLE1_PANEL_A_full_sample.csv`, `TABLE1_PANEL_B_crsp_sample.csv`, `TABLE1_PANEL_C_by_fcc.csv`, `TABLE1_PANEL_D_by_timing.csv`, `TABLE_BALANCE_TEST.csv`, `TABLE_BALANCE_TEST.txt`, `TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv`, `TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv`, `TABLE_CVSS_COMPLEXITY_VOLATILITY_RESULTS.csv` (LFS), `TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv`, `TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv`, `TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv`, `TABLE_GOVERNANCE_QUALITY_VOLATILITY_RESULTS.csv` (LFS), `TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv`, `TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv`, `TABLE_MEDIA_COVERAGE_VOLATILITY_RESULTS.csv` (LFS), `TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv`, `TABLE_SOX404_HETEROGENEITY_RESULTS.csv` (LFS), `TABLE_SOX404_SAMPLE_SUMMARY.csv` (LFS), `company_matching_validation.csv` (LFS), `placebo_test_results.csv` (LFS), `sample_attrition.csv` (LFS), `table1_descriptive_stats.csv` (LFS), `table1_descriptive_stats.tex`, `table2_univariate_comparison.csv` (LFS), `table3_essay2_regressions.tex`, `table3_essay2_summary.csv` (LFS), `table3_robustness_5day.tex`, `table4_essay3_regressions.tex`, `table4_essay3_summary.csv` (LFS), `table_10_648.csv`, `table_11_648.csv`, `table_12_648.csv`, `table_13_648.csv`, `table_1_648.csv`, `table_2_648.csv`, `table_3_648.csv`, `table_4_648.csv`, `table_5_648.csv`, `table_6_648.csv`, `table_7_648.csv`, `table_8_648.csv`, `table_9_648.csv`

### `outputs/tables/essay2/` (22 files, 0.7 MB)

*Reason:* pre-rebuild / superseded output or dataset

`DIAGNOSTICS_VIF_TABLE2_Model2.csv`, `DIAGNOSTICS_VIF_TABLE3_Model1.csv`, `DIAGNOSTICS_VIF_TABLE4_Model1.csv`, `DIAGNOSTICS_VIF_TABLE5_Model1.csv`, `DIAGNOSTICS_VIF_multicollinearity.csv` (LFS), `DIAGNOSTICS_VIF_summary.txt`, `DIAGNOSTICS_residual_plots_model1.png`, `FCC_Causal_ID_Summary.txt`, `H1_TOST_Equivalence_Test.txt`, `H1_Timing_Distribution.txt`, `TABLE2_baseline_disclosure.txt`, `TABLE3_fcc_regulation.txt`, `TABLE3_prior_breaches.txt`, `TABLE4_breach_severity.txt`, `TABLE4_prior_breaches.txt`, `TABLE5_breach_severity.txt`, `TABLE_APPENDIX_alternative_explanations.txt`, `TABLE_B7_alternative_explanations.txt`, `TABLE_B8_post_2007_interaction.txt`, `TABLE_B9_clustered_vs_hc3_comparison.txt`, `TABLE_FCC_Industry_FE_Comparison.txt`, `TABLE_FCC_Size_Sensitivity.txt`

### `outputs/tables/essay2_appendix/` (30 files, 0.1 MB)

*Reason:* tombstoned Essay 2 appendix CSV (no committed generator; Tim: drop unless cited)

`channel_announcement_buildup.csv`, `channel_announcement_differential.csv`, `channel_elevation_calibration.csv`, `channel_microstructure.csv`, `cluster_deletion_prerule.csv`, `delay_distribution_by_group.csv`, `descriptives_differences.csv`, `disclosure_delay.csv`, `form499_registry_matches.csv`, `four_panel_decomposition.csv`, `identifier_collisions.csv`, `identifier_collisions_recycled_tickers.csv`, `manifest.csv`, `misclassified_group_comparisons.csv`, `misclassified_group_contrasts.csv`, `misclassified_records.csv`, `missingness_precase.csv`, `prerule_events.csv`, `program_test_enumeration.csv`, `q1_transition_components.csv`, `q1_transition_records.csv`, `sample_attrition.csv`, `sic_convention_errors.csv`, `sic_conventions_vs_form499.csv`, `sich_unavailable_treated.csv`, `sich_vs_curated_sic.csv`, `size_variable_reconciliation.csv`, `specification_curve.csv`, `specification_curve_permutation.csv`, `treatment_adjudications.csv`

### `outputs/tables/essay3/` (9 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`FCC_Causal_ID_Summary_Volatility.txt`, `Mediation_Summary_Essay3.txt`, `TABLE2_volatility_changes.txt`, `TABLE3_information_asymmetry.txt`, `TABLE_B8_post_2007_interaction_volatility.txt`, `TABLE_FCC_Industry_FE_Comparison_Volatility.txt`, `TABLE_FCC_Size_Sensitivity_Volatility.txt`, `TABLE_Mediation_Effects_Essay3.txt`, `essay3_canonical_h6_results.csv`

### `outputs/tables/essay3_governance/` (22 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`CAUSAL_ID_COVARIATE_BALANCE.csv`, `CAUSAL_ID_DOSE_RESPONSE.csv`, `CAUSAL_ID_PLACEBO_TESTS.csv`, `H6_TOST_Equivalence_Test.txt`, `TABLE2_turnover_summary.csv`, `TABLE3_enforcement_cases.csv`, `cfo_turnover_placebo_results.csv`, `cox_model_all_turnover.csv`, `essay3_canonical_h6_results.csv`, `essay3_h6_heterogeneity.csv`, `h6_firm_size_heterogeneity_full.csv`, `h6_reduced_form_all_coefficients.csv`, `h6_tost_equivalence_results.csv`, `mediation_bootstrap_indirect_effects.csv`, `mediator_first_stage_results.csv`, `negative_binomial_h6_results.csv`, `ols_lpm_h6_results.csv`, `reduced_form_h6_results.csv`, `robustness_check1_turnover_definitions.csv`, `robustness_check2_disclosure_thresholds.csv`, `robustness_check3_restricted_samples.csv`, `with_mediator_model_coefficients.csv`

### `outputs/tables/robustness/` (3 files, 0.0 MB)

*Reason:* pre-rebuild / superseded output or dataset

`TABLE_Falsification_Tests.txt`, `TABLE_Low_R2_Sensitivity.txt`, `TABLE_Market_Model_Sensitivity.txt`

### `outputs/validation/` (4 files, 0.3 MB)

*Reason:* pre-rebuild / superseded output or dataset

`dissertation_robustness_section.txt`, `feature_importance_by_category.png`, `feature_importance_combined.png`, `ols_vs_ml_comparison.csv`

### `scripts/` (214 files, 1.7 MB)

*Reason:* retired / non-live script (superseded pipeline)

`00_data_validation_checks.py`, `00_setup_wrds.py`, `01_data_validation.py`, `02_quick_validation.py`, `03_company_matching.py`, `04_create_manual_mapping.py`, `05_apply_corrections.py`, `06_create_master_dataset.py`, `09_add_stock_data_robust.py`, `100_ransomware_heterogeneity.py`, `101_media_coverage_heterogeneity.py`, `101_media_coverage_heterogeneity_essay2.py`, `102_extended_governance_windows.py`, `103_breach_type_diversity.py`, `104_restatement_prediction.py`, `104_restatement_summary.py`, `110_fcc_form499_treatment_classifier.py`, `111_edgar_8k_timestamps_h1_precision.py`, `112_hhs_ocr_h4_health_breach_classification.py`, `113_state_ag_breach_databases_h3_completeness.py`, `120_form499_historical_availability_test.py`, `121a_form499_entity_matching.py`, `121b_form499_coverage_validation.py`, `121c_merge_form499_classification.py`, `122_manual_form499_corrections.py`, `12_recover_delisted_stocks.py`, `13_debug_recovery.py`, `143_essay1_results_supplements.py`, `144_residual_duplicate_audit.py`, `15b_download_wrds_data_fixed.py`, `161_old_vs_new_exhibit.py`, `162_calibration_sample_5_02.py`, `167_essay2_microstructure.py`, `168_essay3_audit.py`, `172_essay2_run_all.py`, `178_essay2_appendix_docx.py`, `179_dish_crsp_topup.py`, `183_essay3_q1_discovery.py`, `184_essay3_q1_tmobile_502_text.py`, `185_essay3_q1_tmobile_handcode.py`, `20_final_comprehensive_merge.py`, `216_wrds_access_probe.py`, `241_sic_fe_reestimate_v4.py`, `248_essay_to_output_match.py`, `24_expand_sample_analysis.py`, `30_explore_audit_tables.py`, `31_download_audit_data_FINAL.py`, `32_merge_audit_data.py`, `40_MASTER_enrichment.py`, `41_prior_breaches.py`, `42_industry_returns.py`, `43_analyst_coverage.py`, `44_institutional_ownership.py`, `45_breach_severity_nlp.py`, `46_diagnostic_item5_02_fast.py`, `46_executive_changes.py`, `46_executive_changes_item5_02.py`, `46_executive_changes_item5_02_with_cache.py`, `46_test_item5_02_subset.py`, `47_build_8k_cache.py`, `47_item5_02_cache_builder.py`, `47_regulatory_enforcement.py`, `48_nexis_uni_query_generator.py`, `48b_import_nexis_results.py`, `49_media_coverage.py`, `53_merge_CONFIRMED_enrichments.py`, `53_merge_item5_02_corrected.py`, `54_merge_crsp_data.py`, `60_train_ml_model.py`, `61_ml_validation.py`, `70_summary_statistics.py`, `81_post_2007_interaction_test.py`, `82_clustered_vs_hc3_comparison.py`, `84_essay2_post_2007_interaction_test_volatility.py`, `85_essay1_h2_regression_form499.py`, `86_essay3_fcc_causal_identification.py`, `86b_essay1_h2_regression_form499_corrected.py`, `86c_essay1_h1_h4_form499_corrected.py`, `90_essay2_volatility_regressions.py`, `90b_essay2_h5_form499_corrected.py`, `91_essay3_governance_regressions.py`, `91_essay3_mediation_analysis.py`, `91b_essay3_reduced_form_mediation.py`, `91c_essay3_mediation_bootstrap.py`, `91d_essay3_h6_heterogeneity.py`, `91e_essay3_h6_tost_equivalence.py`, `91f_essay3_h6_firm_size_heterogeneity.py`, `91g_extract_reduced_form_controls.py`, `91h_essay3_cox_hazards.py`, `91i_essay3_cfo_placebo.py`, `91j_essay3_ols_lpm_and_negbin.py`, `91k_essay3_robustness_checks.py`, `91m_essay3_h6_form499_corrected.py`, `92_enforcement_analysis.py`, `92_heterogeneity_analysis.py`, `93_market_model_sensitivity.py`, `95_low_r2_sensitivity.py`, `96_economic_significance.py`, `97_heterogeneous_mechanisms.py`, `98_propensity_score_matching.py`, `98_sox404_heterogeneity.py`, `98_sox404_heterogeneity_essay2.py`, `99_add_cpni_hhi_variables.py`, `99_firm_fixed_effects_analysis.py`, `99_firm_fixed_effects_analysis_BROKEN_June22.py`, `analyze_articles.py`, `apply_exact_matching_full_dataset.py`, `apply_known_subsidiaries.py`, `apply_reasoning_pass_results.py`, `boost_mobile_detailed_forensics.py`, `boost_mobile_forensics.py`, `bridge_to_crsp_and_recompute.py`, `build_essay1_appendix_word_complete.py`, `build_essay3_appendix_all_tables.py`, `build_validation_set.py`, `calendar_month_clustering_60_90.py`, `canonical_fcc_firm_list.py`, `check_boost_mobile.py`, `check_file_state.py`, `check_scdatamulti_params.py`, `cik_assignment_investigation.py`, `compare_cik_corrections.py`, `complete_pronoun_removal.py`, `config_causal_id.py`, `consolidate_subsidiaries_to_parents.py`, `consolidate_validation_results.py`, `convert_essay3_appendix_to_word.py`, `corrected_longrun_car_clustering.py`, `cox_timevarying_hazard.py`, `create_defense_qa_guide.py`, `create_essay1_appendix_word.py`, `create_essay3_appendix_docx.py`, `create_essay3_appendix_sequential.py`, `create_essay3_appendix_word.py`, `create_regression_coefficient_plots.py`, `create_table_b7_word.py`, `create_updated_presentation.py`, `defense_prep_all_tasks.py`, `diagnostic_top_five_near_duplicates.py`, `download_fama_french_factors.py`, `download_fama_french_factors_alt.py`, `download_ff_factors_fred.py`, `exact_match_validation_set.py`, `extended_bhar_60d_90d.py`, `extract_all_unmatched_org_names.py`, `extract_ex21_subsidiaries.py`, `extract_merge_fama_french.py`, `factor_model_carhart_ff5.py`, `factor_model_robustness.py`, `factor_models_complete.py`, `ff3_canonical_specification.py`, `ff3_simple_merge.py`, `firm_by_firm_scm_analysis.py`, `firm_by_firm_scm_analysis_BROKEN_June22.py`, `firm_by_firm_scm_simple_working.py`, `firm_count_reconciliation.py`, `fix_cik_assignments_and_dedup.py`, `fix_essay1_appendix_tables.py`, `fix_source_xlsx_and_resync.py`, `h1_abnormal_trading_volume.py`, `h1_complete_robustness_648.py`, `h1_timing_fcc_interaction.py`, `h1_timing_robustness_648.py`, `h2_firm_level_estimation.py`, `h2_robustness_three_analyses.py`, `longrun_bhar_analysis.py`, `longrun_bhar_extended.py`, `master_reconciliation_audit.py`, `overlap_audit_fcc_clustering.py`, `power_analysis_h3_h4.py`, `prepare_full_reasoning_pass.py`, `prepare_reasoning_pass_batch.py`, `rebuild_essay1_appendix.py`, `recalc_car_consolidated.py`, `reconciliation_and_cleanup.py`, `remove_duplicates_and_save.py`, `rerun_defense_prep_on_648.py`, `rerun_regressions_consolidated.py`, `rerun_regressions_corrected.py`, `robustness_1_alternative_windows.py`, `robustness_2_timing_thresholds.py`, `robustness_3_sample_restrictions.py`, `robustness_4_standard_errors.py`, `robustness_5_fixed_effects.py`, `robustness_summary_648.py`, `run_all_robustness.py`, `run_causal_identification_pipeline.py`, `run_causal_identification_pipeline_BROKEN_June22.py`, `run_enrichments.py`, `sample_composition_diagnostic.py`, `scm_breach_event_level.py`, `scm_breach_event_nearest_neighbor.py`, `scm_breach_event_numpy.py`, `scm_breach_event_numpy_fast.py`, `scm_data_preparation.py`, `scm_data_preparation_BROKEN_June22.py`, `scm_mahalanobis_distance.py`, `score_exact_matcher.py`, `scpi_corrected.py`, `scpi_scm_implementation.py`, `scpi_simple.py`, `sec_2023_rule_preliminary.py`, `step1_build_edgar_cik_map.py`, `step2_match_prc_to_edgar.py`, `step2_match_prc_to_sec_efficient.py`, `step2_match_prc_to_sec_historical.py`, `step2b_enhance_manual_worksheet.py`, `update_dashboard.py`, `update_presentation.py`, `verify_cfo_placebo.py`, `verify_cox_schoenfeld.py`, `verify_duplicate_candidates.py`, `verify_fcc_entity_assignments.py`, `verify_h4_coefficient.py`

### `scripts/archive/` (12 files, 0.1 MB)

*Reason:* retired / non-live script (superseded pipeline)

`07_add_stock_data.py`, `08_add_stock_data_fixed.py`, `15_download_wrds_data.py`, `16_merge_wrds_data.py`, `18_download_fcc_data_v2.py`, `22_essay2_comprehensive_analysis.py`, `22_essay2_comprehensive_analysis_FIXED.py`, `23_essay2_FULL_analysis.py`, `25_essay2_EXPANDED_sample.py`, `26_essay3_information_asymmetry.py`, `28_download_audit_analytics_FIXED.py`, `29_download_audit_analytics_CORRECT.py`

### `scripts/ml_models/` (4 files, 0.0 MB)

*Reason:* retired / non-live script (superseded pipeline)

`__init__.py`, `breach_impact_model.py`, `feature_importance.py`, `model_evaluation.py`

### `scripts/root_dev_archive/` (18 files, 0.1 MB)

*Reason:* retired / non-live script (superseded pipeline)

`QUICK_RESULTS_EXTRACT.sh`, `build_essay1_appendix_docx.py`, `build_essay1_appendix_verified.py`, `build_final_appendix_14tables.py`, `calculate_preannouncement.py`, `calculate_preannouncement_648.py`, `check_step2_results.py`, `check_ticker_mapping.py`, `debug_sec_format.py`, `expand_validation_set.py`, `finalize_validation_40.py`, `rebuild_essay1_appendix_tables.py`, `rebuild_tables_4_5_7_with_log.py`, `reconcile_appendix_numbers.py`, `update_readme.py`, `update_table_references.py`, `verify_factor_models.py`, `verify_validation_set.py`


## B2 - kept docs that cite an ARCHIVE path (27 docs, 687 cited files)

Each citation would be repointed to `archive/<same path>` in Stage 2.

- **`docs/DATA_QUALITY_DOCUMENTATION.md`** (2): `Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv`, `scripts/root_dev_archive/rebuild_essay1_appendix_tables.py`
- **`docs/claude/ESSAY3_POST_RERUN_STATE.md`** (1): `scripts/46_executive_changes.py`
- **`docs/claude/ESSAY3_QUERY_1.md`** (1): `scripts/91e_essay3_h6_tost_equivalence.py`
- **`docs/claude/KNOWN_LIMITATIONS.md`** (1): `Data/processed/DATA_DICTIONARY_ENRICHED.csv`
- **`docs/claude/REBUILD_V4_QUERY.md`** (1): `Data/enrichment/regulatory_enforcement.csv`
- **`docs/claude/REPRODUCE_ESSAY2.md`** (4): `outputs/form499_matched_records.csv`, `outputs/form499_unmatched_with_candidates.csv`, `outputs/tables/essay2_appendix/channel_microstructure.csv`, `scripts/121a_form499_entity_matching.py`
- **`docs/claude/V3_FREEZE_EXCEPTIONS.md`** (5): `scripts/robustness_1_alternative_windows.py`, `scripts/robustness_2_timing_thresholds.py`, `scripts/robustness_3_sample_restrictions.py`, `scripts/robustness_4_standard_errors.py`, `scripts/robustness_5_fixed_effects.py`
- **`outputs/ALIGNMENT_REPORT.md`** (19): `outputs/audit/audit_essay2_sample.csv`, `outputs/tables/essay2_appendix/channel_elevation_calibration.csv`, `outputs/tables/essay2_appendix/channel_microstructure.csv`, `outputs/tables/essay2_appendix/cluster_deletion_prerule.csv`, `outputs/tables/essay2_appendix/delay_distribution_by_group.csv`, `outputs/tables/essay2_appendix/disclosure_delay.csv`, `outputs/tables/essay2_appendix/form499_registry_matches.csv`, `outputs/tables/essay2_appendix/four_panel_decomposition.csv`, `outputs/tables/essay2_appendix/identifier_collisions.csv`, `outputs/tables/essay2_appendix/identifier_collisions_recycled_tickers.csv`, `outputs/tables/essay2_appendix/misclassified_group_comparisons.csv`, `outputs/tables/essay2_appendix/missingness_precase.csv`, `outputs/tables/essay2_appendix/program_test_enumeration.csv`, `outputs/tables/essay2_appendix/q1_transition_components.csv`, `outputs/tables/essay2_appendix/sic_conventions_vs_form499.csv`, `outputs/tables/essay2_appendix/sich_unavailable_treated.csv`, `outputs/tables/essay2_appendix/sich_vs_curated_sic.csv`, `outputs/tables/essay2_appendix/specification_curve_permutation.csv`, `scripts/248_essay_to_output_match.py`
- **`outputs/ESSAY2_QUERY5_REPORT.md`** (2): `scripts/172_essay2_run_all.py`, `scripts/create_defense_qa_guide.py`
- **`outputs/ESSAY3_AUDIT.md`** (3): `outputs/essay2_expanded/tables/regression_full_output.txt`, `outputs/essay3/tables/regression_full_output.txt`, `outputs/tables/essay3_governance/ols_lpm_h6_results.csv`
- **`outputs/ESSAY3_QUERY1_REPORT.md`** (52): `Data/enrichment/executive_changes.csv`, `Data/processed/FINAL_DISSERTATION_DATASET.xlsx`, `outputs/essay3_q1/183_discovery.log`, `outputs/essay3_q1/184_tmobile_text.log`, `outputs/essay3_q1/c4_first_stage_reconciliation.csv`, `outputs/essay3_q1/d1_attrition_ledger.csv`, `outputs/essay3_q1/d2_treated_orgs_essay3.csv`, `outputs/essay3_q1/e2_tmobile_502_text.csv`, `outputs/essay3_q1/e2_tmobile_events_x_filings.csv`, `outputs/essay3_q1/e3_security_title_scan.csv`, `outputs/essay3_q1/g_h6_reestimation.csv`, `outputs/tables/essay3_governance/cox_model_all_turnover.csv`, `outputs/tables/essay3_governance/h6_tost_equivalence_results.csv`, `outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv`, `outputs/tables/essay3_governance/mediator_first_stage_results.csv`, `outputs/tables/essay3_governance/reduced_form_h6_results.csv`, `outputs/tables/essay3_governance/with_mediator_model_coefficients.csv`, `scripts/102_extended_governance_windows.py`, `scripts/161_old_vs_new_exhibit.py`, `scripts/162_calibration_sample_5_02.py`, `scripts/168_essay3_audit.py`, `scripts/183_essay3_q1_discovery.py`, `scripts/184_essay3_q1_tmobile_502_text.py`, `scripts/185_essay3_q1_tmobile_handcode.py`, `scripts/46_diagnostic_item5_02_fast.py`, `scripts/46_executive_changes.py`, `scripts/46_executive_changes_item5_02.py`, `scripts/46_executive_changes_item5_02_with_cache.py`, `scripts/46_test_item5_02_subset.py`, `scripts/47_build_8k_cache.py`, `scripts/47_item5_02_cache_builder.py`, `scripts/53_merge_CONFIRMED_enrichments.py`, `scripts/53_merge_item5_02_corrected.py`, `scripts/86_essay3_fcc_causal_identification.py`, `scripts/91_essay3_governance_regressions.py`, `scripts/91_essay3_mediation_analysis.py`, `scripts/91b_essay3_reduced_form_mediation.py`, `scripts/91c_essay3_mediation_bootstrap.py`, `scripts/91e_essay3_h6_tost_equivalence.py`, `scripts/91h_essay3_cox_hazards.py` ...
- **`outputs/ESSAY3_QUERY2_REPORT.md`** (5): `Data/enrichment/executive_changes.csv`, `scripts/122_manual_form499_corrections.py`, `scripts/40_MASTER_enrichment.py`, `scripts/91_essay3_governance_regressions.py`, `scripts/run_enrichments.py`
- **`outputs/ESSAY3_QUERY3_REPORT.md`** (2): `outputs/preannouncement_648_results.csv`, `scripts/122_manual_form499_corrections.py`
- **`outputs/LAMBERT_LEDGER.md`** (3): `outputs/tables/essay3_governance/h6_tost_equivalence_results.csv`, `outputs/tables/essay3_governance/reduced_form_h6_results.csv`, `scripts/91e_essay3_h6_tost_equivalence.py`
- **`outputs/RETIREMENT_LEDGER.md`** (93): `Data/enrichment/executive_changes.csv`, `Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv`, `Data/processed/data_prepared_for_scm.csv`, `outputs/AUDIT_SCM_PVALUE_RESOLUTION.txt`, `outputs/ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt`, `outputs/H1_timing_fcc_interaction_results.csv`, `outputs/calendar_month_clustering_results.csv`, `outputs/corrected_longrun_analysis_results.csv`, `outputs/defense_prep/task5_scm_vs_ols_summary.txt`, `outputs/economic_significance/economic_impact_summary.csv`, `outputs/economic_significance/economic_significance_report.txt`, `outputs/extended_bhar_60d_90d_results.csv`, `outputs/factor_model_robustness_results.csv`, `outputs/h1_h4_form499_corrected_summary.csv`, `outputs/h5_form499_corrected_heterogeneity.csv`, `outputs/h6_form499_corrected_ame_by_window.csv`, `outputs/h6_form499_corrected_power_analysis.csv`, `outputs/heterogeneous_analysis/Essay3_Heterogeneous_Turnover.png`, `outputs/overlap_audit_summary.csv`, `outputs/retired_originals_20260902/AUDIT_SCM_PVALUE_RESOLUTION.txt`, `outputs/retired_originals_20260902/ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt`, `outputs/retired_originals_20260902/task5_scm_vs_ols_summary.txt`, `outputs/scm_breach_event_nn_results.csv`, `outputs/scm_crsp_comprehensive/firm_effects_with_controls.csv`, `outputs/scm_crsp_comprehensive/scm_crsp_firm_results.csv`, `outputs/scm_crsp_with_sprint/consolidated_by_company.csv`, `outputs/scm_crsp_with_sprint/scm_crsp_sprint_proxy_results.csv`, `outputs/scm_firm_by_firm/TABLE_SCM_AGGREGATE_RESULTS.csv`, `outputs/scm_firm_by_firm/TABLE_SCM_GAPS_BY_YEAR.csv`, `outputs/scm_firm_by_firm/TABLE_SCM_TOP_20_FIRMS.csv`, `outputs/scm_firm_by_firm/scm_aggregate_effect.png`, `outputs/scm_firm_by_firm/scm_aggregate_gaps_over_time.png`, `outputs/scm_firm_by_firm/scm_aggregate_statistics.csv`, `outputs/scm_firm_by_firm/scm_all_firm_gaps.csv`, `outputs/scm_firm_by_firm/scm_effect_distribution.png`, `outputs/scm_firm_by_firm/scm_firm_effects_distribution.png`, `outputs/scm_firm_by_firm/scm_firm_level_effects.png`, `outputs/scm_firm_by_firm/scm_firm_summary_results.csv`, `outputs/scm_firm_by_firm/scm_permutation_distribution.csv`, `outputs/scm_firm_by_firm/scm_permutation_distribution.png` ...
- **`outputs/RUN_ALL_AUDIT_REPORT.md`** (13): `scripts/161_old_vs_new_exhibit.py`, `scripts/96_economic_significance.py`, `scripts/97_heterogeneous_mechanisms.py`, `scripts/create_defense_qa_guide.py`, `scripts/create_essay3_appendix_docx.py`, `scripts/create_essay3_appendix_sequential.py`, `scripts/defense_prep_all_tasks.py`, `scripts/rerun_defense_prep_on_648.py`, `scripts/robustness_1_alternative_windows.py`, `scripts/robustness_2_timing_thresholds.py`, `scripts/robustness_3_sample_restrictions.py`, `scripts/robustness_4_standard_errors.py`, `scripts/robustness_5_fixed_effects.py`
- **`outputs/RUN_ALL_FOLLOWUP_REPORT.md`** (9): `Data/audit_analytics/restatements.csv`, `Data/enrichment/breach_severity_classification.csv`, `Data/enrichment/media_coverage.csv`, `Data/enrichment/prior_breach_history.csv`, `Data/enrichment/regulatory_enforcement.csv`, `Data/processed/DATA_DICTIONARY_ENRICHED.csv`, `outputs/tables/essay2_appendix/sample_attrition.csv`, `outputs/tables/sample_attrition.csv`, `scripts/161_old_vs_new_exhibit.py`
- **`outputs/TIMING_MEASUREMENT_REPORT.md`** (1): `Data/processed/DATA_DICTIONARY_ENRICHED.csv`
- **`outputs/essay3_q2/186_stdout.txt`** (7): `scripts/40_MASTER_enrichment.py`, `scripts/46_executive_changes.py`, `scripts/46_executive_changes_item5_02.py`, `scripts/46_executive_changes_item5_02_with_cache.py`, `scripts/53_merge_CONFIRMED_enrichments.py`, `scripts/91_essay3_governance_regressions.py`, `scripts/run_enrichments.py`
- **`outputs/essay3_q2/a4_consumers.csv`** (117): `scripts/00_data_validation_checks.py`, `scripts/100_ransomware_heterogeneity.py`, `scripts/101_media_coverage_heterogeneity.py`, `scripts/101_media_coverage_heterogeneity_essay2.py`, `scripts/102_extended_governance_windows.py`, `scripts/103_breach_type_diversity.py`, `scripts/104_restatement_prediction.py`, `scripts/104_restatement_summary.py`, `scripts/40_MASTER_enrichment.py`, `scripts/46_executive_changes.py`, `scripts/46_executive_changes_item5_02.py`, `scripts/46_executive_changes_item5_02_with_cache.py`, `scripts/53_merge_CONFIRMED_enrichments.py`, `scripts/60_train_ml_model.py`, `scripts/61_ml_validation.py`, `scripts/70_summary_statistics.py`, `scripts/81_post_2007_interaction_test.py`, `scripts/82_clustered_vs_hc3_comparison.py`, `scripts/84_essay2_post_2007_interaction_test_volatility.py`, `scripts/86_essay3_fcc_causal_identification.py`, `scripts/90_essay2_volatility_regressions.py`, `scripts/91_essay3_governance_regressions.py`, `scripts/91_essay3_mediation_analysis.py`, `scripts/91b_essay3_reduced_form_mediation.py`, `scripts/91c_essay3_mediation_bootstrap.py`, `scripts/91d_essay3_h6_heterogeneity.py`, `scripts/91f_essay3_h6_firm_size_heterogeneity.py`, `scripts/91g_extract_reduced_form_controls.py`, `scripts/91i_essay3_cfo_placebo.py`, `scripts/91j_essay3_ols_lpm_and_negbin.py`, `scripts/91k_essay3_robustness_checks.py`, `scripts/92_enforcement_analysis.py`, `scripts/92_heterogeneity_analysis.py`, `scripts/93_market_model_sensitivity.py`, `scripts/95_low_r2_sensitivity.py`, `scripts/96_economic_significance.py`, `scripts/97_heterogeneous_mechanisms.py`, `scripts/98_propensity_score_matching.py`, `scripts/98_sox404_heterogeneity.py`, `scripts/98_sox404_heterogeneity_essay2.py` ...
- **`outputs/essay3_q2/enforcement_timing_exploratory.md`** (5): `Data/enrichment/regulatory_enforcement.csv`, `Data/fcc/fcc_data_template.csv`, `outputs/audit/audit_fcc_analysis.csv`, `scripts/47_regulatory_enforcement.py`, `scripts/53_merge_CONFIRMED_enrichments.py`
- **`outputs/rebuild/OLD_VS_NEW_EXHIBIT.md`** (1): `outputs/h1_h4_form499_corrected_summary.csv`
- **`outputs/rebuild_v4/211_aborted_runs.md`** (1): `scripts/216_wrds_access_probe.py`
- **`outputs/rebuild_v4/216_access_probe.md`** (1): `scripts/216_wrds_access_probe.py`
- **`outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv`** (685): `Data/F-F_Momentum_Factor_daily.csv`, `Data/F-F_Research_Data_5_Factors_2x3_daily.csv`, `Data/JSON Files/nvdcve-2.0-2007.json`, `Data/JSON Files/nvdcve-2.0-2008.json`, `Data/JSON Files/nvdcve-2.0-2009.json`, `Data/JSON Files/nvdcve-2.0-2010.json`, `Data/JSON Files/nvdcve-2.0-2011.json`, `Data/JSON Files/nvdcve-2.0-2012.json`, `Data/JSON Files/nvdcve-2.0-2013.json`, `Data/JSON Files/nvdcve-2.0-2014.json`, `Data/JSON Files/nvdcve-2.0-2015.json`, `Data/JSON Files/nvdcve-2.0-2016.json`, `Data/JSON Files/nvdcve-2.0-2017.json`, `Data/JSON Files/nvdcve-2.0-2018.json`, `Data/JSON Files/nvdcve-2.0-2019.json`, `Data/JSON Files/nvdcve-2.0-2020.json`, `Data/JSON Files/nvdcve-2.0-2021.json`, `Data/JSON Files/nvdcve-2.0-2022.json`, `Data/JSON Files/nvdcve-2.0-2023.json`, `Data/JSON Files/nvdcve-2.0-2024.json`, `Data/JSON Files/nvdcve-2.0-2025.json`, `Data/audit_analytics/restatements.csv`, `Data/audit_analytics/restatements_sample.csv`, `Data/audit_analytics/sox_404_data.csv`, `Data/audit_analytics/sox_sample.csv`, `Data/enrichment/README.md`, `Data/enrichment/breach_severity_classification.csv`, `Data/enrichment/executive_changes.csv`, `Data/enrichment/executive_changes_item5_02.csv`, `Data/enrichment/industry_adjusted_returns.csv`, `Data/enrichment/media_coverage.csv`, `Data/enrichment/organization_breach_summary.csv`, `Data/enrichment/prior_breach_history.csv`, `Data/enrichment/regulatory_enforcement.csv`, `Data/ex21_extraction_template.csv`, `Data/ex21_subsidiaries_extracted.csv`, `Data/fcc/companies_to_match.csv`, `Data/fcc/companies_to_match_DEDUPLICATED.csv`, `Data/fcc/fcc_data_template.csv`, `Data/processed/.gitkeep` ...
- **`outputs/tables/essay2_appendix/TOMBSTONE.md`** (3): `outputs/tables/essay2_appendix/channel_announcement_buildup.csv`, `outputs/tables/essay2_appendix/cluster_deletion_prerule.csv`, `scripts/178_essay2_appendix_docx.py`
- **`run_all.py`** (126): `Data/enrichment/executive_changes.csv`, `Data/processed/FINAL_DATASET_DEDUP_V2_CANDIDATE.csv`, `Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv`, `Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv`, `outputs/H1_timing_fcc_interaction_results.csv`, `outputs/economic_significance/economic_impact_summary.csv`, `outputs/economic_significance/economic_significance_report.txt`, `outputs/figures/FIGURE_PARALLEL_TRENDS.png`, `outputs/h1_h4_form499_corrected_summary.csv`, `outputs/h5_form499_corrected_heterogeneity.csv`, `outputs/ml_models/feature_importance_car30d.csv`, `outputs/ml_models/feature_importance_car30d.png`, `outputs/ml_models/ml_model_summary.csv`, `outputs/robustness/figures/R02_timing_thresholds.png`, `outputs/robustness/figures/R03_sample_restrictions.png`, `outputs/robustness/figures/R04_standard_errors.png`, `outputs/robustness/figures/R05_fixed_effects.png`, `outputs/robustness/tables/R01_alternative_windows_summary.csv`, `outputs/robustness/tables/R02_timing_thresholds_summary.csv`, `outputs/robustness/tables/R03_sample_restrictions_summary.csv`, `outputs/robustness/tables/R04_standard_errors_summary.csv`, `outputs/robustness/tables/R05_fixed_effects_summary.csv`, `outputs/tables/TABLE1_COMBINED.txt`, `outputs/tables/TABLE1_PANEL_A_full_sample.csv`, `outputs/tables/TABLE1_PANEL_B_crsp_sample.csv`, `outputs/tables/TABLE1_PANEL_C_by_fcc.csv`, `outputs/tables/TABLE1_PANEL_D_by_timing.csv`, `outputs/tables/TABLE_BALANCE_TEST.csv`, `outputs/tables/TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv`, `outputs/tables/TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv`, `outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv`, `outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv`, `outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv`, `outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv`, `outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv`, `outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv`, `outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt`, `outputs/tables/essay2/FCC_Causal_ID_Summary.txt`, `outputs/tables/essay2/H1_TOST_Equivalence_Test.txt`, `outputs/tables/essay2/TABLE2_baseline_disclosure.txt` ...

## C1 - branches other than main and rebuild-v4

| branch | head | last commit | merged into main |
|---|---|---|---|
| defense-supplement (local) | 902a8ea | 2026-10-02 | yes |
| dissertation (local) | f9f7279 | 2026-03-02 | yes |
| feature/committee-feedback-criteria (local) | 532e92d | 2026-02-21 | yes |
| update/author-name-and-columns (local) | 8a30d0f | 2026-02-17 | yes |
| worktree-agent-aad33f2c4403479f4 (local; an agent worktree at .claude/worktrees/) | 7b0c0d4 | 2026-07-27 | yes |
| origin/dissertation | 7a53bde | 2026-03-02 | yes |
| origin/mlmodel | a6c55a7 | 2026-01-23 | yes |
| origin/update/author-name-and-columns | 8a30d0f | 2026-02-17 | yes |
| repo-cleanup (this query) | 76167e8 | 2026-10-02 | yes (no commits yet) |

All are fully merged into `main`, so deleting any of them loses nothing. `rebuild-v4` and every tag are out of scope.

## C2 - README

`README.md` exists (172 lines, last changed 950cb85, 2026-09-11) and covers purpose, setup, licensing (`docs/WRDS_EXTRACT_RECIPE.md`) and the retirement ledger. It is **stale** in three places, so the proposal is a revision, not a new file:
- it says Essay 3 "must not be run through `run_all.py`" - Essay 3 v4 is now staged in `run_all.py`;
- it says "No TOST result is current" - the Essay 1 constants and the defense supplement report TOST p-values;
- it does not mention the `defense-final` tag (902a8ea), `docs/claude/KNOWN_LIMITATIONS.md`, `docs/claude/POST_DEFENSE.md`, the 210 freeze gate, or the clean-clone verification.
Proposed additions: a "Verified state" section (defense-final, how to reproduce: clone with core.longpaths, `git lfs pull`, `python run_all.py`, expected exit 0 with 170 the only declared skip), an "Audit trail" section (RETIREMENT_LEDGER, KNOWN_LIMITATIONS, POST_DEFENSE, V3_FREEZE_EXCEPTIONS, REPRODUCE_*), and an `archive/` note. Not written yet.

## C3 - .gitignore

`.gitignore:79` is `*.md` (with `!README.md`, `!article_monitors/*.md`, `!docs/claude/**`, `!outputs/essay3_q2/**`, `!outputs/rebuild_v4/**`, `!outputs/essay3_v4/**`), which is why every kept report needs `git add -f`. The intent was to keep the ~150 working notes in the repo root out of git. Proposed narrower rule (not applied): replace `*.md` with `/*.md` (root-level only) plus `!/README.md`, so `outputs/**/*.md` and `docs/**/*.md` are tracked normally. Because 210 judges `.gitignore` append-only (the baseline must stay a byte prefix), the change cannot edit line 79 in place: it has to be appended as negations, e.g. `!outputs/**/*.md` and `!docs/**/*.md`. Side effect to check first: outputs/*.md files that are currently untracked by design (run reports with timestamps, e.g. `outputs/REPO_CLEANUP_REPORT.md` itself, `RESULTS_COMPLETENESS_REPORT.md`, `MATCH_SOURCE_BUNDLE*.md`) would start showing as untracked.

## Stage 2 constraints found in Stage 1 (need rulings before "go")

1. **scripts/210 and archive/.** Removing a baseline file is compatible with 210 once the manifest is re-created (a missing file is recorded as MISSING and passes). An archive *move* is not: the file reappears under `archive/` as a newly tracked path outside the v4 allowlist, and 210 FAILs ("ADDED outside v4 allowlist"). Stage 2 needs `"archive/"` added to `V4_DIRS` in `scripts/210_verify_v3_frozen.py` (a one-line allowlist entry, like the 2026-09-25 and 2026-10-02 widenings; scripts/217 would get a matching test case). That touches a gate script, which Part 0 forbids for logic - ruling needed.
2. **t24 depends on what is in `scripts/` and `Dashboard/`.** `scripts/164` A4 scans `scripts/*.py` and `Dashboard/**/*.py` for text describing 64.2011 as a disclosure deadline and writes the hits to `outputs/tables/essay2_v2/t24_a4_deadline_scan.csv` (a cited Essay 2 table). The 20 files it currently lists are held in ASK; archiving any of them changes t24, which breaks D5's byte-identical rule. Options: keep them in place, or accept a t24 change (t24 is literally the deletion list, so archiving them is what it recommends).
3. **Static linkage is a heuristic.** A live script that builds a path at run time without a recognisable literal would not be seen. D5's fresh-clone run is the authoritative check; anything it needs gets restored and reported.
4. **Committee lens.** Pre-rebuild robustness, ML, figure and heterogeneity outputs are ARCHIVE (superseded, per Part A), not KEEP-COMMITTEE; current inference ladders, placebo, power and RI outputs are all KEEP-CITED or KEEP-RUN. KEEP-COMMITTEE holds what no live step touches but a member could ask for: the classifier/validation code (186-201, 220-226 not live), the chronology replication (sample-ceiling evidence), the PRC source workbook, two unused WRDS extracts and docs/fcc_premise_verification.md.
5. **These three Stage 1 files are themselves new tracked paths** (`outputs/REPO_INVENTORY.csv`,
   `outputs/REPO_INVENTORY_SUMMARY.md`, `outputs/REPO_CLEANUP_REPORT.md`). They sit outside 210's v4 allowlist,
   so 210 will report them as "ADDED outside v4 allowlist" until they are listed in `V4_DOCS`. That is the same
   one-line allowlist change as item 1, and it needs to be made in Stage 2.
