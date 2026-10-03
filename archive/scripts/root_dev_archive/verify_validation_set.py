import pandas as pd

df = pd.read_csv('Data/validation_set_40_records.csv')

print('VALIDATION SET: 34 RECORDS')
print('='*80)

telecom = df[df['sic'].astype(str).str.startswith('48')]
print(f'\nTelecom (SIC 48xx): {len(telecom)}')
for _, row in telecom.iterrows():
    print(f'  {row["org_name"][:50]:50s} ticker={row["ticker"]:6s}')

control = df[~df['sic'].astype(str).str.startswith('48')]
print(f'\nControl/Other (non-48xx): {len(control)}')
for _, row in control.iterrows():
    print(f'  {row["org_name"][:50]:50s} sic={row["sic"]:>5} ticker={row["ticker"]:6s}')

print(f'\nKEY COVERAGE:')
print(f'  T-Mobile (TMUS): {len(df[df["ticker"] == "TMUS"])} records')
print(f'  AT&T (T): {len(df[df["ticker"] == "T"])} records')
print(f'  Verizon (VZ): {len(df[df["ticker"] == "VZ"])} records')
print(f'  Comcast (CMCSA): {len(df[df["ticker"] == "CMCSA"])} records')
print(f'  Charter (CHTR): {len(df[df["ticker"] == "CHTR"])} records')
print(f'  DISH: {len(df[df["ticker"] == "DISH"])} records')
print(f'  Other: {len(df[~df["ticker"].isin(["TMUS", "T", "VZ", "CMCSA", "CHTR", "DISH"])])} records')
