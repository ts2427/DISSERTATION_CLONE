"""
MASTER RECONCILIATION AUDIT
Extract all key coefficients, p-values, and sample sizes from authoritative sources
Build a single source of truth for all numeric values
"""

import os
import re
import pandas as pd
from pathlib import Path

# Dictionary to store all values
MASTER_VALUES = {}

print("=" * 90)
print("MASTER RECONCILIATION AUDIT - EXTRACTING AUTHORITATIVE VALUES")
print("=" * 90)
print()

# ============================================================================
# ESSAY 1: MARKET REACTIONS (CAR)
# ============================================================================
print("ESSAY 1: MARKET REACTIONS (CAR)")
print("-" * 90)

essay1_file = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\essay2_final\tables\FULL_REGRESSION_OUTPUT.txt'

if os.path.exists(essay1_file):
    with open(essay1_file, 'r') as f:
        content = f.read()

    # Extract H1 coefficient and p-value from Model 2 (main spec)
    h1_match = re.search(r'immediate_disclosure\s+([0-9.-]+)\s+([0-9.]+)\s+([0-9.-]+)\s+([0-9.]+)', content)
    if h1_match:
        h1_coef = float(h1_match.group(1))
        h1_pval = float(h1_match.group(4))
        MASTER_VALUES['h1_coef'] = h1_coef
        MASTER_VALUES['h1_pval'] = h1_pval
        print(f"  [OK] H1 coefficient (immediate_disclosure): {h1_coef:.4f}")
        print(f"  [OK] H1 p-value: {h1_pval:.4f}")

# ============================================================================
# ESSAY 1: SAMPLE SIZE & DESCRIPTIVE STATS
# ============================================================================
print()

essay1_desc = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\essay2_final\tables\TABLE1_descriptives.csv'

if os.path.exists(essay1_desc):
    try:
        df = pd.read_csv(essay1_desc)
        # Look for N or sample size
        if 'N' in df.columns or 'n' in df.columns:
            col = 'N' if 'N' in df.columns else 'n'
            n_essay1 = df[col].iloc[0]
            MASTER_VALUES['n_essay1'] = int(n_essay1)
            print(f"  [OK] Essay 1 sample size (N): {int(n_essay1)}")
    except Exception as e:
        print(f"  [SKIP] Could not read essay1 descriptives: {e}")

# ============================================================================
# POWER ANALYSIS
# ============================================================================
print()
print("POWER ANALYSIS (H1)")
print("-" * 90)

power_file = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\essay2_final\tables\H1_Comprehensive_Power_Analysis.txt'

if os.path.exists(power_file):
    with open(power_file, 'r') as f:
        content = f.read()

    # Extract timing categories
    timing_match = re.search(r'Immediate \(<=7 days\):\s+(\d+)\s+\(\s*([0-9.]+)%\)', content)
    if timing_match:
        immed_n = int(timing_match.group(1))
        immed_pct = float(timing_match.group(2))
        MASTER_VALUES['immediate_n'] = immed_n
        MASTER_VALUES['immediate_pct'] = immed_pct
        print(f"  [OK] Immediate disclosure (<=7 days): {immed_n} ({immed_pct}%)")

    delayed_match = re.search(r'Delayed \(>7 days\):\s+(\d+)\s+\(\s*([0-9.]+)%\)', content)
    if delayed_match:
        delayed_n = int(delayed_match.group(1))
        delayed_pct = float(delayed_match.group(2))
        MASTER_VALUES['delayed_n'] = delayed_n
        MASTER_VALUES['delayed_pct'] = delayed_pct
        print(f"  [OK] Delayed disclosure (>7 days): {delayed_n} ({delayed_pct}%)")

    # Extract MDE
    mde_match = re.search(r'Minimal Detectable Effect at 80% power: \+/-([0-9.]+)pp', content)
    if mde_match:
        mde = float(mde_match.group(1))
        MASTER_VALUES['mde_80'] = mde
        print(f"  [OK] MDE at 80% power: +/-{mde}pp")

    # Extract equivalence bounds
    equiv_match = re.search(r'Equivalence Bounds: \+/-([0-9.]+)', content)
    if equiv_match:
        equiv = float(equiv_match.group(1))
        MASTER_VALUES['equiv_bound'] = equiv
        print(f"  [OK] Equivalence bounds: +/-{equiv}pp")

# ============================================================================
# FCC CAUSAL IDENTIFICATION (Pre/Post 2007)
# ============================================================================
print()
print("FCC CAUSAL IDENTIFICATION")
print("-" * 90)

# Look for pre-2007 and post-2007 results
robustness_file = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\robustness\tables\R05_fixed_effects_full.csv'

if os.path.exists(robustness_file):
    try:
        df = pd.read_csv(robustness_file)
        print(f"  [INFO] Found robustness file with {len(df)} specifications")
        # This file should have pre/post 2007 results
        if 'Model' in df.columns or 'specification' in df.columns:
            print(f"  [INFO] Columns: {list(df.columns)[:10]}")
    except Exception as e:
        print(f"  [SKIP] Could not read robustness file: {e}")

# ============================================================================
# ESSAY 3: GOVERNANCE RESPONSE
# ============================================================================
print()
print("ESSAY 3: GOVERNANCE RESPONSE")
print("-" * 90)

essay3_file = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\essay3_governance/TABLE2_turnover_summary.csv'

if os.path.exists(essay3_file):
    try:
        df = pd.read_csv(essay3_file)
        print(f"  [OK] Found Essay 3 governance table")
        print(f"       Shape: {df.shape}, Columns: {list(df.columns)}")
        # Look for 30-day effect
        if 'fcc_effect_30d' in df.columns or 'effect_30d' in df.columns:
            col = 'fcc_effect_30d' if 'fcc_effect_30d' in df.columns else 'effect_30d'
            effect_30d = df[col].iloc[0]
            MASTER_VALUES['essay3_30d_effect'] = effect_30d
            print(f"       30-day FCC effect: {effect_30d}")
    except Exception as e:
        print(f"  [SKIP] Could not read Essay 3 file: {e}")

# ============================================================================
# HETEROGENEOUS EFFECTS (Essay 2 - Firm Size)
# ============================================================================
print()
print("HETEROGENEOUS EFFECTS (Essay 2 - Firm Size Quartiles)")
print("-" * 90)

heterog_file = r'C:\Users\mcobp\DISSERTATION_CLONE\outputs\essay2_final\tables\TABLE3_heterogeneity.csv'

if os.path.exists(heterog_file):
    try:
        df = pd.read_csv(heterog_file)
        print(f"  [OK] Found heterogeneity table")
        if 'Quartile' in df.columns or 'Q' in df.columns:
            for idx, row in df.iterrows():
                # Print each row to see what we have
                print(f"       {row.to_dict()}")
    except Exception as e:
        print(f"  [SKIP] Could not read heterogeneity file: {e}")

# ============================================================================
# SUMMARY TABLE
# ============================================================================
print()
print("=" * 90)
print("MASTER VALUES EXTRACTED")
print("=" * 90)
print()

# Create summary
summary_lines = []
summary_lines.append("| Metric | Value | Source |")
summary_lines.append("|--------|-------|--------|")

for key, val in sorted(MASTER_VALUES.items()):
    if isinstance(val, float):
        val_str = f"{val:.4f}" if abs(val) < 10 else f"{val:.2f}"
    else:
        val_str = str(val)

    source_map = {
        'h1_coef': 'FULL_REGRESSION_OUTPUT.txt',
        'h1_pval': 'FULL_REGRESSION_OUTPUT.txt',
        'n_essay1': 'TABLE1_descriptives.csv',
        'immediate_n': 'H1_Comprehensive_Power_Analysis.txt',
        'immediate_pct': 'H1_Comprehensive_Power_Analysis.txt',
        'mde_80': 'H1_Power_Analysis_Summary.csv',
        'equiv_bound': 'H1_Comprehensive_Power_Analysis.txt',
    }

    source = source_map.get(key, '?')
    summary_lines.append(f"| {key} | {val_str} | {source} |")

for line in summary_lines:
    print(line)

print()
print("=" * 90)
print("NEXT STEP: Compare these authoritative values to what's in your documents")
print("=" * 90)
