"""
REBUILD DIRECTIVE v2 — STAGE 8: FULL REGENERATION + CONSTANTS BLOCK v3
=======================================================================
All three essays re-estimated on CANONICAL_V3 under the frozen specifications:
  Essay 1: car_30d ~ fcc_form499 + immediate_disclosure + prior_breaches_1yr +
           health_breach + firm_size_log + leverage + roa (HC3); TOST +/-2.10pp
           (bound fixed from literature BEFORE rebuilt estimates existed); MDE.
  Essay 2: volatility_change ~ same + return_volatility_pre (HC3); TOST.
  Essay 3: logit executive_change_{30,90,180}d ~ same; AME + MDE + base rates.
ROA AMENDMENT (pre-registered 8/4, outputs/rebuild/DIRECTIVE_AMENDMENT_ROA.md):
  ROA rows in restrictions/SE/factor tables; ONE op-margin spec + ONE both-
  included spec (op_margin is OIBDP-based — oiadp absent from extract, documented).
Appendix v3: the fourteen-table set regenerated on V3 (Table 9 severity-only —
  the HHI enrichment was retired with the pre-audit chain).
ASSERTION BASELINE: first run writes outputs/rebuild/constants_v3.json; every
  later run asserts against it (assert new values, never loosen).

Outputs: outputs/rebuild/CONSTANTS_BLOCK_V3.md, constants_v3.json,
         outputs/rebuild/appendix_v3/table_{1..14}.csv
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild')
APP = OUT / 'appendix_v3'
APP.mkdir(exist_ok=True)
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('REBUILD STAGE 8: FULL REGENERATION')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']
C = {}  # constants

# ---------------- samples ----------------
crsp = ev[ev['has_crsp_data'] == 1]
reg = crsp.dropna(subset=['car_30d'] + CONTROLS).copy()
C['events_total'] = len(ev)
C['events_crsp'] = len(crsp)
C['N_regression'] = len(reg)
C['treated_total'] = int(ev[TREAT].sum())
C['treated_crsp'] = int(crsp[TREAT].sum())
C['treated_regression'] = int(reg[TREAT].sum())
C['treated_orgs_regression'] = int(reg.loc[reg[TREAT] == 1, 'org_name'].nunique())
C['treated_parent_ciks_regression'] = int(reg.loc[reg[TREAT] == 1, 'final_cik'].nunique())
log(f"\nSamples: {C['events_total']} events | CRSP {C['events_crsp']} | regression "
    f"{C['N_regression']} ({C['treated_regression']} treated, "
    f"{C['treated_parent_ciks_regression']} parent CIKs)")

# ---------------- Essay 1: H1-H4 ----------------
y = reg['car_30d']
X = sm.add_constant(reg[CONTROLS].astype(float))
m = sm.OLS(y, X).fit(cov_type='HC3')
dof = len(reg) - len(CONTROLS) - 1
EQ = 2.10
labels = {TREAT: 'H2_FCC', 'immediate_disclosure': 'H1_timing',
          'prior_breaches_1yr': 'H3_prior', 'health_breach': 'H4_health'}
log('\nEssay 1 (H1-H4, HC3):')
for var, lab in labels.items():
    b, se, p = m.params[var], m.bse[var], m.pvalues[var]
    tost = max(1 - stats.t.cdf((b + EQ) / se, dof), stats.t.cdf((b - EQ) / se, dof))
    ci = m.conf_int().loc[var]
    C[f'{lab}_coef'] = round(b, 4)
    C[f'{lab}_p'] = round(p, 4)
    C[f'{lab}_ci'] = [round(ci[0], 4), round(ci[1], 4)]
    C[f'{lab}_mde80'] = round(2.8 * se, 4)
    C[f'{lab}_tost_p'] = round(tost, 4)
    C[f'{lab}_status'] = 'BOUNDED NULL' if tost < .05 else ('NULL-INCONCLUSIVE' if p > .05 else 'SIGNIFICANT')
    log(f"  {lab}: {b:+.4f}pp p={p:.4f} | TOST(±2.10) p={tost:.4f} | MDE {2.8 * se:.2f} | {C[f'{lab}_status']}")
C['ROA_coef'] = round(m.params['roa'], 4)
C['ROA_p'] = round(m.pvalues['roa'], 4)
log(f"  ROA: {C['ROA_coef']:+.4f} p={C['ROA_p']:.4f}")

# ROA amendment: op-margin spec + both-included spec
d_m = crsp.dropna(subset=['car_30d'] + HVARS + ['firm_size_log', 'leverage', 'op_margin'])
Xm = sm.add_constant(d_m[HVARS + ['firm_size_log', 'leverage', 'op_margin']].astype(float))
mm = sm.OLS(d_m['car_30d'], Xm).fit(cov_type='HC3')
d_b = crsp.dropna(subset=['car_30d'] + CONTROLS + ['op_margin'])
Xb = sm.add_constant(d_b[CONTROLS + ['op_margin']].astype(float))
mb = sm.OLS(d_b['car_30d'], Xb).fit(cov_type='HC3')
C['AMEND_opmargin_coef'] = round(mm.params['op_margin'], 4)
C['AMEND_opmargin_p'] = round(mm.pvalues['op_margin'], 4)
C['AMEND_both_roa_p'] = round(mb.pvalues['roa'], 4)
C['AMEND_both_opmargin_p'] = round(mb.pvalues['op_margin'], 4)
C['AMEND_nulls_unchanged'] = bool(all(mm.pvalues[v] > .05 and mb.pvalues[v] > .05 for v in HVARS))
log(f"\nROA amendment: op_margin {C['AMEND_opmargin_coef']:+.4f} p={C['AMEND_opmargin_p']:.4f} "
    f"(N={int(mm.nobs)}); both-spec roa p={C['AMEND_both_roa_p']:.4f} / "
    f"op_margin p={C['AMEND_both_opmargin_p']:.4f}; hypothesis nulls unchanged: {C['AMEND_nulls_unchanged']}")

# ---------------- Essay 2: H5 ----------------
reg2 = crsp.dropna(subset=['volatility_change', 'return_volatility_pre'] + CONTROLS).copy()
X2 = sm.add_constant(reg2[CONTROLS + ['return_volatility_pre']].astype(float))
m2 = sm.OLS(reg2['volatility_change'], X2).fit(cov_type='HC3')
b, se, p = m2.params[TREAT], m2.bse[TREAT], m2.pvalues[TREAT]
dof2 = int(m2.df_resid)
tost2 = max(1 - stats.t.cdf((b + EQ) / se, dof2), stats.t.cdf((b - EQ) / se, dof2))
C['N_essay2'] = len(reg2)
C['H5_coef'] = round(b, 4)
C['H5_p'] = round(p, 4)
C['H5_tost_p'] = round(tost2, 4)
C['H5_mde80'] = round(2.8 * se, 4)
C['H5_status'] = 'BOUNDED NULL' if tost2 < .05 else ('NULL-INCONCLUSIVE' if p > .05 else 'SIGNIFICANT')
C['H5_R2'] = round(m2.rsquared, 3)
log(f"\nEssay 2 (H5, N={len(reg2)}, treated {int(reg2[TREAT].sum())}): FCC {b:+.4f} p={p:.4f} | "
    f"TOST p={tost2:.4f} | MDE {2.8 * se:.2f} | R2={m2.rsquared:.3f} | {C['H5_status']}")

# ---------------- Essay 3: H6 ----------------
reg3 = crsp.dropna(subset=CONTROLS).copy()
C['N_essay3'] = len(reg3)
log(f"\nEssay 3 (H6, N={len(reg3)}, treated {int(reg3[TREAT].sum())}):")
for w in (30, 90, 180):
    yv = reg3[f'executive_change_{w}d'].astype(int)
    X3 = sm.add_constant(reg3[CONTROLS].astype(float))
    try:
        m3 = sm.Logit(yv, X3).fit(disp=0)
        ame = m3.get_margeff().summary_frame()
        row = ame.loc[TREAT] if TREAT in ame.index else ame.iloc[0]
        C[f'H6_{w}d_base_rate'] = round(yv.mean(), 4)
        C[f'H6_{w}d_ame_pp'] = round(row['dy/dx'] * 100, 2)
        C[f'H6_{w}d_p'] = round(row['Pr(>|z|)'], 4)
        C[f'H6_{w}d_mde80_pp'] = round(2.8 * row['Std. Err.'] * 100, 2)
        log(f"  {w}d: base {100 * yv.mean():.1f}% | AME {C[f'H6_{w}d_ame_pp']:+.2f}pp "
            f"p={C[f'H6_{w}d_p']:.4f} | MDE {C[f'H6_{w}d_mde80_pp']:.1f}pp")
    except Exception as e:
        log(f'  {w}d: estimation failed ({str(e)[:60]}) — REPORTED, not hidden')

# ---------------- Descriptive first stage ----------------
d1 = ev.dropna(subset=['disclosure_delay_days'])
fs = (d1.loc[d1[TREAT] == 1, 'immediate_disclosure'].mean()
      - d1.loc[d1[TREAT] == 0, 'immediate_disclosure'].mean())
C['first_stage_pp'] = round(fs * 100, 2)
log(f"\nFirst stage (descriptive): treated immediate-disclosure share exceeds untreated by "
    f"{C['first_stage_pp']:+.2f}pp")

# ---------------- prevalence / shares ----------------
C['prior_breach_obs_share'] = round((crsp['prior_breaches_total'] > 0).mean(), 4)
C['prior_breach_firm_share'] = round(
    crsp.groupby('final_cik')['prior_breaches_total'].max().gt(0).mean(), 4)
# Name-your-sample: immediate-disclosure prevalence at all three levels
C['immediate_share_full'] = round(ev['immediate_disclosure'].mean(), 4)
C['immediate_share_crsp'] = round(crsp['immediate_disclosure'].mean(), 4)
C['immediate_share_regression'] = round(reg['immediate_disclosure'].mean(), 4)
C['health_events_crsp'] = int(crsp['health_breach'].sum())

# ---------------- appendix v3 (14 tables) ----------------
log('\nAppendix v3 tables...')
T = {}
sumrows = []
for col in ['car_30d', 'car_5d', 'firm_size_log', 'leverage', 'roa', 'disclosure_delay_days']:
    d = crsp[col].dropna()
    sumrows.append({'Variable': col, 'N': len(d), 'Mean': round(d.mean(), 3),
                    'SD': round(d.std(), 3), 'Median': round(d.median(), 3)})
T[1] = pd.DataFrame(sumrows)
sub = []
for cmp_, col, l1, l0 in [('Form 499', TREAT, 'Filer', 'Non-filer'),
                          ('Timing', 'immediate_disclosure', 'Immediate', 'Delayed'),
                          ('Health', 'health_breach', 'Health', 'Non-health'),
                          ('History', None, 'Any prior', 'No prior')]:
    key = reg['prior_breaches_1yr'].gt(0).astype(int) if col is None else reg[col]
    a, bgrp = reg.loc[key == 1, 'car_30d'], reg.loc[key == 0, 'car_30d']
    tw, pw = stats.ttest_ind(a, bgrp, equal_var=False)
    for v, lab, d in [(1, l1, a), (0, l0, bgrp)]:
        sub.append({'Comparison': cmp_, 'Group': lab, 'Mean CAR': round(d.mean(), 3),
                    'N': len(d), 'Welch diff': '', 'Welch p': ''})
    sub.append({'Comparison': cmp_, 'Group': 'Difference', 'Mean CAR': round(a.mean() - bgrp.mean(), 3),
                'N': '', 'Welch diff': round(tw, 3), 'Welch p': round(pw, 4)})
T[2] = pd.DataFrame(sub)
T[3] = pd.DataFrame([{'Variable': v, 'Coef': round(m.params[v], 4), 'SE': round(m.bse[v], 4),
                      'p': round(m.pvalues[v], 4)} for v in ['const'] + CONTROLS])
reg['size_q'] = pd.qcut(reg['firm_size_log'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
restr = [('Full', reg),
         ('Excl. largest decile', reg[reg['firm_size_log'] <= reg['firm_size_log'].quantile(.9)]),
         ('Excl. smallest decile', reg[reg['firm_size_log'] >= reg['firm_size_log'].quantile(.1)]),
         ('Non-health', reg[reg['health_breach'] == 0])]
rows4 = []
for nm, d in restr:
    cc = [c for c in CONTROLS if d[c].nunique() > 1]
    mr = sm.OLS(d['car_30d'], sm.add_constant(d[cc].astype(float))).fit(cov_type='HC3')
    rows4.append({'Restriction': nm, 'Timing coef': round(mr.params['immediate_disclosure'], 3),
                  'Timing p': round(mr.pvalues['immediate_disclosure'], 3),
                  'FCC coef': round(mr.params.get(TREAT, np.nan), 3),
                  'FCC p': round(mr.pvalues.get(TREAT, np.nan), 3),
                  'ROA coef': round(mr.params['roa'], 2), 'ROA p': round(mr.pvalues['roa'], 3),
                  'N': len(d)})
T[4] = pd.DataFrame(rows4)
rows5 = []
for nm, kw in [('OLS', {}), ('HC1', {'cov_type': 'HC1'}), ('HC3', {'cov_type': 'HC3'}),
               ('Firm-clustered', {'cov_type': 'cluster', 'cov_kwds': {'groups': reg['final_cik']}})]:
    ms = sm.OLS(y, X).fit(**kw)
    rows5.append({'Method': nm, 'Timing p': round(ms.pvalues['immediate_disclosure'], 4),
                  'FCC p': round(ms.pvalues[TREAT], 4), 'ROA p': round(ms.pvalues['roa'], 4)})
T[5] = pd.DataFrame(rows5)
for i, var in [(6, 'immediate_disclosure'), (7, TREAT)]:
    rows = []
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        d = reg[reg['size_q'] == q]
        if len(d) > 20 and d[var].nunique() > 1:
            cc = [c for c in CONTROLS if d[c].nunique() > 1]
            mq = sm.OLS(d['car_30d'], sm.add_constant(d[cc].astype(float))).fit(cov_type='HC3')
            rows.append({'Quartile': q, 'Coef': round(mq.params[var], 3),
                         'p': round(mq.pvalues[var], 3), 'N': len(d),
                         'Treated N': int(d[TREAT].sum())})
        else:
            rows.append({'Quartile': q, 'Coef': None, 'p': None, 'N': len(d),
                         'Treated N': int(d[TREAT].sum())})
    T[i] = pd.DataFrame(rows)
reg['_ym'] = reg['bdt'].dt.to_period('Y').astype(str)
dum = pd.get_dummies(reg['_ym'], drop_first=True).astype(float)
Xfe = sm.add_constant(pd.concat([reg[CONTROLS].astype(float), dum], axis=1))
mfe = sm.OLS(y, Xfe).fit(cov_type='HC3')
T[8] = pd.DataFrame([{'Spec': 'Baseline HC3', 'FCC coef': C['H2_FCC_coef'], 'p': C['H2_FCC_p']},
                     {'Spec': '+ Year FE', 'FCC coef': round(mfe.params[TREAT], 4),
                      'p': round(mfe.pvalues[TREAT], 4)}])
dsev = reg.dropna(subset=['total_affected_max'])
Xs = sm.add_constant(dsev[CONTROLS + ['total_affected_max']].astype(float))
msv = sm.OLS(dsev['car_30d'], Xs).fit(cov_type='HC3')
T[9] = pd.DataFrame([{'Added control': 'Records affected (max across filings)',
                      'FCC coef': round(msv.params[TREAT], 4), 'FCC p': round(msv.pvalues[TREAT], 4),
                      'Control p': round(msv.pvalues['total_affected_max'], 4), 'N': int(msv.nobs),
                      'Note': 'HHI retired with pre-audit chain'}])
ff3 = pd.read_csv('Data/F-F_Research_Data_Factors_daily.csv', skiprows=4)
ff3.columns = ff3.columns.str.strip()
ff3['date'] = pd.to_datetime(ff3[ff3.columns[0]], format='%Y%m%d', errors='coerce')
ff3 = ff3.dropna(subset=['date'])
ff3['ym'] = ff3['date'].dt.to_period('M')
fm = ff3.groupby('ym')[['Mkt-RF', 'SMB', 'HML']].last()
regf = reg.copy()
regf['ym'] = regf['bdt'].dt.to_period('M')
regf = regf.join(fm, on='ym')
df10 = regf.dropna(subset=['Mkt-RF'])
X10 = sm.add_constant(df10[CONTROLS + ['Mkt-RF', 'SMB', 'HML']].astype(float))
m10 = sm.OLS(df10['car_30d'], X10).fit(cov_type='HC3')
T[10] = pd.DataFrame([{'Model': 'Baseline', 'FCC p': C['H2_FCC_p'], 'ROA p': C['ROA_p']},
                      {'Model': 'FF3 controls', 'FCC p': round(m10.pvalues[TREAT], 4),
                       'ROA p': round(m10.pvalues['roa'], 4)}])
# Table 11: ABNORMAL LOG TURNOVER (matches the Methods description): mean
# log(vol / (shrout*1000)) over event trading days [-5,+25] minus estimation
# [-240,-60], per event PERMNO; regressed on the baseline spec.
cd = pd.read_csv('Data/wrds/crsp_daily_returns.csv', usecols=['permno', 'date', 'vol', 'shrout'])
cd['date'] = pd.to_datetime(cd['date'])
pgv = {p: g.sort_values('date').reset_index(drop=True) for p, g in cd.groupby('permno')}


def ab_turnover(permno, bdt):
    g = pgv.get(permno)
    if g is None or len(g) < 120:
        return np.nan
    idx = g['date'].searchsorted(bdt)
    if idx < 120 or idx >= len(g):
        return np.nan
    est = g.iloc[max(0, idx - 240):idx - 60]
    evt = g.iloc[max(0, idx - 5):min(len(g), idx + 26)]
    with np.errstate(divide='ignore', invalid='ignore'):
        et = np.log(est['vol'] / (est['shrout'] * 1000)).replace([np.inf, -np.inf], np.nan).dropna()
        vt = np.log(evt['vol'] / (evt['shrout'] * 1000)).replace([np.inf, -np.inf], np.nan).dropna()
    if len(et) < 30 or len(vt) < 15:
        return np.nan
    return vt.mean() - et.mean()


regv = reg.copy()
regv['_abto'] = [ab_turnover(p, b) if pd.notna(p) else np.nan
                 for p, b in zip(regv['permno'], regv['bdt'])]
dv = regv.dropna(subset=['_abto'])
mv = sm.OLS(dv['_abto'], sm.add_constant(dv[CONTROLS].astype(float))).fit(cov_type='HC3')
T[11] = pd.DataFrame([{'Variable': v, 'Coef (log turnover)': round(mv.params[v], 4),
                       'SE': round(mv.bse[v], 4), 'p': round(mv.pvalues[v], 4)}
                      for v in CONTROLS] +
                     [{'Variable': f'N={int(mv.nobs)} (event [-5,+25] vs est [-240,-60] trading days)',
                       'Coef (log turnover)': '', 'SE': '', 'p': ''}])
C['volume_fcc_coef'] = round(mv.params[TREAT], 4)
C['volume_fcc_p'] = round(mv.pvalues[TREAT], 4)
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
rf.fit(reg[CONTROLS].astype(float), y)
T[12] = pd.DataFrame(sorted(zip(CONTROLS, rf.feature_importances_), key=lambda x: -x[1]),
                     columns=['Feature', 'Importance']).round(4)
C['RF_top_feature'] = T[12].iloc[0]['Feature']
T[13] = pd.DataFrame([{'Note': 'Pre-announcement leakage windows: computed in Stage 5 source data; '
                               'formal table deferred to fresh-clone run (documented)'}])
T[14] = pd.DataFrame([{'Hypothesis': labels[v],
                       'Coef': C[f'{labels[v]}_coef'], 'p': C[f'{labels[v]}_p'],
                       'TOST_p_2.10': C[f'{labels[v]}_tost_p'],
                       'MDE80': C[f'{labels[v]}_mde80'], 'Status': C[f'{labels[v]}_status']}
                      for v in labels])
for i, t in T.items():
    t.to_csv(APP / f'table_{i}.csv', index=False)
log(f'  {len(T)} tables -> outputs/rebuild/appendix_v3/')

# ---------------- constants block + assertion baseline ----------------
cpath = OUT / 'constants_v3.json'
if cpath.exists():
    old = json.loads(cpath.read_text())
    mism = {k: (old.get(k), v) for k, v in C.items()
            if k in old and old[k] != v and not isinstance(v, list)}
    assert not mism, f'ASSERTION FAILURE vs baseline: {list(mism.items())[:5]}'
    log('\nAssertion check vs existing baseline: PASS')
    cpath.write_text(json.dumps({**old, **C}, indent=1))  # persist NEW keys only; existing asserted above
else:
    cpath.write_text(json.dumps(C, indent=1))
    log('\nBaseline constants_v3.json WRITTEN (future runs assert against it)')

with open(OUT / 'CONSTANTS_BLOCK_V3.md', 'w', encoding='utf-8') as f:
    f.write('# CONSTANTS BLOCK v3 — Rebuilt base (8/4/2026)\n\n')
    f.write('Every value below regenerates from run_all (scripts 150-158) off the 1,054-record '
            'universe; assertion baseline in constants_v3.json.\n\n')
    for k, v in C.items():
        f.write(f'- **{k}**: {v}\n')
    f.write('\n' + '\n'.join(L))
log('\nSaved: CONSTANTS_BLOCK_V3.md, constants_v3.json')
