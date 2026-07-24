import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Check Boost Mobile
boost = df[df['org_name'] == 'Boost Mobile']
print('Boost Mobile current status:')
print(f'  Rows: {len(boost)}')
if len(boost) > 0:
    for _, row in boost.iterrows():
        print(f'  CIK: {row["cik"]}')
        print(f'  Breach date: {row["breach_date"]}')
        print(f'  FCC reportable: {row["fcc_reportable"]}')
else:
    print('  No Boost Mobile records found')
