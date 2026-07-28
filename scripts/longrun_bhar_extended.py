"""
LONG-RUN BHAR EXTENDED WINDOWS (60d, 90d)
========================================================================

Tests PERSISTENCE by extending beyond 30-day CAR horizon.
30-day BHAR is measurement robustness (vs CAR), not persistence.
60/90-day BHAR tests whether penalty persists over longer holding periods.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("EXTENDED BHAR WINDOWS: TRUE PERSISTENCE TEST")
print("=" * 90)

# Load data and CRSP
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv')

df['breach_date'] = pd.to_datetime(df['breach_date'])
crsp['date'] = pd.to_datetime(crsp['date'])

controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

def calculate_bhar(ticker, event_date, crsp_data, days):
    """
    Calculate Buy-and-Hold Abnormal Return over specified days
    """
    try:
        ticker_crsp = crsp_data[crsp_data['ticker'] == ticker].copy()
        ticker_crsp = ticker_crsp.sort_values('date').reset_index(drop=True)

        event_idx = ticker_crsp[ticker_crsp['date'] == event_date].index
        if len(event_idx) == 0:
            return np.nan
        event_idx = event_idx[0]

        # Event window: event_date to +days
        evt_end = min(len(ticker_crsp) - 1, event_idx + days)

        if evt_end - event_idx < days * 0.8:  # Need at least 80% of days
            return np.nan

        # Firm BHAR
        firm_ret = ticker_crsp.iloc[event_idx:evt_end]['ret'].values
        if len(firm_ret) < 5:
            return np.nan
        firm_bhar = np.prod(1 + firm_ret) - 1

        # Market BHAR (using VW index proxy from returns)
        market_ret = ticker_crsp.iloc[event_idx:evt_end]['vwretd'].values
        if len(market_ret) == 0:
            market_ret = np.zeros(len(firm_ret))
        market_bhar = np.prod(1 + market_ret) - 1

        return (firm_bhar - market_bhar) * 100  # Convert to percentage

    except Exception as e:
        return np.nan

# Calculate 60d and 90d BHAR
print(f"\nCalculating 60-day and 90-day BHAR for {len(df)} observations...")
bhar_60d = []
bhar_90d = []

for idx, row in df.iterrows():
    bhar_60 = calculate_bhar(row['Map'], row['breach_date'], crsp, 60)
    bhar_90 = calculate_bhar(row['Map'], row['breach_date'], crsp, 90)

    bhar_60d.append(bhar_60)
    bhar_90d.append(bhar_90)

    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1}/{len(df)}")

df['bhar_60d'] = bhar_60d
df['bhar_90d'] = bhar_90d

# Run regressions across all windows
windows = {
    'bhar_5d': 'Strategy 5-day',
    'bhar_30d': 'Strategy 30-day (CAR comparison)',
    'bhar_60d': 'Persistence 60-day',
    'bhar_90d': 'Persistence 90-day'
}

results = []
print(f"\n{'=' * 90}")
print("REGRESSION RESULTS ACROSS WINDOWS")
print(f"{'=' * 90}\n")

for window, label in windows.items():
    if window not in df.columns:
        continue

    df_clean = df.dropna(subset=[window] + controls)
    if len(df_clean) < 50:
        continue

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    results.append({
        'Window': label,
        'Days': int(window.split('_')[1].replace('d', '')),
        'N': int(m.nobs),
        'FCC_Coef': m.params['fcc_reportable'],
        'FCC_SE': m.bse['fcc_reportable'],
        'FCC_P': m.pvalues['fcc_reportable'],
        'R_squared': m.rsquared
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

print(f"\n{'=' * 90}")
print("PERSISTENCE ASSESSMENT")
print(f"{'=' * 90}\n")

# Analyze trajectory
print("FCC Coefficient Trajectory:")
for r in results:
    print(f"  {r['Window']:40s}: {r['FCC_Coef']:>8.4f}% (p={r['FCC_P']:.4f})")

# Check for persistence vs mean reversion
fcc_coefs = [r['FCC_Coef'] for r in results if 'Persistence' in r['Window']]
if fcc_coefs:
    print(f"\nPersistence findings:")
    if all(c < 0 for c in fcc_coefs):
        print(f"  PERSISTS: Negative coefficient holds at 60d and 90d")
        if abs(fcc_coefs[-1]) < abs(fcc_coefs[0]):
            print(f"  DECAY: Magnitude declines over time (mean reversion)")
        else:
            print(f"  STABLE: Magnitude stable or increases (no mean reversion)")
    else:
        print(f"  REVERSAL: Coefficient sign changes or becomes positive")

results_df.to_csv('outputs/longrun_bhar_extended_results.csv', index=False)
print(f"\nResults saved to outputs/longrun_bhar_extended_results.csv")

EOF
