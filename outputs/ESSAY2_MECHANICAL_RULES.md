# Essay 2 — mechanical rules made explicit (Query 5 Part G6)

One sentence each; every rule is implemented in the named script.

1. **Event anchor:** the trading day nearest the public notification date on the matched security's calendar, required within ±7 calendar days; earlier day wins ties (scripts/163).
2. **Volatility windows:** trading days [−25,−5] and [+5,+25] inclusive (21 observations each); minimum 15 non-missing daily returns per window (scripts/163).
3. **Abnormal volatility:** market-model residuals with beta estimated on trading days [−250,−46] (minimum 100 observations); market-volatility benchmark computed identically on the CRSP value-weighted index (scripts/169).
4. **Liquidity windows:** trading days [−52,−11] and [+11,+52]; minimum 25 valid days per window; announcement window excluded (scripts/167).
5. **Price/volume filter:** PRC > 0 and VOL > 0 required for microstructure days; crossed or locked quotes (ASK ≤ BID) and CPQS > 50% dropped (scripts/167).
6. **EDGE:** the authors' `bidask` package, signed estimates retained (`sign=True`), averaged within window, never truncated before averaging (scripts/167).
7. **Amihud transform:** open-to-close |C−O|/O over dollar volume, ×10⁶, winsorized 1/99 within the window cross-section, then logged (scripts/167).
8. **Disclosure-delay regressor:** winsorized at the in-sample 99th percentile (785 days); raw reported alongside; zero-delay records flagged as occurrence-date defaults and the delay analysis re-run excluding them (scripts/163, 164).
9. **Repeat-breach overlap rule:** events of the same firm within 75 calendar days are both retained (each is a distinct disclosure); sensitivity dropping the later of each pair is reported (scripts/169; overlap rate 49.2%).
10. **Confound screen:** none at these window lengths (a screen selects at 84–104 trading days); calendar-time fixed effects and the market-volatility control carry identification; catastrophic confounds (delisting inside the window) drop mechanically via the return-availability rule. **Earnings-composition covariate and the earnings positive control are BLOCKED on an RDQ pull** (Compustat quarterly `RDQ`, chosen over I/B/E/S for coverage; one-line addition to the WRDS pull).
11. **Delisting returns:** NOT incorporated (Shumway 1997) — securities disappearing mid-window simply fail the minimum-days rule; stated as a limitation (five 2025 events and two Motorola events exit at extract boundaries, listed in the ledger).
12. **Sample period:** 2006–2024 (WRDS extract ends 2024-12-31).
13. **Clustering:** parent CIK (G=81, G₁=11) is the assignment level; two-way parent × event-month for the repaired specification; the placebo diagnostic shows CV1 over-rejects (12.1% at α=.05), so CV3/WCR are the calibrated rungs (scripts/165, 169).
14. **Treatment:** Form 499 registration, date-valid at the breach date from the committed registry snapshot; never SIC (scripts/154).
