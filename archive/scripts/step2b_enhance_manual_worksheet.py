"""
STEP 2b: Enhance manual review worksheet with record counts and SIC codes
Helps prioritize which org_names matter most
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("STEP 2b: ENHANCE MANUAL REVIEW WORKSHEET")
print("=" * 100)

# Load data
prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
prc_df = pd.read_csv(prc_path)

worksheet_path = Path("Data/edgar/step2_manual_review_worksheet.csv")
worksheet = pd.read_csv(worksheet_path)

print(f"\nLoading PRC dataset: {len(prc_df):,} records")
print(f"Loading manual review worksheet: {len(worksheet):,} org_names")

# Add record count and SIC codes for each org_name
enhanced = []

for _, row in worksheet.iterrows():
    org_name = row['org_name']

    # Get all records for this org_name
    org_records = prc_df[prc_df['org_name'] == org_name]
    record_count = len(org_records)

    # Get unique SIC codes for this org_name
    sic_codes = org_records['sic'].dropna().unique()
    sic_string = ', '.join(sorted([str(int(x)) if pd.notna(x) else '' for x in sic_codes if pd.notna(x)]))

    # Get unique CIKs currently assigned (if any)
    current_ciks = org_records['cik'].dropna().unique()
    current_cik_string = ', '.join([str(int(x)) for x in current_ciks if pd.notna(x)])

    # Get breach count and date range
    if record_count > 0:
        breach_dates = pd.to_datetime(org_records['breach_date'])
        earliest_breach = breach_dates.min().strftime('%Y-%m-%d')
        latest_breach = breach_dates.max().strftime('%Y-%m-%d')
    else:
        earliest_breach = ''
        latest_breach = ''

    enhanced.append({
        'org_name': row['org_name'],
        'record_count': record_count,
        'prc_breach_count': record_count,
        'earliest_breach': earliest_breach,
        'latest_breach': latest_breach,
        'sic_codes': sic_string,
        'current_assigned_ciks': current_cik_string,
        'org_name_normalized': row['org_name_normalized'],
        'best_edgar_match': row['best_edgar_match'],
        'best_score': row['best_score'],
        'assigned_cik': '',  # For manual entry
        'assigned_ticker': '',  # For manual entry
        'notes': '',  # For manual notes
    })

df_enhanced = pd.DataFrame(enhanced)

# Sort by record_count descending (so most important org_names are first)
df_enhanced_sorted = df_enhanced.sort_values('record_count', ascending=False).reset_index(drop=True)

# Save enhanced worksheet
output_path = Path("Data/edgar/step2_manual_review_worksheet_enhanced.csv")
df_enhanced_sorted.to_csv(output_path, index=False)

print(f"\nEnhanced worksheet saved: {output_path}")
print(f"\nTop 20 org_names by record count:")
print(f"{'Rank':<5} {'Record Count':<15} {'Org Name':<50}")
print("-" * 70)

for idx in range(min(20, len(df_enhanced_sorted))):
    row = df_enhanced_sorted.iloc[idx]
    print(f"{idx+1:<5} {row['record_count']:<15} {row['org_name']:<50}")

print(f"\n... and {max(0, len(df_enhanced_sorted) - 20)} more")

# Summary statistics
print(f"\n" + "=" * 100)
print("WORKSHEET STATISTICS")
print("=" * 100)
print(f"\nTotal org_names requiring manual review: {len(df_enhanced_sorted)}")
print(f"Total PRC records affected: {df_enhanced_sorted['record_count'].sum():,}")
print(f"Coverage: {(df_enhanced_sorted['record_count'].sum() / len(prc_df) * 100):.1f}% of all breaches")

print(f"\nRecord count distribution:")
quartiles = df_enhanced_sorted['record_count'].quantile([0.25, 0.5, 0.75, 1.0])
print(f"  Q1 (25%): {quartiles[0.25]:.0f} records")
print(f"  Q2 (50%): {quartiles[0.5]:.0f} records")
print(f"  Q3 (75%): {quartiles[0.75]:.0f} records")
print(f"  Max:      {quartiles[1.0]:.0f} records")

# Show organizations with >10 breaches
high_volume = df_enhanced_sorted[df_enhanced_sorted['record_count'] > 10]
print(f"\nHigh-volume org_names (>10 breaches): {len(high_volume)}")
print(f"  Representing {high_volume['record_count'].sum():,} records ({high_volume['record_count'].sum() / len(prc_df) * 100:.1f}% of total)")

print(f"\n" + "=" * 100)
print("NEXT STEP: Manual CIK assignment")
print("=" * 100)
print(f"\nOpen the enhanced worksheet and fill in:")
print(f"  1. assigned_cik: The correct CIK from SEC EDGAR")
print(f"  2. assigned_ticker: The ticker symbol (if applicable)")
print(f"  3. notes: Any notes on the assignment (e.g., 'subsidiary of X', 'acquired by Y')")
print(f"\nAll 335 org_names need assignments before proceeding to Step 3.")
