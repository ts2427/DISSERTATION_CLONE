"""
SCM VISUALIZATIONS
==================

Creates plots for firm-by-firm SCM results and statistical inference.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("\n" + "="*70)
print("SCM VISUALIZATIONS")
print("="*70)

# Load data
print("\n[1/4] Loading data...")
results_df = pd.read_csv("outputs/scm_firm_by_firm/scm_firm_summary_results.csv")
inference_df = pd.read_csv("outputs/scm_firm_by_firm/scm_statistical_inference.csv")
perm_df = pd.read_csv("outputs/scm_firm_by_firm/scm_permutation_distribution.csv")

# Extract key statistics
observed_mean = inference_df[inference_df['Statistic'] == 'Mean_effect']['Value'].values[0]
se = inference_df[inference_df['Statistic'] == 'SE']['Value'].values[0]
ci_lower = inference_df[inference_df['Statistic'] == 'CI_lower_95']['Value'].values[0]
ci_upper = inference_df[inference_df['Statistic'] == 'CI_upper_95']['Value'].values[0]
p_value_perm = inference_df[inference_df['Statistic'] == 'P_value_permutation']['Value'].values[0]

print(f"[OK] Loaded results for {len(results_df)} firms")

# ============================================================================
# FIGURE 1: FIRM-LEVEL TREATMENT EFFECTS
# ============================================================================

print("\n[2/4] Creating visualizations...")

fig, ax = plt.subplots(figsize=(10, 6))

# Sort by effect size
results_sorted = results_df.sort_values('mean_gap')

# Plot individual firm effects with error bars
x_pos = np.arange(len(results_sorted))
effects = results_sorted['mean_gap'].values
rmse = results_sorted['rmse_pre'].values

ax.bar(x_pos, effects, color=['red' if e < 0 else 'blue' for e in effects],
       alpha=0.7, edgecolor='black')

# Add mean line
ax.axhline(y=observed_mean, color='green', linestyle='--', linewidth=2,
          label=f'Aggregate mean: {observed_mean:.4f}%')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

# Formatting
ax.set_xticks(x_pos)
ax.set_xticklabels(results_sorted['firm_name'], rotation=45, ha='right')
ax.set_ylabel('Treatment Effect (% CAR 30d)', fontsize=12)
ax.set_title('Firm-Level Treatment Effects from SCM Analysis', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

fig.savefig("outputs/scm_firm_by_firm/scm_firm_level_effects.png", dpi=150, bbox_inches='tight')
print("[OK] Saved: scm_firm_level_effects.png")
plt.close()

# ============================================================================
# FIGURE 2: PERMUTATION TEST NULL DISTRIBUTION
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(perm_df['perm_mean'], bins=50, alpha=0.7, color='lightblue',
        edgecolor='black', label='Permutation distribution')

# Add observed effect line
ax.axvline(x=observed_mean, color='red', linestyle='--', linewidth=2.5,
          label=f'Observed effect: {observed_mean:.4f}% (p={p_value_perm:.4f})')
ax.axvline(x=-observed_mean, color='red', linestyle='--', linewidth=2.5, alpha=0.5)
ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

ax.set_xlabel('Mean Effect (%)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Permutation Test: Null Distribution of Treatment Effects',
            fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

fig.savefig("outputs/scm_firm_by_firm/scm_permutation_distribution.png", dpi=150, bbox_inches='tight')
print("[OK] Saved: scm_permutation_distribution.png")
plt.close()

# ============================================================================
# FIGURE 3: EFFECT SIZE WITH CONFIDENCE INTERVAL
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 5))

# Plot point estimate and CI
ax.errorbar(0, observed_mean, yerr=[[observed_mean - ci_lower], [ci_upper - observed_mean]],
           fmt='o', markersize=10, capsize=10, capthick=2, color='darkblue',
           ecolor='darkblue', linewidth=2)

ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(y=ci_lower, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.axhline(y=ci_upper, color='gray', linestyle=':', linewidth=1, alpha=0.5)

# Fill CI region
ax.fill_between([-0.3, 0.3], ci_lower, ci_upper, alpha=0.2, color='blue')

ax.set_xlim(-0.5, 0.5)
ax.set_xticks([])
ax.set_ylabel('Treatment Effect (% CAR 30d)', fontsize=12)
ax.set_title('Aggregate Treatment Effect with 95% CI', fontsize=13, fontweight='bold')
ax.text(0.1, observed_mean, f'  {observed_mean:.4f}%\n  95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]',
       fontsize=11, va='center')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

fig.savefig("outputs/scm_firm_by_firm/scm_aggregate_effect.png", dpi=150, bbox_inches='tight')
print("[OK] Saved: scm_aggregate_effect.png")
plt.close()

# ============================================================================
# FIGURE 4: DISTRIBUTION OF FIRM-LEVEL EFFECTS
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(results_df['mean_gap'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
ax.axvline(x=observed_mean, color='red', linestyle='--', linewidth=2.5,
          label=f'Mean: {observed_mean:.4f}%')
ax.axvline(x=results_df['mean_gap'].median(), color='green', linestyle='--', linewidth=2.5,
          label=f'Median: {results_df["mean_gap"].median():.4f}%')
ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

ax.set_xlabel('Treatment Effect (% CAR 30d)', fontsize=12)
ax.set_ylabel('Number of Firms', fontsize=12)
ax.set_title('Distribution of Firm-Level Treatment Effects', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

fig.savefig("outputs/scm_firm_by_firm/scm_effect_distribution.png", dpi=150, bbox_inches='tight')
print("[OK] Saved: scm_effect_distribution.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n[3/4] Complete")
print("\n[4/4] Summary of visualizations created:")
print("  - scm_firm_level_effects.png: Individual firm effects sorted by size")
print("  - scm_permutation_distribution.png: Null distribution from permutation test")
print("  - scm_aggregate_effect.png: Aggregate effect with 95% CI")
print("  - scm_effect_distribution.png: Distribution of firm-level effects")

print("\n" + "="*70)
