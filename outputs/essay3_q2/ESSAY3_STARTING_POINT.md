# Essay 3 — starting point (Query 2 chain)

Where to begin when picking Essay 3 back up. Pointers only; the numbers live in the files named here and in `outputs/ESSAY3_QUERY2_REPORT.md`.

## Outcome and classifier

- **Final classifier:** `scripts/195_essay3_q2_classifier_v2.py` (v2).
  - Freeze commit **`6f7be7a`**, blob **`ec3236471df71279531e0593304eb7b478b210b9`**, file sha256 `42a64e12883ce269814b884a5892ca75699185dbfec8d12f875e720b5a88a7c9`.
  - It is FROZEN: do not edit it. Any revision needs a fresh blind validation draw. The stopping rule is in `outputs/essay3_q2/FINAL_CLASSIFIER.txt`.
- **Outcome:** an executive-officer departure reported under Item 5.02(b), coded from the filing text. One departure per person within a parent CIK, dated to its earliest disclosing filing.
- **Validation:** two blind rounds plus a stratified recall audit. All reference codes are Claude's, coded blind, with a verification pass. **Tim did not hand-code.**

## Constants and sample

- **Constants (assertion baseline):** `outputs/essay3_q2/constants_essay3_q2.json`. Script 202 writes it once, then asserts against it on every later run. `constants_v3.json` is untouched by Essay 3.
- **Analysis sample** (`outputs/essay3_q2/e_analysis_sample.csv`, `in_analysis_sample == 1`):
  - **N = 338 events:** 107 treated, 231 control.
  - **Clusters:** 81 parent CIKs, of which 12 are treated.
  - **T-Mobile:** 26 of its 34 events are in the sample.
  - Anchor: reported_date (breach_date is a sensitivity). The ledger is `e_ledger.csv`.

## The four files behind the results tables

| File | Holds |
|---|---|
| `outputs/essay3_q2/f1_ladder.csv` | F1 primary: the inference ladder at 30, 90 and 180 days |
| `outputs/essay3_q2/f4_placebo.csv` | F4: the pre-disclosure placebo |
| `outputs/essay3_q2/f3_sensitivities.csv` | F3: the sensitivities, one row per specification per window |
| `outputs/essay3_q2/f3_loco.csv` | Leave-one-parent-CIK-out ranges and sign flips |

Supporting: `f1_cluster_diagnostics.csv`, `f1_se_diagnostics.csv`, `f1_cv3_variance_shares.csv` (scripts/204), `f1_logit_ame.csv`, `f2_baseline.csv`, `f5_ceo.csv`, `f6_director.csv`, `i_tests.csv` (test ledger and BH).

## T-Mobile case

| File | Holds |
|---|---|
| `outputs/essay3_q2/g6_case_table.csv` | Departures within 180 days of notification, with flags and excerpts |
| `outputs/essay3_q2/g6_restatement_dated.csv` | Additions under the restatement-dated sensitivity |
| `outputs/essay3_q2/tmobile_timeline.csv` | The dated timeline: breaches, notifications, departures, proxy and 10-K passages |

Collection scripts: 190 and 191. Case script: 203.

## Two hard rules

1. **HC3 is disqualified everywhere.** It ignores within-parent clustering. The inferential frame is CV3 and the wild cluster bootstrap. Never read an HC3 p-value as significance; `f3_sensitivities.csv` carries an `hc3_status` column saying so in every row.
2. **The corner-case recall rows are bounding exercises, not estimates.** Two rows per window pair treated recall at one end of its confidence interval with control recall at the other. They bound how far misclassification could move the estimate. The `row_type` column marks them.

## Running the chain

Order: 187 → 195 → 199 → 202 → 190 → 191 → 203 → 204. It is in `run_all.py` under "ESSAY 3 — QUERY 2 CHAIN", but **do not run run_all or script 158** for Essay 3 work. A clean-clone run of 195 through 204 reproduces every committed output (verified at commit `c5f761d`).

Retired legacy Essay 3 code and values are listed in `outputs/RETIREMENT_LEDGER.md`.
