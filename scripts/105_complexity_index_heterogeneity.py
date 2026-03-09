"""
COMPLEXITY INDEX HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION
New Mechanism: Breach Technical & Dimensional Complexity

Analyzes whether breach complexity (severity, CVE volume, breach type diversity)
moderates the FCC volatility effect (Essay 2).

Hypothesis: Complex breaches (multiple CVEs, varied breach types, high severity)
require longer investigation and disclosure complexity, so FCC time pressure
constraints create larger market volatility increases.

Mechanism: FCC mandates 7-day disclosure -> complex breach requires
multi-dimensional investigation -> incomplete disclosure under time pressure
-> markets increase uncertainty -> larger FCC volatility effect for complex breaches.

This tests a NEW unified complexity mechanism distinct from:
- Governance quality (Script 98)
- CVSS technical complexity (Script 99)
- Media coverage (Script 101)
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path
from datetime import datetime

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

print("=" * 90)
print("COMPLEXITY INDEX HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/5] Loading datasets...")

# Load main dissertation dataset
print("  Loading main dissertation dataset...")
main_df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"    [OK] {len(main_df):,} breach observations")

print(f"    Available complexity metrics:")
print(f"      - severity_score: {main_df['severity_score'].notna().sum():,} observations")
print(f"      - total_cves: {main_df['total_cves'].notna().sum():,} observations")
print(f"      - num_breach_types: {main_df['num_breach_types'].notna().sum():,} observations")

# ============================================================================
# SECTION 2: CREATE COMPLEXITY INDEX
# ============================================================================

print("\n[2/5] Creating unified complexity index...")

df = main_df.copy()

# Variable engineering: Create percentile-based components for comparability
print("  Engineering complexity components...")

# Component 1: Severity percentile
df['severity_pct'] = df['severity_score'].rank(pct=True) * 100
print(f"    Severity percentile: {df['severity_pct'].notna().sum():,} observations")

# Component 2: CVE volume percentile
df['cves_pct'] = df['total_cves'].rank(pct=True) * 100
print(f"    CVE volume percentile: {df['cves_pct'].notna().sum():,} observations")

# Component 3: Breach type diversity percentile
df['types_pct'] = df['num_breach_types'].rank(pct=True) * 100
print(f"    Breach type diversity percentile: {df['types_pct'].notna().sum():,} observations")

# Create unified complexity index (average of three percentiles)
df['complexity_index'] = (df['severity_pct'] + df['cves_pct'] + df['types_pct']) / 3

# Create binary high complexity indicator (top quartile)
df['high_complexity_index'] = (df['complexity_index'] >= df['complexity_index'].quantile(0.75)).astype(int)

print(f"\n  Complexity index summary:")
print(f"    Mean complexity index: {df['complexity_index'].mean():.2f} percentile")
print(f"    Median complexity index: {df['complexity_index'].median():.2f} percentile")
print(f"    High complexity breaches (top quartile): {df['high_complexity_index'].sum():,}")

print(f"\n  Complexity components correlation:")
complexity_cols = ['severity_pct', 'cves_pct', 'types_pct']
corr_matrix = df[complexity_cols].corr().round(3)
print(corr_matrix)

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[3/5] Descriptive statistics...")

print("\n  VOLATILITY by complexity index:")
complexity_groups = df[df['volatility_change'].notna()].groupby('high_complexity_index')['volatility_change'].describe().round(4)
print(complexity_groups)

print("\n  VOLATILITY by FCC and complexity index:")
fcc_complexity = df[df['volatility_change'].notna()].groupby(
    ['fcc_reportable', 'high_complexity_index']
)['volatility_change'].agg(['count', 'mean', 'median', 'std']).round(4)
print(fcc_complexity)

# Highlight the interaction
print("\n  FCC effect by complexity:")
non_fcc_low = df[(df['fcc_reportable']==0) & (df['high_complexity_index']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_low = df[(df['fcc_reportable']==1) & (df['high_complexity_index']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
non_fcc_high = df[(df['fcc_reportable']==0) & (df['high_complexity_index']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_high = df[(df['fcc_reportable']==1) & (df['high_complexity_index']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()

print(f"    Non-FCC + Low complexity: {non_fcc_low:.4f}pp")
print(f"    FCC + Low complexity: {fcc_low:.4f}pp")
print(f"    FCC effect for low-complexity: {fcc_low - non_fcc_low:.4f}pp (DIFFERENCE)")
print(f"\n    Non-FCC + High complexity: {non_fcc_high:.4f}pp")
print(f"    FCC + High complexity: {fcc_high:.4f}pp")
print(f"    FCC effect for high-complexity: {fcc_high - non_fcc_high:.4f}pp (DIFFERENCE)")

# ============================================================================
# SECTION 4: HETEROGENEITY ANALYSIS - OLS REGRESSIONS
# ============================================================================

print("\n[4/5] Running heterogeneity models...")

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
except ImportError:
    print("  [FAIL] Required packages not found. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'statsmodels'])
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

# Prepare data for regression
reg_data = df[
    (df['volatility_change'].notna()) &
    (df['severity_score'].notna()) &
    (df['total_cves'].notna()) &
    (df['num_breach_types'].notna())
].copy()

# Volatility is already in percentage point form
reg_data['volatility_outcome'] = reg_data['volatility_change']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['high_complexity'] = reg_data['high_complexity_index'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

print(f"\n  Analysis sample: {len(reg_data):,} breaches with complete complexity data")

# Model 1: Baseline FCC effect (Essay 2)
print("\n  MODEL 1: Baseline FCC Effect (Essay 2)")
model1 = ols('volatility_outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m1 = model1.params['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.params['fcc']
pval_fcc_m1 = model1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.pvalues['fcc']

print(f"    FCC Effect: {coef_fcc_m1:.4f}pp (p={pval_fcc_m1:.4f})")
print(f"    R-squared = {model1.rsquared:.4f}")
print(f"    N = {len(model1.resid):,}")

# Model 2: Add complexity main effect
print("\n  MODEL 2: FCC Effect + Complexity Main Effect")
model2 = ols('volatility_outcome ~ fcc + high_complexity + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_complex = model2.params['high_complexity[T.1]'] if 'high_complexity[T.1]' in model2.params.index else model2.params['high_complexity']
pval_complex = model2.pvalues['high_complexity[T.1]'] if 'high_complexity[T.1]' in model2.params.index else model2.pvalues['high_complexity']

print(f"    FCC Effect: {coef_fcc_m2:.4f}pp (p={pval_fcc_m2:.4f})")
print(f"    Complexity Effect: {coef_complex:.4f}pp (p={pval_complex:.4f})")
print(f"    R-squared = {model2.rsquared:.4f}")

# Model 3: FCC x Complexity Interaction (KEY TEST)
print("\n  MODEL 3: FCC x COMPLEXITY INTERACTION (Key Test)")
model3 = ols('volatility_outcome ~ fcc * high_complexity + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_complex_m3 = model3.params['high_complexity[T.1]'] if 'high_complexity[T.1]' in model3.params.index else model3.params['high_complexity']
pval_complex_m3 = model3.pvalues['high_complexity[T.1]'] if 'high_complexity[T.1]' in model3.params.index else model3.pvalues['high_complexity']

interact_key = 'fcc[T.1]:high_complexity[T.1]' if 'fcc[T.1]:high_complexity[T.1]' in model3.params.index else 'fcc:high_complexity'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}pp (p={pval_fcc_m3:.4f})")
print(f"    Complexity Main Effect: {coef_complex_m3:.4f}pp (p={pval_complex_m3:.4f})")
print(f"    FCC x Complexity: {coef_interact:.4f}pp (p={pval_interact:.4f})")
print(f"    R-squared = {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for low-complexity breaches: {coef_fcc_m3:.4f}pp")
    print(f"    - FCC effect for high-complexity breaches: {coef_fcc_m3 + coef_interact:.4f}pp")
    print(f"    - Difference (interaction): {coef_interact:.4f}pp")

    if coef_interact > 0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC VOLATILITY INCREASE IS AMPLIFIED for complex breaches")
        print(f"    This supports the COMPLEXITY INDEX MECHANISM")
    elif coef_interact < -0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC VOLATILITY INCREASE IS REDUCED for complex breaches")
        print(f"    Alternative: Complex breaches may have inherent uncertainty floor")
    else:
        print(f"\n    FINDING: NO SIGNIFICANT INTERACTION")
        print(f"    Complexity does not moderate FCC volatility effect")

# ============================================================================
# SECTION 5: SAVE RESULTS AND GENERATE TABLES
# ============================================================================

print("\n[5/5] Saving results and generating publication tables...")

# Create regression results table
results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Complexity', 'Model 3: FCC x Complexity'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Complexity Coefficient': [
        'N/A',
        f"{coef_complex:.4f}" if pval_complex > 0.05 else f"{coef_complex:.4f}*",
        f"{coef_complex_m3:.4f}" if pval_complex_m3 > 0.05 else f"{coef_complex_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv', index=False)
print(f"  [OK] Saved regression results: outputs/tables/TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv")

print("\n" + "=" * 90)
print("ESSAY 2 VOLATILITY: COMPLEXITY INDEX HETEROGENEITY ANALYSIS COMPLETE")
print("=" * 90)

print("\nKey Findings:")
print(f"  - Sample with complexity data: {len(reg_data):,} breaches")
print(f"  - Baseline FCC volatility effect: {coef_fcc_m1:.4f}pp")
print(f"  - Complexity main effect: {coef_complex:.4f}pp")
print(f"  - FCC x Complexity interaction: {coef_interact:.4f}pp (p={pval_interact:.4f})")

print("\nInterpretation:")
if coef_interact > 0.1 and pval_interact < 0.05:
    print("  MECHANISM CONFIRMED: Complexity amplifies FCC volatility increase")
    print("  Market mechanism: Complex breaches (high severity, multiple CVEs, mixed types)")
    print("  require time to investigate & disclose, but FCC deadline forces incomplete disclosure")
elif coef_interact < -0.1 and pval_interact < 0.05:
    print("  ALTERNATIVE: FCC volatility reduced for complex breaches")
    print("  Market may already expect high uncertainty for inherently complex breaches")
else:
    print("  FINDING: Complexity does not significantly moderate FCC volatility effect")
    print("  FCC impact operates independently of breach complexity")

print("\n[OK] Essay 2 Mechanism 4 (Complexity Index) analysis complete!")
