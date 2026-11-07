"""ESSAY 2 v5 — disclosure-delay tests with the v5 pre-window control.

New versions of scripts/164 (t16, t16b, t16c) and scripts/249 (delay ladder);
164 and 249 are not edited. The only change: the control `e2_pre_sd` (raw
log-return SD over [-25,-5]) is replaced by the v5 pre-window SD of
market-adjusted abnormal returns over [-60,-11] (scripts/264 event panel,
`prim_pre_sd`). The other controls are unchanged (ln assets, leverage, ROA,
health, prior events). Each specification is also run with the old control
as a BRIDGE row, which must reproduce t16 (CV1) and e2_delay_ladder (CV3)
before any v5 row is written.

  A. delay ~ Form 499 + controls, three outcomes (raw days, winsorized p99,
     log(1+delay)); full ladder (OLS, HC1, HC3, CV1, CV3, WCR, WCU, Webb) and
     MDE80; family A2-delay.
  B. the same on non-zero delays (raw days, log); CV1 and CV3; family A2-delay-nz.
  C. quantile regressions q = .10/.25/.50/.75/.90 (iid SEs, descriptive).
  D. distribution tests that use no controls (Brown-Forsythe, KS, log-rank),
     recomputed and printed for completeness; they cannot move.
Writes outputs/essay2_v5/v5_t17_delay.csv, v5_t17b_delay_nonzero.csv,
v5_t17c_delay_quantiles.csv, v5_t17d_delay_distribution_tests.csv,
constants_parts/271.json.
"""
import importlib.util as _ilu
import json
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
OLDC = ['e2_pre_sd', 'firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events']
NEWC = ['pre_sd'] + OLDC[1:]
fin = L.load_sample()
panel = pd.read_csv(OUT / 'v5_event_panel.csv')
assert (panel['final_cik'].values == fin['final_cik'].values).all()
fin['pre_sd'] = panel['prim_pre_sd'].values
fin['delay_log'] = np.log1p(fin['disclosure_delay_days'])
OUTCOMES = [('disclosure_delay_days', 'delay (raw days)'), ('delay_w', 'delay (winsorized p99)'),
            ('delay_log', 'log(1+delay)')]
t16 = pd.read_csv(L.T2 / 't16_delay_on_treatment.csv')
t16c = pd.read_csv(L.T2 / 't16c_delay_nonzero.csv')
t16b = pd.read_csv(L.T2 / 't16b_delay_quantiles.csv')
lad249 = pd.read_csv('outputs/defense_supplement/e2_delay_ladder.csv')
C, rows = {}, []

# ---------------- A. full sample, full ladder
for dv, lab in OUTCOMES:
    for ctl, cname in [(OLDC, 'BRIDGE old control e2_pre_sd'), (NEWC, 'v5 control pre_sd [-60,-11]')]:
        r = L.ladder(fin, dv, [TREAT] + ctl)
        if ctl is OLDC:      # gate: reproduce 164 t16 (CV1) and 249 (CV3)
            g = t16[t16['dv'] == lab].iloc[0]
            assert round(r['coef'], 3) == g['coef'] and round(r['se_cv1'], 3) == g['se'] \
                and round(r['p_cv1'], 4) == g['p'], (lab, r['coef'], r['se_cv1'], r['p_cv1'], g.to_dict())
            g3 = lad249[(lad249['outcome'] == lab) & (lad249['rung'] == 'CV3 jackknife')].iloc[0]
            assert round(r['se_cv3'], 4) == g3['se'] and round(r['p_cv3'], 4) == g3['p'], (lab, r['p_cv3'], g3['p'])
        for x in L.ladder_rows(r, f'{lab} | {cname}'):
            x.update(outcome=lab, control=cname, mde80_cv3=r['mde'])
            rows.append(x)
        if ctl is NEWC:
            k_ = dv.replace('disclosure_delay_days', 'raw').replace('delay_w', 'winsor').replace('delay_log', 'log')
            C.update({f'delay_{k_}_coef': r['coef'], f'delay_{k_}_se_cv3': r['se_cv3'],
                      f'delay_{k_}_p_cv3': r['p_cv3'], f'delay_{k_}_p_cv1': r['p_cv1'],
                      f'delay_{k_}_p_wcr': r['p_wcr'], f'delay_{k_}_mde80': r['mde']})
        else:
            k_ = dv.replace('disclosure_delay_days', 'raw').replace('delay_w', 'winsor').replace('delay_log', 'log')
            C.update({f'delay_{k_}_coef_oldctl': r['coef'], f'delay_{k_}_p_cv3_oldctl': r['p_cv3']})
A = pd.DataFrame(rows)
A.to_csv(OUT / 'v5_t17_delay.csv', index=False)
print('Gate PASS: old-control rows reproduce t16 (CV1) and e2_delay_ladder (CV3) for all three outcomes.')
print(A[A['rung'].str.startswith('CV3')][['outcome', 'control', 'coef', 'se', 'p', 'N']].round(4).to_string(index=False))
raw = sm.OLS(fin['disclosure_delay_days'], sm.add_constant(fin[[TREAT]].astype(float))).fit()
C['delay_raw_unadjusted_diff'] = float(raw.params[TREAT])

# ---------------- B. non-zero delays
nz = fin[fin['disclosure_delay_days'] > 0]
brows = []
for dv, lab in [('disclosure_delay_days', 'delay (raw days)'), ('delay_log', 'log(delay)')]:
    for ctl, cname in [(OLDC, 'BRIDGE old control'), (NEWC, 'v5 control')]:
        r = L.ladder(nz, dv, [TREAT] + ctl, full=False)
        if ctl is OLDC:
            g = t16c[t16c['dv'] == lab].iloc[0]
            assert round(r['coef'], 3) == g['coef'] and round(r['se_cv1'], 3) == g['se'], (lab, r['coef'], g.to_dict())
        brows.append(dict(outcome=lab, control=cname, coef=r['coef'], se_cv1=r['se_cv1'], p_cv1=r['p_cv1'],
                          se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], N=r['N'], n_treated=r['n_treated']))
Bt = pd.DataFrame(brows)
Bt.to_csv(OUT / 'v5_t17b_delay_nonzero.csv', index=False)
print(Bt.round(4).to_string(index=False))
for _, r in Bt[Bt['control'] == 'v5 control'].iterrows():
    k_ = 'raw' if 'raw' in r['outcome'] else 'log'
    C.update({f'delay_nz_{k_}_coef': r['coef'], f'delay_nz_{k_}_p_cv3': r['p_cv3']})

# ---------------- C. quantile regressions
qrows = []
for ctl, cname in [(OLDC, 'BRIDGE old control'), (NEWC, 'v5 control')]:
    Xq = sm.add_constant(fin[[TREAT] + ctl].astype(float))
    for q in [.10, .25, .50, .75, .90]:
        mq = sm.QuantReg(fin['disclosure_delay_days'].astype(float), Xq).fit(q=q)
        if ctl is OLDC:
            g = t16b[np.isclose(t16b['q'], q)].iloc[0]
            assert round(mq.params[TREAT], 3) == g['coef'], (q, mq.params[TREAT], g['coef'])
        qrows.append(dict(control=cname, q=q, coef=mq.params[TREAT], se=mq.bse[TREAT], p=mq.pvalues[TREAT]))
Q = pd.DataFrame(qrows)
Q.to_csv(OUT / 'v5_t17c_delay_quantiles.csv', index=False)
print(Q.round(3).to_string(index=False))
for _, r in Q[Q['control'] == 'v5 control'].iterrows():
    C[f'delay_q{int(round(r["q"] * 100))}_coef'] = r['coef']

# ---------------- D. control-free distribution tests (cannot move)
from lifelines.statistics import logrank_test  # noqa: E402

tt = fin.loc[fin[TREAT] == 1, 'disclosure_delay_days']
cc = fin.loc[fin[TREAT] == 0, 'disclosure_delay_days']
tn, cn = tt[tt > 0], cc[cc > 0]
lr = logrank_test(tn, cn, event_observed_A=np.ones(len(tn)), event_observed_B=np.ones(len(cn)))
D = pd.DataFrame([
    dict(test='Brown-Forsythe, all delays', stat=stats.levene(tt, cc, center='median')[0],
         p=stats.levene(tt, cc, center='median')[1], sd_treated=tt.std(), sd_control=cc.std()),
    dict(test='Brown-Forsythe, non-zero', stat=stats.levene(tn, cn, center='median')[0],
         p=stats.levene(tn, cn, center='median')[1], sd_treated=tn.std(), sd_control=cn.std()),
    dict(test='KS, non-zero', stat=stats.ks_2samp(tn, cn)[0], p=stats.ks_2samp(tn, cn)[1]),
    dict(test='log-rank, non-zero', stat=lr.test_statistic, p=lr.p_value),
    dict(test='zero-delay events', stat=int((tt == 0).sum() + (cc == 0).sum()),
         p=np.nan, sd_treated=int((tt == 0).sum()), sd_control=int((cc == 0).sum())),
])
D.to_csv(OUT / 'v5_t17d_delay_distribution_tests.csv', index=False)
print(D.round(4).to_string(index=False))
C.update(delay_bf_p=float(D.loc[0, 'p']), delay_sd_treated=float(tt.std()), delay_sd_control=float(cc.std()),
         delay_zero_events=int(D.loc[4, 'stat']), delay_zero_treated=int((tt == 0).sum()),
         delay_zero_control=int((cc == 0).sum()))
C['bh_families'] = {}
C['tests'] = {}   # the A2 families are carried by scripts/269 from the t53 ledger (same tests, new control)
(OUT / 'constants_parts' / '271.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
print('Saved v5_t17* + constants_parts/271.json')
