"""
ESSAY 3 QUERY 2 — D3 ROUND 2, ADJUDICATION WORKBOOK, AND v1 -> v2 OUTCOME-FLAG CHANGES (NEW)
==========================================================================================
1. Round 2: classifier v2 (scripts/195, commit 6f7be7a) answers (validation_classifier_HIDDEN_R2.csv,
   committed edbf670) vs the round-2 reference codes (Claude, blind to v2; file of record
   VALIDATION_SHEET_R2_CLAUDE_RATER.xlsx, checked cell by cell against VALIDATION_REFERENCE_CODES_R2.psv).
   Per field: n, agreement, Cohen's kappa, positives, and precision / recall with exact
   (Clopper-Pearson) 95% CIs. Variant A = reference as given vs the classifier's any-mention codes;
   variant B = restated reference departures recoded N vs the classifier's new-only codes.
   Sheet 9 pre-announced: verified Y primary, blind 'unclear' secondary. Reference 'unclear' cells are
   dropped from that field (sheet 29, exec). Sheet 29 is reported as a recall test of the implied-departure
   rule (which fires on 0 of 1,078 filings).
2. ADJUDICATION.xlsx: every disagreement in round 1 (v1) and round 2 (v2), plus rows the reference coder
   flagged "candidate for adjudication", with blank adjudication columns.
3. Outcome-flag changes, v1 (c_outcomes_events.csv) -> v2 (c2_outcomes_events.csv; primary = one departure
   per person dated to the earliest disclosing filing; rs_ = restatement-dated), at 30/90/180 days on both
   anchors, treated vs control, on the Query 1 Essay 3 sample (340) and the Query 2 scope (341).
4. Prints the November 2019 T-Mobile passage naming Carter (0001193125-19-294093).
Outputs: outputs/essay3_q2/d3_r2_agreement.csv, d3_r2_disagreements.csv, ADJUDICATION.xlsx,
         e_flag_changes_v1_v2.csv, 197_r2.log
"""

import re
import sys
import glob
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


# ------------------------------------------------------------------ 1. round 2
hdr('ROUND 2 — classifier v2 vs round-2 reference codes (Claude, blind to v2; Tim did not hand-code)')
xl = OUT / 'VALIDATION_SHEET_R2_CLAUDE_RATER.xlsx'
log(f'File of record: {xl} sha256 {hashlib.sha256(xl.read_bytes()).hexdigest()}')
X = pd.read_excel(xl, sheet_name='claude_codes', dtype=str).fillna('')
T = pd.read_csv(OUT / 'VALIDATION_REFERENCE_CODES_R2.psv', sep='|', dtype=str, keep_default_na=False)
X.columns = T.columns
X['sheet_id'] = X['sheet_id'].str.replace(r'\.0$', '', regex=True)
nd = sum(T.at[i, c].strip() != X.at[i, c].strip() for i in range(len(T)) for c in T.columns)
log(f'Workbook vs pasted text: {len(X)} rows, {nd} cell differences')
assert nd == 0
C = pd.read_csv(OUT / 'validation_classifier_HIDDEN_R2.csv', dtype=str, keep_default_na=False)
S = pd.read_excel(OUT / 'VALIDATION_SHEET_R2.xlsx', sheet_name='coding', dtype=str).fillna('')
D = X.merge(C, on='sheet_id').merge(S[['sheet_id', 'filing_date', 'url', 'item_5_02_text (caption stripped)']]
                                    .rename(columns={'filing_date': 'sheet_fd', 'item_5_02_text (caption stripped)': 'text'}),
                                    on='sheet_id')
assert len(D) == 30 and (D['filing_date'] == D['sheet_fd']).all()
nex, nceo = int((D['exec_departure'] == 'Y').sum()), int((D['ceo_departure'] == 'Y').sum())
log(f'Round 2 contains {nex} executive departures and {nceo} CEO departures (reference codes); '
    f'CEO-departure validation therefore rests on round 1, which informed v2\'s fixes.')

D['pre_primary'] = D['pre_announced']
D['pre_secondary'] = np.where(D['sheet_id'] == '9', 'unclear', D['pre_announced'])
B = D.copy()
m = B['restates_prior_disclosure'] == 'Y'
for f in ['exec_departure', 'ceo_departure', 'director_only_departure']:
    B.loc[m, f] = 'N'


def cp(k, n):
    if n == 0:
        return (None, None, None)
    lo, hi = proportion_confint(k, n, alpha=0.05, method='beta')
    return (round(k / n, 4), round(lo, 4), round(hi, 4))


def score(label, ref, clf, drop_unclear=True):
    x = pd.DataFrame({'r': ref.values, 'c': clf.values})
    if drop_unclear:
        x = x[x['r'] != 'unclear']
    tp = int(((x.r == 'Y') & (x.c == 'Y')).sum())
    fp = int(((x.r != 'Y') & (x.c == 'Y')).sum())
    fn = int(((x.r == 'Y') & (x.c != 'Y')).sum())
    k = cohen_kappa_score(x.r, x.c) if x.r.nunique() > 1 or x.c.nunique() > 1 else float('nan')
    p, r = cp(tp, tp + fp), cp(tp, tp + fn)
    return dict(field=label, n=len(x), agreement=round((x.r == x.c).mean(), 4), kappa=round(k, 4),
                ref_positives=int((x.r == 'Y').sum()), clf_positives=int((x.c == 'Y').sum()), tp=tp, fp=fp, fn=fn,
                precision=p[0], precision_ci95=f'[{p[1]}, {p[2]}]' if p[0] is not None else 'n/a (no clf positives)',
                recall=r[0], recall_ci95=f'[{r[1]}, {r[2]}]' if r[0] is not None else 'n/a (no ref positives)')


rows = [score('exec departure (A: any)', D['exec_departure'], D['clf_exec_departure']),
        score('exec departure (B: new only)', B['exec_departure'], D['clf_exec_departure_new']),
        score('CEO departure (A: any)', D['ceo_departure'], D['clf_ceo_departure']),
        score('CEO departure (B: new only)', B['ceo_departure'], D['clf_ceo_departure_new']),
        score('director-only departure', D['director_only_departure'], D['clf_director_only_departure']),
        score('pre-announced (sheet 9 verified Y, PRIMARY)', D['pre_primary'], D['clf_pre_announced'], False),
        score('pre-announced (sheet 9 blind unclear, SECONDARY)', D['pre_secondary'], D['clf_pre_announced'], False)]
A = pd.DataFrame(rows)
A.to_csv(OUT / 'd3_r2_agreement.csv', index=False)
log(A.to_string(index=False))

s29 = D[D['sheet_id'] == '29'].iloc[0]
log(f"\nSheet 29 (Sysco 2023-10-17; interim CAO, implied departure; reference exec = 'unclear'): v2 calls "
    f"exec={s29['clf_exec_departure']}, CEO={s29['clf_ceo_departure']}, director-only="
    f"{s29['clf_director_only_departure']}, implied_succession flag={s29['clf_implied_succession']}, "
    f"persons='{s29['clf_person_role']}', action={s29['clf_action']}")
for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z])', s29['text']):
    if re.search(r'(?i)stone|succe|interim|chief accounting', sent):
        log(f'   text: {sent[:400]}')

FIELDS = [('exec_departure', 'clf_exec_departure'), ('ceo_departure', 'clf_ceo_departure'),
          ('director_only_departure', 'clf_director_only_departure'), ('pre_primary', 'clf_pre_announced')]
dis = []
for _, r in D.iterrows():
    fl = [f for f, c in FIELDS if r[f] != 'unclear' and r[f] != r[c]]
    if fl or r['sheet_id'] == '29':
        dis.append(dict(round=2, classifier='v2 (6f7be7a)', sheet_id=int(r['sheet_id']), company=r['company'],
                        filing_date=r['filing_date'], url=r['url'], fields_in_dispute=', '.join(fl) or 'exec: reference unclear',
                        reference=' / '.join(f'{f.split("_")[0]}={r[f]}' for f, _ in FIELDS),
                        classifier_codes=' / '.join(f'{f.split("_")[0]}={r[c]}' for f, c in FIELDS),
                        restates_prior_disclosure=r['restates_prior_disclosure'], reference_person=r['person_and_role'],
                        classifier_person=r['clf_person_role'], reference_note=r['notes'], text_excerpt=r['text'][:1500]))
DS = pd.DataFrame(dis)
DS.to_csv(OUT / 'd3_r2_disagreements.csv', index=False)
log(f'\nRound-2 filings in dispute (any field, plus sheet 29): {len(DS)}')
for _, r in DS.iterrows():
    log(f"  [{r['sheet_id']}] {r['company']} {r['filing_date']} | {r['fields_in_dispute']}\n     ref: {r['reference']} | "
        f"{r['reference_person']}\n     v2 : {r['classifier_codes']} | {r['classifier_person']}\n     note: {r['reference_note']}")

# ------------------------------------------------------------------ 2. adjudication workbook
r1 = pd.read_csv(OUT / 'd3_disagreements.csv', dtype=str).fillna('')
R1 = pd.DataFrame(dict(round=1, classifier='v1 (d39bc6d)', sheet_id=r1['sheet_id'], company=r1['company'],
                       filing_date=r1['filing_date'], url=r1['url'], fields_in_dispute=r1['fields'],
                       reference=r1['ref'], classifier_codes=r1['clf'],
                       restates_prior_disclosure=r1['restates'], reference_person=r1['ref_person'],
                       classifier_person=r1['clf_person'], reference_note=r1['ref_note'],
                       text_excerpt=r1['text_excerpt']))
rf1 = pd.read_csv(OUT / 'VALIDATION_REFERENCE_CODES_R1.psv', sep='|', dtype=str, keep_default_na=False)
FL = pd.concat([rf1[rf1['notes'].str.contains('adjudication', case=False)].assign(round=1),
                X[X['notes'].str.contains('adjudication', case=False)].assign(round=2)])
blank = {'adjudicated_exec (Y/N)': '', 'adjudicated_ceo (Y/N)': '', 'adjudicated_director_only (Y/N)': '',
         'adjudicated_pre_announced (Y/N/unclear)': '', 'adjudicator': '', 'adjudication_note': ''}
readme = pd.DataFrame({'ADJUDICATION — Essay 3 Query 2 validation': [
    'Created 2026-09-11 by scripts/197. No earlier ADJUDICATION.xlsx existed in the repository or on disk.',
    'Tabs: round1_v1 = every round-1 disagreement between frozen classifier v1 (d39bc6d) and the round-1 reference '
    'codes; round2_v2 = every round-2 disagreement between classifier v2 (6f7be7a) and the round-2 reference codes '
    '(plus sheet 29, reference exec = unclear); flagged_by_reference = rows the reference coder marked "candidate '
    'for adjudication".',
    'Reference codes are Claude\'s (blind to the classifier, with a verification pass). Tim did not hand-code.',
    'Fill the adjudicated_* columns from the filing text; the classifier and reference codes are both shown.']})
with pd.ExcelWriter(OUT / 'ADJUDICATION.xlsx', engine='openpyxl') as xw:
    readme.to_excel(xw, sheet_name='README', index=False)
    R1.assign(**blank).to_excel(xw, sheet_name='round1_v1', index=False)
    DS.assign(**blank).to_excel(xw, sheet_name='round2_v2', index=False)
    FL.assign(**blank).to_excel(xw, sheet_name='flagged_by_reference', index=False)
log(f'\nADJUDICATION.xlsx: round1_v1 {len(R1)} rows, round2_v2 {len(DS)} rows, flagged_by_reference {len(FL)} rows')

# ------------------------------------------------------------------ 3. outcome-flag changes v1 -> v2
hdr('OUTCOME-FLAG CHANGES, classifier v1 -> v2 (all 1,078 filings; per event)')
V1 = pd.read_csv(OUT / 'c_outcomes_events.csv')
V2 = pd.read_csv(OUT / 'c2_outcomes_events.csv')
key = ['final_cik', 'breach_date']
M = V1.merge(V2, on=key, suffixes=('_v1', '_v2'))
cv = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
M = M.merge(cv[key + ['immediate_disclosure']], on=key)
M['treat'] = M['fcc_form499_v1']
chg = []
for samp, d in [('Q1 Essay 3 sample 340', M[M['immediate_disclosure'].notna()]), ('Q2 scope 341', M)]:
    for outcome in ['exec_departure', 'ceo_departure', 'director_departure']:
        for anc in ['rd', 'bd']:
            for w in (30, 90, 180):
                c1 = f'{outcome}_{w}_{anc}_v1'
                for ver, c2 in [('v2 primary (person-merged)', f'{outcome}_{w}_{anc}_v2'),
                                ('v2 rs (restatement-dated)', f'rs_{outcome}_{w}_{anc}')]:
                    for g, lab in [(1, 'treated'), (0, 'control')]:
                        x = d[d['treat'] == g]
                        chg.append(dict(sample=samp, outcome=outcome, anchor=anc, window=w, version=ver, group=lab,
                                        n=len(x), v1_rate=round(x[c1].mean(), 4), v2_rate=round(x[c2].mean(), 4),
                                        flips_0_to_1=int(((x[c1] == 0) & (x[c2] == 1)).sum()),
                                        flips_1_to_0=int(((x[c1] == 1) & (x[c2] == 0)).sum())))
CH = pd.DataFrame(chg)
CH.to_csv(OUT / 'e_flag_changes_v1_v2.csv', index=False)
show = CH[(CH['sample'] == 'Q1 Essay 3 sample 340')]
log(show.to_string(index=False))
anyc = (M[[f'any_502_{w}_{a}_v1' for w in (30, 90, 180) for a in ('rd', 'bd')]].values ==
        M[[f'any_502_{w}_{a}_v2' for w in (30, 90, 180) for a in ('rd', 'bd')]].values).all()
log(f'any_502 flags identical across v1 and v2 (all windows, both anchors): {bool(anyc)}')

# ------------------------------------------------------------------ 4. Carter passage
hdr('November 2019 T-Mobile filing naming Carter (0001193125-19-294093)')
spec = importlib.util.spec_from_file_location('clf2', 'scripts/195_essay3_q2_classifier_v2.py')
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)
sf = pd.read_csv(OUT / 'b_scope_filings.csv', dtype={'accession': str})
fr = sf[sf['accession'] == '0001193125-19-294093'].iloc[0]
log(f"Filed {fr['filing_date']}; items {fr['items']}; {fr['local_file']}")
sec = clf.strip_caption(clf.section_502(clf.to_text(Path(fr['local_file']).read_bytes())))
i = sec.find('with J. Braxton Carter')
log('Introduction (verbatim): ' + sec[max(0, i - 160): i + 330])
j = sec.find('Carter Amendment The Carter Amendment')
log('Carter Amendment paragraph (verbatim): ' + sec[j: j + 1400])
k = sec.find('will cease to serve as CEO')
log('Legere sentence (verbatim): ' + sec[max(0, k - 45): k + 130])
(OUT / '197_r2.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
