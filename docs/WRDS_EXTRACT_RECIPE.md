# WRDS Extract Recipe (replication specification for licensed data)

The CRSP and Compustat extracts used by the Canonical V3 chain are licensed
under the University of South Alabama's WRDS subscription and are therefore
NOT redistributed in this repository. This recipe fully specifies the pulls so
that any researcher with equivalent WRDS access can regenerate them; script
`scripts/159_wrds_coverage_topup.py` automates the top-up portion (idempotent:
skips when the artifacts exist, pulls via pgpass when they do not).

## 1. Main CRSP daily extract — Data/wrds/crsp_daily_returns.csv (git-tracked)
- Source: CRSP Daily Stock File (crsp.dsf) joined to crsp.stocknames tickers.
- Variables: permno, date, ticker, ret, retx, prc, shrout, vol, cfacpr, cfacshr.
- Universe: securities matched to the breach sample's public firms (pre-rebuild
  ticker list); date range 2005-05-02 .. 2024-12-31 as committed.
- Vintage: committed to the repository July 2026 (see git history of the file).

## 2. Market indices — Data/wrds/market_indices.csv (git-tracked)
- Source: crsp.dsi (daily index file). Variables: date, vwretd, ewretd, sprtrn.

## 3. CRSP names history — Data/wrds/ticker_permno_mapping.csv (git-tracked)
- Source: crsp.stocknames. Variables: ticker, permno, comnam, namedt,
  nameenddt (renamed nameendt in-file).

## 4. Main Compustat extract — Data/wrds/compustat_annual.csv (git-tracked)
- Source: comp.funda, filters indfmt='INDL', datafmt='STD', popsrc='D',
  consol='C'. Variables: gvkey, datadate, conm, tic, fyear, at, revt, ni, csho,
  prcc_f, sale, lt, act, lct, che, cogs, xsga, ib, ceq, emp, sich.

## 5. Coverage top-up (NOT tracked; pre-specified amendment 8/4/2026)
Files: Data/wrds/crsp_daily_topup.csv, ticker_permno_topup.csv,
compustat_annual_topup.csv. Pulled 2026-08-04 by scripts/159:
- crsp.stocknames: ticker='S' & comnam like 'SPRINT%', or ticker='CTL' &
  comnam like 'CENTURYLINK%'/'CENTURYTEL%' → permnos 39087 (Sprint Nextel,
  2005-2013), 14040 (Sprint Corp, 2013-2020), 60599 (CenturyTel/CenturyLink,
  1999-2020).
- crsp.dsf: permno in (14040, 39087, 60599), date 2008-01-01 .. 2021-01-31;
  variables permno, date, ret, vol.
- comp.funda: **gvkey-exact only** — gvkey in ('010984','002884') [Sprint Corp;
  Lumen Technologies/CenturyLink], datadate 2007-01-01 .. 2020-12-31, same
  INDL/STD/D/C filters; variables at, lt, ni, sale, cogs, xsga; output keyed to
  matched tickers 'S'/'CTL'.

### Identifier warnings (learned the hard way; do not "simplify" this recipe)
- Compustat `tic` is CURRENT vintage: Sprint is now 'S.4' (ticker S reassigned
  to SentinelOne); ticker lookups fail for delisted firms.
- Compustat `conm` is the CURRENT company name: CenturyLink lives under
  'LUMEN TECHNOLOGIES INC'.
- Name wildcards token-collide ('LUMEN%%' matches five unrelated firms).
  gvkey-exact is the only safe join for these pulls.
- The CCM link table (crsp.ccmxpf_lnkhist) is not licensed on this account;
  gvkeys above were resolved by name + verified by fiscal-year coverage.

## Credentials
WRDS pgpass (Windows: %APPDATA%/postgresql/pgpass.conf) for wrds-pgdata
.wharton.upenn.edu:9737; scripts/159 connects as `wrds.Connection(
wrds_username='tispivey')` and never prompts when pgpass is present.

## Replication environment notes
- Windows clones MUST use `git clone -c core.longpaths=true` (or a short target
  path): the article-library filenames exceed default MAX_PATH and checkout
  fails otherwise (observed 8/4/2026).
- Public SEC inputs are git-tracked (EDGAR name/CIK lookup via LFS, ticker
  files, registry snapshot, submissions cache); only WRDS-licensed extracts
  follow the pull-or-skip pattern above.
- Local file:// clones additionally need LFS objects materialized manually
  (git-lfs does not auto-transfer from file:// remotes); clones from the GitHub
  remote smudge normally. Observed and worked around 8/4/2026.
