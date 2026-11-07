"""ESSAY 2 v5 — rest of results on the new outcome (committee item 7, except the
specification curve, which is scripts/266).

  A. Announcement-window test. Definition (unchanged from scripts/175, stated):
     elevation = SD(daily abnormal return, trading days [-4,+4]) minus
     SD(daily abnormal return, [-25,-5]) around the agency reporting date;
     treatment regression elev ~ Form 499 + baseline SD + delay_w + ln assets +
     leverage + ROA + health + prior events, CV3 on parent filer entity; BH
     within the pre-specified family of four (earnings elevation, breach
     elevation, contrast, treatment).
     v5 basis: market-adjusted simple abnormal returns (r - vwretd), 80% rule
     (8 of 9, 17 of 21 days). Bridge row: the committed definition (market
     model, beta on [-250,-46]) reproduced from t42 and gated against t50.
  B. Placebo dates, 200 draws, seed 499 (scripts/180 operative eligibility:
     >= 120 trading days from every breach notification of the security,
     >= 30 from every earnings date), for the primary outcome and the elevation.
  C. Earnings benchmark: the primary outcome and the elevation on the sample
     securities' quarterly earnings dates (Data/wrds/q6_rdq.csv).
  D. Size quartiles (ln total assets, t1 size_q) with treated events,
     organizations, parents; CV3 and HC3; BH within the family of four.
  E. Year / industry (2-digit SIC) / joint FE with effective samples.
  F. Leave-one-parent-out range, the two extreme parents named.
  G. Drop the 6 pre-rule events.  H. Cook's distance exclusion (D > 4/N).
Writes outputs/essay2_v5/v5_t09..t15 and constants_parts/265.json.
"""
import importlib.util as _ilu
import json
import math
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
OUT, TREAT, CTRL = L.OUT, L.TREAT, L.CONTROLS
C = {}
fin = L.load_sample()
panel = pd.read_csv(OUT / 'v5_event_panel.csv')
assert len(panel) == 333 and (panel['final_cik'].values == fin['final_cik'].values).all()
fin['dv'], fin['pre_sd'] = panel['prim_dv'].values, panel['prim_pre_sd'].values
R = L.ladder(fin, 'dv', L.XS4)
C0 = json.loads((OUT / 'constants_parts' / '264.json').read_text(encoding='utf-8'))
assert abs(R['coef'] - C0['primary_coef']) < 1e-12, 'panel and 264 constants disagree'
M = L.Market()
ANN, BASE = (-4, 4), (-25, -5)


def log(m=''):
    print(m)


# ------------------------------------------------------------ A. announcement
log('## A. Announcement-window test')
t42 = pd.read_csv(L.T2 / 't42_final_sample_with_repairs.csv', low_memory=False)
assert (t42['final_cik'].values == fin['final_cik'].values).all()
old = fin.copy()
old['elev'], old['base_sd'] = (t42['abn_ann'] - t42['abn_pre']).values, t42['abn_pre'].values
r_old = L.ladder(old, 'elev', [TREAT, 'base_sd'] + CTRL)
t50 = pd.read_csv(L.T2 / 't50_announcement_contrast.csv')
t50row = t50[t50['row'].str.contains('Form 499', na=False)].iloc[0]
assert round(r_old['coef'], 4) == round(float(t50row['coef']), 4), (r_old['coef'], t50row['coef'])
log(f'  gate: committed definition reproduces t50 ({r_old["coef"]:+.4f}, CV3 p {r_old["p_cv3"]:.4f}, '
    f'N {r_old["N"]}, G {r_old["G"]})')


def elev_at(permno, pos, bench='mkt_adj'):
    ar = M.abnormal(permno, pos, bench)
    a = M.window_sd(ar, pos, ANN)[0]
    b = M.window_sd(ar, pos, BASE)[0]
    return a - b, b


ev = []
for _, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['rdt'])
    ev.append(elev_at(r['permno'], pos) if pos is not None else (np.nan, np.nan))
new = fin.copy()
new['elev'] = [e[0] for e in ev]
new['base_sd'] = [e[1] for e in ev]
r_new = L.ladder(new, 'elev', [TREAT, 'base_sd'] + CTRL)
raw_gap = sm.OLS(new.dropna(subset=['elev'])['elev'],
                 sm.add_constant(new.dropna(subset=['elev'])[[TREAT]].astype(float))).fit(
    cov_type='cluster', cov_kwds={'groups': new.dropna(subset=['elev'])['final_cik']}, use_t=True)

# earnings side (scripts/175 mapping: ticker -> permno within the sample)
rdq = pd.read_csv('Data/wrds/q6_rdq.csv', low_memory=False)
rdq['rdq'] = pd.to_datetime(rdq['rdq'])
rdq = rdq[(rdq['rdq'] >= '2006-01-01') & (rdq['rdq'] <= '2024-12-31')]
t2p = fin.groupby('matched_ticker')['permno'].first().to_dict()
rdq['permno'] = rdq['tic'].map(t2p)
rdq = rdq.dropna(subset=['permno']).drop_duplicates(subset=['permno', 'rdq'])
rdq['permno'] = rdq['permno'].astype(int)
earn = []
for _, r in rdq.iterrows():
    pos = M.anchor(r['permno'], r['rdq'])
    if pos is None:
        continue
    ar = M.abnormal(r['permno'], pos)
    el = M.window_sd(ar, pos, ANN)[0] - M.window_sd(ar, pos, BASE)[0]
    dv = M.window_sd(ar, pos, L.POST_PRIMARY)[0] - M.window_sd(ar, pos, L.PRE_PRIMARY)[0]
    earn.append(dict(permno=r['permno'], elev=el, dv=dv))
EA = pd.DataFrame(earn)


def mean_cl(s, groups):
    d = pd.DataFrame(dict(y=s, g=groups)).dropna()
    f = sm.OLS(d['y'].astype(float), np.ones(len(d))).fit(
        cov_type='cluster', cov_kwds={'groups': d['g']}, use_t=True)
    return float(f.params.iloc[0]), float(f.bse.iloc[0]), float(f.pvalues.iloc[0]), len(d), d['g'].nunique()


e_m = mean_cl(EA['elev'], EA['permno'])
b_m = mean_cl(new['elev'], new['final_cik'])
stack = pd.concat([EA[['permno', 'elev']].assign(is_breach=0.0),
                   new[['permno', 'elev']].assign(is_breach=1.0)]).dropna()
fc = sm.OLS(stack['elev'], sm.add_constant(stack[['is_breach']])).fit(
    cov_type='cluster', cov_kwds={'groups': stack['permno']}, use_t=True)
fam = pd.DataFrame([
    dict(test='earnings elevation (mean)', coef=e_m[0], se=e_m[1], p=e_m[2], N=e_m[3],
         clusters=e_m[4], inference='CV1 by security'),
    dict(test='breach elevation (mean)', coef=b_m[0], se=b_m[1], p=b_m[2], N=b_m[3],
         clusters=b_m[4], inference='CV1 by parent filer entity'),
    dict(test='breach minus earnings (contrast)', coef=float(fc.params['is_breach']),
         se=float(fc.bse['is_breach']), p=float(fc.pvalues['is_breach']), N=int(fc.nobs),
         clusters=int(stack['permno'].nunique()), inference='CV1 by security'),
    dict(test='Form 499 on breach elevation (pre-specified)', coef=r_new['coef'],
         se=r_new['se_cv3'], p=r_new['p_cv3'], N=r_new['N'], clusters=r_new['G'],
         inference='CV3 by parent filer entity'),
])
fam['bh_adj_p'], fam['bh_reject_05'] = L.bh(fam['p'])
fam['basis'] = 'v5: market-adjusted simple returns'
oldrow = dict(test='BRIDGE: Form 499 on breach elevation, committed definition (market model)',
              coef=r_old['coef'], se=r_old['se_cv3'], p=r_old['p_cv3'], N=r_old['N'],
              clusters=r_old['G'], inference='CV3', basis='scripts/169/175 (t42), reproduces t50')
lad_new = pd.DataFrame(L.ladder_rows(r_new, 'announcement elevation, v5 basis'))
fam = pd.concat([fam, pd.DataFrame([oldrow])], ignore_index=True)
fam.to_csv(OUT / 'v5_t09_announcement.csv', index=False)
lad_new.to_csv(OUT / 'v5_t09b_announcement_ladder.csv', index=False)
tr_e = new.loc[new[TREAT] == 1, 'elev'].mean()
co_e = new.loc[new[TREAT] == 0, 'elev'].mean()
log(fam.round(4).to_string(index=False))
log(f'  raw gap (no controls) {raw_gap.params[TREAT]:+.4f} p {raw_gap.pvalues[TREAT]:.4f}; '
    f'treated elevation {tr_e:+.4f}, control {co_e:+.4f}; baseline SD treated '
    f'{new.loc[new[TREAT] == 1, "base_sd"].mean():.4f} vs control {new.loc[new[TREAT] == 0, "base_sd"].mean():.4f}; '
    f'corr(elev, base) {new[["elev", "base_sd"]].corr().iloc[0, 1]:+.4f}')
C.update(ann_coef=r_new['coef'], ann_se_cv3=r_new['se_cv3'], ann_p_cv3=r_new['p_cv3'],
         ann_p_wcr=r_new['p_wcr'], ann_N=r_new['N'], ann_G=r_new['G'], ann_G1=r_new['G1'],
         ann_bh_adj_p=float(fam.loc[3, 'bh_adj_p']), ann_bh_reject=bool(fam.loc[3, 'bh_reject_05']),
         ann_raw_gap=float(raw_gap.params[TREAT]), ann_raw_gap_p=float(raw_gap.pvalues[TREAT]),
         ann_treated_elev=float(tr_e), ann_control_elev=float(co_e),
         ann_base_treated=float(new.loc[new[TREAT] == 1, 'base_sd'].mean()),
         ann_base_control=float(new.loc[new[TREAT] == 0, 'base_sd'].mean()),
         ann_corr_elev_base=float(new[['elev', 'base_sd']].corr().iloc[0, 1]),
         ann_old_coef=r_old['coef'], ann_old_p_cv3=r_old['p_cv3'],
         earn_elev_mean=e_m[0], earn_elev_N=e_m[3], breach_elev_mean=b_m[0],
         contrast_coef=float(fc.params['is_breach']))

# Panel D: raw-to-adjusted buildup of the announcement differential (CV3 at
# every step; same estimation sample as the full model)
bu_specs = [('unadjusted (Form 499 only)', [TREAT]),
            ('+ baseline SD', [TREAT, 'base_sd']),
            ('+ baseline SD + ln assets', [TREAT, 'base_sd', 'firm_size_log']),
            ('full (pre-specified)', [TREAT, 'base_sd'] + CTRL)]
nb = new.dropna(subset=['elev', 'base_sd'] + CTRL)
bu = []
for lab, xs in bu_specs:
    r = L.ladder(nb, 'elev', xs, full=False)
    bu.append(dict(step=lab, coef=r['coef'], se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], N=r['N']))
bu = pd.DataFrame(bu)
span = bu.loc[3, 'coef'] - bu.loc[0, 'coef']
bu['share_of_movement'] = (bu['coef'] - bu.loc[0, 'coef']) / span
bu.to_csv(OUT / 'v5_t09c_announcement_buildup.csv', index=False)
log('\n## A-D. Buildup of the announcement differential (CV3):')
log(bu.round(4).to_string(index=False))
C.update(ann_raw_gap_cv3=float(bu.loc[0, 'coef']), ann_raw_gap_p_cv3=float(bu.loc[0, 'p_cv3']),
         ann_after_base_coef=float(bu.loc[1, 'coef']), ann_after_base_size_coef=float(bu.loc[2, 'coef']),
         ann_share_closed_base=float(bu.loc[1, 'share_of_movement']),
         ann_share_closed_base_size=float(bu.loc[2, 'share_of_movement']))

# ------------------------------------------------------------ C. earnings benchmark (primary DV)
eb = mean_cl(EA['dv'], EA['permno'])
pd.DataFrame([dict(outcome='primary DV on earnings dates', mean=eb[0], se=eb[1], p=eb[2],
                   N_announcements=eb[3], securities=eb[4]),
              dict(outcome='elevation on earnings dates', mean=e_m[0], se=e_m[1], p=e_m[2],
                   N_announcements=e_m[3], securities=e_m[4]),
              dict(outcome='primary DV on breach dates (sample mean)', mean=float(fin['dv'].mean()),
                   se=np.nan, p=np.nan, N_announcements=333, securities=fin['permno'].nunique())]
             ).to_csv(OUT / 'v5_t10_earnings_benchmark.csv', index=False)
log(f'\n## C. Earnings benchmark: primary DV {eb[0]:+.4f} (SE {eb[1]:.4f}, N {eb[3]}); '
    f'elevation {e_m[0]:+.4f}')
C.update(earn_dv_mean=eb[0], earn_dv_se=eb[1], earn_dv_N=eb[3], breach_dv_mean=float(fin['dv'].mean()))

# ------------------------------------------------------------ B. placebo dates
can = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
can = can.dropna(subset=['permno'])
notif = {}
for _, r in can.iterrows():
    notif.setdefault(int(r['permno']), []).append(pd.Timestamp(r['reported_date']))
earnd = {p: list(g['rdq']) for p, g in rdq.groupby('permno')}
ncal = len(M.dates)


def cal_pos(dt):
    return int(np.argmin(np.abs(M.dates - np.datetime64(dt))))


elig = {}
for p in fin['permno'].unique():
    ok = np.zeros(ncal, bool)
    ok[60:ncal - 20] = True
    ok &= np.isfinite(M.R[p])
    for dt in notif.get(p, []):
        i = cal_pos(dt)
        ok[max(0, i - 120):i + 121] = False
    for dt in earnd.get(p, []):
        i = cal_pos(dt)
        ok[max(0, i - 30):i + 31] = False
    elig[p] = np.flatnonzero(ok)
no_elig = [p for p, v in elig.items() if not len(v)]
T_mask = (fin[TREAT] == 1).to_numpy()
rng = np.random.default_rng(L.SEED)
B = 200
pl = []
cache = {}
for b_ in range(B):
    dvs, pres, els, bases = [], [], [], []
    for p in fin['permno']:
        e_ = elig[p]
        if not len(e_):
            dvs.append(np.nan); pres.append(np.nan); els.append(np.nan); bases.append(np.nan)
            continue
        pos = int(rng.choice(e_))
        if (p, pos) not in cache:
            ar = M.abnormal(p, pos)
            a, b = M.window_sd(ar, pos, L.PRE_PRIMARY)[0], M.window_sd(ar, pos, L.POST_PRIMARY)[0]
            x, y = M.window_sd(ar, pos, ANN)[0], M.window_sd(ar, pos, BASE)[0]
            cache[(p, pos)] = (b - a, a, x - y, y)
        v = cache[(p, pos)]
        dvs.append(v[0]); pres.append(v[1]); els.append(v[2]); bases.append(v[3])
    d = fin.copy()
    d['dv'], d['pre_sd'], d['elev'], d['base_sd'] = dvs, pres, els, bases
    r1 = L.ladder(d, 'dv', L.XS4, full=False)
    r2 = L.ladder(d, 'elev', [TREAT, 'base_sd'] + CTRL, full=False)
    pl.append(dict(draw=b_, dv_coef=r1['coef'], dv_p_cv3=r1['p_cv3'], dv_N=r1['N'],
                   dv_mean=float(np.nanmean(dvs)), elev_coef=r2['coef'], elev_p_cv3=r2['p_cv3'],
                   elev_mean=float(np.nanmean(els)),
                   elev_mean_treated=float(np.nanmean(np.array(els)[T_mask])),
                   elev_mean_control=float(np.nanmean(np.array(els)[~T_mask]))))
pl = pd.DataFrame(pl)
pl.to_csv(OUT / 'v5_t11_placebo_draws.csv', index=False)
summ = pd.DataFrame([
    dict(outcome='primary DV', actual=R['coef'], placebo_mean=pl['dv_coef'].mean(),
         placebo_sd=pl['dv_coef'].std(ddof=1),
         draws_abs_ge_actual=int((pl['dv_coef'].abs() >= abs(R['coef'])).sum()),
         draws_cv3_p_lt_05=int((pl['dv_p_cv3'] < .05).sum()), draws=B,
         mean_N=pl['dv_N'].mean(), securities_without_eligible_dates=len(no_elig)),
    dict(outcome='announcement elevation', actual=r_new['coef'], placebo_mean=pl['elev_coef'].mean(),
         placebo_sd=pl['elev_coef'].std(ddof=1),
         draws_abs_ge_actual=int((pl['elev_coef'].abs() >= abs(r_new['coef'])).sum()),
         draws_cv3_p_lt_05=int((pl['elev_p_cv3'] < .05).sum()), draws=B,
         mean_N=np.nan, securities_without_eligible_dates=len(no_elig),
         placebo_level_mean=pl['elev_mean'].mean())])
summ.to_csv(OUT / 'v5_t11_placebo.csv', index=False)
log('\n## B. Placebo dates (200 draws, seed 499):')
log(summ.round(4).to_string(index=False))
C.update(placebo_dv_mean=float(summ.loc[0, 'placebo_mean']),
         placebo_dv_ge_actual=int(summ.loc[0, 'draws_abs_ge_actual']),
         placebo_dv_rejects=int(summ.loc[0, 'draws_cv3_p_lt_05']),
         placebo_elev_mean=float(summ.loc[1, 'placebo_mean']),
         placebo_elev_ge_actual=int(summ.loc[1, 'draws_abs_ge_actual']),
         placebo_elev_rejects=int(summ.loc[1, 'draws_cv3_p_lt_05']),
         placebo_elev_level_mean=float(summ.loc[1, 'placebo_level_mean']),
         placebo_elev_level_treated=float(pl['elev_mean_treated'].mean()),
         placebo_elev_level_control=float(pl['elev_mean_control'].mean()),
         # breach-date elevation minus the same group's quiet-day (placebo) level:
         # where the differential lives
         ann_treated_minus_quiet=float(tr_e - pl['elev_mean_treated'].mean()),
         ann_control_minus_quiet=float(co_e - pl['elev_mean_control'].mean()))
log(f'  side of the differential: treated breach {tr_e:+.4f} vs own quiet days '
    f'{pl["elev_mean_treated"].mean():+.4f} (diff {tr_e - pl["elev_mean_treated"].mean():+.4f}); '
    f'control breach {co_e:+.4f} vs own quiet days {pl["elev_mean_control"].mean():+.4f} '
    f'(diff {co_e - pl["elev_mean_control"].mean():+.4f})')

# ------------------------------------------------------------ D. size quartiles
qrows = []
for q in sorted(fin['size_q'].unique()):
    d = fin[fin['size_q'] == q]
    r = L.ladder(d, 'dv', L.XS4, full=False)
    sd_c = float(d.loc[d[TREAT] == 0, 'dv'].std())
    qrows.append(dict(quartile=q, N=r['N'], treated_events=int(d[TREAT].sum()),
                      treated_orgs=int(d.loc[d[TREAT] == 1, 'org_name'].nunique()),
                      treated_parents=r['G1'], G=r['G'], coef=r['coef'], se_cv3=r['se_cv3'],
                      p_cv3=r['p_cv3'], se_hc3=r['se_hc3'], p_hc3=r['p_hc3'],
                      mde80_cv3=r['mde'], mde_over_full_sesoi=r['mde'] / C0['dr_sesoi_daily'],
                      ci3_lo=r['ci3_lo'], ci3_hi=r['ci3_hi'], sd_control_cell=sd_c,
                      dropped_constant=r['dropped_constant']))
qt = pd.DataFrame(qrows)
qt['bh_adj_p_cv3'], qt['bh_reject_cv3'] = L.bh(qt['p_cv3'])
qt['bh_adj_p_hc3'], qt['bh_reject_hc3'] = L.bh(qt['p_hc3'])
qt.to_csv(OUT / 'v5_t12_size_quartiles.csv', index=False)
log('\n## D. Size quartiles (BH family of 4):')
log(qt.round(4).to_string(index=False))
for _, r in qt.iterrows():
    k_ = r['quartile'].split()[0]
    C.update({f'q_{k_}_coef': r['coef'], f'q_{k_}_p_cv3': r['p_cv3'], f'q_{k_}_p_hc3': r['p_hc3'],
              f'q_{k_}_bh_p': r['bh_adj_p_cv3'], f'q_{k_}_treated': int(r['treated_events']),
              f'q_{k_}_parents': int(r['treated_parents']), f'q_{k_}_mde': r['mde80_cv3']})

# ------------------------------------------------------------ E. fixed effects
fe_rows = []
d = fin.copy()
d['sic2i'] = d['sic2'].astype(int)
d['cell'] = d['year'].astype(str) + '_' + d['sic2i'].astype(str)
for lab, cols in [('year FE', ['year']), ('industry FE (2-digit SIC)', ['sic2i']),
                  ('year + industry FE', ['year', 'sic2i'])]:
    dd = d.copy()
    # singleton strata are fit exactly by their own dummy (leverage 1): they do
    # not move the coefficient and make HC3 undefined, so they are dropped first
    # (iterated until none remain), and counted
    n0 = len(dd)
    while True:
        single = np.zeros(len(dd), bool)
        for c in cols:
            single |= dd.groupby(c)[c].transform('size').to_numpy() == 1
        if not single.any():
            break
        dd = dd[~single]
    dums = pd.get_dummies(dd[cols].astype(str), drop_first=True, dtype=float)
    xs = L.XS4 + list(dums.columns)
    dd = pd.concat([dd, dums], axis=1)
    r = L.ladder(dd, 'dv', xs, full=False)
    singletons = n0 - len(dd)
    eff = []
    for c in cols + (['cell'] if len(cols) == 2 else []):
        mixed = d.groupby(c)[TREAT].agg(lambda s: s.nunique() == 2)
        eff.append((c, int(mixed.sum()), int(len(mixed)),
                    int(d[c].isin(mixed[mixed].index).sum()),
                    int(d.loc[d[c].isin(mixed[mixed].index), TREAT].sum())))
    e = eff[-1]
    fe_rows.append(dict(spec=lab, coef=r['coef'], se_cv3=r['se_cv3'], p_cv3=r['p_cv3'],
                        se_hc3=r['se_hc3'], p_hc3=r['p_hc3'], N=r['N'],
                        mixed_strata=e[1], strata=e[2], effective_obs=e[3], effective_treated=e[4],
                        stratum=e[0], singletons_dropped=singletons))
fe = pd.DataFrame(fe_rows)
fe.to_csv(OUT / 'v5_t13_fixed_effects.csv', index=False)
log('\n## E. Fixed effects:')
log(fe.round(4).to_string(index=False))
for i, r in fe.iterrows():
    k_ = ['year', 'ind', 'both'][i]
    C.update({f'fe_{k_}_coef': r['coef'], f'fe_{k_}_p_cv3': r['p_cv3'], f'fe_{k_}_p_hc3': r['p_hc3'],
              f'fe_{k_}_mixed': int(r['mixed_strata']), f'fe_{k_}_strata': int(r['strata']),
              f'fe_{k_}_eff_obs': int(r['effective_obs']), f'fe_{k_}_eff_treated': int(r['effective_treated'])})

# ------------------------------------------------------------ F/G/H. influence
jk = R['jack_coefs']
names = fin.groupby('final_cik')['org_name'].agg(lambda s: s.value_counts().index[0])
sizes = fin.groupby('final_cik').size()
lo_c, hi_c = jk.idxmin(), jk.idxmax()
sprint_share = 1 - jk.loc[101830] / R['coef']
pre_mask = pd.to_datetime(fin['reported_date']) < '2007-12-08'
assert pre_mask.sum() == 6 and fin.loc[pre_mask, TREAT].sum() == 0
r_pre = L.ladder(fin[~pre_mask], 'dv', L.XS4, full=False)
dd = fin.dropna(subset=['dv'] + L.XS4)
fo = sm.OLS(dd['dv'], sm.add_constant(dd[L.XS4].astype(float))).fit()
cook = fo.get_influence().cooks_distance[0]
keep = cook <= 4 / len(dd)
r_cook = L.ladder(dd[keep], 'dv', L.XS4, full=False)
infl = pd.DataFrame([
    dict(check='full sample (PRIMARY)', coef=R['coef'], se_cv3=R['se_cv3'], p_cv3=R['p_cv3'], N=R['N']),
    dict(check='leave-one-parent-out minimum', coef=float(jk.min()), N=int(R['N'] - sizes[lo_c]),
         detail=f'dropping {names[lo_c]} (final_cik {lo_c}, {sizes[lo_c]} events)'),
    dict(check='leave-one-parent-out maximum', coef=float(jk.max()), N=int(R['N'] - sizes[hi_c]),
         detail=f'dropping {names[hi_c]} (final_cik {hi_c}, {sizes[hi_c]} events)'),
    dict(check='share of estimate removed by deleting Sprint (101830)', coef=float(sprint_share)),
    dict(check='drop 6 pre-rule events (reported before 2007-12-08; all control)', coef=r_pre['coef'],
         se_cv3=r_pre['se_cv3'], p_cv3=r_pre['p_cv3'], N=r_pre['N'],
         detail=f'shift {(r_pre["coef"] - R["coef"]) / R["se_cv3"]:+.3f} CV3 SEs'),
    dict(check="Cook's distance exclusion (D > 4/N)", coef=r_cook['coef'], se_cv3=r_cook['se_cv3'],
         p_cv3=r_cook['p_cv3'], N=r_cook['N'], detail=f'removed {int((~keep).sum())}; HC3 p {r_cook["p_hc3"]:.4f}'),
])
infl.to_csv(OUT / 'v5_t14_influence.csv', index=False)
pd.DataFrame(dict(final_cik=jk.index, parent=names.reindex(jk.index).values,
                  events=sizes.reindex(jk.index).values, coef_without=jk.values)
             ).sort_values('coef_without').to_csv(OUT / 'v5_t14b_leave_one_parent_out.csv', index=False)
log('\n## F-H. Influence:')
log(infl.round(4).to_string(index=False))
C.update(lopo_min=float(jk.min()), lopo_min_parent=names[lo_c], lopo_max=float(jk.max()),
         lopo_max_parent=names[hi_c], sprint_share_removed=float(sprint_share),
         prerule_coef=r_pre['coef'], prerule_p_cv3=r_pre['p_cv3'],
         cook_coef=r_cook['coef'], cook_p_cv3=r_cook['p_cv3'], cook_removed=int((~keep).sum()))
C['bh_families'] = {'announcement_window': 4, 'size_quartiles': 4}
C['tests'] = {'announcement family': 4, 'size quartiles': 4, 'fixed effects': 3,
              'pre-rule exclusion': 1, "Cook's exclusion": 1}
(L.OUT / 'constants_parts' / '265.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
log('\nSaved v5_t09..t14 + constants_parts/265.json')
