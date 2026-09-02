"""
ESSAY 2 QUERY 5 — H1 (intent-scope restriction) + PART A (equivalence bounds)
==============================================================================
H1: 47 CFR 64.2011(e) covers only INTENTIONAL access ("without authorization
or exceeding authorization, has intentionally gained access") until the
(indefinitely delayed) 2024 amendment. PRC breach vectors map to intent:
HACK/INSD/CARD intentional (in scope); DISC inadvertent (out); PHYS/PORT/
STAT ambiguous (theft intentional, loss not) — reported both ways. The
canonical data carry only the legacy vector codes (HACK/INSD/DISC/PHYS/
PORT/STAT/CARD/UNKN and + combinations); the current PRC schema's 36
breach-method subtypes are NOT present, so theft cannot be separated from
loss within PHYS/PORT/STAT (stated). A combination type qualifies if ANY
component qualifies. Treated events failing the scope test are DROPPED
(not recoded to control): they are covered-entity events outside the
rule's event-level scope — ITT vs effective treatment. One-sided
misclassification of a binary regressor attenuates toward zero (Aigner
1973; Bound-Brown-Mathiowetz 2001; Mahajan 2006): the entity-level null is
the WEAK null; these are the sharper tests. Precedent: Kamiya et al.
(2021 JFE) condition on information type; Fiechter-Hitz-Lehmann (2022).
CPNI hand-coding from notification letters is NOT attempted here — stated
as the remaining option (102 letters, double-coded subsample) per the
directive: commit or state; do not approximate from fields.

PART A: equivalence bounds.
A1: spread SESOI = ONE HALF-TICK at the sample median share price (Reg NMS
    Rule 612: $0.01 minimum increment at/above $1.00; one tick in bp =
    100/P). Institutional, reproducible, recognizable. NOT 0.25 x SD
    (Lakens-Scheel-Isager 2018 rank benchmarks last; 0.25 sigma is a WWC/
    balance convention, not an equivalence one; Wellek's 0.36 sigma is
    the nearest named distributional convention and is reported for the
    volatility outcome alongside the equivalence CI).
A2: the equivalence confidence interval — the smallest bound at which
    equivalence would be concluded = the larger absolute endpoint of the
    90% CI (Hartman & Hidalgo 2018) — reported for every outcome.
A3: equivalence concluded at 5% when the 90% CI lies inside (-m, m);
    100-2*alpha because TWO one-sided tests; intersection-union makes the
    combined procedure level-alpha without multiplicity correction
    (Schuirmann 1987; Lakens 2017; Rainey 2014; Abadie 2020).
A4: TOST verdicts (meaningful / negligible / INCONCLUSIVE), MDE and
    MDE/SESOI per outcome; log-OCAM uses a proportional +/-10% bound
    (0.0953 log points) because ILLIQ has no natural cardinal scale —
    each rule derived per outcome, deliberately NOT uniform.

Outputs: outputs/ESSAY2_QUERY5_PART_HA.md + t43-t45 CSVs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
L = []
N_TESTS = []


def log(m=''):
    print(m)
    L.append(str(m))


def test(fam, name):
    N_TESTS.append((fam, name))


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
fin['rdt'] = pd.to_datetime(fin['reported_date'])
XS4 = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
       'health_breach', 'prior_events']
log('=' * 90)
log('ESSAY 2 QUERY 5 — H1 INTENT SCOPE + PART A BOUNDS')
log('=' * 90)

# ---------------- rebuild microstructure outcomes (167 conventions) --------
qd = pd.read_csv('Data/wrds/crsp_quotes_topup.csv', low_memory=False)
qd['date'] = pd.to_datetime(qd['date'])
for c in ['bid', 'ask', 'prc', 'openprc', 'bidlo', 'askhi', 'vol']:
    qd[c] = pd.to_numeric(qd[c], errors='coerce')
qd['valid'] = qd['bid'].notna() & qd['ask'].notna() & (qd['ask'] > qd['bid']) & (qd['bid'] > 0)
qd['cpqs'] = np.where(qd['valid'], (qd['ask'] - qd['bid']) / ((qd['ask'] + qd['bid']) / 2), np.nan)
qd.loc[qd['cpqs'] > 0.5, 'cpqs'] = np.nan
from bidask import edge
PGQ = {p: g.sort_values('date').reset_index(drop=True) for p, g in qd.groupby('permno')}
rows = []
prices = []
for i, r in fin.iterrows():
    g = PGQ.get(int(r['permno']) if pd.notna(r['permno']) else -1)
    if g is None:
        continue
    gaps = (g['date'] - r['rdt']).abs()
    pos = int(gaps.idxmin())
    if gaps.iloc[pos] > pd.Timedelta(days=7):
        continue
    prices.append(abs(g['prc'].iloc[pos]))
    out = dict(idx=i)
    for wlab, lo_, hi_ in [('pre', -52, -11), ('post', 11, 52)]:
        w = g.iloc[max(0, pos + lo_): pos + hi_ + 1]
        w = w[(w['prc'] > 0) & (w['vol'] > 0)]
        if len(w) < 25:
            continue
        out[f'cpqs_{wlab}'] = w['cpqs'].mean()
        try:
            out[f'edge_{wlab}'] = edge(w['openprc'], w['askhi'], w['bidlo'],
                                       abs(w['prc']), sign=True)
        except Exception:
            pass
        dvol = (abs(w['prc']) * w['vol']).replace(0, np.nan)
        out[f'ocam_{wlab}'] = ((abs(abs(w['prc']) - w['openprc']) / w['openprc'])
                               / dvol).mean() * 1e6
    rows.append(out)
ms = pd.DataFrame(rows).set_index('idx')
for w_ in ['pre', 'post']:
    s = ms[f'ocam_{w_}']
    ms[f'ocam_{w_}'] = np.log(s.clip(s.quantile(.01), s.quantile(.99)))
for v in ['cpqs', 'edge', 'ocam']:
    ms[f'{v}_chg'] = ms[f'{v}_post'] - ms[f'{v}_pre']
fin = fin.join(ms[[f'{v}_chg' for v in ['cpqs', 'edge', 'ocam']]])
fin['emonth'] = fin['rdt'].dt.to_period('M').astype(str)
MED_P = float(np.median(prices))

# ---------------- H1: intent-scope restriction ----------------
log('\n## H1 — Intent-scope restriction (64.2011(e); FCC 22-102 para.12; '
    'FCC 23-111 para.21)')
SCOPE_STRICT = {'HACK', 'INSD', 'CARD'}
SCOPE_AMBIG = {'PHYS', 'PORT', 'STAT'}


def in_scope(bt, scope):
    if pd.isna(bt):
        return False
    return any(part in scope for part in str(bt).split('+'))


t_all = fin[fin[TREAT] == 1]
log(f"  Treated breach vectors (N={len(t_all)}): "
    f"{dict(t_all['breach_type'].value_counts())}")
log('  NOTE: the canonical data carry only legacy vector codes; the '
    'current PRC schema\'s 36 breach-method subtypes are absent, so theft '
    'vs loss inside PHYS/PORT/STAT cannot be separated (checked, stated).')


def estimate(d, label, dv='e2_vol_change', pre='e2_pre_sd'):
    d = d.dropna(subset=[dv, pre] + [c for c in XS4 if c not in (TREAT,)])
    d = d[d[dv].notna()]
    rhs = [TREAT, pre] + [c for c in XS4 if c not in (TREAT, 'e2_pre_sd')]
    rhs = list(dict.fromkeys(rhs))
    X = sm.add_constant(d[rhs].astype(float))
    f = sm.OLS(d[dv].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': d['final_cik']}, use_t=True)
    b, se = f.params[TREAT], f.bse[TREAT]
    ci = f.conf_int().loc[TREAT]
    df_ = getattr(f, 'df_resid_inference', f.df_resid)
    tt_ = d[d[TREAT] == 1]
    mde = (stats.t.ppf(.975, df_) + stats.t.ppf(.80, df_)) * se
    row = dict(sample=label, outcome=dv, coef=round(b, 4), se=round(se, 4),
               ci_lo=round(ci[0], 4), ci_hi=round(ci[1], 4), n=int(f.nobs),
               n_treated=int(tt_[TREAT].sum()),
               treated_orgs=int(tt_['org_name'].nunique()),
               treated_parents=int(tt_['final_cik'].nunique()),
               mde80=round(mde, 4))
    log(f"  {label} [{dv}]: coef {b:+.4f} SE {se:.4f} CI [{ci[0]:+.4f}, "
        f"{ci[1]:+.4f}] N={int(f.nobs)} (treated {row['n_treated']}/"
        f"{row['treated_orgs']} orgs/{row['treated_parents']} parents) "
        f"MDE80 {mde:.3f}")
    return row


h1rows = []
samples = {}
for lab, scope, excl_disc in [
        ('ITT (entity-level, all treated events)', None, False),
        ('STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped)',
         SCOPE_STRICT, True),
        ('LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped)',
         SCOPE_STRICT | SCOPE_AMBIG, True)]:
    if scope is None:
        d = fin
    else:
        drop = (fin[TREAT] == 1) & ~fin['breach_type'].map(
            lambda b: in_scope(b, scope))
        d = fin[~drop]
    samples[lab] = d
    h1rows.append(estimate(d, lab))
    test('H1', f'headline {lab}')
log('\n  Channels on the restricted sets:')
for lab in list(samples):
    if lab.startswith('ITT'):
        continue
    d = samples[lab]
    for dv, pre in [('cpqs_chg', 'e2_pre_sd'), ('edge_chg', 'e2_pre_sd'),
                    ('ocam_chg', 'e2_pre_sd')]:
        h1rows.append(estimate(d, lab, dv=dv))
        test('H1', f'{dv} {lab}')
pd.DataFrame(h1rows).to_csv(OUTDIR / 't43_intent_scope.csv', index=False)
log('\n  ITT-vs-effective-treatment framing: entity-level assignment where '
    'the rule applies event-level is one-sided misclassification of a '
    'binary regressor -> attenuation toward zero (Aigner 1973; Bound et '
    'al. 2001; Mahajan 2006). The entity-level null is therefore the WEAK '
    'null and the scope-restricted rows are the sharper tests; equivalence '
    'bounds estimated on the diluted treatment are NOT bounds on the '
    'scope-restricted effect. CPNI hand-coding from the 102 notification '
    'letters (double-coded subsample, inter-rater reliability) is the '
    'remaining option and was NOT attempted — stated in limitations; no '
    'field-based approximation is offered.')

# ---------------- PART A: bounds ----------------
log('\n## PART A — Equivalence bounds')
tick_bp = 100 / MED_P
sesoi_cpqs = 0.5 * tick_bp * 1e-4  # half-tick as a CPQS fraction
log(f'  A1: sample median share price at notification P = ${MED_P:.2f}; '
    f'one tick = 100/P = {tick_bp:.2f} bp; SESOI(spread) = one HALF-TICK '
    f'= {0.5 * tick_bp:.2f} bp = {sesoi_cpqs:.6f} in CPQS units (Reg NMS '
    f'Rule 612; a spread change below the market\'s own pricing '
    f'granularity cannot be implemented by any trader). EDGE shares the '
    f'spread SESOI. log-OCAM: proportional +/-10%% bound (0.0953 log '
    f'points) — ILLIQ has no natural cardinal scale. Volatility: no '
    f'institutional increment exists; the equivalence CI leads, with the '
    f'quarter-SD (0.2742) and Wellek 0.36-sigma (0.3948) distributional '
    f'references reported for context only. One rule per outcome, '
    f'derived, deliberately NOT uniform.')

# regressions to get (coef, se, df) per outcome, month FE for microstructure
def outcome_fit(dv, micro=True):
    d = fin.dropna(subset=[dv, 'e2_pre_sd'] + [c for c in XS4 if c != TREAT])
    rhs = [TREAT] + [c for c in XS4 if c != TREAT]
    X = d[rhs].astype(float)
    if micro:
        X = pd.concat([X, pd.get_dummies(d['emonth'], drop_first=True).astype(float)],
                      axis=1)
    X = sm.add_constant(X)
    f = sm.OLS(d[dv].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': d['final_cik']}, use_t=True)
    return (float(f.params[TREAT]), float(f.bse[TREAT]),
            float(getattr(f, 'df_resid_inference', f.df_resid)), int(f.nobs))


arows = []
for dv, lab, m_, micro in [
        ('e2_vol_change', 'volatility (daily pp)', 0.2742, False),
        ('cpqs_chg', 'CPQS (fraction)', sesoi_cpqs, True),
        ('edge_chg', 'EDGE (fraction)', sesoi_cpqs, True),
        ('ocam_chg', 'log-OCAM', 0.0953, True)]:
    b, se, df_, n_ = outcome_fit(dv, micro)
    t90 = stats.t.ppf(0.95, df_)
    ci90 = (b - t90 * se, b + t90 * se)
    eq_ci = max(abs(ci90[0]), abs(ci90[1]))   # smallest concludable bound
    tost_p = max(1 - stats.t.cdf((b + m_) / se, df_),
                 stats.t.cdf((b - m_) / se, df_))
    mde = (stats.t.ppf(.975, df_) + stats.t.ppf(.80, df_)) * se
    verdict = ('NEGLIGIBLE' if (ci90[0] > -m_ and ci90[1] < m_)
               else ('MEANINGFUL' if stats.t.cdf(-abs(b / se), df_) * 2 < .05
                     else 'INCONCLUSIVE'))
    test('A', f'TOST {lab}')
    arows.append(dict(outcome=lab, coef=b, se=se, ci90_lo=ci90[0],
                      ci90_hi=ci90[1], sesoi=m_, tost_p=round(tost_p, 4),
                      equivalence_ci=eq_ci, mde80=mde,
                      mde_over_sesoi=round(mde / m_, 2), n=n_,
                      verdict=verdict))
    log(f'  {lab}: coef {b:+.6f} (SE {se:.6f}, 90% CI [{ci90[0]:+.6f}, '
        f'{ci90[1]:+.6f}]) | SESOI ±{m_:.6f} | TOST p={tost_p:.4f} | '
        f'equivalence CI (smallest concludable bound) = {eq_ci:.6f} | '
        f'MDE80 {mde:.6f} | MDE/SESOI {mde / m_:.2f} | **{verdict}**')
A = pd.DataFrame(arows)
A.to_csv(OUTDIR / 't44_equivalence_bounds.csv', index=False)
cq = A[A['outcome'].str.startswith('CPQS')].iloc[0]
vq = A[A['outcome'].str.startswith('volatility')].iloc[0]
log(f'\n  THE ONE-SENTENCE ANSWER: '
    + (f'CPQS IS equivalence-bounded at the half-tick SESOI while the '
       f'volatility outcome is NOT bounded at any defensible SESOI — the '
       f'liquidity channel supports a negligible-effect claim; volatility '
       f'supports only an inconclusive null.' if cq['verdict'] == 'NEGLIGIBLE'
       and vq['verdict'] != 'NEGLIGIBLE' else
       f'CPQS verdict: {cq["verdict"]}; volatility verdict: '
       f'{vq["verdict"]} — see table.'))
log('  A3 (stated correctly): equivalence is concluded at the 5% level '
    'when the 90% CI lies entirely within (-m, m); the interval is '
    '100-2*alpha because there are TWO one-sided tests, and the '
    'intersection-union principle makes the combined procedure '
    'level-alpha without multiplicity correction (Schuirmann 1987; '
    'Lakens 2017; Rainey 2014; Abadie 2020). "Equivalence confidence '
    'interval" is the named object (Hartman & Hidalgo 2018); the term '
    '"equivalence curve" is not used.')

fams = pd.Series([f for f, _ in N_TESTS]).value_counts()
log('\n' + '=' * 90)
log(f'Tests this script: {len(N_TESTS)} — '
    + '; '.join(f'{k}: {v}' for k, v in fams.items()))
Path('outputs/ESSAY2_QUERY5_PART_HA.md').write_text(
    '# Essay 2 Query 5 — H1 scope + Part A bounds (computed live)\n\n'
    + '\n'.join(L) + '\n', encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY5_PART_HA.md + t43-t44')
