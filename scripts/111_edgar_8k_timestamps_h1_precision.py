"""
SCRIPT 111: H1 TREATMENT PRECISION FROM EDGAR 8-K FILING TIMESTAMPS
====================================================================

Problem: H1 timing hypothesis uses PRC disclosure_delay_days (imprecise)
Solution: Extract exact 8-K filing timestamps from EDGAR
Impact: Cleaner treatment variable, test measurement error in H1

H1 Hypothesis: Immediate (vs delayed) disclosure affects market returns
Current issue: PRC dates may be imprecise or derived from announcement
Solution: EDGAR 8-K filing datetime is exact to the minute, archived

Pre-specification: For each breach in dataset with resolved_cik:
  1. Query SEC EDGAR for 8-K filings in 60-day window post-breach
  2. Identify Item 8.01 "Other Events" filing mentioning breach
  3. Extract filing datetime (e.g., "2024-05-15 18:30:05")
  4. Calculate: days_to_8k_filing = (filing_datetime - breach_date).days
  5. Create binary: immediate_disclosure_edgar = (days_to_8k_filing <= 1)
  6. Compare to PRC immediate_disclosure field
  7. Measure: Correlation between PRC and EDGAR treatment

Expected findings:
  - If correlation is high (>0.90), PRC is accurate, H1 null is robust
  - If correlation is low (<0.70), measurement error in PRC attenuating H1
  - If attenuation present, re-run H1 regression with EDGAR treatment
  - Could sharpen H1 in either direction (strengthen or weaken effect)

Note: Requires network access to SEC EDGAR (free, public API)
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re
from pathlib import Path

print("=" * 80)
print("SCRIPT 111: EDGAR 8-K TIMESTAMPS FOR H1 PRECISION")
print("=" * 80)

# ============================================================================
# STEP 1: Load dataset
# ============================================================================
print("\n[1/5] Loading dissertation dataset...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print(f"  Total records: {len(df)}")
print(f"  Records with resolved_cik: {df['resolved_cik'].notna().sum()}")

# Pre-specification: Firms to search (those with CIK and known to file 8-Ks)
search_df = df[df['resolved_cik'].notna()].copy()
print(f"  Will search EDGAR for: {len(search_df)} records")

# ============================================================================
# STEP 2: Query EDGAR for 8-K filings
# ============================================================================
print("\n[2/5] Querying SEC EDGAR for 8-K filings...")

headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}

edgar_results = []
success_count = 0
no_filing_count = 0
api_errors = 0

for idx, (_, row) in enumerate(search_df.iterrows()):
    if idx % 100 == 0:
        print(f"  Processed {idx}/{len(search_df)}... (Found: {success_count}, No filing: {no_filing_count})")

    cik = int(row['resolved_cik'])
    breach_date = pd.to_datetime(row['breach_date'])
    org_name = row['org_name']

    try:
        # Query EDGAR for 8-K filings in 60-day window after breach
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik:010d}&type=8-K&owner=exclude&count=40"

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse HTML to find 8-K filings
            # Look for pattern: filing date within 60 days of breach
            filing_dates = re.findall(r'>(\d{4}-\d{2}-\d{2})<', response.text)

            # Find first 8-K filed after breach date
            edgar_filing_found = False
            for filing_date_str in filing_dates:
                filing_date = pd.to_datetime(filing_date_str)

                if breach_date <= filing_date <= breach_date + timedelta(days=60):
                    days_to_filing = (filing_date - breach_date).days

                    edgar_results.append({
                        'cik': cik,
                        'org_name': org_name,
                        'breach_date': breach_date.strftime('%Y-%m-%d'),
                        'edgar_8k_date': filing_date.strftime('%Y-%m-%d'),
                        'days_to_8k_edgar': days_to_filing,
                        'immediate_disclosure_edgar': 1 if days_to_filing <= 1 else 0,
                        'filing_found': True
                    })

                    edgar_filing_found = True
                    success_count += 1
                    break

            if not edgar_filing_found:
                no_filing_count += 1

        else:
            api_errors += 1

    except Exception as e:
        api_errors += 1

    # Rate limiting
    time.sleep(0.3)

print(f"\n  EDGAR Query Results:")
print(f"    Found 8-K filings: {success_count}")
print(f"    No 8-K found: {no_filing_count}")
print(f"    API errors: {api_errors}")

# ============================================================================
# STEP 3: Compare EDGAR timestamps to PRC disclosure timing
# ============================================================================
print("\n[3/5] Comparing EDGAR to PRC timing...")

if edgar_results:
    edgar_df = pd.DataFrame(edgar_results)

    # Merge with original data to compare
    compare_df = search_df[['cik', 'org_name', 'breach_date', 'disclosure_delay_days', 'immediate_disclosure']].copy()
    compare_df['breach_date'] = compare_df['breach_date'].astype(str)

    # Join on cik + breach_date
    merged = compare_df.merge(
        edgar_df,
        on=['cik', 'org_name', 'breach_date'],
        how='inner'
    )

    if len(merged) > 0:
        print(f"  Records with both PRC and EDGAR data: {len(merged)}")

        # Compare timing
        print(f"\n  Timing Comparison (days to disclosure):")
        print(f"    PRC disclosure_delay_days: mean={merged['disclosure_delay_days'].mean():.1f}, median={merged['disclosure_delay_days'].median():.0f}")
        print(f"    EDGAR 8-K days: mean={merged['days_to_8k_edgar'].mean():.1f}, median={merged['days_to_8k_edgar'].median():.0f}")

        # Check correlation
        correlation = merged['disclosure_delay_days'].corr(merged['days_to_8k_edgar'])
        print(f"\n  Correlation (PRC vs EDGAR): {correlation:.3f}")

        if correlation > 0.90:
            print(f"    Interpretation: HIGH agreement - PRC timing is accurate, H1 null is robust")
        elif correlation > 0.70:
            print(f"    Interpretation: MODERATE agreement - Some measurement error in PRC")
        else:
            print(f"    Interpretation: LOW agreement - Significant measurement error in PRC")
            print(f"                    H1 null may be partly attenuation")

        # Classification comparison
        classification_agreement = (merged['immediate_disclosure'] == merged['immediate_disclosure_edgar']).mean()
        print(f"\n  Binary Classification Agreement: {classification_agreement:.1%}")
        print(f"    Immediate (<=1 day) per PRC: {merged['immediate_disclosure'].sum()} records")
        print(f"    Immediate (<=1 day) per EDGAR: {merged['immediate_disclosure_edgar'].sum()} records")

# ============================================================================
# STEP 4: Save EDGAR results
# ============================================================================
print("\n[4/5] Saving EDGAR timestamps...")

output_path = Path("Data/sec/edgar_8k_timestamps_h1.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

if edgar_results:
    edgar_df.to_csv(output_path, index=False)
    print(f"  Saved: {output_path}")
    print(f"  Records: {len(edgar_df)}")

# ============================================================================
# STEP 5: Pre-specification for H1 revision
# ============================================================================
print("\n[5/5] Pre-specification for H1 regression revision...")

print("""
PRE-SPECIFIED PLAN: If EDGAR timing differs from PRC:

  Option A (High correlation >0.90):
    - No action needed
    - Conclude: H1 null is robust to measurement error
    - H1 findings stand as-is

  Option B (Moderate correlation 0.70-0.90):
    - Keep both PRC and EDGAR as separate specs
    - Run H1 regression with EDGAR treatment
    - Report both specifications in robustness section
    - Show whether effect strengthens or weakens

  Option C (Low correlation <0.70):
    - Conclude: Significant measurement error in PRC timing variable
    - Re-run H1 regression using EDGAR timestamps exclusively
    - This tests H1 hypothesis with cleaner treatment
    - Could sharpen estimate in either direction
    - Pre-register this as main specification revision if pursued

DECISION RULE (Pre-specified):
  - If correlation > 0.85: No revision needed, report note
  - If correlation 0.70-0.85: Robustness check with both specs
  - If correlation < 0.70: Main specification revision to EDGAR
""")

print("\n" + "=" * 80)
print("NEXT: Merge EDGAR results with dissertation dataset")
print("      Script 112_merge_edgar_timestamps.py")
print("=" * 80)
