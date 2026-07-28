"""
Extract Exhibit 21 (Subsidiaries) from SEC 10-K filings
Build subsidiary-to-parent mapping for unmatched validation records
"""

import pandas as pd
from pathlib import Path
import requests
from datetime import datetime
import re

print("=" * 100)
print("EXTRACT EX-21 SUBSIDIARY DATA FROM SEC EDGAR")
print("=" * 100)

# ============================================================================
# STEP 1: Load unmatched records from validation results
# ============================================================================
print("\n[1/4] Loading unmatched validation records...")

results_path = Path("outputs/exact_match_validation_results.csv")
df_results = pd.read_csv(results_path)

# Get unmatched records
unmatched = df_results[df_results['match_type'] == 'NO_MATCH'].copy()
print(f"  Unmatched records: {len(unmatched)}")

# Identify parent CIKs needed (via ticker)
# This is a mapping of ticker to expected parent CIK based on exact matches and known structures
ticker_to_parent_cik = {
    'TMUS': 1283699,  # T-Mobile US (or 1578078 for alternative)
    'T': 732717,      # AT&T
    'VZ': 732712,     # Verizon
    'CMCSA': 1166691, # Comcast
    'CHTR': 1018724,  # Charter Communications
    'DISH': 1001082,  # DISH Network
    'FYBR': 20520,    # Frontier Communications
    'SIRI': 908937,   # SiriusXM (or 1592709)
    'LUMN': 18926,    # Lumen (CenturyLink)
    'ATUS': 1702780,  # Altice USA
    # Control firms (less likely to have subsidiaries in our sample, but include anyway)
    'ORCL': 777676,   # Oracle
    'MSFT': 789019,   # Microsoft
    'CSCO': 858877,   # Cisco
}

print(f"\n  Identifying parent CIKs from unmatched records...")
parents_needed = set()
for _, row in unmatched.iterrows():
    ticker = row['ticker']
    if ticker in ticker_to_parent_cik:
        parents_needed.add(ticker_to_parent_cik[ticker])
        print(f"    {row['org_name'][:40]:40s} ({ticker:6s}) -> parent CIK {ticker_to_parent_cik[ticker]}")
    else:
        print(f"    {row['org_name'][:40]:40s} ({ticker:6s}) -> unknown parent")

print(f"\n  Parent CIKs to extract Ex-21 from: {sorted(parents_needed)}")

# ============================================================================
# STEP 2: Plan Ex-21 extraction
# ============================================================================
print("\n[2/4] Planning Ex-21 extraction...")

print(f"\nNote: Ex-21 extraction requires downloading 10-K filings from SEC EDGAR.")
print(f"This is a manual process with several steps:")
print(f"  1. Access SEC EDGAR (https://www.sec.gov/cgi-bin/browse-edgar)")
print(f"  2. Search each parent CIK")
print(f"  3. Download recent 10-K filings (most recent before each breach_date)")
print(f"  4. Extract Exhibit 21 (Subsidiaries of the Registrant)")
print(f"  5. Parse subsidiary names and normalize them")
print(f"  6. Match against PRC org_names")

print(f"\nAlternative: Use WRDS data if available")
print(f"  WRDS company.subsidiary table has structured subsidiary data")
print(f"  More reliable than parsing Ex-21 HTML manually")

# ============================================================================
# STEP 3: Create Ex-21 template for manual data entry
# ============================================================================
print("\n[3/4] Creating Ex-21 template for manual data entry...")

# For each parent, create a template showing what needs to be extracted
ex21_template = []

for parent_cik in sorted(parents_needed):
    # Find all unmatched records pointing to this parent
    matching_unmapped = unmatched[unmatched['ticker'].apply(
        lambda t: ticker_to_parent_cik.get(t) == parent_cik
    )]

    ex21_template.append({
        'parent_cik': parent_cik,
        'unmatched_org_names': '|'.join(matching_unmapped['org_name'].unique()),
        'unmatched_count': len(matching_unmapped),
        'breach_years': '|'.join(
            set(pd.to_datetime(matching_unmapped['breach_date']).dt.year.astype(str))
        ),
        'sec_link': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={parent_cik}&type=10-K&dateb=&owner=exclude&count=100',
        'sec_10k_location': f'Find most recent 10-K filing before breach year, then look for Exhibit 21 in the filing',
    })

df_ex21_template = pd.DataFrame(ex21_template)

template_path = Path("Data/ex21_extraction_template.csv")
df_ex21_template.to_csv(template_path, index=False)

print(f"\n  Created template: {template_path}")
print(f"\n  Template shows:")
print(f"    - Parent CIK to extract Ex-21 from")
print(f"    - Which unmatched org_names belong to each parent")
print(f"    - Breach years (for identifying correct 10-K vintage)")
print(f"    - SEC EDGAR link to access the filing")

# ============================================================================
# STEP 4: Create structured output template for manual Ex-21 data
# ============================================================================
print("\n[4/4] Creating output template for extracted subsidiary data...")

# Template for manual data entry after Ex-21 extraction
subsidiary_template = pd.DataFrame({
    'parent_cik': [],
    'parent_name': [],
    'subsidiary_name_from_ex21': [],
    'subsidiary_name_normalized': [],
    'prc_org_name_match': [],
    'matched_prc_record_count': [],
    '10k_filing_date': [],
    'notes': [],
})

subsidiary_output_path = Path("Data/ex21_subsidiaries_extracted.csv")
subsidiary_template.to_csv(subsidiary_output_path, index=False)

print(f"\n  Created output template: {subsidiary_output_path}")
print(f"\n  After extracting Ex-21, fill in:")
print(f"    - parent_cik: CIK of the parent company")
print(f"    - parent_name: Name of the parent company")
print(f"    - subsidiary_name_from_ex21: Exact name from the Ex-21 exhibit")
print(f"    - subsidiary_name_normalized: Normalized version for matching")
print(f"    - prc_org_name_match: Which PRC org_name it matches")
print(f"    - matched_prc_record_count: How many validation records have this org_name")
print(f"    - 10k_filing_date: Date of the 10-K containing this Ex-21")
print(f"    - notes: Any relevant notes")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("EX-21 EXTRACTION WORKFLOW")
print("=" * 100)

print(f"\nYour next steps:")
print(f"  1. Open {template_path}")
print(f"  2. For each parent CIK:")
print(f"     a. Click the SEC EDGAR link")
print(f"     b. Download the most recent 10-K filing (before the breach years listed)")
print(f"     c. Find Exhibit 21 in the filing")
print(f"     d. Extract subsidiary names that match the unmatched org_names")
print(f"  3. Fill in {subsidiary_output_path} with extracted data")
print(f"  4. Run the next script to map subsidiaries to PRC records")

print(f"\nParent CIKs to extract (with unmatched record counts):")
for _, row in df_ex21_template.iterrows():
    print(f"  CIK {row['parent_cik']:>10d}: {row['unmatched_count']:2d} unmatched records")
    print(f"    Years to cover: {row['breach_years']}")

print(f"\n" + "=" * 100)
