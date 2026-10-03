# GATE 2 — Adjudication Sitting Package

==========================================================================================
REBUILD STAGE 3: DEDUPLICATION
==========================================================================================

Input: 758 retained records, 249 orgs, 165 CIKs
(a) Normalized-name+date consistency: PASS (no name+date pair spans CIKs)
(b) CIK+date collapse: 758 records -> 524 firm-day events (234 collapsed; 99 events carry multi-filing notes)
(c) Adjacency chains: 32 chains — 28 propose COLLAPSE (30 events would merge away), 4 FLAGGED for the sitting

## One unsigned entity resolution (2 records)

- **Fox Entertainment Group / Fox Entertainment Group Inc.** (2009-04-09, 2009-04-15): in 2009 Fox Entertainment Group was a wholly-owned News Corporation subsidiary (public minority bought out 2005; legacy ticker FOXA is anachronistic — Fox Corp exists only from 2019). PROPOSED: parent-map to News Corporation (CIK 1308161) with subsidiary rationale (FedEx Ground class), or exclude. Two records ride on the call.

## FLAGGED chains (your judgment needed)

### CH-06 — Verizon Communications Inc. (CIK 732712, 2 events)
- Dates: 2024-02-06, 2024-02-09 | Types: HACK+INSD
- Variants: Verizon Communications Inc. || Verizon Communications Inc.
- First detail: On February 6, 2024, the Massachusetts Office of Consumer Affairs and Business Regulation reported a data brea
- Rule: Breach types conflict within chain (['HACK', 'INSD']); public-record test applies.

### CH-09 — Intuit Inc (CIK 896878, 3 events)
- Dates: 2016-02-29, 2016-03-01, 2016-03-03 | Types: HACK+INSD
- Variants: Intuit Inc || Intuit Inc. || Intuit Inc
- First detail: The Indiana Office of the Attorney General reported a data breach involving Intuit Inc. on March 16, 2016. The
- Rule: Breach types conflict within chain (['HACK', 'INSD']); public-record test applies.

### CH-10 — Intuit, Inc. (CIK 896878, 3 events)
- Dates: 2016-03-07, 2016-03-08, 2016-03-09 | Types: HACK+INSD
- Variants: Intuit, Inc. || Intuit Inc || Intuit
- First detail: The New Hampshire Attorney General's Office reported on April 1, 2016, that Intuit Inc. experienced unauthoriz
- Rule: Breach types conflict within chain (['HACK', 'INSD']); public-record test applies.

### CH-27 — T-Mobile USA, Inc. (CIK 1283699, 2 events)
- Dates: 2009-10-05, 2009-10-08 | Types: HACK+PHYS
- Variants: T-Mobile USA, Inc. || T-Mobile
- First detail: On October 5, 2009, the Massachusetts Office of Consumer Affairs and Business Regulation reported a data breac
- Rule: Breach types conflict within chain (['HACK', 'PHYS']); public-record test applies.


## COLLAPSE proposals (confirm by exception)

- CH-01 Frontier Communications Parent, Inc. (CIK 20520): 2 events [2024-04-13, 2024-04-14] type=HACK
- CH-02 Frontier Communications Parent, Inc. (CIK 20520): 2 events [2024-06-10, 2024-06-12] type=HACK
- CH-03 Gray Television (CIK 43196): 3 events [2016-08-08, 2016-08-10, 2016-08-12] type=PORT
- CH-04 Sierra Pacific Industries (CIK 90143): 2 events [2022-06-10, 2022-06-11] type=HACK
- CH-05 Snap-on Incorporated (CIK 91440): 2 events [2022-03-01, 2022-03-03] type=HACK
- CH-07 AT&T Inc (CIK 732717): 2 events [2024-04-09, 2024-04-10] type=HACK
- CH-08 Intuit Inc. (CIK 896878): 2 events [2015-12-07, 2015-12-08] type=INSD
- CH-11 Intuit Inc. (CIK 896878): 2 events [2016-03-22, 2016-03-23] type=HACK
- CH-12 Intuit Inc (CIK 896878): 2 events [2016-03-29, 2016-04-01] type=HACK
- CH-13 Intuit (CIK 896878): 2 events [2016-04-29, 2016-05-02] type=HACK
- CH-14 Intuit (CIK 896878): 2 events [2017-01-27, 2017-01-30] type=HACK
- CH-15 Intuit Inc. (CIK 896878): 2 events [2017-02-28, 2017-03-02] type=HACK
- CH-16 Intuit, Inc. (CIK 896878): 2 events [2017-04-02, 2017-04-04] type=HACK
- CH-17 Intuit Inc (CIK 896878): 2 events [2017-04-17, 2017-04-19] type=HACK
- CH-18 Intuit, Inc. (CIK 896878): 2 events [2017-07-30, 2017-08-01] type=HACK
- CH-19 Intuit, Inc. (CIK 896878): 2 events [2019-01-29, 2019-01-30] type=HACK
- CH-20 Intuit, Inc. (CIK 896878): 2 events [2019-02-21, 2019-02-22] type=HACK
- CH-21 TALX Corporation (CIK 917524): 2 events [2016-01-01, 2016-01-04] type=HACK
- CH-22 DISH Network, LLC (CIK 1001082): 2 events [2023-02-22, 2023-02-23] type=HACK
- CH-23 Republic Services (CIK 1060391): 2 events [2013-08-10, 2013-08-11] type=PORT
- CH-24 Republic Services, Inc. (CIK 1060391): 2 events [2019-02-01, 2019-02-02] type=HACK
- CH-25 Fidelity National Information Services, Inc. (CIK 1136893): 3 events [2023-05-27, 2023-05-29, 2023-05-31] type=HACK
- CH-26 Fidelity National Information Services, Inc. (CIK 1136893): 2 events [2023-10-04, 2023-10-06] type=HACK
- CH-28 T-Mobile USA, Inc. (CIK 1283699): 2 events [2015-09-14, 2015-09-15] type=HACK
- CH-29 T-Mobile USA (CIK 1283699): 2 events [2021-08-17, 2021-08-18] type=HACK
- CH-30 GoDaddy.com LLC (CIK 1609711): 2 events [2019-10-16, 2019-10-19] type=HACK
- CH-31 IMA Financial Group, Inc. (CIK 1673769): 2 events [2022-10-18, 2022-10-19] type=HACK
- CH-32 Altice USA (CIK 1702780): 2 events [2024-02-29, 2024-03-01] type=HACK
