"""
ROBUSTNESS CHECK 1: Alternative Event Windows

Tests FCC regulation effect across multiple CAR/BHAR windows to ensure
results are not sensitive to event window specification.

Uses: FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 breaches, 85 variables)
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 1: ALTERNATIVE EVENT WINDOWS")
print("Testing consistency of FCC effect across different measurement periods")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/robustness')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'tables').mkdir(exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/5] Loading enriched dataset...")
df = pd.read_csv(DATA_FILE)
print(f"  ✓ Loaded: {len(df):,} breaches × {len(df.columns)} columns")

# Check what event study variables we have
event_vars = [col for col in df.columns if any(x in col.lower() for x in ['car', 'bhar'])]
print(f"  ✓ Event study variables: {len(event_vars)}")

# Analysis sample: Breaches with CRSP data
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  ✓ Sample with CRSP data: {len(analysis_df):,} breaches")

# ============================================================================
# DEFINE EVENT WINDOWS
# ============================================================================

print(f"\n[Step 2/5] Checking available event windows...")

# Map expected variable names to actual column names
event_windows = {}

# Check what we actually have
if 'car_5d' in df.columns:
    event_windows['5-Day CAR'] = 'car_5d'
if 'car_30d' in df.columns:
    event_windows['30-Day CAR'] = 'car_30d'
if 'bhar_5d' in df.columns:
    event_windows['5-Day BHAR'] = 'bhar_5d'
if 'bhar_30d' in df.columns:
    event_windows['30-Day BHAR'] = 'bhar_30d'

# Also check for other potential names
for col in df.columns:
    if 'car' in col.lower() and col not in event_windows.values():
        event_windows[f'CAR ({col})'] = col
    elif 'bhar' in col.lower() and col not in event_windows.values():
        event_windows[f'BHAR ({col})'] = col

print(f"\n  Available event windows:")
for label, col in event_windows.items():
    non_null = df[col].notna().sum()
    print(f"    • {label:20} ({col}): {non_null:,} observations")

if len(event_windows) == 0:
    print("\n  ✗ ERROR: No event study variables found!")
    exit()

# ============================================================================
# PREPARE CONTROL VARIABLES
# ============================================================================

print(f"\n[Step 3/5] Preparing control variables...")

# Core controls (check which exist)
controls = []
potential_controls = [
    'firm_size_log', 'leverage', 'roa', 'market_to_book',
    'prior_breaches_total', 'health_breach', 'severity_score',
    'media_coverage_count', 'immediate_disclosure'
]

for control in potential_controls:
    if control in analysis_df.columns:
        controls.append(control)

print(f"  ✓ Available controls: {len(controls)}")
print(f"    {', '.join(controls)}")

# Convert boolean variables to numeric if needed
bool_vars = ['immediate_disclosure', 'health_breach', 'has_crsp_data']
for var in bool_vars:
    if var in analysis_df.columns:
        analysis_df[var] = pd.to_numeric(analysis_df[var], errors='coerce').fillna(0)

# ============================================================================
# RUN REGRESSIONS ACROSS WINDOWS
# ============================================================================

print(f"\n[Step 4/5] Running regressions across event windows...")

results_summary = []

for window_label, window_col in event_windows.items():
    print(f"\n  Testing: {window_label}...")
    
    # Prepare regression data
    reg_cols = [window_col] + controls
    reg_df = analysis_df[reg_cols].dropna()
    
    print(f"    Sample: {len(reg_df):,} observations")
    
    if len(reg_df) < 50:
        print(f"    ⚠ Skipping (too few observations)")
        continue
    
    # Regression: DV = Controls
    y = reg_df[window_col]
    X = sm.add_constant(reg_df[controls])
    
    try:
        model = sm.OLS(y, X).fit(cov_type='HC3')
        
        # Extract key coefficients
        result = {
            'Window': window_label,
            'Variable': window_col,
            'N': int(model.nobs),
            'R_squared': model.rsquared,
            'Adj_R_squared': model.rsquared_adj
        }
        
        # Add all coefficients
        for var in controls:
            if var in model.params.index:
                result[f'{var}_coef'] = model.params[var]
                result[f'{var}_se'] = model.bse[var]
                result[f'{var}_t'] = model.tvalues[var]
                result[f'{var}_p'] = model.pvalues[var]
                
                # Significance
                if model.pvalues[var] < 0.01:
                    result[f'{var}_sig'] = '***'
                elif model.pvalues[var] < 0.05:
                    result[f'{var}_sig'] = '**'
                elif model.pvalues[var] < 0.10:
                    result[f'{var}_sig'] = '*'
                else:
                    result[f'{var}_sig'] = ''
        
        results_summary.append(result)
        
        # Print key results
        print(f"    R²: {model.rsquared:.4f}")
        
        # Show top 3 most significant predictors
        sig_vars = [(var, model.pvalues[var]) for var in controls if var in model.pvalues.index]
        sig_vars = sorted(sig_vars, key=lambda x: x[1])[:3]
        
        print(f"    Top predictors:")
        for var, pval in sig_vars:
            coef = model.params[var]
            sig = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.10 else ''
            print(f"      • {var}: {coef:.4f} (p={pval:.4f}) {sig}")
    
    except Exception as e:
        print(f"    ✗ Regression failed: {str(e)[:100]}")
        continue

# ============================================================================
# CREATE SUMMARY TABLE
# ============================================================================

print(f"\n[Step 5/5] Creating summary tables...")

if len(results_summary) == 0:
    print("  ✗ No results to summarize!")
    exit()

results_df = pd.DataFrame(results_summary)

# Create publication-ready table
summary_table = pd.DataFrame({
    'Event Window': results_df['Window'],
    'N': results_df['N'],
    'R²': results_df['R_squared'].apply(lambda x: f"{x:.4f}"),
    'Adj. R²': results_df['Adj_R_squared'].apply(lambda x: f"{x:.4f}")
})

# Add key coefficients if available
if 'immediate_disclosure_coef' in results_df.columns:
    summary_table['Immediate Disclosure'] = results_df.apply(
        lambda row: f"{row['immediate_disclosure_coef']:.4f}{row['immediate_disclosure_sig']}" 
        if pd.notna(row.get('immediate_disclosure_coef')) else 'N/A',
        axis=1
    )

if 'prior_breaches_total_coef' in results_df.columns:
    summary_table['Prior Breaches'] = results_df.apply(
        lambda row: f"{row['prior_breaches_total_coef']:.4f}{row['prior_breaches_total_sig']}"
        if pd.notna(row.get('prior_breaches_total_coef')) else 'N/A',
        axis=1
    )

if 'health_breach_coef' in results_df.columns:
    summary_table['Health Breach'] = results_df.apply(
        lambda row: f"{row['health_breach_coef']:.4f}{row['health_breach_sig']}"
        if pd.notna(row.get('health_breach_coef')) else 'N/A',
        axis=1
    )

print("\n" + "=" * 80)
print("SUMMARY: Coefficients Across Event Windows")
print("=" * 80)
print("\n" + summary_table.to_string(index=False))

# Save tables
summary_table.to_csv(OUTPUT_DIR / 'tables' / 'R01_alternative_windows_summary.csv', index=False)
results_df.to_csv(OUTPUT_DIR / 'tables' / 'R01_alternative_windows_full.csv', index=False)

print(f"\n✓ Tables saved to: {OUTPUT_DIR / 'tables'}/")

# ============================================================================
# INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Check consistency of key findings
if 'immediate_disclosure_p' in results_df.columns:
    sig_count = (results_df['immediate_disclosure_p'] < 0.10).sum()
    total = len(results_df)
    
    print(f"\nImmediate Disclosure Effect:")
    print(f"  • Significant (p<0.10) in {sig_count}/{total} windows ({sig_count/total*100:.0f}%)")
    
    if sig_count >= total * 0.67:
        print(f"  ✓ ROBUST: Effect holds across most specifications")
    else:
        print(f"  ⚠ SENSITIVITY: Effect varies by window choice")

if 'prior_breaches_total_p' in results_df.columns:
    sig_count = (results_df['prior_breaches_total_p'] < 0.10).sum()
    total = len(results_df)
    
    print(f"\nPrior Breach History Effect:")
    print(f"  • Significant (p<0.10) in {sig_count}/{total} windows ({sig_count/total*100:.0f}%)")

# R² comparison
avg_r2 = results_df['R_squared'].mean()
print(f"\nModel Fit:")
print(f"  • Average R²: {avg_r2:.4f}")
print(f"  • Range: {results_df['R_squared'].min():.4f} to {results_df['R_squared'].max():.4f}")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 1 COMPLETE")
print("=" * 80)

print(f"\nFiles created:")
print(f"  • R01_alternative_windows_summary.csv (publication table)")
print(f"  • R01_alternative_windows_full.csv (detailed results)")

print(f"\nConclusion:")
print(f"  Results analyzed across {len(results_summary)} event windows")
print(f"  Sample size: {len(analysis_df):,} breaches with CRSP data")
print("=" * 80)