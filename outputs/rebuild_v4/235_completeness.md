# REBUILD V4 - Item 5.02 fetch completeness (scripts/235)

## Expected vs on disk
in-scope events with a resolved outcome_cik : 412
distinct outcome CIKs                       : 122
event x accession pairs expected            : 3276
distinct accessions expected                : 1517
of those, on disk                           : 1517

## Shortfall by CIK (a shortfall is a silent 'no departure')
NONE - every expected Item 5.02 filing is on disk.

## Outcome CIKs holding zero documents
 outcome_cik                 org_name  events  treated  index_lists_502_in_window  submissions_cached                                   verdict
      860731 Tyler Technologies, Inc.       1        0                          0                   1 genuine - index lists zero 5.02 in-window

fetch failures: 0; genuine zeros: 1

## Scope files for scripts/220 and 224
b_scope_filings.csv    : 1517 filings
b_event_filing_pairs.csv: 3276 event x filing pairs
b_scope_events.csv     : 412 events

written 235_completeness.csv, 235_completeness_by_cik.csv, and the b_* scope files
