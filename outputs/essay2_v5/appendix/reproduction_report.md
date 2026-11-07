# Reproduction report: recomputed classification/data tables vs tombstoned CSVs

Each recomputed table is compared cell by cell with the tombstoned CSV at the tombstone's printed precision.

| table | tombstone | rows new/old | cells matching | differing |
|---|---|---|---|---|
| sample_attrition | archive\outputs\tables\essay2_appendix\sample_attrition.csv | 12/12 | 72/72 | 0 |
| events_by_year | outputs\tables\essay2_appendix\events_by_year.csv | 18/18 | 72/72 | 0 |
| missingness_precase | archive\outputs\tables\essay2_appendix\missingness_precase.csv | 8/8 | 16/16 | 0 |
| four_panel_decomposition | archive\outputs\tables\essay2_appendix\four_panel_decomposition.csv | 36/36 | 343/360 | 17 |
| records_per_event | outputs\tables\essay2_appendix\records_per_event.csv | 43/43 | 43/43 | 0 |
| q1_transition_components | archive\outputs\tables\essay2_appendix\q1_transition_components.csv | 4/4 | 19/20 | 1 |
| q1_transition_records | archive\outputs\tables\essay2_appendix\q1_transition_records.csv | 10/10 | 40/40 | 0 |
| misclassified_records | archive\outputs\tables\essay2_appendix\misclassified_records.csv | 2/2 | 14/14 | 0 |
| misclassified_group_comparisons | archive\outputs\tables\essay2_appendix\misclassified_group_comparisons.csv | 5/5 | 35/35 | 0 |
| misclassified_group_contrasts | archive\outputs\tables\essay2_appendix\misclassified_group_contrasts.csv | 4/4 | 24/24 | 0 |
| gradient_grid | outputs\tables\essay2_appendix\gradient_grid.csv | 3/3 | 12/12 | 0 |
| size_variable_reconciliation | archive\outputs\tables\essay2_appendix\size_variable_reconciliation.csv | 2/2 | 6/14 | 8 |
| identifier_collisions | archive\outputs\tables\essay2_appendix\identifier_collisions.csv | 6/6 | 6/12 | 6 |
| recycled_tickers | archive\outputs\tables\essay2_appendix\identifier_collisions_recycled_tickers.csv | 7/7 | 35/35 | 0 |
| form499_registry_matches | archive\outputs\tables\essay2_appendix\form499_registry_matches.csv | 671/638 | 200/638 | 438 |
| treatment_adjudications | archive\outputs\tables\essay2_appendix\treatment_adjudications.csv | 26/26 | 52/52 | 0 |
| sic_conventions_vs_form499 | archive\outputs\tables\essay2_appendix\sic_conventions_vs_form499.csv | 4/4 | 36/36 | 0 |
| sic_convention_errors | archive\outputs\tables\essay2_appendix\sic_convention_errors.csv | 23/23 | 138/138 | 0 |
| sich_vs_curated_sic | archive\outputs\tables\essay2_appendix\sich_vs_curated_sic.csv | 12/12 | 34/36 | 2 |
| treated_outside_comparison | archive\outputs\tables\essay2_appendix\sich_unavailable_treated.csv | 11/11 | 33/33 | 0 |
| prerule_events | archive\outputs\tables\essay2_appendix\prerule_events.csv | 6/6 | 24/24 | 0 |

## sample_attrition

Reason for differences: step labels are the ledger's own wording

Exact at printed precision.

## events_by_year

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## missingness_precase

Reason for differences: variable label for the window row reworded

Exact at printed precision.

## four_panel_decomposition

Reason for differences: panels iii/iv use CANONICAL_V3 volatility_change, which the 10/2 CRSP de-duplication fix (dd8b564) changed for three treated events (CenturyLink 2020, DISH x2); panels i/ii and the footnotes read the 1,054-record prior dataset, which the fix did not touch

| row | column | tombstone | recomputed |
|---|---|---|---|
| 12 | coef | 3.4413 | 3.4530248990484256 |
| 12 | se | 1.8761 | 1.879099658332318 |
| 12 | t | 1.8343 | 1.8375954057236912 |
| 12 | p | 0.06751 | 0.06702094174682958 |
| 15 | coef | 10.9875 | 11.015792000811567 |
| 15 | se | 5.9568 | 5.971258309548255 |
| 15 | t | 1.8445 | 1.84480245699586 |
| 15 | p | 0.069056 | 0.0690144362038877 |
| 18 | coef | 3.9859 | 3.995764573853233 |
| 18 | se | 1.7995 | 1.8020071007704377 |
| 18 | t | 2.2149 | 2.217396686253271 |
| 18 | p | 0.027446 | 0.027276900037726395 |
| 21 | coef | 10.9875 | 11.015792000811567 |
| 21 | se | 5.9568 | 5.971258309548255 |
| 21 | t | 1.8445 | 1.84480245699586 |
| 21 | p | 0.069056 | 0.0690144362038877 |
| 34 | p | 8e-06 | 8.371725377498224e-06 |

## records_per_event

Reason for differences: ordering of tied "largest" rows may differ

Exact at printed precision.

## q1_transition_components

Reason for differences: N_records, means and SDs match; the never-treated event count differs by one (142 vs 141) under every committed event key (post-reparenting CIK, stage-2 CIK, legacy CIK); the retired emitter event key was never committed and cannot be recovered

| row | column | tombstone | recomputed |
|---|---|---|---|
| 3 | N_events | 141 | 142 |

## q1_transition_records

Reason for differences: row order

Exact at printed precision.

## misclassified_records

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## misclassified_group_comparisons

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## misclassified_group_contrasts

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## gradient_grid

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## size_variable_reconciliation

Reason for differences: ln_total_assets: N, slope, intercept and R2 reproduce exactly (prior dataset assets column, CRSP records); the within-0.10/0.25 shares differ because the retired emitter compared on an undocumented scale. ln_market_cap: the retired CIK-to-security link was never committed; the committed cik_ticker_map resolves fewer records (674 vs 845), so its row is a re-derivation (same conclusion: firm_size_log is market value, slope ~1, R2 ~.86)

| row | column | tombstone | recomputed |
|---|---|---|---|
| 0 | N | 845 | 674 |
| 0 | slope | 0.9817 | 0.9925598693551126 |
| 0 | intercept | 0.1795 | 0.04641132716100632 |
| 0 | R2 | 0.8729 | 0.8649620237505045 |
| 0 | share_within_010 | 0.7124 | 0.6884272997032641 |
| 0 | share_within_025 | 0.9538 | 0.9554896142433235 |
| 1 | share_within_010 | 0.0724 | 0.0400890868596882 |
| 1 | share_within_025 | 0.2416 | 0.14810690423162584 |

## identifier_collisions

Reason for differences: organization lists here are every prior-dataset name on the CIK; the retired table listed a curated subset

| row | column | tombstone | recomputed |
|---|---|---|---|
| 0 | organizations_absorbed | Johnson Matthey, Inc.; Christensen O'Connor Johnson Kindness PLLC; DiGiovine Hnilo Jordan + Johnson Ltd; Johnson Engineering | Christensen Oâ€™Connor Johnson Kindness PLLC; DiGiovine, Hnilo, Jordan + Johnson Ltd; Johnson Engineering; Johnson Matthey, Inc.; Johnson Oâ€™Hare Company, Inc.; Johnson, Lauder & Savidge, LLP; Mead Johnson & Company, LLC; Perry Johnson & Associates, Inc.; Perry Johnson, Inc.; Seim Johnson, LLP |
| 1 | organizations_absorbed | Suddenlink Communications | American Alarm & Communications, Inc.; Centerline Communications, LLC; CenturyLink Communications; Cleo Communications US, LLC; Communications & Power Industries LLC; Entercom Communications Corp.; Focus Medical Communications, LLC; Forum Communications Company; Frontier Communications Parent, Inc.; IES Communications, LLC; Mediacom Communications Corporation; Mediant Communications Inc.; Newcourse Communications, Inc.; Nuance Communications Inc; Nuance Communications, Inc.; Orbus Visual Communications, LLC; Prime Communications; Shawmut Communications Group; Sorenson Communications; Suddenlink Communications; Sumner Communications, Inc.; Superior Communications, Inc.; SupraNet Communications, Inc.; Window to the World Communications, Inc.; Woodward Communications, Inc. |
| 2 | organizations_absorbed | iHeartMedia + Entertainment, Inc. | iHeart Media Inc; iHeartMedia + Entertainment, Inc. |
| 3 | organizations_absorbed | E.W. Wylie Corporation (trucking) | E.W. Wylie Corporation |
| 4 | organizations_absorbed | PULAU Corporation | Dynapar Corporation; MNP Corporation; PULAU Corporation |
| 5 | organizations_absorbed | ATT-SecurityBreach; ATT-SecurityBreach2 (malformed non-firm records) | AT&T; AT&T Inc; AT&T Inc.; AT&T Services; AT&T Services Inc.; AT&T Services, Inc.; AT&T, Inc.; ATT-Breach Notification; ATT-SecurityBreach; ATT-SecurityBreach2; Cricket Wireless LLC |

## recycled_tickers

Reason for differences: the retired table's correct_permno column was a hand annotation

Exact at printed precision.

## form499_registry_matches

Reason for differences: family keyword sets: the retired table used a scratchpad heuristic (FAMS, never committed); this table uses the committed scripts/164 FAMILY lists, so per-parent record counts differ

| row | column | tombstone | recomputed |
|---|---|---|---|
| 0 | parent_cik | 1632127 | 18926 |
| 1 | parent_cik | 1632127 | 18926 |
| 2 | parent_cik | 20520 | 18926 |
| 3 | parent_cik | 1632127 | 18926 |
| 5 | parent_cik | 732712 | 18926 |
| 6 | parent_cik | 1166691 | 18926 |
| 7 | parent_cik | 732717 | 18926 |
| 8 | parent_cik | 1632127 | 18926 |
| 12 | parent_cik | 101830 | 18926 |
| 14 | parent_cik | 20520 | 18926 |
| 15 | parent_cik | 732712 | 18926 |
| 16 | parent_cik | 732712 | 18926 |
| 17 | parent_cik | 732717 | 18926 |
| 18 | parent_cik | 732717 | 18926 |
| 19 | parent_cik | 732717 | 18926 |
| 20 | parent_cik | 732712 | 18926 |
| 21 | parent_cik | 732717 | 18926 |
| 22 | parent_cik | 101830 | 18926 |
| 23 | parent_cik | 101830 | 18926 |
| 24 | parent_cik | 732717 | 18926 |
| 25 | parent_cik | 732717 | 18926 |
| 26 | parent_cik | 732717 | 18926 |
| 27 | parent_cik | 732717 | 18926 |
| 28 | parent_cik | 732717 | 18926 |
| 30 | parent_cik | 732712 | 18926 |
| 31 | parent_cik | 732712 | 18926 |
| 32 | parent_cik | 732712 | 18926 |
| 33 | parent_cik | 732712 | 18926 |
| 34 | parent_cik | 732712 | 18926 |
| 35 | parent_cik | 732717 | 18926 |
| 36 | parent_cik | 101830 | 18926 |
| 37 | parent_cik | 101830 | 18926 |
| 38 | parent_cik | 101830 | 18926 |
| 39 | parent_cik | 101830 | 18926 |
| 40 | parent_cik | 101830 | 18926 |
| 41 | parent_cik | 101830 | 18926 |
| 42 | parent_cik | 101830 | 18926 |
| 43 | parent_cik | 101830 | 18926 |
| 45 | parent_cik | 101830 | 18926 |
| 46 | parent_cik | 1632127 | 18926 |
| 47 | parent_cik | 732712 | 18926 |
| 48 | parent_cik | 732712 | 18926 |
| 49 | parent_cik | 732712 | 18926 |
| 50 | parent_cik | 732712 | 18926 |
| 51 | parent_cik | 20520 | 18926 |
| 52 | parent_cik | 20520 | 18926 |
| 53 | parent_cik | 732712 | 18926 |
| 54 | parent_cik | 732712 | 18926 |
| 55 | parent_cik | 20520 | 18926 |
| 56 | parent_cik | 20520 | 18926 |
| 57 | parent_cik | 20520 | 18926 |
| 58 | parent_cik | 20520 | 18926 |
| 59 | parent_cik | 20520 | 18926 |
| 60 | parent_cik | 20520 | 18926 |
| 61 | parent_cik | 20520 | 18926 |
| 63 | parent_cik | 732712 | 18926 |
| 95 | parent_cik | 18926 | 20520 |
| 96 | parent_cik | 18926 | 20520 |
| 97 | parent_cik | 732717 | 20520 |
| 98 | parent_cik | 732717 | 20520 |
| ... | 378 more | | |

## treatment_adjudications

Reason for differences: basis text is 154's full rationale; the retired table paraphrased it

Exact at printed precision.

## sic_conventions_vs_form499

Reason for differences: the failure-description column is prose

Exact at printed precision.

## sic_convention_errors

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## sich_vs_curated_sic

Reason for differences: the retired table grouped 12 families by hand (Comcast merged into the Cable One row, Sprint and Altice omitted); here one row per canonical treated parent plus Roku (joined on organization: 12 rows in both)

| row | column | tombstone | recomputed |
|---|---|---|---|
| Charter | curated_sic | 4833; 4841 | 4841 |
| Cable One | curated_sic | 4833; 4841 | 4841 |

## treated_outside_comparison

Reason for differences: (no documented reason; investigate)

Exact at printed precision.

## prerule_events

Reason for differences: (no documented reason; investigate)

Exact at printed precision.