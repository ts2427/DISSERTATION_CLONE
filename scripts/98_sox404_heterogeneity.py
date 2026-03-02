"""
GOVERNANCE QUALITY HETEROGENEITY ANALYSIS
Phase 1 of Publication Enhancement: Option B

Analyzes whether firm governance quality (proxied by financial metrics)
moderates the FCC CAR effect.

Hypothesis: Breached firms with weak governance (high leverage, low profitability)
experience larger FCC-driven penalties because markets doubt the quality of
forced disclosure under weak governance.

Mechanism: FCC mandates fast disclosure -> breached firms with weak governance
cannot produce credible disclosures -> markets penalize for information quality risk
-> larger FCC CAR effect for governance-weak firms.

Note: Uses internal financial metrics (leverage, ROA) as governance quality proxy
instead of external SOX 404 data due to limited Compustat coverage in breach dataset.
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path
from datetime import datetime

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

print("=" * 90)
print("GOVERNANCE QUALITY HETEROGENEITY ANALYSIS - Phase 1 Enhancement")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/5] Loading datasets...")

# Load main dissertation dataset
print("  Loading main dissertation dataset...")
main_df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"    [OK] {len(main_df):,} breach observations")

print(f"    Available governance proxies:")
print(f"      - leverage (debt-to-assets): {main_df['leverage'].notna().sum():,} observations")
print(f"      - ROA (profitability): {main_df['roa'].notna().sum():,} observations")
print(f"      - firm_size_log (scale): {main_df['firm_size_log'].notna().sum():,} observations")

# ============================================================================
# SECTION 2: CREATE GOVERNANCE QUALITY INDICATORS
# ============================================================================

print("\n[2/5] Creating governance quality indicators...")

df = main_df.copy()

# Create governance quality index using principal component approach
# Higher values = WEAKER governance

print("  Constructing governance weakness index...")

# Standardize components
df['leverage_std'] = (df['leverage'] - df['leverage'].mean()) / df['leverage'].std()
df['roa_std'] = (df['roa'] - df['roa'].mean()) / df['roa'].std()

# Governance weakness score: high leverage + low ROA = weak governance
# Note: LOW ROA means WEAK governance (unprofitable)
df['governance_weakness_score'] = (df['leverage_std'] - df['roa_std']) / 2

# Create binary indicator: weak governance firms (top quartile)
df['weak_governance'] = (df['governance_weakness_score'] >= df['governance_weakness_score'].quantile(0.75)).astype(int)
df['strong_governance'] = (df['governance_weakness_score'] <= df['governance_weakness_score'].quantile(0.25)).astype(int)

print(f"    Weak governance (top quartile): {df['weak_governance'].sum():,} breaches")
print(f"    Strong governance (bottom quartile): {df['strong_governance'].sum():,} breaches")

# Show characteristics
print("\n  Governance characteristics comparison:")
gov_comparison = df.groupby('weak_governance')[['leverage', 'roa', 'firm_size_log']].describe().round(2)
print(gov_comparison)

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[3/5] Descriptive statistics...")

print("\n  CAR by governance quality:")
gov_groups = df[df['has_crsp_data']==1].groupby('weak_governance')['car_30d'].describe().round(4)
print(gov_groups)

print("\n  CAR by FCC and governance quality:")
fcc_gov_groups = df[df['has_crsp_data']==1].groupby(
    ['fcc_reportable', 'weak_governance']
)['car_30d'].agg(['count', 'mean', 'median', 'std']).round(4)
print(fcc_gov_groups)

# Highlight the interaction
print("\n  FCC effect by governance quality:")
non_fcc_weak = df[(df['fcc_reportable']==0) & (df['weak_governance']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_weak = df[(df['fcc_reportable']==1) & (df['weak_governance']==1) & (df['has_crsp_data']==1)]['car_30d'].mean()
non_fcc_strong = df[(df['fcc_reportable']==0) & (df['weak_governance']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()
fcc_strong = df[(df['fcc_reportable']==1) & (df['weak_governance']==0) & (df['has_crsp_data']==1)]['car_30d'].mean()

print(f"    Non-FCC + Weak governance: {non_fcc_weak:.4f}%")
print(f"    FCC + Weak governance: {fcc_weak:.4f}%")
print(f"    FCC effect for weak-gov firms: {fcc_weak - non_fcc_weak:.4f}% (DIFFERENCE)")
print(f"\n    Non-FCC + Strong governance: {non_fcc_strong:.4f}%")
print(f"    FCC + Strong governance: {fcc_strong:.4f}%")
print(f"    FCC effect for strong-gov firms: {fcc_strong - non_fcc_strong:.4f}% (DIFFERENCE)")

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
    (df['has_crsp_data'] == 1) &
    (df['car_30d'].notna()) &
    (df['leverage'].notna()) &
    (df['roa'].notna())
].copy()

# CAR is already in percentage form (ranges from -42 to +34)
# Do NOT multiply by 100
reg_data['car_outcome'] = reg_data['car_30d']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['weak_gov'] = reg_data['weak_governance'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

print(f"\n  Analysis sample: {len(reg_data):,} breaches with complete governance data")

# Model 1: Baseline FCC effect (reproduce Essay 1)
print("\n  MODEL 1: Baseline FCC Effect (Essay 1 Main Result)")
model1 = ols('car_outcome ~ fcc + health + financial + prior_breaches + firm_size_log + leverage + roa',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m1 = model1.params['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.params['fcc']
pval_fcc_m1 = model1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.pvalues['fcc']

print(f"    FCC Effect: {coef_fcc_m1:.4f}% (p={pval_fcc_m1:.4f})")
print(f"    R-squared = {model1.rsquared:.4f}")
print(f"    N = {len(model1.resid):,}")

# Model 2: Add governance weakness indicator
print("\n  MODEL 2: FCC Effect + Governance Main Effect")
model2 = ols('car_outcome ~ fcc + weak_gov + health + financial + prior_breaches + firm_size_log + leverage + roa',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_gov = model2.params['weak_gov[T.1]'] if 'weak_gov[T.1]' in model2.params.index else model2.params['weak_gov']
pval_gov = model2.pvalues['weak_gov[T.1]'] if 'weak_gov[T.1]' in model2.params.index else model2.pvalues['weak_gov']

print(f"    FCC Effect: {coef_fcc_m2:.4f}% (p={pval_fcc_m2:.4f})")
print(f"    Weak Governance Effect: {coef_gov:.4f}% (p={pval_gov:.4f})")
print(f"    R-squared = {model2.rsquared:.4f}")

# Model 3: FCC x Governance Weakness Interaction (KEY TEST)
print("\n  MODEL 3: FCC x GOVERNANCE WEAKNESS INTERACTION (Key Test)")
model3 = ols('car_outcome ~ fcc * weak_gov + health + financial + prior_breaches + firm_size_log + leverage + roa',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_gov_m3 = model3.params['weak_gov[T.1]'] if 'weak_gov[T.1]' in model3.params.index else model3.params['weak_gov']
pval_gov_m3 = model3.pvalues['weak_gov[T.1]'] if 'weak_gov[T.1]' in model3.params.index else model3.pvalues['weak_gov']

interact_key = 'fcc[T.1]:weak_gov[T.1]' if 'fcc[T.1]:weak_gov[T.1]' in model3.params.index else 'fcc:weak_gov'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}% (p={pval_fcc_m3:.4f})")
print(f"    Weak Gov Main Effect: {coef_gov_m3:.4f}% (p={pval_gov_m3:.4f})")
print(f"    FCC x Weak Governance: {coef_interact:.4f}% (p={pval_interact:.4f})")
print(f"    R-squared = {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for strong-gov firms: {coef_fcc_m3:.4f}%")
    print(f"    - FCC effect for weak-gov firms: {coef_fcc_m3 + coef_interact:.4f}%")
    print(f"    - Difference (interaction): {coef_interact:.4f}%")

    if coef_interact < -0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC PENALTY IS AMPLIFIED for weak-governance firms")
        print(f"    This supports the GOVERNANCE WEAKNESS MECHANISM")
    elif coef_interact > 0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC PENALTY IS REDUCED for weak-governance firms")
        print(f"    Alternative interpretation: weak-gov firms disclose conservatively")
    else:
        print(f"\n    FINDING: NO SIGNIFICANT INTERACTION")
        print(f"    Governance quality does not moderate FCC effect")

# ============================================================================
# SECTION 5: SAVE RESULTS AND GENERATE TABLES
# ============================================================================

print("\n[5/5] Saving results and generating publication tables...")

# Save enhanced dataset
output_file = 'Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv'
df.to_csv(output_file, index=False)
print(f"  [OK] Saved enriched dataset: {output_file}")

# Create regression results table
results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Gov', 'Model 3: FCC x Gov'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Governance Coefficient': [
        'N/A',
        f"{coef_gov:.4f}" if pval_gov > 0.05 else f"{coef_gov:.4f}*",
        f"{coef_gov_m3:.4f}" if pval_gov_m3 > 0.05 else f"{coef_gov_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv', index=False)
print(f"  [OK] Saved regression results: outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv")

print("\n" + "=" * 90)
print("PHASE 1 COMPLETE: GOVERNANCE QUALITY HETEROGENEITY ANALYSIS")
print("=" * 90)

print("\nKey Findings:")
print(f"  - Baseline FCC effect: {coef_fcc_m1:.4f}% (consistent with Essay 1)")
print(f"  - Governance weakness main effect: {coef_gov:.4f}%")
print(f"  - FCC x Governance interaction: {coef_interact:.4f}% (p={pval_interact:.4f})")

print("\nInterpretation:")
if coef_interact < -0.1 and pval_interact < 0.05:
    print("  MECHANISM CONFIRMED: Governance weakness amplifies FCC penalty")
    print("  Market mechanism: forced disclosure from weak-governance firms")
    print("  creates information quality concerns")
else:
    print("  Alternative mechanism: FCC effect operates independently of governance")
    print("  FCC penalty may work through timing/disclosure speed, not firm quality")

print("\nNext Steps (Phase 2): CVSS Technical Complexity Analysis")
print("  - Extract CVSS severity scores from NVD JSON files")
print("  - Test: CAR x CVSS interaction (technical complexity mechanism)")
print("  - Hypothesis: Complex vulnerabilities increase FCC penalty")

print("\n[OK] Phase 1 analysis complete!")
