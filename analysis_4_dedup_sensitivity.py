"""
Deduplication Sensitivity Analysis
Compares H2 OLS across three deduplication levels
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

print("\n" + "="*80)
print("DEDUPLICATION SENSITIVITY: H2 FCC EFFECT ACROSS DEDUP STRATEGIES")
print("="*80)

# Load datasets
original = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
dedup_full = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

print(f"\nDataset versions:")
print(f"  1. Original:                {len(original)} rows (pre-dedup)")
print(f"  2. Full dedup (current):    {len(dedup_full)} rows")

# ============================================================================
# Prepare analysis for each version
# ============================================================================

versions = [
    ("Original (1,054)", original),
    ("Full Dedup (784)", dedup_full),
]

results_table = []

for label, data in versions:
    # Get CRSP sample with all required variables
    required_cols = ['car_30d', 'fcc_reportable', 'immediate_disclosure', 'firm_size_log', 'leverage', 'roa']
    crsp_sample = data[required_cols].dropna().copy()

    # Prepare variables
    y = crsp_sample['car_30d'].astype(float)
    X = crsp_sample[['fcc_reportable', 'immediate_disclosure', 'firm_size_log', 'leverage', 'roa']].astype(float)
    X = sm.add_constant(X)

    # Run regression
    model = sm.OLS(y, X).fit()

    # Extract FCC coefficient
    fcc_coef = model.params['fcc_reportable']
    fcc_se = model.bse['fcc_reportable']
    fcc_pval = model.pvalues['fcc_reportable']
    fcc_tstat = fcc_coef / fcc_se

    results_table.append({
        'Dataset': label,
        'N': len(crsp_sample),
        'FCC Coef': fcc_coef,
        'SE': fcc_se,
        't-stat': fcc_tstat,
        'p-value': fcc_pval,
        'R2': model.rsquared
    })

    print(f"\n{label}:")
    print(f"  N: {len(crsp_sample)}")
    print(f"  FCC coef: {fcc_coef:.4f}%")
    print(f"  SE: {fcc_se:.4f}")
    print(f"  t-stat: {fcc_tstat:.4f}")
    print(f"  p-value: {fcc_pval:.4f}")
    print(f"  R2: {model.rsquared:.4f}")

# Save table
results_df = pd.DataFrame(results_table)
results_df.to_csv('outputs/tables/DEDUP_SENSITIVITY_H2_FCC_EFFECT.csv', index=False)

print(f"\n{'='*80}")
print("INTERPRETATION:")
print("If both versions show FCC ~-2% with stable p-values, dedup choice is robust.")
print(f"{'='*80}\n")

# Verification output
print("DEDUP_SENSITIVITY: COMPLETE")
