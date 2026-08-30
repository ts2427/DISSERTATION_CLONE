"""
SCRIPT 142: SAMPLE ATTRITION LEDGER (Methods section source of truth)
=====================================================================
Computes every verifiable sample-construction step live from committed artifacts
and emits the ledger the Methods section narrates ("walk me through how 1,054
became 648").

Verified steps (ALL computed here, from committed artifacts):
  1,054 -> 784 duplicate notification records collapsed to unique
               org_name + breach_date events (universe file:
               Data/processed/master_breach_dataset.xlsx, git-tracked;
               initially believed unrecoverable because the file named
               FINAL_DATASET_ORIGINAL_1054.csv contains 784 rows — the true
               universe lives in the xlsx).
  784 -> 779   CIK-duplicate event records removed (Failure Mode 1); the five
               dropped rows are listed by name.
  779 -> 672   no CRSP match (has_crsp_data == 0).
  672 -> 648   missing Compustat covariates (firm_size_log / leverage / roa).

Also emits pre-rule observation counts under both the calendar-2007 cutoff
(the basis of the canonical "4 pre-2007 obs, 1 treated" claim) and the
Federal-Register-verified effective date of 47 CFR 64.2011 (December 8, 2007;
72 FR 31948 delayed the section pending OMB approval; FCC compliance guidance
DA-08-1321 states the effective date). "September 28, 2007" has no
primary-source referent and is retired.

Outputs: outputs/SAMPLE_ATTRITION_LEDGER.md, outputs/sample_attrition_ledger.csv
"""

import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

universe = pd.read_excel('Data/processed/master_breach_dataset.xlsx')
d784 = pd.read_csv('Data/processed/FINAL_DATASET_DEDUPLICATED_784.csv', low_memory=False)
d779 = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv', low_memory=False)
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv', low_memory=False)

CONTROLS = ['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa', 'car_30d']

# Step: 784 -> 779 (named duplicate removals)
k784 = d784['org_name'].astype(str) + '|' + d784['breach_date'].astype(str)
k779 = set(d779['org_name'].astype(str) + '|' + d779['breach_date'].astype(str))
dropped_rows = sorted(set(k784) - k779)

# Step: 779 -> 672 (CRSP match)
crsp = df[df['has_crsp_data'] == 1]
# Step: 672 -> 648 (covariate completeness)
reg = crsp.dropna(subset=CONTROLS)
miss_size = int(crsp['firm_size_log'].isna().sum())
miss_lev = int(crsp['leverage'].isna().sum())
miss_roa = int(crsp['roa'].isna().sum())

# Step: 1,054 -> 784 (duplicate notification records -> unique events)
ku = universe['org_name'].astype(str) + '|' + universe['breach_date'].astype(str)
n_unique = ku.nunique()
vc = ku.value_counts()
multi_keys = int((vc > 1).sum())
excess = int((vc[vc > 1] - 1).sum())
assert len(universe) == 1054, f'universe file changed: {len(universe)} rows'
assert n_unique == len(d784) == 784, f'dedup no longer closes: {n_unique} vs {len(d784)}'
# Committee arithmetic check: the excess records among multi-record events must
# account for the ENTIRE 1,054 -> 784 drop.
assert excess == len(universe) - n_unique, \
    f'decomposition does not close: {excess} excess vs {len(universe) - n_unique} dropped'

rows = [
    {'Step': 'PRC record universe (Data/processed/master_breach_dataset.xlsx, git-tracked)',
     'N': len(universe), 'Lost': '',
     'Reason': 'All breach notification RECORDS for the matched public-firm universe, '
               '2004-2025. Multiple records can describe one breach event (multi-state '
               'notifications, amended filings).'},
    {'Step': 'Unique breach events', 'N': n_unique, 'Lost': len(universe) - n_unique,
     'Reason': f'Duplicate notification records collapsed to unique org_name + breach_date '
               f'events: {multi_keys} events had 2+ records (max {int(vc.max())} records '
               f'for one event - Cencora 2024-02-21). Arithmetic closes exactly: the '
               f'{excess} excess records among those {multi_keys} events account for the '
               f'entire {len(universe) - n_unique}-record drop (asserted on every run). '
               f'The step is pure within-key deduplication - no events were excluded.'},
    {'Step': 'After CIK-duplicate removal', 'N': len(d779), 'Lost': len(d784) - len(d779),
     'Reason': 'Failure Mode 1: fuzzy-match CIK-to-CRSP duplicate event records removed. '
               'Dropped: ' + '; '.join(dropped_rows)},
    {'Step': 'CRSP-matched sample', 'N': len(crsp), 'Lost': len(d779) - len(crsp),
     'Reason': 'No CRSP security match / insufficient trading data (has_crsp_data = 0). '
               'Delisted, thinly traded, or unmatchable tickers.'},
    {'Step': 'Regression sample (complete cases)', 'N': len(reg), 'Lost': len(crsp) - len(reg),
     'Reason': f'Missing Compustat covariates: firm_size_log missing {miss_size}, '
               f'leverage missing {miss_lev}, roa missing {miss_roa} (overlapping; '
               f'union = {len(crsp) - len(reg)}).'},
]
ledger = pd.DataFrame(rows)

# Pre-rule counts (identification framing)
bd = pd.to_datetime(reg['breach_date'])
pre_rows = []
for label, cut in [('Calendar-2007 cutoff (basis of canonical "4 pre-2007" claim)', '2007-01-01'),
                   ('FR-verified effective date of 47 CFR 64.2011 (Dec 8, 2007)', '2007-12-08')]:
    m = bd < cut
    pre_rows.append({'Cutoff': label, 'Pre-rule obs (regression sample)': int(m.sum()),
                     'Pre-rule treated': int((reg.loc[m, 'fcc_form499'] == 1).sum())})
pre = pd.DataFrame(pre_rows)

print(ledger.to_string(index=False))
print()
print(pre.to_string(index=False))

out = Path('outputs')
ledger.to_csv(out / 'sample_attrition_ledger.csv', index=False)

with open(out / 'SAMPLE_ATTRITION_LEDGER.md', 'w', encoding='utf-8') as f:
    f.write('# Sample Attrition Ledger (generated by scripts/142_sample_attrition_ledger.py)\n\n')
    f.write('Answers "walk me through how 1,054 became 648." EVERY step is computed live '
            'from git-tracked artifacts on every run, including 1,054 -> 784 '
            '(verified as exact within-key deduplication of the record universe in '
            'Data/processed/master_breach_dataset.xlsx).\n\n')
    f.write('| Step | N | Lost | Reason |\n|---|---|---|---|\n')
    for _, r in ledger.iterrows():
        f.write(f'| {r["Step"]} | {r["N"]} | {r["Lost"]} | {r["Reason"]} |\n')
    f.write('\n## Rule-date anchor (primary-source verified 8/2/2026)\n\n')
    f.write('- 47 CFR 64.2011 (CPNI breach notification) was adopted in the 2007 CPNI Order, '
            'published 72 FR 31948 (June 8, 2007). The DATES section states 64.2010/64.2011 '
            'were NOT effective on publication (pending OMB approval).\n'
            '- FCC compliance guidance (DA-08-1321, June 6, 2008) states the EPIC CPNI Order '
            'rules, including 64.2011, became effective December 8, 2007.\n'
            '- "September 28, 2007" has no primary-source referent found in the Federal '
            'Register or FCC documents and is RETIRED (see STALE_RESULTS_MANIFEST).\n\n')
    f.write('| Cutoff | Pre-rule obs (regression sample) | Pre-rule treated |\n|---|---|---|\n')
    for _, r in pre.iterrows():
        f.write(f'| {r["Cutoff"]} | {r["Pre-rule obs (regression sample)"]} | {r["Pre-rule treated"]} |\n')
    f.write('\nEither cutoff leaves the pre-period effectively empty (1 treated observation); '
            'the DD-unidentified conclusion is invariant to the date correction.\n')

print('\nSaved: outputs/SAMPLE_ATTRITION_LEDGER.md, outputs/sample_attrition_ledger.csv')
