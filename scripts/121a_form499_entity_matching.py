"""
SCRIPT 121A: FORM 499 ENTITY MATCHING
======================================

Match dissertation breaches to Form 499 registry.

Input:  Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv
Output: outputs/form499_matched_records.csv

Process:
  1. Load dissertation breach dataset
  2. Query Form 499 registry (already downloaded XML)
  3. For each breach: search Form 499 by org_name
     - Legal_Name exact match
     - doing_business_as exact match
     - other_trade_name exact match
  4. Save matched FRN, dates, end_reason_desc
  5. Generate summary statistics
"""

import pandas as pd
import requests
import xml.etree.ElementTree as ET
import sys
from datetime import datetime
from pathlib import Path

# Setup
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("SCRIPT 121A: FORM 499 ENTITY MATCHING")
print("=" * 80)

# ============================================================================
# LOAD DISSERTATION DATA
# ============================================================================
print("\n1. LOADING DISSERTATION DATASET...")

data_file = 'Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv'
try:
    df = pd.read_csv(data_file)
    print(f"   Loaded: {len(df)} rows")
    print(f"   Columns: {list(df.columns)[:10]}...")

    # Check for org_name and breach_date
    if 'org_name' not in df.columns or 'breach_date' not in df.columns:
        print("   ERROR: Missing org_name or breach_date columns")
        sys.exit(1)

    # Count unique org_names
    unique_orgs = df['org_name'].nunique()
    print(f"   Unique organizations: {unique_orgs}")

except FileNotFoundError:
    print(f"   ERROR: {data_file} not found")
    sys.exit(1)

# ============================================================================
# LOAD FORM 499 REGISTRY
# ============================================================================
print("\n2. LOADING FORM 499 REGISTRY...")

print("   Retrieving from FCC endpoint...")
endpoint = "https://apps.fcc.gov/cgb/form499/499results.cfm"
params = {'xml': 'TRUE'}
headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu',
}

try:
    response = requests.get(endpoint, params=params, headers=headers, timeout=120)
    if response.status_code != 200:
        print(f"   ERROR: Status {response.status_code}")
        sys.exit(1)

    root = ET.fromstring(response.text)
    all_filers = root.findall('.//Filer')
    print(f"   Loaded: {len(all_filers)} filer records")

    # Normalization function
    import re

    def normalize_name(name):
        """Normalize org name for matching: uppercase, strip punctuation, remove suffixes."""
        if not name:
            return ""

        # Uppercase
        name = str(name).upper().strip()

        # Remove punctuation but keep spaces
        name = re.sub(r'[.,;:\-\'"]', '', name)

        # Remove common corporate suffixes
        suffixes = [' INC', ' INCORPORATED', ' CORP', ' CORPORATION', ' LLC', ' LIMITED LIABILITY',
                   ' LP', ' L.P.', ' CO', ' COMPANY', ' THE', ' &', ' AND', ' USA']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()

        # Collapse multiple spaces
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    # Build search index with normalized names
    print("   Building search index with normalized names...")

    filer_index = {}  # {normalized_name -> list of filer records}
    filer_registry = []  # Track all names for fuzzy matching

    for filer in all_filers:
        # Extract fields
        legal_name_elem = filer.find('.//Legal_Name')
        dba_elem = filer.find('.//doing_business_as')
        trade_elem = filer.find('.//other_trade_name')
        frn_elem = filer.find('.//FRN')
        start_elem = filer.find('.//start_date')
        end_elem = filer.find('.//end_date')
        reason_elem = filer.find('.//end_reason_desc')
        repl_elem = filer.find('.//replacement_id')

        names_to_index = []
        if legal_name_elem is not None and legal_name_elem.text:
            names_to_index.append(legal_name_elem.text.strip())
        if dba_elem is not None and dba_elem.text:
            names_to_index.append(dba_elem.text.strip())
        if trade_elem is not None and trade_elem.text:
            names_to_index.append(trade_elem.text.strip())

        filer_record = {
            'legal_name': legal_name_elem.text if legal_name_elem is not None else None,
            'dba': dba_elem.text if dba_elem is not None else None,
            'trade_name': trade_elem.text if trade_elem is not None else None,
            'frn': frn_elem.text if frn_elem is not None else None,
            'start_date': start_elem.text if start_elem is not None else None,
            'end_date': end_elem.text if end_elem is not None else None,
            'end_reason_desc': reason_elem.text if reason_elem is not None else None,
            'replacement_id': repl_elem.text if repl_elem is not None else None,
        }

        for name in names_to_index:
            normalized = normalize_name(name)
            if normalized:
                if normalized not in filer_index:
                    filer_index[normalized] = []
                filer_index[normalized].append(filer_record)
                filer_registry.append((normalized, name))

    print(f"   Index built: {len(filer_index)} unique normalized names in registry")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# MATCHING ALGORITHM
# ============================================================================
print("\n3. MATCHING BREACHES TO FORM 499 (WITH NORMALIZATION)...")

results = []
unmatched_records = []
match_count = 0
no_match_count = 0

for idx, row in df.iterrows():
    org_name = str(row.get('org_name', '')).strip()
    breach_date = row.get('breach_date')

    # Parse breach_date
    try:
        if isinstance(breach_date, str):
            breach_date_obj = pd.to_datetime(breach_date).date()
        else:
            breach_date_obj = pd.to_datetime(breach_date).date()
    except:
        breach_date_obj = None

    # Normalize org_name for search
    org_name_normalized = normalize_name(org_name)

    # Search Form 499 with normalized name
    matched_filer = None
    matched_field = None

    if org_name_normalized in filer_index:
        matched_filer = filer_index[org_name_normalized][0]  # Take first match
        matched_field = 'normalized_match'

    # Record result
    if matched_filer:
        match_count += 1
        result = {
            'org_name': org_name,
            'breach_date': breach_date,
            'matched': 1,
            'matched_field': matched_field,
            'legal_name': matched_filer['legal_name'],
            'dba': matched_filer['dba'],
            'trade_name': matched_filer['trade_name'],
            'frn': matched_filer['frn'],
            'start_date': matched_filer['start_date'],
            'end_date': matched_filer['end_date'],
            'end_reason_desc': matched_filer['end_reason_desc'],
            'replacement_id': matched_filer['replacement_id'],
            'nearest_candidates': None,
        }
    else:
        no_match_count += 1

        # Find nearest candidates in registry (by substring overlap)
        candidates = []
        org_tokens = set(org_name_normalized.split())

        for reg_normalized, reg_original in filer_registry:
            reg_tokens = set(reg_normalized.split())
            # Calculate token overlap
            overlap = len(org_tokens & reg_tokens)
            if overlap >= 1:  # At least one token matches
                candidates.append((overlap, reg_normalized, reg_original))

        # Sort by overlap descending, take top 3
        candidates.sort(reverse=True, key=lambda x: x[0])
        top_candidates = candidates[:3]
        candidates_str = '; '.join([f"{orig} (overlap={overlap})" for overlap, normalized, orig in top_candidates]) if top_candidates else "None"

        result = {
            'org_name': org_name,
            'breach_date': breach_date,
            'matched': 0,
            'matched_field': None,
            'legal_name': None,
            'dba': None,
            'trade_name': None,
            'frn': None,
            'start_date': None,
            'end_date': None,
            'end_reason_desc': None,
            'replacement_id': None,
            'nearest_candidates': candidates_str,
        }

        unmatched_records.append({
            'org_name': org_name,
            'normalized': org_name_normalized,
            'candidates': candidates_str
        })

    results.append(result)

    if (idx + 1) % 100 == 0:
        print(f"   Progress: {idx + 1} / {len(df)}")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n4. SAVING RESULTS...")

results_df = pd.DataFrame(results)
output_file = output_dir / 'form499_matched_records.csv'
results_df.to_csv(output_file, index=False)
print(f"   Saved: {output_file}")

# ============================================================================
# UNMATCHED RECORDS WITH NEAREST CANDIDATES
# ============================================================================
print("\n5. UNMATCHED RECORDS (WITH NEAREST CANDIDATES)")
print("=" * 80)

if unmatched_records:
    print(f"\nUnmatched organization names (n={len(unmatched_records)}):\n")

    for rec in unmatched_records:
        print(f"  PRC: {rec['org_name']}")
        print(f"    Normalized: {rec['normalized']}")
        print(f"    Candidates: {rec['candidates']}")
        print()

    # Save unmatched to CSV for review
    unmatched_df = pd.DataFrame(unmatched_records)
    unmatched_file = output_dir / 'form499_unmatched_with_candidates.csv'
    unmatched_df.to_csv(unmatched_file, index=False)
    print(f"  Saved unmatched summary: {unmatched_file}\n")

print("=" * 80)

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n6. SUMMARY STATISTICS")
print("=" * 80)

matched = results_df[results_df['matched'] == 1]
print(f"\nMatches found: {match_count} / {len(df)} ({100*match_count/len(df):.1f}%)")
print(f"No matches: {no_match_count} ({100*no_match_count/len(df):.1f}%)")

print(f"\nUnique matched organizations: {matched['org_name'].nunique()}")

# End date distribution in matched records
print(f"\nEnd date distribution in matched records:")
print(f"  With end_date: {matched['end_date'].notna().sum()}")
print(f"  Without end_date (current): {matched['end_date'].isna().sum()}")

# End reason distribution
if matched['end_reason_desc'].notna().sum() > 0:
    print(f"\nEnd reason distribution (matched records only):")
    reason_counts = matched['end_reason_desc'].value_counts()
    for reason, count in reason_counts.items():
        reason_display = (reason[:70] + '...') if len(reason) > 70 else reason
        print(f"  [{count:3d}]  {reason_display}")

print("\n" + "=" * 80)
print("OUTPUT FILES GENERATED:")
print("=" * 80)
print(f"  form499_matched_records.csv (all {len(df)} records with match/no-match status)")
print(f"  form499_unmatched_with_candidates.csv ({len(unmatched_records)} unmatched firms with nearest registry candidates)")
print("\nNEXT STEP: Script 121B (Coverage validation and FCC classification)")
print("=" * 80)
