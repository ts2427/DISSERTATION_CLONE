"""
CORRECTED LONG-HORIZON ANALYSIS
========================================================================

Replaces BHAR with CAR (per Fama 1998) and addresses Mitchell-Stafford
overlap problem through two complementary approaches:

1. Calendar-month clustering of standard errors (keeps full sample)
2. Non-overlapping sample restriction (cleanest design)

Compares results across three specifications to assess robustness.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import timedelta

print("=" * 90)
print("CORRECTED LONG-HORIZON ANALYSIS: CAR WITH CLUSTERING & SAMPLE RESTRICTION")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

# We have CAR at 30d from the data; need to compute 60d and 90d from daily returns
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv', parse_dates=['date'])
market = pd.read_csv('Data/wrds/market_indices.csv', parse_dates=['date'])

# Merge market returns to CRSP
crsp_market = crsp.merge(market[['date', 'vwretd']], on='date', how='left')

print(f"\nSample composition:")
print(f"  Total breaches: {len(df)}")
print(f"  FCC breaches: {(df['fcc_reportable'] == True).sum()}")
print(f"  Non-FCC breaches: {(df['fcc_reportable'] == False).sum()}")

# Calculate CAR at 60 and 90 days
def calculate_car_extended(ticker, breach_date, crsp_data, max_days=90):
    """Calculate CAR from daily abnormal returns to specified horizon"""
    try:
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

            # Need at least 80% of days
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

print(f"  CAR 60d: {df['car_60d'].notna().sum()} observations")
print(f"  CAR 90d: {df['car_90d'].notna().sum()} observations")

# Add calendar month for clustering
df['calendar_month'] = df['breach_date'].dt.to_period('M')

# Canonical controls
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# SPECIFICATION 1: Full sample with calendar-month clustering
print(f"\n" + "=" * 90)
print("SPECIFICATION 1: FULL SAMPLE, CALENDAR-MONTH CLUSTERED STANDARD ERRORS")
print(f"=" * 90)

spec1_results = []

for window_name, window_col in [('60d CAR', 'car_60d'), ('90d CAR', 'car_90d')]:
    df_clean = df.dropna(subset=[window_col] + controls).copy()
    df_clean = df_clean.reset_index(drop=True)

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window_col]

    m = sm.OLS(y, X).fit()

    # Cluster by calendar month
    groups = pd.factorize(df_clean['calendar_month'])[0]

    # Use statsmodels' built-in clustering
    try:
        m_clu = m.get_robustcov_results(cov_type='cluster', groups=groups)

        print(f"\n{window_name} (N={len(df_clean)}):")
        print(f"  H1 (Immediate):  {m_clu.params['immediate_disclosure']:>8.4f}% (p={m_clu.pvalues['immediate_disclosure']:.4f})")
        print(f"  H2 (FCC):        {m_clu.params['fcc_reportable']:>8.4f}% (p={m_clu.pvalues['fcc_reportable']:.4f})")
        print(f"  H3 (Prior):      {m_clu.params['prior_breaches_1yr']:>8.4f}% (p={m_clu.pvalues['prior_breaches_1yr']:.4f})")
        print(f"  H4 (Health):     {m_clu.params['health_breach']:>8.4f}% (p={m_clu.pvalues['health_breach']:.4f})")

        spec1_results.append({
            'Specification': 'Full Sample',
            'Window': window_name,
            'N': len(df_clean),
            'Method': 'Calendar-Month Cluster',
            'H1_Coef': m_clu.params['immediate_disclosure'],
            'H1_P': m_clu.pvalues['immediate_disclosure'],
            'H2_Coef': m_clu.params['fcc_reportable'],
            'H2_P': m_clu.pvalues['fcc_reportable'],
            'H3_Coef': m_clu.params['prior_breaches_1yr'],
            'H3_P': m_clu.pvalues['prior_breaches_1yr'],
            'H4_Coef': m_clu.params['health_breach'],
            'H4_P': m_clu.pvalues['health_breach']
        })
    except Exception as e:
        print(f"\n{window_name}: Error with clustering - {str(e)}")
        print("  Proceeding with HC3 instead...")

        m = sm.OLS(y, X).fit(cov_type='HC3')

        print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f}) [HC3]")

        spec1_results.append({
            'Specification': 'Full Sample',
            'Window': window_name,
            'N': len(df_clean),
            'Method': 'HC3 (clustering failed)',
            'H1_Coef': m.params['immediate_disclosure'],
            'H1_P': m.pvalues['immediate_disclosure'],
            'H2_Coef': m.params['fcc_reportable'],
            'H2_P': m.pvalues['fcc_reportable'],
            'H3_Coef': m.params['prior_breaches_1yr'],
            'H3_P': m.pvalues['prior_breaches_1yr'],
            'H4_Coef': m.params['health_breach'],
            'H4_P': m.pvalues['health_breach']
        })

# SPECIFICATION 2: Non-overlapping sample (one breach per firm max)
print(f"\n" + "=" * 90)
print("SPECIFICATION 2: NON-OVERLAPPING SAMPLE (First breach per firm only)")
print(f"=" * 90)

# For each FCC firm, keep only first breach
df_nonoverlap = df[df['fcc_reportable'] == True].copy()
df_nonoverlap = df_nonoverlap.sort_values('breach_date')
df_nonoverlap = df_nonoverlap.drop_duplicates(subset=['cik'], keep='first')

# Add back non-FCC breaches
df_nonoverlap = pd.concat([
    df_nonoverlap,
    df[df['fcc_reportable'] == False].copy()
], ignore_index=True)

print(f"\nSample reduction:")
print(f"  Original FCC breaches: {(df['fcc_reportable'] == True).sum()}")
print(f"  Non-overlapping FCC: {(df_nonoverlap['fcc_reportable'] == True).sum()}")
print(f"  Total after restriction: {len(df_nonoverlap)}")

spec2_results = []

for window_name, window_col in [('60d CAR', 'car_60d'), ('90d CAR', 'car_90d')]:
    df_clean = df_nonoverlap.dropna(subset=[window_col] + controls)

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window_col]

    m = sm.OLS(y, X).fit(cov_type='HC3')

    print(f"\n{window_name} (N={len(df_clean)}):")
    print(f"  H1 (Immediate):  {m.params['immediate_disclosure']:>8.4f}% (p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  H2 (FCC):        {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  H3 (Prior):      {m.params['prior_breaches_1yr']:>8.4f}% (p={m.pvalues['prior_breaches_1yr']:.4f})")
    print(f"  H4 (Health):     {m.params['health_breach']:>8.4f}% (p={m.pvalues['health_breach']:.4f})")

    spec2_results.append({
        'Specification': 'Non-Overlapping',
        'Window': window_name,
        'N': len(df_clean),
        'Method': 'HC3 Robust',
        'H1_Coef': m.params['immediate_disclosure'],
        'H1_P': m.pvalues['immediate_disclosure'],
        'H2_Coef': m.params['fcc_reportable'],
        'H2_P': m.pvalues['fcc_reportable'],
        'H3_Coef': m.params['prior_breaches_1yr'],
        'H3_P': m.pvalues['prior_breaches_1yr'],
        'H4_Coef': m.params['health_breach'],
        'H4_P': m.pvalues['health_breach']
    })

# BASELINE: 30d CAR for comparison
print(f"\n" + "=" * 90)
print("BASELINE: 30-DAY CAR FOR COMPARISON")
print(f"=" * 90)

df_clean = df.dropna(subset=['car_30d'] + controls)
X = sm.add_constant(df_clean[controls].astype(float))
y = df_clean['car_30d']
m = sm.OLS(y, X).fit(cov_type='HC3')

print(f"\n30d CAR (N={len(df_clean)}, HC3 robust):")
print(f"  H2 (FCC): {m.params['fcc_reportable']:>8.4f}% (p={m.pvalues['fcc_reportable']:.4f})")

# Summary
print(f"\n" + "=" * 90)
print("ROBUSTNESS SUMMARY: H2 FCC EFFECT ACROSS SPECIFICATIONS")
print(f"=" * 90)

all_results = spec1_results + spec2_results
results_df = pd.DataFrame(all_results)

# Focus on H2 only for clarity
h2_summary = results_df[['Specification', 'Window', 'N', 'Method', 'H2_Coef', 'H2_P']].copy()
h2_summary.columns = ['Specification', 'Window', 'N', 'SE Method', 'H2_Coef', 'H2_P']

print(h2_summary.to_string(index=False))

print(f"\nInterpretation:")
print(f"  - H2 30d CAR baseline: -2.0593%, p=0.0577")
print(f"  - If 60d/90d p-values INCREASE significantly under clustering: overlap inflating significance")
print(f"  - If 60d/90d p-values hold in non-overlapping sample: result is robust")
print(f"  - If 60d/90d p-values collapse under clustering OR in non-overlapping sample: result is fragile")

# Save detailed results
results_df.to_csv('outputs/corrected_longrun_analysis_results.csv', index=False)
print(f"\nDetailed results saved to: outputs/corrected_longrun_analysis_results.csv")

