"""
Recalculate CAR for records that were newly mapped to parent company PERMNOs
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path

print("=" * 100)
print("RECALCULATE CAR FOR CONSOLIDATED SUBSIDIARY RECORDS")
print("=" * 100)

# Load consolidated dataset
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_CONSOLIDATED.csv')
print(f"Loaded consolidated dataset: {len(df)} records")

# Load CRSP returns and market data
df_returns = pd.read_csv('Data/wrds/crsp_daily_returns.csv')
df_returns['date'] = pd.to_datetime(df_returns['date'])
print(f"Loaded CRSP returns: {len(df_returns)} records")

df_market = pd.read_csv('Data/wrds/market_indices.csv')
df_market['date'] = pd.to_datetime(df_market['date'])
print(f"Loaded market data: {len(df_market)} records")

# Identify records that need CAR calculation
needs_car = df[(df['permno'].notna()) & (df['car_30d'].isna())].copy()
print(f"\nRecords needing CAR calculation: {len(needs_car)}")

# Recalculate CAR
print("\nRecalculating CAR for consolidated records...")

recalc_count = 0
calc_success = 0

for idx, row in needs_car.iterrows():
    permno = row['permno']
    breach_date = pd.to_datetime(row['breach_date'])

    # Get firm returns
    firm_returns = df_returns[df_returns['permno'] == permno].copy()
    if len(firm_returns) == 0:
        continue

    # Get market returns
    market_window = df_market.copy()

    # Calculate CAR_30d
    end_date = breach_date + timedelta(days=30)
    window_returns = firm_returns[(firm_returns['date'] > breach_date) & (firm_returns['date'] <= end_date)]
    market_w = market_window[(market_window['date'] > breach_date) & (market_window['date'] <= end_date)]

    if len(window_returns) > 0 and len(market_w) > 0:
        firm_cum_ret = (1 + window_returns['ret']).prod() - 1
        market_cum_ret = (1 + market_w['vwretd']).prod() - 1
        car_30d = firm_cum_ret - market_cum_ret

        df.at[idx, 'car_30d'] = car_30d * 100
        calc_success += 1

    recalc_count += 1

    if recalc_count % 5 == 0:
        print(f"  Processed {recalc_count}/{len(needs_car)}... ({calc_success} successful)")

print(f"\nCAR calculations completed: {calc_success}/{len(needs_car)} successful")

# Check new coverage
print("\n" + "=" * 100)
print("FINAL COVERAGE AFTER SUBSIDIARY CONSOLIDATION")
print("=" * 100)

print(f"\nCRSP Coverage:")
print(f"  PERMNO: {df['permno'].notna().sum()} ({df['permno'].notna().sum()/len(df)*100:.1f}%)")
print(f"  CAR_30d: {df['car_30d'].notna().sum()} ({df['car_30d'].notna().sum()/len(df)*100:.1f}%)")

print(f"\nImprovements vs original corrected dataset:")
print(f"  PERMNO: 706 -> {df['permno'].notna().sum()} (+{df['permno'].notna().sum()-706} records, {(df['permno'].notna().sum()-706)/706*100:+.1f}%)")
print(f"  CAR_30d: 669 -> {df['car_30d'].notna().sum()} (+{df['car_30d'].notna().sum()-669} records, {(df['car_30d'].notna().sum()-669)/669*100:+.1f}%)")

# Identify remaining failures
remaining = df[df['car_30d'].isna()]
print(f"\nRemaining records without CAR: {len(remaining)} ({len(remaining)/len(df)*100:.1f}%)")

# Save consolidated + recalculated dataset
output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_CONSOLIDATED_WITH_CAR.csv")
df.to_csv(output_path, index=False)

print(f"\nFinal consolidated dataset saved: {output_path}")

print("\n" + "=" * 100)
print("NEXT STEP: Re-run regressions with consolidated dataset")
print("=" * 100)
