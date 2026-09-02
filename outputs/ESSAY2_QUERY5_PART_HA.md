# Essay 2 Query 5 — H1 scope + Part A bounds (computed live)

==========================================================================================
ESSAY 2 QUERY 5 — H1 INTENT SCOPE + PART A BOUNDS
==========================================================================================

## H1 — Intent-scope restriction (64.2011(e); FCC 22-102 para.12; FCC 23-111 para.21)
  Treated breach vectors (N=102): {'HACK': np.int64(58), 'INSD': np.int64(21), 'PHYS': np.int64(12), 'PORT': np.int64(5), 'HACK+INSD': np.int64(3), 'DISC': np.int64(2), 'HACK+PORT': np.int64(1)}
  NOTE: the canonical data carry only legacy vector codes; the current PRC schema's 36 breach-method subtypes are absent, so theft vs loss inside PHYS/PORT/STAT cannot be separated (checked, stated).
  ITT (entity-level, all treated events) [e2_vol_change]: coef +0.1575 SE 0.1971 CI [-0.2347, +0.5497] N=333 (treated 102/35 orgs/11 parents) MDE80 0.559
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [e2_vol_change]: coef +0.1429 SE 0.2223 CI [-0.2994, +0.5852] N=314 (treated 83/31 orgs/11 parents) MDE80 0.630
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [e2_vol_change]: coef +0.1445 SE 0.1983 CI [-0.2502, +0.5392] N=331 (treated 100/34 orgs/11 parents) MDE80 0.563

  Channels on the restricted sets:
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [cpqs_chg]: coef +0.0000 SE 0.0000 CI [-0.0000, +0.0001] N=314 (treated 83/31 orgs/11 parents) MDE80 0.000
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [edge_chg]: coef +0.0007 SE 0.0021 CI [-0.0035, +0.0049] N=314 (treated 83/31 orgs/11 parents) MDE80 0.006
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [ocam_chg]: coef -0.0278 SE 0.0713 CI [-0.1697, +0.1140] N=314 (treated 83/31 orgs/11 parents) MDE80 0.202
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [cpqs_chg]: coef +0.0001 SE 0.0001 CI [-0.0000, +0.0002] N=331 (treated 100/34 orgs/11 parents) MDE80 0.000
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [edge_chg]: coef +0.0018 SE 0.0023 CI [-0.0028, +0.0065] N=331 (treated 100/34 orgs/11 parents) MDE80 0.007
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [ocam_chg]: coef -0.0467 SE 0.0668 CI [-0.1796, +0.0863] N=331 (treated 100/34 orgs/11 parents) MDE80 0.190

  ITT-vs-effective-treatment framing: entity-level assignment where the rule applies event-level is one-sided misclassification of a binary regressor -> attenuation toward zero (Aigner 1973; Bound et al. 2001; Mahajan 2006). The entity-level null is therefore the WEAK null and the scope-restricted rows are the sharper tests; equivalence bounds estimated on the diluted treatment are NOT bounds on the scope-restricted effect. CPNI hand-coding from the 102 notification letters (double-coded subsample, inter-rater reliability) is the remaining option and was NOT attempted — stated in limitations; no field-based approximation is offered.

## PART A — Equivalence bounds
  A1: sample median share price at notification P = $75.52; one tick = 100/P = 1.32 bp; SESOI(spread) = one HALF-TICK = 0.66 bp = 0.000066 in CPQS units (Reg NMS Rule 612; a spread change below the market's own pricing granularity cannot be implemented by any trader). EDGE shares the spread SESOI. log-OCAM: proportional +/-10%% bound (0.0953 log points) — ILLIQ has no natural cardinal scale. Volatility: no institutional increment exists; the equivalence CI leads, with the quarter-SD (0.2742) and Wellek 0.36-sigma (0.3948) distributional references reported for context only. One rule per outcome, derived, deliberately NOT uniform.
  volatility (daily pp): coef +0.157515 (SE 0.197091, 90% CI [-0.170468, +0.485498]) | SESOI ±0.274200 | TOST p=0.2777 | equivalence CI (smallest concludable bound) = 0.485498 | MDE80 0.558988 | MDE/SESOI 2.04 | **INCONCLUSIVE**
  CPQS (fraction): coef +0.000048 (SE 0.000033, 90% CI [-0.000008, +0.000103]) | SESOI ±0.000066 | TOST p=0.2888 | equivalence CI (smallest concludable bound) = 0.000103 | MDE80 0.000095 | MDE/SESOI 1.43 | **INCONCLUSIVE**
  EDGE (fraction): coef +0.002125 (SE 0.002914, 90% CI [-0.002724, +0.006974]) | SESOI ±0.000066 | TOST p=0.7591 | equivalence CI (smallest concludable bound) = 0.006974 | MDE80 0.008264 | MDE/SESOI 124.82 | **INCONCLUSIVE**
  log-OCAM: coef -0.067594 (SE 0.091941, 90% CI [-0.220595, +0.085407]) | SESOI ±0.095300 | TOST p=0.3820 | equivalence CI (smallest concludable bound) = 0.220595 | MDE80 0.260762 | MDE/SESOI 2.74 | **INCONCLUSIVE**

  THE ONE-SENTENCE ANSWER: CPQS verdict: INCONCLUSIVE; volatility verdict: INCONCLUSIVE — see table.
  A3 (stated correctly): equivalence is concluded at the 5% level when the 90% CI lies entirely within (-m, m); the interval is 100-2*alpha because there are TWO one-sided tests, and the intersection-union principle makes the combined procedure level-alpha without multiplicity correction (Schuirmann 1987; Lakens 2017; Rainey 2014; Abadie 2020). "Equivalence confidence interval" is the named object (Hartman & Hidalgo 2018); the term "equivalence curve" is not used.

==========================================================================================
Tests this script: 13 — H1: 9; A: 4
