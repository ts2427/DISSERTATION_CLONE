"""
DATA PREPARATION & VALIDATION FOR FIRM-BY-FIRM SCM
===================================================

This script helps you:
1. Load and inspect dissertation data
2. Validate required variables
3. Create required variables if missing
4. Prepare data for firm_by_firm_scm.R
5. Check sample sizes and data quality

USAGE:
------
python scm_data_preparation.py --input your_data.csv --output prepared_data.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import argparse
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Required variables for SCM analysis
REQUIRED_VARS = {
    'firm_id': 'numeric or string',
    'firm_name': 'string',
    'year': 'numeric (2000-2024)',
    'sic_code': 'numeric (4-digit SIC)',
    'car_30d': 'numeric (percentage)',
    'volatility_change': 'numeric (percentage points)',
    'executive_change_30d': 'binary (0/1)',
}

# FCC SIC codes
FCC_SICS = [4813, 4899, 4841]

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_data(df):
    """Check that data has required structure"""
    issues = []

    # Check required variables
    for var, dtype in REQUIRED_VARS.items():
        if var not in df.columns:
            issues.append(f"Missing required variable: {var} ({dtype})")
        else:
            # Check for excessive missing values
            missing_pct = df[var].isna().sum() / len(df) * 100
            if missing_pct > 20:
                issues.append(f"  WARNING: {var}: {missing_pct:.1f}% missing (acceptable if < 20%)")

    return issues


def auto_create_variables(df):
    """Create missing variables from available columns"""
    created = []

    # log_assets
    if 'log_assets' not in df.columns and 'total_assets' in df.columns:
        df['log_assets'] = np.log(df['total_assets'] + 1)
        created.append('log_assets (from total_assets)')

    # leverage
    if 'leverage' not in df.columns and 'total_debt' in df.columns and 'total_assets' in df.columns:
        df['leverage'] = df['total_debt'] / (df['total_assets'] + 1)
        created.append('leverage (from total_debt / total_assets)')

    # roa
    if 'roa' not in df.columns and 'net_income' in df.columns and 'total_assets' in df.columns:
        df['roa'] = (df['net_income'] / (df['total_assets'] + 1)) * 100
        created.append('roa (from net_income / total_assets)')

    # log_records_affected
    if 'log_records_affected' not in df.columns and 'records_affected' in df.columns:
        df['log_records_affected'] = np.log(df['records_affected'] + 1)
        created.append('log_records_affected (from records_affected)')

    return df, created


def check_sample_composition(df):
    """Analyze sample composition"""
    print("\n" + "="*70)
    print("SAMPLE COMPOSITION")
    print("="*70)

    # FCC vs non-FCC
    if 'sic_code' in df.columns:
        df['is_fcc'] = df['sic_code'].isin(FCC_SICS)
        fcc_count = df['is_fcc'].sum()
        non_fcc_count = (~df['is_fcc']).sum()

        print(f"\nFirm Type Distribution:")
        print(f"  FCC firms:     {fcc_count:>6} ({fcc_count/len(df)*100:>5.1f}%)")
        print(f"  Non-FCC firms: {non_fcc_count:>6} ({non_fcc_count/len(df)*100:>5.1f}%)")

        # Check FCC firm count
        unique_fcc = df[df['is_fcc']]['firm_id'].nunique()
        print(f"\n  Unique FCC firms: {unique_fcc}")
        if unique_fcc < 10:
            print(f"  WARNING: Only {unique_fcc} unique FCC firms (recommend >=20)")

    # Year distribution
    if 'year' in df.columns:
        print(f"\nYear Distribution:")
        year_counts = df['year'].value_counts().sort_index()
        print(f"  Min year: {df['year'].min()}")
        print(f"  Max year: {df['year'].max()}")
        print(f"  Breaches per year (mean): {year_counts.mean():.1f}")

    # Outcome variables
    print(f"\nOutcome Variables:")
    if 'car_30d' in df.columns:
        print(f"  CAR 30-day:     mu={df['car_30d'].mean():>7.2f}%, sigma={df['car_30d'].std():>6.2f}%, n={df['car_30d'].notna().sum()}")

    if 'volatility_change' in df.columns:
        print(f"  Volatility D:   mu={df['volatility_change'].mean():>7.2f}pp, sigma={df['volatility_change'].std():>6.2f}pp, n={df['volatility_change'].notna().sum()}")

    if 'executive_change_30d' in df.columns:
        rate = df['executive_change_30d'].mean() * 100
        print(f"  Exec change 30d: {rate:.1f}% (n={df['executive_change_30d'].notna().sum()})")


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def main():
    """Main data preparation workflow"""
    parser = argparse.ArgumentParser(description='Prepare data for firm-by-firm SCM')
    parser.add_argument('--input', type=str, default='Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv',
                       help='Input CSV file path')
    parser.add_argument('--output', type=str, default='Data/processed/data_prepared_for_scm.csv',
                       help='Output CSV file path')

    args = parser.parse_args()

    # Use default input if file doesn't exist
    if not Path(args.input).exists():
        default_input = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
        if Path(default_input).exists():
            args.input = default_input
        else:
            print(f"Error: No input file found. Checked: {args.input}, {default_input}")
            return 1

    print("\n" + "="*70)
    print("DATA PREPARATION FOR FIRM-BY-FIRM SCM")
    print("="*70)

    # Load data
    print(f"\n[1/5] Loading data from: {args.input}")
    try:
        df = pd.read_csv(args.input)
        print(f"  [OK] Loaded {len(df):,} rows x {len(df.columns)} columns")
    except FileNotFoundError:
        print(f"  [ERROR] File not found: {args.input}")
        return 1
    except Exception as e:
        print(f"  [ERROR] Error loading file: {e}")
        return 1

    # Validate
    print(f"\n[2/5] Validating required variables...")
    issues = validate_data(df)
    if issues:
        print("  Issues found:")
        for issue in issues:
            print(f"    WARNING: {issue}")
    else:
        print("  [OK] All required variables present")

    # Create missing variables
    print(f"\n[3/5] Creating derived variables...")
    df_updated, created = auto_create_variables(df)
    if created:
        print(f"  [OK] Created {len(created)} variables:")
        for var in created:
            print(f"    - {var}")
    else:
        print("  [OK] All required variables already present")

    # Check composition
    check_sample_composition(df_updated)

    # Save prepared data
    print(f"\n[4/5] Saving prepared data...")
    output_path = Path(args.output)
    df_updated.to_csv(output_path, index=False)
    print(f"  [OK] Saved to: {output_path}")
    print(f"    ({len(df_updated):,} rows x {len(df_updated.columns)} columns)")

    # Summary
    print(f"\n[5/5] Summary & Next Steps")
    print("="*70)
    print(f"[OK] Data is ready for firm_by_firm_scm.R")
    print(f"\nNext steps:")
    print(f"1. Update DATA_FILE path in firm_by_firm_scm.R to point to {output_path}")
    print(f"2. Run: python scripts/firm_by_firm_scm_analysis.py")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
