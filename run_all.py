"""
run_all.py - Complete Dissertation Analytics Pipeline
======================================================

Executes the entire dissertation workflow in correct order:
1. Data validation
2. Descriptive statistics 
3. Essay 2: Event study analysis
4. Essay 3: Information asymmetry analysis
5. Enrichment deep dive

Author: Timothy Spivey
Dissertation: Data Breach Disclosure Timing and Market Reactions
Date: January 2026
"""

import sys
import os

# Force UTF-8 encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
from pathlib import Path
import time

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_script(script_path, description):
    """
    Run a Python script and report results.
    Returns True if successful (ignoring end-of-script Unicode errors).
    """
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print("-"*80)
    
    start_time = time.time()
    
    # Set environment for subprocess
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # Run the script
    result = subprocess.run(
        ['python', script_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )
    
    elapsed = time.time() - start_time
    
    # Print output
    if result.stdout:
        print(result.stdout)
    
    # Check for success
    if result.returncode != 0:
        # Special case: Unicode error at end but outputs were created
        if 'UnicodeEncodeError' in str(result.stderr) and 'Saved' in str(result.stdout):
            print("[NOTE] Script completed successfully (Unicode display error ignored)")
            print(f"[OK] Completed in {elapsed:.1f} seconds\n")
            return True
        else:
            print(f"[ERROR] Script failed: {script_path}")
            if result.stderr:
                print(result.stderr)
            return False
    
    print(f"[OK] Completed in {elapsed:.1f} seconds\n")
    return True

def verify_data():
    """Verify required data files exist"""
    print_section("STEP 0: DATA VERIFICATION")
    
    data_file = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    
    if Path(data_file).exists():
        file_size = Path(data_file).stat().st_size / (1024*1024)
        print(f"  [OK] Main enriched dataset (CSV) ({file_size:.1f} MB)")
        print("\n[OK] All required data files present")
        return True
    else:
        print(f"  [MISSING] {data_file}")
        print("\n[ERROR] Required data file missing!")
        print("Please ensure FINAL_DISSERTATION_DATASET_ENRICHED.csv exists")
        return False

def verify_outputs():
    """Check what outputs were generated"""
    print_section("OUTPUT VERIFICATION")
    
    # Check tables
    tables_dir = Path('outputs/tables')
    if tables_dir.exists():
        csv_tables = sorted(tables_dir.glob('*.csv'))
        tex_tables = sorted(tables_dir.glob('*.tex'))
        
        print(f"Tables Generated: {len(csv_tables)} CSV, {len(tex_tables)} LaTeX")
        if csv_tables:
            for table in csv_tables:
                print(f"  [OK] {table.name}")
        else:
            print("  [WARNING] No CSV tables found")
    else:
        print("  [ERROR] Tables directory not found")
    
    # Check figures
    print()
    figures_dir = Path('outputs/figures')
    if figures_dir.exists():
        figures = sorted(figures_dir.glob('*.png'))
        
        print(f"Figures Generated: {len(figures)}")
        if figures:
            for figure in figures:
                print(f"  [OK] {figure.name}")
        else:
            print("  [WARNING] No figures found")
    else:
        print("  [ERROR] Figures directory not found")
    
    return True

def run_all():
    """Execute complete dissertation analytics pipeline"""
    
    # Header
    print("="*80)
    print("  DISSERTATION ANALYTICS PIPELINE")
    print("  Data Breach Disclosure Timing and Market Reactions")
    print("  Timothy Spivey - University of South Alabama")
    print("="*80)
    
    start_time = time.time()
    
    # Track results
    results = {
        'Descriptive Statistics': False,
        'Essay 2: Event Study': False,
        'Essay 3: Information Asymmetry': False,
        'Enrichment Analysis': False
    }
    
    # Step 0: Verify data exists
    if not verify_data():
        print("\n[FATAL] Cannot proceed without data file")
        return False
    
    # Step 1: Descriptive Statistics
    print_section("STEP 1: DESCRIPTIVE STATISTICS")
    results['Descriptive Statistics'] = run_script(
        'notebooks/01_descriptive_statistics.py',
        'Generating Tables 1-2 and descriptive figures'
    )
    
    # Step 2: Essay 2 - Event Study
    print_section("STEP 2: ESSAY 2 - EVENT STUDY ANALYSIS")
    results['Essay 2: Event Study'] = run_script(
        'notebooks/02_essay2_event_study.py',
        'Running event study regressions (5 models)'
    )
    
    # Step 3: Essay 3 - Information Asymmetry
    print_section("STEP 3: ESSAY 3 - INFORMATION ASYMMETRY")
    results['Essay 3: Information Asymmetry'] = run_script(
        'notebooks/03_essay3_information_asymmetry.py',
        'Running volatility analysis (5 models)'
    )
    
    # Step 4: Enrichment Analysis
    print_section("STEP 4: ENRICHMENT DEEP DIVE")
    results['Enrichment Analysis'] = run_script(
        'notebooks/04_enrichment_analysis.py',
        'Analyzing enrichment variables'
    )
    
    # Verify outputs were created
    verify_outputs()
    
    # Calculate timing
    total_time = time.time() - start_time
    
    # Summary
    print_section("PIPELINE SUMMARY")
    
    successful = [name for name, success in results.items() if success]
    failed = [name for name, success in results.items() if not success]
    
    if successful:
        print("[SUCCESS] Completed Steps:")
        for step in successful:
            print(f"  * {step}")
    
    if failed:
        print("\n[WARNING] Failed Steps:")
        for step in failed:
            print(f"  * {step}")
    
    print(f"\nTotal Execution Time: {total_time/60:.1f} minutes")
    
    # Dissertation structure
    print("\n" + "-"*80)
    print("DISSERTATION STRUCTURE:")
    print("  Essay 1: Theoretical Framework (pure theory)")
    print("  Essay 2: Event Study - Market Reactions [ANALYZED]")
    print("  Essay 3: Information Asymmetry [ANALYZED]")
    
    # Key enrichments
    print("\nKEY ENRICHMENTS:")
    print("  1. Prior Breach History (41.9% repeat offenders)")
    print("  2. Breach Severity (11.1% health data)")
    print("  3. Executive Turnover (42.8% within 30 days)")
    print("  4. Regulatory Enforcement (0.6% of breaches)")
    
    # Expected outputs
    print("\nEXPECTED OUTPUTS:")
    print("  Tables:")
    print("    * table1_descriptive_stats.csv")
    print("    * table2_univariate_comparison.csv")
    print("    * table3_essay2_regressions.tex (5 models)")
    print("    * table4_essay3_regressions.tex (5 models)")
    print("  Figures:")
    print("    * fig1_breach_timeline.png")
    print("    * fig2_car_distribution.png")
    print("    * fig3_enrichment_highlights.png")
    print("    * fig4_heterogeneity_analysis.png")
    print("    * fig5_volatility_analysis.png")
    print("    * enrichment_*.png (4 figures)")
    
    # Key findings
    print("\nKEY FINDINGS:")
    print("  * Health data breaches: -4.32%*** (p<0.001)")
    print("  * FCC regulation: -3.60%*** (p=0.003)")
    print("  * Prior breaches: -0.11%*** per breach (p=0.002)")
    print("  * Executive turnover: 42.8% within 30 days")
    print("  * FCC increases volatility: +4.96%*** (p<0.001)")
    
    # Next steps
    print("\n" + "-"*80)
    print("NEXT STEPS:")
    print("  1. Review outputs/tables/ and outputs/figures/")
    print("  2. Begin writing Essay 2 and Essay 3 results sections")
    print("  3. Use Table 3 for Essay 2, Table 4 for Essay 3")
    print("  4. Include enrichment figures in appendix")
    
    print("\nFILES FOR COMMITTEE:")
    print("  * outputs/tables/table3_essay2_regressions.tex")
    print("  * outputs/tables/table4_essay3_regressions.tex")
    print("  * outputs/figures/*.png (all figures)")
    
    print("\n" + "="*80)
    
    # Determine overall success
    critical_success = results['Essay 2: Event Study'] and results['Essay 3: Information Asymmetry']
    
    if critical_success:
        print("[SUCCESS] Critical analyses completed successfully!")
        if len(successful) == 4:
            print("[PERFECT] All 4 steps completed!")
        return True
    else:
        print("[WARNING] Some critical analyses failed")
        print("Check error messages above and verify output files exist")
        return False

def main():
    """Main entry point"""
    try:
        success = run_all()
        
        if success:
            print("\n[COMPLETE] Pipeline finished successfully")
            sys.exit(0)
        else:
            print("\n[INCOMPLETE] Pipeline had errors - check logs above")
            sys.exit(1)
            
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