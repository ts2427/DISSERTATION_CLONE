"""
Run exact matching on validation set against SEC historical CIK data
Score: how many resolve via exact matching alone?
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

print("=" * 100)
print("EXACT MATCHING: VALIDATION SET vs SEC HISTORICAL CIK DATA")
print("=" * 100)

# ============================================================================
# STEP 1: Load validation set
# ============================================================================
print("\n[1/4] Loading validation set...")

validation_path = Path("Data/validation_set_40_records.csv")
df_validation = pd.read_csv(validation_path)
print(f"  Loaded: {len(df_validation)} records")

# ============================================================================
# STEP 2: Parse SEC historical CIK data
# ============================================================================
print("\n[2/4] Parsing SEC historical CIK data...")

def normalize_name_aggressive(name):
    """
    Aggressive normalization: uppercase, remove punctuation, drop legal suffixes
    """
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

print(f"  Parsed: {len(sec_records):,} unique CIKs")
print(f"  Normalized names: {len(normalized_to_ciks):,}")

# ============================================================================
# STEP 3: Run exact matching on validation set
# ============================================================================
print("\n[3/4] Running exact matching...")

results = []

for idx, row in df_validation.iterrows():
    org_name = row['org_name']
    original_cik = row['cik']
    ticker = row['ticker']
    breach_date = row['breach_date']

    normalized = normalize_name_aggressive(org_name)

    # Exact match lookup
    if normalized in normalized_to_ciks:
        ciks_for_name = normalized_to_ciks[normalized]

        if len(ciks_for_name) == 1:
            # Unambiguous match
            matched_cik = list(ciks_for_name)[0]
            results.append({
                'org_name': org_name,
                'ticker': ticker,
                'breach_date': breach_date,
                'original_cik': original_cik,
                'matched_cik': matched_cik,
                'normalized_name': normalized,
                'match_type': 'EXACT_UNAMBIGUOUS',
                'cik_correct': matched_cik == original_cik,
                'notes': f'SEC name: {sec_records[matched_cik][0]}'
            })
        else:
            # Ambiguous: multiple CIKs
            sec_names = []
            for cik in sorted(ciks_for_name):
                sec_names.extend(sec_records[cik])

            results.append({
                'org_name': org_name,
                'ticker': ticker,
                'breach_date': breach_date,
                'original_cik': original_cik,
                'matched_cik': None,
                'normalized_name': normalized,
                'match_type': 'EXACT_AMBIGUOUS',
                'cik_correct': False,
                'notes': f'Multiple CIKs: {sorted(ciks_for_name)} ({len(sec_names)} SEC names)'
            })
    else:
        # No exact match
        results.append({
            'org_name': org_name,
            'ticker': ticker,
            'breach_date': breach_date,
            'original_cik': original_cik,
            'matched_cik': None,
            'normalized_name': normalized,
            'match_type': 'NO_MATCH',
            'cik_correct': False,
            'notes': 'Not found in SEC historical CIK data'
        })

df_results = pd.DataFrame(results)

# ============================================================================
# STEP 4: Report results
# ============================================================================
print("\n[4/4] Generating report...")

exact_unambiguous = df_results[df_results['match_type'] == 'EXACT_UNAMBIGUOUS']
exact_ambiguous = df_results[df_results['match_type'] == 'EXACT_AMBIGUOUS']
no_match = df_results[df_results['match_type'] == 'NO_MATCH']

print("\n" + "=" * 100)
print("EXACT MATCHING RESULTS")
print("=" * 100)

print(f"\nSummary:")
print(f"  Total validation records: {len(df_results)}")
print(f"  Exact unambiguous matches: {len(exact_unambiguous)} ({len(exact_unambiguous)/len(df_results)*100:.1f}%)")
print(f"  Exact ambiguous matches: {len(exact_ambiguous)} ({len(exact_ambiguous)/len(df_results)*100:.1f}%)")
print(f"  No match: {len(no_match)} ({len(no_match)/len(df_results)*100:.1f}%)")

print(f"\nCorrectness of original CIK assignments (for unambiguous matches):")
correct = len(exact_unambiguous[exact_unambiguous['cik_correct'] == True])
incorrect = len(exact_unambiguous[exact_unambiguous['cik_correct'] == False])
print(f"  Correct (matched CIK = original CIK): {correct}")
print(f"  Incorrect (mismatch): {incorrect}")

if incorrect > 0:
    print(f"\n  Mismatches found:")
    for _, row in exact_unambiguous[exact_unambiguous['cik_correct'] == False].iterrows():
        print(f"    {row['org_name'][:45]:45s} | original: {row['original_cik']:>10} | matched: {row['matched_cik']:>10}")

print(f"\nUnambiguous matches by category:")
telecom_exact = exact_unambiguous[exact_unambiguous['ticker'].isin(['TMUS', 'T', 'VZ', 'CMCSA', 'CHTR', 'DISH', 'FYBR', 'SIRI', 'LUMN', 'ATUS'])]
control_exact = exact_unambiguous[~exact_unambiguous['ticker'].isin(['TMUS', 'T', 'VZ', 'CMCSA', 'CHTR', 'DISH', 'FYBR', 'SIRI', 'LUMN', 'ATUS'])]

print(f"  Telecom (resolved): {len(telecom_exact)}")
for _, row in telecom_exact.iterrows():
    print(f"    {row['org_name'][:50]:50s} {row['ticker']:6s} -> CIK {row['matched_cik']}")

print(f"\n  Control firms (resolved): {len(control_exact)}")
for _, row in control_exact.iterrows():
    print(f"    {row['org_name'][:50]:50s} {row['ticker']:6s} -> CIK {row['matched_cik']}")

print(f"\nRemaining manual review:")
print(f"  Ambiguous (multiple CIKs): {len(exact_ambiguous)}")
for _, row in exact_ambiguous.iterrows():
    print(f"    {row['org_name'][:50]:50s} | {row['notes']}")

print(f"\n  Not found: {len(no_match)}")
for _, row in no_match.iterrows():
    print(f"    {row['org_name'][:50]:50s} | normalized: '{row['normalized_name']}'")

# Save detailed results
output_path = Path("outputs/exact_match_validation_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df_results.to_csv(output_path, index=False)

print(f"\n" + "=" * 100)
print(f"Detailed results saved: {output_path}")
print("=" * 100)
