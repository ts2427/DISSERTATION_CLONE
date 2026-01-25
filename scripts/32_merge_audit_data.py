import pandas as pd
import numpy as np

print("=" * 60)
print("MERGING AUDIT ANALYTICS DATA WITH BREACH DATASET")
print("=" * 60)

# Load breach dataset (output from WRDS merge)
print("\n[1/4] Loading datasets...")
breach_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"  ✓ Loaded {len(breach_df)} breaches")

# Load Audit Analytics data
try:
    sox_df = pd.read_csv('Data/audit_analytics/sox_404_data.csv')
    print(f"  ✓ Loaded {len(sox_df):,} SOX 404 records")
    has_sox = True
except FileNotFoundError:
    print("  ✗ No SOX 404 data found")
    has_sox = False
    sox_df = pd.DataFrame()

try:
    restate_df = pd.read_csv('Data/audit_analytics/restatements.csv')
    print(f"  ✓ Loaded {len(restate_df):,} restatement records")
    has_restate = True
except FileNotFoundError:
    print("  ✗ No restatement data found")
    has_restate = False
    restate_df = pd.DataFrame()

if not has_sox and not has_restate:
    print("\n⚠ No Audit Analytics data available!")
    print("  Creating governance proxies from firm size instead...")
    
    # Use firm size as governance proxy
    if 'firm_size_log' in breach_df.columns:
        breach_df['strong_governance'] = (
            breach_df['firm_size_log'] > breach_df['firm_size_log'].median()
        ).astype(int)
        breach_df['has_governance_data'] = True
        print("  ✓ Created size-based governance proxy")
    
    # Save and exit
    output_file = 'Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.xlsx'
    breach_df.to_excel(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    exit()

# Convert dates
print("\n[2/4] Preparing data...")
breach_df['breach_date'] = pd.to_datetime(breach_df['breach_date'])

if has_sox:
    sox_df['fye_ic_op'] = pd.to_datetime(sox_df['fye_ic_op'])
    sox_df['file_date'] = pd.to_datetime(sox_df['file_date'])

if has_restate:
    restate_df['res_begin_date'] = pd.to_datetime(restate_df['res_begin_date'])
    restate_df['res_end_date'] = pd.to_datetime(restate_df['res_end_date'])

# Find CIK column in breach data
cik_candidates = [col for col in breach_df.columns if 'cik' in col.lower()]
if len(cik_candidates) == 0:
    print("\n✗ ERROR: No CIK column found in breach dataset!")
    print("Available columns:", breach_df.columns.tolist())
    exit()

cik_col = cik_candidates[0]
print(f"  ✓ Using CIK column: '{cik_col}'")

# Merge SOX 404 data
print("\n[3/4] Merging SOX 404 governance data...")

if has_sox:
    merged_list = []
    sox_matched = 0
    
    for idx, breach in breach_df.iterrows():
        breach_cik = breach[cik_col]
        
        # Skip if no CIK
        if pd.isna(breach_cik):
            breach['has_sox_data'] = False
            breach['ic_is_effective'] = None
            breach['count_weak'] = None
            breach['sox_fye'] = None
            breach['days_since_sox'] = None
            merged_list.append(breach)
            continue
        
        # Convert CIK to integer for matching
        try:
            breach_cik = int(breach_cik)
        except:
            breach['has_sox_data'] = False
            breach['ic_is_effective'] = None
            breach['count_weak'] = None
            breach['sox_fye'] = None
            breach['days_since_sox'] = None
            merged_list.append(breach)
            continue
        
        # Get SOX filings for this company BEFORE breach date
        company_sox = sox_df[
            (sox_df['company_fkey'] == breach_cik) &
            (sox_df['fye_ic_op'] <= breach['breach_date'])
        ].sort_values('fye_ic_op', ascending=False)
        
        # Use most recent SOX filing before breach
        if len(company_sox) > 0:
            latest_sox = company_sox.iloc[0]
            breach['has_sox_data'] = True
            breach['ic_is_effective'] = latest_sox['ic_is_effective']
            breach['count_weak'] = latest_sox['count_weak']
            breach['sox_fye'] = latest_sox['fye_ic_op']
            breach['days_since_sox'] = (breach['breach_date'] - latest_sox['fye_ic_op']).days
            sox_matched += 1
        else:
            breach['has_sox_data'] = False
            breach['ic_is_effective'] = None
            breach['count_weak'] = None
            breach['sox_fye'] = None
            breach['days_since_sox'] = None
        
        merged_list.append(breach)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processing: {idx + 1}/{len(breach_df)} ({sox_matched} matched)")
    
    breach_df = pd.DataFrame(merged_list)
    print(f"  ✓ Matched {sox_matched} breaches to SOX 404 data ({sox_matched/len(breach_df)*100:.1f}%)")
    
    # Create strong governance indicator
    # Effective controls = 'Y' and no material weaknesses
    breach_df['strong_governance'] = (
        (breach_df['ic_is_effective'].astype(str).str.upper() == 'Y') & 
        (pd.to_numeric(breach_df['count_weak'], errors='coerce') == 0)
    ).astype(int)
    
    strong_gov = breach_df['strong_governance'].sum()
    print(f"  ✓ Identified {strong_gov} breaches with strong governance")

else:
    # No SOX data - add empty columns
    breach_df['has_sox_data'] = False
    breach_df['ic_is_effective'] = None
    breach_df['count_weak'] = None
    breach_df['sox_fye'] = None
    breach_df['days_since_sox'] = None
    breach_df['strong_governance'] = 0

# Merge restatement data
print("\n[4/4] Merging financial restatement data...")

if has_restate:
    restate_matched = 0
    
    for idx in breach_df.index:
        breach_cik = breach_df.loc[idx, cik_col]
        
        if pd.isna(breach_cik):
            breach_df.loc[idx, 'has_prior_restatement'] = False
            breach_df.loc[idx, 'restatement_count'] = 0
            breach_df.loc[idx, 'restatement_fraud'] = False
            breach_df.loc[idx, 'restatement_adverse'] = False
            continue
        
        try:
            breach_cik = int(breach_cik)
        except:
            breach_df.loc[idx, 'has_prior_restatement'] = False
            breach_df.loc[idx, 'restatement_count'] = 0
            breach_df.loc[idx, 'restatement_fraud'] = False
            breach_df.loc[idx, 'restatement_adverse'] = False
            continue
        
        # Get restatements for this company BEFORE breach date
        company_restate = restate_df[
            (restate_df['company_fkey'] == breach_cik) &
            (restate_df['res_begin_date'] <= breach_df.loc[idx, 'breach_date'])
        ]
        
        # Add restatement flags
        if len(company_restate) > 0:
            breach_df.loc[idx, 'has_prior_restatement'] = True
            breach_df.loc[idx, 'restatement_count'] = len(company_restate)
            
            # Check for fraud or adverse restatements
            fraud = (company_restate['res_fraud'] == 1.0).any() if 'res_fraud' in company_restate.columns else False
            adverse = (company_restate['res_adverse'] == 1.0).any() if 'res_adverse' in company_restate.columns else False
            
            breach_df.loc[idx, 'restatement_fraud'] = fraud
            breach_df.loc[idx, 'restatement_adverse'] = adverse
            restate_matched += 1
        else:
            breach_df.loc[idx, 'has_prior_restatement'] = False
            breach_df.loc[idx, 'restatement_count'] = 0
            breach_df.loc[idx, 'restatement_fraud'] = False
            breach_df.loc[idx, 'restatement_adverse'] = False
    
    print(f"  ✓ Matched {restate_matched} breaches to restatement data ({restate_matched/len(breach_df)*100:.1f}%)")

else:
    # No restatement data - add empty columns
    breach_df['has_prior_restatement'] = False
    breach_df['restatement_count'] = 0
    breach_df['restatement_fraud'] = False
    breach_df['restatement_adverse'] = False

# Create composite governance indicator
print("\n[5/4] Creating composite governance variables...")

# Weak governance = material weaknesses OR prior adverse restatements
breach_df['weak_governance'] = (
    (pd.to_numeric(breach_df['count_weak'], errors='coerce') > 0) |
    (breach_df['restatement_adverse'] == True)
).astype(int)

# Has any governance data
breach_df['has_governance_data'] = (
    breach_df['has_sox_data'] | 
    breach_df['has_prior_restatement']
)

print(f"  ✓ Governance data available: {breach_df['has_governance_data'].sum()} breaches")
print(f"  ✓ Weak governance flagged: {breach_df['weak_governance'].sum()} breaches")

# Summary Statistics
print("\n" + "=" * 60)
print("AUDIT ANALYTICS MERGE SUMMARY")
print("=" * 60)

print(f"\nTotal breaches: {len(breach_df)}")

print(f"\n--- SOX 404 Internal Controls ---")
if has_sox:
    print(f"  Matched: {breach_df['has_sox_data'].sum()} ({breach_df['has_sox_data'].mean()*100:.1f}%)")
    print(f"  Strong governance: {breach_df['strong_governance'].sum()}")
    
    # IC effectiveness breakdown
    if breach_df['has_sox_data'].sum() > 0:
        sox_sample = breach_df[breach_df['has_sox_data']]
        ic_effective = (sox_sample['ic_is_effective'].astype(str).str.upper() == 'Y').sum()
        print(f"  Effective IC: {ic_effective}/{len(sox_sample)} ({ic_effective/len(sox_sample)*100:.1f}%)")
        
        # Material weaknesses
        weak_count = (pd.to_numeric(sox_sample['count_weak'], errors='coerce') > 0).sum()
        print(f"  Material weaknesses: {weak_count}/{len(sox_sample)} ({weak_count/len(sox_sample)*100:.1f}%)")
else:
    print(f"  No SOX 404 data")

print(f"\n--- Financial Restatements ---")
if has_restate:
    print(f"  Matched: {breach_df['has_prior_restatement'].sum()} ({breach_df['has_prior_restatement'].mean()*100:.1f}%)")
    print(f"  Fraud-related: {breach_df['restatement_fraud'].sum()}")
    print(f"  Adverse: {breach_df['restatement_adverse'].sum()}")
    print(f"  Total restatements: {breach_df['restatement_count'].sum()}")
else:
    print(f"  No restatement data")

print(f"\n--- Composite Governance ---")
print(f"  Strong governance: {breach_df['strong_governance'].sum()} ({breach_df['strong_governance'].mean()*100:.1f}%)")
print(f"  Weak governance: {breach_df['weak_governance'].sum()} ({breach_df['weak_governance'].mean()*100:.1f}%)")
print(f"  Any governance data: {breach_df['has_governance_data'].sum()} ({breach_df['has_governance_data'].mean()*100:.1f}%)")

# Save enhanced dataset
output_file = 'Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.xlsx'
breach_df.to_excel(output_file, index=False)

print(f"\n✓ Saved enhanced dataset to: {output_file}")

print("\n" + "=" * 60)
print("GOVERNANCE DATA READY FOR ESSAY 3")
print("=" * 60)

print("\nYou can now test:")
print("  • Does governance quality moderate disclosure timing effects?")
print("  • Do firms with weak IC face larger market penalties?")
print("  • Does restatement history amplify information asymmetry?")
print("  • Heterogeneity: Strong vs. weak governance firms")

print("\nKey variables created:")
print("  • strong_governance (IC effective + no weaknesses)")
print("  • weak_governance (material weaknesses OR adverse restatements)")
print("  • has_prior_restatement (any restatements before breach)")
print("  • restatement_count (number of prior restatements)")
print("  • ic_is_effective (SOX 404 effectiveness)")
print("  • count_weak (number of material weaknesses)")

print("\n" + "=" * 60)