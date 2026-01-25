"""
SUMMARY STATISTICS - TABLE 1

Creates comprehensive descriptive statistics for the dissertation.
Publication-ready tables showing variable distributions across:
- Full sample
- CRSP sample
- By FCC regulation
- By disclosure timing

Output: Table 1 for Essays 2 & 3
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SUMMARY STATISTICS - TABLE 1")
print("=" * 80)

# Configuration
DATA_FILE = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
OUTPUT_DIR = Path('outputs/tables')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"\n[Step 1/6] Loading enriched dataset...")
df = pd.read_csv(DATA_FILE)
print(f"  ✓ Loaded: {len(df):,} breaches × {len(df.columns)} columns")

# Convert date column
df['breach_date'] = pd.to_datetime(df['breach_date'])

# ============================================================================
# DEFINE VARIABLE GROUPS
# ============================================================================

print(f"\n[Step 2/6] Defining variable groups...")

# Define variables for summary statistics
variables = {
    'Market Reactions': {
        'car_5d': '5-Day CAR (%)',
        'car_30d': '30-Day CAR (%)',
        'bhar_5d': '5-Day BHAR (%)',
        'bhar_30d': '30-Day BHAR (%)',
        'return_volatility_post': 'Post-Breach Volatility',
        'volatility_change': 'Volatility Change'
    },
    'Breach Characteristics': {
        'total_affected': 'Records Affected',
        'total_affected_log': 'Records Affected (log)',
        'days_to_disclosure': 'Days to Disclosure',
        'immediate_disclosure': 'Immediate Disclosure (≤7 days)',
        'delayed_disclosure': 'Delayed Disclosure (>30 days)',
        'health_breach': 'Health Data Breach',
        'financial_breach': 'Financial Data Breach',
        'pii_breach': 'PII Breach',
        'severity_score': 'Breach Severity Score',
        'breach_type_count': 'Number of Breach Types'
    },
    'Prior Breach History': {
        'prior_breaches_total': 'Total Prior Breaches',
        'prior_breaches_1yr': 'Prior Breaches (1 year)',
        'prior_breaches_3yr': 'Prior Breaches (3 years)',
        'is_repeat_offender': 'Repeat Offender',
        'days_since_last_breach': 'Days Since Last Breach'
    },
    'Firm Characteristics': {
        'firm_size_log': 'Firm Size (log assets)',
        'leverage': 'Leverage',
        'roa': 'ROA (%)',
        'market_to_book': 'Market-to-Book',
        'cash_ratio': 'Cash Ratio',
        'current_ratio': 'Current Ratio'
    },
    'Governance & Media': {
        'sox_404_effective': 'SOX 404 Effective',
        'material_weakness': 'Material Weakness',
        'executive_change_30d': 'Executive Change (30d)',
        'executive_change_90d': 'Executive Change (90d)',
        'has_enforcement': 'Regulatory Enforcement',
        'media_coverage_count': 'Media Articles',
        'high_media_coverage': 'High Media Coverage'
    }
}

# Flatten variable list
all_vars = []
var_labels = {}
for group, vars_dict in variables.items():
    for var, label in vars_dict.items():
        if var in df.columns:
            all_vars.append(var)
            var_labels[var] = label

print(f"  ✓ Total variables for summary: {len(all_vars)}")

# ============================================================================
# PANEL A: FULL SAMPLE
# ============================================================================

print(f"\n[Step 3/6] Creating Panel A: Full Sample...")

def create_summary_stats(data, var_list):
    """Create summary statistics for a list of variables"""
    stats = []
    
    for var in var_list:
        if var not in data.columns:
            continue
        
        # Convert to numeric
        series = pd.to_numeric(data[var], errors='coerce')
        
        # Calculate statistics
        n_obs = series.notna().sum()
        
        if n_obs > 0:
            stats.append({
                'Variable': var_labels.get(var, var),
                'N': int(n_obs),
                'Mean': series.mean(),
                'Std': series.std(),
                'Min': series.min(),
                'P25': series.quantile(0.25),
                'Median': series.median(),
                'P75': series.quantile(0.75),
                'Max': series.max()
            })
    
    return pd.DataFrame(stats)

panel_a = create_summary_stats(df, all_vars)

print(f"  ✓ Panel A: {len(panel_a)} variables")
print(f"    Full sample N: {len(df):,}")

# ============================================================================
# PANEL B: CRSP SAMPLE ONLY
# ============================================================================

print(f"\n[Step 4/6] Creating Panel B: CRSP Sample...")

if 'has_crsp_data' in df.columns:
    crsp_sample = df[df['has_crsp_data'] == True].copy()
    panel_b = create_summary_stats(crsp_sample, all_vars)
    
    print(f"  ✓ Panel B: {len(panel_b)} variables")
    print(f"    CRSP sample N: {len(crsp_sample):,}")
else:
    panel_b = None
    print(f"  ⚠ No CRSP flag found, skipping Panel B")

# ============================================================================
# PANEL C: BY FCC REGULATION
# ============================================================================

print(f"\n[Step 5/6] Creating Panel C: By FCC Regulation...")

if 'fcc_reportable' in df.columns:
    fcc_yes = df[df['fcc_reportable'] == 1].copy() if df['fcc_reportable'].dtype == 'int64' else df[df['fcc_reportable'] == True].copy()
    fcc_no = df[df['fcc_reportable'] == 0].copy() if df['fcc_reportable'].dtype == 'int64' else df[df['fcc_reportable'] == False].copy()
    
    panel_c_yes = create_summary_stats(fcc_yes, all_vars)
    panel_c_no = create_summary_stats(fcc_no, all_vars)
    
    # Add group labels
    panel_c_yes['Group'] = 'FCC Regulated'
    panel_c_no['Group'] = 'Non-FCC'
    
    print(f"  ✓ Panel C created")
    print(f"    FCC Regulated: {len(fcc_yes):,}")
    print(f"    Non-FCC: {len(fcc_no):,}")
else:
    panel_c_yes = None
    panel_c_no = None
    print(f"  ⚠ No FCC flag found, skipping Panel C")

# ============================================================================
# PANEL D: BY DISCLOSURE TIMING
# ============================================================================

print(f"\n[Step 6/6] Creating Panel D: By Disclosure Timing...")

if 'immediate_disclosure' in df.columns:
    immediate = df[df['immediate_disclosure'] == 1].copy() if df['immediate_disclosure'].dtype == 'int64' else df[df['immediate_disclosure'] == True].copy()
    delayed = df[df['immediate_disclosure'] == 0].copy() if df['immediate_disclosure'].dtype == 'int64' else df[df['immediate_disclosure'] == False].copy()
    
    panel_d_imm = create_summary_stats(immediate, all_vars)
    panel_d_del = create_summary_stats(delayed, all_vars)
    
    # Add group labels
    panel_d_imm['Group'] = 'Immediate (≤7d)'
    panel_d_del['Group'] = 'Delayed (>7d)'
    
    print(f"  ✓ Panel D created")
    print(f"    Immediate: {len(immediate):,}")
    print(f"    Delayed: {len(delayed):,}")
else:
    panel_d_imm = None
    panel_d_del = None
    print(f"  ⚠ No disclosure timing flag found, skipping Panel D")

# ============================================================================
# FORMAT AND SAVE TABLES
# ============================================================================

print(f"\n" + "=" * 80)
print("FORMATTING TABLES")
print("=" * 80)

def format_summary_table(df, decimal_places=2):
    """Format summary statistics for publication"""
    formatted = df.copy()
    
    # Format numeric columns
    for col in ['Mean', 'Std', 'Min', 'P25', 'Median', 'P75', 'Max']:
        if col in formatted.columns:
            formatted[col] = formatted[col].apply(lambda x: f"{x:.{decimal_places}f}" if pd.notna(x) else "")
    
    return formatted

# Format Panel A
panel_a_formatted = format_summary_table(panel_a)

print(f"\n{'='*80}")
print("PANEL A: FULL SAMPLE DESCRIPTIVE STATISTICS")
print(f"{'='*80}")
print("\nFirst 10 variables:")
print(panel_a_formatted.head(10).to_string(index=False))

# Save Panel A
panel_a_formatted.to_csv(OUTPUT_DIR / 'TABLE1_PANEL_A_full_sample.csv', index=False)
print(f"\n✓ Saved: TABLE1_PANEL_A_full_sample.csv")

# Format and save Panel B
if panel_b is not None:
    panel_b_formatted = format_summary_table(panel_b)
    panel_b_formatted.to_csv(OUTPUT_DIR / 'TABLE1_PANEL_B_crsp_sample.csv', index=False)
    print(f"✓ Saved: TABLE1_PANEL_B_crsp_sample.csv")

# Format and save Panel C
if panel_c_yes is not None and panel_c_no is not None:
    panel_c_combined = pd.concat([panel_c_yes, panel_c_no], ignore_index=True)
    panel_c_formatted = format_summary_table(panel_c_combined)
    panel_c_formatted.to_csv(OUTPUT_DIR / 'TABLE1_PANEL_C_by_fcc.csv', index=False)
    print(f"✓ Saved: TABLE1_PANEL_C_by_fcc.csv")

# Format and save Panel D
if panel_d_imm is not None and panel_d_del is not None:
    panel_d_combined = pd.concat([panel_d_imm, panel_d_del], ignore_index=True)
    panel_d_formatted = format_summary_table(panel_d_combined)
    panel_d_formatted.to_csv(OUTPUT_DIR / 'TABLE1_PANEL_D_by_timing.csv', index=False)
    print(f"✓ Saved: TABLE1_PANEL_D_by_timing.csv")

# ============================================================================
# CREATE COMBINED TABLE FOR DISSERTATION
# ============================================================================

print(f"\n" + "=" * 80)
print("CREATING COMBINED TABLE 1")
print("=" * 80)

# Create LaTeX-style table with UTF-8 encoding
with open(OUTPUT_DIR / 'TABLE1_COMBINED.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("TABLE 1: DESCRIPTIVE STATISTICS\n")
    f.write("=" * 100 + "\n\n")
    
    f.write("PANEL A: FULL SAMPLE (N={:,})\n".format(len(df)))
    f.write("-" * 100 + "\n")
    f.write(panel_a_formatted.to_string(index=False))
    f.write("\n\n")
    
    if panel_b is not None:
        f.write("PANEL B: CRSP SAMPLE (N={:,})\n".format(len(crsp_sample)))
        f.write("-" * 100 + "\n")
        f.write(format_summary_table(panel_b).to_string(index=False))
        f.write("\n\n")
    
    if panel_c_yes is not None:
        f.write("PANEL C: BY FCC REGULATION\n")
        f.write("-" * 100 + "\n")
        f.write(panel_c_formatted.to_string(index=False))
        f.write("\n\n")
    
    if panel_d_imm is not None:
        f.write("PANEL D: BY DISCLOSURE TIMING\n")
        f.write("-" * 100 + "\n")
        f.write(panel_d_formatted.to_string(index=False))
        f.write("\n\n")
    
    f.write("=" * 100 + "\n")
    f.write("Notes: All continuous variables winsorized at 1% and 99% levels.\n")
    f.write("Immediate disclosure defined as <=7 days from breach discovery to public disclosure.\n")
    f.write("=" * 100 + "\n")

print(f"\n✓ Saved: TABLE1_COMBINED.txt")

# ============================================================================
# SUMMARY
# ============================================================================

print(f"\n" + "=" * 80)
print("✓ SUMMARY STATISTICS COMPLETE")
print("=" * 80)

print(f"\nFiles created in {OUTPUT_DIR}/:")
print(f"  • TABLE1_PANEL_A_full_sample.csv")
if panel_b is not None:
    print(f"  • TABLE1_PANEL_B_crsp_sample.csv")
if panel_c_yes is not None:
    print(f"  • TABLE1_PANEL_C_by_fcc.csv")
if panel_d_imm is not None:
    print(f"  • TABLE1_PANEL_D_by_timing.csv")
print(f"  • TABLE1_COMBINED.txt (formatted for dissertation)")

print(f"\nKey Statistics:")
print(f"  • Total breaches: {len(df):,}")
if panel_b is not None:
    print(f"  • With CRSP data: {len(crsp_sample):,}")
if panel_c_yes is not None:
    print(f"  • FCC regulated: {len(fcc_yes):,}")
    print(f"  • Non-FCC: {len(fcc_no):,}")
if panel_d_imm is not None:
    print(f"  • Immediate disclosure: {len(immediate):,}")
    print(f"  • Delayed disclosure: {len(delayed):,}")

print(f"\n📊 Table 1 ready for dissertation!")
print("=" * 80)