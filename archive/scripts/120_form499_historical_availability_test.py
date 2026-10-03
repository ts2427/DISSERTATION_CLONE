"""
SCRIPT 120: FORM 499 HISTORICAL AVAILABILITY TEST
===================================================

Gate test: Does Form 499 API return registration_date AND termination_date
for a known deregistered carrier, or only current status?

This determines whether Form 499 can classify firms at breach_date or only today.

Outcome:
  - If termination_date IS returned: Full date-aware matching possible
  - If termination_date NOT returned: Current-status-only limitation, document it

Run this BEFORE any other Form 499 work.
"""

import requests
import json
from datetime import datetime
from urllib.parse import urlencode

print("=" * 80)
print("FORM 499 HISTORICAL AVAILABILITY TEST")
print("=" * 80)

# ============================================================================
# TEST CASE: A known carrier that deregistered mid-sample
# ============================================================================
print("\nTest carrier: Sprint Nextel Corporation")
print("  Expected: Deregistered ~2020 (merged with T-Mobile)")
print("  Registration should show a termination_date or similar")

# Sprint's CIK for reference (for Name search)
test_firm_name = "Sprint Nextel Corporation"
test_firm_states = ["KS", "MO"]  # Sprint headquarters

print(f"\nSearching Form 499 filer database for: {test_firm_name}")

# ============================================================================
# APPROACH 1: Direct URL query to Form 499 filer search
# ============================================================================
print("\nAttempt 1: Direct URL query to Form 499 search...")

# Form 499 filer search base URL
form499_search_url = "https://apps.fcc.gov/cgb/form499/frmMain.cfm"

# Try search with URL parameters (if Form 499 API supports it)
params = {
    'companyname': test_firm_name,
    'strstate': ','.join(test_firm_states),
    'frn': '',  # Leave empty for name search
}

print(f"\nURL: {form499_search_url}")
print(f"Params: {params}")

headers = {
    'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'
}

try:
    response = requests.get(form499_search_url, params=params, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print(f"Response length: {len(response.text)} bytes")

        # Try to extract registration dates from HTML
        import re
        reg_dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', response.text)
        term_dates = re.findall(r'(?:Term|Deregister|Ended).*?(\d{1,2}/\d{1,2}/\d{4})', response.text, re.IGNORECASE)

        print(f"\nDates found in response:")
        print(f"  Registration dates: {reg_dates[:5] if reg_dates else 'None found'}")
        print(f"  Termination dates: {term_dates[:5] if term_dates else 'None found'}")

        if not term_dates:
            print("\n  WARNING: No termination dates found in HTML response")
            print("  This suggests Form 499 may only return current status")
    else:
        print(f"Query failed: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# APPROACH 2: Try FRN-based search (if we know Sprint's FRN)
# ============================================================================
print("\n" + "=" * 80)
print("Attempt 2: Direct FCC Form 499 portal XML search...")

# The FCC Form 499 portal has XML export capability
# URL pattern: https://apps.fcc.gov/cgb/form499/...

fcc_portal_url = "https://apps.fcc.gov/cgb/form499/frmMain.cfm"

print(f"\nTarget: {fcc_portal_url}")
print("\nNote: Form 499 portal requires browser-based interaction")
print("Attempting direct query without JavaScript rendering...")

try:
    # Try JSON/XML API if available
    xml_url = "https://apps.fcc.gov/cgb/form499/frmMain.cfm?output=xml"
    response = requests.get(xml_url, headers=headers, timeout=10)

    if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
        print("✓ XML endpoint found")
        # Parse XML
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(response.text)
            print(f"  Root tag: {root.tag}")

            # Look for registration/termination date fields
            for elem in root.iter():
                if 'date' in elem.tag.lower() or 'term' in elem.tag.lower():
                    print(f"  Found date field: {elem.tag}")
        except:
            print("  XML parsing failed")
    else:
        print("✗ XML endpoint not available or wrong content-type")

except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# DECISION POINT
# ============================================================================
print("\n" + "=" * 80)
print("HISTORICAL DATA ASSESSMENT")
print("=" * 80)

print("""
Based on test queries:

SCENARIO A: Historical dates ARE returned (registration_date + termination_date)
  ✓ Can classify firms at breach_date (2006-2025)
  ✓ Proceed with date-aware Form 499 matching
  ✓ Script: Query filer database with date range checks

SCENARIO B: Only current status returned (no historical dates)
  ✗ Can only classify firms as current filers
  ✗ Cannot determine status at breach_date (2006-2015)
  ✗ Document limitation: "Form 499 classification uses 2026 registry status.
     Historical filer status for 2006-2015 breaches is unavailable."
  ✗ Proceed with current-status-only approach, note caveat in H2 spec

NEXT STEP:
  Based on above outcomes, proceed to Script 121 (full Form 499 lookup)
  or document the limitation and use current registry only.
""")

print("=" * 80)
print("\nGate test complete. Review historical data availability above.")
print("Status: AWAITING MANUAL REVIEW OF FORM 499 PORTAL")
print("=" * 80)
