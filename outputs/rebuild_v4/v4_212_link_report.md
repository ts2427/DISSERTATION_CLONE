- comp_company: 151 rows from 3 file(s) (comp_company.csv, comp_company_topup_20260919T000910Z.csv, comp_company_topup_20260919T135055Z.csv)
- comp_security: 316 rows from 3 file(s) (comp_security.csv, comp_security_topup_20260919T000910Z.csv, comp_security_topup_20260919T135055Z.csv)
- crsp_stocknames: 1,308 rows from 4 file(s) (crsp_stocknames.csv, crsp_stocknames_topup_20260919T000910Z.csv, crsp_stocknames_topup_20260919T135055Z.csv, crsp_stocknames_topup_20260919T135055Z_issuer.csv)
# REBUILD V4 — Stage 2 point-in-time linker (CUSIP route)

- run (UTC): 2026-09-19T14:00:59+00:00
- events 489 | comp.company 151 | comp.security 316 | stocknames 1308
- rule: all US common issues (tpci=0, excntry=USA), ncusip-first, header fallback behind the identity gate

## Regression tests

**T-Mobile before 2013-04-29** — 6 events, linked 0 (must be 0), excluded by the gate 6. **PASS**

| breach_date | comnam | permno_rejected | note |
|---|---|---|---|
| 2009-09-03 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |
| 2009-10-05 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |
| 2009-10-08 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |
| 2011-10-21 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |
| 2012-05-08 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |
| 2012-08-28 | METROPCS COMMUNICATIONS INC | 91937.0 | CRSP name at breach_date does not match the breached organization; parent relationship unverified |

**Sprint pre-2013** — 2 events, permnos reached [39087], v3 used [14040, 39087]. **PASS**

| breach_date | permno | v3_permno | link_source | comnam |
|---|---|---|---|---|
| 2009-02-01 | 39087.0 | 39087.0 | cusip_ncusip | SPRINT NEXTEL CORP |
| 2009-01-01 | 39087.0 | 39087.0 | cusip_ncusip | SPRINT NEXTEL CORP |
| 2015-08-17 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2017-05-01 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2017-05-07 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2018-03-02 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-03-14 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-05-09 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-06-02 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-06-08 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-06-22 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |
| 2019-08-13 | 14040.0 | 14040.0 | cusip_ncusip | SPRINT CORP NEW |

## Linked events, v3 vs v4

| group | events | v3 linked | v4 linked | delta |
|---|---|---|---|---|
| treated | 118 | 111 | 111 | 0 |
| control | 371 | 250 | 303 | 53 |
| ALL | 489 | 361 | 414 | 53 |

link_source:

| link_source | control | treated |
|---|---|---|
| (unlinked) | 68 | 7 |
| cusip_header | 32 | 7 |
| cusip_issuer | 7 | 0 |
| cusip_ncusip | 264 | 104 |

Tie-break usage: {'priusa': 18, 'shrcd': 0, 'namedt': 0} (priusa resolves the dual-class pairs; the shrcd and namedt rules are reported if they ever fire).

## Every unlinked event, by reason

| reason | control | treated | All |
|---|---|---|---|
| CRSP name at breach_date does not match the breached organization; parent relationship unverified | 3 | 6 | 9 |
| no US common issue | 3 | 0 | 3 |
| no gvkey | 19 | 0 | 19 |
| no names row valid on breach_date | 42 | 1 | 43 |
| shrcd not in [10, 11, 12, 18, 72] ([31]) | 1 | 0 | 1 |
| All | 68 | 7 | 75 |

## Identity gate (header links only)

| outcome | treated | control | total |
|---|---|---|---|
| accepted | 7 | 32 | 39 |
| excluded | 6 | 3 | 9 |

### Every header accept, for audit of the normalisation

| final_cik | org_name | comnam | breach_date | permno |
|---|---|---|---|---|
| 18926 | CenturyLink | CENTURYLINK INC | 2013-12-27 | 60599.0 |
| 47217 | Hewlett-Packard Company | HEWLETT PACKARD CO | 2007-07-01 | 27828.0 |
| 68505 | Motorola, Inc. | MOTOROLA INC | 2009-01-01 | 22779.0 |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M RADIO INC | 2012-03-19 | 80924.0 |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M HOLDINGS INC | 2016-02-01 | 80924.0 |
| 1971213 | Sinclair Broadcast Group, Inc. | SINCLAIR BROADCAST GROUP INC | 2020-05-01 | 81740.0 |
| 1051470 | Crown Castle | CROWN CASTLE INTERNATIONAL CORP | 2013-10-31 | 86339.0 |
| 1091667 | Charter Communications, Inc. | CHARTER COMMUNICATIONS INC | 2013-04-26 | 12308.0 |
| 1105705 | Time Warner Inc. | TIME WARNER INC NEW | 2006-12-01 | 77418.0 |
| 1137789 | Seagate US LLC | SEAGATE TECHNOLOGY PLC | 2016-02-29 | 89641.0 |
| 1652044 | Google, Inc. | GOOGLE INC | 2008-06-27 | 90319.0 |

### Every gate exclusion

| final_cik | org_name | comnam | breach_date | permno_rejected |
|---|---|---|---|---|
| 1067837 | Audacy, Inc | ENTERCOM COMMUNICATIONS CORP | 2019-08-04 | 86560.0 |
| 1283699 | T-Mobile USA, Inc. | METROPCS COMMUNICATIONS INC | 2009-09-03 | 91937.0 |
| 1283699 | T-Mobile USA, Inc. | METROPCS COMMUNICATIONS INC | 2009-10-05 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2009-10-08 | 91937.0 |
| 1283699 | T-Mobile USA Inc. | METROPCS COMMUNICATIONS INC | 2011-10-21 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2012-05-08 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2012-08-28 | 91937.0 |
| 1308161 | Fox Entertainment Group | NEWS CORP | 2009-04-09 | 90441.0 |
| 1308161 | Fox Entertainment Group Inc. | NEWS CORP | 2009-04-15 | 90441.0 |

## Report-only: ncusip links whose CRSP name matches neither org nor EDGAR

37 of 368 ncusip links. **None is excluded** — the CUSIP is authoritative here; a name mismatch means the name differs, not that the security is wrong.

| final_cik | org_name | comnam | permno | documented | final_evidence |
|---|---|---|---|---|---|
| 18926 | Centurylink Communications | LUMEN TECHOLOGIES INC | 60599.0 | True | Gate1-G rescue: CenturyLink/Lumen parent (Form 499 relevant carrier) (ticker LUMN -> CIK 18926) |
| 33185 | TALX Corporation | EQUIFAX INC | 52476.0 | True | Gate2 CH-21: TALX filings end 2007 (SEC-verified); 2016 breaches under Equifax ownership; parent-map via EFX |
| 51143 | IBM | INTERNATIONAL BUSINESS MACHS COR | 12490.0 | True | Gate1-G rescue: acronym defeated exact match; documented acronym mapping (ticker IBM -> CIK 51143) |
| 731766 | Change Healthcare Inc. | UNITEDHEALTH GROUP INC | 92655.0 | True | Gate1-C: UnitedHealth parent post-10/2022 acquisition; legacy GEHC was fuzzy error |
| 732717 | AT&T Services, Inc. | A T & T INC | 66093.0 | True | SEC EDGAR: AT&T Services is operating subsidiary of AT&T Inc. | EDGAR-confirmed |
| 789019 | Nuance Communications, Inc. | MICROSOFT CORP | 10107.0 | True | Gate1-B: Microsoft subsidiary, parent-mapped |
| 790070 | EMC Corporation | E M C CORP MA | 10147.0 | True | EDGAR name: EMC CORP |
| 1105705 | Home Box Office, Inc. | TIME WARNER INC NEW | 77418.0 | True | EDGAR name: HOME BOX OFFICE, INC. | EQUITY-PARENT: Home Box Office Inc registrant has no equity; 2017 parent = Time Warner Inc TWX (FedEx Ground class) |
| 1166691 | NBC Sports Group | COMCAST CORP NEW | 89525.0 | True | Gate1-E: identity=Comcast equity; treatment classification independent (clause rules at Stage 4) |
| 1283699 | Sprint | T MOBILE U S INC | 91937.0 | True | Gate1-F: TMUS post-merger |
| 1512673 | Block and Company, Inc. | SQUARE INC | 15826.0 | True | SEC EDGAR: Block Inc. (formerly Square Inc.) CIK 1512673 verified. Name changed Dec 2021 | EDGAR-confirmed |
| 1652044 | Google Inc. | ALPHABET INC | 90319.0 | True | Gate1-B: Alphabet Inc (ticker GOOGL) |
| 1669779 | CWGS Group | CAMPING WORLD HOLDINGS INC | 16437.0 | True | Gate1-G rescue: Camping World Holdings (EDGAR-verified: CWGS Holding LLC 1683140 files nothing; CWH is reporting entity) |

**35** of the 37 carry a Gate 1 or Gate 2 verdict or an EDGAR confirmation in `final_evidence`: the v3 chain already adjudicated the identity, so the differing name is explained. The remaining **2** carry neither and go to `stage3_candidates.csv` as `ncusip_name_mismatch` — the link stands, but the identity is unadjudicated.

### The 2 unadjudicated mismatch(es), in full

| final_cik | org_name | comnam | breach_date | permno | final_evidence |
|---|---|---|---|---|---|
| 732717 | Cricket Wireless LLC | A T & T INC | 2018-08-17 | 66093.0 | AT&T Inc. — Cricket Communications FRN 0004321139; LLC variant; 7/28 adjudication |
| 732717 | Cricket Wireless LLC | A T & T INC | 2018-08-21 | 66093.0 | AT&T Inc. — Cricket Communications FRN 0004321139; LLC variant; 7/28 adjudication |

## Agreement with v3

| group | v3 linked | both | same permno | different |
|---|---|---|---|---|
| treated | 111 | 111 | 111 | 0 |
| control | 250 | 240 | 234 | 6 |

### Every disagreement (6)

| final_cik | org_name | breach_date | v3_permno | permno | comnam | link_source |
|---|---|---|---|---|---|---|
| 2041610 | Paramount | 2023-01-01 | 76226.0 | 75104.0 | PARAMOUNT GLOBAL | cusip_ncusip |
| 2041610 | Paramount Global | 2023-08-10 | 76226.0 | 75104.0 | PARAMOUNT GLOBAL | cusip_ncusip |
| 1652044 | Google Inc. | 2016-03-29 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google Inc. | 2016-05-06 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google Inc. | 2016-08-10 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google, Inc. | 2017-06-29 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |

- v3 linked, v4 not: **10** (treated 0, control 10)
- v4 linked, v3 not: **63** (treated 0, control 63)

| reason | events |
|---|---|
| no names row valid on breach_date | 9 |
| shrcd not in [10, 11, 12, 18, 72] ([31]) | 1 |

## CIKs with no gvkey, classified

| type | CIKs |
|---|---|
| c_no_compustat | 8 |
| b_successor_cik | 4 |
| d_other | 4 |
| a_subsidiary | 3 |

| final_cik | org | grp | events | candidate_type | candidate | confidence | shared_tokens |
|---|---|---|---|---|---|---|---|
| 14745 | Brown, Lisle/Cummings, Inc. | control | 1 | b_successor_cik | BROWN FORMAN CORP (gvkey 2435, cik 14693) | unverified | BROWN |
| 826083 | Dell Inc. | control | 1 | b_successor_cik | DELL TECHNOLOGIES INC (gvkey 14489, cik 1571996) | unverified | DELL |
| 1000564 | Communications & Power Industries LLC | control | 1 | b_successor_cik | AMERICAN ELECTRIC POWER CO (gvkey 1440, cik 4904) | unverified | POWER |
| 1091411 | Sony Corporation of America | control | 1 | a_subsidiary | Sony Group Corporation |  |  |
| 1145813 | Fox Group | control | 1 | d_other |  |  |  |
| 1168812 | HBP, Inc. | control | 1 | d_other |  |  |  |
| 1260451 | Vulcan Industries | control | 1 | c_no_compustat |  |  | INDUSTRIES |
| 1396897 | NCO Financial Systems, Inc. | control | 1 | c_no_compustat |  |  | SYSTEMS |
| 1431473 | Uber | control | 1 | b_successor_cik | UBER TECHNOLOGIES INC (gvkey 35077, cik 1543151) | unverified | UBER |
| 1497060 | Capital Integration Systems LLC | control | 1 | c_no_compustat |  |  | SYSTEMS |
| 1558044 | Professional Compounding Centers of America, Inc. | control | 1 | d_other |  |  |  |
| 1560142 | EatStreet | control | 1 | d_other |  |  |  |
| 1567336 | Mediant Communications Inc. | control | 1 | c_no_compustat |  |  | COMMUNICATIONS |
| 1570434 | Prime Communications | control | 1 | c_no_compustat |  |  | COMMUNICATIONS |
| 1673769 | IMA Financial Group, Inc. | control | 1 | c_no_compustat |  |  | FINANCIAL |
| 1691249 | The iRemedy Healthcare Companies, Inc. | control | 1 | c_no_compustat |  |  | HEALTHCARE |
| 1826210 | KeraLink International | control | 1 | c_no_compustat |  |  | INTERNATIONAL |
| 1834695 | Volkswagen Group of America, Inc. | control | 1 | a_subsidiary | Volkswagen AG |  |  |
| 1984463 | Warn Industries, Inc. | control | 1 | a_subsidiary | Dover Corporation |  |  |

## Shared tokens behind every name match (header accepts + successor nominations)

The rule accepts a match on ONE shared token of length >= 4. That is fine for `CENTURYLINK` and worthless for `COMMUNICATIONS`. Every match is listed with the token(s) that produced it; a match resting ONLY on industry words is flagged. **The rule is unchanged** — nothing below is excluded on this basis.

### Header accepts

| final_cik | org_name | comnam | shared_tokens | matched_against | generic_only |
|---|---|---|---|---|---|
| 18926 | CenturyLink | CENTURYLINK INC | CENTURYLINK | org | False |
| 47217 | Hewlett-Packard Company | HEWLETT PACKARD CO | HEWLETT|PACKARD | org | False |
| 68505 | Motorola, Inc. | MOTOROLA INC | MOTOROLA | org | False |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M RADIO INC | RADIO|SIRIUS | org | False |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M HOLDINGS INC | SIRIUS | org | False |
| 1971213 | Sinclair Broadcast Group, Inc. | SINCLAIR BROADCAST GROUP INC | BROADCAST|SINCLAIR | org | False |
| 1051470 | Crown Castle | CROWN CASTLE INTERNATIONAL CORP | CASTLE|CROWN | org | False |
| 1091667 | Charter Communications, Inc. | CHARTER COMMUNICATIONS INC | CHARTER|COMMUNICATIONS | org | False |
| 1105705 | Time Warner Inc. | TIME WARNER INC NEW | TIME|WARNER | org | False |
| 1137789 | Seagate US LLC | SEAGATE TECHNOLOGY PLC | SEAGATE | org | False |
| 1652044 | Google, Inc. | GOOGLE INC | GOOGLE | org | False |

### b_successor_cik nominations that survive

| final_cik | org | candidate | shared_tokens |
|---|---|---|---|
| 14745 | Brown, Lisle/Cummings, Inc. | BROWN FORMAN CORP (gvkey 2435, cik 14693) | BROWN |
| 826083 | Dell Inc. | DELL TECHNOLOGIES INC (gvkey 14489, cik 1571996) | DELL |
| 1000564 | Communications & Power Industries LLC | AMERICAN ELECTRIC POWER CO (gvkey 1440, cik 4904) | POWER |
| 1431473 | Uber | UBER TECHNOLOGIES INC (gvkey 35077, cik 1543151) | UBER |

### Reclassified to c_no_compustat — nomination rested only on an industry word (8)

These are not nominations and do NOT reach `stage3_candidates.csv`. The rejected candidate is kept in `note` so the decision is auditable.

| final_cik | org | grp | events | candidate_type | shared_tokens | note |
|---|---|---|---|---|---|---|
| 1260451 | Vulcan Industries | control | 1 | c_no_compustat | INDUSTRIES | nomination rested only on an industry word: rejected ABM INDUSTRIES INC (gvkey 1410, cik 771497) on INDUSTRIES |
| 1396897 | NCO Financial Systems, Inc. | control | 1 | c_no_compustat | SYSTEMS | nomination rested only on an industry word: rejected CISCO SYSTEMS INC (gvkey 20779, cik 858877) on SYSTEMS |
| 1497060 | Capital Integration Systems LLC | control | 1 | c_no_compustat | SYSTEMS | nomination rested only on an industry word: rejected CISCO SYSTEMS INC (gvkey 20779, cik 858877) on SYSTEMS |
| 1567336 | Mediant Communications Inc. | control | 1 | c_no_compustat | COMMUNICATIONS | nomination rested only on an industry word: rejected VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) on COMMUNICATIONS |
| 1570434 | Prime Communications | control | 1 | c_no_compustat | COMMUNICATIONS | nomination rested only on an industry word: rejected VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) on COMMUNICATIONS |
| 1673769 | IMA Financial Group, Inc. | control | 1 | c_no_compustat | FINANCIAL | nomination rested only on an industry word: rejected COREBRIDGE FINANCIAL INC (gvkey 41084, cik 1889539) on FINANCIAL |
| 1691249 | The iRemedy Healthcare Companies, Inc. | control | 1 | c_no_compustat | HEALTHCARE | nomination rested only on an industry word: rejected NEXTGEN HEALTHCARE INC (gvkey 8858, cik 708818) on HEALTHCARE |
| 1826210 | KeraLink International | control | 1 | c_no_compustat | INTERNATIONAL | nomination rested only on an industry word: rejected HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) on INTERNATIONAL |

### Header accepts resting on generic tokens only — 0

None: every header accept shares a real identity token.

## Unmatched tpci=0 / USA CUSIPs

73 US common issues have no CRSP names row.

| gvkey | conm | cusip8 | exchg | secstat |
|---|---|---|---|---|
| 176083 | AEROGROW INTERNATIONAL INC | 00768M20 | 19 | I |
| 160329 | ALPHABET INC | 02079K20 | 1 | A |
| 1602 | AMGEN INC | 03116293 | 1 | I |
| 117902 | AUDACY INC | 05070N20 | 19 | I |
| 117902 | AUDACY INC | 29363901 | 1 | I |
| 117902 | AUDACY INC | 29363994 | 1 | I |
| 26367 | BLOCK INC | 85299J93 | 1 | A |
| 19071 | CAMPING WORLD HOLDINGS INC | 13462K01 | 1 | I |
| 19071 | CAMPING WORLD HOLDINGS INC | 13462K02 | 1 | I |
| 13498 | CARNIVAL CORP LTD | G2004J10 | 11 | A |
| 13498 | CARNIVAL CORP LTD | 14365893 | 1 | I |
| 13498 | CARNIVAL CORP LTD | G1908110 | 19 | I |
| 31673 | CENCORA INC | 03073E30 | 1 | I |
| 31673 | CENCORA INC | 03073E20 | 1 | I |
| 25964 | CHART INDUSTRIES INC | 16115Q20 | 13 | I |
| 126136 | CHARTER COMMUNICATIONS INC | 16119P01 | 1 | I |
| 111864 | COGNIZANT TECH SOLUTIONS | 19244620 | 1 | I |
| 111864 | COGNIZANT TECH SOLUTIONS | 19244693 | 1 | I |
| 3226 | COMCAST CORP | 20099Q93 | 1 | A |
| 105999 | CONSOLIDATED EDISON CO OF NY | 20999X00 | 0 | A |
| 35182 | CROWDSTRIKE HOLDINGS INC | 22788C01 | 1 | I |
| 113490 | CROWN CASTLE INC | 22822793 | 20 | I |
| 9537 | CSX TRANSPORTATION INC | 12641000 | 0 | I |
| 14489 | DELL TECHNOLOGIES INC | 24703L02 | 1 | A |
| 14489 | DELL TECHNOLOGIES INC | 24703L03 | 1 | A |
| 14489 | DELL TECHNOLOGIES INC | 24799R93 | 1 | A |
| 14489 | DELL TECHNOLOGIES INC | 24703L01 | 1 | A |
| 14489 | DELL TECHNOLOGIES INC | 24799Q93 | 1 | I |
| 60900 | DISH NETWORK CORP | 25470M01 | 1 | I |
| 37420 | DOORDASH INC | 25999Z93 | 1 | A |
| 4058 | DOVER CORP | 26000312 | 11 | I |
| 61567 | ESTEE LAUDER COMPANIES INC | 51843920 | 1 | A |
| 32886 | GATES INDUSTRIAL CORPORATION | G3910410 | 11 | A |
| 23071 | GODADDY INC | 38099O93 | 1 | I |
| 5597 | HERSHEY CO | 42786630 | 1 | A |
| 26156 | HEWLETT PACKARD ENTERPRISE | 42824C12 | 11 | I |
| 26156 | HEWLETT PACKARD ENTERPRISE | 42824C11 | 11 | I |
| 1300 | HONEYWELL INTERNATIONAL INC | 43851613 | 11 | I |
| 1300 | HONEYWELL INTERNATIONAL INC | 43851620 | 14 | A |
| 3105 | IHEARTMEDIA INC | 45174J60 | 19 | A |
| 3105 | IHEARTMEDIA INC | 12502P98 | 1 | I |
| 3105 | IHEARTMEDIA INC | 12502P01 | 1 | I |
| 3105 | IHEARTMEDIA INC | 45174J10 | 19 | I |
| 6669 | LENNAR CORP | 52605720 | 1 | I |
| 129442 | MEDIACOM COMMUNICATIONS CORP | 58446K93 | 1 | I |
| 170617 | META PLATFORMS INC | 30303M01 | 1 | A |
| 7646 | NCH CORP | 62885020 | 19 | I |
| 23671 | NOKIA OYJ | X6187313 | 19 | A |
| 23671 | NOKIA OYJ | 65490210 | 13 | I |
| 30736 | OKTA INC | 67999I93 | 1 | A |
| 12485 | OPTIMUM COMMUNICATIONS INC | 02199N93 | 1 | A |
| 12485 | OPTIMUM COMMUNICATIONS INC | 12686C01 | 1 | I |
| 13714 | PARAMOUNT SKYDANCE CORP | 69999R93 | 1 | A |
| 13714 | PARAMOUNT SKYDANCE CORP | 69932A20 | 14 | A |
| 23812 | REGENERON PHARMACEUTICALS | 75886F93 | 1 | A |
| 112168 | REPUBLIC SERVICES INC | 76075993 | 1 | I |
| 32382 | ROKU INC | 77543R01 | 1 | A |
| 60800 | SINCLAIR INC | 82922670 | 1 | A |
| 30091 | SNAP INC | 83304A01 | 1 | A |
| 30091 | SNAP INC | 83304A02 | 1 | A |
| 339965 | SNOWFLAKE INC | 83399I93 | 1 | I |
| 9818 | SONY GROUP CORPORATION | J7637910 | 19 | A |
| 10984 | SPRINT CORP | 85206199 | 1 | I |
| 10984 | SPRINT CORP | 85206198 | 1 | I |
| 25056 | TIME WARNER INC | 88731799 | 1 | I |
| 27364 | TWILIO INC | 90138F01 | 1 | I |
| 10484 | UNITED AIRLINES INC | 91004700 | 0 | A |
| 10484 | UNITED AIRLINES INC | 21079593 | 1 | I |
| 178083 | VMWARE INC -CL A | 92856301 | 1 | I |
| 163118 | WARNER MUSIC GROUP CORP | 93499A93 | 1 | A |
| 32771 | WILLSCOT HOLDINGS CORP | 97199S93 | 1 | A |
| 15044 | WORKDAY INC | 98138H20 | 1 | A |
| 11636 | XEROX HOLDINGS CORP | 98412193 | 1 | I |

## Stage 3 candidates

18 rows written to `outputs/rebuild_v4/stage3_candidates.csv`.

| type | rows |
|---|---|
| gate_exclusion | 9 |
| b_successor_cik | 4 |
| a_subsidiary | 3 |
| ncusip_name_mismatch | 2 |

