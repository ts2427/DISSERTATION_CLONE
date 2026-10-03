"""
Feature Importance Analysis

Analyzes and compares feature importance across models and with OLS coefficients.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class FeatureImportanceAnalyzer:
    """Analyze and compare feature importance across models."""

    def __init__(self, output_dir='outputs/ml_models', verbose=True):
        """
        Initialize analyzer.

        Args:
            output_dir (str): Directory to save outputs
            verbose (bool): Print progress
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

    def get_feature_importance_ranking(self, models_dict, top_n=15):
        """
        Get feature importance ranking from multiple models.

        Args:
            models_dict (dict): {model_name: trained_model, ...}
            top_n (int): Number of top features to extract

        Returns:
            dict: {model_name: importance_df, ...}
        """
        rankings = {}

        for name, model in models_dict.items():
            importance_df = model.get_feature_importance()
            rankings[name] = importance_df.head(top_n)

            if self.verbose:
                print(f"\n[✓] Top {top_n} Features - {name}:")
                for idx, row in importance_df.head(top_n).iterrows():
                    print(f"    {row['feature']:<25} {row['importance_pct']:>6.2f}%")

        return rankings

    def compare_ols_vs_ml(self, ols_coefficients, ml_rankings, model_name='Random Forest'):
        """
        Compare OLS coefficients to ML feature importance.

        Args:
            ols_coefficients (pd.DataFrame): OLS results with columns [feature, coefficient, pvalue, ...]
            ml_rankings (dict): Feature importance rankings from ML models
            model_name (str): Which ML model to compare against

        Returns:
            pd.DataFrame: Comparison table
        """
        ml_importance = ml_rankings.get(model_name)
        if ml_importance is None:
            raise ValueError(f"Model '{model_name}' not found in rankings")

        # Merge OLS and ML
        comparison = ols_coefficients[['feature', 'coefficient', 'pvalue']].copy()
        comparison = comparison.merge(
            ml_importance[['feature', 'importance_pct']],
            on='feature',
            how='left'
        )

        # Rank by importance
        comparison['ols_abs_coef'] = abs(comparison['coefficient'])
        comparison['ols_rank'] = comparison['ols_abs_coef'].rank(ascending=False)
        comparison['ml_rank'] = comparison['importance_pct'].rank(ascending=False)
        comparison['rank_difference'] = comparison['ols_rank'] - comparison['ml_rank']

        comparison = comparison.sort_values('importance_pct', ascending=False)

        if self.verbose:
            print(f"\n[✓] OLS vs {model_name} Comparison:")
            print(comparison[['feature', 'coefficient', 'pvalue', 'importance_pct', 'rank_difference']].to_string(index=False))

        return comparison

    def plot_feature_importance(self, importance_df, model_name, top_n=15, figsize=(10, 6)):
        """
        Plot feature importance bar chart.

        Args:
            importance_df (pd.DataFrame): Feature importance from get_feature_importance()
            model_name (str): Name of model
            top_n (int): Number of top features to plot
            figsize (tuple): Figure size

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        top_features = importance_df.head(top_n)

        fig, ax = plt.subplots(figsize=figsize)

        colors = plt.cm.viridis(np.linspace(0, 1, len(top_features)))

        ax.barh(range(len(top_features)), top_features['importance_pct'].values,
               color=colors, edgecolor='black', linewidth=1.2, alpha=0.9)

        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'].values, fontsize=10)
        ax.set_xlabel('Importance (%)', fontsize=11, fontweight='bold')
        ax.set_title(f'Top {top_n} Feature Importance - {model_name}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, val in enumerate(top_features['importance_pct'].values):
            ax.text(val + 0.2, i, f'{val:.1f}%', va='center', fontweight='bold', fontsize=9)

        plt.tight_layout()

        # Save
        fig_path = self.output_dir / f'feature_importance_{model_name.lower().replace(" ", "_")}.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def plot_ols_vs_ml_importance(self, comparison_df, top_n=12):
        """
        Plot OLS coefficients vs ML importance side-by-side.

        Args:
            comparison_df (pd.DataFrame): Output from compare_ols_vs_ml()
            top_n (int): Number of top features

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        top_features = comparison_df.head(top_n).copy()

        # Normalize for comparison
        top_features['ols_norm'] = (top_features['ols_abs_coef'] / top_features['ols_abs_coef'].max()) * 100
        top_features['ml_norm'] = top_features['importance_pct']

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(top_features))
        width = 0.35

        bars1 = ax.bar(x - width/2, top_features['ols_norm'], width, label='OLS (Normalized)',
                      color='#1f77b4', edgecolor='black', linewidth=1.2, alpha=0.8)
        bars2 = ax.bar(x + width/2, top_features['ml_norm'], width, label='ML (Random Forest)',
                      color='#ff7f0e', edgecolor='black', linewidth=1.2, alpha=0.8)

        ax.set_xlabel('Features', fontsize=11, fontweight='bold')
        ax.set_ylabel('Importance (Normalized to 100%)', fontsize=11, fontweight='bold')
        ax.set_title(f'OLS Coefficients vs ML Importance (Top {top_n} Features)', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(top_features['feature'], rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        # Save
        fig_path = self.output_dir / 'ols_vs_ml_importance_comparison.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def plot_coefficient_vs_importance(self, comparison_df, top_n=12):
        """
        Scatter plot: OLS coefficients vs ML importance.

        Args:
            comparison_df (pd.DataFrame): Output from compare_ols_vs_ml()
            top_n (int): Number of top features to highlight

        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot all features
        scatter = ax.scatter(comparison_df['ols_abs_coef'], comparison_df['importance_pct'],
                            s=100, alpha=0.6, c=range(len(comparison_df)), cmap='viridis',
                            edgecolors='black', linewidth=0.5)

        # Annotate top features
        top_features = comparison_df.head(top_n)
        for idx, row in top_features.iterrows():
            ax.annotate(row['feature'], (row['ols_abs_coef'], row['importance_pct']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=0.5))

        ax.set_xlabel('OLS |Coefficient|', fontsize=11, fontweight='bold')
        ax.set_ylabel('ML Importance (%)', fontsize=11, fontweight='bold')
        ax.set_title('OLS Coefficients vs ML Feature Importance', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        fig_path = self.output_dir / 'coefficient_vs_importance_scatter.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        if self.verbose:
            print(f"[✓] Saved {fig_path.name}")

        return fig

    def save_comparison_table(self, comparison_df, filename='ols_vs_ml_comparison.csv'):
        """Save comparison table to CSV."""
        output_path = self.output_dir / filename
        comparison_df.to_csv(output_path, index=False)
        if self.verbose:
            print(f"[✓] Saved {output_path.name}")
        return output_path

    def identify_discrepancies(self, comparison_df, threshold_rank_diff=5):
        """
        Identify features where OLS and ML importance disagree significantly.

        Args:
            comparison_df (pd.DataFrame): Output from compare_ols_vs_ml()
            threshold_rank_diff (int): Minimum rank difference to flag

        Returns:
            pd.DataFrame: Discrepancies
        """
        discrepancies = comparison_df[
            (abs(comparison_df['rank_difference']) >= threshold_rank_diff) &
            (comparison_df['importance_pct'].notna())
        ][['feature', 'coefficient', 'pvalue', 'importance_pct', 'ols_rank', 'ml_rank', 'rank_difference']]

        if self.verbose and len(discrepancies) > 0:
            print(f"\n[!] Potential Discrepancies (|rank_diff| >= {threshold_rank_diff}):")
            print(discrepancies.to_string(index=False))

        return discrepancies
