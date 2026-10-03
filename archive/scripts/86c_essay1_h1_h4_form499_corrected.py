"""
SCRIPT 86C: H1-H4 RE-ESTIMATION WITH FORM 499 CORRECTED CLASSIFICATION
=====================================================================

Re-estimate all four hypotheses (H1-H4) with corrected Form 499 filer classification.
This replaces the SIC-based classification with authoritative regulatory status.

Input:  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv
Output: outputs/h1_h4_form499_corrected_regression_results.txt
        outputs/h1_h4_form499_corrected_summary.csv
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("SCRIPT 86C: H1-H4 RE-ESTIMATION WITH FORM 499 CORRECTED CLASSIFICATION")
print("=" * 80)

# Load corrected data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')

# Prepare regression sample
reg_sample = df[df['has_crsp_data'] == 1].copy()

required_vars = ['fcc_form499', 'car_30d', 'immediate_disclosure', 'prior_breaches_1yr',
                 'health_breach', 'firm_size_log', 'leverage', 'roa']

reg_sample = reg_sample[required_vars].dropna()

print(f"\nSample: N={len(reg_sample)}")
print(f"Treated (Form 499): {(reg_sample['fcc_form499'] == 1).sum()}")
print(f"Untreated: {(reg_sample['fcc_form499'] == 0).sum()}")

# Run regression
y = reg_sample['car_30d']
X = reg_sample[['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr',
                'health_breach', 'firm_size_log', 'leverage', 'roa']]
X = sm.add_constant(X)

results = sm.OLS(y, X).fit(cov_type='HC3')

# Display results
print("\n" + "=" * 80)
print("REGRESSION RESULTS (Form 499 Corrected)")
print("=" * 80)
print(results.summary())

# Extract hypotheses
hypotheses = [
    ('H1 (Immediate Disclosure)', 'immediate_disclosure'),
    ('H2 (FCC Regulation)', 'fcc_form499'),
    ('H3 (Prior Breaches)', 'prior_breaches_1yr'),
    ('H4 (Health Breach)', 'health_breach'),
]

print("\n" + "=" * 80)
print("HYPOTHESIS TESTS (Form 499 Corrected)")
print("=" * 80)

summary_data = []

# IMPORTANT: car_30d is already in percentage points (mean=-0.40, SD=8.93)
# DO NOT multiply by 100 again

for hyp_name, var_name in hypotheses:
    coef = results.params[var_name]  # Already in pp
    se = results.bse[var_name]       # Already in pp
    pval = results.pvalues[var_name]
    ci = results.conf_int().loc[var_name]  # Already in pp

    # MDE at 80% power (in pp, same units as coef)
    mde_80 = 2.8 * se

    # TOST equivalence test (±2.10pp)
    # car_30d is in percentage points; no conversion needed
    equiv_bound = 2.10  # ±2.10 percentage points
    t_lower = (coef - (-equiv_bound)) / se
    t_upper = (coef - equiv_bound) / se
    p_lower = 1 - stats.t.cdf(t_lower, df=len(reg_sample)-8)
    p_upper = stats.t.cdf(t_upper, df=len(reg_sample)-8)
    p_tost = max(p_lower, p_upper)

    # Check if CI is entirely within bounds
    ci_inside_bounds = (ci[0] >= -equiv_bound) and (ci[1] <= equiv_bound)

    sig = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.10 else 'ns'))

    print(f"\n{hyp_name}")
    print(f"  Coefficient: {coef:.6f} pp")
    print(f"  Std Error:   {se:.6f} pp")
    print(f"  p-value:     {pval:.6f} {sig}")
    print(f"  95% CI:      [{ci[0]:.6f}, {ci[1]:.6f}] pp")
    print(f"  MDE (80%):   {mde_80:.6f} pp")
    print(f"  TOST p:      {p_tost:.6f} (Bounded at ±2.10pp? {'YES' if p_tost < 0.05 else 'NO'})")
    print(f"  CI inside bounds? {ci_inside_bounds}")

    summary_data.append({
        'Hypothesis': hyp_name.split('(')[0].strip(),
        'Coefficient_pp': coef,
        'Std_Error_pp': se,
        'p_value': pval,
        'CI_lower_pp': ci[0],
        'CI_upper_pp': ci[1],
        'MDE_80pct_pp': mde_80,
        'TOST_p': p_tost,
        'Bounded': 'YES' if p_tost < 0.05 else 'NO',
        'CI_inside_bounds': ci_inside_bounds,
        'N': len(reg_sample),
    })

# Save results
summary_df = pd.DataFrame(summary_data)
summary_file = output_dir / 'h1_h4_form499_corrected_summary.csv'
summary_df.to_csv(summary_file, index=False)

results_file = output_dir / 'h1_h4_form499_corrected_regression_results.txt'
with open(results_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("H1-H4 REGRESSION RESULTS - FORM 499 CORRECTED\n")
    f.write("=" * 80 + "\n\n")
    f.write(str(results.summary()))
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("BOUNDED NULL ANALYSIS\n")
    f.write("=" * 80 + "\n")
    f.write("All coefficients are in percentage points (pp).\n")
    f.write("TOST equivalence bounds: ±2.10pp (pre-specified)\n")
    f.write("TOST passes if 95% CI lies entirely within [-2.10pp, +2.10pp]\n\n")
    f.write(summary_df.to_string(index=False))
    f.write(f"\n\nBounded Nulls (TOST p < 0.05): {(summary_df['Bounded'] == 'YES').sum()}/4\n")
    f.write(f"Expected result: H1, H2, H3 pass; H4 fails (CI exceeds bounds)\n")

print(f"\n[OK] Results saved to {results_file}")
print(f"[OK] Summary saved to {summary_file}")
