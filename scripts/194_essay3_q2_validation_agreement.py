"""
ESSAY 3 QUERY 2 — PART D3: CLASSIFIER vs REFERENCE CODES (NEW)
=========================================================
Compares the frozen classifier (scripts/188, freeze commit d39bc6d, blob af2c97c) with the reference
codes in outputs/essay3_q2/VALIDATION_REFERENCE_CODES_R1.psv (Claude-coded reference; Tim did not hand-code) (see VALIDATION_REFERENCE_CODES_R1_README.txt for
provenance and the coder's interpretive rules).

Fields: exec departure, CEO departure, director-only departure (Y/N), pre-announced (Y/N/unclear),
person agreement on departing people (surname match).
Samples: all 80; excluding the 7 T-Mobile calibration filings whose Query 1 hand reads were published in the
Query 1 report (identified by accession, source = calibration, CIK 1283699).
Variants: (A) reference codes as given (restated departures = Y, coder rule 3); (B) restated departures
recoded N (restates_prior_disclosure = Y -> exec/CEO/director = N); (S31) sheet 31 CEO at its blind
value 'unclear' (dropped from the CEO field) instead of the post-verification Y.
Outputs: outputs/essay3_q2/d3_agreement.csv, d3_disagreements.csv, 194_agreement.log
"""

import re
import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


T = pd.read_csv(OUT / 'VALIDATION_REFERENCE_CODES_R1.psv', sep='|', dtype=str, keep_default_na=False)
C = pd.read_csv(OUT / 'validation_classifier_HIDDEN.csv', dtype=str, keep_default_na=False)
S = pd.read_excel(OUT / 'VALIDATION_SHEET.xlsx', sheet_name='coding', dtype=str).fillna('')
assert len(T) == 80 and T['sheet_id'].nunique() == 80, 'expected 80 coded rows'
D = T.merge(C, on='sheet_id').merge(S[['sheet_id', 'company', 'filing_date', 'url',
                                        'item_5_02_text (caption stripped)']].rename(
    columns={'company': 'sheet_company', 'filing_date': 'sheet_filing_date',
             'item_5_02_text (caption stripped)': 'text'}), on='sheet_id')
assert (D['filing_date'] == D['sheet_filing_date']).all(), 'coded rows must match sheet rows'
D['cik'] = D['url'].str.extract(r'/data/(\d+)/').astype(int)
D['tmobile_cal7'] = ((D['source'] == 'calibration') & (D['cik'] == 1283699)).astype(int)
log(f'Rows matched: {len(D)} | T-Mobile calibration filings: {int(D["tmobile_cal7"].sum())} '
    f'(sheet_ids {sorted(D.loc[D.tmobile_cal7 == 1, "sheet_id"].astype(int))})')
s31 = D[D['sheet_id'] == '31'].iloc[0]
log(f'Sheet 31: source={s31["source"]}, CIK {s31["cik"]}, accession {s31["accession"]} '
    f'-> in the T-Mobile calibration 7: {bool(s31["tmobile_cal7"])}')

FIELDS = [('exec_departure', 'clf_exec_departure'), ('ceo_departure', 'clf_ceo_departure'),
          ('director_only_departure', 'clf_director_only_departure'), ('pre_announced', 'clf_pre_announced')]


def variant(d, v):
    d = d.copy()
    if v == 'B':
        m = d['restates_prior_disclosure'] == 'Y'
        for f in ['exec_departure', 'ceo_departure', 'director_only_departure']:
            d.loc[m, f] = 'N'
        d.loc[m & (d['exec_departure'] == 'N') & (d['director_only_departure'] == 'N'), 'pre_announced'] = 'N'
    return d


rows = []
for v in ['A', 'B']:
    for samp, sub in [('all 80', D), ('excl. T-Mobile calibration 7', D[D['tmobile_cal7'] == 0])]:
        dv = variant(sub, v)
        for f, cf in FIELDS:
            x = dv[[f, cf]]
            if f == 'ceo_departure' and v == 'A':
                pass
            keep = ~x[f].isin(['unclear', '']) if f != 'pre_announced' else x[f] != ''
            x = x[keep]
            agree = (x[f] == x[cf]).mean()
            try:
                k = cohen_kappa_score(x[f], x[cf])
            except Exception:
                k = float('nan')
            tp = int(((x[f] == 'Y') & (x[cf] == 'Y')).sum())
            fp = int(((x[f] != 'Y') & (x[cf] == 'Y')).sum())
            fn = int(((x[f] == 'Y') & (x[cf] != 'Y')).sum())
            rows.append(dict(variant=v, sample=samp, field=f, n=len(x), agreement=round(agree, 4),
                             kappa=round(k, 4), ref_Y=int((x[f] == 'Y').sum()), clf_Y=int((x[cf] == 'Y').sum()),
                             both_Y=tp, clf_only_Y=fp, ref_only_Y=fn,
                             precision=round(tp / (tp + fp), 4) if tp + fp else None,
                             recall=round(tp / (tp + fn), 4) if tp + fn else None))
# S31 variant: CEO field with sheet 31 at its blind value (unclear -> dropped)
for samp, sub in [('all 80', D), ('excl. T-Mobile calibration 7', D[D['tmobile_cal7'] == 0])]:
    x = sub[sub['sheet_id'] != '31'][['ceo_departure', 'clf_ceo_departure']]
    rows.append(dict(variant='A-S31blind', sample=samp, field='ceo_departure', n=len(x),
                     agreement=round((x.iloc[:, 0] == x.iloc[:, 1]).mean(), 4),
                     kappa=round(cohen_kappa_score(x.iloc[:, 0], x.iloc[:, 1]), 4),
                     ref_Y=int((x.iloc[:, 0] == 'Y').sum()), clf_Y=int((x.iloc[:, 1] == 'Y').sum())))
A = pd.DataFrame(rows)
A.to_csv(OUT / 'd3_agreement.csv', index=False)
log('\n' + A.to_string(index=False))


# person agreement on departing people (exec rows where both say Y)
def surnames(s):
    parts = re.split(r';|\band\b|,\s*(?=[A-Z][a-z]+\s+[A-Z])', s)
    out = set()
    for p in parts:
        nm = re.findall(r"[A-ZÀ-Þ][A-Za-zÀ-ÿ'’\-]+", p.split('(')[0])
        nm = [w for w in nm if w not in {'CEO', 'CFO', 'COO', 'EVP', 'SVP', 'VP', 'President', 'Chief', 'Officer',
                                         'Executive', 'Vice', 'Senior', 'Director', 'Jr', 'III', 'GM', 'Chairman'}]
        if nm:
            out.add(nm[-1].lower())
    return out


both = D[(D['exec_departure'] == 'Y') & (D['clf_exec_departure'] == 'Y')]
pm = [bool(surnames(r['person_and_role']) & surnames(r['clf_person_role'])) for _, r in both.iterrows()]
log(f'\nPerson agreement (exec departure Y in both): {sum(pm)}/{len(pm)} share at least one departing surname')

# disagreements
dis = []
for _, r in D.iterrows():
    diffs = [f for f, cf in FIELDS if r[f] not in ('', ) and r[f] != r[cf]]
    if diffs:
        dis.append(dict(sheet_id=int(r['sheet_id']), company=r['company'], filing_date=r['filing_date'],
                        tmobile_cal7=r['tmobile_cal7'], source=r['source'], fields=', '.join(diffs),
                        ref=' / '.join(f"{f[:4]}={r[f]}" for f, _ in FIELDS),
                        clf=' / '.join(f"{f[:4]}={r[cf]}" for f, cf in FIELDS),
                        restates=r['restates_prior_disclosure'], ref_person=r['person_and_role'],
                        clf_person=r['clf_person_role'], ref_note=r['notes'], url=r['url'],
                        text_excerpt=r['text'][:700]))
DS = pd.DataFrame(dis).sort_values('sheet_id')
DS.to_csv(OUT / 'd3_disagreements.csv', index=False)
log(f'\nFilings with any disagreement: {len(DS)} of 80')
for _, r in DS.iterrows():
    log(f"\n[{r['sheet_id']}] {r['company']} {r['filing_date']} ({r['source']}{', TMO-cal7' if r['tmobile_cal7'] else ''}) "
        f"fields: {r['fields']} | restates={r['restates']}\n   ref : {r['ref']} | {r['ref_person']}\n"
        f"   clf : {r['clf']} | {r['clf_person']}\n   note: {r['ref_note']}\n   text: {r['text_excerpt'][:450]}")
(OUT / '194_agreement.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
