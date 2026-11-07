"""ESSAY 2 v5 — supplementary constants requested before commit.

  1. Anchor check: the primary outcome re-anchored on the BREACH date (same
     windows [-60,-11] / [+1,+20], same market-adjusted benchmark, same 80%
     rule); its correlation with the primary (reporting-date) outcome; and
     the share of breach-anchored post-window days that fall before the
     reporting date (pooled over event-days, and by treated / control).
  2. HC3-based MDE80 for the primary model, using scripts/165's convention
     (2.8 x HC3 SE), and its percent shortfall from the CV3 MDE80
     (100 x (1 - SE_HC3 / SE_CV3), as 165 prints it).
  3. The converted announcement-return equivalence bound (scripts/165
     EQ_CAR = 2.10 pp annualized = 2.10 / sqrt(252) daily): TOST on the new
     outcome with CV3, both one-sided p-values. Not retired: 165 still
     computes it; it is the non-native second threshold.
  4. Primary model with standard errors clustered by two-digit SIC (CV1, as
     in scripts/163, and CV3 for comparison): SE, p, number of clusters.
  5. The number of permutation draws used by scripts/266 (read from its output).
Writes outputs/essay2_v5/v5_t18_supplement.csv and constants_parts/272.json.
"""
import importlib.util as _ilu
import json
import math
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
OUT, TREAT = L.OUT, L.TREAT
fin = L.load_sample()
panel = pd.read_csv(OUT / 'v5_event_panel.csv')
assert (panel['final_cik'].values == fin['final_cik'].values).all()
fin['dv'], fin['pre_sd'] = panel['prim_dv'].values, panel['prim_pre_sd'].values
C0 = json.loads((OUT / 'constants_parts' / '264.json').read_text(encoding='utf-8'))
R = L.ladder(fin, 'dv', L.XS4)
assert abs(R['coef'] - C0['primary_coef']) < 1e-12
C, rows = {}, []

# 1. breach-date anchor
M = L.Market(permnos=fin['permno'].unique())
fin['bdt'] = pd.to_datetime(fin['breach_date'])
ob = L.build_dv(fin, M, L.PRE_PRIMARY, L.POST_PRIMARY, date_col='bdt')
both = pd.DataFrame(dict(rep=fin['dv'], br=ob['dv'])).dropna()
corr = float(both.corr().iloc[0, 1])
before, total = {0: 0, 1: 0}, {0: 0, 1: 0}
for _, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['bdt'])
    if pos is None:
        continue
    days = M.dates[pos + L.POST_PRIMARY[0]:pos + L.POST_PRIMARY[1] + 1]
    t = int(r[TREAT])
    before[t] += int((days < np.datetime64(r['rdt'])).sum())
    total[t] += len(days)
share = {g: before[g] / total[g] for g in (0, 1)}
share_all = (before[0] + before[1]) / (total[0] + total[1])
C.update(breach_anchor_corr=corr, breach_anchor_N=len(both),
         breach_anchor_dropped=int(ob['dv'].isna().sum()),
         breach_post_days_before_report_share=share_all,
         breach_post_days_before_report_share_treated=share[1],
         breach_post_days_before_report_share_control=share[0])
rows += [dict(item='corr(primary, breach-anchored primary)', value=corr, detail=f'N {len(both)}'),
         dict(item='share of breach-anchored post-window days before the reporting date (pooled)',
              value=share_all, detail=f'{before[0] + before[1]} of {total[0] + total[1]} event-days'),
         dict(item='... treated', value=share[1], detail=f'{before[1]} of {total[1]}'),
         dict(item='... control', value=share[0], detail=f'{before[0]} of {total[0]}')]

# 2. HC3-based MDE (165 convention)
mde_hc3 = 2.8 * R['se_hc3']
pct = 100 * (1 - R['se_hc3'] / R['se_cv3'])
C.update(mde80_hc3_daily=mde_hc3, mde80_hc3_ann=mde_hc3 * math.sqrt(252),
         mde80_hc3_pct_below_cv3=pct)
rows += [dict(item='MDE80, HC3 (2.8 x SE_HC3; scripts/165 convention)', value=mde_hc3,
              detail=f'{mde_hc3 * math.sqrt(252):.2f} annualized; CV3 MDE80 {R["mde"]:.4f}'),
         dict(item='HC3 MDE shortfall vs CV3 (percent)', value=pct, detail='100 x (1 - SE_HC3/SE_CV3)')]

# 3. converted announcement-return bound
EQ = 2.10 / math.sqrt(252)
b, se, G = R['coef'], R['se_cv3'], R['G']
p_lo = float(1 - stats.t.cdf((b + EQ) / se, G - 1))
p_hi = float(stats.t.cdf((b - EQ) / se, G - 1))
C.update(sesoi_car_daily=EQ, sesoi_car_ann=2.10, tost_car_p_lower=p_lo, tost_car_p_upper=p_hi,
         tost_car_p=max(p_lo, p_hi))
rows += [dict(item='converted CAR bound (daily pp)', value=EQ, detail='2.10 pp annualized (scripts/165 EQ_CAR)'),
         dict(item='TOST vs CAR bound, lower one-sided p (CV3)', value=p_lo),
         dict(item='TOST vs CAR bound, upper one-sided p (CV3)', value=p_hi)]

# 4. clustered by two-digit SIC
d = fin.dropna(subset=['dv'] + L.XS4)
f = sm.OLS(d['dv'], sm.add_constant(d[L.XS4].astype(float))).fit(
    cov_type='cluster', cov_kwds={'groups': d['sic2'].astype(int)}, use_t=True)
r_sic = L.ladder(d.assign(sic2c=d['sic2'].astype(int)), 'dv', L.XS4, cluster='sic2c', full=False)
assert np.isclose(r_sic['se_cv1'], f.bse[TREAT])
C.update(sic2_cluster_se_cv1=float(f.bse[TREAT]), sic2_cluster_p_cv1=float(f.pvalues[TREAT]),
         sic2_cluster_se_cv3=r_sic['se_cv3'], sic2_cluster_p_cv3=r_sic['p_cv3'],
         sic2_clusters=int(d['sic2'].nunique()))
rows += [dict(item='SE clustered by 2-digit SIC (CV1)', value=float(f.bse[TREAT]),
              detail=f'p {f.pvalues[TREAT]:.4f}; {d["sic2"].nunique()} clusters; t(G-1)'),
         dict(item='SE clustered by 2-digit SIC (CV3)', value=r_sic['se_cv3'], detail=f'p {r_sic["p_cv3"]:.4f}')]

# 5. permutation draws in scripts/266
perm = pd.read_csv(OUT / 'v5_t15b_spec_curve_permutation.csv')
assert perm['draws'].nunique() == 1
C['spec_perm_draws'] = int(perm['draws'].iloc[0])
rows.append(dict(item='specification-curve permutation draws (scripts/266)', value=C['spec_perm_draws'],
                 detail='parent-level, 12 of 82 treated, seed 499'))

pd.DataFrame(rows).to_csv(OUT / 'v5_t18_supplement.csv', index=False)
print(pd.DataFrame(rows).to_string(index=False))
C['bh_families'], C['tests'] = {}, {}
(OUT / 'constants_parts' / '272.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
print('Saved v5_t18_supplement.csv + constants_parts/272.json')
