# Essay 2 — the announcement-window contrast (computed live)

==========================================================================================
THE ANNOUNCEMENT-WINDOW CONTRAST (computed live, scripts/175)
==========================================================================================

## LEVEL 1 — Announcement window (information content): abnormal-vol elevation [-4,+4] vs [-25,-5], identical machinery, same firms
  EARNINGS announcements: +0.7800 daily pp (SE 0.0526, 95% CI [+0.6753, +0.8847], N=4,867, 79 firms)
  BREACH notifications: -0.0907 daily pp (SE 0.0505, 95% CI [-0.1911, +0.0098], N=331, 81 firms)
  CONTRAST (breach minus earnings, firm-clustered): -0.8707 (SE 0.0775, 95% CI [-1.0249, -0.7165], t=-11.2)
  CONTRAST within firm (firm FE): -0.9523 (SE 0.1163, 95% CI [-1.1838, -0.7208]) — the same firms' breach notifications are informationally routine relative to their own earnings announcements.
  The breach point estimate is slightly NEGATIVE — one sentence, not a celebration: the direction is reported, it is not significant, and the announcement-timing literature offers a compositional account (Foerderer & Schuetz 2022: firms time breach disclosures toward high-news-pressure days, which mechanically raises the baseline).

## LEVEL 2 — Shock-excluded persistent window (regime shift, Ohlson-Penman sense)
  Breach estimate (scripts/169 S1, abnormal DV, mkt-vol control, year FE, two-way cluster): +0.086, 95% CI [-0.284, +0.455] — null.
  EARNINGS REFERENCE BOUND (t49): post-pre = -0.003, 95% CI [-0.120, +0.114], N=4,860 — even the strongest scheduled information event produces no persistent shift; the construct is valid and its base rate is low. QUALIFICATION (stated): earnings are scheduled and resolve accumulated uncertainty at the announcement with no reason to move the baseline; a breach is unscheduled and plausibly carries ongoing litigation, regulatory, and churn exposure — so the earnings zero does not make the breach test redundant; it establishes the instrument and the base rate.

## LEVEL 3 — Treatment: no Form 499 differential on any measure
  NEW, AND IT SURVIVES THE LADDER — announcement-window elevation ~ Form 499: +0.4463 (CV1 SE 0.1583 p=0.0061; CV3 SE 0.1951 p=0.0249; WCR p=0.0071, B=49,999; 95% CI(CV1) [+0.1312, +0.7615]; N=331, G=80, G1=11). Jackknife: zero sign flips of 80 deletions; range [+0.336, +0.516] (largest move: deleting Sprint -> +0.336). Raw means: treated -0.013 vs control -0.125. This is the program's FIRST treatment coefficient to survive calibrated inference — registered carriers' breach notifications carry MORE announcement-window information content than controls' (equivalently: controls' notifications are volatility-DAMPING, treated are neutral). MULTIPLICITY, stated: 1 rejection in a 4-test pre-specified family (BH-significant) and in ~60 tests program-wide; the test was pre-specified by the 8/31 rescoping directive ('no Form 499 differential on any measure'), not searched for. FLAGGED AND STOPPED: interpretation and promotion are the author's decision.
  Persistent window: +0.086 [-0.28, +0.45] (S1); channels: CPQS +0.5bp [-0.2, +1.1], EDGE and log-OCAM CIs span zero (t35); delay behavior: null (Part A2). No differential anywhere.

## THE NARROWED CLAIM (limitations, stated plainly)
  The design does not measure uncertainty RESOLUTION — resolution occurs at the announcement, which the persistent-window structure excludes by construction. It measures persistent information-environment destabilization, and none occurs. The essay does NOT claim that mandatory timing leaves uncertainty resolution unaffected.

## THE POSTURE SENTENCE
  The same instrument that detects earnings announcements at t = +15 detects nothing at breach notifications (-0.09 daily pp, CI [-0.19, +0.01]): the market treats breach notifications as informationally routine relative to the strongest scheduled disclosure event in the calendar. "Is your null an artifact?" is now answered by a number, not an argument.

Tests this script: 4 (one pre-specified family; the earnings-elevation and contrast rejections are the rescoped design-validation results, reported with the family stated).
