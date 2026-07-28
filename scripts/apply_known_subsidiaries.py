"""
Apply known public subsidiary relationships to validation set
Resolves major telecom subsidiary mappings without manual Ex-21 extraction
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("APPLY KNOWN SUBSIDIARY RELATIONSHIPS")
print("=" * 100)

# ============================================================================
# STEP 1: Load validation results and unmatched records
# ============================================================================
print("\n[1/3] Loading validation results...")

results_path = Path("outputs/exact_match_validation_results.csv")
df_results = pd.read_csv(results_path)

unmatched = df_results[df_results['match_type'] == 'NO_MATCH'].copy().reset_index(drop=True)
print(f"  Unmatched records: {len(unmatched)}")

# ============================================================================
# STEP 2: Define known subsidiary-to-parent mappings
# ============================================================================
print("\n[2/3] Applying known subsidiary relationships...")

# Known telecom subsidiary relationships (publicly documented, stable across our sample period)
known_subsidiaries = {
    'cricket wireless': {'parent_cik': 732717, 'parent_name': 'AT&T Inc.', 'source': 'Known subsidiary (Cricket Wireless LLC is AT&T)'},
    'at t services': {'parent_cik': 732717, 'parent_name': 'AT&T Inc.', 'source': 'Known subsidiary (AT&T Services is AT&T division)'},
    'boost mobile': {'parent_cik': 1001082, 'parent_name': 'DISH Network Corporation', 'source': 'Known subsidiary (Boost Mobile is DISH wireless brand)'},
    'sprint nextel': {'parent_cik': 1283699, 'parent_name': 'T-Mobile US, Inc.', 'source': 'Known predecessor (Sprint Nextel merged into T-Mobile 2020)'},
    'sprint': {'parent_cik': 1283699, 'parent_name': 'T-Mobile US, Inc.', 'source': 'Known predecessor (Sprint merged into T-Mobile 2020)'},
}

resolved_from_subsidiary = []
unresolved_after_subsidiary = []

for idx, row in unmatched.iterrows():
    org_name_lower = row['org_name'].lower().replace('inc.', '').replace('llc', '').strip()

    # Check if this matches a known subsidiary
    matched = False
    for subsidiary_pattern, parent_info in known_subsidiaries.items():
        if subsidiary_pattern in org_name_lower:
            resolved_from_subsidiary.append({
                'org_name': row['org_name'],
                'ticker': row['ticker'],
                'breach_date': row['breach_date'],
                'original_cik': row['original_cik'],
                'resolved_cik': parent_info['parent_cik'],
                'parent_name': parent_info['parent_name'],
                'match_type': 'SUBSIDIARY_RESOLUTION',
                'source': parent_info['source'],
                'notes': f'Resolved via known subsidiary relationship'
            })
            print(f"  ✓ {row['org_name'][:50]:50s} -> {parent_info['parent_name'][:30]}")
            matched = True
            break

    if not matched:
        unresolved_after_subsidiary.append(row)

print(f"\n  Resolved via subsidiaries: {len(resolved_from_subsidiary)}")
print(f"  Still unresolved: {len(unresolved_after_subsidiary)}")

# ============================================================================
# STEP 3: Combine all results (exact + subsidiary) and report
# ============================================================================
print("\n[3/3] Generating combined results...")

# Get exact matches
exact_matches = df_results[df_results['match_type'] == 'EXACT_UNAMBIGUOUS'].copy()
exact_matches['match_category'] = 'EXACT_MATCH'

# Format subsidiary matches to match exact match schema
df_subsidiary_resolved = pd.DataFrame(resolved_from_subsidiary)
df_subsidiary_resolved['normalized_name'] = df_subsidiary_resolved['org_name'].str.lower()
df_subsidiary_resolved['match_category'] = 'SUBSIDIARY_RESOLUTION'

# Combine
exact_cols = ['org_name', 'ticker', 'breach_date', 'original_cik', 'resolved_cik', 'match_type', 'source', 'notes', 'match_category']
subsidiary_cols = ['org_name', 'ticker', 'breach_date', 'original_cik', 'resolved_cik', 'match_type', 'source', 'notes', 'match_category']

df_combined = pd.concat([
    exact_matches[['org_name', 'ticker', 'breach_date', 'original_cik', 'matched_cik', 'match_type', 'notes']].rename(
        columns={'matched_cik': 'resolved_cik'}
    ).assign(source='Exact match on normalized name', match_category='EXACT_MATCH'),
    df_subsidiary_resolved[['org_name', 'ticker', 'breach_date', 'original_cik', 'resolved_cik', 'match_type', 'source', 'notes', 'match_category']]
], ignore_index=True)

# Save combined results
combined_output = Path("outputs/exact_and_subsidiary_matches.csv")
df_combined.to_csv(combined_output, index=False)

print(f"\n" + "=" * 100)
print("COMBINED RESULTS: EXACT MATCHING + KNOWN SUBSIDIARIES")
print("=" * 100)

total_validation = len(df_results)
exact = len(exact_matches)
subsidiary = len(df_subsidiary_resolved)
resolved = exact + subsidiary
unresolved = total_validation - resolved

print(f"\nResolution summary:")
print(f"  Exact matches: {exact} ({exact/total_validation*100:.1f}%)")
print(f"  Subsidiary matches: {subsidiary} ({subsidiary/total_validation*100:.1f}%)")
print(f"  Total resolved: {resolved} ({resolved/total_validation*100:.1f}%)")
print(f"  Unresolved: {unresolved} ({unresolved/total_validation*100:.1f}%)")

print(f"\nResolved by category:")
print(f"  Telecom: {len(df_combined[df_combined['ticker'].isin(['TMUS', 'T', 'VZ', 'CMCSA', 'CHTR', 'DISH', 'FYBR', 'SIRI', 'LUMN', 'ATUS'])])} / 15")
print(f"  Control/Other: {len(df_combined[~df_combined['ticker'].isin(['TMUS', 'T', 'VZ', 'CMCSA', 'CHTR', 'DISH', 'FYBR', 'SIRI', 'LUMN', 'ATUS'])])} / 19")

print(f"\nRemaining unresolved (for reasoning pass):")
unresolved_list = df_results[
    (df_results['match_type'] == 'NO_MATCH') &
    (~df_results['org_name'].isin(df_subsidiary_resolved['org_name'].unique()))
].copy()

for _, row in unresolved_list.iterrows():
    print(f"  {row['org_name'][:50]:50s} (ticker: {row['ticker']:6s})")

print(f"\n" + "=" * 100)
print(f"Output: {combined_output}")
print("=" * 100)
