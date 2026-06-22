"""
CAUSAL IDENTIFICATION METHOD CONFIGURATION
===========================================

Switch between traditional methods (DiD + Parallel Trends) and
Firm-by-Firm Synthetic Control Method (SCM).

IMPORTANT: Change only the USE_SCM variable below.
Everything else will adjust automatically.
"""

# ============================================================================
# MAIN CONFIGURATION - CHANGE THIS TO SWITCH METHODS
# ============================================================================

# False = Use traditional methods (DiD + Parallel Trends + Industry FE + Size Sensitivity)
# True  = Use Firm-by-Firm Synthetic Control Method (SCM with permutation tests)
USE_SCM = True

# ============================================================================
# AUTOMATIC CONFIGURATION (Do not edit below)
# ============================================================================

import os
from pathlib import Path

if USE_SCM:
    # ========= FIRM-BY-FIRM SCM CONFIGURATION =========

    METHOD_NAME = "Firm-by-Firm Synthetic Control Method (SCM)"
    METHOD_SHORT = "SCM"

    # Primary output files
    PRIMARY_CAUSAL_ID_TABLE = Path("outputs/scm_firm_by_firm/scm_firm_summary_results.csv")
    PRIMARY_CAUSAL_ID_FIGURE = Path("outputs/scm_firm_by_firm/scm_aggregate_effect.png")
    HETEROGENEITY_TABLE = Path("outputs/scm_firm_by_firm/scm_firm_summary_results.csv")
    RESULTS_SUMMARY = Path("outputs/scm_firm_by_firm/SCM_RESULTS_SUMMARY.txt")

    # Additional outputs
    YEAR_BY_YEAR_RESULTS = None
    HETEROGENEITY_FIGURE = Path("outputs/scm_firm_by_firm/scm_firm_level_effects.png")
    INFERENCE_FIGURE = Path("outputs/scm_firm_by_firm/scm_permutation_distribution.png")

    # Scripts
    MAIN_ANALYSIS_SCRIPT = "scripts/firm_by_firm_scm_analysis.py"
    DATA_PREP_SCRIPT = "scripts/scm_data_preparation.py"

    # Description for methods section
    METHODS_DESCRIPTION = """
    Firm-by-Firm Synthetic Control Method

    We employ firm-by-firm synthetic control method to address the n=1 limitation of
    sector-level comparisons. For each FCC-regulated firm, we construct a synthetic
    control as a weighted combination of non-FCC firms matched on pre-2007 characteristics
    (log assets, leverage, ROA, breach size). Individual treatment effects are aggregated
    across firms and tested using permutation-based inference (10,000 iterations), yielding
    n=200 independent treatment units with valid statistical inference.
    """

    # Description for results section
    RESULTS_DESCRIPTION = """
    Firm-by-firm SCM analysis across {n_firms} FCC firms yields a mean treatment effect of
    {effect_estimate}% (95% CI: [{ci_lower}%, {ci_upper}%], permutation p={p_value}).
    This effect is robust to specification, with individual firm effects ranging from
    {min_effect}% to {max_effect}%. The permutation test confirms that the observed
    mean effect is significantly different from zero.
    """

else:
    # ========= TRADITIONAL METHODS CONFIGURATION =========

    METHOD_NAME = "Difference-in-Differences with Parallel Trends Validation"
    METHOD_SHORT = "DiD"

    # Primary output files
    PRIMARY_CAUSAL_ID_TABLE = Path("outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt")
    PRIMARY_CAUSAL_ID_FIGURE = Path("outputs/figures/FIGURE_PARALLEL_TRENDS.png")
    HETEROGENEITY_TABLE = Path("outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt")
    RESULTS_SUMMARY = Path("outputs/tables/essay2/FCC_Causal_ID_Summary.txt")

    # Additional outputs
    YEAR_BY_YEAR_RESULTS = None
    HETEROGENEITY_FIGURE = None
    INFERENCE_FIGURE = None

    # Scripts
    MAIN_ANALYSIS_SCRIPT = "scripts/83_fcc_causal_identification.py"
    DATA_PREP_SCRIPT = None

    # Description for methods section
    METHODS_DESCRIPTION = """
    Difference-in-Differences with Parallel Trends Validation

    We employ difference-in-differences design with FCC regulation (2007) as the natural
    experiment. FCC-regulated firms are compared to non-FCC firms before and after the
    regulation took effect. We validate causal identification through: (1) parallel trends
    visualization confirming pre-treatment trends move together; (2) industry fixed effects
    controlling for sector-specific confounds; (3) size sensitivity analysis testing whether
    effects persist across firm size quartiles.
    """

    # Description for results section
    RESULTS_DESCRIPTION = """
    FCC regulation is associated with a {effect_estimate}% change in {outcome}
    (p={p_value}). This effect persists after controlling for industry-specific trends
    (industry FE) and shows consistent patterns across firm sizes, supporting a causal
    interpretation based on the natural experiment structure.
    """


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_causal_id_method():
    """Return active causal identification method name"""
    return METHOD_NAME

def get_causal_id_method_short():
    """Return short name for causal identification method"""
    return METHOD_SHORT

def is_using_scm():
    """Return True if using SCM, False if using traditional methods"""
    return USE_SCM

def validate_outputs_exist():
    """Check that required output files exist for the active method"""
    required_files = [
        PRIMARY_CAUSAL_ID_TABLE,
        PRIMARY_CAUSAL_ID_FIGURE,
        HETEROGENEITY_TABLE,
        RESULTS_SUMMARY
    ]

    missing = []
    for filepath in required_files:
        if filepath is not None and not filepath.exists():
            missing.append(str(filepath))

    return missing

def get_method_info():
    """Return dictionary with all method configuration"""
    return {
        'method': METHOD_NAME,
        'short': METHOD_SHORT,
        'is_scm': USE_SCM,
        'main_script': MAIN_ANALYSIS_SCRIPT,
        'primary_table': str(PRIMARY_CAUSAL_ID_TABLE),
        'primary_figure': str(PRIMARY_CAUSAL_ID_FIGURE),
        'heterogeneity_table': str(HETEROGENEITY_TABLE),
        'results_summary': str(RESULTS_SUMMARY),
    }


# ============================================================================
# PRINT STATUS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CAUSAL IDENTIFICATION METHOD CONFIGURATION")
    print("="*80)

    print(f"\nActive Method: {METHOD_NAME}")
    print(f"Short Name: {METHOD_SHORT}")

    if USE_SCM:
        print("\n[SCM METHOD]")
        print("  Main Script: scripts/firm_by_firm_scm_analysis.py")
        print(f"  Primary Table: {PRIMARY_CAUSAL_ID_TABLE}")
        print(f"  Primary Figure: {PRIMARY_CAUSAL_ID_FIGURE}")
    else:
        print("\n[TRADITIONAL METHOD (DiD + Parallel Trends)]")
        print("  Main Script: scripts/83_fcc_causal_identification.py")
        print(f"  Primary Table: {PRIMARY_CAUSAL_ID_TABLE}")
        print(f"  Primary Figure: {PRIMARY_CAUSAL_ID_FIGURE}")

    # Check if outputs exist
    missing = validate_outputs_exist()
    if missing:
        print(f"\n[WARNING] Missing output files:")
        for f in missing:
            print(f"  - {f}")
        print("\nRun the main analysis script to generate these files.")
    else:
        print("\n[OK] All expected output files found")

    print("\n" + "="*80)
