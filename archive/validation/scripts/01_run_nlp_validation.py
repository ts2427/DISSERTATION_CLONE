"""
NLP Classifier Validation Script

Compares NLP classifications against manually coded breaches.
Calculates precision, recall, F1-score for each breach category.
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validation.nlp_validation import BreachClassifier

print("=" * 80)
print("NLP CLASSIFIER VALIDATION")
print("=" * 80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default paths (can be overridden via command line)
NLP_OUTPUT_PATH = 'Data/enrichment/breach_severity_classification.csv'
DEFAULT_MANUAL_CODES_PATH = None  # User must provide this
OUTPUT_DIR = 'validation_results'

# Parse command line arguments
manual_codes_path = None
if len(sys.argv) > 1:
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--manual-codes' and i + 1 < len(sys.argv) - 1:
            manual_codes_path = sys.argv[i + 2]

if not manual_codes_path:
    print("\nERROR: Must provide path to manually coded breaches")
    print("Usage: python 01_run_nlp_validation.py --manual-codes <path_to_csv>")
    print("\nExample:")
    print("  python 01_run_nlp_validation.py --manual-codes manual_codes_2026_01_22.csv")
    sys.exit(1)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[1/5] Loading data...")

# Load NLP classifications
if not Path(NLP_OUTPUT_PATH).exists():
    print(f"ERROR: NLP output not found at {NLP_OUTPUT_PATH}")
    sys.exit(1)

nlp_df = pd.read_csv(NLP_OUTPUT_PATH)
print(f"  NLP classifications: {len(nlp_df)} breaches")

# Load manual codes
if not Path(manual_codes_path).exists():
    print(f"ERROR: Manual codes not found at {manual_codes_path}")
    sys.exit(1)

manual_df = pd.read_csv(manual_codes_path)
print(f"  Manual codes: {len(manual_df)} breaches")

# ============================================================================
# PREPARE DATA
# ============================================================================

print(f"\n[2/5] Preparing data...")

# Breach type columns
breach_types = [
    'pii_breach', 'health_breach', 'financial_breach', 'ip_breach',
    'ransomware', 'nation_state', 'insider_threat', 'ddos_attack',
    'phishing', 'malware'
]

# Find matching columns in manual codes
# Could be named "pii_breach_manual", "pii_breach", or similar
manual_cols = {}
for breach_type in breach_types:
    # Check for variations
    candidates = [
        breach_type,
        f'{breach_type}_manual',
        f'manual_{breach_type}',
    ]
    found_col = None
    for candidate in candidates:
        if candidate in manual_df.columns:
            found_col = candidate
            break

    if not found_col:
        print(f"WARNING: Could not find column for {breach_type}")
        print(f"  Tried: {candidates}")
        print(f"  Available columns: {list(manual_df.columns)}")
        sys.exit(1)

    manual_cols[breach_type] = found_col

print(f"  Found {len(manual_cols)} breach type columns")

# Ensure breach_id column for alignment
if 'breach_id' not in nlp_df.columns:
    nlp_df['breach_id'] = range(len(nlp_df))

if 'breach_id' not in manual_df.columns:
    if 'sample_id' in manual_df.columns:
        manual_df['breach_id'] = manual_df['sample_id'] - 1  # Convert 1-indexed to 0-indexed
    else:
        manual_df['breach_id'] = range(len(manual_df))

# Merge on breach_id
merged_df = pd.merge(nlp_df, manual_df, on='breach_id', how='inner')
print(f"  Merged: {len(merged_df)} breaches in both datasets")

if len(merged_df) == 0:
    print("ERROR: No matching breaches found between NLP output and manual codes")
    sys.exit(1)

# ============================================================================
# CALCULATE METRICS
# ============================================================================

print(f"\n[3/5] Calculating metrics...")

metrics = {
    'overall': {},
    'per_category': {},
    'confusion_matrices': {}
}

all_y_true = []
all_y_pred = []

for breach_type in breach_types:
    nlp_col = breach_type
    manual_col = manual_cols[breach_type]

    y_true = merged_df[manual_col].values
    y_pred = merged_df[nlp_col].values

    # Handle any non-binary values
    y_true = np.where(y_true > 0, 1, 0)
    y_pred = np.where(y_pred > 0, 1, 0)

    # Calculate metrics
    try:
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred).tolist()

        metrics['per_category'][breach_type] = {
            'precision': float(prec),
            'recall': float(rec),
            'f1_score': float(f1),
            'n_samples': len(y_true),
            'n_positive_true': int(y_true.sum()),
            'n_positive_pred': int(y_pred.sum()),
        }
        metrics['confusion_matrices'][breach_type] = cm

        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

        print(f"  {breach_type:20} | Prec: {prec:.3f} | Rec: {rec:.3f} | F1: {f1:.3f}")

    except Exception as e:
        print(f"ERROR calculating metrics for {breach_type}: {e}")

# Overall metrics
try:
    all_y_true = np.array(all_y_true)
    all_y_pred = np.array(all_y_pred)

    overall_prec = precision_score(all_y_true, all_y_pred, average='weighted', zero_division=0)
    overall_rec = recall_score(all_y_true, all_y_pred, average='weighted', zero_division=0)
    overall_f1 = f1_score(all_y_true, all_y_pred, average='weighted', zero_division=0)
    accuracy = (all_y_true == all_y_pred).mean()

    metrics['overall'] = {
        'weighted_precision': float(overall_prec),
        'weighted_recall': float(overall_rec),
        'weighted_f1': float(overall_f1),
        'accuracy': float(accuracy),
        'n_total_samples': len(all_y_true),
        'validation_date': datetime.now().isoformat(),
    }

except Exception as e:
    print(f"ERROR calculating overall metrics: {e}")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print(f"\n[4/5] Saving results...")

# Create output directory
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Save metrics as JSON
metrics_path = Path(OUTPUT_DIR) / 'validation_metrics.json'
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"  Saved metrics: {metrics_path}")

# Save summary table as CSV
summary_data = []
for breach_type in breach_types:
    cat_metrics = metrics['per_category'].get(breach_type, {})
    summary_data.append({
        'breach_type': breach_type,
        'precision': cat_metrics.get('precision', 0),
        'recall': cat_metrics.get('recall', 0),
        'f1_score': cat_metrics.get('f1_score', 0),
        'n_samples': cat_metrics.get('n_samples', 0),
        'n_positive_true': cat_metrics.get('n_positive_true', 0),
    })

summary_df = pd.DataFrame(summary_data)
summary_path = Path(OUTPUT_DIR) / 'validation_summary.csv'
summary_df.to_csv(summary_path, index=False)
print(f"  Saved summary: {summary_path}")

# ============================================================================
# PRINT SUMMARY
# ============================================================================

print(f"\n[5/5] Summary")
print("\n" + "=" * 80)
print("VALIDATION RESULTS")
print("=" * 80)

print(f"\nValidation Sample: {metrics['overall']['n_total_samples']} classifications")
print(f"Validation Date: {metrics['overall']['validation_date'][:10]}")

print(f"\nOVERALL METRICS:")
print(f"  Weighted Precision: {metrics['overall']['weighted_precision']:.3f}")
print(f"  Weighted Recall:    {metrics['overall']['weighted_recall']:.3f}")
print(f"  Weighted F1:        {metrics['overall']['weighted_f1']:.3f}")
print(f"  Accuracy:           {metrics['overall']['accuracy']:.3f}")

print(f"\nPER-CATEGORY METRICS:")
print(f"{'Breach Type':<20} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Samples':>10}")
print("-" * 65)
for breach_type in breach_types:
    cat = metrics['per_category'].get(breach_type, {})
    print(f"{breach_type:<20} {cat.get('precision', 0):>10.3f} {cat.get('recall', 0):>10.3f} {cat.get('f1_score', 0):>10.3f} {cat.get('n_samples', 0):>10}")

print("\n" + "=" * 80)
print("INTERPRETATION:")
print("=" * 80)
print("""
Precision: Of predicted positives, what % were actually positive?
  - High precision = low false positive rate
  - Good for: High cost of false alarms

Recall: Of actual positives, what % did we find?
  - High recall = low false negative rate
  - Good for: High cost of missing cases

F1: Harmonic mean of precision and recall
  - Balanced metric (0-1, higher is better)
  - Good overall performance > 0.80
""")

# Recommendations
poor_performance = [bt for bt in breach_types
                   if metrics['per_category'].get(bt, {}).get('f1_score', 0) < 0.75]

if poor_performance:
    print(f"\nAREAS FOR IMPROVEMENT:")
    for bt in poor_performance:
        cat = metrics['per_category'][bt]
        print(f"  • {bt}: F1={cat['f1_score']:.3f}")
        if cat['recall'] < cat['precision']:
            print(f"    → Low recall: classifier missing cases. Add keywords.")
        else:
            print(f"    → Low precision: classifier over-sensitive. Reduce keywords.")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print(f"\nResults saved to: {OUTPUT_DIR}/")
