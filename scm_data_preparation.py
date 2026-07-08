"""
DATA PREPARATION & VALIDATION FOR FIRM-BY-FIRM SCM
===================================================

This script helps you:
1. Load and inspect your dissertation data
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

# Variables that will be auto-created if missing
AUTO_CREATE_VARS = {
    'log_assets': ('total_assets', 'log'),
    'leverage': ('total_debt', 'total_assets', 'divide'),
    'roa': ('net_income', 'total_assets', 'multiply_100'),
    'log_records_affected': ('records_affected', 'log'),
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
                issues.append(f"  ⚠ {var}: {missing_pct:.1f}% missing (acceptable if < 20%)")

    # Check numeric variables
    numeric_vars = ['car_30d', 'volatility_change', 'year', 'sic_code']
    for var in numeric_vars:
        if var in df.columns:
            try:
                pd.to_numeric(df[var])
            except:
                issues.append(f"  ⚠ {var} contains non-numeric values")

    # Check year range
    if 'year' in df.columns:
        year_min = df['year'].min()
        year_max = df['year'].max()
        if year_min < 2000 or year_max > 2025:
            issues.append(f"  ⚠ Year range ({year_min}-{year_max}) unusual. Expected 2000-2024.")

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
            print(f"  ⚠ WARNING: Only {unique_fcc} unique FCC firms (recommend ≥20)")

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
        print(f"  CAR 30-day:     μ={df['car_30d'].mean():>7.2f}%, σ={df['car_30d'].std():>6.2f}%, n={df['car_30d'].notna().sum()}")

    if 'volatility_change' in df.columns:
        print(f"  Volatility Δ:   μ={df['volatility_change'].mean():>7.2f}pp, σ={df['volatility_change'].std():>6.2f}pp, n={df['volatility_change'].notna().sum()}")

    if 'executive_change_30d' in df.columns:
        rate = df['executive_change_30d'].mean() * 100
        print(f"  Exec change 30d: {rate:.1f}% (n={df['executive_change_30d'].notna().sum()})")


def check_data_quality(df):
    """Detailed data quality checks"""
    print("\n" + "="*70)
    print("DATA QUALITY CHECKS")
    print("="*70)

    # Missing values summary
    print("\nMissing Values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    missing_df = pd.DataFrame({'Count': missing, 'Percent': missing_pct})
    missing_df = missing_df[missing_df['Count'] > 0].sort_values('Percent', ascending=False)

    if len(missing_df) == 0:
        print("  ✓ No missing values!")
    else:
        print(missing_df.to_string())

    # Outliers
    print("\nOutlier Detection (CAR 30-day):")
    if 'car_30d' in df.columns:
        q1 = df['car_30d'].quantile(0.25)
        q3 = df['car_30d'].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 3 * iqr
        upper = q3 + 3 * iqr
        outliers = ((df['car_30d'] < lower) | (df['car_30d'] > upper)).sum()
        print(f"  Extreme outliers (>3 IQR): {outliers} ({outliers/len(df)*100:.2f}%)")
        if outliers > 0:
            print(f"    Range: [{lower:.2f}%, {upper:.2f}%]")

    # Duplicates
    print("\nDuplicate Checks:")
    if 'firm_id' in df.columns and 'year' in df.columns:
        dups = df.groupby(['firm_id', 'year']).size()
        dup_count = (dups > 1).sum()
        if dup_count == 0:
            print(f"  ✓ No duplicate firm-year combinations")
        else:
            print(f"  ⚠ {dup_count} duplicate firm-year combinations")


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def main():
    """Main data preparation workflow"""
    parser = argparse.ArgumentParser(description='Prepare data for firm-by-firm SCM')
    parser.add_argument('--input', type=str, help='Input CSV file path')
    parser.add_argument('--output', type=str, default='data_prepared_for_scm.csv',
                       help='Output CSV file path')

    args = parser.parse_args()

    if not args.input:
        print("Usage: python scm_data_preparation.py --input your_data.csv [--output output.csv]")
        print("\nExample:")
        print("  python scm_data_preparation.py --input Data/raw/breaches.csv --output data_scm_ready.csv")
        return 1

    print("\n" + "="*70)
    print("DATA PREPARATION FOR FIRM-BY-FIRM SCM")
    print("="*70)

    # Load data
    print(f"\n[1/5] Loading data from: {args.input}")
    try:
        df = pd.read_csv(args.input)
        print(f"  ✓ Loaded {len(df):,} rows × {len(df.columns)} columns")
    except FileNotFoundError:
        print(f"  ✗ File not found: {args.input}")
        return 1
    except Exception as e:
        print(f"  ✗ Error loading file: {e}")
        return 1

    # Validate
    print(f"\n[2/5] Validating required variables...")
    issues = validate_data(df)
    if issues:
        print("  Issues found:")
        for issue in issues:
            print(f"    ⚠ {issue}")
    else:
        print("  ✓ All required variables present")

    # Create missing variables
    print(f"\n[3/5] Creating derived variables...")
    df_updated, created = auto_create_variables(df)
    if created:
        print(f"  ✓ Created {len(created)} variables:")
        for var in created:
            print(f"    - {var}")
    else:
        print("  ✓ All required variables already present")

    # Check composition
    check_sample_composition(df_updated)

    # Quality checks
    check_data_quality(df_updated)

    # Save prepared data
    print(f"\n[4/5] Saving prepared data...")
    output_path = Path(args.output)
    df_updated.to_csv(output_path, index=False)
    print(f"  ✓ Saved to: {output_path}")
    print(f"    ({len(df_updated):,} rows × {len(df_updated.columns)} columns)")

    # Summary
    print(f"\n[5/5] Summary & Next Steps")
    print("="*70)
    print(f"✓ Data is ready for firm_by_firm_scm.R")
    print(f"\nNext steps:")
    print(f"1. Update DATA_FILE path in firm_by_firm_scm.R to point to {output_path}")
    print(f"2. Run: python firm_by_firm_scm_analysis.py")
    print(f"\nNOTE: If you get errors in R script:")
    print(f"  - Check that firm_id values are unique per firm")
    print(f"  - Verify SIC codes match your FCC definition")
    print(f"  - Ensure year range includes pre-2007 data")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
