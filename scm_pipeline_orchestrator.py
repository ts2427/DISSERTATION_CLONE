"""
FIRM-BY-FIRM SCM PIPELINE ORCHESTRATOR
======================================

Unified pipeline that runs all SCM components:
1. Load and prepare data
2. Run firm-by-firm SCM analysis
3. Conduct statistical inference
4. Generate visualizations
5. Create results summary
"""

import subprocess
import sys
from pathlib import Path
import pandas as pd

print("\n" + "="*80)
print("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - COMPLETE PIPELINE")
print("="*80)

# Pipeline stages
stages = [
    ("Data Loading", "firm_by_firm_scm_simple.py", "Compute firm-level synthetic controls"),
    ("Statistical Inference", "scm_statistical_inference.py", "Run permutation tests and bootstrap CIs"),
    ("Visualizations", "scm_visualizations.py", "Generate result plots"),
]

completed = 0
failed = 0

# ============================================================================
# STAGE 1: FIRM-BY-FIRM SCM ANALYSIS
# ============================================================================

print("\n[1/3] RUNNING FIRM-BY-FIRM SCM ANALYSIS")
print("-" * 80)

try:
    result = subprocess.run([sys.executable, "firm_by_firm_scm_simple.py"],
                          capture_output=False)
    if result.returncode == 0:
        print("[OK] SCM analysis completed successfully")
        completed += 1
    else:
        print("[ERROR] SCM analysis failed")
        failed += 1
except Exception as e:
    print(f"[ERROR] Failed to run SCM analysis: {e}")
    failed += 1

# ============================================================================
# STAGE 2: STATISTICAL INFERENCE
# ============================================================================

print("\n[2/3] RUNNING STATISTICAL INFERENCE")
print("-" * 80)

try:
    result = subprocess.run([sys.executable, "scm_statistical_inference.py"],
                          capture_output=False)
    if result.returncode == 0:
        print("[OK] Statistical inference completed successfully")
        completed += 1
    else:
        print("[ERROR] Statistical inference failed")
        failed += 1
except Exception as e:
    print(f"[ERROR] Failed to run inference: {e}")
    failed += 1

# ============================================================================
# STAGE 3: VISUALIZATIONS
# ============================================================================

print("\n[3/3] GENERATING VISUALIZATIONS")
print("-" * 80)

try:
    result = subprocess.run([sys.executable, "scm_visualizations.py"],
                          capture_output=False)
    if result.returncode == 0:
        print("[OK] Visualizations completed successfully")
        completed += 1
    else:
        print("[ERROR] Visualization generation failed")
        failed += 1
except Exception as e:
    print(f"[ERROR] Failed to generate visualizations: {e}")
    failed += 1

# ============================================================================
# CREATE RESULTS SUMMARY
# ============================================================================

print("\n[4/4] CREATING RESULTS SUMMARY")
print("-" * 80)

try:
    # Load results
    results_df = pd.read_csv("outputs/scm_firm_by_firm/scm_firm_summary_results.csv")
    inference_df = pd.read_csv("outputs/scm_firm_by_firm/scm_statistical_inference.csv")

    # Extract key metrics
    n_firms = len(results_df)
    mean_effect = results_df['mean_gap'].mean()
    median_effect = results_df['mean_gap'].median()
    std_effect = results_df['mean_gap'].std()

    inference_dict = dict(zip(inference_df['Statistic'], inference_df['Value']))
    se = inference_dict['SE']
    ci_lower = inference_dict['CI_lower_95']
    ci_upper = inference_dict['CI_upper_95']
    p_value = inference_dict['P_value_permutation']

    # Create summary
    summary_text = f"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - RESULTS SUMMARY
========================================================

AGGREGATE TREATMENT EFFECT:
  Number of firms: {n_firms}
  Mean effect: {mean_effect:.4f}%
  Median effect: {median_effect:.4f}%
  Std dev: {std_effect:.4f}%
  SE: {se:.4f}%
  95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]

STATISTICAL SIGNIFICANCE:
  Permutation test p-value: {p_value:.4f}
  Significance level: {"Significant at 5%" if p_value < 0.05 else "Not significant at 5%"}

FIRM-LEVEL EFFECTS RANGE:
  Min: {results_df['mean_gap'].min():.4f}%
  Max: {results_df['mean_gap'].max():.4f}%
  Q1: {results_df['mean_gap'].quantile(0.25):.4f}%
  Median: {median_effect:.4f}%
  Q3: {results_df['mean_gap'].quantile(0.75):.4f}%

INTERPRETATION:
The firm-by-firm synthetic control method provides a causal estimate of the FCC
regulation effect on abnormal returns. By constructing individual synthetic controls
for each FCC firm from non-FCC firms, we generate n={n_firms} independent treatment
units, addressing the n=1 concern of sector-level comparisons.

The aggregate effect of {mean_effect:.4f}% (95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%])
with permutation p={p_value:.4f} indicates {"that the regulation had a statistically significant effect" if p_value < 0.05 else "that the regulation effect is not statistically distinguishable from zero"}.
"""

    # Save summary
    summary_path = Path("outputs/scm_firm_by_firm/SCM_RESULTS_SUMMARY.txt")
    with open(summary_path, 'w') as f:
        f.write(summary_text)

    print(f"[OK] Results summary created: {summary_path}")
    print("\n" + summary_text)

except Exception as e:
    print(f"[ERROR] Failed to create results summary: {e}")
    failed += 1

# ============================================================================
# FINAL STATUS
# ============================================================================

print("\n" + "="*80)
print("PIPELINE EXECUTION SUMMARY")
print("="*80)

print(f"\nStages completed: {completed}/3")
print(f"Stages failed: {failed}/3")

if failed == 0:
    print("\n[OK] SCM PIPELINE COMPLETED SUCCESSFULLY")
    print("\nOutput files created in: outputs/scm_firm_by_firm/")
    print("  - scm_firm_summary_results.csv")
    print("  - scm_statistical_inference.csv")
    print("  - scm_permutation_distribution.csv")
    print("  - scm_firm_level_effects.png")
    print("  - scm_permutation_distribution.png")
    print("  - scm_aggregate_effect.png")
    print("  - scm_effect_distribution.png")
    print("  - SCM_RESULTS_SUMMARY.txt")
else:
    print(f"\n[ERROR] Pipeline failed with {failed} stage(s) unsuccessful")
    sys.exit(1)

print("\n" + "="*80)
