# Stage 5 Report

==========================================================================================
REBUILD STAGE 5: MARKET OUTCOMES
==========================================================================================

Input: 489 events
  WRDS top-up names merged (Sprint S, CenturyLink CTL)
  WRDS top-up daily rows merged (scripts/159, and DISH permno 81696 from scripts/179), de-duplicated on (permno, date)
Resolving PERMNOs and computing outcomes...

CRSP coverage: 356/489 events with car_30d (361 with PERMNO)
Treated with CRSP data: 111 events / 13 parent CIKs
No PERMNO (die at CRSP, expected for private registrants): 128 events, 75 CIKs
  TREATED events without PERMNO, classified:
    Mediacom Communications Corporation | 2022-07-18 | CIK 1098659 | NO-EQUITY-AT-DATE (Mediacom private since 2011)
    T-Mobile USA, Inc. | 2009-09-03 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
    T-Mobile USA, Inc. | 2009-10-05 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
    T-Mobile | 2009-10-08 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
    T-Mobile USA Inc. | 2011-10-21 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
    T-Mobile | 2012-05-08 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
    T-Mobile | 2012-08-28 | CIK 1283699 | NO-EQUITY-AT-DATE (pre-2013 T-Mobile)
Stage 5 tripwire: events out 489, events with car_30d 356, treated with CRSP data 111
