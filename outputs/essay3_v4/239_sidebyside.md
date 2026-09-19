# REBUILD V4 - v3-overlap sensitivity and the v3 vs v4 side-by-side

## v3-overlap sensitivity
All treated events kept; control restricted to events also linked in v3.

full v4 sample    : n 405 (treated 109, control 296)
v3-overlap sample : n 347 (treated 109, control 238)
control events dropped: 58

 window     sample   n    coef  se_cv3  p_cv3  ci_cv3_lo  ci_cv3_hi  p_wcr
     30    full v4 405  0.0031  0.0338 0.9272    -0.0639     0.0701 0.9143
     30 v3-overlap 347  0.0175  0.0322 0.5881    -0.0466     0.0817 0.4817
     90    full v4 405 -0.0252  0.0824 0.7603    -0.1884     0.1380 0.7017
     90 v3-overlap 347 -0.0160  0.1028 0.8768    -0.2204     0.1885 0.8253
    180    full v4 405  0.0383  0.1000 0.7026    -0.1598     0.2364 0.6616
    180 v3-overlap 347  0.0351  0.1124 0.7555    -0.1884     0.2587 0.6997

## Constants, v3 vs v4
              constant                                     v3                                     v4  status
          F1_180_B_wcr                                  99999                                  99999    same
              F1_180_G                                     81                                    119 DIFFERS
             F1_180_G1                                     12                                     13 DIFFERS
         F1_180_G_star                                   23.6                                   24.5 DIFFERS
      F1_180_ci_cv3_hi                                 0.2711                                 0.2364 DIFFERS
      F1_180_ci_cv3_lo                                -0.1842                                -0.1598 DIFFERS
      F1_180_ci_wcr_hi                                 0.2352                                 0.2159 DIFFERS
      F1_180_ci_wcr_lo                                -0.1563                                -0.1451 DIFFERS
F1_180_cluster_size_cv                                  2.267                                  2.328 DIFFERS
           F1_180_coef                                 0.0434                                 0.0383 DIFFERS
   F1_180_control_mean                                 0.2511                                 0.2466 DIFFERS
      F1_180_mde80_cv3                                 0.3245                                 0.2826 DIFFERS
              F1_180_n                                    338                                    405 DIFFERS
          F1_180_p_cv1                                  0.607                                 0.6257 DIFFERS
          F1_180_p_cv3                                 0.7052                                 0.7026 DIFFERS
          F1_180_p_hc3                                 0.5158                                 0.5374 DIFFERS
          F1_180_p_wcr                                 0.6474                                 0.6616 DIFFERS
         F1_180_se_cv1                                 0.0841                                 0.0783 DIFFERS
         F1_180_se_cv3                                 0.1144                                    0.1 DIFFERS
         F1_180_se_hc3                                 0.0668                                  0.062 DIFFERS
   F1_180_treated_mean                                 0.3178                                 0.3119 DIFFERS
         F1_180_window                                    180                                    180    same
           F1_30_B_wcr                                  99999                                  99999    same
               F1_30_G                                     81                                    119 DIFFERS
              F1_30_G1                                     12                                     13 DIFFERS
          F1_30_G_star                                   23.6                                   24.5 DIFFERS
       F1_30_ci_cv3_hi                                 0.0823                                 0.0701 DIFFERS
       F1_30_ci_cv3_lo                                -0.0487                                -0.0639 DIFFERS
       F1_30_ci_wcr_hi                                 0.0621                                 0.0575 DIFFERS
       F1_30_ci_wcr_lo                                -0.0336                                -0.0571 DIFFERS
 F1_30_cluster_size_cv                                  2.267                                  2.328 DIFFERS
            F1_30_coef                                 0.0168                                 0.0031 DIFFERS
    F1_30_control_mean                                 0.0433                                 0.0439 DIFFERS
       F1_30_mde80_cv3                                 0.0934                                 0.0956 DIFFERS
               F1_30_n                                    338                                    405 DIFFERS
           F1_30_p_cv1                                  0.395                                 0.9019 DIFFERS
           F1_30_p_cv3                                 0.6118                                 0.9272 DIFFERS
           F1_30_p_hc3                                 0.4703                                 0.9041 DIFFERS
           F1_30_p_wcr                                 0.4924                                 0.9143 DIFFERS
          F1_30_se_cv1                                 0.0196                                 0.0251 DIFFERS
          F1_30_se_cv3                                 0.0329                                 0.0338 DIFFERS
          F1_30_se_hc3                                 0.0232                                 0.0257 DIFFERS
    F1_30_treated_mean                                 0.0374                                 0.0367 DIFFERS
          F1_30_window                                     30                                     30    same
           F1_90_B_wcr                                  99999                                  99999    same
               F1_90_G                                     81                                    119 DIFFERS
              F1_90_G1                                     12                                     13 DIFFERS
          F1_90_G_star                                   23.6                                   24.5 DIFFERS
       F1_90_ci_cv3_hi                                 0.1879                                  0.138 DIFFERS
       F1_90_ci_cv3_lo                                -0.2217                                -0.1884 DIFFERS
       F1_90_ci_wcr_hi                                  0.127                                 0.1054 DIFFERS
       F1_90_ci_wcr_lo                                -0.1517                                -0.1496 DIFFERS
 F1_90_cluster_size_cv                                  2.267                                  2.328 DIFFERS
            F1_90_coef                                -0.0169                                -0.0252 DIFFERS
    F1_90_control_mean                                 0.1602                                 0.1453 DIFFERS
       F1_90_mde80_cv3                                 0.2918                                 0.2328 DIFFERS
               F1_90_n                                    338                                    405 DIFFERS
           F1_90_p_cv1                                 0.7698                                 0.6419 DIFFERS
           F1_90_p_cv3                                 0.8701                                 0.7603 DIFFERS
           F1_90_p_hc3                                 0.7212                                 0.5718 DIFFERS
           F1_90_p_wcr                                 0.8154                                 0.7017 DIFFERS
          F1_90_se_cv1                                 0.0575                                  0.054 DIFFERS
          F1_90_se_cv3                                 0.1029                                 0.0824 DIFFERS
          F1_90_se_hc3                                 0.0473                                 0.0445 DIFFERS
    F1_90_treated_mean                                 0.1121                                 0.1101 DIFFERS
          F1_90_window                                     90                                     90    same
              F4_B_wcr                                  99999                                  99999    same
                  F4_G                                     81                                    119 DIFFERS
                 F4_G1                                     12                                     13 DIFFERS
             F4_G_star                                   23.6                                   24.5 DIFFERS
          F4_ci_cv3_hi                                 0.1408                                 0.0816 DIFFERS
          F4_ci_cv3_lo                                -0.2724                                -0.2482 DIFFERS
          F4_ci_wcr_hi                                 0.0962                                 0.0591 DIFFERS
          F4_ci_wcr_lo                                -0.2188                                -0.2251 DIFFERS
    F4_cluster_size_cv                                  2.267                                  2.328 DIFFERS
               F4_coef                                -0.0658                                -0.0833 DIFFERS
       F4_control_mean                                 0.2035                                 0.2365 DIFFERS
          F4_mde80_cv3                                 0.2945                                 0.2352 DIFFERS
                  F4_n                                    338                                    405 DIFFERS
              F4_p_cv1                                 0.3496                                 0.1984 DIFFERS
              F4_p_cv3                                 0.5281                                 0.3191 DIFFERS
              F4_p_hc3                                 0.2539                                 0.1383 DIFFERS
              F4_p_wcr                                  0.406                                 0.2388 DIFFERS
             F4_se_cv1                                 0.0699                                 0.0644 DIFFERS
             F4_se_cv3                                 0.1038                                 0.0833 DIFFERS
             F4_se_hc3                                 0.0576                                 0.0561 DIFFERS
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
