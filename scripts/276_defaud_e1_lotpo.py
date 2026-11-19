"""
DEFENSE AUDIT — FINAL ITEM 1: ESSAY 1 LEAVE-ONE-TREATED-PARENT-OUT (script 276). SUPPLEMENTARY ONLY.
==================================================================================================
Baseline specification, copied from scripts/158_rebuild_s8_regenerate.py (lines 52-76; 158 is never run):
  sample  = Data/processed/rebuild/CANONICAL_V3.csv, has_crsp_data == 1, complete on car_30d + CONTROLS
  model   = OLS car_30d ~ const + fcc_form499 + immediate_disclosure + prior_breaches_1yr + health_breach
            + firm_size_log + leverage + roa, cov_type='HC3'
  CI      = statsmodels conf_int() under HC3 (normal / z convention, as 158 and constants_v3.json H2_FCC_ci).
Assert first: the full-sample fcc_form499 coef, HC3 SE and p reproduce outputs/rebuild/appendix_v3/table_4.csv
and outputs/rebuild/constants_v3.json to 4 dp (N 340, 106 treated events, 12 treated parent CIKs); abort otherwise.

Deletion rule: for each treated parent CIK (final_cik, the Essay 1 parent identifier), drop ALL regression-sample
events of that final_cik (treated and untreated) and refit the same model with HC3.

Writes ONLY outputs/defense_audit/final/item1_e1_lotpo.csv and item1_e1_lotpo.log.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_audit/final')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


# ---------------- baseline sample and model, exactly as scripts/158 ----------------
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']
crsp = ev[ev['has_crsp_data'] == 1]
reg = crsp.dropna(subset=['car_30d'] + CONTROLS).copy()


def fit(d):
    m = sm.OLS(d['car_30d'], sm.add_constant(d[CONTROLS].astype(float))).fit(cov_type='HC3')
    ci = m.conf_int().loc[TREAT]
    return dict(coef=float(m.params[TREAT]), se_hc3=float(m.bse[TREAT]), p_hc3=float(m.pvalues[TREAT]),
                ci95_lo=float(ci[0]), ci95_hi=float(ci[1]), N=int(m.nobs), treated_events=int(d[TREAT].sum()),
                treated_parent_ciks=int(d.loc[d[TREAT] == 1, 'final_cik'].nunique()))


log('=' * 100)
log('SCRIPT 276 — Essay 1 leave-one-treated-parent-out. SUPPLEMENTARY ONLY (not a pre-specified test).')
log('Baseline: scripts/158 specification, OLS car_30d on fcc_form499 + 6 controls, HC3; 95% CI normal (z) '
    'convention as in 158 conf_int().')
log('=' * 100)

full = fit(reg)
t4 = pd.read_csv('outputs/rebuild/appendix_v3/table_4.csv').set_index('Variable').loc[TREAT]
c3 = json.load(open('outputs/rebuild/constants_v3.json', encoding='utf-8'))
checks = [(round(full['coef'], 4), float(t4['Coef'])), (round(full['se_hc3'], 4), float(t4['SE'])),
          (round(full['p_hc3'], 4), float(t4['p'])), (round(full['coef'], 4), c3['H2_FCC_coef']),
          (round(full['p_hc3'], 4), c3['H2_FCC_p']), (round(full['ci95_lo'], 4), c3['H2_FCC_ci'][0]),
          (round(full['ci95_hi'], 4), c3['H2_FCC_ci'][1]), (full['N'], c3['N_regression']),
          (full['treated_events'], c3['treated_regression']),
          (full['treated_parent_ciks'], c3['treated_parent_ciks_regression'])]
ok = all(abs(a - b) < 1e-9 for a, b in checks)
log(f"Reproduction assert: coef {full['coef']:+.6f} SE {full['se_hc3']:.6f} p {full['p_hc3']:.6f} "
    f"CI [{full['ci95_lo']:.4f}, {full['ci95_hi']:.4f}] N {full['N']} treated {full['treated_events']} "
    f"parents {full['treated_parent_ciks']} vs table_4.csv / constants_v3.json -> {'PASS' if ok else 'FAIL'}")
assert ok, f'reproduction assert failed: {checks}'

names = pd.read_csv('outputs/essay2_v5/parent_filer_names.csv', dtype=str).set_index('cik')['filer_name'].to_dict()
tpar = (reg[reg[TREAT] == 1].groupby('final_cik').size().sort_values(ascending=False, kind='stable'))
assert len(tpar) == 12
rows = [dict(deleted_parent='(none: full sample)', deleted_parent_cik='', name_source='', tmobile_flag='',
             events_removed=0, treated_events_removed=0, **full,
             source='scripts/276 refit of scripts/158 spec; asserted vs outputs/rebuild/appendix_v3/table_4.csv '
                    'row fcc_form499 and constants_v3.json H2_FCC_*')]
for cik in tpar.index:
    cik_s = str(int(cik))
    drop = reg['final_cik'] == cik
    r = fit(reg[~drop])
    nm = names.get(cik_s)
    src = 'outputs/essay2_v5/parent_filer_names.csv' if nm else 'CANONICAL_V3.csv org_name (most frequent)'
    if not nm:
        nm = reg.loc[drop, 'org_name'].mode().iloc[0]
    rows.append(dict(deleted_parent=nm, deleted_parent_cik=cik_s, name_source=src,
                     tmobile_flag='T-MOBILE' if cik_s == '1283699' else '',
                     events_removed=int(drop.sum()), treated_events_removed=int(reg.loc[drop, TREAT].sum()), **r,
                     source='scripts/276 refit of scripts/158 spec (Data/processed/rebuild/CANONICAL_V3.csv), '
                            f'dropping every regression-sample event with final_cik == {cik_s}'))

R = pd.DataFrame(rows)
OUT.mkdir(parents=True, exist_ok=True)
R.to_csv(OUT / 'item1_e1_lotpo.csv', index=False, lineterminator='\n')
show = R[['deleted_parent', 'deleted_parent_cik', 'events_removed', 'treated_events_removed', 'coef', 'se_hc3',
          'p_hc3', 'ci95_lo', 'ci95_hi', 'N', 'treated_events', 'tmobile_flag']]
log('\n' + show.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
d = R.iloc[1:]
log(f"\nRange of the coefficient across deletions: {d.coef.min():+.4f} to {d.coef.max():+.4f}; "
    f"min HC3 p {d.p_hc3.min():.4f}; deletions with p < .05: {(d.p_hc3 < .05).sum()} of {len(d)}")
(OUT / 'item1_e1_lotpo.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
