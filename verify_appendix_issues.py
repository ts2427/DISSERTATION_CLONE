#!/usr/bin/env python3
"""Verify suspicious values in the appendix"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# LOAD DATA
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')

# MAP COLUMNS
df['FCC'] = df['fcc_reportable'].astype(int)
df['firm_size'] = df['firm_size_log']
df['prior_breaches'] = df['prior_breaches_total']
df['pre_breach_volatility'] = df['return_volatility_pre']

# DROP MISSING
df = df.dropna(subset=['volatility_change', 'FCC', 'firm_size', 'leverage', 'roa', 'pre_breach_volatility', 'health_breach', 'prior_breaches'])

y = df['volatility_change'].values
controls = ['pre_breach_volatility', 'firm_size', 'leverage', 'roa', 'health_breach', 'prior_breaches']

print("="*70)
print("VERIFICATION OF SUSPICIOUS APPENDIX VALUES")
print("="*70)

# ============================================================================
# ISSUE 1: TABLE A2 FCC ΔVolatility mean
# ============================================================================

print("\n1. TABLE A2 FCC DESCRIPTIVE MEAN")
print("-"*70)

fcc_volatility = df[df['FCC'] == 1]['volatility_change']
non_fcc_volatility = df[df['FCC'] == 0]['volatility_change']
all_volatility = df['volatility_change']

print(f"FCC mean ΔVolatility: {fcc_volatility.mean():.3f}%")
print(f"Non-FCC mean ΔVolatility: {non_fcc_volatility.mean():.3f}%")
print(f"All mean ΔVolatility: {all_volatility.mean():.3f}%")
print(f"\nAppendix TABLE A2 shows FCC mean as: 1.793%")
print(f"VERDICT: {'MATCH' if abs(fcc_volatility.mean() - 1.793) < 0.01 else 'MISMATCH'} — Actual is {fcc_volatility.mean():.3f}%")

# ============================================================================
# ISSUE 2: SD vs Absolute Returns coefficients identical?
# ============================================================================

print("\n\n2. TABLE C3 SD VS ABSOLUTE RETURNS")
print("-"*70)

X_main = df[['FCC'] + controls].copy()
X_main = sm.add_constant(X_main)

# SD (primary)
m_sd = sm.OLS(y, X_main).fit(cov_type='HC3')

# Absolute returns
y_abs = df['return_volatility_post'].values - df['return_volatility_pre'].values
m_abs = sm.OLS(y_abs, X_main).fit(cov_type='HC3')

print(f"SD coefficient: {m_sd.params['FCC']:.6f}%")
print(f"Absolute returns coefficient: {m_abs.params['FCC']:.6f}%")
print(f"Difference: {abs(m_sd.params['FCC'] - m_abs.params['FCC']):.10f}%")
print(f"\nAppendix claims both are +1.585%")
print(f"VERDICT: {'IDENTICAL (suspicious!)' if abs(m_sd.params['FCC'] - m_abs.params['FCC']) < 0.00001 else 'DIFFERENT (correct)'}")

# ============================================================================
# ISSUE 3: Post-2007 N=887 vs pooled N=891
# ============================================================================

print("\n\n3. TABLE D2 POST-2007 vs POOLED")
print("-"*70)

# Post-2007 only
df_post = df[df['breach_year'] >= 2007].copy()
y_post = df_post['volatility_change'].values
X_post = df_post[['FCC'] + controls].copy()
X_post = sm.add_constant(X_post)
m_post = sm.OLS(y_post, X_post).fit(cov_type='HC3')

# Pooled (all)
m_pooled = sm.OLS(y, X_main).fit(cov_type='HC3')

print(f"Pooled (N=891) FCC coefficient: {m_pooled.params['FCC']:.6f}%")
print(f"Post-2007 (N={len(df_post)}) FCC coefficient: {m_post.params['FCC']:.6f}%")
print(f"Difference: {abs(m_pooled.params['FCC'] - m_post.params['FCC']):.10f}%")
print(f"\nAppendix TABLE D2 shows post-2007 N={len(df_post)} with +1.585%")
print(f"VERDICT: {'IDENTICAL (suspicious!)' if abs(m_pooled.params['FCC'] - m_post.params['FCC']) < 0.00001 else 'DIFFERENT'}")

# ============================================================================
# ISSUE 4: Firm cluster count
# ============================================================================

print("\n\n4. TABLE C5 FIRM CLUSTER COUNT")
print("-"*70)

# Count unique firms overall
unique_firms = df['org_name'].nunique()
fcc_firms = df[df['FCC'] == 1]['org_name'].nunique()
non_fcc_firms = df[df['FCC'] == 0]['org_name'].nunique()

print(f"Total unique firms in sample: {unique_firms}")
print(f"FCC firms: {fcc_firms}")
print(f"Non-FCC firms: {non_fcc_firms}")
print(f"FCC + Non-FCC: {fcc_firms + non_fcc_firms}")
print(f"\nAppendix says 'Firm-clustered (8 FCC clusters)'")
print(f"VERDICT: Should be {unique_firms} total clusters, not 8 FCC-only")

# ============================================================================
# ISSUE 5: Industry FE coefficient
# ============================================================================

print("\n\n5. TABLE D1 INDUSTRY FE COEFFICIENT")
print("-"*70)

# Add industry FE
sic_2digit = df['sic_3digit'].astype(str).str[:2]
industry_dummies = pd.get_dummies(sic_2digit, drop_first=True, prefix='ind')

X_indfe = X_main.copy()
for col in industry_dummies.columns:
    X_indfe[col] = industry_dummies[col].values

m_indfe = sm.OLS(y, X_indfe).fit(cov_type='HC3')

print(f"Baseline (no FE): FCC = {m_pooled.params['FCC']:.4f}%, R² = {m_pooled.rsquared:.4f}")
print(f"Industry FE: FCC = {m_indfe.params['FCC']:.4f}%, R² = {m_indfe.rsquared:.4f}")
print(f"\nAppendix TABLE D1 shows Industry FE as +1.912%, R² = 0.4087")
print(f"Actual is +{m_indfe.params['FCC']:.3f}%, R² = {m_indfe.rsquared:.4f}")
print(f"VERDICT: {'MATCH' if abs(m_indfe.params['FCC'] - 1.912) < 0.01 else 'MISMATCH'}")

# Also check old +5.02% claim
print(f"\nUserMemories claim: Industry FE = +5.02%")
print(f"VERDICT: {'MATCH' if abs(m_indfe.params['FCC'] - 5.02) < 0.1 else 'MISMATCH — actual is ' + str(round(m_indfe.params['FCC'], 3)) + '%'}")

# ============================================================================
# ISSUE 6: Info Environment coefficient shift
# ============================================================================

print("\n\n6. TABLE C2 INFO ENVIRONMENT SHIFT")
print("-"*70)

media = df['media_coverage_count'].fillna(0)
media_std = (media - media.mean()) / media.std()

repeat_offender = df['is_repeat_offender'].fillna(0).values
reputation_comp = 1 - repeat_offender
reputation_std = (reputation_comp - reputation_comp.mean()) / (reputation_comp.std() + 0.0001)

info_env = (media_std.values + reputation_std) / 2
info_env_std = (info_env - info_env.mean()) / (info_env.std() + 0.0001)

# FCC only
m1_info = sm.OLS(y, X_main).fit(cov_type='HC3')

# FCC + Info
X2_info = X_main.copy()
X2_info['info_std'] = info_env_std
m2_info = sm.OLS(y, X2_info).fit(cov_type='HC3')

print(f"FCC Only: {m1_info.params['FCC']:.4f}%")
print(f"FCC + Info: {m2_info.params['FCC']:.4f}%")
print(f"Shift: {m2_info.params['FCC'] - m1_info.params['FCC']:+.4f}pp")
print(f"\nAppendix claims FCC + Info = +1.803%")
print(f"Actual is +{m2_info.params['FCC']:.3f}%")
print(f"Shift from baseline = +{m2_info.params['FCC'] - m1_info.params['FCC']:.3f}pp")
print(f"VERDICT: {'MATCH' if abs(m2_info.params['FCC'] - 1.803) < 0.01 else 'MISMATCH'}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\nIssues to address:")
print("1. TABLE A2 FCC mean: Check if 1.793 is descriptive mean or regression coefficient")
print("2. TABLE C3 identical coefficients: Verify SD vs absolute returns really are identical")
print("3. TABLE D2 N=887: Verify post-2007 coefficient truly identical to pooled")
print("4. TABLE C5 clusters: Change from '8 FCC clusters' to '47 total clusters'")
print("5. TABLE D1 industry FE: Verify +1.912% is correct (vs memory's +5.02%)")
print("6. TABLE C2 info shift: Verify +1.803% is correct")
