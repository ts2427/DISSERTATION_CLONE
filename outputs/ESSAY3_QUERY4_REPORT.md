# Essay 3 — Query 4: Table Inputs, Readouts, and Commit

**Tracking: not tracked** (`.gitignore:79` is `*.md`). CSVs under `outputs/essay3_q4/` are
trackable. **Nothing committed. Part H not started.**

New scripts, both uncommitted: `scripts/243_essay3_q4_readouts.py` (Parts B, C),
`scripts/244_essay3_q4_tables.py` (Part F). No existing script, table, constants file or
prose was edited. `outputs/essay3_v4/` and `outputs/rebuild_v4/` untouched. `run_all.py`
and `scripts/158` not run.

---

# PART A — Table 2 inputs

## A1. Clause split per treated parent CIK

| CIK | Name | Clause 1 | Clause 2 | Total |
|---|---|---:|---:|---:|
| 1283699 | T-Mobile USA, Inc. | 26 | 0 | 26 |
| 732717 | AT&T | 15 | 9 | 24 |
| 101830 | Sprint Nextel | 11 | 1 | 12 |
| 732712 | Verizon | 10 | 0 | 10 |
| 1166691 | Comcast | 1 | 8 | 9 |
| 1091667 | Charter Communications, Inc. | 0 | 8 | 8 |
| 18926 | CenturyLink | 0 | 5 | 5 |
| 20520 | Frontier Communications | 0 | 4 | 4 |
| 1609711 | GoDaddy.com LLC | 3 | 0 | 3 |
| 1001082 | DISH Network, LLC | 0 | 2 | 2 |
| 1447669 | Twilio | 2 | 0 | 2 |
| 1632127 | Cable One, Inc. | 2 | 0 | 2 |
| 1702780 | Altice USA, Inc. | 0 | 2 | 2 |
| **TOTAL** | | **70** | **39** | **109** |

**Rows sum to 109.** Asserted in `scripts/244` (T2: clause columns sum per CIK; total 109).

**Clause-2 rules and FRNs:**

| CIK | n | FRN cited | Rule (`scripts/154` `ADJ`) |
|---|---:|---|---|
| 18926 | 5 | — | Clause (b): CenturyLink/Lumen carrier family (Gate 1 rescue; regional LEC filers) |
| 20520 | 4 | — | Clause (b): parent of regional Form 499 filer subsidiaries (7/28) |
| 101830 | 1 | **0006693022** | Clause (b): prepaid wireless brand of Sprint Spectrum LLC (Boost Mobile, 7/28) |
| 732717 | 9 | — | Clause (b): AT&T Inc. filing family (7/28) |
| 1001082 | 2 | **0027852722; 0029666096** | Clause (b) date-conditional (9/4): DISH, from the 2020-07-01 Boost divestiture |
| 1091667 | 8 | — | Clause (b): parent brand of Charter Communications Operating LLC (7/28) |
| 1166691 | 8 | — | Clause (b): parent brand of Comcast Telephony filers (7/28) |
| 1702780 | 2 | — | Clause (b): parent of Altice Wireless filer (7/28) |

**Six of the eight clause-2 rules cite no FRN at all.** They name a filer family or a
subsidiary brand in prose. Only Sprint/Boost and DISH carry a registration number. That is
a real limit on how far a reader can audit clause 2 from the committed artefacts.

**Clause-1 FRNs:** T-Mobile 499ID 822060 (24 events) and 811754 (2, the post-merger Sprint-
named events); Sprint 811754 (11); Verizon 0003469442 (10); AT&T 0005937974 (13) and
Cricket 0004321139 (2); Comcast — NBCUniversal FRN 20940540 (1); GoDaddy 0025730607 (3);
Twilio 0020237343 (2); Cable One 0003474327 (2).

**Why 8 + 8 = 16 > 13.** Eight CIKs carry at least one clause-1 event and eight carry at
least one clause-2 event, but **three CIKs carry both**: **AT&T (15 + 9)**, **Sprint
(11 + 1)** and **Comcast (1 + 8)**. 8 + 8 − 3 = 13. The Query 3 report presented "8 and 8"
without that overlap; this is the correction.

## A2. Entities versus CIKs

The join is a **hard-coded one-entry map**, `scripts/224:361`:

```python
FAM = {101830: 1283699}
```

applied at `scripts/224:369` as `t['final_cik'].map(lambda c: FAM.get(c, c)).nunique()`.

The two CIKs forming one parent entity are **101830 (Sprint) and 1283699 (T-Mobile USA,
Inc.)** — the merger that closed 2020-04-01. Combined they hold **38 treated events**.

| | parent CIKs | parent entities |
|---|---:|---:|
| treated | 13 | **12** |
| **control** | **109** | **109** |
| all | 119 | 118 |

**`FAM` has no control-side entry, so control entities and control CIKs are equal by
construction, not by finding.** Any Methods sentence implying the entity grouping was
applied symmetrically is unsupported: it is one hand-entered pair on the treated side.

## A3. Twilio and GoDaddy registry detail

Every field the committed snapshot holds, verbatim:

**Twilio Inc — FRN 0020237343**
```
Registration_Current_as_of   2026-04-01
start_date                   2010-10-07
end_date                     (absent — open)
Legal_Name                   Twilio Inc
doing_business_as            Twilio Inc
other_trade_name             Twilio Inc.
holding_company              (absent)
Principal_Communications_Type (ABSENT)
USF_Contributor              No
```

**GoDaddy.com LLC — FRN 0025730607**
```
Registration_Current_as_of   2025-04-01
start_date                   2017-04-01
end_date                     (absent — open)
Legal_Name                   GoDaddy.com LLC
doing_business_as            (absent)
other_trade_name             (absent)
holding_company              GoDaddy Operating Company LLC
management_company           Go Daddy Operating Company LLC
Principal_Communications_Type  Other Toll
USF_Contributor              Yes
```

The registry schema *does* carry `Principal_Communications_Type` (it is populated for
GoDaddy). **Twilio's record has no service-category field at all, and Twilio is not a USF
contributor.** Printed, not interpreted.

**The 5 treated events.** All fall inside their filer's registration coverage.

| Firm | breach | reported | type | `information_affected` (head) |
|---|---|---|---|---|
| Twilio | 2022-08-04 | 2022-08-04 | HACK | "Limited customer data and internal access logs (company said small number)" |
| Twilio | 2024-04-01 | 2024-04-01 | HACK | "Phone numbers and account data in some incidents" |
| GoDaddy | 2019-10-16 | 2020-05-03 | HACK | JSON: Personal Identifiers Affected=Yes, examples ["SSH passwords"] |
| GoDaddy | 2021-09-06 | 2021-11-07 | HACK | JSON: Personal Identifiers Affected=Yes, ["Customer number","Email address"] |
| GoDaddy | 2022-03-14 | 2022-06-01 | INSD | JSON: Personal Identifiers Affected=Yes, ["Name"] |

Note the two Twilio records carry **free-text** `information_affected`, not the CCPA JSON
the rest of the sample uses.

---

# PART B — Control coefficients (NEW readout, CV3 only)

`scripts/243` lifts `TREAT`, `BASE`, `CTRL` and `d0` from `scripts/227` **by AST**, rebuilds
the design and the CV3 jackknife with `227`'s own statements, and reads the full diagonal
of the jackknife covariance where `227` reads one cell.

**Assertion, all three windows: PASSES at full stored precision.** coef 0.0040/−0.0410/
0.0233 and se_cv3 0.0334/0.0791/0.0996 reproduce `f1_ladder.csv` exactly. That is the proof
the design is the frozen one, not a claim about it.

n = 405, G = 119, k = 9, df = 118 at every window.

### 30 days
| term | coef | se_cv3 | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| (intercept) | +0.05847 | 0.12415 | +0.471 | .6385 | [−0.1874, +0.3043] |
| **fcc_form499** | **+0.00395** | **0.03343** | **+0.118** | **.9061** | [−0.0623, +0.0702] |
| prior_breaches_1yr | +0.00221 | 0.00558 | +0.397 | .6920 | [−0.0088, +0.0133] |
| health_breach | −0.03808 | 0.01936 | −1.967 | **.0516** | [−0.0764, +0.0003] |
| firm_size_log | −0.00370 | 0.01121 | −0.330 | .7420 | [−0.0259, +0.0185] |
| leverage | +0.01992 | 0.05364 | +0.371 | .7111 | [−0.0863, +0.1261] |
| roa | +0.05898 | 0.16289 | +0.362 | .7179 | [−0.2636, +0.3816] |
| baseline_exec_rate_py_rd | −0.00161 | 0.01130 | −0.142 | .8873 | [−0.0240, +0.0208] |
| prior12m_mktadj_ret_rd | −0.00103 | 0.05156 | −0.020 | .9841 | [−0.1031, +0.1011] |

### 90 days
| term | coef | se_cv3 | t | p |
|---|---:|---:|---:|---:|
| (intercept) | +0.03772 | 0.21108 | +0.179 | .8585 |
| **fcc_form499** | **−0.04098** | **0.07909** | **−0.518** | **.6053** |
| prior_breaches_1yr | +0.00252 | 0.00571 | +0.441 | .6598 |
| health_breach | −0.02444 | 0.07411 | −0.330 | .7421 |
| firm_size_log | +0.00012 | 0.02088 | +0.006 | .9954 |
| leverage | +0.07464 | 0.14284 | +0.523 | .6023 |
| roa | +0.28833 | 0.50965 | +0.566 | .5726 |
| baseline_exec_rate_py_rd | +0.03532 | 0.04134 | +0.854 | .3946 |
| prior12m_mktadj_ret_rd | −0.10776 | 0.09176 | −1.174 | .2426 |

### 180 days
| term | coef | se_cv3 | t | p |
|---|---:|---:|---:|---:|
| (intercept) | −0.00934 | 0.29545 | −0.032 | .9748 |
| **fcc_form499** | **+0.02325** | **0.09963** | **+0.233** | **.8159** |
| prior_breaches_1yr | +0.00720 | 0.01164 | +0.619 | .5374 |
| health_breach | −0.03724 | 0.09861 | −0.378 | .7064 |
| firm_size_log | +0.02545 | 0.02666 | +0.955 | .3418 |
| leverage | −0.01922 | 0.19540 | −0.098 | .9218 |
| roa | +0.03512 | 0.41046 | +0.086 | .9320 |
| baseline_exec_rate_py_rd | −0.00603 | 0.04136 | −0.146 | .8844 |
| prior12m_mktadj_ret_rd | −0.10138 | 0.10691 | −0.948 | .3449 |

**No control is significant under CV3 at any window. Zero with p < .05.** The nearest is
`health_breach` at 30 days, **p = .0516** — just outside, and note it is the very variable
freeze exception 3 corrected two days ago.

**Family label: DESCRIPTIVE. Not hypothesis tests, not pre-specified, NOT added to the
31-test BH ledger.** Written into every row of `b_control_coefficients.csv`.

Worth stating for the Results text: **not one covariate predicts executive departure.**
The controls are doing nothing, which is consistent with a design in which the outcome is
close to noise at this sample size.

---

# PART C — Logit warnings (NEW readout)

**Assertion: AMEs and SEs reproduce `f1_logit_ame.csv` exactly at all three windows**
(0.0070/0.0311, −0.0420/0.0468, 0.0197/0.0775). No difference; not stopped.

| Window | converged | iterations | n used | dropped | max fitted p | min fitted p | separation |
|---|---|---:|---:|---:|---:|---:|---|
| **30** | **FALSE** | **35** | 405 | 0 | 0.124160 | 0.001347 | none |
| 90 | True | 6 | 405 | 0 | 0.407248 | 0.025157 | none |
| 180 | True | 5 | 405 | 0 | 0.398072 | 0.109489 | none |

**The 30-day logit did not converge.** Verbatim:

```
solver output : Warning: Maximum number of iterations has been exceeded.
                         Current function value: 0.171512
                         Iterations: 35
warning       : ConvergenceWarning: Maximum Likelihood optimization failed to converge.
                Check mle_retvals
```

90d and 180d: `Optimization terminated successfully.` — no warnings raised.

**Why this was never visible.** `scripts/227:198` passes `disp=0`, which suppresses the
solver's printed warning, and its `try/except` catches **exceptions**, not warnings — a
non-converged fit returns normally. So `f1_logit_ame.csv`'s 30-day row was written from a
failed optimisation and nothing recorded it.

**No separation and no dropped observations at any window.** Max fitted probability 0.124
at 30 days, well inside (0,1). The failure is a flat likelihood, not separation: there are
only 17 positives in 405 at 30 days.

**Consequence for the Results section.** The logit is corroboration only — it is not in the
31-test ledger and no verdict depends on it. But **the 30-day AME must not be quoted**, and
if the logit panel is shown at all, the 30-day cell should carry the non-convergence note.
The LPM at 30 days is unaffected; it is OLS and has no convergence step.

---

# PART D — Errata to the Query 3 report

Written here; the Query 3 report is not edited.

### D1. T-Mobile shares — **confirmed, and the Query 3 figures were right**
T-Mobile CIK 1283699: **26 of 109 treated events = 23.9%**. T-Mobile + Sprint (101830):
**38 of 109 = 34.9%**. Sample level: **analysis-sample events**. The instructions' "26 of
106 / 37 of 106" carried a stale denominator and a stale Sprint count.

### D2. Bootstrap versus CV3 — **Query 3's closing sentence was wrong**
The WCR p is **smaller** than the CV3 p at every window and in the placebo:

| | CV3 p | WCR p | WCR smaller? |
|---|---|---|---|
| 30d | .9061 | .8889 | yes |
| 90d | .6053 | .5136 | yes |
| 180d | .8159 | .7901 | yes |
| placebo | .3116 | .2308 | yes |

**Restated:** the two rungs agree on the verdict at every window — all null, none close to
.05. **The bootstrap is not the more conservative rung here; it is uniformly the less
conservative.** My Query 3 close said "the bootstrap slightly the more conservative of the
two." That is retracted.

### D3. Firm size — **"an order of magnitude" was wrong, and so was "overlap this poor"**

Mean `firm_size_log`: treated 11.5762, control 9.6945, **difference +1.8817**.
**exp(1.8817) = 6.56×.** Median difference +2.5230 → **exp = 12.47×**.

Replace "an order of magnitude" with: *treated firms are about **6.6 times larger** at the
mean of log size (12.5× at the median)*.

Overlap, which Query 3 got backwards:

| | range | overlap |
|---|---|---|
| treated | [7.7421, 13.2206] | **93 of 109 treated events (85.3%) fall inside the control range** |
| control | [6.4420, 12.8096] | **287 of 296 control events (97.0%) fall inside the treated range** |

Only 9 control events sit below the treated minimum; **none** sits above the treated
maximum. **Common support is substantial.** Query 3's "no covariate adjustment fixes overlap
this poor" is retracted: the problem is a **mean shift on a well-overlapping distribution**,
not a support failure. That is a materially weaker criticism and should be stated as such.

### D4. T-Mobile flags — **Query 3 had the counts wrong and the inference unfounded**

`scripts/242` printed the right numbers; I transcribed the wrong column into the Query 3
report. Correct counts, from `table11.csv`:

| Window | T-Mobile events with an exec departure | of 26 | CEO | after excluding pre-announced |
|---|---:|---:|---:|---:|
| 30 | **3** | 26 | 0 | 3 |
| 90 | **5** | 26 | 0 | 5 |
| 180 | **13** | 26 | 0 | 13 |
| placebo | **8** | 26 | — | — |

Query 3 printed 0 / 0 / 3 and "seven" for the placebo. All four are wrong. **The correct
figures are 3 / 5 / 13 and 8.**

**Are they one departure or several? Four distinct departures, counted 13 times.** The 13
events resolve to **four** underlying departure events, because several breach records fall
within 180 days of the same 8-K:

| Person | first_date | filing date | accession | is_ceo | n_mentions | n_filings | events it serves |
|---|---|---|---|---|---:|---:|---:|
| Gary A. King | 2016-02-19 | 2016-02-19 | 0001193125-16-470124 | 0 | 1 | 1 | 3 |
| David A. Miller | 2021-09-16 | 2021-09-16 | 0001193125-21-275230 | 0 | 2 | 1 | 6 |
| Neville Ray | 2023-02-13 | 2023-02-13 | 0001193125-23-035719 | 0 | 2 | 1 | 1 |
| Peter Ewens | 2023-09-08 | 2023-09-08 | 0001193125-23-231377 | 0 | 1 | 1 | 3 |

**None is a CEO.** Query 3's further claim that these were "all at the 2015–2016 events …
the same underlying departure reached through three breach records" is wrong: they span
2016, 2021 and 2023, and are four different people.

**Retraction, as instructed.** Query 3 said surviving the pre-announced exclusion means
"none is flagged as pre-announced, retirement-only, or transaction-related by the
classifier's own flags." **There are no retirement or transaction flags.** The only flags
`c2_departure_events.csv` carries are `is_ceo`, `restated_only`, `vacancy_only`,
`director_only`. All four departures have `restated_only = 0` and `vacancy_only = 0`;
`director_only = 1` on these exec rows is an initialisation artefact of `scripts/220` and
carries no meaning for exec rows. The correct statement is: **the classifier records no
retirement or transaction flag because it has none.** Whether these four departures were
retirements or merger-related is not determinable from any committed artefact.

### D5. Crosswalk denominators — **all three expected values confirmed**

| Window | Group | n | filers | 5.02 & no exec | / all events | / filers |
|---|---|---:|---:|---:|---|---|
| 30 | treated | 109 | 26 | 22 | 22/109 = .2018 | 22/26 = **.8462** |
| 30 | control | 296 | 40 | 27 | 27/296 = .0912 | 27/40 = .6750 |
| 30 | **POOLED** | 405 | 66 | 49 | 49/405 = .1210 | 49/66 = .7424 |
| 90 | treated | 109 | 56 | 45 | 45/109 = .4128 | 45/56 = **.8036** |
| 90 | control | 296 | 123 | 80 | 80/296 = .2703 | 80/123 = .6504 |
| 90 | **POOLED** | 405 | 179 | 125 | 125/405 = .3086 | 125/179 = .6983 |
| 180 | treated | 109 | 82 | 49 | 49/109 = .4495 | 49/82 = .5976 |
| 180 | control | 296 | 197 | **124** | **124/296 = .4189** | **124/197 = .6294** |
| 180 | **POOLED** | 405 | 279 | **173** | 173/405 = .4272 | **173/279 = .6201** |

**Confirmed exactly: 124 of 296, 124 of 197, and 173 of 279 pooled.**

---

# PART E — Methods-support facts

## E1. BSO provenance — **Query 3's account was wrong; the file was swapped, not filtered**

| Commit | Date | `Data/DataBreaches.xlsx` | message |
|---|---|---|---|
| `07abde7` | 2025-11-01 | **858 rows** — BSO 755, BSF 70, MED 23, BSR 7, NGO 1, 2 missing | "Complete dissertation with LFS for large files" |
| `433b99d` | 2026-01-22 | **1,054 rows — all BSO** | "Add ML validation framework for Essays 2 & 3" |

| Commit | Date | `Data/processed/master_breach_dataset.xlsx` | message |
|---|---|---|---|
| `07abde7` | 2025-11-01 | 858 rows, six types | "Complete dissertation with LFS for large files" |
| `c2d51a3` | 2026-01-23 | 858 rows, six types | "Fix: Complete Essay 3 analysis and restore data files…" |
| `a1bb401` | 2026-01-25 | **1,054 rows — all BSO** | "Clean up repository: Remove temporary working files and clutter" |

**Query 3 said the BSO restriction "happened before the repository existed." That is
false.** The repository's first commit holds a six-type, 858-row extract. The all-BSO
1,054-row file replaced it on 2026-01-22 / 2026-01-25.

**Was it a filter? No — the row count *rose*.** 858 → 1,054 while types went 6 → 1. Key
matching on `org_name` + `breach_date`:

- only **454 of 597** old BSO keys appear in the new file
- **309** new keys appear in neither old file
- **52 records typed non-BSO in 2025-11 appear in the current all-BSO file** — BSF 28,
  MED 21, NGO 1, 2 missing

The clearest case is **Cencora, Inc.**, typed `MED`/`NGO` in the old extract and `BSO` in
the current one. Cencora is in the analysis sample and is the largest single event in the
chain (31 source records).

**Search of the full history for a filter: none exists.** Across all commits, the only
scripts touching `organization_type` read it or list it; none subsets on it, except
`scripts/130:155` (`is_bso = df['organization_type'] == 'BSO'`, plus a carrier-stray
rescue) — and `scripts/130` is **not referenced by any script in the v3/v4 chain**.

**Methods consequence.** A sentence asserting the sample is "the PRC BSO subset" describes
the *current vintage's labels*, produced outside the repository, in which at least 52
previously non-BSO records — including a healthcare distributor — now carry `BSO`. The
claim is not reproducible from committed code and should either be softened to "the
extract as received" or supported by the provenance of the 2026-01-22 replacement.

## E2. v3-overlap restriction composition

N falls 405 → 347; G falls 119 → 83.

**All 58 dropped events are CONTROL. Zero treated.** They span **37 parent CIKs**.
Largest: Time Warner 8, then Facebook 3, Citrix 3, Fiserv 3, Sinclair 3, VMware 2,
Seagate 2, T. Rowe Price 2, Activision 2, Motorola 2, J.B. Hunt 2, and 26 CIKs with 1.

The linker difference: every one of the 58 is an event **v4 linked and v3 did not** —
`cusip_ncusip` 48, `cusip_header` 8, `cusip_issuer` 2. v3's linker used CCM; v4 rebuilt
the link from `comp.security` → `crsp.stocknames` without it, which recovers control firms
CCM missed. **No treated event turns on the linker rebuild**, which is exactly what the
"control-side linkage gain" claim asserts — now quantified.

## E3. Validation commit pairs, rounds 1–3 — **the order is the reverse of the v4 round, and that is correct**

| Round | Classifier output (sealed) | Reference codes | Gap |
|---|---|---|---|
| 1 | `fd7887a` 2026-09-11 **13:59:17** | `edbf670` 2026-09-11 **14:37:51** | +38 min |
| 2 | `edbf670` 2026-09-11 **14:37:51** | `5ec8f9e` 2026-09-11 **14:44:33** | +7 min |
| Audit | `762a4b9` 2026-09-11 **14:58:46** | `8e18c4e` 2026-09-11 **15:16:52** | +18 min |

**In all three v3-era rounds the classifier output precedes the reference codes.** The
query asked me to confirm the reverse or report where it fails — so, plainly: it does not
hold in any of the three, **and that is the design, not a failure.**

The two designs protect against different things:

- **v3 rounds (1, 2, audit):** the classifier's answers are sealed into a committed
  `validation_classifier_HIDDEN*.csv` **first**, then coded blind. This proves the answers
  were not retuned after seeing the reference codes.
- **v4 final round:** the classifier had **never been run** on those documents, so the
  reference codes were committed first (`93bed94` 10:34:06) and the first-ever classifier
  run followed (`6147414` 10:42:50). This proves the coder could not have seen any output.

Both are blinding-preserving. Neither round has an ordering violation. A Methods sentence
claiming one uniform ordering across all four rounds would be wrong.

---

# PART F — One source CSV per table

`scripts/244_essay3_q4_tables.py` writes `table01.csv` … `table11.csv` plus
`table_provenance.csv` (23 cell-group rows: table, panel, column, source file, source
line/key, emitting script).

| Table | Content | Rows |
|---|---|---|
| 1 | Attrition ledger, with the identity-gate split on the CRSP line | 10 steps |
| 2 | Treated parent CIKs: clause split, same-CIK controls, family grouping | 13 |
| 3 | Breach-type mix by group | 8 types |
| 4 | Covariates with standardized differences + anchor rows | 20 |
| 5 | Four validation rounds + stratified-recall panel | 76 + 16 |
| 6 | Outcome rates by window and group + crosswalk, with a pooled row | 9 |
| 7 | Ladder (MDE, control rate) + logit AME (with convergence) + control coefficients | 3 + 3 + 27 |
| 8 | Placebo ladder + window rates by group | 1 + 3 |
| 9 | 27 sensitivities with BH + SIC-cell panel | 27 + 36 |
| 10 | LOCO range + top-ten variance shares + overlap panel | 3 + 30 + 6 |
| 11 | T-Mobile case rows, health omitted, accession-only citations | 26 |

**Conventions honoured:** `se_hc3` is written **blank** for the three SIC-FE rows with a
note column explaining the rank-deficient design — **no literal `inf` appears anywhere**
(asserted). Recall-corrected rows keep `BOUNDING EXERCISE`. Table 10's overlap panel
carries `panel_note` saying it is **not** a ticker match. Table 11's only health column is
the omission note.

**All 24 assertions PASS, zero failures**, including the five named in the query:

```
T1 closes arithmetically (N never rises)                       PASS
T1 treated + control == N at every populated step              PASS
T2 treated events sum to 109 / rows == 13 / families == 12     PASS
T3 subgroup Ns sum to 109 / 296                                PASS
T6 30/90/180 treated+control == pooled on every count          PASS
T7 treatment rows equal f1_ladder.csv (coef, se_cv3, p_cv3)    PASS
T9 sensitivity rows == 27                                      PASS
T9 no literal 'inf' written anywhere                           PASS
T11 event count == 26                                          PASS
```

---

# PART G — Purge scan

17 files in `outputs/essay3_q4/` scanned against all 13 patterns:

```
Rule 37.3 0 | September 28, 2007 0 | 1,054 breaches 0 | 14.52 0 | 16.71 0 | 15.05 0
651 0 | 648 0 | BoardEx 0 | turnover 0 | natural experiment 0 | deadline 0 | 7-Day Rule 0
TOTAL: 0
```

**Zero hits in the Query 4 CSVs.**

Scanning **this report** returns 14 hits, and every one is self-referential: 13 are the
pattern names themselves printed in the results block two paragraphs above (`Rule 37.3 0 |
September 28, 2007 0 | …`), and the fourteenth is this sentence. No banned figure is
asserted anywhere in the report; the Query 3 values it quotes appear only inside the Part D
errata, explicitly marked as retractions. Reported here rather than suppressed, so the
count is reproducible by anyone re-running the scan.

---

# PART H — Commit and push

**GATED. Not started. Awaiting your "commit" or "push".**

Ready to commit on your word: `scripts/242`, `scripts/243`, `scripts/244`,
`outputs/essay3_q3/*.csv`, `outputs/essay3_q4/*.csv`, and both reports via `git add -f`.

One thing you should decide before "push": the remote tip of `rebuild-v4` is `cc9a8cc`, so
`0a4ad57` and `609a898` (freeze exception 3) are still local-only. A push sends those too.

---

# Close

**1. Do Tables 1–11 each regenerate from committed inputs with all assertions passing?**
Yes — all eleven regenerate from `scripts/244` reading only committed artefacts plus the
Query 3 and Query 4 outputs, and all 24 assertions pass with zero failures, including that
Table 1 closes arithmetically at every step, Table 7's treatment rows equal `f1_ladder.csv`
to stored precision, Table 9 has exactly 27 sensitivity rows with no literal `inf`, and
Table 11 holds exactly 26 T-Mobile events.

**2. Is any control coefficient significant under CV3, and did the logit report separation
or non-convergence?**
No control is significant at any window — zero with p < .05, the nearest being
`health_breach` at 30 days with p = .0516 — and the logit reported **no separation and no
dropped observations at any window**, but the **30-day logit failed to converge** (35
iterations, `ConvergenceWarning`, suppressed by `disp=0` in `scripts/227:198`), so its AME
should not be quoted.

**3. Which Methods sentences does Part E contradict?**
Three: any sentence describing the sample as the PRC **BSO subset** as though a filter were
applied (E1 — the extract was *replaced* on 2026-01-22/25, the row count rose 858 → 1,054,
and at least 52 records typed BSF/MED/NGO in the original now carry BSO, Cencora among
them); any sentence implying the **corporate-entity grouping** is a general rule (A2 — it
is one hard-coded pair, `FAM = {101830: 1283699}`, with no control-side entry); and any
sentence asserting a **single uniform reference-code-before-classifier ordering across all
four validation rounds** (E3 — rounds 1, 2 and the audit seal the classifier output first
and code blind against it, which is the opposite order and equally valid).
