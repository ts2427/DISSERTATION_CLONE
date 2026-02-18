"""
ESSAY 3: DISCLOSURE TIMING AND INFORMATION ASYMMETRY

Creates main regression tables for Essay 3:
- Information asymmetry changes post-breach
- Disclosure timing effects
- Volatility analysis

Tables:
- Table 2: Volatility changes
- Table 3: Information asymmetry measures
- Table 4: Disclosure timing effects
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col
from statsmodels.stats.outliers_influence import variance_inflation_factor
from pathlib import Path
import warnings
import matplotlib.pyplot as plt
from scipy import stats
warnings.filterwarnings('ignore')

print("=" * 80)
print("ESSAY 3: DISCLOSURE TIMING AND INFORMATION ASYMMETRY")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/tables/essay3')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/4] Loading data...")
df = pd.read_csv(DATA_FILE)
print(f"  [OK] Loaded: {len(df):,} breaches")

# Analysis sample
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  [OK] CRSP sample: {len(analysis_df):,} breaches")

# Create column aliases for consistency (Phase 2 variable standardization)
if 'disclosure_delay_days' in analysis_df.columns and 'days_to_disclosure' not in analysis_df.columns:
    analysis_df['days_to_disclosure'] = analysis_df['disclosure_delay_days']
if 'records_affected_numeric' in analysis_df.columns and 'records_affected' not in analysis_df.columns:
    analysis_df['records_affected'] = analysis_df['records_affected_numeric']
if 'has_enforcement' in analysis_df.columns and 'regulatory_enforcement' not in analysis_df.columns:
    analysis_df['regulatory_enforcement'] = analysis_df['has_enforcement']

# Convert boolean columns to numeric for statsmodels compatibility
bool_cols = analysis_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    analysis_df[col] = analysis_df[col].astype(int)

# ============================================================================
# CHECK AVAILABLE VARIABLES
# ============================================================================

print(f"\n[Step 2/4] Checking available variables...")

# Target variables
targets = {
    'volatility_change': 'Volatility Change',
    'return_volatility_post': 'Post-Breach Volatility',
    'volume_volatility_post': 'Volume Volatility'
}

available_targets = {k: v for k, v in targets.items() if k in analysis_df.columns}

if len(available_targets) == 0:
    print(f"  [ERROR] No volatility variables found!")
    print(f"  Available columns with 'volatility': {[c for c in analysis_df.columns if 'volatility' in c.lower()]}")
    exit()

print(f"  [OK] Available targets: {list(available_targets.keys())}")

# Use primary target
if 'volatility_change' in available_targets:
    target = 'volatility_change'
elif 'return_volatility_post' in available_targets:
    target = 'return_volatility_post'
else:
    target = list(available_targets.keys())[0]

print(f"  [OK] Primary target: {target}")

# Controls
controls_base = ['firm_size_log', 'leverage', 'roa']
controls_timing = ['days_to_disclosure', 'immediate_disclosure', 'delayed_disclosure']
controls_regulation = ['fcc_reportable']  # Phase 2 Addition: FCC regulation (H2-Extended)
controls_breach = ['total_affected_log', 'health_breach', 'prior_breaches_total']

# Check availability
available_controls_base = [v for v in controls_base if v in analysis_df.columns]
available_controls_timing = [v for v in controls_timing if v in analysis_df.columns]
available_controls_regulation = [v for v in controls_regulation if v in analysis_df.columns]
available_controls_breach = [v for v in controls_breach if v in analysis_df.columns]

print(f"  [OK] Base controls: {len(available_controls_base)}")
print(f"  [OK] Timing controls: {len(available_controls_timing)}")
print(f"  [OK] Regulation controls: {len(available_controls_regulation)}")
print(f"  [OK] Breach controls: {len(available_controls_breach)}")

# Add pre-breach volatility as control if available
if 'return_volatility_pre' in analysis_df.columns:
    available_controls_base.append('return_volatility_pre')
    print(f"  [OK] Added pre-breach volatility control")

# ============================================================================
# TABLE 2: VOLATILITY CHANGES
# ============================================================================

print(f"\n[Step 3/4] Creating Table 2: Volatility Changes...")

table2_models = []

# Prepare data - include days_to_disclosure if available
reg_cols_t2 = [target] + available_controls_base
if 'days_to_disclosure' in available_controls_timing:
    reg_cols_t2.append('days_to_disclosure')
reg_cols_t2 = [c for c in reg_cols_t2 if c in analysis_df.columns]
initial_n_t2 = len(analysis_df)
reg_df_t2 = analysis_df[reg_cols_t2].dropna()
dropped_t2 = initial_n_t2 - len(reg_df_t2)

print(f"  Sample size: {len(reg_df_t2):,} observations (dropped {dropped_t2:,} due to missing values)")

y2 = reg_df_t2[target]

# Model 1: Base controls only
X2_1 = sm.add_constant(reg_df_t2[available_controls_base])
model2_1 = sm.OLS(y2, X2_1).fit(cov_type='HC3')

# Validate output
assert not np.any(np.isnan(model2_1.params)), "NaN coefficients in Table 2 Model 1"
assert not np.any(np.isinf(model2_1.params)), "Infinite coefficients in Table 2 Model 1"

table2_models.append(model2_1)
print(f"  [OK] Model 1: R-squared = {model2_1.rsquared:.4f}")

# Model 2: Add disclosure timing
if 'days_to_disclosure' in reg_df_t2.columns:
    X2_2 = sm.add_constant(reg_df_t2[available_controls_base + ['days_to_disclosure']])
    model2_2 = sm.OLS(y2, X2_2).fit(cov_type='HC3')

    # Validate output
    assert not np.any(np.isnan(model2_2.params)), "NaN coefficients in Table 2 Model 2"
    assert not np.any(np.isinf(model2_2.params)), "Infinite coefficients in Table 2 Model 2"

    table2_models.append(model2_2)
    print(f"  [OK] Model 2: R-squared = {model2_2.rsquared:.4f}")

# Model 3: Add FCC Regulation (H2-Extended - CRITICAL)
if 'fcc_reportable' in analysis_df.columns:
    reg_cols_t2_3 = [target] + available_controls_base + available_controls_timing + available_controls_regulation
    reg_cols_t2_3 = [c for c in reg_cols_t2_3 if c in analysis_df.columns]
    reg_df_t2_3 = analysis_df[reg_cols_t2_3].dropna()

    y2_3 = reg_df_t2_3[target]
    X2_3 = sm.add_constant(reg_df_t2_3[[c for c in reg_cols_t2_3 if c != target]])
    model2_3 = sm.OLS(y2_3, X2_3).fit(cov_type='HC3')

    # Validate output
    assert not np.any(np.isnan(model2_3.params)), "NaN coefficients in Table 2 Model 3"
    assert not np.any(np.isinf(model2_3.params)), "Infinite coefficients in Table 2 Model 3"

    table2_models.append(model2_3)
    print(f"  [OK] Model 3 (H2-Extended): FCC Regulation, R-squared = {model2_3.rsquared:.4f}")

# Model 4: Add breach characteristics
if 'health_breach' in analysis_df.columns or 'total_affected_log' in analysis_df.columns:
    reg_cols_t2_4 = [target] + available_controls_base + available_controls_timing + available_controls_regulation + available_controls_breach
    reg_cols_t2_4 = [c for c in reg_cols_t2_4 if c in analysis_df.columns]
    reg_df_t2_4 = analysis_df[reg_cols_t2_4].dropna()

    y2_4 = reg_df_t2_4[target]
    X2_4 = sm.add_constant(reg_df_t2_4[[c for c in reg_cols_t2_4 if c != target]])
    model2_4 = sm.OLS(y2_4, X2_4).fit(cov_type='HC3')

    # Validate output
    assert not np.any(np.isnan(model2_4.params)), "NaN coefficients in Table 2 Model 4"
    assert not np.any(np.isinf(model2_4.params)), "Infinite coefficients in Table 2 Model 4"

    table2_models.append(model2_4)
    print(f"  [OK] Model 4 (Full): All controls, R-squared = {model2_4.rsquared:.4f}")

# Create table with proper model labels
model_labels = [
    'Model 1: Base',
    'Model 2: +Timing',
    'Model 3: +FCC (H2-Ext)',
    'Model 4: Full Spec'
]
# Trim to actual number of models
model_labels = model_labels[:len(table2_models)]

table2_summary = summary_col(
    table2_models,
    stars=True,
    float_format='%.4f',
    model_names=model_labels,
    info_dict={
        'N': lambda x: f"{int(x.nobs):,}",
        'R²': lambda x: f"{x.rsquared:.4f}",
        'Adj. R²': lambda x: f"{x.rsquared_adj:.4f}"
    }
)

# Save Table 2
with open(OUTPUT_DIR / 'TABLE2_volatility_changes.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("TABLE 2: POST-BREACH VOLATILITY CHANGES\n")
    f.write(f"Dependent Variable: {target.replace('_', ' ').title()}\n")
    f.write("=" * 100 + "\n\n")
    f.write(str(table2_summary))
    f.write("\n\n")
    f.write("Notes: Heteroskedasticity-robust standard errors (HC3) in parentheses.\n")
    f.write("*** p<0.01, ** p<0.05, * p<0.10\n")
    f.write("=" * 100 + "\n")

print(f"  [OK] Saved: TABLE2_volatility_changes.txt")

# ============================================================================
# TABLE 3: INFORMATION ASYMMETRY BY BREACH CHARACTERISTICS
# ============================================================================

print(f"\n[Step 4/4] Creating Table 3: Information Asymmetry...")

if len(available_controls_breach) > 0:
    
    table3_models = []
    
    # Prepare data - check what's actually available
    reg_cols_t3 = [target] + available_controls_base + available_controls_breach
    reg_cols_t3 = [c for c in reg_cols_t3 if c in analysis_df.columns]
    initial_n_t3 = len(analysis_df)
    reg_df_t3 = analysis_df[reg_cols_t3].dropna()
    dropped_t3 = initial_n_t3 - len(reg_df_t3)

    # Recheck what's available after dropna
    available_in_t3 = [c for c in available_controls_breach if c in reg_df_t3.columns]

    print(f"  Sample size: {len(reg_df_t3):,} observations (dropped {dropped_t3:,} due to missing values)")
    print(f"  Breach controls available: {available_in_t3}")
    
    y3 = reg_df_t3[target]
    
    # Model 1: Add breach size (if available)
    if 'total_affected_log' in available_in_t3:
        X3_1 = sm.add_constant(reg_df_t3[available_controls_base + ['total_affected_log']])
        model3_1 = sm.OLS(y3, X3_1).fit(cov_type='HC3')
        table3_models.append(model3_1)
        print(f"  [OK] Model 1: Breach size, R-squared = {model3_1.rsquared:.4f}")

    # Model 2: Add health breach (if available)
    if 'health_breach' in available_in_t3:
        vars_m2 = available_controls_base.copy()
        if 'total_affected_log' in available_in_t3:
            vars_m2.append('total_affected_log')
        vars_m2.append('health_breach')

        X3_2 = sm.add_constant(reg_df_t3[vars_m2])
        model3_2 = sm.OLS(y3, X3_2).fit(cov_type='HC3')
        table3_models.append(model3_2)
        print(f"  [OK] Model 2: Health breach, R-squared = {model3_2.rsquared:.4f}")

    # Model 3: Add prior breaches (if available)
    if 'prior_breaches_total' in available_in_t3:
        vars_m3 = available_controls_base.copy()
        if 'total_affected_log' in available_in_t3:
            vars_m3.append('total_affected_log')
        if 'health_breach' in available_in_t3:
            vars_m3.append('health_breach')
        vars_m3.append('prior_breaches_total')

        X3_3 = sm.add_constant(reg_df_t3[vars_m3])
        model3_3 = sm.OLS(y3, X3_3).fit(cov_type='HC3')
        table3_models.append(model3_3)
        print(f"  [OK] Model 3: Prior breaches, R-squared = {model3_3.rsquared:.4f}")
    
    # Only create table if we have models
    if len(table3_models) > 0:
        # Create table
        table3_summary = summary_col(
            table3_models,
            stars=True,
            float_format='%.4f',
            model_names=[f'Model {i+1}' for i in range(len(table3_models))],
            info_dict={
                'N': lambda x: f"{int(x.nobs):,}",
                'R²': lambda x: f"{x.rsquared:.4f}",
                'Adj. R²': lambda x: f"{x.rsquared_adj:.4f}"
            }
        )
        
        # Save Table 3
        with open(OUTPUT_DIR / 'TABLE3_information_asymmetry.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("TABLE 3: INFORMATION ASYMMETRY BY BREACH CHARACTERISTICS\n")
            f.write(f"Dependent Variable: {target.replace('_', ' ').title()}\n")
            f.write("=" * 100 + "\n\n")
            f.write(str(table3_summary))
            f.write("\n\n")
            f.write("Notes: Tests how breach characteristics affect information asymmetry.\n")
            f.write("Heteroskedasticity-robust standard errors (HC3). *** p<0.01, ** p<0.05, * p<0.10\n")
            f.write("=" * 100 + "\n")
        
        print(f"  [OK] Saved: TABLE3_information_asymmetry.txt")
    else:
        print(f"  [WARNING] No models created - missing all breach control variables")

else:
    print(f"  [WARNING] Breach characteristic variables not found, skipping Table 3")

# ============================================================================
# SUMMARY
# ============================================================================

print(f"\n" + "=" * 80)
print("[COMPLETE] ESSAY 3 REGRESSION ANALYSIS COMPLETE")
print("=" * 80)

print(f"\nTables created in {OUTPUT_DIR}/:")
print(f"  - TABLE2_volatility_changes.txt (Disclosure timing effects)")
if len(available_controls_breach) > 0:
    print(f"  - TABLE3_information_asymmetry.txt (Breach characteristics)")

print(f"\nMain regression tables ready for Essay 3!")
print("=" * 80)