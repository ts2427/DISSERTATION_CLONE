import pandas as pd
import wrds
import os

print("=" * 60)
print("DOWNLOADING AUDIT ANALYTICS DATA (BEST VERSION)")
print("=" * 60)

# Load breach dataset
breach_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(breach_df)} breach records")

# Get unique CIK codes
ciks_raw = breach_df['cik'].dropna().unique().tolist()
min_date = breach_df['breach_date'].min() - pd.DateOffset(years=2)
max_date = breach_df['breach_date'].max()

print(f"  Unique CIKs: {len(ciks_raw)}")
print(f"  Date range: {min_date.date()} to {max_date.date()}")

# Connect to WRDS
db = wrds.Connection()
print("✓ Connected to WRDS\n")

os.makedirs('Data/audit_analytics', exist_ok=True)

# BEST: Zero-padded CIKs as strings (safest format)
ciks_padded = [str(int(c)).zfill(10) for c in ciks_raw]
cik_list = ','.join([f"'{cik}'" for cik in ciks_padded])

# ============================================================
# 1. SOX 404 INTERNAL CONTROLS
# ============================================================

print("=" * 60)
print("1. SOX 404 INTERNAL CONTROLS")
print("=" * 60)

sox_query = f"""
    SELECT company_fkey, 
           fye_ic_op,
           ic_is_effective,
           count_weak,
           file_date,
           auditor_fkey,
           restatement
    FROM audit.feed11_sox_404_internal_controls
    WHERE company_fkey IN ({cik_list})
    AND fye_ic_op >= '{min_date.strftime('%Y-%m-%d')}'
    AND fye_ic_op <= '{max_date.strftime('%Y-%m-%d')}'
"""

try:
    print("  Querying SOX 404 data...")
    sox_data = db.raw_sql(sox_query, date_cols=['fye_ic_op', 'file_date'])
    
    if len(sox_data) > 0:
        # Convert company_fkey to integer for merging
        sox_data['company_fkey'] = sox_data['company_fkey'].astype(int)
        
        sox_data.to_csv('Data/audit_analytics/sox_404_data.csv', index=False)
        print(f"✓ Downloaded {len(sox_data):,} SOX 404 records")
        print(f"  Unique companies: {sox_data['company_fkey'].nunique()}")
        print(f"  Date range: {sox_data['fye_ic_op'].min()} to {sox_data['fye_ic_op'].max()}")
        
        # Summary stats - HANDLE STRING TYPES
        print(f"\n  Summary:")
        
        # Effective controls
        if sox_data['ic_is_effective'].dtype == 'object':
            effective = (sox_data['ic_is_effective'].astype(str).str.upper() == 'Y').sum()
        else:
            effective = sox_data['ic_is_effective'].sum()
        print(f"    Effective internal controls: {effective}/{len(sox_data)} ({effective/len(sox_data)*100:.1f}%)")
        
        # Material weaknesses
        weak = (pd.to_numeric(sox_data['count_weak'], errors='coerce') > 0).sum()
        print(f"    Material weaknesses: {weak}")
        
        # Restatements
        if sox_data['restatement'].dtype == 'object':
            restate_count = (sox_data['restatement'].astype(str).str.upper() == 'Y').sum()
        else:
            restate_count = sox_data['restatement'].sum()
        print(f"    Restatements: {restate_count}")
        
        print(f"\n  Sample records:")
        print(sox_data[['company_fkey', 'fye_ic_op', 'ic_is_effective', 'count_weak']].head())
    else:
        print("✗ No SOX 404 data found")
        sox_data = pd.DataFrame()
        
except Exception as e:
    print(f"✗ SOX 404 download failed: {e}")
    sox_data = pd.DataFrame()

# ============================================================
# 2. FINANCIAL RESTATEMENTS
# ============================================================

print("\n" + "=" * 60)
print("2. FINANCIAL RESTATEMENTS")
print("=" * 60)

restatement_query = f"""
    SELECT company_fkey, 
           file_date,
           res_begin_date, 
           res_end_date,
           res_accounting, 
           res_fraud,
           res_adverse,
           restatement_notification_key
    FROM audit.feed39_financial_restatements
    WHERE company_fkey IN ({cik_list})
    AND res_begin_date >= '{min_date.strftime('%Y-%m-%d')}'
"""

try:
    print("  Querying restatement data...")
    restatement_data = db.raw_sql(restatement_query, 
                                   date_cols=['file_date', 'res_begin_date', 'res_end_date'])
    
    if len(restatement_data) > 0:
        # Convert company_fkey to integer
        restatement_data['company_fkey'] = restatement_data['company_fkey'].astype(int)
        
        restatement_data.to_csv('Data/audit_analytics/restatements.csv', index=False)
        print(f"✓ Downloaded {len(restatement_data):,} restatement records")
        print(f"  Unique companies: {restatement_data['company_fkey'].nunique()}")
        print(f"  Date range: {restatement_data['res_begin_date'].min()} to {restatement_data['res_end_date'].max()}")
        
        # Summary stats - HANDLE DATA TYPES
        print(f"\n  Summary:")
        for col in ['res_accounting', 'res_fraud', 'res_adverse']:
            if col in restatement_data.columns:
                if restatement_data[col].dtype == 'object':
                    count = (restatement_data[col].astype(str) == '1.0').sum()
                else:
                    count = restatement_data[col].sum()
                print(f"    {col}: {count}")
        
        print(f"\n  Sample records:")
        print(restatement_data[['company_fkey', 'res_begin_date', 'res_accounting', 'res_fraud']].head())
    else:
        print("✗ No restatement data found")
        restatement_data = pd.DataFrame()
        
except Exception as e:
    print(f"✗ Restatement download failed: {e}")
    restatement_data = pd.DataFrame()

db.close()
print("\n✓ WRDS connection closed")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DOWNLOAD SUMMARY")
print("=" * 60)

sox_success = len(sox_data) > 0
restate_success = len(restatement_data) > 0

if sox_success:
    print(f"\n✓ SOX 404: {len(sox_data):,} records, {sox_data['company_fkey'].nunique()} companies")
else:
    print(f"\n✗ SOX 404: No data")

if restate_success:
    print(f"✓ Restatements: {len(restatement_data):,} records, {restatement_data['company_fkey'].nunique()} companies")
else:
    print(f"✗ Restatements: No data")

if sox_success or restate_success:
    print("\n✓ SUCCESS - Ready to merge with breach dataset!")
