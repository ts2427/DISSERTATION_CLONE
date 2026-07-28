"""
SCRIPT 122: MANUAL FORM 499 CORRECTIONS - RECOVER MAJOR CARRIERS
=================================================================

Apply two-clause rule to SIC-flagged unmatched firms:
  (a) Direct Form 499 filer, OR
  (b) Parent brand of Form 499 filer + telecom/subscriber operation

This recovers Comcast, Charter, Frontier, Altice, AT&T Services variants.

Input:  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv
Output: Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv
        outputs/form499_manual_corrections_applied.txt
"""

import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 80)
print("SCRIPT 122: MANUAL FORM 499 CORRECTIONS")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n1. LOADING DATA...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv')
print(f"   Loaded: {len(df)} rows")

# Get H2 sample
h2_sample = df[df['has_crsp_data'] == 1].copy()
print(f"   H2 sample: {len(h2_sample)} rows")

# ============================================================================
# APPLY MANUAL CORRECTIONS
# ============================================================================
print("\n2. APPLYING MANUAL CORRECTIONS...")

# Manual rules as dict: (org_name_pattern, should_treat, reason)
# Patterns are checked with .str.contains()

manual_rules = [
    # Comcast (parent brand + telecom operation)
    (r'Comcast$', 1, 'Parent brand (Rule 1b): Comcast Telephony Communications of Maryland'),
    (r'Comcast Cable Communications', 1, 'Parent brand (Rule 1b): Telecom subscriber operations'),

    # Charter (parent brand + telecom operation)
    (r'Charter Communication', 1, 'Parent brand (Rule 1b): Charter Communications Operating, LLC'),

    # Frontier (parent brand + telecom)
    (r'Frontier Communications', 1, 'Parent brand (Rule 1b): Frontier regional subsidiaries are Form 499 filers'),

    # Altice (parent brand + telecom)
    (r'Altice USA', 1, 'Parent brand (Rule 1b): Altice Wireless Form 499 filer'),

    # AT&T Services (parent AT&T already matched; services variant is same entity)
    (r'AT&T Services', 1, 'Parent brand (Rule 1b): AT&T Inc. is Form 499 filer'),

    # Cricket Wireless (Rule 1a - direct filer; CAUGHT DEFECT 7/28/2026: verification doc
    # confirmed FRN 0004321139 as treated, but exact matcher missed the "LLC" name variant,
    # leaving the dataset contradicting its own audit trail)
    (r'Cricket Wireless', 1, 'Direct Form 499 filer (Rule 1a): Cricket Communications, Inc., FRN 0004321139 - LLC variant missed by exact matcher'),

    # Boost Mobile (Rule 1b - adjudicated 7/28/2026: prepaid wireless brand of Form 499
    # filer parent (Sprint Spectrum LLC, FRN 0006693022); breach involves wireless
    # subscriber data - same clause (b) logic that admitted Comcast telephony)
    (r'Boost Mobile', 1, 'Parent brand (Rule 1b): prepaid wireless brand of Sprint Spectrum LLC (FRN 0006693022), breach involves subscriber data'),

    # Exclude: Not telecom entities
    (r'ATT-Breach Notification|ATT-SecurityBreach', 0, 'Artificial system entities, not telecommunications carriers'),
    (r'NBC Sports', 0, 'Unrelated segment (sports/entertainment), not telecommunications operation'),

    # DISH (adjudicated 7/28/2026 - untreated): satellite television is not a
    # telecommunications service under 47 CFR 64.2011; no documented interconnected
    # VoIP or covered-carrier operation at the breach dates; Sling/DISH wireless
    # ventures postdate the sample window. Burden of proof runs toward exclusion.
    (r'DISH Network', 0, 'Excluded: satellite TV not a telecom service under 64.2011; no covered operation documented at breach dates'),

    # Aero Charter (Failure Mode 2 instance): aviation company caught in treated
    # pool via "Charter" name-token collision under the SIC-era classification
    (r'Aero Charter', 0, 'Excluded: aviation company; name-token collision with Charter Communications (Failure Mode 2 instance)'),
]

# Count current treated/untreated
current_treated = (h2_sample['fcc_form499'] == 1).sum()
current_untreated = (h2_sample['fcc_form499'] == 0).sum()

# Apply corrections
corrections_made = []
for pattern, should_treat, reason in manual_rules:
    mask = h2_sample['org_name'].str.contains(pattern, case=False, na=False, regex=True)
    matching_rows = h2_sample[mask].copy()

    if len(matching_rows) > 0:
        # Apply correction
        old_val = matching_rows['fcc_form499'].unique()
        df.loc[df['org_name'].str.contains(pattern, case=False, na=False, regex=True) & (df['has_crsp_data'] == 1), 'fcc_form499'] = should_treat

        # Track correction
        corrections_made.append({
            'pattern': pattern,
            'n_records': len(matching_rows),
            'old_treatment': old_val[0] if len(old_val) > 0 else None,
            'new_treatment': should_treat,
            'reason': reason
        })

        print(f"   Pattern '{pattern}': {len(matching_rows)} records → fcc_form499={should_treat}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n3. CORRECTION SUMMARY")
print("=" * 80)

# Recalculate
h2_corrected = df[df['has_crsp_data'] == 1]
new_treated = (h2_corrected['fcc_form499'] == 1).sum()
new_untreated = (h2_corrected['fcc_form499'] == 0).sum()

print(f"\nH2 REGRESSION SAMPLE: {len(h2_corrected)} rows")
print(f"\nBefore corrections:")
print(f"  Treated (fcc_form499=1): {current_treated}")
print(f"  Untreated: {current_untreated}")

print(f"\nAfter corrections:")
print(f"  Treated (fcc_form499=1): {new_treated}")
print(f"  Untreated: {new_untreated}")

print(f"\nChange: +{new_treated - current_treated} observations ({100*(new_treated - current_treated)/current_treated:+.1f}%)")

# Unique treated firms
unique_treated = h2_corrected[h2_corrected['fcc_form499'] == 1]['org_name'].nunique()
print(f"Unique treated firms: {unique_treated}")

print("\n" + "=" * 80)
print("CORRECTIONS APPLIED:")
print("=" * 80)

for corr in corrections_made:
    print(f"\n  {corr['pattern']}")
    print(f"    Records: {corr['n_records']}")
    print(f"    Treatment: {corr['old_treatment']} → {corr['new_treatment']}")
    print(f"    Reason: {corr['reason']}")

# ============================================================================
# SAVE
# ============================================================================
print(f"\n4. SAVING CORRECTED DATASET...")

output_file = Path('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')
df.to_csv(output_file, index=False)
print(f"   Saved: {output_file}")

# Save summary
summary_text = f"""
================================================================================
MANUAL FORM 499 CORRECTIONS - SUMMARY
================================================================================

TWO-CLAUSE RULE APPLIED:
  (a) Treated if breached entity was Form 499 filer at breach date, OR
  (b) Treated if breached entity is parent brand of Form 499 filer + breach
      involves telecommunications/subscriber operation

CORRECTIONS MADE:
  Comcast: +10 observations (parent brand → Comcast Telephony Communications)
  Charter: +10 observations (parent brand → Charter Communications Operating)
  Frontier Communications: +3 observations (parent → regional Form 499 filers)
  Altice USA: +2 observations (parent → Altice Wireless)
  AT&T Services variants: +4 observations (parent AT&T already Form 499 filer)
  NBC Sports: -1 observation (unrelated segment, not telecom operation)
  ATT-Breach Notification: -3 observations (artificial system entities)

H2 SAMPLE RESULTS:
  Before corrections: {current_treated} treated observations
  After corrections: {new_treated} treated observations
  Delta: +{new_treated - current_treated} ({100*(new_treated - current_treated)/current_treated:+.1f}%)

EXPECTED H2 RE-ESTIMATION:
  Sample: {len(h2_corrected)} rows
  Treated: {new_treated} observations ({100*new_treated/len(h2_corrected):.1f}%)
  Coefficient: Likely still null, but better specified (major carriers included)

NEXT STEP: Re-estimate H2 with corrected Form 499 classification
================================================================================
"""

summary_file = Path('outputs/form499_manual_corrections_applied.txt')
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(f"   Saved: {summary_file}")

print("\n" + "=" * 80)
print("READY FOR H2 RE-ESTIMATION WITH CORRECTED FORM 499")
print("=" * 80)
