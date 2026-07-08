import pandas as pd

enriched = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
enriched_dedup = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

print(f'ENRICHED shape: {enriched.shape}')
print(f'ENRICHED columns (first 20): {list(enriched.columns)[:20]}')
print(f'Has h_breach: {"h_breach" in enriched.columns}')
print(f'Has prior_breaches: {"prior_breaches" in enriched.columns}')
print()
print(f'ENRICHED_DEDUP shape: {enriched_dedup.shape}')
print(f'ENRICHED_DEDUP columns (first 20): {list(enriched_dedup.columns)[:20]}')
print(f'Has h_breach: {"h_breach" in enriched_dedup.columns}')
print(f'Has prior_breaches: {"prior_breaches" in enriched_dedup.columns}')
