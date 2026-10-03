"""
EXTENDED BHAR WINDOWS: 60-DAY AND 90-DAY PERSISTENCE TEST
========================================================================

Daily returns already exist in CRSP to compute 90-day window (if Table 5
reports CAR at 90 days, daily data extends to +90).

BHAR = compounded return (vs CAR = summed return) over same period.
Window definitions: [-5, +60] and [-5, +90] trading days.

30-day BHAR is measurement robustness (vs 30-day CAR), not persistence.
60/90-day results show whether penalty persists or decays.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("EXTENDED BHAR: 60-DAY AND 90-DAY PERSISTENCE TEST")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv')

# Convert to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'])
crsp['date'] = pd.to_datetime(crsp['date'])

# Sort for efficient lookups
crsp_sorted = crsp.sort_values(['ticker', 'date']).reset_index(drop=True)

print(f"\nDataset: {len(df)} breaches")
print(f"CRSP daily returns: {len(crsp)} observations ({crsp['date'].min().date()} to {crsp['date'].max().date()})")

def calculate_bhar_window(ticker, event_date, crsp_data, window_days=60):
    """
    Calculate Buy-and-Hold Abnormal Return
    Event window: [-5, +window_days] trading days
    Returns BHAR as percentage
    """
    try:
        # Get ticker data
        ticker_data = crsp_data[crsp_data['ticker'] == ticker].copy()
        if len(ticker_data) == 0:
            return np.nan

        ticker_data = ticker_data.sort_values('date').reset_index(drop=True)

        # Find event date index
        event_dates = ticker_data[ticker_data['date'] == event_date].index.tolist()
        if len(event_dates) == 0:
            # Try to find closest date within 2 days
            date_diff = (ticker_data['date'] - event_date).abs()
            if date_diff.min() <= timedelta(days=2):
                event_idx = date_diff.idxmin()
            else:
                return np.nan
        else:
            event_idx = event_dates[0]

        # Event window: [-5, +window_days] trading days
        # -5 is 5 trading days before event
        event_start_idx = max(0, event_idx - 5)
        event_end_idx = min(len(ticker_data) - 1, event_idx + window_days)

        # Need sufficient data
        if (event_end_idx - event_idx) < (window_days * 0.8):
            return np.nan

        # Firm returns (compound from -5 to +window_days)
        firm_returns = ticker_data.iloc[event_start_idx:event_end_idx + 1]['ret'].values
        if len(firm_returns) < 5:
            return np.nan

        firm_bhar = (np.prod(1 + firm_returns) - 1) * 100

        # Market returns (using S&P 500 as benchmark)
        # For now, estimate market using median return of all stocks on those dates
        dates_in_window = ticker_data.iloc[event_start_idx:event_end_idx + 1]['date'].values
        market_data = crsp_data[crsp_data['date'].isin(dates_in_window)]

        if len(market_data) > 0:
            market_returns = market_data.groupby('date')['ret'].median().values
            market_bhar = (np.prod(1 + market_returns) - 1) * 100
        else:
            market_bhar = 0

        return firm_bhar - market_bhar

    except Exception as e:
        return np.nan

# Calculate extended BHAR windows
print(f"\nCalculating 60-day and 90-day BHAR...")

bhar_60d = []
bhar_90d = []

for idx, row in df.iterrows():
    bhar_60 = calculate_bhar_window(row['Map'], row['breach_date'], crsp_sorted, window_days=60)
    bhar_90 = calculate_bhar_window(row['Map'], row['breach_date'], crsp_sorted, window_days=90)

    bhar_60d.append(bhar_60)
    bhar_90d.append(bhar_90)

    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1}/{len(df)} ({(idx + 1) / len(df) * 100:.1f}%)")

df['bhar_60d'] = bhar_60d
df['bhar_90d'] = bhar_90d

# Data availability check
print(f"\nBHAR computation summary:")
print(f"  bhar_5d:   {df['bhar_5d'].notna().sum()} non-null")
print(f"  bhar_30d:  {df['bhar_30d'].notna().sum()} non-null")
print(f"  bhar_60d:  {df['bhar_60d'].notna().sum()} non-null (newly computed)")
print(f"  bhar_90d:  {df['bhar_90d'].notna().sum()} non-null (newly computed)")

# Canonical specification
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Regressions across windows
windows = [
    ('bhar_5d', 'BHAR 5-day'),
    ('bhar_30d', 'BHAR 30-day (CAR comparison)'),
    ('bhar_60d', 'BHAR 60-day (Persistence)'),
    ('bhar_90d', 'BHAR 90-day (Persistence)')
]

results = []

print(f"\n{'=' * 90}")
print("REGRESSION RESULTS: H1-H4 ACROSS WINDOWS")
print(f"{'=' * 90}\n")

for window_col, window_label in windows:
    df_clean = df.dropna(subset=[window_col] + controls)

    if len(df_clean) < 50:
        print(f"{window_label}: Insufficient observations (n={len(df_clean)})")
        continue

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window_col]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    results.append({
        'Window': window_label,
        'Window_Days': int(window_col.split('_')[1].replace('d', '')),
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

    print(f"{window_label} (N={int(m.nobs)}):")
    print(f"  H1 (Immediate): {m.params['immediate_disclosure']:>8.4f}% (p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  H2 (FCC):       {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  H3 (Prior):     {m.params['prior_breaches_1yr']:>8.4f}% (p={m.pvalues['prior_breaches_1yr']:.4f})")
    print(f"  H4 (Health):    {m.params['health_breach']:>8.4f}% (p={m.pvalues['health_breach']:.4f})")
    print(f"  R²: {m.rsquared:.4f}\n")

results_df = pd.DataFrame(results)

# Persistence assessment
print(f"{'=' * 90}")
print("PERSISTENCE ASSESSMENT")
print(f"{'=' * 90}\n")

if len(results) >= 4:
    print("FCC Coefficient (H2) Trajectory:")
    for r in results:
        print(f"  {r['Window']:40s}: {r['H2_Coef']:>8.4f}% (p={r['H2_P']:.4f})")

    coefs = [r['H2_Coef'] for r in results if 'Persistence' in r['Window']]

    print(f"\nPersistence finding:")
    if len(coefs) >= 2:
        print(f"  60-day coefficient:  {coefs[0]:.4f}%")
        print(f"  90-day coefficient:  {coefs[1]:.4f}%")

        if coefs[0] < 0 and coefs[1] < 0:
            print(f"  Pattern: PERSISTS - penalty holds at both 60d and 90d")
            if abs(coefs[1]) < abs(coefs[0]):
                print(f"  Decay: YES - magnitude decreases ({coefs[0]:.4f}% → {coefs[1]:.4f}%), suggesting mean reversion")
            else:
                print(f"  Decay: NO - magnitude stable or increases, suggesting persistent discount")
        elif coefs[0] < 0 and coefs[1] >= 0:
            print(f"  Pattern: REVERSAL - penalty reverses by 90 days")
        else:
            print(f"  Pattern: WEAK - insufficient evidence of persistence")

results_df.to_csv('outputs/extended_bhar_60d_90d_results.csv', index=False)
print(f"\n{'=' * 90}")
print(f"Results saved to outputs/extended_bhar_60d_90d_results.csv")

