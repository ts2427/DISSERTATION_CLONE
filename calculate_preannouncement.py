import pandas as pd
import numpy as np
from datetime import timedelta
import statsmodels.api as sm

print("=" * 90)
print("PRE-ANNOUNCEMENT LEAKAGE TEST - 648 SAMPLE")
print("=" * 90)

# Load data
breaches = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv', parse_dates=['date'])
market = pd.read_csv('Data/wrds/market_indices.csv', parse_dates=['date'])

# Prepare regression sample (648)
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']
df_base = breaches[breaches['car_30d'].notna()].dropna(subset=controls).copy()
df_base['breach_date'] = pd.to_datetime(df_base['breach_date'])

print("\nBase sample: N = {}".format(len(df_base)))

# Merge CRSP with market data
crsp_market = crsp.merge(market[['date', 'vwretd']], on='date', how='left')
crsp_market['abnormal_ret'] = (crsp_market['ret'] - crsp_market['vwretd']) * 100

# Calculate pre-announcement returns for each breach
def calculate_preannouncement(ticker, breach_date, crsp_data, window_days=5):
    """
    Calculate abnormal returns in pre-announcement window [-5, -1] days
    """
    try:
        ticker_data = crsp_data[crsp_data['ticker'] == ticker].copy()
        if len(ticker_data) < 100:
            return None

        ticker_data = ticker_data.sort_values('date').reset_index(drop=True)

        # Find event date index
        date_diffs = abs(ticker_data['date'] - breach_date)
        if date_diffs.min() > timedelta(days=5):
            return None  # Event date too far from available data

        event_idx = date_diffs.idxmin()

        # Pre-announcement window: [-5, -1] trading days
        pre_start_idx = max(0, event_idx - window_days)
        pre_end_idx = max(0, event_idx - 1)

        if pre_end_idx <= pre_start_idx:
            return None

        pre_window = ticker_data.iloc[pre_start_idx:pre_end_idx + 1]

        if len(pre_window) < 3:  # Need at least 3 days
            return None

        car_pre = pre_window['abnormal_ret'].sum()
        mean_pre = pre_window['abnormal_ret'].mean()

        return {
            'car_m5_m1': car_pre,
            'mean_pre': mean_pre,
            'n_trading_days': len(pre_window),
            'has_predata': True
        }

    except Exception as e:
        return None

# Calculate pre-announcement for each breach
print("\nCalculating pre-announcement windows...")
preannounce_results = []
success = 0

for idx, row in df_base.iterrows():
    ticker = row['Map']
    breach_date = row['breach_date']

    if pd.isna(ticker) or pd.isna(breach_date):
        preannounce_results.append({
            'car_m5_m1': np.nan,
            'has_predata': False
        })
        continue

    result = calculate_preannouncement(ticker, breach_date, crsp_market)
    if result:
        preannounce_results.append(result)
        success += 1
    else:
        preannounce_results.append({
            'car_m5_m1': np.nan,
            'has_predata': False
        })

    if (idx + 1) % 100 == 0:
        print("  Processed {}/{} ({} with pre-announcement data)".format(
            idx + 1, len(df_base), success))

df_base['car_m5_m1'] = [r.get('car_m5_m1', np.nan) for r in preannounce_results]
df_base['has_predata'] = [r.get('has_predata', False) for r in preannounce_results]

print("\n" + "=" * 90)
print("PRE-ANNOUNCEMENT RESULTS")
print("=" * 90)

# Sample with pre-announcement data
df_pre = df_base[df_base['has_predata']].copy()
n_pre = len(df_pre)

print("\nSample size with pre-announcement data: N = {}".format(n_pre))
print("(Original sample: N = {}, {} without pre-data)".format(
    len(df_base), len(df_base) - n_pre))

if n_pre > 0:
    # Regression test
    X_pre = sm.add_constant(df_pre[controls].astype(float))
    y_pre = df_pre['car_m5_m1']
    m_pre = sm.OLS(y_pre, X_pre).fit(cov_type='HC3')

    mean_pre = df_pre['car_m5_m1'].mean()
    const_pval = m_pre.pvalues['const']

    print("\nMean abnormal return [-5, -1]: {:.4f}%".format(mean_pre))
    print("Standard deviation: {:.4f}".format(df_pre['car_m5_m1'].std()))
    print("T-statistic (const): {:.4f}".format(m_pre.params['const'] / m_pre.bse['const']))
    print("P-value (two-sided): {:.4f}".format(const_pval))

    if const_pval < 0.05:
        print("\nResult: SIGNIFICANT pre-announcement movement (p < 0.05)")
    elif const_pval < 0.10:
        print("\nResult: Marginal pre-announcement movement (p < 0.10)")
    else:
        print("\nResult: NO significant pre-announcement movement (p >= 0.10)")

    # Check other pre-windows if desired
    print("\n" + "-" * 90)
    print("Testing other pre-announcement windows...")
    print("-" * 90)

    # Test [-10, -1]
    pre_10_1 = []
    for idx, row in df_base.iterrows():
        ticker = row['Map']
        breach_date = row['breach_date']

        if pd.isna(ticker) or pd.isna(breach_date):
            pre_10_1.append(np.nan)
            continue

        try:
            ticker_data = crsp_market[crsp_market['ticker'] == ticker].copy()
            if len(ticker_data) < 100:
                pre_10_1.append(np.nan)
                continue

            ticker_data = ticker_data.sort_values('date').reset_index(drop=True)
            date_diffs = abs(ticker_data['date'] - breach_date)
            event_idx = date_diffs.idxmin()

            pre_start = max(0, event_idx - 10)
            pre_end = max(0, event_idx - 1)

            if pre_end <= pre_start:
                pre_10_1.append(np.nan)
            else:
                car = ticker_data.iloc[pre_start:pre_end + 1]['abnormal_ret'].sum()
                pre_10_1.append(car)
        except:
            pre_10_1.append(np.nan)

    df_base['car_m10_m1'] = pre_10_1
    df_pre10 = df_base.dropna(subset=['car_m10_m1'])

    if len(df_pre10) > 0:
        X_pre10 = sm.add_constant(df_pre10[controls].astype(float))
        y_pre10 = df_pre10['car_m10_m1']
        m_pre10 = sm.OLS(y_pre10, X_pre10).fit(cov_type='HC3')

        print("\nWindow [-10, -1]:")
        print("  N: {}".format(len(df_pre10)))
        print("  Mean: {:.4f}%".format(df_pre10['car_m10_m1'].mean()))
        print("  P-value: {:.4f}".format(m_pre10.pvalues['const']))

print("\n" + "=" * 90)

