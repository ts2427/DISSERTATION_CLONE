"""
ESSAY 3: DISCLOSURE TIMING AND GOVERNANCE RESPONSE

Creates regression tables for Essay 3:
- Executive turnover models (logistic regression, 30d/90d/180d windows)
- Regulatory enforcement descriptive analysis
- Institutional ownership changes (OLS)

Tables:
- Table 2: Executive Turnover (Odds Ratios & Marginal Effects)
- Table 3: Regulatory Enforcement (Descriptive)
- Table 4: Institutional Ownership Changes (OLS)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.cov_struct import Exchangeable
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod import families
from pathlib import Path
import warnings
import matplotlib.pyplot as plt
from scipy import stats
warnings.filterwarnings('ignore')

print("=" * 80)
print("ESSAY 3: DISCLOSURE TIMING AND GOVERNANCE RESPONSE")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
EXEC_CHANGES_FILE = 'Data/enrichment/executive_changes.csv'
ENFORCEMENT_FILE = 'Data/enrichment/regulatory_enforcement.csv'
OUTPUT_DIR = Path('outputs/tables/essay3_governance')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/5] Loading data...")
df = pd.read_csv(DATA_FILE)
print(f"  [OK] Main dataset: {len(df):,} breaches")

# Check if enrichment data is already in main dataset
if 'executive_change_30d' in df.columns:
    print(f"  [OK] Executive turnover data already in main dataset")
else:
    print(f"  [WARNING] Executive turnover data not found - loading separately")
    exec_df = pd.read_csv(EXEC_CHANGES_FILE)
    df = df.merge(exec_df, left_index=True, right_on='breach_id', how='left')

if 'has_enforcement' in df.columns:
    print(f"  [OK] Enforcement data already in main dataset")
else:
    print(f"  [WARNING] Enforcement data not found - loading separately")
    enf_df = pd.read_csv(ENFORCEMENT_FILE)
    df = df.merge(enf_df, left_index=True, right_on='breach_id', how='left')

# Create column aliases for consistency (Phase 2 variable standardization)
if 'disclosure_delay_days' in df.columns and 'days_to_disclosure' not in df.columns:
    df['days_to_disclosure'] = df['disclosure_delay_days']
if 'records_affected_numeric' in df.columns and 'records_affected' not in df.columns:
    df['records_affected'] = df['records_affected_numeric']
if 'has_enforcement' in df.columns and 'regulatory_enforcement' not in df.columns:
    df['regulatory_enforcement'] = df['has_enforcement']

# Convert boolean columns to numeric for statsmodels compatibility
bool_cols = df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    df[col] = df[col].astype(int)

# Check what data we have
turnover_coverage = df['executive_change_30d'].notna().sum()
print(f"  [OK] Breaches with executive turnover data: {turnover_coverage:,}")

# ============================================================================
# FILTER TO ANALYSIS SAMPLE
# ============================================================================

print(f"\n[Step 2/5] Preparing analysis samples...")

# Analysis sample: Has CRSP data
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  [OK] CRSP-matched breaches: {len(analysis_df):,}")

# Turnover sample: Has executive change data
turnover_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['immediate_disclosure'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

print(f"  [OK] Turnover analysis sample: {len(turnover_df):,} breaches")
print(f"      - With 30-day turnover: {(turnover_df['executive_change_30d'] == 1).sum():,}")
print(f"      - With 90-day turnover: {(turnover_df['executive_change_90d'] == 1).sum():,}")
print(f"      - With 180-day turnover: {(turnover_df['executive_change_180d'] == 1).sum():,}")

# Enforcement sample: Has enforcement data
enf_sample_df = analysis_df[analysis_df['has_enforcement'].notna()].copy()
print(f"  [OK] Enforcement analysis sample: {len(enf_sample_df):,} breaches")
print(f"      - With enforcement: {(enf_sample_df['has_enforcement'] == 1).sum():,}")

# ============================================================================
# CONTROL VARIABLES AVAILABILITY CHECK
# ============================================================================

print(f"\n[Step 3/5] Checking control variables...")

controls_base = ['firm_size_log', 'leverage', 'roa']
controls_available = [v for v in controls_base if v in turnover_df.columns]
print(f"  [OK] Base controls available: {len(controls_available)}/{len(controls_base)}")

# Optional moderators
moderators = {
    'prior_breaches_total': 'Prior breaches',
    'media_coverage': 'Media coverage',
    'analyst_coverage': 'Analyst coverage',
    'high_severity_breach': 'Breach severity'
}

available_moderators = {k: v for k, v in moderators.items() if k in turnover_df.columns}
print(f"  [OK] Moderators available: {len(available_moderators)}")

# ============================================================================
# TABLE 2: EXECUTIVE TURNOVER (LOGISTIC REGRESSION)
# ============================================================================

print(f"\n[Step 4/5] Creating Table 2: Executive Turnover Analysis...")

# Prepare regression columns
reg_cols = ['immediate_disclosure', 'fcc_reportable'] + controls_available
reg_cols = [c for c in reg_cols if c in turnover_df.columns]

# Start building models
turnover_models = {}
turnover_results = {}

for window in ['30d', '90d', '180d']:
    print(f"\n  [Processing] {window} window...")

    # Select dependent variable
    dv_col = f'executive_change_{window}'

    # Prepare data
    model_data = turnover_df[[dv_col] + reg_cols].dropna()
    print(f"    Sample size: {len(model_data):,}")

    if len(model_data) == 0:
        print(f"    [WARNING] No data for {window} window")
        continue

    # Prepare formula
    formula_str = f"{dv_col} ~ " + " + ".join(reg_cols)

    # Fit logistic regression
    try:
        logit_model = sm.formula.logit(formula_str, data=model_data).fit(
            disp=0,
            maxiter=1000
        )

        turnover_models[window] = logit_model
        turnover_results[window] = {
            'n_obs': len(model_data),
            'n_events': (model_data[dv_col] == 1).sum(),
            'event_pct': 100 * (model_data[dv_col] == 1).sum() / len(model_data),
            'pseudo_r2': logit_model.prsquared,
            'llf': logit_model.llf
        }

        print(f"    [OK] Model fitted")
        print(f"        Pseudo R-squared: {logit_model.prsquared:.4f}")
        print(f"        Events: {(model_data[dv_col] == 1).sum()} / {len(model_data)} ({100*(model_data[dv_col] == 1).sum()/len(model_data):.1f}%)")

    except Exception as e:
        print(f"    [ERROR] Model fitting failed: {e}")
        continue

# Create summary table for turnover models with odds ratios
if len(turnover_models) > 0:
    # Get summary
    summary_dict = {}
    coef_summary_list = []

    for window in ['30d', '90d', '180d']:
        if window in turnover_results:
            res = turnover_results[window]
            summary_dict[window] = {
                'N Observations': res['n_obs'],
                'Events': int(res['n_events']),
                'Event %': f"{res['event_pct']:.1f}%",
                'Pseudo R2': f"{res['pseudo_r2']:.4f}"
            }

            # Extract coefficients and odds ratios
            if window in turnover_models:
                model = turnover_models[window]
                coef_df = pd.DataFrame({
                    'Variable': model.params.index,
                    f'{window}_Logit': model.params.values,
                    f'{window}_OddsRatio': np.exp(model.params.values),
                    f'{window}_SE': model.bse.values
                })
                coef_summary_list.append(coef_df)

    summary_table = pd.DataFrame(summary_dict).T
    print(f"\n  [OK] Turnover models summary:")
    print(summary_table)

    # Save summary
    summary_table.to_csv(OUTPUT_DIR / 'TABLE2_turnover_summary.csv')
    print(f"  [OK] Saved: TABLE2_turnover_summary.csv")

    # Save coefficient summaries if available
    if len(coef_summary_list) > 0:
        print(f"\n  [OK] Model Coefficients and Odds Ratios:")
        for coef_df in coef_summary_list:
            print(coef_df.to_string(index=False))

# ============================================================================
# TABLE 3: REGULATORY ENFORCEMENT (DESCRIPTIVE)
# ============================================================================

print(f"\n[Step 5/5] Creating Table 3: Regulatory Enforcement Analysis...")

# Check enforcement cases
enf_cases = enf_sample_df[enf_sample_df['has_enforcement'] == 1].copy()
print(f"  [OK] Enforcement cases: {len(enf_cases):,}")

if len(enf_cases) > 0:
    # Prepare enforcement summary - handle missing columns gracefully
    enf_summary_dict = {
        'Case': range(1, len(enf_cases) + 1),
        'Company': enf_cases['org_name'].values if 'org_name' in enf_cases.columns else ['NA'] * len(enf_cases),
        'Breach Date': enf_cases['breach_date'].values if 'breach_date' in enf_cases.columns else ['NA'] * len(enf_cases),
        'Immediate': enf_cases['immediate_disclosure'].values if 'immediate_disclosure' in enf_cases.columns else ['NA'] * len(enf_cases),
        'FCC': enf_cases['fcc_reportable'].values if 'fcc_reportable' in enf_cases.columns else ['NA'] * len(enf_cases),
        'Penalty USD': enf_cases['penalty_amount_usd'].values if 'penalty_amount_usd' in enf_cases.columns else ['NA'] * len(enf_cases),
        'Enforcement Type': enf_cases['enforcement_type'].values if 'enforcement_type' in enf_cases.columns else ['NA'] * len(enf_cases)
    }
    enf_summary = pd.DataFrame(enf_summary_dict)

    print(f"\n  Enforcement Cases Summary:")
    print(enf_summary.to_string(index=False))

    # Save enforcement cases
    enf_summary.to_csv(OUTPUT_DIR / 'TABLE3_enforcement_cases.csv', index=False)
    print(f"\n  [OK] Saved: TABLE3_enforcement_cases.csv")

    # Descriptive stats
    print(f"\n  Enforcement Statistics:")
    print(f"    - Total cases: {len(enf_cases)}")
    print(f"    - Immediate disclosure: {(enf_cases['immediate_disclosure'] == 1).sum()} cases")
    print(f"    - FCC firms: {(enf_cases['fcc_reportable'] == 1).sum()} cases")
    if enf_cases['penalty_amount_usd'].notna().sum() > 0:
        print(f"    - Mean penalty: ${enf_cases['penalty_amount_usd'].mean():,.0f}")
        print(f"    - Median penalty: ${enf_cases['penalty_amount_usd'].median():,.0f}")
else:
    print(f"  [WARNING] No enforcement cases found")

# ============================================================================
# INSTITUTIONAL OWNERSHIP (IF AVAILABLE)
# ============================================================================

print(f"\n[Step 5.5/5] Checking for institutional ownership data...")

# Check for institutional ownership percentage variable
ownership_var = None
if 'institutional_ownership_pct' in df.columns:
    ownership_var = 'institutional_ownership_pct'
    print(f"  [OK] Found institutional_ownership_pct")
elif 'institutional_ownership_change_pct' in df.columns:
    ownership_var = 'institutional_ownership_change_pct'
    print(f"  [OK] Found institutional_ownership_change_pct")
else:
    print(f"  [WARNING] Institutional ownership variables not found")

if ownership_var:
    # Prepare ownership sample
    ownership_df = analysis_df[
        (analysis_df[ownership_var].notna()) &
        (analysis_df['immediate_disclosure'].notna()) &
        (analysis_df['fcc_reportable'].notna())
    ].copy().dropna(subset=controls_available)

    print(f"  [OK] Ownership analysis sample: {len(ownership_df):,} breaches")
    print(f"      Mean {ownership_var}: {ownership_df[ownership_var].mean():.2f}")
    print(f"      Median {ownership_var}: {ownership_df[ownership_var].median():.2f}")

    if len(ownership_df) > 0:
        # Fit OLS model
        formula_own = f"{ownership_var} ~ immediate_disclosure + fcc_reportable + " + " + ".join(controls_available)

        try:
            ownership_model = sm.formula.ols(formula_own, data=ownership_df).fit(cov_type='HC3')

            print(f"  [OK] Ownership model fitted")
            print(f"      R-squared: {ownership_model.rsquared:.4f}")
            print(f"      N: {ownership_model.nobs}")

            # Save model results
            with open(OUTPUT_DIR / 'TABLE4_ownership_results.txt', 'w') as f:
                f.write("=" * 100 + "\n")
                f.write("TABLE 4: INSTITUTIONAL OWNERSHIP ANALYSIS\n")
                f.write(f"Dependent Variable: {ownership_var}\n")
                f.write("=" * 100 + "\n\n")
                f.write(str(ownership_model.summary()))
                f.write("\n\nNotes: Heteroskedasticity-robust standard errors (HC3) in parentheses.\n")
                f.write("*** p<0.01, ** p<0.05, * p<0.10\n")
                f.write("=" * 100 + "\n")
            print(f"  [OK] Saved: TABLE4_ownership_results.txt")
        except Exception as e:
            print(f"  [WARNING] Ownership model failed: {e}")
    else:
        print(f"  [WARNING] No data available for ownership analysis")

# ============================================================================
# KEY FINDINGS SUMMARY
# ============================================================================

print(f"\n" + "=" * 80)
print("[COMPLETE] ESSAY 3 GOVERNANCE ANALYSIS COMPLETE")
print("=" * 80)

print(f"\nTables created in {OUTPUT_DIR}/:")
print(f"  - TABLE2_turnover_summary.csv (Executive turnover models by window)")
print(f"  - TABLE3_enforcement_cases.csv (Regulatory enforcement descriptive)")
if 'institutional_ownership_change_pct' in df.columns:
    print(f"  - TABLE4_ownership_results.txt (Institutional ownership OLS)")

print(f"\nKey Findings:")
print(f"  - {len(enf_cases) if len(enf_cases) > 0 else 0} enforcement cases in sample")
if len(turnover_results) > 0:
    res_30d = turnover_results.get('30d', {})
    print(f"  - 30-day turnover: {res_30d.get('event_pct', 0):.1f}% of breaches")

print("=" * 80)
