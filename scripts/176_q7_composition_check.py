"""
QUERY 7 — (1) Is the +0.446 announcement-window differential composition?
          (2) Where does T-Mobile sit on announcement-window elevation?
==========================================================================
Pre-specified hypothesis (stated before running): the differential
reflects sample composition — severity truncation (H5: 64.2011 routes
reports to law enforcement, CPNI alone does not trigger state PII
statutes, so observed treated breaches are a more severe subset) and/or
size imbalance (H3: standardized size difference 1.51). Pre-specified
reading: substantial attenuation under severity/size conditioning =>
composition effect, reported as such, no regulatory claim; survival under
both => genuine puzzle, FLAG AND STOP.

Outputs: outputs/ESSAY2_QUERY7_REPORT.md + t51-t52 CSVs
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


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't42_final_sample_with_repairs.csv', low_memory=False)
br = fin.dropna(subset=['abn_ann', 'abn_pre']).copy()
br['elev'] = br['abn_ann'] - br['abn_pre']
CTRL = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
        'prior_events']
d = br.dropna(subset=[TREAT, 'abn_pre'] + CTRL).reset_index(drop=True)
log('=' * 90)
log('QUERY 7 (computed live, scripts/176)')
log('=' * 90)

# ---------------- 1.1 severity distributions ----------------
log('\n## 1.1 — Severity distribution, treated vs control (direct evidence '
    'on the truncation mechanism, independent of the regression)')
d['recs'] = pd.to_numeric(d['total_affected_max'], errors='coerce')
tt, cc = d[d[TREAT] == 1], d[d[TREAT] == 0]
qs = [.1, .2, .3, .4, .5, .6, .7, .8, .9]
row_t = [tt['recs'].quantile(q) for q in qs]
row_c = [cc['recs'].quantile(q) for q in qs]
log('  records affected (deciles d10..d90):')
log('    treated: ' + ' | '.join(f'{v:,.0f}' for v in row_t)
    + f"  (n with data {int(tt['recs'].notna().sum())}/{len(tt)})")
log('    control: ' + ' | '.join(f'{v:,.0f}' for v in row_c)
    + f"  (n with data {int(cc['recs'].notna().sum())}/{len(cc)})")
ks = stats.ks_2samp(np.log1p(tt['recs'].dropna()), np.log1p(cc['recs'].dropna()))
N_TESTS.append('KS severity')
log(f'  KS on log records: D={ks[0]:.3f} (p={ks[1]:.4f}) — '
    f'{"treated distribution differs" if ks[1] < .05 else "no distributional difference detected"}.')
d['vec'] = d['breach_type'].astype(str).str.split('+').str[0]
comp = pd.crosstab(d['vec'], d[TREAT], normalize='columns').round(3) * 100
log('  breach-vector composition (% within group; columns 0=control, 1=treated):')
log(comp.to_string())
for kw, lab in [('ssn|social security', 'SSN'), ('financial|credit|debit|account', 'financial'),
                ('medical|health', 'medical'), ("driver", "driver license")]:
    sh_t = tt['information_affected'].astype(str).str.contains(kw, case=False).mean()
    sh_c = cc['information_affected'].astype(str).str.contains(kw, case=False).mean()
    log(f'  data-type "{lab}": treated {100 * sh_t:.0f}% vs control {100 * sh_c:.0f}%')
comp.to_csv(OUTDIR / 't51_severity_composition.csv')

# ---------------- 1.2-1.4 conditioning ladder ----------------
log('\n## 1.2-1.4 — Conditioning the announcement-window specification')
d['ln_recs'] = np.log1p(d['recs'].clip(upper=d['recs'].quantile(.99)))
d['ln_recs'] = d['ln_recs'].fillna(d['ln_recs'].median())
d['recs_missing'] = d['recs'].isna().astype(float)
d['size_q'] = pd.qcut(d['firm_size_log'], 4, labels=False)
d['size2'] = d['firm_size_log'] ** 2
vec_d = pd.get_dummies(d['vec'], prefix='v', drop_first=True).astype(float)
szq_d = pd.get_dummies(d['size_q'], prefix='szq', drop_first=True).astype(float)


def run(extra_cols, extra_frames, label, data=None):
    dd = d if data is None else data
    X = dd[[TREAT, 'abn_pre'] + CTRL + extra_cols].astype(float)
    for fr in extra_frames:
        X = pd.concat([X, fr.loc[dd.index]], axis=1)
    X = sm.add_constant(X)
    f = sm.OLS(dd['elev'].astype(float), X).fit(
        cov_type='cluster', cov_kwds={'groups': dd['final_cik']}, use_t=True)
    b, se = float(f.params[TREAT]), float(f.bse[TREAT])
    ci = f.conf_int().loc[TREAT]
    N_TESTS.append(label)
    log(f'  {label}: {b:+.4f} (SE {se:.4f}, 95% CI [{ci[0]:+.4f}, '
        f'{ci[1]:+.4f}], N={int(f.nobs)})')
    return b, se


b0, se0 = run([], [], 'BASE (the +0.446 spec)')
b_sev, _ = run(['ln_recs', 'recs_missing'], [vec_d],
               '+ severity (ln records winsor p99 + vector FE)')
b_sz, _ = run(['size2'], [szq_d], '+ flexible size (quartile FE + size^2)')
b_joint, se_j = run(['ln_recs', 'recs_missing', 'size2'], [vec_d, szq_d],
                    '+ severity AND flexible size (joint)')
lo_s, hi_s = d.loc[d[TREAT] == 1, 'firm_size_log'].agg(['min', 'max'])
cs = d[(d['firm_size_log'] >= lo_s) & (d['firm_size_log'] <= hi_s)]
b_cs, _ = run([], [], 'common support (controls in treated size range; '
                      'CHANGE OF ESTIMAND)', data=cs)
att = lambda b: 100 * (1 - b / b0)
log(f'\n  ATTENUATION vs base: severity {att(b_sev):+.0f}% | flexible size '
    f'{att(b_sz):+.0f}% | joint {att(b_joint):+.0f}% | common support '
    f'{att(b_cs):+.0f}%')

# ---------------- 1.5 multiplicity position ----------------
log('\n## 1.5 — Multiplicity position of +0.446')
fam = {'earnings elevation': 1e-40, 'contrast': 1e-20,
       'treatment on elevation (CV3)': 0.0249, 'breach elevation': 0.073}
ps = sorted(fam.items(), key=lambda kv: kv[1])
m = len(ps)
log('  Family: the 4-test announcement-window family (scripts/175, '
    'pre-specified by the 8/31 rescope). BH at FDR 5%, using the CV3 '
    'p-value (the calibrated rung):')
rej = []
for i, (k, p) in enumerate(ps):
    thr = 0.05 * (i + 1) / m
    rej.append(p <= thr)
    log(f'    {k}: p={p:.3g} vs threshold {thr:.4f} -> '
        f'{"reject" if p <= thr else "fail"}')
log(f'  +0.446 {"SURVIVES" if rej[2] else "FAILS"} BH within its family at '
    f'the CV3 p-value. Cumulative program tests through Query 6: ~61; '
    f'Query 7 adds {len(N_TESTS)} (this family). Program-wide context '
    f'stated wherever the coefficient is reported.')

# ---------------- pre-specified verdict ----------------
log('\n## PRE-SPECIFIED VERDICT (reading fixed before estimation)')
frac = b_joint / b0
if abs(frac) < 0.5 or (b_joint - 1.97 * se_j) < 0 and abs(frac) < 0.7:
    verdict = ('COMPOSITION' if abs(frac) < 0.5 else 'SUBSTANTIALLY ATTENUATED')
else:
    verdict = 'SURVIVES'
log(f'  Joint-conditioned coefficient = {b_joint:+.4f} = '
    f'{100 * frac:.0f}% of base. ' +
    (f'The differential attenuates under composition conditioning — '
     f'reported as a demonstrated composition effect (H5 severity '
     f'truncation / H3 size imbalance), cited to the mechanisms already '
     f'documented; NO regulatory claim is built on it.' if verdict != 'SURVIVES'
     else 'THE DIFFERENTIAL SURVIVES BOTH CHANNELS — genuine puzzle. FLAG '
          'AND STOP: it needs its own treatment in the essay and the '
          'results structure changes. No ruling is made here.'))

# ---------------- 2: T-Mobile's position ----------------
log('\n' + '=' * 90)
log('## 2 — Where does T-Mobile sit on announcement-window elevation?')
log('=' * 90)
foc = br[(br['final_cik'] == 1283699) & (br['breach_date'] == '2021-08-13')]
fe = float(foc['elev'].iloc[0])
tr_el = br.loc[br[TREAT] == 1, 'elev']
pct_t = 100 * (tr_el < fe).mean()
pct_all = 100 * (br['elev'] < fe).mean()
log(f'  Focal event (Aug 2021): elevation {fe:+.3f} daily pp '
    f'(abn [-4,+4] {float(foc["abn_ann"].iloc[0]):.3f} vs [-25,-5] '
    f'{float(foc["abn_pre"].iloc[0]):.3f}).')
log(f'  Percentile: {pct_t:.0f}th within the treated distribution '
    f'(treated mean {tr_el.mean():+.3f}, median {tr_el.median():+.3f}); '
    f'{pct_all:.0f}th within the full sample.')
fam_ev = br[br['final_cik'].isin([1283699, 101830])]
log(f'  T-Mobile/Sprint family ({len(fam_ev)} final-sample events): '
    f'elevation mean {fam_ev["elev"].mean():+.3f}, median '
    f'{fam_ev["elev"].median():+.3f}, range [{fam_ev["elev"].min():+.2f}, '
    f'{fam_ev["elev"].max():+.2f}] — vs treated group mean '
    f'{tr_el.mean():+.3f} and control mean '
    f'{br.loc[br[TREAT] == 0, "elev"].mean():+.3f}.')
typical = abs(fe - tr_el.mean()) < tr_el.std()
log(f'  PLAINLY: the focal event is '
    f'{"TYPICAL" if typical else "ATYPICAL"} of the treated group on this '
    f'dimension (|focal - treated mean| = {abs(fe - tr_el.mean()):.3f} vs '
    f'treated SD {tr_el.std():.3f}), and the family '
    f'{"tracks" if abs(fam_ev["elev"].mean() - tr_el.mean()) < 0.15 else "diverges from"} '
    f'the treated average.')
fam_ev[['breach_date', 'org_name', 'elev']].to_csv(
    OUTDIR / 't52_tmobile_elevation.csv', index=False)

Path('outputs/ESSAY2_QUERY7_REPORT.md').write_text(
    '# Essay 2 Query 7 (computed live)\n\n' + '\n'.join(L) + '\n',
    encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY7_REPORT.md + t51-t52')
