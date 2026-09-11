VALIDATION REFERENCE CODES — ROUND 1 (received 2026-09-11; saved verbatim as VALIDATION_REFERENCE_CODES_R1.psv, '|'-delimited)

PROVENANCE (recorded on Tim's instruction, 2026-09-11):
- Tim did NOT hand-code this sheet. The reference codes were produced by Claude (a separate session), coded
  BLIND to the classifier output, from the item_5_02_text column of VALIDATION_SHEET.xlsx under the sheet's
  README rules, with a verification pass on uncertain rows (verification log below). Tim reviewed and adopted
  them as the reference standard ("Consider this file mine ... research was done and everything that could
  be confirmed, has been").
- No URL was opened during blind coding. The seven T-Mobile calibration filings were coded from the sheet text.
- Sheet 31: the verified CEO code (Y) is scored as PRIMARY; the blind code ('unclear') as SECONDARY.
  (The coder's note calls sheet 31 a T-Mobile calibration filing; the sheet's own source column shows it is a
  random-draw filing, so it stays in the primary statistics.)

Interpretive rules the coder applied where the sheet README is silent (verbatim):
  1. Pre-announced = Y if any date in the text evidencing the departure (announcement, notice, agreement, or
     effective date) precedes the reference date in column E; 'unclear' only for 'as previously
     announced/disclosed' with no date.
  2. Leaving a covered title counts as a departure even if the person stays employed in another role or stays
     on the board (e.g., CFO becomes non-executive employee; president title relinquished while remaining CEO).
  3. A departure restated from an earlier filing (8-K/A, background sentence, consulting or comp agreement
     about a person who already left) is coded Y, with restates_prior_disclosure = Y so Stage 2 can apply
     either rule.
  4. EVP/SVP departures reported under Item 5.02 are coded as executive-officer departures when the text does
     not state officer status; noted where assumed.
  5. 'unclear' is used where the text does not state a fact needed for the code (see notes).

Verification log (verbatim; the "verification_log tab" of the submission):
sheet_id | question checked | result | source
31 | Was Roger Linquist the CEO? | Yes: Chairman and CEO of MetroPCS until the 2013-04-30 close. CEO code changed unclear -> Y. | MetroPCS 8-K Ex. 99.1, 2013-04-24 (sec.gov); T-Mobile 8-K 2013-05-02 (edgar-online)
13 | Esamann executive status; restatement? | EVP, senior management team; retirement announced 2021-03-30, so the 2021-09-27 filing is a restatement. Codes unchanged. | Duke Energy release 2021-03-30; Duke 8-K 2021-09-27
26 | Was Rencher an executive officer? | Yes, NEO in 2018 proxy. Codes unchanged. | Adobe DEF 14A 2018 (sec.gov)
58 | Was Weeks an executive officer? | Yes, listed with executive officers in FY2021 10-K. Codes unchanged. | Parker-Hannifin 10-K FY2021 (sec.gov)
57 | Was Schwartz an executive officer? | Title confirmed; officer status not confirmed. Code unchanged, flagged for adjudication. | RCR Wireless 2015-10-16; Fierce 2015-11-24
59, 60 | Were long texts truncated? | No: full text read; tails are exhibit references. | sheet text
11, 42 | Texts begin mid-sentence | Extraction artifact at the start; the Item 5.02 content is complete. Codes unchanged. | sheet text
