"""
DOWNLOAD FAMA-FRENCH FACTORS - ALTERNATIVE METHOD
========================================================================

Uses updated Ken French data library URLs (direct CSV links, not zips).
"""

import pandas as pd
import numpy as np
import requests
import io
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("FAMA-FRENCH FACTORS DOWNLOAD (ALTERNATIVE URLS)")
print("=" * 90)

# Check if factors already exist
output_path = 'Data/wrds/fama_french_factors.csv'
if os.path.exists(output_path):
    factors = pd.read_csv(output_path)
    print(f"\n[OK] Factors already exist at {output_path}")
    print(f"     Date range: {factors['date'].min()} to {factors['date'].max()}")
    print(f"     Columns: {', '.join([c for c in factors.columns if c != 'date'])}")
    exit(0)

print("\nAttempting to download from Ken French data library...")
print("Alternative URL structures being tried...\n")

# Alternative URL structures
urls = {
    'ff3_csv': [
        'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily.CSV',
        'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/fama_french_3_factors_daily.csv',
    ],
    'momentum_csv': [
        'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily.CSV',
    ],
    'ff5_csv': [
        'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily.CSV',
    ]
}

downloaded = {}

# Try downloading FF3 factors
print("Attempting FF3 (Mkt-RF, SMB, HML) download...")
for url in urls['ff3_csv']:
    try:
        print(f"  Trying: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            print(f"  [OK] Downloaded. Rows: {len(df)}")
            downloaded['ff3'] = df
            break
    except Exception as e:
        continue

if 'ff3' not in downloaded:
    print("  [FAILED] Could not download FF3")

# Try downloading momentum factor
print("\nAttempting Momentum (Mom/WML) download...")
for url in urls['momentum_csv']:
    try:
        print(f"  Trying: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            print(f"  [OK] Downloaded. Rows: {len(df)}")
            downloaded['momentum'] = df
            break
    except Exception as e:
        continue

if 'momentum' not in downloaded:
    print("  [FAILED] Could not download Momentum")

# Try downloading FF5
print("\nAttempting FF5 (RMW, CMA) download...")
for url in urls['ff5_csv']:
    try:
        print(f"  Trying: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            print(f"  [OK] Downloaded. Rows: {len(df)}")
            downloaded['ff5'] = df
            break
    except Exception as e:
        continue

if 'ff5' not in downloaded:
    print("  [FAILED] Could not download FF5")

# Report results
if not downloaded:
    print("\n" + "=" * 90)
    print("[ACTION REQUIRED] Factor data could not be downloaded automatically.")
    print("=" * 90)
    print("\nManual download instructions:")
    print("1. Visit: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
    print("2. Download these daily files:")
    print("   - Fama-French 3 Factors")
    print("   - Momentum Factor")
    print("   - Fama-French 5 Factors")
    print("3. Each will be a zip file. Extract to get CSV.")
    print("4. For each CSV:")
    print("   - If header row looks like '20050101' (YYYYMMDD), convert date column")
    print("   - Merge all three on date")
    print("5. Save merged file to: Data/wrds/fama_french_factors.csv")
    print("\nAlternative: pandas_datareader can sometimes fetch from FRED, but availability varies.")
    exit(1)

print("\n" + "=" * 90)
print("MERGING FACTORS")
print("=" * 90)

# Merge downloaded factors
merged = None
for source, df in downloaded.items():
    print(f"\nProcessing {source}...")

    # Find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'date_' in col.lower():
            date_col = col
            break

    if date_col is None:
        # Maybe the first column is date (as numeric YYYYMMDD)
        date_col = df.columns[0]

    # Convert date column
    if df[date_col].dtype == 'object':
        df['date'] = pd.to_datetime(df[date_col], format='%Y%m%d', errors='coerce')
    else:
        df['date'] = pd.to_datetime(df[date_col].astype(str), format='%Y%m%d', errors='coerce')

    # Drop original date column if different
    if date_col != 'date':
        df = df.drop(columns=[date_col])

    # Standardize column names to uppercase
    df.columns = df.columns.str.upper()

    print(f"  Rows: {len(df)}, Date range: {df['DATE'].min()} to {df['DATE'].max()}")

    if merged is None:
        merged = df
    else:
        merged = merged.merge(df, on='DATE', how='outer')

# Rename DATE to date for consistency
merged.rename(columns={'DATE': 'date'}, inplace=True)

# Drop rows with missing values
merged_clean = merged.dropna()

print(f"\nAfter merge and dropna: {len(merged_clean)} rows")

# Reorder columns: date first, then factors
factor_cols = ['MKT-RF', 'SMB', 'HML', 'MOM', 'RMW', 'CMA']
available_cols = [c for c in factor_cols if c in merged_clean.columns]
merged_clean = merged_clean[['date'] + available_cols]

# Sort by date
merged_clean = merged_clean.sort_values('date').reset_index(drop=True)

# Save
os.makedirs('Data/wrds', exist_ok=True)
merged_clean.to_csv(output_path, index=False)

print(f"\n[OK] Factors saved to {output_path}")
print(f"     Rows: {len(merged_clean)}")
print(f"     Date range: {merged_clean['date'].min()} to {merged_clean['date'].max()}")
print(f"     Columns: {', '.join([c for c in merged_clean.columns if c != 'date'])}")

print(f"\nYou can now run factor model analysis:")
print(f"  python scripts/factor_model_carhart_ff5.py")

