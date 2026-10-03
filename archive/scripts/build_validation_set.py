"""
Build validation set: hand-resolve 40 records with known truth
These become the ground truth for scoring all subsequent matching steps
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("BUILD VALIDATION SET FOR CIK/PERMNO MATCHING")
print("=" * 100)

# Load original data
df = pd.read_excel('Data/DataBreaches.xlsx', sheet_name=0)
print(f"\nLoaded original DataBreaches.xlsx: {len(df)} records")

# ============================================================================
# Select validation set deliberately
# ============================================================================

validation_records = []

# 1. T-Mobile records (various subsidiary names under TMUS ticker)
tmus_records = df[df['Map'] == 'TMUS'].copy()
print(f"\nT-Mobile (TMUS): {len(tmus_records)} records")
print(f"  Distinct org_names: {tmus_records['org_name'].nunique()}")
# Take a diverse sample: T-Mobile US Inc, T-Mobile USA, Sprint Corporation, Sprint Nextel
for org_name in ['T-Mobile US, Inc.', 'T-Mobile USA, Inc.', 'Sprint Corporation', 'Sprint Nextel']:
    sample = tmus_records[tmus_records['org_name'] == org_name]
    if len(sample) > 0:
        validation_records.append(sample.iloc[0])
        print(f"  Selected: {org_name}")

# 2. AT&T records including Cricket Wireless (subsidiary)
t_records = df[df['Map'] == 'T'].copy()
print(f"\nAT&T (T): {len(t_records)} records")
print(f"  Distinct org_names: {t_records['org_name'].nunique()}")
# Take diverse sample: AT&T Inc, AT&T Services, Cricket Wireless
for org_name in ['AT&T Inc.', 'AT&T Services, Inc.', 'Cricket Wireless LLC']:
    sample = t_records[t_records['org_name'] == org_name]
    if len(sample) > 0:
        validation_records.append(sample.iloc[0])
        print(f"  Selected: {org_name}")

# 3. Verizon (major telecom)
vz_records = df[df['Map'] == 'VZ']
if len(vz_records) > 0:
    print(f"\nVerizon (VZ): {len(vz_records)} records")
    validation_records.append(vz_records.iloc[0])
    print(f"  Selected: {vz_records.iloc[0]['org_name']}")

# 4. Comcast (cable operator)
cmcsa_records = df[df['Map'] == 'CMCSA']
if len(cmcsa_records) > 0:
    print(f"\nComcast (CMCSA): {len(cmcsa_records)} records")
    validation_records.append(cmcsa_records.iloc[0])
    print(f"  Selected: {cmcsa_records.iloc[0]['org_name']}")

# 5. Charter Communications (cable operator)
chtr_records = df[df['Map'] == 'CHTR']
if len(chtr_records) > 0:
    print(f"\nCharter Communications (CHTR): {len(chtr_records)} records")
    validation_records.append(chtr_records.iloc[0])
    print(f"  Selected: {chtr_records.iloc[0]['org_name']}")

# 6. Cox Communications (cable, private — interesting edge case)
cox_records = df[df['org_name'].str.contains('Cox', case=False, na=False)]
if len(cox_records) > 0:
    print(f"\nCox Communications: {len(cox_records)} records")
    validation_records.append(cox_records.iloc[0])
    print(f"  Selected: {cox_records.iloc[0]['org_name']}")

# 7. Windstream (telecom)
ws_records = df[df['org_name'].str.contains('Windstream', case=False, na=False)]
if len(ws_records) > 0:
    print(f"\nWindstream: {len(ws_records)} records")
    validation_records.append(ws_records.iloc[0])
    print(f"  Selected: {ws_records.iloc[0]['org_name']}")

# 8. DISH Network (telecom/satellite)
dish_records = df[df['Map'] == 'DISH']
if len(dish_records) > 0:
    print(f"\nDISH Network (DISH): {len(dish_records)} records")
    validation_records.append(dish_records.iloc[0])
    print(f"  Selected: {dish_records.iloc[0]['org_name']}")

# 9. Ordinary control firms (non-telecom, unremarkable names)
control_tickers = [
    'INTU', 'UBER', 'ORCL', 'INTC', 'MSFT', 'AMZN', 'CSCO', 'NVDA',
    'ADBE', 'CRM', 'SNOW', 'OKTA', 'PNC', 'JPM', 'BAC', 'WFC',
    'AIG', 'DUK', 'NEE', 'D', 'SO', 'EXC', 'FIS', 'FISERV',
]

print(f"\nOrdinary control firms (tech, finance, utilities, non-telecom):")
for ticker in control_tickers:
    sample = df[df['Map'] == ticker]
    if len(sample) > 0:
        validation_records.append(sample.iloc[0])
        print(f"  Selected: {ticker} - {sample.iloc[0]['org_name']}")
    if len(validation_records) >= 40:
        break

# If still short, add some firms without clear tickers (edge cases)
if len(validation_records) < 40:
    print(f"\nAdding firms without clear tickers (edge cases):")
    # Add Nuance, Entercom, Sungard, Qwest, Level3, etc.
    for org_pattern in ['Nuance', 'Entercom', 'Sungard', 'Frontier', 'Level3', 'Qwest',
                        'Mediacom', 'Time Warner', 'Verizon Business', 'AT&T Mobility',
                        'T-Mobile Ventures', 'SiriusXM', 'Cox', 'Bandwidth', 'Vonage',
                        'Limelight', 'Zayo', 'Consolidated Communications']:
        sample = df[df['org_name'].str.contains(org_pattern, case=False, na=False)]
        if len(sample) > 0:
            validation_records.append(sample.iloc[0])
            print(f"  Selected: {sample.iloc[0]['org_name']}")
        if len(validation_records) >= 40:
            break

# Trim to exactly 40
validation_records = validation_records[:40]

# ============================================================================
# Export validation set
# ============================================================================

df_validation = pd.DataFrame(validation_records)[
    ['org_name', 'Map', 'cik', 'breach_date', 'sic', 'organization_type']
].reset_index(drop=True)

# Add blank columns for manual entry
df_validation['correct_cik'] = ''
df_validation['correct_permno'] = ''
df_validation['source'] = ''
df_validation['notes'] = ''

# Rename Map to ticker for clarity
df_validation = df_validation.rename(columns={'Map': 'ticker'})

# Reorder columns
df_validation = df_validation[[
    'org_name', 'ticker', 'cik', 'breach_date', 'sic',
    'correct_cik', 'correct_permno', 'source', 'notes'
]]

# Save
output_path = Path('Data/validation_set_40_records.csv')
df_validation.to_csv(output_path, index=False)

print("\n" + "=" * 100)
print(f"VALIDATION SET EXPORTED")
print("=" * 100)
print(f"\nFile: {output_path}")
print(f"Records: {len(df_validation)}")
print(f"\nColumns:")
print(f"  org_name: Original organization name from PRC")
print(f"  ticker: Stock ticker from original data")
print(f"  cik: CIK from original (likely incorrect for some)")
print(f"  breach_date: Breach date")
print(f"  sic: SIC code from original")
print(f"  correct_cik: [FILL IN] Correct CIK from SEC EDGAR")
print(f"  correct_permno: [FILL IN] Correct PERMNO from CRSP")
print(f"  source: [FILL IN] Where you verified (e.g., 'SEC EDGAR', 'CRSP', 'Company website')")
print(f"  notes: [FILL IN] Any relevant notes")

print(f"\nValidation set ready for manual verification:")
print(f"  1. Open the CSV in Excel")
print(f"  2. For each record, look up correct CIK via SEC EDGAR")
print(f"  3. Verify ticker matches in CRSP stocknames to get PERMNO")
print(f"  4. Fill in correct_cik, correct_permno, source, notes")
print(f"  5. Save the file")

print(f"\nThis validation set will score every subsequent matching step.")
print("=" * 100)
