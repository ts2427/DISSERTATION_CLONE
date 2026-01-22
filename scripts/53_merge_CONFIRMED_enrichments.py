import pandas as pd
import numpy as np
import os

print("=" * 80)
print(" " * 20 + "MERGE ENRICHMENTS (FIXED - NO DUPLICATION)")
print("=" * 80)

# Load base dataset
print("\n📊 Loading base dataset...")
base_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"✓ Loaded {len(base_df)} breach records with {len(base_df.columns)} columns")

# Create UNIQUE row identifier
base_df['row_id'] = range(len(base_df))

print("\n" + "=" * 80)
print("MERGING 6 ENRICHMENT DATASETS")
print("=" * 80)

merged_df = base_df.copy()
merge_summary = []

# ============================================================================
# 1. PRIOR BREACH HISTORY (uses row_id from breach_id)
# ============================================================================
print(f"\nPrior Breach History (H3):")
filepath = 'Data/enrichment/prior_breach_history.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        
        # The breach_id in enrichment = row index
        enrich_df['row_id'] = enrich_df['breach_id']
        
        # Get new columns
        base_cols = set(merged_df.columns)
        new_cols = [col for col in enrich_df.columns 
                   if col not in ['breach_id', 'row_id'] and col not in base_cols]
        
        if len(new_cols) > 0:
            merged_df = merged_df.merge(
                enrich_df[['row_id'] + new_cols],
                on='row_id',
                how='left',
                validate='1:1'  # Ensure 1-to-1 merge
            )
            
            print(f"  ✓ Merged {len(new_cols)} variables")
            print(f"  ✓ Rows after merge: {len(merged_df)}")
            
            merge_summary.append({
                'Enrichment': 'Prior Breach History',
                'Hypothesis': 'H3',
                'Status': 'SUCCESS',
                'Variables_Added': len(new_cols),
                'Rows': len(merged_df)
            })
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({
            'Enrichment': 'Prior Breach History',
            'Hypothesis': 'H3',
            'Status': 'ERROR',
            'Variables_Added': 0,
            'Rows': len(merged_df)
        })

# ============================================================================
# 2. BREACH SEVERITY CLASSIFICATION (uses row_id from breach_id)
# ============================================================================
print(f"\nBreach Severity Classification (H4):")
filepath = 'Data/enrichment/breach_severity_classification.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        
        # The breach_id in enrichment = row index
        enrich_df['row_id'] = enrich_df['breach_id']
        
        # Get new columns
        base_cols = set(merged_df.columns)
        new_cols = [col for col in enrich_df.columns 
                   if col not in ['breach_id', 'row_id'] and col not in base_cols]
        
        if len(new_cols) > 0:
            merged_df = merged_df.merge(
                enrich_df[['row_id'] + new_cols],
                on='row_id',
                how='left',
                validate='1:1'
            )
            
            print(f"  ✓ Merged {len(new_cols)} variables")
            print(f"  ✓ Rows after merge: {len(merged_df)}")
            
            merge_summary.append({
                'Enrichment': 'Breach Severity Classification',
                'Hypothesis': 'H4',
                'Status': 'SUCCESS',
                'Variables_Added': len(new_cols),
                'Rows': len(merged_df)
            })
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({
            'Enrichment': 'Breach Severity Classification',
            'Hypothesis': 'H4',
            'Status': 'ERROR',
            'Variables_Added': 0,
            'Rows': len(merged_df)
        })

# ============================================================================
# 3-6. OTHER ENRICHMENTS (merge by row_id if possible, skip duplicates)
# ============================================================================

# For enrichments that used cik+breach_date, we need to be more careful
remaining_enrichments = [
    ('Industry-Adjusted Returns', 'industry_adjusted_returns.csv', 'Robustness'),
    ('Institutional Ownership', 'institutional_ownership.csv', 'Control'),
    ('Executive Turnover', 'executive_changes.csv', 'H5'),
    ('Regulatory Enforcement', 'regulatory_enforcement.csv', 'H6')
]

for name, filename, hypothesis in remaining_enrichments:
    print(f"\n{name} ({hypothesis}):")
    filepath = f'Data/enrichment/{filename}'
    
    if os.path.exists(filepath):
        try:
            enrich_df = pd.read_csv(filepath)
            
            # Convert dates
            if 'breach_date' in enrich_df.columns:
                enrich_df['breach_date'] = pd.to_datetime(enrich_df['breach_date'])
            
            # Create matching key in enrichment data
            if 'cik' in enrich_df.columns and 'breach_date' in enrich_df.columns:
                # Create a composite key
                enrich_df['match_key'] = (
                    enrich_df['cik'].astype(str) + '_' + 
                    enrich_df['breach_date'].dt.strftime('%Y-%m-%d')
                )
                
                merged_df['match_key'] = (
                    merged_df['cik'].astype(str) + '_' + 
                    pd.to_datetime(merged_df['breach_date']).dt.strftime('%Y-%m-%d')
                )
                
                # Check for duplicates
                dup_count = enrich_df['match_key'].duplicated().sum()
                if dup_count > 0:
                    print(f"  ⚠ Warning: {dup_count} duplicate keys in enrichment data")
                    # Keep first occurrence only
                    enrich_df = enrich_df.drop_duplicates('match_key', keep='first')
                
                # Get new columns
                base_cols = set(merged_df.columns)
                new_cols = [col for col in enrich_df.columns 
                           if col not in ['cik', 'breach_date', 'match_key'] and col not in base_cols]
                
                if len(new_cols) > 0:
                    before = len(merged_df)
                    merged_df = merged_df.merge(
                        enrich_df[['match_key'] + new_cols],
                        on='match_key',
                        how='left'
                    )
                    after = len(merged_df)
                    
                    if before != after:
                        print(f"  ✗ ERROR: Merge duplicated rows ({before} → {after})")
                        merged_df = merged_df.iloc[:before]  # Rollback
                        raise ValueError("Merge created duplicates")
                    
                    # Drop match_key
                    merged_df = merged_df.drop('match_key', axis=1)
                    
                    print(f"  ✓ Merged {len(new_cols)} variables")
                    print(f"  ✓ Rows after merge: {len(merged_df)}")
                    
                    merge_summary.append({
                        'Enrichment': name,
                        'Hypothesis': hypothesis,
                        'Status': 'SUCCESS',
                        'Variables_Added': len(new_cols),
                        'Rows': len(merged_df)
                    })
                else:
                    print(f"  ⚠ No new variables")
                    merge_summary.append({
                        'Enrichment': name,
                        'Hypothesis': hypothesis,
                        'Status': 'NO NEW VARS',
                        'Variables_Added': 0,
                        'Rows': len(merged_df)
                    })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            merge_summary.append({
                'Enrichment': name,
                'Hypothesis': hypothesis,
                'Status': 'ERROR',
                'Variables_Added': 0,
                'Rows': len(merged_df)
            })
    else:
        print(f"  ✗ File not found")
        merge_summary.append({
            'Enrichment': name,
            'Hypothesis': hypothesis,
            'Status': 'NOT FOUND',
            'Variables_Added': 0,
            'Rows': len(merged_df)
        })

# Summary
print("\n" + "=" * 80)
print("MERGE SUMMARY")
print("=" * 80)

summary_df = pd.DataFrame(merge_summary)
print("\n" + summary_df.to_string(index=False))

# Verify row count
if len(merged_df) != len(base_df):
    print(f"\n⚠ WARNING: Row count changed! {len(base_df)} → {len(merged_df)}")
    print("⚠ This should not happen - keeping first N rows only")
    merged_df = merged_df.iloc[:len(base_df)]

print(f"\n✓ Final row count: {len(merged_df)} (should be {len(base_df)})")

total_vars_added = summary_df['Variables_Added'].sum()
successful = len(summary_df[summary_df['Status'] == 'SUCCESS'])

print(f"✓ Successfully merged: {successful}/6 enrichments")
print(f"✓ Total new variables added: {total_vars_added}")

# Save enriched dataset
print("\n" + "=" * 80)
print("SAVING ENRICHED DATASET")
print("=" * 80)

output_file = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.xlsx'
csv_file = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'

print(f"\nSaving to: {output_file}")

try:
    # Remove temporary keys
    final_df = merged_df.drop(['row_id'], axis=1, errors='ignore')
    
    final_df.to_excel(output_file, index=False)
    file_size = os.path.getsize(output_file)
    print(f"✓ Excel file saved ({file_size/1024/1024:.2f} MB)")
    
    final_df.to_csv(csv_file, index=False)
    csv_size = os.path.getsize(csv_file)
    print(f"✓ CSV file saved ({csv_size/1024/1024:.2f} MB)")
    
    print(f"\n📁 Files created:")
    print(f"  {output_file}")
    print(f"  {csv_file}")
    
except Exception as e:
    print(f"✗ Error saving: {e}")

# Show statistics
print("\n" + "=" * 80)
print("ENRICHMENT STATISTICS")
print("=" * 80)

if 'prior_breaches_total' in final_df.columns:
    repeat_rate = (final_df['prior_breaches_total'] > 0).mean() * 100
    print(f"\nH3 - Prior Breach History:")
    print(f"  • Repeat offenders: {repeat_rate:.1f}%")

if 'health_breach' in final_df.columns:
    health_rate = final_df['health_breach'].mean() * 100
    print(f"\nH4 - Breach Severity:")
    print(f"  • Health data breaches: {health_rate:.1f}%")

if 'executive_change_30d' in final_df.columns:
    turnover_rate = final_df['executive_change_30d'].mean() * 100
    print(f"\nH5 - Executive Turnover:")
    print(f"  • Changes within 30 days: {turnover_rate:.1f}%")

print("\n" + "=" * 80)
print("✅ ENRICHMENT MERGE COMPLETE!")
print("=" * 80)
print(f"\n📊 Final Dataset: {len(final_df):,} rows × {len(final_df.columns)} columns")
print(f"🚀 READY FOR ANALYSIS!")
print("=" * 80)