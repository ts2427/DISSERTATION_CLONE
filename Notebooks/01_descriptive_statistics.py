# %% [markdown]
# # Dissertation Analysis - Part 1: Descriptive Statistics
# ## Data Breach Disclosure Timing and Market Reactions

# %%
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend - no popups!
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# %%
# Smart path handling - works from anywhere
if os.path.exists('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = 'outputs'
elif os.path.exists('../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = '../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = '../outputs'
else:
    raise FileNotFoundError("Cannot find enriched dataset. Run from project root or notebooks folder.")

# Create output directories
os.makedirs(f'{output_base}/tables', exist_ok=True)
os.makedirs(f'{output_base}/figures', exist_ok=True)

# Load enriched dataset
df = pd.read_csv(data_path)

print(f"Dataset loaded: {len(df)} breaches")
print(f"Variables: {len(df.columns)}")
print(f"Date range: {df['breach_date'].min()} to {df['breach_date'].max()}")

# %% [markdown]
# ## SAMPLE ATTRITION AND SELECTION ANALYSIS

# %%
print("\n" + "="*80)
print("  SAMPLE SELECTION AND ATTRITION ANALYSIS")
print("="*80 + "\n")

# Total breaches in dataset
total_breaches = len(df)
print(f"Total breaches in dataset: {total_breaches:,}")

# Breaches with CRSP data (needed for Essay 2 - Event Study)
crsp_sample = df[df['car_30d'].notna()]
n_crsp = len(crsp_sample)
pct_crsp = (n_crsp / total_breaches) * 100

print(f"\nEssay 2 (Event Study) Sample:")
print(f"  Breaches with CRSP data: {n_crsp:,} ({pct_crsp:.1f}%)")
print(f"  Excluded from Essay 2: {total_breaches - n_crsp:,} ({100-pct_crsp:.1f}%)")

# Breaches with volatility data (needed for Essay 3)
vol_sample = df[df['return_volatility_post'].notna()]
n_vol = len(vol_sample)
pct_vol = (n_vol / total_breaches) * 100

print(f"\nEssay 3 (Information Asymmetry) Sample:")
print(f"  Breaches with volatility data: {n_vol:,} ({pct_vol:.1f}%)")
print(f"  Excluded from Essay 3: {total_breaches - n_vol:,} ({100-pct_vol:.1f}%)")

# Compare excluded vs included breaches
print("\n" + "-"*80)
print("  COMPARISON: INCLUDED VS EXCLUDED BREACHES")
print("-"*80 + "\n")

excluded = df[df['car_30d'].isna()]
included = df[df['car_30d'].notna()]

# Variables to compare
comparison_vars = {
    'Firm Size (log)': 'firm_size_log',
    'Leverage': 'leverage',
    'ROA': 'roa',
    'Records Affected': 'total_affected',
    'FCC Reportable (%)': 'fcc_reportable',
    'Prior Breaches (mean)': 'prior_breaches_total',
    'Disclosure Delay (days)': 'disclosure_delay_days',
    'Health Data Breach (%)': 'health_breach',
    'High Severity (%)': 'high_severity_breach'
}

attrition_results = []

for label, col in comparison_vars.items():
    if col not in df.columns:
        continue
    
    # Get excluded and included data
    exc_data = excluded[col].dropna()
    inc_data = included[col].dropna()
    
    if len(exc_data) == 0 or len(inc_data) == 0:
        continue
    
    try:
        # Convert to numeric
        exc_numeric = pd.to_numeric(exc_data, errors='coerce').dropna()
        inc_numeric = pd.to_numeric(inc_data, errors='coerce').dropna()
        
        if len(exc_numeric) == 0 or len(inc_numeric) == 0:
            continue
        
        exc_mean = exc_numeric.mean()
        inc_mean = inc_numeric.mean()
        difference = inc_mean - exc_mean
        
        # Check if binary variable
        unique_vals = set(inc_numeric.unique()) | set(exc_numeric.unique())
        is_binary = unique_vals.issubset({0, 1, 0.0, 1.0})
        
        if is_binary:
            # Chi-square test for binary variables
            contingency = pd.crosstab(df['car_30d'].notna(), df[col].fillna(0))
            chi2, p_val = stats.chi2_contingency(contingency)[:2]
            test_stat = chi2
        else:
            # T-test for continuous variables
            test_stat, p_val = stats.ttest_ind(exc_numeric, inc_numeric, equal_var=False)
        
        # Significance stars
        sig = '***' if p_val < 0.01 else '**' if p_val < 0.05 else '*' if p_val < 0.10 else ''
        
        attrition_results.append({
            'Variable': label,
            'Excluded Mean': f"{exc_mean:.3f}",
            'Included Mean': f"{inc_mean:.3f}",
            'Difference': f"{difference:.3f}",
            't-stat': f"{test_stat:.3f}",
            'p-value': f"{p_val:.4f}",
            'Sig': sig
        })
        
    except Exception as e:
        print(f"Warning: Could not process {label}: {e}")
        continue

# Create and display results
attrition_df = pd.DataFrame(attrition_results)
print(attrition_df.to_string(index=False))

# Save to file
attrition_df.to_csv(f'{output_base}/tables/sample_attrition.csv', index=False)
print(f"\nSaved to {output_base}/tables/sample_attrition.csv")

# Summary interpretation
print("\n" + "-"*80)
print("  INTERPRETATION")
print("-"*80)

sig_diffs = attrition_df[attrition_df['Sig'] != '']
if len(sig_diffs) > 0:
    print(f"\nFound {len(sig_diffs)} significant differences between included/excluded breaches:")
    for _, row in sig_diffs.iterrows():
        print(f"  - {row['Variable']}: {row['Sig']} (p={row['p-value']})")
    print("\n  Note: Sample selection may introduce bias. Consider as limitation.")
else:
    print("\nNo significant differences found between included and excluded breaches.")
    print("  Note: Sample appears representative of full dataset.")

print("\n" + "="*80)
print("SAMPLE ATTRITION ANALYSIS COMPLETE")
print("="*80 + "\n")

# %% [markdown]
# ## Disclosure Timing Distribution Analysis

# %%
print("\n" + "="*80)
print("  DISCLOSURE TIMING DISTRIBUTION ANALYSIS")
print("="*80 + "\n")

# Key timing statistics
if 'disclosure_delay_days' in df.columns:
    timing_data = df['disclosure_delay_days'].dropna()

    print("DISCLOSURE DELAY STATISTICS (Days from Breach to Public Announcement):")
    print(f"  N: {len(timing_data):,}")
    print(f"  Mean: {timing_data.mean():.1f} days")
    print(f"  Median: {timing_data.median():.1f} days")
    print(f"  Std Dev: {timing_data.std():.1f} days")
    print(f"  Min: {timing_data.min():.0f} days")
    print(f"  25th percentile: {timing_data.quantile(0.25):.0f} days")
    print(f"  75th percentile: {timing_data.quantile(0.75):.0f} days")
    print(f"  Max: {timing_data.max():.0f} days")

    # Categorical breakdown
    print("\nDISCLOSURE TIMING CATEGORIES:")
    if 'immediate_disclosure' in df.columns:
        immediate_count = (df['immediate_disclosure'] == 1).sum()
        immediate_pct = (immediate_count / len(df)) * 100
        print(f"  <=7 days (Immediate): {immediate_count:,} ({immediate_pct:.1f}%)")

    if 'delayed_disclosure' in df.columns:
        delayed_count = (df['delayed_disclosure'] == 1).sum()
        delayed_pct = (delayed_count / len(df)) * 100
        print(f"  >30 days (Significantly Delayed): {delayed_count:,} ({delayed_pct:.1f}%)")

    # Calculate intermediate category
    medium_count = len(df) - (immediate_count if 'immediate_disclosure' in df.columns else 0) - \
                          (delayed_count if 'delayed_disclosure' in df.columns else 0)
    medium_pct = (medium_count / len(df)) * 100
    print(f"  8-30 days (Moderately Delayed): {medium_count:,} ({medium_pct:.1f}%)")

    print("\nTIMING DISTRIBUTION INTERPRETATION:")
    print(f"  The sample shows clustering in the 8-30 day window ({medium_pct:.1f}%),")
    print(f"  with significant minority showing immediate disclosure ({immediate_pct:.1f}%).")
    print(f"  This limited variation in the immediate disclosure treatment (19%) is consistent")
    print(f"  with the null finding on timing effects in Essay 2 regressions.")

# Figure: Histogram of Disclosure Timing
if 'disclosure_delay_days' in df.columns:
    fig, ax = plt.subplots(figsize=(12, 6))
    timing_data_clean = df['disclosure_delay_days'].dropna()

    ax.hist(timing_data_clean, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(timing_data_clean.mean(), color='red', linestyle='--', linewidth=2,
               label=f"Mean: {timing_data_clean.mean():.1f} days")
    ax.axvline(timing_data_clean.median(), color='green', linestyle='--', linewidth=2,
               label=f"Median: {timing_data_clean.median():.1f} days")
    ax.axvline(7, color='orange', linestyle=':', linewidth=2, label='7-day threshold')
    ax.axvline(30, color='purple', linestyle=':', linewidth=2, label='30-day threshold')

    ax.set_xlabel('Days from Breach to Disclosure', fontsize=12)
    ax.set_ylabel('Frequency (Number of Breaches)', fontsize=12)
    ax.set_title('Distribution of Disclosure Timing in Sample (N={:,})'.format(len(timing_data_clean)),
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_base}/figures/fig_timing_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\nSaved {output_base}/figures/fig_timing_distribution.png")
    plt.close()

print("\n" + "="*80)
print("TIMING DISTRIBUTION ANALYSIS COMPLETE")
print("="*80 + "\n")

# %% [markdown]
# ## Table 1: Descriptive Statistics - Full Sample

# %%
def create_descriptive_stats(df, variables, var_names):
    """Create descriptive statistics table"""
    stats_list = []
    
    for var, name in zip(variables, var_names):
        if var not in df.columns:
            print(f"Warning: {var} not found in dataset - skipping")
            continue
            
        data = df[var].dropna()
        
        # Skip if no data
        if len(data) == 0:
            print(f"Warning: {var} has no data - skipping")
            continue
        
        try:
            # Try to convert to numeric
            numeric_data = pd.to_numeric(data, errors='coerce').dropna()
            
            if len(numeric_data) == 0:
                print(f"Warning: {var} is not numeric - skipping")
                continue
            
            # Check if binary/boolean
            unique_vals = set(numeric_data.unique())
            if unique_vals.issubset({0, 1, 0.0, 1.0}):
                # Binary column - show proportion
                stats_list.append({
                    'Variable': name,
                    'N': len(numeric_data),
                    'Mean': f"{numeric_data.mean():.3f}",
                    'Std': f"{numeric_data.std():.3f}",
                    'Min': int(numeric_data.min()),
                    'P25': '-',
                    'Median': '-',
                    'P75': '-',
                    'Max': int(numeric_data.max())
                })
            else:
                # Continuous column - show full stats
                stats_list.append({
                    'Variable': name,
                    'N': len(numeric_data),
                    'Mean': f"{numeric_data.mean():.3f}",
                    'Std': f"{numeric_data.std():.3f}",
                    'Min': f"{numeric_data.min():.3f}",
                    'P25': f"{numeric_data.quantile(0.25):.3f}",
                    'Median': f"{numeric_data.median():.3f}",
                    'P75': f"{numeric_data.quantile(0.75):.3f}",
                    'Max': f"{numeric_data.max():.3f}"
                })
                
        except Exception as e:
            print(f"Error processing {var}: {e}")
            continue
    
    return pd.DataFrame(stats_list)

# Define variables for Table 1 - ONLY variables that exist
variables = [
    # Dependent Variables
    'car_30d', 'bhar_30d', 'return_volatility_post',
    
    # Key Independent Variables
    'immediate_disclosure', 'delayed_disclosure', 'disclosure_delay_days',
    'fcc_reportable',
    
    # Firm Characteristics
    'firm_size_log', 'leverage', 'roa', 'total_affected',
    
    # Enrichments (using correct variable names)
    'prior_breaches_total', 'high_severity_breach', 
    'executive_change_30d', 'regulatory_enforcement', 
    'health_breach', 'ransomware'
]

var_names = [
    'CAR (30-day, %)', 'BHAR (30-day, %)', 'Return Volatility (Post)',
    'Immediate Disclosure', 'Delayed Disclosure', 'Disclosure Delay (days)',
    'FCC Reportable',
    'Firm Size (log)', 'Leverage', 'ROA', 'Records Affected',
    'Prior Breaches', 'High Severity Breach', 
    'Executive Turnover (30d)', 'Regulatory Enforcement',
    'Health Data Breach', 'Ransomware Attack'
]

table1 = create_descriptive_stats(df, variables, var_names)

print("\n" + "="*80)
print("TABLE 1: DESCRIPTIVE STATISTICS")
print("="*80)
print(table1.to_string(index=False))

# Save
table1.to_csv(f'{output_base}/tables/table1_descriptive_stats.csv', index=False)
print(f"\nSaved to {output_base}/tables/table1_descriptive_stats.csv")

# %% [markdown]
# ## Table 2: Descriptive Statistics by Disclosure Timing

# %%
def compare_groups(df, group_var, variables, var_names):
    """Compare immediate vs delayed disclosure groups"""
    comparison_list = []
    
    for var, name in zip(variables, var_names):
        if var not in df.columns:
            continue
            
        # Get the two groups
        group0 = df[df[group_var] == 0][var].dropna()
        group1 = df[df[group_var] == 1][var].dropna()
        
        if len(group0) == 0 or len(group1) == 0:
            continue
        
        try:
            # Try to convert to numeric
            group0_numeric = pd.to_numeric(group0, errors='coerce').dropna()
            group1_numeric = pd.to_numeric(group1, errors='coerce').dropna()
            
            if len(group0_numeric) == 0 or len(group1_numeric) == 0:
                continue
            
            # Calculate statistics
            mean0 = group0_numeric.mean()
            mean1 = group1_numeric.mean()
            
            # T-test
            t_stat, p_val = stats.ttest_ind(group0_numeric, group1_numeric, equal_var=False)
            
            comparison_list.append({
                'Variable': name,
                'Delayed Mean': f"{mean0:.3f}",
                'Immediate Mean': f"{mean1:.3f}",
                'Difference': f"{mean1 - mean0:.3f}",
                't-stat': f"{t_stat:.3f}",
                'p-value': f"{p_val:.3f}",
                'Sig': '***' if p_val < 0.01 else '**' if p_val < 0.05 else '*' if p_val < 0.10 else ''
            })
            
        except Exception as e:
            continue
    
    return pd.DataFrame(comparison_list)

table2 = compare_groups(df, 'immediate_disclosure', variables, var_names)

print("\n" + "="*80)
print("TABLE 2: UNIVARIATE COMPARISON - IMMEDIATE VS DELAYED")
print("="*80)
print(table2.to_string(index=False))

table2.to_csv(f'{output_base}/tables/table2_univariate_comparison.csv', index=False)
print(f"\nSaved to {output_base}/tables/table2_univariate_comparison.csv")

# %% [markdown]
# ## Figure 1: Timeline of Breaches

# %%
# Convert breach_date to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'])
df['breach_year'] = df['breach_date'].dt.year

# Count by year
breach_timeline = df.groupby('breach_year').size().reset_index(name='count')

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(breach_timeline['breach_year'], breach_timeline['count'], color='steelblue', alpha=0.7)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Number of Breaches', fontsize=12)
ax.set_title('Timeline of Data Breaches (2004-2025)', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/fig1_breach_timeline.png', dpi=300, bbox_inches='tight')
print(f"Saved {output_base}/figures/fig1_breach_timeline.png")
plt.close()

# %% [markdown]
# ## Figure 2: Distribution of CARs

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# CAR distribution
axes[0].hist(df['car_30d'].dropna(), bins=50, color='steelblue', alpha=0.7, edgecolor='black')
axes[0].axvline(df['car_30d'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {df['car_30d'].mean():.2f}%")
axes[0].axvline(0, color='black', linestyle='-', linewidth=1)
axes[0].set_xlabel('30-Day CAR (%)', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)
axes[0].set_title('Distribution of 30-Day CARs', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# CAR by disclosure timing
immediate = df[df['immediate_disclosure'] == 1]['car_30d'].dropna()
delayed = df[df['delayed_disclosure'] == 1]['car_30d'].dropna()

bp = axes[1].boxplot([delayed, immediate], labels=['Delayed', 'Immediate'], 
                      patch_artist=True, widths=0.6)
bp['boxes'][0].set_facecolor('lightcoral')
bp['boxes'][1].set_facecolor('lightgreen')

axes[1].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1].set_title('CARs by Disclosure Timing', fontsize=12, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/fig2_car_distribution.png', dpi=300, bbox_inches='tight')
print(f"Saved {output_base}/figures/fig2_car_distribution.png")
plt.close()

# %% [markdown]
# ## Figure 3: Enrichment Highlights

# %%
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Prior breaches
if 'is_repeat_offender' in df.columns:
    first_time = len(df) - df['is_repeat_offender'].sum()
    repeat = df['is_repeat_offender'].sum()
    
    axes[0, 0].pie([first_time, repeat],
                   labels=['First-Time\nBreaches', 'Repeat\nOffenders'],
                   autopct='%1.1f%%',
                   colors=['lightblue', 'salmon'],
                   startangle=90)
    axes[0, 0].set_title('Prior Breach History', fontsize=12, fontweight='bold')

# Breach severity
severity_vars = ['pii_breach', 'ransomware', 'health_breach', 'financial_breach']
severity_vars = [v for v in severity_vars if v in df.columns]
if severity_vars:
    severity_counts = df[severity_vars].sum()
    axes[0, 1].bar(range(len(severity_counts)), severity_counts.values, color='steelblue', alpha=0.7)
    axes[0, 1].set_xticks(range(len(severity_counts)))
    axes[0, 1].set_xticklabels([v.replace('_breach', '').replace('_', ' ').upper() for v in severity_vars], rotation=45)
    axes[0, 1].set_ylabel('Number of Breaches', fontsize=11)
    axes[0, 1].set_title('Breach Types', fontsize=12, fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)

# Executive turnover
if 'executive_change_30d' in df.columns:
    turnover = df['executive_change_30d'].sum()
    no_turnover = len(df) - turnover
    
    axes[1, 0].pie([turnover, no_turnover],
                   labels=['Executive\nTurnover', 'No\nTurnover'],
                   autopct='%1.1f%%',
                   colors=['lightcoral', 'lightgreen'],
                   startangle=90)
    axes[1, 0].set_title('Executive Turnover Within 30 Days', fontsize=12, fontweight='bold')

# Regulatory enforcement
if 'regulatory_enforcement' in df.columns:
    enforcement = df['regulatory_enforcement'].sum()
    no_enforcement = len(df) - enforcement
    
    axes[1, 1].pie([enforcement, no_enforcement],
                   labels=['Enforcement\nAction', 'No\nAction'],
                   autopct='%1.1f%%',
                   colors=['darkred', 'lightgray'],
                   startangle=90)
    axes[1, 1].set_title('Regulatory Enforcement Actions', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_base}/figures/fig3_enrichment_highlights.png', dpi=300, bbox_inches='tight')
print(f"Saved {output_base}/figures/fig3_enrichment_highlights.png")
plt.close()

# %% [markdown]
# ## Correlation Matrix

# %%
# Select key variables for correlation
corr_vars = ['car_30d', 'immediate_disclosure', 'fcc_reportable', 
             'firm_size_log', 'prior_breaches_total', 'high_severity_breach',
             'executive_change_30d', 'regulatory_enforcement']

# Only include variables that exist
corr_vars = [v for v in corr_vars if v in df.columns]

if len(corr_vars) > 2:
    corr_data = df[corr_vars].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    ax.set_title('Correlation Matrix - Key Variables', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_base}/figures/correlation_matrix.png', dpi=300, bbox_inches='tight')
    print(f"Saved {output_base}/figures/correlation_matrix.png")
    plt.close()

# %%
print("\n" + "="*80)
print("DESCRIPTIVE STATISTICS COMPLETE!")
print("="*80)
print("\nGenerated:")
print("  - Sample Attrition Analysis")
print("  - Table 1: Descriptive Statistics")
print("  - Table 2: Univariate Comparison")
print("  - Figure 1: Breach Timeline")
print("  - Figure 2: CAR Distribution")
print("  - Figure 3: Enrichment Highlights")
print("  - Correlation Matrix")
print("\nAll files saved to outputs/ folder")
print("="*80)