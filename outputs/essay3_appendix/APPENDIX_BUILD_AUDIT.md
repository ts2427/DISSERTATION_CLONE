# Essay 3 appendix - build audit

Produced by `scripts/245_essay3_appendix.py` alongside `ESSAY3_APPENDIX_TABLES.md` and `.docx`. Kept separate from the appendix so that the appendix contains only the title, Tables 1-11 and their notes, and so that grepping the appendix for a banned string cannot match an assertion name.

## ASSERTIONS

- T1 Panel B totals 1,054 **PASS**
- T1 Panel B every label is a GRADE_LABEL value **PASS**
- T1 Panel B no label is a raw final_grade code **PASS**
- T1 ledger closes (N never rises) **PASS**
- T1 treated + control == N at every populated step **PASS**
- T2 treated total == 109 **PASS**
- T2 clause totals == 70 / 39 **PASS**
- T3 totals == 109 / 296 **PASS**
- T6  30d treated + control == pooled on every count **PASS**
- T6  90d treated + control == pooled on every count **PASS**
- T6 180d treated + control == pooled on every count **PASS**
- T7 Panel A CV3 rows equal f1_ladder.csv **PASS**
- T9 Panel A has 27 rows **PASS**
- T9 Panel B events total 405 **PASS**
- T11 Panel A has 26 rows **PASS**
- T11 Panel B every title is verbatim in tmobile_502_text.md **PASS**
- T11 Panel B no title uses an abbreviation **PASS**
- T11 abbreviation regex is live (fires on 'EVP', quiet on the spelled-out title) **PASS**
- T11 Panel B title check has teeth (an abbreviated title is rejected) **PASS**
- T11 Panel B outcome-window column sums to 13 **PASS**
- T11 Panel B outcome-window sum equals Panel A 180-day Y count **PASS**
- Tables numbered 1-11 in order **PASS**
- No cell contains inf, nan, or a hyphen used as a minus sign **PASS**
- Note text contains no banned string (47 CFR, bare 'se', or a grade code) **PASS**

24 assertion(s): 24 PASS, 0 FAIL.

## NOT REGENERABLE

- none

## TEXT-TO-TABLE CHECK

163 figures checked; 0 MISMATCH. Full listing in `text_figures_check.csv`.

