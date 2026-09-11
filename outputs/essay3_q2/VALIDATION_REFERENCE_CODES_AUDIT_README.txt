RECALL-AUDIT REFERENCE CODES (received 2026-09-11; file of record VALIDATION_SHEET_AUDIT_CLAUDE_RATER.xlsx, copied
unchanged from Downloads; verbatim pasted text in VALIDATION_REFERENCE_CODES_AUDIT.psv — scripts/201 checks the two
cell by cell before scoring)

PROVENANCE:
- Tim did NOT hand-code. The audit reference codes were produced by Claude (a separate session), coded BLIND to v2's
  answers (validation_classifier_HIDDEN_AUDIT.csv, committed 762a4b9 before coding) and to the treatment strata.
- Same interpretive rules as rounds 1 and 2 plus the four rulings: pay-agreement departures count; vacancy mentions count
  for directors only; pre-announced includes effective dates before the reference date; restatements are flagged, not
  dropped.
- Coded from the item_5_02_text first. A verification pass followed on uncertain rows, still blind to the classifier.
  Where the verified code differs from the blind one, the main columns hold the VERIFIED value (PRIMARY); the blind_*
  columns hold the text-only value (SECONDARY).
- 'unclear' marks cases the rules do not cover: interim titles (sheet 17), a designation transfer without leaving any
  office (24), a Controller title not stated to be principal accounting officer (55), and a term extension with a stated
  end date not framed as a departure (75, CEO field). Primary statistics exclude 'unclear'; a sensitivity scores them Y.
- Sheet 3 is a structural case: the departure appears only in Exhibit 99.1, not in the Item 5.02 text the classifier reads.
- Blinding limit: company names in the text reveal treatment status for well-known carriers. Codes follow the text-based
  rules regardless.

Verification log (verbatim):
sheet_id | question checked | result | source
2 | Date of the T-Mobile/Sprint Business Combination Agreement | 2018-04-29, before the reference date. Pre-announced unclear -> Y. | Public record of the merger agreement; T-Mobile 8-K 2018-04-30 (sheet 75) describes the Transactions announced 2018-04-29
3 | What does the Exhibit 99.1 the Item 5.02 text points to say? | Donald leaves President and CEO effective 2022-08-01 and becomes Vice Chair. Exec and CEO unclear -> Y. | Carnival 8-K Ex. 99.1, 2022-04-26 (sec.gov)
9 | When did Kevin Lynch leave Adobe? | Resigned 2013-03-18 as EVP and CTO, effective 2013-03-22. Pre-announced unclear -> Y. | Adobe SEC filing as reported by 9to5Mac and The Register, March 2013
47 | What was Stiefler's title? | SVP, Financial Institutions Division. Exec unclear -> Y. Officer status not confirmed; flagged. | Justia (Intuit offer letter exhibit); MarketScreener
70 | When did Carlson give notice? | 2023-11-03, after the reference date. Pre-announced unclear -> N. | DISH 8-K, November 2023 (sec.gov)
