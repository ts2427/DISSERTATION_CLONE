# REBUILD V4 — WRDS access probe

- run (UTC): 2026-09-18T18:50:38+00:00
- read-only: every query is LIMIT 1; no data file is written

- WRDS username: tispivey

## 1. Libraries visible to this account

211 libraries.

```
  aha_sample              ahasamp                 altrata_exec_samp       altsamp                 audit                   audit_audit_comp
  audit_common            auditsmp                auditsmp_all            bank                    bank_all                bank_premium_samp
  banksamp                block                   block_all               boardex_trial           boardsmp                bvd_amadeus_trial
  bvd_bvdbankf_trial      bvd_orbis_trial         bvdsamp                 calcbench_trial         calcbnch                candid_samp
  cboe                    cboe_all                cboe_sample             cboesamp                cddsamp                 ciqsamp
  ciqsamp_capstrct        ciqsamp_common          ciqsamp_keydev          ciqsamp_pplintel        ciqsamp_ratings         ciqsamp_transactions
  ciqsamp_transcripts     cisdmsmp                columnar                comp                    comp_bank_daily         comp_execucomp
  comp_global_daily       comp_na_daily_all       comp_segments_hist_daily  compsamp                compsamp_all            compsamp_computext
  compsamp_snapshot       compseg                 contrib                 contrib_ceo_turnover    contrib_char_returns    contrib_corp_fed_litigation
  contrib_corporate_culture  contrib_general         contrib_global_factor   contrib_intangible_value  contrib_kpss            contrib_liva
  contrib_patent_firm_link  crsp                    crsp_a_indexes          crsp_a_stock            crspsamp                crspsamp_all
  crspsamp_mf             csmsamp_all             djones                  djones_all              dmef                    dmef_all
  doe                     doe_all                 etfg_samp               etfgsamp                execcomp                factsamp_all
  factsamp_revere         ff                      ff_all                  fisdsamp                fisdsamp_all            fjc
  fjc_linking             fjc_litigation          frb                     frb_all                 fssamp                  ftsesamp
  ftsesamp_russell_us     gutenberg               hfrsamp                 hfrsamp_hfrdb           ibessamp_kpi            ifgrsamp
  infasamp                infogroupsamp_business  infogroupsamp_residential  infraclear_samp         insdsamp                iri
  iri_all                 kpisamp                 macrofin                macrofin_comm_trade     midas                   morningstarsamp_cisdm
  mpsych_sample           mrktsamp                mrktsamp_cds            mrktsamp_cdx            mrktsamp_msf            mrktsamp_red
  msci_climate_samp       msci_common_samp        msci_esg_samp           mscicoms                mscicsmp                msciesmp
  msrb                    msrb_all                msrbsamp                msrbsamp_all            omtrial                 optionmsamp_europe
  optionmsamp_us          otc                     otc_endofday            panjiva_samp            phlx                    phlx_all
  pitchsmp                pnjvasmp                preqsamp                preqsamp_all            public                  public_all
  pwt                     pwt_all                 reprisk_sample          repsamp                 revelio_samp            revsamp
  risksamp                risksamp_all            rq_all                  rstat_samp              rstatsmp                sdcsamp
  shvlsamp                snapsamp                snlsamp                 snlsamp_fig             sustainalyticssamp_all  sustsamp
  taqmsamp                taqmsamp_all            taqsamp                 taqsamp_all             totalq                  totalq_all
  tr_sdc_samples          trace                   trace_enhanced          trace_standard          trcstsmp                trdbdmismp
  trdbwbsmp               trdssamp                tresgsmp                trsamp                  trsamp_all              trsamp_db_dmi
  trsamp_db_wb            trsamp_ds_eq            trsamp_dscom            trsamp_dsecon           trsamp_dsfut            trsamp_esg
  trsamp_sdc_ma           trsamp_sdc_ni           trsamp_worldscope       trucost_samp            twoiq_samp              twoiqsmp
  wabssamp                wappsamp                wenvsmp                 wmfsmp                  wrds_abs_samp           wrds_environmental_samp
  wrds_insiders_samp      wrds_mutualfund_samp    wrds_shortvolume_samp   wrdsapps                wrdsapps_eushort        wrdsapps_evtstudy_int
  wrdsapps_evtstudy_us    wrdsapps_finratio       wrdsapps_link_comp_eushort  wrdsapps_link_crsp_bond  wrdsapps_link_crsp_factset  wrdsapps_link_crsp_taq
  wrdsapps_patents        wrdsapps_subsidiary     wrdsapps_windices       wrdsappssamp_all        wrdssec_midas           zacksamp
  zacksamp_all
```

- libraries with 'ccm' in the name: none

## 2. Candidate tables (SELECT * LIMIT 1)

| table | purpose | result | detail |
|---|---|---|---|
| `crsp.ccmxpf_lnkhist` | CCM link history (Stage 2 primary) | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `crsp.ccmxpf_linktable` | CCM link table (alternate name) | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `comp.company` | Compustat company header (CIK -> gvkey) | OK | 40 cols, 1 row: conm, gvkey, add1, add2, add3, add4, addzip, busdesc, cik, city, conml, costat, county, dlrsn... |
| `comp.security` | Compustat security (gvkey -> cusip; CUSIP-route source) | OK | 16 cols, 1 row: tic, gvkey, iid, cusip, dlrsni, dsci, epf, exchg, excntry, ibtic, isin, secstat, sedol, tpci... |
| `crsp.stocknames` | CRSP names, permno/cusip/ticker with date validity | OK | 16 cols, 1 row: permno, namedt, nameenddt, shrcd, exchcd, siccd, ncusip, ticker, comnam, shrcls, permco, hexcd, cusip, st_date... |
| `crsp.msenames` | CRSP monthly names (CUSIP-route fallback) | OK | 21 cols, 1 row: permno, namedt, nameendt, shrcd, exchcd, siccd, ncusip, ticker, comnam, shrcls, tsymbol, naics, primexch, trdstat... |
| `crsp.dsenames` | CRSP daily names (CUSIP-route fallback) | OK | 21 cols, 1 row: permno, namedt, nameendt, shrcd, exchcd, siccd, ncusip, ticker, comnam, shrcls, tsymbol, naics, primexch, trdstat... |
| `crsp.dsf` | CRSP daily stock file | OK | 20 cols, 1 row: cusip, permno, permco, issuno, hexcd, hsiccd, date, bidlo, askhi, prc, vol, ret, bid, ask... |
| `crsp.dsi` | CRSP daily market index | OK | 11 cols, 1 row: date, vwretd, vwretx, ewretd, ewretx, sprtrn, spindx, totval, totcnt, usdval, usdcnt |
| `wrdssec.wciklink_gvkey` | SEC Analytics CIK-GVKEY link | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdssec_common |
| `wrdssec_midas.wciklink_gvkey` | SEC Analytics CIK-GVKEY link (midas) | FAIL | ProgrammingError: (psycopg2.errors.UndefinedTable) relation "wrdssec_midas.wciklink_gvkey" does not exist |

## 3. Discovered tables matching link / ccm / cik / gvkey

- `comp`: 2 of 293 tables match -> `g_sedolgvkey`, `sedolgvkey`
- `crsp`: 7 of 433 tables match -> `ccm_lookup`, `ccm_qvards`, `ccmxpf_linktable`, `ccmxpf_lnkhist`, `ccmxpf_lnkrng`, `ccmxpf_lnkused`, `crsp_cik_map`
- `wrdsapps`: 26 of 71 tables match -> `bdxcrspcomplink`, `bdxinslink`, `boardex_ciq_link`, `boardex_trinsider_link`, `boardex_twoiq_link`, `bondcrsp_link`, `compeushortlink`, `ds2ws_linktable`, `dswslink`, `exec_boardex_link`, `exec_ciq_link`, `exec_trinsider_link`, `exec_twoiq_link`, `firm_ratio_ccm`, `firm_ratio_ibes_ccm`, `fscrsplink`, `id_ccm`, `id_ibes_ccm`, `seglink`, `taqmclink`, `taqmclink_cusip_2010`, `tclink`, `trinsider_ciq_link`, `trinsider_twoiq_link`, `twoiq_ciq_link` ...

### Probing the discovered tables

| table | result | detail |
|---|---|---|
| `comp.g_sedolgvkey` | OK | 3 cols, 1 row: gvkey, iid, sedol |
| `comp.sedolgvkey` | OK | 3 cols, 1 row: gvkey, iid, sedol |
| `crsp.ccm_lookup` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `crsp.ccm_qvards` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `crsp.ccmxpf_lnkrng` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `crsp.ccmxpf_lnkused` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_a_ccm |
| `crsp.crsp_cik_map` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema crsp_q_mutualfunds |
| `wrdsapps.bdxcrspcomplink` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_crsp_comp_bdx |
| `wrdsapps.bdxinslink` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_trinsider_bdx |
| `wrdsapps.boardex_ciq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_boardex_ciq |
| `wrdsapps.boardex_trinsider_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_boardex_trinsider |
| `wrdsapps.boardex_twoiq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_boardex_twoiq |
| `wrdsapps.bondcrsp_link` | OK | 9 cols, 1 row: cusip, permno, permco, trace_startdt, trace_enddt, crsp_startdt, crsp_enddt, link_startdt, link_enddt |
| `wrdsapps.compeushortlink` | OK | 6 cols, 1 row: country, issuer, isin, gvkey, iid, conm |
| `wrdsapps.ds2ws_linktable` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_datastream_wscope |
| `wrdsapps.dswslink` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_dealscan_wscope |
| `wrdsapps.exec_boardex_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_exec_boardex |
| `wrdsapps.exec_ciq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_exec_ciq |
| `wrdsapps.exec_trinsider_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_exec_trinsider |
| `wrdsapps.exec_twoiq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_exec_twoiq |
| `wrdsapps.firm_ratio_ccm` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_finratio_ccm |
| `wrdsapps.firm_ratio_ibes_ccm` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_finratio_ibes_ccm |
| `wrdsapps.fscrsplink` | OK | 18 cols, 1 row: fsym_id, fsym_id_kind, proper_name, fsym_regional_id, fsym_security_id, fs_perm_sec_id, factset_entity_id, entity_proper_name, cusip_fs, ticker_exchange, permno, permco, hdrcusip, cusip... |
| `wrdsapps.id_ccm` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_finratio_ccm |
| `wrdsapps.id_ibes_ccm` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_finratio_ibes_ccm |
| `wrdsapps.seglink` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_supplychain |
| `wrdsapps.taqmclink` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_crsp_taqm |
| `wrdsapps.taqmclink_cusip_2010` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_link_crsp_taqm |
| `wrdsapps.tclink` | OK | 10 cols, 1 row: permno, cusip, date, symbol, name, cusip_full, fdate, comnam, score, namedis |
| `wrdsapps.trinsider_ciq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_trinsider_ciq |
| `wrdsapps.trinsider_twoiq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_trinsider_twoiq |
| `wrdsapps.twoiq_ciq_link` | FAIL | ProgrammingError: (psycopg2.errors.InsufficientPrivilege) permission denied for schema wrdsapps_plink_twoiq_ciq |
| `wrdsapps.uspatents_gvkey_linking` | OK | 8 cols, 1 row: patnum, gvkey_numeric, link_bdate, initial_assign, subsidiary_flag, wrds_score, multi_names_flag, gvkey |

## 4. Verdict for the Stage 2 rule

- reachable tables: 14
- blocked tables  : 30

**A link table IS reachable:** `wrdsapps.bondcrsp_link`, `wrdsapps.compeushortlink`, `wrdsapps.fscrsplink`, `wrdsapps.tclink`, `wrdsapps.uspatents_gvkey_linking`
Stage 2 can use the gvkey -> permno link with linktype/linkprim and date validity, as originally specified.

Do not change the Stage 2 rule from this file alone; return it and the choice is made jointly.

- finished (UTC): 2026-09-18T18:50:57+00:00

---

## CORRECTION — 2026-09-18 (appended; the text above is left as originally emitted)

**The verdict in section 4 above is WRONG. Disregard it.**

Section 4 reports "A link table IS reachable" and names `wrdsapps.bondcrsp_link`,
`wrdsapps.compeushortlink`, `wrdsapps.fscrsplink`, `wrdsapps.tclink` and
`wrdsapps.uspatents_gvkey_linking`. **None of those is a gvkey → permno link.** They are,
respectively, a bond-to-CRSP bridge, a European short-interest link, a FactSet-CRSP link,
a TAQ-CRSP link, and a patent-to-gvkey link.

### Why the probe got it wrong

The verdict predicate was a substring match:

```python
ccm_ok = [t for t in reachable if "ccm" in t.lower() or "lnk" in t.lower()
          or "link" in t.lower()]
```

Every one of those five table names contains the substring `link`, so all five satisfied
it. A substring match on "link" tests what a table is *called*, not what it *links*. The
defect is in `scripts/216_wrds_access_probe.py`, not in the probe results — sections 1
through 3 above are accurate and remain usable.

### Fixed

`is_ccm_link()` now identifies the CCM family structurally: the bare table name must begin
with `ccmxpf_` (`ccmxpf_lnkhist`, `ccmxpf_linktable`, `ccmxpf_lnkused`), or the library
must itself be CCM-family and the name carry `lnk`/`link`. All five tables above are
excluded by construction rather than by blacklist. The corrected verdict also lists any
reachable table whose name contains link/lnk but which does not qualify, so the exclusion
is visible rather than silent, and it asserts both halves of the CUSIP route separately.

### The actual access position

| | |
|---|---|
| **Blocked** | CCM (`crsp_a_ccm`, all `ccmxpf_*`), `wrdssec` / `wrdssec_midas` |
| **Reachable** | `comp.company`, `comp.security`, `crsp.stocknames`, `crsp.dsenames`, `crsp.msenames`, `crsp.dsf`, `crsp.dsi` |

No gvkey → permno link table is reachable on this subscription.

### Decision

**The CUSIP route.** CIK → gvkey (`comp.company`) → primary US issue → CUSIP
(`comp.security`) → permno (`crsp.stocknames`, on historical `ncusip` with date validity,
falling back to header `cusip`), requiring `shrcd ∈ {10, 11}`.

Stage 1 and Stage 2 of `docs/claude/REBUILD_V4_QUERY.md` are amended accordingly in the
same commit as this correction. `scripts/211` drops the `ccmxpf_lnkhist` and `wrdssec`
pulls and adds `comp.security`.
