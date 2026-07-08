"""
CENCORA BREACH STRUCTURE AUDIT
==============================

Investigate the 765 "duplicate" Cencora records.

Hypothesis: These are state-level breach notifications for one or two underlying
mega-breach events (e.g., 2024 healthcare data breach requiring notification to
all 50 states + DC). Each state filing creates a separate PRC record with:
  - Same underlying breach date
  - Similar/identical org name (Cencora, Inc.; Cencora, LLC; etc.)
  - Same market reaction CAR (same event)
  - Different affected-individual counts (state-specific record counts)

If true:
  - Affected counts should differ across records
  - Breach dates should cluster into 1-2 unique events
  - These are genuinely separate administrative records needing aggregation,
    not sloppy data entry needing deletion

Pull all Cencora records and audit the structure.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

# Filter to Cencora
cencora = df[df['org_name'].str.contains('Cencora', case=False, na=False)].copy()
cencora = cencora.sort_values('breach_date')

print("\n" + "="*100)
print("CENCORA BREACH STRUCTURE AUDIT")
print("="*100)

print(f"\nTotal Cencora records: {len(cencora)}")
print(f"Unique org name variants: {cencora['org_name'].nunique()}")
print(f"Unique breach dates: {cencora['breach_date'].nunique()}")

# ============================================================================
# SECTION 1: ORG NAME VARIANTS
# ============================================================================

print("\n" + "-"*100)
print("SECTION 1: ORG NAME VARIANTS")
print("-"*100)

org_variants = cencora['org_name'].value_counts()
print(f"\nOrg name variants and record counts:")
for org, count in org_variants.items():
    print(f"  {org:45s}: {count:3d} records")

# ============================================================================
# SECTION 2: BREACH DATE DISTRIBUTION
# ============================================================================

print("\n" + "-"*100)
print("SECTION 2: BREACH DATE DISTRIBUTION")
print("-"*100)

date_counts = cencora['breach_date'].value_counts().sort_index()
print(f"\nRecords by breach date:")
for date, count in date_counts.items():
    if pd.notna(date):
        date_str = pd.to_datetime(date).strftime('%Y-%m-%d') if isinstance(date, str) else date.strftime('%Y-%m-%d')
    else:
        date_str = 'N/A'
    print(f"  {date_str}: {count:3d} records")

print(f"\nUnique breach dates: {cencora['breach_date'].nunique()}")
min_date = pd.to_datetime(cencora['breach_date'].min()).strftime('%Y-%m-%d')
max_date = pd.to_datetime(cencora['breach_date'].max()).strftime('%Y-%m-%d')
print(f"Date range: {min_date} to {max_date}")

# ============================================================================
# SECTION 3: AFFECTED INDIVIDUALS ANALYSIS
# ============================================================================

print("\n" + "-"*100)
print("SECTION 3: AFFECTED INDIVIDUALS ANALYSIS")
print("-"*100)

print(f"\nAffected individuals statistics (across all {len(cencora)} Cencora records):")
print(f"  Min: {int(cencora['total_affected'].min()):12,d}")
print(f"  Max: {int(cencora['total_affected'].max()):12,d}")
print(f"  Mean: {cencora['total_affected'].mean():12,.0f}")
print(f"  Median: {cencora['total_affected'].median():12,.0f}")
print(f"  SD: {cencora['total_affected'].std():12,.0f}")

print(f"\nUnique affected counts: {cencora['total_affected'].nunique()}")

# Check if counts are identical or different
identical_count = (cencora['total_affected'] == cencora['total_affected'].iloc[0]).sum()
print(f"Records with affected count = {int(cencora['total_affected'].iloc[0]):,d}: {identical_count}")

if identical_count == len(cencora):
    print("  → All records have IDENTICAL affected counts (likely noise/duplicate)")
else:
    print("  → Records have DIFFERENT affected counts (likely state-level notifications)")

# ============================================================================
# SECTION 4: BREACH-BY-BREACH DETAIL
# ============================================================================

print("\n" + "-"*100)
print("SECTION 4: DETAIL BY BREACH DATE")
print("-"*100)

for breach_date in sorted(cencora['breach_date'].unique()):
    breach_records = cencora[cencora['breach_date'] == breach_date]
    date_str = pd.to_datetime(breach_date).strftime('%Y-%m-%d') if pd.notna(breach_date) else 'N/A'
    print(f"\nBreach date: {date_str}")
    print(f"  Total records: {len(breach_records)}")
    print(f"  Org variants: {breach_records['org_name'].nunique()}")
    print(f"  CAR values: {breach_records['car_30d'].nunique()} unique")
    print(f"  Affected counts range: {int(breach_records['total_affected'].min()):,d} to {int(breach_records['total_affected'].max()):,d}")

    # Show all org/affected combinations for this breach
    print(f"\n  Records in detail:")
    for idx, row in breach_records.iterrows():
        print(f"    [{idx:4d}] {row['org_name']:45s} | Affected: {int(row['total_affected']):12,d} | CAR: {row['car_30d']:7.2f}%")

# ============================================================================
# SECTION 5: INTERPRETATION
# ============================================================================

print("\n" + "="*100)
print("SECTION 5: INTERPRETATION & RECOMMENDATION")
print("="*100)

unique_dates = cencora['breach_date'].nunique()
unique_affected = cencora['total_affected'].nunique()

print(f"""
FINDINGS:

Cencora records: {len(cencora)}
Unique breach dates: {unique_dates}
Unique affected counts: {unique_affected}
Unique org names: {cencora['org_name'].nunique()}

INTERPRETATION:

""")

if unique_dates <= 3 and unique_affected > len(cencora) * 0.5:
    print("""
CONSISTENT WITH STATE-NOTIFICATION HYPOTHESIS:
  - Few underlying breach events (1-3)
  - Many unique affected counts (state-specific record counts)
  - Multiple org name variants

Explanation: Likely one or more large breaches requiring notification to
multiple state attorneys general. Each state filing creates a separate
PRC record with the same breach date, same market reaction (CAR), but
different affected-individual counts (state-specific).

RECOMMENDATION:
  Rather than delete these as "duplicates," aggregate them:
  - Keep one record per unique breach date
  - Sum the affected individuals across state-level notifications
  - This preserves the real signal (a major breach happened) while
    avoiding the analytical problem of counting the same event 50+ times
""")

elif unique_affected <= 1:
    print("""
CONSISTENT WITH DATA NOISE HYPOTHESIS:
  - Identical affected counts across all records
  - Suggests these are genuinely redundant copies, not state-level variants

RECOMMENDATION:
  These are legitimate duplicates. Safe to drop all but one per org/date.
""")

else:
    print(f"""
MIXED SIGNAL:
  - {unique_dates} unique dates
  - {unique_affected} unique affected counts

RECOMMENDATION:
  Investigate manually. The structure suggests partial state-notification
  pattern, but with unusual date/count variation. May be a mix of:
  - State-level notifications (legitimate)
  - Genuine duplicates/data errors (should drop)
  - Updates/corrections over time (should aggregate)
""")

print("="*100 + "\n")
