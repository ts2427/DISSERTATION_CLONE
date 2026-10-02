"""
SHARED LOADER — the v3 CRSP daily panel (main file + top-ups), de-duplicated
===========================================================================
Added 2026-10-02 (defense supplement, Tim's ruling: "fix it, with a verdict gate").

THE DEFECT THIS CLOSES. Two top-up files repeat permno-dates that the main file
already carries, with identical returns:
    Data/wrds/crsp_daily_topup.csv       92 rows, permno 60599 (CenturyLink), 2020-09-18..2021-01-29
    Data/wrds/crsp_daily_topup_dish.csv 313 rows, permno 81696 (DISH),       2022-10-03..2023-12-29
Every consumer concatenated the files and then took event windows BY ROW POSITION,
so a window that touched those dates spanned about half the trading days it should,
counting each one twice. Three treated events were affected (CenturyLink 2020-08-20,
DISH 2023-02-22, DISH 2023-05-17); the last one's committed car_30d was +27.94 against
-2.38 on distinct trading days.

THE RULE. Concatenate main first, then the top-ups. Drop duplicate (permno, date) rows
keeping the MAIN-file row, and assert (permno, date) is unique. If any duplicated pair
disagrees on any loaded value column, stop: this loader never chooses between two
different numbers. Raw data files are not touched.

Import (the leading digit rules out a plain import):
    import importlib.util
    _s = importlib.util.spec_from_file_location('crsp_daily', 'scripts/254_crsp_daily.py')
    crsp_daily = importlib.util.module_from_spec(_s); _s.loader.exec_module(crsp_daily)
    crsp = crsp_daily.load(['permno', 'date', 'ret'])
"""

from pathlib import Path
import pandas as pd

MAIN = Path('Data/wrds/crsp_daily_returns.csv')
TOPUPS = (Path('Data/wrds/crsp_daily_topup.csv'),       # scripts/159 (Sprint, CenturyLink)
          Path('Data/wrds/crsp_daily_topup_dish.csv'))  # scripts/179 (DISH)
KEY = ['permno', 'date']


def load(usecols, topups=TOPUPS, verbose=True):
    """Main CRSP daily file plus the top-ups that exist, unique on (permno, date).

    `usecols` must include permno and date. Columns a top-up does not carry (it has
    permno, date, ret, vol) are NaN on its rows - the same as the old pd.concat.
    The returned frame keeps the input column types; dates are NOT parsed here, so
    each caller's own date handling is unchanged.
    """
    usecols = list(usecols)
    assert set(KEY) <= set(usecols), 'usecols must include permno and date'
    frames = [pd.read_csv(MAIN, usecols=usecols, low_memory=False).assign(_src=0)]
    for i, tp in enumerate(topups, start=1):
        tp = Path(tp)
        if not tp.exists():
            continue
        have = pd.read_csv(tp, nrows=0).columns
        cols = [c for c in usecols if c in have]
        frames.append(pd.read_csv(tp, usecols=cols, low_memory=False).assign(_src=i))
    d = pd.concat(frames, ignore_index=True)
    # normalise the key for comparison only; the returned columns keep their types
    k = pd.DataFrame({'permno': pd.to_numeric(d['permno'], errors='coerce'),
                      'date': pd.to_datetime(d['date'], errors='coerce')})
    dup_all = k.duplicated(keep=False)
    n_drop = int(k.duplicated(keep='first').sum())
    if dup_all.any():
        # a duplicate inside ONE file is not something a top-up explains - stop
        within = d.loc[dup_all].assign(_p=k['permno'], _d=k['date']) \
                  .groupby(['_p', '_d'])['_src'].agg(lambda s: s.nunique() < len(s))
        assert not within.any(), \
            f'{int(within.sum())} (permno, date) pairs repeat within a single file'
        vals = [c for c in usecols if c not in KEY]
        g = d.loc[dup_all, vals].assign(_p=k['permno'], _d=k['date'])
        for c in vals:
            x = pd.to_numeric(g[c], errors='coerce')
            # NaN on a top-up row means the top-up does not carry that column - not a conflict
            num_ok = x.notna()
            spread = x[num_ok].groupby([g.loc[num_ok, '_p'], g.loc[num_ok, '_d']]).agg(
                lambda s: s.max() - s.min())
            bad = spread[spread.abs() > 1e-12]
            assert bad.empty, (
                f'STOP: {len(bad)} duplicated (permno, date) pairs DISAGREE on {c} '
                f'between the main CRSP file and a top-up (first: {bad.index[0]}). '
                f'Not choosing one.')
    d = d.loc[~k.duplicated(keep='first')].sort_values('_src', kind='stable')
    d = d.drop(columns='_src').reset_index(drop=True)
    kk = pd.DataFrame({'permno': pd.to_numeric(d['permno'], errors='coerce'),
                       'date': pd.to_datetime(d['date'], errors='coerce')})
    assert not kk.duplicated().any(), '(permno, date) is not unique after de-duplication'
    if verbose:
        print(f'  [crsp_daily] {len(d):,} rows; dropped {n_drop} duplicate (permno, date) '
              f'rows from the top-ups (main-file row kept; returns identical)')
    return d
