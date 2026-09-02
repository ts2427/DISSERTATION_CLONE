# Essay 2 Query 5 — H1 scope + Part A bounds (computed live)

==========================================================================================
ESSAY 2 QUERY 5 — H1 INTENT SCOPE + PART A BOUNDS
==========================================================================================

## H1 — Intent-scope restriction (64.2011(e); FCC 22-102 para.12; FCC 23-111 para.21)
  Treated breach vectors (N=102): {'HACK': np.int64(58), 'INSD': np.int64(21), 'PHYS': np.int64(12), 'PORT': np.int64(5), 'HACK+INSD': np.int64(3), 'DISC': np.int64(2), 'HACK+PORT': np.int64(1)}
  NOTE: the canonical data carry only legacy vector codes; the current PRC schema's 36 breach-method subtypes are absent, so theft vs loss inside PHYS/PORT/STAT cannot be separated (checked, stated).
  ITT (entity-level, all treated events) [e2_vol_change]: coef +0.1486 SE 0.2021 CI [-0.2535, +0.5507] N=331 (treated 102/35 orgs/11 parents) MDE80 0.573
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [e2_vol_change]: coef +0.1340 SE 0.2274 CI [-0.3185, +0.5864] N=312 (treated 83/31 orgs/11 parents) MDE80 0.645
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [e2_vol_change]: coef +0.1359 SE 0.2031 CI [-0.2684, +0.5401] N=329 (treated 100/34 orgs/11 parents) MDE80 0.576

  Channels on the restricted sets:
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [cpqs_chg]: coef +0.0000 SE 0.0000 CI [-0.0000, +0.0001] N=312 (treated 83/31 orgs/11 parents) MDE80 0.000
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [edge_chg]: coef +0.0007 SE 0.0021 CI [-0.0035, +0.0050] N=312 (treated 83/31 orgs/11 parents) MDE80 0.006
  STRICT intent scope (HACK/INSD/CARD; DISC & PHYS/PORT/STAT dropped) [ocam_chg]: coef -0.0270 SE 0.0724 CI [-0.1710, +0.1170] N=312 (treated 83/31 orgs/11 parents) MDE80 0.205
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [cpqs_chg]: coef +0.0001 SE 0.0001 CI [-0.0000, +0.0002] N=329 (treated 100/34 orgs/11 parents) MDE80 0.000
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [edge_chg]: coef +0.0019 SE 0.0024 CI [-0.0029, +0.0066] N=329 (treated 100/34 orgs/11 parents) MDE80 0.007
  LENIENT intent scope (+ PHYS/PORT/STAT; DISC dropped) [ocam_chg]: coef -0.0460 SE 0.0680 CI [-0.1813, +0.0893] N=329 (treated 100/34 orgs/11 parents) MDE80 0.193

  ITT-vs-effective-treatment framing: entity-level assignment where the rule applies event-level is one-sided misclassification of a binary regressor -> attenuation toward zero (Aigner 1973; Bound et al. 2001; Mahajan 2006). The entity-level null is therefore the WEAK null and the scope-restricted rows are the sharper tests; equivalence bounds estimated on the diluted treatment are NOT bounds on the scope-restricted effect. CPNI hand-coding from the 102 notification letters (double-coded subsample, inter-rater reliability) is the remaining option and was NOT attempted — stated in limitations; no field-based approximation is offered.

## PART A — Equivalence bounds
  A1: sample median share price at notification P = $76.09; one tick = 100/P = 1.31 bp; SESOI(spread) = one HALF-TICK = 0.66 bp = 0.000066 in CPQS units (Reg NMS Rule 612; a spread change below the market's own pricing granularity cannot be implemented by any trader). EDGE shares the spread SESOI. log-OCAM: proportional +/-10%% bound (0.0953 log points) — ILLIQ has no natural cardinal scale. Volatility: no institutional increment exists; the equivalence CI leads, with the quarter-SD (0.2742) and Wellek 0.36-sigma (0.3948) distributional references reported for context only. One rule per outcome, derived, deliberately NOT uniform.
  volatility (daily pp): coef +0.148589 (SE 0.202060, 90% CI [-0.187665, +0.484842]) | SESOI ±0.274200 | TOST p=0.2680 | equivalence CI (smallest concludable bound) = 0.484842 | MDE80 0.573084 | MDE/SESOI 2.09 | **INCONCLUSIVE**
  CPQS (fraction): coef +0.000050 (SE 0.000035, 90% CI [-0.000009, +0.000108]) | SESOI ±0.000066 | TOST p=0.3241 | equivalence CI (smallest concludable bound) = 0.000108 | MDE80 0.000099 | MDE/SESOI 1.51 | **INCONCLUSIVE**
  EDGE (fraction): coef +0.002225 (SE 0.003090, 90% CI [-0.002917, +0.007368]) | SESOI ±0.000066 | TOST p=0.7567 | equivalence CI (smallest concludable bound) = 0.007368 | MDE80 0.008764 | MDE/SESOI 133.37 | **INCONCLUSIVE**
  log-OCAM: coef -0.069269 (SE 0.096327, 90% CI [-0.229570, +0.091032]) | SESOI ±0.095300 | TOST p=0.3938 | equivalence CI (smallest concludable bound) = 0.229570 | MDE80 0.273204 | MDE/SESOI 2.87 | **INCONCLUSIVE**

  THE ONE-SENTENCE ANSWER: CPQS verdict: INCONCLUSIVE; volatility verdict: INCONCLUSIVE — see table.
  A3 (stated correctly): equivalence is concluded at the 5% level when the 90% CI lies entirely within (-m, m); the interval is 100-2*alpha because there are TWO one-sided tests, and the intersection-union principle makes the combined procedure level-alpha without multiplicity correction (Schuirmann 1987; Lakens 2017; Rainey 2014; Abadie 2020). "Equivalence confidence interval" is the named object (Hartman & Hidalgo 2018); the term "equivalence curve" is not used.

==========================================================================================
Tests this script: 13 — H1: 9; A: 4
