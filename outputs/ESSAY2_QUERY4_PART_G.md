# Essay 2 Query 4 — Part G (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PART G: MICROSTRUCTURE (N=333 events)
==========================================================================================

## G1 — Coverage by year (% firm-days):
       days  pct_valid  pct_crossed  pct_open
year                                         
2006   5084       93.3          6.7     100.0
2007  15908       98.0          2.0     100.0
2008  16192       97.2          2.8     100.0
2009  15941       95.2          4.8     100.0
2010  15953       98.7          1.3     100.0
2011  16446       99.2          0.8     100.0
2012  16626       99.4          0.6     100.0
2013  17123       99.5          0.5     100.0
2014  17207       99.6          0.4     100.0
2015  17707       99.8          0.2     100.0
2016  18025       99.9          0.1     100.0
2017  18533       99.9          0.1     100.0
2018  19025       99.8          0.2     100.0
2019  19456       99.8          0.2     100.0
2020  19618       99.9          0.1     100.0
2021  19825      100.0          0.0     100.0
2022  19635       99.9          0.1     100.0
2023  19500       99.9          0.1     100.0
2024  19656       99.8          0.2     100.0
  Overall: 99.2% valid uncrossed closing quotes; OPENPRC populated 100.0% — CPQS is the primary microstructure outcome (premise correct: CRSP daily carries closing BID/ASK).

## G2 — Outcomes built: N with CPQS 331, EDGE 331, OCAM 331
  EDGE negative-estimate rate (signed kept, stated): pre 106, post 124 of 331 windows.
  CPQS change: coef +0.00005 SE 0.00003 95% CI [-0.00002, +0.00012] N=331 (102 treated, G=81; month FE; CV1 parent-CIK)
  EDGE change: coef +0.00222 SE 0.00309 95% CI [-0.00392, +0.00837] N=331 (102 treated, G=81; month FE; CV1 parent-CIK)
  log-OCAM change: coef -0.06927 SE 0.09633 95% CI [-0.26098, +0.12244] N=331 (102 treated, G=81; month FE; CV1 parent-CIK)

  Multiplicity (stated): 3 secondary outcomes, Benjamini-Hochberg at FDR 5%:
        outcome      p  bh_threshold  bh_reject
    CPQS change 0.1593        0.0167      False
    EDGE change 0.4736        0.0333      False
log-OCAM change 0.4742        0.0500      False

  Correlation of microstructure changes with the volatility DV (was volatility a reasonable proxy?):
               e2_vol_change  cpqs_chg  edge_chg  ocam_chg
e2_vol_change          1.000    -0.048    -0.109     0.074
cpqs_chg              -0.048     1.000     0.347     0.163
edge_chg              -0.109     0.347     1.000     0.192
ocam_chg               0.074     0.163     0.192     1.000
  Koski (2007): bid-ask bounce biases measured return volatility upward, more for low-priced stocks — a pre/post change in measured volatility can itself be a spread artifact; the measures are reported side by side, volatility retained.

  G4 framing: total effective spread and price impact only — no adverse-selection decomposition is claimed (requires signed trades / intraday data). These are secondary outcomes; not candidate headlines. Precedents: Frino, Gaudiosi & Mollica (2026 A&F) — persistently wider spreads after cyber attacks, smaller for large firms; Katselas, Sidhu & Yu (2020 A&F) window architecture.
