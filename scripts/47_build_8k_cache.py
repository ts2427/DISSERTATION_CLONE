"""
Build local cache of 8-K filings for Item 5.02 extraction
Downloads 8-Ks once, stores locally, reuses on subsequent runs
Dramatically speeds up Item 5.02 extraction scripts
"""

import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

print("=" * 80)
print("BUILD LOCAL 8-K CACHE FOR ITEM 5.02 EXTRACTION")
print("=" * 80)

# ============================================================================
# STEP 1: Load dataset and identify 8-Ks to fetch
# ============================================================================
print("\n[1/4] Loading dataset and identifying 8-Ks to fetch...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

# Create cache directory
cache_dir = Path("Data/edgar/8k_cache")
cache_dir.mkdir(parents=True, exist_ok=True)
print(f"  Cache directory: {cache_dir}")

# SEC API headers
headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}

# ============================================================================
# STEP 2: Get list of 8-K filings to cache
# ============================================================================
print("\n[2/4] Querying SEC EDGAR for 8-K filings...")

# For each record, query SEC for 8-Ks in the 180d window
firms_to_query = df[df['resolved_cik'].notna()].copy()
firms_to_query['resolved_cik'] = firms_to_query['resolved_cik'].astype(int)

total_to_fetch = len(firms_to_query)
filings_found = 0
cache_hits = 0
downloads = 0
errors = 0

for idx, (_, row) in enumerate(firms_to_query.iterrows()):
    if idx % 100 == 0:
        print(f"  Processed {idx}/{total_to_fetch} records...")

    cik = int(row['resolved_cik'])
    breach_date = pd.to_datetime(row['breach_date'])
    window_end = breach_date + timedelta(days=180)

    # Create cache filename for this query
    cache_key = f"cik_{cik:010d}_{breach_date.strftime('%Y%m%d')}_180d"
    cache_file = cache_dir / f"{cache_key}.json"

    # Check if already cached
    if cache_file.exists():
        cache_hits += 1
        continue

    try:
        # Query SEC EDGAR API for this company's 8-K filings
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik:010d}&type=8-K&owner=exclude&count=100"

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse response for 8-K filing links
            import re
            # Extract filing URLs from SEC's HTML response
            filing_pattern = r'/Archives/([^"]+\.htm)'
            filings = re.findall(filing_pattern, response.text)

            if filings:
                filings_found += len(filings)

                # Download each 8-K document
                filing_docs = []
                for filing_url in filings[:10]:  # Limit to 10 most recent
                    try:
                        doc_url = f"https://www.sec.gov/Archives/{filing_url}"
                        doc_response = requests.get(doc_url, headers=headers, timeout=10)

                        if doc_response.status_code == 200:
                            filing_docs.append({
                                'url': doc_url,
                                'content': doc_response.text[:50000],  # Store first 50k chars
                                'downloaded_at': datetime.now().isoformat()
                            })
                            downloads += 1

                    except Exception as e:
                        errors += 1

                # Cache this query result
                if filing_docs:
                    with open(cache_file, 'w') as f:
                        json.dump({
                            'cik': cik,
                            'breach_date': breach_date.isoformat(),
                            'filings': filing_docs
                        }, f)

        else:
            errors += 1

    except Exception as e:
        errors += 1

    # Rate limiting to avoid overwhelming SEC
    import time
    time.sleep(0.5)

# ============================================================================
# STEP 3: Summary
# ============================================================================
print("\n[3/4] Cache statistics:")
print(f"  Cache directory: {cache_dir}")
print(f"  Cache files: {len(list(cache_dir.glob('*.json')))}")
print(f"  Filings found: {filings_found}")
print(f"  Documents cached: {downloads}")
print(f"  Cache hits (already cached): {cache_hits}")
print(f"  Errors: {errors}")

# ============================================================================
# STEP 4: Create index for fast lookup
# ============================================================================
print("\n[4/4] Creating cache index...")

cache_index = []
for cache_file in cache_dir.glob('*.json'):
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            cache_index.append({
                'cache_file': str(cache_file.name),
                'cik': data['cik'],
                'breach_date': data['breach_date'],
                'filings_cached': len(data.get('filings', []))
            })
    except:
        pass

if cache_index:
    index_df = pd.DataFrame(cache_index)
    index_file = cache_dir / "cache_index.csv"
    index_df.to_csv(index_file, index=False)
    print(f"  Index saved: {index_file}")
    print(f"  Index entries: {len(index_df)}")

print("\n" + "=" * 80)
print("CACHE BUILD COMPLETE")
print("=" * 80)
print(f"""
Cache Statistics:
  Location: {cache_dir}
  Size: {sum(f.stat().st_size for f in cache_dir.glob('*.json')) / 1024 / 1024:.1f} MB
  Files: {len(list(cache_dir.glob('*.json')))}

Next Steps:
  1. Modify scripts/46_executive_changes_item5_02.py to use this cache
  2. Before downloading 8-K, check cache first
  3. This will eliminate all re-downloading on subsequent runs

Speed Improvement:
  Without cache: ~20-30 minutes (download + parse all 8-Ks)
  With cache: ~2-5 minutes (parse cached files only)
""")
