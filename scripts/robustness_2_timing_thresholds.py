import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 2: ALTERNATIVE DISCLOSURE TIMING THRESHOLDS")
print("Testing immediate disclosure effect at different cutoffs")
print("=" * 80)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')

# Analysis sample
analysis_df = df[(df['has_crsp_data'] == True) & 
                 (df['firm_size_log'].notna())].copy()

# Convert booleans
bool_cols = ['fcc_reportable', 'large_firm']
for col in bool_cols:
    if col in analysis_df.columns:
        analysis_df[col] = analysis_df[col].astype(int)

print(f"\n✓ Analysis sample: {len(analysis_df)} records")

import os
os.makedirs('outputs/robustness/tables', exist_ok=True)

# ============================================================
# CREATE ALTERNATIVE TIMING DEFINITIONS
# ============================================================

print("\n" + "=" * 80)
print("CREATING ALTERNATIVE TIMING THRESHOLDS")
print("=" * 80)

# Test different cutoffs
thresholds = [3, 5, 7, 14, 30, 60]

for threshold in thresholds:
    col_name = f'immediate_{threshold}d'
    analysis_df[col_name] = (analysis_df['disclosure_delay_days'] <= threshold).astype(int)
    count = analysis_df[col_name].sum()
    pct = count / len(analysis_df) * 100
    print(f"✓ ≤{threshold:2d} days: {count:4d} observations ({pct:5.1f}%)")

# ============================================================
# RUN REGRESSIONS FOR EACH THRESHOLD
# ============================================================

results_summary = []

for threshold in thresholds:
    print(f"\n{'='*80}")
    print(f"THRESHOLD: ≤{threshold} DAYS")
    print(f"{'='*80}")
    
    immediate_col = f'immediate_{threshold}d'
    
    # Prepare regression data
    reg_df = analysis_df[['car_30d', immediate_col, 'fcc_reportable',
                          'firm_size_log', 'leverage', 'roa']].dropna()
    
    print(f"Sample size: n={len(reg_df)}")
    print(f"Immediate disclosures: {reg_df[immediate_col].sum()} ({reg_df[immediate_col].mean()*100:.1f}%)")
    
    # Create interactions
    reg_df['fcc_x_immediate'] = reg_df['fcc_reportable'] * reg_df[immediate_col]
    
    # Full model
    y = reg_df['car_30d']
    X = sm.add_constant(reg_df[[immediate_col, 'fcc_reportable', 
                                 'fcc_x_immediate', 'firm_size_log', 
                                 'leverage', 'roa']])
    
    model = sm.OLS(y, X).fit(cov_type='HC3')
    
    # Extract key results
    results_summary.append({
        'Threshold': f'≤{threshold} days',
        'Threshold_Days': threshold,
        'N': int(model.nobs),
        'N_Immediate': int(reg_df[immediate_col].sum()),
        'Pct_Immediate': reg_df[immediate_col].mean() * 100,
        'Immediate_coef': model.params[immediate_col],
        'Immediate_se': model.bse[immediate_col],
        'Immediate_t': model.tvalues[immediate_col],
        'Immediate_p': model.pvalues[immediate_col],
        'FCC_coef': model.params['fcc_reportable'],
        'FCC_p': model.pvalues['fcc_reportable'],
        'Interaction_coef': model.params['fcc_x_immediate'],
        'Interaction_p': model.pvalues['fcc_x_immediate'],
        'R_squared': model.rsquared
    })
    
    # Print key results
    print(f"\nKey Results:")
    print(f"  Immediate Effect: {model.params[immediate_col]:.4f} (t={model.tvalues[immediate_col]:.2f}, p={model.pvalues[immediate_col]:.4f})")
    print(f"  FCC Effect: {model.params['fcc_reportable']:.4f} (p={model.pvalues['fcc_reportable']:.4f})")
    print(f"  Interaction: {model.params['fcc_x_immediate']:.4f} (p={model.pvalues['fcc_x_immediate']:.4f})")
    
    # Significance
    if model.pvalues[immediate_col] < 0.01:
        sig = '***'
    elif model.pvalues[immediate_col] < 0.05:
        sig = '**'
    elif model.pvalues[immediate_col] < 0.10:
        sig = '*'
    else:
        sig = ''
    
    print(f"  Significance: {sig if sig else 'Not significant'}")

# ============================================================
# CREATE SUMMARY TABLE
# ============================================================

results_df = pd.DataFrame(results_summary)

print("\n" + "=" * 80)
print("SUMMARY TABLE: DISCLOSURE TIMING EFFECTS")
print("=" * 80)

# Create formatted table
summary_table = pd.DataFrame({
    'Threshold': results_df['Threshold'],
    'N': results_df['N'],
    'N Immediate': results_df['N_Immediate'],
    '% Immediate': results_df['Pct_Immediate'].apply(lambda x: f"{x:.1f}%"),
    'Coefficient': results_df['Immediate_coef'].apply(lambda x: f"{x:.4f}"),
    'Std. Error': results_df['Immediate_se'].apply(lambda x: f"({x:.4f})"),
    'T-stat': results_df['Immediate_t'].apply(lambda x: f"{x:.2f}"),
    'P-value': results_df['Immediate_p'].apply(lambda x: f"{x:.4f}"),
    'Sig.': results_df.apply(lambda row: 
        '***' if row['Immediate_p'] < 0.01 else 
        '**' if row['Immediate_p'] < 0.05 else 
        '*' if row['Immediate_p'] < 0.10 else 
        '', axis=1)
})

print("\n" + summary_table.to_string(index=False))

# Save table
summary_table.to_csv('outputs/robustness/tables/TABLE_B2_timing_thresholds.csv', index=False)
results_df.to_csv('outputs/robustness/tables/TABLE_B2_detailed_results.csv', index=False)

# ============================================================
# VISUALIZATION: COEFFICIENT PLOT
# ============================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATION")
print("=" * 80)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

# Plot coefficients with confidence intervals
x = results_df['Threshold_Days']
y = results_df['Immediate_coef']
yerr = results_df['Immediate_se'] * 1.96  # 95% CI

ax.errorbar(x, y, yerr=yerr, fmt='o-', linewidth=2, markersize=8,
            capsize=5, capthick=2, color='#1f77b4', label='Immediate Disclosure Effect')

# Add zero line
ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7)

# Highlight FCC threshold (7 days)
ax.axvline(x=7, color='green', linestyle=':', linewidth=2, alpha=0.5, label='FCC Threshold (7 days)')

ax.set_xlabel('Disclosure Threshold (Days)', fontsize=12, fontweight='bold')
ax.set_ylabel('Immediate Disclosure Coefficient', fontsize=12, fontweight='bold')
ax.set_title('Disclosure Timing Effect Across Alternative Thresholds\n(95% Confidence Intervals)', 
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/robustness/tables/FIGURE_B2_timing_thresholds.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure saved")

# ============================================================
# INTERPRETATION
# ============================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Check 7-day threshold specifically
threshold_7 = results_df[results_df['Threshold_Days'] == 7].iloc[0]
print(f"\n📊 FCC THRESHOLD (7 days):")
print(f"   Coefficient: {threshold_7['Immediate_coef']:.4f}")
print(f"   P-value: {threshold_7['Immediate_p']:.4f}")
print(f"   Significant: {'Yes' if threshold_7['Immediate_p'] < 0.10 else 'No'}")

# Compare to other thresholds
significant_thresholds = results_df[results_df['Immediate_p'] < 0.10]
print(f"\n✓ Significant thresholds (p<0.10): {len(significant_thresholds)}/{len(results_df)}")
for _, row in significant_thresholds.iterrows():
    print(f"  - {row['Threshold']}: {row['Immediate_coef']:.4f} (p={row['Immediate_p']:.4f})")

# Check sign consistency
all_positive = (results_df['Immediate_coef'] > 0).all()
all_negative = (results_df['Immediate_coef'] < 0).all()

if all_positive or all_negative:
    direction = "positive" if all_positive else "negative"
    print(f"\n✓ Sign consistency: Immediate disclosure effect is {direction} across ALL thresholds")
else:
    print(f"\n⚠ Sign inconsistency: Immediate disclosure effect changes sign")

# Economic magnitude at FCC threshold
if threshold_7['Immediate_p'] < 0.10:
    print(f"\n💡 CONCLUSION: FCC 7-day threshold shows significant effect")
    print(f"   Immediate disclosure (≤7 days): {threshold_7['Immediate_coef']:.2f}% market impact")
else:
    print(f"\n💡 CONCLUSION: FCC 7-day threshold shows no significant effect")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 2 COMPLETE")
print("=" * 80)
print("\nOutput saved to:")
print("  - outputs/robustness/tables/TABLE_B2_timing_thresholds.csv")
print("  - outputs/robustness/tables/FIGURE_B2_timing_thresholds.png")