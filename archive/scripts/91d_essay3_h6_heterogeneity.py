"""
ESSAY 3: H6 ROBUSTNESS - BREACH-CAUSE HETEROGENEITY

Two tests across 30d/90d/180d windows:
  Test 1: Does the FCC effect on turnover differ by breach cause?
          -> answers "your aggregate null hides offsetting subgroups"
  Test 2: Does breach cause itself drive turnover, FCC aside?
          -> the "boards do respond to culpability, not timing" finding (Banker & Feng)

Writes to: outputs/tables/essay3_governance/essay3_h6_heterogeneity.csv
Machine-written. No hand transcription.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("ESSAY 3: H6 ROBUSTNESS - BREACH-CAUSE HETEROGENEITY")
print("=" * 90)

# Load data
DATA_PATH = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(DATA_PATH)

# Filter to analysis sample (match script 91/91b exactly)
analysis_df = df[df['has_crsp_data'] == True].copy()
turnover_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['immediate_disclosure'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

bool_cols = turnover_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    turnover_df[col] = turnover_df[col].astype(int)

print(f"\n[Sample] {len(turnover_df):,} breaches with complete data")

# ============================================================================
# PRE-SPECIFY breach cause from Banker & Feng (2019)
# Do NOT tune after seeing results, or the positive finding looks like fishing.
# System deficiency = firm's own security/process failure
# (misconfiguration, unintended disclosure, lost/stolen unencrypted device, poor security)
# Map YOUR breach-type codes here and document in appendix.
# ============================================================================

print("\n[Defining system_deficiency from Banker & Feng (2019)]")
print("  Breach type mapping (breach_type column):")
print("  System deficiency (1): DISC (unintended disclosure), PORT (portable device), PHYS (physical loss)")
print("  External/Other (0): HACK (hacking/malicious), INSD (insider threat/intentional)")

# Map breach types to system deficiency based on Banker & Feng (2019)
# Internal failures (system deficiency = 1):
#   - DISC: Unintended disclosure (configuration error)
#   - PORT: Portable device loss/theft (unencrypted)
#   - PHYS: Physical device loss/theft
# External attacks (system deficiency = 0):
#   - HACK: Hacking/malicious external attack
#   - INSD: Insider threat (intentional malicious act)

if 'breach_type' in turnover_df.columns:
    sysdef_types = {'DISC', 'PORT', 'PHYS'}
    turnover_df['system_deficiency'] = turnover_df['breach_type'].isin(sysdef_types).astype(int)
    print(f"\n  Mapped from breach_type column:")
    print(f"    System deficiency (1): {turnover_df['system_deficiency'].sum()}")
    print(f"    Other/External (0): {(1 - turnover_df['system_deficiency']).sum()}")
else:
    raise ValueError("No breach_type column found in dataset. Cannot map system_deficiency.")

print(f"  System deficiency breaches: {(turnover_df['system_deficiency'] == 1).sum()}")
print(f"  Other breaches: {(turnover_df['system_deficiency'] == 0).sum()}")

# ============================================================================
# HETEROGENEITY ANALYSIS
# ============================================================================

def discrete_ame_pp(res, data, var, mask=None):
    """Average change in predicted probability from flipping a 0/1 var, in pp.
    Restrict to a subgroup with `mask` to get a within-group AME."""
    d = data if mask is None else data[mask]
    d0 = d.copy()
    d0[var] = 0
    d1 = d.copy()
    d1[var] = 1
    return 100.0 * (res.predict(d1) - res.predict(d0)).mean()


windows = {'30d': 'executive_change_30d', '90d': 'executive_change_90d', '180d': 'executive_change_180d'}
controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

rows = []

for window_label, dv_col in windows.items():
    print(f"\n[{window_label.upper()} WINDOW]")

    # Prepare data for this window
    needed = [dv_col, 'fcc_reportable', 'system_deficiency'] + controls
    model_data = turnover_df[needed].dropna().copy()
    model_data[dv_col] = model_data[dv_col].astype(int)

    print(f"  Sample: {len(model_data):,}")

    # Model with interaction: turnover ~ fcc * system_deficiency + controls
    formula = f"{dv_col} ~ fcc_reportable * system_deficiency + " + " + ".join(controls)

    try:
        res = smf.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

        # Extract interaction term
        interaction_names = [n for n in res.params.index
                           if 'fcc_reportable:system_deficiency' in n or
                              'system_deficiency:fcc_reportable' in n]

        if len(interaction_names) == 0:
            print(f"  [WARNING] Interaction term not found in model. Skipping.")
            continue

        interaction_name = interaction_names[0]
        interaction_coef = res.params[interaction_name]
        interaction_p = res.pvalues[interaction_name]

        # Test 2: Does system_deficiency itself drive turnover? (boards responding to culpability)
        sysdef_ame = discrete_ame_pp(res, model_data, 'system_deficiency')

        # Test 1: FCC effect within each breach-cause subgroup
        # FCC effect for system-deficiency breaches (system_deficiency = 1)
        fcc_ame_sysdef1 = discrete_ame_pp(res, model_data, 'fcc_reportable',
                                         mask=(model_data['system_deficiency'] == 1))

        # FCC effect for non-system-deficiency breaches (system_deficiency = 0)
        fcc_ame_sysdef0 = discrete_ame_pp(res, model_data, 'fcc_reportable',
                                         mask=(model_data['system_deficiency'] == 0))

        # Cell counts for power assessment
        n_sysdef1 = int((model_data['system_deficiency'] == 1).sum())
        n_sysdef0 = int((model_data['system_deficiency'] == 0).sum())
        n_fcc_and_sysdef1 = int(((model_data['system_deficiency'] == 1) &
                                  (model_data['fcc_reportable'] == 1)).sum())
        n_fcc_and_sysdef0 = int(((model_data['system_deficiency'] == 0) &
                                  (model_data['fcc_reportable'] == 1)).sum())

        print(f"  System deficiency effect: {sysdef_ame:.2f}pp (p={res.pvalues['system_deficiency']:.4f})")
        print(f"  FCC effect | sysdef=1: {fcc_ame_sysdef1:.2f}pp (n={n_fcc_and_sysdef1})")
        print(f"  FCC effect | sysdef=0: {fcc_ame_sysdef0:.2f}pp (n={n_fcc_and_sysdef0})")
        print(f"  Interaction p-value: {interaction_p:.4f}")

        rows.append({
            'window': window_label,
            'n': int(res.nobs),
            # Test 2: Breach cause drives turnover? (boards respond to culpability)
            'sysdef_main_ame_pp': round(sysdef_ame, 2),
            'sysdef_main_p': round(res.pvalues['system_deficiency'], 4),
            # Test 1: FCC effect heterogeneity by breach cause
            'fcc_ame_sysdef1_pp': round(fcc_ame_sysdef1, 2),
            'fcc_ame_sysdef0_pp': round(fcc_ame_sysdef0, 2),
            'interaction_coef': round(interaction_coef, 4),
            'interaction_p': round(interaction_p, 4),
            # Cell sizes - govern power of interaction test
            'n_sysdef1': n_sysdef1,
            'n_sysdef0': n_sysdef0,
            'n_fcc_and_sysdef1': n_fcc_and_sysdef1,
            'n_fcc_and_sysdef0': n_fcc_and_sysdef0,
        })

    except Exception as e:
        print(f"  [ERROR] Model failed: {e}")
        continue

# Save results
out = pd.DataFrame(rows)
out.to_csv('outputs/tables/essay3_governance/essay3_h6_heterogeneity.csv', index=False)

print("\n" + "=" * 90)
print("HETEROGENEITY RESULTS")
print("=" * 90)
print(out.to_string(index=False))
print(f"\nSaved -> outputs/tables/essay3_governance/essay3_h6_heterogeneity.csv")

print("\n" + "=" * 90)
print("INTERPRETATION")
print("=" * 90)

print("\nTest 2 (System deficiency main effect):")
print("  - If sysdef_main_ame_pp is positive and significant (like Banker & Feng),")
print("    boards DO respond to breach culpability.")
print("  - This reinforces the FCC null: governance activates, just not to timing.")
print("  - Strengthens the main finding: 'boards respond to causes, not clock.'")

print("\nTest 1 (FCC effect heterogeneity):")
print("  - If fcc_ame in BOTH subgroups is near zero AND interaction_p > 0.05,")
print("    your aggregate FCC null is NOT hiding offsetting subgroups.")
print("  - This closes the standard attack on any aggregate null.")

print("\nPower caveat:")
print("  - Test 1 is the underpowered cell. Watch n_fcc_and_sysdef1.")
print("  - If that cell is thin (< 30), call the FCC × sysdef interaction")
print("    underpowered rather than a clean null.")

print("\n" + "=" * 90)
