"""
STEP 1: Build authoritative CIK map from SEC EDGAR company_tickers.json
Normalize and structure data for org_name matching
"""

import json
import pandas as pd
import requests
from pathlib import Path
import re

print("=" * 100)
print("STEP 1: BUILD EDGAR CIK MAP")
print("=" * 100)

# Configuration
EDGAR_URL = "https://www.sec.gov/files/company_tickers.json"
LOCAL_EDGAR_PATH = Path("Data/edgar/company_tickers.json")
OUTPUT_PATH = Path("Data/edgar/cik_ticker_map_normalized.csv")

# Ensure output directory exists
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# STEP 1a: Fetch EDGAR company_tickers.json
# ============================================================================
print("\n[1/3] Fetching SEC EDGAR company_tickers.json...")

if LOCAL_EDGAR_PATH.exists():
    print(f"  Using cached copy at {LOCAL_EDGAR_PATH}")
    with open(LOCAL_EDGAR_PATH, 'r') as f:
        edgar_data = json.load(f)
else:
    print(f"  Downloading from {EDGAR_URL}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(EDGAR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        edgar_data = response.json()

        # Cache locally
        with open(LOCAL_EDGAR_PATH, 'w') as f:
            json.dump(edgar_data, f, indent=2)
        print(f"  Saved to {LOCAL_EDGAR_PATH}")
    except Exception as e:
        print(f"  ERROR: Could not fetch EDGAR data: {e}")
        exit(1)

print(f"  Loaded {len(edgar_data)} companies from EDGAR")

# ============================================================================
# STEP 1b: Normalize company names and structure data
# ============================================================================
print("\n[2/3] Normalizing company data...")

def normalize_name(name):
    """
    Normalize company name for matching:
    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse internal whitespace
    - Remove common legal suffixes (LLC, Inc., Corp., Ltd., etc.)
    - Remove punctuation except spaces
    """
    if not isinstance(name, str):
        return ""

    # Lowercase
    normalized = name.lower().strip()

    # Collapse whitespace
    normalized = re.sub(r'\s+', ' ', normalized)

    # Remove common legal suffixes (but keep as separate field for reference)
    # This helps match "Verizon Communications Inc." to "Verizon Communications"
    suffixes = [
        r'\s+inc\.?$', r'\s+corp\.?$', r'\s+corporation$',
        r'\s+ltd\.?$', r'\s+limited$', r'\s+llc$',
        r'\s+lp$', r'\s+l\.?p\.?$',
        r'\s+co\.?$', r'\s+company$',
        r'\s+na$',  # "NA" = national association
    ]

    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)

    # Remove trailing punctuation and re-collapse whitespace
    normalized = normalized.rstrip('.,;:')
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized


# Parse EDGAR data
records = []
for entry_id, entry_data in edgar_data.items():
    record = {
        'cik': int(entry_data['cik_str']),
        'ticker': entry_data['ticker'].upper(),
        'company_name': entry_data['title'],
        'company_name_normalized': normalize_name(entry_data['title']),
    }
    records.append(record)

df_edgar = pd.DataFrame(records)

print(f"  Parsed {len(df_edgar)} companies")
print(f"\n  Sample entries:")
for idx in range(min(5, len(df_edgar))):
    row = df_edgar.iloc[idx]
    print(f"    CIK {row['cik']:>10d} | {row['ticker']:>6s} | {row['company_name']}")

# Check for duplicates
dup_ciks = df_edgar['cik'].duplicated().sum()
dup_tickers = df_edgar['ticker'].duplicated().sum()

print(f"\n  Quality checks:")
print(f"    Duplicate CIKs: {dup_ciks}")
print(f"    Duplicate tickers: {dup_tickers}")

if dup_ciks > 0:
    print(f"    WARNING: Some CIKs appear multiple times (holdings, subsidiaries)")
    print(f"    Keeping all entries for visibility")

# ============================================================================
# STEP 1c: Save normalized CIK map
# ============================================================================
print("\n[3/3] Saving normalized CIK map...")

# Sort by CIK for easy lookup
df_edgar_sorted = df_edgar.sort_values('cik').reset_index(drop=True)

# Save to CSV
df_edgar_sorted.to_csv(OUTPUT_PATH, index=False)

print(f"  Saved to {OUTPUT_PATH}")
print(f"\n  File statistics:")
print(f"    Total records: {len(df_edgar_sorted)}")
print(f"    Columns: {', '.join(df_edgar_sorted.columns)}")
print(f"    File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1 COMPLETE: EDGAR CIK MAP READY FOR MATCHING")
print("=" * 100)

print(f"\nAuthoritative reference data prepared:")
print(f"  Input: SEC EDGAR company_tickers.json ({len(df_edgar_sorted)} companies)")
print(f"  Output: {OUTPUT_PATH}")
print(f"\nColumns in output CSV:")
print(f"  - cik: SEC Central Index Key (integer)")
print(f"  - ticker: Stock ticker symbol (uppercase)")
print(f"  - company_name: Official company name from EDGAR")
print(f"  - company_name_normalized: Lowercased, suffixes removed, for matching")

print(f"\nNext: Match 779 PRC org_names against this reference in Step 2")
print("=" * 100)
