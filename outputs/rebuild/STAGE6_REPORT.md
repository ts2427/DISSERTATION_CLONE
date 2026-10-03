# Stage 6 Report

==========================================================================================
REBUILD STAGE 6: COVARIATES AND ASSEMBLY
==========================================================================================

Input: 489 events
  Compustat top-up merged (Sprint, CenturyLink)
Compustat coverage: size 346, leverage 346, roa 346, op_margin 346 (of 489)
  delay_invalid: Sprint Nextel | breach 2012-08-01 | reported 2009-03-30 | delay -1220 -> missing
  delay_recoded: Apple Inc. | breach 2015-09-18 | reported 2015-09-16 | delay -2 -> 0
  delay_recoded: AT&T Inc. | breach 2024-04-14 | reported 2024-04-10 | delay -4 -> 0
Immediate disclosure: 160/487 known (32.9%; 2 missing)
Health events (derived): 24
Item 5.02 extraction (live EDGAR, cached)...
  40/162 CIKs...
  80/162 CIKs...
  120/162 CIKs...
  160/162 CIKs...
Item 5.02 base rates (all events): 30d 14.9%, 90d 38.4%, 180d 61.1%
Stage 6 tripwire: events 489, treated events 118, events with CRSP data 356, treated parent CIKs 14

CANONICAL_V3: 489 events | CRSP sample 356 | regression sample 340 (106 treated, 12 parent CIKs)
