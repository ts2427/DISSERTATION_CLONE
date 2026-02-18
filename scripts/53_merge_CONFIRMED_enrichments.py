import pandas as pd
import numpy as np
import os

print("=" * 80)
print(" " * 20 + "MERGE ALL ENRICHMENTS - FINAL")
print("=" * 80)

# Load base dataset
print("\n📊 Loading base dataset...")
base_df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"✓ Loaded {len(base_df)} breach records with {len(base_df.columns)} columns")

# Create UNIQUE row identifier
base_df['row_id'] = range(len(base_df))

print("\n" + "=" * 80)
print("AVAILABLE ENRICHMENTS")
print("=" * 80)

# Check what enrichment files actually exist
enrichment_dir = 'Data/enrichment'
if os.path.exists(enrichment_dir):
    available_files = os.listdir(enrichment_dir)
    print(f"\nFound {len(available_files)} files in Data/enrichment/:")
    for f in sorted(available_files):
        if f.endswith('.csv'):
            print(f"  • {f}")
else:
    print("\n⚠ Enrichment directory not found!")
    exit()

print("\n" + "=" * 80)
print("MERGING ENRICHMENTS")
print("=" * 80)

merged_df = base_df.copy()
merge_summary = []

# ============================================================================
# 1. PRIOR BREACH HISTORY (H3)
# ============================================================================
print(f"\n1. Prior Breach History (H3):")
filepath = 'Data/enrichment/prior_breach_history.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        enrich_df['row_id'] = enrich_df['breach_id']
        
        base_cols = set(merged_df.columns)
        new_cols = [col for col in enrich_df.columns 
                   if col not in ['breach_id', 'row_id', 'org_name', 'breach_date'] 
                   and col not in base_cols]
        
        if len(new_cols) > 0:
            merged_df = merged_df.merge(
                enrich_df[['row_id'] + new_cols],
                on='row_id',
                how='left',
                validate='1:1'
            )
            
            print(f"  ✓ Merged {len(new_cols)} variables: {', '.join(new_cols[:3])}...")
            print(f"  ✓ Rows: {len(merged_df)} (no change)")
            
            merge_summary.append({
                'Enrichment': 'Prior Breach History',
                'Hypothesis': 'H3',
                'Status': 'SUCCESS',
                'Variables': len(new_cols),
                'Key_Vars': 'prior_breaches_total, days_since_last_breach'
            })
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({'Enrichment': 'Prior Breach History', 'Status': 'ERROR'})
else:
    print(f"  ✗ File not found")
    merge_summary.append({'Enrichment': 'Prior Breach History', 'Status': 'NOT FOUND'})

# ============================================================================
# 2. BREACH SEVERITY CLASSIFICATION (H4)
# ============================================================================
print(f"\n2. Breach Severity Classification (H4):")
filepath = 'Data/enrichment/breach_severity_classification.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        enrich_df['row_id'] = enrich_df['breach_id']
        
        base_cols = set(merged_df.columns)
        new_cols = [col for col in enrich_df.columns 
                   if col not in ['breach_id', 'row_id', 'org_name', 'breach_date'] 
                   and col not in base_cols]
        
        if len(new_cols) > 0:
            merged_df = merged_df.merge(
                enrich_df[['row_id'] + new_cols],
                on='row_id',
                how='left',
                validate='1:1'
            )
            
            print(f"  ✓ Merged {len(new_cols)} variables: {', '.join(new_cols[:3])}...")
            print(f"  ✓ Rows: {len(merged_df)} (no change)")
            
            merge_summary.append({
                'Enrichment': 'Breach Severity',
                'Hypothesis': 'H4',
                'Status': 'SUCCESS',
                'Variables': len(new_cols),
                'Key_Vars': 'health_breach, financial_breach, severity_score'
            })
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({'Enrichment': 'Breach Severity', 'Status': 'ERROR'})
else:
    print(f"  ✗ File not found")
    merge_summary.append({'Enrichment': 'Breach Severity', 'Status': 'NOT FOUND'})

# ============================================================================
# 3. MEDIA COVERAGE (NEW!)
# ============================================================================
print(f"\n3. Media Coverage (Heterogeneity Test):")
filepath = 'Data/enrichment/media_coverage.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        enrich_df['row_id'] = enrich_df['breach_id']
        
        base_cols = set(merged_df.columns)
        new_cols = [col for col in enrich_df.columns 
                   if col not in ['breach_id', 'row_id', 'org_name', 'breach_date'] 
                   and col not in base_cols]
        
        if len(new_cols) > 0:
            merged_df = merged_df.merge(
                enrich_df[['row_id'] + new_cols],
                on='row_id',
                how='left',
                validate='1:1'
            )
            
            print(f"  ✓ Merged {len(new_cols)} variables: {', '.join(new_cols[:3])}...")
            print(f"  ✓ Rows: {len(merged_df)} (no change)")
            
            # Show coverage stats
            coverage_rate = merged_df['has_media_coverage'].mean() * 100
            print(f"  📰 Coverage rate: {coverage_rate:.1f}%")
            
            merge_summary.append({
                'Enrichment': 'Media Coverage',
                'Hypothesis': 'Heterogeneity',
                'Status': 'SUCCESS',
                'Variables': len(new_cols),
                'Key_Vars': 'media_coverage_count, high_media_coverage'
            })
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({'Enrichment': 'Media Coverage', 'Status': 'ERROR'})
else:
    print(f"  ✗ File not found")
    merge_summary.append({'Enrichment': 'Media Coverage', 'Status': 'NOT FOUND'})

# ============================================================================
# 4. EXECUTIVE TURNOVER (H5) - FIXED VERSION
# ============================================================================
print(f"\n4. Executive Turnover (H5):")
filepath = 'Data/enrichment/executive_changes.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        
        # Check if breach_id exists
        if 'breach_id' in enrich_df.columns:
            enrich_df['row_id'] = enrich_df['breach_id']
            
            base_cols = set(merged_df.columns)
            new_cols = [col for col in enrich_df.columns 
                       if col not in ['breach_id', 'row_id', 'cik', 'org_name', 'breach_date'] 
                       and col not in base_cols]
            
            if len(new_cols) > 0:
                before = len(merged_df)
                merged_df = merged_df.merge(
                    enrich_df[['row_id'] + new_cols],
                    on='row_id',
                    how='left',
                    validate='1:1'
                )
                
                if len(merged_df) == before:
                    print(f"  ✓ Merged {len(new_cols)} variables: {', '.join(new_cols[:3])}...")
                    print(f"  ✓ Rows: {len(merged_df)} (no change)")
                    
                    # Show turnover rate
                    if 'executive_change_30d' in merged_df.columns:
                        rate_30d = merged_df['executive_change_30d'].mean() * 100
                        print(f"  📊 30-day turnover rate: {rate_30d:.1f}%")
                    
                    merge_summary.append({
                        'Enrichment': 'Executive Turnover',
                        'Hypothesis': 'H5',
                        'Status': 'SUCCESS',
                        'Variables': len(new_cols),
                        'Key_Vars': 'executive_change_30d, executive_change_90d'
                    })
                else:
                    print(f"  ✗ Merge created duplicates ({before} → {len(merged_df)})")
                    merged_df = merged_df.iloc[:before]
                    merge_summary.append({'Enrichment': 'Executive Turnover', 'Status': 'ERROR - duplicates'})
            else:
                print(f"  ⚠ No new variables to merge")
                merge_summary.append({'Enrichment': 'Executive Turnover', 'Status': 'NO NEW VARS'})
        else:
            print(f"  ✗ No breach_id column found")
            merge_summary.append({'Enrichment': 'Executive Turnover', 'Status': 'ERROR - no breach_id'})
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({'Enrichment': 'Executive Turnover', 'Status': f'ERROR: {str(e)[:50]}'})
else:
    print(f"  ✗ File not found")
    merge_summary.append({'Enrichment': 'Executive Turnover', 'Status': 'NOT FOUND'})

# ============================================================================
# 5. REGULATORY ENFORCEMENT (H6) - FIXED VERSION
# ============================================================================
print(f"\n5. Regulatory Enforcement (H6):")
filepath = 'Data/enrichment/regulatory_enforcement.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        
        # Check if breach_id exists
        if 'breach_id' in enrich_df.columns:
            enrich_df['row_id'] = enrich_df['breach_id']
            
            base_cols = set(merged_df.columns)
            new_cols = [col for col in enrich_df.columns 
                       if col not in ['breach_id', 'row_id', 'cik', 'org_name', 'breach_date'] 
                       and col not in base_cols]
            
            if len(new_cols) > 0:
                before = len(merged_df)
                merged_df = merged_df.merge(
                    enrich_df[['row_id'] + new_cols],
                    on='row_id',
                    how='left',
                    validate='1:1'
                )
                
                if len(merged_df) == before:
                    print(f"  ✓ Merged {len(new_cols)} variables: {', '.join(new_cols[:3])}...")
                    print(f"  ✓ Rows: {len(merged_df)} (no change)")
                    
                    # Show enforcement rate
                    if 'has_enforcement' in merged_df.columns:
                        rate = merged_df['has_enforcement'].mean() * 100
                        print(f"  ⚖️ Enforcement rate: {rate:.1f}%")
                    
                    merge_summary.append({
                        'Enrichment': 'Regulatory Enforcement',
                        'Hypothesis': 'H6',
                        'Status': 'SUCCESS',
                        'Variables': len(new_cols),
                        'Key_Vars': 'has_enforcement, enforcement_within_365d'
                    })
                else:
                    print(f"  ✗ Merge created duplicates ({before} → {len(merged_df)})")
                    merged_df = merged_df.iloc[:before]
                    merge_summary.append({'Enrichment': 'Regulatory Enforcement', 'Status': 'ERROR - duplicates'})
            else:
                print(f"  ⚠ No new variables to merge")
                merge_summary.append({'Enrichment': 'Regulatory Enforcement', 'Status': 'NO NEW VARS'})
        else:
            print(f"  ✗ No breach_id column found")
            merge_summary.append({'Enrichment': 'Regulatory Enforcement', 'Status': 'ERROR - no breach_id'})
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        merge_summary.append({'Enrichment': 'Regulatory Enforcement', 'Status': f'ERROR: {str(e)[:50]}'})
else:
    print(f"  ✗ File not found")
    merge_summary.append({'Enrichment': 'Regulatory Enforcement', 'Status': 'NOT FOUND'})

# ============================================================================
# 6. ANALYST COVERAGE (Optional)
# ============================================================================
print(f"\n6. Analyst Coverage (Optional):")
filepath = 'Data/enrichment/analyst_coverage.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        
        # Check if it's just placeholder zeros
        if 'num_analysts' in enrich_df.columns:
            if enrich_df['num_analysts'].sum() == 0:
                print(f"  ⚠ File contains only zeros (no IBES access) - skipping")
                merge_summary.append({'Enrichment': 'Analyst Coverage', 'Status': 'SKIPPED (no data)'})
            else:
                enrich_df['row_id'] = enrich_df['breach_id']
                
                base_cols = set(merged_df.columns)
                new_cols = [col for col in enrich_df.columns 
                           if col not in ['breach_id', 'row_id', 'ticker', 'breach_date'] 
                           and col not in base_cols]
                
                if len(new_cols) > 0:
                    merged_df = merged_df.merge(
                        enrich_df[['row_id'] + new_cols],
                        on='row_id',
                        how='left',
                        validate='1:1'
                    )
                    
                    print(f"  ✓ Merged {len(new_cols)} variables")
                    print(f"  ✓ Rows: {len(merged_df)} (no change)")
                    
                    merge_summary.append({
                        'Enrichment': 'Analyst Coverage',
                        'Hypothesis': 'Control',
                        'Status': 'SUCCESS',
                        'Variables': len(new_cols),
                        'Key_Vars': 'num_analysts, high_analyst_coverage'
                    })
        
    except Exception as e:
        print(f"  ⚠ Skipping (error: {str(e)[:50]})")
else:
    print(f"  ⚠ File not found (optional)")

# ============================================================================
# INSTITUTIONAL OWNERSHIP (CONTROL VARIABLE)
# ============================================================================

print("\n[Step 7/9] Institutional Ownership...")
filepath = 'Data/enrichment/institutional_ownership.csv'

if os.path.exists(filepath):
    try:
        enrich_df = pd.read_csv(filepath)
        print(f"  [OK] Loaded: {len(enrich_df)} records")

        if len(enrich_df) > 0:
            # Try to merge by CIK and date
            if 'cik' in enrich_df.columns and 'breach_date' in enrich_df.columns:
                enrich_df['cik'] = enrich_df['cik'].astype(int)
                enrich_df['breach_date'] = pd.to_datetime(enrich_df['breach_date'])

                base_cols = set(merged_df.columns)
                new_cols = [col for col in enrich_df.columns
                           if col not in ['cik', 'breach_date']
                           and col not in base_cols]

                if len(new_cols) > 0:
                    merged_df = merged_df.merge(
                        enrich_df[['cik', 'breach_date'] + new_cols],
                        on=['cik', 'breach_date'],
                        how='left'
                    )

                    print(f"  [OK] Merged {len(new_cols)} variables")
                    print(f"  [OK] Rows: {len(merged_df)} (no change)")

                    merge_summary.append({
                        'Enrichment': 'Institutional Ownership',
                        'Hypothesis': 'Control',
                        'Status': 'SUCCESS',
                        'Variables': len(new_cols),
                        'Key_Vars': 'institutional_ownership_pct, num_institutions'
                    })

    except Exception as e:
        print(f"  [WARNING] Skipping (error: {str(e)[:50]})")
        merge_summary.append({
            'Enrichment': 'Institutional Ownership',
            'Hypothesis': 'Control',
            'Status': 'SKIPPED',
            'Variables': 0,
            'Key_Vars': 'N/A'
        })
else:
    print(f"  [WARNING] File not found (optional)")
    merge_summary.append({
        'Enrichment': 'Institutional Ownership',
        'Hypothesis': 'Control',
        'Status': 'NOT_FOUND',
        'Variables': 0,
        'Key_Vars': 'N/A'
    })

# ============================================================================
# VERIFY & SAVE
# ============================================================================

print("\n" + "=" * 80)
print("MERGE SUMMARY")
print("=" * 80)

summary_df = pd.DataFrame(merge_summary)
print("\n" + summary_df.to_string(index=False))

# Verify row count
if len(merged_df) != len(base_df):
    print(f"\n⚠ CRITICAL ERROR: Row count changed! {len(base_df)} → {len(merged_df)}")
    print("⚠ This indicates a merge problem - aborting!")
    exit()

print(f"\n✓ Final row count: {len(merged_df)} (correct!)")

successful = len([s for s in merge_summary if s.get('Status') == 'SUCCESS'])
total_vars = sum([s.get('Variables', 0) for s in merge_summary if isinstance(s.get('Variables'), (int, float))])

print(f"✓ Successfully merged: {successful} enrichments")
print(f"✓ Total new variables added: {total_vars}")

# Save enriched dataset
print("\n" + "=" * 80)
print("SAVING ENRICHED DATASET")
print("=" * 80)

# Remove temporary keys
final_df = merged_df.drop(['row_id'], axis=1, errors='ignore')

# ============================================================================
# CREATE COMPUTED VARIABLES (Per Phase 2 variable specification)
# ============================================================================

print("\n" + "=" * 80)
print("CREATING COMPUTED VARIABLES")
print("=" * 80)

# total_affected_log: Log-transform records affected
if 'records_affected_numeric' in final_df.columns:
    final_df['total_affected_log'] = np.log(final_df['records_affected_numeric'] + 1)
    print(f"\n✓ Created total_affected_log")
    print(f"  Range: {final_df['total_affected_log'].min():.2f} to {final_df['total_affected_log'].max():.2f}")
    print(f"  N non-null: {final_df['total_affected_log'].notna().sum():,}")
else:
    print(f"\n⚠ Warning: records_affected_numeric not found - skipping total_affected_log")

output_file = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.xlsx'
csv_file = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'

print(f"\nSaving final enriched dataset...")

try:
    final_df.to_excel(output_file, index=False)
    file_size = os.path.getsize(output_file)
    print(f"✓ Excel: {output_file} ({file_size/1024/1024:.2f} MB)")
    
    final_df.to_csv(csv_file, index=False)
    csv_size = os.path.getsize(csv_file)
    print(f"✓ CSV: {csv_file} ({csv_size/1024/1024:.2f} MB)")
    
except Exception as e:
    print(f"✗ Error saving: {e}")
    exit()

# Show enrichment statistics
print("\n" + "=" * 80)
print("ENRICHMENT STATISTICS")
print("=" * 80)

if 'prior_breaches_total' in final_df.columns:
    repeat_rate = (final_df['prior_breaches_total'] > 0).mean() * 100
    print(f"\n📊 H3 - Prior Breach History:")
    print(f"  • Repeat offenders: {repeat_rate:.1f}%")
    print(f"  • Mean prior breaches: {final_df['prior_breaches_total'].mean():.2f}")

if 'health_breach' in final_df.columns:
    health_rate = final_df['health_breach'].mean() * 100
    print(f"\n📊 H4 - Breach Severity:")
    print(f"  • Health data breaches: {health_rate:.1f}%")
    if 'financial_breach' in final_df.columns:
        fin_rate = final_df['financial_breach'].mean() * 100
        print(f"  • Financial data breaches: {fin_rate:.1f}%")

if 'has_media_coverage' in final_df.columns:
    coverage_rate = final_df['has_media_coverage'].mean() * 100
    high_coverage = final_df['high_media_coverage'].mean() * 100
    print(f"\n📊 Media Coverage:")
    print(f"  • Any coverage: {coverage_rate:.1f}%")
    print(f"  • High coverage (10+ articles): {high_coverage:.1f}%")
    print(f"  • Total articles tracked: {final_df['media_coverage_count'].sum():,}")

if 'executive_change_30d' in final_df.columns:
    turnover_30d = final_df['executive_change_30d'].mean() * 100
    print(f"\n📊 H5 - Executive Turnover:")
    print(f"  • Changes within 30 days: {turnover_30d:.1f}%")
    if 'executive_change_90d' in final_df.columns:
        turnover_90d = final_df['executive_change_90d'].mean() * 100
        print(f"  • Changes within 90 days: {turnover_90d:.1f}%")

if 'has_enforcement' in final_df.columns:
    enforcement_rate = final_df['has_enforcement'].mean() * 100
    print(f"\n📊 H6 - Regulatory Enforcement:")
    print(f"  • Enforcement actions: {enforcement_rate:.1f}%")

print("\n" + "=" * 80)
print("✅ ENRICHMENT MERGE COMPLETE!")
print("=" * 80)

print(f"\n📊 FINAL DATASET SUMMARY:")
print(f"  • Total breaches: {len(final_df):,}")
print(f"  • Total variables: {len(final_df.columns)}")
print(f"  • With CRSP data: {final_df['has_crsp_data'].sum():,}")

# Only show Compustat if column exists
if 'has_compustat' in final_df.columns:
    print(f"  • With Compustat data: {final_df['has_compustat'].sum():,}")

print(f"  • With enrichments: {successful} datasets merged")

print(f"\n📁 Output files:")
print(f"  • {output_file}")
print(f"  • {csv_file}")

print(f"\n🚀 READY FOR DISSERTATION ANALYSIS!")
print("=" * 80)