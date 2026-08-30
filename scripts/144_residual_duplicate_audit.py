"""
SCRIPT 144: RESIDUAL-DUPLICATE AUDIT (name-variant twins surviving dedup)
=========================================================================
The 1,054 -> 784 deduplication keyed EXACT org_name + breach_date, so spelling
variants of the same organization defeat it (found 8/4/2026: T-Mobile
2015-09-14 survives three times with identical CARs; four more dates twice).

This audit:
  1. Re-keys the 784-event set on normalize_name_aggressive(org_name) +
     breach_date (the same normalizer the CIK-resolution chain uses), and
     separately on cik + breach_date, and quantifies collapse under each.
  2. Lists every collapsing group (names, dates, CARs, treatment, sample
     membership) — full list to outputs, summary to console.
  3. Reports +/-3-day same-CIK adjacent-date candidates SEPARATELY, without
     collapsing them (case-by-case adjudication required).
  4. Emits a corrected candidate event set (normalized-key dedup only) to
     Data/processed/FINAL_DATASET_DEDUP_V2_CANDIDATE.csv. NOTHING canonical is
     overwritten. Survivor rule (deterministic): within each group keep the row
     with non-null car_30d, then longest incident_details, then lexicographically
     first org_name.
  5. Stop-and-report: states whether the 1,054 -> 784 closure assertion in
     script 142 is affected (it is not modified here either way).

Outputs: outputs/RESIDUAL_DUPLICATE_AUDIT.md
         outputs/residual_duplicate_groups.csv
         outputs/residual_duplicate_adjacent_candidates.csv
         Data/processed/FINAL_DATASET_DEDUP_V2_CANDIDATE.csv
"""

import sys
import re
import pandas as pd
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs')
lines = []


def log(m=''):
    print(m)
    lines.append(str(m))


def normalize_name_aggressive(name):
    """Copied verbatim from scripts/apply_exact_matching_full_dataset.py (ll. 24-41)."""
    if not isinstance(name, str):
        return ""
    normalized = name.upper().strip()
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    suffixes = [r'\bINC\b', r'\bCORPORATION\b', r'\bLLC\b', r'\bLLP\b', r'\bLP\b',
                r'\bCO\b', r'\bCOMPANY\b', r'\bLTD\b', r'\bLIMITED\b',
                r'\bNA\b', r'\bNOT FOR PROFIT\b', r'\bTHE\b']
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized)
    return re.sub(r'\s+', ' ', normalized).strip()


log('=' * 90)
log('SCRIPT 144: RESIDUAL-DUPLICATE AUDIT')
log('=' * 90)

d784 = pd.read_csv('Data/processed/FINAL_DATASET_DEDUPLICATED_784.csv', low_memory=False)
assert len(d784) == 784, f'input changed: {len(d784)}'
canon = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv', low_memory=False)
CONTROLS = ['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']
canon['k'] = canon['org_name'].astype(str) + '|' + canon['breach_date'].astype(str)
regk = set(canon[canon['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS)['k'])
crspk = set(canon[canon['has_crsp_data'] == 1]['k'])
treatmap = dict(zip(canon['k'], canon['fcc_form499']))
carmap = dict(zip(canon['k'], canon['car_30d']))

d784['k'] = d784['org_name'].astype(str) + '|' + d784['breach_date'].astype(str)
d784['norm_name'] = d784['org_name'].map(normalize_name_aggressive)
d784['nk'] = d784['norm_name'] + '|' + d784['breach_date'].astype(str)
d784['ck'] = d784['cik'].astype(str) + '|' + d784['breach_date'].astype(str)
d784['in_crsp'] = d784['k'].isin(crspk)
d784['in_reg'] = d784['k'].isin(regk)
d784['fcc_canon'] = d784['k'].map(treatmap)
d784['car_canon'] = d784['k'].map(carmap)

# ---------------------------------------------------------------------------
# Pass 1: normalized name + date
# ---------------------------------------------------------------------------
log('\n[1] Normalized-name + breach_date key...')
vc_n = d784['nk'].value_counts()
groups_n = d784[d784['nk'].isin(vc_n[vc_n > 1].index)].sort_values(['nk', 'org_name'])
n_groups = int((vc_n > 1).sum())
n_excess_n = int((vc_n[vc_n > 1] - 1).sum())
log(f'  Collapsing groups: {n_groups}; excess rows: {n_excess_n}')
log(f'  Corrected event count under this key: {d784["nk"].nunique()} (784 - {n_excess_n})')

# ---------------------------------------------------------------------------
# Pass 2: CIK + date
# ---------------------------------------------------------------------------
log('\n[2] CIK + breach_date key...')
has_cik = d784[d784['cik'].notna()]
vc_c = has_cik['ck'].value_counts()
groups_c = has_cik[has_cik['ck'].isin(vc_c[vc_c > 1].index)].sort_values(['ck', 'org_name'])
n_groups_c = int((vc_c > 1).sum())
n_excess_c = int((vc_c[vc_c > 1] - 1).sum())
log(f'  Collapsing groups: {n_groups_c}; excess rows: {n_excess_c}')
log(f'  Corrected event count under this key: {d784["ck"].nunique()} '
    f'(note: CIK key can over-collapse distinct same-day events at one parent)')

extra_over_norm = groups_c[~groups_c['ck'].isin(
    groups_n.assign(ck=groups_n['cik'].astype(str) + '|' + groups_n['breach_date'].astype(str))['ck'])]
log(f'  CIK-key groups NOT caught by the normalized-name key: '
    f'{extra_over_norm["ck"].nunique()} groups, {len(extra_over_norm)} rows '
    f'(different brands, same parent, same day - adjudication, not auto-collapse)')

# ---------------------------------------------------------------------------
# Impact on downstream samples (normalized-name key, the collapse actually applied)
# ---------------------------------------------------------------------------
log('\n[3] Sample impact of the normalized-name collapse...')
excess_rows = groups_n.groupby('nk').apply(lambda g: g.iloc[1:], include_groups=False)
imp_crsp = int(groups_n.groupby('nk')['in_crsp'].apply(lambda s: max(0, s.sum() - 1)).sum())
imp_reg = int(groups_n.groupby('nk')['in_reg'].apply(lambda s: max(0, s.sum() - 1)).sum())
imp_treated = int(groups_n[groups_n['fcc_canon'] == 1].groupby('nk')['in_reg']
                  .apply(lambda s: max(0, s.sum() - 1)).sum())
log(f'  Excess rows currently in CRSP sample: {imp_crsp} (672 would become ~{672 - imp_crsp})')
log(f'  Excess rows currently in regression sample: {imp_reg} (648 would become ~{648 - imp_reg})')
log(f'  Excess TREATED regression rows: {imp_treated} (115 would become ~{115 - imp_treated})')
log('  (approximate: exact downstream Ns require the full regeneration, step 4 of the plan)')

# ---------------------------------------------------------------------------
# Adjacent-date candidates (+/-3 days, same CIK) - REPORT ONLY
# ---------------------------------------------------------------------------
log('\n[4] Same-CIK adjacent-date candidates (+/-3 days, NOT collapsed)...')
adj_rows = []
for cik, g in has_cik.groupby('cik'):
    g = g.sort_values('breach_date')
    dts = pd.to_datetime(g['breach_date']).values
    for i in range(len(g) - 1):
        delta = (dts[i + 1] - dts[i]) / np.timedelta64(1, 'D')
        if 0 < delta <= 3:
            a, b = g.iloc[i], g.iloc[i + 1]
            if a['nk'] != b['nk']:  # same-key pairs already counted in pass 1
                adj_rows.append({'cik': cik, 'org_1': a['org_name'], 'date_1': a['breach_date'],
                                 'org_2': b['org_name'], 'date_2': b['breach_date'],
                                 'days_apart': int(delta), 'car_1': a['car_canon'],
                                 'car_2': b['car_canon'],
                                 'same_normalized_name': a['norm_name'] == b['norm_name']})
adj_df = pd.DataFrame(adj_rows)
log(f'  Adjacent-date candidate pairs: {len(adj_df)} '
    f'(of which same normalized name, different date: '
    f'{int(adj_df["same_normalized_name"].sum()) if len(adj_df) else 0})')

# ---------------------------------------------------------------------------
# Emit corrected candidate set (normalized-name key only)
# ---------------------------------------------------------------------------
log('\n[5] Emitting corrected candidate event set...')
d = d784.copy()
d['_has_car'] = d['car_canon'].notna()
d['_det_len'] = d['incident_details'].astype(str).str.len()
d = d.sort_values(['nk', '_has_car', '_det_len', 'org_name'],
                  ascending=[True, False, False, True])
dedup_v2 = d.drop_duplicates(subset='nk', keep='first').drop(
    columns=['_has_car', '_det_len', 'k', 'nk', 'ck', 'in_crsp', 'in_reg',
             'fcc_canon', 'car_canon', 'norm_name'])
cand_path = Path('Data/processed/FINAL_DATASET_DEDUP_V2_CANDIDATE.csv')
dedup_v2.to_csv(cand_path, index=False)
log(f'  {cand_path}: {len(dedup_v2)} events (784 - {784 - len(dedup_v2)})')
assert len(dedup_v2) == d784['nk'].nunique()

# ---------------------------------------------------------------------------
# Closure statement (script 142)
# ---------------------------------------------------------------------------
log('\n[6] Script 142 closure statement:')
log('  The 1,054 -> 784 closure (exact-key dedup, 270 excess records) is arithmetic '
    'over EXACT keys and remains true as stated; this audit shows the exact key was '
    'INSUFFICIENT, not miscounted. If the v2 candidate is adopted, the ledger gains a '
    'row (784 -> {} residual name-variant dedup) rather than changing the existing one. '
    'Script 142 NOT modified.'.format(len(dedup_v2)))

# Save artifacts
gcols = ['nk', 'org_name', 'norm_name', 'breach_date', 'cik', 'car_canon',
         'fcc_canon', 'in_crsp', 'in_reg']
groups_n[gcols].to_csv(OUT / 'residual_duplicate_groups.csv', index=False)
if len(adj_df):
    adj_df.to_csv(OUT / 'residual_duplicate_adjacent_candidates.csv', index=False)

with open(OUT / 'RESIDUAL_DUPLICATE_AUDIT.md', 'w', encoding='utf-8') as f:
    f.write('# Residual-Duplicate Audit (scripts/144, live-computed)\n\n')
    f.write('\n'.join(lines))
    f.write('\n\n## Collapsing groups (normalized-name key)\n\n')
    for nk, g in groups_n.groupby('nk'):
        f.write(f"\n**{nk}** ({len(g)} rows):\n")
        for _, r in g.iterrows():
            f.write(f"- {r['org_name']} | {r['breach_date']} | CAR {r['car_canon']} | "
                    f"fcc={r['fcc_canon']} | crsp={r['in_crsp']} reg={r['in_reg']}\n")

log('\nSaved: outputs/RESIDUAL_DUPLICATE_AUDIT.md, residual_duplicate_groups.csv, '
    'residual_duplicate_adjacent_candidates.csv, FINAL_DATASET_DEDUP_V2_CANDIDATE.csv')
