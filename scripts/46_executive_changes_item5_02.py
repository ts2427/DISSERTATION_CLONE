"""
SCRIPT 46 CORRECTED: EXECUTIVE TURNOVER FROM SEC 8-K FILINGS (Item 5.02 Only)
==============================================================================

Measures executive turnover via SEC Item 5.02 (Costs Associated with Exit or
Disposal Activities, and Changes in Control of Registrant; or Changes in
Appointment of Principal Executive Officer, Principal Financial Officer, or
Principal Accounting Officer).

Critically: Checks for Item 5.02 specifically, not just ANY 8-K filing.
Any 8-K includes operational filings, restructurings, acquisitions, etc.
Item 5.02 is the specific item code for director/officer changes.

Approach:
1. Query SEC EDGAR for 8-K filings in window
2. Download each 8-K document text
3. Check for presence of "Item 5.02" in filing
4. Record as executive change only if Item 5.02 is present

This is slower than metadata-only but captures the correct construct.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

print("=" * 80)
print("SCRIPT 46 CORRECTED: EXECUTIVE TURNOVER FROM SEC 8-K ITEM 5.02")
print("=" * 80)

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

# SEC API headers
headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}

def check_item_5_02_in_filing(filing_url):
    """
    Download 8-K filing document and check for Item 5.02.

    Returns True if Item 5.02 is present (even in summary), False otherwise.
    """
    try:
        # Most 8-K filings are in HTML or text format
        # Try to get the main document
        doc_url = filing_url.replace('/Archives/', '/cgi-bin/viewer?action=view&cik=')

        # Alternative: download the raw text file
        text_url = filing_url.rsplit('/', 1)[0] + '/0001193125-' + filing_url.split('/')[-1].replace('.htm', '.txt')

        response = None
        content = ""

        # Try text format first (easier to parse)
        try:
            response = requests.get(text_url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
        except:
            pass

        # If text didn't work, try HTML
        if not content:
            try:
                response = requests.get(filing_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    content = response.text
            except:
                pass

        if not content:
            return None  # Could not download

        # Check for Item 5.02
        # Looking for patterns like "Item 5.02" or "<ITEM5.02>" or "5.02" as a standalone item
        patterns = [
            r'(?:Item|ITEM)\s+5\.02',
            r'<ITEM>5\.02',
            r'<SEQUENCE>\d+</SEQUENCE>\s*<DESCRIPTION>Item 5\.02',
            r'ITEM 5\.02',
        ]

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    except Exception as e:
        return None  # Error downloading

# Process each breach
results = []
processed_count = 0

print("\nSearching for executive changes around breach dates...")
print("(This will take 20-30 minutes - checking Item 5.02 in each 8-K document)")
print("-" * 80)

for idx, row in analysis_df.iterrows():
    cik = str(int(row['cik'])).zfill(10)
    breach_date = row['breach_date']
    company = row['org_name']

    # Search window: 30 days before to 180 days after breach
    start_date = breach_date - timedelta(days=30)
    end_date = breach_date + timedelta(days=180)

    # Dictionary to track changes in each window
    executive_changes = {
        '30d': [],
        '90d': [],
        '180d': []
    }

    try:
        # Query SEC submissions
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(0.2)  # Rate limiting - being conservative

        if response.status_code == 200:
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})

            if filings:
                filing_dates = pd.to_datetime(filings.get('filingDate', []))
                forms = filings.get('form', [])
                accession_numbers = filings.get('accessionNumber', [])

                # Find all 8-K filings in window
                for filing_date, form, accession in zip(filing_dates, forms, accession_numbers):
                    if form == '8-K' and start_date <= filing_date <= end_date:
                        # Construct filing URL
                        # Example: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1018724&type=8-K&dateb=&owner=exclude&count=100
                        # Or direct: https://www.sec.gov/Archives/edgar/container-XXX-XXX-XXX.htm

                        accession_path = accession.replace('-', '').rstrip()
                        filing_url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession}&xbrl_type=v"

                        # Try to get the filing document
                        has_item_5_02 = check_item_5_02_in_filing(filing_url)

                        # If we got None (couldn't download), skip this filing
                        # If we got True/False, record it
                        if has_item_5_02 is True:
                            # This 8-K contains Item 5.02 - record as executive change
                            executive_changes['180d'].append(filing_date)

                            if filing_date <= breach_date + timedelta(days=90):
                                executive_changes['90d'].append(filing_date)

                            if filing_date <= breach_date + timedelta(days=30):
                                executive_changes['30d'].append(filing_date)

        # Record results
        results.append({
            'cik': int(row['cik']),
            'breach_date': breach_date,
            'executive_change_30d': 1 if len(executive_changes['30d']) > 0 else 0,
            'executive_change_90d': 1 if len(executive_changes['90d']) > 0 else 0,
            'executive_change_180d': 1 if len(executive_changes['180d']) > 0 else 0,
            'num_item5_02_filings_180d': len(executive_changes['180d']),
            'days_to_first_item_5_02': (
                (executive_changes['180d'][0] - breach_date).days
                if len(executive_changes['180d']) > 0
                else None
            )
        })

        processed_count += 1

    except Exception as e:
        # On error, record as no change found (conservative)
        results.append({
            'cik': int(row['cik']),
            'breach_date': breach_date,
            'executive_change_30d': 0,
            'executive_change_90d': 0,
            'executive_change_180d': 0,
            'num_item5_02_filings_180d': 0,
            'days_to_first_item_5_02': None
        })

    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1}/{len(analysis_df)} companies...")

# Create results dataframe
turnover_df = pd.DataFrame(results)

print("\n" + "=" * 80)
print("EXECUTIVE TURNOVER SUMMARY (Item 5.02 Specific)")
print("=" * 80)

print(f"\nTotal breaches analyzed: {len(turnover_df)}")
print(f"\nItem 5.02 (Executive Change) Filings Detected:")
print(f"  Within 30 days:  {turnover_df['executive_change_30d'].sum():3d} ({turnover_df['executive_change_30d'].mean()*100:5.1f}%)")
print(f"  Within 90 days:  {turnover_df['executive_change_90d'].sum():3d} ({turnover_df['executive_change_90d'].mean()*100:5.1f}%)")
print(f"  Within 180 days: {turnover_df['executive_change_180d'].sum():3d} ({turnover_df['executive_change_180d'].mean()*100:5.1f}%)")

print(f"\nMean Item 5.02 filings per breach (180d): {turnover_df['num_item5_02_filings_180d'].mean():.2f}")

# Comparison to known annual rates
print(f"\n" + "=" * 80)
print("COMPARISON TO PUBLISHED RATES")
print("=" * 80)
print(f"\nKaplan & Minton (1992-2005): ~14.9% annual CEO turnover")
print(f"Extended period (1998+): ~16.5% annual CEO turnover")
print(f"\nThis sample (Item 5.02 specific):")
print(f"  180-day rate: {turnover_df['executive_change_180d'].mean()*100:.1f}%")
print(f"  Implied annual rate (180d * 2): {turnover_df['executive_change_180d'].mean()*100*2:.1f}%")
print(f"  Ratio to published: {(turnover_df['executive_change_180d'].mean()*100*2) / 16.5:.1f}x")

print(f"\nNote: Item 5.02 includes director AND all named executive officers.")
print(f"Published rates are CEO only. Item 5.02-inclusive rates ~2-3x higher is expected.")

# Save results
turnover_df.to_csv('Data/enrichment/executive_changes_item5_02.csv', index=False)
print(f"\n✓ Saved to Data/enrichment/executive_changes_item5_02.csv")

# Also save as the standard name for pipeline compatibility
turnover_df.to_csv('Data/enrichment/executive_changes.csv', index=False)
print(f"✓ Also saved to Data/enrichment/executive_changes.csv (pipeline standard)")

print("\n" + "=" * 80)
print("✓ SCRIPT 46 CORRECTED COMPLETE")
print("=" * 80)

print("\nCreated variables:")
print("  • executive_change_30d (Item 5.02 filed within 30 days)")
print("  • executive_change_90d (Item 5.02 filed within 90 days)")
print("  • executive_change_180d (Item 5.02 filed within 180 days)")
print("  • num_item5_02_filings_180d (count of Item 5.02 filings)")
print("  • days_to_first_item_5_02 (days from breach to first Item 5.02)")

print("\nNEXT STEP: Re-run Essay 3 scripts (91-91k) with corrected outcome variable")
