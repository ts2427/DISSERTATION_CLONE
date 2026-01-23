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
        print(f"  Date range: {sox_data['file_date'].min()} to {sox_data['file_date'].max()}")
        
        # Summary stats
        print(f"\n  SOX Summary:")
        print(f"    Effective internal controls: {sox_data['ic_is_effective'].sum()}")
        print(f"    Records with weaknesses: {(sox_data['count_weak'] > 0).sum()}")
        print(f"    Average weaknesses: {sox_data['count_weak'].mean():.2f}")
        
        print(f"\n  Sample records:")
        print(sox_data[['company_fkey', 'file_date', 'ic_is_effective', 'count_weak']].head(3))
    else:
        print("✗ No SOX 404 data found")
        
except Exception as e:
    print(f"✗ SOX 404 download failed: {e}")

# ============================================================
# 2. FINANCIAL RESTATEMENTS
# ============================================================

print("\n[3/3] Downloading financial restatement data...")

restatement_query = f"""
    SELECT company_fkey, file_date, event_date,
           res_begin_date, res_end_date,
           res_accounting, res_fraud, 
           res_sec_investigation,
           restatement_notification_key
    FROM audit.feed39_financial_restatements
    WHERE company_fkey IN ({cik_list})
    AND res_begin_date >= '{min_date.strftime('%Y-%m-%d')}'
"""

try:
    print("  Querying restatement data...")
    restatement_data = db.raw_sql(restatement_query, date_cols=['file_date', 'event_date', 'res_begin_date', 'res_end_date'])
    
    if len(restatement_data) > 0:
        restatement_data.to_csv('Data/audit_analytics/restatements.csv', index=False)
        print(f"✓ Downloaded {len(restatement_data):,} restatement records")
        print(f"  Unique companies: {restatement_data['company_fkey'].nunique()}")
        
        print(f"\n  Restatement Summary:")
        print(f"    Accounting issues: {restatement_data['res_accounting'].sum()}")
        print(f"    Fraud-related: {restatement_data['res_fraud'].sum()}")
        print(f"    SEC investigations: {restatement_data['res_sec_investigation'].sum()}")
        
        print(f"\n  Sample records:")
        print(restatement_data[['company_fkey', 'file_date', 'res_accounting', 'res_fraud']].head(3))
    else:
        print("✗ No restatement data found")
        
except Exception as e:
    print(f"✗ Restatement download failed: {e}")

db.close()
print("\n✓ WRDS connection closed")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DOWNLOAD SUMMARY")
print("=" * 60)

sox_success = 'sox_data' in locals() and len(sox_data) > 0
restate_success = 'restatement_data' in locals() and len(restatement_data) > 0

if sox_success:
    print(f"\n✓ SOX 404: {len(sox_data)} records")
    print(f"  Coverage: {sox_data['company_fkey'].nunique()}/{len(ciks)} companies ({sox_data['company_fkey'].nunique()/len(ciks)*100:.1f}%)")
else:
    print(f"\n✗ SOX 404: No data")

if restate_success:
    print(f"\n✓ Restatements: {len(restatement_data)} records")
    print(f"  Coverage: {restatement_data['company_fkey'].nunique()}/{len(ciks)} companies ({restatement_data['company_fkey'].nunique()/len(ciks)*100:.1f}%)")
else:
    print(f"\n✗ Restatements: No data")

if sox_success or restate_success:
    print("\n" + "=" * 60)
    print("✓ SUCCESS")
    print("=" * 60)
    print("\nNext: python scripts/merge_audit_data.py")
else:
    print("\n" + "=" * 60)
    print("⚠ NO DATA")
    print("=" * 60)