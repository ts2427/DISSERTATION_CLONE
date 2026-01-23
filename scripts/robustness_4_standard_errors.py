import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 4: ALTERNATIVE STANDARD ERRORS")
print("Testing inference robustness with different clustering approaches")
print("=" * 80)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')

# Analysis sample
analysis_df = df[(df['has_crsp_data'] == True) & 
                 (df['firm_size_log'].notna())].copy()

# Convert booleans
bool_cols = ['fcc_reportable', 'immediate_disclosure', 'large_firm']
for col in bool_cols:
    if col in analysis_df.columns:
        analysis_df[col] = analysis_df[col].astype(int)

print(f"\n✓ Analysis sample: {len(analysis_df)} records")

# Create year variable
analysis_df['year'] = analysis_df['breach_date'].dt.year

import os
os.makedirs('outputs/robustness/tables', exist_ok=True)

# ============================================================
# PREPARE REGRESSION DATA
# ============================================================

print("\n" + "=" * 80)
print("PREPARING REGRESSION DATA")
print("=" * 80)

reg_df = analysis_df[['car_30d', 'immediate_disclosure', 'fcc_reportable',
                       'firm_size_log', 'leverage', 'roa', 'cik', 'year']].dropna()

# Create interactions
reg_df['fcc_x_immediate'] = reg_df['fcc_reportable'] * reg_df['immediate_disclosure']

print(f"Regression sample: n={len(reg_df)}")
print(f"Unique firms: {reg_df['cik'].nunique()}")
print(f"Unique years: {reg_df['year'].nunique()}")
print(f"Year range: {reg_df['year'].min()} - {reg_df['year'].max()}")

# ============================================================
# RUN MODELS WITH DIFFERENT STANDARD ERRORS
# ============================================================

results_summary = []

print("\n" + "=" * 80)
print("ESTIMATING MODELS WITH ALTERNATIVE STANDARD ERRORS")
print("=" * 80)

# Prepare X and y
y = reg_df['car_30d']
X = sm.add_constant(reg_df[['immediate_disclosure', 'fcc_reportable', 
                             'fcc_x_immediate', 'firm_size_log', 
                             'leverage', 'roa']])

# 1. HOMOSKEDASTIC (Classical OLS)
print("\n1. Homoskedastic (Classical OLS)")
print("-" * 40)
model_homo = OLS(y, X).fit()
print(f"   FCC Effect: {model_homo.params['fcc_reportable']:.4f}")
print(f"   Std. Error: {model_homo.bse['fcc_reportable']:.4f}")
print(f"   T-stat: {model_homo.tvalues['fcc_reportable']:.2f}")
print(f"   P-value: {model_homo.pvalues['fcc_reportable']:.4f}")

results_summary.append({
    'Method': 'Homoskedastic',
    'FCC_coef': model_homo.params['fcc_reportable'],
    'FCC_se': model_homo.bse['fcc_reportable'],
    'FCC_t': model_homo.tvalues['fcc_reportable'],
    'FCC_p': model_homo.pvalues['fcc_reportable'],
    'Immediate_coef': model_homo.params['immediate_disclosure'],
    'Immediate_se': model_homo.bse['immediate_disclosure'],
    'Interaction_coef': model_homo.params['fcc_x_immediate'],
    'Interaction_se': model_homo.bse['fcc_x_immediate']
})

# 2. HETEROSKEDASTICITY-ROBUST (HC1)
print("\n2. Heteroskedasticity-Robust (HC1)")
print("-" * 40)
model_hc1 = OLS(y, X).fit(cov_type='HC1')
print(f"   FCC Effect: {model_hc1.params['fcc_reportable']:.4f}")
print(f"   Std. Error: {model_hc1.bse['fcc_reportable']:.4f}")
print(f"   T-stat: {model_hc1.tvalues['fcc_reportable']:.2f}")
print(f"   P-value: {model_hc1.pvalues['fcc_reportable']:.4f}")

results_summary.append({
    'Method': 'Robust (HC1)',
    'FCC_coef': model_hc1.params['fcc_reportable'],
    'FCC_se': model_hc1.bse['fcc_reportable'],
    'FCC_t': model_hc1.tvalues['fcc_reportable'],
    'FCC_p': model_hc1.pvalues['fcc_reportable'],
    'Immediate_coef': model_hc1.params['immediate_disclosure'],
    'Immediate_se': model_hc1.bse['immediate_disclosure'],
    'Interaction_coef': model_hc1.params['fcc_x_immediate'],
    'Interaction_se': model_hc1.bse['fcc_x_immediate']
})

# 3. HETEROSKEDASTICITY-ROBUST (HC3) - MAIN SPECIFICATION
print("\n3. Heteroskedasticity-Robust (HC3) [MAIN]")
print("-" * 40)
model_hc3 = OLS(y, X).fit(cov_type='HC3')
print(f"   FCC Effect: {model_hc3.params['fcc_reportable']:.4f}")
print(f"   Std. Error: {model_hc3.bse['fcc_reportable']:.4f}")
print(f"   T-stat: {model_hc3.tvalues['fcc_reportable']:.2f}")
print(f"   P-value: {model_hc3.pvalues['fcc_reportable']:.4f}")

results_summary.append({
    'Method': 'Robust (HC3) [Main]',
    'FCC_coef': model_hc3.params['fcc_reportable'],
    'FCC_se': model_hc3.bse['fcc_reportable'],
    'FCC_t': model_hc3.tvalues['fcc_reportable'],
    'FCC_p': model_hc3.pvalues['fcc_reportable'],
    'Immediate_coef': model_hc3.params['immediate_disclosure'],
    'Immediate_se': model_hc3.bse['immediate_disclosure'],
    'Interaction_coef': model_hc3.params['fcc_x_immediate'],
    'Interaction_se': model_hc3.bse['fcc_x_immediate']
})

# 4. FIRM-CLUSTERED
print("\n4. Firm-Clustered Standard Errors")
print("-" * 40)
try:
    model_firm = OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': reg_df['cik']})
    print(f"   FCC Effect: {model_firm.params['fcc_reportable']:.4f}")
    print(f"   Std. Error: {model_firm.bse['fcc_reportable']:.4f}")
    print(f"   T-stat: {model_firm.tvalues['fcc_reportable']:.2f}")
    print(f"   P-value: {model_firm.pvalues['fcc_reportable']:.4f}")
    
    results_summary.append({
        'Method': 'Firm-Clustered',
        'FCC_coef': model_firm.params['fcc_reportable'],
        'FCC_se': model_firm.bse['fcc_reportable'],
        'FCC_t': model_firm.tvalues['fcc_reportable'],
        'FCC_p': model_firm.pvalues['fcc_reportable'],
        'Immediate_coef': model_firm.params['immediate_disclosure'],
        'Immediate_se': model_firm.bse['immediate_disclosure'],
        'Interaction_coef': model_firm.params['fcc_x_immediate'],
        'Interaction_se': model_firm.bse['fcc_x_immediate']
    })
except Exception as e:
    print(f"   ⚠ Firm clustering failed: {e}")

# 5. YEAR-CLUSTERED
print("\n5. Year-Clustered Standard Errors")
print("-" * 40)
try:
    model_year = OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': reg_df['year']})
    print(f"   FCC Effect: {model_year.params['fcc_reportable']:.4f}")
    print(f"   Std. Error: {model_year.bse['fcc_reportable']:.4f}")
    print(f"   T-stat: {model_year.tvalues['fcc_reportable']:.2f}")
    print(f"   P-value: {model_year.pvalues['fcc_reportable']:.4f}")
    
    results_summary.append({
        'Method': 'Year-Clustered',
        'FCC_coef': model_year.params['fcc_reportable'],
        'FCC_se': model_year.bse['fcc_reportable'],
        'FCC_t': model_year.tvalues['fcc_reportable'],
        'FCC_p': model_year.pvalues['fcc_reportable'],
        'Immediate_coef': model_year.params['immediate_disclosure'],
        'Immediate_se': model_year.bse['immediate_disclosure'],
        'Interaction_coef': model_year.params['fcc_x_immediate'],
        'Interaction_se': model_year.bse['fcc_x_immediate']
    })
except Exception as e:
    print(f"   ⚠ Year clustering failed: {e}")

# ============================================================
# CREATE SUMMARY TABLE
# ============================================================

results_df = pd.DataFrame(results_summary)

print("\n" + "=" * 80)
print("SUMMARY TABLE: FCC EFFECT WITH ALTERNATIVE STANDARD ERRORS")
print("=" * 80)

# Create formatted table
summary_table = pd.DataFrame({
    'Standard Error Method': results_df['Method'],
    'FCC Coefficient': results_df['FCC_coef'].apply(lambda x: f"{x:.4f}"),
    'Std. Error': results_df['FCC_se'].apply(lambda x: f"({x:.4f})"),
    'T-statistic': results_df['FCC_t'].apply(lambda x: f"{x:.2f}"),
    'P-value': results_df['FCC_p'].apply(lambda x: f"{x:.4f}"),
    'Sig.': results_df.apply(lambda row: 
        '***' if row['FCC_p'] < 0.01 else 
        '**' if row['FCC_p'] < 0.05 else 
        '*' if row['FCC_p'] < 0.10 else 
        '', axis=1)
})

print("\n" + summary_table.to_string(index=False))

# Save table
summary_table.to_csv('outputs/robustness/tables/TABLE_B4_standard_errors.csv', index=False)
results_df.to_csv('outputs/robustness/tables/TABLE_B4_detailed_results.csv', index=False)

# ============================================================
# COMPARISON TABLE (All Key Variables)
# ============================================================

print("\n" + "=" * 80)
print("DETAILED COMPARISON: ALL KEY VARIABLES")
print("=" * 80)

detailed_table = pd.DataFrame({
    'Variable': ['FCC Regulated', 'Immediate Disclosure', 'FCC × Immediate'],
    'Coefficient': [
        f"{results_df.iloc[2]['FCC_coef']:.4f}",
        f"{results_df.iloc[2]['Immediate_coef']:.4f}",
        f"{results_df.iloc[2]['Interaction_coef']:.4f}"
    ]
})

# Add columns for each SE method
for _, row in results_df.iterrows():
    method = row['Method']
    detailed_table[f'{method}\nSE'] = [
        f"({row['FCC_se']:.4f})",
        f"({row['Immediate_se']:.4f})",
        f"({row['Interaction_se']:.4f})"
    ]

print("\n" + detailed_table.to_string(index=False))

detailed_table.to_csv('outputs/robustness/tables/TABLE_B4_all_variables.csv', index=False)

# ============================================================
# VISUALIZATION
# ============================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATION")
print("=" * 80)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

# Plot standard errors by method
x_pos = np.arange(len(results_df))
ses = results_df['FCC_se'].values
coef = results_df['FCC_coef'].iloc[0]  # Same across all methods

# Color main specification differently
colors = ['#7f7f7f'] * len(results_df)
main_idx = results_df[results_df['Method'].str.contains('Main')].index[0]
colors[main_idx] = '#1f77b4'

ax.bar(x_pos, ses, color=colors, alpha=0.7, edgecolor='black')

# Highlight main specification
ax.axhline(y=ses[main_idx], color='red', linestyle='--', linewidth=2, 
           alpha=0.5, label=f'Main Specification SE = {ses[main_idx]:.4f}')

ax.set_xticks(x_pos)
ax.set_xticklabels(results_df['Method'].values, rotation=45, ha='right')
ax.set_ylabel('Standard Error', fontsize=12, fontweight='bold')
ax.set_title(f'FCC Effect Standard Errors Across Methods\n(Coefficient = {coef:.4f})', 
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/robustness/tables/FIGURE_B4_standard_errors.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure saved")

# ============================================================
# INTERPRETATION
# ============================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Compare SEs to main specification
main_se = results_df[results_df['Method'].str.contains('Main')].iloc[0]['FCC_se']
print(f"\n📊 MAIN SPECIFICATION (HC3):")
print(f"   Standard Error: {main_se:.4f}")

# Check how much SEs vary
se_range = results_df['FCC_se'].max() - results_df['FCC_se'].min()
se_pct_range = (se_range / main_se) * 100
print(f"\n📈 Standard Error Range: {se_pct_range:.1f}% of main SE")
print(f"   Min SE: {results_df['FCC_se'].min():.4f} ({results_df[results_df['FCC_se'] == results_df['FCC_se'].min()]['Method'].iloc[0]})")
print(f"   Max SE: {results_df['FCC_se'].max():.4f} ({results_df[results_df['FCC_se'] == results_df['FCC_se'].max()]['Method'].iloc[0]})")

# Check inference consistency
significant_all = results_df[results_df['FCC_p'] < 0.10]
print(f"\n✓ FCC effect significant (p<0.10) in {len(significant_all)}/{len(results_df)} specifications")

for _, row in results_df.iterrows():
    sig = '***' if row['FCC_p'] < 0.01 else '**' if row['FCC_p'] < 0.05 else '*' if row['FCC_p'] < 0.10 else ''
    print(f"  - {row['Method']}: SE={row['FCC_se']:.4f}, p={row['FCC_p']:.4f} {sig}")

if len(significant_all) == len(results_df):
    print(f"\n💡 CONCLUSION: Inference is ROBUST across all SE methods")
    print(f"   FCC effect remains significant regardless of clustering approach")
elif len(significant_all) >= len(results_df) * 0.75:
    print(f"\n💡 CONCLUSION: Inference is LARGELY ROBUST")
    print(f"   Significant in {len(significant_all)}/{len(results_df)} specifications")
else:
    print(f"\n⚠ CONCLUSION: Inference shows SENSITIVITY to SE method")
    print(f"   Only significant in {len(significant_all)}/{len(results_df)} specifications")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 4 COMPLETE")
print("=" * 80)
print("\nOutput saved to:")
print("  - outputs/robustness/tables/TABLE_B4_standard_errors.csv")
print("  - outputs/robustness/tables/TABLE_B4_all_variables.csv")
print("  - outputs/robustness/tables/FIGURE_B4_standard_errors.png")