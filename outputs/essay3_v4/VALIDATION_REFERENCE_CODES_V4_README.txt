VALIDATION REFERENCE CODES — REBUILD V4, NEW-DOCUMENT ROUND
(saved as VALIDATION_REFERENCE_CODES_V4.psv, '|'-delimited; same fields and format as
 VALIDATION_REFERENCE_CODES_R2.psv)

PROVENANCE (recorded in the same terms as the v3 rounds):
- Tim did NOT hand-code. The reference codes were produced by Claude (Claude Opus 5, this
  session), coded BLIND to any classifier output. Disclosed exactly as the v3 rounds
  disclosed their LLM coder.
- BLIND IS A PROPERTY HERE, NOT A CLAIM. The frozen classifier (scripts/220) had never
  been run on these documents when the codes were written: no c_filing_codes.csv,
  c2_outcomes_events.csv or any other 220 output existed on disk for them, and this
  file is committed BEFORE the first classifier run so that git history, not assertion,
  fixes the order.
- Coded from the Item 5.02 text only, extracted with the same helpers scripts/196 used to
  build the v3 sheet (to_text -> section_502 -> strip_caption). Those are text-extraction
  functions; classify() was never called.
- No URL was opened and no external source was consulted during coding. Where the text
  does not settle a question, the row is flagged for adjudication rather than resolved
  from outside knowledge. This differs from the v3 rounds, which ran a verification pass
  against outside sources on uncertain rows; no verification pass has been run here.

THE DRAW:
- 30 documents from outputs/rebuild_v4/237_validation_new_ids.csv, seed 20260919.
- Pool = files under Data/edgar/item5_02_text/ that are NOT in git ls-tree -r v3-frozen,
  intersected with the documents named in b_scope_filings.csv: 1576 on disk - 1126 frozen
  = 450 added by v4, all 450 in scope. Size = min(30, 450).
- sheet_id is assigned by sorting the draw on (cik, accession). The mapping from sheet_id
  to cik / accession / local_file is validation_ids_v4.csv, written with this file.
- These are NEW documents only, so none was seen by the v3 rounds. The v3-era draws and
  the v2 classifier are frozen; no result from this round may retune them.

RULES APPLIED — the round-1 and round-2 rules, unchanged:
  Sheet README (VALIDATION_SHEET_R2.xlsx):
    EXEC officer departure = Y if the filing reports that a person leaves (resigns,
      retires, is terminated, steps down, dies, or will leave on a stated date) a position
      as principal executive officer, president, principal financial officer, principal
      accounting officer, principal operating officer, or another named executive /
      executive officer. Appointments, elections and pay items alone are N.
    CEO departure = Y if the person leaving is the principal executive officer.
    DIRECTOR-ONLY departure = Y if a person who serves only as a director leaves the board.
    pre-announced = Y if the text references an announcement, agreement or notice about
      the departure dated BEFORE the reference date; unclear if it says "as previously
      announced/disclosed" without a date; N otherwise (or if there is no departure).
  Round-1 interpretive rules 1-5 (VALIDATION_REFERENCE_CODES_R1_README.txt), in particular
    rule 2 (leaving a covered title counts even if the person stays employed), rule 3
    (a restated departure is Y with restates_prior_disclosure = Y) and rule 4 (EVP/SVP
    departures reported under Item 5.02 are executive-officer departures when the text
    does not state officer status).
  Round-2 rulings: pay-agreement departures count; vacancy mentions count for directors
    only; pre-announced includes effective dates before the reference date; restatements
    flagged in restates_prior_disclosure.

NOTE ON pre_announced IN THIS ROUND:
  The reference date is the EVENT's reported_date, and the pool is drawn from the whole
  fetch window [min(bd, rd) - 730d, max(bd, rd) + 180d]. Many drawn filings therefore sit
  in the baseline window, years before the reference date, and pre_announced is Y
  mechanically. That is the rule as round 1 stated and applied it; it is recorded here so
  the figure is not misread as a substantive finding.

CANDIDATES FOR ADJUDICATION (4): sheets 12, 13, 21, 28.
  Each is coded, with the reasoning and the competing reading given in its notes field.
  None was resolved by consulting a source outside the filing text.

COUNTS: exec_departure Y=5 (sheets 5, 8, 13, 21, 27); ceo_departure Y=0;
        director_only_departure Y=2 (sheets 16, 30); pre_announced Y=6;
        restates_prior_disclosure Y=0.
