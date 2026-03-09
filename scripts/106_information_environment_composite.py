"""
INFORMATION ENVIRONMENT COMPOSITE HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION
New Mechanism: Investor Information Gaps and Reputation Risk

Analyzes whether firm information environment (media attention + reputation)
moderates the FCC volatility effect (Essay 2).

Hypothesis: Firms with weak information environments (low media coverage, prior offender status)
experience larger FCC-driven volatility increases because forced disclosure reveals more unknown
information in information-scarce firms.

Mechanism: FCC mandates 7-day disclosure -> for firms with weak information environments,
fast disclosure reveals more novel/surprising information -> larger market uncertainty
-> larger FCC volatility effect for information-disadvantaged firms.

Tests three specifications:
- Spec A: Media attention interaction (media coverage binary)
- Spec B: Reputation weakness interaction (repeat offender status)
- Spec C: Composite information environment risk (combined index)
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path
from datetime import datetime

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

print("=" * 90)
print("INFORMATION ENVIRONMENT COMPOSITE HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/6] Loading datasets...")

# Load main dissertation dataset
print("  Loading main dissertation dataset...")
main_df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"    [OK] {len(main_df):,} breach observations")

print(f"    Available information environment metrics:")
print(f"      - media_coverage_count: {main_df['media_coverage_count'].notna().sum():,} observations")
print(f"      - is_repeat_offender: {main_df['is_repeat_offender'].notna().sum():,} observations")

# ============================================================================
# SECTION 2: CREATE INFORMATION ENVIRONMENT INDICATORS
# ============================================================================

print("\n[2/6] Creating information environment indicators...")

df = main_df.copy()

# Binary indicator: High media attention (above median)
print("  Engineering information environment components...")

df['media_attention'] = (df['media_coverage_count'] > df['media_coverage_count'].median()).astype(int)
print(f"    Media attention (above median): {df['media_attention'].sum():,} breaches")

# Binary indicator: Reputation weakness (repeat offender)
df['reputation_weakness'] = df['is_repeat_offender'].astype(int)
print(f"    Reputation weakness (repeat offender): {df['reputation_weakness'].sum():,} breaches")

# Composite information environment risk (average of two binary indicators)
# Higher values = weaker information environment
df['info_env_risk'] = (df['media_attention'] + df['reputation_weakness']) / 2

# Create high risk indicator (firms weak on both dimensions or on one major dimension)
# Interpretation: threshold >= 0.5 means either (a) low media + repeat offender, or
# (b) at least one dimension indicates weak information environment
df['high_info_env_risk'] = (df['info_env_risk'] >= 0.5).astype(int)

print(f"\n  Information environment risk distribution:")
print(f"    High info env risk (composite >= 0.5): {df['high_info_env_risk'].sum():,}")

# Breakdown of information environment groups
info_env_breakdown = pd.crosstab(
    df['media_attention'],
    df['reputation_weakness'],
    margins=True,
    rownames=['Media Attention'],
    colnames=['Repeat Offender']
)
print(f"\n  Information environment breakdown:")
print(info_env_breakdown)

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS (SPEC C - COMPOSITE)
# ============================================================================

print("\n[3/6] Descriptive statistics (Spec C - Composite)...")

print("\n  VOLATILITY by information environment risk:")
info_env_groups = df[df['volatility_change'].notna()].groupby('high_info_env_risk')['volatility_change'].describe().round(4)
print(info_env_groups)

print("\n  VOLATILITY by FCC and information environment:")
fcc_info_env = df[df['volatility_change'].notna()].groupby(
    ['fcc_reportable', 'high_info_env_risk']
)['volatility_change'].agg(['count', 'mean', 'median', 'std']).round(4)
print(fcc_info_env)

# Highlight the interaction
print("\n  FCC effect by information environment:")
non_fcc_low_risk = df[(df['fcc_reportable']==0) & (df['high_info_env_risk']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_low_risk = df[(df['fcc_reportable']==1) & (df['high_info_env_risk']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
non_fcc_high_risk = df[(df['fcc_reportable']==0) & (df['high_info_env_risk']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_high_risk = df[(df['fcc_reportable']==1) & (df['high_info_env_risk']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()

print(f"    Non-FCC + Low info env risk: {non_fcc_low_risk:.4f}pp")
print(f"    FCC + Low info env risk: {fcc_low_risk:.4f}pp")
print(f"    FCC effect for low-risk: {fcc_low_risk - non_fcc_low_risk:.4f}pp (DIFFERENCE)")
print(f"\n    Non-FCC + High info env risk: {non_fcc_high_risk:.4f}pp")
print(f"    FCC + High info env risk: {fcc_high_risk:.4f}pp")
print(f"    FCC effect for high-risk: {fcc_high_risk - non_fcc_high_risk:.4f}pp (DIFFERENCE)")

# ============================================================================
# SECTION 4: HETEROGENEITY ANALYSIS - OLS REGRESSIONS
# ============================================================================

print("\n[4/6] Running heterogeneity models (3 Specifications)...")

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
    (df['media_coverage_count'].notna()) &
    (df['is_repeat_offender'].notna())
].copy()

# Volatility is already in percentage point form
reg_data['volatility_outcome'] = reg_data['volatility_change']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)
reg_data['media_attn'] = reg_data['media_attention'].astype(int)
reg_data['reputation_weak'] = reg_data['reputation_weakness'].astype(int)
reg_data['high_info_env'] = reg_data['high_info_env_risk'].astype(int)

print(f"\n  Analysis sample: {len(reg_data):,} breaches with complete info environment data")

# ============================================================================
# SPECIFICATION A: MEDIA ATTENTION INTERACTION
# ============================================================================

print("\n  SPECIFICATION A: MEDIA ATTENTION INTERACTION")

# A1: Baseline
print("    A1: Baseline FCC Effect")
model_a1 = ols('volatility_outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
               data=reg_data).fit(cov_type='HC3')

coef_fcc_a1 = model_a1.params['fcc[T.1]'] if 'fcc[T.1]' in model_a1.params.index else model_a1.params['fcc']
pval_fcc_a1 = model_a1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model_a1.params.index else model_a1.pvalues['fcc']
print(f"      FCC Effect: {coef_fcc_a1:.4f}pp (p={pval_fcc_a1:.4f})")

# A2: FCC x Media Attention
print("    A2: FCC x Media Attention Interaction")
model_a2 = ols('volatility_outcome ~ fcc * media_attn + health + financial + prior_breaches + firm_size_log',
               data=reg_data).fit(cov_type='HC3')

coef_fcc_a2 = model_a2.params['fcc[T.1]'] if 'fcc[T.1]' in model_a2.params.index else model_a2.params['fcc']
pval_fcc_a2 = model_a2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model_a2.params.index else model_a2.pvalues['fcc']
coef_media = model_a2.params['media_attn[T.1]'] if 'media_attn[T.1]' in model_a2.params.index else model_a2.params['media_attn']
pval_media = model_a2.pvalues['media_attn[T.1]'] if 'media_attn[T.1]' in model_a2.params.index else model_a2.pvalues['media_attn']

interact_key_a = 'fcc[T.1]:media_attn[T.1]' if 'fcc[T.1]:media_attn[T.1]' in model_a2.params.index else 'fcc:media_attn'
if interact_key_a in model_a2.params.index:
    coef_interact_a = model_a2.params[interact_key_a]
    pval_interact_a = model_a2.pvalues[interact_key_a]
else:
    coef_interact_a = 0
    pval_interact_a = 1.0

print(f"      FCC Effect: {coef_fcc_a2:.4f}pp (p={pval_fcc_a2:.4f})")
print(f"      Media Attention Effect: {coef_media:.4f}pp (p={pval_media:.4f})")
print(f"      FCC x Media Attention: {coef_interact_a:.4f}pp (p={pval_interact_a:.4f})")

# ============================================================================
# SPECIFICATION B: REPUTATION WEAKNESS INTERACTION
# ============================================================================

print("\n  SPECIFICATION B: REPUTATION WEAKNESS INTERACTION")

# B1: Baseline (already have from A1)
print("    B1: Baseline FCC Effect (same as A1)")
print(f"      FCC Effect: {coef_fcc_a1:.4f}pp (p={pval_fcc_a1:.4f})")

# B2: FCC x Reputation Weakness
print("    B2: FCC x Reputation Weakness Interaction")
model_b2 = ols('volatility_outcome ~ fcc * reputation_weak + health + financial + prior_breaches + firm_size_log',
               data=reg_data).fit(cov_type='HC3')

coef_fcc_b2 = model_b2.params['fcc[T.1]'] if 'fcc[T.1]' in model_b2.params.index else model_b2.params['fcc']
pval_fcc_b2 = model_b2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model_b2.params.index else model_b2.pvalues['fcc']
coef_repw = model_b2.params['reputation_weak[T.1]'] if 'reputation_weak[T.1]' in model_b2.params.index else model_b2.params['reputation_weak']
pval_repw = model_b2.pvalues['reputation_weak[T.1]'] if 'reputation_weak[T.1]' in model_b2.params.index else model_b2.pvalues['reputation_weak']

interact_key_b = 'fcc[T.1]:reputation_weak[T.1]' if 'fcc[T.1]:reputation_weak[T.1]' in model_b2.params.index else 'fcc:reputation_weak'
if interact_key_b in model_b2.params.index:
    coef_interact_b = model_b2.params[interact_key_b]
    pval_interact_b = model_b2.pvalues[interact_key_b]
else:
    coef_interact_b = 0
    pval_interact_b = 1.0

print(f"      FCC Effect: {coef_fcc_b2:.4f}pp (p={pval_fcc_b2:.4f})")
print(f"      Reputation Weakness Effect: {coef_repw:.4f}pp (p={pval_repw:.4f})")
print(f"      FCC x Reputation Weakness: {coef_interact_b:.4f}pp (p={pval_interact_b:.4f})")

# ============================================================================
# SPECIFICATION C: COMPOSITE INFORMATION ENVIRONMENT RISK (KEY TEST)
# ============================================================================

print("\n  SPECIFICATION C: COMPOSITE INFORMATION ENVIRONMENT RISK (Key Test)")

# C1: Baseline (already have from A1)
print("    C1: Baseline FCC Effect (same as A1)")
print(f"      FCC Effect: {coef_fcc_a1:.4f}pp (p={pval_fcc_a1:.4f})")

# C2: FCC x Composite Info Environment Risk
print("    C2: FCC x Composite Info Environment Risk (KEY INTERACTION)")
model_c2 = ols('volatility_outcome ~ fcc * high_info_env + health + financial + prior_breaches + firm_size_log',
               data=reg_data).fit(cov_type='HC3')

coef_fcc_c2 = model_c2.params['fcc[T.1]'] if 'fcc[T.1]' in model_c2.params.index else model_c2.params['fcc']
pval_fcc_c2 = model_c2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model_c2.params.index else model_c2.pvalues['fcc']
coef_infoenv = model_c2.params['high_info_env[T.1]'] if 'high_info_env[T.1]' in model_c2.params.index else model_c2.params['high_info_env']
pval_infoenv = model_c2.pvalues['high_info_env[T.1]'] if 'high_info_env[T.1]' in model_c2.params.index else model_c2.pvalues['high_info_env']

interact_key_c = 'fcc[T.1]:high_info_env[T.1]' if 'fcc[T.1]:high_info_env[T.1]' in model_c2.params.index else 'fcc:high_info_env'
if interact_key_c in model_c2.params.index:
    coef_interact_c = model_c2.params[interact_key_c]
    pval_interact_c = model_c2.pvalues[interact_key_c]
else:
    coef_interact_c = 0
    pval_interact_c = 1.0

print(f"      FCC Effect: {coef_fcc_c2:.4f}pp (p={pval_fcc_c2:.4f})")
print(f"      High Info Env Risk Effect: {coef_infoenv:.4f}pp (p={pval_infoenv:.4f})")
print(f"      FCC x Info Env Risk: {coef_interact_c:.4f}pp (p={pval_interact_c:.4f})")

if coef_interact_c != 0:
    print(f"\n      INTERPRETATION (Spec C - Key Test):")
    print(f"      - FCC effect for low-risk firms: {coef_fcc_c2:.4f}pp")
    print(f"      - FCC effect for high-risk firms: {coef_fcc_c2 + coef_interact_c:.4f}pp")
    print(f"      - Difference (interaction): {coef_interact_c:.4f}pp")

    if coef_interact_c > 0.1 and pval_interact_c < 0.05:
        print(f"\n      FINDING: FCC VOLATILITY INCREASE IS AMPLIFIED for weak info env firms")
        print(f"      This supports the INFORMATION ENVIRONMENT MECHANISM")
    elif coef_interact_c < -0.1 and pval_interact_c < 0.05:
        print(f"\n      FINDING: FCC VOLATILITY INCREASE IS REDUCED for weak info env firms")
        print(f"      Alternative: Weak info env firms may already have high baseline uncertainty")
    else:
        print(f"\n      FINDING: NO SIGNIFICANT INTERACTION")
        print(f"      Information environment does not moderate FCC volatility effect")

# ============================================================================
# SECTION 5: SAVE RESULTS AND GENERATE TABLES
# ============================================================================

print("\n[5/6] Saving results and generating publication tables...")

# Create comprehensive results table with all three specifications
results_table = pd.DataFrame({
    'Specification': ['Spec A: Media Attention', 'Spec A: Media Attention',
                     'Spec B: Reputation Weakness', 'Spec B: Reputation Weakness',
                     'Spec C: Composite Info Env', 'Spec C: Composite Info Env'],
    'Model': ['Baseline', 'FCC x Dimension', 'Baseline', 'FCC x Dimension',
             'Baseline', 'FCC x Dimension (KEY)'],
    'FCC Coefficient': [
        f"{coef_fcc_a1:.4f}***" if pval_fcc_a1 < 0.01 else f"{coef_fcc_a1:.4f}**" if pval_fcc_a1 < 0.05 else f"{coef_fcc_a1:.4f}",
        f"{coef_fcc_a2:.4f}***" if pval_fcc_a2 < 0.01 else f"{coef_fcc_a2:.4f}**" if pval_fcc_a2 < 0.05 else f"{coef_fcc_a2:.4f}",
        f"{coef_fcc_a1:.4f}***" if pval_fcc_a1 < 0.01 else f"{coef_fcc_a1:.4f}**" if pval_fcc_a1 < 0.05 else f"{coef_fcc_a1:.4f}",
        f"{coef_fcc_b2:.4f}***" if pval_fcc_b2 < 0.01 else f"{coef_fcc_b2:.4f}**" if pval_fcc_b2 < 0.05 else f"{coef_fcc_b2:.4f}",
        f"{coef_fcc_a1:.4f}***" if pval_fcc_a1 < 0.01 else f"{coef_fcc_a1:.4f}**" if pval_fcc_a1 < 0.05 else f"{coef_fcc_a1:.4f}",
        f"{coef_fcc_c2:.4f}***" if pval_fcc_c2 < 0.01 else f"{coef_fcc_c2:.4f}**" if pval_fcc_c2 < 0.05 else f"{coef_fcc_c2:.4f}"
    ],
    'Dimension Coefficient': [
        f"{coef_media:.4f}" if pval_media > 0.05 else f"{coef_media:.4f}*",
        f"{coef_media:.4f}" if pval_media > 0.05 else f"{coef_media:.4f}*",
        f"{coef_repw:.4f}" if pval_repw > 0.05 else f"{coef_repw:.4f}*",
        f"{coef_repw:.4f}" if pval_repw > 0.05 else f"{coef_repw:.4f}*",
        f"{coef_infoenv:.4f}" if pval_infoenv > 0.05 else f"{coef_infoenv:.4f}*",
        f"{coef_infoenv:.4f}" if pval_infoenv > 0.05 else f"{coef_infoenv:.4f}*"
    ],
    'Interaction': [
        'N/A',
        f"{coef_interact_a:.4f}" if pval_interact_a > 0.05 else f"{coef_interact_a:.4f}*" if pval_interact_a < 0.05 else f"{coef_interact_a:.4f}",
        'N/A',
        f"{coef_interact_b:.4f}" if pval_interact_b > 0.05 else f"{coef_interact_b:.4f}*" if pval_interact_b < 0.05 else f"{coef_interact_b:.4f}",
        'N/A',
        f"{coef_interact_c:.4f}" if pval_interact_c > 0.05 else f"{coef_interact_c:.4f}*" if pval_interact_c < 0.05 else f"{coef_interact_c:.4f}"
    ],
    'R-squared': [
        f"{model_a1.rsquared:.4f}",
        f"{model_a2.rsquared:.4f}",
        f"{model_a1.rsquared:.4f}",
        f"{model_b2.rsquared:.4f}",
        f"{model_a1.rsquared:.4f}",
        f"{model_c2.rsquared:.4f}"
    ]
})

results_table.to_csv('outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv', index=False)
print(f"  [OK] Saved regression results: outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv")

print("\n[6/6] Summary and interpretation...")

print("\n" + "=" * 90)
print("ESSAY 2 VOLATILITY: INFORMATION ENVIRONMENT COMPOSITE HETEROGENEITY ANALYSIS COMPLETE")
print("=" * 90)

print("\nKey Findings Across Three Specifications:")
print(f"  Specification A (Media Attention):")
print(f"    - FCC x Media Attention interaction: {coef_interact_a:.4f}pp (p={pval_interact_a:.4f})")
print(f"\n  Specification B (Reputation Weakness):")
print(f"    - FCC x Reputation Weakness interaction: {coef_interact_b:.4f}pp (p={pval_interact_b:.4f})")
print(f"\n  Specification C (Composite Info Environment - KEY TEST):")
print(f"    - FCC x Info Environment Risk interaction: {coef_interact_c:.4f}pp (p={pval_interact_c:.4f})")

print("\nInterpretation (Spec C - Composite):")
if coef_interact_c > 0.1 and pval_interact_c < 0.05:
    print("  MECHANISM CONFIRMED: Information environment risk amplifies FCC volatility increase")
    print("  Market mechanism: Firms with weak information environments (low media + reputation risk)")
    print("  experience larger uncertainty shocks when forced to disclose under FCC deadline")
elif coef_interact_c < -0.1 and pval_interact_c < 0.05:
    print("  ALTERNATIVE: FCC volatility reduced for weak information environment firms")
    print("  Possible: Weak information environment creates ceiling effect on uncertainty")
else:
    print("  FINDING: Information environment does not significantly moderate FCC volatility effect")
    print("  FCC impact operates independently of firm media attention and reputation status")

print("\n[OK] Essay 2 Mechanism 5 (Information Environment) analysis complete!")
