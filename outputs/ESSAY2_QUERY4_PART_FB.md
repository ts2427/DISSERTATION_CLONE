# Essay 2 Query 4 — Parts F & B (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PART F GRID + B1/B3 GRADIENT (N=333)
==========================================================================================

Precomputing window SDs (48 window configs x 333 events)...

## F1 — Specification grid: 193 specifications
  coef distribution (daily pp): min +0.063 | p25 +0.181 | median +0.219 | p75 +0.257 | max +0.387
  p<.05: 1/193 (0.5%), all positive
  sign: 100% of specs positive
  draft-spec position: coef +0.2119 sits at percentile 44 of the distribution (p=0.298)

  Node influence (range of mean coef across the node's options):
    anchor  : 0.0271 daily pp  (breach=+0.239; notification=+0.212)
    basis   : 0.0585 daily pp  (calendar=+0.254; trading=+0.196)
    L       : 0.0849 daily pp  (21=+0.276; 31=+0.208; 42=+0.191)
    gap     : 0.0296 daily pp  (0=+0.238; 1=+0.221; 3=+0.208; 5=+0.234)
    returns : 0.0065 daily pp  (log=+0.222; simple=+0.228)
    winsor  : 0.0168 daily pp  (raw=+0.234; w199=+0.217)
  Largest single decision node: L (CORRECTS the expectation that anchor moves the estimate most).

  Significant cells with their decision paths (family = 193 specifications; multiplicity: at alpha=.05 one expects ~10 by chance):
    breach/calendar/L21/g5/simple/w199/SD: +0.348 (p=0.048)

  DV-variant correlation matrix (extends the r=0.45 finding):
                      notif_t_21_5  notif_t_31_3  notif_t_42_5  notif_c_31_0  breach_t_21_5  breach_c_31_0  garch_notif  canonical_ann_breach
notif_t_21_5                 1.000         0.894         0.727         0.930          0.467          0.471        0.748                 0.453
notif_t_31_3                 0.894         1.000         0.848         0.842          0.510          0.511        0.716                 0.503
notif_t_42_5                 0.727         0.848         1.000         0.670          0.487          0.487        0.681                 0.471
notif_c_31_0                 0.930         0.842         0.670         1.000          0.473          0.530        0.692                 0.499
breach_t_21_5                0.467         0.510         0.487         0.473          1.000          0.907        0.426                 0.928
breach_c_31_0                0.471         0.511         0.487         0.530          0.907          1.000        0.395                 0.964
garch_notif                  0.748         0.716         0.681         0.692          0.426          0.395        1.000                 0.411
canonical_ann_breach         0.453         0.503         0.471         0.499          0.928          0.964        0.411                 1.000

  F3 node classification (Del Giudice & Gangestad 2021): anchor = TYPE N (breach-anchoring construct-invalid per Part A; shown as documentation, not pooled); basis, L, gap, returns = Type E (principled equivalence); winsor = Type U (genuine uncertainty). Units axis excluded as a pure rescaling.
  F2: no joint permutation test is run (Semken & Rossell 2022: SCA median test Type I error can reach 1). Dispersion is the finding; framed as non-standard errors (Menkveld et al. 2024: NSE ~2.7x sampling SE; Mitton 2022: 73% of random variables significant under routine method variation).

## B3 — Gradient across the corrected-data grid (48 window-specs, log returns, raw DV):
  Q1>Q4 (small-firm effect exceeds large-firm): 0% of specs
  strictly monotone step-down Q1>Q2>Q3>Q4 (the old draft's claim): 0% of specs
              q1_gt_q4  monotone_down
anchor                               
breach             0.0            0.0
notification       0.0            0.0
  On the PRE-DEDUP vintage the grid cannot be rebuilt (no committed security-day link for the retired record set) — the uncorrected side of B3 is the fixed-spec four-panel below, stated as such. Harvey's refutation-hurdle point cuts both ways and is honored by reporting the full surface rather than the single flipping cell.

## B1 — Four-panel decomposition of the gradient reversal
  Named prior specification: the draft's own published quartile specification (the direct object of replication); Doyle & Magilke (2013 JAR) engaged in text as the deadline-heterogeneity precedent (their 10-K acceleration setting has no analogue sample here).
  (record->CIK key join: 757/1054 records matched)
  (i)  pre-dedup + SIC treatment: main +1.612 (SE 0.911) | Q1..Q4: 7.65, 2.86, -2.05, -3.51 | N=891 (183 treated)
  (ii) pre-dedup + Form 499 (family-level reconstruction): main +1.182 (SE 0.952) | Q1..Q4: 5.15, 2.86, -3.19, -3.79 | N=891 (188 treated)
  (iii) dedup + SIC treatment (record-modal SIC): main +3.453 (SE 1.879) | Q1..Q4: -13.08, 8.57, 11.02, 5.55 | N=339 (105 treated)
  (iv) dedup + Form 499 (canonical): main +3.996 (SE 1.802) | Q1..Q4: -13.08, 6.35, 11.02, 6.8 | N=339 (106 treated)
  READING: compare (i)->(ii) [treatment reclassification holding the record-level data] against (i)->(iii) [deduplication holding SIC treatment] to see which decision does the work in killing the step-down. Reconstruction approximations for (ii)/(iii) are stated in the header. Genre precedents: Karpoff & Wittry 2018 (legal-context reclassification); Karpoff et al. 2017 (database substitution, 39% replication).

## H2 — Winsorization sensitivity (headline spec)
  raw: coef +0.2119 SE 0.2024 95% CI [-0.1909, +0.6147] (CV1 parent-CIK)
  1/99: coef +0.1850 SE 0.1932 95% CI [-0.1993, +0.5694] (CV1 parent-CIK)
  5/95: coef +0.1285 SE 0.1414 95% CI [-0.1528, +0.4098] (CV1 parent-CIK)

Grid = 193 descriptive specifications (0 hypothesis tests); B1 = 4 panels x (1 main + 4 quartiles) = 20 estimates reported as one decomposition family; H2 = 3 sensitivity rows of the single main-effect hypothesis.
