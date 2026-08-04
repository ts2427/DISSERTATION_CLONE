import pandas as pd

df = pd.read_excel('Data/DataBreaches.xlsx', sheet_name=0)

# Check ticker-to-org_name-to-CIK mapping
print('Ticker-to-org_name-to-CIK mapping in original DataBreaches.xlsx:')
print('=' * 100)

for ticker in ['TMUS', 'T', 'INTU', 'UBER', 'INTC', 'ORCL']:
    subset = df[df['Map'] == ticker][['org_name', 'Map', 'cik']].drop_duplicates()
    if len(subset) > 0:
        print(f'\n{ticker}:')
        print(f'  Distinct org_names: {subset["org_name"].nunique()}')
        print(f'  Distinct CIKs: {subset["cik"].nunique()}')
        for _, row in subset.iterrows():
            print(f'    org_name={row["org_name"][:45]:45s} cik={row["cik"]:>10}')

# Summary
print('\n' + '=' * 100)
print('SUMMARY:')
print('=' * 100)
ticker_cik_consistency = df.groupby('Map').apply(
    lambda x: x['cik'].nunique()
).value_counts()

print('\nTickers per CIK mapping:')
print('  1:1 (correct): ', ticker_cik_consistency.get(1, 0), 'tickers')
print('  1:N (ambiguous):', sum(ticker_cik_consistency[ticker_cik_consistency.index > 1]))
