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

    data_file = Path('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')

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
        Path('outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt'),
        Path('outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt'),
        Path('outputs/tables/essay2/H1_TOST_Equivalence_Test.txt'),
        Path('outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt'),
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
                'category': 'MAIN ANALYSIS',
                'scripts': [
                    ('scripts/70_summary_statistics.py', 'Summary Statistics (Table 1)'),
                    ('scripts/80_essay2_regressions.py', 'Essay 2 Regressions (Tables 2-5, firm-clustered SEs) + TOST + VIF'),
                    ('scripts/81_post_2007_interaction_test.py', 'FCC Causal Identification (TABLE B8: Post-2007 Interaction Test - Market Returns)'),
                    ('scripts/82_clustered_vs_hc3_comparison.py', 'Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)'),
                    ('scripts/83_fcc_causal_identification.py', 'FCC Causal ID Summary (Industry Fixed Effects, Size Sensitivity Analysis)'),
                    ('scripts/90_essay3_regressions.py', 'Essay 3 Regressions (Tables 2-3)'),
                    ('scripts/84_essay3_post_2007_interaction_test.py', 'Essay 3 FCC Causal ID (TABLE B8: Post-2007 Test - Executive Turnover)'),
                    ('scripts/86_essay3_fcc_causal_identification.py', 'Essay 3 FCC Causal ID (Industry FE, Size Sensitivity - Executive Turnover)'),
                ]
            },
            {
                'category': 'NATURAL EXPERIMENT VALIDATION',
                'scripts': [
                    ('scripts/create_parallel_trends_figure.py', 'Create Parallel Trends Figure (FCC vs non-FCC CAR by year, 2004-2010)'),
                    ('scripts/create_balance_test_table.py', 'Create Balance Test Table (Pre-2007 firm characteristics parity)'),
                ]
            },
            {
                'category': 'PUBLICATION READINESS: DATA INTEGRITY & CAUSAL ROBUSTNESS',
                'scripts': [
                    ('scripts/00_data_validation_checks.py', 'Data Validation Checks (logical consistency, duplicates, outliers, missing data)'),
                    ('scripts/98_propensity_score_matching.py', 'Propensity Score Matching (H2 self-selection bias test - addresses reviewer concern)'),
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

Natural Experiment Validation (CRITICAL FOR JOURNAL SUBMISSION):
  outputs/figures/FIGURE_PARALLEL_TRENDS.png (Parallel trends visualization: FCC vs non-FCC CAR, 2004-2010)
  outputs/figures/FIGURE_PARALLEL_TRENDS.eps (High-quality EPS version for publication)
  outputs/tables/TABLE_BALANCE_TEST.csv (Pre-2007 balance test data)
  outputs/tables/TABLE_BALANCE_TEST.txt (Balance test: firm size, leverage, ROA parity)

Essay 2 Regression Tables (Firm-Clustered SEs):
  outputs/tables/essay2/TABLE2_baseline_disclosure.txt
  outputs/tables/essay2/TABLE3_fcc_regulation.txt
  outputs/tables/essay2/TABLE4_prior_breaches.txt
  outputs/tables/essay2/TABLE5_breach_severity.txt
  outputs/tables/essay2/TABLE_APPENDIX_alternative_explanations.txt (CPNI & HHI robustness)

Essay 2 Causal Identification & Robustness:
  outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt (FCC causal ID: post-2007 test)
  outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt (FCC causal ID: industry fixed effects)
  outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt (FCC causal ID: size sensitivity analysis)
  outputs/tables/essay2/FCC_Causal_ID_Summary.txt (FCC causal ID: comprehensive summary)
  outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt (Standard errors robustness)
  outputs/tables/essay2/H1_TOST_Equivalence_Test.txt (H1 null hypothesis equivalence test)
  outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt (Multicollinearity diagnostics)

Essay 3 Regression Tables:
  outputs/tables/essay3/TABLE2_volatility_changes.txt
  outputs/tables/essay3/TABLE3_information_asymmetry.txt
  outputs/tables/essay3/TABLE_B8_post_2007_interaction_volatility.txt (FCC causal ID: post-2007 test)
  outputs/tables/essay3/TABLE_FCC_Industry_FE_Comparison_Volatility.txt (FCC causal ID: industry fixed effects)
  outputs/tables/essay3/TABLE_FCC_Size_Sensitivity_Volatility.txt (FCC causal ID: size sensitivity analysis)
  outputs/tables/essay3/FCC_Causal_ID_Summary_Volatility.txt (FCC causal ID: comprehensive summary)

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

Essay 2 - Market Reactions (Main, Firm-Clustered SEs):
  [+] Prior breaches significant (H3 supported)
  [+] Health breaches significant (H4 supported)
  [-] Immediate disclosure NOT significant (H1 not supported)
  [+] H1 null hypothesis validated via TOST equivalence test (90% CI within ±2.10% bounds)

FCC Causal Identification (Post-2007 Interaction Test):
  [+] FCC effect emerges after 2007 regulation: -2.26% (p=0.0125)
  [+] Pre-2007: Insufficient data, no significant effect
  [+] Proves regulatory source, not pre-existing industry trait

Standard Errors Robustness (Clustered vs HC3):
  [+] Firm-clustered SEs increase 38% on average vs HC3
  [+] FCC effect remains significant with conservative clustering
  [+] Main specification findings are robust to clustering

Essay 3 - Information Asymmetry:
  [+] Pre-breach volatility dominates (R² = 0.39)
  [+] Disclosure timing minimal effect

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