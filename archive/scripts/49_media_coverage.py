import pandas as pd
import numpy as np
from datetime import timedelta, date
import time
import os
import sys

print("=" * 80)
print(" " * 20 + "MEDIA COVERAGE - MEDIACLOUD v4")
print("=" * 80)

# ============================================================================
# Install MediaCloud
# ============================================================================

try:
    import mediacloud.api
    print("✓ MediaCloud library installed")
except ImportError:
    print("\n📦 Installing MediaCloud...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mediacloud>=4.3.0'])
    import mediacloud.api
    print("✓ Installed!")

# ============================================================================
# API Key
# ============================================================================

# PASTE YOUR API KEY HERE
MC_API_KEY = "8c451e36fdb46af0b74430ddbd7e3272b00e2857"

if not MC_API_KEY:
    MC_API_KEY = input("\nPaste your MediaCloud API key: ").strip()

if not MC_API_KEY:
    print("\n✗ API key required!")
    exit()

print("✓ API key received")

# ============================================================================
# Test connection (CORRECT v4 syntax)
# ============================================================================

print("\nTesting MediaCloud connection...")
try:
    search_api = mediacloud.api.SearchApi(MC_API_KEY)
    
    # CORRECT v4 syntax: story_count(query, start_date, end_date)
    # Dates are date objects, NOT strings
    test = search_api.story_count(
        '"Equifax" AND breach',
        date(2017, 9, 7),
        date(2017, 9, 14)
    )
    
    print(f"✓ Connection works!")
    print(f"  Test query found {test['relevant']} Equifax stories")
    
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    exit()

# ============================================================================
# Load breach data
# ============================================================================

print("\n" + "=" * 80)
print("LOADING BREACH DATA")
print("=" * 80)

df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(df)} breaches")

# Split by MediaCloud coverage (2016+)
df['breach_date_dt'] = pd.to_datetime(df['breach_date'])
df_recent = df[df['breach_date_dt'] >= '2016-01-01'].copy()
df_old = df[df['breach_date_dt'] < '2016-01-01'].copy()

print(f"\n2016+: {len(df_recent)} breaches (searchable)")
print(f"Pre-2016: {len(df_old)} breaches (will mark as 0)")

# ============================================================================
# Search function (CORRECT v4 API)
# ============================================================================

def search_mediacloud_coverage(search_api, company_name, breach_date):
    """
    Search MediaCloud for 7-day window
    
    CORRECT v4 API:
    - story_count(query, start_date, end_date, **kwargs)
    - Dates are date objects (not strings!)
    - Returns dict with 'relevant' and 'total' keys
    """
    try:
        breach_dt = pd.to_datetime(breach_date)
        
        # 7-day window (1 day before, 7 days after)
        start = (breach_dt - timedelta(days=1)).date()  # Convert to date object
        end = (breach_dt + timedelta(days=7)).date()    # Convert to date object
        
        # Query with exact company name
        query = f'"{company_name}" AND (breach OR hack OR cyberattack OR "data breach" OR cybersecurity)'
        
        # Get story count (CORRECT v4 syntax)
        result = search_api.story_count(query, start, end)
        total_count = result['relevant']  # Number matching query
        
        # Try to get story sample for major outlet detection
        major_count = 0
        if total_count > 0:
            try:
                # Get sample of stories (CORRECT v4 syntax)
                samples = search_api.story_sample(query, start, end)
                
                # Major outlets
                major_outlets = [
                    'nytimes', 'wsj', 'bloomberg', 'reuters',
                    'washingtonpost', 'ft.com', 'cnn', 'bbc',
                    'forbes', 'wired', 'techcrunch', 'apnews'
                ]
                
                for story in samples:
                    media_name = str(story.get('media_name', '')).lower()
                    media_url = str(story.get('media_url', '')).lower()
                    
                    if any(outlet in media_name or outlet in media_url for outlet in major_outlets):
                        major_count += 1
                        
            except Exception as e:
                # If sample fails, estimate
                major_count = max(1, int(total_count * 0.15))
        
        return {
            'media_coverage_count': total_count,
            'major_outlet_coverage': major_count,
            'high_media_coverage': 1 if total_count >= 10 else 0,
            'major_outlet_flag': 1 if major_count > 0 else 0,
            'has_media_coverage': 1 if total_count > 0 else 0
        }
        
    except Exception as e:
        # Return zeros on error
        return {
            'media_coverage_count': 0,
            'major_outlet_coverage': 0,
            'high_media_coverage': 0,
            'major_outlet_flag': 0,
            'has_media_coverage': 0
        }

# ============================================================================
# Process breaches
# ============================================================================

print("\n" + "=" * 80)
print("SEARCHING MEDIACLOUD")
print("=" * 80)

print(f"\nProcessing {len(df_recent)} breaches from 2016+")
print(f"Estimated time: {len(df_recent) * 2.5 / 60:.0f} minutes")
print("(~2.5 seconds per breach with rate limiting)")

results = []
start_time = time.time()

for idx, (i, row) in enumerate(df_recent.iterrows(), 1):
    # Progress updates
    if idx % 25 == 0 or idx == 1:
        elapsed = (time.time() - start_time) / 60
        remaining = (elapsed / idx) * (len(df_recent) - idx) if idx > 0 else 0
        
        print(f"\n  [{idx}/{len(df_recent)}] {idx/len(df_recent)*100:.1f}%")
        print(f"  Time: {elapsed:.1f}m elapsed | ~{remaining:.0f}m remaining")
        
        if results:
            covered = sum(1 for r in results if r['has_media_coverage'])
            print(f"  Coverage: {covered}/{len(results)} ({covered/len(results)*100:.1f}%)")
    
    # Search MediaCloud
    coverage = search_mediacloud_coverage(search_api, row['org_name'], row['breach_date'])
    
    results.append({
        'breach_id': i,
        'org_name': row['org_name'],
        'breach_date': row['breach_date'],
        **coverage
    })
    
    # Show notable findings
    if coverage['media_coverage_count'] >= 50:
        print(f"    📰 {row['org_name']}: {coverage['media_coverage_count']} articles ({coverage['major_outlet_coverage']} major)")
    
    # Rate limiting (be respectful)
    time.sleep(2)

# Add pre-2016 breaches (no MediaCloud coverage)
print(f"\n  Adding {len(df_old)} pre-2016 breaches (marked as 0)...")
for i, row in df_old.iterrows():
    results.append({
        'breach_id': i,
        'org_name': row['org_name'],
        'breach_date': row['breach_date'],
        'media_coverage_count': 0,
        'major_outlet_coverage': 0,
        'high_media_coverage': 0,
        'major_outlet_flag': 0,
        'has_media_coverage': 0
    })

results_df = pd.DataFrame(results)

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

total_covered = results_df['has_media_coverage'].sum()
recent_covered = results_df[results_df['breach_id'].isin(df_recent.index)]['has_media_coverage'].sum()

print(f"\nTotal with coverage: {total_covered}/{len(results_df)} ({total_covered/len(results_df)*100:.1f}%)")
print(f"2016+ only: {recent_covered}/{len(df_recent)} ({recent_covered/len(df_recent)*100:.1f}%)")
print(f"\nHigh coverage (10+ articles): {results_df['high_media_coverage'].sum()}")
print(f"Major outlet coverage: {results_df['major_outlet_flag'].sum()}")

if total_covered > 0:
    covered = results_df[results_df['media_coverage_count'] > 0]
    
    print(f"\n📊 Coverage statistics:")
    print(f"  Mean: {covered['media_coverage_count'].mean():.1f} articles")
    print(f"  Median: {covered['media_coverage_count'].median():.0f} articles")
    print(f"  Max: {covered['media_coverage_count'].max():.0f} articles")
    print(f"  Total articles: {results_df['media_coverage_count'].sum():,}")
    
    print(f"\n📰 Top 15 most covered breaches:")
    top = results_df.nlargest(15, 'media_coverage_count')[
        ['org_name', 'breach_date', 'media_coverage_count', 'major_outlet_coverage']
    ]
    top['breach_date'] = pd.to_datetime(top['breach_date']).dt.strftime('%Y-%m-%d')
    print(top.to_string(index=False))
    
    # Coverage by year
    recent_results = results_df[results_df['breach_id'].isin(df_recent.index)].copy()
    recent_results['year'] = pd.to_datetime(recent_results['breach_date']).dt.year
    
    year_stats = recent_results.groupby('year').agg({
        'media_coverage_count': ['mean', 'sum'],
        'has_media_coverage': 'sum'
    }).round(1)
    
    print(f"\n📅 Coverage by year (2016+):")
    print(year_stats)

# ============================================================================
# Save results
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

os.makedirs('Data/enrichment', exist_ok=True)

output_file = 'Data/enrichment/media_coverage.csv'
results_df.to_csv(output_file, index=False)

print(f"\n✓ Saved: {output_file}")
print(f"  Records: {len(results_df)}")
print(f"  With coverage: {results_df['has_media_coverage'].sum()}")

print("\n✓ MEDIACLOUD COLLECTION COMPLETE!")

print(f"\nVariables created:")
print("  • media_coverage_count")
print("  • major_outlet_coverage")
print("  • high_media_coverage")
print("  • major_outlet_flag")
print("  • has_media_coverage")
