"""
FACTOR MODEL ROBUSTNESS: MARKET MODEL, CARHART 4-FACTOR, FF5
========================================================================

Tests H1-H4 under three models:
1. Market model (baseline, what we have)
2. Carhart 4-factor (market + SMB + HML + Mom) - tests momentum artifact
3. Fama-French 5-factor (market + SMB + HML + RMW + CMA)

Factors pulled from Ken French data library (same source already used
for prior analysis, cited as French 2025).

Critical for BHAR at p=0.048: breach firms load on momentum by construction
(negative news → momentum reversal). Carhart 4-factor reveals if result
is real abnormal return or momentum artifact.

Windows tested: 30-day CAR, 5-day BHAR, 30-day BHAR
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("FACTOR MODEL ROBUSTNESS TEST")
print("=" * 90)

# Load breach data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print(f"\nBreaches dataset: {len(df)} observations")

# Try to load Fama-French factors from data directory
print("\nAttempting to load Fama-French factors...")

factor_file = 'Data/wrds/fama_french_factors.csv'
try:
    factors = pd.read_csv(factor_file)
    factors['date'] = pd.to_datetime(factors['date'])
    print(f"  [OK] Fama-French factors loaded from {factor_file}")
    print(f"      Columns: {', '.join([c for c in factors.columns if c != 'date'])}")
except FileNotFoundError:
    print(f"  [WARNING] Factor file not found at {factor_file}")
    print(f"\n  To download from Ken French data library:")
    print(f"  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
    print(f"\n  Required files:")
    print(f"    1. F-F_Research_Data_Factors_daily.CSV (contains Mkt-RF, SMB, HML)")
    print(f"    2. F-F_Momentum_Factor_daily.CSV (contains Mom/WML)")
    print(f"    3. F-F_Research_Data_5_Factors_2x3_daily.CSV (contains RMW, CMA)")
    print(f"\n  These should be merged on date and placed in Data/wrds/fama_french_factors.csv")
    print(f"\n  Script will proceed with MARKET MODEL ONLY (baseline).")
    factors = None

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Windows to test
windows = [
    ('car_30d', '30-day CAR (main result)'),
    ('bhar_5d', '5-day BHAR'),
    ('bhar_30d', '30-day BHAR (significance at p=0.048)')
]

available_windows = [(w, l) for w, l in windows if w in df.columns]

results_list = []

print(f"\n{'=' * 90}")
print("MARKET MODEL (BASELINE)")
print(f"{'=' * 90}\n")

for window_col, window_label in available_windows:
    df_clean = df.dropna(subset=[window_col] + controls)

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window_col]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    print(f"{window_label} (N={int(m.nobs)}):")
    print(f"  H1 (Immediate):  {m.params['immediate_disclosure']:>8.4f}% (p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  H3 (Prior):      {m.params['prior_breaches_1yr']:>8.4f}% (p={m.pvalues['prior_breaches_1yr']:.4f})")
    print(f"  H4 (Health):     {m.params['health_breach']:>8.4f}% (p={m.pvalues['health_breach']:.4f})")
    print(f"  R²: {m.rsquared:.4f}\n")

    results_list.append({
        'Model': 'Market Model',
        'Window': window_label,
        'Window_Col': window_col,
        'N': int(m.nobs),
        'H1_Coef': m.params['immediate_disclosure'],
        'H1_P': m.pvalues['immediate_disclosure'],
        'H2_Coef': m.params['fcc_reportable'],
        'H2_SE': m.bse['fcc_reportable'],
        'H2_P': m.pvalues['fcc_reportable'],
        'H3_Coef': m.params['prior_breaches_1yr'],
        'H3_P': m.pvalues['prior_breaches_1yr'],
        'H4_Coef': m.params['health_breach'],
        'H4_P': m.pvalues['health_breach'],
        'R2': m.rsquared
    })

# Carhart and FF5 models (if factors available)
if factors is not None:
    print(f"{'=' * 90}")
    print("CARHART 4-FACTOR MODEL (adds Momentum)")
    print(f"{'=' * 90}\n")

    # Merge factors to breach dates
    df_factors = df.merge(factors, left_on='breach_date', right_on='date', how='left')

    # Check factor coverage
    factor_cols = [c for c in ['MOM', 'Mom', 'WML', 'Momentum'] if c in factors.columns]
    if not factor_cols:
        print("[WARNING] Momentum factor column not found. Check factor file column names.")
    else:
        print(f"[OK] Momentum factor found: {factor_cols[0]}")

    # Carhart models on available windows
    for window_col, window_label in available_windows:
        # Build dataset with factor controls
        required_cols = [window_col] + controls + ['MKT-RF', 'SMB', 'HML'] + factor_cols
        df_carhart = df_factors.dropna(subset=required_cols)

        if len(df_carhart) < 50:
            print(f"{window_label}: Insufficient data with factors (n={len(df_carhart)})")
            continue

        X = sm.add_constant(df_carhart[controls + ['MKT-RF', 'SMB', 'HML'] + factor_cols].astype(float))
        y = df_carhart[window_col]
        m = sm.OLS(y, X).fit(cov_type='HC3')

        print(f"{window_label} (N={int(m.nobs)}):")
        print(f"  H1 (Immediate):  {m.params['immediate_disclosure']:>8.4f}% (p={m.pvalues['immediate_disclosure']:.4f})")
        print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")
        print(f"  H3 (Prior):      {m.params['prior_breaches_1yr']:>8.4f}% (p={m.pvalues['prior_breaches_1yr']:.4f})")
        print(f"  H4 (Health):     {m.params['health_breach']:>8.4f}% (p={m.pvalues['health_breach']:.4f})")
        print(f"  R²: {m.rsquared:.4f}\n")

        results_list.append({
            'Model': 'Carhart 4F',
            'Window': window_label,
            'Window_Col': window_col,
            'N': int(m.nobs),
            'H1_Coef': m.params['immediate_disclosure'],
            'H1_P': m.pvalues['immediate_disclosure'],
            'H2_Coef': m.params['fcc_reportable'],
            'H2_SE': m.bse['fcc_reportable'],
            'H2_P': m.pvalues['fcc_reportable'],
            'H3_Coef': m.params['prior_breaches_1yr'],
            'H3_P': m.pvalues['prior_breaches_1yr'],
            'H4_Coef': m.params['health_breach'],
            'H4_P': m.pvalues['health_breach'],
            'R2': m.rsquared
        })

    print(f"{'=' * 90}")
    print("FF5 MODEL (Fama-French 5-Factor)")
    print(f"{'=' * 90}\n")

    # FF5 models on available windows
    for window_col, window_label in available_windows:
        required_cols = [window_col] + controls + ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA']
        df_ff5 = df_factors.dropna(subset=required_cols)

        if len(df_ff5) < 50:
            print(f"{window_label}: Insufficient data with FF5 (n={len(df_ff5)})")
            continue

        X = sm.add_constant(df_ff5[controls + ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA']].astype(float))
        y = df_ff5[window_col]
        m = sm.OLS(y, X).fit(cov_type='HC3')

        print(f"{window_label} (N={int(m.nobs)}):")
        print(f"  H1 (Immediate):  {m.params['immediate_disclosure']:>8.4f}% (p={m.pvalues['immediate_disclosure']:.4f})")
        print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")
        print(f"  H3 (Prior):      {m.params['prior_breaches_1yr']:>8.4f}% (p={m.pvalues['prior_breaches_1yr']:.4f})")
        print(f"  H4 (Health):     {m.params['health_breach']:>8.4f}% (p={m.pvalues['health_breach']:.4f})")
        print(f"  R²: {m.rsquared:.4f}\n")

        results_list.append({
            'Model': 'FF5',
            'Window': window_label,
            'Window_Col': window_col,
            'N': int(m.nobs),
            'H1_Coef': m.params['immediate_disclosure'],
            'H1_P': m.pvalues['immediate_disclosure'],
            'H2_Coef': m.params['fcc_reportable'],
            'H2_SE': m.bse['fcc_reportable'],
            'H2_P': m.pvalues['fcc_reportable'],
            'H3_Coef': m.params['prior_breaches_1yr'],
            'H3_P': m.pvalues['prior_breaches_1yr'],
            'H4_Coef': m.params['health_breach'],
            'H4_P': m.pvalues['health_breach'],
            'R2': m.rsquared
        })

else:
    print(f"\n{'=' * 90}")
    print("CARHART 4-FACTOR AND FF5 MODELS")
    print(f"{'=' * 90}\n")
    print("[ACTION REQUIRED] Factor data not found.")
    print("To complete factor model testing:")
    print("  1. Download from Ken French data library (link provided above)")
    print("  2. Merge factors on date and save to Data/wrds/fama_french_factors.csv")
    print("  3. Rerun this script")
    print("\nThe market model results above are complete. Factor models will add robustness.")

# Save results
results_df = pd.DataFrame(results_list)
results_df.to_csv('outputs/factor_model_robustness_results.csv', index=False)

print(f"\n{'=' * 90}")
print("SUMMARY")
print(f"{'=' * 90}\n")

if len(results_df) > 0:
    print("Results saved to outputs/factor_model_robustness_results.csv")
    print("\nInterpretation priorities:")
    print("  - BHAR 30d (p=0.048): Test with Carhart to rule out momentum artifact")
    print("  - If H2 p-value INCREASES under Carhart, finding is partly momentum-driven")
    print("  - If H2 p-value unchanged, finding is robust to momentum risk factor")
    print("  - FF5 tests full profitability and investment risk factor exposure")

