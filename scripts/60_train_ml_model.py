"""
Machine Learning Models for Data Breach Impact Prediction
==========================================================

Trains Random Forest models to predict:
1. Market reactions (30-day CAR)
2. Information asymmetry changes (volatility)

Uses complete enriched dataset with all 85 variables.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("MACHINE LEARNING MODELS - BREACH IMPACT PREDICTION")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/ml_models')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/6] Loading data...")
df = pd.read_csv(DATA_FILE)
print(f"  ✓ Loaded: {len(df):,} breaches × {len(df.columns)} columns")

# Check for required variables
print(f"\n[Step 2/6] Checking available variables...")

# Target variables
targets = {
    'car_30d': 'has_crsp_data',
    'car_5d': 'has_crsp_data',
    'bhar_30d': 'has_crsp_data',
    'bhar_5d': 'has_crsp_data',
    'volatility_change': None
}

available_targets = {}
for target, flag in targets.items():
    if target in df.columns:
        if flag and flag in df.columns:
            count = (df[flag] == True).sum()
        else:
            count = df[target].notna().sum()
        available_targets[target] = count
        print(f"  ✓ {target}: {count:,} observations")

if len(available_targets) == 0:
    print("  ✗ No target variables found!")
    exit()

# ============================================================================
# PREPARE FEATURES
# ============================================================================

print(f"\n[Step 3/6] Preparing features...")

# Define feature groups
feature_groups = {
    'firm_controls': [
        'firm_size_log', 'leverage', 'roa', 'market_to_book',
        'cash_ratio', 'current_ratio', 'total_assets_log'
    ],
    'breach_characteristics': [
        'total_affected', 'total_affected_log',
        'days_to_disclosure', 'immediate_disclosure', 'delayed_disclosure'
    ],
    'prior_breaches': [
        'prior_breaches_total', 'prior_breaches_1yr', 'prior_breaches_3yr',
        'is_repeat_offender', 'days_since_last_breach'
    ],
    'breach_severity': [
        'health_breach', 'financial_breach', 'pii_breach',
        'severity_score', 'breach_type_count'
    ],
    'media_coverage': [
        'media_coverage_count', 'high_media_coverage',
        'major_outlet_coverage', 'major_outlet_flag', 'has_media_coverage'
    ],
    'governance': [
        'sox_404_effective', 'material_weakness',
        'executive_change_30d', 'executive_change_90d', 'executive_change_180d'
    ],
    'regulatory': [
        'has_enforcement', 'enforcement_within_365d',
        'enforcement_within_1yr', 'enforcement_within_2yr'
    ]
}

# Collect all available features
all_features = []
for group_name, features in feature_groups.items():
    available = [f for f in features if f in df.columns]
    all_features.extend(available)
    print(f"  • {group_name}: {len(available)}/{len(features)} available")

print(f"\n  Total features available: {len(all_features)}")

# Remove duplicates
all_features = list(dict.fromkeys(all_features))

# ============================================================================
# MODEL 1: PREDICT 30-DAY CAR
# ============================================================================

print(f"\n[Step 4/6] Training Model 1: 30-day CAR prediction...")

if 'car_30d' in available_targets:
    
    # Prepare data
    model1_data = df[all_features + ['car_30d']].copy()
    
    # Convert to numeric
    for col in all_features:
        model1_data[col] = pd.to_numeric(model1_data[col], errors='coerce')
    
    # Remove missing values
    model1_clean = model1_data.dropna()
    
    print(f"  Sample size: {len(model1_clean):,} observations")
    print(f"  Features: {len(all_features)}")
    print(f"  Target (car_30d): mean={model1_clean['car_30d'].mean():.4f}, std={model1_clean['car_30d'].std():.4f}")
    
    # Split data
    X = model1_clean[all_features]
    y = model1_clean['car_30d']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    print(f"\n  Train/Test split: {len(X_train):,} / {len(X_test):,}")
    
    # Train Random Forest
    print(f"\n  Training Random Forest...")
    rf_model1 = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model1.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = rf_model1.predict(X_train)
    y_pred_test = rf_model1.predict(X_test)
    
    # Metrics
    metrics_m1 = {
        'train_r2': r2_score(y_train, y_pred_train),
        'test_r2': r2_score(y_test, y_pred_test),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
        'test_mae': mean_absolute_error(y_test, y_pred_test)
    }
    
    print(f"\n  Results:")
    print(f"    Train R²: {metrics_m1['train_r2']:.4f}")
    print(f"    Test R²:  {metrics_m1['test_r2']:.4f}")
    print(f"    Test RMSE: {metrics_m1['test_rmse']:.4f}")
    print(f"    Test MAE:  {metrics_m1['test_mae']:.4f}")
    
    # Cross-validation
    print(f"\n  Running 5-fold cross-validation...")
    cv_scores = cross_val_score(rf_model1, X, y, cv=5, scoring='r2', n_jobs=-1)
    print(f"    CV R² (mean): {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    # Feature importance
    importance_m1 = pd.DataFrame({
        'feature': all_features,
        'importance': rf_model1.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_m1['importance_pct'] = (importance_m1['importance'] / importance_m1['importance'].sum() * 100)
    
    print(f"\n  Top 10 most important features:")
    for idx, row in importance_m1.head(10).iterrows():
        print(f"    {row['feature']:<35} {row['importance_pct']:>6.2f}%")
    
    # Save feature importance
    importance_m1.to_csv(OUTPUT_DIR / 'feature_importance_car30d.csv', index=False)
    
else:
    print("  ⚠ Skipping (car_30d not available)")
    rf_model1 = None
    metrics_m1 = None
    importance_m1 = None

# ============================================================================
# MODEL 2: PREDICT VOLATILITY CHANGE
# ============================================================================

print(f"\n[Step 5/6] Training Model 2: Volatility change prediction...")

if 'volatility_change' in available_targets:
    
    # Prepare data
    model2_features = all_features.copy()
    
    # Add pre-breach volatility as control
    if 'return_volatility_pre' in df.columns:
        model2_features.append('return_volatility_pre')
    
    model2_data = df[model2_features + ['volatility_change']].copy()
    
    # Convert to numeric
    for col in model2_features:
        model2_data[col] = pd.to_numeric(model2_data[col], errors='coerce')
    
    # Remove missing values
    model2_clean = model2_data.dropna()
    
    print(f"  Sample size: {len(model2_clean):,} observations")
    print(f"  Features: {len(model2_features)}")
    print(f"  Target (volatility_change): mean={model2_clean['volatility_change'].mean():.4f}")
    
    # Split data
    X2 = model2_clean[model2_features]
    y2 = model2_clean['volatility_change']
    
    X2_train, X2_test, y2_train, y2_test = train_test_split(
        X2, y2, test_size=0.3, random_state=42
    )
    
    print(f"\n  Train/Test split: {len(X2_train):,} / {len(X2_test):,}")
    
    # Train Random Forest
    print(f"\n  Training Random Forest...")
    rf_model2 = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model2.fit(X2_train, y2_train)
    
    # Predictions
    y2_pred_test = rf_model2.predict(X2_test)
    
    # Metrics
    metrics_m2 = {
        'test_r2': r2_score(y2_test, y2_pred_test),
        'test_rmse': np.sqrt(mean_squared_error(y2_test, y2_pred_test)),
        'test_mae': mean_absolute_error(y2_test, y2_pred_test)
    }
    
    print(f"\n  Results:")
    print(f"    Test R²:  {metrics_m2['test_r2']:.4f}")
    print(f"    Test RMSE: {metrics_m2['test_rmse']:.4f}")
    
    # Feature importance
    importance_m2 = pd.DataFrame({
        'feature': model2_features,
        'importance': rf_model2.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_m2['importance_pct'] = (importance_m2['importance'] / importance_m2['importance'].sum() * 100)
    
    print(f"\n  Top 10 most important features:")
    for idx, row in importance_m2.head(10).iterrows():
        print(f"    {row['feature']:<35} {row['importance_pct']:>6.2f}%")
    
    # Save
    importance_m2.to_csv(OUTPUT_DIR / 'feature_importance_volatility.csv', index=False)
    
else:
    print("  ⚠ Skipping (volatility_change not available)")
    rf_model2 = None
    metrics_m2 = None
    importance_m2 = None

# ============================================================================
# VISUALIZATIONS
# ============================================================================

print(f"\n[Step 6/6] Creating visualizations...")

if rf_model1 is not None:
    # Plot 1: Feature Importance (CAR)
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features = importance_m1.head(15)
    ax.barh(range(len(top_features)), top_features['importance_pct'])
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'])
    ax.set_xlabel('Importance (%)')
    ax.set_title('Top 15 Features - CAR Prediction')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'feature_importance_car30d.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: feature_importance_car30d.png")
    
    # Plot 2: Predictions vs Actual (CAR)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(y_test, y_pred_test, alpha=0.5, s=20)
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred_test.min())
    max_val = max(y_test.max(), y_pred_test.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    ax.set_xlabel('Actual CAR (30-day)')
    ax.set_ylabel('Predicted CAR (30-day)')
    ax.set_title(f'Random Forest Predictions vs Actual\nTest R² = {metrics_m1["test_r2"]:.4f}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'predictions_vs_actual_car30d.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: predictions_vs_actual_car30d.png")

if rf_model2 is not None:
    # Plot 3: Feature Importance (Volatility)
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features2 = importance_m2.head(15)
    ax.barh(range(len(top_features2)), top_features2['importance_pct'])
    ax.set_yticks(range(len(top_features2)))
    ax.set_yticklabels(top_features2['feature'])
    ax.set_xlabel('Importance (%)')
    ax.set_title('Top 15 Features - Volatility Change Prediction')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'feature_importance_volatility.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: feature_importance_volatility.png")

# ============================================================================
# SAVE SUMMARY
# ============================================================================

print(f"\nSaving results summary...")

summary = []

if metrics_m1:
    summary.append({
        'Model': 'CAR 30-day',
        'Sample_Size': len(model1_clean),
        'Features': len(all_features),
        'Train_R2': metrics_m1['train_r2'],
        'Test_R2': metrics_m1['test_r2'],
        'Test_RMSE': metrics_m1['test_rmse'],
        'Test_MAE': metrics_m1['test_mae'],
        'CV_R2_Mean': cv_scores.mean(),
        'CV_R2_Std': cv_scores.std()
    })

if metrics_m2:
    summary.append({
        'Model': 'Volatility Change',
        'Sample_Size': len(model2_clean),
        'Features': len(model2_features),
        'Train_R2': np.nan,
        'Test_R2': metrics_m2['test_r2'],
        'Test_RMSE': metrics_m2['test_rmse'],
        'Test_MAE': metrics_m2['test_mae'],
        'CV_R2_Mean': np.nan,
        'CV_R2_Std': np.nan
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv(OUTPUT_DIR / 'ml_model_summary.csv', index=False)

print(f"  ✓ Saved: ml_model_summary.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n" + "=" * 80)
print("✓ MACHINE LEARNING MODELS COMPLETE")
print("=" * 80)

if metrics_m1:
    print(f"\nModel 1: CAR 30-day Prediction")
    print(f"  Sample: {len(model1_clean):,} breaches")
    print(f"  Test R²: {metrics_m1['test_r2']:.4f}")
    print(f"  Test RMSE: {metrics_m1['test_rmse']:.4f}")
    print(f"  5-Fold CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

if metrics_m2:
    print(f"\nModel 2: Volatility Change Prediction")
    print(f"  Sample: {len(model2_clean):,} breaches")
    print(f"  Test R²: {metrics_m2['test_r2']:.4f}")
    print(f"  Test RMSE: {metrics_m2['test_rmse']:.4f}")

print(f"\n📁 All outputs saved to: {OUTPUT_DIR}/")
print(f"\nFiles created:")
print(f"  • ml_model_summary.csv")
print(f"  • feature_importance_car30d.csv")
if rf_model1:
    print(f"  • feature_importance_car30d.png")
    print(f"  • predictions_vs_actual_car30d.png")
if rf_model2:
    print(f"  • feature_importance_volatility.csv")
    print(f"  • feature_importance_volatility.png")

print(f"\n🚀 Models ready for dissertation analysis!")
print("=" * 80)