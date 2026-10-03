"""
ABNORMAL TRADING VOLUME TEST - H1 MECHANISM VIA VOLUME CHANNEL
========================================================================

Measures trading turnover (volume / shares outstanding) abnormal response to disclosure.
Turnover is log-transformed to match standard practice (Beaver 1968, Bamber et al. 2011).

Estimation window: [-240, -60] trading days (same as CAR)
Event window: [-5, +25] trading days (same as CAR)
Regression: Identical RHS as H1-H4 on CAR

Theory: Kim & Verrecchia (1991) - volume response indicates disagreement/information asymmetry
Citation: Veronica Zeng et al. plus Beaver, Bamber/Barron/Stevens
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("ABNORMAL TRADING VOLUME ANALYSIS")
print("Dataset: CRSP daily + dissertation breach sample")
print("=" * 90)

# Load data
breaches = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv')

# Ensure date columns are datetime
breaches['breach_date'] = pd.to_datetime(breaches['breach_date'])
crsp['date'] = pd.to_datetime(crsp['date'])

print(f"\nDatasets loaded:")
print(f"  Breaches: {len(breaches)} observations")
print(f"  CRSP daily: {len(crsp):,} records")

# Merge CRSP data with breaches
breaches_crsp = breaches.merge(
    crsp[['ticker', 'date', 'ret', 'vol', 'shrout']],
    left_on=['Map', 'breach_date'],
    right_on=['ticker', 'date'],
    how='left'
)

# For each breach, calculate abnormal volume
def calculate_abnormal_volume(ticker_data, breach_idx, event_date, crsp_data):
    """
    Calculate abnormal volume (turnover) for a breach event.

    Turnover = log(volume / shares outstanding) normalized by estimation window mean
    Estimation window: [-240, -60] trading days
    Event window: [-5, +25] trading days
    """
    try:
        ticker_crsp = crsp_data[crsp_data['ticker'] == ticker_data].copy()
        if len(ticker_crsp) < 120:
            return None

        ticker_crsp = ticker_crsp.sort_values('date').reset_index(drop=True)

        # Find event date index
        event_idx = ticker_crsp[ticker_crsp['date'] == event_date].index
        if len(event_idx) == 0:
            return None
        event_idx = event_idx[0]

        # Estimation window: -240 to -60 trading days before event
        est_start = max(0, event_idx - 240)
        est_end = max(0, event_idx - 60)

        # Event window: -5 to +25 trading days from event
        evt_start = max(0, event_idx - 5)
        evt_end = min(len(ticker_crsp) - 1, event_idx + 25)

        # Calculate turnover = vol / shrout (log-transformed)
        est_data = ticker_crsp.iloc[est_start:est_end].copy()
        evt_data = ticker_crsp.iloc[evt_start:evt_end].copy()

        if len(est_data) < 30:  # Need at least 30 days in estimation window
            return None

        # Calculate log turnover
        est_data['turnover'] = np.log(est_data['vol'] / (est_data['shrout'] * 1000))  # shrout in 1000s
        evt_data['turnover'] = np.log(evt_data['vol'] / (evt_data['shrout'] * 1000))

        # Remove infinite/NaN values
        est_turnover = est_data['turnover'].replace([np.inf, -np.inf], np.nan).dropna()
        evt_turnover = evt_data['turnover'].replace([np.inf, -np.inf], np.nan).dropna()

        if len(est_turnover) < 20 or len(evt_turnover) < 20:
            return None

        # Abnormal volume = event period mean - estimation period mean
        est_mean = est_turnover.mean()
        est_std = est_turnover.std()
        evt_mean = evt_turnover.mean()

        abnormal_vol = evt_mean - est_mean

        return {
            'abnormal_volume': abnormal_vol,
            'estimation_mean': est_mean,
            'event_mean': evt_mean,
            'estimation_std': est_std,
            'has_volume_data': True
        }

    except Exception as e:
        return None

# Calculate abnormal volume for each breach
print(f"\nCalculating abnormal trading volume for {len(breaches_crsp)} breaches...")
abnormal_volumes = []
success_count = 0

for idx, row in breaches_crsp.iterrows():
    result = calculate_abnormal_volume(row['Map'], idx, row['breach_date'], crsp)
    if result:
        abnormal_volumes.append(result)
        success_count += 1
    else:
        abnormal_volumes.append({'abnormal_volume': np.nan, 'has_volume_data': False})

    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1}/{len(breaches_crsp)} ({success_count} with volume data)")

breaches_crsp['abnormal_volume'] = [v.get('abnormal_volume', np.nan) for v in abnormal_volumes]
breaches_crsp['has_volume_data'] = [v.get('has_volume_data', False) for v in abnormal_volumes]

print(f"\nResults:")
print(f"  Successful volume calculations: {success_count}/{len(breaches_crsp)}")
print(f"  Missing data: {len(breaches_crsp) - success_count}")

# Run regression on clean volume sample
df_vol = breaches_crsp.dropna(subset=['abnormal_volume', 'firm_size_log', 'leverage', 'roa'])

print(f"\nVolume regression sample: N = {len(df_vol)}")
print(f"Mean abnormal volume: {df_vol['abnormal_volume'].mean():.4f}")
print(f"SD abnormal volume: {df_vol['abnormal_volume'].std():.4f}")

# H1-H4 regressions on abnormal volume
X = sm.add_constant(df_vol[['immediate_disclosure', 'fcc_reportable',
                             'prior_breaches_1yr', 'health_breach',
                             'firm_size_log', 'leverage', 'roa']].astype(float))
y = df_vol['abnormal_volume']
m = sm.OLS(y, X).fit(cov_type='HC3')

print(f"\n{'=' * 90}")
print("ABNORMAL VOLUME REGRESSION RESULTS")
print(f"{'=' * 90}\n")
print(f"Dependent variable: Abnormal trading turnover (log volume / shares outstanding)")
print(f"Event window: [-5, +25] trading days")
print(f"Estimation window: [-240, -60] trading days")
print(f"Sample: N = {int(m.nobs)}")
print(f"R² = {m.rsquared:.4f}")

print(f"\n{'Coefficient':<30} {'Estimate':<12} {'SE':<12} {'P-value':<12}")
print("-" * 90)
for var in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']:
    print(f"{var:<30} {m.params[var]:>10.6f}  {m.bse[var]:>10.6f}  {m.pvalues[var]:>10.4f}")

print(f"\n{'=' * 90}")
print("INTERPRETATION")
print(f"{'=' * 90}\n")

if m.pvalues['fcc_reportable'] < 0.10:
    print(f"H2 (FCC volume effect): {m.params['fcc_reportable']:.6f} (p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  Significant at p<0.10")
else:
    print(f"H2 (FCC volume effect): {m.params['fcc_reportable']:.6f} (p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  Not significant")

if m.pvalues['immediate_disclosure'] < 0.10:
    print(f"H1 (Timing volume effect): {m.params['immediate_disclosure']:.6f} (p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  Significant at p<0.10 - Timing affects trading disagreement")
else:
    print(f"H1 (Timing volume effect): {m.params['immediate_disclosure']:.6f} (p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  Not significant - Timing does not change trading disagreement")

print(f"\nComparison to price results:")
print(f"  H2 on CAR (30-day): -2.0593% (p=0.0577)")
print(f"  H2 on volume: {m.params['fcc_reportable']:.6f} (p={m.pvalues['fcc_reportable']:.4f})")
print(f"\n  Mechanism insight: FCC effect operates through {'both price AND volume' if m.pvalues['fcc_reportable'] < 0.10 else 'price, not trading disagreement'}")

print(f"\n{'=' * 90}\n")

# Save results
results_df = pd.DataFrame({
    'Variable': ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr', 'health_breach',
                 'firm_size_log', 'leverage', 'roa'],
    'Coefficient': [m.params[v] for v in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
                                           'health_breach', 'firm_size_log', 'leverage', 'roa']],
    'SE': [m.bse[v] for v in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
                               'health_breach', 'firm_size_log', 'leverage', 'roa']],
    'P_value': [m.pvalues[v] for v in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
                                        'health_breach', 'firm_size_log', 'leverage', 'roa']]
})

results_df.to_csv('outputs/h1h4_abnormal_volume_results.csv', index=False)
print(f"Results saved to outputs/h1h4_abnormal_volume_results.csv")
