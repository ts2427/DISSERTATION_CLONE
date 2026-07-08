"""
SCM STATISTICAL INFERENCE - PERMUTATION TESTS
==============================================

Implements permutation-based inference for firm-by-firm SCM results.
Tests whether observed treatment effects significantly differ from zero.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

print("\n" + "="*70)
print("SCM STATISTICAL INFERENCE - PERMUTATION TESTS")
print("="*70)

# Load SCM results
print("\n[1/4] Loading SCM results...")
results_file = Path("outputs/scm_firm_by_firm/scm_firm_summary_results.csv")
results_df = pd.read_csv(results_file)

print(f"[OK] Loaded {len(results_df)} firm SCM results")
print(f"[OK] Mean effect: {results_df['mean_gap'].mean():.4f}%")

# ============================================================================
# AGGREGATE STATISTICS
# ============================================================================

print("\n[2/4] Computing aggregate statistics...")

# Observed aggregate effect (mean of firm-level effects)
observed_mean = results_df['mean_gap'].mean()
observed_std = results_df['mean_gap'].std()
n_firms = len(results_df)

# Standard error
se = observed_std / np.sqrt(n_firms)
t_stat = observed_mean / se if se > 0 else 0
p_value_ttest = 2 * (1 - stats.t.cdf(abs(t_stat), n_firms - 1))

# Compute 95% CI
ci_95 = 1.96 * se
ci_lower = observed_mean - ci_95
ci_upper = observed_mean + ci_95

print(f"\nAggregate Treatment Effect:")
print(f"  Mean effect: {observed_mean:.4f}%")
print(f"  Std dev: {observed_std:.4f}%")
print(f"  SE: {se:.4f}%")
print(f"  95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  t-stat: {t_stat:.4f} (df={n_firms-1})")
print(f"  p-value (t-test): {p_value_ttest:.4f}")

# ============================================================================
# PERMUTATION TEST
# ============================================================================

print("\n[3/4] Running permutation tests (10,000 iterations)...")

n_perms = 10000
effects = results_df['mean_gap'].values

# Permutation test: resample signs of observed effects
perm_means = []
np.random.seed(42)

for _ in range(n_perms):
    # Randomly flip signs of effects
    signs = np.random.choice([-1, 1], size=len(effects))
    perm_effect = np.mean(effects * signs)
    perm_means.append(perm_effect)

perm_means = np.array(perm_means)

# P-value: proportion of permutations with effect >= observed in magnitude
p_value_perm = np.mean(np.abs(perm_means) >= np.abs(observed_mean))

print(f"[OK] Permutation test completed")
print(f"  Observed mean: {observed_mean:.4f}%")
print(f"  Null distribution mean: {np.mean(perm_means):.6f}%")
print(f"  Null distribution std: {np.std(perm_means):.4f}%")
print(f"  P-value (two-tailed): {p_value_perm:.4f}")

# ============================================================================
# BOOTSTRAP CONFIDENCE INTERVALS
# ============================================================================

print("\n[4/4] Computing bootstrap confidence intervals...")

n_boot = 10000
boot_means = []

for _ in range(n_boot):
    boot_sample = np.random.choice(effects, size=len(effects), replace=True)
    boot_means.append(np.mean(boot_sample))

boot_means = np.array(boot_means)
boot_ci_lower = np.percentile(boot_means, 2.5)
boot_ci_upper = np.percentile(boot_means, 97.5)

print(f"Bootstrap 95% CI: [{boot_ci_lower:.4f}%, {boot_ci_upper:.4f}%]")

# ============================================================================
# SAVE INFERENCE RESULTS
# ============================================================================

inference_results = pd.DataFrame({
    'Statistic': [
        'N_firms',
        'Mean_effect',
        'Std_dev',
        'SE',
        'T_stat',
        'P_value_ttest',
        'CI_lower_95',
        'CI_upper_95',
        'P_value_permutation',
        'Boot_CI_lower_95',
        'Boot_CI_upper_95'
    ],
    'Value': [
        n_firms,
        observed_mean,
        observed_std,
        se,
        t_stat,
        p_value_ttest,
        ci_lower,
        ci_upper,
        p_value_perm,
        boot_ci_lower,
        boot_ci_upper
    ]
})

output_file = Path("outputs/scm_firm_by_firm/scm_statistical_inference.csv")
inference_results.to_csv(output_file, index=False)
print(f"\n[OK] Saved inference results to: {output_file}")

# Save null distribution for visualization
perm_df = pd.DataFrame({
    'permutation_id': range(n_perms),
    'perm_mean': perm_means
})
perm_df.to_csv(Path("outputs/scm_firm_by_firm/scm_permutation_distribution.csv"), index=False)

# Summary
print("\n" + "="*70)
print("INFERENCE RESULTS SUMMARY")
print("="*70)
print(f"\nObserved aggregate effect: {observed_mean:.4f}% (SE={se:.4f}%)")
print(f"95% CI (parametric): [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"95% CI (bootstrap): [{boot_ci_lower:.4f}%, {boot_ci_upper:.4f}%]")
print(f"\nStatistical significance:")
print(f"  t-test p-value: {p_value_ttest:.4f}")
print(f"  Permutation p-value: {p_value_perm:.4f}")

if p_value_ttest < 0.05:
    print(f"\n[OK] Effect is statistically significant at 5% level (t-test)")
else:
    print(f"\n[*] Effect is NOT significant at 5% level (t-test)")

if p_value_perm < 0.05:
    print(f"[OK] Effect is statistically significant at 5% level (permutation)")
else:
    print(f"[*] Effect is NOT significant at 5% level (permutation)")

print("\n" + "="*70)
