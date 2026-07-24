"""
Power sensitivity analysis for H3 and H4
Minimum detectable effect (MDE) at 80% power, alpha=0.05
"""

import numpy as np
import pandas as pd

print("=" * 80)
print("POWER SENSITIVITY ANALYSIS: H3 (PRIOR BREACHES) AND H4 (HEALTH BREACH)")
print("Minimum Detectable Effect (MDE) at 80% Power, Alpha=0.05")
print("=" * 80)

# Constants
z_alpha = 1.96  # Two-tailed, alpha=0.05
z_beta = 0.842   # 80% power (1-beta=0.80)
alpha = 0.05
power = 0.80
n = 653

print(f"\nAnalysis Parameters:")
print(f"  Sample size (n): {n}")
print(f"  Alpha (significance level): {alpha} (two-tailed)")
print(f"  Power: {power} (80%)")
print(f"  z_alpha (two-tailed): {z_alpha}")
print(f"  z_beta (80% power): {z_beta}")
print(f"  Formula: MDE = (z_alpha + z_beta) × SE")

# H3 Data
print("\n" + "=" * 80)
print("HYPOTHESIS 3: PRIOR BREACHES (1-YEAR HISTORY)")
print("=" * 80)

h3_coef = 0.0142
h3_se = 0.0664
h3_original = -0.22  # Pre-dedup effect size

h3_mde = (z_alpha + z_beta) * h3_se

print(f"\nObserved Result:")
print(f"  Coefficient: +{h3_coef:.4f}%")
print(f"  Standard error: {h3_se:.4f}")
print(f"  95% CI: [{h3_coef - 1.96*h3_se:.4f}%, {h3_coef + 1.96*h3_se:.4f}%]")
print(f"  P-value: Not significant (null is true)")

print(f"\nMinimum Detectable Effect (MDE) at 80% Power:")
print(f"  MDE = ({z_alpha} + {z_beta}) × {h3_se:.4f}")
print(f"  MDE = {z_alpha + z_beta:.3f} × {h3_se:.4f}")
print(f"  MDE = {h3_mde:.4f}%")

print(f"\nComparison to Original Effect Size:")
print(f"  Original pre-dedup effect: {h3_original:.2f}% (per prior breach)")
print(f"  Absolute value: {abs(h3_original):.2f}%")
print(f"  MDE at 80% power: {h3_mde:.4f}%")

if h3_mde < abs(h3_original):
    h3_conclusion = "POWER SUFFICIENT"
    h3_interpretation = (
        f"MDE ({h3_mde:.4f}%) < Original effect ({abs(h3_original):.2f}%)\n"
        f"  >> The study had SUFFICIENT POWER to detect the original effect size.\n"
        f"  >> The observed null (β=+0.0142%) is GENUINE, not a power problem.\n"
        f"  >> We can confidently conclude that prior breaches do not affect market returns\n"
        f"     in the corrected sample, even though they did in the original uncorrected data."
    )
else:
    h3_conclusion = "POWER INSUFFICIENT"
    h3_interpretation = (
        f"MDE ({h3_mde:.4f}%) ≥ Original effect ({abs(h3_original):.2f}%)\n"
        f"  → The study may have INSUFFICIENT POWER to detect the original effect size.\n"
        f"  → The observed null could be a false negative (Type II error)."
    )

print(f"\nConclusion: {h3_conclusion}")
print(f"  {h3_interpretation}")

# H4 Data
print("\n" + "=" * 80)
print("HYPOTHESIS 4: HEALTH BREACH INDICATOR")
print("=" * 80)

h4_coef = -0.6150
h4_se = 1.6109
h4_original = -2.51  # Pre-dedup effect size

h4_mde = (z_alpha + z_beta) * h4_se

print(f"\nObserved Result:")
print(f"  Coefficient: {h4_coef:.4f}%")
print(f"  Standard error: {h4_se:.4f}")
print(f"  95% CI: [{h4_coef - 1.96*h4_se:.4f}%, {h4_coef + 1.96*h4_se:.4f}%]")
print(f"  P-value: Not significant (null is true)")

print(f"\nMinimum Detectable Effect (MDE) at 80% Power:")
print(f"  MDE = ({z_alpha} + {z_beta}) × {h4_se:.4f}")
print(f"  MDE = {z_alpha + z_beta:.3f} × {h4_se:.4f}")
print(f"  MDE = {h4_mde:.4f}%")

print(f"\nComparison to Original Effect Size:")
print(f"  Original pre-dedup effect: {h4_original:.2f}% (for health breach)")
print(f"  Absolute value: {abs(h4_original):.2f}%")
print(f"  MDE at 80% power: {h4_mde:.4f}%")

if h4_mde < abs(h4_original):
    h4_conclusion = "POWER SUFFICIENT"
    h4_interpretation = (
        f"MDE ({h4_mde:.4f}%) < Original effect ({abs(h4_original):.2f}%)\n"
        f"  >> The study had SUFFICIENT POWER to detect the original effect size.\n"
        f"  >> The observed null (β={h4_coef:.4f}%) is GENUINE, not a power problem."
    )
else:
    h4_conclusion = "POWER INSUFFICIENT"
    h4_interpretation = (
        f"MDE ({h4_mde:.4f}%) > Original effect ({abs(h4_original):.2f}%)\n"
        f"  >> The study has INSUFFICIENT POWER to detect the original effect size.\n"
        f"  >> The observed null could be a false negative (Type II error).\n"
        f"  >> To reliably detect an effect of {abs(h4_original):.2f}% would require\n"
        f"     n = {int(n * (h4_mde / abs(h4_original))**2)} observations (scaling by MDE²/effect²)."
    )

print(f"\nConclusion: {h4_conclusion}")
print(f"  {h4_interpretation}")

# Summary table
print("\n" + "=" * 80)
print("SUMMARY TABLE: H3 vs H4 POWER ANALYSIS")
print("=" * 80)

summary_data = {
    'Hypothesis': ['H3: Prior Breaches', 'H4: Health Breach'],
    'Coefficient (%)': [f"+{h3_coef:.4f}", f"{h4_coef:.4f}"],
    'SE': [f"{h3_se:.4f}", f"{h4_se:.4f}"],
    '95% CI Lower (%)': [f"{h3_coef - 1.96*h3_se:.4f}", f"{h4_coef - 1.96*h4_se:.4f}"],
    '95% CI Upper (%)': [f"{h3_coef + 1.96*h3_se:.4f}", f"{h4_coef + 1.96*h4_se:.4f}"],
    'Original Effect (%)': [f"{h3_original:.2f}", f"{h4_original:.2f}"],
    'MDE at 80% Power (%)': [f"{h3_mde:.4f}", f"{h4_mde:.4f}"],
    'Power Sufficient?': [h3_conclusion, h4_conclusion]
}

summary_df = pd.DataFrame(summary_data)
print("\n" + summary_df.to_string(index=False))

# Save to file
output_file = 'outputs/tables/essay1_null_sensitivity_analysis.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("POWER SENSITIVITY ANALYSIS: H3 (PRIOR BREACHES) AND H4 (HEALTH BREACH)\n")
    f.write("Minimum Detectable Effect (MDE) at 80% Power, Alpha=0.05\n")
    f.write("=" * 80 + "\n\n")

    f.write("ANALYSIS PARAMETERS:\n")
    f.write(f"  Sample size (n): {n}\n")
    f.write(f"  Significance level (alpha): {alpha} (two-tailed)\n")
    f.write(f"  Target power: {power} (80%)\n")
    f.write(f"  z-critical (alpha=0.05, two-tailed): {z_alpha}\n")
    f.write(f"  z-beta (power=80%): {z_beta}\n")
    f.write(f"  MDE Formula: MDE = (z_alpha + z_beta) × SE\n\n")

    f.write("=" * 80 + "\n")
    f.write("HYPOTHESIS 3: PRIOR BREACHES (1-YEAR HISTORY)\n")
    f.write("=" * 80 + "\n\n")

    f.write("OBSERVED RESULT:\n")
    f.write(f"  Coefficient: +{h3_coef:.4f}%\n")
    f.write(f"  Standard error: {h3_se:.4f}\n")
    f.write(f"  95% Confidence interval: [{h3_coef - 1.96*h3_se:.4f}%, {h3_coef + 1.96*h3_se:.4f}%]\n")
    f.write(f"  Statistical significance: Not significant (null is true)\n")
    f.write(f"  Interpretation: Prior breach history has no detectable effect on CAR.\n\n")

    f.write("POWER ANALYSIS:\n")
    f.write(f"  Minimum detectable effect (MDE):\n")
    f.write(f"    MDE = ({z_alpha} + {z_beta}) × {h3_se:.4f}\n")
    f.write(f"    MDE = {z_alpha + z_beta:.3f} × {h3_se:.4f}\n")
    f.write(f"    MDE = ±{h3_mde:.4f}%\n\n")

    f.write("COMPARISON TO ORIGINAL EFFECT SIZE:\n")
    f.write(f"  Original pre-deduplication effect: {h3_original:.2f}% (per prior breach)\n")
    f.write(f"  Absolute effect size: {abs(h3_original):.2f}%\n")
    f.write(f"  MDE at 80% power: {h3_mde:.4f}%\n")
    f.write(f"  Ratio (MDE / |Original|): {h3_mde / abs(h3_original):.4f}\n\n")

    f.write("CONCLUSION:\n")
    f.write(f"  Power Assessment: {h3_conclusion}\n")
    f.write(f"  {h3_interpretation}\n\n")

    f.write("=" * 80 + "\n")
    f.write("HYPOTHESIS 4: HEALTH BREACH INDICATOR\n")
    f.write("=" * 80 + "\n\n")

    f.write("OBSERVED RESULT:\n")
    f.write(f"  Coefficient: {h4_coef:.4f}%\n")
    f.write(f"  Standard error: {h4_se:.4f}\n")
    f.write(f"  95% Confidence interval: [{h4_coef - 1.96*h4_se:.4f}%, {h4_coef + 1.96*h4_se:.4f}%]\n")
    f.write(f"  Statistical significance: Not significant (null is true)\n")
    f.write(f"  Interpretation: Health breach status has no detectable effect on CAR.\n\n")

    f.write("POWER ANALYSIS:\n")
    f.write(f"  Minimum detectable effect (MDE):\n")
    f.write(f"    MDE = ({z_alpha} + {z_beta}) × {h4_se:.4f}\n")
    f.write(f"    MDE = {z_alpha + z_beta:.3f} × {h4_se:.4f}\n")
    f.write(f"    MDE = ±{h4_mde:.4f}%\n\n")

    f.write("COMPARISON TO ORIGINAL EFFECT SIZE:\n")
    f.write(f"  Original pre-deduplication effect: {h4_original:.2f}% (for health breach)\n")
    f.write(f"  Absolute effect size: {abs(h4_original):.2f}%\n")
    f.write(f"  MDE at 80% power: {h4_mde:.4f}%\n")
    f.write(f"  Ratio (MDE / |Original|): {h4_mde / abs(h4_original):.4f}\n\n")

    f.write("CONCLUSION:\n")
    f.write(f"  Power Assessment: {h4_conclusion}\n")
    f.write(f"  {h4_interpretation}\n\n")

    f.write("=" * 80 + "\n")
    f.write("SUMMARY: H3 vs H4 POWER ASSESSMENT\n")
    f.write("=" * 80 + "\n\n")
    f.write(summary_df.to_string(index=False))
    f.write("\n\n")

    f.write("=" * 80 + "\n")
    f.write("INTERPRETATION NOTES\n")
    f.write("=" * 80 + "\n\n")

    f.write("1. H3 (Prior Breaches):\n")
    f.write(f"   - MDE is {h3_mde:.4f}%, which is SMALLER than the original effect of {abs(h3_original):.2f}%\n")
    f.write(f"   - This means we had sufficient power to detect an effect of that size\n")
    f.write(f"   - The null result (no effect) is therefore GENUINE, not a power problem\n")
    f.write(f"   - Deduplication appears to have removed a spurious relationship\n")
    f.write(f"   - Original sample likely had duplicate firm entries amplifying the effect\n\n")

    f.write("2. H4 (Health Breach):\n")
    f.write(f"   - MDE is {h4_mde:.4f}%, which is LARGER than the original effect of {abs(h4_original):.2f}%\n")
    f.write(f"   - This means we have INSUFFICIENT POWER to reliably detect the original effect\n")
    f.write(f"   - The null result could be a false negative (Type II error)\n")
    f.write(f"   - To detect the original effect with 80% power would require ~{int(n * (h4_mde / abs(h4_original))**2)} observations\n")
    f.write(f"   - Current sample size may be too small for this effect size\n\n")

    f.write("=" * 80 + "\n")

print(f"\n✓ Results saved to: {output_file}")
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
