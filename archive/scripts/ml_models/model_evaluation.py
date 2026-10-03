"""
Model Evaluation & Comparison

Provides utilities for evaluating ML models, comparing to OLS, and generating visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class ModelEvaluator:
    """Evaluate and compare ML models to OLS regressions."""

    def __init__(self, output_dir='outputs/ml_models', verbose=True):
        """
        Initialize evaluator.

        Args:
            output_dir (str): Directory to save outputs
            verbose (bool): Print progress
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

    def compare_models(self, models_dict, X_test, y_test):
        """
        Compare multiple ML models.

        Args:
            models_dict (dict): {name: trained_model, ...}
            X_test (pd.DataFrame): Test features
            y_test (pd.Series): Test target

        Returns:
            pd.DataFrame: Comparison table
        """
        results = []

        for name, model in models_dict.items():
            y_pred = model.predict(X_test)

            rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
            mae = np.mean(np.abs(y_test - y_pred))
            r2 = model.model.score(X_test, y_test)
            correlation = np.corrcoef(y_test, y_pred)[0, 1]

            results.append({
                'Model': name,
                'RMSE': rmse,
                'MAE': mae,
                'R²': r2,
                'Correlation': correlation,
            })

        comparison_df = pd.DataFrame(results)

        if self.verbose:
            print("\n[✓] Model Comparison:")
            print(comparison_df.to_string(index=False))

        return comparison_df

    def compare_to_ols(self, ml_r2, ols_r2, model_names):
        """
        Compare ML model fit to OLS model fit.

        Args:
            ml_r2 (dict): {model_name: r2_value, ...}
            ols_r2 (float): OLS model R²
            model_names (list): Names of ML models

        Returns:
            pd.DataFrame: Comparison table
        """
        comparison = []

        # OLS baseline
        comparison.append({
            'Methodology': 'OLS (Baseline)',
            'R²': ols_r2,
            'Improvement': '—',
            'Improvement %': '—',
        })

        # ML models
        for model_name, r2 in ml_r2.items():
            improvement = r2 - ols_r2
            improvement_pct = (improvement / ols_r2 * 100) if ols_r2 != 0 else 0

            comparison.append({
                'Methodology': f'{model_name}',
                'R²': r2,
                'Improvement': f'{improvement:+.4f}',
                'Improvement %': f'{improvement_pct:+.1f}%',
            })

        comparison_df = pd.DataFrame(comparison)

        if self.verbose:
            print("\n[✓] OLS vs ML Comparison:")
            print(comparison_df.to_string(index=False))

        return comparison_df

    def plot_predictions_vs_actual(self, y_actual, y_pred, model_name, target_name='CAR'):
        """
        Plot actual vs predicted values.

        Args:
            y_actual (pd.Series or np.array): Actual target values
            y_pred (np.array): Model predictions
            model_name (str): Name of model
            target_name (str): Name of target variable

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Scatter plot
        axes[0].scatter(y_actual, y_pred, alpha=0.5, edgecolors='k', linewidth=0.5)
        axes[0].plot([y_actual.min(), y_actual.max()],
                     [y_actual.min(), y_actual.max()], 'r--', lw=2)
        axes[0].set_xlabel(f'Actual {target_name}', fontsize=11)
        axes[0].set_ylabel(f'Predicted {target_name}', fontsize=11)
        axes[0].set_title(f'{model_name}: Actual vs Predicted', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # Residuals
        residuals = y_actual - y_pred
        axes[1].scatter(y_pred, residuals, alpha=0.5, edgecolors='k', linewidth=0.5)
        axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel(f'Predicted {target_name}', fontsize=11)
        axes[1].set_ylabel('Residuals', fontsize=11)
        axes[1].set_title(f'{model_name}: Residual Plot', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        fig_path = self.output_dir / f'pred_vs_actual_{model_name.lower().replace(" ", "_")}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def plot_model_comparison(self, comparison_df, metric='R²'):
        """
        Plot model comparison bar chart.

        Args:
            comparison_df (pd.DataFrame): Comparison table from compare_to_ols()
            metric (str): Metric to plot ('R²', 'RMSE', etc.)

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        fig, ax = plt.subplots(figsize=(10, 5))

        colors = ['#1f77b4' if 'OLS' in row else '#2ca02c' for row in comparison_df['Methodology']]

        ax.bar(comparison_df['Methodology'], comparison_df[metric], color=colors,
               edgecolor='black', linewidth=1.5, alpha=0.8)
        ax.set_ylabel(metric, fontsize=12, fontweight='bold')
        ax.set_title(f'Model Comparison: {metric}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for i, (model, val) in enumerate(zip(comparison_df['Methodology'], comparison_df[metric])):
            ax.text(i, val + 0.01, f'{val:.4f}', ha='center', va='bottom', fontweight='bold')

        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()

        # Save
        fig_path = self.output_dir / f'model_comparison_{metric.lower()}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def plot_heterogeneous_effects(self, df, treatment_col, outcome_col, group_col,
                                   model=None, model_name='ML Model'):
        """
        Plot heterogeneous treatment effects by subgroup.

        Args:
            df (pd.DataFrame): Data with treatment, outcome, group
            treatment_col (str): Treatment column name
            outcome_col (str): Outcome column name
            group_col (str): Grouping variable
            model (optional): Trained model for predictions
            model_name (str): Name of model for plotting

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        # Plot 1: Mean outcomes by group and treatment
        group_treatment = df.groupby([group_col, treatment_col])[outcome_col].agg(['mean', 'count'])

        if len(df[group_col].unique()) <= 5:  # Only if reasonable number of groups
            for group in df[group_col].unique():
                group_data = df[df[group_col] == group]
                treated = group_data[group_data[treatment_col] == 1][outcome_col].mean()
                control = group_data[group_data[treatment_col] == 0][outcome_col].mean()
                effect = treated - control

                axes[0].scatter([0, 1], [control, treated], s=100, label=f'{group}', alpha=0.7)
                axes[0].plot([0, 1], [control, treated], '--', alpha=0.5)

            axes[0].set_xticks([0, 1])
            axes[0].set_xticklabels(['Control (Delayed)', 'Treatment (Immediate)'])
            axes[0].set_ylabel(outcome_col, fontsize=11)
            axes[0].set_title(f'Heterogeneous Effects by {group_col}', fontsize=12, fontweight='bold')
            axes[0].legend(loc='best', fontsize=9)
            axes[0].grid(True, alpha=0.3)

        # Plot 2: Effect size by group
        effects = []
        groups = []
        for group in sorted(df[group_col].unique()):
            group_data = df[df[group_col] == group]
            treated = group_data[group_data[treatment_col] == 1][outcome_col].mean()
            control = group_data[group_data[treatment_col] == 0][outcome_col].mean()
            effect = treated - control
            effects.append(effect)
            groups.append(group)

        colors_effects = ['#d62728' if e < 0 else '#2ca02c' for e in effects]
        axes[1].barh(groups, effects, color=colors_effects, edgecolor='black', linewidth=1.5, alpha=0.8)
        axes[1].axvline(x=0, color='black', linestyle='-', linewidth=1)
        axes[1].set_xlabel(f'Treatment Effect ({treatment_col})', fontsize=11)
        axes[1].set_title(f'Effect Sizes by {group_col}', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        # Save
        fig_path = self.output_dir / f'heterogeneous_effects_{group_col.lower()}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def save_comparison_table(self, comparison_df, filename='model_comparison.csv'):
        """Save comparison table to CSV."""
        output_path = self.output_dir / filename
        comparison_df.to_csv(output_path, index=False)
        if self.verbose:
            print(f"[✓] Saved {output_path.name}")
        return output_path
