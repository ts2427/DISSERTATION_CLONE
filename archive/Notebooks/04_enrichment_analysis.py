# %% [markdown]
# # Deep Dive: Enrichment Variables Analysis
# ## Prior Breaches, Severity, Turnover, Regulation, Dark Web

# %%
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # No popups!
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

# %%
# Smart path handling
if os.path.exists('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = 'outputs'
elif os.path.exists('../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = '../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = '../outputs'
else:
    raise FileNotFoundError("Cannot find enriched dataset")

# Create output directories
os.makedirs(f'{output_base}/figures', exist_ok=True)

df = pd.read_csv(data_path)

print(f"Full Dataset: {len(df)} breaches")

# %% [markdown]
# ## 1. PRIOR BREACH HISTORY ANALYSIS

# %%
print("="*80)
print("PRIOR BREACH HISTORY")
print("="*80)

print(f"\nRepeat Offenders: {df['is_repeat_offender'].sum()} ({df['is_repeat_offender'].mean()*100:.1f}%)")
print(f"First-Time Breaches: {df['is_first_breach'].sum()} ({df['is_first_breach'].mean()*100:.1f}%)")
print(f"\nAverage prior breaches: {df['prior_breaches_total'].mean():.2f}")
print(f"Median prior breaches: {df['prior_breaches_total'].median():.0f}")
print(f"Max prior breaches: {df['prior_breaches_total'].max():.0f}")

# Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df['prior_breaches_total'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
axes[0].set_xlabel('Number of Prior Breaches', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)
axes[0].set_title('Distribution of Prior Breaches', fontsize=12, fontweight='bold')
axes[0].axvline(df['prior_breaches_total'].median(), color='red', linestyle='--', 
                label=f"Median: {df['prior_breaches_total'].median():.0f}")
axes[0].legend()
axes[0].grid(alpha=0.3)

# CARs by prior breach status
first_time_car = df[df['is_first_breach'] == 1]['car_30d'].dropna()
repeat_car = df[df['is_repeat_offender'] == 1]['car_30d'].dropna()

bp = axes[1].boxplot([first_time_car, repeat_car], labels=['First-Time', 'Repeat Offender'],
                      patch_artist=True)
bp['boxes'][0].set_facecolor('lightgreen')
bp['boxes'][1].set_facecolor('lightcoral')

axes[1].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1].set_title('Market Reaction: First-Time vs Repeat Offenders', fontsize=12, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

# Add means
axes[1].text(1, first_time_car.mean(), f'{first_time_car.mean():.2f}%', 
             ha='center', va='bottom', fontweight='bold')
axes[1].text(2, repeat_car.mean(), f'{repeat_car.mean():.2f}%', 
             ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_base}/figures/enrichment_prior_breaches.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved {output_base}/figures/enrichment_prior_breaches.png")
plt.close()

# Statistical test
t_stat, p_val = stats.ttest_ind(first_time_car, repeat_car)
print(f"\nT-test: First-time vs Repeat Offenders")
print(f"  First-time mean CAR: {first_time_car.mean():.4f}%")
print(f"  Repeat offender mean CAR: {repeat_car.mean():.4f}%")
print(f"  Difference: {repeat_car.mean() - first_time_car.mean():.4f}%")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_val:.4f}")

# %% [markdown]
# ## 2. BREACH SEVERITY ANALYSIS

# %%
print("\n" + "="*80)
print("BREACH SEVERITY & TYPES")
print("="*80)

breach_types = {
    'PII Breach': df['pii_breach'].sum(),
    'Ransomware': df['ransomware'].sum(),
    'Financial Data': df['financial_breach'].sum(),
    'Health Data': df['health_breach'].sum(),
    'Insider Threat': df['insider_threat'].sum(),
    'Nation-State': df['nation_state'].sum()
}

for breach_type, count in breach_types.items():
    pct = (count / len(df)) * 100
    print(f"{breach_type:20} {count:4} ({pct:5.1f}%)")

# Severity distribution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Breach types
types_df = pd.DataFrame(list(breach_types.items()), columns=['Type', 'Count'])
axes[0, 0].barh(types_df['Type'], types_df['Count'], color='steelblue', alpha=0.7)
axes[0, 0].set_xlabel('Number of Breaches', fontsize=11)
axes[0, 0].set_title('Breach Types (Non-Exclusive)', fontsize=12, fontweight='bold')
axes[0, 0].grid(axis='x', alpha=0.3)

# Plot 2: Severity score distribution
axes[0, 1].hist(df['combined_severity_score'], bins=30, color='darkred', alpha=0.7, edgecolor='black')
axes[0, 1].axvline(df['combined_severity_score'].median(), color='yellow', linestyle='--', linewidth=2,
                   label=f"Median: {df['combined_severity_score'].median():.1f}")
axes[0, 1].set_xlabel('Combined Severity Score', fontsize=11)
axes[0, 1].set_ylabel('Frequency', fontsize=11)
axes[0, 1].set_title('Distribution of Severity Scores', fontsize=12, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Plot 3: CARs by severity
low_sev_car = df[df['high_severity_breach'] == 0]['car_30d'].dropna()
high_sev_car = df[df['high_severity_breach'] == 1]['car_30d'].dropna()

bp = axes[1, 0].boxplot([low_sev_car, high_sev_car], 
                         labels=['Low Severity', 'High Severity'],
                         patch_artist=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('darkred')

axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1, 0].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1, 0].set_title('Market Reaction by Severity', fontsize=12, fontweight='bold')
axes[1, 0].grid(axis='y', alpha=0.3)

# Plot 4: Health data breaches (HIPAA)
no_health_car = df[df['health_breach'] == 0]['car_30d'].dropna()
health_car = df[df['health_breach'] == 1]['car_30d'].dropna()

bp = axes[1, 1].boxplot([no_health_car, health_car], 
                         labels=['Non-Health', 'Health Data'],
                         patch_artist=True)
bp['boxes'][0].set_facecolor('lightgray')
bp['boxes'][1].set_facecolor('salmon')

axes[1, 1].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1, 1].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1, 1].set_title('Health Data Breaches (HIPAA)', fontsize=12, fontweight='bold')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/enrichment_severity.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved {output_base}/figures/enrichment_severity.png")
plt.close()

# Statistical tests
print(f"\nSeverity Analysis:")
print(f"  Low severity mean CAR: {low_sev_car.mean():.4f}%")
print(f"  High severity mean CAR: {high_sev_car.mean():.4f}%")
print(f"  Difference: {high_sev_car.mean() - low_sev_car.mean():.4f}%")

t_stat, p_val = stats.ttest_ind(low_sev_car, high_sev_car)
print(f"  t-statistic: {t_stat:.4f}, p-value: {p_val:.4f}")

print(f"\nHealth Data Breaches:")
print(f"  Non-health mean CAR: {no_health_car.mean():.4f}%")
print(f"  Health data mean CAR: {health_car.mean():.4f}%")
print(f"  Difference: {health_car.mean() - no_health_car.mean():.4f}%")

t_stat, p_val = stats.ttest_ind(no_health_car, health_car)
print(f"  t-statistic: {t_stat:.4f}, p-value: {p_val:.4f}")

# %% [markdown]
# ## 3. EXECUTIVE TURNOVER ANALYSIS

# %%
print("\n" + "="*80)
print("EXECUTIVE TURNOVER")
print("="*80)

# FIXED: Use correct variable names
print(f"\nBreaches with executive turnover (30d): {df['executive_change_30d'].sum()} ({df['executive_change_30d'].mean()*100:.1f}%)")

# Check if we have detailed turnover data
if 'num_8k_filings' in df.columns:
    print(f"Average 8-K filings per breach: {df['num_8k_filings'].mean():.2f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Turnover prevalence (30-day)
turnover_counts = [df['executive_change_30d'].sum(), 
                   len(df) - df['executive_change_30d'].sum()]
axes[0, 0].pie(turnover_counts, labels=['Turnover', 'No Turnover'],
               autopct='%1.1f%%', colors=['lightcoral', 'lightgreen'],
               startangle=90)
axes[0, 0].set_title('Executive Turnover Within 30 Days', fontsize=12, fontweight='bold')

# Plot 2: Turnover by breach count
turnover_by_breaches = df.groupby('prior_breaches_total')['executive_change_30d'].mean() * 100
if len(turnover_by_breaches) > 0:
    axes[0, 1].plot(turnover_by_breaches.index[:20], turnover_by_breaches.values[:20], 
                    marker='o', color='darkred', linewidth=2)
    axes[0, 1].set_xlabel('Number of Prior Breaches', fontsize=11)
    axes[0, 1].set_ylabel('Turnover Rate (%)', fontsize=11)
    axes[0, 1].set_title('Turnover Rate vs Prior Breaches', fontsize=12, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)

# Plot 3: CARs by turnover
no_turnover_car = df[df['executive_change_30d'] == 0]['car_30d'].dropna()
turnover_car = df[df['executive_change_30d'] == 1]['car_30d'].dropna()

bp = axes[1, 0].boxplot([no_turnover_car, turnover_car],
                         labels=['No Turnover', 'Turnover'],
                         patch_artist=True)
bp['boxes'][0].set_facecolor('lightgreen')
bp['boxes'][1].set_facecolor('lightcoral')

axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1, 0].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1, 0].set_title('Market Reaction by Executive Turnover', fontsize=12, fontweight='bold')
axes[1, 0].grid(axis='y', alpha=0.3)

# Plot 4: Turnover rate by industry (if available)
if 'industry' in df.columns:
    turnover_by_industry = df.groupby('industry')['executive_change_30d'].agg(['sum', 'count'])
    turnover_by_industry['rate'] = (turnover_by_industry['sum'] / turnover_by_industry['count'] * 100)
    top_industries = turnover_by_industry.nlargest(10, 'rate')
    
    axes[1, 1].barh(range(len(top_industries)), top_industries['rate'], color='steelblue', alpha=0.7)
    axes[1, 1].set_yticks(range(len(top_industries)))
    axes[1, 1].set_yticklabels(top_industries.index, fontsize=9)
    axes[1, 1].set_xlabel('Turnover Rate (%)', fontsize=11)
    axes[1, 1].set_title('Top 10 Industries by Turnover Rate', fontsize=12, fontweight='bold')
    axes[1, 1].grid(axis='x', alpha=0.3)
    axes[1, 1].invert_yaxis()
else:
    # Just show turnover vs severity
    turnover_by_severity = df.groupby('high_severity_breach')['executive_change_30d'].mean() * 100
    axes[1, 1].bar(['Low Severity', 'High Severity'], turnover_by_severity.values, 
                   color=['lightblue', 'darkred'], alpha=0.7)
    axes[1, 1].set_ylabel('Turnover Rate (%)', fontsize=11)
    axes[1, 1].set_title('Turnover Rate by Breach Severity', fontsize=12, fontweight='bold')
    axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/enrichment_executive_turnover.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved {output_base}/figures/enrichment_executive_turnover.png")
plt.close()

# Statistical test
t_stat, p_val = stats.ttest_ind(no_turnover_car, turnover_car)
print(f"\nTurnover Effect on CARs:")
print(f"  No turnover mean CAR: {no_turnover_car.mean():.4f}%")
print(f"  Turnover mean CAR: {turnover_car.mean():.4f}%")
print(f"  Difference: {turnover_car.mean() - no_turnover_car.mean():.4f}%")
print(f"  t-statistic: {t_stat:.4f}, p-value: {p_val:.4f}")

# %% [markdown]
# ## 4. REGULATORY ENFORCEMENT ANALYSIS

# %%
print("\n" + "="*80)
print("REGULATORY ENFORCEMENT")
print("="*80)

# FIXED: Use correct variable name
print(f"\nBreaches with regulatory actions: {df['regulatory_enforcement'].sum()} ({df['regulatory_enforcement'].mean()*100:.1f}%)")

# Check if we have penalty data
if 'penalty_amount_usd' in df.columns:
    total_penalties = df['penalty_amount_usd'].sum()
    print(f"\nTotal regulatory costs: ${total_penalties:,.0f}")
    print(f"Mean penalty (if penalized): ${df[df['regulatory_enforcement']==1]['penalty_amount_usd'].mean():,.0f}")
    print(f"Median penalty (if penalized): ${df[df['regulatory_enforcement']==1]['penalty_amount_usd'].median():,.0f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Regulatory action prevalence
reg_counts = [df['regulatory_enforcement'].sum(), 
              len(df) - df['regulatory_enforcement'].sum()]
axes[0, 0].pie(reg_counts, labels=['Regulatory Action', 'No Action'],
               autopct='%1.1f%%', colors=['darkred', 'lightgreen'],
               startangle=90)
axes[0, 0].set_title('Regulatory Enforcement Actions', fontsize=12, fontweight='bold')

# Plot 2: Enforcement rate over time
df['breach_year'] = pd.to_datetime(df['breach_date']).dt.year
enforcement_by_year = df.groupby('breach_year')['regulatory_enforcement'].mean() * 100
if len(enforcement_by_year) > 0:
    axes[0, 1].plot(enforcement_by_year.index, enforcement_by_year.values, 
                    marker='o', color='darkred', linewidth=2)
    axes[0, 1].set_xlabel('Year', fontsize=11)
    axes[0, 1].set_ylabel('Enforcement Rate (%)', fontsize=11)
    axes[0, 1].set_title('Regulatory Enforcement Rate Over Time', fontsize=12, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)

# Plot 3: CARs by regulatory action
no_reg_car = df[df['regulatory_enforcement'] == 0]['car_30d'].dropna()
reg_car = df[df['regulatory_enforcement'] == 1]['car_30d'].dropna()

bp = axes[1, 0].boxplot([no_reg_car, reg_car],
                         labels=['No Action', 'Regulatory Action'],
                         patch_artist=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('darkred')

axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1, 0].set_ylabel('30-Day CAR (%)', fontsize=11)
axes[1, 0].set_title('Market Reaction by Regulatory Status', fontsize=12, fontweight='bold')
axes[1, 0].grid(axis='y', alpha=0.3)

# Plot 4: Enforcement rate by severity
enforcement_by_severity = df.groupby('high_severity_breach')['regulatory_enforcement'].mean() * 100
axes[1, 1].bar(['Low Severity', 'High Severity'], enforcement_by_severity.values, 
               color=['lightblue', 'darkred'], alpha=0.7)
axes[1, 1].set_ylabel('Enforcement Rate (%)', fontsize=11)
axes[1, 1].set_title('Enforcement Rate by Breach Severity', fontsize=12, fontweight='bold')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/enrichment_regulatory.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved {output_base}/figures/enrichment_regulatory.png")
plt.close()

# Statistical test
if len(reg_car) > 0:
    t_stat, p_val = stats.ttest_ind(no_reg_car, reg_car)
    print(f"\nRegulatory Action Effect on CARs:")
    print(f"  No action mean CAR: {no_reg_car.mean():.4f}%")
    print(f"  Regulatory action mean CAR: {reg_car.mean():.4f}%")
    print(f"  Difference: {reg_car.mean() - no_reg_car.mean():.4f}%")
    print(f"  t-statistic: {t_stat:.4f}, p-value: {p_val:.4f}")

# %%
print("\n" + "="*80)
print("✅ ENRICHMENT ANALYSIS COMPLETE!")
print("="*80)
print(f"\nAll enrichment visualizations saved to {output_base}/figures/")
print("\nGenerated:")
print("  ✓ enrichment_prior_breaches.png")
print("  ✓ enrichment_severity.png")
print("  ✓ enrichment_executive_turnover.png")
print("  ✓ enrichment_regulatory.png")
print("="*80)