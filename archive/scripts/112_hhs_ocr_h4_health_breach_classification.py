"""
SCRIPT 112: H4 HEALTH BREACH CLASSIFICATION FROM HHS OCR BREACH PORTAL
=======================================================================

Problem: H4 uses PRC health_breach field (potentially incomplete)
Solution: Use HHS OCR "Wall of Shame" - authoritative PHI breach registry
Impact: Definitive classification of health breaches (500+ person threshold)

HHS OCR Breach Notification Portal:
  - Covers: PHI (Protected Health Information) breaches 500+ individuals
  - Authoritative since: 2009
  - Source: HIPAA Breach Notification Rule
  - URL: https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf
  - Coverage: ~100% of HIPAA-reportable breaches

Pre-specification: For each breach in dissertation dataset:
  1. Search HHS OCR portal by org_name, breach_date (+/- 30 days)
  2. If found: Classify as health_breach_ocr = 1 (definitive)
  3. If not found: Classify as health_breach_ocr = 0
  4. Compare to PRC health_breach field
  5. Measure: Sensitivity and specificity vs PRC

Expected findings:
  - High sensitivity: HHS OCR captures most PRC health breaches
  - Medium sensitivity: HHS OCR finds health breaches PRC missed
  - Specificity: HHS OCR won't misclassify non-health as health
  - Impact on H4: Cleaner outcome measure, but null may persist

Improvement: Uses ground-truth regulatory source, not self-reported data
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
from pathlib import Path
import re

print("=" * 80)
print("SCRIPT 112: HHS OCR BREACH PORTAL FOR H4 HEALTH CLASSIFICATION")
print("=" * 80)

# ============================================================================
# STEP 1: Load dataset
# ============================================================================
print("\n[1/5] Loading dissertation dataset...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print(f"  Total records: {len(df)}")
print(f"  PRC health_breach=1: {df['health_breach'].sum()}")

# Pre-specification: Search for health breaches in HHS OCR
unique_orgs = df['org_name'].unique()
print(f"  Unique organizations: {len(unique_orgs)}")

# ============================================================================
# STEP 2: Query HHS OCR Breach Portal
# ============================================================================
print("\n[2/5] Querying HHS OCR Breach Notification Portal...")

headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}

hhs_results = []
found_count = 0
not_found_count = 0
api_errors = 0

# HHS OCR portal URL (public searchable database)
hhs_portal_url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"

print(f"  Target: HHS OCR Breach Notification Portal")
print(f"  Coverage: PHI breaches 500+ individuals, since 2009")

# Note: HHS OCR requires browser-based search, not direct API
# Alternative: Use publicly available downloadable dataset if available

print("\n  NOTE: HHS OCR does not expose programmatic API")
print("  Options to retrieve data:")
print("    1. Download CSV from OCR portal (if available)")
print("    2. Use web scraping (Selenium/BeautifulSoup)")
print("    3. Manual lookup for high-priority firms")

# Create template for HHS OCR data
hhs_template = pd.DataFrame({
    'org_name': [],
    'breach_date_ocr': [],
    'individuals_affected': [],
    'breach_type': [],
    'state': [],
    'ocr_health_breach': [],  # Boolean
})

output_path = Path("Data/hhs/ocr_health_breaches_TEMPLATE.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
hhs_template.to_csv(output_path, index=False)

print(f"\n  Template created: {output_path}")

# ============================================================================
# STEP 3: Alternative - Try web scraping if Selenium available
# ============================================================================
print("\n[3/5] Attempting automated retrieval (if Selenium available)...")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import time as time_lib

    print("  Selenium available - attempting OCR portal scraping")

    # Note: This would require browser automation setup
    print("  (Requires Chrome/Firefox driver configuration)")
    print("  Skipping automated scraping for now - manual lookup recommended")

except ImportError:
    print("  Selenium not available - skipping automated scraping")
    print("  Recommend: Manual lookup from HHS OCR portal or data download")

# ============================================================================
# STEP 4: Pre-specification for H4 revision
# ============================================================================
print("\n[4/5] Pre-specification for H4 health classification...")

print("""
PRE-SPECIFIED COMPARISON:

  PRC health_breach field:
    - Source: Self-reported breach description
    - Accuracy: Unknown (private database)
    - Count: {df['health_breach'].sum()} breaches in dissertation

  HHS OCR health_breach (if obtained):
    - Source: Regulatory reporting (HIPAA compliance)
    - Accuracy: 100% (ground truth for HIPAA-reportable breaches)
    - Coverage: PHI breaches 500+ individuals only

EXPECTED FINDINGS:

  Sensitivity (recall):
    - Proportion of PRC health breaches also in HHS OCR
    - If low: PRC missed many health breaches or classified too broadly
    - If high: PRC and HHS OCR largely agree on health classification

  Specificity:
    - Proportion of non-health PRC breaches NOT in HHS OCR
    - Should be high (HHS won't misclassify non-health)

REVISION OPTIONS:

  Option A (High agreement >0.90):
    - No action needed
    - Conclude: H4 classification is robust
    - H4 null findings stand

  Option B (Moderate agreement 0.70-0.90):
    - Run H4 with both PRC and HHS OCR classifications
    - Show whether null persists with HHS definition
    - Pre-register both specs in robustness section

  Option C (Low agreement <0.70):
    - Use HHS OCR as definitive health classification
    - Re-run H4 regression with HHS-based health_breach
    - Could sharpen H4 estimate if measurement error was suppressing effect

DECISION RULE (Pre-specified):
  - Retrieve HHS OCR data for all dissertation health claims
  - Pre-register classification method before re-running H4
  - Report both PRC and HHS results to show robustness
  - Only revise main spec if agreement is low (<0.70)
""".format(df=df))

# ============================================================================
# STEP 5: Instructions for manual OCR lookup
# ============================================================================
print("\n[5/5] Manual HHS OCR Lookup Instructions...")

print("""
MANUAL RETRIEVAL FROM HHS OCR PORTAL:

1. Visit: https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf

2. For each organization in dissertation:
   a. Enter organization name in search box
   b. Set date range: breach_date +/- 30 days
   c. Search
   d. Record: Breach name, date, individuals affected, state
   e. Record: Whether appears in OCR breach list (yes/no)

3. Export results as CSV

ALTERNATIVE - Batch Download:

  HHS OCR publishes consolidated breach list:
    https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf
    (Check for downloadable CSV option)

EXPECTED TIME:
  - Manual: ~30-60 min for ~50 health-related organizations
  - Automated (if successful): ~5-10 min after Selenium setup

Once OCR data obtained:
  1. Save to: Data/hhs/ocr_health_breaches.csv
  2. Run script 113_merge_ocr_classification.py
  3. Compare PRC vs OCR classifications
  4. Re-run H4 regression with HHS-based health measure
""")

print("\n" + "=" * 80)
print("NEXT: Obtain HHS OCR breach portal data, then merge with dissertation")
print("      Script 113_merge_ocr_classification.py")
print("=" * 80)
