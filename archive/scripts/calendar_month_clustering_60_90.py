"""
CALENDAR-MONTH CLUSTERING: MITCHELL-STAFFORD CORRECTION
========================================================================

Tests whether 60d/90d CAR results survive calendar-month clustering
of standard errors on the full sample. This directly addresses cross-
correlation from overlapping event windows without sample restriction.

If results hold: reportable with documented robustness check.
If results fail: clean answer to drop longer horizons.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
import scipy as sp
import scipy.stats

print("=" * 90)
print("CALENDAR-MONTH CLUSTERING: MITCHELL-STAFFORD ROBUSTNESS TEST")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

# Load CAR at 60d/90d
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv', parse_dates=['date'])
market = pd.read_csv('Data/wrds/market_indices.csv', parse_dates=['date'])

crsp_market = crsp.merge(market[['date', 'vwretd']], on='date', how='left')

# Calculate CAR at 60 and 90 days
def calculate_car_extended(ticker, breach_date, crsp_data, max_days=90):
    """Calculate CAR from daily abnormal returns to specified horizon"""
    try:
        from datetime import timedelta
        ticker_data = crsp_data[crsp_data['ticker'] == ticker].copy()
        if len(ticker_data) == 0:
            return {60: np.nan, 90: np.nan}

        ticker_data = ticker_data.sort_values('date').reset_index(drop=True)

        # Find breach date in returns
        date_diff = (ticker_data['date'] - breach_date).abs()
        if date_diff.min() > timedelta(days=2):
            return {60: np.nan, 90: np.nan}

        event_idx = date_diff.idxmin()

        # Calculate abnormal returns
        ticker_data['abnormal_ret'] = ticker_data['ret'] - ticker_data['vwretd']
        ticker_data['abnormal_ret'] = ticker_data['abnormal_ret'] * 100

        results = {}
        for horizon_days in [60, 90]:
            end_idx = min(len(ticker_data) - 1, event_idx + horizon_days)

            if (end_idx - event_idx) < (horizon_days * 0.8):
                results[horizon_days] = np.nan
            else:
                car = ticker_data.iloc[event_idx:end_idx + 1]['abnormal_ret'].sum()
                results[horizon_days] = car

        return results

    except Exception as e:
        return {60: np.nan, 90: np.nan}

print("\nCalculating CAR at 60d and 90d...")
car_60d = []
car_90d = []

for idx, row in df.iterrows():
    cars = calculate_car_extended(row['Map'], row['breach_date'], crsp_market)
    car_60d.append(cars[60])
    car_90d.append(cars[90])

    if (idx + 1) % 200 == 0:
        print(f"  Processed {idx + 1}/{len(df)}")

df['car_60d'] = car_60d
df['car_90d'] = car_90d

# Add calendar month for clustering
df['calendar_month'] = df['breach_date'].dt.to_period('M')

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

print(f"\n" + "=" * 90)
print("RESULTS WITH CALENDAR-MONTH CLUSTERING")
print(f"=" * 90)

def run_regression_clustered(df_clean, y_col, controls, window_name):
    """Run OLS with calendar-month clustering"""

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[y_col]

    m = sm.OLS(y, X).fit()

    # Manual clustering using statsmodels function
    groups = pd.factorize(df_clean['calendar_month'])[0]

    # Get clustered covariance matrix
    cov_clu = cov_cluster(m, group=groups)

    # Compute clustered standard errors and t-stats
    se_clu = np.sqrt(np.diag(cov_clu))
    t_clu = m.params / se_clu
    p_clu = 2 * (1 - sp.stats.t.cdf(np.abs(t_clu), df=m.df_resid))

    return {
        'window': window_name,
        'n': len(df_clean),
        'n_months': len(df_clean['calendar_month'].unique()),
        'params': m.params,
        'se_clustered': se_clu,
        't_stats': t_clu,
        'p_values': p_clu,
        'r2': m.rsquared
    }

# Run for both 60d and 90d
results_clustered = []

for window_col, window_name in [('car_60d', '60-day CAR'), ('car_90d', '90-day CAR')]:
    df_clean = df.dropna(subset=[window_col] + controls).copy()
    df_clean = df_clean.reset_index(drop=True)

    res = run_regression_clustered(df_clean, window_col, controls, window_name)

    print(f"\n{window_name} (N={res['n']}, clustered by {res['n_months']} calendar months)")
    print(f"  H1 (Immediate):  {res['params']['immediate_disclosure']:>8.4f}% (SE={res['se_clustered'][1]:.4f}, p={res['p_values'][1]:.4f})")
    print(f"  H2 (FCC):        {res['params']['fcc_reportable']:>8.4f}% (SE={res['se_clustered'][2]:.4f}, p={res['p_values'][2]:.4f})")
    print(f"  H3 (Prior):      {res['params']['prior_breaches_1yr']:>8.4f}% (SE={res['se_clustered'][3]:.4f}, p={res['p_values'][3]:.4f})")
    print(f"  H4 (Health):     {res['params']['health_breach']:>8.4f}% (SE={res['se_clustered'][4]:.4f}, p={res['p_values'][4]:.4f})")
    print(f"  R²: {res['r2']:.4f}")

    results_clustered.append({
        'Window': window_name,
        'N': res['n'],
        'N_Months': res['n_months'],
        'H1_Coef': res['params']['immediate_disclosure'],
        'H1_SE_Clustered': res['se_clustered'][1],
        'H1_P_Clustered': res['p_values'][1],
        'H2_Coef': res['params']['fcc_reportable'],
        'H2_SE_Clustered': res['se_clustered'][2],
        'H2_P_Clustered': res['p_values'][2],
        'H3_Coef': res['params']['prior_breaches_1yr'],
        'H3_SE_Clustered': res['se_clustered'][3],
        'H3_P_Clustered': res['p_values'][3],
        'H4_Coef': res['params']['health_breach'],
        'H4_SE_Clustered': res['se_clustered'][4],
        'H4_P_Clustered': res['p_values'][4],
        'R2': res['r2']
    })

# Compare to 30d baseline
print(f"\n" + "=" * 90)
print("COMPARISON: 30-DAY BASELINE (HC3)")
print(f"=" * 90)

df_clean = df.dropna(subset=['car_30d'] + controls)
X = sm.add_constant(df_clean[controls].astype(float))
y = df_clean['car_30d']
m = sm.OLS(y, X).fit(cov_type='HC3')

print(f"\n30-day CAR (N={len(df_clean)}, HC3 robust)")
print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (SE={m.bse['fcc_reportable']:.4f}, p={m.pvalues['fcc_reportable']:.4f})")

# Summary table
print(f"\n" + "=" * 90)
print("SUMMARY: H2 FCC EFFECT ACROSS WINDOWS AND SE SPECIFICATIONS")
print(f"=" * 90)

summary_data = [
    {
        'Window': '30d CAR',
        'SE Method': 'HC3',
        'H2 Coef': m.params['fcc_reportable'],
        'H2 SE': m.bse['fcc_reportable'],
        'H2 p-value': m.pvalues['fcc_reportable'],
        'Verdict': 'Baseline'
    }
]

for res in results_clustered:
    summary_data.append({
        'Window': res['Window'],
        'SE Method': 'Calendar-Month Clustered',
        'H2 Coef': res['H2_Coef'],
        'H2 SE': res['H2_SE_Clustered'],
        'H2 p-value': res['H2_P_Clustered'],
        'Verdict': 'Significant' if res['H2_P_Clustered'] < 0.05 else 'Not Sig'
    })

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

# Interpretation
print(f"\n" + "=" * 90)
print("INTERPRETATION")
print(f"=" * 90)

print(f"""
The question: Do 60-day and 90-day results survive calendar-month clustering
that addresses the Mitchell-Stafford cross-correlation problem?

Key findings:
1. If p-values STAY BELOW 0.05 with clustering: result is reportable
2. If p-values RISE ABOVE 0.05 with clustering: longer horizons unreliable
3. The magnitude of SE change indicates the severity of clustering bias

Decision rule:
- If 60d and 90d hold significance with calendar clustering, report with caveat
- If either fails, drop longer horizons due to methodological concern
""")

# Save results
results_df = pd.DataFrame(results_clustered)
results_df.to_csv('outputs/calendar_month_clustering_results.csv', index=False)
print(f"\nDetailed results saved to: outputs/calendar_month_clustering_results.csv")

