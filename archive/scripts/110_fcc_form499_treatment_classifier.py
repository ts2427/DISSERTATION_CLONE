"""
SCRIPT 110: H2 TREATMENT CLASSIFICATION FROM FCC FORM 499 FILER DATABASE
=========================================================================

HIGH-IMPACT DATA SOURCE (Closest to Decisive)

Problem: Current H2 uses SIC codes as proxy for FCC § 64.2011 coverage
Solution: Use FCC Form 499 Filer Database - the actual regulatory population

Form 499 covers:
  - Interstate telecommunications carriers (ITC)
  - Interconnected VoIP providers
  - Certain other interstate telecom providers
  - Annual registration via USAC (Universal Service Fund)

Source: apps.fcc.gov/cgb/form499 (XML/JSON, searchable, free, public)
Identifiers: FRN (Filer Registration Number) + Filer ID
Coverage: Registration dates (not just current status)

Expected Impact:
  - Will catch VoIP providers SIC codes miss
  - Will catch subsidiary filers not identified by parent SIC
  - May substantially expand treated group (N of FCC firms)
  - If N expands meaningfully, shrinks inference problem for H2

Pre-specification: Match by company name against Form 499 registry,
flag by FRN assignment date vs breach date for period coverage.
"""

import requests
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

print("=" * 80)
print("SCRIPT 110: FCC FORM 499 FILER DATABASE CLASSIFICATION")
print("=" * 80)

# ============================================================================
# STEP 1: Load dissertation dataset
# ============================================================================
print("\n[1/4] Loading dissertation dataset...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')
print(f"  Total records: {len(df)}")

# Get unique firms
unique_firms = df[['resolved_cik', 'org_name']].drop_duplicates()
print(f"  Unique firms: {len(unique_firms)}")

# ============================================================================
# STEP 2: Query FCC Form 499 Filer Database
# ============================================================================
print("\n[2/4] Querying FCC Form 499 Filer Database...")
print("  Note: This queries the public USAC database at apps.fcc.gov/cgb/form499")

# FCC Form 499 API endpoint
form499_url = "https://apps.fcc.gov/cgb/form499/Form499Main.cfm"

print(f"  Target database: FCC Form 499 Filer Registry")
print(f"  Expected to match: ~{len(unique_firms)} unique firms against ~2000+ active filers")

# For now, create placeholder for manual/batch retrieval
# (FCC doesn't expose programmatic API, but XML exports available via portal)

form499_results = []

# Pre-specification: Companies we expect to find in Form 499
expected_fcc_filers = {
    'AT&T': True,  # Major ITC
    'T-Mobile': True,  # Major ITC
    'Verizon': True,  # Major ITC
    'Comcast': True,  # ITC
    'Charter': True,  # ITC
    'CenturyLink': True,  # ITC
    'Frontier': True,  # ITC
    'Windstream': True,  # ITC
    'Sprint': True,  # Now T-Mobile (historical)
    'Cricket': True,  # VoIP provider (AT&T subsidiary)
    'Boost': True,  # VoIP provider (DISH subsidiary)
    'Vonage': True,  # VoIP provider
    'MagicJack': True,  # VoIP provider
    'Ooma': True,  # VoIP provider
}

print("\n  Pre-specified FCC filers to match:")
for filer, _ in list(expected_fcc_filers.items())[:10]:
    print(f"    - {filer}")
print(f"    ... and {len(expected_fcc_filers) - 10} more")

# ============================================================================
# STEP 3: Manual lookup instructions (until programmatic API available)
# ============================================================================
print("\n[3/4] Form 499 Retrieval Instructions")
print("-" * 80)

print("""
MANUAL STEPS (FCC does not expose programmatic API):

1. Visit: https://apps.fcc.gov/cgb/form499/
2. Click "Search Filer Database"
3. For each firm in dataset:
   a. Search by company name
   b. Record: FRN (Filer Registration Number)
   c. Record: Filer ID
   d. Record: Registration Date
   e. Record: Filer Category (ITC / VoIP / Other)

4. Export as CSV or JSON (portal supports both)

Alternatively, request FCC dataset via:
  - FOIA request to Wireline Competition Bureau
  - USAC technical contact for bulk registry

Expected Coverage: ~95% of dissertation FCC firms should appear in Form 499
Expected New Coverage: VoIP subsidiaries not in SIC classification
Expected Sample Impact: Potential expansion of treated group (N of FCC firms)

Once Form 499 data obtained, match to dissertation dataset by:
  - Firm name normalization
  - CIK to FRN cross-reference (if available)
  - Registration date coverage at breach_date
""")

# ============================================================================
# STEP 4: Placeholder for Form 499 data (to be populated manually)
# ============================================================================
print("\n[4/4] Placeholder for Form 499 results...")

# For now, create template structure
form499_template = pd.DataFrame({
    'org_name': [],
    'frn': [],
    'filer_id': [],
    'category': [],  # ITC, VoIP, Other
    'registration_date': [],
    'form499_filer': [],  # Boolean
})

output_path = Path("Data/fcc/form499_filer_results_TEMPLATE.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
form499_template.to_csv(output_path, index=False)

print(f"\nTemplate created: {output_path}")
print(f"Rows: {len(form499_template)} (populate manually from FCC portal)")

print("\n" + "=" * 80)
print("NEXT STEP: MANUAL FORM 499 LOOKUP")
print("=" * 80)
print("""
Pre-specification: We will match dissertation firms against FCC Form 499 registry.
  - Firms appearing in Form 499 = FCC § 64.2011 filers (definitive classification)
  - Filers NOT in Form 499 = non-covered carriers (reclassify as control)
  - Expected precision: 100% (FCC registry is ground truth)
  - Expected impact on H2: Sample size may expand if VoIP/subsidiary filers added

Once Form 499 data obtained:
  1. Import to Data/fcc/form499_filers.csv
  2. Run script 111_match_form499_to_dissertation.py
  3. Regenerate H2 classification and re-run H2 regressions
  4. Compare to SIC-based classification
""")

print("=" * 80)
