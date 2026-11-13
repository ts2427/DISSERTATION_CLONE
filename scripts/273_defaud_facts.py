"""DEFENSE AUDIT — descriptive facts for likely committee questions (Part C).

Counts and arithmetic on frozen samples and committed outputs only. No new
hypothesis test and no new estimate of any hypothesis variable. Every sample is
asserted against its committed ledger before anything is computed:
  Essay 1  N = 340, 106 treated events (outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md;
           constants_v3.json N_regression), recipe scripts/247:97-104
  Essay 2  N = 333, 104 treated events, G = 82 (outputs/tables/essay2_v2/t1_final_sample.csv)
  Essay 2 announcement sample  N = 331 (t42: abn_ann and abn_pre present)
  Essay 3  N = 405, 109 treated events, G = 119, 13 treated parent CIKs
           (outputs/essay3_v4/e_analysis_sample.csv, in_analysis_sample == 1)
C5 refits the COMMITTED Essay 3 LPM (scripts/227: same columns, same sample) only to
obtain fitted values; it first asserts the treatment coefficient equals the committed
constant (constants_essay3_v4.json) to 4 dp, so no estimate is new.
Writes outputs/defense_audit/defense_facts.csv (key, value, source), c1_treated_scope.csv,
c6_treated_parents.csv, c8_states.csv, DEFENSE_FACTS.md.
"""
import importlib.util as _ilu
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_audit')
OUT.mkdir(parents=True, exist_ok=True)
TREAT = 'fcc_form499'
F = []          # (section, key, value, source)


def put(sec, key, val, src):
    F.append(dict(section=sec, key=key, value=val, source=src))


_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L5 = _ilu.module_from_spec(_s)
_s.loader.exec_module(L5)

# ------------------------------------------------------------------ samples
V3 = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
V4 = pd.read_csv('Data/processed/rebuild_v4/CANONICAL_V4.csv', low_memory=False)
E1_CTRL = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
           'firm_size_log', 'leverage', 'roa']                       # scripts/158:54-55
e1 = V3[V3['has_crsp_data'] == 1].dropna(subset=E1_CTRL + ['car_30d']).reset_index(drop=True)
c3 = json.loads(Path('outputs/rebuild/constants_v3.json').read_text(encoding='utf-8'))
assert len(e1) == 340 == c3['N_regression'] and int(e1[TREAT].sum()) == 106, 'Essay 1 sample'
led1 = Path('outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md').read_text(encoding='utf-8')
assert '| Essay 1 regression sample (N) | **340** |' in led1 and '| Treated events in it | **106** |' in led1
e2 = pd.read_csv('outputs/tables/essay2_v2/t1_final_sample.csv', low_memory=False)
assert len(e2) == 333 and int(e2[TREAT].sum()) == 104 and e2['final_cik'].nunique() == 82, 'Essay 2'
t42 = pd.read_csv('outputs/tables/essay2_v2/t42_final_sample_with_repairs.csv', low_memory=False)
e2a = t42.dropna(subset=['abn_ann', 'abn_pre'])
assert len(e2a) == 331, 'Essay 2 announcement sample'
e3 = pd.read_csv('outputs/essay3_v4/e_analysis_sample.csv', low_memory=False)
e3 = e3[e3['in_analysis_sample'] == 1].reset_index(drop=True)
assert len(e3) == 405 and int(e3[TREAT].sum()) == 109 and e3['final_cik'].nunique() == 119 \
    and e3.loc[e3[TREAT] == 1, 'final_cik'].nunique() == 13, 'Essay 3 sample'
print('Sample assertions PASS: E1 340/106; E2 333/104/G82; E2 announcement 331; E3 405/109/G119/13 parents')
KEY = ['final_cik', 'breach_date', 'org_name']
SAMPLES = {'E1': (e1, V3, 'Essay 1 (CANONICAL_V3 recipe 247:97-104)'),
           'E2': (e2, V3, 'Essay 2 (t1_final_sample.csv)'),
           'E3': (e3, V4, 'Essay 3 (e_analysis_sample.csv)')}

# records -> canonical events (CIK + breach date, plus Gate-2 chain component dates)
rec = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)


def components(canon):
    rows = []
    for _, r in canon.iterrows():
        dates = {str(r['breach_date'])[:10]}
        m = re.search(r'collapsed \[([^\]]+)\]', str(r['chain_note']))
        if m:
            dates |= {d.strip() for d in m.group(1).split(',')}
        for d_ in dates:
            rows.append(dict(final_cik=r['final_cik'], comp_date=d_, ev_breach=r['breach_date'],
                             ev_org=r['org_name']))
    return pd.DataFrame(rows)


def records_for(canon):
    comp = components(canon)
    r = rec.dropna(subset=['final_cik']).copy()
    r['final_cik'] = r['final_cik'].astype(float)
    r['comp_date'] = r['breach_date'].astype(str).str[:10]
    comp['final_cik'] = comp['final_cik'].astype(float)
    return r.merge(comp, on=['final_cik', 'comp_date'], how='inner')


# ------------------------------------------------------------------ C1 rule scope
CUST = r'call record|call detail|\bcdr\b|account|billing|customer|phone number|telephone number|subscriber|cpni|pin\b|wireless'
EMPL = r'employee|\bw-?2\b|payroll|human resources|\bhr\b|personnel|staff|workforce|benefit'
c1rows = []
for ess, (smp, canon, lab) in SAMPLES.items():
    tr = smp[smp[TREAT] == 1][KEY].merge(canon, on=KEY, how='left')
    assert len(tr) == int(smp[TREAT].sum())
    recs = records_for(tr)
    for _, r in tr.iterrows():
        rr = recs[(recs['final_cik'] == float(r['final_cik'])) & (recs['ev_breach'] == r['breach_date'])
                  & (recs['ev_org'] == r['org_name'])]
        text = ' '.join([str(r['information_affected']), str(r['incident_details'])]
                        + rr['information_affected'].astype(str).tolist()
                        + rr['incident_details'].astype(str).tolist()).lower()
        cu, em = bool(re.search(CUST, text)), bool(re.search(EMPL, text))
        flag = 'customer-terms only' if cu and not em else 'employee-terms only' if em and not cu \
            else 'both' if cu and em else 'neither'
        c1rows.append(dict(essay=ess, parent_cik=int(r['final_cik']), org_name=r['org_name'],
                           breach_date=r['breach_date'], reported_date=str(r['reported_date'])[:10],
                           breach_type=r['breach_type'], information_affected=r['information_affected'],
                           incident_details=r['incident_details'], n_component_records=len(rr),
                           keyword_flag_READING_AID_NOT_A_CLASSIFICATION=flag))
c1 = pd.DataFrame(c1rows)
c1.to_csv(OUT / 'c1_treated_scope.csv', index=False)
for ess in SAMPLES:
    vc = c1[c1['essay'] == ess]['keyword_flag_READING_AID_NOT_A_CLASSIFICATION'].value_counts()
    for k, v in vc.items():
        put('C1', f'{ess}_treated_events_flag_{k}', int(v), 'c1_treated_scope.csv (keyword reading aid; CUST/EMPL regex in scripts/273)')

# ------------------------------------------------------------------ C2 equivalence bound
na = pd.read_csv('outputs/defense_supplement/e1_notification_anchored.csv')
base = na[(na['section'] == 'D2') & (na['anchor'] == 'breach (committed baseline, reference)')
          & (na['window'] == '(0,+30)')]
assert len(base) == 4, 'expected the four committed baseline rows'
for _, r in base.iterrows():
    b = max(abs(r['ci90_lo']), abs(r['ci90_hi']))
    src = f'e1_notification_anchored.csv section D2 {r["variable"]} ci90_lo/ci90_hi'
    put('C2', f'E1_{r["hypothesis"]}_ci90', f'[{r["ci90_lo"]:.4f}, {r["ci90_hi"]:.4f}]', src)
    put('C2', f'E1_{r["hypothesis"]}_smallest_rejectable_bound', round(b, 4), src + ' -> max(|lo|,|hi|)')
sd_car = float(e1['car_30d'].std(ddof=1))
put('C2', 'E1_car_30d_sd', round(sd_car, 4), 'CANONICAL_V3 car_30d on the 340 (ddof 1)')
put('C2', 'E1_bound_2.10_share_of_sd', round(2.10 / sd_car, 4), '2.10 / E1_car_30d_sd')

# ------------------------------------------------------------------ C3 SEC Item 1.05 overlap
for ess, smp in [('E1', e1), ('E2', e2), ('E2ann', e2a), ('E3', e3)]:
    rd = pd.to_datetime(smp['reported_date'], errors='coerce')
    for cut, lab in [('2023-12-18', 'on_or_after_2023-12-18_effective'), ('2023-09-05', 'on_or_after_2023-09-05_adoption')]:
        m = rd >= cut
        put('C3', f'{ess}_{lab}_treated', int((m & (smp[TREAT] == 1)).sum()), f'{ess} sample reported_date')
        put('C3', f'{ess}_{lab}_control', int((m & (smp[TREAT] == 0)).sum()), f'{ess} sample reported_date')

# ------------------------------------------------------------------ C4 calendar clustering (E1)
cal = pd.to_datetime(pd.read_csv('Data/wrds/market_indices.csv', usecols=['date'])['date']).to_numpy()
pos = np.array([int(np.argmin(np.abs(cal - np.datetime64(pd.Timestamp(d))))) for d in e1['breach_date']])
cnt = pd.Series(pos).value_counts()
put('C4', 'E1_events_sharing_day0', int(cnt[cnt > 1].sum()),
    'day 0 = market trading day nearest breach_date (scripts/155:7 rule, market calendar)')
put('C4', 'E1_max_events_on_one_day0', int(cnt.max()), 'same')
pairs = int(sum((np.abs(pos[i] - pos[i + 1:]) <= 30).sum() for i in range(len(pos))))
put('C4', 'E1_event_pairs_overlapping_0_30_windows', pairs, '|day0_i - day0_j| <= 30 trading days')
put('C4', 'E1_event_pairs_total', len(pos) * (len(pos) - 1) // 2, 'n(n-1)/2')

# ------------------------------------------------------------------ C5 LPM fitted values (E3)
c4j = json.loads(Path('outputs/essay3_v4/constants_essay3_v4.json').read_text(encoding='utf-8'))
CTRL3 = ['prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa',
         'baseline_exec_rate_py_rd', 'prior12m_mktadj_ret_rd']          # scripts/227:80-84
for lab, y, key in [('30', 'exec_departure_30_rd', 'F1_30_coef'), ('90', 'exec_departure_90_rd', 'F1_90_coef'),
                    ('180', 'exec_departure_180_rd', 'F1_180_coef'), ('placebo', 'placebo_exec_departure_rd', 'F4_coef')]:
    d = e3.dropna(subset=[y, TREAT] + CTRL3)
    f = sm.OLS(d[y].astype(float), sm.add_constant(d[[TREAT] + CTRL3].astype(float))).fit()
    assert round(float(f.params[TREAT]), 4) == c4j[key], (lab, f.params[TREAT], c4j[key])
    fv = f.fittedvalues
    put('C5', f'E3_{lab}_fitted_min', round(float(fv.min()), 4), f'refit of scripts/227 spec; gate {key}')
    put('C5', f'E3_{lab}_fitted_max', round(float(fv.max()), 4), f'refit of scripts/227 spec; gate {key}')
    put('C5', f'E3_{lab}_fitted_outside_0_1', int(((fv < 0) | (fv > 1)).sum()), f'of N {len(d)}')

# ------------------------------------------------------------------ C6 treated clusters + G*
c6rows = []
for ess, smp in [('E1', e1), ('E2', e2), ('E3', e3)]:
    tr = smp[smp[TREAT] == 1]
    g = tr.groupby('final_cik').agg(events=('org_name', 'size'),
                                    name=('org_name', lambda s: s.value_counts().index[0])).sort_values('events', ascending=False)
    for cik, r in g.iterrows():
        c6rows.append(dict(essay=ess, parent_cik=int(cik), name=r['name'], treated_events=int(r['events'])))
    put('C6', f'{ess}_treated_parent_ciks', len(g), f'{ess} sample')
    put('C6', f'{ess}_largest_parent_share', round(g['events'].iloc[0] / g['events'].sum(), 4),
        f'{g["name"].iloc[0]} {g["events"].iloc[0]} of {g["events"].sum()} treated events')
pd.DataFrame(c6rows).to_csv(OUT / 'c6_treated_parents.csv', index=False)


def gstar(d, xs):
    d = d.dropna(subset=xs)
    X = sm.add_constant(d[xs].astype(float)).to_numpy()
    gi = np.unique(d['final_cik'], return_inverse=True)[1]
    return L5.cluster_diag(X, gi, gi.max() + 1, 1 + xs.index(TREAT))['G_star'], len(d)


gs1, n1 = gstar(e1, E1_CTRL)
put('C6', 'E1_G_star', round(gs1, 1), 'CSS on treatment partial leverage (scripts/263 cluster_diag = 165 D2), E1 baseline X')
xs2 = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT, 'health_breach', 'prior_events']
gs2, _ = gstar(e2, xs2)
put('C6', 'E2_G_star_defense_era', round(gs2, 1), 'same formula, defense-era XS4 (outputs/ESSAY2_QUERY4_PART_DE.md:20 = 24.2)')
v5c = json.loads(Path('outputs/essay2_v5/constants_essay2.json').read_text(encoding='utf-8'))['values']
put('C6', 'E2_G_star_v5', round(v5c['primary_G_star'], 1), 'outputs/essay2_v5/constants_essay2.json primary_G_star')
gs3, _ = gstar(e3, [TREAT] + CTRL3)
put('C6', 'E3_G_star', round(gs3, 1), f'same formula, E3 30d X; committed F1_30_G_star = {c4j.get("F1_30_G_star")}')

# ------------------------------------------------------------------ C7 base rates
for g_, m in [('treated', e1[TREAT] == 1), ('control', e1[TREAT] == 0)]:
    s = e1.loc[m, 'car_30d']
    put('C7', f'E1_car30_{g_}_mean', round(float(s.mean()), 4), 'CANONICAL_V3 car_30d, E1 sample')
    put('C7', f'E1_car30_{g_}_median', round(float(s.median()), 4), 'same')
    put('C7', f'E1_car30_{g_}_sd', round(float(s.std(ddof=1)), 4), 'same')
for g_, m in [('treated', e2[TREAT] == 1), ('control', e2[TREAT] == 0)]:
    s = e2.loc[m, 'disclosure_delay_days']
    for st, v in [('mean', s.mean()), ('median', s.median()), ('p25', s.quantile(.25)),
                  ('p75', s.quantile(.75)), ('max', s.max())]:
        put('C7', f'E2_delay_{g_}_{st}', round(float(v), 2), 't1 disclosure_delay_days (raw days)')
for w in ['30', '90', '180']:
    for g_, m, ck in [('treated', e3[TREAT] == 1, f'F1_{w}_treated_mean'), ('control', e3[TREAT] == 0, f'F1_{w}_control_mean')]:
        s = e3.loc[m, f'exec_departure_{w}_rd']
        assert round(float(s.mean()), 4) == c4j[ck], (ck, s.mean())
        put('C7', f'E3_departure_{w}d_{g_}', f'{int(s.sum())}/{len(s)} = {s.mean():.4f}', f'constants_essay3_v4.json {ck}')

# ------------------------------------------------------------------ C8 coverage (states)
STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
          'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
          'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
          'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
          'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
SRX = re.compile(r'\b(' + '|'.join(sorted(STATES, key=len, reverse=True)) + r')\b')


def reporting_state(text):
    """The state of the reporting agency: the first state name in the sentence that
    contains 'reported' (reading rule; the PRC export has no state field)."""
    for sent in re.split(r'(?<=\.)\s', str(text)):
        if 'report' in sent.lower():
            m = SRX.search(sent.replace('Washington, D.C.', '').replace('District of Columbia', ''))
            return m.group(1) if m else 'UNPARSED'
    return 'UNPARSED'


rec['state'] = rec['incident_details'].map(reporting_state)
put('C8', 'records_total', len(rec), 'stage2_signed.csv (= master_breach_dataset.xlsx, 1,054)')
put('C8', 'records_states_distinct', int(rec.loc[rec['state'] != 'UNPARSED', 'state'].nunique()),
    'reporting-agency state parsed from incident_details (scripts/273 reporting_state)')
put('C8', 'records_state_unparsed', int((rec['state'] == 'UNPARSED').sum()), 'same')
put('C8', 'records_massachusetts', int((rec['state'] == 'Massachusetts').sum()), 'same')
put('C8', 'records_mentioning_massachusetts_anywhere',
    int(rec['incident_details'].astype(str).str.contains('Massachusetts').sum()), 'substring count')
rm = records_for(V3)
ev_states = rm.groupby(['ev_org', 'ev_breach'])['state'].apply(set)
put('C8', 'canonical_events_matched_to_records', int(len(ev_states)), 'of 489 (CIK + breach date incl. Gate-2 components)')
srows = []
for st in sorted({s for ss in ev_states for s in ss}):
    n_ev = int(sum(st in ss for ss in ev_states))
    srows.append(dict(state=st, records=int((rec['state'] == st).sum()),
                      canonical_events_with_a_record=n_ev, share_of_489=round(n_ev / 489, 4)))
sdf = pd.DataFrame(srows).sort_values('canonical_events_with_a_record', ascending=False)
sdf.to_csv(OUT / 'c8_states.csv', index=False)
ma = sdf[sdf['state'] == 'Massachusetts'].iloc[0]
put('C8', 'massachusetts_canonical_events', int(ma['canonical_events_with_a_record']), 'c8_states.csv')
put('C8', 'massachusetts_share_of_489', float(ma['share_of_489']), 'c8_states.csv')

# ------------------------------------------------------------------ C9 existence
EX = [('leave-one-treated-parent-out, Essay 1', None,
       'NO: no committed output; scripts/255 computes the cluster jackknife internally (betas_del, lifted from 165) but writes only SEs/p (e1_cluster_ladder.csv)'),
      ('leave-one-parent-out, Essay 2 (defense era: 165 cluster-deleted range; v5 table)',
       'outputs/tables/essay2_v2/t25_cluster_diagnostics.csv; outputs/essay2_v5/v5_t14b_leave_one_parent_out.csv', None),
      ('market-model or factor-model CAR (Essay 1)', None,
       'NO: car_30d is market-adjusted (ret - vwretd, scripts/155:6); FF3 enters only as monthly factor CONTROLS in a CAR regression (scripts/158:319-333, appendix Table 13), not as a factor-model CAR'),
      ('logit or probit, Essay 3', 'outputs/essay3_v4/f1_logit_ame.csv', None),
      ('CV3 or WCR p for Essay 1 hypothesis variables', 'outputs/defense_supplement/e1_cluster_ladder.csv', None),
      ('power/MDE for the Essay 2 announcement test', None,
       'NO: scripts/175 and 180 emit no MDE; v5 v5_t09b_announcement_ladder.csv has no MDE column'),
      ('notification-anchored Essay 1 values', 'outputs/defense_supplement/e1_notification_anchored.csv', None)]
for lab, f, why in EX:
    if f:
        ok = all(Path(p.strip()).exists() for p in f.split(';'))
        put('C9', lab, 'yes' if ok else 'NO (file missing)', f)
    else:
        put('C9', lab, 'no', why)

df = pd.DataFrame(F)
df.to_csv(OUT / 'defense_facts.csv', index=False)
print(df.to_string(index=False))
print(f'\nSaved {len(df)} facts -> {OUT}/defense_facts.csv (+ c1, c6, c8 tables)')

# ------------------------------------------------------------------ DEFENSE_FACTS.md
md = ['# Defense facts (Part C)', '',
      'Generated by `scripts/273_defaud_facts.py`: counts and arithmetic on the frozen samples and committed '
      'outputs only. Samples asserted first: Essay 1 340 / 106 treated events; Essay 2 333 / 104 treated '
      'events / G 82; Essay 2 announcement 331; Essay 3 405 / 109 treated events / G 119 / 13 treated parent CIKs. '
      'Full values with sources: `defense_facts.csv`.', '',
      '**C1 is a reading aid, not a classification.** The keyword flag marks whether the PRC text contains '
      'customer-side terms (account, billing, customer, phone number, subscriber, CPNI, call records) and/or '
      'employee-side terms (employee, W-2, payroll, HR, personnel, staff, benefit). In the treated events the '
      'employee terms nearly always describe the actor ("an employee accessed customer accounts"), not employee '
      'data; every treated event in every essay carries at least one customer-side term. The verbatim fields are '
      'in `c1_treated_scope.csv` for hand review.', '']
for sec in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']:
    md += [f'## {sec}', '', '| key | value | source |', '|---|---|---|']
    for r in [x for x in F if x['section'] == sec]:
        md.append(f"| {r['key']} | {r['value']} | {str(r['source']).replace('|', '/')} |")
    md.append('')
md += ['Notes: C4 day 0 uses the market trading calendar (nearest trading day to the breach date, the scripts/155 '
       'rule); scripts/155 itself steps through each stock\'s own trading rows. C8 parses the reporting agency\'s '
       'state from the sentence of `incident_details` that contains "report" (the PRC export has no state field); '
       'records with no state name in that sentence are UNPARSED.']
(OUT / 'DEFENSE_FACTS.md').write_text('\n'.join(md), encoding='utf-8')
print('Saved DEFENSE_FACTS.md')
