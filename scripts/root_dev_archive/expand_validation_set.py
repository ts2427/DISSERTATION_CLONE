import pandas as pd

# Load current validation set
df_validation = pd.read_csv('Data/validation_set_40_records.csv')
print(f"Current validation set: {len(df_validation)} records")

# Load original data
df_original = pd.read_excel('Data/DataBreaches.xlsx', sheet_name=0)

# Add more records to reach 40
additional_orgs = [
    'Sirius',
    'CenturyLink',
    'US Cellular',
    'Level 3',
    'Vonage',
    'Bandwidth',
    'Altice',
    'Wave',
    'Sungard',
]

additional_records = []
for org_pattern in additional_orgs:
    sample = df_original[df_original['org_name'].str.contains(org_pattern, case=False, na=False)]
    if len(sample) > 0:
        additional_records.append(sample.iloc[0])
        print(f"  Adding: {sample.iloc[0]['org_name']}")
    if len(additional_records) >= 9:
        break

# Convert to same format
df_additional = pd.DataFrame(additional_records)[[
    'org_name', 'Map', 'cik', 'breach_date', 'sic'
]].reset_index(drop=True)

df_additional.columns = ['org_name', 'ticker', 'cik', 'breach_date', 'sic']
df_additional['correct_cik'] = ''
df_additional['correct_permno'] = ''
df_additional['source'] = ''
df_additional['notes'] = ''

# Combine
df_combined = pd.concat([df_validation[['org_name', 'ticker', 'cik', 'breach_date', 'sic', 'correct_cik', 'correct_permno', 'source', 'notes']],
                         df_additional], ignore_index=True)

print(f"\nCombined validation set: {len(df_combined)} records")

# Save
df_combined.to_csv('Data/validation_set_40_records.csv', index=False)
print(f"Saved: Data/validation_set_40_records.csv")
