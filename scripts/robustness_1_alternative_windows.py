import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 1: ALTERNATIVE EVENT WINDOWS")
print("Testing FCC effect across different CAR windows")
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

import os
os.makedirs('outputs/robustness/tables', exist_ok=True)

# ============================================================
# TEST ACROSS MULTIPLE EVENT WINDOWS
# ============================================================

print("\n" + "=" * 80)
print("TESTING ALTERNATIVE EVENT WINDOWS")
print("=" * 80)

# Define event windows to test
event_windows = {
    '3-Day CAR[-1,+1]': 'car_3d',
    '5-Day CAR[-2,+2]': 'car_5d', 
    '11-Day CAR[-5,+5]': 'car_11d',
    '30-Day CAR[-1,+30]': 'car_30d',
    '5-Day BHAR': 'bhar_5d',
    '30-Day BHAR': 'bhar_30d'
}

# Check which windows exist
available_windows = {}
for label, col in event_windows.items():
    if col in analysis_df.columns:
        available_windows[label] = col
        print(f"✓ {label}: {analysis_df[col].notna().sum()} observations")
    else:
        print(f"✗ {label}: Column '{col}' not found")

# ============================================================
# RUN REGRESSIONS FOR EACH WINDOW
# ============================================================

results_summary = []

for window_label, window_col in available_windows.items():
    print(f"\n{'='*80}")
    print(f"WINDOW: {window_label}")
    print(f"{'='*80}")
    
    # Prepare regression data
    reg_df = analysis_df[[window_col, 'immediate_disclosure', 'fcc_reportable',
                          'firm_size_log', 'leverage', 'roa']].dropna()
    
    print(f"Sample size: n={len(reg_df)}")
    
    # Create interactions
    reg_df['fcc_x_immediate'] = reg_df['fcc_reportable'] * reg_df['immediate_disclosure']
    
    # Full model
    y = reg_df[window_col]
    X = sm.add_constant(reg_df[['immediate_disclosure', 'fcc_reportable', 
                                 'fcc_x_immediate', 'firm_size_log', 
                                 'leverage', 'roa']])
    
    model = sm.OLS(y, X).fit(cov_type='HC3')
    
    # Extract key results
    results_summary.append({
        'Window': window_label,
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
    
    # Significance stars
    if model.pvalues['fcc_reportable'] < 0.01:
        sig = '***'
    elif model.pvalues['fcc_reportable'] < 0.05:
        sig = '**'
    elif model.pvalues['fcc_reportable'] < 0.10:
        sig = '*'
    else:
        sig = ''
    
    print(f"  Significance: {sig}")

# ============================================================
# CREATE SUMMARY TABLE
# ============================================================

results_df = pd.DataFrame(results_summary)

print("\n" + "=" * 80)
print("SUMMARY TABLE: FCC EFFECT ACROSS EVENT WINDOWS")
print("=" * 80)

# Create formatted table
summary_table = pd.DataFrame({
    'Event Window': results_df['Window'],
    'N': results_df['N'],
    'FCC Coefficient': results_df['FCC_coef'].apply(lambda x: f"{x:.4f}"),
    'Std. Error': results_df['FCC_se'].apply(lambda x: f"({x:.4f})"),
    'T-statistic': results_df['FCC_t'].apply(lambda x: f"{x:.2f}"),
    'P-value': results_df['FCC_p'].apply(lambda x: f"{x:.4f}"),
    'Significance': results_df.apply(lambda row: 
        '***' if row['FCC_p'] < 0.01 else 
        '**' if row['FCC_p'] < 0.05 else 
        '*' if row['FCC_p'] < 0.10 else 
        '', axis=1),
    'R²': results_df['R_squared'].apply(lambda x: f"{x:.4f}")
})

print("\n" + summary_table.to_string(index=False))

# Save table
summary_table.to_csv('outputs/robustness/tables/TABLE_B1_alternative_windows.csv', index=False)
results_df.to_csv('outputs/robustness/tables/TABLE_B1_detailed_results.csv', index=False)

# ============================================================
# INTERPRETATION
# ============================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

significant_windows = results_df[results_df['FCC_p'] < 0.10]['Window'].tolist()
print(f"\n✓ FCC effect significant (p<0.10) in {len(significant_windows)}/{len(results_df)} windows:")
for window in significant_windows:
    result = results_df[results_df['Window'] == window].iloc[0]
    print(f"  - {window}: {result['FCC_coef']:.4f} (p={result['FCC_p']:.4f})")

if len(significant_windows) >= len(results_df) * 0.67:
    print(f"\n💡 CONCLUSION: FCC effect is ROBUST across event windows")
    print(f"   Results hold in {len(significant_windows)}/{len(results_df)} specifications")
else:
    print(f"\n⚠ CONCLUSION: FCC effect shows some sensitivity to window choice")
    print(f"   Significant in {len(significant_windows)}/{len(results_df)} specifications")

# Check consistency of sign
all_negative = (results_df['FCC_coef'] < 0).all()
if all_negative:
    print(f"\n✓ Sign consistency: FCC effect is NEGATIVE across all windows")
else:
    print(f"\n⚠ Sign inconsistency: FCC effect changes sign across windows")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 1 COMPLETE")
print("=" * 80)
print("\nOutput saved to:")
print("  - outputs/robustness/tables/TABLE_B1_alternative_windows.csv")
print("  - outputs/robustness/tables/TABLE_B1_detailed_results.csv")