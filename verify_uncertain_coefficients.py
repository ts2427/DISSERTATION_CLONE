#!/usr/bin/env python3
"""Verify uncertain coefficients: D1 industry FE and D2 pre-2007"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')

df['FCC'] = df['fcc_reportable'].astype(int)
df['firm_size'] = df['firm_size_log']
df['prior_breaches'] = df['prior_breaches_total']
df['pre_breach_volatility'] = df['return_volatility_pre']

df = df.dropna(subset=['volatility_change', 'FCC', 'firm_size', 'leverage', 'roa', 'pre_breach_volatility', 'health_breach', 'prior_breaches'])

y = df['volatility_change'].values
controls = ['pre_breach_volatility', 'firm_size', 'leverage', 'roa', 'health_breach', 'prior_breaches']

print("="*80)
print("VERIFY UNCERTAIN COEFFICIENTS")
print("="*80)

# ============================================================================
# TABLE D1: INDUSTRY FE COEFFICIENT
# ============================================================================

print("\n1. TABLE D1 - INDUSTRY FIXED EFFECTS COEFFICIENT")
print("-"*80)

X_main = df[['FCC'] + controls].copy()
X_main = sm.add_constant(X_main)
m_baseline = sm.OLS(y, X_main).fit(cov_type='HC3')

print(f"\nBaseline (no FE):")
print(f"  FCC Coefficient: {m_baseline.params['FCC']:.4f}%")
print(f"  SE: {m_baseline.bse['FCC']:.4f}")
print(f"  p-value: {m_baseline.pvalues['FCC']:.4f}")
print(f"  R²: {m_baseline.rsquared:.4f}")

# Industry FE
sic_2digit = df['sic_3digit'].astype(str).str[:2]
industry_dummies = pd.get_dummies(sic_2digit, drop_first=True, prefix='ind', dtype=int)

X_indfe = X_main.copy()
for col in industry_dummies.columns:
    X_indfe[col] = industry_dummies[col].astype(int).values

X_indfe = X_indfe.astype(float)  # Ensure all columns are numeric
m_indfe = sm.OLS(y, X_indfe).fit(cov_type='HC3')

print(f"\nWith Industry FE:")
print(f"  FCC Coefficient: {m_indfe.params['FCC']:.4f}%")
print(f"  SE: {m_indfe.bse['FCC']:.4f}")
print(f"  p-value: {m_indfe.pvalues['FCC']:.4f}")
print(f"  R²: {m_indfe.rsquared:.4f}")

print(f"\nAPPENDIX SHOWS: +1.912%, p=0.054, R²=0.4087")
print(f"PROJECT FILES HAD: +5.018%, p=0.026")
print(f"VERIFICATION RESULT: {m_indfe.params['FCC']:.3f}%, p={m_indfe.pvalues['FCC']:.3f}, R²={m_indfe.rsquared:.4f}")

if abs(m_indfe.params['FCC'] - 1.912) < 0.01:
    print(f"VERDICT: Appendix +1.912% is CORRECT")
elif abs(m_indfe.params['FCC'] - 5.018) < 0.1:
    print(f"VERDICT: Project files +5.018% was correct, appendix +1.912% is WRONG")
else:
    print(f"VERDICT: UNEXPECTED VALUE - neither matches")

# ============================================================================
# TABLE D2: PRE-2007 COEFFICIENT
# ============================================================================

print("\n\n2. TABLE D2 - PRE-2007 FALSIFICATION COEFFICIENT")
print("-"*80)

df_pre = df[df['breach_year'] < 2007].copy()
y_pre = df_pre['volatility_change'].values
X_pre = df_pre[['FCC'] + controls].copy()
X_pre = sm.add_constant(X_pre)

print(f"\nPre-2007 sample (N={len(df_pre)}):")

if len(df_pre) > 0:
    m_pre = sm.OLS(y_pre, X_pre).fit(cov_type='HC3')
    print(f"  FCC Coefficient: {m_pre.params['FCC']:.4f}%")
    print(f"  SE: {m_pre.bse['FCC']:.4f}")
    print(f"  p-value: {m_pre.pvalues['FCC']:.4f}")

    print(f"\nAPPENDIX SHOWS: +13.96%, SE=36.07, p=0.882")
    print(f"VERIFICATION FOUND: +61.701%, SE=116.2320, p=0.5955")
    print(f"CURRENT CALC RESULT: {m_pre.params['FCC']:.3f}%, SE={m_pre.bse['FCC']:.4f}, p={m_pre.pvalues['FCC']:.4f}")

    if abs(m_pre.params['FCC'] - 13.96) < 1:
        print(f"VERDICT: Appendix +13.96% is CORRECT")
    elif abs(m_pre.params['FCC'] - 61.701) < 1:
        print(f"VERDICT: Previous verification +61.701% was correct, appendix +13.96% is WRONG")
    else:
        print(f"VERDICT: Different value again - {m_pre.params['FCC']:.3f}%")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n\n" + "="*80)
print("SUMMARY - WHAT TO FIX")
print("="*80)

print(f"\nTABLE A1 vs TABLE A2 FCC/non-FCC count:")
print(f"  TABLE A1 says: 184 FCC, 707 non-FCC")
print(f"  TABLE A2 says: 183 FCC, 708 non-FCC")
print(f"  Actual in data: {df['FCC'].sum()} FCC, {(df['FCC']==0).sum()} non-FCC")
print(f"  ACTION: Correct whichever is wrong")

print(f"\nTABLE D1 industry FE:")
print(f"  Appendix: +1.912%")
print(f"  This run: {m_indfe.params['FCC']:.3f}%")
print(f"  ACTION: Verify which is correct for the Model 4 spec")

print(f"\nTABLE D2 pre-2007:")
print(f"  Appendix: +13.96%")
if len(df_pre) > 0:
    print(f"  This run: {m_pre.params['FCC']:.3f}%")
print(f"  ACTION: Verify which is correct")

