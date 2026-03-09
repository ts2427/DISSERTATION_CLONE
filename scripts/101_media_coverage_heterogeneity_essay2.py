"""
MEDIA COVERAGE HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION
Analysis #4: Information Environment & Stakeholder Pressure

Tests whether media coverage moderates FCC volatility effect through information
environment channel (attention, pressure, reputation risk) in Essay 2.

Hypothesis: High media coverage amplifies FCC pressure because:
1. Public visibility increases stakeholder scrutiny
2. Media coverage increases reputational risk
3. Combined with forced disclosure timing → larger volatility increases

Alternative: Media coverage signals awareness/attention, reducing information
asymmetry → FCC volatility effect diminished for high-media breaches (market already informed)
"""

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

print("=" * 90)
print("MEDIA COVERAGE HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/5] Loading data...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"  [OK] {len(df):,} breach observations")

# ============================================================================
# SECTION 2: MEDIA COVERAGE ANALYSIS
# ============================================================================

print("\n[2/5] Analyzing media coverage...")

print("\n  Media coverage distribution:")
print(f"    media_coverage_count: {df['media_coverage_count'].describe().round(2)}")
print(f"    high_media_coverage: {df['high_media_coverage'].sum():,} ({df['high_media_coverage'].mean()*100:.1f}%)")
print(f"    has_media_coverage: {df['has_media_coverage'].sum():,} ({df['has_media_coverage'].mean()*100:.1f}%)")

# Create binary high-media indicator
df['is_high_media'] = df['high_media_coverage'].astype(int)

# Correlation with other variables
print("\n  Media coverage correlation with key variables:")
corr_vars = ['fcc_reportable', 'health_breach', 'financial_breach', 'ransomware', 'volatility_change']
for var in corr_vars:
    if var in df.columns:
        corr = df[['media_coverage_count', var]].corr().iloc[0, 1]
        print(f"    media_coverage <-> {var:20s}: {corr:+.3f}")

# ============================================================================
# SECTION 3: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[3/5] Descriptive statistics...")

print("\n  VOLATILITY by media coverage level:")
media_stats = df[df['volatility_change'].notna()].groupby('is_high_media')['volatility_change'].describe().round(4)
print(media_stats)

print("\n  FCC effect by media coverage:")
print("    High Media Coverage:")
non_fcc_media_high = df[(df['fcc_reportable']==0) & (df['is_high_media']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_media_high = df[(df['fcc_reportable']==1) & (df['is_high_media']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()
print(f"      Non-FCC: {non_fcc_media_high:.4f}pp")
print(f"      FCC: {fcc_media_high:.4f}pp")
print(f"      FCC Effect: {fcc_media_high - non_fcc_media_high:.4f}pp")

print("\n    Low/No Media Coverage:")
non_fcc_media_low = df[(df['fcc_reportable']==0) & (df['is_high_media']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_media_low = df[(df['fcc_reportable']==1) & (df['is_high_media']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
print(f"      Non-FCC: {non_fcc_media_low:.4f}pp")
print(f"      FCC: {fcc_media_low:.4f}pp")
print(f"      FCC Effect: {fcc_media_low - non_fcc_media_low:.4f}pp")

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
    (df['volatility_change'].notna())
].copy()

reg_data['volatility_outcome'] = reg_data['volatility_change']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['media'] = reg_data['is_high_media'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

print(f"\n  Analysis sample: {len(reg_data):,} breaches")

# Model 1: Baseline FCC
print("\n  MODEL 1: Baseline FCC Effect (Essay 2)")
model1 = ols('volatility_outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m1 = model1.params['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.params['fcc']
pval_fcc_m1 = model1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.pvalues['fcc']

print(f"    FCC Effect: {coef_fcc_m1:.4f}pp (p={pval_fcc_m1:.4f})")
print(f"    R-squared: {model1.rsquared:.4f}")

# Model 2: Add media main effect
print("\n  MODEL 2: FCC + Media Coverage Main Effect")
model2 = ols('volatility_outcome ~ fcc + media + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_media = model2.params['media[T.1]'] if 'media[T.1]' in model2.params.index else model2.params['media']
pval_media = model2.pvalues['media[T.1]'] if 'media[T.1]' in model2.params.index else model2.pvalues['media']

print(f"    FCC Effect: {coef_fcc_m2:.4f}pp (p={pval_fcc_m2:.4f})")
print(f"    Media Coverage Effect: {coef_media:.4f}pp (p={pval_media:.4f})")
print(f"    R-squared: {model2.rsquared:.4f}")

# Model 3: FCC x Media Interaction
print("\n  MODEL 3: FCC x MEDIA COVERAGE INTERACTION (Key Test)")
model3 = ols('volatility_outcome ~ fcc * media + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_media_m3 = model3.params['media[T.1]'] if 'media[T.1]' in model3.params.index else model3.params['media']
pval_media_m3 = model3.pvalues['media[T.1]'] if 'media[T.1]' in model3.params.index else model3.pvalues['media']

interact_key = 'fcc[T.1]:media[T.1]' if 'fcc[T.1]:media[T.1]' in model3.params.index else 'fcc:media'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}pp (p={pval_fcc_m3:.4f})")
print(f"    Media Main Effect: {coef_media_m3:.4f}pp (p={pval_media_m3:.4f})")
print(f"    FCC x Media: {coef_interact:.4f}pp (p={pval_interact:.4f})")
print(f"    R-squared: {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for low-media breaches: {coef_fcc_m3:.4f}pp")
    print(f"    - FCC effect for high-media breaches: {coef_fcc_m3 + coef_interact:.4f}pp")
    if abs(coef_interact) > 0.1 and pval_interact < 0.05:
        direction = "AMPLIFIED" if coef_interact > 0 else "REDUCED"
        print(f"    - High media coverage {direction} FCC volatility effect")

# ============================================================================
# SECTION 5: SAVE RESULTS
# ============================================================================

print("\n[5/5] Saving results...")

results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Media', 'Model 3: FCC x Media'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Media Coefficient': [
        'N/A',
        f"{coef_media:.4f}" if pval_media > 0.05 else f"{coef_media:.4f}*",
        f"{coef_media_m3:.4f}" if pval_media_m3 > 0.05 else f"{coef_media_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_MEDIA_COVERAGE_VOLATILITY_RESULTS.csv', index=False)
print(f"  [OK] Saved: TABLE_MEDIA_COVERAGE_VOLATILITY_RESULTS.csv")

print("\n" + "=" * 90)
print("ESSAY 2 VOLATILITY: MEDIA COVERAGE HETEROGENEITY ANALYSIS COMPLETE")
print("=" * 90)

print("\nKey Findings:")
print(f"  - Baseline FCC volatility effect: {coef_fcc_m1:.4f}pp")
print(f"  - Media coverage main effect: {coef_media:.4f}pp")
print(f"  - FCC x Media interaction: {coef_interact:.4f}pp (p={pval_interact:.4f})")

print("\nInterpretation:")
if coef_interact > 0.1 and pval_interact < 0.05:
    print("  AMPLIFICATION HYPOTHESIS: Media coverage amplifies FCC volatility effect")
    print("  Market mechanism: High visibility + forced disclosure timing")
    print("  creates compound uncertainty effect")
elif coef_interact < -0.1 and pval_interact < 0.05:
    print("  SUBSTITUTION HYPOTHESIS: Media coverage reduces FCC volatility effect")
    print("  Market mechanism: High media coverage pre-signals information,")
    print("  reducing additional uncertainty from mandatory disclosure")
else:
    print("  NO SIGNIFICANT INTERACTION: Media coverage does not moderate FCC effect")
    print("  FCC volatility effect independent of information environment")

print("\n[OK] Essay 2 Mechanism 4 (Media Coverage) analysis complete!")
