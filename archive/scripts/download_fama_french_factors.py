"""
DOWNLOAD FAMA-FRENCH FACTORS
========================================================================

Downloads daily factor data from Ken French data library if not available locally.
Sources:
  - F-F_Research_Data_Factors_daily.CSV (Mkt-RF, SMB, HML)
  - F-F_Momentum_Factor_daily.CSV (Mom/WML)
  - F-F_Research_Data_5_Factors_2x3_daily.CSV (RMW, CMA)

Merged output: Data/wrds/fama_french_factors.csv
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
print("FAMA-FRENCH FACTORS DOWNLOAD & MERGE")
print("=" * 90)

# Check if factors already exist
output_path = 'Data/wrds/fama_french_factors.csv'
if os.path.exists(output_path):
    factors = pd.read_csv(output_path)
    print(f"\n[OK] Factors already exist at {output_path}")
    print(f"     Date range: {factors['date'].min()} to {factors['date'].max()}")
    print(f"     Columns: {', '.join([c for c in factors.columns if c != 'date'])}")
    exit(0)

print("\nDownloading from Ken French data library...")
print("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html\n")

# Base URL for daily factors (zipfiles)
base_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"

# Files to download
files = {
    'three_factors': 'F-F_Research_Data_Factors_daily.zip',
    'momentum': 'F-F_Momentum_Factor_daily.zip',
    'five_factors': 'F-F_Research_Data_5_Factors_2x3_daily.zip'
}

# Download and parse each file
factors_dict = {}

for name, filename in files.items():
    try:
        url = base_url + filename
        print(f"Downloading {filename}...")

        # Download the zip file
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Extract and read CSV from zip
        import zipfile
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Find CSV file in zip (names vary)
            csv_files = [f for f in z.namelist() if f.endswith('.CSV')]
            if not csv_files:
                print(f"  [WARNING] No CSV found in {filename}")
                continue

            csv_name = csv_files[0]
            print(f"  [OK] Found {csv_name}")

            # Read CSV
            with z.open(csv_name) as f:
                df = pd.read_csv(f)

                # Parse date column (format: YYYYMMDD)
                if 'Date' in df.columns:
                    df.rename(columns={'Date': 'date'}, inplace=True)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

                factors_dict[name] = df
                print(f"       Rows: {len(df)}, Date range: {df['date'].min().date()} to {df['date'].max().date()}")

    except Exception as e:
        print(f"  [ERROR] Failed to download {filename}: {str(e)}")
        print(f"         Manual download: {base_url + filename}")

# Merge all factors on date
print(f"\nMerging factors on date...")

if not factors_dict:
    print("[ERROR] No factors successfully downloaded.")
    print("\nManual alternative:")
    print("  1. Visit https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
    print("  2. Download:")
    print("     - Fama-French 3 Factors (daily)")
    print("     - Momentum Factor (daily)")
    print("     - Fama-French 5 Factors (daily)")
    print("  3. Extract and merge on date")
    print("  4. Save to Data/wrds/fama_french_factors.csv")
    exit(1)

# Start with first dataframe
merged = factors_dict[list(factors_dict.keys())[0]].copy()

# Merge others on date
for name, df in list(factors_dict.items())[1:]:
    merged = merged.merge(df, on='date', how='outer')

# Drop rows with NaN (days where some markets didn't trade)
merged = merged.dropna()

# Sort by date
merged = merged.sort_values('date').reset_index(drop=True)

# Standardize column names to uppercase
merged.columns = merged.columns.str.upper()

print(f"\n[OK] Merged factors:")
print(f"     Rows: {len(merged)}")
print(f"     Date range: {merged['DATE'].min()} to {merged['DATE'].max()}")
print(f"     Columns: {', '.join([c for c in merged.columns if c != 'DATE'])}")

# Rename DATE back to date for consistency
merged.rename(columns={'DATE': 'date'}, inplace=True)

# Reorder columns
factor_cols = ['MKT-RF', 'SMB', 'HML', 'MOM', 'RMW', 'CMA']
available_cols = [c for c in factor_cols if c in merged.columns]
merged = merged[['date'] + available_cols]

# Save
os.makedirs('Data/wrds', exist_ok=True)
merged.to_csv(output_path, index=False)

print(f"\n[OK] Factors saved to {output_path}")
print(f"\nYou can now run factor model analysis:")
print(f"  python scripts/factor_model_carhart_ff5.py")

