"""
SCRIPT 121B: FORM 499 COVERAGE VALIDATION
===========================================

Apply classification rule to matched records.

Input:  outputs/form499_matched_records.csv (from Script 121A)
Output: outputs/form499_classification_final.csv
        outputs/form499_classification_summary.txt

Process:
  1. Load matched records
  2. For each record: apply coverage validation logic
     - Check date ranges (start_date <= breach_date)
     - Classify end_reason_desc (terminating/non-terminating/indeterminate)
     - Handle 1997-01-01 sentinel
     - Apply replacement chain logic if needed
  3. Assign fcc_form499 = 1 or 0
  4. Document decision rule and rationale
  5. Generate summary including end_reason_desc distribution
"""

import pandas as pd
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("SCRIPT 121B: FORM 499 COVERAGE VALIDATION")
print("=" * 80)

# ============================================================================
# LOAD MATCHED RECORDS
# ============================================================================
print("\n1. LOADING MATCHED RECORDS...")

input_file = output_dir / 'form499_matched_records.csv'
try:
    df = pd.read_csv(input_file)
    print(f"   Loaded: {len(df)} rows")
except FileNotFoundError:
    print(f"   ERROR: {input_file} not found")
    print("   Run Script 121A first")
    sys.exit(1)

# ============================================================================
# END_REASON_DESC CATEGORIZATION
# ============================================================================

TERMINATING = [
    "This company has gone out of business in it's entirety",
    "This company still exists, however it is no longer providing",
    "This company has filed for Chapter 7 bankruptcy"
]

NON_TERMINATING = [
    "All assets of this company have been sold to another party",
    "This legal entity account has been closed because their Form 499 filing is now submitted on a consolidated basis",
    "The company has been absorbed by another filing entity"
]

def categorize_reason(reason):
    """Classify end_reason_desc into category."""
    if reason is None or pd.isna(reason):
        return 'none'

    reason_str = str(reason).strip()

    # Check terminating
    for term in TERMINATING:
        if term.lower() in reason_str.lower():
            return 'terminating'

    # Check non-terminating
    for term in NON_TERMINATING:
        if term.lower() in reason_str.lower():
            return 'non_terminating'

    # Default: indeterminate
    return 'indeterminate'

# ============================================================================
# COVERAGE VALIDATION LOGIC
# ============================================================================

def validate_coverage(row):
    """
    Apply coverage validation logic to a single record.

    Returns: {
      'fcc_form499': 0 or 1,
      'reason_classified': description of decision,
      'date_valid': whether date range is valid,
      'termination_status': which category end_reason_desc falls into
    }
    """

    # No match case
    if row['matched'] == 0:
        return {
            'fcc_form499': 0,
            'reason_classified': 'No Form 499 match found',
            'date_valid': False,
            'termination_status': None
        }

    # Extract dates
    try:
        breach_date = pd.to_datetime(row['breach_date']).date()
    except:
        return {
            'fcc_form499': 0,
            'reason_classified': 'Invalid breach_date',
            'date_valid': False,
            'termination_status': None
        }

    try:
        start_date = pd.to_datetime(row['start_date']).date() if pd.notna(row['start_date']) else None
    except:
        start_date = None

    try:
        end_date = pd.to_datetime(row['end_date']).date() if pd.notna(row['end_date']) else None
    except:
        end_date = None

    # Check start_date <= breach_date
    if start_date is None:
        return {
            'fcc_form499': 0,
            'reason_classified': 'No start_date in Form 499 record',
            'date_valid': False,
            'termination_status': None
        }

    if breach_date < start_date:
        return {
            'fcc_form499': 0,
            'reason_classified': f'Breach date {breach_date} before start_date {start_date}',
            'date_valid': False,
            'termination_status': None
        }

    # If no end_date (current filer)
    if end_date is None:
        return {
            'fcc_form499': 1,
            'reason_classified': 'Current Form 499 filer; no end_date',
            'date_valid': True,
            'termination_status': 'current'
        }

    # Handle 1997-01-01 sentinel
    if end_date == pd.to_datetime('1997-01-01').date():
        return {
            'fcc_form499': 1,
            'reason_classified': 'end_date is 1997-01-01 sentinel (treated as indeterminate, coverage continues)',
            'date_valid': True,
            'termination_status': 'indeterminate_sentinel'
        }

    # Categorize end_reason_desc
    termination_status = categorize_reason(row['end_reason_desc'])

    if termination_status == 'non_terminating':
        # Coverage continues through successor
        if breach_date <= end_date:
            return {
                'fcc_form499': 1,
                'reason_classified': f'Non-terminating reason (consolidated/absorbed); breach within coverage dates',
                'date_valid': True,
                'termination_status': 'non_terminating'
            }
        else:
            return {
                'fcc_form499': 0,
                'reason_classified': f'Non-terminating reason but breach {breach_date} after end_date {end_date}; would require replacement_id traversal',
                'date_valid': False,
                'termination_status': 'non_terminating'
            }

    elif termination_status == 'terminating':
        # Service ceased; only valid before cessation
        if breach_date < end_date:
            return {
                'fcc_form499': 1,
                'reason_classified': f'Terminating reason but breach {breach_date} before service cessation at {end_date}',
                'date_valid': True,
                'termination_status': 'terminating'
            }
        else:
            return {
                'fcc_form499': 0,
                'reason_classified': f'Terminating reason and breach {breach_date} >= end_date {end_date}; service ceased',
                'date_valid': False,
                'termination_status': 'terminating'
            }

    else:  # indeterminate
        # Conservative: assume coverage continues
        if breach_date <= end_date:
            return {
                'fcc_form499': 1,
                'reason_classified': f'Indeterminate reason but within date range; assuming coverage continues',
                'date_valid': True,
                'termination_status': 'indeterminate'
            }
        else:
            return {
                'fcc_form499': 0,
                'reason_classified': f'Indeterminate reason and breach after end_date; conservative classification as untreated',
                'date_valid': False,
                'termination_status': 'indeterminate'
            }

# ============================================================================
# APPLY VALIDATION LOGIC
# ============================================================================
print("\n2. APPLYING COVERAGE VALIDATION LOGIC...")

results = []
for idx, row in df.iterrows():
    validation = validate_coverage(row)
    result = {
        'org_name': row['org_name'],
        'breach_date': row['breach_date'],
        'fcc_form499': validation['fcc_form499'],
        'reason_classified': validation['reason_classified'],
        'date_valid': validation['date_valid'],
        'termination_status': validation['termination_status'],
        'frn': row['frn'],
        'start_date': row['start_date'],
        'end_date': row['end_date'],
        'end_reason_desc': row['end_reason_desc'],
    }
    results.append(result)

results_df = pd.DataFrame(results)

# Save detailed results
output_file = output_dir / 'form499_classification_final.csv'
results_df.to_csv(output_file, index=False)
print(f"   Saved: {output_file}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n3. CLASSIFICATION SUMMARY")
print("=" * 80)

treated = results_df[results_df['fcc_form499'] == 1]
untreated = results_df[results_df['fcc_form499'] == 0]

print(f"\nTotal breaches: {len(results_df)}")
print(f"  Treated (fcc_form499=1): {len(treated)} ({100*len(treated)/len(results_df):.1f}%)")
print(f"  Untreated (fcc_form499=0): {len(untreated)} ({100*len(untreated)/len(results_df):.1f}%)")

print(f"\nUnique treated organizations: {treated['org_name'].nunique()}")

print(f"\nTermination status distribution (all records):")
for status in ['current', 'non_terminating', 'terminating', 'indeterminate', 'indeterminate_sentinel', None]:
    count = (results_df['termination_status'] == status).sum()
    if count > 0:
        print(f"  {status or 'no_match'}: {count}")

print(f"\nTermination status distribution (TREATED only):")
for status in ['current', 'non_terminating', 'terminating', 'indeterminate', 'indeterminate_sentinel']:
    count = (treated['termination_status'] == status).sum()
    if count > 0:
        print(f"  {status}: {count}")

print(f"\nEnd reason distribution (TREATED only):")
treated_with_reason = treated[treated['end_reason_desc'].notna()]
if len(treated_with_reason) > 0:
    reason_counts = treated_with_reason['end_reason_desc'].value_counts()
    for reason, count in reason_counts.items():
        reason_display = (reason[:70] + '...') if len(reason) > 70 else reason
        print(f"  [{count:3d}]  {reason_display}")

# ============================================================================
# DECISION GATE: INDETERMINATE CHECK
# ============================================================================
print(f"\n" + "=" * 80)
print("DECISION GATE: INDETERMINATE CASES")
print("=" * 80)

indeterminate_treated = treated[treated['termination_status'].isin(['indeterminate', 'indeterminate_sentinel'])]
print(f"\nIndeterminate cases in treated group: {len(indeterminate_treated)}")

if len(indeterminate_treated) > 0:
    print("\nIndeterminate records (may warrant review):")
    for idx, row in indeterminate_treated.head(10).iterrows():
        print(f"  {row['org_name']} ({row['breach_date']}): {row['reason_classified']}")
    if len(indeterminate_treated) > 10:
        print(f"  ... and {len(indeterminate_treated) - 10} more")
else:
    print("\n✓ No indeterminate cases in treated group")
    print("  (indeterminate category is moot for H2 analysis)")

print("\n" + "=" * 80)
print("RESULT: form499_classification_final.csv ready for H2 re-estimation")
print("=" * 80)
