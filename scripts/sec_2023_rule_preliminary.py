"""
SEC 2023 RULE PRELIMINARY ANALYSIS
========================================================================

The SEC four-day disclosure rule took effect December 18, 2023.
This is a DESCRIPTIVE comparison only, not a hypothesis test.

Sample: 55 observations in 2024 + 18 observations in 2025 = 73 total
Frame: Preliminary pattern recognition, underpowered, future-research directional signal

Question: Does the same FCC penalty appear under a second, stricter mandate?
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime

print("=" * 90)
print("SEC 2023 FOUR-DAY RULE PRELIMINARY ANALYSIS (DESCRIPTIVE)")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Split into FCC 7-day rule era (pre-Dec 2023) and SEC 4-day rule era (post-Dec 2023)
rule_change_date = pd.to_datetime('2023-12-18')

df['era'] = 'FCC 7-Day (Pre-Dec 2023)'
df.loc[df['breach_date'] >= rule_change_date, 'era'] = 'SEC 4-Day (Post-Dec 2023)'

fcc_era = df[df['era'] == 'FCC 7-Day (Pre-Dec 2023)']
sec_era = df[df['era'] == 'SEC 4-Day (Post-Dec 2023)']

print(f"\nSample composition:")
print(f"  FCC 7-Day era (pre-Dec 2023): {len(fcc_era):,} observations")
print(f"  SEC 4-Day era (post-Dec 2023): {len(sec_era)} observations")
print(f"    2024: {len(sec_era[sec_era['breach_date'].dt.year == 2024])}")
print(f"    2025: {len(sec_era[sec_era['breach_date'].dt.year == 2025])}")
print(f"\n[WARNING] SAMPLE SIZE WARNING")
print(f"The SEC 4-Day sample (n=73) is UNDERPOWERED for hypothesis testing.")
print(f"This analysis is DESCRIPTIVE and directional only.\n")

# Univariate comparison
print(f"{'=' * 90}")
print("UNIVARIATE COMPARISON")
print(f"{'=' * 90}\n")

fcc_mean = fcc_era[fcc_era['fcc_reportable'] == True]['car_30d'].mean()
fcc_se = fcc_era[fcc_era['fcc_reportable'] == True]['car_30d'].sem()
fcc_n = (fcc_era['fcc_reportable'] == True).sum()

sec_mean = sec_era[sec_era['fcc_reportable'] == True]['car_30d'].mean()
sec_se = sec_era[sec_era['fcc_reportable'] == True]['car_30d'].sem()
sec_n = (sec_era['fcc_reportable'] == True).sum()

non_fcc_mean = fcc_era[fcc_era['fcc_reportable'] == False]['car_30d'].mean()
non_sec_mean = sec_era[sec_era['fcc_reportable'] == False]['car_30d'].mean()

print(f"{'Metric':<30} {'FCC 7-Day':<20} {'SEC 4-Day':<20}")
print("-" * 90)
print(f"{'FCC firms mean CAR':<30} {fcc_mean:>8.4f}% (n={fcc_n:<3.0f}) {sec_mean:>8.4f}% (n={sec_n:<3.0f})")
print(f"{'Non-FCC firms mean CAR':<30} {non_fcc_mean:>8.4f}% {non_sec_mean:>8.4f}%")
print(f"{'Difference (FCC - Non-FCC)':<30} {fcc_mean - non_fcc_mean:>8.4f}% {sec_mean - non_sec_mean:>8.4f}%")

# Regression comparison
controls = ['immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']

print(f"\n{'=' * 90}")
print("REGRESSION COMPARISON: H2 Effect Across Regulatory Eras")
print(f"{'=' * 90}\n")

for era_name, era_data in [('FCC 7-Day (n=648)', fcc_era), ('SEC 4-Day (n=73)', sec_era)]:
    X = sm.add_constant(era_data[['fcc_reportable'] + controls].astype(float))
    y = era_data['car_30d']
    m = sm.OLS(y, X).fit(cov_type='HC3')

    print(f"{era_name}:")
    print(f"  H2 (FCC effect):  {m.params['fcc_reportable']:>8.4f}% (SE={m.bse['fcc_reportable']:.4f}, p={m.pvalues['fcc_reportable']:.4f})")
    print(f"  H1 (Timing):      {m.params['immediate_disclosure']:>8.4f}% (SE={m.bse['immediate_disclosure']:.4f}, p={m.pvalues['immediate_disclosure']:.4f})")
    print(f"  R²:               {m.rsquared:>8.4f}")
    print()

print(f"{'=' * 90}")
print("ASSESSMENT")
print(f"{'=' * 90}\n")

print("Given the small SEC 4-Day sample (n=73), this is a PRELIMINARY OBSERVATION.")
print("Interpretation:")
print(f"  - FCC 7-Day pattern: Regulatory classification penalizes {fcc_mean:.2f}%")
print(f"  - SEC 4-Day pattern: {'Similar' if abs(sec_mean - fcc_mean) < 2 else 'Different'} magnitude")
print(f"  - Direction consistency: {'YES - pattern repeats' if (sec_mean < non_sec_mean) else 'NO - reverses or flattens'}")
print(f"\nConclusion: The SEC 4-Day rule introduces a SECOND regulatory mandate in the dataset.")
print(f"If the same FCC penalty pattern appears (negative FCC coefficient), it suggests the")
print(f"finding generalizes to stricter disclosure regimes, not just the FCC 7-Day rule.")
print(f"However, power is limited (n=73) and this must be framed as exploratory.\n")

# Save summary
sec_summary = pd.DataFrame({
    'Era': ['FCC 7-Day', 'SEC 4-Day'],
    'N_Total': [len(fcc_era), len(sec_era)],
    'N_FCC': [fcc_n, sec_n],
    'FCC_Mean_CAR': [fcc_mean, sec_mean],
    'FCC_SE': [fcc_se, sec_se],
    'Non_FCC_Mean': [non_fcc_mean, non_sec_mean],
    'FCC_Minus_NonFCC': [fcc_mean - non_fcc_mean, sec_mean - non_sec_mean]
})

sec_summary.to_csv('outputs/sec_2023_rule_preliminary.csv', index=False)
print(f"Summary saved to outputs/sec_2023_rule_preliminary.csv")
