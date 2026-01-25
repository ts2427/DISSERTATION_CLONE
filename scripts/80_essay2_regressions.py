"""
ESSAY 2: MAIN REGRESSION ANALYSIS

Creates main regression tables for Essay 2:
- Market reactions to data breach disclosures
- Tests H1-H5

Tables:
- Table 2: Baseline models (Immediate disclosure - H1)
- Table 3: FCC Regulation (H2)
- Table 4: Prior breach effects (Reputation - H3)
- Table 5: Breach severity (Heterogeneity - H4)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ESSAY 2: MAIN REGRESSION ANALYSIS")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/tables/essay2')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/6] Loading data...")
df = pd.read_csv(DATA_FILE)
print(f"  ✓ Loaded: {len(df):,} breaches")

# Analysis sample (with CRSP data)
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"  ✓ CRSP sample: {len(analysis_df):,} breaches")

# Target variable
target = 'car_30d'
print(f"  ✓ Dependent variable: {target}")

# ============================================================================
# DEFINE VARIABLE GROUPS
# ============================================================================

print(f"\n[Step 2/6] Preparing variables...")

# Core controls
controls_base = ['firm_size_log', 'leverage', 'roa']

# Extended controls
controls_extended = controls_base + ['market_to_book', 'total_affected_log']

# Governance
controls_governance = ['sox_404_effective', 'material_weakness']

# Check what's available
available_controls_base = [v for v in controls_base if v in analysis_df.columns]
available_controls_extended = [v for v in controls_extended if v in analysis_df.columns]
available_controls_gov = [v for v in controls_governance if v in analysis_df.columns]

print(f"  ✓ Base controls: {len(available_controls_base)}")
print(f"  ✓ Extended controls: {len(available_controls_extended)}")
print(f"  ✓ Governance controls: {len(available_controls_gov)}")

# ============================================================================
# TABLE 2: BASELINE MODELS (H1: IMMEDIATE DISCLOSURE)
# ============================================================================

print(f"\n[Step 3/6] Creating Table 2: Baseline Models (H1)...")

table2_models = []

# Prepare regression data
reg_cols = [target, 'immediate_disclosure'] + available_controls_extended + available_controls_gov
reg_df = analysis_df[reg_cols].dropna()

# Convert to numeric
for col in reg_df.columns:
    reg_df[col] = pd.to_numeric(reg_df[col], errors='coerce')

reg_df = reg_df.dropna()

print(f"  Sample size: {len(reg_df):,} observations")

# Model 1: Immediate disclosure only + base controls
y = reg_df[target]
X1 = sm.add_constant(reg_df[['immediate_disclosure'] + available_controls_base])
model1 = sm.OLS(y, X1).fit(cov_type='HC3')
table2_models.append(model1)
print(f"  ✓ Model 1: R² = {model1.rsquared:.4f}")

# Model 2: Add extended controls
X2 = sm.add_constant(reg_df[['immediate_disclosure'] + available_controls_extended])
model2 = sm.OLS(y, X2).fit(cov_type='HC3')
table2_models.append(model2)
print(f"  ✓ Model 2: R² = {model2.rsquared:.4f}")

# Model 3: Add governance
if len(available_controls_gov) > 0:
    X3 = sm.add_constant(reg_df[['immediate_disclosure'] + available_controls_extended + available_controls_gov])
    model3 = sm.OLS(y, X3).fit(cov_type='HC3')
    table2_models.append(model3)
    print(f"  ✓ Model 3: R² = {model3.rsquared:.4f}")

# Create regression table
table2_summary = summary_col(
    table2_models,
    stars=True,
    float_format='%.4f',
    model_names=[f'Model {i+1}' for i in range(len(table2_models))],
    info_dict={
        'N': lambda x: f"{int(x.nobs):,}",
        'R²': lambda x: f"{x.rsquared:.4f}",
        'Adj. R²': lambda x: f"{x.rsquared_adj:.4f}"
    }
)

# Save Table 2
with open(OUTPUT_DIR / 'TABLE2_baseline_disclosure.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("TABLE 2: MARKET REACTIONS TO IMMEDIATE DISCLOSURE (H1)\n")
    f.write("Dependent Variable: 30-Day Cumulative Abnormal Returns (CAR)\n")
    f.write("=" * 100 + "\n\n")
    f.write(str(table2_summary))
    f.write("\n\n")
    f.write("Notes: Heteroskedasticity-robust standard errors (HC3) in parentheses.\n")
    f.write("*** p<0.01, ** p<0.05, * p<0.10\n")
    f.write("=" * 100 + "\n")

print(f"  ✓ Saved: TABLE2_baseline_disclosure.txt")

# ============================================================================
# TABLE 3: FCC REGULATION (H2)
# ============================================================================

print(f"\n[Step 4/6] Creating Table 3: FCC Regulation Effects (H2)...")

if 'fcc_reportable' in analysis_df.columns:
    
    table3_models = []# ============================================================================
# TABLE 3: FCC REGULATION (H2)
# ============================================================================

print(f"\n[Step 4/6] Creating Table 3: FCC Regulation Effects (H2)...")

if 'fcc_reportable' in analysis_df.columns:
    
    table3_models = []
    
    # Prepare data
    reg_cols_t3 = [target, 'fcc_reportable'] + available_controls_base + ['immediate_disclosure']
    reg_df_t3 = analysis_df[reg_cols_t3].copy()
    
    # Convert to numeric FIRST
    for col in reg_df_t3.columns:
        reg_df_t3[col] = pd.to_numeric(reg_df_t3[col], errors='coerce')
    
    reg_df_t3 = reg_df_t3.dropna()
    
    # Extract as numpy arrays with explicit float64
    y3 = reg_df_t3[target].values.astype(np.float64)
    
    # Model 1: FCC + base controls
    X3_1_data = reg_df_t3[['fcc_reportable'] + available_controls_base].values.astype(np.float64)
    X3_1 = sm.add_constant(X3_1_data)
    model3_1 = sm.OLS(y3, X3_1).fit(cov_type='HC3')
    table3_models.append(model3_1)
    print(f"  ✓ Model 1: FCC + base controls, R² = {model3_1.rsquared:.4f}")
    
    # Model 2: FCC + immediate disclosure
    X3_2_data = reg_df_t3[['fcc_reportable', 'immediate_disclosure'] + available_controls_base].values.astype(np.float64)
    X3_2 = sm.add_constant(X3_2_data)
    model3_2 = sm.OLS(y3, X3_2).fit(cov_type='HC3')
    table3_models.append(model3_2)
    print(f"  ✓ Model 2: FCC + timing, R² = {model3_2.rsquared:.4f}")
    
    # Model 3: Interaction (FCC × Immediate)
    fcc_array = reg_df_t3['fcc_reportable'].values.astype(np.float64)
    immediate_array = reg_df_t3['immediate_disclosure'].values.astype(np.float64)
    interaction = fcc_array * immediate_array
    
    X3_3_data = np.column_stack([
        fcc_array,
        immediate_array,
        interaction,
        reg_df_t3[available_controls_base].values.astype(np.float64)
    ])
    X3_3 = sm.add_constant(X3_3_data)
    model3_3 = sm.OLS(y3, X3_3).fit(cov_type='HC3')
    table3_models.append(model3_3)
    print(f"  ✓ Model 3: FCC × Immediate interaction, R² = {model3_3.rsquared:.4f}")
    
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
    with open(OUTPUT_DIR / 'TABLE3_fcc_regulation.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("TABLE 3: FCC REGULATION EFFECTS (H2)\n")
        f.write("Dependent Variable: 30-Day Cumulative Abnormal Returns (CAR)\n")
        f.write("=" * 100 + "\n\n")
        f.write(str(table3_summary))
        f.write("\n\n")
        f.write("Notes: FCC-regulated firms subject to mandatory 7-day disclosure.\n")
        f.write("Heteroskedasticity-robust standard errors (HC3). *** p<0.01, ** p<0.05, * p<0.10\n")
        f.write("=" * 100 + "\n")
    
    print(f"  ✓ Saved: TABLE3_fcc_regulation.txt")

else:
    print(f"  ⚠ FCC variable not found, skipping Table 3")

# ============================================================================
# TABLE 4: PRIOR BREACH EFFECTS (H3: REPUTATION)
# ============================================================================

print(f"\n[Step 5/6] Creating Table 4: Prior Breach Effects (H3)...")

if 'prior_breaches_total' in analysis_df.columns:
    
    table4_models = []
    
    # Prepare data
    reg_cols_t4 = [target, 'immediate_disclosure', 'prior_breaches_total', 
                   'prior_breaches_1yr', 'is_repeat_offender'] + available_controls_extended
    reg_cols_t4 = [c for c in reg_cols_t4 if c in analysis_df.columns]
    reg_df_t4 = analysis_df[reg_cols_t4].copy()
    
    # Convert to numeric
    for col in reg_df_t4.columns:
        reg_df_t4[col] = pd.to_numeric(reg_df_t4[col], errors='coerce')
    
    reg_df_t4 = reg_df_t4.dropna()
    
    y4 = reg_df_t4[target]
    
    # Model 1: Total prior breaches
    X4_1 = sm.add_constant(reg_df_t4[['immediate_disclosure', 'prior_breaches_total'] + available_controls_base])
    model4_1 = sm.OLS(y4, X4_1).fit(cov_type='HC3')
    table4_models.append(model4_1)
    print(f"  ✓ Model 1: Prior breaches total, R² = {model4_1.rsquared:.4f}")
    
    # Model 2: 1-year prior breaches
    if 'prior_breaches_1yr' in reg_df_t4.columns:
        X4_2 = sm.add_constant(reg_df_t4[['immediate_disclosure', 'prior_breaches_1yr'] + available_controls_base])
        model4_2 = sm.OLS(y4, X4_2).fit(cov_type='HC3')
        table4_models.append(model4_2)
        print(f"  ✓ Model 2: Prior breaches 1yr, R² = {model4_2.rsquared:.4f}")
    
    # Model 3: Repeat offender flag
    if 'is_repeat_offender' in reg_df_t4.columns:
        X4_3 = sm.add_constant(reg_df_t4[['immediate_disclosure', 'is_repeat_offender'] + available_controls_base])
        model4_3 = sm.OLS(y4, X4_3).fit(cov_type='HC3')
        table4_models.append(model4_3)
        print(f"  ✓ Model 3: Repeat offender, R² = {model4_3.rsquared:.4f}")
    
    # Create table
    table4_summary = summary_col(
        table4_models,
        stars=True,
        float_format='%.4f',
        model_names=[f'Model {i+1}' for i in range(len(table4_models))],
        info_dict={
            'N': lambda x: f"{int(x.nobs):,}",
            'R²': lambda x: f"{x.rsquared:.4f}",
            'Adj. R²': lambda x: f"{x.rsquared_adj:.4f}"
        }
    )
    
    # Save Table 4
    with open(OUTPUT_DIR / 'TABLE4_prior_breaches.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("TABLE 4: PRIOR BREACH HISTORY AND MARKET REACTIONS (H3)\n")
        f.write("Dependent Variable: 30-Day Cumulative Abnormal Returns (CAR)\n")
        f.write("=" * 100 + "\n\n")
        f.write(str(table4_summary))
        f.write("\n\n")
        f.write("Notes: Tests reputation effects. Heteroskedasticity-robust standard errors (HC3).\n")
        f.write("*** p<0.01, ** p<0.05, * p<0.10\n")
        f.write("=" * 100 + "\n")
    
    print(f"  ✓ Saved: TABLE4_prior_breaches.txt")

else:
    print(f"  ⚠ Prior breach variables not found, skipping Table 4")

# ============================================================================
# TABLE 5: HETEROGENEITY (H4: BREACH SEVERITY)
# ============================================================================

print(f"\n[Step 6/6] Creating Table 5: Breach Severity (H4)...")

if 'health_breach' in analysis_df.columns:
    
    table5_models = []
    
    # Prepare data
    reg_cols_t5 = [target, 'immediate_disclosure', 'health_breach', 
                   'financial_breach', 'severity_score'] + available_controls_base
    reg_cols_t5 = [c for c in reg_cols_t5 if c in analysis_df.columns]
    reg_df_t5 = analysis_df[reg_cols_t5].copy()
    
    # Convert to numeric
    for col in reg_df_t5.columns:
        reg_df_t5[col] = pd.to_numeric(reg_df_t5[col], errors='coerce')
    
    reg_df_t5 = reg_df_t5.dropna()
    
    y5 = reg_df_t5[target]
    
    # Model 1: Health breach
    X5_1 = sm.add_constant(reg_df_t5[['immediate_disclosure', 'health_breach'] + available_controls_base])
    model5_1 = sm.OLS(y5, X5_1).fit(cov_type='HC3')
    table5_models.append(model5_1)
    print(f"  ✓ Model 1: Health breach, R² = {model5_1.rsquared:.4f}")
    
    # Model 2: Financial breach
    if 'financial_breach' in reg_df_t5.columns:
        X5_2 = sm.add_constant(reg_df_t5[['immediate_disclosure', 'financial_breach'] + available_controls_base])
        model5_2 = sm.OLS(y5, X5_2).fit(cov_type='HC3')
        table5_models.append(model5_2)
        print(f"  ✓ Model 2: Financial breach, R² = {model5_2.rsquared:.4f}")
    
    # Model 3: Severity score
    if 'severity_score' in reg_df_t5.columns:
        X5_3 = sm.add_constant(reg_df_t5[['immediate_disclosure', 'severity_score'] + available_controls_base])
        model5_3 = sm.OLS(y5, X5_3).fit(cov_type='HC3')
        table5_models.append(model5_3)
        print(f"  ✓ Model 3: Severity score, R² = {model5_3.rsquared:.4f}")
    
    # Model 4: All breach types
    if 'financial_breach' in reg_df_t5.columns:
        X5_4 = sm.add_constant(reg_df_t5[['immediate_disclosure', 'health_breach', 'financial_breach'] + available_controls_base])
        model5_4 = sm.OLS(y5, X5_4).fit(cov_type='HC3')
        table5_models.append(model5_4)
        print(f"  ✓ Model 4: All breach types, R² = {model5_4.rsquared:.4f}")
    
    # Create table
    table5_summary = summary_col(
        table5_models,
        stars=True,
        float_format='%.4f',
        model_names=[f'Model {i+1}' for i in range(len(table5_models))],
        info_dict={
            'N': lambda x: f"{int(x.nobs):,}",
            'R²': lambda x: f"{x.rsquared:.4f}",
            'Adj. R²': lambda x: f"{x.rsquared_adj:.4f}"
        }
    )
    
    # Save Table 5
    with open(OUTPUT_DIR / 'TABLE5_breach_severity.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("TABLE 5: HETEROGENEOUS EFFECTS BY BREACH SEVERITY (H4)\n")
        f.write("Dependent Variable: 30-Day Cumulative Abnormal Returns (CAR)\n")
        f.write("=" * 100 + "\n\n")
        f.write(str(table5_summary))
        f.write("\n\n")
        f.write("Notes: Tests heterogeneity across breach types. HC3 standard errors.\n")
        f.write("*** p<0.01, ** p<0.05, * p<0.10\n")
        f.write("=" * 100 + "\n")
    
    print(f"  ✓ Saved: TABLE5_breach_severity.txt")

else:
    print(f"  ⚠ Breach severity variables not found, skipping Table 5")

# ============================================================================
# SUMMARY
# ============================================================================

print(f"\n" + "=" * 80)
print("✓ ESSAY 2 REGRESSION ANALYSIS COMPLETE")
print("=" * 80)

print(f"\nTables created in {OUTPUT_DIR}/:")
print(f"  • TABLE2_baseline_disclosure.txt (H1: Immediate disclosure)")
if 'fcc_reportable' in analysis_df.columns:
    print(f"  • TABLE3_fcc_regulation.txt (H2: FCC regulation)")
if 'prior_breaches_total' in analysis_df.columns:
    print(f"  • TABLE4_prior_breaches.txt (H3: Reputation effects)")
if 'health_breach' in analysis_df.columns:
    print(f"  • TABLE5_breach_severity.txt (H4: Heterogeneity)")

print(f"\n📊 Main regression tables ready for Essay 2!")
print("=" * 80)