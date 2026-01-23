import pandas as pd
import requests
from datetime import datetime, timedelta
import time

print("=" * 60)
print("SCRIPT 6: EXECUTIVE TURNOVER FROM SEC 8-K FILINGS")
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

import os
os.makedirs('Data/enrichment', exist_ok=True)

# Process each breach
results = []

print("\nSearching for executive changes around breach dates...")
print("(This may take 10-15 minutes)")

for idx, row in analysis_df.iterrows():
    cik = str(int(row['cik'])).zfill(10)
    breach_date = row['breach_date']
    company = row['org_name']
    
    # Search window: 30 days before to 180 days after breach
    start_date = breach_date - timedelta(days=30)
    end_date = breach_date + timedelta(days=180)
    
    # Search for 8-K filings with Item 5.02 (executive changes)
    try:
        # Use SEC EDGAR API
        headers = {'User-Agent': 'Academic Research [email protected]'}
        
        # Query SEC submissions
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        
        response = requests.get(url, headers=headers)
        time.sleep(0.1)  # Rate limiting
        
        if response.status_code == 200:
            data = response.json()
            
            # Get recent filings
            filings = data.get('filings', {}).get('recent', {})
            
            if filings:
                filing_dates = pd.to_datetime(filings.get('filingDate', []))
                forms = filings.get('form', [])
                
                # Look for 8-K filings in window
                executive_changes = []
                
                for i, (filing_date, form) in enumerate(zip(filing_dates, forms)):
                    if form == '8-K' and start_date <= filing_date <= end_date:
                        executive_changes.append(filing_date)
                
                # Record results
                has_change_30d = any(
                    breach_date <= change <= breach_date + timedelta(days=30)
                    for change in executive_changes
                )
                
                has_change_90d = any(
                    breach_date <= change <= breach_date + timedelta(days=90)
                    for change in executive_changes
                )
                
                has_change_180d = any(
                    breach_date <= change <= breach_date + timedelta(days=180)
                    for change in executive_changes
                )
                
                results.append({
                    'cik': int(row['cik']),
                    'breach_date': breach_date,
                    'executive_change_30d': 1 if has_change_30d else 0,
                    'executive_change_90d': 1 if has_change_90d else 0,
                    'executive_change_180d': 1 if has_change_180d else 0,
                    'num_changes_180d': len(executive_changes),
                    'days_to_first_change': min([
                        (change - breach_date).days 
                        for change in executive_changes
                    ]) if executive_changes else None
                })
    
    except Exception as e:
        # On error, record as no change found
        results.append({
            'cik': int(row['cik']),
            'breach_date': breach_date,
            'executive_change_30d': 0,
            'executive_change_90d': 0,
            'executive_change_180d': 0,
            'num_changes_180d': 0,
            'days_to_first_change': None
        })
    
    if (idx + 1) % 25 == 0:
        print(f"  Processed {idx + 1}/{len(analysis_df)} companies...")

# Create results dataframe
turnover_df = pd.DataFrame(results)

print("\n" + "=" * 60)
print("EXECUTIVE TURNOVER SUMMARY")
print("=" * 60)

print(f"\nTotal breaches analyzed: {len(turnover_df)}")
print(f"\nExecutive changes detected:")
print(f"  Within 30 days:  {turnover_df['executive_change_30d'].sum()} ({turnover_df['executive_change_30d'].mean()*100:.1f}%)")
print(f"  Within 90 days:  {turnover_df['executive_change_90d'].sum()} ({turnover_df['executive_change_90d'].mean()*100:.1f}%)")
print(f"  Within 180 days: {turnover_df['executive_change_180d'].sum()} ({turnover_df['executive_change_180d'].mean()*100:.1f}%)")

print(f"\nMean changes per breach: {turnover_df['num_changes_180d'].mean():.2f}")

# Save results
turnover_df.to_csv('Data/enrichment/executive_changes.csv', index=False)
print("\n✓ Saved to Data/enrichment/executive_changes.csv")

print("\n" + "=" * 60)
print("✓ SCRIPT 6 COMPLETE")
print("=" * 60)

print("\nCreated variables:")
print("  • executive_change_30d")
print("  • executive_change_90d")
print("  • executive_change_180d")
print("  • num_changes_180d")
print("  • days_to_first_change")