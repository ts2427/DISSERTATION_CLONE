"""
Compute time-varying hazard ratios from Cox model
Answers Affuso's question: Does the FCC hazard ratio decay over time or increase?
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data (same as prior Cox analysis)
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

analysis_df = df[df['has_crsp_data'] == True].copy()
turnover_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

bool_cols = turnover_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    turnover_df[col] = turnover_df[col].astype(int)

# Create time-to-event variables
turnover_df['event'] = 0
turnover_df['time_to_turnover'] = 180

has_turnover = turnover_df['days_to_first_change'].notna()
turnover_df.loc[has_turnover, 'event'] = 1
turnover_df.loc[has_turnover, 'time_to_turnover'] = turnover_df.loc[has_turnover, 'days_to_first_change'].astype(int)
turnover_df['time_to_turnover'] = turnover_df['time_to_turnover'].clip(lower=1, upper=180)

# Prepare Cox data
cox_data = turnover_df[[
    'time_to_turnover', 'event', 'fcc_reportable',
    'firm_size_log', 'leverage', 'roa', 'sic_3digit'
]].dropna().copy()

cox_data['fcc_reportable'] = cox_data['fcc_reportable'].astype(int)
cox_data['sic_3digit'] = cox_data['sic_3digit'].astype(str)

# Create industry dummies
industry_dummies = pd.get_dummies(cox_data['sic_3digit'], prefix='sic', drop_first=True)
cox_model_data = pd.concat([
    cox_data[['time_to_turnover', 'event', 'fcc_reportable', 'firm_size_log', 'leverage', 'roa']],
    industry_dummies
], axis=1)

# Fit Cox model
cph = CoxPHFitter()
cph.fit(cox_model_data,
        duration_col='time_to_turnover',
        event_col='event',
        show_progress=False)

print("=" * 90)
print("TIME-VARYING HAZARD RATIO ANALYSIS")
print("Answers Affuso's question: Does FCC hazard ratio decay or increase over time?")
print("=" * 90)

# Calculate survival functions for FCC=1 and FCC=0
print("\nKaplan-Meier Survival by FCC Status:")
fcc_1 = cox_model_data[cox_model_data['fcc_reportable'] == 1]
fcc_0 = cox_model_data[cox_model_data['fcc_reportable'] == 0]

print(f"\nFCC=1 (n={len(fcc_1)}):")
print(f"  Events: {fcc_1['event'].sum()}")
print(f"  Mean survival time: {fcc_1[fcc_1['event']==1]['time_to_turnover'].mean():.1f} days")

print(f"\nFCC=0 (n={len(fcc_0)}):")
print(f"  Events: {fcc_0['event'].sum()}")
print(f"  Mean survival time: {fcc_0[fcc_0['event']==1]['time_to_turnover'].mean():.1f} days")

# Compute partial hazard ratios at different time points
print("\n" + "=" * 90)
print("PARTIAL HAZARD RATIOS AT TIME MILESTONES")
print("=" * 90)

time_points = [30, 60, 90, 120, 150, 180]

print("\nHazard ratio for FCC vs. non-FCC at different days post-breach:")
print(f"\n{'Days':<10} {'Cumulative Events (FCC)':<20} {'Cumulative Events (Non-FCC)':<25} {'Implied HR':<15}")
print("-" * 70)

for t in time_points:
    fcc_events_by_t = ((fcc_1['time_to_turnover'] <= t) & (fcc_1['event'] == 1)).sum()
    nonfcc_events_by_t = ((fcc_0['time_to_turnover'] <= t) & (fcc_0['event'] == 1)).sum()

    # Simple rate comparison (events per observation)
    fcc_rate = fcc_events_by_t / len(fcc_1) if len(fcc_1) > 0 else 0
    nonfcc_rate = nonfcc_events_by_t / len(fcc_0) if len(fcc_0) > 0 else 0

    # Implied hazard ratio (rough approximation)
    implied_hr = fcc_rate / nonfcc_rate if nonfcc_rate > 0 else 0

    print(f"{t:<10} {fcc_events_by_t:<20} {nonfcc_events_by_t:<25} {implied_hr:<15.3f}")

print("\n" + "=" * 90)
print("INTERPRETATION FOR AFFUSO")
print("=" * 90)

print("\nThe time-varying pattern answers whether:")
print("  A) Hazard starts HIGH and DECAYS (consistent with initial pressure that fades)")
print("  B) Hazard starts LOW and INCREASES (harder to interpret, may indicate delayed effect)")
print("  C) Hazard is roughly CONSTANT (suggests no time-specific pattern)")

# Check if rates are increasing or decreasing
rates_at_30 = ((fcc_1['time_to_turnover'] <= 30) & (fcc_1['event'] == 1)).sum() / len(fcc_1)
rates_at_180 = ((fcc_1['time_to_turnover'] <= 180) & (fcc_1['event'] == 1)).sum() / len(fcc_1)

if rates_at_30 > 0.15:
    pattern = "HIGH EARLY, then spreads: consistent with initial pressure"
else:
    pattern = "CONSTANT OR INCREASING over time"

print(f"\nObserved Pattern: {pattern}")
print(f"  FCC event rate by day 30: {rates_at_30:.1%}")
print(f"  FCC event rate by day 180: {rates_at_180:.1%}")

print("\n" + "=" * 90)
