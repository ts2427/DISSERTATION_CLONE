import pandas as pd
import wrds
from datetime import datetime
import os

print("=" * 60)
print("DOWNLOADING AUDIT ANALYTICS DATA (FIXED V2)")
print("=" * 60)

# Load breach dataset
breach_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(breach_df)} breach records")

# Get unique CIK codes
cik_col = 'CIK CODE' if 'CIK CODE' in breach_df.columns else 'cik'
ciks_raw = breach_df[cik_col].dropna().unique().tolist()

min_date = breach_df['breach_date'].min() - pd.DateOffset(years=2)
max_date = breach_df['breach_date'].max()

print(f"  Unique CIKs: {len(ciks_raw)}")
print(f"  Date range: {min_date.date()} to {max_date.date()}")

# Connect to WRDS
print("\n[1/3] Connecting to WRDS...")
db = wrds.Connection()
print("✓ Connected")

# Zero-pad CIKs to 10 digits AND add quotes
ciks_padded = [str(int(c)).zfill(10) for c in ciks_raw]
cik_list = ','.join([f"'{cik}'" for cik in ciks_padded])

print(f"\n✓ Created properly formatted CIK list")
print(f"  Sample: {ciks_padded[:3]}")

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
        
        # FIXED: Handle string types in summary stats
        try:
            if 'ic_is_effective' in sox_data.columns:
                # Convert to boolean if string
                if sox_data['ic_is_effective'].dtype == 'object':
                    effective = (sox_data['ic_is_effective'].astype(str).str.upper() == 'Y').sum()
                else:
                    effective = sox_data['ic_is_effective'].sum()
                print(f"  Effective internal controls: {effective}/{len(sox_data)} ({effective/len(sox_data)*100:.1f}%)")
            
            if 'count_weak' in sox_data.columns:
                weak = (sox_data['count_weak'] > 0).sum()
                print(f"  Records with material weaknesses: {weak}")
        except Exception as e:
            print(f"  (Note: Summary stats error: {e})")
        
    else:
        print("✗ No SOX 404 data found")
        
except Exception as e:
    print(f"✗ SOX 404 download failed: {e}")
    sox_data = pd.DataFrame()

# ============================================================
# 2. FINANCIAL RESTATEMENTS - FIXED COLUMNS
# ============================================================

print("\n[3/3] Downloading financial restatement data...")

# FIXED: Remove res_sec_invest (doesn't exist)
restatement_query = f"""
    SELECT company_fkey, file_date, 
           res_begin_date, res_end_date,
           res_accounting, res_adverse, res_fraud, 
           restatement_key
    FROM audit.feed39_financial_restatements
    WHERE company_fkey IN ({cik_list})
    AND res_begin_date >= '{min_date.strftime('%Y-%m-%d')}'
"""

try:
    print("  Querying restatement data...")
    restatement_data = db.raw_sql(restatement_query, 
                                   date_cols=['file_date', 'res_begin_date', 'res_end_date'])
    
    if len(restatement_data) > 0:
        restatement_data.to_csv('Data/audit_analytics/restatements.csv', index=False)
        print(f"✓ Downloaded {len(restatement_data):,} restatement records")
        print(f"  Unique companies: {restatement_data['company_fkey'].nunique()}")
        print(f"  Date range: {restatement_data['res_begin_date'].min()} to {restatement_data['res_begin_date'].max()}")
        
        # Summary stats - handle data type issues
        try:
            if 'res_accounting' in restatement_data.columns:
                if restatement_data['res_accounting'].dtype == 'object':
                    acct = (restatement_data['res_accounting'].astype(str).str.upper() == 'Y').sum()
                else:
                    acct = restatement_data['res_accounting'].sum()
                print(f"  Accounting restatements: {acct}")
            
            if 'res_fraud' in restatement_data.columns:
                if restatement_data['res_fraud'].dtype == 'object':
                    fraud = (restatement_data['res_fraud'].astype(str).str.upper() == 'Y').sum()
                else:
                    fraud = restatement_data['res_fraud'].sum()
                print(f"  Fraud-related: {fraud}")
        except Exception as e:
            print(f"  (Note: Summary stats error: {e})")
        
    else:
        print("✗ No restatement data found")
        restatement_data = pd.DataFrame()
        
except Exception as e:
    print(f"✗ Restatement download failed: {e}")
    restatement_data = pd.DataFrame()

# Close connection
db.close()
print("\n✓ WRDS connection closed")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DOWNLOAD SUMMARY")
print("=" * 60)

sox_success = len(sox_data) > 0 if 'sox_data' in locals() else False
restate_success = len(restatement_data) > 0 if 'restatement_data' in locals() else False

if sox_success:
    print(f"\n✓ SOX 404 Data: {len(sox_data):,} records")
    print(f"  Companies: {sox_data['company_fkey'].nunique()}")
    print(f"  Coverage: {sox_data['company_fkey'].nunique()}/{len(ciks_raw)} CIKs ({sox_data['company_fkey'].nunique()/len(ciks_raw)*100:.1f}%)")
else:
    print(f"\n✗ SOX 404 Data: No records")

if restate_success:
    print(f"\n✓ Restatement Data: {len(restatement_data):,} records")
    print(f"  Companies: {restatement_data['company_fkey'].nunique()}")
else:
    print(f"\n✗ Restatement Data: No records")

if sox_success or restate_success:
    print("\n" + "=" * 60)
    print("✓ SUCCESS")
    print("=" * 60)
    print("\nAudit Analytics data ready for analysis!")
    print("\nYou now have governance quality data for:")
    print("  - Internal control effectiveness (SOX 404)")
    if restate_success:
        print("  - Financial restatements")
    
    print("\nThis enhances your Essay 3 analysis:")
    print("  - Test if governance moderates disclosure timing effects")
    print("  - Control for firm quality in event study")
else:
    print("\n⚠ Partial success: SOX 404 only")