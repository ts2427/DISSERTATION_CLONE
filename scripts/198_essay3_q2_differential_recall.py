"""
ESSAY 3 QUERY 2 — DIFFERENTIAL-RECALL CHECK (NEW)
=================================================
Lists every classifier miss (reference = Y, classifier = N) across both validation rounds by treatment status
and company, and reports recall separately for treated and control filings. Tests the assumption behind the
stopping rule: misses that fall equally on treated and control attenuate the treated-control difference; misses
that cluster in one group bias it.
Rounds / classifiers:
  round 1, v1 (frozen d39bc6d)                       — the validated round-1 comparison
  round 1, v2 (final 6f7be7a) — IN-SAMPLE            — round 1 informed v2's fixes; not a validation
  round 2, v2 (final 6f7be7a)                        — the out-of-sample validation of the final classifier
Treatment status of a filing = fcc_form499 of the in-scope event it was drawn for (earliest reported_date among
the events whose B1 window contains it; calibration documents use their calibration event).
Reference codes: Claude-coded, blind to the classifier (Tim did not hand-code); variant A (restated = Y).
Outputs: outputs/essay3_q2/d3_misses_by_treatment.csv, d3_recall_by_treatment.csv, 198_recall.log
"""

import sys
import importlib.util
from pathlib import Path
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


spec = importlib.util.spec_from_file_location('clf2', 'scripts/195_essay3_q2_classifier_v2.py')
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)
P = pd.read_csv(OUT / 'b_event_filing_pairs.csv', dtype={'accession': str})
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
cal = pd.read_csv('outputs/rebuild/calibration_5_02/coding_sheet.csv', dtype={'accession': str})


def treated_of(acc, cik):
    pp = P[(P['accession'] == acc)].sort_values('reported_date')
    if len(pp):
        return int(pp['fcc_form499'].iloc[0])
    c = cal[cal['accession'] == acc]
    return int(c['treated'].iloc[0]) if len(c) else None


FIELDS = [('exec_departure', 'exec'), ('ceo_departure', 'ceo'), ('director_only_departure', 'director_only')]


def frame(round_, clfname, ref_file, sheet_file, hidden_file, use_v2_live):
    T = pd.read_csv(OUT / ref_file, sep='|', dtype=str, keep_default_na=False)
    S = pd.read_excel(OUT / sheet_file, sheet_name='coding', dtype=str).fillna('')
    H = pd.read_csv(OUT / hidden_file, dtype=str, keep_default_na=False)
    D = T.merge(H[['sheet_id', 'accession'] + [c for c in H.columns if c.startswith('clf_')]], on='sheet_id') \
         .merge(S[['sheet_id', 'url', 'item_5_02_text (caption stripped)']], on='sheet_id')
    D['cik'] = D['url'].str.extract(r'/data/(\d+)/').astype(int)
    if use_v2_live:  # v2 on round-1 texts (in-sample)
        for i, r in D.iterrows():
            codes, persons, refs = clf.classify(r['item_5_02_text (caption stripped)'])
            D.at[i, 'clf_exec_departure'] = 'Y' if codes['exec_departure'] else 'N'
            D.at[i, 'clf_ceo_departure'] = 'Y' if codes['ceo_departure'] else 'N'
            D.at[i, 'clf_director_only_departure'] = 'Y' if codes['director_departure'] else 'N'
    D['treated'] = [treated_of(a, c) for a, c in zip(D['accession'], D['cik'])]
    D['round'], D['classifier'] = round_, clfname
    return D


R = [frame(1, 'v1 (d39bc6d)', 'VALIDATION_REFERENCE_CODES_R1.psv', 'VALIDATION_SHEET.xlsx',
           'validation_classifier_HIDDEN.csv', False),
     frame(1, 'v2 (6f7be7a) IN-SAMPLE', 'VALIDATION_REFERENCE_CODES_R1.psv', 'VALIDATION_SHEET.xlsx',
           'validation_classifier_HIDDEN.csv', True),
     frame(2, 'v2 (6f7be7a)', 'VALIDATION_REFERENCE_CODES_R2.psv', 'VALIDATION_SHEET_R2.xlsx',
           'validation_classifier_HIDDEN_R2.csv', False)]
miss, rec = [], []
for D in R:
    for f, lab in FIELDS:
        cf = f'clf_{f}'
        x = D[D[f] != 'unclear']
        for _, r in x[(x[f] == 'Y') & (x[cf] != 'Y')].iterrows():
            miss.append(dict(round=r['round'], classifier=r['classifier'], field=lab, sheet_id=int(r['sheet_id']),
                             company=r['company'], cik=r['cik'], filing_date=r['filing_date'],
                             treated=r['treated'], reference_person=r['person_and_role'],
                             restates_prior_disclosure=r['restates_prior_disclosure']))
        for g, gl in [(1, 'treated'), (0, 'control')]:
            xg = x[(x['treated'] == g) & (x[f] == 'Y')]
            k, n = int((xg[cf] == 'Y').sum()), len(xg)
            ci = proportion_confint(k, n, method='beta') if n else (None, None)
            rec.append(dict(round=D['round'].iloc[0], classifier=D['classifier'].iloc[0], field=lab, group=gl,
                            reference_positives=n, classifier_hits=k, misses=n - k,
                            recall=round(k / n, 4) if n else None,
                            recall_ci95=f'[{ci[0]:.3f}, {ci[1]:.3f}]' if n else 'n/a',
                            filings_in_group=int((x['treated'] == g).sum())))
M = pd.DataFrame(miss)
RC = pd.DataFrame(rec)
M.to_csv(OUT / 'd3_misses_by_treatment.csv', index=False)
RC.to_csv(OUT / 'd3_recall_by_treatment.csv', index=False)
log('Every miss (reference Y, classifier N), both rounds:')
log(M.to_string(index=False))
log('\nRecall by treatment status:')
log(RC.to_string(index=False))
(OUT / '198_recall.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
