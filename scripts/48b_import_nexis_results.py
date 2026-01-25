import pandas as pd
import numpy as np
import os

print("=" * 80)
print(" " * 20 + "IMPORT NEXIS UNI RESULTS")
print("=" * 80)

# Load your completed collection template
collection_file = 'Data/enrichment/nexis_uni_collection_template.csv'

if not os.path.exists(collection_file):
    print(f"\n✗ ERROR: Collection file not found!")
    print(f"  Expected: {collection_file}")
    print(f"\n  You need to:")
    print(f"  1. Run 48_nexis_uni_query_generator.py first")
    print(f"  2. Fill in the template with Nexis Uni results")
    print(f"  3. Save the file")
    exit()

# Load results
results_df = pd.read_csv(collection_file)
print(f"\n✓ Loaded {len(results_df)} breach records")

# Convert columns to numeric (handle any text/errors)
results_df['total_articles'] = pd.to_numeric(results_df['total_articles'], errors='coerce').fillna(0).astype(int)
results_df['major_outlets'] = pd.to_numeric(results_df['major_outlets'], errors='coerce').fillna(0).astype(int)

# Create derived variables
results_df['media_coverage_count'] = results_df['total_articles']
results_df['major_outlet_coverage'] = results_df['major_outlets']
results_df['high_media_coverage'] = (results_df['total_articles'] >= 10).astype(int)
results_df['major_outlet_flag'] = (results_df['major_outlets'] > 0).astype(int)
results_df['has_media_coverage'] = (results_df['total_articles'] > 0).astype(int)

# Summary statistics
print("\n" + "=" * 80)
print("MEDIA COVERAGE SUMMARY")
print("=" * 80)

completed = results_df['total_articles'].notna().sum()
print(f"\nCompleted records: {completed}/{len(results_df)} ({completed/len(results_df)*100:.1f}%)")

if completed > 0:
    coverage_sample = results_df[results_df['has_media_coverage'] == 1]
    
    print(f"\nBreaches with media coverage: {len(coverage_sample)} ({len(coverage_sample)/completed*100:.1f}%)")
    print(f"Breaches with high coverage (10+ articles): {results_df['high_media_coverage'].sum()}")
    print(f"Breaches covered by major outlets: {results_df['major_outlet_flag'].sum()}")
    
    print(f"\nMedia coverage distribution:")
    print(results_df['media_coverage_count'].describe())
    
    print(f"\nTop 10 most covered breaches:")
    top = results_df.nlargest(10, 'media_coverage_count')[
        ['company', 'breach_date', 'media_coverage_count', 'major_outlet_coverage']
    ]
    print(top.to_string(index=False))
    
    # Analyze by year
    results_df['year'] = pd.to_datetime(results_df['breach_date']).dt.year
    year_stats = results_df.groupby('year').agg({
        'media_coverage_count': ['mean', 'median', 'sum'],
        'has_media_coverage': 'sum'
    }).round(1)
    
    print(f"\nCoverage by year:")
    print(year_stats)

# Save final enrichment file
output_cols = ['breach_id', 'company', 'breach_date', 
               'media_coverage_count', 'major_outlet_coverage',
               'high_media_coverage', 'major_outlet_flag', 'has_media_coverage']

final_df = results_df[output_cols].copy()

output_file = 'Data/enrichment/media_coverage.csv'
final_df.to_csv(output_file, index=False)

print(f"\n✓ Saved to: {output_file}")

print("\n" + "=" * 80)
print("✓ NEXIS UNI IMPORT COMPLETE!")
print("=" * 80)

print(f"\nCreated variables:")
print("  • media_coverage_count (total news articles)")
print("  • major_outlet_coverage (articles in major publications)")
print("  • high_media_coverage (1 if 10+ articles)")
print("  • major_outlet_flag (1 if any major outlet coverage)")
print("  • has_media_coverage (1 if any coverage)")

print(f"\nNext: Merge with main dataset")
print("  Run: python scripts/50_merge_all_enrichments.py")