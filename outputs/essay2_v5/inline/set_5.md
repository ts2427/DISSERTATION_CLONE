**Table 12**

*Robustness of the Main Estimate*

Panel A: Post-window length

| Post-window | Estimate (CV3 SE) | p | BH-adjusted p | Wild cluster p | 95% CI |
|:---|---:|---:|---:|---:|---:|
| [+1, +5] | 0.198 (0.198) | .320 | .495 | .152 | [−0.196, 0.593] |
| [+1, +10] | 0.193 (0.282) | .495 | .495 | .482 | [−0.369, 0.755] |
| [+1, +20] | 0.137 (0.193) | .481 | .495 | .426 | [−0.248, 0.521] |

Panel B: Return benchmark

| Benchmark | Post-window | Estimate (CV3 SE) | p | N | 95% CI |
|:---|---:|---:|---:|---:|---:|
| Market-adjusted | [+1, +5] | 0.198 (0.198) | .320 | 333 | [−0.196, 0.593] |
| Market-adjusted | [+1, +10] | 0.193 (0.282) | .495 | 333 | [−0.369, 0.755] |
| Market-adjusted | [+1, +20] | 0.137 (0.193) | .481 | 333 | [−0.248, 0.521] |
| Market model | [+1, +5] | 0.180 (0.209) | .391 | 327 | [−0.235, 0.595] |
| Market model | [+1, +10] | 0.191 (0.293) | .516 | 327 | [−0.392, 0.774] |
| Market model | [+1, +20] | 0.156 (0.199) | .436 | 327 | [−0.241, 0.553] |
| Fama–French three-factor | [+1, +5] | 0.228 (0.219) | .303 | 327 | [−0.209, 0.664] |
| Fama–French three-factor | [+1, +10] | 0.223 (0.293) | .448 | 327 | [−0.359, 0.806] |
| Fama–French three-factor | [+1, +20] | 0.173 (0.188) | .361 | 327 | [−0.202, 0.548] |

Panel C: Estimation-window contamination

| Group | Events | Earlier notification in window | Share | Earlier breach date in window | Share |
|:---|---:|---:|---:|---:|---:|
| Form 499 registrant events | 104 | 42 | .40 | 61 | .59 |
| Other events | 229 | 101 | .44 | 134 | .59 |
| All events | 333 | 143 | .43 | 195 | .59 |

Panel D: Events dropped by the 80% coverage rule

| Benchmark and pre-window (all three post-windows) | Dropped | Registrant dropped | Other dropped | Events kept | Parents kept (G) |
|:---|---:|---:|---:|---:|---:|
| Market-adjusted, pre-window [−60, −11] | 0 | 0 | 0 | 333 | 82 |
| Market model, pre-window [−60, −11] | 6 | 1 | 5 | 327 | 80 |
| Fama–French three-factor, pre-window [−60, −11] | 6 | 1 | 5 | 327 | 80 |
| Market-adjusted, pre-window [−45, −11] | 0 | 0 | 0 | 333 | 82 |

Panel E: Alternative pre-window and the bridge from the earlier outcome

| Specification | Estimate (CV3 SE) | p | 95% CI |
|:---|---:|---:|---:|
| Pre-window [−45, −11], post-window [+1, +5], market-adjusted | 0.228 (0.210) | .280 | [−0.190, 0.647] |
| Pre-window [−45, −11], post-window [+1, +10], market-adjusted | 0.209 (0.285) | .465 | [−0.357, 0.776] |
| Pre-window [−45, −11], post-window [+1, +20], market-adjusted | 0.163 (0.198) | .413 | [−0.231, 0.557] |
| Bridge a: raw log returns, [−25, −5] / [+5, +25], committed earlier outcome | 0.212 (0.243) | .386 | [−0.272, 0.696] |
| Bridge b: raw log returns, [−25, −5] / [+5, +25], current calendar and 80% rule | 0.212 (0.243) | .386 | [−0.272, 0.696] |
| Bridge c: market-adjusted simple returns, [−25, −5] / [+5, +25] | 0.178 (0.229) | .440 | [−0.278, 0.633] |
| Bridge d (primary): market-adjusted simple returns, [−60, −11] / [+1, +20] | 0.137 (0.193) | .481 | [−0.248, 0.521] |

*Note.* Each row re-estimates the primary model M4 with one change and reports the Form 499 registrant coefficient, its CV3 standard error (SE) in parentheses, its p-value and its 95 percent confidence interval (CI); the analytical sample has N = 333 events and G = 82 parent filer entities (12 with registrant events) unless the N column shows otherwise. CV3 is the cluster jackknife standard error, clustered by parent filer entity, with p-values from the t distribution with G − 1 degrees of freedom. Panel A varies the post-window, the trading days after the agency reporting date over which volatility is measured, from [+1, +5] to [+1, +20], against the pre-window [−60, −11]. The three windows form one family of 3 tests, and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within that family; the wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. Every window must have at least 80 percent of its trading days with returns, the 80 percent coverage rule. Panel B replaces the market adjustment (RET − vwretd, the stock return minus the value-weighted market return) with abnormal returns from the market model and from the Fama–French three-factor (FF3) model, both estimated over trading days [−250, −30]; 6 events (1 registrant event) drop because their estimation window has less than 80 percent coverage, by organization Cencora, Inc. (3); T-Mobile USA, Inc. (1); Uber Technologies, Inc. (1); Zscaler, Inc. (1), which leaves 327 events and 80 parents. Panel C counts contaminated estimation windows: an estimation window is contaminated when another event at the same parent filer entity falls inside it, counted once by that event’s notification date and once by its breach date. The counts exclude the focal event itself and events in its own Gate 2 chain, after the correction of November 13, 2026 that stopped an event’s own breach date counting against it; across all events the shares are .43 by notification date and .59 by breach date. Panel D lists the coverage-rule drops for each benchmark and pre-window; the primary market-adjusted windows drop no event. Panel E builds the outcome step by step from the earlier construction to the current one: bridge a is the committed earlier outcome, the change in the SD of raw log returns between [−25, −5] and [+5, +25]; bridge b recomputes it on the current trading calendar with the 80 percent rule; bridge c switches to market-adjusted simple returns on the same windows; bridge d moves to the current windows and is the primary estimate. The first rows of Panel E start the pre-window at day −45 instead of −60. No row gives p below .05. SD is the standard deviation; RET and vwretd are from the Center for Research in Security Prices (CRSP).
