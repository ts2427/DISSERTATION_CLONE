import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 3: SAMPLE RESTRICTIONS")
print("Testing FCC effect across different sample compositions")
print("=" * 80)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')

# Base analysis sample
base_df = df[(df['has_crsp_data'] == True) & 
             (df['firm_size_log'].notna())].copy()

# Convert booleans
bool_cols = ['fcc_reportable', 'immediate_disclosure', 'large_firm']
for col in bool_cols:
    if col in base_df.columns:
        base_df[col] = base_df[col].astype(int)

print(f"\n✓ Full sample: {len(base_df)} records")

import os
os.makedirs('outputs/robustness/tables', exist_ok=True)

# ============================================================
# DEFINE SAMPLE RESTRICTIONS
# ============================================================

print("\n" + "=" * 80)
print("DEFINING SAMPLE RESTRICTIONS")
print("=" * 80)

sample_restrictions = {}

# 1. FULL SAMPLE (Baseline)
sample_restrictions['Full Sample'] = base_df.copy()
print(f"\n1. Full Sample: {len(sample_restrictions['Full Sample'])} observations")

# 2. EXCLUDE FINANCIAL CRISIS (2008-2009)
crisis_df = base_df[~base_df['breach_date'].dt.year.isin([2008, 2009])].copy()
sample_restrictions['Exclude Crisis (2008-2009)'] = crisis_df
print(f"2. Exclude Crisis: {len(crisis_df)} observations")
print(f"   Dropped: {len(base_df) - len(crisis_df)} crisis-year observations")

# 3. EXCLUDE COVID PERIOD (2020-2021)
covid_df = base_df[~base_df['breach_date'].dt.year.isin([2020, 2021])].copy()
sample_restrictions['Exclude COVID (2020-2021)'] = covid_df
print(f"3. Exclude COVID: {len(covid_df)} observations")
print(f"   Dropped: {len(base_df) - len(covid_df)} COVID-year observations")

# 4. EXCLUDE SMALLEST 25% OF FIRMS
size_q25 = base_df['firm_size_log'].quantile(0.25)
no_small_df = base_df[base_df['firm_size_log'] > size_q25].copy()
sample_restrictions['Exclude Smallest Quartile'] = no_small_df
print(f"4. Exclude Smallest Quartile: {len(no_small_df)} observations")
print(f"   Size threshold (log): {size_q25:.2f}")
print(f"   Dropped: {len(base_df) - len(no_small_df)} small firms")

# 5. EXCLUDE LARGEST 10% OF FIRMS
size_p90 = base_df['firm_size_log'].quantile(0.90)
no_large_df = base_df[base_df['firm_size_log'] <= size_p90].copy()
sample_restrictions['Exclude Largest Decile'] = no_large_df
print(f"5. Exclude Largest Decile: {len(no_large_df)} observations")
print(f"   Size threshold (log): {size_p90:.2f}")
print(f"   Dropped: {len(base_df) - len(no_large_df)} large firms")

# 6. POST-2015 ONLY (Modern cybersecurity era)
post2015_df = base_df[base_df['breach_date'].dt.year >= 2015].copy()
sample_restrictions['Post-2015 Only'] = post2015_df
print(f"6. Post-2015 Only: {len(post2015_df)} observations")
print(f"   Dropped: {len(base_df) - len(post2015_df)} pre-2015 observations")

# 7. WINSORIZE EXTREME RETURNS (1% tails)
winsor_df = base_df.copy()
lower = winsor_df['car_30d'].quantile(0.01)
upper = winsor_df['car_30d'].quantile(0.99)
winsor_df['car_30d'] = winsor_df['car_30d'].clip(lower=lower, upper=upper)
sample_restrictions['Winsorized Returns (1%)'] = winsor_df
print(f"7. Winsorized Returns: {len(winsor_df)} observations")
print(f"   Lower bound: {lower:.2f}%, Upper bound: {upper:.2f}%")

# ============================================================
# RUN REGRESSIONS FOR EACH SAMPLE
# ============================================================

results_summary = []

for sample_name, sample_df in sample_restrictions.items():
    print(f"\n{'='*80}")
    print(f"SAMPLE: {sample_name}")
    print(f"{'='*80}")
    
    # Prepare regression data
    reg_df = sample_df[['car_30d', 'immediate_disclosure', 'fcc_reportable',
                        'firm_size_log', 'leverage', 'roa']].dropna()
    
    print(f"Sample size: n={len(reg_df)}")
    
    if len(reg_df) < 50:
        print(f"⚠ Sample too small, skipping")
        continue
    
    # Create interactions
    reg_df['fcc_x_immediate'] = reg_df['fcc_reportable'] * reg_df['immediate_disclosure']
    
    # Full model
    y = reg_df['car_30d']
    X = sm.add_constant(reg_df[['immediate_disclosure', 'fcc_reportable', 
                                 'fcc_x_immediate', 'firm_size_log', 
                                 'leverage', 'roa']])
    
    model = sm.OLS(y, X).fit(cov_type='HC3')
    
    # Extract key results
    results_summary.append({
        'Sample': sample_name,
        'N': int(model.nobs),
        'FCC_coef': model.params['fcc_reportable'],
        'FCC_se': model.bse['fcc_reportable'],
        'FCC_t': model.tvalues['fcc_reportable'],
        'FCC_p': model.pvalues['fcc_reportable'],
        'Immediate_coef': model.params['immediate_disclosure'],
        'Immediate_p': model.pvalues['immediate_disclosure'],
        'Interaction_coef': model.params['fcc_x_immediate'],
        'Interaction_p': model.pvalues['fcc_x_immediate'],
        'R_squared': model.rsquared,
        'Adj_R_squared': model.rsquared_adj
    })
    
    # Print key results
    print(f"\nKey Results:")
    print(f"  FCC Effect: {model.params['fcc_reportable']:.4f} (t={model.tvalues['fcc_reportable']:.2f}, p={model.pvalues['fcc_reportable']:.4f})")
    print(f"  Immediate Disclosure: {model.params['immediate_disclosure']:.4f} (p={model.pvalues['immediate_disclosure']:.4f})")
    print(f"  FCC × Immediate: {model.params['fcc_x_immediate']:.4f} (p={model.pvalues['fcc_x_immediate']:.4f})")
    print(f"  R²: {model.rsquared:.4f}")
    
    # Significance
    if model.pvalues['fcc_reportable'] < 0.01:
        sig = '***'
    elif model.pvalues['fcc_reportable'] < 0.05:
        sig = '**'
    elif model.pvalues['fcc_reportable'] < 0.10:
        sig = '*'
    else:
        sig = ''
    
    print(f"  Significance: {sig if sig else 'Not significant'}")

# ============================================================
# CREATE SUMMARY TABLE
# ============================================================

results_df = pd.DataFrame(results_summary)

print("\n" + "=" * 80)
print("SUMMARY TABLE: FCC EFFECT ACROSS SAMPLE RESTRICTIONS")
print("=" * 80)

# Create formatted table
summary_table = pd.DataFrame({
    'Sample Restriction': results_df['Sample'],
    'N': results_df['N'],
    'FCC Coefficient': results_df['FCC_coef'].apply(lambda x: f"{x:.4f}"),
    'Std. Error': results_df['FCC_se'].apply(lambda x: f"({x:.4f})"),
    'T-statistic': results_df['FCC_t'].apply(lambda x: f"{x:.2f}"),
    'P-value': results_df['FCC_p'].apply(lambda x: f"{x:.4f}"),
    'Sig.': results_df.apply(lambda row: 
        '***' if row['FCC_p'] < 0.01 else 
        '**' if row['FCC_p'] < 0.05 else 
        '*' if row['FCC_p'] < 0.10 else 
        '', axis=1),
    'R²': results_df['R_squared'].apply(lambda x: f"{x:.4f}")
})

print("\n" + summary_table.to_string(index=False))

# Save table
summary_table.to_csv('outputs/robustness/tables/TABLE_B3_sample_restrictions.csv', index=False)
results_df.to_csv('outputs/robustness/tables/TABLE_B3_detailed_results.csv', index=False)

# ============================================================
# VISUALIZATION: COEFFICIENT PLOT
# ============================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATION")
print("=" * 80)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 7))

# Sort by coefficient
results_df = results_df.sort_values('FCC_coef')

# Plot coefficients with confidence intervals
y_pos = np.arange(len(results_df))
coeffs = results_df['FCC_coef'].values
errors = results_df['FCC_se'].values * 1.96

# Color by significance
colors = []
for p in results_df['FCC_p'].values:
    if p < 0.01:
        colors.append('#d62728')  # Red for p<0.01
    elif p < 0.05:
        colors.append('#ff7f0e')  # Orange for p<0.05
    elif p < 0.10:
        colors.append('#2ca02c')  # Green for p<0.10
    else:
        colors.append('#7f7f7f')  # Gray for not significant

ax.barh(y_pos, coeffs, xerr=errors, capsize=5, color=colors, alpha=0.7, edgecolor='black')

# Add zero line
ax.axvline(x=0, color='black', linestyle='--', linewidth=2, alpha=0.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(results_df['Sample'].values)
ax.set_xlabel('FCC Effect Coefficient (95% CI)', fontsize=12, fontweight='bold')
ax.set_title('FCC Regulation Effect Across Sample Restrictions', fontsize=13, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#d62728', alpha=0.7, label='p < 0.01 (***)'),
    Patch(facecolor='#ff7f0e', alpha=0.7, label='p < 0.05 (**)'),
    Patch(facecolor='#2ca02c', alpha=0.7, label='p < 0.10 (*)'),
    Patch(facecolor='#7f7f7f', alpha=0.7, label='Not significant')
]
ax.legend(handles=legend_elements, loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/robustness/tables/FIGURE_B3_sample_restrictions.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure saved")

# ============================================================
# INTERPRETATION
# ============================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Compare to baseline
baseline = results_df[results_df['Sample'] == 'Full Sample'].iloc[0]
print(f"\n📊 BASELINE (Full Sample):")
print(f"   N: {baseline['N']}")
print(f"   FCC Effect: {baseline['FCC_coef']:.4f} (p={baseline['FCC_p']:.4f})")

# Count significant across restrictions
significant_samples = results_df[results_df['FCC_p'] < 0.10]
print(f"\n✓ FCC effect significant (p<0.10) in {len(significant_samples)}/{len(results_df)} samples")

for _, row in significant_samples.iterrows():
    print(f"  - {row['Sample']}: {row['FCC_coef']:.4f} (p={row['FCC_p']:.4f})")

# Check sign consistency
all_negative = (results_df['FCC_coef'] < 0).all()
all_positive = (results_df['FCC_coef'] > 0).all()

if all_negative:
    print(f"\n✓ Sign consistency: FCC effect is NEGATIVE across ALL samples")
elif all_positive:
    print(f"\n✓ Sign consistency: FCC effect is POSITIVE across ALL samples")
else:
    print(f"\n⚠ Sign inconsistency: FCC effect changes sign across samples")
    pos_samples = results_df[results_df['FCC_coef'] > 0]['Sample'].tolist()
    neg_samples = results_df[results_df['FCC_coef'] < 0]['Sample'].tolist()
    print(f"  Positive: {pos_samples}")
    print(f"  Negative: {neg_samples}")

# Range of estimates
min_coef = results_df['FCC_coef'].min()
max_coef = results_df['FCC_coef'].max()
print(f"\n📈 Range of FCC estimates: [{min_coef:.4f}, {max_coef:.4f}]")

if len(significant_samples) >= len(results_df) * 0.67:
    print(f"\n💡 CONCLUSION: FCC effect is ROBUST to sample restrictions")
    print(f"   Significant in {len(significant_samples)}/{len(results_df)} samples")
    print(f"   Main finding holds across different sample compositions")
else:
    print(f"\n⚠ CONCLUSION: FCC effect shows sensitivity to sample composition")
    print(f"   Significant in only {len(significant_samples)}/{len(results_df)} samples")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 3 COMPLETE")
print("=" * 80)
print("\nOutput saved to:")
print("  - outputs/robustness/tables/TABLE_B3_sample_restrictions.csv")
print("  - outputs/robustness/tables/FIGURE_B3_sample_restrictions.png")