"""
Sample Composition Comparison
Explains what changed between 1,054 and 784 observations
"""
import pandas as pd
import numpy as np

print("\n" + "="*80)
print("SAMPLE COMPOSITION COMPARISON: ORIGINAL VS DEDUPLICATED")
print("="*80)

# Load datasets
original = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
dedup = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

print(f"\nDataset sizes:")
print(f"  Original: {len(original)} rows")
print(f"  Deduplicated: {len(dedup)} rows")
print(f"  Duplicates removed: {len(original) - len(dedup)} ({100*(len(original)-len(dedup))/len(original):.1f}%)")

# ============================================================================
# Key composition metrics
# ============================================================================

comparison = []

# 1. FCC share
fcc_original = len(original[original['fcc_reportable'] == 1])
fcc_dedup = len(dedup[dedup['fcc_reportable'] == 1])

comparison.append({
    'Metric': 'FCC reportable breaches',
    'Original': fcc_original,
    'Deduplicated': fcc_dedup,
    'Change': fcc_dedup - fcc_original,
    'Pct Change': f"{100*(fcc_dedup - fcc_original)/fcc_original:.1f}%"
})

# 2. Health breaches
health_original = len(original[original['health_breach'] == 1])
health_dedup = len(dedup[dedup['health_breach'] == 1])

comparison.append({
    'Metric': 'Health breaches (h_breach=1)',
    'Original': health_original,
    'Deduplicated': health_dedup,
    'Change': health_dedup - health_original,
    'Pct Change': f"{100*(health_dedup - health_original)/health_original:.1f}%"
})

# 3. Immediate disclosure
immediate_original = len(original[original['immediate_disclosure'] == 1])
immediate_dedup = len(dedup[dedup['immediate_disclosure'] == 1])

comparison.append({
    'Metric': 'Immediate disclosure (<=7 days)',
    'Original': immediate_original,
    'Deduplicated': immediate_dedup,
    'Change': immediate_dedup - immediate_original,
    'Pct Change': f"{100*(immediate_dedup - immediate_original)/immediate_original:.1f}%"
})

# 4. CRSP sample (has CAR data)
crsp_original = len(original[original['car_30d'].notna()])
crsp_dedup = len(dedup[dedup['car_30d'].notna()])

comparison.append({
    'Metric': 'CRSP matched sample (has CAR)',
    'Original': crsp_original,
    'Deduplicated': crsp_dedup,
    'Change': crsp_dedup - crsp_original,
    'Pct Change': f"{100*(crsp_dedup - crsp_original)/crsp_original:.1f}%"
})

# Print table
print("\nCOMPOSITION TABLE:")
print("-" * 100)
for row in comparison:
    print(f"{row['Metric']:40} | {row['Original']:6d} | {row['Deduplicated']:6d} | {row['Change']:+6d} | {row['Pct Change']:>8}")

# ============================================================================
# Key statistics
# ============================================================================

print("\n\nKEY STATISTICS:")
print("-" * 100)

stats_comparison = []

# Mean CAR
car_orig_mean = original[original['car_30d'].notna()]['car_30d'].mean()
car_dedup_mean = dedup[dedup['car_30d'].notna()]['car_30d'].mean()

stats_comparison.append({
    'Statistic': 'Mean CAR 30d (%)',
    'Original': f"{car_orig_mean:.4f}",
    'Deduplicated': f"{car_dedup_mean:.4f}",
    'Difference': f"{car_dedup_mean - car_orig_mean:.4f}"
})

# Median CAR
car_orig_median = original[original['car_30d'].notna()]['car_30d'].median()
car_dedup_median = dedup[dedup['car_30d'].notna()]['car_30d'].median()

stats_comparison.append({
    'Statistic': 'Median CAR 30d (%)',
    'Original': f"{car_orig_median:.4f}",
    'Deduplicated': f"{car_dedup_median:.4f}",
    'Difference': f"{car_dedup_median - car_orig_median:.4f}"
})

# Std dev CAR
car_orig_std = original[original['car_30d'].notna()]['car_30d'].std()
car_dedup_std = dedup[dedup['car_30d'].notna()]['car_30d'].std()

stats_comparison.append({
    'Statistic': 'Std Dev CAR 30d (%)',
    'Original': f"{car_orig_std:.4f}",
    'Deduplicated': f"{car_dedup_std:.4f}",
    'Difference': f"{car_dedup_std - car_orig_std:.4f}"
})

# Firm size (log)
size_orig_mean = original[original['firm_size_log'].notna()]['firm_size_log'].mean()
size_dedup_mean = dedup[dedup['firm_size_log'].notna()]['firm_size_log'].mean()

stats_comparison.append({
    'Statistic': 'Mean firm size (log)',
    'Original': f"{size_orig_mean:.4f}",
    'Deduplicated': f"{size_dedup_mean:.4f}",
    'Difference': f"{size_dedup_mean - size_orig_mean:.4f}"
})

# Leverage
lev_orig_mean = original[original['leverage'].notna()]['leverage'].mean()
lev_dedup_mean = dedup[dedup['leverage'].notna()]['leverage'].mean()

stats_comparison.append({
    'Statistic': 'Mean leverage',
    'Original': f"{lev_orig_mean:.4f}",
    'Deduplicated': f"{lev_dedup_mean:.4f}",
    'Difference': f"{lev_dedup_mean - lev_orig_mean:.4f}"
})

# Prior breaches
prior_orig_mean = original[original['prior_breaches_total'].notna()]['prior_breaches_total'].mean()
prior_dedup_mean = dedup[dedup['prior_breaches_total'].notna()]['prior_breaches_total'].mean()

stats_comparison.append({
    'Statistic': 'Mean prior breaches',
    'Original': f"{prior_orig_mean:.4f}",
    'Deduplicated': f"{prior_dedup_mean:.4f}",
    'Difference': f"{prior_dedup_mean - prior_orig_mean:.4f}"
})

for row in stats_comparison:
    print(f"{row['Statistic']:30} | {row['Original']:>15} | {row['Deduplicated']:>15} | {row['Difference']:>15}")

# ============================================================================
# Notable shifts
# ============================================================================

print("\n\nNOTABLE SHIFTS:")
print("-" * 100)

# Immediate disclosure rate shift
immed_rate_orig = 100 * immediate_original / crsp_original
immed_rate_dedup = 100 * immediate_dedup / crsp_dedup

print(f"Immediate disclosure rate (of CRSP sample):")
print(f"  Original:      {immed_rate_orig:.1f}%")
print(f"  Deduplicated:  {immed_rate_dedup:.1f}%")
print(f"  Shift:         {immed_rate_dedup - immed_rate_orig:+.1f} pp")

# Health breach rate shift
health_rate_orig = 100 * health_original / crsp_original
health_rate_dedup = 100 * health_dedup / crsp_dedup

print(f"\nHealth breach rate (of CRSP sample):")
print(f"  Original:      {health_rate_orig:.1f}%")
print(f"  Deduplicated:  {health_rate_dedup:.1f}%")
print(f"  Shift:         {health_rate_dedup - health_rate_orig:+.1f} pp")
print(f"  Note: Cencora (pharma distributor) reduced from 54 to 3 records")

# FCC breach rate shift
fcc_rate_orig = 100 * fcc_original / len(original)
fcc_rate_dedup = 100 * fcc_dedup / len(dedup)

print(f"\nFCC reportable rate (of all records):")
print(f"  Original:      {fcc_rate_orig:.1f}%")
print(f"  Deduplicated:  {fcc_rate_dedup:.1f}%")
print(f"  Shift:         {fcc_rate_dedup - fcc_rate_orig:+.1f} pp")

# Save to CSV
comp_df = pd.DataFrame(comparison)
comp_df.to_csv('outputs/tables/SAMPLE_COMPOSITION_COMPARISON.csv', index=False)

print(f"\n[OK] Results saved to: outputs/tables/SAMPLE_COMPOSITION_COMPARISON.csv")
print("\n" + "="*80)
print("VERIFICATION OUTPUT:")
print("SAMPLE_COMPOSITION: COMPLETE")
print("="*80 + "\n")
