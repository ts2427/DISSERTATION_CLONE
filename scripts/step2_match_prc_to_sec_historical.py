"""
STEP 2: Match PRC org_names to SEC historical CIK data
Uses cik-lookup-data.txt (cumulative historical, includes delisted firms)
Strict matching only; residual to manual review
"""

import pandas as pd
import numpy as np
from pathlib import Path
from difflib import SequenceMatcher
import re
import requests

print("=" * 100)
print("STEP 2: MATCH PRC ORG_NAMES TO SEC HISTORICAL CIK DATA")
print("=" * 100)

# ============================================================================
# STEP 2a: Fetch SEC historical CIK data
# ============================================================================
print("\n[1/6] Fetching SEC historical CIK lookup data...")

SEC_URL = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
LOCAL_SEC_PATH = Path("Data/edgar/cik-lookup-data.txt")

# Ensure output directory exists
LOCAL_SEC_PATH.parent.mkdir(parents=True, exist_ok=True)

if LOCAL_SEC_PATH.exists():
    print(f"  Using cached copy at {LOCAL_SEC_PATH}")
    with open(LOCAL_SEC_PATH, 'r', encoding='utf-8') as f:
        sec_lines = f.readlines()
else:
    print(f"  Downloading from {SEC_URL}")
    try:
        headers = {
            'User-Agent': 'fsuace826@gmail.com'
        }
        response = requests.get(SEC_URL, headers=headers, timeout=60)
        response.raise_for_status()
        sec_lines = response.text.splitlines(keepends=True)

        # Save locally
        with open(LOCAL_SEC_PATH, 'w', encoding='utf-8') as f:
            f.writelines(sec_lines)
        print(f"  Saved to {LOCAL_SEC_PATH}")
    except Exception as e:
        print(f"  ERROR: Could not fetch SEC data: {e}")
        exit(1)

print(f"  Loaded {len(sec_lines):,} lines from SEC")

# ============================================================================
# STEP 2b: Parse SEC historical CIK data
# ============================================================================
print("\n[2/6] Parsing SEC historical CIK data...")

def normalize_name(name):
    """
    Normalize company name for matching:
    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse internal whitespace
    - Remove common legal suffixes
    - Remove punctuation
    """
    if not isinstance(name, str):
        return ""

    normalized = name.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)

    suffixes = [
        r'\s+inc\.?$', r'\s+corp\.?$', r'\s+corporation$',
        r'\s+ltd\.?$', r'\s+limited$', r'\s+llc$',
        r'\s+lp$', r'\s+l\.?p\.?$',
        r'\s+co\.?$', r'\s+company$',
        r'\s+na$', r'\s+inc\.$',
    ]
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)

    normalized = normalized.rstrip('.,;:')
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized


# Parse SEC format: "Company Name:CIK:" (colon-delimited with trailing colon)
sec_records = []
for line in sec_lines:
    line = line.strip()
    if not line or ':' not in line:
        continue

    # Remove trailing colon if present
    if line.endswith(':'):
        line = line[:-1]

    # Split on the last colon
    last_colon_idx = line.rfind(':')
    if last_colon_idx == -1:
        continue

    company_name = line[:last_colon_idx].strip()
    cik_str = line[last_colon_idx + 1:].strip()

    if not cik_str:
        continue

    # Skip lines with no company name (they're just CIKs)
    if not company_name:
        continue

    try:
        cik = int(cik_str)

        sec_records.append({
            'cik': cik,
            'sec_company_name': company_name,
            'sec_company_name_normalized': normalize_name(company_name),
        })
    except ValueError:
        continue

df_sec = pd.DataFrame(sec_records)

print(f"  Parsed {len(df_sec):,} CIK-name pairs from SEC")
print(f"  Unique CIKs: {df_sec['cik'].nunique():,}")
print(f"  Unique names: {df_sec['sec_company_name_normalized'].nunique():,}")

# Check for multi-name CIKs (historical name changes, subsidiaries)
ciks_multi_names = df_sec['cik'].value_counts()
ciks_multi_names = ciks_multi_names[ciks_multi_names > 1]
print(f"  CIKs with multiple names (historical, subsidiaries): {len(ciks_multi_names):,}")

# Sample multi-name CIKs
print(f"\n  Sample multi-name CIKs:")
for cik in ciks_multi_names.head(5).index:
    names = df_sec[df_sec['cik'] == cik]['sec_company_name'].unique()
    print(f"    CIK {cik}: {', '.join(names[:3])}...")

# Create normalized lookup dictionary for faster matching
sec_lookup = {}
for _, row in df_sec.iterrows():
    normalized = row['sec_company_name_normalized']
    if normalized not in sec_lookup:
        sec_lookup[normalized] = []
    sec_lookup[normalized].append({
        'cik': row['cik'],
        'sec_company_name': row['sec_company_name'],
    })

print(f"\n  Built lookup with {len(sec_lookup):,} unique normalized names")

# ============================================================================
# STEP 2c: Load PRC dataset
# ============================================================================
print("\n[3/6] Loading PRC dataset...")

prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
prc_df = pd.read_csv(prc_path)
print(f"  Loaded PRC dataset: {len(prc_df):,} records")

# Extract unique org_names
unique_org_names = sorted(prc_df['org_name'].unique())
print(f"  Unique org_names in PRC: {len(unique_org_names)}")

# ============================================================================
# STEP 2d: Match each PRC org_name to SEC historical data
# ============================================================================
print("\n[4/6] Matching PRC org_names to SEC historical data...")

def fuzzy_match_ratio(s1, s2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, s1, s2).ratio()


matches = []
unmatched = []

for org_name in unique_org_names:
    normalized_prc = normalize_name(org_name)

    # Try exact match first
    if normalized_prc in sec_lookup:
        candidates = sec_lookup[normalized_prc]
        for cand in candidates:
            matches.append({
                'org_name': org_name,
                'org_name_normalized': normalized_prc,
                'cik': cand['cik'],
                'sec_company_name': cand['sec_company_name'],
                'match_type': 'EXACT',
                'confidence': 1.0,
                'review_needed': False,
            })
    else:
        # Try fuzzy matching against SEC normalized names
        best_match = None
        best_score = 0.0

        for sec_normalized, candidates in sec_lookup.items():
            score = fuzzy_match_ratio(normalized_prc, sec_normalized)
            if score > best_score:
                best_score = score
                best_match = (sec_normalized, candidates)

        # Only accept fuzzy matches above 0.90 confidence
        if best_score >= 0.90:
            _, candidates = best_match
            for cand in candidates:
                matches.append({
                    'org_name': org_name,
                    'org_name_normalized': normalized_prc,
                    'cik': cand['cik'],
                    'sec_company_name': cand['sec_company_name'],
                    'match_type': 'FUZZY',
                    'confidence': best_score,
                    'review_needed': True,
                })
        else:
            # Below threshold - goes to manual review
            unmatched.append({
                'org_name': org_name,
                'org_name_normalized': normalized_prc,
                'best_sec_match': best_match[0] if best_match else None,
                'best_score': best_score,
            })

df_matches = pd.DataFrame(matches)
df_unmatched = pd.DataFrame(unmatched)

print(f"  Exact matches: {len(df_matches[df_matches['match_type'] == 'EXACT']):,}")
print(f"  Fuzzy matches (>= 0.90): {len(df_matches[df_matches['match_type'] == 'FUZZY']):,}")
print(f"  Unmatched (< 0.90): {len(df_unmatched):,}")

# ============================================================================
# STEP 2e: Deduplicate by org_name (not by match result)
# ============================================================================
print("\n[5/6] Deduplicating matches by org_name...")

# For each org_name with multiple match candidates (multi-name CIKs),
# keep all but note the duplication
matches_dedup = df_matches.copy()
matches_dedup['match_count_for_org'] = matches_dedup.groupby('org_name')['cik'].transform('count')
matches_dedup['is_multi_match'] = matches_dedup['match_count_for_org'] > 1

dup_org_names = matches_dedup[matches_dedup['is_multi_match']]['org_name'].unique()
print(f"  Org_names with multiple CIK matches: {len(dup_org_names)}")

if len(dup_org_names) > 0:
    print(f"\n  Sample multi-match org_names:")
    for org_name in list(dup_org_names)[:5]:
        ciks = matches_dedup[matches_dedup['org_name'] == org_name]['cik'].unique()
        print(f"    {org_name:50s} -> CIKs: {', '.join(map(str, ciks))}")

# ============================================================================
# STEP 2f: Save outputs
# ============================================================================
print("\n[6/6] Saving outputs...")

# Sort matched by match type, then org_name
matches_sorted = matches_dedup.sort_values(['match_type', 'org_name']).reset_index(drop=True)

output_matched = Path("Data/edgar/step2_matched_org_names.csv")
matches_sorted.to_csv(output_matched, index=False)
print(f"  Saved matched: {output_matched}")
print(f"    - {len(matches_sorted[matches_sorted['match_type'] == 'EXACT'])} rows from exact matches")
print(f"    - {len(matches_sorted[matches_sorted['match_type'] == 'FUZZY'])} rows from fuzzy matches")

# Count unique org_names (accounting for multi-matches)
exact_org_names = len(df_matches[df_matches['match_type'] == 'EXACT']['org_name'].unique())
fuzzy_org_names = len(df_matches[df_matches['match_type'] == 'FUZZY']['org_name'].unique())
print(f"\n    Org_names: {exact_org_names} exact, {fuzzy_org_names} fuzzy")

# Save unmatched for manual review
unmatched_sorted = df_unmatched.sort_values('org_name').reset_index(drop=True)
output_unmatched = Path("Data/edgar/step2_manual_review_worksheet.csv")
unmatched_sorted.to_csv(output_unmatched, index=False)
print(f"  Saved manual review: {output_unmatched}")
print(f"    - {len(unmatched_sorted)} org_names requiring manual CIK assignment")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2 SUMMARY: SEC HISTORICAL CIK MATCHING COMPLETE")
print("=" * 100)

total_org_names = len(unique_org_names)
exact_org_names = len(df_matches[df_matches['match_type'] == 'EXACT']['org_name'].unique())
fuzzy_org_names = len(df_matches[df_matches['match_type'] == 'FUZZY']['org_name'].unique())
unmatched_org_names = len(df_unmatched)

print(f"\nMatching results (deduped by org_name):")
print(f"  Total unique PRC org_names: {total_org_names}")
print(f"  Exact matches: {exact_org_names}")
print(f"  Fuzzy matches (>= 0.90): {fuzzy_org_names}")
print(f"  Manual review required: {unmatched_org_names}")
print(f"\n  Automated coverage: {((exact_org_names + fuzzy_org_names) / total_org_names * 100):.1f}%")
print(f"  Manual review share: {(unmatched_org_names / total_org_names * 100):.1f}%")

print(f"\nCIK collision check (multi-name CIKs from SEC):")
print(f"  Org_names with multiple CIK matches: {len(dup_org_names)}")
print(f"    (These need manual review to pick correct CIK)")

# Map unmatched to record counts
prc_unmatched_counts = {}
for org_name in df_unmatched['org_name']:
    count = len(prc_df[prc_df['org_name'] == org_name])
    prc_unmatched_counts[org_name] = count

df_unmatched['record_count'] = df_unmatched['org_name'].map(prc_unmatched_counts)
total_unmatched_records = df_unmatched['record_count'].sum()

print(f"\nRecord impact of unmatched org_names:")
print(f"  Unmatched org_names: {len(df_unmatched)}")
print(f"  PRC records affected: {total_unmatched_records:,} out of {len(prc_df):,}")
print(f"  Coverage: {((len(prc_df) - total_unmatched_records) / len(prc_df) * 100):.1f}%")

print(f"\nOutput files:")
print(f"  1. {output_matched}")
print(f"     Columns: org_name, org_name_normalized, cik, sec_company_name,")
print(f"              match_type, confidence, review_needed, match_count_for_org, is_multi_match")
print(f"\n  2. {output_unmatched}")
print(f"     Columns: org_name, org_name_normalized, best_sec_match, best_score, record_count")

print(f"\nNext step: Enhance worksheet with PRC metadata for manual review")
print("=" * 100)

# Show sample of unmatched
if len(df_unmatched) > 0:
    df_unmatched_sorted_by_records = df_unmatched.sort_values('record_count', ascending=False)
    print(f"\nTop 15 unmatched org_names by record count:")
    print(f"{'Rank':<5} {'Record Count':<15} {'Org Name':<60}")
    print("-" * 80)
    for idx in range(min(15, len(df_unmatched_sorted_by_records))):
        row = df_unmatched_sorted_by_records.iloc[idx]
        print(f"{idx+1:<5} {row['record_count']:<15} {row['org_name']:<60}")
