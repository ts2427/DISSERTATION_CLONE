"""
SCRIPT 46: EXECUTIVE TURNOVER FROM 8-K ITEM 5.02 (SUBMISSIONS API + LOCAL CACHE)

Uses the SEC EDGAR submissions JSON API (data.sec.gov/submissions/), which returns
every filing for a company with form type, filing date, and the structured `items`
field for 8-Ks (e.g. "5.02,9.01"). Item detection is exact metadata matching, not
HTML scraping.

Replaces the broken browse-edgar version, which parsed filing dates from a
/Archives/YYYY/MM/DD/ URL pattern that does not exist in EDGAR URLs - it therefore
detected zero events for every firm.

Cache: one submissions fetch per unique CIK (not per breach), stored in
Data/edgar/8k_item5_02_cache/submissions_cache.pkl.
First run: ~600 unique CIKs at SEC-compliant rate -> a few minutes.
Subsequent runs: near-instant.

Output:
  Data/enrichment/executive_changes.csv        (merged by script 53)
  Data/enrichment/executive_changes_item5_02.csv (same content, explicit name)
"""

import pandas as pd
import requests
import pickle
import time
from datetime import timedelta
from pathlib import Path

print("=" * 80)
print("SCRIPT 46: ITEM 5.02 VIA SUBMISSIONS API (WITH LOCAL CACHE)")
print("=" * 80)

# ============================================================================
# SETUP
# ============================================================================
cache_dir = Path("Data/edgar/8k_item5_02_cache")
cache_dir.mkdir(parents=True, exist_ok=True)
cache_file = cache_dir / "submissions_cache.pkl"

if cache_file.exists():
    with open(cache_file, 'rb') as f:
        cik_cache = pickle.load(f)
    print(f"[SETUP] Existing cache: {len(cik_cache)} CIKs")
else:
    cik_cache = {}
    print(f"[SETUP] New cache (first run)")

HEADERS = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}
REQUEST_DELAY = 0.12  # SEC allows 10 req/s; stay under

# ============================================================================
# STEP 1: Load dataset
# ============================================================================
print("\n[1/4] Loading dataset...")
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"  Loaded: {len(df)} breach records")

analysis_df = df[df['cik'].notna()].copy()
analysis_df['cik'] = analysis_df['cik'].astype(int)
analysis_df['breach_date'] = pd.to_datetime(analysis_df['breach_date'])
print(f"  Records with CIK: {len(analysis_df)}")
print(f"  Unique CIKs: {analysis_df['cik'].nunique()}")


# ============================================================================
# STEP 2: Fetch 8-K filing lists per unique CIK (submissions API)
# ============================================================================
def fetch_json(url):
    """GET with one retry; returns parsed JSON or None."""
    for attempt in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
        except Exception:
            pass
        time.sleep(1.0)
    return None


def get_8k_filings(cik):
    """Return DataFrame of all 8-K filings (filing_date, items) for a CIK.

    Combines the `recent` block with any paginated older-filing files so the
    full history back to 2004 (when Item 5.02 was introduced) is covered.
    """
    base = fetch_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    if base is None:
        return None

    frames = []
    recent = base.get('filings', {}).get('recent', {})
    if recent.get('form'):
        frames.append(pd.DataFrame({
            'form': recent['form'],
            'filing_date': recent['filingDate'],
            'items': recent.get('items', [''] * len(recent['form'])),
        }))

    for extra in base.get('filings', {}).get('files', []):
        time.sleep(REQUEST_DELAY)
        page = fetch_json(f"https://data.sec.gov/submissions/{extra['name']}")
        if page and page.get('form'):
            frames.append(pd.DataFrame({
                'form': page['form'],
                'filing_date': page['filingDate'],
                'items': page.get('items', [''] * len(page['form'])),
            }))

    if not frames:
        return pd.DataFrame(columns=['form', 'filing_date', 'items'])

    filings = pd.concat(frames, ignore_index=True)
    filings = filings[filings['form'].isin(['8-K', '8-K/A'])].copy()
    filings['filing_date'] = pd.to_datetime(filings['filing_date'])
    filings['items'] = filings['items'].fillna('')
    return filings


print("\n[2/4] Fetching 8-K filing histories from submissions API...")
unique_ciks = analysis_df['cik'].unique()
new_fetches = 0
failed_ciks = []

for i, cik in enumerate(unique_ciks):
    if i % 100 == 0:
        print(f"  {i}/{len(unique_ciks)} CIKs... (new fetches: {new_fetches}, failures: {len(failed_ciks)})")
    if cik in cik_cache:
        continue
    time.sleep(REQUEST_DELAY)
    filings = get_8k_filings(cik)
    new_fetches += 1
    if filings is None:
        failed_ciks.append(cik)
        cik_cache[cik] = None
    else:
        cik_cache[cik] = filings
    # Periodic cache flush so an interruption doesn't lose progress
    if new_fetches % 50 == 0:
        with open(cache_file, 'wb') as f:
            pickle.dump(cik_cache, f)

with open(cache_file, 'wb') as f:
    pickle.dump(cik_cache, f)

print(f"  Done. New fetches: {new_fetches}, cache total: {len(cik_cache)}, failures: {len(failed_ciks)}")
if failed_ciks:
    print(f"  [WARN] {len(failed_ciks)} CIKs returned no submissions data (coded as missing, not zero)")

# ============================================================================
# STEP 3: Detect Item 5.02 filings within breach windows
# ============================================================================
print("\n[3/4] Detecting Item 5.02 filings within 30/90/180-day windows...")

results = []
for _, row in analysis_df.iterrows():
    cik = row['cik']
    breach_date = row['breach_date']
    filings = cik_cache.get(cik)

    if filings is None:
        results.append({
            'cik': cik, 'breach_date': breach_date.strftime('%Y-%m-%d'),
            'executive_change_30d': None, 'executive_change_90d': None,
            'executive_change_180d': None, 'num_item5_02_filings_180d': None,
            'days_to_first_item_5_02': None,
        })
        continue

    window = filings[
        (filings['filing_date'] >= breach_date) &
        (filings['filing_date'] <= breach_date + timedelta(days=180)) &
        (filings['items'].str.contains('5.02', regex=False))
    ]

    if len(window) == 0:
        results.append({
            'cik': cik, 'breach_date': breach_date.strftime('%Y-%m-%d'),
            'executive_change_30d': 0, 'executive_change_90d': 0,
            'executive_change_180d': 0, 'num_item5_02_filings_180d': 0,
            'days_to_first_item_5_02': None,
        })
        continue

    days_to_first = int((window['filing_date'].min() - breach_date).days)
    results.append({
        'cik': cik, 'breach_date': breach_date.strftime('%Y-%m-%d'),
        'executive_change_30d': 1 if days_to_first <= 30 else 0,
        'executive_change_90d': 1 if days_to_first <= 90 else 0,
        'executive_change_180d': 1,
        'num_item5_02_filings_180d': len(window),
        'days_to_first_item_5_02': days_to_first,
    })

results_df = pd.DataFrame(results)

# ============================================================================
# STEP 4: Save and report
# ============================================================================
print("\n[4/4] Saving results...")
out_dir = Path('Data/enrichment')
out_dir.mkdir(parents=True, exist_ok=True)
results_df.to_csv(out_dir / 'executive_changes_item5_02.csv', index=False)
results_df.to_csv(out_dir / 'executive_changes.csv', index=False)
print(f"  Saved: {out_dir / 'executive_changes_item5_02.csv'}")
print(f"  Saved: {out_dir / 'executive_changes.csv'}")

print("\n" + "=" * 80)
print("SCRIPT 46 COMPLETE (SUBMISSIONS API)")
print("=" * 80)

valid = results_df.dropna(subset=['executive_change_180d'])
print(f"\nCoverage: {len(valid)}/{len(results_df)} records with valid data")
print(f"\nBase Rates (Item 5.02 only):")
for w in ['30d', '90d', '180d']:
    col = f'executive_change_{w}'
    print(f"  {w:>5}: {100 * valid[col].mean():.1f}%  ({int(valid[col].sum())} events)")

events = valid[valid['executive_change_180d'] == 1]
if len(events) > 0:
    print(f"\nDays to first Item 5.02 (events): mean {events['days_to_first_item_5_02'].mean():.1f}, "
          f"median {events['days_to_first_item_5_02'].median():.0f}")

# Sanity guard: an all-zero result indicates a broken extraction, not reality
if valid['executive_change_180d'].sum() == 0:
    print("\n[ERROR] Zero Item 5.02 detections across all firms - extraction is broken.")
    print("        Do NOT merge this output. Investigate before proceeding.")
    raise SystemExit(1)
