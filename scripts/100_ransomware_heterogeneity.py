"""
RANSOMWARE ATTACK VECTOR HETEROGENEITY ANALYSIS
Analysis #3: Breach Type & Attack Vector Effects

Tests whether FCC penalty differs by attack vector (ransomware vs other).

Hypothesis: Ransomware requires careful investigation of encryption/decryption methods,
so FCC 7-day deadline creates larger penalties than for non-ransomware breaches.

Alternatively: Ransomware is already expected to be complex, so markets discount expectations
(similar to Phase 2 finding on CVSS complexity).
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

print("=" * 90)
print("RANSOMWARE ATTACK VECTOR HETEROGENEITY ANALYSIS - Analysis #3")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/5] Loading data...")

# Load latest enriched dataset (with CVSS data from Phase 2)
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')
print(f"  [OK] {len(df):,} breach observations")

# ============================================================================
# SECTION 2: RANSOMWARE CLASSIFICATION
# ============================================================================

print("\n[2/5] Analyzing attack vectors...")

# Get all attack vector indicators
attack_vectors = ['ransomware', 'insider_threat', 'phishing', 'malware', 'nation_state', 'ip_breach']

print("\n  Attack vector distribution:")
for vector in attack_vectors:
    if vector in df.columns:
        count = df[vector].sum() if df[vector].dtype in ['int64', 'float64'] else df[vector].notna().sum()
        pct = count / len(df) * 100
        print(f"    {vector:20s}: {count:>5.0f} ({pct:>5.1f}%)")

# Create binary indicator for ransomware vs others
df['is_ransomware'] = df['ransomware'].astype(int)
df['is_insider'] = df['insider_threat'].astype(int)

print(f"\n  Mutual exclusivity check:")
both = ((df['is_ransomware'] == 1) & (df['is_insider'] == 1)).sum()
print(f"    Breaches with both ransomware + insider: {both}")

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[3/5] Descriptive statistics...")

print("\n  CAR by attack vector:")
for vector in ['is_ransomware', 'is_insider']:
    if vector in df.columns:
        stats = df[df['has_crsp_data']==1].groupby(vector)['car_30d'].describe().round(4)
        print(f"\n  {vector}:")
        print(stats)

print("\n  FCC effect by attack vector:")
print("    Ransomware:")
non_fcc_ransom = df[(df['fcc_reportable']==0) & (df['is_ransomware']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_ransom = df[(df['fcc_reportable']==1) & (df['is_ransomware']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
print(f"      Non-FCC: {non_fcc_ransom:.4f}%")
print(f"      FCC: {fcc_ransom:.4f}%")
print(f"      FCC Effect: {fcc_ransom - non_fcc_ransom:.4f}%")

print("\n    Insider Threat:")
non_fcc_insider = df[(df['fcc_reportable']==0) & (df['is_insider']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_insider = df[(df['fcc_reportable']==1) & (df['is_insider']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
print(f"      Non-FCC: {non_fcc_insider:.4f}%")
print(f"      FCC: {fcc_insider:.4f}%")
print(f"      FCC Effect: {fcc_insider - non_fcc_insider:.4f}%")

print("\n    Other Breaches (Non-Ransomware, Non-Insider):")
non_fcc_other = df[(df['fcc_reportable']==0) & (df['is_ransomware']==0) & (df['is_insider']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_other = df[(df['fcc_reportable']==1) & (df['is_ransomware']==0) & (df['is_insider']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()
print(f"      Non-FCC: {non_fcc_other:.4f}%")
print(f"      FCC: {fcc_other:.4f}%")
print(f"      FCC Effect: {fcc_other - non_fcc_other:.4f}%")

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
reg_data['ransom'] = reg_data['is_ransomware'].astype(int)
reg_data['insider'] = reg_data['is_insider'].astype(int)
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

# Model 2: Add ransomware main effect
print("\n  MODEL 2: FCC + Ransomware Main Effect")
model2 = ols('car_outcome ~ fcc + ransom + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_ransom = model2.params['ransom[T.1]'] if 'ransom[T.1]' in model2.params.index else model2.params['ransom']
pval_ransom = model2.pvalues['ransom[T.1]'] if 'ransom[T.1]' in model2.params.index else model2.pvalues['ransom']

print(f"    FCC Effect: {coef_fcc_m2:.4f}% (p={pval_fcc_m2:.4f})")
print(f"    Ransomware Effect: {coef_ransom:.4f}% (p={pval_ransom:.4f})")
print(f"    R-squared: {model2.rsquared:.4f}")

# Model 3: FCC x Ransomware Interaction
print("\n  MODEL 3: FCC x RANSOMWARE INTERACTION (Key Test)")
model3 = ols('car_outcome ~ fcc * ransom + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_ransom_m3 = model3.params['ransom[T.1]'] if 'ransom[T.1]' in model3.params.index else model3.params['ransom']
pval_ransom_m3 = model3.pvalues['ransom[T.1]'] if 'ransom[T.1]' in model3.params.index else model3.pvalues['ransom']

interact_key = 'fcc[T.1]:ransom[T.1]' if 'fcc[T.1]:ransom[T.1]' in model3.params.index else 'fcc:ransom'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}% (p={pval_fcc_m3:.4f})")
print(f"    Ransomware Main Effect: {coef_ransom_m3:.4f}% (p={pval_ransom_m3:.4f})")
print(f"    FCC x Ransomware: {coef_interact:.4f}% (p={pval_interact:.4f})")
print(f"    R-squared: {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for non-ransomware: {coef_fcc_m3:.4f}%")
    print(f"    - FCC effect for ransomware: {coef_fcc_m3 + coef_interact:.4f}%")
    if abs(coef_interact) > 0.1 and pval_interact < 0.05:
        direction = "AMPLIFIED" if coef_interact < 0 else "REDUCED"
        print(f"    - Ransomware FCC penalty is {direction}")

# ============================================================================
# SECTION 5: SAVE RESULTS
# ============================================================================

print("\n[5/5] Saving results...")

results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Ransomware', 'Model 3: FCC x Ransomware'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Ransomware Coefficient': [
        'N/A',
        f"{coef_ransom:.4f}" if pval_ransom > 0.05 else f"{coef_ransom:.4f}*",
        f"{coef_ransom_m3:.4f}" if pval_ransom_m3 > 0.05 else f"{coef_ransom_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv', index=False)
print(f"  [OK] Saved: TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv")

print("\n" + "=" * 90)
print("ANALYSIS #3 COMPLETE")
print("=" * 90)
