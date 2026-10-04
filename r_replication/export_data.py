"""
R replication package - export the four estimation samples (read-only on the pipeline).

Run from the repository root:   python r_replication/export_data.py

Each CSV holds exactly the rows and variables the committed Python models use: an event id, the
parent-CIK cluster id, the outcome(s), the treatment indicator and the controls. No raw CRSP or
Compustat fields are exported - only derived outcomes (abnormal returns, volatility measures,
departure indicators) and derived controls (log size, leverage, ROA, ...).

Before writing, each sample's N, treated-event count and cluster count are asserted against the
committed constants, so a file can never describe a different sample from the one the essays use.

  essay1_car.csv            scripts/158  baseline sample, N = 340
  essay2_volatility.csv     scripts/165 (volatility) and scripts/164 (delay) sample, N = 333
  essay2_announcement.csv   scripts/175  elevation model, N = 331
  essay3_departures.csv     scripts/227  30/90/180-day and placebo models, N = 405
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('r_replication')
TREAT = 'fcc_form499'


def check(name, got, expected):
    assert got == expected, f'{name}: {got} != committed {expected}'
    print(f'  ok  {name} = {got}')


def finish(df, cols, fname):
    out = df[cols].copy()
    assert not out.isna().any().any(), f'{fname}: missing values in exported columns'
    assert out['event_id'].is_unique, f'{fname}: event_id not unique'
    out.to_csv(OUT / fname, index=False, lineterminator='\n')
    print(f'  wrote {OUT / fname}: {len(out)} rows x {len(cols)} columns')


def event_id(df):
    """parent CIK + breach date; a running suffix is added only where that pair repeats."""
    base = df['final_cik'].astype(int).astype(str) + '_' + df['breach_date'].astype(str).str[:10]
    dup = base.duplicated(keep=False)
    return base.where(~dup, base + '_' + (base.groupby(base).cumcount() + 1).astype(str))


# ------------------------------------------------------------------ Essay 1 (scripts/158:59-72)
print('Essay 1')
c1 = json.loads(Path('outputs/rebuild/constants_v3.json').read_text())
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
H = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = H + ['firm_size_log', 'leverage', 'roa']
reg = ev[ev['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS).copy()
check('N', len(reg), c1['N_regression'])
check('treated events', int(reg[TREAT].sum()), c1['treated_regression'])
check('treated parent CIKs', reg.loc[reg[TREAT] == 1, 'final_cik'].nunique(), c1['treated_parent_ciks_regression'])
ref = pd.read_csv('outputs/defense_supplement/e1_notification_anchored.csv')
check('parent-CIK clusters', reg['final_cik'].nunique(), int(ref.loc[ref['anchor'].str.startswith('breach'), 'n_clusters'].iloc[0]))
reg['event_id'] = event_id(reg)
reg['parent_cik'] = reg['final_cik'].astype(int)
finish(reg, ['event_id', 'parent_cik', 'car_30d'] + CONTROLS, 'essay1_car.csv')

# ------------------------------------------------------------------ Essay 2 (scripts/165:48-60, 164:113-136)
print('Essay 2 - volatility and delay')
cs = json.loads(Path('outputs/defense_supplement/constants_defense_supplement.json').read_text())
fin = pd.read_csv('outputs/tables/essay2_v2/t1_final_sample.csv', low_memory=False)
check('N', len(fin), cs['E2_N'])
check('treated events', int(fin[TREAT].sum()), cs['E2_treated_events'])
check('parent-CIK clusters', fin['final_cik'].nunique(), cs['E2_G'])
check('treated parent CIKs', fin.loc[fin[TREAT] == 1, 'final_cik'].nunique(), cs['E2_G1'])
fin['event_id'] = event_id(fin)
fin['parent_cik'] = fin['final_cik'].astype(int)
finish(fin, ['event_id', 'parent_cik', 'e2_vol_change', 'disclosure_delay_days', 'delay_w', TREAT,
             'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events'],
       'essay2_volatility.csv')

# ------------------------------------------------------------------ Essay 2 announcement (scripts/175:59-60, 175-180)
print('Essay 2 - announcement elevation')
t42 = pd.read_csv('outputs/tables/essay2_v2/t42_final_sample_with_repairs.csv', low_memory=False)
CTRL = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events']
br = t42.dropna(subset=['abn_ann', 'abn_pre']).copy()
br['elev'] = br['abn_ann'] - br['abn_pre']
d3 = br.dropna(subset=[TREAT, 'abn_pre'] + CTRL).copy()
t50 = pd.read_csv('outputs/tables/essay2_v2/t50_announcement_contrast.csv')
check('N', len(d3), int(t50.loc[t50['level'] == 'L3', 'n'].iloc[0]))
check('treated events', int(d3[TREAT].sum()), cs['E2_treated_events'])  # both dropped events are controls
d3['event_id'] = event_id(d3)
d3['parent_cik'] = d3['final_cik'].astype(int)
print(f"  parent-CIK clusters = {d3['parent_cik'].nunique()}, treated parent CIKs = "
      f"{d3.loc[d3[TREAT] == 1, 'parent_cik'].nunique()} (reported in ESSAY2_ANNOUNCEMENT_CONTRAST.md)")
assert d3['parent_cik'].nunique() == 81 and d3.loc[d3[TREAT] == 1, 'parent_cik'].nunique() == 12
finish(d3, ['event_id', 'parent_cik', 'elev', TREAT, 'abn_pre'] + CTRL, 'essay2_announcement.csv')

# ------------------------------------------------------------------ Essay 3 (scripts/227:80-84)
print('Essay 3')
c3 = json.loads(Path('outputs/essay3_v4/constants_essay3_v4.json').read_text())
d0 = pd.read_csv('outputs/essay3_v4/e_analysis_sample.csv', low_memory=False)
d0 = d0[d0['in_analysis_sample'] == 1].reset_index(drop=True)
check('N', len(d0), c3['N'])
check('treated events', int(d0[TREAT].sum()), c3['treated'])
check('parent-CIK clusters', d0['final_cik'].nunique(), c3['parent_ciks'])
check('treated parent CIKs', d0.loc[d0[TREAT] == 1, 'final_cik'].nunique(), c3['treated_parent_ciks'])
d0['event_id'] = event_id(d0)
d0['parent_cik'] = d0['final_cik'].astype(int)
finish(d0, ['event_id', 'parent_cik', 'exec_departure_30_rd', 'exec_departure_90_rd', 'exec_departure_180_rd',
            'placebo_exec_departure_rd', TREAT, 'prior_breaches_1yr', 'health_breach', 'firm_size_log',
            'leverage', 'roa', 'baseline_exec_rate_py_rd', 'prior12m_mktadj_ret_rd'],
       'essay3_departures.csv')
print('done')
