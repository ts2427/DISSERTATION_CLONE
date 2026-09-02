# Essay 2 Query 6 — closeout (computed live)

==========================================================================================
QUERY 6 CLOSEOUT (computed live)
==========================================================================================

## 1 — T-Mobile / Sprint / MetroPCS event ledger (pipeline numbers only; no published price-move figures)
  46 family events (Sprint CIK 101830: 12; T-Mobile CIK 1283699: 34); all treated; 35 survive to the final N=333.

  AUGUST 2021 FOCAL EVENT — in the final sample, treated, HACK.
  Date verification: canonical breach_date = 2021-08-13 (the intrusion date
  stated in the Wisconsin DOJ filing); canonical reported_date =
  **2021-08-16 — exactly the pre-market confirmation date** (Vice/
  Motherboard reported the forum claim Sunday 8/15; T-Mobile confirmed
  Monday 8/16). Essay 2 anchors on the notification date, so the anchor is
  ALREADY 8/16 — no correction required. Essay 1's car_30d anchors on the
  8/13 occurrence date (breach-anchored convention; the Part-F flag
  applies). STRUCTURE NOTE for the intro: the incident appears as THREE
  canonical events (8/13 Wisconsin, 8/17 Maryland, 8/26 Massachusetts
  filings carrying different stated breach dates), kept distinct by the
  signed 3-day adjacency rule — the records-vs-events problem in
  miniature, from the essay's own focal case.
  Pipeline numbers, focal event (permno 91937):
    Essay 1 car_30d (breach-anchored [0,+30]): -12.30%  | car_5d -0.91%
    Essay 2 raw vol change ([-25,-5] vs [+5,+25], daily pp): -0.036 (pre 0.919 -> post 0.883)
    abnormal (market-model) vol change: -0.113 daily pp | GARCH DV +0.077 | canonical annualized +2.09pp | delay 3 days
    channels: CPQS 2.31 -> 2.11 bp (-0.20); EDGE -20.4 -> 30.6 bp

  SEPT 30 2024 FCC CONSENT DECREE (ILLUSTRATIVE ONLY — not a breach event, outside the estimation sample): car_5d +2.25%, car_30d +10.34% under the identical script-155 convention. The market reaction to the $31.5M settlement is what those numbers show.

  DISCLOSURE VEHICLE (from the cached EDGAR submissions — every PRC record is itself a state-AG/regulator filing; the 8-K record shows the SEC-side vehicle): the August 2021 incident drew Item 7.01 (Regulation FD, FURNISHED press releases) 8-Ks on 8/16, 8/18, 8/20, 8/27 — the newsroom statements furnished after journalists had already reported the breach; the January 2023 incident drew a FILED Item 8.01 8-K on 2023-01-19. The vehicle premise sharpens rather than fails: 2021 was furnished Reg-FD material, 2023 was a filed disclosure — formality varies by incident, sourced from the data (full per-event table t47).

## 3 — Sprint merger seam (close 2020-04-01; Boost to DISH 2020-07-01)
  Pre-2020-04-01 Sprint-named events on a non-Sprint CIK: 0 (want 0).
  Post-close Sprint-named events: 2, all on CIK [np.int64(1283699)] — the 2020-04-02 and 2020-04-15 events correctly sit on the TMUS side of the seam (breach dates after the 4/1 close).
  Boost-named events in the 489-event canonical universe: 0; DISH-named events: 2 — no post-7/2020 Boost record exists to misattribute (DISH itself was adjudicated OUT of treatment 7/28).
  VERDICT: the seam is CLEAN — zero events cross either date with wrong attribution; no re-estimation is required. (Checked, not assumed — same class of seam as the SIC-era misclassification.)

## 2 — Listed-carrier denominator, 2006-2024
  (a) SIC 481x, CRSP common shares (the RECOMMENDED definition — CRSP-native, historical SIC, CRSP coverage by construction):
    2006: 92 listed carriers -> 2024: 26; treated parents present 4 -> 5 (full series t48).
  (b) GICS group 5010 (Telecommunication Services, HISTORICAL co_hgic codes — the group survives the September 2018 sector restructuring even as sector 50 becomes Communication Services): 203 US companies (2006) -> 67 (2024). Caveat: a Compustat COMPANY count (no CRSP link pulled), so it overstates CRSP-listed carriers; definition (a) remains recommended.
  (c) Form-499-matched: the registry census (Query 4 Part J) — exact-name matching reaches 81 SEC-matched CIKs (a demonstrated undercount); the verified intersection is 13 parents. External corroboration held for the text: 2,319 wireline + 53 mobile providers (FCC, 6/30/2024); nationwide wireless 5->4 (10/2004), 4->3 (4/2020); FCC wireless HHI 2,706 (2005) -> 3,027 (2013); S&P 500 telecom ~12 constituents (2000) -> 4 (mid-2017).
  Exhibit saved: fig_C5_carrier_denominator.png

## 4 — Positive control: post-earnings volatility decline through the IDENTICAL pipeline
  Earnings events (sample firms, RDQ, identical abnormal-vol pipeline): N=4,860 firm-quarters, 79 firms.
  Raw mean post-earnings abnormal-vol change: -0.0100 daily pp. Year-FE constant (two-way clustered firm x month): -0.0028 (SE 0.0588, 95% CI [-0.1198, +0.1142]).
  INSTRUMENT DIAGNOSTIC (same events, same machinery, announcement window [-4,+4] vs [-25,-5]): mean elevation +0.7743 daily pp, t=+39.1, p=1.8e-290 — the pipeline detects the earnings announcement volatility spike with overwhelming precision. THE INSTRUMENT IS NOT BROKEN.
  VERDICT (flag raised, reported, not acted on): the pipeline DOES NOT recover a post-earnings decline in the SHOCK-EXCLUDED window structure — post-pre = -0.0028 (CI [-0.1198, +0.1142]) at N=4,860, i.e., persistent shifts larger than ~0.12 daily pp are EXCLUDED even for earnings. Read together: uncertainty resolution at the strongest scheduled information event in markets shows up AT the announcement (+0.77) and leaves NO persistent shift between the flanking windows. What this changes: the shock-excluded DV measures PERSISTENT baseline-volatility shifts, and even earnings produce none — so the breach null cannot be claimed as evidence about transient uncertainty resolution, and the essay's claim must be scoped to persistent information-environment destabilization (which the Diamond-Verrecchia regime story does predict, and which does not occur). Against the breach design's MDE (0.661): even a full-sample effect the size of the earnings announcement spike (0.77) would be marginally detectable at 11 treated parents. DECISION IS TIM'S: rescope the claim, or the positive control stands as a design limitation stated plainly.
