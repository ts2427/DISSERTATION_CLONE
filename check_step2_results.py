import pandas as pd

# Load matched results
matched = pd.read_csv('Data/edgar/step2_matched_org_names.csv')
print('MATCHED RESULTS:')
print(f'  Total match rows: {len(matched)}')
print(f'  Unique org_names matched: {matched["org_name"].nunique()}')
print(f'  Exact matches: {len(matched[matched["match_type"] == "EXACT"])}')
print(f'  Fuzzy matches: {len(matched[matched["match_type"] == "FUZZY"])}')

# Show samples
print('\n  Sample exact matches:')
for idx, row in matched[matched['match_type'] == 'EXACT'].head(5).iterrows():
    print(f'    {row["org_name"][:50]:50s} -> CIK {row["cik"]} ({row["sec_company_name"][:40]})')

# Load unmatched
unmatched = pd.read_csv('Data/edgar/step2_manual_review_worksheet.csv')
print(f'\nUNMATCHED (MANUAL REVIEW):')
print(f'  Total org_names: {len(unmatched)}')
print(f'  Top 10 by best_score:')
for idx, row in unmatched.nlargest(10, 'best_score').iterrows():
    print(f'    {row["org_name"][:50]:50s} best_score={row["best_score"]:.3f}')

# Load PRC to check record counts
prc = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
print(f'\nRECORD COVERAGE:')
print(f'  Total PRC records: {len(prc)}')

# Count records from matched org_names
matched_org_names = set(matched['org_name'].unique())
matched_records = prc[prc['org_name'].isin(matched_org_names)]
print(f'  Records from matched org_names: {len(matched_records)} ({len(matched_records)/len(prc)*100:.1f}%)')

# Count records from unmatched org_names
unmatched_org_names = set(unmatched['org_name'].unique())
unmatched_records = prc[prc['org_name'].isin(unmatched_org_names)]
print(f'  Records from unmatched org_names: {len(unmatched_records)} ({len(unmatched_records)/len(prc)*100:.1f}%)')

# Summary
print(f'\n' + '='*80)
print('STEP 2 SUMMARY:')
print(f'  Automated CIK matching: {len(matched_org_names)}/{matched["org_name"].nunique()} org_names')
print(f'  Coverage: {(len(matched_org_names) / (len(matched_org_names) + len(unmatched_org_names)) * 100):.1f}%')
print(f'  Record coverage: {(len(matched_records) / len(prc) * 100):.1f}%')
print(f'  Manual review: {len(unmatched_org_names)} org_names, {len(unmatched_records)} records')
