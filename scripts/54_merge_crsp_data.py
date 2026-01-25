import pandas as pd
import numpy as np

print("=" * 80)
print("MERGE CRSP EVENT STUDY DATA INTO ENRICHED DATASET")
print("=" * 80)

# Load enriched dataset
print("\n[1/3] Loading enriched dataset...")
enriched = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.xlsx')
print(f"  ✓ {len(enriched):,} breaches × {len(enriched.columns)} columns")

# Load CRSP event study results
print("\n[2/3] Loading CRSP event study data...")
crsp_file = 'Data/processed/crsp_event_study_results.csv'

try:
    crsp = pd.read_csv(crsp_file)
    print(f"  ✓ {len(crsp):,} event study observations")
    
    # Show what event study variables we have
    car_vars = [col for col in crsp.columns if 'CAR' in col or 'BHAR' in col]
    print(f"\n  Event study variables found: {len(car_vars)}")
    print(f"  Examples: {car_vars[:5]}")
    
except FileNotFoundError:
    print(f"  ✗ CRSP data not found at: {crsp_file}")
    print("\n  You need to run: python scripts/10_crsp_event_study.py")
    exit()

# Merge CRSP data
print("\n[3/3] Merging CRSP event study data...")

# Check what merge keys we have
print(f"\n  Checking merge keys...")
print(f"  Enriched has 'cik': {'cik' in enriched.columns}")
print(f"  Enriched has 'breach_date': {'breach_date' in enriched.columns}")
print(f"  CRSP has 'cik': {'cik' in crsp.columns}")
print(f"  CRSP has 'breach_date': {'breach_date' in crsp.columns}")

# Create match key
enriched['breach_date_dt'] = pd.to_datetime(enriched['breach_date'])
crsp['breach_date_dt'] = pd.to_datetime(crsp['breach_date'])

enriched['merge_key'] = (
    enriched['cik'].astype(str) + '_' + 
    enriched['breach_date_dt'].dt.strftime('%Y-%m-%d')
)

crsp['merge_key'] = (
    crsp['cik'].astype(str) + '_' + 
    crsp['breach_date_dt'].dt.strftime('%Y-%m-%d')
)

print(f"\n  Enriched unique keys: {enriched['merge_key'].nunique():,}")
print(f"  CRSP unique keys: {crsp['merge_key'].nunique():,}")

# Check for duplicates in CRSP
crsp_dups = crsp['merge_key'].duplicated().sum()
if crsp_dups > 0:
    print(f"  ⚠ CRSP has {crsp_dups} duplicate keys - keeping first")
    crsp = crsp.drop_duplicates('merge_key', keep='first')

# Select CRSP variables to merge
crsp_vars = [col for col in crsp.columns 
             if col not in enriched.columns 
             and col not in ['merge_key', 'cik', 'breach_date', 'breach_date_dt', 'org_name']]

print(f"\n  Merging {len(crsp_vars)} CRSP variables...")

# Merge
before = len(enriched)
final_df = enriched.merge(
    crsp[['merge_key'] + crsp_vars],
    on='merge_key',
    how='left'
)

if len(final_df) != before:
    print(f"  ✗ ERROR: Merge created duplicates ({before} → {len(final_df)})")
    exit()

# Drop temporary columns
final_df = final_df.drop(['merge_key', 'breach_date_dt'], axis=1)

print(f"  ✓ Merge successful!")
print(f"  ✓ Rows: {len(final_df):,} (no change)")
print(f"  ✓ Columns: {len(enriched.columns)} → {len(final_df.columns)} (+{len(final_df.columns) - len(enriched.columns)})")

# Show merge coverage
matched = final_df[crsp_vars[0]].notna().sum()
print(f"\n  Coverage: {matched:,}/{len(final_df):,} breaches have CRSP data ({matched/len(final_df)*100:.1f}%)")

# Save
print("\n" + "=" * 80)
print("SAVING FINAL DATASET")
print("=" * 80)

output_excel = 'Data/processed/FINAL_DISSERTATION_DATASET_COMPLETE.xlsx'
output_csv = 'Data/processed/FINAL_DISSERTATION_DATASET_COMPLETE.csv'

print(f"\nSaving complete dataset with CRSP data...")

final_df.to_excel(output_excel, index=False)
print(f"  ✓ Excel: {output_excel}")

final_df.to_csv(output_csv, index=False)
print(f"  ✓ CSV: {output_csv}")

# Summary
print("\n" + "=" * 80)
print("✓ COMPLETE DATASET CREATED!")
print("=" * 80)

print(f"\n📊 Final Dataset Summary:")
print(f"  • Total breaches: {len(final_df):,}")
print(f"  • Total variables: {len(final_df.columns)}")
print(f"  • With CRSP data: {matched:,} ({matched/len(final_df)*100:.1f}%)")

# Check key variables
key_vars = ['CAR_0_1', 'CAR_-1_1', 'BHAR_126', 'abnormal_volume_0_1']
available = [var for var in key_vars if var in final_df.columns]

print(f"\n  Key event study variables:")
for var in available:
    non_missing = final_df[var].notna().sum()
    print(f"    ✓ {var}: {non_missing:,} observations")

if len(available) == 0:
    print(f"    ⚠ No standard CAR variables found")
    print(f"    Available columns starting with 'car' or 'CAR':")
    car_cols = [col for col in final_df.columns if 'car' in col.lower()]
    for col in car_cols[:10]:
        print(f"      • {col}")

print(f"\n📁 Files created:")
print(f"  • {output_excel}")
print(f"  • {output_csv}")

print(f"\n🚀 Ready for ML models and analysis!")
print("=" * 80)