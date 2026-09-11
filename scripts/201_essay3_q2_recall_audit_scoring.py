"""
ESSAY 3 QUERY 2 — RECALL-AUDIT SCORING (NEW)
============================================
Final classifier v2 (scripts/195, 6f7be7a) answers (validation_classifier_HIDDEN_AUDIT.csv, committed 762a4b9 before
coding) vs the audit reference codes (Claude, blind to v2 and to the strata; file of record
VALIDATION_SHEET_AUDIT_CLAUDE_RATER.xlsx). Tim did not hand-code.
Scoring:
  PRIMARY    main (verified) columns; 'unclear' rows excluded (count reported)
  SECONDARY  blind_* (text-only) columns for exec, CEO, pre-announced (director has no blind column)
  SENSITIVITY 'unclear' scored as Y
Recall and precision with exact (Clopper-Pearson) 95% CIs, overall and by treatment stratum (from the hidden file),
for executive and CEO departure; variant A (restatements counted, as coded) and variant B (restated recoded N vs v2's
new-only code) for executive departure.
Sheet 3 (Carnival; departure only in Exhibit 99.1) is reported separately as a STRUCTURAL miss; exhibit-only candidates
(Item 5.02 text that points to an exhibit or press release and contains no departure language v2 recognises) are counted
by stratum in the audit and in all 1,078 filings (heuristic, labeled).
Sheet 75 (T-Mobile 2018-04-30): v2's call, and whether v2's de-duplication treats it as the first disclosure of Legere's
departure.
Outputs: outputs/essay3_q2/d3_audit_agreement.csv, d3_audit_recall_by_stratum.csv, d3_audit_disagreements.csv,
         d3_exhibit_only_candidates.csv, ADJUDICATION.xlsx (adds tab audit_v2), 201_audit.log
"""

import re
import sys
import hashlib
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.proportion import proportion_confint

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 100 + '\n' + t + '\n' + '=' * 100)


spec = importlib.util.spec_from_file_location('clf2', 'scripts/195_essay3_q2_classifier_v2.py')
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)

xl = OUT / 'VALIDATION_SHEET_AUDIT_CLAUDE_RATER.xlsx'
T = pd.read_csv(OUT / 'VALIDATION_REFERENCE_CODES_AUDIT.psv', sep='|', dtype=str, keep_default_na=False)
book = pd.read_excel(xl, sheet_name=None, dtype=str)
X = book[[k for k in book if 'verif' not in k.lower() and 'readme' not in k.lower()][0]].fillna('')
X.columns = T.columns
X['sheet_id'] = X['sheet_id'].str.replace(r'\.0$', '', regex=True)
nd = sum(T.at[i, c].strip() != X.at[i, c].strip() for i in range(len(T)) for c in T.columns)
hdr('RECALL AUDIT — v2 vs audit reference codes (Claude, blind to v2 and strata; Tim did not hand-code)')
log(f'File of record {xl} sha256 {hashlib.sha256(xl.read_bytes()).hexdigest()}; workbook vs pasted text: {nd} cell differences')
assert nd == 0
H = pd.read_csv(OUT / 'validation_classifier_HIDDEN_AUDIT.csv', dtype=str, keep_default_na=False)
S = pd.read_excel(OUT / 'VALIDATION_SHEET_AUDIT.xlsx', sheet_name='coding', dtype=str).fillna('')
D = X.merge(H, on='sheet_id').merge(S[['sheet_id', 'filing_date', 'url', 'item_5_02_text (caption stripped)']]
                                    .rename(columns={'filing_date': 'sfd', 'item_5_02_text (caption stripped)': 'text'}), on='sheet_id')
assert len(D) == 80 and (D['filing_date'] == D['sfd']).all()
D['treated'] = D['treated_stratum'].astype(int)
for f in ['exec_departure', 'ceo_departure', 'director_only_departure', 'pre_announced']:
    log(f"  '{f}' unclear rows (primary): {int((D[f] == 'unclear').sum())} {D.loc[D[f] == 'unclear', 'sheet_id'].tolist()}")


def cp(k, n):
    if n == 0:
        return None, 'n/a'
    lo, hi = proportion_confint(k, n, method='beta')
    return round(k / n, 4), f'[{lo:.3f}, {hi:.3f}]'


def score(ref, cl, mode):
    r = ref.copy()
    if mode == 'unclear->Y':
        r = r.replace('unclear', 'Y')
    keep = (r != 'unclear') if mode != 'keep' else pd.Series(True, index=r.index)  # 'keep': 3-category field
    r, c = r[keep], cl[keep]
    tp, fp, fn = int(((r == 'Y') & (c == 'Y')).sum()), int(((r != 'Y') & (c == 'Y')).sum()), int(((r == 'Y') & (c != 'Y')).sum())
    pr, prci = cp(tp, tp + fp)
    rc, rcci = cp(tp, tp + fn)
    k = cohen_kappa_score(r, c) if (r.nunique() > 1 or c.nunique() > 1) else np.nan
    return dict(n=int(keep.sum()), excluded_unclear=int((~keep).sum()), agreement=round((r == c).mean(), 4),
                kappa=round(k, 4), ref_Y=int((r == 'Y').sum()), clf_Y=int((c == 'Y').sum()), tp=tp, fp=fp, fn=fn,
                precision=pr, precision_ci95=prci, recall=rc, recall_ci95=rcci)


B = D.copy()
B.loc[B['restates_prior_disclosure'] == 'Y', 'exec_departure'] = 'N'
specs = [('exec departure (A)', 'exec_departure', 'blind_exec', 'clf_exec_departure', D),
         ('exec departure (B: restated->N vs new-only)', 'exec_departure', None, 'clf_exec_departure_new', B),
         ('CEO departure', 'ceo_departure', 'blind_ceo', 'clf_ceo_departure', D),
         ('director-only departure', 'director_only_departure', None, 'clf_director_only_departure', D),
         ('pre-announced', 'pre_announced', 'blind_pre', 'clf_pre_announced', D)]
rows, strat = [], []
for lab, f, bf, cf, d in specs:
    for mode, col in [('PRIMARY (verified)', f), ('SECONDARY (blind)', bf), ('SENSITIVITY unclear->Y', f)]:
        if col is None:
            continue
        m = 'unclear->Y' if mode.startswith('SENS') else 'exclude'
        if f == 'pre_announced':  # 3-category field: unclear is a legitimate value, not excluded
            x = d[[col, cf]]
            rows.append(dict(field=lab, scoring=mode, **score(x[col].replace('unclear', 'unclear'), x[cf], 'keep')))
            continue
        rows.append(dict(field=lab, scoring=mode, **score(d[col], d[cf], m)))
        if f in ('exec_departure', 'ceo_departure'):
            for g, gl in [(1, 'treated'), (0, 'control')]:
                dg = d[d['treated'] == g]
                strat.append(dict(field=lab, scoring=mode, stratum=gl, **score(dg[col], dg[cf], m)))
A = pd.DataFrame(rows)
RS = pd.DataFrame(strat)
A.to_csv(OUT / 'd3_audit_agreement.csv', index=False)
RS.to_csv(OUT / 'd3_audit_recall_by_stratum.csv', index=False)
log('\nOverall:')
log(A.to_string(index=False))
log('\nBy treatment stratum (executive and CEO departure):')
log(RS[['field', 'scoring', 'stratum', 'n', 'excluded_unclear', 'ref_Y', 'clf_Y', 'tp', 'fp', 'fn', 'precision',
        'precision_ci95', 'recall', 'recall_ci95']].to_string(index=False))

hdr('Disagreements (primary codes)')
dis = []
for _, r in D.iterrows():
    fl = [f for f, c in [('exec_departure', 'clf_exec_departure'), ('ceo_departure', 'clf_ceo_departure'),
                         ('director_only_departure', 'clf_director_only_departure'), ('pre_announced', 'clf_pre_announced')]
          if r[f] != 'unclear' and r[f] != r[c]]
    if fl or 'unclear' in (r['exec_departure'], r['ceo_departure']):
        dis.append(dict(round='audit', classifier='v2 (6f7be7a)', sheet_id=int(r['sheet_id']), company=r['company'],
                        filing_date=r['filing_date'], treated=r['treated'], url=r['url'],
                        fields_in_dispute=', '.join(fl) or 'reference unclear',
                        reference=f"exec={r['exec_departure']} / ceo={r['ceo_departure']} / dir={r['director_only_departure']} / pre={r['pre_announced']}",
                        classifier_codes=f"exec={r['clf_exec_departure']} / ceo={r['clf_ceo_departure']} / dir={r['clf_director_only_departure']} / pre={r['clf_pre_announced']}",
                        blind=f"exec={r['blind_exec']} / ceo={r['blind_ceo']} / pre={r['blind_pre']}",
                        restates_prior_disclosure=r['restates_prior_disclosure'], reference_person=r['person_and_role'],
                        classifier_person=r['clf_person_role'], reference_note=r['notes'], text_excerpt=r['text'][:1500]))
DS = pd.DataFrame(dis)
DS.to_csv(OUT / 'd3_audit_disagreements.csv', index=False)
for _, r in DS.iterrows():
    log(f"  [{r['sheet_id']}] {r['company']} {r['filing_date']} ({'treated' if r['treated'] else 'control'}) | {r['fields_in_dispute']}\n"
        f"     ref: {r['reference']} (blind {r['blind']}) | {r['reference_person'][:160]}\n     v2 : {r['classifier_codes']} | {r['classifier_person'][:160]}")

hdr('Sheet 3 — structural (exhibit-only) miss; exhibit-only candidates by stratum')
s3 = D[D['sheet_id'] == '3'].iloc[0]
log(f"Sheet 3 {s3['company']} {s3['filing_date']} ({'treated' if s3['treated'] else 'control'}): reference exec={s3['exec_departure']} "
    f"CEO={s3['ceo_departure']} (blind {s3['blind_exec']}/{s3['blind_ceo']}); v2 exec={s3['clf_exec_departure']} "
    f"CEO={s3['clf_ceo_departure']}. Item 5.02 text ({len(s3['text'])} chars): {s3['text'][:600]}")
EXH = re.compile(r'(?i)exhibit\s+99|press\s+release|attached\s+(?:hereto\s+)?as\s+exhibit|incorporated\s+(?:herein\s+)?by\s+reference')


def exhibit_only(sec):
    codes, persons, _ = clf.classify(sec)
    has_dep = any(p['action'] == 'departure' for p in persons) or bool(clf.DEP.search(clf.RET_PLAN.sub(' ', sec)))
    return int(bool(EXH.search(sec)) and not has_dep and len(sec) < 1500)


D['exhibit_only_candidate'] = [exhibit_only(t) for t in D['text']]
log('Audit sample, exhibit-only candidates (heuristic: short 5.02 text that points to an exhibit/press release and has no '
    'departure language): ' + '; '.join(f"{gl} {int(D.loc[D.treated == g, 'exhibit_only_candidate'].sum())}/40"
                                        for g, gl in [(1, 'treated'), (0, 'control')])
    + f" | sheet ids {D.loc[D.exhibit_only_candidate == 1, 'sheet_id'].tolist()}")
secs = pd.read_csv(OUT / 'c2_sections.csv', dtype={'accession': str})
pairs = pd.read_csv(OUT / 'b_event_filing_pairs.csv', dtype={'accession': str}).sort_values('reported_date') \
    .drop_duplicates('accession')[['accession', 'fcc_form499']]
secs = secs.merge(pairs, on='accession', how='left')
secs['exhibit_only_candidate'] = [exhibit_only(str(t)) for t in secs['section_text']]
ex_all = secs.groupby('fcc_form499')['exhibit_only_candidate'].agg(['sum', 'count'])
log('All 1,078 filings, exhibit-only candidates by stratum (heuristic, unverified): ' +
    '; '.join(f"{'treated' if g == 1 else 'control'} {int(r['sum'])}/{int(r['count'])} ({100 * r['sum'] / r['count']:.1f}%)"
              for g, r in ex_all.iterrows()))
secs[secs['exhibit_only_candidate'] == 1][['accession', 'fcc_form499', 'section_text']].assign(
    section_text=lambda x: x['section_text'].str[:500]).to_csv(OUT / 'd3_exhibit_only_candidates.csv', index=False)

hdr('Sheet 75 — T-Mobile 2018-04-30 (0001104659-18-028086)')
s75 = D[D['sheet_id'] == '75'].iloc[0]
log(f"Reference: exec={s75['exec_departure']} CEO={s75['ceo_departure']} (blind CEO {s75['blind_ceo']}); "
    f"{s75['person_and_role']}")
log(f"v2: exec={s75['clf_exec_departure']} (new-only {s75['clf_exec_departure_new']}) CEO={s75['clf_ceo_departure']}; "
    f"persons: {s75['clf_person_role']}")
E = pd.read_csv(OUT / 'c2_departure_events.csv', dtype=str)
le = E[(E['cik'] == '1283699') & (E['pkey'].isin(['legere', 'sievert', 'carter']))]
log(le[['grp', 'pkey', 'first_date', 'n_filings', 'accessions', 'is_ceo']].to_string(index=False))
log("De-duplication: the 2018-04-30 filing forms its OWN Legere event (exec group, is_ceo=0: the President title), "
    "separate from the Legere CEO-departure event first dated 2019-11-18 (0001193125-19-294093), because the two "
    "disclosures are 567 days apart (> the 540-day merge window). v2 therefore does NOT treat the 2018 filing as the "
    "first disclosure of Legere's CEO departure.")
PRw = pd.read_csv(OUT / 'c2_person_rows.csv', dtype=str)
for _, r in PRw[(PRw['accession'] == '0001104659-18-028086') & (PRw['action'] == 'departure')].iterrows():
    log(f"  v2 row: {r['person']} [{r['role_class']}] verb='{r['verb']}' :: {r['sentence'][:380]}")

# adjudication workbook: add the audit tab
book2 = pd.read_excel(OUT / 'ADJUDICATION.xlsx', sheet_name=None)
blank = {'adjudicated_exec (Y/N)': '', 'adjudicated_ceo (Y/N)': '', 'adjudicated_director_only (Y/N)': '',
         'adjudicated_pre_announced (Y/N/unclear)': '', 'adjudicator': '', 'adjudication_note': ''}
with pd.ExcelWriter(OUT / 'ADJUDICATION.xlsx', engine='openpyxl') as xw:
    for k, v in book2.items():
        if k != 'audit_v2':
            v.to_excel(xw, sheet_name=k, index=False)
    DS.assign(**blank).to_excel(xw, sheet_name='audit_v2', index=False)
log(f'\nADJUDICATION.xlsx: added tab audit_v2 ({len(DS)} rows)')
(OUT / '201_audit.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
