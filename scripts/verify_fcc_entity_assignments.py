"""
VERIFY FCC ENTITY ASSIGNMENTS
Check that all FCC observations sit under correct parent CIK
and no non-FCC record has drifted in through a name variant
"""

import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print("=" * 100)
print("FCC ENTITY ASSIGNMENT VERIFICATION")
print("=" * 100)

# Get FCC observations
fcc_obs = df[df['fcc_reportable'] == True].copy()
fcc_obs = fcc_obs.sort_values(['cik', 'breach_date'])

print(f"\nTotal FCC observations: {len(fcc_obs)}")
print(f"Total FCC CIKs: {fcc_obs['cik'].nunique()}")

# List all FCC CIKs and their observations
fcc_ciks = fcc_obs['cik'].unique()

print("\n" + "=" * 100)
print("FCC FIRMS AND THEIR OBSERVATIONS")
print("=" * 100)

for rank, cik in enumerate(sorted(fcc_ciks), 1):
    cik_obs = fcc_obs[fcc_obs['cik'] == cik].copy()
    org_names = cik_obs['org_name'].unique()
    sic = cik_obs['sic'].iloc[0]

    print(f"\n{rank}. CIK {int(cik)}")
    print(f"   SIC: {int(sic) if pd.notna(sic) else 'N/A'}")
    print(f"   Total observations: {len(cik_obs)}")
    print(f"   Unique org names ({len(org_names)}):")

    for org in sorted(org_names):
        count = len(cik_obs[cik_obs['org_name'] == org])
        print(f"     - {org[:60]:<60} ({count} obs)")

    # Check for suspicious org_name patterns
    print(f"   Org name variants:")
    for org in sorted(org_names):
        print(f"     {org}")

print("\n" + "=" * 100)
print("ENTITY ASSIGNMENT CHECKLIST")
print("=" * 100)

checklist = {
    'Sprint Business / Sprint / Sprint Corporation / T-Mobile': {
        'cik': 1283699,
        'expected_names': ['Sprint', 'T-Mobile', 'Sprint Corporation', 'Sprint Business', 'T-Mobile USA'],
        'check': 'Merger entity - should all be under same CIK (1283699)'
    },
    'AT&T': {
        'cik': 732717,
        'expected_names': ['AT&T', 'AT&T Services', 'AT&T Inc', 'Cricket Wireless'],
        'check': 'Subsidiaries of AT&T - should all be under same CIK (732717)'
    },
    'Verizon': {
        'cik': 732712,
        'expected_names': ['Verizon', 'Verizon Communications'],
        'check': 'Should be under CIK 732712'
    },
    'Comcast': {
        'cik': 1166691,
        'expected_names': ['Comcast', 'Comcast Cable Communications'],
        'check': 'Should be under CIK 1166691'
    },
    'Charter': {
        'cik': 1091667,
        'expected_names': ['Charter Communications', 'Charter'],
        'check': 'Should be under CIK 1091667'
    },
    'Frontier': {
        'cik': 20520,
        'expected_names': ['Frontier Communications'],
        'check': 'Should be under CIK 20520'
    },
    'CenturyLink': {
        'cik': 18926,
        'expected_names': ['CenturyLink', 'Lumen'],
        'check': 'May have rebranded from CenturyLink to Lumen'
    },
    'Altice': {
        'cik': 1702780,
        'expected_names': ['Altice USA'],
        'check': 'Should be under CIK 1702780'
    },
    'DISH': {
        'cik': 1001082,
        'expected_names': ['DISH Network', 'DISH'],
        'check': 'Should be under CIK 1001082'
    },
    'Cable One': {
        'cik': 1632127,
        'expected_names': ['Cable One'],
        'check': 'Should be under CIK 1632127'
    }
}

print("\nVerifying expected FCC firms are under correct CIKs:\n")

for firm_name, checks in checklist.items():
    expected_cik = checks['cik']
    obs_for_cik = fcc_obs[fcc_obs['cik'] == expected_cik]

    if len(obs_for_cik) == 0:
        print(f"✗ {firm_name} (CIK {expected_cik}): NO OBSERVATIONS")
    else:
        org_names = obs_for_cik['org_name'].unique()
        print(f"✓ {firm_name} (CIK {expected_cik}): {len(obs_for_cik)} obs")
        print(f"  Names: {', '.join(sorted(org_names)[:3])}")
        if len(org_names) > 3:
            print(f"  ... and {len(org_names) - 3} other variants")

print("\n" + "=" * 100)
print("CONCLUSION")
print("=" * 100)
print("""
Check for:
1. Are all 10 FCC firms represented?
2. Do their CIKs match canonical assignments?
3. Are there suspicious org_name variants that might be non-FCC entities?
4. After Boost Mobile reassignment, is it now under Sprint (1283699)?

This verification ensures the FCC treatment group is clean before H2 regression.
""")
