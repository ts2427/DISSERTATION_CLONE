# Item 4: what the Essay 2 v5 TOST p-values .047 and .390 test

Both p-values are the two one-sided tests (TOST) on the primary estimate. Read-only lookup; nothing recomputed.

**Primary estimate**
- Coefficient: the Form 499 registrant coefficient in model M4. M4 is OLS with the pre-window level, the disclosure gap, log total assets, leverage, ROA, the health-breach flag and prior breach events.
- Sample: N = 333 events, 104 treated events, G = 82 parent filer entities.
- Outcome: the change in the SD of daily market-adjusted returns (RET − vwretd, in daily percentage points), from [−60, −11] to [+1, +20].
- Rung: CV3, the cluster jackknife SE by parent filer entity. The coefficient b = 0.13667 and SE_CV3 = 0.19314. Both tests use the t distribution with G − 1 = 81 df.

**Bound (SESOI)**
- SESOI = 0.25 × SD of the outcome among control events = 0.25 × 0.76283 = **±0.19071 daily pp**.
- Annualized this is ±3.027 pp (× √252).

| p | Test | Null hypothesis | Statistic | Reading | File and key |
|:---|:---|:---|:---|:---|:---|
| **.047** (0.046957) | Lower one-sided test | H0: β ≤ −0.19071, a meaningfully negative effect | p = 1 − F_t81((b + SESOI)/SE_CV3) | Rejects at .05: a negative effect of SESOI size or larger is ruled out | outputs/essay2_v5/constants_essay2.json `values.dr_tost_p_lower`; appendix/20_design_resolution.csv `tost_p_lower` (= v5_t04_design_resolution.csv) |
| **.390** (0.390181) | Upper one-sided test | H0: β ≥ +0.19071, a meaningfully positive effect | p = F_t81((b − SESOI)/SE_CV3) | Does not reject: a positive effect of SESOI size or larger stays open | constants `values.dr_tost_p_upper`; appendix/20 `tost_p_upper` |

**Overall result:** the TOST p-value is the larger of the two, .390, so equivalence within ±SESOI is not established. This agrees with constants `dr_ci90_inside_sesoi` = False: the 90% CI is [−0.185, 0.458] (appendix/20 `ci90_lo`, `ci90_hi`).

**Code**
- scripts/263_e2v5_lib.py, `design_resolution()`, lines 364–389: `sesoi_mult = 0.25`, `tost_p_lower`, `tost_p_upper`.
- Called from scripts/264_e2v5_primary.py, section 6, lines 165–169. `sd_ctrl` there is the SD of `dv` among control events.

**Not to be confused with** the CAR-based TOST in the same constants file. That one is set by scripts/272: `tost_car_p_lower` = .084, `tost_car_p_upper` = .509, bound `sesoi_car_ann` = 2.1.
