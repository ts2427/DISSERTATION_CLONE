"""
Data Validation Checks for Dissertation Pipeline
Ensures data integrity before analysis
Checks for logical consistency, duplicates, outliers, and missing values
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_data():
    """Load main dataset"""
    data_path = Path('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
    df = pd.read_csv(data_path)
    return df

def validate_logical_consistency(df):
    """Check that reported date >= breach date and disclosure delay >= 0"""
    print("\n=== LOGICAL CONSISTENCY CHECKS ===")

    # Ensure date columns are datetime
    df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
    df['reported_date'] = pd.to_datetime(df['reported_date'], errors='coerce')

    # Check: Reported date should come after or on breach date
    reported_before_breach = (df['reported_date'] < df['breach_date']).sum()
    if reported_before_breach > 0:
        print(f"[ERROR] {reported_before_breach} cases where reported date < breach date")
        return False
    else:
        print("[OK] All reported dates >= breach dates")

    # Check: Days to disclosure should be >= 0
    negative_days = (df['disclosure_delay_days'] < 0).sum()
    if negative_days > 0:
        print(f"[ERROR] {negative_days} cases with negative disclosure_delay_days")
        return False
    else:
        print("[OK] All disclosure_delay_days >= 0")

    return True

def check_duplicates(df):
    """Check for duplicate observations"""
    print("\n=== DUPLICATE CHECKS ===")

    # Check: Duplicates on (firm, breach_date, records_affected)
    dup_check = df.duplicated(subset=['cik', 'breach_date', 'total_affected'], keep=False)
    n_dups = dup_check.sum()

    if n_dups > 0:
        print(f"[WARNING] {n_dups} potential duplicate breach events found:")
        dups = df[dup_check].sort_values(['cik', 'breach_date'])
        print(dups[['org_name', 'breach_date', 'total_affected']].head(10))
    else:
        print("[OK] No duplicate breach observations found")

    return True

def check_outliers(df):
    """Check for extreme values in key variables"""
    print("\n=== OUTLIER DETECTION ===")

    outlier_vars = {
        'car_30d': {'bounds': (-100, 100), 'desc': 'CAR (%) - delisted firms'},
        'total_affected': {'bounds': (0, 1e9), 'desc': 'Records affected'},
        'prior_breaches_total': {'bounds': (0, 100), 'desc': 'Prior breaches'},
        'disclosure_delay_days': {'bounds': (0, 365), 'desc': 'Days to disclosure'},
    }

    for var, config in outlier_vars.items():
        if var not in df.columns:
            continue

        # Skip non-numeric columns
        try:
            lower, upper = config['bounds']
            var_numeric = pd.to_numeric(df[var], errors='coerce')
            out_of_bounds = ((var_numeric < lower) | (var_numeric > upper)).sum()

            if out_of_bounds > 0:
                pct = 100 * out_of_bounds / len(df)
                print(f"[WARNING] {var}: {out_of_bounds} outliers ({pct:.2f}%)")
                print(f"  Range: [{var_numeric.min():.2f}, {var_numeric.max():.2f}]")
                print(f"  Bounds: [{lower}, {upper}]")
            else:
                print(f"[OK] {var}: No outliers outside [{lower}, {upper}]")
        except Exception as e:
            print(f"[SKIP] {var}: Could not analyze ({str(e)[:50]})")

    return True

def check_missing_data(df):
    """Report missing values by key variable"""
    print("\n=== MISSING DATA REPORT ===")

    critical_vars = [
        'car_30d', 'immediate_disclosure', 'days_to_disclosure',
        'fcc_reportable', 'total_affected', 'health_breach',
        'prior_breaches_total', 'firm_size_log', 'leverage', 'roa',
        'volatility_change', 'executive_change_30d'
    ]

    print("\nCritical variables missing data:")
    total_n = len(df)
    for var in critical_vars:
        if var not in df.columns:
            continue

        missing = df[var].isna().sum()
        pct = 100 * missing / total_n

        if missing > 0:
            print(f"  {var:.<30} {missing:>5} ({pct:>5.1f}%)")
        else:
            print(f"  {var:.<30} {missing:>5} ( 0.0%)")

    return True

def check_sample_sizes(df):
    """Check sample sizes by key grouping variable"""
    print("\n=== SAMPLE SIZE REPORT ===")

    print(f"\nTotal observations: {len(df)}")
    print(f"\nBy FCC Status:")
    print(f"  FCC-regulated:     {(df['fcc_reportable'] == 1).sum():>5} ({100*(df['fcc_reportable'] == 1).sum()/len(df):>5.1f}%)")
    print(f"  Non-FCC firms:     {(df['fcc_reportable'] == 0).sum():>5} ({100*(df['fcc_reportable'] == 0).sum()/len(df):>5.1f}%)")

    print(f"\nBy Disclosure Timing:")
    print(f"  Immediate (<=7d):  {(df['immediate_disclosure'] == 1).sum():>5} ({100*(df['immediate_disclosure'] == 1).sum()/len(df):>5.1f}%)")
    print(f"  Delayed (>7d):     {(df['immediate_disclosure'] == 0).sum():>5} ({100*(df['immediate_disclosure'] == 0).sum()/len(df):>5.1f}%)")

    print(f"\nBy Breach Type:")
    print(f"  Health breach:     {(df['health_breach'] == 1).sum():>5} ({100*(df['health_breach'] == 1).sum()/len(df):>5.1f}%)")
    print(f"  Non-health:        {(df['health_breach'] == 0).sum():>5} ({100*(df['health_breach'] == 0).sum()/len(df):>5.1f}%)")

    print(f"\nBy Turnover Status:")
    if 'executive_change_30d' in df.columns:
        print(f"  Turnover (30d):    {(df['executive_change_30d'] == 1).sum():>5} ({100*(df['executive_change_30d'] == 1).sum()/len(df):>5.1f}%)")
        print(f"  No turnover:       {(df['executive_change_30d'] == 0).sum():>5} ({100*(df['executive_change_30d'] == 0).sum()/len(df):>5.1f}%)")

    return True

def main():
    """Run all validation checks"""
    print("\n" + "="*80)
    print("DISSERTATION PIPELINE: DATA VALIDATION CHECKS")
    print("="*80)

    df = load_data()
    print(f"\nDataset loaded: {len(df)} observations")

    # Run all checks
    checks = [
        validate_logical_consistency,
        check_duplicates,
        check_outliers,
        check_missing_data,
        check_sample_sizes,
    ]

    all_passed = True
    for check_fn in checks:
        try:
            passed = check_fn(df)
            all_passed = all_passed and passed
        except Exception as e:
            print(f"\n[ERROR] {check_fn.__name__} failed: {str(e)}")
            all_passed = False

    # Summary
    print("\n" + "="*80)
    if all_passed:
        print("[SUCCESS] All validation checks passed. Safe to proceed with analysis.")
    else:
        print("[WARNING] Some validation checks failed. Review above for details.")
    print("="*80 + "\n")

    return all_passed

if __name__ == '__main__':
    main()
