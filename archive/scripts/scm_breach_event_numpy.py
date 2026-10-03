"""
SYNTHETIC CONTROL METHOD - BREACH EVENT LEVEL
Event-level matching without scpi_pkg
Abadie et al. (2010) framework applied to breach events
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SYNTHETIC CONTROL METHOD - BREACH EVENT LEVEL")
print("Event-matched approach without scpi_pkg")
print("=" * 80)

# Load corrected sample
print("\n[1/5] Loading data...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Separate FCC and non-FCC
fcc = df[df['fcc_reportable'] == True].copy()
nonfcc = df[df['fcc_reportable'] == False].copy()

print(f"  - FCC breach events: {len(fcc)}")
print(f"  - Non-FCC donor pool: {len(nonfcc)}")
print(f"  - Total observations: {len(df)}")

# Matching variables
match_vars = ['firm_size_log', 'leverage', 'roa']

# Standardize matching variables
print("\n[2/5] Standardizing matching variables...")
scaler = StandardScaler()
all_data = pd.concat([fcc, nonfcc])
scaler.fit(all_data[match_vars])

fcc_scaled = scaler.transform(fcc[match_vars])
nonfcc_scaled = scaler.transform(nonfcc[match_vars])
nonfcc_car = nonfcc['car_30d'].values

print(f"  - Matching variables: {match_vars}")
print(f"  - Scaling applied: StandardScaler")

def get_synthetic_car(treated_obs, donor_matrix, donor_car):
    """
    Find optimal weights for synthetic control.
    Minimizes distance between treated unit and
    weighted combination of donors on matching variables.
    """
    n_donors = len(donor_car)

    def objective(w):
        synthetic = donor_matrix.T @ w
        return np.sum((treated_obs - synthetic) ** 2)

    # Constraints: weights sum to 1, all non-negative
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n_donors
    w0 = np.ones(n_donors) / n_donors

    result = minimize(objective, w0, method='SLSQP',
                     bounds=bounds, constraints=constraints,
                     options={'ftol': 1e-6, 'maxiter': 100})

    if result.success:
        synthetic_car = donor_car @ result.x
        return synthetic_car, result.x
    else:
        # Fallback to nearest neighbor
        distances = np.sum((donor_matrix - treated_obs) ** 2, axis=1)
        nearest = np.argmin(distances)
        w = np.zeros(n_donors)
        w[nearest] = 1.0
        return donor_car[nearest], w

# Calculate synthetic control for each FCC breach
print("\n[3/5] Calculating synthetic controls for FCC breaches...")
results = []
for i, (idx, row) in enumerate(fcc.iterrows()):
    if (i + 1) % 25 == 0:
        print(f"  - Processed {i + 1}/{len(fcc)} breaches")

    treated_obs = fcc_scaled[i]

    synthetic_car, weights = get_synthetic_car(
        treated_obs, nonfcc_scaled, nonfcc_car
    )

    treatment_effect = row['car_30d'] - synthetic_car

    results.append({
        'cik': row['cik'],
        'org_name': row['org_name'],
        'breach_date': row['breach_date'],
        'actual_car': row['car_30d'],
        'synthetic_car': synthetic_car,
        'treatment_effect': treatment_effect
    })

results_df = pd.DataFrame(results)
print(f"  ✓ Synthetic controls calculated for all {len(results_df)} breaches")

# Aggregate results
print("\n[4/5] Aggregate SCM results...")
mean_effect = results_df['treatment_effect'].mean()
se_effect = results_df['treatment_effect'].std() / np.sqrt(len(results_df))
t_stat = mean_effect / se_effect
ci_lower = mean_effect - 1.96 * se_effect
ci_upper = mean_effect + 1.96 * se_effect

print(f"  - N FCC breach events: {len(results_df)}")
print(f"  - Mean treatment effect: {mean_effect:.4f}%")
print(f"  - Standard error: {se_effect:.4f}%")
print(f"  - T-statistic: {t_stat:.4f}")
print(f"  - 95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")

# Permutation inference
print("\n[5/5] Permutation inference (200 permutations for speed)...")
n_perms = 200
perm_effects = []

np.random.seed(42)  # For reproducibility
for perm in range(n_perms):
    if (perm + 1) % 200 == 0:
        print(f"  - Completed {perm + 1}/{n_perms} permutations")

    # Randomly assign FCC labels to non-FCC firms
    perm_indices = np.random.choice(len(nonfcc), len(fcc), replace=False)
    perm_fcc = nonfcc_scaled[perm_indices]
    perm_car = nonfcc_car[perm_indices]

    perm_results = []
    for i in range(len(perm_fcc)):
        # Use remaining non-FCC as donor pool
        donor_mask = np.ones(len(nonfcc), dtype=bool)
        donor_mask[perm_indices[i]] = False

        if donor_mask.sum() < 2:
            # Not enough donors, skip this permutation
            continue

        synthetic_car, _ = get_synthetic_car(
            perm_fcc[i],
            nonfcc_scaled[donor_mask],
            nonfcc_car[donor_mask]
        )
        perm_results.append(perm_car[i] - synthetic_car)

    if len(perm_results) > 0:
        perm_effects.append(np.mean(perm_results))

perm_effects = np.array(perm_effects)
p_value = np.mean(np.abs(perm_effects) >= np.abs(mean_effect))

print(f"  ✓ Permutation inference complete")

print("\n" + "=" * 80)
print("SCM RESULTS SUMMARY")
print("=" * 80)
print(f"\nAggregate Treatment Effect:")
print(f"  Mean effect:          {mean_effect:.4f}%")
print(f"  Standard error:       {se_effect:.4f}%")
print(f"  T-statistic:          {t_stat:.4f}")
print(f"  95% CI:               [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  Permutation p-value:  {p_value:.4f}")
print(f"  N observations:       {len(results_df)}")
print(f"  N donor pool:         {len(nonfcc)}")

# Firm-level results
print("\n" + "=" * 80)
print("FIRM-LEVEL TREATMENT EFFECTS")
print("=" * 80)
firm_results = results_df.groupby(['cik', 'org_name']).agg({
    'treatment_effect': ['mean', 'count', 'std']
}).reset_index()
firm_results.columns = ['cik', 'org_name', 'mean_effect', 'n_breaches', 'std_effect']
firm_results = firm_results.sort_values('mean_effect', ascending=False)

print(f"\n{len(firm_results)} firms with {len(results_df)} total breaches:\n")
print(firm_results.to_string(index=False))

# Distribution of treatment effects
print("\n" + "=" * 80)
print("DISTRIBUTION OF INDIVIDUAL BREACH TREATMENT EFFECTS")
print("=" * 80)
print(f"\nMin:       {results_df['treatment_effect'].min():.4f}%")
print(f"Q1 (25%):  {results_df['treatment_effect'].quantile(0.25):.4f}%")
print(f"Median:    {results_df['treatment_effect'].median():.4f}%")
print(f"Q3 (75%):  {results_df['treatment_effect'].quantile(0.75):.4f}%")
print(f"Max:       {results_df['treatment_effect'].max():.4f}%")
print(f"Std Dev:   {results_df['treatment_effect'].std():.4f}%")

# Save results
print("\n" + "=" * 80)
print("Saving results...")
results_df.to_csv('outputs/scm_breach_event_level_results.csv', index=False)
firm_results.to_csv('outputs/scm_firm_level_results.csv', index=False)

# Save summary
summary_df = pd.DataFrame({
    'Metric': ['N FCC Breaches', 'N Non-FCC Donor Pool', 'Mean Treatment Effect (%)',
               'Standard Error (%)', 'T-Statistic', 'Permutation P-Value',
               '95% CI Lower (%)', '95% CI Upper (%)'],
    'Value': [len(results_df), len(nonfcc), mean_effect, se_effect, t_stat, p_value, ci_lower, ci_upper]
})
summary_df.to_csv('outputs/scm_summary_results.csv', index=False)

print("  ✓ Results saved to outputs/scm_*.csv")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
