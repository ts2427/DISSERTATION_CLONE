# GATE 1 — Entity Verification Sign-off Package

==========================================================================================
REBUILD STAGES 1-2: UNIVERSE + ENTITY RESOLUTION
==========================================================================================

Stage 1: universe = 1054 records, 452 unique organizations. PASS

Stage 2: building EDGAR name index...
  EDGAR index: 1,020,265 normalized names, 978,691 CIKs
  Reasoning pass: 451 entries; 391 unworked placeholders EXCLUDED from resolution (echo fuzzy CIKs); 60 substantive entries retained

  Resolving organizations (exact-and-abstain -> reasoning -> adjudicated)...

  Grade distribution (orgs / records):
    ADJUDICATED               2 orgs       3 records
    AMBIGUOUS                64 orgs     194 records
    EXCLUDED-UNRESOLVED     213 orgs     323 records
    REVIEW                    4 orgs       7 records
    VERIFIED                163 orgs     495 records
    VERIFIED-REASONING        6 orgs      32 records

  Legacy-vs-resolved (orgs):
    legacy_vs_resolved
    NEWLY-EXCLUDED    278
    SAME              103
    CORRECTED          71

  Suspect-CIK sinks (legacy records -> fate under fresh resolution):
    CIK 713676: 23 legacy orgs / 50 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 927628: 14 legacy orgs / 16 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 1324404: 36 legacy orgs / 50 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 19617: 6 legacy orgs / 6 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 1034054: 25 legacy orgs / 58 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 1932393: 10 legacy orgs / 15 records; retained by fresh resolution: 0 orgs (0 records)
    CIK 1755336: 8 legacy orgs / 18 records; retained by fresh resolution: 0 orgs (0 records)

  Record-level output: 1054 records, all graded. Retained for downstream (non-excluded): 731

## Items requiring your eyes (everything else is deterministic)

### REVIEW (4 orgs, 7 records)

- **Boost Mobile** (1 rec) -> nan | Single breach 2019-03-14 (Sprint era). Options: (a) successor-equity convention -> 1283699 (consistent with Sprint rows); (b) Sprint-era equity CIK; (c) exclude as brand without own listing. Legacy canonical carried 1283699.
- **NBC Sports Group** (3 rec) -> 1166691.0 | SEC EDGAR (HIGH): NBC/Comcast subsidiary | NOT independently confirmed
- **Verizon Corporate Services Group Inc.** (1 rec) -> 732712.0 | SEC EDGAR (HIGH): Verizon operating subsidiary | NOT independently confirmed
- **Verizon Media** (2 rec) -> 732712.0 | SEC EDGAR (HIGH): Verizon Media (acquired Yahoo/AOL assets) | NOT independently confirmed

### AMBIGUOUS (64 orgs, 194 records)

- **AT&T** (13 rec) | Candidates: 5907 (AMERICAN TELEPHONE & TELEGRAPH CO) | 732717 (AT&T INC., T) || legacy ticker: T
- **AT&T Inc** (1 rec) | Candidates: 5907 (AMERICAN TELEPHONE & TELEGRAPH CO) | 732717 (AT&T INC., T) || legacy ticker: T
- **AT&T Inc.** (10 rec) | Candidates: 5907 (AMERICAN TELEPHONE & TELEGRAPH CO) | 732717 (AT&T INC., T) || legacy ticker: T
- **AT&T, Inc.** (1 rec) | Candidates: 5907 (AMERICAN TELEPHONE & TELEGRAPH CO) | 732717 (AT&T INC., T) || legacy ticker: T
- **Adobe Systems Incorporated** (3 rec) | Candidates: 714164 (ADOBE SYSTEMS LTD) | 796343 (ADOBE INC., ADBE) || legacy ticker: ADBE
- **AeroGrow International** (1 rec) | Candidates: 1272660 (AEROGROW  INTERNATIONAL INC) | 1316644 (AEROGROW INTERNATIONAL, INC.) | 1334121 (AEROGROW INTERNATIONAL INC) || legacy ticker: AIG
- **AeroGrow International, Inc.** (1 rec) | Candidates: 1272660 (AEROGROW  INTERNATIONAL INC) | 1316644 (AEROGROW INTERNATIONAL, INC.) | 1334121 (AEROGROW INTERNATIONAL INC) || legacy ticker: AIG
- **Aladdin Capital** (1 rec) | Candidates: 1059126 (ALADDIN CAPITAL CORP) | 1102487 (ALADDIN CAPITAL LLC) || legacy ticker: COF
- **American Electric Power** (2 rec) | Candidates: 4904 (AMERICAN ELECTRIC POWER CO INC, AEP) | 1218721 (AMERICAN ELECTRIC POWER CO) || legacy ticker: AEP
- **Aon Corporation** (1 rec) | Candidates: 315293 (AON CORP, AON) | 1556748 (AON CORP) || legacy ticker: AON
- **Aon Corporation PLC** (1 rec) | Candidates: 315293 (AON CORP, AON) | 1808065 (AON PLC) || legacy ticker: AON
- **Aon PLC** (1 rec) | Candidates: 315293 (AON CORP, AON) | 1808065 (AON PLC) || legacy ticker: AON
- **Audacy, Inc** (1 rec) | Candidates: 1067837 (AUDACY, INC.) | 1650982 (AUDACY CORP) || legacy ticker: AUDAQ
- **Caesars Entertainment, Inc.** (2 rec) | Candidates: 858339 (CAESARS ENTERTAINMENT CORP) | 1070794 (CAESARS ENTERTAINMENT INC) | 1590895 (CAESARS ENTERTAINMENT, INC., CZR) || legacy ticker: CZR
- **Carnival Corporation** (2 rec) | Candidates: 815097 (CARNIVAL CORP, CCL) | 1584022 (CARNIVAL, INC.) || legacy ticker: CCL
- **Change Healthcare Inc.** (1 rec) | Candidates: 1414847 (CHANGE HEALTHCARE CORP) | 1756497 (CHANGE HEALTHCARE INC.) || legacy ticker: GEHC
- **Charter Communications** (2 rec) | Candidates: 19392 (CHARTER COMMUNICATIONS INC) | 1686835 (CHARTER COMMUNICATIONS, LLC) || legacy ticker: CHTR
- **Charter Communications, Inc.** (5 rec) | Candidates: 19392 (CHARTER COMMUNICATIONS INC) | 1686835 (CHARTER COMMUNICATIONS, LLC) || legacy ticker: CHTR
- **Comcast** (4 rec) | Candidates: 22301 (COMCAST CORP) | 1166691 (AT&T COMCAST CORP, CMCSA) || legacy ticker: CMCSA
- **CyrusOne, Inc.** (1 rec) | Candidates: 1553023 (CYRUSONE HOLDCO LLC) | 1575809 (CYRUSONE LLC) | 1575810 (CYRUSONE LP) || legacy ticker: CONE
- **DISH Network Corporation** (1 rec) | Candidates: 920436 (DISH NETWORK LLC) | 1001082 (DISH NETWORK CORP) || legacy ticker: DISH
- **DISH Network, LLC** (6 rec) | Candidates: 920436 (DISH NETWORK LLC) | 1001082 (DISH NETWORK CORP) || legacy ticker: DISH
- **Deluxe Corporation** (1 rec) | Candidates: 27996 (DELUXE CORP, DLX) | 1200788 (DELUXE CORP INC) || legacy ticker: IEX
- **Duke Energy** (1 rec) | Candidates: 30371 (DUKE ENERGY CAROLINAS, LLC) | 1326160 (DEER HOLDING CORP., DUK) || legacy ticker: DUK
- **Duke Energy Corporation** (2 rec) | Candidates: 30371 (DUKE ENERGY CAROLINAS, LLC) | 1326160 (DEER HOLDING CORP., DUK) || legacy ticker: DUK
- **Eagle Capital Management, LLC** (1 rec) | Candidates: 945631 (EAGLE CAPITAL MANAGEMENT LLC) | 1600746 (EAGLE CAPITAL MANAGEMENT, LLC) || legacy ticker: COF
- **FedEx Ground Package System, Inc.** (1 rec) | Candidates: 1139209 (FEDEX GROUND PACKAGE SYSTEM INC) | 1139210 (FEDEX GROUND PACKAGE SYSTEM LTD) || legacy ticker: FDX
- **Fidelity National Information Services, Inc.** (21 rec) | Candidates: 1136893 (CERTEGY INC, FIS) | 1291080 (FIDELITY NATIONAL INFORMATION SERVICES, ) || legacy ticker: FIS
- **First American Financial Corporation** (2 rec) | Candidates: 36047 (CORELOGIC, INC.) | 1472787 (FIRST AMERICAN FINANCIAL CORP, FAF) || legacy ticker: PNC
- **Fox Entertainment Group** (1 rec) | Candidates: 1068002 (FOX ENTERTAINMENT GROUP INC) | 1321244 (FOX ENTERTAINMENT GROUP, INC.) || legacy ticker: FOXA
- **Fox Entertainment Group Inc.** (1 rec) | Candidates: 1068002 (FOX ENTERTAINMENT GROUP INC) | 1321244 (FOX ENTERTAINMENT GROUP, INC.) || legacy ticker: FOXA
- **Freeport-McMoRan Inc.** (1 rec) | Candidates: 351116 (FREEPORT MCMORAN INC) | 831259 (FREEPORT MCMORAN COPPER & GOLD INC, FCX) || legacy ticker: FCX
- **Google** (1 rec) | Candidates: 1136101 (GOOGLE INC) | 1288776 (GOOGLE INC.) | 1302837 (GOOGLE INC) | 1824723 (GOOGLE LLC) || legacy ticker: GOOG
- **Google Inc.** (5 rec) | Candidates: 1136101 (GOOGLE INC) | 1288776 (GOOGLE INC.) | 1302837 (GOOGLE INC) | 1824723 (GOOGLE LLC) || legacy ticker: GOOG
- **Google, Inc.** (2 rec) | Candidates: 1136101 (GOOGLE INC) | 1288776 (GOOGLE INC.) | 1302837 (GOOGLE INC) | 1824723 (GOOGLE LLC) || legacy ticker: GOOG
- **LPL Financial LLC** (1 rec) | Candidates: 80386 (LINSCO PRIVATE LEDGER CORP              ) | 1403438 (LINSCO/PRIVATE LEDGER CORP.) || legacy ticker: PNC
- **MSX International Inc.** (3 rec) | Candidates: 1059274 (MSX INTERNATIONAL INC) | 1264091 (MSX INTERNATIONAL LTD) || legacy ticker: AIG
- **Nuance Communications Inc** (1 rec) | Candidates: 1002517 (NUANCE COMMUNICATIONS, INC.) | 1102556 (NUANCE COMMUNICATIONS) || legacy ticker: SBAC
- **Nuance Communications, Inc.** (5 rec) | Candidates: 1002517 (NUANCE COMMUNICATIONS, INC.) | 1102556 (NUANCE COMMUNICATIONS) || legacy ticker: SBAC
- **Oracle Corporation** (2 rec) | Candidates: 727632 (ORACLE CORP) | 1341439 (ORACLE CORP, ORCL) || legacy ticker: ORCL
- **Roku Inc** (1 rec) | Candidates: 1350999 (ROKU LLC) | 1428439 (ROKU INC, ROKU) || legacy ticker: ROKU
- **Roku Inc.** (1 rec) | Candidates: 1350999 (ROKU LLC) | 1428439 (ROKU INC, ROKU) || legacy ticker: ROKU
- **Roku, Inc.** (2 rec) | Candidates: 1350999 (ROKU LLC) | 1428439 (ROKU INC, ROKU) || legacy ticker: ROKU
- **Seagate Technology LLC** (1 rec) | Candidates: 354952 (SEAGATE TECHNOLOGY INC) | 1137781 (SEAGATE TECHNOLOGY LLC) | 1137789 (SEAGATE TECHNOLOGY, STX) | 1554935 (SEAGATE TECHNOLOGY) || legacy ticker: STX
- **Sirius XM Radio Inc** (3 rec) | Candidates: 908937 (CD RADIO INC, SIRI) | 1592709 (SIRIUS XM RADIO INC.) || legacy ticker: SIRI
- **Sirius XM Radio Inc.** (12 rec) | Candidates: 908937 (CD RADIO INC, SIRI) | 1592709 (SIRIUS XM RADIO INC.) || legacy ticker: SIRI
- **Sirius XM Radio, Inc.** (3 rec) | Candidates: 908937 (CD RADIO INC, SIRI) | 1592709 (SIRIUS XM RADIO INC.) || legacy ticker: SIRI
- **Snap Inc.** (1 rec) | Candidates: 1282388 (SNAP LP) | 1564408 (SNAP INC, SNAP) | 1652940 (CAREERSCORE, INC.) || legacy ticker: SNAP
- **T-Mobile USA** (10 rec) | Candidates: 1097609 (T MOBILE USA) | 1578078 (T-MOBILE USA, INC.) || legacy ticker: TMUS
- **T-Mobile USA Inc** (2 rec) | Candidates: 1097609 (T MOBILE USA) | 1578078 (T-MOBILE USA, INC.) || legacy ticker: TMUS
- **T-Mobile USA Inc.** (4 rec) | Candidates: 1097609 (T MOBILE USA) | 1578078 (T-MOBILE USA, INC.) || legacy ticker: TMUS
- **T-Mobile USA, Inc.** (19 rec) | Candidates: 1097609 (T MOBILE USA) | 1578078 (T-MOBILE USA, INC.) || legacy ticker: TMUS
- **T-Mobile, USA** (1 rec) | Candidates: 1097609 (T MOBILE USA) | 1578078 (T-MOBILE USA, INC.) || legacy ticker: TMUS
- **The J.M. Smucker Company** (1 rec) | Candidates: 91419 (J M SMUCKER CO, SJM) | 1532058 (J.M. SMUCKER LLC) | 1553211 (J.M. SMUCKER CO) || legacy ticker: SJM
- **The Walt Disney Company** (1 rec) | Candidates: 926480 (WALT DISNEY CO) | 1001039 (DC HOLDCO INC) | 1744489 (TWDC HOLDCO 613 CORP, DIS) || legacy ticker: DIS
- **Time Warner Inc.** (4 rec) | Candidates: 736157 (TIME WARNER COMPANIES INC) | 1021387 (HISTORIC TW INC) | 1105705 (AOL TIME WARNER INC) || legacy ticker: WBD
- **W.W. Grainger Inc.** (1 rec) | Candidates: 277135 (GRAINGER W W INC, GWW) | 1170725 (W W GRAINGER INC) || legacy ticker: GWW
- **W.W. Grainger, Inc.** (2 rec) | Candidates: 277135 (GRAINGER W W INC, GWW) | 1170725 (W W GRAINGER INC) || legacy ticker: GWW
- **Warner Music Group** (5 rec) | Candidates: 1309952 (WARNER MUSIC GROUP INC) | 1319161 (WARNER MUSIC GROUP CORP., WMG) || legacy ticker: WBD
- **Warner Music Group Corp** (1 rec) | Candidates: 1309952 (WARNER MUSIC GROUP INC) | 1319161 (WARNER MUSIC GROUP CORP., WMG) || legacy ticker: WBD
- **Yahoo** (1 rec) | Candidates: 1011006 (ALTABA INC.) | 1426140 (YAHOO INC) | 1962736 (YAHOO, INC.) || legacy ticker: YHOO
- **Yahoo Inc.** (2 rec) | Candidates: 1011006 (ALTABA INC.) | 1426140 (YAHOO INC) | 1962736 (YAHOO, INC.) || legacy ticker: YHOO
- **Yahoo! Inc.** (2 rec) | Candidates: 1011006 (ALTABA INC.) | 1426140 (YAHOO INC) | 1962736 (YAHOO, INC.) || legacy ticker: YHOO
- **Yahoo, Inc.** (1 rec) | Candidates: 1011006 (ALTABA INC.) | 1426140 (YAHOO INC) | 1962736 (YAHOO, INC.) || legacy ticker: YHOO

### ADJUDICATED mappings for confirmation

- **Cricket Wireless LLC** -> 732717.0 | AT&T Inc. — Cricket Communications FRN 0004321139; LLC variant; 7/28 adjudication
- **Sprint Business** -> 1283699.0 | T-Mobile US, Inc. — successor-equity convention for Sprint entities (merger 4/2020); FLAGGED for Gate 1: pre-2020 events arguably belong to Sprint Corp equity

### GATE 1 DECISIONS (options presented, no default taken)

- **Boost Mobile**: Single breach 2019-03-14 (Sprint era). Options: (a) successor-equity convention -> 1283699 (consistent with Sprint rows); (b) Sprint-era equity CIK; (c) exclude as brand without own listing. Legacy canonical carried 1283699.

### Exclusion scan (top 40 EXCLUDED-UNRESOLVED by record count)

Scan for recognizable PUBLIC firms only — everything you do not flag is excluded per the FISC precedent (no valid public-market observation).

- Financial Business and Consumer Solutions, Inc. (15 rec, type=BSO, legacy_cik=713676)
- Newcourse Communications, Inc. (11 rec, type=BSO, legacy_cik=1034054)
- Financial Institution Service Corporation (9 rec, type=BSO, legacy_cik=713676)
- USA Waste-Management Resources, LLC (6 rec, type=BSO, legacy_cik=823768)
- GoDaddy.com, LLC (5 rec, type=BSO, legacy_cik=1609711)
- Perry Johnson & Associates, Inc. (5 rec, type=BSO, legacy_cik=200406)
- GC Services (4 rec, type=BSO, legacy_cik=1136893)
- Gallagher NAC (4 rec, type=BSO, legacy_cik=354190)
- ASAP Semiconductor LLC (3 rec, type=BSO, legacy_cik=1097864)
- Brown Paindiris & Scott, LLP (3 rec, type=BSO, legacy_cik=79282)
- Burrelles Information Services, LLC (3 rec, type=BSO, legacy_cik=1136893)
- CWGS Group (3 rec, type=BSO, legacy_cik=831001)
- Orbus Visual Communications, LLC (3 rec, type=BSO, legacy_cik=1034054)
- Paramount (3 rec, type=BSO, legacy_cik=2041610)
- The EstÃ©e Lauder Companies Inc. (3 rec, type=BSO, legacy_cik=1001250)
- Worthen Industries, Inc. (3 rec, type=BSO, legacy_cik=1324404)
- A&A Services (2 rec, type=BSO, legacy_cik=1136893)
- ADF International, Inc. (2 rec, type=BSO, legacy_cik=5272)
- ASIS International (2 rec, type=BSO, legacy_cik=5272)
- ATT-Breach Notification (2 rec, type=BSO, legacy_cik=732717)
- Allied-Locke Industries, Inc. (2 rec, type=BSO, legacy_cik=1324404)
- Bray International, Inc. (2 rec, type=BSO, legacy_cik=5272)
- CLAS Information Services (2 rec, type=BSO, legacy_cik=1136893)
- Capital Lumber Company (2 rec, type=BSO, legacy_cik=927628)
- CenturyLink Communications (2 rec, type=BSO, legacy_cik=18926)
- Derby Industries, LLC (2 rec, type=BSO, legacy_cik=1324404)
- EBSCO Industries, Inc. (2 rec, type=BSO, legacy_cik=1324404)
- Ensinger Industries, Inc. (2 rec, type=BSO, legacy_cik=1324404)
- Festo Corporation (2 rec, type=BSO, legacy_cik=874761)
- Financial Risk Mitigation, Inc. (2 rec, type=BSO, legacy_cik=713676)
- Flutter International Inc. (2 rec, type=BSO, legacy_cik=5272)
- Franklin International (2 rec, type=BSO, legacy_cik=5272)
- GoDaddy.com (2 rec, type=BSO, legacy_cik=1609711)
- GoDaddy.com LLC (2 rec, type=BSO, legacy_cik=1609711)
- Healthcare Fiscal Management, Inc. (2 rec, type=BSO, legacy_cik=1932393)
- Huntwood Industries (2 rec, type=BSO, legacy_cik=1324404)
- IBM (2 rec, type=BSO, legacy_cik=51143)
- Impact Mobile Home Communities (2 rec, type=BSO, legacy_cik=1283699)
- Jet Industries, Inc. (2 rec, type=BSO, legacy_cik=1324404)
- Johnson Oâ€™Hare Company, Inc. (2 rec, type=BSO, legacy_cik=200406)
