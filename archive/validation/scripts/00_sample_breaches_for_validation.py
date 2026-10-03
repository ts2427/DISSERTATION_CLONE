"""
Sample Breaches for Manual Validation Coding

Selects 150 representative breaches from the dataset for manual coding.
Uses stratified sampling to ensure:
- All breach types represented
- Balanced difficulty (all severity levels)
- Random unbiased selection
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("SAMPLING BREACHES FOR NLP VALIDATION")
print("=" * 80)

# Load dataset
data_path = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
print(f"\nLoading: {data_path}")
df = pd.read_csv(data_path)
print(f"Total breaches: {len(df)}")

# Set random seed for reproducibility
np.random.seed(42)

# Stratified sampling parameters
n_samples = 150
print(f"\nStratified sampling: {n_samples} breaches")

# Strategy: Sample from multiple strata to ensure representation
try:
    # Get combined_severity_score if it exists, else use alternative
    if 'combined_severity_score' in df.columns:
        severity_col = 'combined_severity_score'
    elif 'severity_score' in df.columns:
        severity_col = 'severity_score'
    else:
        severity_col = None

    if severity_col:
        # Create severity quartiles for stratification
        df['_severity_quartile'] = pd.qcut(df[severity_col], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
        print(f"Using {severity_col} for stratification")

        # Stratified sample across quartiles
        samples_per_quartile = n_samples // 4
        sampled = df.groupby('_severity_quartile', group_keys=False).apply(
            lambda x: x.sample(n=min(samples_per_quartile, len(x)), random_state=42)
        )

        # If we need more samples to reach n_samples, add randomly
        if len(sampled) < n_samples:
            remaining = n_samples - len(sampled)
            remaining_df = df[~df.index.isin(sampled.index)]
            additional = remaining_df.sample(n=min(remaining, len(remaining_df)), random_state=42)
            sampled = pd.concat([sampled, additional])
        elif len(sampled) > n_samples:
            sampled = sampled.sample(n=n_samples, random_state=42)
    else:
        # Simple random sample if no severity data
        sampled = df.sample(n=n_samples, random_state=42)

except Exception as e:
    print(f"Warning: Could not stratify ({e}), using simple random sample")
    sampled = df.sample(n=n_samples, random_state=42)

# Remove temporary column
if '_severity_quartile' in sampled.columns:
    sampled = sampled.drop(columns=['_severity_quartile'])

print(f"Sampled: {len(sampled)} breaches")

# Select relevant columns for manual coding
output_cols = [
    'org_name', 'breach_date', 'incident_details', 'information_affected',
    'total_affected', 'breach_type', 'disclosed_date'
]

# Check which columns exist
available_cols = [col for col in output_cols if col in sampled.columns]
print(f"\nAvailable columns for manual coding: {len(available_cols)}")

# Add mandatory columns for coding
coding_cols = available_cols + [
    'pii_breach_manual', 'health_breach_manual', 'financial_breach_manual',
    'ip_breach_manual', 'ransomware_manual', 'nation_state_manual',
    'insider_threat_manual', 'ddos_attack_manual', 'phishing_manual',
    'malware_manual'
]

# Create output DataFrame
output_df = sampled[available_cols].copy()
output_df.insert(0, 'sample_id', range(1, len(output_df) + 1))

# Add empty columns for manual coding
for col in ['pii_breach_manual', 'health_breach_manual', 'financial_breach_manual',
            'ip_breach_manual', 'ransomware_manual', 'nation_state_manual',
            'insider_threat_manual', 'ddos_attack_manual', 'phishing_manual',
            'malware_manual']:
    output_df[col] = ''

# Add instruction column
output_df['CODER_INSTRUCTIONS'] = 'Enter 0 (no) or 1 (yes) for each breach type'

# Save to CSV
output_path = 'validation/nlp_validation/sample_breaches_for_coding.csv'
output_df.to_csv(output_path, index=False)
print(f"\nSaved sample to: {output_path}")
print(f"Size: {len(output_df)} rows × {len(output_df.columns)} columns")

# Create Excel template as well
try:
    excel_path = 'validation/nlp_validation/manual_coding_template.xlsx'
    output_df.to_excel(excel_path, index=False, sheet_name='Breaches to Code')
    print(f"Saved Excel template to: {excel_path}")
except:
    print("(Could not create Excel template - use CSV instead)")

# Summary
print("\n" + "=" * 80)
print("SAMPLING COMPLETE")
print("=" * 80)
print(f"\nNext steps:")
print("1. Open: validation/nlp_validation/sample_breaches_for_coding.csv")
print("2. For each breach, manually code the 10 breach type columns")
print("3. Use 0 = No, 1 = Yes")
print("4. Save as: manual_codes_YYYY_MM_DD.csv")
print("5. Run: validation/scripts/01_run_nlp_validation.py")
print("   with --manual-codes parameter pointing to your coded file")

print("\nBreach Types to Code:")
print("  • pii_breach: Personally identifiable information")
print("  • health_breach: Protected health information (HIPAA)")
print("  • financial_breach: Financial account/payment data")
print("  • ip_breach: Intellectual property or trade secrets")
print("  • ransomware: Ransom/encryption attack")
print("  • nation_state: Nation-state or advanced persistent threat")
print("  • insider_threat: Employee or insider involvement")
print("  • ddos_attack: Denial of service attack")
print("  • phishing: Phishing or social engineering")
print("  • malware: Malware, virus, trojan, etc.")

print("\n" + "=" * 80)
