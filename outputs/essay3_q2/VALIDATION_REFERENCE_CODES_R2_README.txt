VALIDATION REFERENCE CODES — ROUND 2 (received 2026-09-11; saved verbatim as VALIDATION_REFERENCE_CODES_R2.psv, '|'-delimited)

PROVENANCE:
- Tim did NOT hand-code. The round-2 reference codes were produced by Claude (a separate session), BLIND to the
  v2 classifier's answers (validation_classifier_HIDDEN_R2.csv), coded from the item_5_02_text column of
  VALIDATION_SHEET_R2.xlsx first, under the same interpretive rules as round 1 (README of
  VALIDATION_SHEET_CLAUDE_RATER.xlsx; reproduced in VALIDATION_REFERENCE_CODES_R1_README.txt) and Tim's four
  rulings: pay-agreement departures count; vacancy mentions count for directors only; pre-announced includes
  effective dates before the reference date; restatements flagged in restates_prior_disclosure.
- A verification pass followed, still blind to the classifier, on uncertain rows only (log below). One code
  differs between blind and verified: sheet 9, pre-announced. Primary = verified (Y); secondary = blind
  ('unclear'), following the round-1 sheet 31 precedent.
- 'unclear' is used where the rules do not cover the case (sheet 29, interim title).
- File of record: the attached workbook VALIDATION_SHEET_R2_CLAUDE_RATER.xlsx (tabs README, claude_codes,
  verification_log), found at Downloads/ and copied unchanged into outputs/essay3_q2/ (sha256
  96fa041ee5d0b09a…; full hash in scripts/197's log). The .psv here is the verbatim pasted text of the same
  codes; scripts/197 checks the two cell by cell before scoring.

Verification log (verbatim):
sheet_id | question checked | result | source
9 | When was Rutledge's Executive Chairman retirement announced? | 2022-09-21 release: he would serve as Executive Chairman through the end of his contract in November 2023. Pre-announced changed unclear -> Y (primary). | Charter release 2022-09-21 (ir.charter.com); Charter 8-K Ex. 99.1 2023-10-25 (sec.gov)
16 | Was Crull an executive officer? | Chief Strategy Officer reporting directly to the CEO (2017 reorganization); officer status not confirmed. Code unchanged, flagged for adjudication. | Fierce Network 2017-11-21
