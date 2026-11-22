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
  essay2_announcement.csv   scripts/265  v5 elevation model, N = 333 (replaced scripts/175's N = 331 on 2026-11-22)
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

# ------------------------------------------------------------------ Essay 2 announcement, v5 (scripts/265:51-86)
# 2026-11-22: the v5 estimate replaces the defense-era scripts/175 one (market-model residuals,
# N = 331). Elevation is computed exactly as scripts/265 does it, through scripts/263's Market class:
# SD of market-adjusted returns over trading days [-4,+4] around the reporting date minus SD over
# [-25,-5], 80% coverage. Before writing, the point estimate and the CV1 and CV3 SEs must
# reproduce outputs/essay2_v5/v5_t09b_announcement_ladder.csv.
print('Essay 2 - announcement elevation (v5)')
import importlib.util as _ilu  # noqa: E402
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L5 = _ilu.module_from_spec(_s)
_s.loader.exec_module(L5)
CTRL = list(L5.CONTROLS)
d3 = L5.load_sample()
M5 = L5.Market()
elev, base = [], []
for _, r_ in d3.iterrows():
    pos = M5.anchor(r_['permno'], r_['rdt'])
    if pos is None:
        elev.append(float('nan')); base.append(float('nan'))
        continue
    ar = M5.abnormal(r_['permno'], pos)
    b_ = M5.window_sd(ar, pos, (-25, -5))[0]
    elev.append(M5.window_sd(ar, pos, (-4, 4))[0] - b_); base.append(b_)
d3['elev'], d3['base_sd'] = elev, base
lad = pd.read_csv('outputs/essay2_v5/v5_t09b_announcement_ladder.csv').set_index('rung')
got = L5.ladder(d3, 'elev', [TREAT, 'base_sd'] + CTRL, full=False)
for k_, rung in [('coef', 'CV1 parent filer entity'), ('se_cv1', 'CV1 parent filer entity'),
                 ('se_cv3', 'CV3 cluster jackknife (PRIMARY)')]:
    want = float(lad.loc[rung, 'coef' if k_ == 'coef' else 'se'])
    assert abs(got[k_] - want) < 1e-10, f'v5 announcement {k_}: {got[k_]} != committed {want}'
    print(f'  ok  {k_} = {got[k_]:.6f} (v5_t09b)')
check('N', got['N'], int(lad['N'].iloc[0]))
check('treated events', int(d3[TREAT].sum()), cs['E2_treated_events'])
d3['event_id'] = event_id(d3)
d3['parent_cik'] = d3['final_cik'].astype(int)
check('parent-CIK clusters', d3['parent_cik'].nunique(), int(lad['G'].iloc[0]))
check('treated parent CIKs', d3.loc[d3[TREAT] == 1, 'parent_cik'].nunique(), int(lad['G1'].iloc[0]))
finish(d3, ['event_id', 'parent_cik', 'elev', TREAT, 'base_sd'] + CTRL, 'essay2_announcement.csv')

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
