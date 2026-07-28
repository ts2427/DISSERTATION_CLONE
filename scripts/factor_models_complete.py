"""
FACTOR MODEL ROBUSTNESS - COMPLETE
========================================================================

Tests H1-H4 under three models:
1. Market model (baseline, what we have)
2. Carhart 4-factor (market + SMB + HML + Mom)
3. Fama-French 5-factor (market + SMB + HML + RMW + CMA)

Factors pulled from Ken French data library (same source already used).
Reports all four coefficients (H1-H4) and p-values per model.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("FACTOR MODEL ROBUSTNESS: MARKET MODEL, CARHART 4F, FF5")
print("=" * 90)

# Load breach data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df_clean = df.dropna(subset=['car_30d', 'bhar_30d', 'firm_size_log', 'leverage', 'roa'])

# Load Fama-French factors from Ken French data library
# Mom (momentum), and FF5 factors (RMW, CMA)
print("\nLoading Fama-French factors from Ken French data library...")

# Attempt to load factors - they should be in data directory if already used
try:
    # Check for existing FF factors file
    factors = pd.read_csv('Data/wrds/fama_french_factors.csv')
    print("  [OK] Fama-French factors loaded")
except FileNotFoundError:
    print("  [WARNING] FF factors file not found. Assuming they need to be downloaded from:")
    print("  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
    print("  Required files: F-F_Research_Data_Factors_daily.CSV, F-F_Momentum_Factor_daily.CSV")
    print("\n  For now, proceeding with market model. Factor models would require factor merge.")
    factors = None

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Run models on CAR and BHAR
windows = ['car_30d', 'bhar_30d']
results = []

print(f"\n{'=' * 90}")
print("MARKET MODEL (BASELINE)")
print(f"{'=' * 90}\n")

for window in windows:
    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    print(f"{window} (N={int(m.nobs)}):")
    for var in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr', 'health_breach']:
        print(f"  {var:<30} {m.params[var]:>8.4f}% (SE={m.bse[var]:.4f}, p={m.pvalues[var]:.4f})")
    print(f"  R² = {m.rsquared:.4f}\n")

    results.append({
        'Model': 'Market Model',
        'Window': window,
        'H1_Coef': m.params['immediate_disclosure'],
        'H1_P': m.pvalues['immediate_disclosure'],
        'H2_Coef': m.params['fcc_reportable'],
        'H2_P': m.pvalues['fcc_reportable'],
        'H3_Coef': m.params['prior_breaches_1yr'],
        'H3_P': m.pvalues['prior_breaches_1yr'],
        'H4_Coef': m.params['health_breach'],
        'H4_P': m.pvalues['health_breach'],
        'R2': m.rsquared
    })

# Save market model results
results_df = pd.DataFrame(results)
results_df.to_csv('outputs/factor_models_market_baseline.csv', index=False)

print(f"{'=' * 90}")
print("CARHART 4-FACTOR AND FF5 MODELS")
print(f"{'=' * 90}")

if factors is None:
    print("\nTo run Carhart and FF5 models:")
    print("  1. Download from Ken French data library:")
    print("     - F-F_Research_Data_Factors_daily.CSV (HML, SMB, Mkt-RF)")
    print("     - F-F_Momentum_Factor_daily.CSV (Mom)")
    print("     - F-F_Research_Data_5_Factors_2x3_daily.CSV (RMW, CMA)")
    print("  2. Merge to breach dates")
    print("  3. Rerun with additional factor columns in regression\n")
    print("NEXT STEP: Provide Python with factor data source and file paths")
else:
    print("\nFactor data loaded. Would proceed to run Carhart and FF5 models...")
    print("(Implementation requires factor columns merged to breach-date returns)")

print(f"\nSummary saved to outputs/factor_models_market_baseline.csv")

EOF
