"""
Bridge resolved CIKs to CRSP PERMNO and recompute dependent variables
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

print("=" * 100)
print("BRIDGE TO CRSP AND RECOMPUTE DEPENDENT VARIABLES")
print("=" * 100)

# ============================================================================
# STEP 1: Load corrected dataset and CRSP mapping
# ============================================================================
print("\n[1/5] Loading data...")

dataset_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_WITH_CORRECTED_CIK.csv")
df = pd.read_csv(dataset_path)
print(f"  Dataset: {len(df):,} records, {df['resolved_cik'].notna().sum()} with CIK")

# Load ticker-PERMNO mapping
mapping_path = Path("Data/wrds/ticker_permno_mapping.csv")
df_mapping = pd.read_csv(mapping_path)
print(f"  Ticker-PERMNO mapping: {len(df_mapping):,} records")

# Check for name-based columns
print(f"  Mapping columns: {list(df_mapping.columns)}")

# ============================================================================
# STEP 2: Map CIK to ticker (need this first)
# ============================================================================
print("\n[2/5] Mapping CIK to ticker and PERMNO...")

# For firms with CIK, we need to find their ticker
# The dataset already has a 'Map' column with tickers from the original data
if 'Map' not in df.columns:
    print("  WARNING: Dataset missing 'Map' column (original ticker)")
    print("  Will need to look up ticker from company name")

# Convert namedt/nameendt to datetime
df_mapping['namedt'] = pd.to_datetime(df_mapping['namedt'])
df_mapping['nameendt'] = pd.to_datetime(df_mapping['nameendt'])

# For each record, find PERMNO by matching:
# 1. Ticker (if available from original data)
# 2. Breach date within name date range
def find_permno(row, mapping_df):
    """Find PERMNO for a record using ticker and breach date"""
    ticker = row.get('Map')
    breach_date = pd.to_datetime(row['breach_date'])

    if pd.isna(ticker):
        return None

    # Find matching ticker with date range
    matches = mapping_df[mapping_df['ticker'] == ticker]
    if len(matches) == 0:
        return None

    # Find the right permno for the breach date
    for _, m in matches.iterrows():
        if pd.isna(m['namedt']) or pd.isna(m['nameendt']):
            return m['permno']
        if m['namedt'] <= breach_date <= m['nameendt']:
            return m['permno']

    # If no exact date match, use the most recent permno before breach date
    valid_matches = matches[matches['namedt'] <= breach_date]
    if len(valid_matches) > 0:
        return valid_matches.iloc[-1]['permno']

    return None

print("  Mapping CIKs to PERMNOs...")
df['permno'] = df.apply(lambda row: find_permno(row, df_mapping), axis=1)
permno_coverage = df['permno'].notna().sum()
print(f"  PERMNO coverage: {permno_coverage:,} ({permno_coverage/len(df)*100:.1f}%)")

# ============================================================================
# STEP 3: Load CRSP returns
# ============================================================================
print("\n[3/5] Loading CRSP stock returns...")

returns_path = Path("Data/wrds/crsp_daily_returns.csv")
df_returns = pd.read_csv(returns_path)
df_returns['date'] = pd.to_datetime(df_returns['date'])
print(f"  Returns data: {len(df_returns):,} records")
print(f"  Date range: {df_returns['date'].min()} to {df_returns['date'].max()}")

# Load market returns
market_path = Path("Data/wrds/market_indices.csv")
df_market = pd.read_csv(market_path)
df_market['date'] = pd.to_datetime(df_market['date'])
print(f"  Market data: {len(df_market):,} records")

# ============================================================================
# STEP 4: Recompute dependent variables
# ============================================================================
print("\n[4/5] Recomputing dependent variables...")

# Initialize columns
df['car_30d'] = np.nan
df['car_60d'] = np.nan
df['car_90d'] = np.nan
df['bhar_30d'] = np.nan
df['volatility_30d'] = np.nan
df['abnormal_volume_30d'] = np.nan

processed = 0
failed = 0

for idx, row in df.iterrows():
    if idx % 100 == 0:
        print(f"  Processing record {idx + 1}/{len(df)}...")

    permno = row['permno']
    if pd.isna(permno):
        failed += 1
        continue

    breach_date = pd.to_datetime(row['breach_date'])

    # Get stock returns for this firm
    firm_returns = df_returns[df_returns['permno'] == permno].copy()
    if len(firm_returns) == 0:
        failed += 1
        continue

    # Get market returns
    market_returns = df_market.copy()

    # Calculate abnormal returns for different windows
    windows = [30, 60, 90]
    for window in windows:
        end_date = breach_date + timedelta(days=window)

        # Get returns in window
        window_returns = firm_returns[(firm_returns['date'] > breach_date) & (firm_returns['date'] <= end_date)]
        market_window = market_returns[(market_returns['date'] > breach_date) & (market_returns['date'] <= end_date)]

        if len(window_returns) > 0 and len(market_window) > 0:
            # Calculate CAR
            firm_cum_ret = (1 + window_returns['ret']).prod() - 1
            market_cum_ret = (1 + market_window['vwretd']).prod() - 1
            car = firm_cum_ret - market_cum_ret

            df.at[idx, f'car_{window}d'] = car * 100  # Convert to percentage

            # Calculate volatility
            if len(window_returns) > 1:
                volatility = window_returns['ret'].std() * np.sqrt(252)  # Annualized
                df.at[idx, f'volatility_{window}d'] = volatility * 100

    processed += 1

print(f"  Processed: {processed:,} records with valid PERMNO and return data")
print(f"  Failed: {failed:,} records")

# ============================================================================
# STEP 5: Save corrected dataset
# ============================================================================
print("\n[5/5] Saving corrected dataset...")

output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv")
df.to_csv(output_path, index=False)

print(f"\nOutput: {output_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("DEPENDENT VARIABLE RECOMPUTATION COMPLETE")
print("=" * 100)

print(f"""
CRSP MAPPING RESULTS:
  Records with PERMNO: {permno_coverage:,} ({permno_coverage/len(df)*100:.1f}%)
  Records processed: {processed:,}
  Records failed: {failed:,}

DEPENDENT VARIABLES RECOMPUTED:
  CAR (30d): {df['car_30d'].notna().sum():,} records
  CAR (60d): {df['car_60d'].notna().sum():,} records
  CAR (90d): {df['car_90d'].notna().sum():,} records
  Volatility (30d): {df['volatility_30d'].notna().sum():,} records
  Abnormal Volume (30d): {df['abnormal_volume_30d'].notna().sum():,} records

SAMPLE CAR VALUES (CAR_30D):
{df['car_30d'].describe()}

NEXT STEPS:
  1. Re-run H1-H6 regressions with corrected CAR, BHAR, volatility, turnover
  2. Compare new coefficients to original (pre-correction) results
  3. Document all changes in methodology appendix
  4. Interpret impact on dissertation conclusions

OUTPUT: {output_path}
""")

print("=" * 100)
