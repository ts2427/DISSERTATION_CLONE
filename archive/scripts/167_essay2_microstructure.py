"""
ESSAY 2 QUERY 4 — PART G: MICROSTRUCTURE OUTCOMES (spreads, price impact)
==========================================================================
BLOCKED ON WRDS LOGIN: the committed CRSP extract carries only
[permno, date, ret, vol] — no BID/ASK/PRC/OPENPRC/BIDLO/ASKHI. This script
(1) pulls the needed daily fields for the sample permnos into a separate
top-up file (committed extracts untouched, house convention), then
(2) computes the three pre-specified outcomes and their regressions.

Run interactively (WRDS prompts for the password of user 'tispivey'):
    python scripts/167_essay2_microstructure.py

Outcomes (secondary, reported as a set; multiplicity: Benjamini-Hochberg
across the three):
  1. CPQS  = (ASK-BID)/midpoint, closing quotes (Chung & Zhang 2014;
     best daily percent-cost proxy, Fong-Holden-Trzcinka 2017).
  2. EDGE  (Ardia, Guidotti & Kroencke 2024 JFE) via the authors' bidask
     package — NOT hand-coded; signed estimates kept (sign=True), averaged
     within window, no pre-averaging truncation (truncation manufactures a
     spurious effect with the predicted sign — stated in methods).
  3. OCAM  open-to-close Amihud (Barardehi et al. 2021 RAPS):
     |C-O|/O / dollar volume, winsorized 1/99 within period cross-section,
     then logged.
Windows: trading days [-52,-11] pre and [+11,+52] post around the
notification anchor (announcement window excluded; Bohmann et al. 2019;
estimator noise ~ 1/sqrt(T)). Market adjustment: notification
calendar-month fixed effects in every regression (spreads have large
common time variation; the sample spans 2008 and 2020). Inference: CV1
clustered at parent CIK. Coverage diagnostics, crossed/locked-quote
filters, and negative-estimate rates reported first. Firm-level inference
is NOT supported (EDGE SD at true spread 0.5%/21d is ~0.34pp) —
cross-sectional statements only. No adverse-selection decomposition is
claimed: total spread and price impact only (Part G4).
Not built (G5): Roll, Amivest, Zeros/FHT/LOT, Gibbs, Effective Tick,
Parkinson-as-liquidity, turnover-as-adverse-selection.

Outputs: Data/wrds/crsp_quotes_topup.csv (cache; pull once),
         outputs/ESSAY2_QUERY4_PART_G.md + t34-t36 CSVs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
QFILE = Path('Data/wrds/crsp_quotes_topup.csv')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
fin['rdt'] = pd.to_datetime(fin['reported_date'])
permnos = sorted(set(int(p) for p in fin['permno'].dropna()))

# ------------------------- pull (once, cached) ------------------------------
if not QFILE.exists():
    import wrds
    db = wrds.Connection(wrds_username='tispivey')
    lo = (fin['rdt'].min() - pd.Timedelta(days=130)).date()
    hi = (fin['rdt'].max() + pd.Timedelta(days=130)).date()
    q = f"""
        select permno, date, bid, ask, prc, openprc, bidlo, askhi, vol, shrout,
               hexcd
        from crsp.dsf
        where permno in ({','.join(map(str, permnos))})
          and date between '{lo}' and '{hi}'
    """
    df = db.raw_sql(q)
    df.to_csv(QFILE, index=False)
    print(f'Pulled {len(df):,} rows -> {QFILE}')
    db.close()

qd = pd.read_csv(QFILE, low_memory=False)
qd['date'] = pd.to_datetime(qd['date'])
for c in ['bid', 'ask', 'prc', 'openprc', 'bidlo', 'askhi', 'vol', 'shrout']:
    qd[c] = pd.to_numeric(qd[c], errors='coerce')

log('=' * 90)
log('ESSAY 2 QUERY 4 — PART G: MICROSTRUCTURE (N=%d events)' % len(fin))
log('=' * 90)

# ---------------- G1: coverage diagnostics FIRST ----------------
qd['year'] = qd['date'].dt.year
qd['valid_quote'] = (qd['bid'].notna() & qd['ask'].notna()
                     & (qd['ask'] > qd['bid']) & (qd['bid'] > 0))
qd['crossed'] = qd['bid'].notna() & qd['ask'].notna() & (qd['ask'] <= qd['bid'])
qd['cpqs'] = np.where(qd['valid_quote'],
                      (qd['ask'] - qd['bid']) / ((qd['ask'] + qd['bid']) / 2),
                      np.nan)
qd.loc[qd['cpqs'] > 0.5, 'cpqs'] = np.nan   # implausible-spread filter, stated
cov = qd.groupby('year').agg(days=('date', 'size'),
                             pct_valid=('valid_quote', 'mean'),
                             pct_crossed=('crossed', 'mean'),
                             pct_open=('openprc', lambda s: s.notna().mean()))
cov[['pct_valid', 'pct_crossed', 'pct_open']] = (
    100 * cov[['pct_valid', 'pct_crossed', 'pct_open']]).round(1)
log('\n## G1 — Coverage by year (% firm-days):')
log(cov.to_string())
cov.to_csv(OUTDIR / 't34_g1_coverage.csv')
log(f"  Overall: {100 * qd['valid_quote'].mean():.1f}% valid uncrossed "
    f"closing quotes; OPENPRC populated {100 * qd['openprc'].notna().mean():.1f}% "
    f"— CPQS is the primary microstructure outcome (premise correct: CRSP "
    f"daily carries closing BID/ASK).")

# ---------------- G2: build outcomes per event ----------------
from bidask import edge

PRE_LO, PRE_HI, POST_LO, POST_HI = -52, -11, 11, 52
PG = {p: g.sort_values('date').reset_index(drop=True)
      for p, g in qd.groupby('permno')}
rows = []
neg_edge = [0, 0]
for i, r in fin.iterrows():
    g = PG.get(int(r['permno']) if pd.notna(r['permno']) else -1)
    if g is None:
        continue
    gaps = (g['date'] - r['rdt']).abs()
    pos = int(gaps.idxmin())
    if gaps.iloc[pos] > pd.Timedelta(days=7):
        continue
    out = dict(idx=i)
    for wlab, lo_, hi_ in [('pre', PRE_LO, PRE_HI), ('post', POST_LO, POST_HI)]:
        w = g.iloc[max(0, pos + lo_): pos + hi_ + 1]
        w = w[(w['prc'] > 0) & (w['vol'] > 0)]  # directive: PRC>0, VOL>0
        if len(w) < 25:
            continue
        out[f'cpqs_{wlab}'] = w['cpqs'].mean()
        try:
            e = edge(w['openprc'], w['askhi'], w['bidlo'], abs(w['prc']),
                     sign=True)
        except Exception:
            e = np.nan
        out[f'edge_{wlab}'] = e
        if pd.notna(e) and e < 0:
            neg_edge[0 if wlab == 'pre' else 1] += 1
        dvol = (abs(w['prc']) * w['vol']).replace(0, np.nan)
        ocam = (abs(abs(w['prc']) - w['openprc']) / w['openprc']) / dvol
        out[f'ocam_{wlab}'] = ocam.mean() * 1e6
    rows.append(out)
ms = pd.DataFrame(rows).set_index('idx')
for v in ['cpqs', 'edge', 'ocam']:
    if f'{v}_pre' not in ms.columns:
        continue
    if v == 'ocam':
        for w in ['pre', 'post']:
            s = ms[f'ocam_{w}']
            ms[f'ocam_{w}'] = np.log(s.clip(s.quantile(.01), s.quantile(.99)))
    ms[f'{v}_chg'] = ms[f'{v}_post'] - ms[f'{v}_pre']
D = fin.join(ms, how='inner')
n_ms = D[['cpqs_chg', 'edge_chg', 'ocam_chg']].notna().sum()
log(f'\n## G2 — Outcomes built: N with CPQS {n_ms["cpqs_chg"]}, EDGE '
    f'{n_ms["edge_chg"]}, OCAM {n_ms["ocam_chg"]}')
log(f'  EDGE negative-estimate rate (signed kept, stated): pre '
    f'{neg_edge[0]}, post {neg_edge[1]} of {len(ms)} windows.')

# ---------------- G2 regressions (month FE, CV1 parent) ----------------
D['month'] = D['rdt'].dt.to_period('M').astype(str)
CTRL = ['e2_pre_sd', 'delay_w', 'firm_size_log', 'leverage', 'roa',
        'health_breach', 'prior_events']
res = []
for v, lab in [('cpqs_chg', 'CPQS change'), ('edge_chg', 'EDGE change'),
               ('ocam_chg', 'log-OCAM change')]:
    d = D.dropna(subset=[v] + CTRL)
    mfe = pd.get_dummies(d['month'], drop_first=True).astype(float)
    X = sm.add_constant(pd.concat([d[[TREAT] + CTRL].astype(float), mfe], axis=1))
    f = sm.OLS(d[v].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': d['final_cik']}, use_t=True)
    ci = f.conf_int().loc[TREAT]
    res.append(dict(outcome=lab, coef=f.params[TREAT], se=f.bse[TREAT],
                    ci_lo=ci[0], ci_hi=ci[1], p=f.pvalues[TREAT],
                    n=int(f.nobs),
                    n_treated=int(d[TREAT].sum()),
                    G=d['final_cik'].nunique()))
    log(f"  {lab}: coef {f.params[TREAT]:+.5f} SE {f.bse[TREAT]:.5f} 95% CI "
        f"[{ci[0]:+.5f}, {ci[1]:+.5f}] N={int(f.nobs)} "
        f"({int(d[TREAT].sum())} treated, G={d['final_cik'].nunique()}; "
        f"month FE; CV1 parent-CIK)")
R = pd.DataFrame(res)
# BH across the three secondary outcomes
R = R.sort_values('p').reset_index(drop=True)
R['bh_threshold'] = [0.05 * (i + 1) / len(R) for i in range(len(R))]
R['bh_reject'] = R['p'] <= R['bh_threshold']
log('\n  Multiplicity (stated): 3 secondary outcomes, Benjamini-Hochberg '
    'at FDR 5%:')
log(R[['outcome', 'p', 'bh_threshold', 'bh_reject']].round(4).to_string(index=False))
R.round(6).to_csv(OUTDIR / 't35_microstructure.csv', index=False)

# correlations with the volatility DV + Koski note
cors = D[['e2_vol_change', 'cpqs_chg', 'edge_chg', 'ocam_chg']].corr().round(3)
log('\n  Correlation of microstructure changes with the volatility DV '
    '(was volatility a reasonable proxy?):')
log(cors.to_string())
cors.to_csv(OUTDIR / 't36_ms_vol_correlation.csv')
log('  Koski (2007): bid-ask bounce biases measured return volatility '
    'upward, more for low-priced stocks — a pre/post change in measured '
    'volatility can itself be a spread artifact; the measures are '
    'reported side by side, volatility retained.')
log('\n  G4 framing: total effective spread and price impact only — no '
    'adverse-selection decomposition is claimed (requires signed trades / '
    'intraday data). These are secondary outcomes; not candidate '
    'headlines. Precedents: Frino, Gaudiosi & Mollica (2026 A&F) — '
    'persistently wider spreads after cyber attacks, smaller for large '
    'firms; Katselas, Sidhu & Yu (2020 A&F) window architecture.')

Path('outputs/ESSAY2_QUERY4_PART_G.md').write_text(
    '# Essay 2 Query 4 — Part G (computed live)\n\n' + '\n'.join(L) + '\n',
    encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY4_PART_G.md + t34-t36 CSVs')
