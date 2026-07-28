"""
STEP 2: Match 779 PRC org_names against EDGAR reference
Strict matching only; residual to manual review
"""

import pandas as pd
import numpy as np
from pathlib import Path
from difflib import SequenceMatcher
import re

print("=" * 100)
print("STEP 2: MATCH PRC ORG_NAMES TO EDGAR REFERENCE")
print("=" * 100)

# ============================================================================
# STEP 2a: Load data
# ============================================================================
print("\n[1/5] Loading data...")

# Load PRC dataset
prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
prc_df = pd.read_csv(prc_path)
print(f"  Loaded PRC dataset: {len(prc_df):,} records")

# Extract unique org_names
unique_org_names = sorted(prc_df['org_name'].unique())
print(f"  Unique org_names in PRC: {len(unique_org_names)}")

# Load EDGAR reference
edgar_path = Path("Data/edgar/cik_ticker_map_normalized.csv")
edgar_df = pd.read_csv(edgar_path)
print(f"  Loaded EDGAR reference: {len(edgar_df):,} records")

# Create normalized lookup dictionary for faster matching
# Key: normalized company name, Value: list of (cik, ticker, original_name) tuples
edgar_lookup = {}
for _, row in edgar_df.iterrows():
    normalized = row['company_name_normalized']
    if normalized not in edgar_lookup:
        edgar_lookup[normalized] = []
    edgar_lookup[normalized].append({
        'cik': row['cik'],
        'ticker': row['ticker'],
        'company_name': row['company_name'],
    })

print(f"  Built lookup with {len(edgar_lookup):,} unique normalized names")

# ============================================================================
# STEP 2b: Normalize PRC org_names with same logic as EDGAR
# ============================================================================
print("\n[2/5] Normalizing PRC org_names...")

def normalize_name(name):
    """Same normalization as Step 1"""
    if not isinstance(name, str):
        return ""
    normalized = name.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    suffixes = [
        r'\s+inc\.?$', r'\s+corp\.?$', r'\s+corporation$',
        r'\s+ltd\.?$', r'\s+limited$', r'\s+llc$',
        r'\s+lp$', r'\s+l\.?p\.?$',
        r'\s+co\.?$', r'\s+company$',
        r'\s+na$',
    ]
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)
    normalized = normalized.rstrip('.,;:')
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


# ============================================================================
# STEP 2c: Attempt to match each PRC org_name
# ============================================================================
print("\n[3/5] Matching PRC org_names to EDGAR...")

def fuzzy_match_ratio(s1, s2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, s1, s2).ratio()


matches = []
unmatched = []

for org_name in unique_org_names:
    normalized_prc = normalize_name(org_name)

    # Try exact match first
    if normalized_prc in edgar_lookup:
        candidates = edgar_lookup[normalized_prc]
        for cand in candidates:
            matches.append({
                'org_name': org_name,
                'org_name_normalized': normalized_prc,
                'cik': cand['cik'],
                'ticker': cand['ticker'],
                'edgar_company_name': cand['company_name'],
                'match_type': 'EXACT',
                'confidence': 1.0,
                'review_needed': False,
            })
    else:
        # If no exact match, try fuzzy matching against all EDGAR normalized names
        # But only keep high-confidence matches
        best_match = None
        best_score = 0.0

        for edgar_normalized, candidates in edgar_lookup.items():
            score = fuzzy_match_ratio(normalized_prc, edgar_normalized)
            if score > best_score:
                best_score = score
                best_match = (edgar_normalized, candidates)

        # Only accept fuzzy matches above 0.90 confidence
        if best_score >= 0.90:
            _, candidates = best_match
            for cand in candidates:
                matches.append({
                    'org_name': org_name,
                    'org_name_normalized': normalized_prc,
                    'cik': cand['cik'],
                    'ticker': cand['ticker'],
                    'edgar_company_name': cand['company_name'],
                    'match_type': 'FUZZY',
                    'confidence': best_score,
                    'review_needed': True,
                })
        else:
            # Below threshold - goes to manual review
            unmatched.append({
                'org_name': org_name,
                'org_name_normalized': normalized_prc,
                'best_edgar_match': best_match[0] if best_match else None,
                'best_score': best_score,
            })

df_matches = pd.DataFrame(matches)
df_unmatched = pd.DataFrame(unmatched)

print(f"  Exact matches: {len(df_matches[df_matches['match_type'] == 'EXACT']):,}")
print(f"  Fuzzy matches (>= 0.90): {len(df_matches[df_matches['match_type'] == 'FUZZY']):,}")
print(f"  Unmatched (< 0.90): {len(df_unmatched):,}")

# ============================================================================
# STEP 2d: Handle duplicate CIKs (firms with multiple holdings/subsidiaries)
# ============================================================================
print("\n[4/5] Handling duplicate CIKs...")

# For CIKs with multiple org_names, flag for review
dup_ciks_in_matches = df_matches['cik'].value_counts()
dup_ciks_in_matches = dup_ciks_in_matches[dup_ciks_in_matches > 1]

print(f"  CIKs with multiple org_names in matched set: {len(dup_ciks_in_matches)}")

# Flag duplicates for review
df_matches['has_duplicate_cik'] = df_matches['cik'].isin(dup_ciks_in_matches.index)

# If an org_name already has a duplicate CIK, note it
for cik in dup_ciks_in_matches.index:
    org_names_for_cik = df_matches[df_matches['cik'] == cik]['org_name'].unique()
    print(f"    CIK {cik}: {', '.join(org_names_for_cik[:3])}...")

# ============================================================================
# STEP 2e: Save outputs
# ============================================================================
print("\n[5/5] Saving outputs...")

# Sort matched by match type (exact first) and by org_name
df_matches_sorted = df_matches.sort_values(['match_type', 'org_name']).reset_index(drop=True)

output_matched = Path("Data/edgar/step2_matched_org_names.csv")
df_matches_sorted.to_csv(output_matched, index=False)
print(f"  Saved matched: {output_matched}")
print(f"    - {len(df_matches_sorted[df_matches_sorted['match_type'] == 'EXACT'])} exact matches")
print(f"    - {len(df_matches_sorted[df_matches_sorted['match_type'] == 'FUZZY'])} fuzzy matches (flagged for review)")

# Save unmatched for manual review
df_unmatched_sorted = df_unmatched.sort_values('org_name').reset_index(drop=True)
output_unmatched = Path("Data/edgar/step2_manual_review_worksheet.csv")
df_unmatched_sorted.to_csv(output_unmatched, index=False)
print(f"  Saved manual review: {output_unmatched}")
print(f"    - {len(df_unmatched_sorted)} org_names requiring manual CIK assignment")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2 SUMMARY: ORG_NAME MATCHING COMPLETE")
print("=" * 100)

print(f"\nMatching results:")
print(f"  Total unique PRC org_names: {len(unique_org_names)}")
print(f"  Exact matches: {len(df_matches[df_matches['match_type'] == 'EXACT']):,}")
print(f"  Fuzzy matches (>= 0.90): {len(df_matches[df_matches['match_type'] == 'FUZZY']):,}")
print(f"  Manual review required: {len(df_unmatched):,}")
print(f"\n  Automated coverage: {(len(df_matches) / len(unique_org_names) * 100):.1f}%")
print(f"  Manual review share: {(len(df_unmatched) / len(unique_org_names) * 100):.1f}%")

print(f"\nCIK collision check:")
print(f"  CIKs with multiple org_names: {len(dup_ciks_in_matches)}")
print(f"    (These are legitimate holdings/subsidiaries)")

print(f"\nOutput files:")
print(f"  1. {output_matched}")
print(f"     - Columns: org_name, org_name_normalized, cik, ticker, edgar_company_name,")
print(f"               match_type, confidence, review_needed, has_duplicate_cik")
print(f"\n  2. {output_unmatched}")
print(f"     - Columns: org_name, org_name_normalized, best_edgar_match, best_score")
print(f"     - ACTION: Manual assignment of CIK for each row")

print(f"\nNext step: Manual review of {len(df_unmatched):,} unmatched org_names")
print(f"          (Search SEC EDGAR or business database for each CIK)")
print("=" * 100)

# Show sample of unmatched
if len(df_unmatched) > 0:
    print(f"\nSample unmatched org_names:")
    for idx in range(min(10, len(df_unmatched))):
        row = df_unmatched.iloc[idx]
        print(f"  {row['org_name']:50s} | best_match: {row['best_edgar_match']:40s} ({row['best_score']:.3f})")
