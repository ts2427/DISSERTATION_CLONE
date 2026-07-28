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

CRITICAL: DATA PIPELINE ROOT (FORM 499 CORRECTED)
==================================================
The current source of truth for this pipeline is:
  → Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv

This dataset incorporates:
  1. CIK audit (removed fuzzy-match duplicates, n=5)
  2. Entity matching (two-clause rule for Form 499 filers)
  3. Form 499 filer registry (authoritative regulatory classification)

Treatment variable: fcc_form499 (Form 499 filer at breach date)
  - Replaces: fcc_reportable (SIC-based proxy)
  - FINAL membership (7/28/2026 adjudications: Cricket treated, Boost treated,
    DISH untreated, Aero Charter excluded): 118 treated / 37 firms in CRSP
    sample; 115 treated in the H1-H4 regression sample (N=648)

This pipeline regenerates the corrected dataset from scratch via the chain:
  46 (Item 5.02 extraction) -> 53 (enrichment merge) -> 99 (CPNI/HHI) ->
  98 (governance) -> 121a-c (Form 499 matching) -> 122 (manual adjudications)
Individual script runs may produce stale outputs. Always run the complete
pipeline for final analysis numbers.

ESSAY 3 OUTCOME (ITEM 5.02, SUBMISSIONS API)
============================================
Script 46 extracts Item 5.02 filings via the EDGAR submissions JSON API
(structured item metadata, no HTML scraping). Cached per CIK; first run
~10-20 min, subsequent runs ~2-5 min. Verified base rates: 20.1% (30d),
44.1% (90d), 68.2% (180d). Note: Item 5.02 covers all director/officer
events (appointments, elections, comp), not only departures.

CANONICAL RESULTS (AUDIT CLOSED 7/28/2026)
==========================================
See ESSAY_RESULTS_SUMMARY_CORRECTED.md for the authoritative figures.
Summary: Essay 1 H1-H3 bounded nulls (TOST .045/.013/<.001 at +-2.10pp),
H4 inconclusive; Essay 2 H5 bounded null (main +0.12pp p=.914, TOST .044),
quartile pattern = noise; Essay 3 H6 null-unbounded -> inconclusive
(MDEs 11.5-14.9pp), Cox HR 1.43 p=.018 reported as robustness only, not
promoted. First stage 16.71pp descriptive-only (DD unidentified, 4 pre-2007
obs). Superseded values are listed in outputs/STALE_RESULTS_MANIFEST.txt.
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

# Scripts that legitimately need more than the default 10-minute timeout
LONG_RUNNING_SCRIPTS = {
    'scripts/46_executive_changes_item5_02_with_cache.py': 2400,  # SEC 8-K download, 20-30 min first run
}

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

    script_timeout = LONG_RUNNING_SCRIPTS.get(script_path.replace('\\', '/'), 600)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=script_timeout,
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
        status = f"[ERROR] Script timeout (>{script_timeout//60} minutes)\n"
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

    # Primary: Form 499 corrected dataset
    data_file = Path('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')

    if data_file.exists():
        file_size = data_file.stat().st_size / (1024 * 1024)
        msg = f"  [OK] Form 499 corrected dataset found ({file_size:.1f} MB)\n  [OK] Ready to proceed\n"
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
        # Form 499 Corrected (PRIMARY)
        Path('outputs/h1_h4_form499_corrected_summary.csv'),
        Path('outputs/h1_h4_form499_corrected_regression_results.txt'),
        Path('outputs/h5_form499_corrected_heterogeneity.csv'),
        Path('outputs/h5_form499_corrected_regression_results.txt'),
        Path('outputs/h6_form499_corrected_power_analysis.csv'),
        Path('outputs/h6_form499_corrected_regression_results.txt'),
        # Reference (SIC-based)
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
                'category': 'DATA PREPARATION - OUTCOME EXTRACTION',
                'scripts': [
                    ('scripts/46_executive_changes_item5_02_with_cache.py', 'Essay 3 Outcome: Executive Turnover from 8-K Item 5.02 (cached; 20-30 min on first run, 2-5 min after) [MUST RUN BEFORE SCRIPT 53]'),
                ]
            },
            {
                'category': 'DATA PREPARATION - ENRICHMENTS',
                'scripts': [
                    ('scripts/53_merge_CONFIRMED_enrichments.py', 'Merge All Enrichments (Prior breaches, breach severity, media coverage, Item 5.02 executive turnover, enforcement) → FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'),
                    ('scripts/99_add_cpni_hhi_variables.py', 'Add CPNI & HHI Variables (Essay 1 Alternative Explanations)'),
                    ('scripts/98_sox404_heterogeneity.py', 'Governance Enrichment: SOX 404 proxy → FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv (required by 121c)'),
                ]
            },
            {
                'category': 'DATA PREPARATION - FORM 499 CLASSIFICATION',
                'scripts': [
                    ('scripts/121a_form499_entity_matching.py', 'Form 499 Entity Matching: Exact-string match (normalized) PRC firms to FCC registry (107/779 matched)'),
                    ('scripts/121b_form499_coverage_validation.py', 'Form 499 Coverage Validation: Validate matches against start/end dates (88 date-valid)'),
                    ('scripts/121c_merge_form499_classification.py', 'Merge Form 499 Classification: Add fcc_form499 binary to dataset (79 treated in regression sample)'),
                    ('scripts/122_manual_form499_corrections.py', 'Manual Form 499 Corrections: Apply two-clause rule to SIC-flagged firms (add +36 treated via parent-brand rule) → FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv'),
                ]
            },
            {
                'category': 'FORM 499 CORRECTED ANALYSES (PRIMARY)',
                'scripts': [
                    ('scripts/86c_essay1_h1_h4_form499_corrected.py', 'H1-H4 Re-estimation with Form 499 Corrected Classification (n=115 treated, authoritative regulatory status)'),
                    ('scripts/90b_essay2_h5_form499_corrected.py', 'H5 Volatility Re-estimation with Form 499 Corrected (First real result, post-deduplication)'),
                    ('scripts/91m_essay3_h6_form499_corrected.py', 'H6 Executive Turnover Re-estimation with Form 499 Corrected (First real result, MDE/TOST)'),
                ]
            },
            {
                'category': 'MAIN ANALYSIS (REFERENCE)',
                'scripts': [
                    ('scripts/70_summary_statistics.py', 'Summary Statistics (Table 1)'),
                    ('scripts/80_essay1_car_regressions.py', 'Essay 1 Main Regressions (H1-H4: CAR on disclosure/FCC/reputation/severity) - HC3 robust SEs as primary [REFERENCE - SIC-BASED]'),
                    ('scripts/h1_timing_fcc_interaction.py', 'H1 Theoretical Test: Timing × FCC Interaction (formal test of differential effects by regulatory status, canonical specification)'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/81_post_2007_interaction_test.py', 'FCC Causal Identification (TABLE B8: Post-2007 Interaction Test - Market Returns)'),
                    ('scripts/82_clustered_vs_hc3_comparison.py', 'Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)'),
                    ('scripts/83_fcc_causal_identification.py', 'FCC Causal ID Summary (Industry Fixed Effects, Size Sensitivity Analysis)'),
                    ('scripts/90_essay2_volatility_regressions.py', 'Essay 2 Volatility Analysis (FCC effect on post-breach volatility, Tables 2-3) [COMPLETE]'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/84_essay2_post_2007_interaction_test_volatility.py', 'Essay 2 Volatility Causal ID (TABLE B8: Post-2007 Test)'),
                    ('scripts/86_essay3_fcc_causal_identification.py', 'Essay 2 Volatility Causal ID (Industry FE, Size Sensitivity)'),
                    ('scripts/91_essay3_governance_regressions.py', 'Essay 3 Main Regressions (Executive Turnover - Logistic Regression by Window) [UNBLOCKED]'),
                    ('scripts/91b_essay3_reduced_form_mediation.py', 'Essay 3 Reduced-Form H6 Test (Correct Specification - No Post-Treatment Variables)'),
                    ('scripts/91c_essay3_mediation_bootstrap.py', 'Essay 3 Bootstrap Indirect Effect (Nonlinear Mediation on Probability Scale with 95% CI)'),
                    ('scripts/91e_essay3_h6_tost_equivalence.py', 'Essay 3 H6 TOST Equivalence Test (N=651, confirms FCC effect is economically negligible)'),
                    ('scripts/91f_essay3_h6_firm_size_heterogeneity.py', 'Essay 3 H6 Firm Size Heterogeneity (30d/90d/180d quartile analysis - addresses temporal persistence)'),
                    ('scripts/91g_extract_reduced_form_controls.py', 'Essay 3 H6 Control Variable Significance (which breach/firm characteristics predict turnover)'),
                    ('scripts/91h_essay3_cox_hazards.py', 'Essay 3 H6 Cox Proportional Hazards (Alternative functional form robustness; continuous time-to-turnover)'),
                    ('scripts/91j_essay3_ols_lpm_and_negbin.py', 'Essay 3 H6 OLS Linear Probability Model & Negative Binomial (Alternative specifications robustness)'),
                    ('scripts/91k_essay3_robustness_checks.py', 'Essay 3 H6 Robustness: Alternative Thresholds & Restricted Samples (5/10/14-day disclosure windows, data quality checks)'),
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
                    ('scripts/extract_merge_fama_french.py', 'Extract and Merge Fama-French Factors: Process Ken French data files (FF3, Momentum, FF5) locally with proper header handling'),
                    ('scripts/sample_composition_diagnostic.py', 'Sample Composition Diagnostic: Isolate model choice effects from sample loss (critical: market-adjusted remains p=0.058 on restricted N=519 sample)'),
                    ('scripts/ff3_simple_merge.py', 'FF3 Simple Merge Robustness: Test H1-H4 under FF3 specification (N=519, coefficient stable -2.12%, p-value inflation from factor adjustment, not sample loss)'),
                    ('scripts/factor_model_carhart_ff5.py', 'Factor Model Robustness: Test H1-H4 under market model, Carhart 4-factor, FF5 (coefficient stable across all specifications)'),
                    ('scripts/extended_bhar_60d_90d.py', 'Extended BHAR Windows: Compute 60-day and 90-day BHAR from daily returns, test persistence vs mean reversion (Mitchell-Stafford test)'),
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
CANONICAL RESULTS (AUDIT CLOSED 7/28/2026)
{'=' * 80}

Authoritative figures live in ESSAY_RESULTS_SUMMARY_CORRECTED.md - read that,
not this log, when drafting. Superseded values: outputs/STALE_RESULTS_MANIFEST.txt.

Essay 1 (N=648, treated 115, Form 499 classification):
  H1 +0.61pp p=.482, TOST .045  -> BOUNDED NULL
  H2 -0.42pp p=.575, TOST .013  -> BOUNDED NULL
  H3 +0.03pp p=.645, TOST <.001 -> BOUNDED NULL
  H4 -0.39pp p=.811, TOST .148  -> INCONCLUSIVE (underpowered)
  Frame: three bounded nulls and one underpowered.
  First stage 16.71pp is DESCRIPTIVE ONLY (DD unidentified: 4 pre-2007 obs).

Essay 2 (H5, N=644, spec includes return_volatility_pre, R2=.42):
  Main +0.12pp p=.914, MDE 3.23pp, TOST +-2.10pp p=.044 -> BOUNDED NULL
  Quartiles: only Q2 significant (one cell of four, no gradient) -> noise.

Essay 3 (H6, N=646, Item 5.02 outcome, base rates 20.1/46.3/72.0%):
  AMEs +1.79/+9.14/+3.08pp (p=.664/.086/.535), MDEs 11.5-14.9pp
  -> NULL, UNBOUNDED -> report as INCONCLUSIVE; equivalence claims retired.
  Cox HR 1.43 p=.018 (Schoenfeld .479): robustness only, NOT promoted.

Membership (final, 7/28 adjudications): Cricket treated (caught defect),
Boost treated (clause b), DISH untreated, Aero Charter excluded.
118 treated / 37 firms CRSP; 115 in regression.

Data-quality contribution: four documented failure modes
(DATA_QUALITY_DOCUMENTATION.md) - CIK duplicates, name-token collisions,
SIC-as-regulatory-proxy, silent Item 5.02 extraction failure.

Open questions (Dr. Johnson): identification path (descriptive vs state-law
staggered adoption) and Essay 2 / job-talk center. SCM: rebuild under scpi
with Form 499 membership or drop (pending Lambert) - not committee-locked.

Complete log saved to: {log_path}

{'=' * 80}
"""
        print_to_both(outputs, log_file)
        
        # Final status - keyed to the Form 499 primary analyses (match pipeline descriptions)
        critical_keys = [
            'H1-H4 Re-estimation with Form 499 Corrected Classification (n=115 treated, authoritative regulatory status)',
            'H5 Volatility Re-estimation with Form 499 Corrected (First real result, post-deduplication)',
            'H6 Executive Turnover Re-estimation with Form 499 Corrected (First real result, MDE/TOST)',
        ]
        critical_scripts_succeeded = all(results.get(k, False) for k in critical_keys)

        # Verify critical outputs exist regardless of status
        outputs_verified = verify_outputs(log_file)

        if critical_scripts_succeeded and outputs_verified:
            final = f"\n[***] [SUCCESS] Core dissertation analysis complete and outputs verified.\n{'=' * 80}\n"
            print_to_both(final, log_file)
            return True
        elif critical_scripts_succeeded:
            final = f"\n[OK] Primary analyses succeeded; some expected output files missing - review verification above.\n{'=' * 80}\n"
            print_to_both(final, log_file)
            return True
        else:
            missing = [k for k in critical_keys if not results.get(k, False)]
            final = ("\n[WARNING] Primary Form 499 analyses did not all succeed - review log.\n"
                     + "\n".join(f"  [-] {k}" for k in missing)
                     + f"\n{'=' * 80}\n")
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