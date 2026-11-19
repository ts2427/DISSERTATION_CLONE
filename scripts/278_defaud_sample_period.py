"""
DEFENSE AUDIT — FINAL ITEM 3: SAMPLE PERIOD BY ESSAY (script 278)
=================================================================
Read-only on results. For each essay's analysis sample, identified from a committed event-level file and
asserted against its committed N and treated count, reports:
  * first and last breach date and notification (reported) date, overall and by treatment group;
  * events per calendar year by treatment group, on both the breach-date year and the notification-date year;
  * events with breach date, and with notification date, before 2007-12-08 (FCC CPNI rule effective date).
Cross-checks the pre-rule counts against the committed figures and records which date each one uses.

Samples
  Essay 1  Data/processed/rebuild/CANONICAL_V3.csv, has_crsp_data == 1, dropna(car_30d + CONTROLS)
           (the scripts/158 recipe, lines 57-60)                       -> N 340, 106 treated
  Essay 2  outputs/essay2_v5/v5_event_panel.csv (all rows, prim_dv present) -> N 333, 104 treated
  Essay 3  outputs/essay3_v4/e_analysis_sample.csv, in_analysis_sample == 1 -> N 405, 109 treated

Writes ONLY outputs/defense_audit/final/item3_sample_period.csv and item3_sample_period.log.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_audit/final')
RULE = pd.Timestamp('2007-12-08')
TREAT = 'fcc_form499'
L, ROWS = [], []


def log(m=''):
    print(m)
    L.append(str(m))


def add(essay, group, measure, value, source):
    ROWS.append(dict(essay=essay, group=group, measure=measure, value=value, source=source))


# ---------------------------------------------------------------- samples
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
CONTROLS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
e1 = ev[ev['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS).copy()
c3 = json.load(open('outputs/rebuild/constants_v3.json', encoding='utf-8'))


def find(d, k):
    if isinstance(d, dict):
        if k in d:
            return d[k]
        for v in d.values():
            r = find(v, k)
            if r is not None:
                return r
    return None


assert len(e1) == 340 == find(c3, 'N_regression'), (len(e1), find(c3, 'N_regression'))
assert int(e1[TREAT].sum()) == 106 == find(c3, 'treated_regression')

e2 = pd.read_csv('outputs/essay2_v5/v5_event_panel.csv', low_memory=False)
assert e2['prim_dv'].notna().all()
c2 = json.load(open('outputs/essay2_v5/constants_essay2.json', encoding='utf-8'))['values']
assert len(e2) == 333 == c2['primary_N'] and int(e2[TREAT].sum()) == 104 == c2['primary_treated']

e3a = pd.read_csv('outputs/essay3_v4/e_analysis_sample.csv', low_memory=False)
e3 = e3a[e3a['in_analysis_sample'] == 1].copy()
led = pd.read_csv('outputs/essay3_v4/e_ledger.csv')
lrow = led[led['note'].astype(str).str.contains('ANALYSIS SAMPLE')].iloc[0]
assert len(e3) == 405 == int(lrow.N) and int(e3[TREAT].sum()) == 109 == int(lrow.treated)

SAMPLES = [
    ('Essay 1', e1, 'Data/processed/rebuild/CANONICAL_V3.csv (has_crsp_data==1, dropna car_30d + 7 regressors; scripts/158 L57-60)'),
    ('Essay 2 v5', e2, 'outputs/essay2_v5/v5_event_panel.csv (all 333 rows)'),
    ('Essay 3 v4', e3, 'outputs/essay3_v4/e_analysis_sample.csv (in_analysis_sample==1)'),
]

log('=' * 90)
log('SCRIPT 278 - sample period by essay (defense audit, read-only)')
log('=' * 90)
for name, d, src in SAMPLES:
    d['bdt'] = pd.to_datetime(d['breach_date'])
    d['rdt'] = pd.to_datetime(d['reported_date'])
    d['grp'] = d[TREAT].map({1: 'treated', 0: 'control'})
    assert d[['bdt', 'rdt']].notna().all().all(), f'{name}: missing dates'
    log(f'\n## {name}: N = {len(d)} events ({int(d[TREAT].sum())} treated / {int((d[TREAT] == 0).sum())} control); {src}')
    add(name, 'all', 'N events', len(d), src)
    for g, s in [('all', d), ('treated', d[d.grp == 'treated']), ('control', d[d.grp == 'control'])]:
        if g != 'all':
            add(name, g, 'N events', len(s), src)
        for col, lab in [('bdt', 'breach date'), ('rdt', 'notification date')]:
            lo, hi = s[col].min().date().isoformat(), s[col].max().date().isoformat()
            add(name, g, f'first {lab}', lo, src)
            add(name, g, f'last {lab}', hi, src)
            log(f'   {g:8s} {lab:18s} {lo} to {hi}')
        nb = int((s['bdt'] < RULE).sum())
        nr = int((s['rdt'] < RULE).sum())
        add(name, g, 'events with breach date before 2007-12-08', nb, src)
        add(name, g, 'events with notification date before 2007-12-08', nr, src)
        log(f'   {g:8s} before 2007-12-08: breach date {nb}, notification date {nr}')
    for col, basis in [('bdt', 'breach-date year'), ('rdt', 'notification-date year')]:
        tab = pd.crosstab(d[col].dt.year, d['grp']).reindex(columns=['treated', 'control'], fill_value=0)
        assert tab.values.sum() == len(d)
        log(f'   events per year ({basis}):')
        log('   ' + tab.assign(total=tab.sum(1)).to_string().replace('\n', '\n   '))
        for y, r in tab.iterrows():
            for g in ['treated', 'control']:
                add(name, g, f'events in {y} ({basis})', int(r[g]), src)

# ---------------------------------------------------------------- cross-checks against committed figures
log('\n## Cross-checks: pre-rule counts vs committed figures')
chk = []


def check(name, d, basis, committed, cfile, ckey, group='all'):
    s = d if group == 'all' else d[d.grp == group]
    col = 'bdt' if basis == 'breach' else 'rdt'
    mine = int((s[col] < RULE).sum())
    ok = mine == int(committed)
    chk.append(ok)
    log(f'   {name} {group} pre-rule ({basis} date): computed {mine}, committed {committed} '
        f'[{cfile} :: {ckey}] -> {"MATCH" if ok else "MISMATCH"}')
    add(name, group, f'cross-check pre-rule ({basis} date) vs {cfile} :: {ckey}',
        f'{mine} vs {committed} ({"MATCH" if ok else "MISMATCH"})', cfile)


cf2 = 'outputs/essay2_v5/constants_essay2.json'
check('Essay 2 v5', e2, 'notification', c2['prerule_events'], cf2, 'values.prerule_events (scripts/269 L803: reported_date)')
check('Essay 2 v5', e2, 'notification', c2['prerule_treated'], cf2, 'values.prerule_treated (reported_date)', 'treated')
check('Essay 2 v5', e2, 'breach', c2['prerule_breach_anchor'], cf2, 'values.prerule_breach_anchor (breach_date)')
check('Essay 3 v4', e3, 'breach', int(lrow.pre_rule_treated), 'outputs/essay3_v4/e_ledger.csv',
      'ANALYSIS SAMPLE row, pre_rule_treated (scripts/224 L366: breach_date)', 'treated')
check('Essay 3 v4', e3, 'breach', int(lrow.pre_rule_control), 'outputs/essay3_v4/e_ledger.csv',
      'ANALYSIS SAMPLE row, pre_rule_control (breach_date)', 'control')
el = 'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md'
txt = Path(el).read_text(encoding='utf-8')
assert '| breach_date | 6 | 0 |' in txt and '| reported_date | 6 | 0 |' in txt
check('Essay 1', e1, 'breach', 6, el, '"Cross-essay pre-rule check (Essay 1 v3 regression sample)", breach_date row')
check('Essay 1', e1, 'breach', 0, el, 'same table, breach_date pre-rule treated', 'treated')
check('Essay 1', e1, 'notification', 6, el, 'same table, reported_date row')
check('Essay 1', e1, 'notification', 0, el, 'same table, reported_date pre-rule treated', 'treated')
log(f'   cross-checks: {sum(chk)} of {len(chk)} MATCH')

OUT.mkdir(parents=True, exist_ok=True)
pd.DataFrame(ROWS).to_csv(OUT / 'item3_sample_period.csv', index=False, lineterminator='\n', encoding='utf-8')
(OUT / 'item3_sample_period.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
log(f'\nwrote {OUT / "item3_sample_period.csv"} ({len(ROWS)} rows)')
