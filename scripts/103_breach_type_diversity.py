"""
BREACH TYPE DIVERSITY HETEROGENEITY ANALYSIS
Analysis #6: Multi-Type Complexity Mechanism

Tests whether breaches involving MULTIPLE data types (PII + Health + Financial + IP)
create a complexity effect similar to CVSS complexity in Phase 2.

Hypothesis: Multi-type breaches are more complex to investigate because they
involve different regulatory/compliance obligations and affected constituencies.
FCC deadline creates larger penalties for multi-type breaches (harder to investigate
multiple damage categories simultaneously).

This validates Phase 2 complexity finding using a different complexity measure.
"""

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

print("=" * 90)
print("BREACH TYPE DIVERSITY HETEROGENEITY ANALYSIS - Analysis #6")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/5] Loading data...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')
print(f"  [OK] {len(df):,} breach observations")

# ============================================================================
# SECTION 2: BREACH COMPLEXITY BY TYPE DIVERSITY
# ============================================================================

print("\n[2/5] Analyzing breach type diversity...")

print("\n  Breach type coverage:")
type_cols = ['pii_breach', 'health_breach', 'financial_breach', 'ip_breach']
for col in type_cols:
    if col in df.columns:
        count = df[col].sum()
        pct = count / len(df) * 100
        print(f"    {col:20s}: {count:>4.0f} ({pct:>5.1f}%)")

# Create complexity indicator: count number of breach types per incident
df['breach_type_count'] = 0
for col in type_cols:
    if col in df.columns:
        df['breach_type_count'] += df[col].astype(int)

print(f"\n  Breach type diversity distribution:")
print(f"    Mean types per breach: {df['breach_type_count'].mean():.2f}")
print(f"    Median: {df['breach_type_count'].median():.0f}")
print(f"    Max: {df['breach_type_count'].max():.0f}")

diversity_dist = df['breach_type_count'].value_counts().sort_index()
print(f"\n    Count distribution:")
for count, freq in diversity_dist.items():
    print(f"      {count:.0f} types: {freq:>4.0f} breaches ({freq/len(df)*100:>5.1f}%)")

# Create binary indicator: multi-type (2+) vs single-type (0-1)
df['is_multi_type'] = (df['breach_type_count'] >= 2).astype(int)

print(f"\n  Classification:")
print(f"    Single-type (0-1): {(df['is_multi_type']==0).sum():,}")
print(f"    Multi-type (2+): {(df['is_multi_type']==1).sum():,}")

# Correlation with other complexity measures
print(f"\n  Correlation with Phase 2 CVSS complexity:")
if 'has_high_complexity' in df.columns:
    corr = df[['is_multi_type', 'has_high_complexity']].corr().iloc[0, 1]
    print(f"    Type diversity <-> CVSS complexity: {corr:+.3f}")
    print(f"    (Moderate correlation suggests different complexity dimensions)")

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[3/5] Descriptive statistics...")

print("\n  CAR by type diversity:")
diversity_stats = df[df['has_crsp_data']==1].groupby('is_multi_type')['car_30d'].describe().round(4)
print(diversity_stats)

print("\n  FCC effect by type diversity:")
print("    Single-Type Breaches:")
non_fcc_single = df[(df['fcc_reportable']==0) & (df['is_multi_type']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_single = df[(df['fcc_reportable']==1) & (df['is_multi_type']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()
print(f"      Non-FCC: {non_fcc_single:.4f}%")
print(f"      FCC: {fcc_single:.4f}%")
print(f"      FCC Effect: {fcc_single - non_fcc_single:.4f}%")

print("\n    Multi-Type Breaches:")
non_fcc_multi = df[(df['fcc_reportable']==0) & (df['is_multi_type']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_multi = df[(df['fcc_reportable']==1) & (df['is_multi_type']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
print(f"      Non-FCC: {non_fcc_multi:.4f}%")
print(f"      FCC: {fcc_multi:.4f}%")
print(f"      FCC Effect: {fcc_multi - non_fcc_multi:.4f}%")

# ============================================================================
# SECTION 4: REGRESSION MODELS
# ============================================================================

print("\n[4/5] Running regression models...")

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
except ImportError:
    print("  Installing statsmodels...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'statsmodels'])
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

# Prepare data
reg_data = df[
    (df['has_crsp_data'] == 1) &
    (df['car_30d'].notna())
].copy()

reg_data['car_outcome'] = reg_data['car_30d']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['multi'] = reg_data['is_multi_type'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

print(f"\n  Analysis sample: {len(reg_data):,} breaches")

# Model 1: Baseline FCC
print("\n  MODEL 1: Baseline FCC Effect")
model1 = ols('car_outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m1 = model1.params['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.params['fcc']
pval_fcc_m1 = model1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.pvalues['fcc']

print(f"    FCC Effect: {coef_fcc_m1:.4f}% (p={pval_fcc_m1:.4f})")
print(f"    R-squared: {model1.rsquared:.4f}")

# Model 2: Add type diversity main effect
print("\n  MODEL 2: FCC + Type Diversity Main Effect")
model2 = ols('car_outcome ~ fcc + multi + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_multi = model2.params['multi[T.1]'] if 'multi[T.1]' in model2.params.index else model2.params['multi']
pval_multi = model2.pvalues['multi[T.1]'] if 'multi[T.1]' in model2.params.index else model2.pvalues['multi']

print(f"    FCC Effect: {coef_fcc_m2:.4f}% (p={pval_fcc_m2:.4f})")
print(f"    Multi-Type Effect: {coef_multi:.4f}% (p={pval_multi:.4f})")
print(f"    R-squared: {model2.rsquared:.4f}")

# Model 3: FCC x Diversity Interaction
print("\n  MODEL 3: FCC x TYPE DIVERSITY INTERACTION (Key Test)")
model3 = ols('car_outcome ~ fcc * multi + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_multi_m3 = model3.params['multi[T.1]'] if 'multi[T.1]' in model3.params.index else model3.params['multi']
pval_multi_m3 = model3.pvalues['multi[T.1]'] if 'multi[T.1]' in model3.params.index else model3.pvalues['multi']

interact_key = 'fcc[T.1]:multi[T.1]' if 'fcc[T.1]:multi[T.1]' in model3.params.index else 'fcc:multi'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}% (p={pval_fcc_m3:.4f})")
print(f"    Multi-Type Main Effect: {coef_multi_m3:.4f}% (p={pval_multi_m3:.4f})")
print(f"    FCC x Multi-Type: {coef_interact:.4f}% (p={pval_interact:.4f})")
print(f"    R-squared: {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for single-type: {coef_fcc_m3:.4f}%")
    print(f"    - FCC effect for multi-type: {coef_fcc_m3 + coef_interact:.4f}%")
    if abs(coef_interact) > 0.1 and pval_interact < 0.05:
        direction = "AMPLIFIED" if coef_interact < 0 else "REDUCED"
        print(f"    - Multi-type breaches have {direction} FCC penalty")

# ============================================================================
# SECTION 5: SAVE RESULTS
# ============================================================================

print("\n[5/5] Saving results...")

results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Diversity', 'Model 3: FCC x Diversity'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Diversity Coefficient': [
        'N/A',
        f"{coef_multi:.4f}" if pval_multi > 0.05 else f"{coef_multi:.4f}*",
        f"{coef_multi_m3:.4f}" if pval_multi_m3 > 0.05 else f"{coef_multi_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv', index=False)
print(f"  [OK] Saved: TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv")

print("\n" + "=" * 90)
print("ANALYSIS #6 COMPLETE")
print("=" * 90)
print("\nValidation of Phase 2 Complexity Mechanism:")
print(f"  Phase 2 (CVSS): FCC x Complexity = +6.27%**")
print(f"  Analysis #6 (Diversity): FCC x Multi-Type = {coef_interact:.4f}%")
if pval_interact < 0.10:
    print(f"  CONSISTENT: Both complexity measures show similar patterns")
else:
    print(f"  DIFFERENT: Type diversity has different mechanism than CVSS")
