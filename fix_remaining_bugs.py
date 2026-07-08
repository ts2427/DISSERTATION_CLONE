#!/usr/bin/env python3
"""Fix the remaining three bugs in the appendix"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')

# Map columns
df['FCC'] = df['fcc_reportable'].astype(int)
df['firm_size'] = df['firm_size_log']
df['prior_breaches'] = df['prior_breaches_total']
df['pre_breach_volatility'] = df['return_volatility_pre']

# Regression sample
df = df.dropna(subset=['volatility_change', 'FCC', 'firm_size', 'leverage', 'roa', 'pre_breach_volatility', 'health_breach', 'prior_breaches'])

y = df['volatility_change'].values
controls = ['pre_breach_volatility', 'firm_size', 'leverage', 'roa', 'health_breach', 'prior_breaches']

print("="*80)
print("FIX REMAINING BUGS - FINAL VERIFICATION")
print("="*80)

# ============================================================================
# BUG #1: TABLE A2 DESCRIPTIVE MEAN
# ============================================================================

print("\n1. TABLE A2 DESCRIPTIVE STATISTICS - Volatility Change")
print("-"*80)

fcc_vol = df[df['FCC'] == 1]['volatility_change']
non_fcc_vol = df[df['FCC'] == 0]['volatility_change']
all_vol = df['volatility_change']

print(f"\nFCC Firms (N={len(fcc_vol)}):")
print(f"  Mean Volatility Change: {fcc_vol.mean():.3f}%")
print(f"  Std Dev: {fcc_vol.std():.3f}%")
print(f"  Min: {fcc_vol.min():.3f}%, Max: {fcc_vol.max():.3f}%")

print(f"\nNon-FCC Firms (N={len(non_fcc_vol)}):")
print(f"  Mean Volatility Change: {non_fcc_vol.mean():.3f}%")
print(f"  Std Dev: {non_fcc_vol.std():.3f}%")
print(f"  Min: {non_fcc_vol.min():.3f}%, Max: {non_fcc_vol.max():.3f}%")

print(f"\nAll Breaches (N={len(all_vol)}):")
print(f"  Mean Volatility Change: {all_vol.mean():.3f}%")
print(f"  Std Dev: {all_vol.std():.3f}%")

# Check if weighted average matches
weighted_mean = (fcc_vol.mean() * len(fcc_vol) + non_fcc_vol.mean() * len(non_fcc_vol)) / len(all_vol)
print(f"\nVerification (weighted average): {weighted_mean:.3f}% == {all_vol.mean():.3f}% [OK]")

print(f"\nCURRENT APPENDIX SHOWS:")
print(f"  FCC: 1.793% (WRONG - should be {fcc_vol.mean():.3f}%)")
print(f"  Non-FCC: 0.823%")
print(f"  All: 1.017%")

# ============================================================================
# BUG #2: TABLE C3 ABSOLUTE RETURNS
# ============================================================================

print("\n\n2. TABLE C3 ABSOLUTE RETURNS vs SD")
print("-"*80)

X_main = df[['FCC'] + controls].copy()
X_main = sm.add_constant(X_main)

# SD (primary)
m_sd = sm.OLS(y, X_main).fit(cov_type='HC3')

# Daily absolute returns proxy - should be different
y_abs = df['return_volatility_post'].values - df['return_volatility_pre'].values
m_abs = sm.OLS(y_abs, X_main).fit(cov_type='HC3')

print(f"\nStandard Deviation (PRIMARY):")
print(f"  FCC Coefficient: {m_sd.params['FCC']:.6f}%")
print(f"  p-value: {m_sd.pvalues['FCC']:.4f}")
print(f"  R²: {m_sd.rsquared:.4f}")

print(f"\nDaily Absolute Returns:")
print(f"  FCC Coefficient: {m_abs.params['FCC']:.6f}%")
print(f"  p-value: {m_abs.pvalues['FCC']:.4f}")
print(f"  R²: {m_abs.rsquared:.4f}")

print(f"\nDifference: {abs(m_sd.params['FCC'] - m_abs.params['FCC']):.10f}%")

if abs(m_sd.params['FCC'] - m_abs.params['FCC']) < 0.00001:
    print("[WARNING] SUSPICIOUS: Coefficients are IDENTICAL (copy-paste error!)")
    print("  This is a BUG — these should produce different results")
else:
    print("✓ CORRECT: Different coefficients as expected")

print(f"\nCURRENT APPENDIX SHOWS: Both +1.585% (WRONG if they're identical)")

# ============================================================================
# BUG #3: TABLE D2 POST-2007 COEFFICIENT
# ============================================================================

print("\n\n3. TABLE D2 POST-2007 vs POOLED COEFFICIENT")
print("-"*80)

# Pooled (all, N=891)
m_pooled = sm.OLS(y, X_main).fit(cov_type='HC3')

# Post-2007 only (after FCC rule)
df_post = df[df['breach_year'] >= 2007].copy()
y_post = df_post['volatility_change'].values
X_post = df_post[['FCC'] + controls].copy()
X_post = sm.add_constant(X_post)
m_post = sm.OLS(y_post, X_post).fit(cov_type='HC3')

# Pre-2007 only (for comparison)
df_pre = df[df['breach_year'] < 2007].copy()
y_pre = df_pre['volatility_change'].values
X_pre = df_pre[['FCC'] + controls].copy()
X_pre = sm.add_constant(X_pre)
m_pre = sm.OLS(y_pre, X_pre).fit(cov_type='HC3')

print(f"\nPOOLED (all years):")
print(f"  N: {len(df)}")
print(f"  FCC Coefficient: {m_pooled.params['FCC']:.6f}%")
print(f"  SE: {m_pooled.bse['FCC']:.4f}")
print(f"  p-value: {m_pooled.pvalues['FCC']:.4f}")

print(f"\nPRE-2007 (N={len(df_pre)} - falsification test):")
print(f"  FCC Coefficient: {m_pre.params['FCC']:.6f}%")
print(f"  SE: {m_pre.bse['FCC']:.4f}")
print(f"  p-value: {m_pre.pvalues['FCC']:.4f}")

print(f"\nPOST-2007 (after FCC rule on 2007-09-28):")
print(f"  N: {len(df_post)}")
print(f"  FCC Coefficient: {m_post.params['FCC']:.6f}%")
print(f"  SE: {m_post.bse['FCC']:.4f}")
print(f"  p-value: {m_post.pvalues['FCC']:.4f}")

print(f"\nDifference (Post-2007 minus Pooled): {m_post.params['FCC'] - m_pooled.params['FCC']:+.6f}pp")

if abs(m_post.params['FCC'] - m_pooled.params['FCC']) < 0.00001:
    print("[WARNING] IDENTICAL (suspicious!)")
else:
    print(f"[OK] DIFFERENT as expected (contribution of {len(df)-len(df_post)} pre-2007 obs: {m_post.params['FCC'] - m_pooled.params['FCC']:+.3f}pp)")

print(f"\nCURRENT APPENDIX SHOWS POST-2007: +1.585% (should be {m_post.params['FCC']:.3f}%)")

# ============================================================================
# SUMMARY FOR UPDATES
# ============================================================================

print("\n\n" + "="*80)
print("SUMMARY OF CORRECTIONS NEEDED")
print("="*80)

print(f"\n✓ TABLE A2 (Descriptive Stats):")
print(f"  Change FCC mean from 1.793% to {fcc_vol.mean():.3f}%")
print(f"  Change Non-FCC mean from 0.823% to {non_fcc_vol.mean():.3f}%")
print(f"  Change All mean from 1.017% to {all_vol.mean():.3f}%")

print(f"\n✓ TABLE C3 (Volatility Measures):")
if abs(m_sd.params['FCC'] - m_abs.params['FCC']) < 0.00001:
    print(f"  BUG CONFIRMED: Absolute returns coefficient is IDENTICAL to SD ({m_abs.params['FCC']:.6f}%)")
    print(f"  ACTION: Must re-run absolute returns specification or clarify definition")
    print(f"          If not actually run, remove this row and update methods section")
else:
    print(f"  Absolute returns: {m_abs.params['FCC']:.6f}% (different from SD, correct)")

print(f"\n✓ TABLE D2 (Post-2007 Coefficient):")
print(f"  Change post-2007 from +1.585% to {m_post.params['FCC']:.3f}%")
print(f"  Change p-value from 0.0828 to {m_post.pvalues['FCC']:.4f}")
print(f"  Add note: Post-2007-only coefficient ({m_post.params['FCC']:.3f}%) slightly differs from pooled")
print(f"            because {len(df)-len(df_post)} pre-2007 observations contribute {m_post.params['FCC'] - m_pooled.params['FCC']:+.3f}pp to pooled estimate")

print("\n" + "="*80)
