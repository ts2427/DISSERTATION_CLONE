"""
SCRIPT 85: H2 RE-ESTIMATION WITH FORM 499 CLASSIFICATION
==========================================================

Re-estimate H2 hypothesis with Form 499 classification instead of SIC.

Input:  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv

Output: outputs/H2_FORM499_REGRESSION_RESULTS.txt
        outputs/h2_form499_regression_summary.csv

Specification:
  DV: car_30d (30-day cumulative abnormal return)
  IV: fcc_form499 (Form 499 classification)
  Controls: immediate_disclosure, prior_breaches_1yr, health_breach,
            firm_size_log, leverage, roa
  SE: HC3 robust
  Sample: has_crsp_data == 1

This is the primary H2 result. Accept whatever coefficient/p-value emerges.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("SCRIPT 85: H2 RE-ESTIMATION WITH FORM 499 CLASSIFICATION")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n1. LOADING DATA...")

data_file = Path('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv')
try:
    df = pd.read_csv(data_file)
    print(f"   Loaded: {len(df)} rows")
except FileNotFoundError:
    print(f"   ERROR: {data_file} not found")
    print("   Run Script 121C (merge) first")
    sys.exit(1)

# ============================================================================
# PREPARE REGRESSION SAMPLE
# ============================================================================
print("\n2. PREPARING REGRESSION SAMPLE...")

# H2 regression requires has_crsp_data
reg_sample = df[df['has_crsp_data'] == 1].copy()
print(f"   Sample with CRSP data: {len(reg_sample)} rows")

# Required variables
required_vars = ['fcc_form499', 'car_30d', 'immediate_disclosure', 'prior_breaches_1yr',
                 'health_breach', 'firm_size_log', 'leverage', 'roa']

missing_vars = [v for v in required_vars if v not in reg_sample.columns]
if missing_vars:
    print(f"   ERROR: Missing variables: {missing_vars}")
    sys.exit(1)

# Drop rows with missing values
reg_sample = reg_sample[required_vars].dropna()
print(f"   After dropping missing values: {len(reg_sample)} rows")

# Check treatment distribution
fcc_form499_treated = (reg_sample['fcc_form499'] == 1).sum()
print(f"\n   Treatment distribution:")
print(f"     Form 499 treated (fcc_form499=1): {fcc_form499_treated}")
print(f"     Form 499 untreated (fcc_form499=0): {(reg_sample['fcc_form499'] == 0).sum()}")

# Unique firms
treated_firms = df[df['fcc_form499'] == 1]['org_name'].nunique()
print(f"     Unique treated firms: {treated_firms}")

# ============================================================================
# REGRESSION: FORM 499 CLASSIFICATION
# ============================================================================
print("\n3. RUNNING H2 REGRESSION (FORM 499)...")

# Prepare X and y
y = reg_sample['car_30d']
X = reg_sample[['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr',
                'health_breach', 'firm_size_log', 'leverage', 'roa']]

# Add constant
X = sm.add_constant(X)

# Fit OLS with HC3 standard errors
model = sm.OLS(y, X)
results = model.fit(cov_type='HC3')

print(f"\n   Regression complete")
print(f"   R-squared: {results.rsquared:.4f}")
print(f"   N: {len(reg_sample)}")

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
print("\n4. H2 RESULTS (FORM 499 CLASSIFICATION)")
print("=" * 80)

# Extract key coefficient (fcc_form499)
fcc_coef = results.params['fcc_form499']
fcc_se = results.bse['fcc_form499']
fcc_tstat = results.tvalues['fcc_form499']
fcc_pval = results.pvalues['fcc_form499']
fcc_ci = results.conf_int().loc['fcc_form499']

print(f"\nFCC (Form 499) Coefficient:")
print(f"  Coefficient: {fcc_coef:.6f} ({100*fcc_coef:.4f}%)")
print(f"  Std Error: {fcc_se:.6f}")
print(f"  t-statistic: {fcc_tstat:.4f}")
print(f"  p-value: {fcc_pval:.6f}")
print(f"  95% CI: [{fcc_ci[0]:.6f}, {fcc_ci[1]:.6f}]")

if fcc_pval < 0.05:
    sig = "**" if fcc_pval < 0.01 else "*"
    print(f"  Significance: {sig} (p < 0.05)")
else:
    print(f"  Significance: ns (p >= 0.05)")

print(f"\nFull Regression Results:")
print(results.summary())

# ============================================================================
# COMPARISON TO SIC-BASED
# ============================================================================
print("\n5. COMPARISON TO SIC-BASED H2")
print("=" * 80)

print("""
SIC-BASED (fcc_reportable):
  Coefficient: -2.2131%
  p-value: 0.0174
  N: 647 (128 treated observations)

FORM 499-BASED (fcc_form499):
  Coefficient: {:.4f}%
  p-value: {:.6f}
  N: {} ({} treated observations)

Delta:
  Coefficient change: {:.4f} percentage points
  p-value change: {:.6f}
  Sample size change: {} observations
""".format(
    100*fcc_coef,
    fcc_pval,
    len(reg_sample),
    fcc_form499_treated,
    100*fcc_coef - (-2.2131),
    fcc_pval - 0.0174,
    len(reg_sample) - 647
))

print("\nPRE-SPECIFIED COMMITMENT:")
print("  Accept Form 499 result as final, regardless of comparison to SIC.")
print("  If Form 499 coefficient differs, that is the finding.")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n6. SAVING RESULTS...")

# Text summary
results_text = f"""
================================================================================
H2 REGRESSION RESULTS - FORM 499 CLASSIFICATION
================================================================================

{results.summary()}

================================================================================
KEY FINDINGS
================================================================================

FCC (Form 499) Treatment Effect:
  Coefficient: {fcc_coef:.6f} ({100*fcc_coef:.4f}%)
  Std Error: {fcc_se:.6f}
  t-statistic: {fcc_tstat:.4f}
  p-value: {fcc_pval:.6f}
  95% CI: [{fcc_ci[0]:.6f}, {fcc_ci[1]:.6f}]

Sample:
  N: {len(reg_sample)} observations
  Treated firms: {treated_firms}
  Treated observations: {fcc_form499_treated}
  Untreated observations: {(reg_sample['fcc_form499'] == 0).sum()}

================================================================================
COMPARISON TO SIC-BASED H2
================================================================================

SIC-BASED (previous):
  Coefficient: -2.2131% (p=0.0174)
  N: 647

FORM 499-BASED (current):
  Coefficient: {100*fcc_coef:.4f}% (p={fcc_pval:.6f})
  N: {len(reg_sample)}

DECISION:
  Form 499 classification defines treatment for H2.
  Accept this result and proceed with robustness checks.

================================================================================
NEXT STEP: Scripts 121D-F (robustness checks)
================================================================================
"""

results_file = output_dir / 'H2_FORM499_REGRESSION_RESULTS.txt'
with open(results_file, 'w') as f:
    f.write(results_text)
print(f"   Saved: {results_file}")

# CSV summary
summary_data = {
    'Hypothesis': ['H2 (Form 499)'],
    'Coefficient': [fcc_coef],
    'Percentage': [100*fcc_coef],
    'Std_Error': [fcc_se],
    't_statistic': [fcc_tstat],
    'p_value': [fcc_pval],
    'CI_lower': [fcc_ci[0]],
    'CI_upper': [fcc_ci[1]],
    'N': [len(reg_sample)],
    'Treated_Obs': [fcc_form499_treated],
    'R_squared': [results.rsquared],
    'Classification': ['Form 499']
}

summary_df = pd.DataFrame(summary_data)
summary_file = output_dir / 'h2_form499_regression_summary.csv'
summary_df.to_csv(summary_file, index=False)
print(f"   Saved: {summary_file}")

print("\n" + "=" * 80)
print("H2 RE-ESTIMATION COMPLETE")
print("=" * 80)
