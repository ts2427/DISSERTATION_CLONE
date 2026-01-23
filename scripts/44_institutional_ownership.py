import pandas as pd
import wrds
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("SCRIPT 4: INSTITUTIONAL OWNERSHIP DATA")
print("=" * 60)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(df)} breach records")

# Filter to records with CIK
analysis_df = df[df['cik'].notna()].copy()
print(f"✓ Records with CIK: {len(analysis_df)}")

if len(analysis_df) == 0:
    print("\n✗ No records with CIK available")
    exit(0)

# Connect to WRDS
print("\nConnecting to WRDS...")
db = wrds.Connection()
print("✓ Connected")

import os
os.makedirs('Data/enrichment', exist_ok=True)

# Get unique CIKs and breach dates
ciks_dates = analysis_df[['cik', 'breach_date']].dropna().copy()
ciks_dates['cik'] = ciks_dates['cik'].astype(int).astype(str).str.zfill(10)

print(f"\nProcessing {len(ciks_dates)} breach events...")

# Query Thomson Reuters 13F data
results = []

for idx, row in ciks_dates.iterrows():
    cik = row['cik']
    breach_date = row['breach_date']
    
    # Get most recent quarter before breach
    query_date = breach_date - timedelta(days=1)
    
    try:
        # Query 13F holdings
        ownership_query = f"""
            SELECT 
                fdate,
                SUM(shares) as total_shares_held,
                COUNT(DISTINCT mgrno) as num_institutions,
                SUM(shares * prc) as total_value
            FROM tfn.s34
            WHERE cusip IN (
                SELECT cusip 
                FROM comp.security 
                WHERE gvkey IN (
                    SELECT gvkey 
                    FROM comp.company 
                    WHERE cik = '{cik}'
                )
            )
            AND fdate <= '{query_date.strftime('%Y-%m-%d')}'
            AND fdate >= '{(query_date - timedelta(days=180)).strftime('%Y-%m-%d')}'
            GROUP BY fdate
            ORDER BY fdate DESC
            LIMIT 1
        """
        
        ownership_data = db.raw_sql(ownership_query, date_cols=['fdate'])
        
        if len(ownership_data) > 0:
            latest = ownership_data.iloc[0]
            
            results.append({
                'cik': int(cik),
                'breach_date': breach_date,
                'institutional_ownership_date': latest['fdate'],
                'num_institutions': latest['num_institutions'],
                'total_shares_held': latest['total_shares_held'],
                'institutional_value': latest['total_value']
            })
    
    except Exception as e:
        # Silently continue on errors
        continue
    
    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1}/{len(ciks_dates)} events...")

db.close()
print("\n✓ WRDS connection closed")

# Create results dataframe
if len(results) > 0:
    ownership_df = pd.DataFrame(results)
    
    # Calculate institutional ownership percentage (need shares outstanding)
    # For now, just save raw numbers
    
    print("\n" + "=" * 60)
    print("INSTITUTIONAL OWNERSHIP SUMMARY")
    print("=" * 60)
    
    print(f"\nSuccessfully retrieved for {len(ownership_df)} breach events")
    print(f"\nMean institutional holders: {ownership_df['num_institutions'].mean():.1f}")
    print(f"Median institutional holders: {ownership_df['num_institutions'].median():.1f}")
    
    # Create high/low institutional ownership flag
    median_institutions = ownership_df['num_institutions'].median()
    ownership_df['high_institutional_ownership'] = (
        ownership_df['num_institutions'] > median_institutions
    ).astype(int)
    
    ownership_df.to_csv('Data/enrichment/institutional_ownership.csv', index=False)
    print("\n✓ Saved to Data/enrichment/institutional_ownership.csv")
    
    print("\n" + "=" * 60)
    print("✓ SCRIPT 4 COMPLETE")
    print("=" * 60)
    
    print("\nCreated variables:")
    print("  • num_institutions")
    print("  • total_shares_held")
    print("  • institutional_value")
    print("  • high_institutional_ownership")

else:
    print("\n✗ No institutional ownership data found")
    print("Creating placeholder file...")
    
    placeholder = analysis_df[['cik', 'breach_date']].copy()
    placeholder['num_institutions'] = np.nan
    placeholder['high_institutional_ownership'] = np.nan
    
    placeholder.to_csv('Data/enrichment/institutional_ownership.csv', index=False)
    print("✓ Placeholder saved")