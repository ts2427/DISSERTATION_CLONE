# Essay 2 Query 7 (computed live)

==========================================================================================
QUERY 7 (computed live, scripts/176)
==========================================================================================

## 1.1 — Severity distribution, treated vs control (direct evidence on the truncation mechanism, independent of the regression)
  records affected (deciles d10..d90):
    treated: 1 | 2 | 4 | 10 | 38 | 489 | 1,930 | 194,448 | 7,040,000  (n with data 102/102)
    control: 3 | 10 | 15 | 66 | 168 | 383 | 1,443 | 24,149 | 175,843  (n with data 229/229)
  KS on log records: D=0.213 (p=0.0027) — treated distribution differs.
  breach-vector composition (% within group; columns 0=control, 1=treated):
fcc_form499     0     1
vec                    
DISC          3.9   2.0
HACK         76.9  60.8
INSD         10.5  20.6
PHYS          1.3  11.8
PORT          7.4   4.9
  data-type "SSN": treated 45% vs control 51%
  data-type "financial": treated 44% vs control 34%
  data-type "medical": treated 0% vs control 7%
  data-type "driver license": treated 25% vs control 25%

## 1.2-1.4 — Conditioning the announcement-window specification
  BASE (the +0.446 spec): +0.4463 (SE 0.1583, 95% CI [+0.1312, +0.7615], N=331)
  + severity (ln records winsor p99 + vector FE): +0.4590 (SE 0.1669, 95% CI [+0.1267, +0.7913], N=331)
  + flexible size (quartile FE + size^2): +0.4812 (SE 0.1722, 95% CI [+0.1384, +0.8239], N=331)
  + severity AND flexible size (joint): +0.4838 (SE 0.1793, 95% CI [+0.1269, +0.8407], N=331)
  common support (controls in treated size range; CHANGE OF ESTIMAND): +0.4321 (SE 0.1572, 95% CI [+0.1190, +0.7452], N=326)

  ATTENUATION vs base: severity -3% | flexible size -8% | joint -8% | common support +3%

## 1.5 — Multiplicity position of +0.446
  Family: the 4-test announcement-window family (scripts/175, pre-specified by the 8/31 rescope). BH at FDR 5%, using the CV3 p-value (the calibrated rung):
    earnings elevation: p=1e-40 vs threshold 0.0125 -> reject
    contrast: p=1e-20 vs threshold 0.0250 -> reject
    treatment on elevation (CV3): p=0.0249 vs threshold 0.0375 -> reject
    breach elevation: p=0.073 vs threshold 0.0500 -> fail
  +0.446 SURVIVES BH within its family at the CV3 p-value. Cumulative program tests through Query 6: ~61; Query 7 adds 6 (this family). Program-wide context stated wherever the coefficient is reported.

## PRE-SPECIFIED VERDICT (reading fixed before estimation)
  Joint-conditioned coefficient = +0.4838 = 108% of base. THE DIFFERENTIAL SURVIVES BOTH CHANNELS — genuine puzzle. FLAG AND STOP: it needs its own treatment in the essay and the results structure changes. No ruling is made here.

==========================================================================================
## 2 — Where does T-Mobile sit on announcement-window elevation?
==========================================================================================
  Focal event (Aug 2021): elevation +0.182 daily pp (abn [-4,+4] 1.118 vs [-25,-5] 0.936).
  Percentile: 61th within the treated distribution (treated mean -0.013, median -0.191); 68th within the full sample.
  T-Mobile/Sprint family (35 final-sample events): elevation mean +0.045, median +0.169, range [-2.96, +2.79] — vs treated group mean -0.013 and control mean -0.125.
  PLAINLY: the focal event is TYPICAL of the treated group on this dimension (|focal - treated mean| = 0.195 vs treated SD 1.036), and the family tracks the treated average.


==========================================================================================
CONTROL-SIDE DAMPING — descriptive anatomy (no tests, no p-values)
==========================================================================================

Reference: control mean elevation -0.125 (n=229), treated -0.013 (n=102).

           dimension                             cell   n  mean_elev  median  share_negative
                year                        2006-2010  16     -0.148  -0.088            0.56
                year                        2011-2015  40     -0.077  -0.167            0.65
                year                        2016-2019  94     -0.156  -0.066            0.54
                year                        2020-2024  79     -0.109  -0.139            0.56
            industry    finance/insurance (SIC 60-67)   7     -0.146   0.006            0.43
            industry                   retail (52-59)   2     -0.141  -0.141            0.50
            industry            manufacturing (20-39)  36     -0.146  -0.116            0.61
            industry            services/tech (70-79) 124     -0.039  -0.067            0.55
            industry                      health (80)   0        NaN     NaN             NaN
            industry transport/utilities/comm (40-49)  49     -0.322  -0.173            0.61
            industry               other/unclassified  11     -0.135  -0.394            0.55
breach-size quintile                  d1-2 (smallest)  46     -0.050  -0.029            0.50
breach-size quintile                             d3-4  46     -0.150  -0.200            0.67
breach-size quintile                             d5-6  45     -0.149  -0.056            0.51
breach-size quintile                             d7-8  46     -0.213  -0.144            0.54
breach-size quintile                  d9-10 (largest)  46     -0.065  -0.122            0.61

CHARACTERIZATION (descriptive only): within-dimension spreads of the cell means — breach-size quintile: 0.16; industry: 0.28; year: 0.08. The damping is DIFFUSE — no single sector, period, or size class carries it.
