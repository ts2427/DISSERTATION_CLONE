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

# R1-R14: descriptives of the primary outcome and its two windows
def welch(col):
    a = fin.loc[fin[TREAT] == 1, col].dropna()
    b_ = fin.loc[fin[TREAT] == 0, col].dropna()
    t, p = stats.ttest_ind(a, b_, equal_var=False)
    va, vb = a.var(ddof=1) / len(a), b_.var(ddof=1) / len(b_)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b_) - 1))
    return a, b_, float(a.mean() - b_.mean()), float(df), float(t), float(p)


fin['post_sd'] = panel['prim_post_sd'].values
a, b_, gap, dfw, tw, pw = welch('dv')
_, _, gpre, _, _, ppre = welch('pre_sd')
_, _, gpost, _, _, ppost = welch('post_sd')
C.update(dv_mean_all=float(fin['dv'].mean()), dv_sd_all=float(fin['dv'].std(ddof=1)),
         dv_mean_treated=float(a.mean()), dv_sd_treated=float(a.std(ddof=1)),
         dv_mean_control=float(b_.mean()), dv_sd_control=float(b_.std(ddof=1)),
         dv_welch_gap=gap, dv_welch_df=dfw, dv_welch_t=tw, dv_welch_p=pw,
         pre_sd_gap=gpre, pre_sd_gap_p=ppre, post_sd_gap=gpost, post_sd_gap_p=ppost)
rows.append(dict(item='R1-R14 descriptives (treated minus control; Welch)', value=gap,
                 detail=f'df {dfw:.2f}, t {tw:.3f}, p {pw:.4f}; pre-SD gap {gpre:+.4f} (p {ppre:.4f}); '
                        f'post-SD gap {gpost:+.4f} (p {ppost:.4f})'))

# R15-R17: M3 CV3 p (264 key M3_p_cv3) and M4 R-squared without / with treatment
xs_no_t = [c for c in L.XS4 if c != TREAT]
dd = fin.dropna(subset=['dv'] + L.XS4)
r2_without = float(sm.OLS(dd['dv'], sm.add_constant(dd[xs_no_t].astype(float))).fit().rsquared)
r2_with = float(sm.OLS(dd['dv'], sm.add_constant(dd[L.XS4].astype(float))).fit().rsquared)
assert abs(r2_with - C0['primary_r2_M4']) < 1e-12
C.update(M3_p_cv3_check=C0['M3_p_cv3'], r2_M4_without_treatment=r2_without, r2_M4_with_treatment=r2_with)
rows.append(dict(item='R-squared, M4 without / with Form 499', value=r2_with, detail=f'without {r2_without:.4f}'))

# R18: announcement sensitivities (scripts/176 specifications) on the v5 construction:
# elevation = SD(market-adjusted AR, [-4,+4]) - SD([-25,-5]); base = scripts/265 model
C5 = json.loads((OUT / 'constants_parts' / '265.json').read_text(encoding='utf-8'))
el, base = [], []
for _, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['rdt'])
    ar = M.abnormal(r['permno'], pos) if pos is not None else None
    x = M.window_sd(ar, pos, (-4, 4))[0] if ar is not None else np.nan
    y = M.window_sd(ar, pos, (-25, -5))[0] if ar is not None else np.nan
    el.append(x - y)
    base.append(y)
e = fin.copy()
e['elev'], e['base_sd'] = el, base
CTRL = L.CONTROLS
e = e.dropna(subset=['elev', 'base_sd'] + CTRL).reset_index(drop=True)
e['recs'] = pd.to_numeric(e['total_affected_max'], errors='coerce')
e['ln_recs'] = np.log1p(e['recs'].clip(upper=e['recs'].quantile(.99)))
e['ln_recs'] = e['ln_recs'].fillna(e['ln_recs'].median())
e['recs_missing'] = e['recs'].isna().astype(float)
e['size2'] = e['firm_size_log'] ** 2
vec = pd.get_dummies(e['breach_type'].astype(str).str.split('+').str[0], prefix='v', drop_first=True, dtype=float)
szq = pd.get_dummies(pd.qcut(e['firm_size_log'], 4, labels=False), prefix='szq', drop_first=True, dtype=float)
e = pd.concat([e, vec, szq], axis=1)
lo_s, hi_s = e.loc[e[TREAT] == 1, 'firm_size_log'].agg(['min', 'max'])
sens = []
for lab, extra, data in [
        ('base (scripts/265)', [], e),
        ('+ severity (ln records + vector FE)', ['ln_recs', 'recs_missing'] + list(vec.columns), e),
        ('+ flexible size (quartile FE + size^2)', ['size2'] + list(szq.columns), e),
        ('+ severity and flexible size', ['ln_recs', 'recs_missing', 'size2'] + list(vec.columns) + list(szq.columns), e),
        ('common support (controls in treated size range)', [],
         e[(e['firm_size_log'] >= lo_s) & (e['firm_size_log'] <= hi_s)])]:
    r = L.ladder(data, 'elev', [TREAT, 'base_sd'] + CTRL + extra, full=False)
    sens.append(dict(spec=lab, coef=r['coef'], se_cv1=r['se_cv1'], p_cv1=r['p_cv1'],
                     se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], N=r['N'], n_treated=r['n_treated'],
                     dropped_constant=r['dropped_constant']))
sens = pd.DataFrame(sens)
assert abs(sens.loc[0, 'coef'] - C5['ann_coef']) < 1e-10, 'announcement base differs from scripts/265'
sens.to_csv(OUT / 'v5_t18b_announcement_sensitivities.csv', index=False)
print(sens.round(4).to_string(index=False))
s4 = sens.iloc[1:]
C.update(ann_sens_min=float(s4['coef'].min()), ann_sens_max=float(s4['coef'].max()),
         ann_sens_max_p_cv3=float(s4['p_cv3'].max()), ann_sens_max_p_cv1=float(s4['p_cv1'].max()),
         **{f'ann_sens_{i}_coef': float(r['coef']) for i, r in s4.iterrows()},
         **{f'ann_sens_{i}_p_cv3': float(r['p_cv3']) for i, r in s4.iterrows()})

# R19-R23: size-quartile MDE range against the full-sample SESOI; smallest BH-adjusted CV3 p
qt = pd.read_csv(OUT / 'v5_t12_size_quartiles.csv')
sesoi = C0['dr_sesoi_daily']
C.update(q_mde_min=float(qt['mde80_cv3'].min()), q_mde_max=float(qt['mde80_cv3'].max()),
         q_mde_min_x_sesoi=float(qt['mde80_cv3'].min() / sesoi),
         q_mde_max_x_sesoi=float(qt['mde80_cv3'].max() / sesoi),
         q_min_bh_p_cv3=float(qt['bh_adj_p_cv3'].min()))
# per-cell Rainey 90% CI (CV3, t with df = cell G - 1) against the full-sample SESOI
qrows = []
for _, r in qt.iterrows():
    t95 = stats.t.ppf(0.95, int(r['G']) - 1)
    lo, hi = r['coef'] - t95 * r['se_cv3'], r['coef'] + t95 * r['se_cv3']
    inside = bool(lo > -sesoi and hi < sesoi)
    k_ = r['quartile'].split()[0]
    C.update({f'q_{k_}_ci90_lo': float(lo), f'q_{k_}_ci90_hi': float(hi), f'q_{k_}_ci90_inside_sesoi': inside})
    qrows.append(dict(quartile=r['quartile'], coef=r['coef'], se_cv3=r['se_cv3'], df=int(r['G']) - 1,
                      ci90_lo=lo, ci90_hi=hi, sesoi=sesoi, inside_sesoi=inside))
qci = pd.DataFrame(qrows)
qci.to_csv(OUT / 'v5_t18c_quartile_ci90.csv', index=False)
print(qci.round(4).to_string(index=False))
C['q_cells_negligible'] = int(qci['inside_sesoi'].sum())

# specification curve: significance counts under CV3 and CV1 (any sign), from 266's table
sc = pd.read_csv(OUT / 'v5_t15_spec_curve.csv')
C.update(spec_sig_cv3_any=int((sc['p_cv3'] < .05).sum()), spec_sig_cv1_any=int((sc['p_cv1'] < .05).sum()),
         spec_n_check=len(sc))
print(f'spec curve: {len(sc)} specs; p<.05 under CV3 {C["spec_sig_cv3_any"]}, under CV1 {C["spec_sig_cv1_any"]}; '
      f'min p CV3 {sc["p_cv3"].min():.4f}, min p CV1 {sc["p_cv1"].min():.4f}')
C.update(spec_min_p_cv3=float(sc['p_cv3'].min()), spec_min_p_cv1=float(sc['p_cv1'].min()))

pd.DataFrame(rows).to_csv(OUT / 'v5_t18_supplement.csv', index=False)
print(pd.DataFrame(rows).to_string(index=False))
C['bh_families'], C['tests'] = {}, {}
(OUT / 'constants_parts' / '272.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
print('Saved v5_t18_supplement.csv + constants_parts/272.json')
