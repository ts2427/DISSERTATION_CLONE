# Essay 2 Query 7 (computed live)

==========================================================================================
QUERY 7 (computed live, scripts/176)
==========================================================================================

## 1.1 — Severity distribution, treated vs control (direct evidence on the truncation mechanism, independent of the regression)
  records affected (deciles d10..d90):
    treated: 1 | 2 | 4 | 10 | 38 | 489 | 1,930 | 194,448 | 7,040,000  (n with data 102/102)
    control: 3 | 10 | 15 | 72 | 168 | 436 | 1,468 | 24,149 | 185,254  (n with data 227/227)
  KS on log records: D=0.220 (p=0.0017) — treated distribution differs.
  breach-vector composition (% within group; columns 0=control, 1=treated):
fcc_form499     0     1
vec                    
DISC          4.0   2.0
HACK         76.7  60.8
INSD         10.6  20.6
PHYS          1.3  11.8
PORT          7.5   4.9
  data-type "SSN": treated 45% vs control 51%
  data-type "financial": treated 44% vs control 35%
  data-type "medical": treated 0% vs control 7%
  data-type "driver license": treated 25% vs control 25%

## 1.2-1.4 — Conditioning the announcement-window specification
  BASE (the +0.446 spec): +0.4388 (SE 0.1625, 95% CI [+0.1154, +0.7622], N=329)
  + severity (ln records winsor p99 + vector FE): +0.4500 (SE 0.1697, 95% CI [+0.1122, +0.7877], N=329)
  + flexible size (quartile FE + size^2): +0.4845 (SE 0.1806, 95% CI [+0.1249, +0.8440], N=329)
  + severity AND flexible size (joint): +0.4809 (SE 0.1840, 95% CI [+0.1147, +0.8470], N=329)
  common support (controls in treated size range; CHANGE OF ESTIMAND): +0.4244 (SE 0.1613, 95% CI [+0.1030, +0.7457], N=324)

  ATTENUATION vs base: severity -3% | flexible size -10% | joint -10% | common support +3%

## 1.5 — Multiplicity position of +0.446
  Family: the 4-test announcement-window family (scripts/175, pre-specified by the 8/31 rescope). BH at FDR 5%, using the CV3 p-value (the calibrated rung):
    earnings elevation: p=1e-40 vs threshold 0.0125 -> reject
    contrast: p=1e-20 vs threshold 0.0250 -> reject
    treatment on elevation (CV3): p=0.0249 vs threshold 0.0375 -> reject
    breach elevation: p=0.073 vs threshold 0.0500 -> fail
  +0.446 SURVIVES BH within its family at the CV3 p-value. Cumulative program tests through Query 6: ~61; Query 7 adds 6 (this family). Program-wide context stated wherever the coefficient is reported.

## PRE-SPECIFIED VERDICT (reading fixed before estimation)
  Joint-conditioned coefficient = +0.4809 = 110% of base. THE DIFFERENTIAL SURVIVES BOTH CHANNELS — genuine puzzle. FLAG AND STOP: it needs its own treatment in the essay and the results structure changes. No ruling is made here.

==========================================================================================
## 2 — Where does T-Mobile sit on announcement-window elevation?
==========================================================================================
  Focal event (Aug 2021): elevation +0.182 daily pp (abn [-4,+4] 1.118 vs [-25,-5] 0.936).
  Percentile: 61th within the treated distribution (treated mean -0.013, median -0.191); 68th within the full sample.
  T-Mobile/Sprint family (35 final-sample events): elevation mean +0.045, median +0.169, range [-2.96, +2.79] — vs treated group mean -0.013 and control mean -0.123.
  PLAINLY: the focal event is TYPICAL of the treated group on this dimension (|focal - treated mean| = 0.195 vs treated SD 1.036), and the family tracks the treated average.


==========================================================================================
CONTROL-SIDE DAMPING — descriptive anatomy (no tests, no p-values)
==========================================================================================

Reference: control mean elevation -0.123 (n=227), treated -0.013 (n=102).

           dimension                             cell   n  mean_elev  median  share_negative
                year                        2006-2010  16     -0.148  -0.088            0.56
                year                        2011-2015  38     -0.062  -0.148            0.63
                year                        2016-2019  94     -0.156  -0.066            0.54
                year                        2020-2024  79     -0.109  -0.139            0.56
            industry    finance/insurance (SIC 60-67)   7     -0.146   0.006            0.43
            industry                   retail (52-59)   2     -0.141  -0.141            0.50
            industry            manufacturing (20-39)  36     -0.146  -0.116            0.61
            industry            services/tech (70-79) 124     -0.039  -0.067            0.55
            industry                      health (80)   0        NaN     NaN             NaN
            industry transport/utilities/comm (40-49)  47     -0.320  -0.173            0.60
            industry               other/unclassified  11     -0.135  -0.394            0.55
breach-size quintile                  d1-2 (smallest)  46     -0.028   0.004            0.48
breach-size quintile                             d3-4  45     -0.168  -0.211            0.69
breach-size quintile                             d5-6  45     -0.139   0.006            0.49
breach-size quintile                             d7-8  45     -0.219  -0.232            0.56
breach-size quintile                  d9-10 (largest)  46     -0.065  -0.122            0.61

CHARACTERIZATION (descriptive only): within-dimension spreads of the cell means — breach-size quintile: 0.19; industry: 0.28; year: 0.09. The damping is DIFFUSE — no single sector, period, or size class carries it.
