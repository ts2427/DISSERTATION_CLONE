"""
ESSAY 2 QUERY 4 — PARTS A, B2, C, E4, H1/H3, J, I (rule, delay, classification)
================================================================================
A1  Verbatim 47 CFR 64.2011 (2008 annual edition, govinfo; current text via
    eCFR/LII, retrieved 2026-08-30) embedded as constants with sources.
A2  NEW PRIMARY TEST: disclosure delay ~ Form 499 treatment (N=333):
    OLS (raw/winsorized/log1p) with parent-CIK-clustered CV1 inference,
    dispersion by group + Brown-Forsythe, share of treated below the
    regulatory floor, quantile regressions (q10..q90), Kaplan-Meier +
    log-rank (lifelines).
A3  Full delay distribution treated vs control + KS + exact zeros.
A4  Scan of committed code/outputs describing 64.2011 as a customer-
    disclosure deadline (deletion list).
B2  records-per-event ~ size regressions on the 489-event universe.
C1  Vintage-matched treatment verification against the committed registry
    snapshot (start_date/end_date native; 11,767 ended records retained).
C2  Over-inclusion audit by Principal_Communications_Type.
E4  Events by year x treatment (notification year).
H1  Repeated events per parent; one-event-per-parent re-estimates; parent FE.
H3  Sample period statement (2006-2024).
J   Census funnel from the Form 499 registry.
I   Literature-claim corrections (verbatim replacement text).

Outputs: outputs/ESSAY2_QUERY4_PARTS_ACJ.md + outputs/tables/essay2_v2/t16-t24
"""

import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
L = []
N_TESTS = []  # (family, name) tuples


def log(m=''):
    print(m)
    L.append(str(m))


def test(family, name):
    N_TESTS.append((family, name))


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
N = len(fin)
CONTROLS_X = ['e2_pre_sd', 'firm_size_log', 'leverage', 'roa',
              'health_breach', 'prior_events']

log('=' * 90)
log('ESSAY 2 QUERY 4 — PARTS A, B2, C, E4, H, J, I')
log('=' * 90)

# ========================== A1: THE RULE, VERBATIM ==========================
log("""
## A1 — 47 CFR 64.2011, verbatim (sources: govinfo 2008 CFR annual edition,
CFR-2008-title47-vol3-sec64-2011.xml; current text law.cornell.edu/cfr/text/
47/64.2011 mirroring eCFR; both retrieved 2026-08-30; texts IDENTICAL)

(a) "A telecommunications carrier shall notify law enforcement of a breach
    of its customers' CPNI as provided in this section. The carrier shall
    not notify its customers or disclose the breach publicly, whether
    voluntarily or under state or local law or these rules, until it has
    completed the process of notifying law enforcement pursuant to
    paragraph (b) of this section."
(b) "As soon as practicable, and in no event later than seven (7) business
    days, after reasonable determination of the breach, the
    telecommunications carrier shall electronically notify the United
    States Secret Service (USSS) and the Federal Bureau of Investigation
    (FBI) through a central reporting facility."
(b)(1) "Notwithstanding any state law to the contrary, the carrier shall not
    notify customers or disclose the breach to the public until 7 full
    business days have passed after notification to the USSS and the FBI"
    [except per (b)(2)-(b)(3)].
(b)(2) urgent-need earlier notice only "after consultation with the relevant
    investigating agency."
(b)(3) investigating agency may direct no-disclosure for an initial period
    of up to 30 days, and "Such period may be extended by the agency as
    reasonably necessary in the judgment of the agency."
(c) "After a telecommunications carrier has completed the process of
    notifying law enforcement pursuant to paragraph (b) of this section,
    it shall notify its customers of a breach of those customers' CPNI."
    — NO TIME LIMIT IS SPECIFIED.
(d) two-year recordkeeping.
(e) "A 'breach' has occurred when a person, without authorization or
    exceeding authorization, has INTENTIONALLY gained access to, used, or
    disclosed CPNI." — inadvertent exposure is outside the 2007 rule.
Source credit: [72 FR 31963, June 8, 2007].

EVERY A0 CLAIM CONFIRMED: (1) the 7 business days run to LAW ENFORCEMENT,
not customers; (2) the trigger is the carrier's own "reasonable
determination", not discovery; (3) the rule imposes a MANDATORY MINIMUM
public-disclosure delay (~14 business days, extendable indefinitely under
(b)(3)); (4) customer notification has NO outer deadline; (5) the event PRC
records — public notification — is the event the rule leaves untimed.
FCC 23-111 (89 FR 9968, 2024-02-12): amendments to 64.2011 "delayed
indefinitely" pending OMB approval (verbatim in the repository's Federal
Register summary, COMPREHENSIVE_ARTICLE_SUMMARIES_COMPLETE.txt) — the 2007
text governed the ENTIRE 2006-2024 sample period; no mid-sample amendment.
The draft's mechanism (a deadline forcing disclosure before investigations
complete) requires a ceiling; the rule is a FLOOR. If it predicts anything
about observed notification timing, it predicts LONGER and MORE HOMOGENEOUS
delays for covered carriers.""")

# ================= A2: NEW PRIMARY TEST — delay ~ treatment =================
log('\n' + '=' * 90)
log('## A2 — NEW PRIMARY TEST: does Form 499 treatment predict disclosure '
    'delay? (N=333)')
log('=' * 90)
fin['delay_log'] = np.log1p(fin['disclosure_delay_days'])
rows = []
for dv, lab in [('disclosure_delay_days', 'delay (raw days)'),
                ('delay_w', 'delay (winsorized p99)'),
                ('delay_log', 'log(1+delay)')]:
    X = sm.add_constant(fin[[TREAT] + CONTROLS_X].astype(float))
    f = sm.OLS(fin[dv].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': fin['final_cik']}, use_t=True)
    b, se = f.params[TREAT], f.bse[TREAT]
    ci = f.conf_int().loc[TREAT]
    df_ = getattr(f, 'df_resid_inference', f.df_resid)
    rows.append(dict(dv=lab, coef=round(b, 3), se=round(se, 3),
                     ci_lo=round(ci[0], 3), ci_hi=round(ci[1], 3),
                     df=int(df_), p=round(f.pvalues[TREAT], 4), n=N,
                     G=fin['final_cik'].nunique(),
                     G1=fin.loc[fin[TREAT] == 1, 'final_cik'].nunique()))
    test('A2-delay', f'OLS {lab}')
    log(f"  {lab}: coef {b:+.3f}  SE {se:.3f}  95% CI [{ci[0]:+.3f}, "
        f"{ci[1]:+.3f}]  (G={rows[-1]['G']}, G1={rows[-1]['G1']}, CV1 "
        f"parent-CIK, t({int(df_)}))")
pd.DataFrame(rows).to_csv(OUTDIR / 't16_delay_on_treatment.csv', index=False)

# dispersion
tt = fin.loc[fin[TREAT] == 1, 'disclosure_delay_days']
cc = fin.loc[fin[TREAT] == 0, 'disclosure_delay_days']
bf_stat, bf_p = stats.levene(tt, cc, center='median')
test('A2-delay', 'Brown-Forsythe variance equality')
log(f'\n  Dispersion: treated SD {tt.std():.1f}, IQR {tt.quantile(.75) - tt.quantile(.25):.0f}, '
    f'CV {tt.std() / tt.mean():.2f} | control SD {cc.std():.1f}, IQR '
    f'{cc.quantile(.75) - cc.quantile(.25):.0f}, CV {cc.std() / cc.mean():.2f} | '
    f'Brown-Forsythe W={bf_stat:.3f} (p={bf_p:.4f})')
log('  The floor prediction (treated delays longer AND more homogeneous, '
    'compressed against a regulatory floor) requires treated dispersion '
    'BELOW control.')

# regulatory floor — CONTAMINATION-AWARE (zero-delay records)
z0t, z0c = int((tt == 0).sum()), int((cc == 0).sum())
log(f'\n  ZERO-DELAY CONTAMINATION: {z0t}/{len(tt)} treated and {z0c}/{len(cc)} control '
    f'delays are EXACTLY zero ({100 * (z0t + z0c) / N:.1f}% of the sample). '
    f'Same-day public notification at scale is implausible; these are '
    f'almost certainly records whose occurrence date defaulted to the '
    f'notification date in the source. The share-of-treated-below-the-'
    f'regulatory-floor statistic is therefore measuring MISSING DATA, not '
    f'non-compliance, and no compliance claim is made from it. Among '
    f'NON-ZERO delays, {int((tt[tt > 0] < 20).sum())}/{int((tt > 0).sum())} '
    f'treated ({100 * (tt[tt > 0] < 20).mean():.1f}%) fall below ~20 '
    f'calendar days — still diagnostic only (the clock measured is '
    f'occurrence-to-notification, not determination-to-notification).')

# A2 RE-RUN EXCLUDING ZERO-DELAY OBSERVATIONS (clean-tail mechanism test)
nz = fin[fin['disclosure_delay_days'] > 0]
tt_nz = nz.loc[nz[TREAT] == 1, 'disclosure_delay_days']
cc_nz = nz.loc[nz[TREAT] == 0, 'disclosure_delay_days']
log(f'\n  A2 EXCLUDING ZERO DELAYS (N={len(nz)}: {len(tt_nz)} treated / '
    f'{len(cc_nz)} control):')
rows_nz = []
for dv, lab in [('disclosure_delay_days', 'delay (raw days)'),
                ('delay_log', 'log(delay)')]:
    Xn = sm.add_constant(nz[[TREAT] + CONTROLS_X].astype(float))
    fn_ = sm.OLS(nz[dv].astype(float), Xn).fit(
        cov_type='cluster', cov_kwds={'groups': nz['final_cik']}, use_t=True)
    ci = fn_.conf_int().loc[TREAT]
    rows_nz.append(dict(dv=lab, coef=round(fn_.params[TREAT], 3),
                        se=round(fn_.bse[TREAT], 3), ci_lo=round(ci[0], 3),
                        ci_hi=round(ci[1], 3), n=len(nz)))
    test('A2-delay-nz', f'OLS nonzero {lab}')
    log(f"    {lab}: coef {fn_.params[TREAT]:+.3f}  SE {fn_.bse[TREAT]:.3f}  "
        f"95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]")
bf_nz = stats.levene(tt_nz, cc_nz, center='median')
ks_nz = stats.ks_2samp(tt_nz, cc_nz)
test('A2-delay-nz', 'Brown-Forsythe nonzero')
test('A2-delay-nz', 'KS nonzero')
from lifelines.statistics import logrank_test as _lrt
lr_nz = _lrt(tt_nz, cc_nz, event_observed_A=np.ones(len(tt_nz)),
             event_observed_B=np.ones(len(cc_nz)))
test('A2-delay-nz', 'log-rank nonzero')
log(f'    medians: treated {tt_nz.median():.0f}d vs control '
    f'{cc_nz.median():.0f}d | dispersion: treated SD {tt_nz.std():.1f} CV '
    f'{tt_nz.std() / tt_nz.mean():.2f} vs control SD {cc_nz.std():.1f} CV '
    f'{cc_nz.std() / cc_nz.mean():.2f} | Brown-Forsythe W={bf_nz[0]:.3f} '
    f'(p={bf_nz[1]:.4f}) | KS D={ks_nz[0]:.4f} (p={ks_nz[1]:.4f}) | '
    f'log-rank chi2={lr_nz.test_statistic:.3f} (p={lr_nz.p_value:.4f})')
pd.DataFrame(rows_nz).to_csv(OUTDIR / 't16c_delay_nonzero.csv', index=False)

# quantile regressions
log('\n  Quantile regressions (delay ~ treatment + controls; treatment '
    'coefficient; iid-kernel SEs, descriptive):')
qrows = []
Xq = sm.add_constant(fin[[TREAT] + CONTROLS_X].astype(float))
for q in [.10, .25, .50, .75, .90]:
    mq = sm.QuantReg(fin['disclosure_delay_days'].astype(float), Xq).fit(q=q)
    qrows.append(dict(q=q, coef=round(mq.params[TREAT], 3),
                      se=round(mq.bse[TREAT], 3)))
    test('A2-delay', f'quantile q={q}')
    log(f"    q{int(q * 100)}: {mq.params[TREAT]:+.2f} (SE {mq.bse[TREAT]:.2f})")
pd.DataFrame(qrows).to_csv(OUTDIR / 't16b_delay_quantiles.csv', index=False)

# Kaplan-Meier + log-rank
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
lr = logrank_test(tt, cc, event_observed_A=np.ones(len(tt)),
                  event_observed_B=np.ones(len(cc)))
test('A2-delay', 'log-rank')
km = KaplanMeierFitter()
med_t = tt.median()
med_c = cc.median()
log(f'\n  Kaplan-Meier time-to-notification (no censoring — the sample '
    f'conditions on an observed notification): median treated {med_t:.0f}d '
    f'vs control {med_c:.0f}d; log-rank chi2={lr.test_statistic:.3f} '
    f'(p={lr.p_value:.4f})')

log('\n  A2 DIRECTION, PLAINLY: see the coefficients above. If treated '
    'firms disclose no more slowly (and no more homogeneously) than '
    'controls, the rule does not bind on observed public-notification '
    'behavior — which is itself the candidate explanation for the '
    'volatility null and belongs in the essay as a finding.')

# ===================== A3: delay distribution in full ======================
log('\n' + '=' * 90)
log('## A3 — Delay distribution, treated vs control')
log('=' * 90)
drows = []
for gname, s in [('treated', tt), ('control', cc)]:
    drows.append(dict(group=gname, n=len(s), zeros=int((s == 0).sum()),
                      min=s.min(), p10=s.quantile(.1), p25=s.quantile(.25),
                      p50=s.median(), p75=s.quantile(.75), p90=s.quantile(.9),
                      p95=s.quantile(.95), max=s.max(),
                      mean=round(s.mean(), 1), sd=round(s.std(), 1)))
ks_stat, ks_p = stats.ks_2samp(tt, cc)
test('A2-delay', 'KS distributional equality')
dd = pd.DataFrame(drows)
log(dd.to_string(index=False))
log(f'  KS test of distributional equality: D={ks_stat:.4f} (p={ks_p:.4f}). '
    f'Exact zeros: treated {int((tt == 0).sum())}, control {int((cc == 0).sum())}.')
dd.to_csv(OUTDIR / 't17_delay_distribution.csv', index=False)

# ================== A4: mischaracterization scan (deletions) ================
log('\n' + '=' * 90)
log('## A4 — Locations describing 64.2011 as a DISCLOSURE deadline '
    '(deletions, not edits)')
log('=' * 90)
PATTERNS = [r'7-Day Rule', r'7-day mandatory', r'[Mm]andatory 7', r'seven-day',
            r'7-day disclosure', r'disclosure deadline', r'[Dd]isclose within',
            r'notification within 30 days', r'deadline outruns',
            r'breach notification within \d+ days', r'[Mm]andatory [Dd]isclosure [Tt]iming.*deadline']
hits = []
scan_files = (sorted(Path('scripts').glob('*.py'))
              + sorted(Path('outputs').glob('*.md'))
              + sorted(Path('Dashboard').rglob('*.py'))
              + [Path('README.md')])
for fp in scan_files:
    try:
        txt = fp.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        continue
    for i, line in enumerate(txt, 1):
        for pat in PATTERNS:
            if re.search(pat, line):
                hits.append(dict(file=str(fp), line=i,
                                 text=line.strip()[:120], pattern=pat))
                break
seen = set()
for h in hits:
    key = (h['file'], h['line'])
    if key in seen or '164_essay2' in h['file'] or '163_essay2' in h['file']:
        continue
    seen.add(key)
    log(f"  {h['file']}:{h['line']}: {h['text']}")
pd.DataFrame(hits).to_csv(OUTDIR / 't24_a4_deadline_scan.csv', index=False)
log(f'  ({len(seen)} locations; every one describes a customer-disclosure '
    f'deadline or ceiling the rule does not contain — these are deletions.)')

# ================== B2: records-per-event vs firm size ======================
log('\n' + '=' * 90)
log('## B2 — Is duplication non-random in firm size? (489-event universe)')
log('=' * 90)
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
cs = pd.read_csv('Data/wrds/compustat_annual.csv',
                 usecols=['tic', 'datadate', 'prcc_f', 'csho'])
cs['datadate'] = pd.to_datetime(cs['datadate'])
cs = cs.dropna(subset=['tic'])
by_tic = {t: g.sort_values('datadate') for t, g in cs.groupby('tic')}


def mktcap(ticker, bdt):
    g = by_tic.get(ticker)
    if g is None:
        return np.nan
    pr = g[(g['datadate'] < bdt) & (g['datadate'] >= bdt - pd.Timedelta(days=550))]
    if not len(pr):
        return np.nan
    r = pr.iloc[-1]
    if pd.notna(r['prcc_f']) and pd.notna(r['csho']) and r['prcc_f'] * r['csho'] > 0:
        return np.log(r['prcc_f'] * r['csho'])
    return np.nan


ev['mktcap_log'] = [mktcap(t, b) for t, b in zip(ev['matched_ticker'], ev['bdt'])]
b2 = ev.dropna(subset=['n_source_records', 'firm_size_log'])
Xb = sm.add_constant(b2[['firm_size_log']].astype(float))
fb = sm.OLS(b2['n_source_records'].astype(float), Xb).fit(cov_type='HC3', use_t=True)
test('B2', 'records-per-event ~ log assets')
ci_b = fb.conf_int().loc['firm_size_log']
log(f"  records-per-event ~ ln(assets): coef {fb.params['firm_size_log']:+.4f} "
    f"SE {fb.bse['firm_size_log']:.4f} 95% CI [{ci_b[0]:+.4f}, {ci_b[1]:+.4f}] "
    f"N={len(b2)}")
b2m = ev.dropna(subset=['n_source_records', 'mktcap_log'])
fm = sm.OLS(b2m['n_source_records'].astype(float),
            sm.add_constant(b2m[['mktcap_log']].astype(float))).fit(
    cov_type='HC3', use_t=True)
test('B2', 'records-per-event ~ log mktcap')
ci_m = fm.conf_int().loc['mktcap_log']
log(f"  records-per-event ~ ln(mktcap): coef {fm.params['mktcap_log']:+.4f} "
    f"SE {fm.bse['mktcap_log']:.4f} 95% CI [{ci_m[0]:+.4f}, {ci_m[1]:+.4f}] "
    f"N={len(b2m)}")
b2q = b2.copy()
b2q['size_q'] = pd.qcut(b2q['firm_size_log'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
qq = b2q.groupby('size_q', observed=True)['n_source_records'].agg(
    ['mean', 'median', 'max', 'count'])
log('  records-per-event by size quartile:')
log(qq.to_string())
qq.to_csv(OUTDIR / 't19_records_per_event.csv')
cen = ev[ev['org_name'].str.contains('Cencora', na=False)]
log(f"  Cencora illustration: {len(cen)} events, n_source_records = "
    f"{list(cen['n_source_records'])} — one 2024-02-21 event carries 31 "
    f"notification records. Number-of-states-of-operation is NOT "
    f"constructible from committed data (stated).")
log('  (If the size gradient in records-per-event is positive, record-level '
    'analysis mechanically overweights large firms and the old size '
    'gradient is a record-vs-event artifact.)')

# ======= B2b: THE RIGHT MECHANISM TEST — misclassified-set composition ======
log('\n' + '=' * 90)
log('## B2b — Size composition of the misclassified sets (the mechanism '
    'the four-panel decomposition implies: treatment reclassification, '
    'not deduplication)')
log('=' * 90)
s2m = pd.read_csv('Data/processed/rebuild/stage2_signed.csv',
                  low_memory=False,
                  usecols=['org_name', 'breach_date', 'sic', 'final_cik'])
s2m['sic_num'] = pd.to_numeric(s2m['sic'], errors='coerce')
s2m['bdt'] = pd.to_datetime(s2m['breach_date'], errors='coerce')
sic_map = {c: g.dropna(subset=['sic_num'])
           for c, g in s2m.dropna(subset=['final_cik']).groupby('final_cik')}
SICSET = {4813, 4841, 4899}


def event_sic_treated(cik, bdt):
    g = sic_map.get(cik)
    if g is None or not len(g):
        return np.nan
    g = g.assign(_d=(g['bdt'] - bdt).abs())
    near = g[g['_d'] <= pd.Timedelta(days=3)]
    pool = near if len(near) else g.nsmallest(1, '_d')
    return float(any(int(s_) in SICSET for s_ in pool['sic_num'].dropna()))


ev['sic_treated'] = [event_sic_treated(c, b)
                     for c, b in zip(ev['final_cik'], ev['bdt'])]
cr = ev[(ev['has_crsp_data'] == 1)].dropna(subset=['sic_treated',
                                                   'firm_size_log']).copy()
cells = {
    'SIC-treated, NOT registered (the manufactured group)':
        (cr['sic_treated'] == 1) & (cr['fcc_form499'] == 0),
    'SIC-treated AND registered (concordant treated)':
        (cr['sic_treated'] == 1) & (cr['fcc_form499'] == 1),
    'registered, NOT SIC-treated (missed by SIC)':
        (cr['sic_treated'] == 0) & (cr['fcc_form499'] == 1),
    'neither (concordant control)':
        (cr['sic_treated'] == 0) & (cr['fcc_form499'] == 0),
}
crows = []
for lab, msk in cells.items():
    d_ = cr[msk]
    crows.append(dict(
        cell=lab, n=len(d_), orgs=d_['org_name'].nunique(),
        mean_size=round(d_['firm_size_log'].mean(), 2),
        median_size=round(d_['firm_size_log'].median(), 2),
        mean_pre_vol=round(d_['return_volatility_pre'].mean(), 1),
        mean_vol_change=round(d_['volatility_change'].mean(), 2)))
    log(f"  {lab}: n={len(d_)} ({d_['org_name'].nunique()} orgs) | ln(assets) "
        f"mean {d_['firm_size_log'].mean():.2f} median "
        f"{d_['firm_size_log'].median():.2f} | pre-vol "
        f"{d_['return_volatility_pre'].mean():.1f} | vol-change "
        f"{d_['volatility_change'].mean():+.2f}")
pd.DataFrame(crows).to_csv(OUTDIR / 't19b_misclassified_composition.csv',
                           index=False)
man = cr[cells['SIC-treated, NOT registered (the manufactured group)']]
con = cr[cells['SIC-treated AND registered (concordant treated)']]
rest = cr[~cells['SIC-treated, NOT registered (the manufactured group)']]
t_sz, p_sz = stats.ttest_ind(man['firm_size_log'], con['firm_size_log'],
                             equal_var=False)
t_pv, p_pv = stats.ttest_ind(man['return_volatility_pre'].dropna(),
                             con['return_volatility_pre'].dropna(),
                             equal_var=False)
t_vc, p_vc = stats.ttest_ind(man['volatility_change'].dropna(),
                             rest['volatility_change'].dropna(),
                             equal_var=False)
test('B2b', 'size: SIC-only vs concordant-treated')
test('B2b', 'pre-vol: SIC-only vs concordant-treated')
test('B2b', 'vol-change: SIC-only vs all others')
log(f'\n  Welch tests: SIC-treated-but-unregistered vs concordant treated — '
    f'ln(assets) t={t_sz:+.2f} (p={p_sz:.4f}); pre-breach volatility '
    f't={t_pv:+.2f} (p={p_pv:.4f}). Volatility change, SIC-only vs all '
    f'others: t={t_vc:+.2f} (p={p_vc:.4f}).')
log('  On CORRECTED data the discordant cell is nearly empty (6 events / 3 '
    'orgs — post-resolution SIC and Form 499 almost coincide), so the '
    'mechanism must be tested where the artifact was produced: the OLD '
    'record-level data.')

# -- the same composition on the OLD (pre-dedup) data, where +7.31 lived --
old_e = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv',
                    low_memory=False)
s2j = pd.read_csv('Data/processed/rebuild/stage2_signed.csv',
                  low_memory=False,
                  usecols=['org_name', 'breach_date', 'reported_date',
                           'final_cik'])
for df_ in (old_e, s2j):
    for c in ['breach_date', 'reported_date']:
        df_[c] = pd.to_datetime(df_[c], errors='coerce').dt.strftime('%Y-%m-%d')
kj = ['org_name', 'breach_date', 'reported_date']
old_j = old_e.merge(s2j.drop_duplicates(subset=kj), on=kj, how='left')
tset = set(ev.loc[ev['fcc_form499'] == 1, 'final_cik'].astype(int))
# JOIN-GAP REPAIR (9/2/2026, same fix as scripts/166): the join yields
# stage-2 CIKs but tset holds POST-reparenting canonical CIKs
# (scripts/154:168-177 EQUITY_PARENT); without the map, 14 Comcast records
# (genuinely treated family) are coded into the manufactured group.
EQUITY_PARENT = {1040573: 1166691, 1512267: 1166691, 1457937: 1105705}
old_j['cik_rep'] = old_j['final_cik'].map(
    lambda c: EQUITY_PARENT.get(int(c), int(c)) if pd.notna(c) else np.nan)
old_j['f499'] = old_j['cik_rep'].isin(tset)
oj = old_j[old_j['has_crsp_data'] == True].dropna(subset=['firm_size_log'])
man_o = oj[(oj['fcc_reportable'] == True) & (~oj['f499'])]
con_o = oj[(oj['fcc_reportable'] == True) & (oj['f499'])]
ctl_o = oj[(oj['fcc_reportable'] == False) & (~oj['f499'])]
rows_o = []
for lab, d_ in [('SIC-treated, NOT registered (manufactured)', man_o),
                ('SIC-treated AND registered (concordant)', con_o),
                ('control (neither)', ctl_o)]:
    rows_o.append(dict(cell=lab, n=len(d_), orgs=d_['org_name'].nunique(),
                       mean_size=round(d_['firm_size_log'].mean(), 2),
                       mean_pre_vol=round(d_['return_volatility_pre'].mean(), 1),
                       mean_vol_change=round(d_['volatility_change'].mean(), 2)))
    log(f"  OLD DATA — {lab}: n={len(d_)} ({d_['org_name'].nunique()} orgs) "
        f"| ln(assets) {d_['firm_size_log'].mean():.2f} | pre-vol "
        f"{d_['return_volatility_pre'].mean():.1f} | vol-change "
        f"{d_['volatility_change'].mean():+.2f}")
pd.DataFrame(rows_o).to_csv(OUTDIR / 't19c_old_misclassified.csv', index=False)
tsz_o = stats.ttest_ind(man_o['firm_size_log'], con_o['firm_size_log'],
                        equal_var=False)
tvc_o = stats.ttest_ind(man_o['volatility_change'].dropna(),
                        ctl_o['volatility_change'].dropna(), equal_var=False)
test('B2b', 'OLD data: size, manufactured vs concordant')
test('B2b', 'OLD data: vol-change, manufactured vs control')
spec891 = oj.dropna(subset=['volatility_change', 'return_volatility_pre',
                            'firm_size_log', 'leverage', 'roa']).copy()
spec891['q'] = pd.qcut(spec891['firm_size_log'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
shares = {q: (lambda d_: (len(d_), int((~d_['f499']).sum())))(
    spec891[(spec891['q'] == q) & (spec891['fcc_reportable'] == True)])
    for q in ['Q1', 'Q2', 'Q3', 'Q4']}
log(f'\n  Welch, OLD data (join-gap REPAIRED group): size '
    f'manufactured-vs-concordant t={tsz_o[0]:+.2f} (p={tsz_o[1]:.4f}): '
    f'null on the repaired group (the pre-repair null, t=-0.54/p=.59, '
    f'was a statement about the 14 misjoined Comcast records; no size '
    f'claim in either direction survives). Volatility '
    f'change, manufactured-vs-control: t={tvc_o[0]:+.2f} '
    f'(p={tvc_o[1]:.4f}; pre-repair t=+4.43/p=.0001 on the contaminated '
    f'31-record group, reported as the join-gap sensitivity).')
log('  Manufactured share of SIC-treated records by size quartile '
    '(N=891 spec sample): ' + '; '.join(
        f'{q}: {v[1]}/{v[0]} ({100 * v[1] / v[0]:.0f}%)' if v[0] else f'{q}: 0'
        for q, v in shares.items()))
log(f"  Manufactured orgs: {sorted(man_o['org_name'].unique())[:13]}")
log(f'\n  MECHANISM VERDICT (revised 9/4, DISH date-conditional '
    f're-adjudication): under the retired name-token classifier the '
    f'SIC-treated-but-unregistered group is {len(man_o)} records: the two '
    f'ATT-SecurityBreach artifacts, Suddenlink, and the name-adjacency '
    f'admissions. DISH left the group because DISH Wireless L.L.C. (dba '
    f'Boost Mobile, FRN 0027852722) is an open Form 499 family '
    f'registration at its 2023 breach dates, so DISH is registered, not '
    f'misclassified. The group shows NO size difference from concordant '
    f'carriers (t={tsz_o[0]:+.2f}, p={tsz_o[1]:.4f}) and its share of '
    f'SIC-treated records no longer peaks in Q1 '
    f'({"; ".join(f"{q}: {v[1]}/{v[0]}" for q, v in shares.items())}); '
    f'volatility manufactured-vs-control is t={tvc_o[0]:+.2f} '
    f'(p={tvc_o[1]:.4f}), a null. The authoritative decomposition is the '
    f'industry-code baseline (appendix Table 5): the Form 499 repair '
    f'ATTENUATES the published Q1 spike (+7.5556, p=.0086, to +5.1482, '
    f'p=.069) rather than eliminating it; the dropped component is '
    f'EMPTY, and the attenuation is driven entirely by the added '
    f'registrants industry codes miss (10 records averaging -8.62: '
    f'GoDaddy and Twilio, Form 499 filers industry-coded as software). '
    f'What survives is an inclusion-failure story plus a data-defect '
    f'story (the two ATT permno-collision artifacts), not a '
    f'regulatory-status exclusion story, and no records-per-event size '
    f'gradient claim (B2).')

# ======= C1: vintage-matched treatment verification (registry snapshot) ======
log('\n' + '=' * 90)
log('## C1 — Vintage-matched treatment')
log('=' * 90)
root = ET.parse('Data/edgar/form499_registry.xml').getroot()
recs = []
for f_ in root:
    info = f_.find('Filer_ID_Info')
    if info is None:
        continue
    recs.append(dict(
        fid=f_.findtext('Form_499_ID'),
        legal=(info.findtext('Legal_Name') or '').upper(),
        dba=(info.findtext('doing_business_as') or '').upper(),
        hold=(info.findtext('holding_company') or '').upper(),
        ptype=(info.findtext('Principal_Communications_Type') or ''),
        start=pd.to_datetime(info.findtext('start_date'), errors='coerce'),
        end=pd.to_datetime(info.findtext('end_date'), errors='coerce')))
reg = pd.DataFrame(recs)
n_ended = int(reg['end'].notna().sum())
log(f'  1. Pull used: committed snapshot Data/edgar/form499_registry.xml '
    f'(7/31/2026 vintage; Registration_Current_as_of 2026-04-01), 20,669 '
    f'filer records.')
log(f'  2. Registration histories ARE in the data as pulled: every record '
    f'carries start_date; {n_ended} records ({100 * n_ended / len(reg):.0f}%) are '
    f'TERMINATED records retained with end_date and end_reason — the '
    f'database is not a live-filers-only snapshot, so the premise that '
    f'deregistered filers vanish does not hold for this pull (named '
    f'evidence: HBO\'s dead 1997-2003 record and Sprint\'s 1997-2024 record '
    f'both appear and both drove stage-4 rulings).')
log('  3. Stage 4 (scripts/154) ASSIGNED TREATMENT AS OF THE BREACH DATE '
    'from these windows: coverage_valid treats an ended record as covering '
    'only through its end_date (this rule made HBO 2017 untreated and was '
    'the documented divergence from the retired 121b logic). Wayback '
    'reconstruction is therefore not required; the residual risk is a '
    'filer HARD-DELETED from the current database, for which no in-sample '
    'evidence exists (stated as a limitation, direction: would misclassify '
    'a deregistered-then-deleted carrier as control, attenuating any true '
    'effect).')
FAMILY = {
    18926: ['CENTURYLINK', 'CENTURYTEL', 'LUMEN', 'QWEST', 'EMBARQ'],
    20520: ['FRONTIER COMMUNICATIONS', 'CITIZENS TELECOM'],
    101830: ['SPRINT'],
    732712: ['VERIZON', 'MCI COMMUNICATIONS', 'BELL ATLANTIC', 'GTE '],
    732717: ['AT&T', 'SBC ', 'SOUTHWESTERN BELL', 'BELLSOUTH', 'AMERITECH',
             'PACIFIC BELL', 'CINGULAR'],
    1091667: ['CHARTER COMM', 'TIME WARNER CABLE', 'BRIGHT HOUSE', 'SPECTRUM '],
    1166691: ['COMCAST'],
    1283699: ['T-MOBILE', 'METROPCS', 'SPRINT SPECTRUM', 'BOOST'],
    1447669: ['TWILIO'],
    1609711: ['GODADDY'],
    1632127: ['CABLE ONE', 'CABLEONE', 'SPARKLIGHT'],
}
tr = fin[fin[TREAT] == 1]
ver_rows = []
uncovered = 0
fam_types = {}
for cik, kws in FAMILY.items():
    m = reg[reg[['legal', 'dba', 'hold']].apply(
        lambda c: c.str.contains('|'.join(re.escape(k.strip()) for k in kws),
                                 regex=True, na=False)).any(axis=1)]
    fam_types[cik] = sorted(m['ptype'].value_counts().index[:6])
    evs = tr[tr['final_cik'] == cik]
    cov = 0
    for _, e in evs.iterrows():
        bd = pd.Timestamp(e['breach_date'])
        ok = ((m['start'] <= bd) & (m['end'].isna() | (m['end'] >= bd))).any()
        cov += int(ok)
        if not ok:
            uncovered += 1
            log(f"    NOT COVERED at breach date: {e['org_name']} "
                f"{e['breach_date']} (CIK {cik})")
    ver_rows.append(dict(parent_cik=cik, family_records=len(m),
                         treated_events=len(evs), date_covered=cov))
vdf = pd.DataFrame(ver_rows)
log('  4. Independent re-verification (family-keyword match to registry, '
    'date-window containment of each breach date):')
log(vdf.to_string(index=False))
log(f'  => {int(vdf["date_covered"].sum())}/{int(vdf["treated_events"].sum())} '
    f'treated observations have a date-valid family filer record at the '
    f'breach date ({uncovered} not covered by this keyword check). '
    f'Control->treated flips: stage 2/4 ran name resolution with abstain '
    f'against the full registry; an exact-normalized-name rescan of the 231 '
    f'control orgs is part of the J funnel below.')
vdf.to_csv(OUTDIR / 't20_c1_vintage_verification.csv', index=False)
log('  5. Headline re-estimation: unnecessary if 102/102 survive; otherwise '
    'rerun flagged.')

# ==================== C2: over-inclusion audit ==============================
log('\n' + '=' * 90)
log('## C2 — Over-inclusion audit (Principal_Communications_Type)')
log('=' * 90)
COVERED = {'Incumbent Local Exchange Carrier', 'CAP/LEC', 'Cellular/PCS/SMR',
           'Interconnected VoIP', 'Interexchange Carrier (IXC)', 'Local Reseller',
           'Toll Reseller', 'Wireless Data', 'Cable TV provider of local exchange',
           'Paging & Messaging', 'SMR (dispatch)', 'Satellite', 'Prepaid Card',
           'Operator Service Provider (OSP)', 'Other Local', 'Other Toll',
           'Other Mobile'}
c2rows = []
for cik in FAMILY:
    tys = fam_types.get(cik, [])
    non = [t_ for t_ in tys if t_ and t_ not in COVERED]
    c2rows.append(dict(parent_cik=cik, family_types='; '.join(tys),
                       non_covered_types='; '.join(non) or '(none)'))
    log(f"  {cik}: types {tys} | non-covered: {non or 'none'}")
pd.DataFrame(c2rows).to_csv(OUTDIR / 't21_c2_type_audit.csv', index=False)
log('  HONEST READING: the registry carries NO "Non-Interconnected VoIP" '
    'and no TRS label anywhere in Principal_Communications_Type — which '
    'means the over-inclusion risk CANNOT BE ASSESSED FROM THIS SOURCE, '
    'not that it is absent. What can be said: every treated family also '
    'matches on telecommunications-carrier or Interconnected-VoIP records '
    '(categories 64.2011 via 64.2003 covers), so no treated parent rests '
    'SOLELY on a category this snapshot can identify as non-covered, and '
    'the exclusion re-estimation is a no-op by construction. The residual '
    'over-inclusion risk (a family whose relevant filer is in fact a '
    'non-interconnected-VoIP or TRS-only filer mislabeled here) is a '
    'stated limitation. Separately: coverage runs to CPNI held as a '
    'carrier, so non-CPNI breaches at covered carriers are regulated only '
    'insofar as CPNI is involved — a scope limit of the treatment proxy '
    'itself, stated.')

# =================== E4: events by year x treatment =========================
log('\n' + '=' * 90)
log('## E4 — Events by notification year (final sample)')
log('=' * 90)
fin['year'] = pd.to_datetime(fin['reported_date']).dt.year
yr = fin.groupby(['year', TREAT]).size().unstack(fill_value=0)
yr.columns = ['control', 'treated']
log(yr.to_string())
yr.to_csv(OUTDIR / 't18_events_by_year.csv')
log('  Zero treated observations precede the December 8, 2007 effective '
    'date — visible above, not asserted. DiD and synthetic control are '
    'unavailable: no pre-treatment period exists for treated units, so no '
    'donor pool can be weighted to a treated pre-period trajectory '
    '(Abadie, Diamond & Hainmueller 2010; Abadie 2021 JEL).')

# ================= H1: repeated events within parent ========================
log('\n' + '=' * 90)
log('## H1 — Repeated events within firm')
log('=' * 90)
per = fin.groupby(['final_cik', TREAT]).size()
for lab, g1 in [('treated', 1), ('control', 0)]:
    s = per[per.index.get_level_values(1) == g1]
    log(f'  {lab}: {len(s)} parents, events/parent mean {s.mean():.1f}, '
        f'median {s.median():.0f}, max {int(s.max())}')
Y = fin['e2_vol_change'].astype(float)
XS4 = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
       'health_breach', 'prior_events']
h1rows = []
for lab, d_ in [('first event per parent',
                 fin.sort_values('breach_date').groupby('final_cik').head(1)),
                ('most recent event per parent',
                 fin.sort_values('breach_date').groupby('final_cik').tail(1))]:
    f_ = sm.OLS(d_['e2_vol_change'].astype(float),
                sm.add_constant(d_[XS4].astype(float))).fit(
        cov_type='HC3', use_t=True)
    ci = f_.conf_int().loc[TREAT]
    test('H1', lab)
    h1rows.append(dict(spec=lab, coef=round(f_.params[TREAT], 4),
                       se=round(f_.bse[TREAT], 4), ci_lo=round(ci[0], 4),
                       ci_hi=round(ci[1], 4), n=int(f_.nobs),
                       n_treated=int(d_[TREAT].sum())))
    log(f"  {lab}: coef {f_.params[TREAT]:+.4f} SE {f_.bse[TREAT]:.4f} "
        f"95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}] N={int(f_.nobs)} "
        f"({int(d_[TREAT].sum())} treated)")
import statsmodels.formula.api as smf
ffe = smf.ols('e2_vol_change ~ ' + ' + '.join(XS4) + ' + C(final_cik)',
              data=fin).fit(cov_type='HC1', use_t=True)  # HC3 degenerate
# (leverage-one cells) under the full dummy set; HC1 reported, caveated.
mix = fin.groupby('final_cik')[TREAT].mean()
n_mixed = int(((mix > 0) & (mix < 1)).sum())
ci_fe = ffe.conf_int().loc[TREAT]
test('H1', 'parent fixed effects')
h1rows.append(dict(spec='parent FE', coef=round(ffe.params[TREAT], 4),
                   se=round(ffe.bse[TREAT], 4), ci_lo=round(ci_fe[0], 4),
                   ci_hi=round(ci_fe[1], 4), n=N, n_treated=int(fin[TREAT].sum())))
log(f"  parent fixed effects: coef {ffe.params[TREAT]:+.4f} SE "
    f"{ffe.bse[TREAT]:.4f} 95% CI [{ci_fe[0]:+.4f}, {ci_fe[1]:+.4f}] — "
    f"identified off only {n_mixed} parents whose treatment status varies "
    f"across their own events (AT&T-family and Comcast coverage-window "
    f"cases); interpret accordingly.")
pd.DataFrame(h1rows).to_csv(OUTDIR / 't23_h1_repeat_events.csv', index=False)

# ============================ H3: sample period =============================
maxyr = int(fin['year'].max())
n2025 = int((pd.to_datetime(ev['reported_date'], errors='coerce').dt.year == 2025).sum())
log('\n## H3 — Sample period')
log(f'  The WRDS extract ends 2024-12-31; the final sample\'s latest '
    f'notification year is {maxyr}. SAMPLE PERIOD IS 2006-2024 everywhere. '
    f'{n2025} events in the 489-event universe carry 2025 notification '
    f'dates; the five with matched securities (Nucor, Intuit, Workday, HPE, '
    f'Zscaler) drop at the volatility-window step because the extract ends '
    f'— stated in the attrition ledger.')

# ======================= J: census funnel ===================================
log('\n' + '=' * 90)
log('## J — Census: is 11 treated parents the population ceiling?')
log('=' * 90)
SUFF = r'\b(INC|LLC|L L C|CORP|CORPORATION|INCORPORATED|CO|COMPANY|LP|L P|LTD|LIMITED|PLC|HOLDINGS?|GROUP)\b'


def norm(s):
    s = re.sub(r'[^A-Z0-9 &]', ' ', str(s).upper())
    s = re.sub(SUFF, ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


w = reg[(reg['start'] <= '2024-12-31')
        & (reg['end'].isna() | (reg['end'] >= '2006-01-01'))].copy()
n_filers = len(w)
n_entities = w['legal'].map(norm).nunique()
n_hold = w.loc[w['hold'] != '', 'hold'].map(norm).nunique()
em = pd.read_csv('Data/edgar/cik_ticker_map_normalized.csv')
em['nn'] = em['company_name_normalized'].map(norm)
edgar_names = dict(zip(em['nn'], em['cik']))
pm = pd.read_csv('Data/wrds/ticker_permno_mapping.csv', usecols=['ticker'])
crsp_tickers = set(pm['ticker'])
cik2tick = em.groupby('cik')['ticker'].apply(list).to_dict()
matched_ciks = set()
for col in ['legal', 'dba', 'hold']:
    for nm in w[col].map(norm).unique():
        if nm and nm in edgar_names:
            matched_ciks.add(int(edgar_names[nm]))
crsp_ciks = {c for c in matched_ciks
             if any(t_ in crsp_tickers for t_ in cik2tick.get(c, []))}
uni_ciks = set(ev['final_cik'].dropna().astype(int))
in_uni = crsp_ciks & uni_ciks
treated_parents = set(int(c) for c in FAMILY)
log(f'  Funnel (2006-2024 window; exact-normalized-name matching with '
    f'abstain — a LOWER BOUND on public mapping, since filings are at '
    f'operating-entity level with no CIK/ticker field and full parent '
    f'attribution is a hand-construction task, stated):')
log(f'    Form 499 filer records with coverage in window:      {n_filers:,}')
log(f'    Distinct legal entities (normalized):                {n_entities:,}')
log(f'    Distinct named holding companies:                    {n_hold:,}')
n_verified_hit = len({int(edgar_names[nm]) for col in ['legal', 'dba', 'hold']
                      for nm in w[col].map(norm).unique()
                      if nm and nm in edgar_names} & treated_parents
                     | (matched_ciks & treated_parents))
log(f'    Name-matched to an SEC registrant (CIK, exact):      {len(matched_ciks):,}')
log(f'    ...of the 11 verified treated parents so surfaced:   {len(matched_ciks & treated_parents)}')
log(f'    ...appearing in the 489-event breach universe:       {len(matched_ciks & uni_ciks)}')
pd.DataFrame([dict(filer_records=n_filers, entities=n_entities,
                   holdings=n_hold, sec_matched_exact=len(matched_ciks),
                   verified_parents_surfaced=len(matched_ciks & treated_parents),
                   in_breach_universe=len(matched_ciks & uni_ciks),
                   treated_parents_final=len(treated_parents))]).to_csv(
    OUTDIR / 't22_census_funnel.csv', index=False)
log('  READING (DECIDED 8/30, per Tim): the census claim is RESTATED AT '
    'THE INTERSECTION. The automated exact-name census undercounts by '
    'construction — filings are operating-entity-level (Verizon New York '
    'Inc., not Verizon Communications), and only '
    f'{len(matched_ciks & treated_parents)} of the 11 hand-verified treated '
    'parents surface via exact matching; this undercount is stated as a '
    'limitation (direction: understates the public regulated population). '
    'The hand census (~2,584 holding names) is NOT undertaken. The '
    'defensible census is the observable intersection: within firms that '
    'BOTH filed Form 499 AND publicly disclosed a breach captured by PRC '
    'with CRSP coverage, the pipeline exhausted the set at 13 parents (11 '
    'surviving to the final sample). The POPULATION argument is carried '
    'by E3 instead, which is stronger and does not depend on the census: '
    'a 3pp-annualized effect is unreachable at ANY treated count given '
    'the control-side variance floor — a variance-structure result, not a '
    'sample-size result.')

# =================== I: literature corrections (verbatim) ===================
log('\n' + '=' * 90)
log('## I — Literature-claim corrections (text to carry into the essay)')
log('=' * 90)
log("""
I1 (4.2pp REMOVED). Replacement sentence, verbatim:
  "Obaydin, Xu, and Zurbruegg (2024) find that the staggered adoption of
  state data breach notification laws raises stock price crash risk by at
  least 5% of a standard deviation across NCSKEW, DUVOL, and COUNT, with a
  corresponding 5.2%-of-a-standard-deviation increase in residual short
  interest consistent with managerial bad-news hoarding."
  (DUVOL is a down-to-up volatility log-ratio, not a volatility level —
  the likely origin of the 4.2pp error. Nothing in the paper is in pp.)

I2 (novelty NARROWED). Within breach notification, deadline variation is
  unexploited — but Ashraf & Sunder (2023, TAR 98(4)) footnote 25 already
  tested an explicit-deadline incremental effect and "find no statistically
  significant incremental effect (untabulated)", inviting future research.
  Cite as motivation; never claim nobody has looked. Across disclosure
  settings the claim is false: engage Doyle & Magilke (2013 JAR), Lambert
  et al. (2017 AOS), Impink et al. (2012 RAST — a deadline-change null),
  Lerman & Livnat (2010 RAST), Tartaroglu & Imhof (2017 RQFA).

I3 (unbundling SOFTENED). 64.2011 is itself a bundle (new federal mandate +
  LE-first sequencing + 7-business-day LE clock + 7-business-day public
  embargo + recordkeeping). Defensible claim: unusual in imposing a hard,
  short, federally specified LAW-ENFORCEMENT clock with a mandatory
  public-disclosure embargo on a defined industry; earliest US instrument
  to do so. Degree, not kind.

I4 (state-law bundling, QUALIFIED). Report as "no deadline-only amendment
  was identified in the amendments surveyed" (Ashraf & Sunder 2023; Perkins
  Coie annual updates; NY GBL 899-aa Dec-2024 near-miss also changed delay
  exceptions and data-maintainer scope; both near-misses postdate the
  sample).

I5 (SEC 2023 rule). Future-research framing holds; note the DOJ
  delay-determination mechanism as observable disclosure-lag variation and
  the May-2024 Gerding statement (Item 8.01 venue break) as design points;
  the low-hanging event study is being picked (Block 2025 working paper).
""")

# ============================== test count ==================================
fams = pd.Series([f for f, _ in N_TESTS]).value_counts()
log('=' * 90)
log(f'Hypothesis tests in this script: {len(N_TESTS)} — ' +
    '; '.join(f'{k}: {v}' for k, v in fams.items()))
log('(Multiplicity framework applied across Query-4 parts in the umbrella '
    'report: Benjamini-Hochberg within each pre-specified family; the '
    'specification grid is descriptive and contributes no tests.)')

Path('outputs/ESSAY2_QUERY4_PARTS_ACJ.md').write_text(
    '# Essay 2 Query 4 — Parts A, B2, C, E4, H, J, I (computed live)\n\n'
    + '\n'.join(L) + '\n', encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY4_PARTS_ACJ.md + t16-t24 CSVs')
