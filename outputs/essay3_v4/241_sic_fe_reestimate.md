# SIC-FE sensitivity, re-estimated on the Compustat header SIC

Freeze exception 2026-09-24, reason 1 (docs/claude/POST_DEFENSE.md).

## sic2 composition (new)
cells: 36; cells containing treated events: 2
              events  treated  control
sic2                                  
73               146        5      141
48               144      104       40
35                13        0       13
49                11        0       11
36                10        0       10
28                 8        0        8
45                 6        0        6
64                 6        0        6
unclassified       5        0        5
20                 5        0        5
51                 4        0        4
37                 4        0        4
67                 4        0        4
79                 3        0        3
62                 3        0        3
99                 3        0        3
63                 3        0        3
50                 3        0        3
34                 3        0        3
41                 3        0        3
44                 2        0        2
42                 2        0        2
10                 1        0        1
13                 1        0        1
15                 1        0        1
29                 1        0        1
27                 1        0        1
21                 1        0        1
38                 1        0        1
26                 1        0        1
33                 1        0        1
52                 1        0        1
55                 1        0        1
58                 1        0        1
72                 1        0        1
65                 1        0        1

cells with treated events: SIC 48: 104 treated / 40 control; SIC 73: 5 treated / 141 control

## Old vs new, the three SIC-FE rows
 window               which   n   coef  p_cv3  p_wcr   p_bh
     30 old (inherited sic) 405 0.0374 0.3866 0.2981    NaN
     30 new (Compustat sic) 405 0.0379 0.2677 0.1742 0.9912
     90 old (inherited sic) 405 0.0644 0.5979 0.5413    NaN
     90 new (Compustat sic) 405 0.0539 0.5062 0.3898 0.9912
    180 old (inherited sic) 405 0.1007 0.6077 0.5459    NaN
    180 new (Compustat sic) 405 0.1430 0.2770 0.2563 0.9912

BH over the sensitivities family (27 rows) recomputed; family min BH p: 0.9912
sensitivities-family BH p unchanged elsewhere: yes

written f3_sensitivities.csv (3 rows), i_tests.csv (BH), f3_sic2_cells.csv
