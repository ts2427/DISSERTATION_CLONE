"""
ESSAY 3 QUERY 2 — PART G6 + T-MOBILE TIMELINE (NEW; print, do not interpret)
============================================================================
G6  T-Mobile (CIK 1283699; MetroPCS before 2013-04-29) on the NOTIFICATION anchor with the final classifier v2 (scripts/195,
    6f7be7a) codes and flags: for every T-Mobile event, every executive departure (ruling 1: one per person, dated to its
    earliest disclosing filing) in (reported_date, reported_date + 180d], with the text excerpt, the context flags of the
    first disclosing filing, pre-announced status relative to reported_date, and controlled-holder affiliation from the
    parsed proxy rosters (G3; rosters list directors only). Restatement-dated mentions in the window are listed separately.
    EX-99 excerpts for King (2016-02-19) and Legere-to-Sievert (2020-04-01). The 2019-11-26 event: dates of the Sievert
    employment agreement and of the public CEO-succession announcement (0001193125-19-294093, 2019-11-18) relative to
    that event's reported_date and breach_date.
Timeline: G2 (breaches, public notifications, incident 8-Ks), G3 by proxy year (controlled-company status; first committee
    cyber mentions; CD&A statements that adjust pay for the August 2021 cyberattack, re-scanned from the full proxy text),
    G4 (cyber-related charges, settlements, insurance recoveries; Item 1C role sentences), G6 (executive and director
    departures) on one dated file.
Outputs: outputs/essay3_q2/g6_case_table.csv, g6_restatement_dated.csv, tmobile_timeline.csv, 203_case.log
"""

import re
import sys
import gzip
import glob
import html
import importlib.util
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
TM = 1283699
METRO_END = pd.Timestamp('2013-04-29')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 100 + '\n' + t + '\n' + '=' * 100)


spec = importlib.util.spec_from_file_location('clf2', 'scripts/195_essay3_q2_classifier_v2.py')
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev = ev[ev['final_cik'] == TM].copy()
ev['bdt'], ev['rdt'] = pd.to_datetime(ev['breach_date']), pd.to_datetime(ev['reported_date'])
samp = pd.read_csv(OUT / 'e_analysis_sample.csv', low_memory=False)
ev = ev.merge(samp[['final_cik', 'breach_date', 'in_analysis_sample']], on=['final_cik', 'breach_date'], how='left')
ev['in_analysis_sample'] = ev['in_analysis_sample'].fillna(0).astype(int)
E = pd.read_csv(OUT / 'c2_departure_events.csv', dtype={'accessions': str, 'first_accession': str})
E = E[E['cik'] == TM].copy()
E['first_date'] = pd.to_datetime(E['first_date'])
F = pd.read_csv(OUT / 'c2_filing_codes.csv', dtype={'accession': str})
F['fdt'] = pd.to_datetime(F['filing_date'])
F['ref_list'] = F['ref_dates'].fillna('').apply(lambda s: [pd.Timestamp(x) for x in s.split(';') if x])
Fx = F.set_index('accession')
PR = pd.read_csv(OUT / 'c2_person_rows.csv', dtype={'accession': str})
R = pd.read_csv(OUT / 'g3_director_roster.csv', dtype=str).fillna('')
aff = R[R['affiliation_as_stated'].str.contains('Deutsche|SoftBank', case=False)]
FLAGS = ['flag_retirement', 'flag_health', 'flag_transaction', 'flag_termination', 'flag_severance_release',
         'flag_no_disagreement']


def affiliation(persons):
    out = []
    for p in str(persons).split(' | '):
        sur = (clf.person_key(p) or '').lower()
        hit = aff[aff['name'].str.lower().str.contains(r'\b' + re.escape(sur) + r'\b', regex=True)] if sur else aff.iloc[0:0]
        out.append(f"{p}: {'; '.join(sorted(set(hit['affiliation_as_stated'] + ' designee (proxy ' + hit['proxy_date'] + ')')))}"
                   if len(hit) else f'{p}: not a Deutsche Telekom/SoftBank designee in the parsed rosters (2021, 2022 '
                                    f'nominee tables; rosters list directors only)')
    return ' || '.join(out)


def excerpt(acc, persons):
    rows = PR[(PR['accession'] == acc) & (PR['action'] == 'departure')]
    for p in str(persons).split(' | '):
        k = clf.person_key(p)
        m = rows[rows['person'].apply(lambda x: clf.person_key(x) == k)]
        if len(m):
            return m['sentence'].iloc[0][:450]
    return rows['sentence'].iloc[0][:450] if len(rows) else ''


hdr('G6 — T-Mobile executive departures within 180 days of NOTIFICATION (v2; one per person, earliest disclosure)')
rows, rs_rows = [], []
for _, e in ev.sort_values('bdt').iterrows():
    t0 = e['rdt']
    x = E[(E['grp'] == 'exec') & (E['first_date'] > t0) & (E['first_date'] <= t0 + timedelta(days=180))]
    if len(x) == 0:
        rows.append(dict(breach_date=e['breach_date'], reported_date=str(t0.date()), in_analysis_sample=e['in_analysis_sample'],
                         departure='none'))
    for _, d in x.sort_values('first_date').iterrows():
        fr = Fx.loc[d['first_accession']]
        rows.append(dict(breach_date=e['breach_date'], reported_date=str(t0.date()), in_analysis_sample=e['in_analysis_sample'],
                         departure=d['persons'], is_ceo=int(d['is_ceo']), first_disclosure=str(d['first_date'].date()),
                         days_from_notification=(d['first_date'] - t0).days, first_accession=d['first_accession'],
                         filer_vintage='MetroPCS' if d['first_date'] <= METRO_END else 'T-Mobile US',
                         pre_announced=clf.pre_announced(fr, fr['ref_list'], t0),
                         flags=','.join(f[5:] for f in FLAGS if fr[f] == 1) or 'none',
                         controlled_holder_affiliate=affiliation(d['persons']),
                         excerpt=excerpt(d['first_accession'], d['persons'])))
    # restatement-dated view: filings in the window coded as exec departures whose person was first disclosed earlier
    fw = F[(F['cik'] == TM) & (F['fdt'] > t0) & (F['fdt'] <= t0 + timedelta(days=180)) & (F['exec_departure'] == 1)]
    for _, f in fw.iterrows():
        if f['accession'] in set(x['first_accession']):
            continue
        rs_rows.append(dict(breach_date=e['breach_date'], reported_date=str(t0.date()), filing_date=str(f['fdt'].date()),
                            days_from_notification=(f['fdt'] - t0).days, accession=f['accession'],
                            persons='; '.join(PR[(PR['accession'] == f['accession']) & (PR['action'] == 'departure') &
                                                 PR['role_class'].isin(list(clf.EXEC_CLASSES))]['person'].astype(str).unique())))
G6 = pd.DataFrame(rows)
G6.to_csv(OUT / 'g6_case_table.csv', index=False)
RSD = pd.DataFrame(rs_rows)
RSD.to_csv(OUT / 'g6_restatement_dated.csv', index=False)
dep = G6[G6['departure'] != 'none']
for _, r in G6.iterrows():
    if r['departure'] == 'none':
        log(f"  {r['breach_date']} (notified {r['reported_date']}; sample {r['in_analysis_sample']}): none")
    else:
        log(f"  {r['breach_date']} (notified {r['reported_date']}; sample {r['in_analysis_sample']}): +{r['days_from_notification']}d "
            f"{r['first_disclosure']} {r['departure']}{' [CEO]' if r['is_ceo'] else ''} | pre-announced {r['pre_announced']} | "
            f"flags {r['flags']} | {r['first_accession']} ({r['filer_vintage']})\n      \"{r['excerpt'][:300]}\"\n"
            f"      affiliation: {r['controlled_holder_affiliate'][:220]}")
log(f"\nEvent-departure pairs within 180d of notification: {len(dep)}; distinct departures (person x first filing): "
    f"{dep[['departure', 'first_accession']].drop_duplicates().shape[0]}; pairs flagged pre-announced Y "
    f"{int((dep['pre_announced'] == 'Y').sum())}, retirement {int(dep['flags'].str.contains('retirement').sum())}, "
    f"transaction {int(dep['flags'].str.contains('transaction').sum())}; carrying ANY of pre-announced/retirement/transaction "
    f"{int(((dep['pre_announced'] == 'Y') | dep['flags'].str.contains('retirement|transaction')).sum())} of {len(dep)}")
u = dep.drop_duplicates(['departure', 'first_accession'])
log(f"Distinct departures carrying ANY of pre-announced/retirement/transaction: "
    f"{int(((u['pre_announced'] == 'Y') | u['flags'].str.contains('retirement|transaction')).sum())} of {len(u)}")
log(f'Restatement-dated additions (filings in the window re-mentioning a departure first disclosed earlier): {len(RSD)}')
for _, r in RSD.iterrows():
    log(f"  {r['breach_date']}: +{r['days_from_notification']}d {r['filing_date']} {r['accession']} {r['persons']}")

hdr('EX-99 excerpts (King 2016-02-19; Legere-to-Sievert 2020-04-01)')
EXL = pd.read_csv(OUT / 'b_exhibits_log.csv', dtype=str).fillna('')
for acc, lab in [('0001193125-16-470124', 'King'), ('0001193125-20-093622', 'Legere-to-Sievert')]:
    x = EXL[EXL['accession'] == acc]
    got = x[x['local_file'] != '']
    if len(got) == 0:
        log(f"  {lab} ({acc}): {x['status'].iloc[0] if len(x) else 'not in the exhibit log'} — no EX-99 excerpt exists")
        continue
    t = clf.to_text(Path(got['local_file'].iloc[0]).read_bytes())
    sents = [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', t) if re.search(r'Legere|Sievert|Chief Executive|CEO', s)]
    log(f"  {lab} ({acc}, {Path(got['local_file'].iloc[0]).name}):")
    for s in sents[:4]:
        log(f'    "{s[:420]}"')

hdr('2019-11-26 event: CEO succession timing')
e19 = ev[ev['breach_date'] == '2019-11-26'].iloc[0]
f19 = glob.glob(f'Data/edgar/item5_02_text/{TM}/0001193125-19-294093_*')[0]
t19 = clf.to_text(Path(f19).read_bytes())
m = re.search(r'[^.]*Sievert Employment Agreement[^.]*\.', t19)
ag = re.search(r'on\s+(November\s+\d{1,2},\s+2019)[^.]{0,160}employment\s+agreement\s+with\s+Mr\.\s+Sievert', t19)
log(f"Filing 0001193125-19-294093 filed 2019-11-18 (public announcement of the succession). Sentence naming the agreement: "
    f"\"{m.group(0).strip()[:400] if m else 'not found'}\"")
agd = pd.Timestamp(ag.group(1)) if ag else pd.Timestamp('2019-11-15')
log(f"Sievert employment agreement date: {agd.date()} ({'from the filing text' if ag else 'from the 2020-04-01 filing text: dated November 15, 2019'})")
for lab, dt in [('Sievert employment agreement', agd), ('public announcement (8-K filed)', pd.Timestamp('2019-11-18'))]:
    log(f"  {lab} {dt.date()}: {(dt - e19['rdt']).days:+d} days vs reported_date {e19['rdt'].date()}; "
        f"{(dt - e19['bdt']).days:+d} days vs breach_date {e19['bdt'].date()}")

hdr('TIMELINE (tmobile_timeline.csv)')
TL = []
for _, e in ev.iterrows():
    TL.append(dict(date=e['breach_date'], type='breach occurrence (PRC)', description=f"{e['org_name']}; "
                   f"{int(e['n_source_records'])} record(s); in analysis sample {e['in_analysis_sample']}", source='CANONICAL_V3'))
g2 = pd.read_csv(OUT / 'g2_disclosure_channel.csv', dtype=str).fillna('')
for _, r in g2.iterrows():
    TL.append(dict(date=r['reported_date'], type='public notification (PRC reported_date)',
                   description=f"breach {r['breach_date']}; PRC source {r['prc_source_types']}; incident 8-K "
                               f"{r['incident_8k_accession'] or 'none within +/-30d'}", source='g2_disclosure_channel'))
p2 = pd.read_csv(OUT / 'g2_8k_passages.csv', dtype=str).fillna('')
for _, r in p2[p2['incident_sentences'].astype(int) > 0].drop_duplicates('accession').iterrows():
    TL.append(dict(date=r['filing_date'], type='incident 8-K (7.01/8.01)', description=r['first_incident_passages'][:300],
                   source=r['accession']))
for _, d in E.iterrows():
    TL.append(dict(date=str(d['first_date'].date()), type=f"{d['grp']} departure (v2, first disclosure)"
                   + (' [CEO]' if d['is_ceo'] else ''), description=f"{d['persons']}"
                   + (' (MetroPCS-era filer)' if d['first_date'] <= METRO_END else ''), source=d['first_accession']))
cc = pd.read_csv(OUT / 'g3_controlled_company.csv', dtype=str).fillna('')
for pdt, g in cc.groupby('proxy_date'):
    s = g[g['controlled_company_sentence'].str.lower().isin(['true', '1'])]
    s = s if len(s) else g
    TL.append(dict(date=pdt, type='proxy: controlled-company status', description=f"holders {s['holders_named'].iloc[0]}; "
                   f"stated % {s['percentages'].iloc[0]}", source=s['accession'].iloc[0]))
cm = pd.read_csv(OUT / 'g3_committee_cyber.csv', dtype=str).fillna('')
for (com, term), g in cm.groupby(['committee', 'term']):
    TL.append(dict(date=g['first_proxy_date'].iloc[0], type='proxy: first committee cyber/privacy mention',
                   description=f'{com} — {term}', source=g.sort_values('proxy_date')['accession'].iloc[0]))
for f in sorted(glob.glob('Data/edgar/tmobile_filings/DEF_14A/*.gz')):
    s = re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?s)<[^>]+>', ' ', gzip.decompress(Path(f).read_bytes()).decode('utf-8', 'replace'))))
    acc = Path(f).name.split('_')[0]
    inv = pd.read_csv(OUT / 'g34_filing_inventory.csv', dtype=str)
    fd = inv.loc[inv['accession'] == acc, 'filing_date']
    fd = fd.iloc[0] if len(fd) else ''
    for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z(])', s):
        if re.search(r'(?i)cyberattack|cyber attack', sent) and re.search(r'(?i)free cash flow|STIP|incentive|Plan\b|payout', sent):
            TL.append(dict(date=fd, type='proxy CD&A: pay metric adjusted for the August 2021 cyberattack',
                           description=sent[:420], source=acc))
ch = pd.read_csv(OUT / 'g4_charges_settlements.csv', dtype=str).fillna('')
for _, r in ch[ch['cyber_related'].str.lower().isin(['true', '1'])].iterrows():
    TL.append(dict(date=r['first_filing_date'], type=f"10-K/10-Q: charge/settlement/recovery ({r['first_form']})",
                   description=f"amounts {r['amounts']}: {r['sentence'][:300]}", source=r['first_accession']))
ic = pd.read_csv(OUT / 'g4_item1c.csv', dtype=str).fillna('')
for (fd, acc), g in ic.groupby(['filing_date', 'accession']):
    role = g[g['kind'].str.contains('role', case=False)]
    TL.append(dict(date=fd, type='10-K Item 1C: named security role and oversight',
                   description=(role['text'].iloc[0] if len(role) else g['text'].iloc[0])[:420], source=acc))
T = pd.DataFrame(TL)
T['date'] = pd.to_datetime(T['date'], errors='coerce')
T = T.dropna(subset=['date']).sort_values(['date', 'type']).reset_index(drop=True)
T['date'] = T['date'].dt.date.astype(str)
T.to_csv(OUT / 'tmobile_timeline.csv', index=False)
log(f'{len(T)} dated rows; by type:\n' + T['type'].value_counts().to_string())
(OUT / '203_case.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
