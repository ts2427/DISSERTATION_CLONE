"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - PYTHON AGGREGATION & ANALYSIS
========================================================================

This script:
1. Runs the R script for individual SCM estimation
2. Aggregates firm-level treatment effects
3. Performs statistical inference (permutation tests, bootstrap CI)
4. Creates publication-ready visualizations
5. Generates comprehensive results tables

USAGE:
------
python firm_by_firm_scm_analysis.py

PREREQUISITE:
Run in R first (or this script will call it):
  source("firm_by_firm_scm.R")
"""

import os
import sys
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path('outputs/scm_firm_by_firm')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11

# ============================================================================
# STEP 1: RUN R SCRIPT (if needed)
# ============================================================================

def run_r_script():
    """Execute the R script to generate SCM results"""
    print("\n" + "="*70)
    print("RUNNING FIRM-BY-FIRM SCM (R)")
    print("="*70)

    try:
        result = subprocess.run(
            ['C:\Program Files\R\R-4.6.0\bin\Rscript.exe', 'firm_by_firm_scm_dissertation.R'],
            capture_output=True,
            text=True,
            timeout=3600
        )

        if result.returncode == 0:
            print("[OK] R script completed successfully")
            print(result.stdout)
        else:
            print("[ERROR] R script failed:")
            print(result.stderr)
            return False

        return True

    except FileNotFoundError:
        print("[WARNING] Rscript not found. Make sure R is installed and in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("[WARNING] R script timed out (>1 hour)")
        return False
    except Exception as e:
        print(f"[ERROR] Error running R script: {e}")
        return False


# ============================================================================
# STEP 2: LOAD AND AGGREGATE RESULTS
# ============================================================================

def load_scm_results():
    """Load SCM results from R output"""
    print("\n" + "="*70)
    print("LOADING AND AGGREGATING RESULTS")
    print("="*70)

    # Load individual firm results
    firm_summary_file = OUTPUT_DIR / "scm_firm_summary_results.csv"
    gaps_file = OUTPUT_DIR / "scm_all_firm_gaps.csv"
    stats_file = OUTPUT_DIR / "scm_aggregate_statistics.csv"

    if not firm_summary_file.exists():
        print(f"[ERROR] Results file not found: {firm_summary_file}")
        print("  Make sure R script ran successfully")
        return None, None, None

    firm_results = pd.read_csv(firm_summary_file)
    all_gaps = pd.read_csv(gaps_file)
    agg_stats = pd.read_csv(stats_file)

    print(f"[OK] Loaded results for {len(firm_results)} FCC firms")
    print(f"[OK] Total gap observations: {len(all_gaps)}")

    return firm_results, all_gaps, agg_stats


# ============================================================================
# STEP 3: STATISTICAL INFERENCE
# ============================================================================

def permutation_test(gaps_df, n_permutations=1000, seed=12345):
    """
    Run permutation test for null hypothesis that mean effect = 0.

    This tests whether the observed mean effect could plausibly occur by chance
    if treatment assignment was random.
    """
    np.random.seed(seed)

    # Observed mean effect (post-treatment only)
    post_gaps = gaps_df[gaps_df['is_post_treatment'] == True]['gap']
    observed_mean = post_gaps.mean()
    observed_sd = post_gaps.std()

    # Permutation distribution under null (mean = 0)
    perm_means = []
    for _ in range(n_permutations):
        # Randomly shuffle gap signs (permutation under null)
        perm_gaps = post_gaps * np.random.choice([-1, 1], size=len(post_gaps))
        perm_means.append(perm_gaps.mean())

    perm_means = np.array(perm_means)

    # P-value (two-tailed)
    p_value = np.mean(np.abs(perm_means) >= np.abs(observed_mean))

    results = {
        'observed_mean': observed_mean,
        'observed_sd': observed_sd,
        'observed_se': observed_sd / np.sqrt(len(post_gaps)),
        't_statistic': observed_mean / (observed_sd / np.sqrt(len(post_gaps))),
        'p_value_permutation': p_value,
        'p_value_ttest': stats.ttest_1samp(post_gaps, 0)[1],
        'ci_lower': np.percentile(perm_means, 2.5),
        'ci_upper': np.percentile(perm_means, 97.5),
        'n_obs': len(post_gaps),
        'n_firms': len(gaps_df['firm_id'].unique())
    }

    return results, perm_means


def bootstrap_ci(firm_results, n_bootstrap=1000, seed=12345):
    """
    Bootstrap confidence intervals for mean treatment effect.
    """
    np.random.seed(seed)

    effects = firm_results['mean_gap'].dropna().values
    boot_means = []

    for _ in range(n_bootstrap):
        boot_sample = np.random.choice(effects, size=len(effects), replace=True)
        boot_means.append(boot_sample.mean())

    boot_means = np.array(boot_means)

    return {
        'mean': effects.mean(),
        'median': np.median(effects),
        'sd': effects.std(),
        'ci_lower': np.percentile(boot_means, 2.5),
        'ci_upper': np.percentile(boot_means, 97.5),
        'ci_lower_90': np.percentile(boot_means, 5),
        'ci_upper_90': np.percentile(boot_means, 95)
    }


# ============================================================================
# STEP 4: VISUALIZATIONS
# ============================================================================

def plot_firm_effects_distribution(firm_results, output_dir):
    """Distribution of individual firm treatment effects"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Histogram
    ax = axes[0, 0]
    ax.hist(firm_results['mean_gap'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(firm_results['mean_gap'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    ax.axvline(firm_results['mean_gap'].median(), color='green', linestyle='--', linewidth=2, label='Median')
    ax.axvline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('Treatment Effect (Mean Gap, %)', fontsize=11)
    ax.set_ylabel('Number of Firms', fontsize=11)
    ax.set_title('Distribution of Individual Firm Treatment Effects', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Box plot by quartile of pre-period fit
    ax = axes[0, 1]
    firm_results['fit_quality'] = pd.qcut(firm_results['rmse_pre'], q=4, labels=['Best', 'Good', 'Fair', 'Poor'])
    firm_results.boxplot(column='mean_gap', by='fit_quality', ax=ax)
    ax.set_xlabel('Pre-Treatment Fit Quality (RMSE)', fontsize=11)
    ax.set_ylabel('Treatment Effect (%)', fontsize=11)
    ax.set_title('Treatment Effects by Model Fit Quality', fontsize=12, fontweight='bold')
    ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    plt.sca(ax)
    plt.xticks(rotation=0)

    # Scatter: Effect size vs pre-fit
    ax = axes[1, 0]
    ax.scatter(firm_results['rmse_pre'], firm_results['mean_gap'], alpha=0.6, s=50, color='steelblue')
    ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Pre-Treatment RMSE (Model Fit)', fontsize=11)
    ax.set_ylabel('Treatment Effect (%)', fontsize=11)
    ax.set_title('Treatment Effect vs Model Fit Quality', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Cumulative effect distribution
    ax = axes[1, 1]
    sorted_effects = np.sort(firm_results['mean_gap'].dropna())
    cumulative = np.arange(1, len(sorted_effects) + 1) / len(sorted_effects)
    ax.plot(sorted_effects, cumulative, linewidth=2.5, color='steelblue')
    ax.axvline(sorted_effects.mean(), color='red', linestyle='--', linewidth=1.5, label='Mean')
    ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax.fill_between(sorted_effects, 0, cumulative, alpha=0.3, color='steelblue')
    ax.set_xlabel('Treatment Effect (%)', fontsize=11)
    ax.set_ylabel('Cumulative Proportion', fontsize=11)
    ax.set_title('Cumulative Distribution of Effects', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'scm_firm_effects_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: scm_firm_effects_distribution.png")
    plt.close()


def plot_aggregate_gaps_over_time(gaps_df, output_dir):
    """Aggregate treatment effect gaps over time (mean ± SE)"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Aggregate gap (mean and SE by year)
    gap_by_year = gaps_df.groupby('year')['gap'].agg(['mean', 'std', 'count'])
    gap_by_year['se'] = gap_by_year['std'] / np.sqrt(gap_by_year['count'])
    gap_by_year['ci_lower'] = gap_by_year['mean'] - 1.96 * gap_by_year['se']
    gap_by_year['ci_upper'] = gap_by_year['mean'] + 1.96 * gap_by_year['se']

    # Main plot
    ax = axes[0]
    ax.plot(gap_by_year.index, gap_by_year['mean'], linewidth=2.5, marker='o', color='steelblue', label='Mean gap')
    ax.fill_between(gap_by_year.index, gap_by_year['ci_lower'], gap_by_year['ci_upper'], alpha=0.3, color='steelblue', label='95% CI')
    ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.6)
    ax.axvline(2007, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='Treatment onset (2007)')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Treatment Effect Gap (Treated - Synthetic Control, %)', fontsize=11)
    ax.set_title('Aggregate Treatment Effect Over Time', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Pre vs Post comparison
    ax = axes[1]
    pre_gap = gaps_df[gaps_df['is_post_treatment'] == False]['gap']
    post_gap = gaps_df[gaps_df['is_post_treatment'] == True]['gap']

    data_to_plot = [pre_gap, post_gap]
    bp = ax.boxplot(data_to_plot, labels=['Pre-Treatment\n(Before 2007)', 'Post-Treatment\n(2007+)'],
                    patch_artist=True, widths=0.6)

    for patch, color in zip(bp['boxes'], ['lightblue', 'lightcoral']):
        patch.set_facecolor(color)

    ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.6)
    ax.set_ylabel('Gap (%)', fontsize=11)
    ax.set_title('Pre vs Post Treatment Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add statistics to plot
    pre_mean = pre_gap.mean()
    post_mean = post_gap.mean()
    ax.text(0.5, 0.95, f'Pre: μ={pre_mean:.3f}%, n={len(pre_gap)}',
            transform=ax.transAxes, va='top', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax.text(0.5, 0.85, f'Post: μ={post_mean:.3f}%, n={len(post_gap)}',
            transform=ax.transAxes, va='top', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

    plt.tight_layout()
    plt.savefig(output_dir / 'scm_aggregate_gaps_over_time.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: scm_aggregate_gaps_over_time.png")
    plt.close()


def plot_permutation_distribution(perm_means, observed_mean, output_dir):
    """Permutation test null distribution"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogram of permutation distribution
    ax.hist(perm_means, bins=50, alpha=0.7, color='steelblue', edgecolor='black', label='Permutation distribution')
    ax.axvline(observed_mean, color='red', linestyle='--', linewidth=2.5, label=f'Observed mean ({observed_mean:.4f}%)')
    ax.axvline(0, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Null (effect = 0)')
    ax.axvline(-observed_mean, color='red', linestyle=':', linewidth=1.5, alpha=0.5)

    ax.set_xlabel('Mean Treatment Effect (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Permutation Test: Null Distribution of Mean Effect', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'scm_permutation_test_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: scm_permutation_test_distribution.png")
    plt.close()


# ============================================================================
# STEP 5: GENERATE RESULTS TABLES
# ============================================================================

def create_results_tables(firm_results, gaps_df, perm_test_results, boot_results, output_dir):
    """Create publication-ready results tables"""

    # ===== TABLE 1: Aggregate Results =====
    agg_table = pd.DataFrame({
        'Metric': [
            'Number of FCC firms',
            'Mean Treatment Effect (%)',
            'Std Dev Effect (%)',
            'Median Effect (%)',
            'Min Effect (%)',
            'Max Effect (%)',
            '95% CI Lower (%)',
            '95% CI Upper (%)',
            'Permutation p-value',
            't-test p-value',
            'Avg RMSE (pre-treatment fit)'
        ],
        'Value': [
            f"{perm_test_results['n_firms']:.0f}",
            f"{perm_test_results['observed_mean']:.4f}",
            f"{perm_test_results['observed_sd']:.4f}",
            f"{firm_results['mean_gap'].median():.4f}",
            f"{firm_results['mean_gap'].min():.4f}",
            f"{firm_results['mean_gap'].max():.4f}",
            f"{perm_test_results['ci_lower']:.4f}",
            f"{perm_test_results['ci_upper']:.4f}",
            f"{perm_test_results['p_value_permutation']:.4f}",
            f"{perm_test_results['p_value_ttest']:.4f}",
            f"{firm_results['rmse_pre'].mean():.4f}"
        ]
    })

    agg_table.to_csv(output_dir / 'TABLE_SCM_AGGREGATE_RESULTS.csv', index=False)
    print(f"  Saved: TABLE_SCM_AGGREGATE_RESULTS.csv")

    # ===== TABLE 2: Individual Firm Results (top 20 by effect size) =====
    firm_table = firm_results.nlargest(20, 'mean_gap')[
        ['firm_id', 'firm_name', 'n_controls', 'mean_gap', 'mean_gap_pre', 'mean_gap_post', 'rmse_pre']
    ].copy()
    firm_table.columns = ['Firm ID', 'Firm Name', 'N Controls', 'Mean Effect (%)', 'Pre Effect (%)', 'Post Effect (%)', 'RMSE']
    firm_table.to_csv(output_dir / 'TABLE_SCM_TOP_20_FIRMS.csv', index=False)
    print(f"  Saved: TABLE_SCM_TOP_20_FIRMS.csv")

    # ===== TABLE 3: Gap Summary by Year =====
    gap_by_year = gaps_df.groupby('year')['gap'].agg(['mean', 'std', 'count', 'min', 'max'])
    gap_by_year = gap_by_year.round(4)
    gap_by_year.to_csv(output_dir / 'TABLE_SCM_GAPS_BY_YEAR.csv')
    print(f"  Saved: TABLE_SCM_GAPS_BY_YEAR.csv")

    # ===== TEXT SUMMARY =====
    summary_text = f"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - RESULTS SUMMARY
{'='*70}

AGGREGATE TREATMENT EFFECT (n={perm_test_results['n_firms']} FCC firms)
Mean Effect:            {perm_test_results['observed_mean']:>10.4f}%
Std Dev:                {perm_test_results['observed_sd']:>10.4f}%
Standard Error:         {perm_test_results['observed_se']:>10.4f}%
95% CI:                 [{perm_test_results['ci_lower']:>8.4f}, {perm_test_results['ci_upper']:>8.4f}]%

STATISTICAL INFERENCE
t-statistic:            {perm_test_results['t_statistic']:>10.4f}
p-value (t-test):       {perm_test_results['p_value_ttest']:>10.4f}
p-value (permutation):  {perm_test_results['p_value_permutation']:>10.4f}
Observations (gaps):    {perm_test_results['n_obs']:>10.0f}

BOOTSTRAP RESULTS
Bootstrap Mean:         {boot_results['mean']:>10.4f}%
Bootstrap Median:       {boot_results['median']:>10.4f}%
Bootstrap 95% CI:       [{boot_results['ci_lower']:>8.4f}, {boot_results['ci_upper']:>8.4f}]%
Bootstrap 90% CI:       [{boot_results['ci_lower_90']:>8.4f}, {boot_results['ci_upper_90']:>8.4f}]%

HETEROGENEITY IN INDIVIDUAL FIRM EFFECTS
Median Effect:          {firm_results['mean_gap'].median():>10.4f}%
Min Effect:             {firm_results['mean_gap'].min():>10.4f}%
Max Effect:             {firm_results['mean_gap'].max():>10.4f}%
IQR (Q1-Q3):            {firm_results['mean_gap'].quantile(0.25):.4f}% to {firm_results['mean_gap'].quantile(0.75):.4f}%

MODEL FIT QUALITY
Mean RMSE (pre-treat):  {firm_results['rmse_pre'].mean():>10.4f}
Median RMSE:            {firm_results['rmse_pre'].median():>10.4f}

INTERPRETATION
- Treatment assignment now has n={perm_test_results['n_firms']} (individual firms), not n=1 (sector-level)
- Mean effect is {abs(perm_test_results['observed_mean']):.4f}% with SE={perm_test_results['observed_se']:.4f}%
- Permutation test p-value: {perm_test_results['p_value_permutation']:.4f}
- Effect is {'SIGNIFICANT' if perm_test_results['p_value_permutation'] < 0.05 else 'NOT SIGNIFICANT'} at α=0.05 level
- Substantial heterogeneity across firms: range {firm_results['mean_gap'].min():.2f}% to {firm_results['mean_gap'].max():.2f}%
"""

    with open(output_dir / 'SCM_RESULTS_SUMMARY.txt', 'w') as f:
        f.write(summary_text)

    print(f"  Saved: SCM_RESULTS_SUMMARY.txt")
    print(summary_text)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete analysis pipeline"""

    print("\n" + "="*70)
    print("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - COMPLETE ANALYSIS")
    print("="*70)

    # Step 1: Run R script
    run_r_script()

    # Step 2: Load results
    firm_results, gaps_df, agg_stats = load_scm_results()
    if firm_results is None:
        print("Failed to load results. Exiting.")
        return 1

    # Step 3: Statistical inference
    print("\n" + "="*70)
    print("PERFORMING STATISTICAL INFERENCE")
    print("="*70)

    perm_test_results, perm_means = permutation_test(gaps_df, n_permutations=10000)
    boot_results = bootstrap_ci(firm_results, n_bootstrap=10000)

    print(f"\n[OK] Permutation test (n=10,000):")
    print(f"  Mean effect: {perm_test_results['observed_mean']:.4f}%")
    print(f"  p-value: {perm_test_results['p_value_permutation']:.4f}")
    print(f"  95% CI: [{perm_test_results['ci_lower']:.4f}, {perm_test_results['ci_upper']:.4f}]")

    print(f"\n[OK] Bootstrap (n=10,000):")
    print(f"  Mean: {boot_results['mean']:.4f}%")
    print(f"  95% CI: [{boot_results['ci_lower']:.4f}, {boot_results['ci_upper']:.4f}]")

    # Step 4: Visualizations
    print("\n" + "="*70)
    print("CREATING VISUALIZATIONS")
    print("="*70)

    plot_firm_effects_distribution(firm_results, OUTPUT_DIR)
    plot_aggregate_gaps_over_time(gaps_df, OUTPUT_DIR)
    plot_permutation_distribution(perm_means, perm_test_results['observed_mean'], OUTPUT_DIR)

    # Step 5: Results tables
    print("\n" + "="*70)
    print("GENERATING RESULTS TABLES")
    print("="*70)

    create_results_tables(firm_results, gaps_df, perm_test_results, boot_results, OUTPUT_DIR)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("\nKey files:")
    print("  - SCM_RESULTS_SUMMARY.txt (detailed results)")
    print("  - TABLE_SCM_AGGREGATE_RESULTS.csv (publication table)")
    print("  - TABLE_SCM_TOP_20_FIRMS.csv (heterogeneity)")
    print("  - scm_firm_effects_distribution.png (visualization)")
    print("  - scm_aggregate_gaps_over_time.png (main figure)")
    print("  - scm_permutation_test_distribution.png (inference)")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
