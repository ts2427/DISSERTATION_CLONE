"""
Re-run H1-H4 regressions with consolidated dataset (larger sample with subsidiaries mapped)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

print("=" * 100)
print("H1-H4 REGRESSIONS WITH CONSOLIDATED SUBSIDIARY DATA")
print("=" * 100)

# Load consolidated dataset
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CONSOLIDATED_WITH_CAR.csv')

# Filter to records with valid CAR
df_sample = df[df['car_30d'].notna()].copy()
print(f"\nSample size: {len(df_sample)}")

# Define controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Drop rows with missing controls
df_sample = df_sample.dropna(subset=['car_30d'] + controls).copy()
print(f"After dropping missing controls: {len(df_sample)}")

# Convert to numeric arrays
y_data = df_sample['car_30d'].values.astype(np.float64)
X_data = df_sample[controls].values.astype(np.float64)
X_const = np.column_stack([np.ones(len(X_data)), X_data])

print(f"Final sample: {len(y_data)} observations")

# ============================================================================
# Run Regression
# ============================================================================
print("\n" + "=" * 100)
print("H1-H4 RESULTS (CONSOLIDATED DATASET WITH SUBSIDIARIES)")
print("=" * 100)

model = sm.OLS(y_data, X_const).fit(cov_type='HC3')

print(f"\nSample size: {len(y_data)}")
print(f"R-squared: {model.rsquared:.4f}")
print(f"Adj R-squared: {model.rsquared_adj:.4f}")
print(f"F-statistic: {model.fvalue:.4f}")
print(f"Prob (F-stat): {model.f_pvalue:.6f}")

print("\n" + "-" * 100)
print("COEFFICIENT TABLE")
print("-" * 100)

var_names = ['const'] + controls
results_data = []
for i, var in enumerate(var_names):
    results_data.append({
        'Variable': var,
        'Coef': model.params[i],
        'Std Err': model.bse[i],
        'p-value': model.pvalues[i]
    })

results_table = pd.DataFrame(results_data)
results_table['Sig'] = results_table['p-value'].apply(
    lambda p: '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else 'ns'
)

print(results_table.to_string(index=False))

# ============================================================================
# KEY FINDINGS
# ============================================================================
print("\n" + "=" * 100)
print("KEY FINDINGS (CONSOLIDATED DATASET)")
print("=" * 100)

idx_h1 = 1
idx_h2 = 2
idx_h3 = 3
idx_h4 = 4

h1_coef = model.params[idx_h1]
h1_pval = model.pvalues[idx_h1]
h1_sig = "***" if h1_pval < 0.01 else "**" if h1_pval < 0.05 else "*" if h1_pval < 0.10 else "ns"

h2_coef = model.params[idx_h2]
h2_pval = model.pvalues[idx_h2]
h2_sig = "***" if h2_pval < 0.01 else "**" if h2_pval < 0.05 else "*" if h2_pval < 0.10 else "ns"

h3_coef = model.params[idx_h3]
h3_pval = model.pvalues[idx_h3]
h3_sig = "***" if h3_pval < 0.01 else "**" if h3_pval < 0.05 else "*" if h3_pval < 0.10 else "ns"

h4_coef = model.params[idx_h4]
h4_pval = model.pvalues[idx_h4]
h4_sig = "***" if h4_pval < 0.01 else "**" if h4_pval < 0.05 else "*" if h4_pval < 0.10 else "ns"

print(f"""
H1 (Timing Effect): {h1_coef:.4f}% {h1_sig} (p={h1_pval:.4f})

H2 (FCC Regulation): {h2_coef:.4f}% {h2_sig} (p={h2_pval:.4f})

H3 (Prior Breaches): {h3_coef:.4f}% {h3_sig} (p={h3_pval:.4f})

H4 (Health Breach): {h4_coef:.4f}% {h4_sig} (p={h4_pval:.4f})

SAMPLE COMPARISON:
  Original corrected:  n=647 observations
  Consolidated:        n={len(y_data)} observations (+{len(y_data)-647} records)
  Improvement:         {(len(y_data)-647)/647*100:+.1f}%
""")

print("=" * 100)

# Save full regression output
output_path = Path("outputs/H1-H4_CONSOLIDATED_REGRESSION_RESULTS.txt")
with open(output_path, 'w') as f:
    f.write("=" * 100 + "\n")
    f.write("H1-H4 REGRESSION RESULTS (CONSOLIDATED DATASET WITH SUBSIDIARIES MAPPED)\n")
    f.write("=" * 100 + "\n\n")
    f.write(model.summary().as_text())
    f.write(f"\n\n{results_table.to_string(index=False)}\n")

print(f"\nFull output saved: {output_path}")
