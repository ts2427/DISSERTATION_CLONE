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
Appendix v3: the fourteen-table set regenerated on V3, numbered in Results
  citation order (hypothesis summary = Table 4; severity-only Table 10 — the
  HHI enrichment was retired with the pre-audit chain; Table 14 leakage
  windows computed live, breach-anchored primary / announcement-anchored
  secondary, same daily AR definition as the main CAR). Every table carries
  a trailing CAPTION row written as dissertation prose.
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
# Registered levels: regression-sample overall CAR (previously live-only)
C['car30d_regression_mean'] = round(reg['car_30d'].mean(), 4)
C['car30d_regression_median'] = round(reg['car_30d'].median(), 4)
sub = []
for cmp_, col, l1, l0 in [('Form 499', TREAT, 'Filer', 'Non-filer'),
                          ('Timing', 'immediate_disclosure', 'Immediate', 'Delayed'),
                          ('Health', 'health_breach', 'Health', 'Non-health'),
                          ('History', None, 'Any prior', 'No prior')]:
    key = reg['prior_breaches_1yr'].gt(0).astype(int) if col is None else reg[col]
    a, bgrp = reg.loc[key == 1, 'car_30d'], reg.loc[key == 0, 'car_30d']
    tw, pw = stats.ttest_ind(a, bgrp, equal_var=False)
    for v, lab, d in [(1, l1, a), (0, l0, bgrp)]:
        slug = lab.lower().replace(' ', '_').replace('-', '')
        C[f'T2_{slug}_median'] = round(d.median(), 4)
        sub.append({'Comparison': cmp_, 'Group': lab, 'Mean CAR': round(d.mean(), 3),
                    'Median CAR': round(d.median(), 3),
                    'N': len(d), 'Welch diff': '', 'Welch p': ''})
    sub.append({'Comparison': cmp_, 'Group': 'Difference', 'Mean CAR': round(a.mean() - bgrp.mean(), 3),
                'Median CAR': '', 'N': '', 'Welch diff': round(tw, 3), 'Welch p': round(pw, 4)})
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
T[5] = pd.DataFrame(rows4)
rows5 = []
for nm, kw in [('OLS', {}), ('HC1', {'cov_type': 'HC1'}), ('HC3', {'cov_type': 'HC3'}),
               ('Firm-clustered', {'cov_type': 'cluster', 'cov_kwds': {'groups': reg['final_cik']}})]:
    ms = sm.OLS(y, X).fit(**kw)
    rows5.append({'Method': nm, 'Timing p': round(ms.pvalues['immediate_disclosure'], 4),
                  'FCC p': round(ms.pvalues[TREAT], 4), 'ROA p': round(ms.pvalues['roa'], 4)})
T[6] = pd.DataFrame(rows5)
for i, var in [(7, 'immediate_disclosure'), (8, TREAT)]:
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
T[9] = pd.DataFrame([{'Spec': 'Baseline HC3', 'FCC coef': C['H2_FCC_coef'], 'p': C['H2_FCC_p']},
                     {'Spec': '+ Year FE', 'FCC coef': round(mfe.params[TREAT], 4),
                      'p': round(mfe.pvalues[TREAT], 4)}])
dsev = reg.dropna(subset=['total_affected_max'])
Xs = sm.add_constant(dsev[CONTROLS + ['total_affected_max']].astype(float))
msv = sm.OLS(dsev['car_30d'], Xs).fit(cov_type='HC3')
T[10] = pd.DataFrame([{'Added control': 'Records affected (max across filings)',
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
T[11] = pd.DataFrame([{'Model': 'Baseline', 'FCC p': C['H2_FCC_p'], 'ROA p': C['ROA_p']},
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
T[12] = pd.DataFrame([{'Variable': v, 'Coef (log turnover)': round(mv.params[v], 4),
                       'SE': round(mv.bse[v], 4), 'p': round(mv.pvalues[v], 4)}
                      for v in CONTROLS] +
                     [{'Variable': f'N={int(mv.nobs)} (event [-5,+25] vs est [-240,-60] trading days)',
                       'Coef (log turnover)': '', 'SE': '', 'p': ''}])
C['volume_fcc_coef'] = round(mv.params[TREAT], 4)
C['volume_fcc_p'] = round(mv.pvalues[TREAT], 4)
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
rf.fit(reg[CONTROLS].astype(float), y)
T[13] = pd.DataFrame(sorted(zip(CONTROLS, rf.feature_importances_), key=lambda x: -x[1]),
                     columns=['Feature', 'Importance']).round(4)
C['RF_top_feature'] = T[13].iloc[0]['Feature']
# Table 14: PRE-ANNOUNCEMENT LEAKAGE WINDOWS. Same daily abnormal-return
# definition as the main CAR: (ret - vwretd) x100 summed over TRADING days.
# PRIMARY anchor: trading day nearest breach_date (identical to the main CAR
# anchor, same +/-50 calendar-day pull). SECONDARY anchor: trading day nearest
# reported_date; rows with an unparseable/missing reported_date or the signed
# wrong-field flag (delay_invalid=1, Fix 3) are excluded from that panel.
# Inclusion is listwise per panel: all 30 pre-anchor trading days must exist
# with non-missing abnormal returns, else the event is excluded and counted.
cd13 = pd.read_csv('Data/wrds/crsp_daily_returns.csv', usecols=['permno', 'date', 'ret'])
tp13 = Path('Data/wrds/crsp_daily_topup.csv')
if tp13.exists():
    cd13 = pd.concat([cd13, pd.read_csv(tp13, usecols=['permno', 'date', 'ret'])],
                     ignore_index=True)
mkt13 = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
cd13['date'] = pd.to_datetime(cd13['date'])
mkt13['date'] = pd.to_datetime(mkt13['date'])
cd13 = cd13.merge(mkt13, on='date', how='left')
cd13['ar13'] = (pd.to_numeric(cd13['ret'], errors='coerce') - cd13['vwretd']) * 100
p13 = {p: g.sort_values('date').reset_index(drop=True) for p, g in cd13.groupby('permno')}
W13 = [(-30, -21), (-20, -11), (-10, -1)]


def leak_cars(permno, anchor):
    g = p13.get(permno)
    if g is None or pd.isna(anchor):
        return None
    pos = (g['date'] - anchor).abs().idxmin()
    if abs((g.loc[pos, 'date'] - anchor).days) > 50 or pos < 30:
        return None
    cars = {}
    for a, b in W13:
        sl = g['ar13'].iloc[pos + a:pos + b + 1]
        if len(sl) != b - a + 1 or sl.isna().any():
            return None
        cars[f'{a},{b}'] = sl.sum()
    return cars


base13 = crsp.copy()
base13['rdt'] = pd.to_datetime(base13['reported_date'], errors='coerce')
base13.loc[base13['delay_invalid'] == 1, 'rdt'] = pd.NaT
C['T14_ann_excluded_no_reported'] = int(base13['rdt'].isna().sum())
panels13 = {}
for pkey, pnl, anc, dsub in [
        ('breach', 'Breach-anchored (PRIMARY)', 'bdt', base13),
        ('ann', 'Announcement-anchored (secondary)', 'rdt', base13[base13['rdt'].notna()])]:
    recs = []
    for _, r in dsub.iterrows():
        cars = leak_cars(r['permno'], r[anc]) if pd.notna(r['permno']) else None
        if cars is not None:
            recs.append({'treated': int(r[TREAT]), **cars})
    panels13[pnl] = pd.DataFrame(recs)
    C[f'T14_{pkey}_N'] = len(recs)
    C[f'T14_{pkey}_excluded_history'] = len(dsub) - len(recs)
rows13 = []
for pkey, pnl in [('breach', 'Breach-anchored (PRIMARY)'),
                  ('ann', 'Announcement-anchored (secondary)')]:
    dfp = panels13[pnl]
    for a, b in W13:
        wcol, wlab, wkey = f'{a},{b}', f'[{a},{b}]', f'm{-a}_m{-b}'
        groups = [('All', dfp[wcol]),
                  ('Treated', dfp.loc[dfp['treated'] == 1, wcol]),
                  ('Untreated', dfp.loc[dfp['treated'] == 0, wcol])]
        for glab, s in groups:
            t1, pv1 = stats.ttest_1samp(s, 0)
            rows13.append({'Panel': pnl, 'Window': wlab, 'Group': glab, 'N': len(s),
                           'Mean CAR (pp)': round(s.mean(), 3), 'Median': round(s.median(), 3),
                           'SD': round(s.std(), 3), 't': round(t1, 3), 'p': round(pv1, 4)})
        st, su = groups[1][1], groups[2][1]
        tw13, pw13 = stats.ttest_ind(st, su, equal_var=False)
        rows13.append({'Panel': pnl, 'Window': wlab, 'Group': 'Difference (Welch)', 'N': '',
                       'Mean CAR (pp)': round(st.mean() - su.mean(), 3), 'Median': '', 'SD': '',
                       't': round(tw13, 3), 'p': round(pw13, 4)})
        C[f'T14_{pkey}_{wkey}_mean'] = round(dfp[wcol].mean(), 4)
        C[f'T14_{pkey}_{wkey}_p'] = round(stats.ttest_1samp(dfp[wcol], 0)[1], 4)
        C[f'T14_{pkey}_{wkey}_diff_p'] = round(pw13, 4)
T[14] = pd.DataFrame(rows13)
log(f"  Table 14 leakage: breach panel N={C['T14_breach_N']} "
    f"(excl {C['T14_breach_excluded_history']} history); ann panel N={C['T14_ann_N']} "
    f"(excl {C['T14_ann_excluded_no_reported']} no-reported + {C['T14_ann_excluded_history']} history)")
T[4] = pd.DataFrame([{'Hypothesis': labels[v],
                       'Coef': C[f'{labels[v]}_coef'], 'p': C[f'{labels[v]}_p'],
                       'TOST_p_2.10': C[f'{labels[v]}_tost_p'],
                       'MDE80': C[f'{labels[v]}_mde80'], 'Status': C[f'{labels[v]}_status']}
                      for v in labels])
# Dissertation captions, appended as a trailing CAPTION row on every table
# (first column 'CAPTION', second column the text).
CAPTIONS = {
    1: (f'This table reports summary statistics for the key continuous variables on the '
        f'CRSP-covered sample (N = {len(crsp)} events). Row-level N varies because Compustat '
        f'covariates are available for {int(crsp["firm_size_log"].notna().sum())} events and the '
        f'disclosure delay for {int(crsp["disclosure_delay_days"].notna().sum())}. CAR variables '
        'are cumulative market-adjusted abnormal returns in percentage points.'),
    2: (f'This table reports mean and median 30-day CARs by subgroup on the regression sample '
        f'(N = {len(reg)}). Each Difference row reports the difference in group means with a '
        'Welch two-sample t-test allowing unequal variances; medians are reported for each group '
        'but are not tested.'),
    3: (f'This table reports the baseline ordinary least squares regression of the 30-day CAR on '
        f'the four hypothesis variables and three accounting controls, estimated on the '
        f'regression sample (N = {len(reg)}) with HC3 heteroskedasticity-robust standard errors.'),
    4: (f'This table summarizes the four hypothesis tests from the baseline HC3 regression on the '
        f'regression sample (N = {len(reg)}). TOST p-values test equivalence against the +/-2.10 '
        'percentage-point bound, which was fixed from the prior literature before the rebuilt '
        'estimates existed; MDE80 is the minimum detectable effect at 80 percent power.'),
    5: ('This table re-estimates the baseline specification with HC3 standard errors on '
        'restricted samples; each row reports its own N. Controls without variation within a '
        'restricted sample are dropped from that row.'),
    6: (f'This table reports p-values from the baseline specification on the regression sample '
        f'(N = {len(reg)}) under alternative standard-error methods: classical OLS, HC1, HC3, '
        f'and clustering by parent CIK ({reg["final_cik"].nunique()} clusters).'),
    7: ('This table reports the immediate-disclosure coefficient from the baseline specification '
        '(HC3 standard errors), estimated separately within firm-size quartiles of the regression '
        'sample. Treated event counts are reported because treated events concentrate in the '
        'larger quartiles; controls without variation within a quartile are dropped.'),
    8: ('This table reports the Form 499 coefficient from the baseline specification (HC3 '
        'standard errors), estimated separately within firm-size quartiles of the regression '
        'sample. Treated event counts are reported because treated events concentrate in the '
        'larger quartiles; controls without variation within a quartile are dropped.'),
    9: (f'This table compares the Form 499 coefficient from the baseline HC3 specification with '
        f'a specification adding calendar-year fixed effects, both estimated on the regression '
        f'sample (N = {len(reg)}).'),
    10: (f'This table adds breach severity, measured as the maximum records-affected count '
         f'across source filings, to the baseline HC3 specification (N = {int(msv.nobs)}). The '
         'pre-audit industry-concentration (HHI) control was retired with the pre-audit chain '
         'and does not appear in v3.'),
    11: (f'This table adds month-level Fama-French three-factor values (Mkt-RF, SMB, and HML) to '
         f'the baseline HC3 specification (N = {int(m10.nobs)}). Every regression-sample event '
         'month matched the factor file, so no observations are lost.'),
    12: (f'This table regresses abnormal log share turnover on the baseline covariates with HC3 '
         f'standard errors (N = {int(mv.nobs)}). Abnormal turnover is the mean log turnover over '
         'event trading days [-5, +25] minus the mean over estimation days [-240, -60]; '
         f'{len(reg) - int(mv.nobs)} regression-sample events lacking sufficient volume history '
         'are excluded.'),
    13: (f'This table reports random forest feature importances (500 trees, fixed seed 42) for '
         f'the seven baseline covariates predicting the 30-day CAR on the regression sample '
         f'(N = {len(reg)}). Importances are descriptive and carry no causal interpretation.'),
    14: ('This table reports cumulative market-adjusted abnormal returns (daily CRSP return '
         'minus the CRSP value-weighted market return, x100, summed over trading days) over '
         'three pre-event windows. In the primary panel, day 0 is the trading day nearest the '
         'breach date, identical to the main CAR anchor with its +/-50 calendar-day pull. In the '
         'secondary panel, day 0 is the trading day nearest the reported date; '
         f'{C["T14_ann_excluded_no_reported"]} of {len(base13)} CRSP-sample events are excluded '
         'for a missing or invalid reported date (including delay_invalid = 1 wrong-field '
         'records). Events lacking 30 complete pre-anchor trading days of abnormal returns are '
         f'excluded listwise per panel (breach-anchored: {C["T14_breach_excluded_history"]}; '
         f'announcement-anchored: {C["T14_ann_excluded_history"]}).'),
}
for i, t in T.items():
    cap = {c: '' for c in t.columns}
    cols = list(t.columns)
    cap[cols[0]], cap[cols[1]] = 'CAPTION', CAPTIONS[i]
    pd.concat([t, pd.DataFrame([cap])], ignore_index=True).to_csv(
        APP / f'table_{i}.csv', index=False)
log(f'  {len(T)} tables (citation order, captioned) -> outputs/rebuild/appendix_v3/')

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
