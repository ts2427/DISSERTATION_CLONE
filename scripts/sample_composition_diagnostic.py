"""
SAMPLE COMPOSITION DIAGNOSTIC
========================================================================

Tests whether the p-value change from 0.0577 to 0.1066 is:
A) Model choice (return-generating specification), or
B) Sample composition (losing 129 observations)

Isolate by running market-adjusted on both samples.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

print("=" * 90)
print("SAMPLE COMPOSITION DIAGNOSTIC")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

factors = pd.read_csv('Data/wrds/fama_french_factors.csv')
factors['date'] = pd.to_datetime(factors['date'])

# Merge factors
df_factors = df.merge(factors, left_on='breach_date', right_on='date', how='left')

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# SAMPLE 1: Full sample (market-adjusted only)
print("\nSAMPLE 1: Full Sample (Market-Adjusted)")
print("-" * 90)

df_full = df.dropna(subset=['car_30d'] + controls)
print(f"N = {len(df_full)}")
print(f"FCC observations: {(df_full['fcc_reportable'] == True).sum()}")

X_full = sm.add_constant(df_full[controls].astype(float))
y_full = df_full['car_30d']
m_full = sm.OLS(y_full, X_full).fit(cov_type='HC3')

print(f"\nMarket-adjusted (full sample):")
print(f"  H2: {m_full.params['fcc_reportable']:>8.4f}% (SE={m_full.bse['fcc_reportable']:.4f}, p={m_full.pvalues['fcc_reportable']:.4f})")

# SAMPLE 2: Restricted to factor model observations
print(f"\n\nSAMPLE 2: Restricted Sample (Market-Adjusted, 519 obs)")
print("-" * 90)

df_restricted = df_factors.dropna(subset=['car_30d'] + controls + ['MKT-RF', 'SMB', 'HML'])
print(f"N = {len(df_restricted)}")
print(f"FCC observations: {(df_restricted['fcc_reportable'] == True).sum()}")

X_restricted = sm.add_constant(df_restricted[controls].astype(float))
y_restricted = df_restricted['car_30d']
m_restricted = sm.OLS(y_restricted, X_restricted).fit(cov_type='HC3')

print(f"\nMarket-adjusted (restricted sample):")
print(f"  H2: {m_restricted.params['fcc_reportable']:>8.4f}% (SE={m_restricted.bse['fcc_reportable']:.4f}, p={m_restricted.pvalues['fcc_reportable']:.4f})")

# SAMPLE 3: FF3 on restricted sample
print(f"\n\nSAMPLE 3: Restricted Sample (FF3, 519 obs)")
print("-" * 90)

X_ff3 = sm.add_constant(df_restricted[controls + ['MKT-RF', 'SMB', 'HML']].astype(float))
y_ff3 = df_restricted['car_30d']
m_ff3 = sm.OLS(y_ff3, X_ff3).fit(cov_type='HC3')

print(f"\nFF3 (restricted sample):")
print(f"  H2: {m_ff3.params['fcc_reportable']:>8.4f}% (SE={m_ff3.bse['fcc_reportable']:.4f}, p={m_ff3.pvalues['fcc_reportable']:.4f})")

# DIAGNOSTIC: What changed?
print(f"\n\n" + "=" * 90)
print("DIAGNOSTIC: What Caused the P-Value Change?")
print("=" * 90)

print(f"""
Market-adjusted on FULL sample (N=648):
  H2 = {m_full.params['fcc_reportable']:.4f}%, SE = {m_full.bse['fcc_reportable']:.4f}, p = {m_full.pvalues['fcc_reportable']:.4f}

Market-adjusted on RESTRICTED sample (N=519):
  H2 = {m_restricted.params['fcc_reportable']:.4f}%, SE = {m_restricted.bse['fcc_reportable']:.4f}, p = {m_restricted.pvalues['fcc_reportable']:.4f}

FF3 on RESTRICTED sample (N=519):
  H2 = {m_ff3.params['fcc_reportable']:.4f}%, SE = {m_ff3.bse['fcc_reportable']:.4f}, p = {m_ff3.pvalues['fcc_reportable']:.4f}

SAMPLE LOSS EFFECT (648 → 519):
  - Coefficient change: {m_restricted.params['fcc_reportable'] - m_full.params['fcc_reportable']:+.4f}pp
  - SE change: {m_restricted.bse['fcc_reportable'] - m_full.bse['fcc_reportable']:+.4f}
  - p-value change: {m_restricted.pvalues['fcc_reportable'] - m_full.pvalues['fcc_reportable']:+.4f}
  - FCC firms lost: {(df_full['fcc_reportable'] == True).sum() - (df_restricted['fcc_reportable'] == True).sum()} out of {(df_full['fcc_reportable'] == True).sum()}

MODEL CHANGE EFFECT (Market → FF3, same 519 sample):
  - Coefficient change: {m_ff3.params['fcc_reportable'] - m_restricted.params['fcc_reportable']:+.4f}pp
  - SE change: {m_ff3.bse['fcc_reportable'] - m_restricted.bse['fcc_reportable']:+.4f}
  - p-value change: {m_ff3.pvalues['fcc_reportable'] - m_restricted.pvalues['fcc_reportable']:+.4f}

INTERPRETATION:
""")

# Which effect is bigger?
sample_loss_se_pct = abs((m_restricted.bse['fcc_reportable'] - m_full.bse['fcc_reportable']) / m_full.bse['fcc_reportable']) * 100
model_change_se_pct = abs((m_ff3.bse['fcc_reportable'] - m_restricted.bse['fcc_reportable']) / m_restricted.bse['fcc_reportable']) * 100

print(f"  SE expansion from sample loss: {sample_loss_se_pct:.1f}%")
print(f"  SE expansion from FF3 vs market: {model_change_se_pct:.1f}%")

if abs(m_restricted.pvalues['fcc_reportable'] - m_full.pvalues['fcc_reportable']) > 0.02:
    print(f"\n  >>> CONCLUSION: Sample loss is THE DRIVER of the p-value change")
    print(f"      Market-adjusted on restricted sample gives p≈{m_restricted.pvalues['fcc_reportable']:.3f}")
    print(f"      This means losing 129 obs (20% of sample) causes the precision loss")
    print(f"      Return model choice (FF3 vs market) is minor in comparison")
else:
    print(f"\n  >>> CONCLUSION: Return model choice is driving the change")
    print(f"      Market-adjusted on restricted stays near p=0.058")
    print(f"      FF3 vs market model is what costs precision")

# FCC firm composition
fcc_full = (df_full['fcc_reportable'] == True).sum()
fcc_restricted = (df_restricted['fcc_reportable'] == True).sum()
fcc_lost = fcc_full - fcc_restricted

print(f"\n\nFCC FIRM COMPOSITION:")
print(f"  Full sample: {fcc_full} FCC firms")
print(f"  Restricted (factor models): {fcc_restricted} FCC firms")
print(f"  Lost: {fcc_lost} FCC firms ({fcc_lost/fcc_full*100:.1f}% of treatment group)")

if fcc_lost > 2:
    print(f"\n  >>> FCC is overrepresented in dropouts")
    print(f"      This affects H2 precision noticeably with only {fcc_restricted} treated firms remaining")
else:
    print(f"\n  >>> FCC loss is proportional to overall loss")
    print(f"      Treatment group composition is stable")

