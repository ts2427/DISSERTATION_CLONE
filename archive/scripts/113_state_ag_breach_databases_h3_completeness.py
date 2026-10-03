"""
SCRIPT 113: STATE AG BREACH NOTIFICATION DATABASES FOR H3 PRIOR BREACH COMPLETENESS
===================================================================================

Problem: H3 uses PRC prior_breaches_1yr count (potentially incomplete)
Solution: Merge state AG breach notification databases for complete history
Impact: More accurate prior breach history measurement

State AG Sources (Free, Public):
  - Maine: https://www.maine.gov/ag/consumer/protection/privateinformationpolicy
  - California: https://oag.ca.gov/consumer/databreach
  - Washington: https://dor.wa.gov/taxes-rates/other-taxes/public-utility-tax/data-breaches
  - Indiana: https://www.in.gov/attorney-general/consumer-protection/
  - Connecticut: https://portal.ct.gov/ag/consumer-protection/data-breaches
  - Virginia: https://www.oag.state.va.us/consumer-protection/data-breach-notification
  - Texas: https://www.texasattorneygeneral.gov/consumer-protection/data-breaches

Coverage:
  - Firms must report breaches affecting TX/ME/CA/WA/IN/CT/VA residents
  - Creates more complete breach history than any single private database
  - Fills gaps in PRC (which may undersample breaches in certain states/years)

Pre-specification: For each firm in dissertation:
  1. Collect all reported breaches from state AG databases
  2. Merge with PRC data (union of both sources)
  3. Count: prior_breaches_1yr_expanded = breaches from all sources
  4. Compare to PRC-only count
  5. Measure: Difference in prior breach history per firm

Expected findings:
  - Some firms have more breaches in state DBs than PRC
  - Especially tech companies (may underreport to PRC)
  - Especially older breaches (PRC starts 2005)
  - More complete history could strengthen H3 coefficient

Improvement: Ground truth from official state sources, not self-reported
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import requests

print("=" * 80)
print("SCRIPT 113: STATE AG BREACH DATABASES FOR H3 PRIOR BREACH COMPLETENESS")
print("=" * 80)

# ============================================================================
# STEP 1: Load dissertation dataset
# ============================================================================
print("\n[1/5] Loading dissertation dataset...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print(f"  Total records: {len(df)}")
print(f"  Records with prior_breaches_1yr: {df['prior_breaches_1yr'].notna().sum()}")

unique_firms = df[['org_name']].drop_duplicates()
print(f"  Unique firms: {len(unique_firms)}")

# Pre-specification: Firms to search in state AG databases
print(f"\n  Pre-specification: Will search state AG databases for all {len(unique_firms)} firms")

# ============================================================================
# STEP 2: Explain state AG data sources
# ============================================================================
print("\n[2/5] State AG Breach Notification Database Sources...")

state_sources = {
    'Maine': {
        'url': 'https://www.maine.gov/ag/consumer/protection/privateinformationpolicy',
        'coverage': 'All breaches affecting Maine residents',
        'format': 'Searchable database'
    },
    'California': {
        'url': 'https://oag.ca.gov/consumer/databreach',
        'coverage': 'All breaches affecting California residents',
        'format': 'Downloadable list'
    },
    'Washington': {
        'url': 'https://dor.wa.gov/taxes-rates/other-taxes/public-utility-tax/data-breaches',
        'coverage': 'Data breaches notified to WA residents',
        'format': 'Searchable database'
    },
    'Indiana': {
        'url': 'https://www.in.gov/attorney-general/consumer-protection/',
        'coverage': 'Indiana data breach notification list',
        'format': 'Web list'
    },
    'Connecticut': {
        'url': 'https://portal.ct.gov/ag/consumer-protection/data-breaches',
        'coverage': 'Connecticut breach notification list',
        'format': 'Searchable'
    },
    'Virginia': {
        'url': 'https://www.oag.state.va.us/consumer-protection/data-breach-notification',
        'coverage': 'Virginia breach notification list',
        'format': 'Database'
    },
    'Texas': {
        'url': 'https://www.texasattorneygeneral.gov/consumer-protection/data-breaches',
        'coverage': 'Texas breach notification list',
        'format': 'Database'
    },
}

print("\n  State AG Breach Databases (Free, Public):")
for state, info in state_sources.items():
    print(f"\n    {state}:")
    print(f"      URL: {info['url']}")
    print(f"      Coverage: {info['coverage']}")
    print(f"      Format: {info['format']}")

# ============================================================================
# STEP 3: Create template for merged state AG data
# ============================================================================
print("\n[3/5] Creating template for state AG breach data...")

state_ag_template = pd.DataFrame({
    'org_name': [],
    'breach_date': [],
    'state_ag_source': [],  # Which state AG reported it (ME, CA, WA, IN, CT, VA, TX)
    'individuals_affected': [],
    'state_ag_breach': [],  # Boolean
})

output_path = Path("Data/state_ag/breach_databases_merged_TEMPLATE.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
state_ag_template.to_csv(output_path, index=False)

print(f"  Template created: {output_path}")

# ============================================================================
# STEP 4: Pre-specification for H3 revision
# ============================================================================
print("\n[4/5] Pre-specification for H3 prior breach history expansion...")

print("""
PRE-SPECIFIED MERGE STRATEGY:

1. Data Collection:
   - Download/scrape all 7 state AG breach databases
   - Normalize organization names for matching
   - Include all breaches from 2005-present (dissertation period)

2. Deduplication:
   - Merge PRC data with state AG data (union by org_name + breach_date)
   - Remove duplicates (same breach reported by multiple states)
   - Result: Complete breach history per firm

3. Comparison:
   - Count prior_breaches_1yr per firm using:
     a) PRC only (current approach)
     b) State AG only
     c) Merged (union of both)

   - Measure: How much does prior breach count change with merged data?

EXPECTED FINDINGS:

  Completeness Gain:
    - Median increase in prior_breaches_1yr: 10-30%
    - Some firms may have 2-3x more breaches when merged
    - Especially likely: Tech companies, multi-state operators

  Distribution Changes:
    - Some firms shift from "0 prior breaches" to "2-3 prior"
    - Changes correlation between prior breaches and current breach
    - Could strengthen H3 coefficient if measurement error was suppressing it

REVISION OPTIONS:

  Option A (Minimal change <10%):
    - Keep PRC as main specification
    - Note state AG data as robustness check
    - No substantial revision needed

  Option B (Moderate change 10-30%):
    - Report both PRC and merged specifications
    - Show whether H3 strengthens with expanded prior breach count
    - Pre-register both as robustness checks

  Option C (Large change >30%):
    - Use merged state AG + PRC data as main specification
    - Prior breach history is substantially mismeasured in PRC alone
    - Re-run H3 regression with complete prior breach count
    - Pre-register this as specification revision

DECISION RULE (Pre-specified):
  - If correlation between PRC and merged count > 0.90: No revision
  - If correlation 0.70-0.90: Run both specifications
  - If correlation < 0.70: Revise to merged data as main spec
  - Always report comparison in robustness section
""")

# ============================================================================
# STEP 5: Manual data collection instructions
# ============================================================================
print("\n[5/5] Manual Data Collection Instructions...")

print("""
WORKFLOW FOR STATE AG DATA:

Step 1: Maine
  - Visit: https://www.maine.gov/ag/consumer/protection/privateinformationpolicy
  - Search for each firm's name in Maine breach list
  - Record all breaches with date and individuals affected

Step 2: California
  - Visit: https://oag.ca.gov/consumer/databreach
  - Download dataset if available (or scrape)
  - Search for firms in dataset

Step 3-7: Repeat for WA, IN, CT, VA, TX
  - Visit each state AG website
  - Search for firm names
  - Record breaches and dates

Step 8: Consolidate
  - Combine all 7 state databases into single file
  - Deduplicate by firm name + breach date
  - Merge with PRC data (union)

ALTERNATIVE - Automated Web Scraping:

  If using Python requests + BeautifulSoup:
    - Script can download and parse state breach lists
    - Estimated time: 1-2 hours to set up, <5 min to run
    - More reliable than manual lookup

  If using Selenium:
    - Can query interactive state AG databases
    - Estimated time: 2-3 hours to set up, 1-2 hours to run
    - More comprehensive but slower

ESTIMATED TIME:
  - Manual lookup: 2-4 hours
  - Automated scraping: 1-2 hours setup + <5 min execution

Once data collected:
  1. Save to: Data/state_ag/merged_breach_history.csv
  2. Run script 114_merge_state_ag_to_dissertation.py
  3. Recalculate prior_breaches_1yr with merged data
  4. Re-run H3 regression with complete prior breach history
""")

print("\n" + "=" * 80)
print("NEXT: Obtain state AG breach databases, then merge with dissertation")
print("      Script 114_merge_state_ag_to_dissertation.py")
print("=" * 80)
