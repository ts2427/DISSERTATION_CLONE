"""
FF3 SIMPLE MERGE
========================================================================

Uses the same merge approach as Carhart/FF5:
- Load pre-computed CAR 30d
- Merge factor values at breach_date
- Regress CAR on controls + FF3 factors (Mkt-RF, SMB, HML)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

print("=" * 90)
print("FF3 SPECIFICATION (Simple Merge, matching Carhart/FF5 approach)")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

factors = pd.read_csv('Data/wrds/fama_french_factors.csv')
factors['date'] = pd.to_datetime(factors['date'])

print(f"\nDataset: {len(df)} breaches")
print(f"Factors: {len(factors)} observations")
print(f"Factor columns: {', '.join([c for c in factors.columns if c != 'date'])}")

# Merge factors to breach dates
df_factors = df.merge(factors, left_on='breach_date', right_on='date', how='left')

print(f"\nAfter merge: {len(df_factors)} rows")
print(f"Factor values available: {df_factors[['MKT-RF', 'SMB', 'HML']].notna().sum().min()} / {len(df_factors)}")

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# FF3 specification: controls + Mkt-RF, SMB, HML
required_cols = ['car_30d'] + controls + ['MKT-RF', 'SMB', 'HML']

df_ff3 = df_factors.dropna(subset=required_cols)

print(f"\nFF3 regression sample: {len(df_ff3)} observations")

# Run FF3 regression
X = sm.add_constant(df_ff3[controls + ['MKT-RF', 'SMB', 'HML']].astype(float))
y = df_ff3['car_30d']

m = sm.OLS(y, X).fit(cov_type='HC3')

print(f"\n" + "=" * 90)
print("FF3 RESULTS (30-day CAR)")
print(f"=" * 90 + "\n")

print(f"H1 (Immediate):  {m.params['immediate_disclosure']:>8.4f}% (SE={m.bse['immediate_disclosure']:.4f}, p={m.pvalues['immediate_disclosure']:.4f})")
print(f"H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (SE={m.bse['fcc_reportable']:.4f}, p={m.pvalues['fcc_reportable']:.4f})")
print(f"H3 (Prior):      {m.params['prior_breaches_1yr']:>8.4f}% (SE={m.bse['prior_breaches_1yr']:.4f}, p={m.pvalues['prior_breaches_1yr']:.4f})")
print(f"H4 (Health):     {m.params['health_breach']:>8.4f}% (SE={m.bse['health_breach']:.4f}, p={m.pvalues['health_breach']:.4f})")
print(f"R²: {m.rsquared:.4f}")

# Compare all factor models
print(f"\n" + "=" * 90)
print("COMPARISON: All Factor Model Specifications")
print(f"=" * 90)

print(f"""
Market-Adjusted (N=648):
  H2: -2.0593% (p=0.0577)

FF3 (N={len(df_ff3)}):
  H2: {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})

Carhart 4F (N=519):
  H2: -2.1415% (p=0.1049)

FF5 (N=519):
  H2: -2.1967% (p=0.0951)

Coefficient trajectory: -2.06% → FF3 → -2.14% → -2.20%
Pattern: Stable coefficient, declining precision with model complexity
""")

