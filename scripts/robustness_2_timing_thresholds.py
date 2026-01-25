"""
ROBUSTNESS CHECK 2: Alternative Disclosure Timing Thresholds

Tests whether market reaction to disclosure timing is sensitive to the choice
of "immediate" disclosure threshold (3, 5, 7, 14, 30, 60 days).

Uses: FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 breaches, 85 variables)
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 2: ALTERNATIVE DISCLOSURE TIMING THRESHOLDS")
print("Testing sensitivity to 'immediate disclosure' definition")
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

# Analysis sample
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  ✓ Sample with CRSP data: {len(analysis_df):,} breaches")

# Check for disclosure timing variable
timing_vars = [col for col in analysis_df.columns if 'disclos' in col.lower() and 'delay' in col.lower()]
print(f"\n  Timing variables found: {timing_vars}")

# Determine which variable to use
if 'days_to_disclosure' in analysis_df.columns:
    timing_var = 'days_to_disclosure'
elif 'disclosure_delay_days' in analysis_df.columns:
    timing_var = 'disclosure_delay_days'
elif len(timing_vars) > 0:
    timing_var = timing_vars[0]
else:
    print("\n  ✗ ERROR: No disclosure timing variable found!")
    exit()

print(f"  ✓ Using timing variable: {timing_var}")

# Check for immediate disclosure flag
if 'immediate_disclosure' in analysis_df.columns:
    print(f"  ✓ Existing immediate_disclosure: {analysis_df['immediate_disclosure'].sum()} breaches")

# ============================================================================
# CREATE ALTERNATIVE THRESHOLDS
# ============================================================================

print(f"\n[Step 2/5] Creating alternative timing thresholds...")

# Test different cutoffs
thresholds = [3, 5, 7, 14, 30, 60, 90]

for threshold in thresholds:
    col_name = f'immediate_{threshold}d'
    analysis_df[col_name] = (analysis_df[timing_var] <= threshold).astype(int)
    
    count = analysis_df[col_name].sum()
    pct = count / len(analysis_df) * 100
    print(f"  • ≤{threshold:3d} days: {count:4d} breaches ({pct:5.1f}%)")

# ============================================================================
# PREPARE CONTROLS
# ============================================================================

print(f"\n[Step 3/5] Preparing control variables...")

# Check for available controls
controls = []
potential_controls = [
    'firm_size_log', 'leverage', 'roa', 'market_to_book',
    'prior_breaches_total', 'health_breach', 'severity_score',
    'total_affected_log'
]

for control in potential_controls:
    if control in analysis_df.columns:
        controls.append(control)

print(f"  ✓ Available controls: {', '.join(controls)}")

# Target variable
if 'car_30d' in analysis_df.columns:
    target = 'car_30d'
elif 'car_5d' in analysis_df.columns:
    target = 'car_5d'
else:
    print("\n  ✗ ERROR: No CAR variable found!")
    exit()

print(f"  ✓ Target variable: {target}")

# ============================================================================
# RUN REGRESSIONS FOR EACH THRESHOLD
# ============================================================================

print(f"\n[Step 4/5] Running regressions across thresholds...")

results_summary = []

for threshold in thresholds:
    immediate_col = f'immediate_{threshold}d'
    
    print(f"\n  Testing ≤{threshold} days threshold...")
    
    # Prepare regression data
    reg_cols = [target, immediate_col] + controls
    reg_df = analysis_df[reg_cols].dropna()
    
    print(f"    Sample: {len(reg_df):,} observations")
    print(f"    Immediate: {reg_df[immediate_col].sum()} ({reg_df[immediate_col].mean()*100:.1f}%)")
    
    if len(reg_df) < 50:
        print(f"    ⚠ Skipping (too few observations)")
        continue
    
    # Regression
    y = reg_df[target]
    X = sm.add_constant(reg_df[[immediate_col] + controls])
    
    try:
        model = sm.OLS(y, X).fit(cov_type='HC3')
        
        # Extract results
        result = {
            'Threshold': f'≤{threshold} days',
            'Threshold_Days': threshold,
            'N': int(model.nobs),
            'N_Immediate': int(reg_df[immediate_col].sum()),
            'Pct_Immediate': reg_df[immediate_col].mean() * 100,
            'Immediate_coef': model.params[immediate_col],
            'Immediate_se': model.bse[immediate_col],
            'Immediate_t': model.tvalues[immediate_col],
            'Immediate_p': model.pvalues[immediate_col],
            'R_squared': model.rsquared,
            'Adj_R_squared': model.rsquared_adj
        }
        
        # Significance
        if model.pvalues[immediate_col] < 0.01:
            result['Sig'] = '***'
        elif model.pvalues[immediate_col] < 0.05:
            result['Sig'] = '**'
        elif model.pvalues[immediate_col] < 0.10:
            result['Sig'] = '*'
        else:
            result['Sig'] = ''
        
        results_summary.append(result)
        
        # Print key result
        print(f"    Coefficient: {model.params[immediate_col]:.4f} (t={model.tvalues[immediate_col]:.2f}, p={model.pvalues[immediate_col]:.4f}) {result['Sig']}")
    
    except Exception as e:
        print(f"    ✗ Regression failed: {str(e)[:100]}")
        continue

# ============================================================================
# CREATE SUMMARY TABLE & VISUALIZATION
# ============================================================================

print(f"\n[Step 5/5] Creating summary tables and visualizations...")

if len(results_summary) == 0:
    print("  ✗ No results to summarize!")
    exit()

results_df = pd.DataFrame(results_summary)

# Publication table
summary_table = pd.DataFrame({
    'Threshold': results_df['Threshold'],
    'N': results_df['N'],
    'N Immediate': results_df['N_Immediate'],
    '% Immediate': results_df['Pct_Immediate'].apply(lambda x: f"{x:.1f}%"),
    'Coefficient': results_df['Immediate_coef'].apply(lambda x: f"{x:.4f}"),
    'Std. Error': results_df['Immediate_se'].apply(lambda x: f"({x:.4f})"),
    'T-statistic': results_df['Immediate_t'].apply(lambda x: f"{x:.2f}"),
    'P-value': results_df['Immediate_p'].apply(lambda x: f"{x:.4f}"),
    'Sig.': results_df['Sig'],
    'R²': results_df['R_squared'].apply(lambda x: f"{x:.4f}")
})

print("\n" + "=" * 80)
print("SUMMARY: Disclosure Timing Effects Across Thresholds")
print("=" * 80)
print("\n" + summary_table.to_string(index=False))

# Save tables
summary_table.to_csv(OUTPUT_DIR / 'tables' / 'R02_timing_thresholds_summary.csv', index=False)
results_df.to_csv(OUTPUT_DIR / 'tables' / 'R02_timing_thresholds_full.csv', index=False)

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Coefficient plot with CIs
x = results_df['Threshold_Days']
y = results_df['Immediate_coef']
yerr = results_df['Immediate_se'] * 1.96  # 95% CI

ax1.errorbar(x, y, yerr=yerr, fmt='o-', linewidth=2, markersize=8,
            capsize=5, capthick=2, color='steelblue', label='Immediate Disclosure Effect')
ax1.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Zero Effect')
ax1.axvline(x=7, color='green', linestyle=':', linewidth=2, alpha=0.5, label='Regulatory Threshold')

ax1.set_xlabel('Disclosure Threshold (Days)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Coefficient on Immediate Disclosure', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Effect Size by Threshold', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(alpha=0.3)

# Panel B: Sample composition
n_immediate = results_df['N_Immediate'].values
n_delayed = results_df['N'].values - n_immediate

ax2.bar(x, n_immediate, label='Immediate', color='lightgreen', alpha=0.8)
ax2.bar(x, n_delayed, bottom=n_immediate, label='Delayed', color='coral', alpha=0.8)

ax2.axvline(x=7, color='green', linestyle=':', linewidth=2, alpha=0.5)
ax2.set_xlabel('Disclosure Threshold (Days)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Number of Breaches', fontsize=11, fontweight='bold')
ax2.set_title('Panel B: Sample Composition by Threshold', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figures' / 'R02_timing_thresholds.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✓ Figure saved to: {OUTPUT_DIR / 'figures' / 'R02_timing_thresholds.png'}")

# ============================================================================
# INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Check 7-day threshold (regulatory standard)
if 7 in results_df['Threshold_Days'].values:
    threshold_7 = results_df[results_df['Threshold_Days'] == 7].iloc[0]
    print(f"\n📊 REGULATORY THRESHOLD (7 days):")
    print(f"   • Coefficient: {threshold_7['Immediate_coef']:.4f}")
    print(f"   • P-value: {threshold_7['Immediate_p']:.4f}")
    print(f"   • Significant: {'Yes' if threshold_7['Immediate_p'] < 0.10 else 'No'} {threshold_7['Sig']}")
    print(f"   • Sample: {threshold_7['N_Immediate']:.0f}/{threshold_7['N']:.0f} immediate ({threshold_7['Pct_Immediate']:.1f}%)")

# Count significant results
sig_count = (results_df['Immediate_p'] < 0.10).sum()
total = len(results_df)

print(f"\nSignificance Across Thresholds:")
print(f"  • Significant (p<0.10): {sig_count}/{total} thresholds ({sig_count/total*100:.0f}%)")

if sig_count >= total * 0.67:
    print(f"  ✓ ROBUST: Timing effect holds across most specifications")
else:
    print(f"  ⚠ SENSITIVE: Timing effect varies by threshold choice")

# Check sign consistency
all_positive = (results_df['Immediate_coef'] > 0).all()
all_negative = (results_df['Immediate_coef'] < 0).all()

print(f"\nSign Consistency:")
if all_positive:
    print(f"  ✓ All coefficients POSITIVE - consistent direction")
elif all_negative:
    print(f"  ✓ All coefficients NEGATIVE - consistent direction")
else:
    print(f"  ⚠ Mixed signs - inconsistent direction")

# Economic magnitude
mean_effect = results_df['Immediate_coef'].mean()
print(f"\nEconomic Magnitude:")
print(f"  • Mean effect across thresholds: {mean_effect:.4f}")
print(f"  • Range: {results_df['Immediate_coef'].min():.4f} to {results_df['Immediate_coef'].max():.4f}")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 2 COMPLETE")
print("=" * 80)

print(f"\nFiles created:")
print(f"  • {OUTPUT_DIR / 'tables' / 'R02_timing_thresholds_summary.csv'}")
print(f"  • {OUTPUT_DIR / 'tables' / 'R02_timing_thresholds_full.csv'}")
print(f"  • {OUTPUT_DIR / 'figures' / 'R02_timing_thresholds.png'}")

print(f"\nConclusion:")
print(f"  Tested {len(results_df)} alternative thresholds")
print(f"  Results {'ROBUST' if sig_count >= total * 0.67 else 'SENSITIVE'} to threshold choice")
print("=" * 80)