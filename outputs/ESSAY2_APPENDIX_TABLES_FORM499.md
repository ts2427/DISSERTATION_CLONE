# Essay 2 Appendix Tables â€” Form 499 rerun (ground truth)

**Generated live by scripts/163_essay2_rerun_form499.py on CANONICAL_V3.
Nothing here is carried forward from the old draft.**

## Plain-language report

**1. Main effect.** Treatment (Form 499) on volatility change (daily-pp,
log-return SD, [-25,-5] vs [+5,+25] trading days around notification):
coef +0.1863, SE 0.1346, t +1.384,
df 324, p 0.1673, N 333. Verdict: **null â€” underpowered/inconclusive**
(TOST p = 0.6557 against the Essay 1 bound converted to
daily units; MDE80 = 0.3768 daily pp =
5.98pp annualized â€” the design cannot
detect, at 80% power, effect sizes of the magnitude the prior literature
discusses). DV-convention note: the breach-anchored annualized DV the old
CODE used gives +4.26 (p=0.024 HC3, p=0.074
firm-clustered) on this sample, but it is DISQUALIFIED on construct
validity â€” 56.7% of its measured post-window days precede public
notification (median observation: 74%) â€” see Phase E. The draft-spec
measure is the valid one, and it is null.

**2. Firm-size step-down.** Q1 (smallest): -1.000 (p=0.002, 1 treated parent CIKs, <5 â€” do not interpret bare); Q2: +0.322 (p=0.322, 4 treated parent CIKs, <5 â€” do not interpret bare); Q3: +0.756 (p=0.022, 4 treated parent CIKs, <5 â€” do not interpret bare); Q4 (largest): +0.348 (p=0.063, 5 treated parent CIKs). (Old draft's +7.31 Q1 figure is not
reproduced; treated parent-CIK counts are now printed beside every quartile.)

**3. Final N = 333** (104 treated / 36 orgs /
12 parent CIKs), vs Essay 1 v3 regression N = 338.
The old draft's N = 891 is not reproducible from the canonical chain â€” it
predates deduplication (1,054 records -> 489 events) and entity resolution.
Full chain in ESSAY2_SAMPLE_ATTRITION_LEDGER.md; the volatility-window
requirement and the delay-regressor requirement are separate lines.

**4. Old vs new.** No old-draft coefficient was confirmed; none reproduced
(see leak check). NOT REGENERABLE AT ALL: the five moderators (CVSS, media,
governance, information-environment, reputation), the N = 891 sample, the
records-based prior-breach count (mean 3.65, range 0-68), and the old
draft's t/p columns (which were internally inconsistent â€” every t was
0.8806 x coef/SE, and its headline p = .047 was the single reconciled cell;
the printed t = 1.769 implies p = .077).

**5. Pipeline findings** are listed at the end of this file.

---
==========================================================================================
ESSAY 2 RERUN â€” GROUND TRUTH (Form 499 treatment, CANONICAL_V3)
==========================================================================================
ASSERT PASS â€” treatment column is fcc_form499 (Form 499), not SIC

Computing Essay 2 volatility DV (log-return SD, trading days [-25,-5]/[+5,+25], notification-anchored)...
ASSERT PASS â€” prior_breaches_total equals recomputed prior-event count
ASSERT PASS â€” universe is 1,054 notification records [1054]
ASSERT PASS â€” entity resolution retains 758 records
ASSERT PASS â€” dedup yields 524 firm-day events
ASSERT PASS â€” Gate 2 yields 489 events
ASSERT PASS â€” record chain closes: 1054 - 296 = 758
ASSERT PASS â€” event chain closes: 524 -> 489 removes 35
ASSERT PASS â€” CRSP daily extract ends at the 2024-12-31 WRDS boundary [max trading date in extract = 2024-12-31]
ASSERT PASS â€” every notification beyond the boundary is calendar-2025 (none later) [years: [2025]]
ASSERT PASS â€” boundary line reorders attrition only: window step would drop every 2025-notified event anyway
ASSERT PASS â€” ledger closes: no CRSP match [489 -> 361 (-128)]
ASSERT PASS â€” ledger closes: no notification date [361 -> 361 (-0)]
ASSERT PASS â€” ledger closes: beyond WRDS extract boundary [361 -> 355 (-6)]
ASSERT PASS â€” ledger closes: windows not computable [355 -> 351 (-4)]
ASSERT PASS â€” ledger closes: missing covariates [351 -> 336 (-15)]
ASSERT PASS â€” ledger closes: missing delay [336 -> 335 (-1)]
ASSERT PASS â€” ledger closes: malformed ATT-artifact records [335 -> 333 (-2)]
ASSERT PASS â€” final N is nowhere near the old draft N=891 (dedup+CRSP applied) [N=333]
ASSERT PASS â€” window-loss decomposition closes [1+0+3+0 == 4]
ASSERT PASS â€” CRSP-match failures = canonical minus matched [128 == 489 - 361]
ASSERT PASS â€” treated CRSP-match failures reconcile
ASSERT PASS â€” org-type composition sums to CRSP-fail total
ASSERT PASS â€” by-year canonical column sums to canonical N/treated
ASSERT PASS â€” by-year final column sums to final N/treated

==========================================================================================
PHASE B â€” DESCRIPTIVES BY TREATMENT STATUS
==========================================================================================
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_vol_change) [1.0940 vs 1.1012]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_vol_change)
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_pre_sd) [1.2375 vs 1.0541]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_pre_sd)
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_post_sd) [1.1300 vs 1.0222]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_post_sd)
ASSERT PASS â€” group SDs computed independently and NOT identical (disclosure_delay_days) [252.1475 vs 125.5262]
ASSERT PASS â€” pooled mean reconciles to subgroup means (disclosure_delay_days)
ASSERT PASS â€” group SDs computed independently and NOT identical (delay_w) [159.2897 vs 120.4904]
ASSERT PASS â€” pooled mean reconciles to subgroup means (delay_w)
ASSERT PASS â€” group SDs computed independently and NOT identical (firm_size_log) [1.2282 vs 1.3676]
ASSERT PASS â€” pooled mean reconciles to subgroup means (firm_size_log)
ASSERT PASS â€” group SDs computed independently and NOT identical (leverage) [0.1635 vs 0.2176]
ASSERT PASS â€” pooled mean reconciles to subgroup means (leverage)
ASSERT PASS â€” group SDs computed independently and NOT identical (roa) [0.0470 vs 0.1238]
ASSERT PASS â€” pooled mean reconciles to subgroup means (roa)
ASSERT PASS â€” group SDs computed independently and NOT identical (health_breach) [0.0000 vs 0.2480]
ASSERT PASS â€” pooled mean reconciles to subgroup means (health_breach)
ASSERT PASS â€” group SDs computed independently and NOT identical (prior_events) [9.1465 vs 21.1154]
ASSERT PASS â€” pooled mean reconciles to subgroup means (prior_events)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (treated)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (control)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (pooled)
             variable  mean_treated  sd_treated  mean_control  sd_control  mean_pooled  sd_pooled  n_treated  n_control
        e2_vol_change        0.0033      1.0940       -0.0402      1.1012      -0.0266     1.0975        104        229
            e2_pre_sd        1.7711      1.2375        1.6878      1.0541       1.7138     1.1134        104        229
           e2_post_sd        1.7744      1.1300        1.6476      1.0222       1.6872     1.0570        104        229
disclosure_delay_days       98.9135    252.1475       71.0961    125.5262      79.7838   175.2491        104        229
              delay_w       82.4604    159.2897       70.3273    120.4904      74.1166   133.6925        104        229
        firm_size_log       11.6093      1.2282        9.6211      1.3676      10.2420     1.6137        104        229
             leverage        0.7216      0.1635        0.6412      0.2176       0.6663     0.2055        104        229
                  roa        0.0243      0.0470        0.0771      0.1238       0.0606     0.1087        104        229
        health_breach        0.0000      0.0000        0.0655      0.2480       0.0450     0.2077        104        229
         prior_events       10.0288      9.1465       13.9039     21.1154      12.6937    18.3134        104        229

(The old Table A2 reported identical treated/control SDs on three variables â€” 14.2/14.2, 16.3/16.3, 1.84/1.84 â€” impossible for unequal groups; the independent SDs above replace it.)

==========================================================================================
PHASE C â€” MAIN EFFECT, NESTED MODELS, SE SPECIFICATIONS
==========================================================================================
ASSERT PASS â€” t == coef/se (M1 timing + pre-vol :: delay_w) [t=0.061866 coef/se=0.061866]
ASSERT PASS â€” p follows from t and df (M1 timing + pre-vol :: delay_w) [p=0.950707 implied=0.950707 df=330]
ASSERT PASS â€” t == coef/se (M1 timing + pre-vol :: e2_pre_sd) [t=-8.095339 coef/se=-8.095339]
ASSERT PASS â€” p follows from t and df (M1 timing + pre-vol :: e2_pre_sd) [p=0.000000 implied=0.000000 df=330]

M1 timing + pre-vol: N=333 df_resid=330 R2=0.2948
ASSERT PASS â€” t == coef/se (M2 + financial controls :: delay_w) [t=0.012676 coef/se=0.012676]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: delay_w) [p=0.989894 implied=0.989894 df=327]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: e2_pre_sd) [t=-8.466760 coef/se=-8.466760]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: e2_pre_sd) [p=0.000000 implied=0.000000 df=327]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: firm_size_log) [t=-0.792033 coef/se=-0.792033]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: firm_size_log) [p=0.428916 implied=0.428916 df=327]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: leverage) [t=-0.984771 coef/se=-0.984771]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: leverage) [p=0.325465 implied=0.325465 df=327]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: roa) [t=-1.185825 coef/se=-1.185825]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: roa) [p=0.236552 implied=0.236552 df=327]

M2 + financial controls: N=333 df_resid=327 R2=0.2996
ASSERT PASS â€” t == coef/se (M3 + treatment :: delay_w) [t=0.020916 coef/se=0.020916]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: delay_w) [p=0.983325 implied=0.983325 df=326]
ASSERT PASS â€” t == coef/se (M3 + treatment :: e2_pre_sd) [t=-8.665710 coef/se=-8.665710]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: e2_pre_sd) [p=0.000000 implied=0.000000 df=326]
ASSERT PASS â€” t == coef/se (M3 + treatment :: firm_size_log) [t=-1.670909 coef/se=-1.670909]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: firm_size_log) [p=0.095699 implied=0.095699 df=326]
ASSERT PASS â€” t == coef/se (M3 + treatment :: leverage) [t=-1.239265 coef/se=-1.239265]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: leverage) [p=0.216139 implied=0.216139 df=326]
ASSERT PASS â€” t == coef/se (M3 + treatment :: roa) [t=-1.108095 coef/se=-1.108095]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: roa) [p=0.268637 implied=0.268637 df=326]
ASSERT PASS â€” t == coef/se (M3 + treatment :: fcc_form499) [t=1.417119 coef/se=1.417119]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: fcc_form499) [p=0.157403 implied=0.157403 df=326]

M3 + treatment: N=333 df_resid=326 R2=0.3033
  M3 + treatment :: fcc_form499: coef +0.1809  SE 0.1276  t +1.417  df 326  p 0.1574  N 333
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: delay_w) [t=-0.026520 coef/se=-0.026520]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: delay_w) [p=0.978859 implied=0.978859 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: e2_pre_sd) [t=-8.569055 coef/se=-8.569055]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: e2_pre_sd) [p=0.000000 implied=0.000000 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: firm_size_log) [t=-1.699382 coef/se=-1.699382]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: firm_size_log) [p=0.090207 implied=0.090207 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: leverage) [t=-1.407567 coef/se=-1.407567]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: leverage) [p=0.160218 implied=0.160218 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: roa) [t=-0.930276 coef/se=-0.930276]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: roa) [p=0.352921 implied=0.352921 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: fcc_form499) [t=1.384191 coef/se=1.384191]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: fcc_form499) [p=0.167253 implied=0.167253 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: health_breach) [t=-0.043459 coef/se=-0.043459]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: health_breach) [p=0.965362 implied=0.965362 df=324]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: prior_events) [t=-0.242141 coef/se=-0.242141]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: prior_events) [p=0.808824 implied=0.808824 df=324]

M4 + breach controls (HEADLINE): N=333 df_resid=324 R2=0.3035
  M4 + breach controls (HEADLINE) :: fcc_form499: coef +0.1863  SE 0.1346  t +1.384  df 324  p 0.1673  N 333
ASSERT PASS â€” t == coef/se (MAIN EFFECT (M4, HC3)) [t=1.384191 coef/se=1.384191]
ASSERT PASS â€” p follows from t and df (MAIN EFFECT (M4, HC3)) [p=0.167253 implied=0.167253 df=324]

HEADLINE: MAIN EFFECT (M4, HC3): coef +0.1863  SE 0.1346  t +1.384  df 324  p 0.1673  N 333
ASSERT PASS â€” t == coef/se (MAIN EFFECT (untrimmed delay)) [t=1.389121 coef/se=1.389121]
ASSERT PASS â€” p follows from t and df (MAIN EFFECT (untrimmed delay)) [p=0.165750 implied=0.165750 df=324]
ASSERT PASS â€” t == coef/se (delay (winsorized p99)) [t=-0.026520 coef/se=-0.026520]
ASSERT PASS â€” p follows from t and df (delay (winsorized p99)) [p=0.978859 implied=0.978859 df=324]
ASSERT PASS â€” t == coef/se (delay (untrimmed)) [t=-0.322927 coef/se=-0.322927]
ASSERT PASS â€” p follows from t and df (delay (untrimmed)) [p=0.746959 implied=0.746959 df=324]

Winsorization rule: delay capped at in-sample p99 = 785 days (documented). Clock note: 47 CFR 64.2011(b) starts its seven-BUSINESS-day law-enforcement clock at "reasonable determination" of the breach, not discovery, and customer notice waits a further seven business days; days_to_disclosure here is reported_date minus breach OCCURRENCE date, which measures neither statutory clock â€” it proxies total public-notification lag, and the theory should be read against that. With vs without winsorization:
  MAIN EFFECT (M4, HC3): coef +0.1863  SE 0.1346  t +1.384  df 324  p 0.1673  N 333
  MAIN EFFECT (untrimmed delay): coef +0.1877  SE 0.1351  t +1.389  df 324  p 0.1657  N 333
  delay (winsorized p99): coef -0.0000  SE 0.0003  t -0.027  df 324  p 0.9789  N 333
  delay (untrimmed): coef -0.0001  SE 0.0002  t -0.323  df 324  p 0.7470  N 333

SE specifications for the M4 treatment coefficient (the old draft scaled every t by 0.8806 â€” coef and t/p came from different runs; here each row is one fit):
ASSERT PASS â€” t == coef/se (classical OLS) [t=1.324027 coef/se=1.324027]
ASSERT PASS â€” p follows from t and df (classical OLS) [p=0.186427 implied=0.186427 df=324]
ASSERT PASS â€” t == coef/se (HC1) [t=1.404560 coef/se=1.404560]
ASSERT PASS â€” p follows from t and df (HC1) [p=0.161110 implied=0.161110 df=324]
ASSERT PASS â€” t == coef/se (HC3) [t=1.384191 coef/se=1.384191]
ASSERT PASS â€” p follows from t and df (HC3) [p=0.167253 implied=0.167253 df=324]
ASSERT PASS â€” t == coef/se (firm-clustered) [t=0.934146 coef/se=0.934146]
ASSERT PASS â€” p follows from t and df (firm-clustered) [p=0.353005 implied=0.353005 df=81]
ASSERT PASS â€” t == coef/se (industry-clustered (N=333)) [t=1.128460 coef/se=1.128460]
ASSERT PASS â€” p follows from t and df (industry-clustered (N=333)) [p=0.270280 implied=0.270280 df=24]
  classical OLS: coef +0.1863  SE 0.1407  t +1.324  df 324  p 0.1864  N 333
  HC1: coef +0.1863  SE 0.1326  t +1.405  df 324  p 0.1611  N 333
  HC3: coef +0.1863  SE 0.1346  t +1.384  df 324  p 0.1673  N 333
  firm-clustered: coef +0.1863  SE 0.1994  t +0.934  df 81  p 0.3530  N 333  clusters=82
  industry-clustered (N=333): coef +0.1863  SE 0.1651  t +1.128  df 24  p 0.2703  N 333  clusters=25
  Cluster counts: firm 82 (meets the ~40-50 convention), industry 25 2-digit-SIC clusters (BELOW the conventional ~40-50 threshold for asymptotic cluster-robust inference â€” treat industry-clustered p with caution).

==========================================================================================
PHASE D â€” FIRM-SIZE HETEROGENEITY (quartiles of log total assets)
==========================================================================================
ASSERT PASS â€” t == coef/se (quartile Q1 (smallest)) [t=-3.163611 coef/se=-3.163611]
ASSERT PASS â€” p follows from t and df (quartile Q1 (smallest)) [p=0.002221 implied=0.002221 df=78]
  quartile Q1 (smallest): coef -1.0004  SE 0.3162  t -3.164  df 78  p 0.0022  N 86  treated 2 obs / 1 orgs / 1 parent CIKs  MDE80 0.89pp  FEWER THAN 5 TREATED PARENT CIKs (1) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q2) [t=0.997380 coef/se=0.997380]
ASSERT PASS â€” p follows from t and df (quartile Q2) [p=0.321920 implied=0.321920 df=72]
  quartile Q2: coef +0.3216  SE 0.3225  t +0.997  df 72  p 0.3219  N 81  treated 14 obs / 8 orgs / 4 parent CIKs  MDE80 0.90pp  FEWER THAN 5 TREATED PARENT CIKs (4) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q3) [t=2.344455 coef/se=2.344455]
ASSERT PASS â€” p follows from t and df (quartile Q3) [p=0.021741 implied=0.021741 df=74]
  quartile Q3: coef +0.7560  SE 0.3225  t +2.344  df 74  p 0.0217  N 83  treated 29 obs / 13 orgs / 4 parent CIKs  MDE80 0.90pp  FEWER THAN 5 TREATED PARENT CIKs (4) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q4 (largest)) [t=1.889915 coef/se=1.889915]
ASSERT PASS â€” p follows from t and df (quartile Q4 (largest)) [p=0.062686 implied=0.062686 df=74]
  quartile Q4 (largest): coef +0.3485  SE 0.1844  t +1.890  df 74  p 0.0627  N 83  treated 59 obs / 19 orgs / 5 parent CIKs  MDE80 0.52pp  
ASSERT PASS â€” quartile Ns sum to full sample N [333 == 333]

Prior-breach count reconstruction (records vs events â€” substantive finding, not a silent fix):
                                                                                 measure   n  mean    sd  p50  p90  max
                                   NEW: prior deduplicated events (canonical, regressor) 333 12.69 18.31  4.0 41.8   75
OLD-STYLE regenerated: prior notification RECORDS (sum n_source_records of prior events) 333 17.12 23.86  5.0 53.0   94
        OLD DRAFT (quoted, NOT regenerable: computed on pre-dedup records, N=891 sample) 891  3.65   NaN  NaN  NaN   68
NOTE: the canonical count is per PARENT CIK (post entity-resolution), so large carrier families accumulate more prior events than the old org-name-string count even after dedup â€” the two differences (dedup, parent aggregation) move in opposite directions.

==========================================================================================
PHASE E â€” MODERATORS AND ROBUSTNESS
==========================================================================================
                         moderator          status n                                                                                                                                                                                                                                 reason
          Breach complexity (CVSS) NOT REGENERABLE 0 NVD/CVSS columns and scripts (99, 105) retired at Rebuild Stage 0; no CVE linkage exists in CANONICAL_V3. The old claim that this ran on the full N=891 while being defined only for CVE-linked breaches was internally contradictory.
                    Media coverage NOT REGENERABLE 0                                                                                                       Constructed on the pre-audit dataset (script 101); source columns absent from CANONICAL_V3; no committed pipeline produces them.
Governance quality (SOX 404 proxy) NOT REGENERABLE 0                                                                                                                                                                                Old-draft construct; no source data in canonical chain.
 Information-environment composite NOT REGENERABLE 0                                                  Script 106 construct on pre-audit base. The old draft reported p=.275 in prose vs p=.0589 in the table for this interaction â€” neither value survives; retired, not carried forward.
               Reputation weakness NOT REGENERABLE 0                                                                                        Old-draft construct (its table row also printed R2=.0156 against ~.39 for every other row â€” a different-model artifact); no canonical source.
ASSERT PASS â€” t == coef/se (year FE) [t=1.155486 coef/se=1.155486]
ASSERT PASS â€” p follows from t and df (year FE) [p=0.248790 implied=0.248790 df=307]
  year FE: coef +0.1794  SE 0.1553  t +1.155  df 307  p 0.2488  N 333  R2=0.4172
ASSERT PASS â€” t == coef/se (industry FE (2-digit SIC)) [t=2.138509 coef/se=2.138509]
ASSERT PASS â€” p follows from t and df (industry FE (2-digit SIC)) [p=0.033283 implied=0.033283 df=300]
  industry FE (2-digit SIC): coef +0.3963  SE 0.1853  t +2.139  df 300  p 0.0333  N 333  R2=0.3606
ASSERT PASS â€” t == coef/se (year + industry FE) [t=1.055577 coef/se=1.055577]
ASSERT PASS â€” p follows from t and df (year + industry FE) [p=0.292062 implied=0.292062 df=283]
  year + industry FE: coef +0.2086  SE 0.1976  t +1.056  df 283  p 0.2921  N 333  R2=0.4821
  Identification check: the combined year+industry FE treatment coefficient is IDENTIFIED (SE finite at 0.198) â€” an improvement over the old draft, whose combined specification collapsed because SIC-based treatment was a function of three SIC codes. BUT the identification is THIN: only 2 of 25 2-digit-SIC cells contain both treated and control events, so the within-industry comparison rests on those 2 cells. The industry-FE-only estimate (p=0.0333) leans on the same thin variation and on 25 clusters (below the ~40-50 convention) â€” do not headline it.

VIF (M4 design):
     variable  VIF
      delay_w 1.05
    e2_pre_sd 1.16
firm_size_log 1.68
     leverage 1.11
          roa 1.48
  fcc_form499 1.65
health_breach 1.09
 prior_events 1.41

Breusch-Pagan (stated ONCE, used everywhere): chi2(8) = 10.0768, p = 0.2597. (The old draft printed chi2=3.92/p=.049 in prose and 15.5838/p=.0487 in its table â€” both retired.)
Jarque-Bera residual normality: JB = 2007.5, p = 0.00e+00, skew 2.56, kurtosis 13.89 â€” heavy-tailed; HC3 primary inference stands, normality rejected as expected for volatility data.
ASSERT PASS â€” t == coef/se (M4 excl. Cook's D > 4/N (17 obs)) [t=1.275787 coef/se=1.275787]
ASSERT PASS â€” p follows from t and df (M4 excl. Cook's D > 4/N (17 obs)) [p=0.202995 implied=0.202995 df=307]

Influence: 17 obs with Cook's D > 4/N (0.0120); 17 with |DFFITS| > 0.329.
  M4 excl. Cook's D > 4/N (17 obs): coef +0.1172  SE 0.0918  t +1.276  df 307  p 0.2030  N 316

GARCH(1,1) conditional-volatility DV (Gaussian MLE, Nelder-Mead; estimation window trading days [-250,+25] around the anchor, min 200 obs; DV = mean conditional SD over [+5,+25] minus [-25,-5], daily pp):
ASSERT PASS â€” t == coef/se (GARCH(1,1) DV (N=330)) [t=0.830762 coef/se=0.830762]
ASSERT PASS â€” p follows from t and df (GARCH(1,1) DV (N=330)) [p=0.406726 implied=0.406726 df=321]
  GARCH(1,1) DV (N=330): coef +0.0600  SE 0.0722  t +0.831  df 321  p 0.4067  N 330
ASSERT PASS â€” t == coef/se (canonical DV, HC3 (N=333)) [t=2.273994 coef/se=2.273994]
ASSERT PASS â€” p follows from t and df (canonical DV, HC3 (N=333)) [p=0.023620 implied=0.023620 df=324]
ASSERT PASS â€” t == coef/se (canonical DV, firm-clustered) [t=1.812227 coef/se=1.812227]
ASSERT PASS â€” p follows from t and df (canonical DV, firm-clustered) [p=0.073657 implied=0.073657 df=81]

DV-convention sensitivity (canonical breach-anchored annualized DV, the convention the old CODE actually used, on THIS sample and control set; corr with the draft-spec DV = 0.451):
  canonical DV, HC3 (N=333): coef +4.2595  SE 1.8731  t +2.274  df 324  p 0.0236  N 333
  canonical DV, firm-clustered: coef +4.2595  SE 2.3504  t +1.812  df 81  p 0.0737  N 333  clusters=82
  Under the old code's convention the effect is +4.26 annualized pp (p=0.0236 HC3) but dies under firm clustering (p=0.0737) â€” the same pattern as the v3 baseline H5 (Essay 2's hypothesis in constants_v3: +3.29, p=.063, estimated under this same breach-anchored convention).

  Breach-to-notification delay (N=333): min 0 | p10 0 | p25 0 | median 23 | p75 80 | p90 201 | max 1917 | mean 79.8 | SD 175.2
  all: window fully pre-notification 45.3% | contains notification 54.7% | mean 56.4% (median 74.2%) of window days precede notification
  treated: window fully pre-notification 47.1% | contains notification 52.9% | mean 53.7% (median 71.0%) of window days precede notification
  control: window fully pre-notification 44.5% | contains notification 55.5% | mean 57.6% (median 77.4%) of window days precede notification
  CONSTRUCT VERDICT: a strict majority of observations does NOT have the window close before notification (45.6% do), but a majority of what the measure contains is pre-notification volatility â€” 56.7% of all measured post-window days precede public notification, and the median observation has 74% of its "post" window before the market learned anything. The breach-anchored DV is disqualified as a measure of post-DISCLOSURE uncertainty on construct validity: it mostly measures volatility before the event it claims to measure. The treated/control difference in truncation is trivial (47.1% vs 45.0% fully-pre; treated windows contain slightly MORE post-notification days, 46.3% vs 42.0%), so there is no mechanical treatment-correlated measurement bias on top â€” the disqualification is construct-wide, not treatment-differential.

==========================================================================================
PHASE F â€” INFERENCE QUALITY
==========================================================================================
  MAIN EFFECT (M4, HC3): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.6557  MDE80=0.3768pp  -> NULL â€” UNDERPOWERED (inconclusive)
  quartile Q1 (smallest): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.9962  MDE80=0.8855pp  -> SIGNIFICANT [1 treated parent CIKs â€” do not interpret bare]
  quartile Q2: TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.7205  MDE80=0.9029pp  -> NULL â€” UNDERPOWERED (inconclusive) [4 treated parent CIKs â€” do not interpret bare]
  quartile Q3: TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.9715  MDE80=0.9029pp  -> SIGNIFICANT [4 treated parent CIKs â€” do not interpret bare]
  quartile Q4 (largest): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.8776  MDE80=0.5163pp  -> NULL â€” UNDERPOWERED (inconclusive)

  BOUND PROVENANCE: the Â±2.10pp bound was pre-specified for Essay 1's CAR outcome ("fixed from literature before rebuilt estimates existed", scripts/158) and was never independently justified as a smallest volatility effect of interest â€” its use here is a unit conversion only, stated as such.
  LITERATURE-ANCHORED CHECK (conditional): against a candidate SESOI of 4.2pp annualized (0.2646 daily pp), TOST p=0.2805 â€” still not equivalence-bounded. MDE80 = 0.3768 daily pp = 5.98pp annualized, which EXCEEDS 4.2pp: this design cannot detect, at 80% power, even the effect size used as the literature anchor. CAVEAT: the 4.2pp figure attributed to Obaydin, Xu & Zurbruegg (2024) could not be verified in the repository's article summary â€” their JBFA 2024 paper reports crash-risk effects (NSKEW/DUVOL/COUNT, >=5% of a SD) and bad-news-hoarding proxies, not a post-breach volatility change in pp. No commensurable volatility-native SESOI has been located in the prior literature on file; until one is, the defensible sentence is the MDE one, not any TOST verdict.

Economic significance: main effect +0.1863 daily pp = +11.0% of mean post-breach volatility (1.6872 daily pp). Incremental R2 from the treatment indicator: +0.0038 (M4 0.3035 vs without-treatment 0.2998). (Old draft: .3922 vs .3896 â€” about a quarter of one percent.)

==========================================================================================
OLD-DRAFT LEAK CHECK AND CODEBASE FLAGS
==========================================================================================
No regenerated coefficient reproduces any old-draft value (+1.83, +7.31, +3.64, -3.39, -0.54, +1.763, +2.48, +4.074, +1.894, +0.7956) to within 0.005 â€” no evidence of old-number leakage.

FORENSIC â€” old-draft provenance closure (nothing here is a result; pre-dedup data, SIC-based fcc_reportable treatment, both retired):
  N=891 (reproduces the old draft's 891 exactly from the PRE-dedup ENRICHED file) | main FCC +1.6121 p=0.0772 (old draft: +1.83 / +1.763)
  Q1: +7.6515 (p=0.0060, N=229) vs old draft +7.31
  Q2: +2.8621 (p=0.0725, N=224) vs old draft +3.64
  Q3: -2.0526 (p=0.3707, N=215) vs old draft -0.54
  Q4: -3.5119 (p=0.0236, N=223) vs old draft -3.39
  The +7.31/+3.64/-0.54/-3.39 step-down REPRODUCES in sign, ordering, and approximate magnitude (+7.65/+2.86/-2.05/-3.51 under the full old control set) â€” the old quartile numbers are the pre-deduplication + SIC-treatment artifact, not a third-source mystery. Provenance closed. On corrected data the pattern does not exist (Phase D).

Codebase flags (directive): "September 28 2007"/"Rule 37.3" and SIC-code treatment (4813/4841/4899) appear ONLY in retired pre-rebuild scripts (83, 94, 20, build_essay1_*, create_*, scm_*, fix/rebuild_essay1_appendix, boost_mobile_forensics, consolidate_validation_results, and chronology-side scripts 131/137) and in script 142's note deliberately documenting the retirement. NO live v3-chain script (150-158) or this script assigns treatment by SIC or references the wrong date/rule.

==========================================================================================
PIPELINE FINDINGS (item 5 â€” things not already named in the directive)
==========================================================================================
1. FINAL_DATASET_ORIGINAL_1054.csv contained 784 rows, not 1,054 â€” misnamed
   (a vintage of the retired dedup set; script 142's docstring had already
   documented this). RENAMED 8/30/2026 to
   FINAL_DATASET_ORIGINAL_1054_MISNAMED_RETIRED.csv; no script reads it; the
   true 1,054-record universe is rebuild/stage2_signed.csv (and
   master_breach_dataset.xlsx).
2. has_crsp_data in CANONICAL_V3 is defined by car_30d computability
   (breach-anchored), not by security match: 5 events carry a
   permno but has_crsp_data = 0. Essay 2's notification-anchored windows are
   computable for some of these, so this rerun keys on permno + its own
   window requirement rather than reusing has_crsp_data â€” the two essays'
   CRSP samples overlap but are not nested.
3. The canonical prior-breach count is per PARENT CIK (post entity
   resolution), so carrier families accumulate more prior events (mean
   12.7 in this sample) than the old org-string
   count even after deduplication removed the Cencora-style record inflation.
   The regressor's semantics changed twice, in opposite directions.
4. The timing regressor is dead in every specification (|t| < 0.25 with and
   without winsorization): with corrected dates and the 8/17 wrong-field
   fixes, disclosure delay carries no volatility information at all. The old
   draft's timing narrative has no support in the corrected data.
5. Form 499 treatment concentrates in 2 mixed 2-digit-SIC cells;
   industry FE/clustered specifications are technically identified but rest
   on very thin within-industry variation (25 industry clusters,
   below the ~40-50 convention).
6. The old draft's N = 891 REPRODUCES EXACTLY from
   FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 rows, PRE-deduplication,
   926 CRSP) under the old spec's dropna â€” the old Essay 2 ran on duplicate
   notification records and pre-resolution identities.
7. The old Essay 2 CODE never implemented the draft's stated volatility
   windows: scripts 20/90/90b used the breach-anchored annualized
   [-40,-1]/[0,+30] convention; the [-25,-5]/[+5,+25] language exists only
   in create_regression_formulas_document.py, the same file that carries
   "Rule 37.3", SIC-code treatment, and "January 1, 2007" (a THIRD wrong
   rule date). The draft's methods prose described a measure that was never
   computed. See the DV-convention sensitivity in Phase E.

Total reconciliation/consistency assertions passed: 131
