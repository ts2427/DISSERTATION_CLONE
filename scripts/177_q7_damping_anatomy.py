"""
QUERY 7 ADDENDUM — descriptive anatomy of the control-side damping
===================================================================
Bounded exception per Tim (8/31): a purely DESCRIPTIVE breakdown of which
control firms drive the announcement-window volatility damping (-0.125
mean elevation) — by year bucket, broad industry, and breach-size decile
bucket. No hypothesis tests, no p-values, one table. Characterizes a
finding already reported (scripts/175-176); opens no new front.
Output: outputs/tables/essay2_v2/t53_damping_anatomy.csv + report section
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


fin = pd.read_csv(OUTDIR / 't42_final_sample_with_repairs.csv', low_memory=False)
br = fin.dropna(subset=['abn_ann', 'abn_pre']).copy()
br['elev'] = br['abn_ann'] - br['abn_pre']
c = br[br['fcc_form499'] == 0].copy()
t = br[br['fcc_form499'] == 1]
log('=' * 90)
log('CONTROL-SIDE DAMPING — descriptive anatomy (no tests, no p-values)')
log('=' * 90)
log(f'\nReference: control mean elevation {c["elev"].mean():+.3f} '
    f'(n={len(c)}), treated {t["elev"].mean():+.3f} (n={len(t)}).')

rows = []


def cell(dim, lab, s):
    rows.append(dict(dimension=dim, cell=lab, n=len(s),
                     mean_elev=round(s.mean(), 3), median=round(s.median(), 3),
                     share_negative=round((s < 0).mean(), 2)))


c['year'] = pd.to_datetime(c['reported_date']).dt.year
for lo, hi in [(2006, 2010), (2011, 2015), (2016, 2019), (2020, 2024)]:
    cell('year', f'{lo}-{hi}', c.loc[c['year'].between(lo, hi), 'elev'])

IND = [('finance/insurance (SIC 60-67)', (60, 67)),
       ('retail (52-59)', (52, 59)), ('manufacturing (20-39)', (20, 39)),
       ('services/tech (70-79)', (70, 79)), ('health (80)', (80, 80)),
       ('transport/utilities/comm (40-49)', (40, 49))]
c['sic2n'] = pd.to_numeric(c['sic2'], errors='coerce')
assigned = pd.Series(False, index=c.index)
for lab, (lo, hi) in IND:
    m = c['sic2n'].between(lo, hi)
    assigned |= m
    cell('industry', lab, c.loc[m, 'elev'])
cell('industry', 'other/unclassified', c.loc[~assigned, 'elev'])

c['recs'] = pd.to_numeric(c['total_affected_max'], errors='coerce')
c['size_bucket'] = pd.qcut(c['recs'].rank(method='first'), 5,
                           labels=['d1-2 (smallest)', 'd3-4', 'd5-6',
                                   'd7-8', 'd9-10 (largest)'])
for lab in c['size_bucket'].cat.categories:
    cell('breach-size quintile', lab, c.loc[c['size_bucket'] == lab, 'elev'])

T = pd.DataFrame(rows)
log('\n' + T.to_string(index=False))
T.to_csv(OUTDIR / 't53_damping_anatomy.csv', index=False)
spread = T.groupby('dimension')['mean_elev'].agg(lambda s: s.max() - s.min())
log('\nCHARACTERIZATION (descriptive only): within-dimension spreads of the '
    'cell means — ' + '; '.join(f'{k}: {v:.2f}' for k, v in spread.items())
    + '. ' + ('The damping is DIFFUSE — no single sector, period, or size '
              'class carries it.' if (T['mean_elev'] < 0).mean() > 0.7 else
              'See the table for where the damping concentrates.'))
Path('outputs/ESSAY2_QUERY7_REPORT.md').write_text(
    Path('outputs/ESSAY2_QUERY7_REPORT.md').read_text(encoding='utf-8')
    + '\n\n' + '\n'.join(L) + '\n', encoding='utf-8')
print('Saved: t53 + appended to ESSAY2_QUERY7_REPORT.md')
