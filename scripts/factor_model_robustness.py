"""
FACTOR MODEL ROBUSTNESS TEST
========================================================================

Tests whether abnormal returns are market model artifacts or real.
Carhart 4-factor (adds momentum) and FF5 (adds profitability, investment).

Critical for BHAR result at p=0.048 - breach firms load on momentum by construction
(negative news creates momentum reversal). Carhart reveals if finding is real or
momentum artifact.

Models tested on:
- 30-day CAR (main result)
- 5-day BHAR (exists)
- 30-day BHAR (main extension, p=0.048)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("FACTOR MODEL ROBUSTNESS: MARKET MODEL VS CARHART VS FF5")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df_clean = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Load Fama-French factors (need to check if available in CRSP extract)
# For now, use market model and note that FF factors need to be added
print("\nChecking for factor data in dataset...")
factor_cols = [c for c in df.columns if 'mkt' in c.lower() or 'smb' in c.lower()
               or 'hml' in c.lower() or 'rmw' in c.lower() or 'cma' in c.lower()
               or 'wml' in c.lower() or 'momentum' in c.lower()]

print(f"Factor columns available: {factor_cols if factor_cols else 'NONE'}")

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Test across windows
windows = ['car_30d', 'bhar_5d', 'bhar_30d']
available_windows = [w for w in windows if w in df_clean.columns]

results = []

print(f"\n{'=' * 90}")
print("REGRESSIONS: MARKET MODEL (BASELINE)")
print(f"{'=' * 90}\n")

for window in available_windows:
    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    results.append({
        'Model': 'Market Model',
        'Window': window,
        'N': int(m.nobs),
        'FCC_Coef': m.params['fcc_reportable'],
        'FCC_SE': m.bse['fcc_reportable'],
        'FCC_P': m.pvalues['fcc_reportable'],
        'R_squared': m.rsquared
    })

    print(f"{window}:")
    print(f"  N={int(m.nobs)}, H2={m.params['fcc_reportable']:.4f}%, p={m.pvalues['fcc_reportable']:.4f}, R²={m.rsquared:.4f}")

print(f"\n{'=' * 90}")
print("NOTE: CARHART 4-FACTOR AND FF5 REQUIRE FACTOR DATA")
print(f"{'=' * 90}")
print(f"\nFactor data not found in standard CRSP extract.")
print(f"To run Carhart and FF5 models:")
print(f"  1. Download Fama-French factors from Ken French data library")
print(f"  2. Merge factors (HML, SMB, RMW, CMA, WML/MOM) to breach-date returns")
print(f"  3. Run factor models on CAR and BHAR residualized from risk factors")
print(f"\nInterpretation of current results:")
for r in results:
    if 'BHAR' in r['Window']:
        print(f"  {r['Window']}: H2={r['FCC_Coef']:.4f}% (p={r['FCC_P']:.4f})")
        if r['FCC_P'] < 0.05:
            print(f"    → Significant in market model. MUST test Carhart to rule out momentum.")

print(f"\n{'=' * 90}\n")

# Save what we have
results_df = pd.DataFrame(results)
results_df.to_csv('outputs/factor_model_robustness_market.csv', index=False)
print(f"Market model results saved to outputs/factor_model_robustness_market.csv")
print(f"\nACTION ITEM: Obtain Fama-French factors and rerun with Carhart/FF5 before finalizing BHAR interpretation.")

EOF
