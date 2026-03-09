"""
CVSS TECHNICAL COMPLEXITY HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION
Phase 2 of Publication Enhancement: Option B

Analyzes whether vulnerability technical complexity (CVSS severity) moderates
the FCC volatility effect (Essay 2).

Hypothesis: Complex vulnerabilities (high CVSS scores) require longer investigation,
so FCC time pressure constraints create larger market volatility increases.

Mechanism: FCC mandates 7-day disclosure -> complex breach (high CVSS) requires
more investigation time to understand technical details -> incomplete disclosure
under time pressure -> markets increase uncertainty -> larger FCC volatility effect
for high-complexity breaches.

This tests the TECHNICAL COMPLEXITY mechanism distinct from governance quality
(Phase 1) and timing/speed (Essays 2-3).
"""

import pandas as pd
import numpy as np
import json
import warnings
from pathlib import Path
from datetime import datetime
import re

# Suppress warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("CVSS TECHNICAL COMPLEXITY HETEROGENEITY ANALYSIS - ESSAY 2 VOLATILITY VERSION")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/6] Loading datasets...")

# Load main dissertation dataset
print("  Loading main dissertation dataset...")
main_df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f"    [OK] {len(main_df):,} breach observations")

# Load governance data from Phase 1
print("  Loading Phase 1 governance indicators...")
try:
    gov_df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')
    has_gov_data = True
    print(f"    [OK] Governance indicators loaded")
except:
    has_gov_data = False
    print(f"    [NOTE] Using main dataset (Phase 1 optional)")

# ============================================================================
# SECTION 2: EXTRACT CVSS SCORES FROM NVD JSON FILES
# ============================================================================

print("\n[2/6] Extracting CVSS scores from NVD JSON files...")
print("  Processing 2007-2024 NVD CVE database...")

# Build dictionary: vendor -> list of CVSS scores
vendor_cvss_map = {}
years_processed = 0

# Process each year's NVD data
nvd_dir = Path('data/JSON Files')
json_files = sorted(nvd_dir.glob('nvdcve-2.0-*.json'))

print(f"  Found {len(json_files)} NVD files to process")

for json_file in json_files:
    year = json_file.stem.split('-')[-1]

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            vulnerabilities = data.get('vulnerabilities', [])

            for vuln in vulnerabilities:
                cve_data = vuln.get('cve', {})
                cve_id = cve_data.get('id', '')

                # Extract CVSS scores (prefer v3.1, fall back to v3.0, then v2.0)
                metrics = cve_data.get('metrics', {})
                cvss_score = None
                severity = None

                if 'cvssMetricV31' in metrics:
                    cvss_data = metrics['cvssMetricV31'][0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    severity = cvss_data.get('baseSeverity', '')
                elif 'cvssMetricV3' in metrics:
                    cvss_data = metrics['cvssMetricV3'][0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    severity = cvss_data.get('baseSeverity', '')
                elif 'cvssMetricV2' in metrics:
                    cvss_data = metrics['cvssMetricV2'][0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    # Map CVSS v2 scores to severity
                    if cvss_score:
                        if cvss_score < 4.0:
                            severity = 'LOW'
                        elif cvss_score < 7.0:
                            severity = 'MEDIUM'
                        elif cvss_score < 9.0:
                            severity = 'HIGH'
                        else:
                            severity = 'CRITICAL'

                # Extract affected vendors/products from configurations
                configurations = cve_data.get('configurations', [])
                for config in configurations:
                    nodes = config.get('nodes', [])
                    for node in nodes:
                        cpe_matches = node.get('cpeMatch', [])
                        for cpe in cpe_matches:
                            criteria = cpe.get('criteria', '')
                            # Extract vendor from CPE
                            # Format: cpe:2.3:TYPE:VENDOR:PRODUCT:...
                            parts = criteria.split(':')
                            if len(parts) >= 4:
                                vendor = parts[3].lower()

                                if vendor and vendor != '*':
                                    if vendor not in vendor_cvss_map:
                                        vendor_cvss_map[vendor] = []

                                    if cvss_score is not None:
                                        vendor_cvss_map[vendor].append({
                                            'cvss_score': cvss_score,
                                            'severity': severity,
                                            'cve_id': cve_id,
                                            'year': int(year)
                                        })

            years_processed += 1
            if years_processed % 5 == 0:
                print(f"    Processed {years_processed} years, {len(vendor_cvss_map):,} vendors found")

    except Exception as e:
        print(f"    [WARN] Error processing {json_file}: {str(e)[:50]}")

print(f"\n  Extracted CVSS data for {len(vendor_cvss_map):,} vendors")
print(f"  Total CVE-vendor pairs: {sum(len(v) for v in vendor_cvss_map.values()):,}")

# ============================================================================
# SECTION 3: CREATE CVSS COMPLEXITY INDICATORS
# ============================================================================

print("\n[3/6] Creating CVSS complexity indicators for breaches...")

# Use governance data if available, otherwise main data
df = gov_df.copy() if has_gov_data else main_df.copy()

# Initialize CVSS columns
df['vendor_mean_cvss'] = np.nan
df['vendor_max_cvss'] = np.nan
df['vendor_high_severity_pct'] = np.nan
df['has_high_complexity'] = 0
df['complexity_category'] = 'Low'

# Match each breach's vendor to CVSS data
print("  Matching breaches to vendor CVSS profiles...")

for idx, row in df.iterrows():
    vendor = row['nvd_vendor']

    if pd.isna(vendor) or vendor == '' or vendor == '*':
        continue

    # Normalize vendor name
    vendor_norm = str(vendor).lower().strip()

    # Look for exact match or partial match
    matched_scores = None

    if vendor_norm in vendor_cvss_map:
        matched_scores = vendor_cvss_map[vendor_norm]
    else:
        # Try partial match on first word
        first_word = vendor_norm.split()[0]
        for v, scores in vendor_cvss_map.items():
            if v.startswith(first_word[:5]):
                matched_scores = scores
                break

    if matched_scores and len(matched_scores) > 0:
        scores = [s['cvss_score'] for s in matched_scores]
        severities = [s['severity'] for s in matched_scores]

        df.loc[idx, 'vendor_mean_cvss'] = np.mean(scores)
        df.loc[idx, 'vendor_max_cvss'] = np.max(scores)

        # High severity percentage (CVSS >= 7.0)
        high_sev_count = sum(1 for s in scores if s >= 7.0)
        df.loc[idx, 'vendor_high_severity_pct'] = high_sev_count / len(scores) if len(scores) > 0 else 0

        # Binary high complexity indicator
        mean_cvss = np.mean(scores)
        if mean_cvss >= 7.0:
            df.loc[idx, 'has_high_complexity'] = 1
            df.loc[idx, 'complexity_category'] = 'High'
        elif mean_cvss >= 5.0:
            df.loc[idx, 'complexity_category'] = 'Medium'

# Summary statistics
print(f"\n  CVSS complexity indicator summary:")
print(f"    Breaches with CVSS data: {df['vendor_mean_cvss'].notna().sum():,}")
print(f"    Mean vendor CVSS: {df['vendor_mean_cvss'].mean():.2f}")
print(f"    High complexity breaches (CVSS >= 7.0): {df['has_high_complexity'].sum():,}")

print(f"\n  Complexity distribution:")
complexity_dist = df['complexity_category'].value_counts()
for cat, count in complexity_dist.items():
    print(f"    {cat}: {count:,}")

# ============================================================================
# SECTION 4: DESCRIPTIVE STATISTICS
# ============================================================================

print("\n[4/6] Descriptive statistics by complexity...")

print("\n  VOLATILITY by complexity:")
complexity_stats = df[df['volatility_change'].notna()].groupby('has_high_complexity')['volatility_change'].describe().round(4)
print(complexity_stats)

print("\n  VOLATILITY by FCC and complexity:")
fcc_complexity = df[df['volatility_change'].notna()].groupby(
    ['fcc_reportable', 'has_high_complexity']
)['volatility_change'].agg(['count', 'mean', 'median', 'std']).round(4)
print(fcc_complexity)

# Calculate FCC effect by complexity
print("\n  FCC effect by complexity:")
non_fcc_low = df[(df['fcc_reportable']==0) & (df['has_high_complexity']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_low = df[(df['fcc_reportable']==1) & (df['has_high_complexity']==0) & (df['volatility_change'].notna())]['volatility_change'].mean()
non_fcc_high = df[(df['fcc_reportable']==0) & (df['has_high_complexity']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()
fcc_high = df[(df['fcc_reportable']==1) & (df['has_high_complexity']==1) & (df['volatility_change'].notna())]['volatility_change'].mean()

print(f"    Non-FCC + Low complexity: {non_fcc_low:.4f}pp")
print(f"    FCC + Low complexity: {fcc_low:.4f}pp")
print(f"    FCC effect for low-complexity: {fcc_low - non_fcc_low:.4f}pp")
print(f"\n    Non-FCC + High complexity: {non_fcc_high:.4f}pp")
print(f"    FCC + High complexity: {fcc_high:.4f}pp")
print(f"    FCC effect for high-complexity: {fcc_high - non_fcc_high:.4f}pp")

# ============================================================================
# SECTION 5: HETEROGENEITY ANALYSIS - REGRESSION MODELS
# ============================================================================

print("\n[5/6] Running heterogeneity models...")

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
except ImportError:
    print("  [FAIL] Installing required packages...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'statsmodels'])
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

# Prepare regression data
reg_data = df[
    (df['volatility_change'].notna()) &
    (df['vendor_mean_cvss'].notna())
].copy()

reg_data['volatility_outcome'] = reg_data['volatility_change']
reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
reg_data['high_complexity'] = reg_data['has_high_complexity'].astype(int)
reg_data['health'] = reg_data['health_breach'].astype(int)
reg_data['financial'] = reg_data['financial_breach'].astype(int)
reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

print(f"\n  Analysis sample: {len(reg_data):,} breaches with CVSS complexity data")

# Model 1: Baseline FCC effect
print("\n  MODEL 1: Baseline FCC Effect (Essay 2)")
model1 = ols('volatility_outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m1 = model1.params['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.params['fcc']
pval_fcc_m1 = model1.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model1.params.index else model1.pvalues['fcc']

print(f"    FCC Effect: {coef_fcc_m1:.4f}pp (p={pval_fcc_m1:.4f})")
print(f"    R-squared = {model1.rsquared:.4f}")
print(f"    N = {len(model1.resid):,}")

# Model 2: Add complexity main effect
print("\n  MODEL 2: FCC Effect + Complexity Main Effect")
model2 = ols('volatility_outcome ~ fcc + high_complexity + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m2 = model2.params['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.params['fcc']
pval_fcc_m2 = model2.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model2.params.index else model2.pvalues['fcc']
coef_complex = model2.params['high_complexity[T.1]'] if 'high_complexity[T.1]' in model2.params.index else model2.params['high_complexity']
pval_complex = model2.pvalues['high_complexity[T.1]'] if 'high_complexity[T.1]' in model2.params.index else model2.pvalues['high_complexity']

print(f"    FCC Effect: {coef_fcc_m2:.4f}pp (p={pval_fcc_m2:.4f})")
print(f"    High Complexity Effect: {coef_complex:.4f}pp (p={pval_complex:.4f})")
print(f"    R-squared = {model2.rsquared:.4f}")

# Model 3: FCC x Complexity Interaction (KEY TEST)
print("\n  MODEL 3: FCC x COMPLEXITY INTERACTION (Key Test)")
model3 = ols('volatility_outcome ~ fcc * high_complexity + health + financial + prior_breaches + firm_size_log',
             data=reg_data).fit(cov_type='HC3')

coef_fcc_m3 = model3.params['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.params['fcc']
pval_fcc_m3 = model3.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model3.params.index else model3.pvalues['fcc']
coef_complex_m3 = model3.params['high_complexity[T.1]'] if 'high_complexity[T.1]' in model3.params.index else model3.params['high_complexity']
pval_complex_m3 = model3.pvalues['high_complexity[T.1]'] if 'high_complexity[T.1]' in model3.params.index else model3.pvalues['high_complexity']

interact_key = 'fcc[T.1]:high_complexity[T.1]' if 'fcc[T.1]:high_complexity[T.1]' in model3.params.index else 'fcc:high_complexity'
if interact_key in model3.params.index:
    coef_interact = model3.params[interact_key]
    pval_interact = model3.pvalues[interact_key]
else:
    coef_interact = 0
    pval_interact = 1.0

print(f"    FCC Main Effect: {coef_fcc_m3:.4f}pp (p={pval_fcc_m3:.4f})")
print(f"    High Complexity Main Effect: {coef_complex_m3:.4f}pp (p={pval_complex_m3:.4f})")
print(f"    FCC x High Complexity: {coef_interact:.4f}pp (p={pval_interact:.4f})")
print(f"    R-squared = {model3.rsquared:.4f}")

if coef_interact != 0:
    print(f"\n    INTERPRETATION:")
    print(f"    - FCC effect for low-complexity breaches: {coef_fcc_m3:.4f}pp")
    print(f"    - FCC effect for high-complexity breaches: {coef_fcc_m3 + coef_interact:.4f}pp")
    print(f"    - Difference (interaction): {coef_interact:.4f}pp")

    if coef_interact > 0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC VOLATILITY INCREASE IS AMPLIFIED for high-complexity breaches")
        print(f"    This supports the TECHNICAL COMPLEXITY MECHANISM")
        print(f"    Interpretation: Complex breaches need more investigation time,")
        print(f"    so FCC 7-day deadline creates uncertainty & larger volatility increases")
    elif coef_interact < -0.1 and pval_interact < 0.05:
        print(f"\n    FINDING: FCC VOLATILITY INCREASE IS REDUCED for high-complexity breaches")
        print(f"    Alternative: Simple+Fast may create more uncertainty than Complex+Fast")
    else:
        print(f"\n    FINDING: NO SIGNIFICANT INTERACTION")
        print(f"    Complexity does not moderate FCC volatility effect")

# ============================================================================
# SECTION 6: SAVE RESULTS AND GENERATE TABLES
# ============================================================================

print("\n[6/6] Saving results and generating publication tables...")

# Create regression results table
results_table = pd.DataFrame({
    'Model': ['Model 1: FCC Only', 'Model 2: FCC + Complexity', 'Model 3: FCC x Complexity'],
    'FCC Coefficient': [
        f"{coef_fcc_m1:.4f}***" if pval_fcc_m1 < 0.01 else f"{coef_fcc_m1:.4f}**" if pval_fcc_m1 < 0.05 else f"{coef_fcc_m1:.4f}",
        f"{coef_fcc_m2:.4f}***" if pval_fcc_m2 < 0.01 else f"{coef_fcc_m2:.4f}**" if pval_fcc_m2 < 0.05 else f"{coef_fcc_m2:.4f}",
        f"{coef_fcc_m3:.4f}***" if pval_fcc_m3 < 0.01 else f"{coef_fcc_m3:.4f}**" if pval_fcc_m3 < 0.05 else f"{coef_fcc_m3:.4f}"
    ],
    'Complexity Coefficient': [
        'N/A',
        f"{coef_complex:.4f}" if pval_complex > 0.05 else f"{coef_complex:.4f}*",
        f"{coef_complex_m3:.4f}" if pval_complex_m3 > 0.05 else f"{coef_complex_m3:.4f}*"
    ],
    'Interaction': [
        'N/A',
        'N/A',
        f"{coef_interact:.4f}" if pval_interact > 0.05 else f"{coef_interact:.4f}*" if pval_interact < 0.05 else f"{coef_interact:.4f}"
    ],
    'R-squared': [f"{model1.rsquared:.4f}", f"{model2.rsquared:.4f}", f"{model3.rsquared:.4f}"]
})

results_table.to_csv('outputs/tables/TABLE_CVSS_COMPLEXITY_VOLATILITY_RESULTS.csv', index=False)
print(f"  [OK] Saved regression results: outputs/tables/TABLE_CVSS_COMPLEXITY_VOLATILITY_RESULTS.csv")

print("\n" + "=" * 90)
print("ESSAY 2 VOLATILITY: CVSS TECHNICAL COMPLEXITY HETEROGENEITY ANALYSIS COMPLETE")
print("=" * 90)

print("\nKey Findings:")
print(f"  - Sample with CVSS data: {len(reg_data):,} breaches")
print(f"  - Baseline FCC volatility effect: {coef_fcc_m1:.4f}pp")
print(f"  - Complexity main effect: {coef_complex:.4f}pp")
print(f"  - FCC x Complexity interaction: {coef_interact:.4f}pp (p={pval_interact:.4f})")

print("\nInterpretation:")
if coef_interact > 0.1 and pval_interact < 0.05:
    print("  MECHANISM CONFIRMED: Technical complexity amplifies FCC volatility increase")
    print("  Market mechanism: Complex breaches need investigation time that")
    print("  FCC deadline doesn't allow, creating disclosure uncertainty")
elif coef_interact < -0.1 and pval_interact < 0.05:
    print("  ALTERNATIVE: FCC volatility reduced for complex breaches")
    print("  Possible: Market already expects high uncertainty for complex breaches")
else:
    print("  FINDING: Complexity does not significantly moderate FCC volatility effect")
    print("  Similar to Essay 1: FCC works through speed/pressure, not complexity")

print("\n[OK] Essay 2 Mechanism 2 (Complexity) analysis complete!")
