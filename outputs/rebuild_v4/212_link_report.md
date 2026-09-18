# REBUILD V4 — Stage 2 point-in-time linker (CUSIP route)

- run (UTC): 2026-09-18T19:40:38+00:00
- events 489 | comp.company 148 | comp.security 308 | stocknames 613
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
| 2012-08-01 | 39087.0 | 39087.0 | cusip_ncusip | SPRINT NEXTEL CORP |
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
| control | 371 | 250 | 267 | 17 |
| ALL | 489 | 361 | 378 | 17 |

link_source:

| link_source | control | treated |
|---|---|---|
| (unlinked) | 104 | 7 |
| cusip_header | 25 | 7 |
| cusip_ncusip | 242 | 104 |

Tie-break usage: {'priusa': 17, 'shrcd': 0, 'namedt': 0} (priusa resolves the dual-class pairs; the shrcd and namedt rules are reported if they ever fire).

## Every unlinked event, by reason

| reason | control | treated | All |
|---|---|---|---|
| CRSP name at breach_date does not match the breached organization; parent relationship unverified | 2 | 6 | 8 |
| no US common issue | 3 | 0 | 3 |
| no gvkey | 46 | 0 | 46 |
| no names row valid on breach_date | 48 | 1 | 49 |
| shrcd not in {10,11} ([12]) | 3 | 0 | 3 |
| shrcd not in {10,11} ([18]) | 2 | 0 | 2 |
| All | 104 | 7 | 111 |

## Identity gate (header links only)

| outcome | treated | control | total |
|---|---|---|---|
| accepted | 7 | 25 | 32 |
| excluded | 6 | 2 | 8 |

### Every header accept, for audit of the normalisation

| final_cik | org_name | comnam | breach_date | permno |
|---|---|---|---|---|
| 18926 | CenturyLink | CENTURYLINK INC | 2013-12-27 | 60599.0 |
| 47217 | Hewlett-Packard Company | HEWLETT PACKARD CO | 2007-07-01 | 27828.0 |
| 68505 | Motorola, Inc. | MOTOROLA INC | 2009-01-01 | 22779.0 |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M RADIO INC | 2012-03-19 | 80924.0 |
| 908937 | Sirius XM Radio Inc. | SIRIUS X M HOLDINGS INC | 2016-02-01 | 80924.0 |
| 1051470 | Crown Castle | CROWN CASTLE INTERNATIONAL CORP | 2013-10-31 | 86339.0 |
| 1091667 | Charter Communications, Inc. | CHARTER COMMUNICATIONS INC | 2013-04-26 | 12308.0 |
| 1105705 | Time Warner Inc. | TIME WARNER INC NEW | 2006-12-01 | 77418.0 |

### Every gate exclusion

| final_cik | org_name | comnam | breach_date | permno_rejected |
|---|---|---|---|---|
| 1283699 | T-Mobile USA, Inc. | METROPCS COMMUNICATIONS INC | 2009-09-03 | 91937.0 |
| 1283699 | T-Mobile USA, Inc. | METROPCS COMMUNICATIONS INC | 2009-10-05 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2009-10-08 | 91937.0 |
| 1283699 | T-Mobile USA Inc. | METROPCS COMMUNICATIONS INC | 2011-10-21 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2012-05-08 | 91937.0 |
| 1283699 | T-Mobile | METROPCS COMMUNICATIONS INC | 2012-08-28 | 91937.0 |
| 1308161 | Fox Entertainment Group | NEWS CORP | 2009-04-09 | 90441.0 |
| 1308161 | Fox Entertainment Group Inc. | NEWS CORP | 2009-04-15 | 90441.0 |

## Report-only: ncusip links whose CRSP name matches neither org nor EDGAR

53 of 346 ncusip links. **None is excluded** — the CUSIP is authoritative here; a name mismatch means the name differs, not that the security is wrong.

| final_cik | org_name | comnam | permno | upstream_note | final_evidence |
|---|---|---|---|---|---|
| 18926 | Centurylink Communications | LUMEN TECHOLOGIES INC | 60599.0 | True | Gate1-G rescue: CenturyLink/Lumen parent (Form 499 relevant carrier) (ticker LUMN -> CIK 18926) |
| 33185 | TALX Corporation | EQUIFAX INC | 52476.0 | True | Gate2 CH-21: TALX filings end 2007 (SEC-verified); 2016 breaches under Equifax ownership; parent-map via EFX |
| 51143 | IBM | INTERNATIONAL BUSINESS MACHS COR | 12490.0 | False | Gate1-G rescue: acronym defeated exact match; documented acronym mapping (ticker IBM -> CIK 51143) |
| 731766 | Change Healthcare Inc. | UNITEDHEALTH GROUP INC | 92655.0 | True | Gate1-C: UnitedHealth parent post-10/2022 acquisition; legacy GEHC was fuzzy error |
| 732717 | AT&T | A T & T INC | 66093.0 | False | Gate1-A: active registrant; 5907 is pre-2005 AT&T Corp (ticker T -> CIK 732717) |
| 789019 | Nuance Communications, Inc. | MICROSOFT CORP | 10107.0 | True | Gate1-B: Microsoft subsidiary, parent-mapped |
| 790070 | EMC Corporation | E M C CORP MA | 10147.0 | False | EDGAR name: EMC CORP |
| 1105705 | TimeWarner | TIME WARNER INC NEW | 77418.0 | False | Gate1-B: TWX registrant 2009-6/2018 |
| 1166691 | NBC Sports Group | COMCAST CORP NEW | 89525.0 | False | Gate1-E: identity=Comcast equity; treatment classification independent (clause rules at Stage 4) |
| 1283699 | Sprint | T MOBILE U S INC | 91937.0 | True | Gate1-F: TMUS post-merger |
| 1512673 | Block and Company, Inc. | SQUARE INC | 15826.0 | False | SEC EDGAR: Block Inc. (formerly Square Inc.) CIK 1512673 verified. Name changed Dec 2021 | EDGAR-confirmed |
| 1652044 | Google Inc. | ALPHABET INC | 90319.0 | False | Gate1-B: Alphabet Inc (ticker GOOGL) |
| 1669779 | CWGS Group | CAMPING WORLD HOLDINGS INC | 16437.0 | False | Gate1-G rescue: Camping World Holdings (EDGAR-verified: CWGS Holding LLC 1683140 files nothing; CWH is reporting entity) |

Of these, **19** carry an upstream documented parent/successor relationship in `final_evidence` (the name differs because the v3 chain already re-parented the event, and says so). The remaining **34** have no such note and go to `stage3_candidates.csv` as `ncusip_name_mismatch` — the link stands, but the identity is unexplained.

## Agreement with v3

| group | v3 linked | both | same permno | different |
|---|---|---|---|---|
| treated | 111 | 111 | 111 | 0 |
| control | 250 | 225 | 221 | 4 |

### Every disagreement (4)

| final_cik | org_name | breach_date | v3_permno | permno | comnam | link_source |
|---|---|---|---|---|---|---|
| 1652044 | Google Inc. | 2016-03-29 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google Inc. | 2016-05-06 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google Inc. | 2016-08-10 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |
| 1652044 | Google, Inc. | 2017-06-29 | 14542.0 | 90319.0 | ALPHABET INC | cusip_ncusip |

- v3 linked, v4 not: **25** (treated 0, control 25)
- v4 linked, v3 not: **42** (treated 0, control 42)

| reason | events |
|---|---|
| no names row valid on breach_date | 15 |
| no gvkey | 6 |
| shrcd not in {10,11} ([12]) | 2 |
| shrcd not in {10,11} ([18]) | 2 |

## CIKs with no gvkey, classified

| type | CIKs |
|---|---|
| b_successor_cik | 16 |
| a_subsidiary | 13 |
| d_other | 4 |
| c_no_compustat | 3 |

| final_cik | org | grp | events | candidate_type | candidate | confidence | shared_tokens |
|---|---|---|---|---|---|---|---|
| 14745 | Brown, Lisle/Cummings, Inc. | control | 1 | b_successor_cik | BROWN FORMAN CORP (gvkey 2435, cik 14693) | unverified | BROWN |
| 58696 | Lennar Corporation | control | 1 | b_successor_cik | LENNAR CORP (gvkey 6669, cik 920760) | unverified | LENNAR |
| 72945 | Northrop Grumman Systems Corporation | control | 1 | a_subsidiary | Northrop Grumman Corporation |  |  |
| 108772 | Xerox Corporation | control | 1 | a_subsidiary | Xerox Holdings Corporation |  |  |
| 353394 | Leidos, Inc. | control | 1 | a_subsidiary | Leidos Holdings, Inc. |  |  |
| 813828 | Paramount | control | 2 | c_no_compustat |  |  |  |
| 826083 | Dell Inc. | control | 1 | b_successor_cik | DELL TECHNOLOGIES INC (gvkey 14489, cik 1571996) | unverified | DELL |
| 912752 | Sinclair Broadcast Group, Inc. | control | 3 | b_successor_cik | SINCLAIR INC (gvkey 60800, cik 1971213) | unverified | SINCLAIR |
| 926480 | The Walt Disney Company | control | 1 | c_no_compustat |  |  |  |
| 1000564 | Communications & Power Industries LLC | control | 1 | b_successor_cik | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | unverified | INDUSTRIES |
| 1091411 | Sony Corporation of America | control | 1 | a_subsidiary | Sony Group Corporation |  |  |
| 1137785 | Seagate US LLC | control | 2 | a_subsidiary | Seagate Technology Holdings plc |  |  |
| 1145813 | Fox Group | control | 1 | d_other |  |  |  |
| 1168812 | HBP, Inc. | control | 1 | d_other |  |  |  |
| 1205274 | Herbalife International of America, Inc. | control | 1 | a_subsidiary | Herbalife Ltd. |  |  |
| 1260451 | Vulcan Industries | control | 1 | b_successor_cik | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | unverified | INDUSTRIES |
| 1283246 | International Paper Company | control | 1 | b_successor_cik | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | unverified | INTERNATIONAL |
| 1288776 | Google, Inc. | control | 1 | c_no_compustat |  |  |  |
| 1387793 | T. Rowe Price Retirement Plan Services, Inc. | control | 2 | a_subsidiary | T. Rowe Price Group, Inc. |  |  |
| 1396897 | NCO Financial Systems, Inc. | control | 1 | b_successor_cik | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | unverified | SYSTEMS |
| 1431473 | Uber | control | 1 | b_successor_cik | UBER TECHNOLOGIES INC (gvkey 35077, cik 1543151) | unverified | UBER |
| 1457738 | iHeartMedia + Entertainment, Inc. | control | 2 | a_subsidiary | iHeartMedia, Inc. |  |  |
| 1497060 | Capital Integration Systems LLC | control | 1 | b_successor_cik | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | unverified | SYSTEMS |
| 1501362 | J.B. Hunt Transport, Inc. | control | 2 | a_subsidiary | J.B. Hunt Transport Services, Inc. |  |  |
| 1516658 | Gates Corporation | control | 2 | a_subsidiary | Gates Industrial Corporation plc |  |  |
| 1558044 | Professional Compounding Centers of America, Inc. | control | 1 | d_other |  |  |  |
| 1560142 | EatStreet | control | 1 | d_other |  |  |  |
| 1567336 | Mediant Communications Inc. | control | 1 | b_successor_cik | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | unverified | COMMUNICATIONS |
| 1570434 | Prime Communications | control | 1 | b_successor_cik | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | unverified | COMMUNICATIONS |
| 1673769 | IMA Financial Group, Inc. | control | 1 | b_successor_cik | COREBRIDGE FINANCIAL INC (gvkey 41084, cik 1889539) | unverified | FINANCIAL |
| 1691249 | The iRemedy Healthcare Companies, Inc. | control | 1 | b_successor_cik | NEXTGEN HEALTHCARE INC (gvkey 8858, cik 708818) | unverified | HEALTHCARE |
| 1808065 | Aon Corporation PLC | control | 2 | b_successor_cik | AON PLC (gvkey 3221, cik 315293) | unverified | AON |
| 1826210 | KeraLink International | control | 1 | b_successor_cik | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | unverified | INTERNATIONAL |
| 1834695 | Volkswagen Group of America, Inc. | control | 1 | a_subsidiary | Volkswagen AG |  |  |
| 1870564 | Activision Publishing, Inc. | control | 2 | a_subsidiary | Activision Blizzard, Inc. |  |  |
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
| 1051470 | Crown Castle | CROWN CASTLE INTERNATIONAL CORP | CASTLE|CROWN | org | False |
| 1091667 | Charter Communications, Inc. | CHARTER COMMUNICATIONS INC | CHARTER|COMMUNICATIONS | org | False |
| 1105705 | Time Warner Inc. | TIME WARNER INC NEW | TIME|WARNER | org | False |

### b_successor_cik nominations

| final_cik | org | candidate | shared_tokens | generic_only |
|---|---|---|---|---|
| 14745 | Brown, Lisle/Cummings, Inc. | BROWN FORMAN CORP (gvkey 2435, cik 14693) | BROWN | False |
| 58696 | Lennar Corporation | LENNAR CORP (gvkey 6669, cik 920760) | LENNAR | False |
| 826083 | Dell Inc. | DELL TECHNOLOGIES INC (gvkey 14489, cik 1571996) | DELL | False |
| 912752 | Sinclair Broadcast Group, Inc. | SINCLAIR INC (gvkey 60800, cik 1971213) | SINCLAIR | False |
| 1000564 | Communications & Power Industries LLC | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | INDUSTRIES | True |
| 1260451 | Vulcan Industries | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | INDUSTRIES | True |
| 1283246 | International Paper Company | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | INTERNATIONAL | True |
| 1396897 | NCO Financial Systems, Inc. | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | SYSTEMS | True |
| 1431473 | Uber | UBER TECHNOLOGIES INC (gvkey 35077, cik 1543151) | UBER | False |
| 1497060 | Capital Integration Systems LLC | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | SYSTEMS | True |
| 1567336 | Mediant Communications Inc. | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | COMMUNICATIONS | True |
| 1570434 | Prime Communications | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | COMMUNICATIONS | True |
| 1673769 | IMA Financial Group, Inc. | COREBRIDGE FINANCIAL INC (gvkey 41084, cik 1889539) | FINANCIAL | True |
| 1691249 | The iRemedy Healthcare Companies, Inc. | NEXTGEN HEALTHCARE INC (gvkey 8858, cik 708818) | HEALTHCARE | True |
| 1808065 | Aon Corporation PLC | AON PLC (gvkey 3221, cik 315293) | AON | False |
| 1826210 | KeraLink International | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | INTERNATIONAL | True |

### FLAGGED: matched on generic tokens only — 0 header accept(s), 10 successor nomination(s)

No header accept rests on generic tokens alone.

| final_cik | org | candidate | shared_tokens | generic_only |
|---|---|---|---|---|
| 1000564 | Communications & Power Industries LLC | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | INDUSTRIES | True |
| 1260451 | Vulcan Industries | ABM INDUSTRIES INC (gvkey 1410, cik 771497) | INDUSTRIES | True |
| 1283246 | International Paper Company | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | INTERNATIONAL | True |
| 1396897 | NCO Financial Systems, Inc. | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | SYSTEMS | True |
| 1497060 | Capital Integration Systems LLC | CISCO SYSTEMS INC (gvkey 20779, cik 858877) | SYSTEMS | True |
| 1567336 | Mediant Communications Inc. | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | COMMUNICATIONS | True |
| 1570434 | Prime Communications | VERIZON COMMUNICATIONS INC (gvkey 2136, cik 732712) | COMMUNICATIONS | True |
| 1673769 | IMA Financial Group, Inc. | COREBRIDGE FINANCIAL INC (gvkey 41084, cik 1889539) | FINANCIAL | True |
| 1691249 | The iRemedy Healthcare Companies, Inc. | NEXTGEN HEALTHCARE INC (gvkey 8858, cik 708818) | HEALTHCARE | True |
| 1826210 | KeraLink International | HONEYWELL INTERNATIONAL INC (gvkey 1300, cik 773840) | INTERNATIONAL | True |

## Unmatched tpci=0 / USA CUSIPs

71 US common issues have no CRSP names row.

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
| 23812 | REGENERON PHARMACEUTICALS | 75886F93 | 1 | A |
| 112168 | REPUBLIC SERVICES INC | 76075993 | 1 | I |
| 32382 | ROKU INC | 77543R01 | 1 | A |
| 60800 | SINCLAIR INC | 82922670 | 1 | A |
| 30091 | SNAP INC | 83304A01 | 1 | A |
| 30091 | SNAP INC | 83304A02 | 1 | A |
| 339965 | SNOWFLAKE INC | 83399I93 | 1 | I |
| 9818 | SONY GROUP CORPORATION | J7637910 | 19 | A |
| 10984 | SPRINT CORP | 85206198 | 1 | I |
| 10984 | SPRINT CORP | 85206199 | 1 | I |
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

71 rows written to `outputs/rebuild_v4/stage3_candidates.csv`.

| type | rows |
|---|---|
| ncusip_name_mismatch | 34 |
| b_successor_cik | 16 |
| a_subsidiary | 13 |
| gate_exclusion | 8 |

