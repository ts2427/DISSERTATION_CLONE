"""
Consolidate validation set results: exact + subsidiary + reasoning passes
"""

import pandas as pd
import json
from pathlib import Path

print("=" * 100)
print("CONSOLIDATE VALIDATION SET RESULTS")
print("=" * 100)

# Load all components
print("\nLoading results from all stages...")

# Exact + subsidiary matches
combined_path = Path("outputs/exact_and_subsidiary_matches.csv")
df_combined = pd.read_csv(combined_path)

# Reasoning pass results
reasoning_json_path = Path("C:/Users/mcobp/AppData/Local/Temp/claude/C--Users-mcobp-DISSERTATION-CLONE/a1bdce89-dcb5-4813-8e9d-168e93c18750/scratchpad/sec_cik_resolution.json")
with open(reasoning_json_path, 'r') as f:
    reasoning_results = json.load(f)

df_reasoning = pd.DataFrame(reasoning_results)

print(f"  Exact + Subsidiary matches: {len(df_combined)}")
print(f"  Reasoning pass results: {len(df_reasoning)}")

# ============================================================================
# Consolidate into unified results
# ============================================================================
print("\nConsolidating into unified validation results...")

# For exact/subsidiary: already have resolved_cik
exact_sub = df_combined[['org_name', 'ticker', 'breach_date', 'original_cik', 'resolved_cik', 'match_category']].copy()
exact_sub['final_cik'] = exact_sub['resolved_cik']
exact_sub['source'] = exact_sub['match_category'].apply(
    lambda x: 'Exact match on normalized name' if x == 'EXACT_MATCH' else 'Known subsidiary relationship'
)
exact_sub['confidence'] = 'HIGH'

# For reasoning: use correct_cik from agent
reasoning_resolved = df_reasoning[['org_name', 'correct_ticker', 'correct_cik', 'source', 'confidence']].copy()
reasoning_resolved = reasoning_resolved.rename(columns={
    'correct_ticker': 'ticker',
    'correct_cik': 'final_cik'
})

# Merge with validation for breach_date and original_cik
validation_path = Path("Data/validation_set_40_records.csv")
df_validation = pd.read_csv(validation_path)

reasoning_resolved = reasoning_resolved.merge(
    df_validation[['org_name', 'breach_date', 'cik']].rename(columns={'cik': 'original_cik'}),
    on='org_name',
    how='left'
)

reasoning_resolved['match_category'] = 'REASONING_RESOLUTION'

# Combine all
df_final = pd.concat([
    exact_sub[['org_name', 'ticker', 'breach_date', 'original_cik', 'final_cik', 'match_category', 'source', 'confidence']],
    reasoning_resolved[['org_name', 'ticker', 'breach_date', 'original_cik', 'final_cik', 'match_category', 'source', 'confidence']]
], ignore_index=True)

df_final = df_final.sort_values(['match_category', 'org_name']).reset_index(drop=True)

# Save consolidated results
output_path = Path("outputs/validation_set_complete_resolution.csv")
df_final.to_csv(output_path, index=False)

print(f"  Consolidated results saved: {output_path}")

# ============================================================================
# Summary Report
# ============================================================================
print("\n" + "=" * 100)
print("VALIDATION SET RESOLUTION SUMMARY")
print("=" * 100)

total_validation = 34
exact = len(df_final[df_final['match_category'] == 'EXACT_MATCH'])
subsidiary = len(df_final[df_final['match_category'] == 'SUBSIDIARY_RESOLUTION'])
reasoning = len(df_final[df_final['match_category'] == 'REASONING_RESOLUTION'])
resolved = exact + subsidiary + reasoning

print(f"\nResolution by method:")
print(f"  Exact matches:           {exact:2d} ({exact/total_validation*100:5.1f}%)")
print(f"  Subsidiary resolution:   {subsidiary:2d} ({subsidiary/total_validation*100:5.1f}%)")
print(f"  Reasoning resolution:    {reasoning:2d} ({reasoning/total_validation*100:5.1f}%)")
print(f"  TOTAL RESOLVED:          {resolved:2d} ({resolved/total_validation*100:5.1f}%)")

print(f"\nConfidence in final CIKs:")
high_conf = len(df_final[df_final['confidence'] == 'HIGH'])
medium_conf = len(df_final[df_final['confidence'] == 'MEDIUM'])
low_conf = len(df_final[df_final['confidence'] == 'LOW'])
null_cik = len(df_final[df_final['final_cik'].isna()])

print(f"  HIGH confidence:         {high_conf:2d} ({high_conf/total_validation*100:5.1f}%)")
print(f"  MEDIUM confidence:       {medium_conf:2d} ({medium_conf/total_validation*100:5.1f}%)")
print(f"  LOW confidence:          {low_conf:2d} ({low_conf/total_validation*100:5.1f}%)")
print(f"  NULL CIK (not found):    {null_cik:2d} ({null_cik/total_validation*100:5.1f}%)")

print(f"\nData quality issues detected:")
issues = df_final[
    (df_final['confidence'].isin(['MEDIUM', 'LOW'])) |
    (df_final['final_cik'].isna())
].copy()

print(f"  Records with issues:     {len(issues):2d}")

if len(issues) > 0:
    print(f"\n  Detailed issues:")
    for _, row in issues.iterrows():
        if pd.isna(row['final_cik']):
            reason = "NOT FOUND (private/nonprofit)"
        else:
            reason = row['source'][:60]
        print(f"    {row['org_name'][:45]:45s} | {row['confidence']:6s} | {reason}")

print(f"\n" + "=" * 100)
print("VALIDATION SET READY FOR CIK/PERMNO MAPPING")
print("=" * 100)

print(f"""
Next steps:
1. Review the consolidated results in {output_path}
2. For HIGH confidence CIKs: use directly in re-matching
3. For MEDIUM/LOW confidence: verify against CRSP stocknames
4. For NULL CIKs (private/nonprofit): flag as unmatched
5. Build final CIK-to-PERMNO mapping using CRSP date-aware matching
6. Score the exact matcher against validation set results
""")
