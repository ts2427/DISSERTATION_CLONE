"""
RUN_ALL_ANALYSIS.py - Complete Dissertation Analytics Pipeline
================================================================

Executes the entire dissertation workflow with comprehensive logging:
1. Summary Statistics (Table 1)
2. Essay 2: Main Regression Analysis (Tables 2-5, Firm-Clustered SEs + TOST + VIF)
3. FCC Causal Identification (TABLE B8: Post-2007 Interaction Test)
4. Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)
5. Essay 3: Main Regression Analysis (Tables 2-3)
6. ML Model Training & Validation (Optional)
7. Recommendation Scripts (Scripts 91-95: Mediation, Heterogeneity, Window Sensitivity, Falsification, Low R²)
8. Robustness Checks (9 checks including alternative windows, timing, samples, SEs, fixed effects)

All output is captured to timestamped log file.

Key Enhancements (Phase 3):
- Firm-clustered standard errors as main specification
- TOST equivalence test for H1 null hypothesis validation
- VIF multicollinearity diagnostics
- Post-2007 interaction test for FCC causal identification
- Comprehensive robustness comparisons

Author: Timothy D. Spivey
Dissertation: Data Breach Disclosure Timing and Market Reactions
University of South Alabama
Date: February 2026

CRITICAL: DATA PIPELINE ROOT
============================
The source of truth for this pipeline is:
  → Data/processed/FINAL_DISSERTATION_DATASET.xlsx

Do NOT manually edit the CSV file:
  ✗ Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv

Why: Script 53 (merge_CONFIRMED_enrichments.py) reads from the Excel file and regenerates
the CSV. Any corrections made directly to the CSV will be overwritten when script 53 runs.

If you need to correct data:
  1. Apply corrections to FINAL_DISSERTATION_DATASET.xlsx (the Excel source)
  2. Delete or move the old CSV (to force regeneration)
  3. Run this pipeline from start to finish
  4. All downstream results will use the corrected data

This pipeline must run sequentially in full order. Individual script runs may produce
stale outputs or intermediate inconsistencies. Always run the complete pipeline for
final analysis numbers.
"""

import sys
import os
import subprocess
from pathlib import Path
import time
from datetime import datetime
import io

# Force UTF-8 encoding for entire script
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set stdout to UTF-8 (for Windows terminal support)
if sys.stdout.encoding.lower() != 'utf-8':
    # Recreate stdout with UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_section(title):
    """Print formatted section header"""
    separator = "\n" + "=" * 80
    print(f"{separator}\n  {title}\n{'=' * 80}\n")

def print_to_both(message, log_file):
    """Print to both console and log file"""
    print(message)
    log_file.write(message + "\n")
    log_file.flush()

def run_script(script_path, description, log_file):
    """
    Run a Python script and capture output to log.
    Returns True if successful.
    """
    header = f"\nRunning: {description}\nScript: {script_path}\n" + "-" * 80
    print_to_both(header, log_file)

    start_time = time.time()

    # Set environment
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=600,  # 10 minute timeout
            env=env
        )

        elapsed = time.time() - start_time

        # Write output to log
        if result.stdout:
            log_file.write(result.stdout)
            print(result.stdout)

        if result.stderr:
            log_file.write("\nSTDERR:\n" + result.stderr)
            if result.returncode != 0:
                print(result.stderr)

        # Check result
        if result.returncode == 0:
            status = f"[OK] Completed in {elapsed:.1f} seconds\n"
            print_to_both(status, log_file)
            return True
        else:
            status = f"[ERROR] Script failed (return code {result.returncode}) after {elapsed:.1f} seconds\n"
            print_to_both(status, log_file)
            return False

    except subprocess.TimeoutExpired:
        status = "[ERROR] Script timeout (>10 minutes)\n"
        print_to_both(status, log_file)
        return False

    except Exception as e:
        status = f"[ERROR] Exception: {str(e)}\n"
        print_to_both(status, log_file)
        return False

def verify_data(log_file):
    """Verify required data files exist"""
    print_section("STEP 0: DATA VERIFICATION")
    log_file.write("\n" + "=" * 80 + "\nSTEP 0: DATA VERIFICATION\n" + "=" * 80 + "\n\n")

    data_file = Path('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

    if data_file.exists():
        file_size = data_file.stat().st_size / (1024 * 1024)
        msg = f"  [OK] Enriched dataset found ({file_size:.1f} MB)\n  [OK] Ready to proceed\n"
        print_to_both(msg, log_file)
        return True
    else:
        msg = f"  [ERROR] Required data file missing: {data_file}\n"
        print_to_both(msg, log_file)
        return False

def verify_outputs(log_file):
    """Verify critical output files exist after analysis"""
    print_section("OUTPUT VERIFICATION")
    log_file.write("\n" + "=" * 80 + "\nOUTPUT VERIFICATION\n" + "=" * 80 + "\n\n")

    # Define critical output files
    critical_files = [
        Path('outputs/tables/TABLE1_COMBINED.txt'),
        Path('outputs/tables/essay2/TABLE2_baseline_disclosure.txt'),
        Path('outputs/tables/essay2/TABLE3_fcc_regulation.txt'),
        Path('outputs/tables/essay2/TABLE4_prior_breaches.txt'),
        Path('outputs/tables/essay2/TABLE5_breach_severity.txt'),
        Path('outputs/H1_timing_fcc_interaction_results.csv'),
        Path('outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt'),
        Path('outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt'),
        Path('outputs/tables/essay2/H1_TOST_Equivalence_Test.txt'),
        Path('outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt'),
        Path('outputs/tables/essay3_governance/h6_tost_equivalence_results.csv'),
        Path('outputs/tables/essay3_governance/H6_TOST_Equivalence_Test.txt'),
        Path('outputs/tables/essay3_governance/h6_firm_size_heterogeneity_full.csv'),
        Path('outputs/tables/essay3_governance/h6_reduced_form_all_coefficients.csv'),
        Path('outputs/tables/essay3_governance/cox_model_all_turnover.csv'),
        Path('outputs/tables/essay3_governance/H6_Cox_Model_Results.txt'),
        Path('outputs/tables/essay3_governance/ols_lpm_h6_results.csv'),
        Path('outputs/tables/essay3_governance/negative_binomial_h6_results.csv'),
        Path('outputs/tables/essay3_governance/robustness_check1_turnover_definitions.csv'),
        Path('outputs/tables/essay3_governance/robustness_check2_disclosure_thresholds.csv'),
        Path('outputs/tables/essay3_governance/robustness_check3_restricted_samples.csv'),
        Path('outputs/tables/essay3/TABLE2_volatility_changes.txt'),
        Path('outputs/tables/essay3/TABLE3_information_asymmetry.txt'),
        Path('outputs/economic_significance/economic_impact_summary.csv'),
        Path('outputs/economic_significance/economic_significance_report.txt'),
        Path('outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv'),
        Path('outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv'),
    ]

    present_files = []
    missing_files = []

    for filepath in critical_files:
        if filepath.exists():
            present_files.append(str(filepath))
        else:
            missing_files.append(str(filepath))

    # Report results
    msg = f"\nCritical Output Files:\n"
    msg += f"  Present: {len(present_files)}/{len(critical_files)}\n"
    msg += f"  Missing: {len(missing_files)}/{len(critical_files)}\n"

    if present_files:
        msg += f"\n[OK] Files found:\n"
        for f in sorted(present_files):
            msg += f"  [+] {f}\n"

    if missing_files:
        msg += f"\n[!] Files missing:\n"
        for f in sorted(missing_files):
            msg += f"  [-] {f}\n"
        msg += f"\nNote: Some expected files may not be present if certain scripts were skipped.\n"

    print_to_both(msg, log_file)

    return len(missing_files) == 0

def run_all():
    """Execute complete dissertation analytics pipeline"""
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path('outputs/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f'analysis_log_{timestamp}.txt'
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        
        # Header
        header = f"""
{'=' * 80}
  DISSERTATION ANALYTICS PIPELINE
  Data Breach Disclosure Timing and Market Reactions
  Timothy D. Spivey - University of South Alabama
  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

Log file: {log_path}
"""
        print_to_both(header, log_file)
        
        start_time = time.time()
        
        # Define pipeline
        pipeline = [
            {
                'category': 'DATA ENRICHMENT',
                'scripts': [
                    ('scripts/99_add_cpni_hhi_variables.py', 'Add CPNI & HHI Variables (Essay 1 Alternative Explanations)'),
                ]
            },
            {
                'category': 'DATA PREPARATION',
                'scripts': [
                    ('scripts/53_merge_CONFIRMED_enrichments.py', 'Merge All Enrichments (Prior breaches, breach severity, media coverage, executive turnover, enforcement) → FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'),
                ]
            },
            {
                'category': 'MAIN ANALYSIS',
                'scripts': [
                    ('scripts/70_summary_statistics.py', 'Summary Statistics (Table 1)'),
                    ('scripts/80_essay1_car_regressions.py', 'Essay 1 Main Regressions (H1-H4: CAR on disclosure/FCC/reputation/severity) - HC3 robust SEs as primary'),
                    ('scripts/h1_timing_fcc_interaction.py', 'H1 Theoretical Test: Timing × FCC Interaction (formal test of differential effects by regulatory status, canonical specification)'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/81_post_2007_interaction_test.py', 'FCC Causal Identification (TABLE B8: Post-2007 Interaction Test - Market Returns)'),
                    ('scripts/82_clustered_vs_hc3_comparison.py', 'Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)'),
                    ('scripts/83_fcc_causal_identification.py', 'FCC Causal ID Summary (Industry Fixed Effects, Size Sensitivity Analysis)'),
                    ('scripts/91_essay3_governance_regressions.py', 'Essay 3 Main Regressions (Executive Turnover - Logistic Regression by Window)'),
                    ('scripts/91b_essay3_reduced_form_mediation.py', 'Essay 3 Reduced-Form H6 Test (Correct Specification - No Post-Treatment Variables) + Mediation Decomposition'),
                    ('scripts/91c_essay3_mediation_bootstrap.py', 'Essay 3 Bootstrap Indirect Effect (Nonlinear Mediation on Probability Scale with 95% CI)'),
                    ('scripts/91e_essay3_h6_tost_equivalence.py', 'Essay 3 H6 TOST Equivalence Test (N=651, confirms FCC effect is economically negligible)'),
                    ('scripts/91f_essay3_h6_firm_size_heterogeneity.py', 'Essay 3 H6 Firm Size Heterogeneity (30d/90d/180d quartile analysis - addresses temporal persistence)'),
                    ('scripts/91g_extract_reduced_form_controls.py', 'Essay 3 H6 Control Variable Significance (which breach/firm characteristics predict turnover)'),
                    ('scripts/91h_essay3_cox_hazards.py', 'Essay 3 H6 Cox Proportional Hazards (Alternative functional form robustness; continuous time-to-turnover)'),
                    ('scripts/91j_essay3_ols_lpm_and_negbin.py', 'Essay 3 H6 OLS Linear Probability Model & Negative Binomial (Alternative specifications robustness)'),
                    ('scripts/91k_essay3_robustness_checks.py', 'Essay 3 H6 Robustness: Alternative Thresholds & Restricted Samples (5/10/14-day disclosure windows, data quality checks)'),
                    ('scripts/90_essay2_volatility_regressions.py', 'Essay 2 Volatility Analysis (FCC effect on post-breach volatility, Tables 2-3)'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/84_essay2_post_2007_interaction_test_volatility.py', 'Essay 2 Volatility Causal ID (TABLE B8: Post-2007 Test)'),
                    ('scripts/86_essay3_fcc_causal_identification.py', 'Essay 2 Volatility Causal ID (Industry FE, Size Sensitivity)'),
                ]
            },
            {
                'category': 'CAUSAL IDENTIFICATION: SYNTHETIC CONTROL METHOD',
                'scripts': [
                    ('scripts/scm_mahalanobis_distance.py', 'Essay 1 H2 Causal Identification: Mahalanobis Distance Weighted SCM (Abadie et al. 2010) - breach-event level matching with 500 permutations'),
                ]
            },
            {
                'category': 'NATURAL EXPERIMENT VALIDATION (ARCHIVED: Pre-2007 tests replaced by SCM)',
                'scripts': [
                    # ARCHIVED: Parallel trends and balance test used pre-2007/post-2007 comparison.
                    # Causal ID now uses Synthetic Control Matching. These run as archived checks only.
                    # ('scripts/create_parallel_trends_figure.py', 'Create Parallel Trends Figure (FCC vs non-FCC CAR by year, 2004-2010)'),
                    # ('scripts/create_balance_test_table.py', 'Create Balance Test Table (Pre-2007 firm characteristics parity)'),
                ]
            },
            {
                'category': 'PUBLICATION READINESS: DATA INTEGRITY & CAUSAL ROBUSTNESS',
                'scripts': [
                    ('scripts/00_data_validation_checks.py', 'Data Validation Checks (logical consistency, duplicates, outliers, missing data)'),
                    ('scripts/99_firm_fixed_effects_analysis.py', 'Firm Fixed Effects (H1-H4 within-firm variation, controls unobserved heterogeneity)'),
                    ('scripts/92_enforcement_analysis.py', 'H6 Enforcement Analysis (regulatory enforcement prevalence and predictors)'),
                ]
            },
            {
                'category': 'MACHINE LEARNING',
                'scripts': [
                    ('scripts/60_train_ml_model.py', 'Train ML Model'),
                    ('scripts/61_ml_validation.py', 'ML Validation & Robustness Text'),
                ]
            },
            {
                'category': 'ECONOMIC SIGNIFICANCE & COMPREHENSIVE HETEROGENEITY ANALYSIS',
                'scripts': [
                    ('scripts/96_economic_significance.py', 'Economic Significance Analysis: FCC costs, volatility impact, governance disruption in dollar terms'),
                    ('scripts/97_heterogeneous_mechanisms.py', 'Heterogeneous Mechanisms: Effects vary by firm size, breach type, prior history'),
                    ('scripts/98_sox404_heterogeneity.py', 'HETEROGENEITY PHASE 1: Governance Quality (SOX 404 proxy) - FCC x Governance interaction'),
                    ('scripts/99_cvss_complexity_heterogeneity.py', 'HETEROGENEITY PHASE 2: CVSS Technical Complexity - FCC x Complexity interaction (BREAKTHROUGH: +6.27%**)'),
                    ('scripts/100_ransomware_heterogeneity.py', 'HETEROGENEITY ANALYSIS #3: Ransomware Attack Vector - FCC x Ransomware interaction'),
                    ('scripts/101_media_coverage_heterogeneity.py', 'HETEROGENEITY ANALYSIS #4: Media Coverage Moderation - FCC x Media interaction (+7.08%**)'),
                    ('scripts/102_extended_governance_windows.py', 'HETEROGENEITY ANALYSIS #5: Extended Governance Time Windows - 30d/90d/180d comparison'),
                    ('scripts/103_breach_type_diversity.py', 'HETEROGENEITY ANALYSIS #6: Breach Type Diversity - Multi-type complexity'),
                    ('scripts/104_restatement_summary.py', 'HETEROGENEITY ANALYSIS #7: Restatement Prediction - Data limitation documentation'),
                    ('scripts/105_complexity_index_heterogeneity.py', 'HETEROGENEITY ANALYSIS #8: Complexity Index - Unified severity/CVE/type complexity mechanism'),
                    ('scripts/106_information_environment_composite.py', 'HETEROGENEITY ANALYSIS #9: Information Environment Composite - Media attention & reputation interaction (Spec A/B/C)'),
                ]
            },
            {
                'category': 'ROBUSTNESS CHECKS',
                'scripts': [
                    ('scripts/91_essay3_mediation_analysis.py', 'Mediation Analysis (Essay 3): Does volatility mediate timing→turnover relationship?'),
                    ('scripts/92_heterogeneity_analysis.py', 'Heterogeneity Analysis: CAR/volatility effects vary by firm size quartiles?'),
                    ('scripts/93_market_model_sensitivity.py', 'Event Window Sensitivity: Robustness across 5d, 10d, 30d, 60d, 90d CARs'),
                    ('scripts/94_falsification_tests.py', 'Falsification Tests: Pre-breach validation & breach-specificity confirmation'),
                    ('scripts/95_low_r2_sensitivity.py', 'Low R² Sensitivity: Model adequacy with alternative specifications'),
                    ('scripts/robustness_1_alternative_windows.py', 'Alternative Event Windows: CAR across multiple breach-to-event intervals'),
                    ('scripts/robustness_2_timing_thresholds.py', 'Timing Thresholds: Disclosure timing effects (1d, 3d, 7d, 14d, 30d)'),
                    ('scripts/robustness_3_sample_restrictions.py', 'Sample Restrictions: Results stratified by FCC, data type, firm size'),
                    ('scripts/robustness_4_standard_errors.py', 'Standard Errors: HC3, Clustered, Bootstrap comparison'),
                    ('scripts/robustness_5_fixed_effects.py', 'Fixed Effects: Industry 2-digit, 4-digit SIC, Year, and Firm FE'),
                    ('scripts/power_analysis_h3_h4.py', 'Power Sensitivity Analysis: H3/H4 null hypothesis assessment (MDE at 80% power)'),
                ]
            },
            {
                'category': 'LONG-HORIZON ANALYSIS & MITCHELL-STAFFORD ROBUSTNESS',
                'scripts': [
                    ('scripts/overlap_audit_fcc_clustering.py', 'Overlap Audit: Quantify event clustering in FCC sample (72.7% overlap at 90d) - diagnose Mitchell-Stafford problem severity'),
                    ('scripts/corrected_longrun_car_clustering.py', 'Corrected Long-Horizon CAR: Compute CAR at 60d/90d (not BHAR), test with calendar-month clustering and non-overlapping sample'),
                    ('scripts/calendar_month_clustering_60_90.py', 'Calendar-Month Clustering Test: Check whether 60d/90d results survive clustering correction for overlapping events'),
                ]
            },
            {
                'category': 'FACTOR MODEL & PERSISTENCE TESTING',
                'scripts': [
                    ('scripts/download_fama_french_factors.py', 'Download Fama-French Factors (if not already available): Mom, FF5 factors from Ken French data library'),
                    ('scripts/factor_model_carhart_ff5.py', 'Factor Model Robustness: Test H1-H4 under market model, Carhart 4-factor, FF5 (detect momentum artifact in BHAR p=0.048)'),
                    ('scripts/extended_bhar_60d_90d.py', 'Extended BHAR Windows: Compute 60-day and 90-day BHAR from daily returns, test persistence vs mean reversion (H2 coefficient trajectory)'),
                ]
            },
            {
                'category': 'DEFENSE PREPARATION',
                'scripts': [
                    ('scripts/defense_prep_all_tasks.py', 'Pre-Defense Preparation: Five critical tasks - FCC economic significance, deduplication summary, H2 stability, power analysis, SCM vs OLS comparison'),
                ]
            }
        ]
        
        # Track results
        results = {}
        
        # Step 0: Verify data
        if not verify_data(log_file):
            msg = "\n[FATAL] Cannot proceed without data file\n"
            print_to_both(msg, log_file)
            return False

        # Run all scripts
        for section in pipeline:
            category = section['category']
            scripts = section['scripts']
            
            # Category header
            cat_header = f"\n{'=' * 80}\n{category}\n{'=' * 80}\n"
            print_to_both(cat_header, log_file)
            
            for script_path, description in scripts:
                # Check if script exists
                if not Path(script_path).exists():
                    msg = f"\n[SKIP] Script not found: {script_path}\n"
                    print_to_both(msg, log_file)
                    results[description] = False
                    continue
                
                # Run script
                success = run_script(script_path, description, log_file)
                results[description] = success
        
        # Calculate timing
        total_time = time.time() - start_time
        
        # Summary
        summary_header = f"\n{'=' * 80}\nPIPELINE SUMMARY\n{'=' * 80}\n"
        print_to_both(summary_header, log_file)
        
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]

        summary = f"""
Results:
  [OK] Successful: {len(successful)}/{len(results)}
  [XX] Failed:     {len(failed)}/{len(results)}

Total Execution Time: {total_time/60:.1f} minutes
"""
        print_to_both(summary, log_file)

        if successful:
            success_list = "\n[SUCCESS] Completed:\n" + "\n".join([f"  [+] {s}" for s in successful]) + "\n"
            print_to_both(success_list, log_file)

        if failed:
            fail_list = "\n[FAILED] Incomplete:\n" + "\n".join([f"  [-] {f}" for f in failed]) + "\n"
            print_to_both(fail_list, log_file)
        
        # Output locations
        outputs = f"""
{'=' * 80}
OUTPUT LOCATIONS
{'=' * 80}

Summary Statistics:
  outputs/tables/TABLE1_PANEL_A_full_sample.csv
  outputs/tables/TABLE1_PANEL_B_crsp_sample.csv
  outputs/tables/TABLE1_PANEL_C_by_fcc.csv
  outputs/tables/TABLE1_PANEL_D_by_timing.csv
  outputs/tables/TABLE1_COMBINED.txt

ARCHIVED (Pre-2007 comparison):
  outputs/figures/FIGURE_PARALLEL_TRENDS.png (Archived: Parallel trends, 2004-2010)
  outputs/tables/TABLE_BALANCE_TEST.csv (Archived: Pre-2007 balance test)

Essay 2 Regression Tables (Firm-Clustered SEs):
  outputs/tables/essay2/TABLE2_baseline_disclosure.txt
  outputs/tables/essay2/TABLE3_fcc_regulation.txt
  outputs/tables/essay2/TABLE4_prior_breaches.txt
  outputs/tables/essay2/TABLE5_breach_severity.txt
  outputs/tables/essay2/TABLE_APPENDIX_alternative_explanations.txt (CPNI & HHI robustness)

Essay 1 - Synthetic Control Matching (PRIMARY CAUSAL ID for H2):
  outputs/scm_crsp_with_sprint/scm_crsp_sprint_proxy_results.csv (SCM results: n=41 FCC firms, -4.03% effect, p=0.003)
  outputs/scm_crsp_with_sprint/consolidated_by_company.csv (Aggregate by company)
  outputs/ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt (Complete summary of SCM methodology and results)

Essay 2 Robustness Checks (Post-2007 sample restriction test):
  outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt (Robustness: FCC effect in post-2007 sample)
  outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt (Robustness: FCC effect with industry FE)
  outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt (Robustness: FCC effect by firm size)
  outputs/tables/essay2/FCC_Causal_ID_Summary.txt (Robustness summary)
  outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt (Standard errors robustness)
  outputs/tables/essay2/H1_TOST_Equivalence_Test.txt (H1 null hypothesis equivalence test)
  outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt (Multicollinearity diagnostics)

Essay 3 Governance Response (Executive Turnover - Main Results):
  outputs/tables/essay3_governance/reduced_form_h6_results.csv (Reduced form: FCC effect on turnover, N=651)
  outputs/tables/essay3_governance/mediator_first_stage_results.csv (First stage: FCC → immediate_disclosure, 14.52pp)
  outputs/tables/essay3_governance/with_mediator_model_coefficients.csv (Mediation model: FCC + immediate_disclosure)
  outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv (Bootstrap indirect effects, 1,000 iterations)
  outputs/tables/essay3_governance/h6_tost_equivalence_results.csv (TOST equivalence test, N=651, ±10pp bounds)
  outputs/tables/essay3_governance/H6_TOST_Equivalence_Test.txt (TOST interpretation and results)
  outputs/tables/essay3_governance/h6_reduced_form_all_coefficients.csv (Control variable significance: which predictors reach p<.10)
  outputs/tables/essay3_governance/h6_firm_size_heterogeneity_full.csv (Heterogeneity by firm size: 30d/90d/180d quartile analysis)
  outputs/tables/essay3_governance/CAUSAL_ID_COVARIATE_BALANCE.csv (Balance test: FCC vs non-FCC firms)
  outputs/tables/essay3_governance/CAUSAL_ID_PLACEBO_TESTS.csv (Placebo tests: alternative governance outcomes)
  outputs/tables/essay3_governance/CAUSAL_ID_DOSE_RESPONSE.csv (Dose-response: FCC effect by severity)
  outputs/tables/essay3_governance/cox_model_all_turnover.csv (Cox PH: FCC HR=1.127, p=.702; Schoenfeld p=.020 for FCC)
  outputs/tables/essay3_governance/H6_Cox_Model_Results.txt (Cox interpretation: PH violation noted, logistic regression is primary spec)
  outputs/tables/essay3_governance/ols_lpm_h6_results.csv (OLS LPM: FCC effects 0.024pp, 0.0015pp, -0.0138pp; all p>.63)
  outputs/tables/essay3_governance/negative_binomial_h6_results.csv (Neg Binomial: FCC IRR=1.220, p=.069; marginally NS)
  outputs/tables/essay3_governance/robustness_check2_disclosure_thresholds.csv (Alternative thresholds 5/10/14-day: FCC all null p>.35)
  outputs/tables/essay3_governance/robustness_check3_restricted_samples.csv (Restricted samples: unambiguous dates, large firms, complete data all N=651, identical results)

Essay 3 Robustness Checks (Volatility):
  outputs/tables/essay3/TABLE2_volatility_changes.txt
  outputs/tables/essay3/TABLE3_information_asymmetry.txt
  outputs/tables/essay3/TABLE_B8_post_2007_interaction_volatility.txt (Robustness: FCC volatility effect in post-2007 sample)
  outputs/tables/essay3/TABLE_FCC_Industry_FE_Comparison_Volatility.txt (Robustness: FCC volatility effect with industry FE)
  outputs/tables/essay3/TABLE_FCC_Size_Sensitivity_Volatility.txt (Robustness: FCC volatility effect by firm size)
  outputs/tables/essay3/FCC_Causal_ID_Summary_Volatility.txt (Robustness summary)

Heterogeneity Analysis Results (Publication Appendix Tables B11-B17):
  outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv (Phase 1: Governance quality, B11)
  outputs/tables/TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv (Phase 2: CVSS complexity, B12) [BREAKTHROUGH: +6.27%**]
  outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv (Analysis #3: Ransomware, B13)
  outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv (Analysis #4: Media coverage, B14) [+7.08%**]
  outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv (Analysis #5: Time windows, B15)
  outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv (Analysis #6: Type diversity)
  outputs/tables/TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv (Analysis #8: Complexity index, Essay 2 mechanism)
  outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv (Analysis #9: Information environment, Essay 2 mechanism - Spec A/B/C)

Enriched Datasets:
  Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv (Phase 1)
  Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv (Phase 2, used by Analyses #3-7)

ML Outputs:
  outputs/ml_models/ml_model_summary.csv
  outputs/ml_models/feature_importance_car30d.csv
  outputs/ml_models/feature_importance_car30d.png
  outputs/validation/dissertation_robustness_section.txt

Robustness Tables:
  outputs/robustness/tables/R01_alternative_windows_summary.csv
  outputs/robustness/tables/R02_timing_thresholds_summary.csv
  outputs/robustness/tables/R03_sample_restrictions_summary.csv
  outputs/robustness/tables/R04_standard_errors_summary.csv
  outputs/robustness/tables/R05_fixed_effects_summary.csv

Robustness Figures:
  outputs/robustness/figures/R02_timing_thresholds.png
  outputs/robustness/figures/R03_sample_restrictions.png
  outputs/robustness/figures/R04_standard_errors.png
  outputs/robustness/figures/R05_fixed_effects.png

{'=' * 80}
KEY FINDINGS
{'=' * 80}

Essay 1 - Market Reactions (Alternative Explanations):
  [+] CPNI sensitivity test: FCC coefficient robust to CPNI control (-1.15%, p=0.010)
  [+] Market concentration test: FCC coefficient robust to HHI control (-2.44%, p=0.006)
  [+] Both controls: FCC coefficient remains significant (-1.22%, p=0.006)

Essay 2 - Market Reactions (Main, Deduplicated 784-row sample):
  [-] Prior breaches NOT significant (H3 null on clean data)
  [-] Health breaches NOT significant (H4 null on clean data)
  [-] Immediate disclosure NOT significant (H1 not supported)
  [+] H1 null hypothesis validated via TOST equivalence test (90% CI within ±2.10% bounds)
  [+] Sensitivity check: H3/H4 null when Cencora excluded from 1,054 dataset, confirming artifacts not real effects

FCC Causal Identification (PRIMARY: Synthetic Control Matching):
  [+] SCM n=41 firms: −4.03% FCC effect (p=0.003, 95% CI: [-6.52%, -1.55%])
  [+] Sprint recovered via T-Mobile proxy: 13 breaches, result robust
  [+] Firm heterogeneity: range −29% (DISH) to +10% (Charter)

  ROBUSTNESS (Post-2007 sample restriction test):
  [+] FCC effect in post-2007 period: −2.19% (p=0.031, HC3 SEs)
  [+] Confirms FCC penalty exists in post-regulation era

Standard Errors Robustness (Clustered vs HC3):
  [+] Firm-clustered SEs increase 38% on average vs HC3
  [+] FCC effect remains significant with conservative clustering
  [+] Main specification findings are robust to clustering

Essay 3 - Information Asymmetry (Volatility):
  [+] Pre-breach volatility dominates (R² = 0.39)
  [+] Disclosure timing minimal effect

Essay 3 - Governance Response (Executive Turnover - H6):
  [-] FCC effect on CEO turnover: 2.55pp (30d), 0.11pp (90d), -1.42pp (180d) — ALL NULL (p>.05, N=651)
  [+] TOST Equivalence Test (N=651, ±10pp bounds):
      - 30d: INCONCLUSIVE (CI: [-6.80pp, +11.90pp], upper bound exceeds by 1.90pp)
      - 90d: PASSES (CI: [-9.38pp, +9.60pp], both bounds pass)
      - 180d: INCONCLUSIVE (CI: [-10.84pp, +8.00pp], lower bound exceeds by 0.84pp)
  [+] Mediation analysis: FCC → immediate_disclosure (14.52pp, p<.001) but disclosure → turnover NOT significant
  [+] Causal ID validation: Balance test ✓, Placebo tests ✓, Dose-response ✓, Temporal ✓
  [+] Control variable significance (N=651):
      - Leverage predicts turnover at 30d (p=.007***)
      - Prior breaches predict turnover at 90d/180d (p=.019**, .023**)
      - Health breach predicts turnover at 90d/180d (p=.056*, .035**)
      - Firm size does NOT predict turnover (all p>.21)
  [+] Firm-size heterogeneity (30d/90d/180d quartile analysis):
      - Q2 produces singular matrix at 90d/180d (outcome lacks variation)
      - Q3 shows consistent negative FCC pattern (-17.5pp at 30d, -11.5pp at 90d, -17.6pp at 180d, marginal significance)
      - Q1/Q4 show null FCC effects across all windows
      - Interpretation: Heterogeneity is exploratory; appendix-only due to singular matrix in Q2 and marginal p-values in Q3
  [+] Interpretation: FCC regulation does not trigger executive turnover in aggregate; baseline turnover (46%) is breach-driven, moderated by prior history and breach type

Robustness:
  [+] Prior breach effects robust across all specifications
  [+] Health breach effects robust across all specifications
  [+] FCC effect robust to firm-level clustering
  [-] Disclosure timing effects NOT robust

Heterogeneity Analysis (Phase 1-2 + Analyses #3-7):
  [+] PHASE 1 (Governance Quality): Governance weakness independent of FCC (+0.55%, NS)
  [+] PHASE 2 (CVSS Complexity) - BREAKTHROUGH: Simple breaches penalized 6x more by FCC
      - Low-complexity FCC effect: -6.46%***
      - High-complexity FCC effect: -0.19%
      - Interaction: +6.27%** (p=0.007)
  [+] ANALYSIS #3 (Ransomware): Ransomware protected from FCC penalty (-8.34%, p=0.069)
  [+] ANALYSIS #4 (Media Coverage): Media shields FCC penalty (+7.08%**, p=0.006)
      - Low-media breaches: -3.33%*** FCC effect
      - High-media breaches: +3.75% FCC effect
  [+] ANALYSIS #5 (Governance Windows): FCC effect immediate but transient (decays over time)
  [+] ANALYSIS #6 (Type Diversity): Type diversity NOT moderator (-0.315%, NS)
  [-] ANALYSIS #7 (Restatement): Data limitation - Compustat covers only 2.6% of breach firms

Essay 2 Mechanism Analysis (Scripts 105-106):
  [+] ANALYSIS #8 (Complexity Index): Complexity does NOT amplify FCC volatility effect
      - FCC × Complexity interaction: -0.0784pp (p=0.9700, NS)
      - Finds: FCC impact independent of unified severity/CVE/type complexity
  [+] ANALYSIS #9 (Information Environment Composite):
      - Spec A (Media Attention): +0.5585pp (p=0.80, NS)
      - Spec B (Reputation Weakness): -4.5897pp (p=0.03)*
      - Spec C (Composite, KEY): -2.6142pp (p=0.27, NS)
      - Finding: Information environment does not significantly amplify FCC volatility effect

Central Finding: FCC penalty operates through EXPECTATION MISMATCH
  - Markets expect simple breaches to resolve quickly → FCC deadline violates expectations
  - Markets expect complex breaches will take time → FCC deadline adds no penalty
  - Media coverage signals information already available → FCC adds no marginal value
  - Firm size is the dominant moderator: smallest firms most constrained by FCC deadline

{'=' * 80}
NEXT STEPS
{'=' * 80}

1. Review Essay 1 alternative explanations (CPNI & HHI) in outputs/tables/essay2/TABLE_APPENDIX_alternative_explanations.txt
2. Review FCC causal identification test (TABLE B8) in outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt
3. Review standard errors robustness (TABLE B9) in outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt
4. Review H1 equivalence test results in outputs/tables/essay2/H1_TOST_Equivalence_Test.txt
5. Review VIF diagnostics in outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt
6. Copy regression tables and appendix tables into dissertation
7. Review robustness check results in outputs/robustness/
8. Include ML validation (optional) in appendix
9. Begin writing Results sections for Essays 2 & 3

Complete log saved to: {log_path}

{'=' * 80}
"""
        print_to_both(outputs, log_file)
        
        # Final status - check with updated description names
        critical_scripts_succeeded = (
            results.get('Summary Statistics (Table 1)', False) and
            results.get('Essay 2 Regressions (Tables 2-5, firm-clustered SEs) + TOST + VIF', False) and
            results.get('Essay 3 Regressions (Tables 2-3)', False)
        )

        if critical_scripts_succeeded:
            final = f"\n[***] [SUCCESS] Core dissertation analysis complete!\n{'=' * 80}\n"
            print_to_both(final, log_file)

            # Verify critical outputs exist
            outputs_verified = verify_outputs(log_file)

            # Launch Streamlit dashboard
            dashboard_msg = f"""
{'=' * 80}
LAUNCHING DASHBOARD
{'=' * 80}

Opening Streamlit dashboard in your browser...
Dashboard URL: http://localhost:8502

If browser doesn't open automatically, visit the URL above.
To stop the dashboard, press Ctrl+C in the terminal.

{'=' * 80}
"""
            print_to_both(dashboard_msg, log_file)

            # Launch dashboard in a new process
            try:
                dashboard_path = Path(__file__).parent / 'Dashboard' / 'app.py'
                if dashboard_path.exists():
                    # Use subprocess to launch Streamlit
                    subprocess.Popen(
                        [sys.executable, '-m', 'streamlit', 'run', str(dashboard_path)],
                        env=os.environ.copy()
                    )
                    print("\n[+] Dashboard launched successfully")
                else:
                    print(f"\n[!] Dashboard app not found at {dashboard_path}")
            except Exception as e:
                print(f"\n[!] Could not launch dashboard: {str(e)}")
                print("  You can manually launch it with: streamlit run Dashboard/app.py")

            return True
        else:
            final = f"\n⚠ [WARNING] Some critical analyses failed or script descriptions don't match - review log\n{'=' * 80}\n"
            print_to_both(final, log_file)
            return False

def main():
    """Main entry point"""
    try:
        success = run_all()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n[FATAL ERROR] Pipeline crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()