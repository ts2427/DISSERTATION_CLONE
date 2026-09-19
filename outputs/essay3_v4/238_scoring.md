# REBUILD V4 - new-document classifier accuracy (scripts/238)

PRIMARY = verified reference codes; SECONDARY = raw blind codes.
Both were committed before the classifier was run on these documents.

## Agreement
                                                      field  n  agreement  kappa  ref_positives  clf_positives  tp  fp  fn  precision         precision_ci95  recall            recall_ci95
               PRIMARY (verified) | exec departure (A: any) 30     0.9667 0.8696              5              4   4   0   1        1.0          [0.3976, 1.0]  0.8000       [0.2836, 0.9949]
          PRIMARY (verified) | exec departure (B: new only) 30     0.9667 0.8696              5              4   4   0   1        1.0          [0.3976, 1.0]  0.8000       [0.2836, 0.9949]
                PRIMARY (verified) | CEO departure (A: any) 30     0.9667 0.0000              0              1   0   1   0        0.0           [0.0, 0.975]     NaN n/a (no ref positives)
           PRIMARY (verified) | CEO departure (B: new only) 30     0.9667 0.0000              0              1   0   1   0        0.0           [0.0, 0.975]     NaN n/a (no ref positives)
               PRIMARY (verified) | director-only departure 30     1.0000 1.0000              2              2   2   0   0        1.0          [0.1581, 1.0]  1.0000          [0.1581, 1.0]
PRIMARY (verified) | pre-announced (FULL POOL - MECHANICAL) 30     0.9667 0.8889              6              5   5   0   1        1.0          [0.4782, 1.0]  0.8333       [0.3588, 0.9958]
   PRIMARY (verified) | pre-announced (OUTCOME WINDOW ONLY)  3     1.0000    NaN              0              0   0   0   0        NaN n/a (no clf positives)     NaN n/a (no ref positives)
                SECONDARY (blind) | exec departure (A: any) 30     0.9667 0.8696              5              4   4   0   1        1.0          [0.3976, 1.0]  0.8000       [0.2836, 0.9949]
           SECONDARY (blind) | exec departure (B: new only) 30     0.9667 0.8696              5              4   4   0   1        1.0          [0.3976, 1.0]  0.8000       [0.2836, 0.9949]
                 SECONDARY (blind) | CEO departure (A: any) 30     0.9667 0.0000              0              1   0   1   0        0.0           [0.0, 0.975]     NaN n/a (no ref positives)
            SECONDARY (blind) | CEO departure (B: new only) 30     0.9667 0.0000              0              1   0   1   0        0.0           [0.0, 0.975]     NaN n/a (no ref positives)
                SECONDARY (blind) | director-only departure 30     1.0000 1.0000              2              2   2   0   0        1.0          [0.1581, 1.0]  1.0000          [0.1581, 1.0]
 SECONDARY (blind) | pre-announced (FULL POOL - MECHANICAL) 30     0.9667 0.8889              6              5   5   0   1        1.0          [0.4782, 1.0]  0.8333       [0.3588, 0.9958]
    SECONDARY (blind) | pre-announced (OUTCOME WINDOW ONLY)  3     1.0000    NaN              0              0   0   0   0        NaN n/a (no clf positives)     NaN n/a (no ref positives)

## Bounds - every flagged row (5, 8, 21, 28) forced Y, then forced N
                                          field  n  agreement  kappa  ref_positives  clf_positives  tp  fp  fn  precision   precision_ci95  recall      recall_ci95
     flagged forced Y | exec departure (A: any) 30     0.9667 0.8696              5              4   4   0   1        1.0    [0.3976, 1.0]  0.8000 [0.2836, 0.9949]
flagged forced Y | exec departure (B: new only) 30     0.9667 0.8696              5              4   4   0   1        1.0    [0.3976, 1.0]  0.8000 [0.2836, 0.9949]
     flagged forced Y | director-only departure 30     0.9667 0.7826              3              2   2   0   1        1.0    [0.1581, 1.0]  0.6667 [0.0943, 0.9916]
     flagged forced N | exec departure (A: any) 30     0.9333 0.6341              2              4   2   2   0        0.5 [0.0676, 0.9324]  1.0000    [0.1581, 1.0]
flagged forced N | exec departure (B: new only) 30     0.9333 0.6341              2              4   2   2   0        0.5 [0.0676, 0.9324]  1.0000    [0.1581, 1.0]
     flagged forced N | director-only departure 30     1.0000 1.0000              2              2   2   0   0        1.0    [0.1581, 1.0]  1.0000    [0.1581, 1.0]

## v3-era round 2, for comparison (outputs/essay3_q2/d3_r2_agreement.csv)
                                           field  n  agreement  kappa  ref_positives  clf_positives  tp  fp  fn  precision         precision_ci95  recall            recall_ci95
                         exec departure (A: any) 29     0.9310 0.7129              5              3   3   0   2     1.0000          [0.2924, 1.0]  0.6000       [0.1466, 0.9473]
                    exec departure (B: new only) 29     0.8966 0.5140              4              3   2   1   2     0.6667       [0.0943, 0.9916]  0.5000       [0.0676, 0.9324]
                          CEO departure (A: any) 30     1.0000    NaN              0              0   0   0   0        NaN n/a (no clf positives)     NaN n/a (no ref positives)
                     CEO departure (B: new only) 30     1.0000    NaN              0              0   0   0   0        NaN n/a (no clf positives)     NaN n/a (no ref positives)
                         director-only departure 30     1.0000 1.0000              9              9   9   0   0     1.0000          [0.6637, 1.0]  1.0000          [0.6637, 1.0]
     pre-announced (sheet 9 verified Y, PRIMARY) 30     0.8667 0.7183             12              8   8   0   4     1.0000          [0.6306, 1.0]  0.6667       [0.3489, 0.9008]
pre-announced (sheet 9 blind unclear, SECONDARY) 30     0.9000 0.7921             11              8   8   0   3     1.0000          [0.6306, 1.0]  0.7273       [0.3903, 0.9398]

## Reading these numbers
The classifier is FROZEN: scripts/220 is byte-identical to v3's scripts/195.
No result here may retune it. n is 30 documents, so every interval is wide;
the exact intervals are reported rather than point estimates alone.

written 238_new_document_agreement.csv, 238_new_document_bounds.csv
