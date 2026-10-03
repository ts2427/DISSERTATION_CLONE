"""
SYNTHETIC CONTROL - NEAREST NEIGHBOR MATCHING
Fastest version: 1-to-1 nearest neighbor matching on breach characteristics
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SYNTHETIC CONTROL - NEAREST NEIGHBOR MATCHING")
print("Ultra-fast 1-to-1 event matching approach")
print("=" * 80)

# Load corrected sample
print("\n[1/3] Loading and preparing data...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Separate FCC and non-FCC
fcc = df[df['fcc_reportable'] == True].copy().reset_index(drop=True)
nonfcc = df[df['fcc_reportable'] == False].copy().reset_index(drop=True)

print(f"  - FCC breach events: {len(fcc)}")
print(f"  - Non-FCC donor pool: {len(nonfcc)}")

# Matching variables
match_vars = ['firm_size_log', 'leverage', 'roa']

# Standardize matching variables
scaler = StandardScaler()
all_data = pd.concat([fcc, nonfcc])
scaler.fit(all_data[match_vars])

fcc_scaled = scaler.transform(fcc[match_vars])
nonfcc_scaled = scaler.transform(nonfcc[match_vars])

# Fit nearest neighbor model on non-FCC donors
nn_model = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(nonfcc_scaled)

print(f"  - Matching variables: {match_vars}")
print(f"  - Matching algorithm: Nearest neighbor (1-to-1)")

# Find nearest neighbor match for each FCC breach
print("\n[2/3] Matching FCC breaches to nearest non-FCC donors...")
distances, indices = nn_model.kneighbors(fcc_scaled)

results = []
for i in range(len(fcc)):
    fcc_row = fcc.iloc[i]
    donor_idx = indices[i, 0]
    nonfcc_row = nonfcc.iloc[donor_idx]

    treatment_effect = fcc_row['car_30d'] - nonfcc_row['car_30d']
    distance = distances[i, 0]

    results.append({
        'fcc_cik': fcc_row['cik'],
        'fcc_org': fcc_row['org_name'],
        'fcc_breach_date': fcc_row['breach_date'],
        'fcc_car': fcc_row['car_30d'],
        'donor_cik': nonfcc_row['cik'],
        'donor_org': nonfcc_row['org_name'],
        'donor_breach_date': nonfcc_row['breach_date'],
        'donor_car': nonfcc_row['car_30d'],
        'matching_distance': distance,
        'treatment_effect': treatment_effect
    })

results_df = pd.DataFrame(results)

# Aggregate results
mean_effect = results_df['treatment_effect'].mean()
se_effect = results_df['treatment_effect'].std() / np.sqrt(len(results_df))
t_stat = mean_effect / se_effect
ci_lower = mean_effect - 1.96 * se_effect
ci_upper = mean_effect + 1.96 * se_effect

print(f"  ✓ Matched {len(results_df)} FCC breaches to nearest non-FCC neighbors")

# Simple permutation test (randomize FCC labels)
print("\n[3/3] Permutation inference (500 permutations)...")
n_perms = 500
perm_effects = []

np.random.seed(42)
for perm in range(n_perms):
    if (perm + 1) % 100 == 0:
        print(f"  - Completed {perm + 1}/{n_perms} permutations")

    # Randomly shuffle FCC labels
    shuffled_labels = np.random.choice([0, 1], size=len(results_df), p=[526/653, 127/653])

    perm_results = []
    for i in range(len(results_df)):
        if shuffled_labels[i] == 0:  # If permuted to non-FCC
            effect = results_df.iloc[i]['donor_car'] - results_df.iloc[i]['fcc_car']
        else:  # If permuted to FCC
            effect = results_df.iloc[i]['treatment_effect']
        perm_results.append(effect)

    perm_effects.append(np.mean(perm_results))

perm_effects = np.array(perm_effects)
p_value = np.mean(np.abs(perm_effects) >= np.abs(mean_effect))

print("\n" + "=" * 80)
print("NEAREST NEIGHBOR SYNTHETIC CONTROL RESULTS")
print("=" * 80)
print(f"\nAggregate Treatment Effect:")
print(f"  Mean effect:              {mean_effect:.4f}%")
print(f"  Standard error:           {se_effect:.4f}%")
print(f"  T-statistic:              {t_stat:.4f}")
print(f"  95% CI:                   [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  Permutation p-value:      {p_value:.4f} (500 permutations)")
print(f"  N FCC breaches:           {len(results_df)}")
print(f"  N unique non-FCC donors:  {nonfcc['cik'].nunique()}")

print(f"\nMatching Quality:")
print(f"  Mean matching distance:   {results_df['matching_distance'].mean():.4f}")
print(f"  Median matching distance: {results_df['matching_distance'].median():.4f}")
print(f"  Max matching distance:    {results_df['matching_distance'].max():.4f}")

# Firm-level results
print("\n" + "=" * 80)
print("FIRM-LEVEL TREATMENT EFFECTS (FCC FIRMS)")
print("=" * 80)
firm_results = results_df.groupby(['fcc_cik', 'fcc_org']).agg({
    'treatment_effect': ['mean', 'count', 'std'],
    'matching_distance': 'mean'
}).reset_index()
firm_results.columns = ['cik', 'org_name', 'mean_effect', 'n_breaches', 'std_effect', 'mean_distance']
firm_results = firm_results.sort_values('mean_effect', ascending=False)

print(f"\n{len(firm_results)} FCC firms with {len(results_df)} total breaches:\n")
for idx, row in firm_results.iterrows():
    print(f"{row['org_name'][:40]:40s} | Effect: {row['mean_effect']:7.2f}% | N breaches: {int(row['n_breaches']):3d} | Distance: {row['mean_distance']:.4f}")

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

# Save results
results_df.to_csv('outputs/scm_breach_event_nn_results.csv', index=False)
firm_results.to_csv('outputs/scm_firm_level_nn_results.csv', index=False)

summary_df = pd.DataFrame({
    'Metric': ['N FCC Breaches', 'N Non-FCC Donor Pool', 'N Unique Non-FCC Firms',
               'Mean Treatment Effect (%)', 'Standard Error (%)', 'T-Statistic',
               'Permutation P-Value (500 perms)', '95% CI Lower (%)', '95% CI Upper (%)'],
    'Value': [len(results_df), len(nonfcc), nonfcc['cik'].nunique(),
              mean_effect, se_effect, t_stat, p_value, ci_lower, ci_upper]
})
summary_df.to_csv('outputs/scm_summary_nn_results.csv', index=False)

print("\n✓ Results saved:")
print("  - outputs/scm_breach_event_nn_results.csv")
print("  - outputs/scm_firm_level_nn_results.csv")
print("  - outputs/scm_summary_nn_results.csv")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
