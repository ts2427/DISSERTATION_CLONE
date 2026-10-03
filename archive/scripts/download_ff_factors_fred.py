"""
DOWNLOAD FAMA-FRENCH FACTORS VIA FRED
========================================================================

Uses pandas_datareader to fetch FF factors from Federal Reserve Economic Data (FRED).
This is reliable when direct Ken French URLs are blocked.
"""

import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("FAMA-FRENCH FACTORS VIA FRED (Federal Reserve Economic Data)")
print("=" * 90)

# Check if factors already exist
output_path = 'Data/wrds/fama_french_factors.csv'
if os.path.exists(output_path):
    factors = pd.read_csv(output_path)
    print(f"\n[OK] Factors already exist at {output_path}")
    print(f"     Date range: {factors['date'].min()} to {factors['date'].max()}")
    print(f"     Columns: {', '.join([c for c in factors.columns if c != 'date'])}")
    exit(0)

print("\nAttempting to download Fama-French factors from FRED...")
print("This may take a minute...\n")

# Try to download factors
try:
    # FF3 factors from FRED
    print("Downloading Mkt-RF (market excess return)...")
    mkt_rf = pdr.get_data_fred('MKTRF', start='2004-01-01', end='2025-12-31')
    mkt_rf.name = 'MKT-RF'
    mkt_rf = mkt_rf.rename('MKT-RF')
    print(f"  [OK] {len(mkt_rf)} observations")

    print("Downloading SMB (size factor)...")
    smb = pdr.get_data_fred('SMB', start='2004-01-01', end='2025-12-31')
    smb = smb.rename('SMB')
    print(f"  [OK] {len(smb)} observations")

    print("Downloading HML (value factor)...")
    hml = pdr.get_data_fred('HML', start='2004-01-01', end='2025-12-31')
    hml = hml.rename('HML')
    print(f"  [OK] {len(hml)} observations")

    # Try to get momentum
    print("Downloading MOM (momentum factor)...")
    try:
        mom = pdr.get_data_fred('MOM', start='2004-01-01', end='2025-12-31')
        mom = mom.rename('MOM')
        print(f"  [OK] {len(mom)} observations")
        has_mom = True
    except Exception as e:
        print(f"  [WARNING] Momentum not available on FRED: {str(e)}")
        print("           Proceeding without momentum for now")
        has_mom = False

    # Try FF5 factors
    print("Downloading RMW (profitability factor)...")
    try:
        rmw = pdr.get_data_fred('RMW', start='2004-01-01', end='2025-12-31')
        rmw = rmw.rename('RMW')
        print(f"  [OK] {len(rmw)} observations")
        has_rmw = True
    except Exception as e:
        print(f"  [WARNING] RMW not available: {str(e)}")
        has_rmw = False

    print("Downloading CMA (investment factor)...")
    try:
        cma = pdr.get_data_fred('CMA', start='2004-01-01', end='2025-12-31')
        cma = cma.rename('CMA')
        print(f"  [OK] {len(cma)} observations")
        has_cma = True
    except Exception as e:
        print(f"  [WARNING] CMA not available: {str(e)}")
        has_cma = False

    # Merge all factors
    print("\nMerging factors on date...")
    merged = pd.concat([mkt_rf, smb, hml], axis=1)

    if has_mom:
        merged = merged.merge(mom, left_index=True, right_index=True, how='outer')
    if has_rmw:
        merged = merged.merge(rmw, left_index=True, right_index=True, how='outer')
    if has_cma:
        merged = merged.merge(cma, left_index=True, right_index=True, how='outer')

    # Reset index and rename
    merged = merged.reset_index()
    merged.rename(columns={'index': 'date'}, inplace=True)

    # Drop any remaining NaN rows
    merged_clean = merged.dropna()

    # Save
    os.makedirs('Data/wrds', exist_ok=True)
    merged_clean.to_csv(output_path, index=False)

    print(f"\n[OK] Factors saved to {output_path}")
    print(f"     Rows: {len(merged_clean)}")
    print(f"     Date range: {merged_clean['date'].min().date()} to {merged_clean['date'].max().date()}")
    print(f"     Columns: {', '.join([c for c in merged_clean.columns if c != 'date'])}")
    print(f"\nYou can now run factor model analysis:")
    print(f"  python scripts/factor_model_carhart_ff5.py")

except Exception as e:
    print(f"\n[ERROR] Failed to download factors: {str(e)}")
    print(f"\nThe data library may be unavailable or network access is restricted.")
    print(f"Try manually downloading from: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html")
    exit(1)

