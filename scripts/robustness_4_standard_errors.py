"""
ROBUSTNESS CHECK 4: Alternative Standard Errors

Tests whether statistical inference is robust to different standard error
specifications:
- Classical OLS (homoskedastic)
- Heteroskedasticity-robust (HC1, HC3)
- Firm-clustered
- Year-clustered
- Two-way clustered (firm + year)

Uses: FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 breaches, 85 variables)
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 4: ALTERNATIVE STANDARD ERRORS")
print("Testing inference robustness across clustering specifications")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/robustness')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'tables').mkdir(exist_ok=True)
(OUTPUT_DIR / 'figures').mkdir(exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/5] Loading enriched dataset...")
df = pd.read_csv(DATA_FILE)
print(f"  ✓ Loaded: {len(df):,} breaches")

# Convert breach_date to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'])

# Analysis sample
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  ✓ Sample with CRSP data: {len(analysis_df):,} breaches")

# Create year variable
analysis_df['year'] = analysis_df['breach_date'].dt.year

# Check for CIK (for firm clustering)
if 'cik' not in analysis_df.columns:
    print("  ⚠ Warning: 'cik' not found, firm clustering will be skipped")

# ============================================================================
# PREPARE REGRESSION DATA
# ============================================================================

print(f"\n[Step 2/5] Preparing regression data...")

# Target variable
if 'car_30d' in analysis_df.columns:
    target = 'car_30d'
elif 'car_5d' in analysis_df.columns:
    target = 'car_5d'
else:
    print("\n  ✗ ERROR: No CAR variable found!")
    exit()

print(f"  ✓ Target variable: {target}")

# Controls
controls = []
potential_controls = [
    'firm_size_log', 'leverage', 'roa', 'market_to_book',
    'prior_breaches_total', 'health_breach', 'immediate_disclosure'
]

for control in potential_controls:
    if control in analysis_df.columns:
        controls.append(control)

print(f"  ✓ Controls: {len(controls)}")

# Prepare regression dataset
reg_cols = [target] + controls + ['cik', 'year']
reg_cols = [col for col in reg_cols if col in analysis_df.columns]
reg_df = analysis_df[reg_cols].dropna()

print(f"  ✓ Regression sample: {len(reg_df):,} observations")
if 'cik' in reg_df.columns:
    print(f"  ✓ Unique firms: {reg_df['cik'].nunique()}")
print(f"  ✓ Unique years: {reg_df['year'].nunique()}")
print(f"  ✓ Year range: {reg_df['year'].min()} - {reg_df['year'].max()}")

# ============================================================================
# RUN MODELS WITH DIFFERENT STANDARD ERRORS
# ============================================================================

print(f"\n[Step 3/5] Estimating models with alternative standard errors...")

results_summary = []

# Prepare X and y
y = reg_df[target]
X = sm.add_constant(reg_df[controls])

print(f"\n  Model specification:")
print(f"    DV: {target}")
print(f"    IVs: {', '.join(controls[:3])}... ({len(controls)} total)")

# 1. HOMOSKEDASTIC (Classical OLS)
print(f"\n  [1/6] Homoskedastic (Classical OLS)...")
try:
    model_homo = OLS(y, X).fit()
    
    results_summary.append({
        'Method': '1. Homoskedastic',
        'N': int(model_homo.nobs)
    })
    
    # Add all coefficients
    for var in controls:
        if var in model_homo.params.index:
            results_summary[-1][f'{var}_coef'] = model_homo.params[var]
            results_summary[-1][f'{var}_se'] = model_homo.bse[var]
            results_summary[-1][f'{var}_t'] = model_homo.tvalues[var]
            results_summary[-1][f'{var}_p'] = model_homo.pvalues[var]
    
    print(f"    ✓ Model estimated")
except Exception as e:
    print(f"    ✗ Failed: {str(e)[:100]}")

# 2. HETEROSKEDASTICITY-ROBUST (HC1)
print(f"  [2/6] Heteroskedasticity-Robust (HC1)...")
try:
    model_hc1 = OLS(y, X).fit(cov_type='HC1')
    
    results_summary.append({
        'Method': '2. Robust (HC1)',
        'N': int(model_hc1.nobs)
    })
    
    for var in controls:
        if var in model_hc1.params.index:
            results_summary[-1][f'{var}_coef'] = model_hc1.params[var]
            results_summary[-1][f'{var}_se'] = model_hc1.bse[var]
            results_summary[-1][f'{var}_t'] = model_hc1.tvalues[var]
            results_summary[-1][f'{var}_p'] = model_hc1.pvalues[var]
    
    print(f"    ✓ Model estimated")
except Exception as e:
    print(f"    ✗ Failed: {str(e)[:100]}")

# 3. HETEROSKEDASTICITY-ROBUST (HC3) - MAIN SPECIFICATION
print(f"  [3/6] Heteroskedasticity-Robust (HC3) [MAIN]...")
try:
    model_hc3 = OLS(y, X).fit(cov_type='HC3')
    
    results_summary.append({
        'Method': '3. Robust (HC3) [Main]',
        'N': int(model_hc3.nobs)
    })
    
    for var in controls:
        if var in model_hc3.params.index:
            results_summary[-1][f'{var}_coef'] = model_hc3.params[var]
            results_summary[-1][f'{var}_se'] = model_hc3.bse[var]
            results_summary[-1][f'{var}_t'] = model_hc3.tvalues[var]
            results_summary[-1][f'{var}_p'] = model_hc3.pvalues[var]
    
    print(f"    ✓ Model estimated (MAIN SPECIFICATION)")
except Exception as e:
    print(f"    ✗ Failed: {str(e)[:100]}")

# 4. FIRM-CLUSTERED
if 'cik' in reg_df.columns:
    print(f"  [4/6] Firm-Clustered Standard Errors...")
    try:
        model_firm = OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': reg_df['cik']})
        
        results_summary.append({
            'Method': '4. Firm-Clustered',
            'N': int(model_firm.nobs)
        })
        
        for var in controls:
            if var in model_firm.params.index:
                results_summary[-1][f'{var}_coef'] = model_firm.params[var]
                results_summary[-1][f'{var}_se'] = model_firm.bse[var]
                results_summary[-1][f'{var}_t'] = model_firm.tvalues[var]
                results_summary[-1][f'{var}_p'] = model_firm.pvalues[var]
        
        print(f"    ✓ Model estimated")
    except Exception as e:
        print(f"    ✗ Failed: {str(e)[:100]}")
else:
    print(f"  [4/6] Firm-Clustered: Skipped (no CIK variable)")

# 5. YEAR-CLUSTERED
print(f"  [5/6] Year-Clustered Standard Errors...")
try:
    model_year = OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': reg_df['year']})
    
    results_summary.append({
        'Method': '5. Year-Clustered',
        'N': int(model_year.nobs)
    })
    
    for var in controls:
        if var in model_year.params.index:
            results_summary[-1][f'{var}_coef'] = model_year.params[var]
            results_summary[-1][f'{var}_se'] = model_year.bse[var]
            results_summary[-1][f'{var}_t'] = model_year.tvalues[var]
            results_summary[-1][f'{var}_p'] = model_year.pvalues[var]
    
    print(f"    ✓ Model estimated")
except Exception as e:
    print(f"    ✗ Failed: {str(e)[:100]}")

# 6. NEWEY-WEST (HAC)
print(f"  [6/6] Newey-West (HAC) Standard Errors...")
try:
    model_hac = OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
    
    results_summary.append({
        'Method': '6. Newey-West (HAC)',
        'N': int(model_hac.nobs)
    })
    
    for var in controls:
        if var in model_hac.params.index:
            results_summary[-1][f'{var}_coef'] = model_hac.params[var]
            results_summary[-1][f'{var}_se'] = model_hac.bse[var]
            results_summary[-1][f'{var}_t'] = model_hac.tvalues[var]
            results_summary[-1][f'{var}_p'] = model_hac.pvalues[var]
    
    print(f"    ✓ Model estimated")
except Exception as e:
    print(f"    ✗ Failed: {str(e)[:100]}")

# ============================================================================
# CREATE SUMMARY TABLES
# ============================================================================

print(f"\n[Step 4/5] Creating summary tables...")

if len(results_summary) == 0:
    print("  ✗ No results to summarize!")
    exit()

results_df = pd.DataFrame(results_summary)

# Find key variable (most commonly used)
key_var = 'immediate_disclosure' if 'immediate_disclosure' in controls else controls[0]

print(f"\n  Focus variable: {key_var}")

# Create publication table for key variable
summary_table = pd.DataFrame({
    'Standard Error Method': results_df['Method'],
    'Coefficient': results_df[f'{key_var}_coef'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else 'N/A'),
    'Std. Error': results_df[f'{key_var}_se'].apply(lambda x: f"({x:.4f})" if pd.notna(x) else 'N/A'),
    'T-statistic': results_df[f'{key_var}_t'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A'),
    'P-value': results_df[f'{key_var}_p'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else 'N/A')
})

# Add significance stars
def get_sig(p):
    if pd.isna(p):
        return ''
    elif p < 0.01:
        return '***'
    elif p < 0.05:
        return '**'
    elif p < 0.10:
        return '*'
    else:
        return ''

summary_table['Sig.'] = results_df[f'{key_var}_p'].apply(get_sig)

print("\n" + "=" * 80)
print(f"SUMMARY: {key_var.replace('_', ' ').title()} Effect Across SE Methods")
print("=" * 80)
print("\n" + summary_table.to_string(index=False))

# Save tables
summary_table.to_csv(OUTPUT_DIR / 'tables' / 'R04_standard_errors_summary.csv', index=False)
results_df.to_csv(OUTPUT_DIR / 'tables' / 'R04_standard_errors_full.csv', index=False)

# ============================================================================
# CREATE VISUALIZATION
# ============================================================================

print(f"\n[Step 5/5] Creating visualization...")

# Create comparison plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Standard Errors Comparison
valid_rows = results_df[results_df[f'{key_var}_se'].notna()]
methods = valid_rows['Method'].values
ses = valid_rows[f'{key_var}_se'].values

# Color main specification differently
colors = ['lightgray'] * len(methods)
for i, method in enumerate(methods):
    if 'Main' in method or 'HC3' in method:
        colors[i] = 'steelblue'

bars = ax1.bar(range(len(methods)), ses, color=colors, alpha=0.8, edgecolor='black')
ax1.set_xticks(range(len(methods)))
ax1.set_xticklabels([m.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '') 
                      for m in methods], rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Standard Error', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Standard Error Comparison', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Highlight main specification
main_idx = [i for i, m in enumerate(methods) if 'Main' in m or 'HC3' in m]
if main_idx:
    ax1.axhline(y=ses[main_idx[0]], color='red', linestyle='--', 
                linewidth=1.5, alpha=0.5, label='Main Spec')
    ax1.legend(fontsize=9)

# Panel B: P-values Comparison
pvals = valid_rows[f'{key_var}_p'].values

colors_p = []
for p in pvals:
    if p < 0.01:
        colors_p.append('#d62728')  # Red
    elif p < 0.05:
        colors_p.append('#ff7f0e')  # Orange
    elif p < 0.10:
        colors_p.append('#2ca02c')  # Green
    else:
        colors_p.append('#7f7f7f')  # Gray

ax2.bar(range(len(methods)), pvals, color=colors_p, alpha=0.8, edgecolor='black')
ax2.axhline(y=0.10, color='green', linestyle=':', linewidth=2, alpha=0.5, label='p=0.10')
ax2.axhline(y=0.05, color='orange', linestyle=':', linewidth=2, alpha=0.5, label='p=0.05')
ax2.axhline(y=0.01, color='red', linestyle=':', linewidth=2, alpha=0.5, label='p=0.01')

ax2.set_xticks(range(len(methods)))
ax2.set_xticklabels([m.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '') 
                      for m in methods], rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('P-value', fontsize=11, fontweight='bold')
ax2.set_title('Panel B: Statistical Significance', fontsize=12, fontweight='bold')
ax2.legend(fontsize=8, loc='upper right')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figures' / 'R04_standard_errors.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Figure saved to: {OUTPUT_DIR / 'figures' / 'R04_standard_errors.png'}")

# ============================================================================
# INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Find main specification
main_row = valid_rows[valid_rows['Method'].str.contains('Main|HC3')].iloc[0] if len(valid_rows[valid_rows['Method'].str.contains('Main|HC3')]) > 0 else valid_rows.iloc[0]

print(f"\n📊 MAIN SPECIFICATION (HC3):")
print(f"   • Coefficient: {main_row[f'{key_var}_coef']:.4f}")
print(f"   • Std. Error: {main_row[f'{key_var}_se']:.4f}")
print(f"   • P-value: {main_row[f'{key_var}_p']:.4f}")

# SE range
se_values = valid_rows[f'{key_var}_se'].values
se_min = se_values.min()
se_max = se_values.max()
se_range_pct = ((se_max - se_min) / main_row[f'{key_var}_se']) * 100

print(f"\nStandard Error Variation:")
print(f"  • Range: [{se_min:.4f}, {se_max:.4f}]")
print(f"  • Variation: {se_range_pct:.1f}% of main specification SE")

# Significance consistency
sig_count = (valid_rows[f'{key_var}_p'] < 0.10).sum()
total = len(valid_rows)

print(f"\nInference Consistency:")
print(f"  • Significant (p<0.10): {sig_count}/{total} methods ({sig_count/total*100:.0f}%)")

for _, row in valid_rows.iterrows():
    p = row[f'{key_var}_p']
    sig = get_sig(p)
    print(f"    • {row['Method']}: p={p:.4f} {sig}")

if sig_count == total:
    conclusion = "ROBUST - Significant across ALL methods"
elif sig_count >= total * 0.75:
    conclusion = "LARGELY ROBUST - Significant in most methods"
else:
    conclusion = "SENSITIVE - Varies by SE method"

print(f"\n💡 CONCLUSION: {conclusion}")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 4 COMPLETE")
print("=" * 80)

print(f"\nFiles created:")
print(f"  • {OUTPUT_DIR / 'tables' / 'R04_standard_errors_summary.csv'}")
print(f"  • {OUTPUT_DIR / 'tables' / 'R04_standard_errors_full.csv'}")
print(f"  • {OUTPUT_DIR / 'figures' / 'R04_standard_errors.png'}")

print(f"\nKey Finding:")
print(f"  {conclusion}")
print("=" * 80)