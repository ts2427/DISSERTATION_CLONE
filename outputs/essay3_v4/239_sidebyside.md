# REBUILD V4 - v3-overlap sensitivity and the v3 vs v4 side-by-side

## v3-overlap sensitivity
All treated events kept; control restricted to events also linked in v3.

full v4 sample    : n 405 (treated 109, control 296)
v3-overlap sample : n 347 (treated 109, control 238)
control events dropped: 58

 window     sample   n    coef  se_cv3  p_cv3  ci_cv3_lo  ci_cv3_hi  p_wcr
     30    full v4 405  0.0040  0.0334 0.9061    -0.0623     0.0702 0.8889
     30 v3-overlap 347  0.0177  0.0323 0.5850    -0.0465     0.0819 0.4656
     90    full v4 405 -0.0410  0.0791 0.6053    -0.1976     0.1156 0.5136
     90 v3-overlap 347 -0.0345  0.1000 0.7313    -0.2334     0.1645 0.6213
    180    full v4 405  0.0233  0.0996 0.8159    -0.1740     0.2206 0.7901
    180 v3-overlap 347  0.0208  0.1111 0.8521    -0.2001     0.2417 0.8181

## Verdicts, v3 vs v4
                         test vintage   n    coef  p_cv3  p_wcr  mde80                      verdict
        H6 exec departure 30d      v3 338  0.0168 0.6118 0.4924 0.0934 NULL (fail to reject at .05)
        H6 exec departure 30d      v4 405  0.0040 0.9061 0.8889 0.0944 NULL (fail to reject at .05)
        H6 exec departure 90d      v3 338 -0.0169 0.8701 0.8154 0.2918 NULL (fail to reject at .05)
        H6 exec departure 90d      v4 405 -0.0410 0.6053 0.5136 0.2234 NULL (fail to reject at .05)
       H6 exec departure 180d      v3 338  0.0434 0.7052 0.6474 0.3245 NULL (fail to reject at .05)
       H6 exec departure 180d      v4 405  0.0233 0.8159 0.7901 0.2815 NULL (fail to reject at .05)
F4 placebo (pre-notification)      v3 338 -0.0658 0.5281 0.4060 0.2945 NULL (fail to reject at .05)
F4 placebo (pre-notification)      v4 405 -0.0862 0.3116 0.2308 0.2397 NULL (fail to reject at .05)

verdicts that differ between v3 and v4: 0

## Constants, v3 vs v4
              constant                                     v3                                     v4  status
          F1_180_B_wcr                                  99999                                  99999    same
              F1_180_G                                     81                                    119 DIFFERS
             F1_180_G1                                     12                                     13 DIFFERS
         F1_180_G_star                                   23.6                                   24.5 DIFFERS
      F1_180_ci_cv3_hi                                 0.2711                                 0.2206 DIFFERS
      F1_180_ci_cv3_lo                                -0.1842                                 -0.174 DIFFERS
      F1_180_ci_wcr_hi                                 0.2352                                 0.2011 DIFFERS
      F1_180_ci_wcr_lo                                -0.1563                                -0.1576 DIFFERS
F1_180_cluster_size_cv                                  2.267                                  2.328 DIFFERS
           F1_180_coef                                 0.0434                                 0.0233 DIFFERS
   F1_180_control_mean                                 0.2511                                 0.2466 DIFFERS
      F1_180_mde80_cv3                                 0.3245                                 0.2815 DIFFERS
              F1_180_n                                    338                                    405 DIFFERS
          F1_180_p_cv1                                  0.607                                 0.7668 DIFFERS
          F1_180_p_cv3                                 0.7052                                 0.8159 DIFFERS
          F1_180_p_hc3                                 0.5158                                 0.7034 DIFFERS
          F1_180_p_wcr                                 0.6474                                 0.7901 DIFFERS
         F1_180_se_cv1                                 0.0841                                 0.0782 DIFFERS
         F1_180_se_cv3                                 0.1144                                 0.0996 DIFFERS
         F1_180_se_hc3                                 0.0668                                  0.061 DIFFERS
   F1_180_treated_mean                                 0.3178                                 0.3028 DIFFERS
         F1_180_window                                    180                                    180    same
           F1_30_B_wcr                                  99999                                  99999    same
               F1_30_G                                     81                                    119 DIFFERS
              F1_30_G1                                     12                                     13 DIFFERS
          F1_30_G_star                                   23.6                                   24.5 DIFFERS
       F1_30_ci_cv3_hi                                 0.0823                                 0.0702 DIFFERS
       F1_30_ci_cv3_lo                                -0.0487                                -0.0623 DIFFERS
       F1_30_ci_wcr_hi                                 0.0621                                 0.0578 DIFFERS
       F1_30_ci_wcr_lo                                -0.0336                                -0.0553 DIFFERS
 F1_30_cluster_size_cv                                  2.267                                  2.328 DIFFERS
            F1_30_coef                                 0.0168                                  0.004 DIFFERS
    F1_30_control_mean                                 0.0433                                 0.0439 DIFFERS
       F1_30_mde80_cv3                                 0.0934                                 0.0944 DIFFERS
               F1_30_n                                    338                                    405 DIFFERS
           F1_30_p_cv1                                  0.395                                  0.873 DIFFERS
           F1_30_p_cv3                                 0.6118                                 0.9061 DIFFERS
           F1_30_p_hc3                                 0.4703                                 0.8764 DIFFERS
           F1_30_p_wcr                                 0.4924                                 0.8889 DIFFERS
          F1_30_se_cv1                                 0.0196                                 0.0247 DIFFERS
          F1_30_se_cv3                                 0.0329                                 0.0334 DIFFERS
          F1_30_se_hc3                                 0.0232                                 0.0254 DIFFERS
    F1_30_treated_mean                                 0.0374                                 0.0367 DIFFERS
          F1_30_window                                     30                                     30    same
           F1_90_B_wcr                                  99999                                  99999    same
               F1_90_G                                     81                                    119 DIFFERS
              F1_90_G1                                     12                                     13 DIFFERS
          F1_90_G_star                                   23.6                                   24.5 DIFFERS
       F1_90_ci_cv3_hi                                 0.1879                                 0.1156 DIFFERS
       F1_90_ci_cv3_lo                                -0.2217                                -0.1976 DIFFERS
       F1_90_ci_wcr_hi                                  0.127                                 0.0805 DIFFERS
       F1_90_ci_wcr_lo                                -0.1517                                -0.1596 DIFFERS
 F1_90_cluster_size_cv                                  2.267                                  2.328 DIFFERS
            F1_90_coef                                -0.0169                                 -0.041 DIFFERS
    F1_90_control_mean                                 0.1602                                 0.1453 DIFFERS
       F1_90_mde80_cv3                                 0.2918                                 0.2234 DIFFERS
               F1_90_n                                    338                                    405 DIFFERS
           F1_90_p_cv1                                 0.7698                                 0.4128 DIFFERS
           F1_90_p_cv3                                 0.8701                                 0.6053 DIFFERS
           F1_90_p_hc3                                 0.7212                                 0.3445 DIFFERS
           F1_90_p_wcr                                 0.8154                                 0.5136 DIFFERS
          F1_90_se_cv1                                 0.0575                                 0.0499 DIFFERS
          F1_90_se_cv3                                 0.1029                                 0.0791 DIFFERS
          F1_90_se_hc3                                 0.0473                                 0.0433 DIFFERS
    F1_90_treated_mean                                 0.1121                                 0.1009 DIFFERS
          F1_90_window                                     90                                     90    same
              F4_B_wcr                                  99999                                  99999    same
                  F4_G                                     81                                    119 DIFFERS
                 F4_G1                                     12                                     13 DIFFERS
             F4_G_star                                   23.6                                   24.5 DIFFERS
          F4_ci_cv3_hi                                 0.1408                                 0.0818 DIFFERS
          F4_ci_cv3_lo                                -0.2724                                -0.2543 DIFFERS
          F4_ci_wcr_hi                                 0.0962                                 0.0592 DIFFERS
          F4_ci_wcr_lo                                -0.2188                                -0.2324 DIFFERS
    F4_cluster_size_cv                                  2.267                                  2.328 DIFFERS
               F4_coef                                -0.0658                                -0.0862 DIFFERS
       F4_control_mean                                 0.2035                                 0.2365 DIFFERS
          F4_mde80_cv3                                 0.2945                                 0.2397 DIFFERS
                  F4_n                                    338                                    405 DIFFERS
              F4_p_cv1                                 0.3496                                 0.1867 DIFFERS
              F4_p_cv3                                 0.5281                                 0.3116 DIFFERS
              F4_p_hc3                                 0.2539                                 0.1244 DIFFERS
              F4_p_wcr                                  0.406                                 0.2308 DIFFERS
             F4_se_cv1                                 0.0699                                 0.0649 DIFFERS
             F4_se_cv3                                 0.1038                                 0.0849 DIFFERS
             F4_se_hc3                                 0.0576                                  0.056 DIFFERS
       F4_treated_mean                                 0.2243                                 0.2294 DIFFERS
                     N                                    338                                    405 DIFFERS
            classifier scripts/195 v2 (6f7be7a, blob ec32364) scripts/195 v2 (6f7be7a, blob ec32364)    same
               control                                    231                                    296 DIFFERS
               n_tests                                     31                                     31    same
           parent_ciks                                     81                                    119 DIFFERS
               treated                                    107                                    109 DIFFERS
   treated_parent_ciks                                     12                                     13 DIFFERS

constants that differ: 85 of 94

written 239_v3_overlap_sensitivity.csv, 239_v3_vs_v4_constants.csv
