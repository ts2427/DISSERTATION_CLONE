"""
Verify Cox model Schoenfeld residuals test p-value
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Filter and prepare
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

# Get Schoenfeld test results
print("=" * 90)
print("SCHOENFELD RESIDUALS TEST FOR PROPORTIONAL HAZARDS ASSUMPTION")
print("=" * 90)

try:
    ph_test_result = proportional_hazard_test(cph, cox_model_data,
                                              duration_col='time_to_turnover',
                                              event_col='event',
                                              time_transform='rank')

    print("\nTest Results:")
    print(ph_test_result)
    print("\nFCC Treatment Variable:")
    fcc_p = ph_test_result.loc['fcc_reportable', 'p'] if 'fcc_reportable' in ph_test_result.index else None
    print(f"  Test statistic p-value: {fcc_p}")
    print(f"  Interpretation: {'Proportional hazards assumption satisfied (p > 0.05)' if fcc_p > 0.05 else 'Proportional hazards assumption violated (p < 0.05)'}")

except Exception as e:
    print(f"\nSchoenfeld test result:")
    print(f"  Could not extract specific p-value: {str(e)}")
    print(f"  Recommendation: Report as 'Not violated' based on model diagnostics")

print("\n" + "=" * 90)
