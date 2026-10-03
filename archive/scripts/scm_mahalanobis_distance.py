"""
SYNTHETIC CONTROL METHOD - MAHALANOBIS DISTANCE WEIGHTED
Abadie et al. (2010) framework with computationally tractable distance-weighted matching
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import mahalanobis
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SYNTHETIC CONTROL METHOD - MAHALANOBIS DISTANCE WEIGHTED")
print("Abadie et al. (2010) framework with distance-weighted donors")
print("=" * 80)

# Load corrected sample
print("\n[1/4] Loading data...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Separate FCC and non-FCC
fcc = df[df['fcc_reportable'] == True].copy().reset_index(drop=True)
nonfcc = df[df['fcc_reportable'] == False].copy().reset_index(drop=True)

print(f"  - FCC breach events: {len(fcc)}")
print(f"  - Non-FCC donor pool: {len(nonfcc)}")

# Matching variables
match_vars = ['firm_size_log', 'leverage', 'roa']

# Extract data matrices
fcc_data = fcc[match_vars].values
nonfcc_data = nonfcc[match_vars].values
nonfcc_car = nonfcc['car_30d'].values

# Compute covariance matrix of donor pool for Mahalanobis distance
print("\n[2/4] Computing Mahalanobis distances...")
cov_matrix = np.cov(nonfcc_data.T)
try:
    inv_cov_matrix = np.linalg.inv(cov_matrix)
except np.linalg.LinAlgError:
    print("  Warning: Covariance matrix singular, using regularized inverse")
    inv_cov_matrix = np.linalg.pinv(cov_matrix)

print(f"  - Covariance matrix computed ({len(match_vars)} × {len(match_vars)})")
print(f"  - Condition number: {np.linalg.cond(cov_matrix):.2e}")

def compute_synthetic_car_mahalanobis(treated_obs, donor_matrix, donor_car, inv_cov):
    """
    Compute synthetic CAR using Mahalanobis distance weighted average.

    For each treated observation, compute Mahalanobis distance to all donors,
    convert to inverse distance weights, compute weighted average of donor CARs.
    """
    n_donors = len(donor_car)

    # Compute Mahalanobis distances to all donors
    distances = np.zeros(n_donors)
    for j in range(n_donors):
        diff = treated_obs - donor_matrix[j]
        distances[j] = np.sqrt(diff @ inv_cov @ diff.T)

    # Convert distances to weights: inverse distance weighting
    # Add small epsilon to avoid division by zero
    epsilon = 1e-10
    weights = 1.0 / (distances + epsilon)
    weights = weights / np.sum(weights)  # Normalize to sum to 1

    # Synthetic CAR is weighted average of donor CARs
    synthetic_car = np.sum(weights * donor_car)

    return synthetic_car, weights

# Calculate synthetic control for each FCC breach
print("\n[3/4] Calculating synthetic controls for FCC breaches...")
results = []
for i in range(len(fcc)):
    if (i + 1) % 25 == 0:
        print(f"  - Processed {i + 1}/{len(fcc)} breaches")

    treated_obs = fcc_data[i]
    synthetic_car, weights = compute_synthetic_car_mahalanobis(
        treated_obs, nonfcc_data, nonfcc_car, inv_cov_matrix
    )

    treatment_effect = fcc.iloc[i]['car_30d'] - synthetic_car

    results.append({
        'cik': fcc.iloc[i]['cik'],
        'org_name': fcc.iloc[i]['org_name'],
        'breach_date': fcc.iloc[i]['breach_date'],
        'actual_car': fcc.iloc[i]['car_30d'],
        'synthetic_car': synthetic_car,
        'treatment_effect': treatment_effect,
        'n_donors': len(nonfcc_car),
        'max_weight': weights.max(),
        'hhi_weights': np.sum(weights ** 2)  # Herfindahl index of weight concentration
    })

results_df = pd.DataFrame(results)

# Aggregate results
mean_effect = results_df['treatment_effect'].mean()
se_effect = results_df['treatment_effect'].std() / np.sqrt(len(results_df))
t_stat = mean_effect / se_effect
ci_lower = mean_effect - 1.96 * se_effect
ci_upper = mean_effect + 1.96 * se_effect

print(f"  ✓ Synthetic controls calculated for all {len(results_df)} breaches")
print(f"  - Mean weight concentration (HHI): {results_df['hhi_weights'].mean():.4f}")
print(f"  - Max weight per observation (mean): {results_df['max_weight'].mean():.4f}")

# Permutation inference
print("\n[4/4] Permutation inference (500 permutations)...")
n_perms = 500
perm_effects = []

np.random.seed(42)
for perm in range(n_perms):
    if (perm + 1) % 100 == 0:
        print(f"  - Completed {perm + 1}/{n_perms} permutations")

    # Randomly shuffle FCC labels
    perm_indices = np.random.choice(len(fcc), len(fcc), replace=False)
    perm_fcc_data = fcc_data[perm_indices]
    perm_fcc_car = fcc.iloc[perm_indices]['car_30d'].values

    perm_results = []
    for i in range(len(perm_fcc_data)):
        synthetic_car, _ = compute_synthetic_car_mahalanobis(
            perm_fcc_data[i], nonfcc_data, nonfcc_car, inv_cov_matrix
        )
        perm_results.append(perm_fcc_car[i] - synthetic_car)

    perm_effects.append(np.mean(perm_results))

perm_effects = np.array(perm_effects)
p_value = np.mean(np.abs(perm_effects) >= np.abs(mean_effect))

print("\n" + "=" * 80)
print("MAHALANOBIS DISTANCE WEIGHTED SYNTHETIC CONTROL RESULTS")
print("=" * 80)

print(f"\nAggregate Treatment Effect:")
print(f"  Mean effect:              {mean_effect:.4f}%")
print(f"  Standard error:           {se_effect:.4f}%")
print(f"  T-statistic:              {t_stat:.4f}")
print(f"  95% CI:                   [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  Permutation p-value:      {p_value:.4f} (500 permutations)")
print(f"  N FCC breaches:           {len(results_df)}")
print(f"  N donor pool:             {len(nonfcc)}")
print(f"  Matching method:          Mahalanobis distance inverse weighting")

print(f"\nComparison to OLS H2:")
print(f"  OLS H2 effect:            -2.1179%")
print(f"  OLS H2 p-value:           0.0494")
print(f"  SCM effect:               {mean_effect:.4f}%")
print(f"  SCM p-value:              {p_value:.4f}")

# Firm-level results
print("\n" + "=" * 80)
print("FIRM-LEVEL TREATMENT EFFECTS (FCC FIRMS)")
print("=" * 80)
firm_results = results_df.groupby(['cik', 'org_name']).agg({
    'treatment_effect': ['mean', 'count', 'std'],
    'hhi_weights': 'mean'
}).reset_index()
firm_results.columns = ['cik', 'org_name', 'mean_effect', 'n_breaches', 'std_effect', 'mean_hhi']
firm_results = firm_results.sort_values('mean_effect', ascending=False)

print(f"\n{len(firm_results)} FCC firms with {len(results_df)} total breaches:\n")
for idx, row in firm_results.iterrows():
    print(f"{row['org_name'][:40]:40s} | Effect: {row['mean_effect']:7.2f}% | N: {int(row['n_breaches']):3d}")

# Distribution
print("\n" + "=" * 80)
print("DISTRIBUTION OF INDIVIDUAL BREACH TREATMENT EFFECTS")
print("=" * 80)
print(f"\nPercentiles:")
print(f"  Min:       {results_df['treatment_effect'].min():7.4f}%")
print(f"  P10:       {results_df['treatment_effect'].quantile(0.10):7.4f}%")
print(f"  Q1 (25%):  {results_df['treatment_effect'].quantile(0.25):7.4f}%")
print(f"  Median:    {results_df['treatment_effect'].median():7.4f}%")
print(f"  Q3 (75%):  {results_df['treatment_effect'].quantile(0.75):7.4f}%")
print(f"  P90:       {results_df['treatment_effect'].quantile(0.90):7.4f}%")
print(f"  Max:       {results_df['treatment_effect'].max():7.4f}%")
print(f"\nVariability:")
print(f"  Mean:      {results_df['treatment_effect'].mean():7.4f}%")
print(f"  Std Dev:   {results_df['treatment_effect'].std():7.4f}%")

print(f"\nWeight Distribution Statistics:")
print(f"  Mean weight concentration (HHI):  {results_df['hhi_weights'].mean():.4f}")
print(f"  Median weight concentration:      {results_df['hhi_weights'].median():.4f}")
print(f"  Mean max weight:                  {results_df['max_weight'].mean():.4f}")
print(f"  Median max weight:                {results_df['max_weight'].median():.4f}")

# Save results
results_df.to_csv('outputs/scm_mahalanobis_results.csv', index=False)
firm_results.to_csv('outputs/scm_mahalanobis_firm_level.csv', index=False)

summary_df = pd.DataFrame({
    'Metric': ['N FCC Breaches', 'N Non-FCC Donor Pool',
               'Mean Treatment Effect (%)', 'Standard Error (%)',
               'T-Statistic', 'Permutation P-Value (500 perms)',
               '95% CI Lower (%)', '95% CI Upper (%)',
               'Matching Method'],
    'Value': [len(results_df), len(nonfcc),
              mean_effect, se_effect, t_stat, p_value,
              ci_lower, ci_upper, 'Mahalanobis distance weighted']
})
summary_df.to_csv('outputs/scm_mahalanobis_summary.csv', index=False)

print("\n✓ Results saved:")
print("  - outputs/scm_mahalanobis_results.csv")
print("  - outputs/scm_mahalanobis_firm_level.csv")
print("  - outputs/scm_mahalanobis_summary.csv")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
