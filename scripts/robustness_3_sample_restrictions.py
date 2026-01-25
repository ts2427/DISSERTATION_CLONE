"""
ROBUSTNESS CHECK 3: Sample Restrictions

Tests whether main findings hold across different sample compositions:
- Excluding crisis periods (2008-2009, 2020-2021)
- Excluding extreme firm sizes
- Different time periods
- Winsorized returns

Uses: FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 breaches, 85 variables)
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROBUSTNESS CHECK 3: SAMPLE RESTRICTIONS")
print("Testing consistency of findings across sample compositions")
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

# Base analysis sample
base_df = df[df['has_crsp_data'] == True].copy()
print(f"  ✓ Base sample with CRSP data: {len(base_df):,} breaches")

# Check for required variables
required = ['firm_size_log', 'breach_date']
missing = [var for var in required if var not in base_df.columns]
if missing:
    print(f"  ✗ Missing required variables: {missing}")
    exit()

# Target variable
if 'car_30d' in base_df.columns:
    target = 'car_30d'
elif 'car_5d' in base_df.columns:
    target = 'car_5d'
else:
    print("\n  ✗ ERROR: No CAR variable found!")
    exit()

print(f"  ✓ Target variable: {target}")

# ============================================================================
# DEFINE SAMPLE RESTRICTIONS
# ============================================================================

print(f"\n[Step 2/5] Defining sample restrictions...")

sample_restrictions = {}

# 1. FULL SAMPLE (Baseline)
sample_restrictions['1. Full Sample'] = base_df.copy()
print(f"\n  1. Full Sample: {len(sample_restrictions['1. Full Sample']):,} observations")

# 2. EXCLUDE FINANCIAL CRISIS (2008-2009)
crisis_df = base_df[~base_df['breach_date'].dt.year.isin([2008, 2009])].copy()
sample_restrictions['2. Exclude Crisis (2008-09)'] = crisis_df
dropped = len(base_df) - len(crisis_df)
print(f"  2. Exclude Crisis: {len(crisis_df):,} observations (dropped {dropped})")

# 3. EXCLUDE COVID PERIOD (2020-2021)
covid_df = base_df[~base_df['breach_date'].dt.year.isin([2020, 2021])].copy()
sample_restrictions['3. Exclude COVID (2020-21)'] = covid_df
dropped = len(base_df) - len(covid_df)
print(f"  3. Exclude COVID: {len(covid_df):,} observations (dropped {dropped})")

# 4. EXCLUDE BOTH CRISIS AND COVID
crisis_covid_df = base_df[~base_df['breach_date'].dt.year.isin([2008, 2009, 2020, 2021])].copy()
sample_restrictions['4. Exclude Crisis & COVID'] = crisis_covid_df
dropped = len(base_df) - len(crisis_covid_df)
print(f"  4. Exclude Crisis & COVID: {len(crisis_covid_df):,} observations (dropped {dropped})")

# 5. EXCLUDE SMALLEST 25% OF FIRMS
size_q25 = base_df['firm_size_log'].quantile(0.25)
no_small_df = base_df[base_df['firm_size_log'] > size_q25].copy()
sample_restrictions['5. Exclude Smallest Quartile'] = no_small_df
dropped = len(base_df) - len(no_small_df)
print(f"  5. Exclude Smallest Quartile: {len(no_small_df):,} observations (dropped {dropped})")
print(f"     Size threshold (log): {size_q25:.2f}")

# 6. EXCLUDE LARGEST 10% OF FIRMS
size_p90 = base_df['firm_size_log'].quantile(0.90)
no_large_df = base_df[base_df['firm_size_log'] <= size_p90].copy()
sample_restrictions['6. Exclude Largest Decile'] = no_large_df
dropped = len(base_df) - len(no_large_df)
print(f"  6. Exclude Largest Decile: {len(no_large_df):,} observations (dropped {dropped})")
print(f"     Size threshold (log): {size_p90:.2f}")

# 7. POST-2015 ONLY (Modern cybersecurity era)
post2015_df = base_df[base_df['breach_date'].dt.year >= 2015].copy()
sample_restrictions['7. Post-2015 Only'] = post2015_df
dropped = len(base_df) - len(post2015_df)
print(f"  7. Post-2015 Only: {len(post2015_df):,} observations (dropped {dropped})")

# 8. WINSORIZE EXTREME RETURNS (1% tails)
winsor_df = base_df.copy()
if target in winsor_df.columns:
    lower = winsor_df[target].quantile(0.01)
    upper = winsor_df[target].quantile(0.99)
    winsor_df[target] = winsor_df[target].clip(lower=lower, upper=upper)
    sample_restrictions['8. Winsorized Returns (1%)'] = winsor_df
    print(f"  8. Winsorized Returns: {len(winsor_df):,} observations")
    print(f"     Bounds: [{lower:.2f}, {upper:.2f}]")

# ============================================================================
# PREPARE CONTROLS
# ============================================================================

print(f"\n[Step 3/5] Preparing control variables...")

# Check for available controls
controls = []
potential_controls = [
    'firm_size_log', 'leverage', 'roa', 'market_to_book',
    'prior_breaches_total', 'health_breach', 'severity_score',
    'immediate_disclosure', 'media_coverage_count'
]

for control in potential_controls:
    if control in base_df.columns:
        controls.append(control)

print(f"  ✓ Available controls: {len(controls)}")
print(f"    {', '.join(controls[:5])}...")

# ============================================================================
# RUN REGRESSIONS FOR EACH SAMPLE
# ============================================================================

print(f"\n[Step 4/5] Running regressions across sample restrictions...")

results_summary = []

for sample_name, sample_df in sample_restrictions.items():
    print(f"\n  Testing: {sample_name}...")
    
    # Prepare regression data
    reg_cols = [target] + controls
    reg_df = sample_df[reg_cols].dropna()
    
    print(f"    Sample: {len(reg_df):,} observations")
    
    if len(reg_df) < 50:
        print(f"    ⚠ Skipping (too few observations)")
        continue
    
    # Regression
    y = reg_df[target]
    X = sm.add_constant(reg_df[controls])
    
    try:
        model = sm.OLS(y, X).fit(cov_type='HC3')
        
        # Extract results
        result = {
            'Sample': sample_name,
            'N': int(model.nobs),
            'R_squared': model.rsquared,
            'Adj_R_squared': model.rsquared_adj
        }
        
        # Add key coefficients
        key_vars = ['immediate_disclosure', 'prior_breaches_total', 'health_breach']
        for var in key_vars:
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
        
        # Print key result
        print(f"    R²: {model.rsquared:.4f}, N={model.nobs}")
        
        # Show most significant predictor
        if len(model.params) > 1:
            sig_vars = [(var, model.pvalues[var]) for var in controls if var in model.pvalues.index]
            if sig_vars:
                top_var, top_pval = min(sig_vars, key=lambda x: x[1])
                top_coef = model.params[top_var]
                sig = '***' if top_pval < 0.01 else '**' if top_pval < 0.05 else '*' if top_pval < 0.10 else ''
                print(f"    Top: {top_var} = {top_coef:.4f} (p={top_pval:.4f}) {sig}")
    
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
    'Sample Restriction': results_df['Sample'],
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

print("\n" + "=" * 80)
print("SUMMARY: Key Coefficients Across Sample Restrictions")
print("=" * 80)
print("\n" + summary_table.to_string(index=False))

# Save tables
summary_table.to_csv(OUTPUT_DIR / 'tables' / 'R03_sample_restrictions_summary.csv', index=False)
results_df.to_csv(OUTPUT_DIR / 'tables' / 'R03_sample_restrictions_full.csv', index=False)

# Create visualization
fig, ax = plt.subplots(figsize=(12, 8))

# Plot R-squared values
y_pos = np.arange(len(results_df))
r2_values = results_df['R_squared'].values

# Create color scale based on sample size
sizes = results_df['N'].values
norm_sizes = (sizes - sizes.min()) / (sizes.max() - sizes.min())
colors = plt.cm.viridis(norm_sizes)

bars = ax.barh(y_pos, r2_values, color=colors, alpha=0.8, edgecolor='black')

ax.set_yticks(y_pos)
ax.set_yticklabels(results_df['Sample'].values, fontsize=10)
ax.set_xlabel('R² (Model Fit)', fontsize=12, fontweight='bold')
ax.set_title('Model Fit Across Sample Restrictions', fontsize=13, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add sample size labels
for i, (bar, n) in enumerate(zip(bars, results_df['N'])):
    width = bar.get_width()
    ax.text(width + 0.005, bar.get_y() + bar.get_height()/2,
            f'n={n:,}', ha='left', va='center', fontsize=9)

# Color bar for sample size
sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, 
                           norm=plt.Normalize(vmin=sizes.min(), vmax=sizes.max()))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.12)
cbar.set_label('Sample Size', fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figures' / 'R03_sample_restrictions.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✓ Figure saved to: {OUTPUT_DIR / 'figures' / 'R03_sample_restrictions.png'}")

# ============================================================================
# INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Compare to baseline
baseline = results_df[results_df['Sample'].str.contains('Full Sample')].iloc[0]
print(f"\n📊 BASELINE (Full Sample):")
print(f"   • N: {baseline['N']:,}")
print(f"   • R²: {baseline['R_squared']:.4f}")

# R² stability
avg_r2 = results_df['R_squared'].mean()
std_r2 = results_df['R_squared'].std()
min_r2 = results_df['R_squared'].min()
max_r2 = results_df['R_squared'].max()

print(f"\nModel Fit Stability:")
print(f"  • Average R²: {avg_r2:.4f}")
print(f"  • Std Dev: {std_r2:.4f}")
print(f"  • Range: [{min_r2:.4f}, {max_r2:.4f}]")

if std_r2 < 0.02:
    print(f"  ✓ STABLE: Model fit is consistent across samples")
else:
    print(f"  ⚠ VARIABLE: Model fit varies by sample composition")

# Sample size variation
print(f"\nSample Size Range:")
print(f"  • Min: {results_df['N'].min():,} ({results_df[results_df['N'] == results_df['N'].min()]['Sample'].iloc[0]})")
print(f"  • Max: {results_df['N'].max():,} ({results_df[results_df['N'] == results_df['N'].max()]['Sample'].iloc[0]})")

# Key findings consistency
if 'immediate_disclosure_p' in results_df.columns:
    sig_count = (results_df['immediate_disclosure_p'] < 0.10).sum()
    total = (~results_df['immediate_disclosure_p'].isna()).sum()
    
    print(f"\nImmediate Disclosure Effect:")
    print(f"  • Significant (p<0.10) in {sig_count}/{total} samples ({sig_count/total*100:.0f}%)")
    
    if sig_count >= total * 0.67:
        print(f"  ✓ ROBUST: Effect holds across most specifications")

print("\n" + "=" * 80)
print("✓ ROBUSTNESS CHECK 3 COMPLETE")
print("=" * 80)

print(f"\nFiles created:")
print(f"  • {OUTPUT_DIR / 'tables' / 'R03_sample_restrictions_summary.csv'}")
print(f"  • {OUTPUT_DIR / 'tables' / 'R03_sample_restrictions_full.csv'}")
print(f"  • {OUTPUT_DIR / 'figures' / 'R03_sample_restrictions.png'}")

print(f"\nConclusion:")
print(f"  Tested {len(results_df)} sample restrictions")
print(f"  Model fit range: {min_r2:.4f} to {max_r2:.4f}")
print(f"  Findings {'ROBUST' if std_r2 < 0.02 else 'SENSITIVE'} to sample composition")
print("=" * 80)