"""
VERIFICATION: CFO Placebo Test Dependent Variable Check

Confirm: What outcome variable was actually used in the CFO placebo analysis?
Did it use a CFO-specific turnover indicator, or did it duplicate the primary H6 outcome?
"""

import pandas as pd

print("=" * 90)
print("VERIFICATION: CFO PLACEBO DEPENDENT VARIABLE")
print("=" * 90)

# Load data
DATA_PATH = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(DATA_PATH)

print(f"\n[DATASET CHECK]")
print(f"Total rows: {len(df):,}")

# Check what turnover variables exist
turnover_cols = [col for col in df.columns if 'turnover' in col.lower() or 'executive_change' in col.lower() or 'cfo' in col.lower()]
print(f"\nTurnover-related columns in dataset:")
for col in sorted(turnover_cols):
    print(f"  - {col}")

# Count events by window
print(f"\n[OUTCOME VARIABLE COUNTS]")

if 'executive_change_30d' in df.columns:
    print(f"\nexecutive_change_30d:")
    print(f"  Total events: {df['executive_change_30d'].sum():,.0f}")
    print(f"  Event rate: {df['executive_change_30d'].mean()*100:.1f}%")

if 'executive_change_90d' in df.columns:
    print(f"\nexecutive_change_90d:")
    print(f"  Total events: {df['executive_change_90d'].sum():,.0f}")
    print(f"  Event rate: {df['executive_change_90d'].mean()*100:.1f}%")

if 'executive_change_180d' in df.columns:
    print(f"\nexecutive_change_180d:")
    print(f"  Total events: {df['executive_change_180d'].sum():,.0f}")
    print(f"  Event rate: {df['executive_change_180d'].mean()*100:.1f}%")

# Check for CFO-specific variables
cfo_cols = [col for col in df.columns if 'cfo' in col.lower()]
print(f"\nCFO-specific columns in dataset: {cfo_cols if cfo_cols else 'NONE FOUND'}")

print(f"\n" + "=" * 90)
print("CONCLUSION")
print("=" * 90)

if not cfo_cols:
    print(f"\n✗ CRITICAL: Dataset contains NO CFO-specific turnover variables.")
    print(f"  The CFO placebo test cannot be run with the current data.")
    print(f"  The script used executive_change_* (CEO/general executive) instead.")
    print(f"  This is NOT a valid placebo test — it measures the same outcome as primary H6.")
else:
    print(f"\n✓ CFO variables found: {cfo_cols}")
    print(f"  Placebo test may be valid if these were used as outcome.")
