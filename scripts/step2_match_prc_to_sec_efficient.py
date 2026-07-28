"""
STEP 2 (REVISED): Match PRC org_names to SEC historical CIK data
Efficient: normalize once, exact-match via dict, fuzzy only on residual with blocking
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import defaultdict

print("=" * 100)
print("STEP 2 (REVISED): EFFICIENT SEC HISTORICAL CIK MATCHING")
print("=" * 100)

# ============================================================================
# STEP 2a: Load data
# ============================================================================
print("\n[1/6] Loading data...")

# Load SEC historical CIK data
sec_path = Path("Data/edgar/cik-lookup-data.txt")
prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")

sec_lines = []
with open(sec_path, 'r', encoding='utf-8') as f:
    sec_lines = f.readlines()
print(f"  SEC file: {len(sec_lines):,} lines")

prc_df = pd.read_csv(prc_path)
print(f"  PRC dataset: {len(prc_df):,} records, {prc_df['org_name'].nunique()} unique org_names")

# ============================================================================
# STEP 2b: Define normalization (applied to both SEC and PRC)
# ============================================================================

def normalize_name_aggressive(name):
    """
    Aggressive normalization for matching:
    - Uppercase
    - Remove punctuation
    - Strip legal suffixes (INC, CORP, LLC, LP, CO, THE)
    - Collapse whitespace
    """
    if not isinstance(name, str):
        return ""

    # Uppercase and strip
    normalized = name.upper().strip()

    # Remove punctuation (keep only alphanumeric and space)
    normalized = re.sub(r'[^\w\s]', ' ', normalized)

    # Collapse whitespace
    normalized = re.sub(r'\s+', ' ', normalized)

    # Remove common legal suffixes (word boundaries)
    suffixes = [
        r'\bINC\b', r'\bCORPORATION\b', r'\bCORPORATION\b',
        r'\bLLC\b', r'\bLLP\b', r'\bLP\b',
        r'\bCO\b', r'\bCOMPANY\b',
        r'\bLTD\b', r'\bLIMITED\b',
        r'\bNA\b', r'\bNOT FOR PROFIT\b',
        r'\bTHE\b',  # Common prefix
    ]
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)

    # Re-collapse whitespace after suffix removal
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized


def get_first_token(name):
    """Get first token of normalized name for blocking"""
    parts = name.split()
    return parts[0] if parts else ""


def get_first_four_chars(name):
    """Get first 4 characters for blocking"""
    return name[:4]


# ============================================================================
# STEP 2c: Parse and normalize SEC data (once)
# ============================================================================
print("\n[2/6] Parsing SEC data and building lookup...")

sec_records = {}  # cik -> list of (orig_name, normalized_name)
normalized_to_ciks = defaultdict(set)  # normalized_name -> set of CIKs

for line_idx, line in enumerate(sec_lines):
    line = line.strip()
    if not line or ':' not in line:
        continue

    # Remove trailing colon
    if line.endswith(':'):
        line = line[:-1]

    # Split on last colon
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

        if normalized:  # Only if normalization produced something
            if cik not in sec_records:
                sec_records[cik] = []
            sec_records[cik].append((company_name, normalized))
            normalized_to_ciks[normalized].add(cik)

    except ValueError:
        continue

print(f"  Parsed SEC data:")
print(f"    Unique CIKs: {len(sec_records):,}")
print(f"    Unique normalized names: {len(normalized_to_ciks):,}")
print(f"    CIKs with multiple names: {sum(1 for v in sec_records.values() if len(v) > 1):,}")
print(f"    Normalized names mapping to multiple CIKs: {sum(1 for v in normalized_to_ciks.values() if len(v) > 1):,}")

# ============================================================================
# STEP 2d: Extract and normalize PRC org_names (once)
# ============================================================================
print("\n[3/6] Normalizing PRC org_names...")

prc_org_names = sorted(prc_df['org_name'].unique())
prc_normalized_map = {}  # org_name -> normalized_name

for org_name in prc_org_names:
    normalized = normalize_name_aggressive(org_name)
    prc_normalized_map[org_name] = normalized

print(f"  Normalized {len(prc_org_names)} unique PRC org_names")

# ============================================================================
# STEP 2e: Exact matching via dict lookup (hash join)
# ============================================================================
print("\n[4/6] Exact matching (hash join)...")

exact_matches = []
residual_org_names = []

for org_name in prc_org_names:
    normalized_prc = prc_normalized_map[org_name]

    # Exact match: normalized_prc is a key in normalized_to_ciks
    if normalized_prc in normalized_to_ciks:
        ciks_for_name = normalized_to_ciks[normalized_prc]

        if len(ciks_for_name) == 1:
            # Unambiguous: one CIK for this normalized name
            cik = list(ciks_for_name)[0]
            sec_names = sec_records[cik]
            for sec_name, sec_normalized in sec_names:
                if sec_normalized == normalized_prc:  # Use first matching SEC name
                    exact_matches.append({
                        'org_name': org_name,
                        'normalized_name': normalized_prc,
                        'cik': cik,
                        'sec_company_name': sec_name,
                        'match_type': 'EXACT_UNAMBIGUOUS',
                        'confidence': 1.0,
                        'review_needed': False,
                        'ambiguity': False,
                    })
                    break
        else:
            # Ambiguous: multiple CIKs for this normalized name
            # Without breach date context, flag all as ambiguous
            for cik in ciks_for_name:
                sec_names = sec_records[cik]
                for sec_name, sec_normalized in sec_names:
                    if sec_normalized == normalized_prc:
                        exact_matches.append({
                            'org_name': org_name,
                            'normalized_name': normalized_prc,
                            'cik': cik,
                            'sec_company_name': sec_name,
                            'match_type': 'EXACT_AMBIGUOUS',
                            'confidence': 0.95,
                            'review_needed': True,
                            'ambiguity': True,
                        })
                        break
    else:
        # No exact match: goes to residual for fuzzy matching
        residual_org_names.append(org_name)

print(f"  Exact matches: {len(exact_matches)}")
print(f"  Residual (for fuzzy): {len(residual_org_names)}")

# ============================================================================
# STEP 2f: Fuzzy matching on residual with blocking
# ============================================================================
print("\n[5/6] Fuzzy matching on residual (with blocking)...")

try:
    from rapidfuzz import fuzz
    use_rapidfuzz = True
    print("  Using rapidfuzz for fuzzy matching")
except ImportError:
    print("  rapidfuzz not available, using difflib")
    from difflib import SequenceMatcher
    use_rapidfuzz = False


fuzzy_matches = []

for org_name in residual_org_names:
    normalized_prc = prc_normalized_map[org_name]

    # Blocking: only consider SEC names that share first token or first 4 chars
    first_token_prc = get_first_token(normalized_prc)
    first_four_prc = get_first_four_chars(normalized_prc)

    candidates = []

    # Find candidates that match first token or first 4 chars
    for sec_normalized, ciks_set in normalized_to_ciks.items():
        first_token_sec = get_first_token(sec_normalized)
        first_four_sec = get_first_four_chars(sec_normalized)

        # Blocking condition: share first token OR first 4 chars
        if first_token_prc == first_token_sec or first_four_prc == first_four_sec:
            candidates.append((sec_normalized, ciks_set))

    if not candidates:
        # No candidates even with blocking: goes to manual review
        continue

    # Fuzzy match against candidates
    best_score = 0.0
    best_normalized_sec = None
    best_ciks = None

    for sec_normalized, ciks_set in candidates:
        if use_rapidfuzz:
            score = fuzz.ratio(normalized_prc, sec_normalized) / 100.0
        else:
            score = SequenceMatcher(None, normalized_prc, sec_normalized).ratio()

        if score > best_score:
            best_score = score
            best_normalized_sec = sec_normalized
            best_ciks = ciks_set

    # Only accept fuzzy matches above 0.90
    if best_score >= 0.90:
        for cik in best_ciks:
            sec_names = sec_records[cik]
            for sec_name, sec_normalized in sec_names:
                if sec_normalized == best_normalized_sec:
                    fuzzy_matches.append({
                        'org_name': org_name,
                        'normalized_name': normalized_prc,
                        'cik': cik,
                        'sec_company_name': sec_name,
                        'match_type': 'FUZZY',
                        'confidence': best_score,
                        'review_needed': True,
                        'ambiguity': len(best_ciks) > 1,
                    })
                    break

unmatched_org_names = [org for org in residual_org_names
                       if org not in [m['org_name'] for m in fuzzy_matches]]

print(f"  Fuzzy matches (>= 0.90): {len(fuzzy_matches)}")
print(f"  Unmatched after fuzzy: {len(unmatched_org_names)}")

# ============================================================================
# STEP 2g: Combine and save outputs
# ============================================================================
print("\n[6/6] Saving outputs...")

df_matched = pd.DataFrame(exact_matches + fuzzy_matches)
df_matched_sorted = df_matched.sort_values(['match_type', 'org_name']).reset_index(drop=True)

# New output filenames to avoid confusion with old run
output_matched = Path("Data/edgar/step2_matched_org_names_v2.csv")
df_matched_sorted.to_csv(output_matched, index=False)

print(f"  Saved matched: {output_matched}")
print(f"    Rows: {len(df_matched_sorted)}")
print(f"    Exact unambiguous: {len(df_matched_sorted[df_matched_sorted['match_type'] == 'EXACT_UNAMBIGUOUS'])}")
print(f"    Exact ambiguous: {len(df_matched_sorted[df_matched_sorted['match_type'] == 'EXACT_AMBIGUOUS'])}")
print(f"    Fuzzy: {len(df_matched_sorted[df_matched_sorted['match_type'] == 'FUZZY'])}")

# Unmatched org_names
df_unmatched = pd.DataFrame([
    {'org_name': org_name, 'normalized_name': prc_normalized_map[org_name]}
    for org_name in unmatched_org_names
]).sort_values('org_name').reset_index(drop=True)

output_unmatched = Path("Data/edgar/step2_manual_review_v2.csv")
df_unmatched.to_csv(output_unmatched, index=False)

print(f"  Saved manual review: {output_unmatched}")
print(f"    Org_names: {len(df_unmatched)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2 COMPLETE: EFFICIENT MATCHING")
print("=" * 100)

total_org_names = len(prc_org_names)
matched_org_names = len(df_matched_sorted['org_name'].unique())
unmatched = len(df_unmatched)

print(f"\nMatching results (by unique org_name):")
print(f"  Total PRC org_names: {total_org_names}")
print(f"  Matched (exact + fuzzy): {matched_org_names}")
print(f"  Unmatched: {unmatched}")
print(f"  Automated coverage: {(matched_org_names / total_org_names * 100):.1f}%")

# Record coverage
prc_matched_records = prc_df[prc_df['org_name'].isin(df_matched_sorted['org_name'].unique())]
prc_unmatched_records = prc_df[prc_df['org_name'].isin(df_unmatched['org_name'].unique())]

print(f"\nRecord coverage:")
print(f"  Total PRC records: {len(prc_df)}")
print(f"  From matched org_names: {len(prc_matched_records)} ({len(prc_matched_records)/len(prc_df)*100:.1f}%)")
print(f"  From unmatched org_names: {len(prc_unmatched_records)} ({len(prc_unmatched_records)/len(prc_df)*100:.1f}%)")

print(f"\nAmbiguous matches (require breach date for disambiguation):")
ambig = df_matched_sorted[df_matched_sorted['ambiguity'] == True]
print(f"  Rows: {len(ambig)}")
print(f"  Unique org_names: {ambig['org_name'].nunique()}")

print(f"\nOutput files:")
print(f"  1. {output_matched}")
print(f"  2. {output_unmatched}")

print("\n" + "=" * 100)
