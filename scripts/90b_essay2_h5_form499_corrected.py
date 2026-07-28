"""
SCRIPT 90B: ESSAY 2 - H5 VOLATILITY RE-ESTIMATION WITH FORM 499 CORRECTED
===========================================================================

First real estimate of H5 (volatility changes) on corrected data
(deduplication + Form 499 entity matching).

Input:  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv
Output: outputs/h5_form499_corrected_regression_results.txt
        outputs/h5_form499_corrected_heterogeneity.csv
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("SCRIPT 90B: H5 VOLATILITY RE-ESTIMATION (FORM 499 CORRECTED)")
print("=" * 80)

# Load corrected data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')

# Prepare sample
reg_sample = df[df['has_crsp_data'] == 1].copy()

# IMPORTANT: Match established Essay 2 specification
# This includes return_volatility_pre (mean-reversion control)
# Omitting it produces R²=0.013; including it produces R²=0.42
required_vars = ['fcc_form499', 'volatility_change', 'return_volatility_pre',
                 'firm_size_log', 'leverage', 'roa']
reg_sample = reg_sample[required_vars].dropna()

# Create firm-size quartiles
reg_sample['size_quartile'] = pd.qcut(reg_sample['firm_size_log'], q=4,
                                      labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')

print(f"\nSample: N={len(reg_sample)}, Treated={reg_sample['fcc_form499'].sum()}")
print(f"Note: Including return_volatility_pre control (established Essay 2 spec)")

# Main effect
y = reg_sample['volatility_change']
X = reg_sample[['fcc_form499', 'return_volatility_pre', 'firm_size_log', 'leverage', 'roa']]
X = sm.add_constant(X)

results_main = sm.OLS(y, X).fit(cov_type='HC3')

fcc_coef = results_main.params['fcc_form499']
fcc_pval = results_main.pvalues['fcc_form499']

print(f"\n" + "=" * 80)
print("H5 MAIN EFFECT")
print("=" * 80)
print(f"FCC coefficient: {fcc_coef:.6f}, p={fcc_pval:.6f}")
print(results_main.summary())

# Heterogeneity (with return_volatility_pre control)
reg_sample_het = reg_sample.copy()
for q in ['Q1', 'Q2', 'Q3']:
    reg_sample_het[f'fcc_{q}'] = (reg_sample_het['fcc_form499'] *
                                 (reg_sample_het['size_quartile'] == q)).astype(int)

y_het = reg_sample_het['volatility_change']
X_het = reg_sample_het[['fcc_Q1', 'fcc_Q2', 'fcc_Q3', 'return_volatility_pre',
                        'firm_size_log', 'leverage', 'roa']]
X_het = sm.add_constant(X_het)

results_het = sm.OLS(y_het, X_het).fit(cov_type='HC3')

print(f"\n" + "=" * 80)
print("H5 HETEROGENEITY (Firm Size Quartiles, Q4 baseline)")
print("=" * 80)
print(results_het.summary())

# Extract heterogeneity results
het_data = []
for q in ['Q1', 'Q2', 'Q3']:
    col = f'fcc_{q}'
    coef = results_het.params[col]
    se = results_het.bse[col]
    pval = results_het.pvalues[col]
    sig = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.10 else 'ns'))
    print(f"{q}: {coef:.6f} (SE={se:.6f}, p={pval:.6f}) {sig}")
    het_data.append({'Quartile': q, 'Coefficient': coef, 'Std_Error': se, 'p_value': pval})

# Save results
het_df = pd.DataFrame(het_data)
het_file = output_dir / 'h5_form499_corrected_heterogeneity.csv'
het_df.to_csv(het_file, index=False)

results_file = output_dir / 'h5_form499_corrected_regression_results.txt'
with open(results_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("H5 VOLATILITY REGRESSION - FORM 499 CORRECTED\n")
    f.write("=" * 80 + "\n\n")
    f.write("MAIN EFFECT:\n")
    f.write(str(results_main.summary()))
    f.write(f"\n\nFCC coefficient: {fcc_coef:.6f}, p={fcc_pval:.6f}\n")
    f.write("\n" + "=" * 80 + "\n")
    f.write("HETEROGENEITY (Firm Size Quartiles):\n")
    f.write("=" * 80 + "\n")
    f.write(str(results_het.summary()))
    f.write("\n\n" + het_df.to_string(index=False))

print(f"\n[OK] Results saved to {results_file}")
print(f"[OK] Heterogeneity saved to {het_file}")
