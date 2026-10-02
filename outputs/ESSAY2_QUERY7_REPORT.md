# Essay 2 Query 7 (computed live)

==========================================================================================
QUERY 7 (computed live, scripts/176)
==========================================================================================

## 1.1 — Severity distribution, treated vs control (direct evidence on the truncation mechanism, independent of the regression)
  records affected (deciles d10..d90):
    treated: 1 | 2 | 5 | 11 | 46 | 584 | 1,931 | 240,092 | 5,920,000  (n with data 104/104)
    control: 3 | 10 | 15 | 72 | 168 | 436 | 1,468 | 24,149 | 185,254  (n with data 227/227)
  KS on log records: D=0.213 (p=0.0026) — treated distribution differs.
  breach-vector composition (% within group; columns 0=control, 1=treated):
fcc_form499     0     1
vec                    
DISC          4.0   1.9
HACK         76.7  61.5
INSD         10.6  20.2
PHYS          1.3  11.5
PORT          7.5   4.8
  data-type "SSN": treated 45% vs control 51%
  data-type "financial": treated 44% vs control 35%
  data-type "medical": treated 0% vs control 7%
  data-type "driver license": treated 25% vs control 25%

## 1.2-1.4 — Conditioning the announcement-window specification
  BASE (the scripts/175 announcement-window spec): +0.4717 (SE 0.1594, 95% CI [+0.1546, +0.7888], N=331)
  + severity (ln records winsor p99 + vector FE): +0.4856 (SE 0.1659, 95% CI [+0.1554, +0.8157], N=331)
  + flexible size (quartile FE + size^2): +0.5181 (SE 0.1735, 95% CI [+0.1729, +0.8632], N=331)
  + severity AND flexible size (joint): +0.5197 (SE 0.1779, 95% CI [+0.1656, +0.8737], N=331)
  common support (controls in treated size range; CHANGE OF ESTIMAND): +0.4569 (SE 0.1581, 95% CI [+0.1421, +0.7718], N=326)

  ATTENUATION vs base: severity -3% | flexible size -10% | joint -10% | common support +3%

## 1.5 — Multiplicity position of +0.4717
  Family: the 4-test announcement-window family (scripts/175, pre-specified by the 8/31 rescope). BH at FDR 5%, using the CV3 p-value (the calibrated rung):
    earnings elevation: p=1e-40 vs threshold 0.0125 -> reject
    contrast: p=1e-20 vs threshold 0.0250 -> reject
    treatment on elevation (CV3): p=0.0208 vs threshold 0.0375 -> reject
    breach elevation: p=0.073 vs threshold 0.0500 -> fail
  +0.4717 SURVIVES BH within its family at the CV3 p-value. Cumulative program tests through Query 6: 56 (enumerated per test in scripts/182, t53_test_ledger.csv; the earlier ~61 was an unenumerated estimate); Query 7 adds 6 (this family), total 62. Program-wide context stated wherever the coefficient is reported.

## PRE-SPECIFIED VERDICT (reading fixed before estimation)
  Joint-conditioned coefficient = +0.5197 = 110% of base. THE DIFFERENTIAL SURVIVES BOTH CHANNELS — genuine puzzle. FLAG AND STOP: it needs its own treatment in the essay and the results structure changes. No ruling is made here.

==========================================================================================
## 2 — Where does T-Mobile sit on announcement-window elevation?
==========================================================================================
  Focal event (Aug 2021): elevation +0.182 daily pp (abn [-4,+4] 1.118 vs [-25,-5] 0.936).
  Percentile: 61th within the treated distribution (treated mean -0.004, median -0.191); 68th within the full sample.
  T-Mobile/Sprint family (35 final-sample events): elevation mean +0.045, median +0.169, range [-2.96, +2.79] — vs treated group mean -0.004 and control mean -0.123.
  PLAINLY: the focal event is TYPICAL of the treated group on this dimension (|focal - treated mean| = 0.186 vs treated SD 1.039), and the family tracks the treated average.
