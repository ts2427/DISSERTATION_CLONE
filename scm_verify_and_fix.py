"""
Verify SCM data integrity and create deduplicated FCC companies file
"""
import pandas as pd
import sys

print("\n" + "="*80)
print("SCM DATA INTEGRITY VERIFICATION")
print("="*80)

# Load both versions
print("\nLoading datasets...")
original = pd.read_csv('Data/processed/FINAL_DATASET_ORIGINAL_1054.csv')
dedup = pd.read_csv('Data/processed/FINAL_DATASET_DEDUPLICATED_784.csv')
current_fcc_file = pd.read_csv('Data/fcc/companies_to_match.csv')

# Check current state
print(f"\nCurrent companies_to_match.csv:")
print(f"  Total rows: {len(current_fcc_file)}")
print(f"  FCC breaches: {len(current_fcc_file[current_fcc_file['fcc_reportable']==True])}")

# Extract FCC firms from deduplicated version
print(f"\nDeduplicated dataset (FINAL_DATASET_DEDUPLICATED_784.csv):")
print(f"  Total rows: {len(dedup)}")
print(f"  FCC breaches: {len(dedup[dedup['fcc_reportable']==1])}")
print(f"  Unique FCC firms: {dedup[dedup['fcc_reportable']==1]['org_name'].nunique()}")

# Create deduplicated FCC companies file
fcc_dedup = dedup[dedup['fcc_reportable'] == 1].copy()
fcc_breaches = fcc_dedup[['org_name', 'breach_date']].drop_duplicates().copy()

# Get fcc_category from original
category_map = original[original['fcc_reportable'] == 1][['org_name', 'fcc_category']].drop_duplicates(subset=['org_name'])

# Merge
fcc_breaches_full = fcc_breaches.merge(category_map, on='org_name', how='left')
fcc_breaches_full['fcc_reportable'] = True

print(f"\nDeduplicated FCC companies file (to be created):")
print(f"  Total FCC breaches: {len(fcc_breaches_full)}")
print(f"  Unique FCC firms: {fcc_breaches_full['org_name'].nunique()}")

# DISH verification
dish_original = original[original['org_name'].str.contains('DISH', case=False, na=False)]
dish_dedup = fcc_breaches_full[fcc_breaches_full['org_name'].str.contains('DISH', case=False, na=False)]

print(f"\nDISH verification:")
print(f"  Original dataset: {len(dish_original)} records")
print(f"  Deduplicated: {len(dish_dedup)} records")
print(f"  DISH breach dates in dedup:")
for date in sorted(dish_dedup['breach_date'].unique()):
    print(f"    {date}")

# Save deduplicated FCC companies file
fcc_breaches_full[['org_name', 'breach_date', 'fcc_category', 'fcc_reportable']].to_csv(
    'Data/fcc/companies_to_match_DEDUPLICATED.csv', index=False
)

print(f"\n✓ Created: Data/fcc/companies_to_match_DEDUPLICATED.csv ({len(fcc_breaches_full)} rows)")
print("\nNext step: Update SCM script to load companies_to_match_DEDUPLICATED.csv")
print("="*80 + "\n")
