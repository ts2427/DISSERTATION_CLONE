"""
SYNTHETIC CONTROL METHOD - PRODUCTION PIPELINE
===============================================

Complete pipeline for computing synthetic control analysis in Python.
Uses V and W weights from R's synth() package for exact numerical matching.

USAGE:
------
1. Run synth() in R to get optimal V and W weights
2. Export them: write.csv(as.data.frame(V), "v_weights.csv"); write.csv(as.data.frame(W), "w_weights.csv")
3. Run this script: python synth_pipeline.py

CUSTOMIZATION:
--------------
Edit the CONFIG section below for your specific analysis:
- data_file: Path to your CSV data file
- v_weights_file: Path to R's V weights CSV
- w_weights_file: Path to R's W weights CSV
- treatment_id: Treatment unit identifier
- control_ids: List of control unit identifiers
- time_plot: Years/periods for gap analysis
- output_prefix: Prefix for output files
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys


# ============================================================================
# CONFIGURATION - EDIT THIS SECTION FOR YOUR DATA
# ============================================================================

class Config:
    """Configuration for synthetic control analysis"""

    # Data files
    data_file = 'basque_data.csv'
    v_weights_file = 'v_weights.csv'
    w_weights_file = 'w_weights.csv'

    # Treatment and control units
    treatment_id = 17  # Basque region ID
    control_ids = list(range(2, 17)) + [18]  # All regions except Basque

    # Time periods
    time_plot = list(range(1955, 1998))  # Years for gap analysis (1955-1997)

    # Output files
    output_prefix = 'python_scm'  # Prefix for output files (gaps, plots, etc.)
    output_dir = Path('.')

    # Treatment onset year (for visualization)
    treatment_year = 1970

    # Plot settings
    plot_dpi = 150
    plot_figsize = (12, 6)


# ============================================================================
# SYNTHETIC CONTROL COMPUTATION
# ============================================================================

class SyntheticControl:
    """Compute synthetic control gaps given V and W weights"""

    def __init__(self, data_csv, v_weights_csv, w_weights_csv,
                 treatment_id, control_ids, time_plot):
        """
        Initialize synthetic control analysis.

        Parameters:
        -----------
        data_csv : str
            Path to data CSV file
        v_weights_csv : str
            Path to V weights from R (can be single column or multiple)
        w_weights_csv : str
            Path to W weights from R (can be single column or multiple)
        treatment_id : int or str
            ID of treatment unit
        control_ids : list
            IDs of control units
        time_plot : list
            Time periods for analysis
        """
        self.data = pd.read_csv(data_csv)
        self.treatment_id = treatment_id
        self.control_ids = sorted(control_ids)
        self.time_plot = time_plot

        # Load V weights (handle various CSV formats)
        v_df = pd.read_csv(v_weights_csv, index_col=0)
        if v_df.shape[0] == 1:  # Single row (from R output)
            self.V = v_df.iloc[0].values
        else:  # Single column (from R output)
            self.V = v_df.iloc[:, 0].values

        # Load W weights (handle various CSV formats)
        w_df = pd.read_csv(w_weights_csv, index_col=0)
        if w_df.shape[0] == 1:  # Single row
            self.W = w_df.iloc[0].values
        else:  # Single column
            self.W = w_df.iloc[:, 0].values

        print(f"Loaded V weights: shape {self.V.shape}")
        print(f"Loaded W weights: shape {self.W.shape}")
        print(f"V sum: {self.V.sum():.6f} (should be ~1.0)")
        print(f"W sum: {self.W.sum():.6f} (should be ~1.0)")

        self._extract_outcome_data()

    def _extract_outcome_data(self):
        """Extract treated and control outcome data for time_plot period"""
        treated = self.data[self.data['firm_id'] == self.treatment_id].copy()
        controls = self.data[self.data['firm_id'].isin(self.control_ids)].copy()

        # Extract outcome (assuming column is 'car_mean' - modify if needed)
        outcome_col = 'car_mean'
        if outcome_col not in self.data.columns:
            raise ValueError(f"Column '{outcome_col}' not found in data. Available: {list(self.data.columns)}")

        # Treated unit outcomes for time_plot
        self.Y1 = treated[treated['year'].isin(self.time_plot)].sort_values('year')[outcome_col].values

        # Control unit outcomes for time_plot
        Y0_list = []
        for control_id in self.control_ids:
            ctrl_subset = controls[controls['firm_id'] == control_id]
            y_vals = ctrl_subset[ctrl_subset['year'].isin(self.time_plot)].sort_values('year')[outcome_col].values
            Y0_list.append(y_vals)
        self.Y0 = np.array(Y0_list).T  # Shape: (n_years, n_controls)

        print(f"Outcome data shapes:")
        print(f"  Y1 (treated): {self.Y1.shape}")
        print(f"  Y0 (controls): {self.Y0.shape}")

    def compute_gaps(self):
        """Compute treatment effect gaps (Y - synthetic)"""
        synthetic = self.Y0 @ self.W
        gaps = self.Y1 - synthetic

        results_df = pd.DataFrame({
            'year': self.time_plot,
            'gap': gaps,
            'treated': self.Y1,
            'synthetic': synthetic
        })

        return results_df

    def compute_loss(self):
        """Compute prediction loss metric"""
        synthetic = self.Y0 @ self.W
        loss = np.sum((self.Y1 - synthetic) ** 2)

        return {
            'z_loss': loss,
            'mse': loss / len(self.Y1),
            'rmse': np.sqrt(loss / len(self.Y1))
        }

    def plot_gaps(self, figsize=None, treatment_year=None, title=None):
        """Plot treatment effect gaps over time"""
        if figsize is None:
            figsize = Config.plot_figsize
        if treatment_year is None:
            treatment_year = Config.treatment_year
        if title is None:
            title = "Treatment Effect Over Time"

        gaps_df = self.compute_gaps()

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(gaps_df['year'], gaps_df['gap'], 'b-', linewidth=2.5, label='Treatment effect')
        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axvline(x=treatment_year, color='r', linestyle='--', linewidth=1.5, alpha=0.6,
                   label=f'Treatment onset ({treatment_year})')

        ax.fill_between(gaps_df['year'], 0, gaps_df['gap'],
                        where=(gaps_df['gap'] >= 0), alpha=0.3, color='blue', label='Positive effect')
        ax.fill_between(gaps_df['year'], 0, gaps_df['gap'],
                        where=(gaps_df['gap'] < 0), alpha=0.3, color='red', label='Negative effect')

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Gap (Treated - Synthetic)', fontsize=12)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig

    def plot_trajectories(self, figsize=None, treatment_year=None, title=None):
        """Plot treated vs synthetic control trajectories"""
        if figsize is None:
            figsize = Config.plot_figsize
        if treatment_year is None:
            treatment_year = Config.treatment_year
        if title is None:
            title = "Treated Unit vs Synthetic Control"

        gaps_df = self.compute_gaps()

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(gaps_df['year'], gaps_df['treated'], 'b-', linewidth=2.5, marker='o',
                markersize=3, label='Treated unit')
        ax.plot(gaps_df['year'], gaps_df['synthetic'], 'r--', linewidth=2.5, marker='s',
                markersize=3, label='Synthetic control')
        ax.axvline(x=treatment_year, color='gray', linestyle='--', linewidth=1.2, alpha=0.5)
        ax.text(treatment_year + 0.5, ax.get_ylim()[1] * 0.95, 'Treatment',
                fontsize=10, alpha=0.7)

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Outcome Value', fontsize=12)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete synthetic control analysis"""

    print("\n" + "="*70)
    print("SYNTHETIC CONTROL METHOD - PYTHON PIPELINE")
    print("="*70)

    # Initialize
    print("\n[1/5] Loading data and weights...")
    try:
        scm = SyntheticControl(
            data_csv=str(Config.data_file),
            v_weights_csv=str(Config.v_weights_file),
            w_weights_csv=str(Config.w_weights_file),
            treatment_id=Config.treatment_id,
            control_ids=Config.control_ids,
            time_plot=Config.time_plot
        )
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print(f"Make sure these files exist:")
        print(f"  - {Config.data_file}")
        print(f"  - {Config.v_weights_file}")
        print(f"  - {Config.w_weights_file}")
        return 1

    # Compute gaps
    print("\n[2/5] Computing treatment effect gaps...")
    gaps_df = scm.compute_gaps()
    gaps_file = Config.output_dir / f"{Config.output_prefix}_gaps.csv"
    gaps_df.to_csv(gaps_file, index=False)
    print(f"Saved gaps to: {gaps_file}")
    print(f"\nFirst 10 years of gaps:")
    print(gaps_df.head(10).to_string(index=False))

    # Compute losses
    print("\n[3/5] Computing loss metrics...")
    losses = scm.compute_loss()
    print(f"Z loss (total squared error): {losses['z_loss']:.8f}")
    print(f"MSE: {losses['mse']:.8f}")
    print(f"RMSE: {losses['rmse']:.8f}")

    # Save losses
    losses_file = Config.output_dir / f"{Config.output_prefix}_losses.csv"
    pd.DataFrame([losses]).to_csv(losses_file, index=False)
    print(f"Saved losses to: {losses_file}")

    # Create plots
    print("\n[4/5] Creating visualization plots...")

    fig_gaps = scm.plot_gaps(
        treatment_year=Config.treatment_year,
        title=f"Treatment Effect Over Time"
    )
    gaps_plot_file = Config.output_dir / f"{Config.output_prefix}_gaps_plot.png"
    fig_gaps.savefig(gaps_plot_file, dpi=Config.plot_dpi, bbox_inches='tight')
    print(f"Saved gaps plot to: {gaps_plot_file}")

    fig_traj = scm.plot_trajectories(
        treatment_year=Config.treatment_year,
        title=f"Treated Unit vs Synthetic Control"
    )
    traj_plot_file = Config.output_dir / f"{Config.output_prefix}_trajectories_plot.png"
    fig_traj.savefig(traj_plot_file, dpi=Config.plot_dpi, bbox_inches='tight')
    print(f"Saved trajectories plot to: {traj_plot_file}")

    # Summary statistics
    print("\n[5/5] Generating summary statistics...")
    summary = {
        'Metric': ['Mean gap (all years)', 'Mean gap (pre-treatment)', 'Mean gap (post-treatment)',
                  'Std dev gap (all)', 'Min gap', 'Max gap'],
        'Value': [
            gaps_df['gap'].mean(),
            gaps_df[gaps_df['year'] < Config.treatment_year]['gap'].mean(),
            gaps_df[gaps_df['year'] >= Config.treatment_year]['gap'].mean(),
            gaps_df['gap'].std(),
            gaps_df['gap'].min(),
            gaps_df['gap'].max()
        ]
    }
    summary_df = pd.DataFrame(summary)
    summary_file = Config.output_dir / f"{Config.output_prefix}_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"\nSummary statistics:")
    print(summary_df.to_string(index=False))
    print(f"Saved summary to: {summary_file}")

    # Final message
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput files created in: {Config.output_dir}")
    print(f"  - {Config.output_prefix}_gaps.csv (treatment effect gaps)")
    print(f"  - {Config.output_prefix}_losses.csv (loss metrics)")
    print(f"  - {Config.output_prefix}_summary.csv (summary statistics)")
    print(f"  - {Config.output_prefix}_gaps_plot.png (gaps visualization)")
    print(f"  - {Config.output_prefix}_trajectories_plot.png (trajectories visualization)")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
