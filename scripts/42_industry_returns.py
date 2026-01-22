import pandas as pd
import wrds
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("SCRIPT 2: INDUSTRY-ADJUSTED RETURNS")
print("=" * 60)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(df)} breach records")

# Filter to records with CRSP data
analysis_df = df[df['has_crsp_data'] == True].copy()
print(f"✓ Records with CRSP data: {len(analysis_df)}")

if len(analysis_df) == 0:
    print("\n✗ No records with CRSP data available")
    print("Skipping industry-adjusted returns")
    exit(0)

# Connect to WRDS
print("\nConnecting to WRDS...")
db = wrds.Connection()
print("✓ Connected")

import os
os.makedirs('Data/enrichment', exist_ok=True)

# Get unique CIKs with breach dates
ciks_dates = analysis_df[['cik', 'breach_date', 'sic']].dropna().copy()
ciks_dates['cik'] = ciks_dates['cik'].astype(int)
ciks_dates['sic'] = ciks_dates['sic'].astype(int)

print(f"\nProcessing {len(ciks_dates)} breach events...")

# Step 1: Get CRSP data for breach firms
print("\nStep 1: Getting CRSP data for breach firms...")

# Create date range for queries (get data ±60 days around breaches)
min_date = ciks_dates['breach_date'].min() - timedelta(days=60)
max_date = ciks_dates['breach_date'].max() + timedelta(days=60)

# Get PERMNO mapping
cik_list = ','.join([str(int(c)) for c in ciks_dates['cik'].unique()])

permno_query = f"""
    SELECT ncusip, permno
    FROM crsp.stocknames
    WHERE ncusip IN (
        SELECT ncusip 
        FROM comp.security 
        WHERE gvkey IN (
            SELECT gvkey 
            FROM comp.company 
            WHERE cik IN ({cik_list})
        )
    )
"""

try:
    permno_mapping = db.raw_sql(permno_query)
    print(f"✓ Found PERMNO mappings: {len(permno_mapping)}")
except Exception as e:
    print(f"⚠ Could not get PERMNO mapping: {e}")
    print("Creating simplified industry returns without firm-specific matching")
    permno_mapping = pd.DataFrame()

# Step 2: Get industry returns using SIC codes
print("\nStep 2: Calculating industry-adjusted returns...")

results = []

for idx, row in ciks_dates.iterrows():
    breach_date = row['breach_date']
    sic = row['sic']
    cik = row['cik']
    
    # Get industry peers (same 2-digit SIC)
    sic_2digit = int(sic / 100)
    
    # Date windows
    start_date = breach_date - timedelta(days=30)
    end_date = breach_date + timedelta(days=30)
    
    try:
        # Query industry returns
        industry_query = f"""
            SELECT date, AVG(ret) as industry_ret
            FROM crsp.dsf a
            INNER JOIN crsp.dsenames b ON a.permno = b.permno
            WHERE b.siccd >= {sic_2digit * 100}
            AND b.siccd < {(sic_2digit + 1) * 100}
            AND date >= '{start_date.strftime('%Y-%m-%d')}'
            AND date <= '{end_date.strftime('%Y-%m-%d')}'
            GROUP BY date
            ORDER BY date
        """
        
        industry_returns = db.raw_sql(industry_query, date_cols=['date'])
        
        if len(industry_returns) > 0:
            # Calculate industry CAR
            breach_window = industry_returns[
                (industry_returns['date'] >= breach_date - timedelta(days=1)) &
                (industry_returns['date'] <= breach_date + timedelta(days=30))
            ]
            
            if len(breach_window) > 0:
                industry_car_30d = breach_window['industry_ret'].sum() * 100
                
                results.append({
                    'cik': cik,
                    'breach_date': breach_date,
                    'industry_car_30d': industry_car_30d,
                    'sic_2digit': sic_2digit,
                    'industry_obs': len(breach_window)
                })
    
    except Exception as e:
        print(f"  ⚠ Error for CIK {cik}: {e}")
        continue
    
    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1}/{len(ciks_dates)} events...")

db.close()
print("\n✓ WRDS connection closed")

# Create results dataframe
if len(results) > 0:
    industry_df = pd.DataFrame(results)
    
    # Merge with original data
    merged_df = analysis_df.merge(
        industry_df[['cik', 'breach_date', 'industry_car_30d']],
        on=['cik', 'breach_date'],
        how='left'
    )
    
    # Calculate industry-adjusted CAR
    merged_df['industry_adjusted_car_30d'] = merged_df['car_30d'] - merged_df['industry_car_30d']
    
    # Save results
    output_df = merged_df[['cik', 'breach_date', 'car_30d', 'industry_car_30d', 
                           'industry_adjusted_car_30d']].copy()
    
    output_df.to_csv('Data/enrichment/industry_adjusted_returns.csv', index=False)
    
    print("\n" + "=" * 60)
    print("INDUSTRY-ADJUSTED RETURNS SUMMARY")
    print("=" * 60)
    
    print(f"\nSuccessfully calculated for {len(output_df[output_df['industry_car_30d'].notna()])} events")
    print(f"\nMean values:")
    print(f"  Raw CAR (30d):               {output_df['car_30d'].mean():.4f}%")
    print(f"  Industry CAR (30d):          {output_df['industry_car_30d'].mean():.4f}%")
    print(f"  Industry-adjusted CAR (30d): {output_df['industry_adjusted_car_30d'].mean():.4f}%")
    
    print("\n✓ Saved to Data/enrichment/industry_adjusted_returns.csv")
    
    print("\n" + "=" * 60)
    print("✓ SCRIPT 2 COMPLETE")
    print("=" * 60)
    
    print("\nCreated variables:")
    print("  • industry_car_30d")
    print("  • industry_adjusted_car_30d")

else:
    print("\n✗ No industry returns calculated")
    print("Creating placeholder file...")
    
    placeholder = analysis_df[['cik', 'breach_date']].copy()
    placeholder['industry_car_30d'] = np.nan
    placeholder['industry_adjusted_car_30d'] = np.nan
    
    placeholder.to_csv('Data/enrichment/industry_adjusted_returns.csv', index=False)
    print("✓ Placeholder saved")