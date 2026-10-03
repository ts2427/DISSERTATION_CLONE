"""
Apply exact matching + known subsidiaries to full 779-record dataset
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

print("=" * 100)
print("APPLY EXACT MATCHING TO FULL DATASET (779 RECORDS)")
print("=" * 100)

# ============================================================================
# STEP 1: Load full dataset and SEC historical CIK data
# ============================================================================
print("\n[1/4] Loading data...")

prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
df_prc = pd.read_csv(prc_path)
print(f"  PRC dataset: {len(df_prc):,} records, {df_prc['org_name'].nunique()} unique org_names")

# Parse SEC historical CIK data (same as validation)
def normalize_name_aggressive(name):
    if not isinstance(name, str):
        return ""
    normalized = name.upper().strip()
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    suffixes = [
        r'\bINC\b', r'\bCORPORATION\b',
        r'\bLLC\b', r'\bLLP\b', r'\bLP\b',
        r'\bCO\b', r'\bCOMPANY\b',
        r'\bLTD\b', r'\bLIMITED\b',
        r'\bNA\b', r'\bNOT FOR PROFIT\b',
        r'\bTHE\b',
    ]
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

sec_path = Path("Data/edgar/cik-lookup-data.txt")
sec_records = {}
normalized_to_ciks = defaultdict(set)

print(f"  Parsing SEC historical CIK data...")
with open(sec_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or ':' not in line:
            continue
        if line.endswith(':'):
            line = line[:-1]
        last_colon = line.rfind(':')
        if last_colon == -1:
            continue
        company_name = line[:last_colon].strip()
        cik_str = line[last_colon + 1:].strip()
        if not company_name or not cik_str:
            continue
        try:
            cik = int(cik_str)
            normalized = normalize_name_aggressive(company_name)
            if normalized:
                if cik not in sec_records:
                    sec_records[cik] = []
                sec_records[cik].append(company_name)
                normalized_to_ciks[normalized].add(cik)
        except ValueError:
            continue

print(f"  SEC data: {len(sec_records):,} unique CIKs, {len(normalized_to_ciks):,} normalized names")

# ============================================================================
# STEP 2: Extract unique org_names and run exact matching
# ============================================================================
print("\n[2/4] Running exact matching on all unique org_names...")

unique_org_names = sorted(df_prc['org_name'].unique())
print(f"  Total unique org_names: {len(unique_org_names)}")

exact_matches = []
unmatched_org_names = []

for org_name in unique_org_names:
    normalized = normalize_name_aggressive(org_name)

    if normalized in normalized_to_ciks:
        ciks_for_name = normalized_to_ciks[normalized]
        if len(ciks_for_name) == 1:
            cik = list(ciks_for_name)[0]
            exact_matches.append({
                'org_name': org_name,
                'cik': cik,
                'match_type': 'EXACT_UNAMBIGUOUS',
                'source': f'SEC name: {sec_records[cik][0]}'
            })
        else:
            exact_matches.append({
                'org_name': org_name,
                'cik': None,
                'match_type': 'EXACT_AMBIGUOUS',
                'source': f'Multiple CIKs: {sorted(ciks_for_name)}'
            })
    else:
        unmatched_org_names.append(org_name)

print(f"  Exact unambiguous: {len([m for m in exact_matches if m['match_type'] == 'EXACT_UNAMBIGUOUS'])}")
print(f"  Exact ambiguous: {len([m for m in exact_matches if m['match_type'] == 'EXACT_AMBIGUOUS'])}")
print(f"  Unmatched: {len(unmatched_org_names)}")

# ============================================================================
# STEP 3: Apply known subsidiary mappings
# ============================================================================
print("\n[3/4] Applying known subsidiary mappings...")

known_subsidiaries = {
    'cricket wireless': {'cik': 732717, 'parent': 'AT&T Inc.'},
    'at t services': {'cik': 732717, 'parent': 'AT&T Inc.'},
    'boost mobile': {'cik': 1001082, 'parent': 'DISH Network Corporation'},
    'sprint nextel': {'cik': 1283699, 'parent': 'T-Mobile US, Inc.'},
    'sprint': {'cik': 1283699, 'parent': 'T-Mobile US, Inc.'},
}

subsidiary_matches = []

for org_name in unmatched_org_names:
    org_name_lower = org_name.lower().replace('inc.', '').replace('llc', '').strip()
    matched = False

    for pattern, parent_info in known_subsidiaries.items():
        if pattern in org_name_lower:
            subsidiary_matches.append({
                'org_name': org_name,
                'cik': parent_info['cik'],
                'match_type': 'SUBSIDIARY_RESOLUTION',
                'source': f'Known subsidiary → {parent_info["parent"]}'
            })
            matched = True
            break

    if not matched:
        unmatched_org_names.remove(org_name)

print(f"  Subsidiary matches: {len(subsidiary_matches)}")
print(f"  Remaining unmatched: {len(unmatched_org_names)}")

# ============================================================================
# STEP 4: Create full mapping and apply to PRC dataset
# ============================================================================
print("\n[4/4] Creating full mapping and applying to dataset...")

# Combine all matches
all_matches = pd.DataFrame(exact_matches + subsidiary_matches)

# Create mapping: org_name → cik
org_name_to_cik = {}
org_name_to_source = {}
for _, row in all_matches.iterrows():
    if pd.notna(row['cik']):
        org_name_to_cik[row['org_name']] = row['cik']
        org_name_to_source[row['org_name']] = row['source']

# Apply to full dataset
df_prc['resolved_cik'] = df_prc['org_name'].map(org_name_to_cik)
df_prc['resolution_source'] = df_prc['org_name'].map(org_name_to_source)

# Count results
resolved_records = df_prc['resolved_cik'].notna().sum()
unresolved_records = df_prc['resolved_cik'].isna().sum()

print(f"\n  Records with resolved CIK: {resolved_records:,} ({resolved_records/len(df_prc)*100:.1f}%)")
print(f"  Records without resolved CIK: {unresolved_records:,} ({unresolved_records/len(df_prc)*100:.1f}%)")

# Save results
output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_WITH_RESOLVED_CIK.csv")
df_prc.to_csv(output_path, index=False)

# Save summary
summary_output = Path("outputs/full_dataset_resolution_summary.csv")
all_matches.to_csv(summary_output, index=False)

print(f"\nOutput files:")
print(f"  1. {output_path}")
print(f"     Full dataset with 'resolved_cik' and 'resolution_source' columns")
print(f"\n  2. {summary_output}")
print(f"     Summary of all org_name → CIK mappings")

# ============================================================================
# REPORT
# ============================================================================
print("\n" + "=" * 100)
print("FULL DATASET RESOLUTION REPORT")
print("=" * 100)

print(f"""
DATASET COVERAGE:
  Total records: {len(df_prc):,}
  Total unique org_names: {len(unique_org_names)}

RESOLUTION BY METHOD:
  Exact unambiguous: {len([m for m in exact_matches if m['match_type'] == 'EXACT_UNAMBIGUOUS']):3d} org_names
  Exact ambiguous:   {len([m for m in exact_matches if m['match_type'] == 'EXACT_AMBIGUOUS']):3d} org_names
  Subsidiary:        {len(subsidiary_matches):3d} org_names
  Unmatched:         {len(unmatched_org_names):3d} org_names

RECORD COVERAGE:
  Resolved: {resolved_records:,} records ({resolved_records/len(df_prc)*100:.1f}%)
  Unresolved: {unresolved_records:,} records ({unresolved_records/len(df_prc)*100:.1f}%)

NEXT STEPS:
  1. The 'resolved_cik' column in the output dataset is the corrected CIK mapping
  2. Compare resolved_cik vs original 'cik' column to identify corrections
  3. For unresolved records ({unresolved_records}), consider:
     - Running reasoning pass (Claude Code lookup)
     - Manual verification for critical cases
     - Flagging as unmatched if private/not found in SEC
  4. Bridge to PERMNO using CRSP stocknames with date-aware filtering
  5. Re-compute dependent variables (CAR, BHAR, volatility) with corrected stock returns
""")

print("=" * 100)
