"""
ESSAY 2 QUERY 4 — PART F (measurement grid) + B1/B3 (gradient decomposition)
=============================================================================
F1: treatment coefficient across every defensible measurement choice.
Axes (2x2x3x4x2x2 = 192 realized-SD specs + 2 GARCH rows):
  anchor    : notification date vs breach date [TYPE N NODE — Part A
              establishes breach-anchoring is construct-invalid; reported
              in the grid as documentation of what the wrong choice
              produces, never pooled as equivalent]
  day basis : trading vs calendar days                          [Type E]
  window L  : 21, 31, 42 days per side                          [Type E]
  gap g     : 0, 1, 3, 5 days each side                         [Type E]
  returns   : log vs simple                                     [Type E]
  DV winsor : raw vs 1/99                                       [Type U]
Annualized-vs-daily is EXCLUDED as an axis: a pure sqrt(252) rescaling of
the same statistic would double-count identical specifications (stated).
All coefficients are reported in daily pp. Inference: CV1 clustered at
parent CIK (descriptive grid — dispersion is the finding; NO joint
permutation test is run: Semken & Rossell 2022 show the SCA median test
can have Type I error of 1 under control-set variation. Framed as a
non-standard-error decomposition, Menkveld et al. 2024; Mitton 2022).

B1: four-panel decomposition of the gradient reversal (fixed old spec):
  (i) pre-dedup + SIC, (ii) pre-dedup + Form 499 (family-level
  reconstruction, stated), (iii) dedup + SIC (record-modal SIC mapped to
  events, stated), (iv) dedup + Form 499 (canonical).
B3: the size-gradient across the corrected-data grid (share of specs
  where Q1 exceeds Q4 / where the step-down is monotone).
H2: winsorization sensitivity rows.

Outputs: outputs/ESSAY2_QUERY4_PART_FB.md + t29-t33 CSVs
"""

import sys
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
fin['rdt'] = pd.to_datetime(fin['reported_date'])
fin['bdt'] = pd.to_datetime(fin['breach_date'])
N = len(fin)
log('=' * 90)
log('ESSAY 2 QUERY 4 — PART F GRID + B1/B3 GRADIENT (N=%d)' % N)
log('=' * 90)

# ---------------- price data ----------------
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv',
                   usecols=['permno', 'date', 'ret'])
tp = Path('Data/wrds/crsp_daily_topup.csv')
if tp.exists():
    crsp = pd.concat([crsp, pd.read_csv(tp, usecols=['permno', 'date', 'ret'])],
                     ignore_index=True)
tp_dish = Path('Data/wrds/crsp_daily_topup_dish.csv')
if tp_dish.exists():
    crsp = pd.concat([crsp, pd.read_csv(tp_dish, usecols=['permno', 'date', 'ret'])],
                     ignore_index=True)
crsp['date'] = pd.to_datetime(crsp['date'])
crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')
crsp = crsp.dropna(subset=['ret'])
PG = {p: g.sort_values('date').reset_index(drop=True)
      for p, g in crsp.groupby('permno')}

ANCHORS = ['notification', 'breach']
BASES = ['trading', 'calendar']
LS = [21, 31, 42]
GS = [0, 1, 3, 5]
RETS = ['log', 'simple']
MIN_FRAC = 0.7  # min share of window days with valid returns

# Precompute per-event, per-(anchor,basis,L,g) pre/post SDs for both return types
log('\nPrecomputing window SDs (%d window configs x %d events)...'
    % (len(ANCHORS) * len(BASES) * len(LS) * len(GS), N))
sd_store = {}  # (i, anchor, basis, L, g, rtype) -> (pre_sd, post_sd) in daily pp
for i, r in fin.iterrows():
    g_ = PG.get(r['permno'])
    if g_ is None:
        continue
    dates = g_['date']
    lr = np.log1p(g_['ret'].to_numpy())
    sr = g_['ret'].to_numpy()
    for anchor in ANCHORS:
        adt = r['rdt'] if anchor == 'notification' else r['bdt']
        gaps = (dates - adt).abs()
        pos = int(gaps.idxmin())
        if gaps.iloc[pos] > timedelta(days=7):
            continue
        for basis in BASES:
            for Lw in LS:
                span = Lw - 1
                for gp in GS:
                    if basis == 'trading':
                        if gp == 0:
                            pre_ix = np.arange(max(0, pos - span - 1), pos)
                            post_ix = np.arange(pos, min(len(g_), pos + span + 1))
                        else:
                            pre_ix = np.arange(max(0, pos - gp - span), pos - gp + 1)
                            post_ix = np.arange(pos + gp, min(len(g_), pos + gp + span + 1))
                    else:
                        if gp == 0:
                            m_pre = (dates >= adt - timedelta(days=span + 1)) & (dates < adt)
                            m_post = (dates >= adt) & (dates <= adt + timedelta(days=span))
                        else:
                            m_pre = (dates >= adt - timedelta(days=gp + span)) & (dates <= adt - timedelta(days=gp))
                            m_post = (dates >= adt + timedelta(days=gp)) & (dates <= adt + timedelta(days=gp + span))
                        pre_ix = np.where(m_pre)[0]
                        post_ix = np.where(m_post)[0]
                    need = int(MIN_FRAC * Lw) if basis == 'trading' else int(MIN_FRAC * Lw * 5 / 7)
                    if len(pre_ix) < need or len(post_ix) < need:
                        continue
                    for rtype, arr in [('log', lr), ('simple', sr)]:
                        pre_sd = np.std(arr[pre_ix], ddof=1) * 100
                        post_sd = np.std(arr[post_ix], ddof=1) * 100
                        sd_store[(i, anchor, basis, Lw, gp, rtype)] = (pre_sd, post_sd)

CTRL = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
        'prior_events']


def run_spec(dv, pre, d):
    d = d.copy()
    d['_dv'] = dv
    d['_pre'] = pre
    d = d.dropna(subset=['_dv', '_pre'])
    X = sm.add_constant(d[[TREAT, '_pre'] + CTRL].astype(float))
    f = sm.OLS(d['_dv'].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': d['final_cik']}, use_t=True)
    return f, d


grid_rows = []
grad_rows = []
for anchor in ANCHORS:
    for basis in BASES:
        for Lw in LS:
            for gp in GS:
                for rtype in RETS:
                    key_ok = [i for i in fin.index
                              if (i, anchor, basis, Lw, gp, rtype) in sd_store]
                    if len(key_ok) < 150:
                        continue
                    pre = pd.Series({i: sd_store[(i, anchor, basis, Lw, gp, rtype)][0]
                                     for i in key_ok})
                    post = pd.Series({i: sd_store[(i, anchor, basis, Lw, gp, rtype)][1]
                                      for i in key_ok})
                    dv_raw = (post - pre).reindex(fin.index)
                    pre_f = pre.reindex(fin.index)
                    for wins in ['raw', 'w199']:
                        dv = dv_raw.clip(dv_raw.quantile(.01), dv_raw.quantile(.99)) \
                            if wins == 'w199' else dv_raw
                        f, d = run_spec(dv, pre_f, fin)
                        b, se, p = f.params[TREAT], f.bse[TREAT], f.pvalues[TREAT]
                        grid_rows.append(dict(
                            anchor=anchor, basis=basis, L=Lw, gap=gp,
                            returns=rtype, winsor=wins, estimator='SD',
                            n=int(f.nobs), coef=round(b, 4), se=round(se, 4),
                            p=round(p, 4)))
                        # gradient within this spec
                        if wins == 'raw' and rtype == 'log':
                            dq = d.copy()
                            dq['q'] = pd.qcut(dq['firm_size_log'], 4,
                                              labels=[1, 2, 3, 4])
                            qc = {}
                            for qq in [1, 2, 3, 4]:
                                sub = dq[dq['q'] == qq]
                                if sub[TREAT].nunique() < 2:
                                    qc[qq] = np.nan
                                    continue
                                Xq = sm.add_constant(
                                    sub[[TREAT, '_pre'] + CTRL].astype(float))
                                fq = sm.OLS(sub['_dv'].astype(float), Xq).fit()
                                qc[qq] = fq.params[TREAT]
                            grad_rows.append(dict(
                                anchor=anchor, basis=basis, L=Lw, gap=gp,
                                q1=round(qc[1], 3) if pd.notna(qc[1]) else np.nan,
                                q2=round(qc[2], 3) if pd.notna(qc[2]) else np.nan,
                                q3=round(qc[3], 3) if pd.notna(qc[3]) else np.nan,
                                q4=round(qc[4], 3) if pd.notna(qc[4]) else np.nan))

# GARCH rows: reuse the stored GARCH DV (notification-anchored) + note
gd = fin.dropna(subset=['garch_dv'])
f_g, _ = run_spec(fin['garch_dv'], fin['e2_pre_sd'], fin)
grid_rows.append(dict(anchor='notification', basis='trading', L=21, gap=5,
                      returns='log', winsor='raw', estimator='GARCH(1,1)',
                      n=int(f_g.nobs), coef=round(f_g.params[TREAT], 4),
                      se=round(f_g.bse[TREAT], 4),
                      p=round(f_g.pvalues[TREAT], 4)))
grid = pd.DataFrame(grid_rows)
grid = grid.sort_values('coef').reset_index(drop=True)
grid.to_csv(OUTDIR / 't29_spec_grid.csv', index=False)

# ---------------- F1 reporting ----------------
log(f'\n## F1 — Specification grid: {len(grid)} specifications')
log(f"  coef distribution (daily pp): min {grid['coef'].min():+.3f} | p25 "
    f"{grid['coef'].quantile(.25):+.3f} | median {grid['coef'].median():+.3f} "
    f"| p75 {grid['coef'].quantile(.75):+.3f} | max {grid['coef'].max():+.3f}")
sig = grid[grid['p'] < .05]
log(f"  p<.05: {len(sig)}/{len(grid)} ({100 * len(sig) / len(grid):.1f}%), all "
    f"{'positive' if (sig['coef'] > 0).all() else 'MIXED SIGN' if len(sig) else 'n/a'}")
log(f"  sign: {100 * (grid['coef'] > 0).mean():.0f}% of specs positive")
draft = grid[(grid.anchor == 'notification') & (grid.basis == 'trading')
             & (grid.L == 21) & (grid.gap == 5) & (grid.returns == 'log')
             & (grid.winsor == 'raw') & (grid.estimator == 'SD')]
if len(draft):
    rank = int((grid['coef'] < draft['coef'].iloc[0]).sum())
    log(f"  draft-spec position: coef {draft['coef'].iloc[0]:+.4f} sits at "
        f"percentile {100 * rank / len(grid):.0f} of the distribution "
        f"(p={draft['p'].iloc[0]:.3f})")
# node influence: mean |coef| difference across each axis
log('\n  Node influence (range of mean coef across the node\'s options):')
infl = {}
for node in ['anchor', 'basis', 'L', 'gap', 'returns', 'winsor']:
    mm = grid[grid.estimator == 'SD'].groupby(node)['coef'].mean()
    infl[node] = mm.max() - mm.min()
    log(f"    {node:8s}: {infl[node]:.4f} daily pp  "
        f"({'; '.join(f'{k}={v:+.3f}' for k, v in mm.items())})")
top_node = max(infl, key=infl.get)
log(f"  Largest single decision node: {top_node.upper()} "
    f"({'confirms' if top_node == 'anchor' else 'CORRECTS'} the expectation "
    f"that anchor moves the estimate most).")
# significant-cell context
if len(sig):
    log('\n  Significant cells with their decision paths (family = '
        f'{len(grid)} specifications; multiplicity: at alpha=.05 one '
        f'expects ~{0.05 * len(grid):.0f} by chance):')
    for _, r in sig.iterrows():
        log(f"    {r['anchor']}/{r['basis']}/L{r['L']}/g{r['gap']}/"
            f"{r['returns']}/{r['winsor']}/{r['estimator']}: "
            f"{r['coef']:+.3f} (p={r['p']:.3f})")
# DV correlation matrix (key variants)
variants = {}
for lab, key in [('notif_t_21_5', ('notification', 'trading', 21, 5, 'log')),
                 ('notif_t_31_3', ('notification', 'trading', 31, 3, 'log')),
                 ('notif_t_42_5', ('notification', 'trading', 42, 5, 'log')),
                 ('notif_c_31_0', ('notification', 'calendar', 31, 0, 'log')),
                 ('breach_t_21_5', ('breach', 'trading', 21, 5, 'log')),
                 ('breach_c_31_0', ('breach', 'calendar', 31, 0, 'log'))]:
    variants[lab] = pd.Series(
        {i: sd_store[(i, *key)][1] - sd_store[(i, *key)][0]
         for i in fin.index if (i, *key) in sd_store})
vdf = pd.DataFrame(variants)
vdf['garch_notif'] = fin['garch_dv']
vdf['canonical_ann_breach'] = fin['volatility_change'] / np.sqrt(252)
corr = vdf.corr().round(3)
log('\n  DV-variant correlation matrix (extends the r=0.45 finding):')
log(corr.to_string())
corr.to_csv(OUTDIR / 't30_dv_correlations.csv')
log('\n  F3 node classification (Del Giudice & Gangestad 2021): anchor = '
    'TYPE N (breach-anchoring construct-invalid per Part A; shown as '
    'documentation, not pooled); basis, L, gap, returns = Type E '
    '(principled equivalence); winsor = Type U (genuine uncertainty). '
    'Units axis excluded as a pure rescaling.')
log('  F2: no joint permutation test is run (Semken & Rossell 2022: SCA '
    'median test Type I error can reach 1). Dispersion is the finding; '
    'framed as non-standard errors (Menkveld et al. 2024: NSE ~2.7x '
    'sampling SE; Mitton 2022: 73% of random variables significant under '
    'routine method variation).')

# ---------------- B3: gradient across the grid ----------------
gr = pd.DataFrame(grad_rows).dropna()
gr['q1_gt_q4'] = gr['q1'] > gr['q4']
gr['monotone_down'] = (gr['q1'] > gr['q2']) & (gr['q2'] > gr['q3']) & (gr['q3'] > gr['q4'])
gr.to_csv(OUTDIR / 't31_gradient_grid.csv', index=False)
log(f'\n## B3 — Gradient across the corrected-data grid ({len(gr)} '
    f'window-specs, log returns, raw DV):')
log(f"  Q1>Q4 (small-firm effect exceeds large-firm): "
    f"{100 * gr['q1_gt_q4'].mean():.0f}% of specs")
log(f"  strictly monotone step-down Q1>Q2>Q3>Q4 (the old draft's claim): "
    f"{100 * gr['monotone_down'].mean():.0f}% of specs")
by_anchor = gr.groupby('anchor')[['q1_gt_q4', 'monotone_down']].mean().round(2)
log(by_anchor.to_string())
log('  On the PRE-DEDUP vintage the grid cannot be rebuilt (no committed '
    'security-day link for the retired record set) — the uncorrected side '
    'of B3 is the fixed-spec four-panel below, stated as such. Harvey\'s '
    'refutation-hurdle point cuts both ways and is honored by reporting '
    'the full surface rather than the single flipping cell.')

# ---------------- B1: four-panel decomposition ----------------
log('\n## B1 — Four-panel decomposition of the gradient reversal')
log('  Named prior specification: the draft\'s own published quartile '
    'specification (the direct object of replication); Doyle & Magilke '
    '(2013 JAR) engaged in text as the deadline-heterogeneity precedent '
    '(their 10-K acceleration setting has no analogue sample here).')
old = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv',
                  low_memory=False)
s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
treated_ciks = set(ev.loc[ev[TREAT] == 1, 'final_cik'].astype(int))
# record -> final_cik (key join; normalize date strings — stage2_signed
# carries a 00:00:00 time suffix)
key = ['org_name', 'breach_date', 'reported_date']
for df_ in (old, s2):
    for c in ['breach_date', 'reported_date']:
        df_[c] = pd.to_datetime(df_[c], errors='coerce').dt.strftime('%Y-%m-%d')
s2k = s2.drop_duplicates(subset=key)[key + ['final_cik']]
old2 = old.merge(s2k, on=key, how='left')
log(f'  (record->CIK key join: {int(old2["final_cik"].notna().sum())}/1054 '
    f'records matched)')
# JOIN-GAP REPAIR (9/2/2026): the record->CIK join yields stage-2 CIKs, but
# treated_ciks holds POST-reparenting canonical CIKs (scripts/154:168-177
# EQUITY_PARENT). Without the map, 15 genuinely treated-family records
# (14 Comcast + 1 NBCUniversal) are coded control in panel (ii). Map first.
EQUITY_PARENT = {1040573: 1166691, 1512267: 1166691, 1457937: 1105705}
old2['final_cik_rep'] = old2['final_cik'].map(
    lambda c: EQUITY_PARENT.get(int(c), int(c)) if pd.notna(c) else np.nan)
old2['form499_family'] = old2['final_cik_rep'].isin(treated_ciks).astype(float)
# event-level record-modal SIC (via nearest-event mapping within final_cik)
s2['sic_num'] = pd.to_numeric(s2['sic'], errors='coerce')
s2['bdt'] = pd.to_datetime(s2['breach_date'], errors='coerce')
sic_map = {}
for cik, g in s2.dropna(subset=['final_cik']).groupby('final_cik'):
    sic_map[cik] = g.dropna(subset=['sic_num'])
SICSET = {4813, 4841, 4899}


def event_sic_treated(cik, bdt):
    g = sic_map.get(cik)
    if g is None or not len(g):
        return np.nan
    g = g.assign(_d=(g['bdt'] - bdt).abs())
    near = g[g['_d'] <= timedelta(days=3)]
    pool = near if len(near) else g.nsmallest(1, '_d')
    return float(any(int(s_) in SICSET for s_ in pool['sic_num'].dropna()))


ev['sic_treated'] = [event_sic_treated(c, b) for c, b in zip(ev['final_cik'], ev['bdt'])]
OXS = ['return_volatility_pre', 'firm_size_log', 'leverage', 'roa',
       'disclosure_delay_days', 'prior_breaches_total', 'health_breach']


def panel(d, tcol, label):
    d = d[[tcol, 'volatility_change'] + OXS].dropna().copy()
    d = d.rename(columns={tcol: '_t'})
    X = sm.add_constant(d[['_t'] + OXS].astype(float))
    f = sm.OLS(d['volatility_change'].astype(float), X).fit(cov_type='HC3',
                                                            use_t=True)
    d['q'] = pd.qcut(d['firm_size_log'], 4, labels=[1, 2, 3, 4])
    qc = []
    for qq in [1, 2, 3, 4]:
        sub = d[d['q'] == qq]
        if sub['_t'].nunique() < 2:
            qc.append(np.nan)
            continue
        fq = sm.OLS(sub['volatility_change'].astype(float),
                    sm.add_constant(sub[['_t'] + OXS].astype(float))).fit(
            cov_type='HC3', use_t=True)
        qc.append(fq.params['_t'])
    row = dict(panel=label, n=int(f.nobs), n_treated=int(d['_t'].sum()),
               main=round(f.params['_t'], 3), main_se=round(f.bse['_t'], 3),
               q1=round(qc[0], 2) if pd.notna(qc[0]) else np.nan,
               q2=round(qc[1], 2) if pd.notna(qc[1]) else np.nan,
               q3=round(qc[2], 2) if pd.notna(qc[2]) else np.nan,
               q4=round(qc[3], 2) if pd.notna(qc[3]) else np.nan)
    log(f"  {label}: main {row['main']:+.3f} (SE {row['main_se']}) | "
        f"Q1..Q4: {row['q1']}, {row['q2']}, {row['q3']}, {row['q4']} | "
        f"N={row['n']} ({row['n_treated']} treated)")
    return row


old_crsp = old2[old2['has_crsp_data'] == True].copy()
old_crsp['sic_reportable'] = old_crsp['fcc_reportable'].astype(float)
panels = [
    panel(old_crsp, 'sic_reportable', '(i)  pre-dedup + SIC treatment'),
    panel(old_crsp, 'form499_family', '(ii) pre-dedup + Form 499 (family-level reconstruction)'),
    panel(ev.assign(volatility_change=ev['volatility_change']),
          'sic_treated', '(iii) dedup + SIC treatment (record-modal SIC)'),
    panel(ev.assign(_f=ev[TREAT].astype(float)), '_f',
          '(iv) dedup + Form 499 (canonical)'),
]
pd.DataFrame(panels).to_csv(OUTDIR / 't32_four_panel.csv', index=False)
log('  READING: compare (i)->(ii) [treatment reclassification holding the '
    'record-level data] against (i)->(iii) [deduplication holding SIC '
    'treatment] to see which decision does the work in killing the '
    'step-down. Reconstruction approximations for (ii)/(iii) are stated in '
    'the header. Genre precedents: Karpoff & Wittry 2018 (legal-context '
    'reclassification); Karpoff et al. 2017 (database substitution, 39% '
    'replication).')

# ---------------- H2: winsorization sensitivity ----------------
log('\n## H2 — Winsorization sensitivity (headline spec)')
h2 = []
for lab, lo, hi in [('raw', None, None), ('1/99', .01, .99), ('5/95', .05, .95)]:
    d = fin.copy()
    dv = d['e2_vol_change']
    if lo:
        dv = dv.clip(dv.quantile(lo), dv.quantile(hi))
        for c in ['e2_pre_sd', 'firm_size_log', 'leverage', 'roa', 'delay_w',
                  'prior_events']:
            d[c] = d[c].clip(d[c].quantile(lo), d[c].quantile(hi))
    X = sm.add_constant(d[[TREAT, 'e2_pre_sd', 'delay_w', 'firm_size_log',
                           'leverage', 'roa', 'health_breach',
                           'prior_events']].astype(float))
    f = sm.OLS(dv.astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': d['final_cik']}, use_t=True)
    ci = f.conf_int().loc[TREAT]
    h2.append(dict(winsor=lab, coef=round(f.params[TREAT], 4),
                   se=round(f.bse[TREAT], 4), ci_lo=round(ci[0], 4),
                   ci_hi=round(ci[1], 4)))
    log(f"  {lab}: coef {f.params[TREAT]:+.4f} SE {f.bse[TREAT]:.4f} "
        f"95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}] (CV1 parent-CIK)")
pd.DataFrame(h2).to_csv(OUTDIR / 't33_winsor_sensitivity.csv', index=False)

log(f'\nGrid = {len(grid)} descriptive specifications (0 hypothesis tests); '
    f'B1 = 4 panels x (1 main + 4 quartiles) = 20 estimates reported as '
    f'one decomposition family; H2 = 3 sensitivity rows of the single '
    f'main-effect hypothesis.')
Path('outputs/ESSAY2_QUERY4_PART_FB.md').write_text(
    '# Essay 2 Query 4 — Parts F & B (computed live)\n\n' + '\n'.join(L) + '\n',
    encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY4_PART_FB.md + t29-t33 CSVs')
