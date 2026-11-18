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

Panel E: Alternative pre-window and steps from the earlier outcome

| Specification | Estimate (CV3 SE) | p | 95% CI |
|:---|---:|---:|---:|
| Pre-window [−45, −11], post-window [+1, +5], market-adjusted | 0.228 (0.210) | .280 | [−0.190, 0.647] |
| Pre-window [−45, −11], post-window [+1, +10], market-adjusted | 0.209 (0.285) | .465 | [−0.357, 0.776] |
| Pre-window [−45, −11], post-window [+1, +20], market-adjusted | 0.163 (0.198) | .413 | [−0.231, 0.557] |
| Raw log returns, [−25, −5] vs. [+5, +25] | 0.212 (0.243) | .386 | [−0.272, 0.696] |
| Raw log returns, [−25, −5] vs. [+5, +25], with the 80% rule | 0.212 (0.243) | .386 | [−0.272, 0.696] |
| Market-adjusted simple returns, [−25, −5] vs. [+5, +25] | 0.178 (0.229) | .440 | [−0.278, 0.633] |
| Market-adjusted simple returns, [−60, −11] vs. [+1, +20] (primary) | 0.137 (0.193) | .481 | [−0.248, 0.521] |

*Note.* Each row re-estimates the primary model M4 with one change and reports the Form 499 registrant coefficient, its CV3 standard error (SE) in parentheses, its p-value, and its 95 percent confidence interval; N = 333 and G = 82 unless the N column shows otherwise. CV3 is the cluster jackknife SE by parent filer entity. Panel A ends the post-window at day +5, +10, or +20 against the pre-window [−60, −11]; the three windows form one family, and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it. The wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. Every window must have returns on at least 80 percent of its trading days. Panel B replaces the market adjustment with abnormal returns from the market model and the Fama–French three-factor (FF3) model, both estimated over trading days [−250, −30]; 6 events (1 registrant event) lack 80 percent coverage in that window, leaving 327 events. Panel C counts contaminated estimation windows, those containing another event at the same parent filer entity, dated by that event's notification date and by its breach date; the focal event itself is excluded. The shares across all events are .43 by notification date and .59 by breach date. Panel D lists coverage drops by benchmark and pre-window; the primary windows drop no event. Panel E moves step by step from the earlier outcome, raw log-return volatility over [−25, −5] and [+5, +25], to the primary one: the same outcome with the 80 percent rule, then market-adjusted simple returns on the same windows, then the current windows. Its first rows start the pre-window at day −45. No row gives a p-value below .05.
