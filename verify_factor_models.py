import pandas as pd
import numpy as np
import statsmodels.api as sm

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Load Fama-French factors (skip header rows) - use DAILY data
ff3 = pd.read_csv('Data/F-F_Research_Data_Factors_daily.csv', skiprows=4)
ff3.columns = ff3.columns.str.strip()
ff3['date'] = pd.to_datetime(ff3[ff3.columns[0]], format='%Y%m%d', errors='coerce')
ff3 = ff3[['date', 'Mkt-RF', 'SMB', 'HML']].copy()
ff3.columns = ['date', 'mkt_rf', 'smb', 'hml']
ff3 = ff3.dropna()

carhart = pd.read_csv('Data/F-F_Momentum_Factor_daily.csv', skiprows=13)
carhart.columns = carhart.columns.str.strip()
carhart = carhart.dropna(axis=1, how='all')
date_col = carhart.columns[0]
carhart['date'] = pd.to_datetime(carhart[date_col], format='%Y%m%d', errors='coerce')
mom_col = 'Mom'
if mom_col in carhart.columns:
    carhart_factors = carhart[['date', mom_col]].copy()
    carhart_factors.columns = ['date', 'mom']
    carhart_factors = carhart_factors.dropna()
else:
    carhart_factors = pd.DataFrame()

ff5 = pd.read_csv('Data/F-F_Research_Data_5_Factors_2x3_daily.csv', skiprows=4)
ff5.columns = ff5.columns.str.strip()
ff5['date'] = pd.to_datetime(ff5[ff5.columns[0]], format='%Y%m%d', errors='coerce')
ff5 = ff5[['date', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']].copy()
ff5.columns = ['date', 'mkt_rf', 'smb', 'hml', 'rmw', 'cma']
ff5 = ff5.dropna()

# Prepare base regression sample
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']
df_base = df[df['car_30d'].notna()].dropna(subset=controls).copy()
df_base['breach_date_col'] = pd.to_datetime(df_base['breach_date'])

print("=" * 90)
print("FACTOR MODEL VERIFICATION - COEFFICIENT CONFIRMATION")
print("=" * 90)

# Full sample (648): market-adjusted
print("\n[1] FULL SAMPLE (N=648) - MARKET-ADJUSTED")
print("-" * 90)

df_648 = df_base.copy()
X_648 = sm.add_constant(df_648[controls].astype(float))
y_648 = df_648['car_30d']
m_648 = sm.OLS(y_648, X_648).fit(cov_type='HC3')

print("N = {}".format(len(df_648)))
print("FCC coefficient: {:.2f}%".format(m_648.params['fcc_reportable']))
print("P-value:        {:.4f}".format(m_648.pvalues['fcc_reportable']))

# Restricted sample: factor models
print("\n[2] RESTRICTED SAMPLE - FACTOR MODELS")
print("-" * 90)

# Merge FF3 (daily, exact date matching)
df_ff3 = df_base.merge(ff3, left_on='breach_date_col', right_on='date', how='left')
df_ff3_clean = df_ff3.dropna(subset=['mkt_rf', 'smb', 'hml'])

# Merge Carhart (daily, exact date matching)
df_carhart = df_ff3_clean.merge(carhart_factors, left_on='breach_date_col', right_on='date', how='left')
df_carhart_clean = df_carhart.dropna(subset=['mom'])

# Merge FF5 (daily, exact date matching)
df_ff5 = df_base.merge(ff5, left_on='breach_date_col', right_on='date', how='left')
df_ff5_clean = df_ff5.dropna(subset=['mkt_rf', 'smb', 'hml', 'rmw', 'cma'])

# Market-adjusted on restricted sample
print("\n2a. Market-Adjusted (N={})".format(len(df_ff3_clean)))
X_market = sm.add_constant(df_ff3_clean[controls].astype(float))
y_market = df_ff3_clean['car_30d']
m_market = sm.OLS(y_market, X_market).fit(cov_type='HC3')
print("    FCC coefficient: {:.2f}%".format(m_market.params['fcc_reportable']))
print("    P-value:        {:.4f}".format(m_market.pvalues['fcc_reportable']))

# FF3
print("\n2b. Fama-French 3-Factor (N={})".format(len(df_ff3_clean)))
X_ff3 = sm.add_constant(df_ff3_clean[controls + ['mkt_rf', 'smb', 'hml']].astype(float))
y_ff3 = df_ff3_clean['car_30d']
m_ff3 = sm.OLS(y_ff3, X_ff3).fit(cov_type='HC3')
print("    FCC coefficient: {:.2f}%".format(m_ff3.params['fcc_reportable']))
print("    P-value:        {:.4f}".format(m_ff3.pvalues['fcc_reportable']))

# Carhart
print("\n2c. Carhart 4-Factor (N={})".format(len(df_carhart_clean)))
X_carhart = sm.add_constant(df_carhart_clean[controls + ['mkt_rf', 'smb', 'hml', 'mom']].astype(float))
y_carhart = df_carhart_clean['car_30d']
m_carhart = sm.OLS(y_carhart, X_carhart).fit(cov_type='HC3')
print("    FCC coefficient: {:.2f}%".format(m_carhart.params['fcc_reportable']))
print("    P-value:        {:.4f}".format(m_carhart.pvalues['fcc_reportable']))

# FF5
print("\n2d. Fama-French 5-Factor (N={})".format(len(df_ff5_clean)))
X_ff5 = sm.add_constant(df_ff5_clean[controls + ['mkt_rf', 'smb', 'hml', 'rmw', 'cma']].astype(float))
y_ff5 = df_ff5_clean['car_30d']
m_ff5 = sm.OLS(y_ff5, X_ff5).fit(cov_type='HC3')
print("    FCC coefficient: {:.2f}%".format(m_ff5.params['fcc_reportable']))
print("    P-value:        {:.4f}".format(m_ff5.pvalues['fcc_reportable']))

print("\n" + "=" * 90)
print("VERIFICATION SUMMARY")
print("=" * 90)
print("\nExpected figures (from this afternoon):")
print("  Market-adjusted (519):  -2.47%")
print("  FF3 (519):              -2.12%, p=0.107")
print("  Carhart (519):          -2.14%, p=0.105")
print("  FF5 (519):              -2.20%, p=0.095")
print("  Market-adjusted (648):  -2.06%, p=0.058")

print("\nActual figures (current run):")
print("  Market-adjusted ({}):   {:.2f}%, p={:.4f}".format(len(df_ff3_clean),
                                                            m_market.params['fcc_reportable'],
                                                            m_market.pvalues['fcc_reportable']))
print("  FF3 ({}):               {:.2f}%, p={:.4f}".format(len(df_ff3_clean),
                                                           m_ff3.params['fcc_reportable'],
                                                           m_ff3.pvalues['fcc_reportable']))
print("  Carhart ({}):           {:.2f}%, p={:.4f}".format(len(df_carhart_clean),
                                                           m_carhart.params['fcc_reportable'],
                                                           m_carhart.pvalues['fcc_reportable']))
print("  FF5 ({}):               {:.2f}%, p={:.4f}".format(len(df_ff5_clean),
                                                           m_ff5.params['fcc_reportable'],
                                                           m_ff5.pvalues['fcc_reportable']))
print("  Market-adjusted (648):  {:.2f}%, p={:.4f}".format(m_648.params['fcc_reportable'],
                                                           m_648.pvalues['fcc_reportable']))
