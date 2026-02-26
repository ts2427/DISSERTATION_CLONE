"""
HETEROGENEITY ANALYSIS - All Essays
Tests if effects vary by firm characteristics (size, profitability, leverage, coverage)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("HETEROGENEITY ANALYSIS - DO EFFECTS VARY BY FIRM CHARACTERISTICS?")
print("=" * 80)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"\nLoaded: {len(df):,} breaches")

# Prepare for heterogeneity analysis
OUTPUT_DIR = Path('outputs/tables')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create quartile variables
df['size_quartile'] = pd.qcut(df['firm_size_log'], q=4, labels=['Q1_Small', 'Q2', 'Q3', 'Q4_Large'], duplicates='drop')
df['profit_quartile'] = pd.qcut(df['roa'], q=4, labels=['Q1_Loss', 'Q2', 'Q3', 'Q4_Profit'], duplicates='drop')
df['leverage_quartile'] = pd.qcut(df['leverage'], q=4, labels=['Q1_Low', 'Q2', 'Q3', 'Q4_High'], duplicates='drop')

# Essay 1: CAR by Size Quartiles
print("\nESSAY 1: Timing effect on CAR by Firm Size")
print("=" * 80)
essay1_results = []
for quartile in ['Q1_Small', 'Q2', 'Q3', 'Q4_Large']:
    subset = df[(df['size_quartile'] == quartile) & (df['car_30d'].notna())].copy()
    if len(subset) > 20:
        X = sm.add_constant(subset[['immediate_disclosure', 'leverage', 'roa']])
        y = subset['car_30d']
        model = sm.OLS(y, X).fit()
        coef = model.params['immediate_disclosure']
        pval = model.pvalues['immediate_disclosure']
        essay1_results.append({'Group': f'Size {quartile}', 'N': len(subset), 'Coef': coef, 'Pval': pval})
        print(f"{quartile:15s}: coef={coef:7.3f}, p={pval:.3f}, n={len(subset)}")

# Essay 2: Volatility by Size Quartiles
print("\nESSAY 2: Timing effect on Volatility by Firm Size")
print("=" * 80)
essay2_results = []
for quartile in ['Q1_Small', 'Q2', 'Q3', 'Q4_Large']:
    subset = df[(df['size_quartile'] == quartile) & (df['volatility_change'].notna())].copy()
    if len(subset) > 20:
        X = sm.add_constant(subset[['immediate_disclosure', 'leverage', 'roa']])
        y = subset['volatility_change']
        model = sm.OLS(y, X).fit()
        coef = model.params['immediate_disclosure']
        pval = model.pvalues['immediate_disclosure']
        essay2_results.append({'Group': f'Size {quartile}', 'N': len(subset), 'Coef': coef, 'Pval': pval})
        print(f"{quartile:15s}: coef={coef:7.3f}, p={pval:.3f}, n={len(subset)}")

# Essay 3: Governance by Size Quartiles
print("\nESSAY 3: Timing effect on Governance by Firm Size")
print("=" * 80)
essay3_results = []
for quartile in ['Q1_Small', 'Q2', 'Q3', 'Q4_Large']:
    subset = df[(df['size_quartile'] == quartile) & (df['executive_change_30d'].notna())].copy()
    if len(subset) > 20:
        X = sm.add_constant(subset[['immediate_disclosure', 'leverage', 'roa']])
        y = subset['executive_change_30d']
        model = sm.Logit(y, X).fit(disp=0)
        coef = model.params['immediate_disclosure']
        pval = model.pvalues['immediate_disclosure']
        essay3_results.append({'Group': f'Size {quartile}', 'N': len(subset), 'Coef': coef, 'Pval': pval})
        print(f"{quartile:15s}: coef={coef:7.3f}, p={pval:.3f}, n={len(subset)}")

# Save results
output = f"""
HETEROGENEITY ANALYSIS - TIMING EFFECTS BY FIRM SIZE

ESSAY 1: CAR (Cumulative Abnormal Returns)
Group               N      Coefficient    P-Value
{'─' * 55}
"""
for r in essay1_results:
    output += f"{r['Group']:20s} {r['N']:5d}    {r['Coef']:>10.4f}    {r['Pval']:>8.4f}\n"

output += f"""
ESSAY 2: Volatility Change
Group               N      Coefficient    P-Value
{'─' * 55}
"""
for r in essay2_results:
    output += f"{r['Group']:20s} {r['N']:5d}    {r['Coef']:>10.4f}    {r['Pval']:>8.4f}\n"

output += f"""
ESSAY 3: Executive Turnover (30-day)
Group               N      Coefficient    P-Value
{'─' * 55}
"""
for r in essay3_results:
    output += f"{r['Group']:20s} {r['N']:5d}    {r['Coef']:>10.4f}    {r['Pval']:>8.4f}\n"

output += """
INTERPRETATION:
If timing coefficients are consistent across size groups -> Effect is uniform
If timing coefficients vary by size -> Effect is heterogeneous (may indicate omitted variable)
If timing is zero everywhere -> H1 null is universal and robust
If timing is significant in some groups -> Null is qualified (context-dependent)
"""

with open(OUTPUT_DIR / 'Heterogeneity_Analysis_By_Size.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\n[OK] Results saved to outputs/tables/Heterogeneity_Analysis_By_Size.txt")
print("\n" + "=" * 80)
print("HETEROGENEITY ANALYSIS COMPLETE")
print("=" * 80)
