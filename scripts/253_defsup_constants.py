"""
DEFENSE SUPPLEMENT — CONSTANTS BLOCK + ASSERTION BASELINE (scripts 249-252)
==========================================================================
Collects the headline numbers of the four defense-supplement outputs into
outputs/defense_supplement/constants_defense_supplement.json, with the same
assert-against-baseline pattern as scripts/202 and scripts/227: if the file
exists, every key computed now must equal the committed value exactly, or the
run fails; if it is absent, it is written once. So the supplement verdicts are
reproduced on every run, not re-derived.

Inputs (all written earlier in the same run):
  e2_delay_ladder.csv            scripts/249 (Essay 2, N=333)
  e3_randomization_inference.csv scripts/250 (Essay 3, N=405)
  e1_notification_anchored.csv   scripts/251 (Essay 1, N=340)
  deck_exhibits.csv              scripts/252 (arithmetic on committed outputs)
  e1_cluster_ladder.csv          scripts/255 (Essay 1, N=340; added 2026-10-04)
"""

import json
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_supplement')
C = {}


def put(key, v, nd=4):
    C[key] = round(float(v), nd) if isinstance(v, float) else (int(v) if hasattr(v, 'item') else v)


# ---- Essay 2: disclosure-delay ladder (scripts/249) ----
e2 = pd.read_csv(OUT / 'e2_delay_ladder.csv')
assert set(e2['N']) == {333} and set(e2['n_treated_events']) == {104}, 'E2 sample'
assert set(e2['G']) == {82} and set(e2['G1']) == {12}, 'E2 clusters'
put('E2_N', 333); put('E2_treated_events', 104); put('E2_G', 82); put('E2_G1', 12)
OUTC = {'delay (raw days)': 'raw', 'delay (winsorized p99)': 'wins', 'log(1+delay)': 'log'}
RUNG = {'HC3': 'hc3', 'CV1 parent CIK': 'cv1', 'CV3 jackknife': 'cv3',
        'WCR restricted Rademacher': 'wcr', 'WCU unrestricted Rademacher': 'wcu',
        'WCR Webb six-point': 'webb'}
assert set(e2['outcome']) == set(OUTC) and set(e2['rung']) == set(RUNG), 'E2 rows'
for _, r in e2.iterrows():
    o, g = OUTC[r['outcome']], RUNG[r['rung']]
    put(f'E2_delay_{o}_coef', float(r['coef']))
    put(f'E2_delay_{o}_p_{g}', float(r['p']))
    if g in ('cv3', 'wcr'):
        put(f'E2_delay_{o}_ci_{g}_lo', float(r['ci_lo']))
        put(f'E2_delay_{o}_ci_{g}_hi', float(r['ci_hi']))
    put(f'E2_delay_{o}_mde80_cv3', float(r['mde80_cv3']))

# ---- Essay 3: randomization inference (scripts/250) ----
e3 = pd.read_csv(OUT / 'e3_randomization_inference.csv')
assert set(e3['N']) == {405} and set(e3['G']) == {119} and set(e3['G1']) == {13}, 'E3 sample'
assert set(e3['treated_events_obs']) == {109}, 'E3 treated events'
put('E3_N', 405); put('E3_treated_events', 109); put('E3_G', 119); put('E3_G1', 13)
for _, r in e3.iterrows():
    w = 'placebo' if 'placebo' in str(r['outcome']) else f"{int(r['window'])}d"
    v = 'all' if str(r['variant']).startswith('C1') else 'sizematched'
    put(f'E3_RI_{w}_{v}_p_coef', float(r['ri_p_coef']))
    put(f'E3_RI_{w}_{v}_p_cv3t', float(r['ri_p_t']))
    put(f'E3_RI_{w}_{v}_eligible_parents', int(r['n_eligible_parents']))
    put(f'E3_RI_{w}_{v}_B', int(r['B']))

# ---- Essay 1: notification-anchored CARs (scripts/251) ----
e1 = pd.read_csv(OUT / 'e1_notification_anchored.csv')
d2 = e1[(e1['section'] == 'D2') & e1['anchor'].astype(str).str.startswith('notification')]
assert len(d2) == 12, 'E1 notification-anchored D2 rows: %d, expected 12' % len(d2)
WIN = {'(0,+1)': '0_1', '(0,+5)': '0_5', '(0,+30)': '0_30'}
for _, r in d2.iterrows():
    k = f"E1_notif_{WIN[r['window']]}_{r['hypothesis'].split('_')[0]}"
    put(k + '_coef', float(r['coef']))
    put(k + '_p_hc3', float(r['p_hc3']))
    put(k + '_p_cv1', float(r['p_cv1_parentcik']))
    put(k + '_tost_p', float(r['tost_p_2_10']))
    put(f"E1_notif_{WIN[r['window']]}_N", int(r['N']))
    put(f"E1_notif_{WIN[r['window']]}_treated_events", int(r['n_treated']))
C['E1_notif_any_p_lt_05'] = bool(((d2['p_hc3'] < .05) | (d2['p_cv1_parentcik'] < .05)).any())

# ---- Essay 1: cluster ladder (scripts/255, added 2026-10-04) ----
el = pd.read_csv(OUT / 'e1_cluster_ladder.csv')
assert set(el['N']) == {340} and set(el['G']) == {83} and set(el['G1_treated_parent_ciks']) == {12}, 'E1 ladder sample'
RUNG1 = {'CV1 parent CIK, t(G-1)': 'cv1', 'CV3 jackknife, t(G-1)': 'cv3', 'WCR restricted Rademacher': 'wcr'}
for _, r in el[el['rung'].isin(RUNG1)].iterrows():
    kk = f"E1_ladder_{r['hypothesis']}_{RUNG1[r['rung']]}"
    put(kk + '_p', float(r['p']))
    if RUNG1[r['rung']] == 'cv3':
        put(kk + '_se', float(r['se']))
        put(kk + '_ci95_lo', float(r['ci95_lo'])); put(kk + '_ci95_hi', float(r['ci95_hi']))
        put(kk + '_mde80', float(r['mde80'])); put(kk + '_tost_p', float(r['tost_p']))
        C[kk + '_status'] = str(r['status'])
C['E1_ladder_any_status_change_under_cv3'] = bool(
    (el.loc[el['rung'] == 'CV3 jackknife, t(G-1)', 'status'].values !=
     el.loc[el['rung'].str.startswith('HC3'), 'status'].values).any())

# ---- deck exhibits (scripts/252): row count + every value, hashed by key ----
dx = pd.read_csv(OUT / 'deck_exhibits.csv')
put('DECK_rows', len(dx))
for ex, g in dx.groupby('exhibit'):
    put(f'DECK_{ex}_rows', len(g))
C = {k: (v.item() if hasattr(v, 'item') else v) for k, v in C.items()}

cp_ = OUT / 'constants_defense_supplement.json'
if cp_.exists():
    old = json.loads(cp_.read_text())
    mism = {k: (old.get(k), v) for k, v in C.items() if old.get(k) != v}
    gone = sorted(set(old) - set(C))
    assert not mism and not gone, \
        f'ASSERTION FAILURE vs defense-supplement baseline: {list(mism.items())[:5]} missing {gone[:5]}'
    print(f'Assertion check vs {cp_}: PASS ({len(C)} keys)')
else:
    cp_.write_text(json.dumps(C, indent=1))
    print(f'Baseline {cp_} WRITTEN ({len(C)} keys; later runs assert against it)')
