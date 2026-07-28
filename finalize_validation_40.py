import pandas as pd

df_validation = pd.read_csv('Data/validation_set_40_records.csv')
df_original = pd.read_excel('Data/DataBreaches.xlsx', sheet_name=0)

print(f"Starting with: {len(df_validation)} records")

# Get distinct org_names already in validation set
validation_orgs = set(df_validation['org_name'].unique())

# Find additional records not yet included
additional_patterns = ['Limelight', 'Zayo', 'GTT', 'FirstEnergy', 'Exelon', 'NextEra', 'Berkshire', 'Lemonade']

for pattern in additional_patterns:
    if len(df_validation) >= 40:
        break
    sample = df_original[df_original['org_name'].str.contains(pattern, case=False, na=False)]
    sample = sample[~sample['org_name'].isin(validation_orgs)]
    if len(sample) > 0:
        rec = sample.iloc[0]
        new_row = pd.DataFrame([{
            'org_name': rec['org_name'],
            'ticker': rec['Map'],
            'cik': rec['cik'],
            'breach_date': rec['breach_date'],
            'sic': rec['sic'],
            'correct_cik': '',
            'correct_permno': '',
            'source': '',
            'notes': ''
        }])
        df_validation = pd.concat([df_validation, new_row], ignore_index=True)
        validation_orgs.add(rec['org_name'])
        print(f"  Added: {rec['org_name']}")

# Trim to exactly 40
df_validation = df_validation.iloc[:40]
df_validation.to_csv('Data/validation_set_40_records.csv', index=False)
print(f"\nFinal validation set: {len(df_validation)} records")
print(f"File: Data/validation_set_40_records.csv")
