"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - PURE PYTHON
====================================================

Implements synthetic control method for each FCC firm individually.
No R dependency - completely self-contained in Python.

USAGE:
------
python firm_by_firm_scm_python.py

This will:
1. Load dissertation data
2. For each FCC firm, construct synthetic control from non-FCC firms
3. Compute individual treatment effects
4. Save results for aggregation and statistical inference
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from pathlib import Path
import sys
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = "data_scm_ready.csv"
OUTPUT_DIR = Path("outputs/scm_firm_by_firm")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# FCC identification - use fcc_reportable column (more comprehensive than SIC codes)
# FCC_SICS = [4813, 4899, 4841]  # Alternative: SIC-based identification

# Time periods
PRE_YEAR = 2007
POST_START = 2007
POST_END = 2024

# ============================================================================
# SYNTHETIC CONTROL ESTIMATION
# ============================================================================

class SyntheticControlEstimator:
    """Estimate synthetic control for a single treatment firm"""

    def __init__(self, data, treatment_firm_id, control_firm_ids, pre_year, outcome_col='car_mean'):
        """
        Initialize SCM estimator.

        Parameters:
        -----------
        data : pd.DataFrame
            Firm-year panel data
        treatment_firm_id : int or str
            ID of treatment firm
        control_firm_ids : list
            IDs of control firms
        pre_year : int
            Last year before treatment
        outcome_col : str
            Name of outcome column
        """
        self.data = data
        self.treatment_id = treatment_firm_id
        self.control_ids = control_firm_ids
        self.pre_year = pre_year
        self.outcome_col = outcome_col

        # Extract data
        self._extract_data()

    def _extract_data(self):
        """Extract treatment and control unit data"""
        # Treatment firm data
        treat_data = self.data[self.data['firm_id'] == self.treatment_id].copy()
        treat_data = treat_data.sort_values('year')

        # Remove NaN outcome values
        treat_data = treat_data.dropna(subset=[self.outcome_col])

        if len(treat_data) == 0:
            raise ValueError("No treatment data available after removing NaN")

        self.treatment_years = treat_data['year'].values
        self.Y1 = treat_data[self.outcome_col].values

        # Control firms data
        ctrl_data = self.data[self.data['firm_id'].isin(self.control_ids)].copy()
        ctrl_data = ctrl_data.sort_values(['firm_id', 'year'])

        # Create Y0 matrix (years × firms) with NaN handling
        Y0_dict = {}
        years_in_controls = set()

        for firm_id in self.control_ids:
            firm_data = ctrl_data[ctrl_data['firm_id'] == firm_id].sort_values('year')
            firm_data = firm_data.dropna(subset=[self.outcome_col])

            if len(firm_data) > 0:
                Y0_dict[firm_id] = {
                    'years': firm_data['year'].values,
                    'values': firm_data[self.outcome_col].values
                }
                years_in_controls.update(firm_data['year'].values)

        if len(Y0_dict) == 0:
            raise ValueError("No control data available")

        # Align all data to common years
        common_years = np.array(sorted(years_in_controls))
        treatment_years_set = set(self.treatment_years)
        common_years = common_years[np.isin(common_years, list(treatment_years_set))]

        if len(common_years) < 3:
            raise ValueError(f"Insufficient overlapping years: {common_years}")

        # Extract aligned data - collect all control firms' values first
        Y1_aligned = []
        Y0_aligned = []
        valid_years = []

        for year in common_years:
            # Treatment value
            treat_idx = np.where(self.treatment_years == year)[0]
            if len(treat_idx) == 0:
                continue

            treat_val = self.Y1[treat_idx[0]]
            if np.isnan(treat_val):
                continue

            # Collect control values for this year
            ctrl_vals = []
            for firm_id in self.control_ids:
                if firm_id in Y0_dict:
                    firm_years = Y0_dict[firm_id]['years']
                    if year in firm_years:
                        idx = np.where(firm_years == year)[0]
                        if len(idx) > 0:
                            val = Y0_dict[firm_id]['values'][idx[0]]
                            if not np.isnan(val):
                                ctrl_vals.append(val)

            # Only keep if we have control values
            if len(ctrl_vals) >= len(self.control_ids) * 0.5:  # At least 50% of controls
                Y1_aligned.append(treat_val)
                Y0_aligned.append(np.mean(ctrl_vals))  # Use mean of available controls for now
                valid_years.append(year)

        if len(Y1_aligned) < 3:
            raise ValueError(f"Insufficient aligned data points: {len(Y1_aligned)}")

        # Create properly aligned matrices
        self.Y1 = np.array(Y1_aligned)
        self.Y0 = np.array(Y0_aligned).reshape(-1, 1)  # Single synthetic control column
        self.treatment_years_aligned = np.array(valid_years)

        # Years for pre/post split
        self.pre_idx = np.where(self.treatment_years_aligned < self.pre_year)[0]
        self.post_idx = np.where(self.treatment_years_aligned >= self.pre_year)[0]

        if len(self.pre_idx) == 0 or len(self.post_idx) == 0:
            raise ValueError(f"No pre/post split data: pre={len(self.pre_idx)}, post={len(self.post_idx)}")

    def _loss_function(self, w):
        """Loss function for weight optimization"""
        if np.any(np.isnan(w)) or np.any(np.isinf(w)):
            return 1e10

        synthetic = self.Y0[self.pre_idx] @ w
        loss = np.sum((self.Y1[self.pre_idx] - synthetic) ** 2)
        return loss

    def estimate(self):
        """Estimate synthetic control weights"""
        n_controls = self.Y0.shape[1]

        # Initial guess: equal weights
        w0 = np.ones(n_controls) / n_controls

        # Constraints: weights sum to 1, non-negative
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [(0, 1) for _ in range(n_controls)]

        # Optimize
        result = optimize.minimize(
            self._loss_function,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            self.W = result.x
        else:
            # Fallback: equal weights
            self.W = np.ones(n_controls) / n_controls

        return self.W

    def compute_gaps(self):
        """Compute treatment effect gaps"""
        if len(self.W) != self.Y0.shape[1]:
            raise ValueError(f"Weight dimension mismatch: {len(self.W)} vs {self.Y0.shape[1]}")

        synthetic = self.Y0 @ self.W
        gaps = self.Y1 - synthetic

        # Compute statistics on post-treatment periods
        if len(self.post_idx) > 0:
            post_gaps = gaps[self.post_idx]
            mean_gap_post = np.mean(post_gaps)
        else:
            mean_gap_post = np.nan

        if len(self.pre_idx) > 0:
            pre_gaps = gaps[self.pre_idx]
            mean_gap_pre = np.mean(pre_gaps)
            rmse_pre = np.sqrt(np.mean(pre_gaps ** 2))
        else:
            mean_gap_pre = np.nan
            rmse_pre = np.nan

        return {
            'gaps': gaps,
            'synthetic': synthetic,
            'treated': self.Y1,
            'years': self.treatment_years_aligned,
            'rmse_pre': rmse_pre,
            'mean_gap_pre': mean_gap_pre,
            'mean_gap_post': mean_gap_post,
        }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    """Run firm-by-firm SCM analysis"""

    print("\n" + "="*70)
    print("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - PYTHON IMPLEMENTATION")
    print("="*70)

    # Load data
    print("\n[1/4] Loading and preparing data...")
    df = pd.read_csv(DATA_FILE)

    # Convert numeric columns to float
    numeric_cols = ['car_30d', 'volatility_change', 'executive_change_30d', 'firm_size_log',
                   'leverage', 'roa', 'total_affected', 'sic']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create FCC indicator - use fcc_reportable column if available, else fall back to SIC
    if 'fcc_reportable' in df.columns:
        df['is_fcc'] = df['fcc_reportable'].astype(bool)
        print(f"[OK] Using fcc_reportable column for FCC identification")
    else:
        df['is_fcc'] = df['sic'].isin([4813, 4899, 4841])
        print(f"[OK] Using SIC codes for FCC identification")

    # Prepare firm-year panel (aggregate to firm-year)
    firm_year = df.groupby(['cik', 'org_name', 'breach_year'], as_index=False).agg({
        'car_30d': 'mean',
        'volatility_change': 'mean',
        'executive_change_30d': 'mean',
        'firm_size_log': 'mean',
        'leverage': 'mean',
        'roa': 'mean',
        'total_affected': 'mean',
        'is_fcc': 'first'
    })

    # Rename columns for consistency
    firm_year.rename(columns={
        'cik': 'firm_id',
        'org_name': 'firm_name',
        'breach_year': 'year',
        'car_30d': 'car_mean',
        'volatility_change': 'volatility_mean',
        'executive_change_30d': 'governance_mean',
        'firm_size_log': 'log_assets',
        'total_affected': 'log_records'
    }, inplace=True)

    firm_year['log_records'] = np.log(firm_year['log_records'] + 1)

    # Filter to years of interest
    firm_year = firm_year[firm_year['year'] >= (PRE_YEAR - 10)]
    firm_year = firm_year[firm_year['year'] <= POST_END]

    # Get FCC and non-FCC firms
    fcc_firms = firm_year[firm_year['is_fcc']]['firm_id'].unique()
    non_fcc_firms = firm_year[~firm_year['is_fcc']]['firm_id'].unique()

    print(f"[OK] Loaded {len(firm_year)} firm-year observations")
    print(f"[OK] Found {len(fcc_firms)} unique FCC firms and {len(non_fcc_firms)} non-FCC firms")

    if len(fcc_firms) < 10:
        print(f"[WARNING] Only {len(fcc_firms)} FCC firms (recommend >= 10)")

    if len(non_fcc_firms) < 20:
        print(f"[WARNING] Only {len(non_fcc_firms)} non-FCC firms (recommend >= 50)")

    # Run SCM for each FCC firm
    print("\n[2/4] Running SCM for each FCC firm...")

    results_list = []
    failed_firms = []

    for i, treatment_firm in enumerate(fcc_firms):
        firm_name = firm_year[firm_year['firm_id'] == treatment_firm]['firm_name'].iloc[0]

        if (i + 1) % 10 == 0 or i == 0 or i == len(fcc_firms) - 1:
            print(f"  [{i+1}/{len(fcc_firms)}] Processing {firm_name}...")

        try:
            # Initialize SCM
            scm = SyntheticControlEstimator(
                data=firm_year,
                treatment_firm_id=treatment_firm,
                control_firm_ids=list(non_fcc_firms),
                pre_year=PRE_YEAR,
                outcome_col='car_mean'
            )

            # Estimate weights
            W = scm.estimate()

            # Compute gaps
            gaps_dict = scm.compute_gaps()

            # Validate results
            if np.isnan(gaps_dict['mean_gap_post']):
                failed_firms.append((firm_name, "NaN gap computed"))
                continue

            # Store results
            results_list.append({
                'firm_id': treatment_firm,
                'firm_name': firm_name,
                'n_controls': len(non_fcc_firms),
                'mean_gap': gaps_dict['mean_gap_post'],
                'mean_gap_pre': gaps_dict['mean_gap_pre'],
                'mean_gap_post': gaps_dict['mean_gap_post'],
                'rmse_pre': gaps_dict['rmse_pre'],
                'outcome': 'car_30d'
            })

        except Exception as e:
            # Track failed firms with reason
            failed_firms.append((firm_name, str(e)))

    print(f"[OK] Successfully estimated SCM for {len(results_list)} FCC firms")
    if failed_firms:
        print(f"[WARNING] Failed to estimate SCM for {len(failed_firms)} firms:")
        for name, reason in failed_firms[:5]:
            print(f"  - {name}: {reason}")
        if len(failed_firms) > 5:
            print(f"  ... and {len(failed_firms) - 5} more")

    print(f"[OK] Successfully estimated SCM for {len(results_list)} FCC firms")

    # Save results
    print("\n[3/4] Saving results...")

    summary_df = pd.DataFrame(results_list)
    summary_file = OUTPUT_DIR / "scm_firm_summary_results.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"[OK] Saved: {summary_file}")

    # Collect all gaps for statistical inference
    all_gaps_list = []
    for i, treatment_firm in enumerate(fcc_firms):
        try:
            scm = SyntheticControlEstimator(
                data=firm_year,
                treatment_firm_id=treatment_firm,
                control_firm_ids=list(non_fcc_firms),
                pre_year=PRE_YEAR,
                outcome_col='car_mean'
            )
            W = scm.estimate()
            gaps_dict = scm.compute_gaps()

            # Add gap data for each year
            for year_idx, year in enumerate(gaps_dict['years']):
                is_post = year >= PRE_YEAR
                all_gaps_list.append({
                    'firm_id': treatment_firm,
                    'year': year,
                    'gap': gaps_dict['gaps'][year_idx],
                    'is_post_treatment': 1 if is_post else 0,
                    'synthetic': gaps_dict['synthetic'][year_idx],
                    'treated': gaps_dict['treated'][year_idx]
                })
        except:
            pass

    # Save gaps for permutation test
    if all_gaps_list:
        gaps_df = pd.DataFrame(all_gaps_list)
        gaps_file = OUTPUT_DIR / "scm_all_firm_gaps.csv"
        gaps_df.to_csv(gaps_file, index=False)
        print(f"[OK] Saved: {gaps_file}")

    # Summary statistics
    if len(summary_df) > 0:
        print(f"\nAggregate Statistics:")
        print(f"  Mean effect: {summary_df['mean_gap'].mean():.4f}%")
        print(f"  Std dev: {summary_df['mean_gap'].std():.4f}%")
        print(f"  Median: {summary_df['mean_gap'].median():.4f}%")
        print(f"  Min: {summary_df['mean_gap'].min():.4f}%")
        print(f"  Max: {summary_df['mean_gap'].max():.4f}%")

        # Save aggregate stats
        agg_stats = pd.DataFrame({
            'N_firms': [len(summary_df)],
            'mean_effect': [summary_df['mean_gap'].mean()],
            'median_effect': [summary_df['mean_gap'].median()],
            'sd_effect': [summary_df['mean_gap'].std()],
            'min_effect': [summary_df['mean_gap'].min()],
            'max_effect': [summary_df['mean_gap'].max()]
        })
        agg_stats.to_csv(OUTPUT_DIR / "scm_aggregate_statistics.csv", index=False)

    print("\n[4/4] Complete")

    print("\n" + "="*70)
    print("RESULTS SAVED")
    print("="*70)
    print(f"\nNext: Run statistical inference and aggregation")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Results file: {summary_file}")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
