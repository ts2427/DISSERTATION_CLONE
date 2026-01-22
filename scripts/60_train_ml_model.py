"""
Train ML Models for Breach Impact Prediction

Trains Random Forest and XGBoost models to predict:
1. Essay 2: 30-day Cumulative Abnormal Returns (CAR)
2. Essay 3: Post-breach stock return volatility

Outputs:
- Trained models (pickled)
- Feature importance rankings
- Cross-validation results
- Model metrics for comparison to OLS
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from sklearn.model_selection import train_test_split

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from ml_models import BreachImpactModel, ModelEvaluator, FeatureImportanceAnalyzer

print("=" * 90)
print("TRAIN ML MODELS FOR BREACH IMPACT PREDICTION")
print("=" * 90)

# Configuration
DATA_PATH = Path(__file__).parent.parent / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs' / 'ml_models'
MODELS_DIR = OUTPUT_DIR / 'trained_models'

# Create output directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n[1/6] Loading data from {DATA_PATH.name}...")

if not DATA_PATH.exists():
    print(f"ERROR: Data file not found at {DATA_PATH}")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)
print(f"  Loaded: {len(df)} breaches × {len(df.columns)} columns")

# ============================================================================
# ESSAY 2: CAR 30-DAY PREDICTION
# ============================================================================

print(f"\n[2/6] Training models for Essay 2 (30-day CAR prediction)...")

# Prepare data for Essay 2
essay2_features = [
    'immediate_disclosure', 'fcc_reportable', 'firm_size_log', 'leverage', 'roa',
    'prior_breaches_total', 'high_severity_breach', 'ransomware', 'health_breach',
    'executive_change_30d', 'days_to_disclosure', 'total_affected',
    'is_repeat_offender', 'governance_score'
]

# Filter available features
essay2_features_available = [f for f in essay2_features if f in df.columns]

# Clean data: convert to numeric and remove rows with invalid values
essay2_data = df[essay2_features_available + ['car_30d']].copy()
for col in essay2_features_available:
    essay2_data[col] = pd.to_numeric(essay2_data[col], errors='coerce')
essay2_data = essay2_data.dropna()

print(f"  Sample size: {len(essay2_data)} breaches")
print(f"  Features: {len(essay2_features_available)}")
print(f"  Target: car_30d (Mean: {essay2_data['car_30d'].mean():.4f}, Std: {essay2_data['car_30d'].std():.4f})")

# Separate features and target
X_essay2 = essay2_data[essay2_features_available]
y_essay2 = essay2_data['car_30d']

# Train/test split (70/30)
X_train_e2, X_test_e2, y_train_e2, y_test_e2 = train_test_split(
    X_essay2, y_essay2, test_size=0.3, random_state=42
)

print(f"\n  Train/Test Split: {len(X_train_e2)} / {len(X_test_e2)}")

# Initialize and train Random Forest (Essay 2)
print(f"\n  Training Random Forest...")
rf_e2 = BreachImpactModel(model_type='rf', random_state=42, verbose=False)
rf_e2.feature_names = essay2_features_available
rf_e2.initialize_model(n_estimators=100, max_depth=10, min_samples_leaf=5)
rf_e2.train(X_train_e2, y_train_e2)
rf_e2_metrics = rf_e2.evaluate(X_test_e2, y_test_e2, X_train_e2, y_train_e2)
rf_e2.save_model(MODELS_DIR / 'rf_essay2_car30d.pkl')

# Initialize and train Gradient Boosting (Essay 2)
print(f"  Training Gradient Boosting...")
gb_e2 = BreachImpactModel(model_type='gb', random_state=42, verbose=False)
gb_e2.feature_names = essay2_features_available
gb_e2.initialize_model(n_estimators=100, max_depth=4, learning_rate=0.1)
gb_e2.train(X_train_e2, y_train_e2)
gb_e2_metrics = gb_e2.evaluate(X_test_e2, y_test_e2, X_train_e2, y_train_e2)
gb_e2.save_model(MODELS_DIR / 'gb_essay2_car30d.pkl')

print(f"\n  Essay 2 Results:")
print(f"    Random Forest    - R²: {rf_e2_metrics['test_r2']:.4f}, RMSE: {rf_e2_metrics['test_rmse']:.4f}")
print(f"    Gradient Boost   - R²: {gb_e2_metrics['test_r2']:.4f}, RMSE: {gb_e2_metrics['test_rmse']:.4f}")

# ============================================================================
# ESSAY 3: POST-BREACH VOLATILITY PREDICTION
# ============================================================================

print(f"\n[3/6] Training models for Essay 3 (post-breach volatility prediction)...")

# Prepare data for Essay 3
essay3_features = [
    'return_volatility_pre', 'immediate_disclosure', 'fcc_reportable',
    'firm_size_log', 'leverage', 'roa', 'large_firm',
    'prior_breaches_total', 'high_severity_breach', 'executive_change_30d',
    'days_to_disclosure', 'total_affected', 'is_repeat_offender'
]

# Filter available features
essay3_features_available = [f for f in essay3_features if f in df.columns]

# Clean data: convert to numeric and remove rows with invalid values
essay3_data = df[essay3_features_available + ['return_volatility_post']].copy()
for col in essay3_features_available:
    essay3_data[col] = pd.to_numeric(essay3_data[col], errors='coerce')
essay3_data = essay3_data.dropna()

print(f"  Sample size: {len(essay3_data)} breaches")
print(f"  Features: {len(essay3_features_available)}")
print(f"  Target: return_volatility_post (Mean: {essay3_data['return_volatility_post'].mean():.4f})")

# Separate features and target
X_essay3 = essay3_data[essay3_features_available]
y_essay3 = essay3_data['return_volatility_post']

# Train/test split (70/30)
X_train_e3, X_test_e3, y_train_e3, y_test_e3 = train_test_split(
    X_essay3, y_essay3, test_size=0.3, random_state=42
)

print(f"\n  Train/Test Split: {len(X_train_e3)} / {len(X_test_e3)}")

# Initialize and train Random Forest (Essay 3)
print(f"\n  Training Random Forest...")
rf_e3 = BreachImpactModel(model_type='rf', random_state=42, verbose=False)
rf_e3.feature_names = essay3_features_available
rf_e3.initialize_model(n_estimators=100, max_depth=10, min_samples_leaf=5)
rf_e3.train(X_train_e3, y_train_e3)
rf_e3_metrics = rf_e3.evaluate(X_test_e3, y_test_e3, X_train_e3, y_train_e3)
rf_e3.save_model(MODELS_DIR / 'rf_essay3_volatility.pkl')

# Initialize and train Gradient Boosting (Essay 3)
print(f"  Training Gradient Boosting...")
gb_e3 = BreachImpactModel(model_type='gb', random_state=42, verbose=False)
gb_e3.feature_names = essay3_features_available
gb_e3.initialize_model(n_estimators=100, max_depth=4, learning_rate=0.1)
gb_e3.train(X_train_e3, y_train_e3)
gb_e3_metrics = gb_e3.evaluate(X_test_e3, y_test_e3, X_train_e3, y_train_e3)
gb_e3.save_model(MODELS_DIR / 'gb_essay3_volatility.pkl')

print(f"\n  Essay 3 Results:")
print(f"    Random Forest    - R²: {rf_e3_metrics['test_r2']:.4f}, RMSE: {rf_e3_metrics['test_rmse']:.4f}")
print(f"    Gradient Boost   - R²: {gb_e3_metrics['test_r2']:.4f}, RMSE: {gb_e3_metrics['test_rmse']:.4f}")

# ============================================================================
# CROSS-VALIDATION
# ============================================================================

print(f"\n[4/6] Cross-validation (5-fold time-aware splits)...")

print(f"\n  Essay 2 (CAR prediction):")
cv_rf_e2 = rf_e2.cross_validate(X_essay2, y_essay2, n_splits=5, time_aware=True)
print(f"    Random Forest CV R²: {cv_rf_e2['mean_r2']:.4f} (±{cv_rf_e2['std_r2']:.4f})")

print(f"\n  Essay 3 (Volatility prediction):")
cv_rf_e3 = rf_e3.cross_validate(X_essay3, y_essay3, n_splits=5, time_aware=True)
print(f"    Random Forest CV R²: {cv_rf_e3['mean_r2']:.4f} (±{cv_rf_e3['std_r2']:.4f})")

# ============================================================================
# FEATURE IMPORTANCE & ANALYSIS
# ============================================================================

print(f"\n[5/6] Analyzing feature importance...")

evaluator = ModelEvaluator(output_dir=OUTPUT_DIR, verbose=False)
importance_analyzer = FeatureImportanceAnalyzer(output_dir=OUTPUT_DIR, verbose=False)

# Essay 2 feature importance
print(f"\n  Essay 2 (CAR) - Top 10 Features:")
importance_e2_rf = rf_e2.get_feature_importance().head(10)
for idx, row in importance_e2_rf.iterrows():
    print(f"    {row['feature']:<25} {row['importance_pct']:>6.2f}%")

# Essay 3 feature importance
print(f"\n  Essay 3 (Volatility) - Top 10 Features:")
importance_e3_rf = rf_e3.get_feature_importance().head(10)
for idx, row in importance_e3_rf.iterrows():
    print(f"    {row['feature']:<25} {row['importance_pct']:>6.2f}%")

# Generate visualizations
print(f"\n  Generating visualizations...")
evaluator.plot_predictions_vs_actual(y_test_e2, rf_e2.predict(X_test_e2), 'Random Forest', 'CAR 30d')
evaluator.plot_predictions_vs_actual(y_test_e3, rf_e3.predict(X_test_e3), 'Random Forest', 'Volatility')

importance_analyzer.plot_feature_importance(importance_e2_rf, 'Random Forest (Essay 2)', top_n=12)
importance_analyzer.plot_feature_importance(importance_e3_rf, 'Random Forest (Essay 3)', top_n=12)

# ============================================================================
# SAVE RESULTS & METADATA
# ============================================================================

print(f"\n[6/6] Saving results and metadata...")

# Create results summary
results_summary = {
    'essay2': {
        'description': '30-day Cumulative Abnormal Returns (CAR) Prediction',
        'sample_size': len(essay2_data),
        'train_test_split': f"{len(X_train_e2)}/{len(X_test_e2)}",
        'features': essay2_features_available,
        'random_forest': {
            'test_r2': float(rf_e2_metrics['test_r2']),
            'test_rmse': float(rf_e2_metrics['test_rmse']),
            'test_mae': float(rf_e2_metrics['test_mae']),
            'correlation': float(rf_e2_metrics['correlation']),
            'cv_r2_mean': float(cv_rf_e2['mean_r2']),
            'cv_r2_std': float(cv_rf_e2['std_r2']),
        },
        'gradient_boosting': {
            'test_r2': float(gb_e2_metrics['test_r2']),
            'test_rmse': float(gb_e2_metrics['test_rmse']),
            'test_mae': float(gb_e2_metrics['test_mae']),
            'correlation': float(gb_e2_metrics['correlation']),
        },
    },
    'essay3': {
        'description': 'Post-Breach Stock Return Volatility Prediction',
        'sample_size': len(essay3_data),
        'train_test_split': f"{len(X_train_e3)}/{len(X_test_e3)}",
        'features': essay3_features_available,
        'random_forest': {
            'test_r2': float(rf_e3_metrics['test_r2']),
            'test_rmse': float(rf_e3_metrics['test_rmse']),
            'test_mae': float(rf_e3_metrics['test_mae']),
            'correlation': float(rf_e3_metrics['correlation']),
            'cv_r2_mean': float(cv_rf_e3['mean_r2']),
            'cv_r2_std': float(cv_rf_e3['std_r2']),
        },
        'gradient_boosting': {
            'test_r2': float(gb_e3_metrics['test_r2']),
            'test_rmse': float(gb_e3_metrics['test_rmse']),
            'test_mae': float(gb_e3_metrics['test_mae']),
            'correlation': float(gb_e3_metrics['correlation']),
        },
    }
}

# Save metadata
with open(OUTPUT_DIR / 'ml_model_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

# Save feature importance tables
importance_e2_rf.to_csv(OUTPUT_DIR / 'feature_importance_essay2_rf.csv', index=False)
importance_e3_rf.to_csv(OUTPUT_DIR / 'feature_importance_essay3_rf.csv', index=False)

print(f"\n  Saved results to {OUTPUT_DIR}")
print(f"  - ml_model_results.json (metrics)")
print(f"  - feature_importance_essay2_rf.csv")
print(f"  - feature_importance_essay3_rf.csv")
print(f"  - Trained models in {MODELS_DIR}")
print(f"  - Visualizations (PNG files)")

print(f"\n" + "=" * 90)
print("MODEL TRAINING COMPLETE")
print("=" * 90)

print(f"\nKey Results Summary:")
print(f"\nEssay 2 (CAR Prediction):")
print(f"  Random Forest Test R²:     {rf_e2_metrics['test_r2']:.4f}")
print(f"  Gradient Boosting Test R²: {gb_e2_metrics['test_r2']:.4f}")
print(f"  5-Fold CV R² (RF):         {cv_rf_e2['mean_r2']:.4f} (±{cv_rf_e2['std_r2']:.4f})")

print(f"\nEssay 3 (Volatility Prediction):")
print(f"  Random Forest Test R²:     {rf_e3_metrics['test_r2']:.4f}")
print(f"  Gradient Boosting Test R²: {gb_e3_metrics['test_r2']:.4f}")
print(f"  5-Fold CV R² (RF):         {cv_rf_e3['mean_r2']:.4f} (±{cv_rf_e3['std_r2']:.4f})")

print(f"\nNext: Run script 61_ml_validation.py to compare with OLS and generate robustness sections")
