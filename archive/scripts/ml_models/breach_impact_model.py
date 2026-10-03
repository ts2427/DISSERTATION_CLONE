"""
Breach Impact Prediction Model

Unified interface for Random Forest and XGBoost models predicting breach market impact.
Handles preprocessing, training, evaluation, and prediction.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')


class BreachImpactModel:
    """
    Unified model interface for predicting breach market impact (CAR or volatility).

    Supports:
    - Random Forest regression
    - Gradient Boosting (XGBoost alternative) regression
    - Preprocessing and feature scaling
    - Time-aware cross-validation
    - Prediction with uncertainty quantification
    """

    def __init__(self, model_type='rf', random_state=42, verbose=True):
        """
        Initialize breach impact model.

        Args:
            model_type (str): 'rf' for RandomForest, 'gb' for GradientBoosting
            random_state (int): Random seed for reproducibility
            verbose (bool): Print progress messages
        """
        self.model_type = model_type
        self.random_state = random_state
        self.verbose = verbose
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None
        self.preprocessed = False

    def initialize_model(self, **hyperparams):
        """
        Initialize ML model with hyperparameters.

        Args:
            **hyperparams: Model-specific hyperparameters
        """
        if self.model_type == 'rf':
            self._init_random_forest(**hyperparams)
        elif self.model_type == 'gb':
            self._init_gradient_boosting(**hyperparams)
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

        if self.verbose:
            print(f"[✓] Initialized {self.model_type.upper()} model")

    def _init_random_forest(self, **hyperparams):
        """Initialize RandomForest with default or custom hyperparameters."""
        defaults = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'max_features': 'sqrt',
            'random_state': self.random_state,
            'n_jobs': -1,
            'bootstrap': True,
        }
        defaults.update(hyperparams)
        self.model = RandomForestRegressor(**defaults)

    def _init_gradient_boosting(self, **hyperparams):
        """Initialize GradientBoosting with default or custom hyperparameters."""
        defaults = {
            'n_estimators': 100,
            'max_depth': 4,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'max_features': 0.8,
            'random_state': self.random_state,
            'verbose': 0,
        }
        defaults.update(hyperparams)
        self.model = GradientBoostingRegressor(**defaults)

    def preprocess_features(self, df, target_col='car_30d', features=None,
                           handle_missing='drop', scale=True):
        """
        Preprocess features for ML model.

        Args:
            df (pd.DataFrame): Input dataframe
            target_col (str): Name of target variable
            features (list): Feature names to use. If None, auto-detect.
            handle_missing (str): 'drop' removes rows with NaN, 'mean' imputes
            scale (bool): Whether to scale features with StandardScaler

        Returns:
            tuple: (X, y, feature_names)
        """
        # Make copy to avoid modifying original
        data = df.copy()

        # Auto-detect features if not provided
        if features is None:
            exclude_cols = [
                target_col, 'org_name', 'ticker', 'cik', 'firm_name',
                'breach_id', 'sample_id', 'index'
            ]
            features = [col for col in data.columns
                       if col not in exclude_cols and data[col].dtype in [np.float64, np.int64]]

        # Extract X and y
        X = data[features].copy()
        y = data[target_col].copy()

        # Handle missing values
        if handle_missing == 'drop':
            mask = X.notna().all(axis=1) & y.notna()
            X = X[mask]
            y = y[mask]
        elif handle_missing == 'mean':
            X = X.fillna(X.mean())

        # Scale features
        if scale:
            X_scaled = self.scaler.fit_transform(X)
            X = pd.DataFrame(X_scaled, columns=features, index=X.index)

        self.feature_names = features
        self.preprocessed = True

        if self.verbose:
            print(f"[✓] Preprocessed {len(features)} features, {len(X)} samples")

        return X, y, features

    def train(self, X, y, verbose_eval=False):
        """
        Train model on provided data.

        Args:
            X (pd.DataFrame): Feature matrix
            y (pd.Series): Target variable
            verbose_eval (bool): Print training progress (GB only)

        Returns:
            dict: Training metrics
        """
        if self.model is None:
            self.initialize_model()

        self.model.fit(X, y)

        # Training metrics
        train_pred = self.model.predict(X)
        train_rmse = np.sqrt(np.mean((y - train_pred) ** 2))
        train_r2 = self.model.score(X, y)

        metrics = {
            'n_samples': len(X),
            'train_rmse': train_rmse,
            'train_r2': train_r2,
        }

        if self.verbose:
            print(f"[✓] Trained {self.model_type.upper()} model")
            print(f"    Training RMSE: {train_rmse:.4f}")
            print(f"    Training R²: {train_r2:.4f}")

        return metrics

    def evaluate(self, X_test, y_test, X_train=None, y_train=None):
        """
        Evaluate model on test set.

        Args:
            X_test (pd.DataFrame): Test feature matrix
            y_test (pd.Series): Test target values
            X_train (pd.DataFrame): Training features (optional, for train vs test comparison)
            y_train (pd.Series): Training targets (optional)

        Returns:
            dict: Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")

        # Test metrics
        y_pred = self.model.predict(X_test)
        test_rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        test_mae = np.mean(np.abs(y_test - y_pred))
        test_r2 = self.model.score(X_test, y_test)
        correlation = np.corrcoef(y_test, y_pred)[0, 1]

        metrics = {
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_r2': test_r2,
            'correlation': correlation,
            'n_test': len(X_test),
        }

        # Optional train comparison
        if X_train is not None and y_train is not None:
            y_train_pred = self.model.predict(X_train)
            train_r2 = self.model.score(X_train, y_train)
            metrics['train_r2'] = train_r2
            metrics['overfitting_gap'] = abs(train_r2 - test_r2)

        if self.verbose:
            print(f"[✓] Evaluated {self.model_type.upper()} model")
            print(f"    Test RMSE: {test_rmse:.4f}")
            print(f"    Test MAE: {test_mae:.4f}")
            print(f"    Test R²: {test_r2:.4f}")
            print(f"    Correlation (actual vs pred): {correlation:.4f}")

        return metrics

    def cross_validate(self, X, y, n_splits=5, time_aware=True):
        """
        Cross-validate model using time-aware splits.

        Args:
            X (pd.DataFrame): Feature matrix
            y (pd.Series): Target variable
            n_splits (int): Number of CV folds
            time_aware (bool): Use TimeSeriesSplit for temporal ordering

        Returns:
            dict: Cross-validation results
        """
        if time_aware:
            cv = TimeSeriesSplit(n_splits=n_splits)
        else:
            from sklearn.model_selection import KFold
            cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        fold_results = []

        for fold, (train_idx, test_idx) in enumerate(cv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Train and evaluate
            if self.model is None:
                self.initialize_model()
            else:
                # Reinitialize for fresh fold
                if self.model_type == 'rf':
                    self._init_random_forest()
                else:
                    self._init_gradient_boosting()

            self.model.fit(X_train, y_train)

            fold_metrics = self.evaluate(X_test, y_test, X_train, y_train)
            fold_metrics['fold'] = fold
            fold_results.append(fold_metrics)

        # Aggregate CV results
        cv_results = {
            'n_folds': n_splits,
            'mean_r2': np.mean([r['test_r2'] for r in fold_results]),
            'std_r2': np.std([r['test_r2'] for r in fold_results]),
            'mean_rmse': np.mean([r['test_rmse'] for r in fold_results]),
            'fold_details': fold_results,
        }

        if self.verbose:
            print(f"[✓] {n_splits}-Fold Cross-Validation Results:")
            print(f"    Mean R²: {cv_results['mean_r2']:.4f} (±{cv_results['std_r2']:.4f})")
            print(f"    Mean RMSE: {cv_results['mean_rmse']:.4f}")

        return cv_results

    def predict(self, X):
        """
        Make predictions on new data.

        Args:
            X (pd.DataFrame): Feature matrix

        Returns:
            np.array: Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")

        return self.model.predict(X)

    def predict_with_intervals(self, X, percentile=95):
        """
        Predict with uncertainty intervals (RF only).

        Args:
            X (pd.DataFrame): Feature matrix
            percentile (int): Confidence level for intervals

        Returns:
            pd.DataFrame: Predictions with lower/upper bounds
        """
        if self.model_type != 'rf':
            raise NotImplementedError("Prediction intervals only implemented for Random Forest")

        predictions = []

        for estimator in self.model.estimators_:
            predictions.append(estimator.predict(X))

        predictions = np.array(predictions)

        mean_pred = predictions.mean(axis=0)
        lower = np.percentile(predictions, (100 - percentile) / 2, axis=0)
        upper = np.percentile(predictions, 100 - (100 - percentile) / 2, axis=0)

        return pd.DataFrame({
            'prediction': mean_pred,
            f'lower_{percentile}': lower,
            f'upper_{percentile}': upper,
        })

    def get_feature_importance(self):
        """
        Get feature importance from trained model.

        Returns:
            pd.DataFrame: Features ranked by importance
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")

        importances = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances,
            'importance_pct': importances / importances.sum() * 100,
        }).sort_values('importance', ascending=False)

        return importance_df

    def save_model(self, path):
        """Save trained model to disk."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        if self.verbose:
            print(f"[✓] Model saved to {path}")

    def load_model(self, path):
        """Load trained model from disk."""
        import pickle
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        if self.verbose:
            print(f"[✓] Model loaded from {path}")
