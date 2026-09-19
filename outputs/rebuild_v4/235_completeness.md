# REBUILD V4 - Item 5.02 fetch completeness (scripts/235)

## Expected vs on disk
in-scope events with a resolved outcome_cik : 412
distinct outcome CIKs                       : 122
event x accession pairs expected            : 3276
distinct accessions expected                : 1517
of those, on disk                           : 1512

## Shortfall by CIK (a shortfall is a silent 'no departure')
 outcome_cik       org_name  expected  on_disk  missing
     1137789 Seagate US LLC        21       16        5

Missing accessions:
 outcome_cik       org_name            accession filing_date       primary_doc
     1137789 Seagate US LLC 0001104659-15-033202  2015-05-01 a15-10570_18k.htm
     1137789 Seagate US LLC 0001104659-14-073609  2014-10-24 a14-22946_18k.htm
     1137789 Seagate US LLC 0001104659-14-066107  2014-09-12 a14-20892_28k.htm
     1137789 Seagate US LLC 0001104659-14-052995  2014-07-23 a14-17631_18k.htm
     1137789 Seagate US LLC 0001104659-14-029197  2014-04-22 a14-10680_18k.htm

## Outcome CIKs holding zero documents
 outcome_cik                 org_name  events  treated  index_lists_502_in_window  submissions_cached                                   verdict
      860731 Tyler Technologies, Inc.       1        0                          0                   1 genuine - index lists zero 5.02 in-window

fetch failures: 0; genuine zeros: 1

## Scope files for scripts/220 and 224
b_scope_filings.csv    : 1517 filings
b_event_filing_pairs.csv: 3276 event x filing pairs
b_scope_events.csv     : 412 events
WARNING: 5 listed filing(s) are NOT on disk. 220 would classify a short document set. Re-run 231 --documents.

written 235_completeness.csv, 235_completeness_by_cik.csv, and the b_* scope files
