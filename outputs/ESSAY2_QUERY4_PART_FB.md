# Essay 2 Query 4 — Parts F & B (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PART F GRID + B1/B3 GRADIENT (N=333)
==========================================================================================

Precomputing window SDs (48 window configs x 333 events)...

## F1 — Specification grid: 193 specifications
  coef distribution (daily pp): min +0.060 | p25 +0.175 | median +0.219 | p75 +0.253 | max +0.386
  p<.05: 1/193 (0.5%), all positive
  sign: 100% of specs positive
  draft-spec position: coef +0.1863 sits at percentile 31 of the distribution (p=0.353)

  Node influence (range of mean coef across the node's options):
    anchor  : 0.0361 daily pp  (breach=+0.241; notification=+0.205)
    basis   : 0.0610 daily pp  (calendar=+0.254; trading=+0.193)
    L       : 0.0718 daily pp  (21=+0.266; 31=+0.210; 42=+0.194)
    gap     : 0.0258 daily pp  (0=+0.233; 1=+0.215; 3=+0.209; 5=+0.235)
    returns : 0.0069 daily pp  (log=+0.220; simple=+0.226)
    winsor  : 0.0169 daily pp  (raw=+0.231; w199=+0.215)
  Largest single decision node: L (CORRECTS the expectation that anchor moves the estimate most).

  Significant cells with their decision paths (family = 193 specifications; multiplicity: at alpha=.05 one expects ~10 by chance):
    breach/calendar/L21/g5/simple/w199/SD: +0.347 (p=0.048)

  DV-variant correlation matrix (extends the r=0.45 finding):
                      notif_t_21_5  notif_t_31_3  notif_t_42_5  notif_c_31_0  breach_t_21_5  breach_c_31_0  garch_notif  canonical_ann_breach
notif_t_21_5                 1.000         0.889         0.722         0.921          0.461          0.468        0.750                 0.451
notif_t_31_3                 0.889         1.000         0.849         0.845          0.513          0.513        0.714                 0.505
notif_t_42_5                 0.722         0.849         1.000         0.672          0.489          0.489        0.680                 0.473
notif_c_31_0                 0.921         0.845         0.672         1.000          0.476          0.530        0.689                 0.499
breach_t_21_5                0.461         0.513         0.489         0.476          1.000          0.906        0.423                 0.927
breach_c_31_0                0.468         0.513         0.489         0.530          0.906          1.000        0.394                 0.964
garch_notif                  0.750         0.714         0.680         0.689          0.423          0.394        1.000                 0.411
canonical_ann_breach         0.451         0.505         0.473         0.499          0.927          0.964        0.411                 1.000

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
  (iii) dedup + SIC treatment (record-modal SIC): main +3.441 (SE 1.876) | Q1..Q4: -13.08, 8.57, 10.99, 5.55 | N=339 (105 treated)
  (iv) dedup + Form 499 (canonical): main +3.986 (SE 1.8) | Q1..Q4: -13.08, 6.35, 10.99, 6.8 | N=339 (106 treated)
  READING: compare (i)->(ii) [treatment reclassification holding the record-level data] against (i)->(iii) [deduplication holding SIC treatment] to see which decision does the work in killing the step-down. Reconstruction approximations for (ii)/(iii) are stated in the header. Genre precedents: Karpoff & Wittry 2018 (legal-context reclassification); Karpoff et al. 2017 (database substitution, 39% replication).

## H2 — Winsorization sensitivity (headline spec)
  raw: coef +0.1863 SE 0.1994 95% CI [-0.2105, +0.5830] (CV1 parent-CIK)
  1/99: coef +0.1592 SE 0.1905 95% CI [-0.2199, +0.5383] (CV1 parent-CIK)
  5/95: coef +0.0941 SE 0.1388 95% CI [-0.1821, +0.3703] (CV1 parent-CIK)

Grid = 193 descriptive specifications (0 hypothesis tests); B1 = 4 panels x (1 main + 4 quartiles) = 20 estimates reported as one decomposition family; H2 = 3 sensitivity rows of the single main-effect hypothesis.
