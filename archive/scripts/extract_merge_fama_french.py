"""
Extract and merge Fama-French factor files from Ken French data library
"""

import pandas as pd
import os

print("=" * 90)
print("EXTRACTING AND MERGING FAMA-FRENCH FACTORS")
print("=" * 90)

data_dir = "Data"

# Define the three files
files = {
    'ff3': 'F-F_Research_Data_Factors_daily.csv',
    'momentum': 'F-F_Momentum_Factor_daily.csv',
    'ff5': 'F-F_Research_Data_5_Factors_2x3_daily.csv'
}

# Read and process each file
dfs = {}

for key, filename in files.items():
    filepath = os.path.join(data_dir, filename)
    print(f"\nReading {filename}...")

    # Read the CSV, skipping Ken French's header rows (first 4 lines are metadata)
    try:
        df = pd.read_csv(filepath, skiprows=4)
    except Exception as e:
        print(f"  Error with skiprows=4, trying skiprows=0...")
        df = pd.read_csv(filepath)

    # First column is the date in YYYYMMDD format
    # Ken French files have trailing copyright lines, so filter to numeric dates only
    first_col = df.columns[0]
    df.rename(columns={first_col: 'date'}, inplace=True)

    # Filter to rows where date is numeric (YYYYMMDD format)
    df['date'] = pd.to_numeric(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['date'] = df['date'].astype(int).astype(str)

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    print(f"  Rows: {len(df)}, Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"  Columns: {', '.join(df.columns.tolist())}")

    dfs[key] = df

# Merge all three on date
print(f"\nMerging factors on date...")

# Start with FF3 (best coverage: 1926-2026)
merged = dfs['ff3'].copy()

# Left merge with FF5 (1963-2026) - keeps all FF3 dates
merged = merged.merge(dfs['ff5'], on='date', how='left', suffixes=('_FF3', '_FF5'))
print(f"  After FF5 merge (left): {len(merged)} rows")

# Left merge with momentum (1926-2026) - keeps all dates from above
merged = merged.merge(dfs['momentum'], on='date', how='left', suffixes=('', '_MOM'))
print(f"  After momentum merge (left): {len(merged)} rows")

# For analysis period (breach data is 2005-2026), drop rows before 2004
merged = merged[merged['date'] >= pd.to_datetime('2004-01-01')]
print(f"  After filtering to 2004+: {len(merged)} rows")

# Clean up column names - the FF3 columns should have no suffix
# Rename FF5 duplicates if they exist
if 'Mkt-RF_FF5' in merged.columns:
    merged['Mkt-RF'] = merged['Mkt-RF_FF3'].fillna(merged['Mkt-RF_FF5'])
    merged['SMB'] = merged['SMB_FF3'].fillna(merged['SMB_FF5'])
    merged['HML'] = merged['HML_FF3'].fillna(merged['HML_FF5'])
    merged = merged.drop(['Mkt-RF_FF3', 'SMB_FF3', 'HML_FF3', 'Mkt-RF_FF5', 'SMB_FF5', 'HML_FF5'], axis=1)

# Handle momentum column names
if 'Unnamed: 1' in merged.columns or 'Unnamed: 1_MOM' in merged.columns:
    mom_col = 'Unnamed: 1_MOM' if 'Unnamed: 1_MOM' in merged.columns else 'Unnamed: 1'
    merged.rename(columns={mom_col: 'MOM'}, inplace=True)
    merged = merged.drop([c for c in merged.columns if 'Unnamed: 2' in c], axis=1, errors='ignore')

# Drop rows where key factors are missing
key_cols = ['Mkt-RF', 'SMB', 'HML']
merged_clean = merged.dropna(subset=key_cols)
print(f"\nAfter removing rows with missing key factors: {len(merged_clean)} rows")

# Sort by date
merged_clean = merged_clean.sort_values('date').reset_index(drop=True)

# Standardize column names to uppercase and clean
merged_clean.columns = merged_clean.columns.str.upper().str.strip()

print(f"\nFinal columns: {', '.join(merged_clean.columns.tolist())}")
print(f"Date range: {merged_clean['DATE'].min().date()} to {merged_clean['DATE'].max().date()}")

# Rename DATE back to date for consistency with other files
merged_clean.rename(columns={'DATE': 'date'}, inplace=True)

# Reorder: date first, then all factor columns
factor_cols = [c for c in merged_clean.columns if c != 'date']
merged_clean = merged_clean[['date'] + factor_cols]

# Save to wrds directory
output_path = os.path.join(data_dir, 'wrds', 'fama_french_factors.csv')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

merged_clean.to_csv(output_path, index=False)

print(f"\n[OK] Factors saved to: {output_path}")
print(f"\nFile statistics:")
print(f"  Rows: {len(merged_clean)}")
print(f"  Columns: {len(merged_clean.columns)}")
print(f"  Date range: {merged_clean['date'].min().date()} to {merged_clean['date'].max().date()}")
print(f"  Factor columns: {', '.join([c for c in merged_clean.columns if c != 'date'])}")

print(f"\nYou can now run the factor model analysis:")
print(f"  python scripts/factor_model_carhart_ff5.py")

