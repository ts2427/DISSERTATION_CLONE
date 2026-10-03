import pandas as pd
from datetime import timedelta

print("=" * 80)
print(" " * 20 + "NEXIS UNI QUERY GENERATOR")
print("=" * 80)

# Load breach data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(df)} breach records")

# Create search queries
queries = []

for idx, row in df.iterrows():
    company_name = row['org_name']
    breach_date = pd.to_datetime(row['breach_date'])
    
    # 7-day window (1 day before, 7 days after)
    start_date = breach_date - timedelta(days=1)
    end_date = breach_date + timedelta(days=7)
    
    # Nexis Uni search format
    # Use exact company name in quotes to reduce false matches
    query = f'"{company_name}" AND (breach OR hack OR cyberattack OR "data breach" OR security OR hacker)'
    
    # Date format for Nexis Uni
    date_filter = f'{start_date.strftime("%B %d, %Y")} to {end_date.strftime("%B %d, %Y")}'
    
    queries.append({
        'breach_id': idx,
        'company': company_name,
        'breach_date': breach_date.strftime('%Y-%m-%d'),
        'search_query': query,
        'date_range': date_filter,
        'start_date': start_date.strftime('%m/%d/%Y'),
        'end_date': end_date.strftime('%m/%d/%Y')
    })

queries_df = pd.DataFrame(queries)

# Group by year for batch processing
queries_df['year'] = pd.to_datetime(queries_df['breach_date']).dt.year

print("\n" + "=" * 80)
print("BATCH STRATEGY")
print("=" * 80)

year_counts = queries_df['year'].value_counts().sort_index(ascending=False)
print("\nBreaches by year:")
for year, count in year_counts.items():
    print(f"  {year}: {count:3d} breaches")

# Save master query list
queries_df.to_csv('Data/enrichment/nexis_uni_queries_master.csv', index=False)
print(f"\n✓ Saved master query list: Data/enrichment/nexis_uni_queries_master.csv")

# Create batches by year (easier to process)
import os
os.makedirs('Data/enrichment/nexis_batches', exist_ok=True)

for year in sorted(queries_df['year'].unique(), reverse=True):
    year_batch = queries_df[queries_df['year'] == year].copy()
    batch_file = f'Data/enrichment/nexis_batches/batch_{year}.csv'
    year_batch.to_csv(batch_file, index=False)
    print(f"✓ Created batch_{year}.csv ({len(year_batch)} breaches)")

# Create a simple collection template
print("\n" + "=" * 80)
print("COLLECTION TEMPLATE CREATED")
print("=" * 80)

template = queries_df[['breach_id', 'company', 'breach_date', 'search_query', 'date_range']].copy()
template['total_articles'] = ''
template['major_outlets'] = ''
template['notes'] = ''

template.to_csv('Data/enrichment/nexis_uni_collection_template.csv', index=False)
print("✓ Saved collection template: nexis_uni_collection_template.csv")

print("\n" + "=" * 80)
print("NEXIS UNI COLLECTION INSTRUCTIONS")
print("=" * 80)

print(f"""
YOU HAVE {len(df)} BREACHES TO PROCESS

FASTEST APPROACH (Recommended):
================================

1. OPEN NEXIS UNI:
   - Go to: https://www.southalabama.edu/departments/library/
   - Find "Nexis Uni" in database list
   - Login with your USA credentials

2. BATCH PROCESS BY YEAR:
   - Start with batch_2024.csv ({len(queries_df[queries_df['year']==2024])}) breaches)
   - Open file in Excel alongside Nexis Uni
   
3. FOR EACH BREACH:
   
   a) In Nexis Uni:
      - Click "News" (not Legal or Business)
      - Click "Advanced Search"
   
   b) Enter search details:
      - Search Terms: Copy from 'search_query' column
      - Date Range: Copy from 'date_range' column
      - Source: "Major U.S. and World Publications" (optional filter)
   
   c) Click "Search"
   
   d) Record results:
      - Total Results → 'total_articles' column
      - Filter by "Major Publications" → 'major_outlets' column
      - Add any notes → 'notes' column
   
   e) Move to next row

4. SAVE PROGRESS:
   - Save Excel file frequently
   - Work in batches (do 100 at a time)

TIME ESTIMATE:
==============
- ~5-10 seconds per breach (if fast)
- ~100 breaches/hour
- ~10-11 hours total for all {len(df)} breaches

SHORTCUTS TO SAVE TIME:
=======================
- Use keyboard shortcuts (Ctrl+C, Ctrl+V)
- Keep Nexis Uni in one window, Excel in another
- Process recent years first (2020-2025) - these matter most
- Can skip very old breaches (2004-2010) if time limited

BATCH PRIORITY ORDER:
=====================
1. 2024-2025: Most recent, most coverage
2. 2020-2023: Good coverage, recent memory
3. 2015-2019: Decent coverage
4. 2010-2014: Limited coverage, can skip if needed
5. 2004-2009: Very limited, probably skip
""")

print("\n" + "=" * 80)
print("ALTERNATIVE: FOCUS ON KEY BREACHES")
print("=" * 80)

# Identify key breaches (largest, most recent, publicly traded)
key_breaches = df[
    (df['has_crsp_data'] == True) |  # Has stock data
    (pd.to_datetime(df['breach_date']).dt.year >= 2015)  # Recent
].copy()

print(f"""
SMART STRATEGY: Focus on {len(key_breaches)} KEY breaches

These are:
- Publicly traded companies (have stock data)
- OR breaches from 2015+ (recent, more media coverage)

This reduces workload by {(1 - len(key_breaches)/len(df))*100:.0f}%!

Would you like to create this filtered list?
""")

# Create filtered batch
key_queries = queries_df[queries_df['breach_id'].isin(key_breaches.index)].copy()
key_queries.to_csv('Data/enrichment/nexis_uni_KEY_BREACHES_ONLY.csv', index=False)
print(f"✓ Created KEY_BREACHES_ONLY.csv ({len(key_queries)} breaches)")

print("\n" + "=" * 80)
print("✓ SETUP COMPLETE!")
print("=" * 80)

print(f"""
FILES CREATED:
==============
1. nexis_uni_queries_master.csv - All {len(df)} queries
2. nexis_uni_collection_template.csv - For recording results
3. nexis_uni_KEY_BREACHES_ONLY.csv - Filtered to {len(key_queries)} key breaches
4. nexis_batches/batch_YYYY.csv - One file per year

NEXT STEPS:
===========
1. Run this script: ✓ DONE
2. Open Nexis Uni in browser
3. Open collection template in Excel
4. Start with batch_2024.csv or KEY_BREACHES_ONLY.csv
5. Record results in template
6. When done: python scripts/48b_import_nexis_results.py
""")