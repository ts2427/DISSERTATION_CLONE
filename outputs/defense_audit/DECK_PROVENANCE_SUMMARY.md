# Deck provenance summary (Part A1/A3)

Source: `DECK_TEXT_V25.md` (45 slides; not committed). Full table: `DECK_PROVENANCE.csv` (424 numbers from 41 slides).
Essay 2 numbers are matched against the defense-final outputs (the deck's vintage); where the v5 chain differs, the v5 value is in the note.

| status | n |
|---|---:|
| MATCH | 347 |
| NO-SOURCE | 61 |
| DERIVED | 13 |
| MISMATCH | 2 |
| ROUNDING | 1 |

## MISMATCH (2)

| slide | quoted text | value on slide | source / note |
|---|---|---|---|
| e3q (23) | disclosed under Item 5.02(b) | 5.02(b) | scripts/220_essay3_v4_classifier_v2.py lines 26-29, 28 Item 5.02 section (sub-items a-f recorded, not filtered); the outcome is any executive departure in the Item 5.02 section text, not restricted to sub-item (b) |
| brepro (B9) | all 99 analytic values match Python | 99 | r_replication/VERIFICATION.md line 9 (current, c298475): "143 / 143 of 143"; 1566d02:r_replication/VERIFICATION.md:9 "99 of 99" 143 of 143; deck carries the superseded same-day 1566d02 count; current file reports 143 of 143 analytic values plus 8 of 8 Essay 1 90% CIs (line 10) |

## NO-SOURCE (61)

| slide | quoted text | value on slide | source / note |
|---|---|---|---|
| motivation (2) | T-Mobile's 2021 breach | 2021 |   ; literature/regulatory - not a pipeline output |
| motivation (2) | affected 76 million people | 76 million |   ; literature/regulatory - not a pipeline output |
| motivation (2) | settled class claims for $350 million | $350 million |   ; literature/regulatory - not a pipeline output |
| motivation (2) | (In re T-Mobile, 2023) | 2023 |   ; literature/regulatory - not a pipeline output |
| motivation (2) | $31.5 million FCC enforcement action | $31.5 million |   ; literature/regulatory - not a pipeline output; essay text gives a $15.75M penalty plus an equal security spend (sum $31.5M), consistent |
| motivation (2) | breaches in 2021, 2022, and 2023 | 2021, 2022, 2023 |   ; literature/regulatory - not a pipeline output |
| motivation (2) | (FCC, 2024b) | 2024 |   ; literature/regulatory - not a pipeline output |
| rule (3) | 47 CFR § 64.2011 | § 64.2011 |   ; literature/regulatory - not a pipeline output |
| rule (3) | DAY 0 | 0 |   ; literature/regulatory - not a pipeline output |
| rule (3) | ≤ 7 BUSINESS DAYS | 7 business days |   ; literature/regulatory - not a pipeline output |
| rule (3) | ≥ 7 MORE BUSINESS DAYS | 7 business days |   ; literature/regulatory - not a pipeline output |
| rule (3) | Adopted in the 2007 CPNI Order | 2007 |   ; literature/regulatory - not a pipeline output |
| rule (3) | published June 8, 2007 | June 8, 2007 |   ; literature/regulatory - not a pipeline output |
| rule (3) | 72 FR 31948 | 72 FR 31948 |   ; literature/regulatory - not a pipeline output |
| rule (3) | effective December 8, 2007 | December 8, 2007 |   ; literature/regulatory - not a pipeline output |
| rule (3) | The 2024 amendments are delayed indefinitely | 2024 |   ; literature/regulatory - not a pipeline output; Essay 2 Methods (M027) says the amendments were "adopted in 2023" - make the year consistent |
| rule (3) | NOTES: at least seven more business days | seven |   ; literature/regulatory - not a pipeline output |
| chain (4) | public firms reporting breaches after December 8, 2007 | December 8, 2007 |   ; literature/regulatory - not a pipeline output; the pipeline uses the same cutoff 2007-12-08 (outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md:20, 94) |
| chain (4) | 47 CFR § 64.2011 (a Form 499 filer) | § 64.2011 |   ; literature/regulatory - not a pipeline output |
| roadmap (5) | 4 min (rule, premise, data) | 4 min |   ; presentation timing - not a data value |
| roadmap (5) | 10 min (Essay 1) | 10 min |   ; presentation timing - not a data value |
| roadmap (5) | 10 min (Essay 2) | 10 min |   ; presentation timing - not a data value |
| roadmap (5) | 10 min (Essay 3) | 10 min |   ; presentation timing - not a data value |
| roadmap (5) | 4 min (together) | 4 min |   ; presentation timing - not a data value |
| roadmap (5) | NOTES: Thirty seconds | 30 seconds |   ; presentation timing - not a data value |
| roadmap (5) | NOTES: the next forty minutes | 40 minutes |   ; presentation timing - not a data value; the five blocks sum to 38 min (4+10+10+10+4) |
| e1div (7) | NOTES: Ten minutes | 10 minutes |   ; presentation timing - not a data value |
| e1q (8) | (Akerlof, 1970) | 1970 |   ; citation year - literature, not a pipeline output |
| e1q (8) | Diamond & Verrecchia, 1991 | 1991 |   ; citation year - literature, not a pipeline output |
| e1q (8) | (Spence, 1973) | 1973 |   ; citation year - literature, not a pipeline output |
| e1q (8) | (Tushman & Nadler, 1978) | 1978 |   ; citation year - literature, not a pipeline output |
| e1model (9) | it matches the two-day penalty in Cavusoglu et al. (2004) | two-day; 2004 |   ; literature/regulatory - not a pipeline output; A2-8: untracked drafts give Cavusoglu -2.1% with no "two-day"; another draft says -1.0% to -1.5% |
| e1results (10) | axis tick −8 | −8 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick −6 | −6 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick −4 | −4 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick −2 | −2 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick 0 | 0 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick +2 | +2 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick +4 | +4 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick +6 | +6 |   ; chart axis tick label - not a data value |
| e1results (10) | axis tick +8 | +8 |   ; chart axis tick label - not a data value |
| e1take (14) | NOTES: Ten minutes ends here | 10 minutes |   ; presentation timing - not a data value |
| e2div (15) | NOTES: Ten minutes. | ten minutes |   ; presentation timing note, not a data claim |
| e2q (16) | H5a · Disclosure delay | H5a |   ; the labels H5a / H5b appear nowhere in the repo (docs, outputs, scripts, archive searched) |
| e2q (16) | H5b · Uncertainty after disclosure | H5b |   ; label not in repo (see H5a) |
| e2q (16) | Tushman & Nadler, 1978 | 1978 |   ; literature/regulatory — not a pipeline output |
| e2q (16) | Fabrizio & Kim, 2019 | 2019 |   ; literature/regulatory — not a pipeline output |
| e2q (16) | Diamond & Verrecchia, 1991 | 1991 |   ; literature/regulatory — not a pipeline output |
| e2results (18) | H5a and H5b are not rejected | H5a/H5b |   ; labels not in repo; the underlying nulls are t26 and e2_delay_ladder |
| e3div (22) | NOTES: Ten minutes. | ten minutes |   ; presentation timing note, not a data claim |
| future (32) | Since December 2023 | December 2023 |   ; literature/regulatory - not a pipeline output; Tim to check PDFs (SEC Item 1.05 effective 2023-12-18) |
| future (32) | within four business days | 4 |   ; literature/regulatory - not a pipeline output; Tim to check PDFs |
| bbound (B1) | Cavusoglu et al. (2004) / Two days / -2.1% | -2.1% two days |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Gordon et al. (2024), 670 breaches | 670 |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Gordon et al. (2024) / Three days / -0.63% | -0.63% three days |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Kamiya et al. (2021) / Three days / -1.09% | -1.09% three days |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Martins et al. (2025), 53 major attacks | 53 |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Martins et al. (2025) / Three days / -4.08% | -4.08% three days |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | Campbell et al. (2003) / Event window / -5.46% | -5.46% |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | exceeds Gordon et al.'s 0.63% | 0.63% |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |
| bbound (B1) | matches Cavusoglu et al.'s two-day penalty | 2.1% two-day |   ; literature/regulatory - not a pipeline output; Tim to check PDFs; untracked March drafts: Cavusoglu -2.1% with no "two-day", another draft -1.0% to -1.5%; Gordon -2.91/-0.35/-1.04, no -0.63%; Kamiya/Martins/Campbell absent (A2_TENSION_CHECKS.md A2-8) |

## ROUNDING (1)

| slide | quoted text | value on slide | source / note |
|---|---|---|---|
| e2results (18) | Volatility change ... Wild bootstrap p .333 | .333 | outputs/tables/essay2_v2/t26_inference_ladder.csv row 5 (WCR) p 0.3325; 0.3325 -> .333 under round-half-up (.332 under round-half-even); v5: .4257 |
