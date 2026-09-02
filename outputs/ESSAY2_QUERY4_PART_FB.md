# Essay 2 Query 4 — Parts F & B (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PART F GRID + B1/B3 GRADIENT (N=333)
==========================================================================================

Precomputing window SDs (48 window configs x 333 events)...

## F1 — Specification grid: 193 specifications
  coef distribution (daily pp): min +0.048 | p25 +0.142 | median +0.182 | p75 +0.217 | max +0.333
  p<.05: 0/193 (0.0%), all positive
  sign: 100% of specs positive
  draft-spec position: coef +0.1575 sits at percentile 32 of the distribution (p=0.426)

  Node influence (range of mean coef across the node's options):
    anchor  : 0.0376 daily pp  (breach=+0.203; notification=+0.166)
    basis   : 0.0530 daily pp  (calendar=+0.211; trading=+0.158)
    L       : 0.0691 daily pp  (21=+0.227; 31=+0.168; 42=+0.158)
    gap     : 0.0308 daily pp  (0=+0.198; 1=+0.182; 3=+0.167; 5=+0.191)
    returns : 0.0043 daily pp  (log=+0.182; simple=+0.186)
    winsor  : 0.0153 daily pp  (raw=+0.192; w199=+0.177)
  Largest single decision node: L (CORRECTS the expectation that anchor moves the estimate most).

  DV-variant correlation matrix (extends the r=0.45 finding):
                      notif_t_21_5  notif_t_31_3  notif_t_42_5  notif_c_31_0  breach_t_21_5  breach_c_31_0  garch_notif  canonical_ann_breach
notif_t_21_5                 1.000         0.895         0.727         0.930          0.466          0.469        0.749                 0.451
notif_t_31_3                 0.895         1.000         0.848         0.844          0.509          0.510        0.717                 0.502
notif_t_42_5                 0.727         0.848         1.000         0.670          0.485          0.486        0.682                 0.470
notif_c_31_0                 0.930         0.844         0.670         1.000          0.470          0.527        0.694                 0.496
breach_t_21_5                0.466         0.509         0.485         0.470          1.000          0.906        0.426                 0.928
breach_c_31_0                0.469         0.510         0.486         0.527          0.906          1.000        0.395                 0.963
garch_notif                  0.749         0.717         0.682         0.694          0.426          0.395        1.000                 0.411
canonical_ann_breach         0.451         0.502         0.470         0.496          0.928          0.963        0.411                 1.000

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
  (ii) pre-dedup + Form 499 (family-level reconstruction): main +0.016 (SE 0.919) | Q1..Q4: 0.13, 2.86, -3.19, -3.79 | N=891 (180 treated)
  (iii) dedup + SIC treatment (record-modal SIC): main +2.614 (SE 1.814) | Q1..Q4: -13.08, 8.57, 8.91, 5.02 | N=337 (103 treated)
  (iv) dedup + Form 499 (canonical): main +3.259 (SE 1.745) | Q1..Q4: -13.08, 6.35, 8.91, 6.6 | N=337 (104 treated)
  READING: compare (i)->(ii) [treatment reclassification holding the record-level data] against (i)->(iii) [deduplication holding SIC treatment] to see which decision does the work in killing the step-down. Reconstruction approximations for (ii)/(iii) are stated in the header. Genre precedents: Karpoff & Wittry 2018 (legal-context reclassification); Karpoff et al. 2017 (database substitution, 39% replication).

## H2 — Winsorization sensitivity (headline spec)
  raw: coef +0.1575 SE 0.1971 95% CI [-0.2347, +0.5497] (CV1 parent-CIK)
  1/99: coef +0.1344 SE 0.1887 95% CI [-0.2410, +0.5099] (CV1 parent-CIK)
  5/95: coef +0.0765 SE 0.1355 95% CI [-0.1932, +0.3461] (CV1 parent-CIK)

Grid = 193 descriptive specifications (0 hypothesis tests); B1 = 4 panels x (1 main + 4 quartiles) = 20 estimates reported as one decomposition family; H2 = 3 sensitivity rows of the single main-effect hypothesis.
