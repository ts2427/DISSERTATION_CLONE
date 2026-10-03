import pandas as pd
import wrds
from datetime import datetime
import os

print("=" * 60)
print("DOWNLOADING AUDIT ANALYTICS DATA (STRING CIKS)")
print("=" * 60)

# Load breach dataset
breach_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(breach_df)} breach records")

# Get unique CIK codes and date range
ciks = breach_df['cik'].dropna().unique().tolist()
min_date = breach_df['breach_date'].min() - pd.DateOffset(years=2)
max_date = breach_df['breach_date'].max()

print(f"  Unique CIKs: {len(ciks)}")
print(f"  Date range: {min_date.date()} to {max_date.date()}")

# Connect to WRDS
print("\n[1/3] Connecting to WRDS...")
db = wrds.Connection()
print("✓ Connected")

# CRITICAL FIX: Create CIK list with QUOTES for string matching
cik_list = ','.join([f"'{int(c)}'" for c in ciks])
print(f"\n✓ Created CIK list with {len(ciks)} companies (as strings)")

os.makedirs('Data/audit_analytics', exist_ok=True)

# ============================================================
# 1. SOX 404 INTERNAL CONTROLS
# ============================================================

print("\n[2/3] Downloading SOX 404 internal control data...")

sox_query = f"""
    SELECT company_fkey, file_date, 
           ic_is_effective, count_weak,
           auditor_fkey, eventdate_aud_name
    FROM audit.feed11_sox_404_internal_controls
    WHERE company_fkey IN ({cik_list})
    AND file_date >= '{min_date.strftime('%Y-%m-%d')}'
    AND file_date <= '{max_date.strftime('%Y-%m-%d')}'
"""

try:
    print("  Querying SOX 404 data...")
    sox_data = db.raw_sql(sox_query, date_cols=['file_date'])
    
    if len(sox_data) > 0:
        sox_data.to_csv('Data/audit_analytics/sox_404_data.csv', index=False)
        print(f"✓ Downloaded {len(sox_data):,} SOX 404 records")
        print(f"  Unique companies: {sox_data['company_fkey'].nunique()}")