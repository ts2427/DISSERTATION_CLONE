"""
ESSAY 2 APPENDIX - WORD DOCUMENT
=================================
Renders the 27-table appendix from outputs/tables/essay2_appendix/*.csv
into outputs/ESSAY2_APPENDIX.docx, matching the format of
ESSAY3_H6_APPENDIX.docx (scripts/create_essay3_appendix_docx.py): 1-inch
margins, centered bold title, Light Grid Accent 1 tables with bold
headers, bold-led indented Notes paragraphs.

Style rules applied to produced text (they intentionally differ from the
older exemplar's own text): no em dashes; p-values without leading zeros
in prose; no sentence-initial numerals. Data cells come verbatim from the
emitted CSVs (commit lineage 6e0fbb9).

    python scripts/178_essay2_appendix_docx.py
"""
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC = 'outputs/tables/essay2_appendix/'
OUT_PATH = 'outputs/ESSAY2_APPENDIX.docx'


def load(name):
    return pd.read_csv(SRC + name, dtype=str).fillna('')


def add_table(doc, df, font_pt=9, bold_first_col=False):
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr[i].text = str(col)
        for parag in hdr[i].paragraphs:
            for run in parag.runs:
                run.font.bold = True
                run.font.size = Pt(font_pt)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = str(val)
            for parag in cells[j].paragraphs:
                for run in parag.runs:
                    run.font.size = Pt(font_pt)
            if bold_first_col and j == 0:
                for run in cells[j].paragraphs[0].runs:
                    run.font.bold = True
    return table


def add_notes(doc, text, lead='Notes: '):
    notes = doc.add_paragraph()
    r = notes.add_run(lead)
    r.font.bold = True
    notes.add_run(text)
    for run in notes.runs:
        run.font.size = Pt(10)
    notes.paragraph_format.left_indent = Inches(0.25)
    doc.add_paragraph()


G12 = ('The two Gate-1-surviving malformed AT&T records are excluded from '
       'the canonical analysis (N = 333) and retained in the '
       'prior-specification replication, which reproduces that '
       'specification on its own terms, including its defects.')

NOTES = {
    1: ('Panel A is record level; treatment is undefined there. The '
        'volatility-window requirement is at least 15 daily returns in '
        'each 21-trading-day notification-anchored window ([-25, -5] and '
        '[+5, +25], anchor within 7 calendar days). ' + G12 + ' Source: '
        'scripts/163 (chain), sample_attrition.csv.'),
    2: ('Daily percentage points, not annualized: the standard deviation '
        'of daily log returns times 100 (scripts/163). Group statistics '
        'are computed within group with the group N shown. The '
        'health_breach row reports cell counts (treated 0 of 102, control '
        '15 of 229): the variable has zero treated-group variance and '
        'conditions the control group only.'),
    3: ('Pearson correlations, N = 333 analytical. The treatment-size '
        'correlation (r = .56) is the design\'s principal confound. The '
        'health_breach column with treatment is the phi implied by the '
        'empty treated cell.'),
    4: ('Year is the notification anchor year. Years lacking a treated or '
        'a control observation contribute nothing under year fixed '
        'effects: 2007, 2009, 2010, 2011, and 2016, together 52 events '
        '(3 treated); see Table 27.'),
    5: ("(a) The decomposition reproduces the prior specification on its own dependent variable, breach-anchored and annualized, at 891 records and 339 events; the corrected results follow at 333 events on daily log-return volatility (Table 18). (b) The prior partition is log market capitalization (Table 10); the canonical partition is log total assets. (c) Within-row comparisons are controlled; between-row comparisons change the unit of observation from records to events and are not. (d) The two Gate-1-surviving malformed AT&T records are excluded from the canonical analysis (N = 333) and retained here, because the replication reproduces the prior specification on its own terms, including its defects. (e) Treatment definitions: panel (i) is the record's own curated sic in 4813, 4841, or 4899; panel (ii) is Form 499 family membership with stage-2 CIKs mapped through the stage-4 equity-parent table; panel (iii) is the record-modal curated sic on events, same code set and annotation; panel (iv) is canonical fcc_form499 (scripts/154). Panels (ii) and (iv) reflect the September 4 date-conditional DISH re-adjudication: DISH is treated from the July 1, 2020 Boost divestiture, when DISH Wireless L.L.C. (FRN 0027852722, dba Boost Mobile) became an open family registration, so the eight DISH records (2023 breach dates) are Form 499 family. Under that correction the Form 499 repair attenuates the Q1 spike (+7.5556, p = .008608, to +5.1482, p = .069062) rather than eliminating it; the attenuation is driven entirely by the added registrants industry codes miss (GoDaddy, Twilio; Table 6). The prior name-token indicator (archive/16 classify_fcc) appears only as a footnote row; its six substring accidents move to Table 10 Panel B and the data-quality discussion."),
    9: ('Computed on the analytical sample (N = 333) across the 48 window '
        'specifications of the grid (scripts/166). The pre-deduplication '
        'vintage cannot support a grid: no committed security-day link '
        'exists for the retired record set.'),
    7: ('The group is defined against the industry-code baseline: records whose curated sic codes them as communications carriers yet carry no Form 499 family registration at the breach date. After the September 4 date-conditional DISH re-adjudication (DISH treated from the July 1, 2020 Boost divestiture; its eight records carry 2023 breach dates), the group contains only the two malformed ATT-SecurityBreach records: non-firm artifact records that drew returns from a matched security and were excluded from the canonical event set by Gate 1. The six substring accidents of the retired name-token indicator (Johnson Matthey, Suddenlink, Aero Charter, WillScot, Impact Mobile Home Communities, and Charter Next Generation) are not industry-coded as carriers and appear in Table 10 Panel B instead. The firm_size_log column is log market capitalization (Table 10).'),
    8: ('The size measure is log market capitalization (Table 10). Groups are defined against the industry-code baseline under the corrected DISH adjudication; the four cells sum to 891 (misclassified 2, concordant 160, missed-by-industry-codes 28, control 701). With two records in the misclassified cell the contrasts have Welch degrees of freedom near 2 and are reported for completeness, not inference. The pre-repair sensitivity row (14 records) undoes the join-gap repair and adds twelve Comcast records that are genuinely treated family.'
        " The missed-by-industry-codes row reports the 28 registrant records the code set cannot reach: its mean conceals opposing tails (the Q1 additions are strongly negative, the Q4 misses positive), which Table 6 decomposes."),
    6: ('Components are defined against the industry-code baseline on the prior market-capitalization partition, under the corrected DISH adjudication. The dropped component is empty: every industry-coded Q1 record with a family registration test failure before the re-adjudication was a DISH record, and DISH is Form 499 family at its 2023 breach dates. The Q1 attenuation (+7.5556 to +5.1482) therefore comes entirely from the added records: ten records, six events, mean volatility change -8.6179 (GoDaddy and Twilio, Form 499 filers industry-coded as software; one GoDaddy event contributes five identical records). The count identity holds: 33 stayed plus 10 added equals the 43 treated Q1 records of panel (ii).'),
    10: ('Panel A establishes that the prior specification\'s size '
         'variable is log market capitalization recorded under an assets '
         'label (slope .98, R-squared .87 against ln market cap; .46 and '
         '.44 against ln assets). Panel B lists the six verified '
         'identifier-collision sinks in the legacy annotation. The '
         'residual screen is one-sided: it detects collisions where the '
         'column and the re-match disagree, and a collision consistent '
         'across both passes with a small residual. Panel B is therefore '
         'a floor, not a census. Panel C is a second failure mode of the same class, found 9/6: the stage-5 ticker-to-permno fallback matched seven events to prior holders of recycled tickers (Facebook to Metatec, Motorola 2009 to Movie Star, DoorDash 2019 to Dash Industries). All seven carried no CRSP data in any build, so no estimate was touched; the fallback now rejects a name row that ended more than seven days before the event unless it is truncated at the extract boundary, and the seven resolve to no security, which is the true state of each event date.'),
    11: ("The base is the 355 events with a permno, a parseable notification, and notification on or before 2024-12-31, after the September 6 fallback guard removed seven recycled-ticker misidentifications that previously inflated the base (Table 10 Panel C). The window-missing and covariate-missing sets no longer overlap, so the arithmetic reconciles: 355 minus 4 minus 15 minus 1 minus 2 equals 333. The three Compustat covariates are missing on the same 15 events (one join failure, not three)."),
    12: ("Registration is the treatment criterion; universal-service contributor status is not. Two registry entries carry end dates preceding their start dates, a defect in the registry source data. The Twilio row is flagged: the matched filer (Twilio Inc, FRN 0020237343) differs from the FRN carrying the Interconnected VoIP classification (Twilio US Technology Inc., FRN 0028844892). Coverage was verified against every treated event's breach date on 9/2/2026 and re-verified across all twelve parents on 9/4/2026 after the DISH re-adjudication; the CSV carries all family registration rows. The events column sums to 104."),
    13: ("Twenty-two signed stage-4 adjudication rules plus three equity-parent re-mappings. Matching is name-based; one rule is date-conditional, adjudicated September 4: DISH is treated on or after the July 1, 2020 Boost divestiture (DISH Wireless L.L.C., FRN 0027852722, dba Boost Mobile, an open family registration at its breach dates) and retains the satellite exclusion before it. Gate 1 and Gate 2 verdict files: outputs/rebuild/GATE1_*, GATE2_ADJACENCY_SHEET (scripts/150-153)."),
    14: ("Compustat sich, canonical events; 143 events lack sich (Table 16). These conventions were built for other purposes; the table reports what industry codes can express about the contribution base, not an error audit of their authors."),
    15: ('Counts reconcile to Table 14. Subsidiary events carry the '
         'parent ticker\'s sich: Verizon Media and NBC Sports inherit '
         'their families\' codes.'),
    17: ('The curated sic column is a hand annotation in the source file '
         '(DataBreaches.xlsx), not a Compustat field. It hand-codes '
         'T-Mobile, AT&T, and Verizon as 4813 or 4833 where Compustat '
         'says 4812.'),
    16: ("Eleven treated events lack sich. The classification comparison covers 346 of 489 canonical events (70.8 percent) and 107 of 118 treated events (90.7 percent)."),
    18: ('The R-squared base includes a mechanical relationship: the '
         'dependent variable is a change score regressed on its own '
         'baseline. Conditioning on the baseline is the standard ANCOVA '
         'choice and is cited as such; the progression is not a measure '
         'of explanatory power. health_breach conditions the control '
         'group only (zero treated-group variance).'),
    19: ("Clustering on final_cik; G = 82, with 12 treated clusters and an effective cluster count of 24.2. Weight schemes: Rademacher and Webb six-point; bootstrap p resolution is 1/(B+1). Every apparent rejection in this essay outside the classification work, namely the prior draft's headline, the Q1 and Q3 quartile cells, and the industry fixed-effects specification, is produced by the same standard-error choice, one blind to within-parent correlation across twelve treated parent entities. All are null under the calibrated frame."),
    20: ("All quantities are on the CV3 frame. The negative direction is rejected at the SESOI (one-sided p = .028); the positive is not (p = .355). The null is bounded on one side. Failed equivalence evaluations are reported, not omitted. The asymptotic floor replaces unattainable entries: no treated count brings the design below 4.05 annualized percentage points with the control side fixed."),
    22: ("The variable is reported_date minus breach occurrence date and proxies neither statutory clock of 47 C.F.R. 64.2011(b). Exactly 117 of 333 delays are zero (35.1 percent, occurrence defaulted to notification); no compliance claim attaches to the sub-floor share, and the q10 and q25 quantile rows sit inside the zero mass and are uninformative. Treated dispersion is higher than control, the opposite of the floor-compression prediction."),
    21: ("The announcement-window family is four pre-specified tests; the base treatment-on-elevation specification is the pre-specified member and rejects at its Benjamini-Hochberg threshold (p = .026 against .0375). The conditioning rows are sensitivities; all four sit numerically below that threshold but only the pre-specified member is BH-tested. Program-wide, 62 tests were run, enumerated one row per test in Table 28 (scripts/182); about 3.1 rejections would be expected by chance under a global null, and the program produced one. The differential lives on the control side (treated elevation -.029, control -.123); identifying its source requires data the design does not have. Reported, not interpreted."
        " Panel C calibrates the elevation measure (scripts/180): the c4(n) unbiasing correction shifts levels (the treated mean is exactly zero corrected) and leaves inference invariant; parent-preserving placebo dates (200 draws, seed 499) put quiet-day elevation at +0.031 against the breach-date -0.094, so breach dates genuinely damp, on the control side, and no placebo draw reaches the actual differential or rejects under CV3; the earnings benchmark on the same securities is +0.788 daily pp (t = 14.6, N = 5,057 announcements), the scale of a real information event on this measure."
        " Panel A carries each channel measure's correlation with the main volatility change (from the chain artifact t36). Panel D is the raw-to-adjusted buildup of the announcement differential: the unadjusted gap is +0.094 (p = .368); conditioning on baseline abnormal volatility (treated enter the window higher, 1.54 against 1.29, and elevation is mean-reverting, r = -.49) and firm size carries four fifths of the movement to +0.4475, so the differential is a covariate-adjusted quantity and is reported with its raw counterpart."),
    23: ("Note 1: organization and parent counts do not sum to sample totals because a firm's events fall in different quartiles as its assets change. Note 2: all four cells rest on five or fewer treated parent entities; under the frame all four are inconclusive, and the HC3 rejections are the anticonservative-bound artifact. Note 3: quartile membership is sensitive to sample composition, but at this sample the malformed-record exclusion moves only three events across boundaries and no treated event changes quartile (treated counts 2, 14, 29, and 59 under both compositions). Note 4: where health_breach is constant in a cell, the HC3 fit retains it by pseudoinverse and the stated cell df reflects the reduced rank; the CV3 fit drops it, as flagged in the dropped_in_cv3 column."),
    24: ('The cutoff is December 8, 2007, the effective date of 47 '
         'C.F.R. Sec. 64.2011 (FCC DA 07-4915). The six events are '
         'identical under the breach-date and reporting-date anchors, '
         'and all are control.'
        "All rows are the analytical sample (N = 333)."),
    25: ('The grid is 192 realized-SD specifications (anchor, day basis, '
         'window length, gap, return type, winsorization) plus one '
         'GARCH(1,1) row. Within-grid inference is CV1 parent-CIK and '
         'descriptive; dispersion is the finding.'
        " Panel B is the joint permutation test (Simonsohn, Simmons and Nelson 2020, step 3; scripts/181): treatment permuted at the parent filer entity level preserving 12 of 82 treated clusters, 1,000 draws, p resolution 1/1001. None of the three statistics rejects (median p = .242, dominant-sign p = .345, significant-dominant p = .400). Unanimous-sign curves arise in over a third of placebo draws, so sign unanimity measures the grid correlation structure, not effect strength; the observed curve has fewer significant specifications than the average placebo curve."),
    26: ("The three panels are one argument about which observations carry the estimate: it is robust to control-side composition (the pre-rule exclusion moves it 0.063 CV3 standard errors), largely attributable to one carrier on the treated side (deleting Sprint removes 74 percent of the point estimate), and not robust to influential observations. The last reverses the prior draft's claim that outlier exclusion strengthened the estimate."
        "All panels are on the analytical sample (N = 333; G = 82)."
        " Panel A also states the full leave-one-cluster-out range with the deleted cluster identified at each end, and the cluster-size coefficient of variation computed from the per-cluster diagnostic table."),
    27: ('All three specifications are null under the CV3 frame; the '
         'industry-only HC3 rejection was the anticonservative bound on '
         'a two-mixed-cell identification. Effective identifying samples '
         'appear beside the nominal N; the excluded year strata are '
         'named in Table 4. No rank deficiency; no warnings emitted.'),
    28: ('One row per hypothesis test: originating script, family, and test name. Concatenation of the N_TESTS ledgers the six testing scripts already keep (scripts 164, 169, 170, 174, 175, 176), captured unmodified by scripts/182; no test is added or re-counted. Family labels pool across scripts and the script column disambiguates (H1 is 3 tests in scripts/164 and 9 in scripts/170). Total 62; at a 5 percent global null about 3.1 rejections would be expected, and the program produced one (Table 21).'),
}

SECTIONS = [
    ('SAMPLE AND DATA', [1, 2, 3, 4]),
    ('THE PRIOR-SPECIFICATION DECOMPOSITION', [5, 6, 7, 8, 9, 10, 11]),
    ('CLASSIFICATION AND TREATMENT', [12, 13, 14, 15, 16, 17]),
    ('MAIN RESULTS AND INFERENCE', [18, 19, 20]),
    ('DELAY AND CHANNEL TESTS', [21, 22]),
    ('HETEROGENEITY AND ROBUSTNESS', [23, 24, 25, 26, 27]),
    ('PROGRAM TEST ENUMERATION', [28]),
]

TITLES = {
    1: 'Sample Attrition', 2: 'Descriptive Statistics (N = 333)',
    3: 'Correlation Matrix (N = 333)', 4: 'Events by Year (N = 333)',
    5: 'Four-Panel Decomposition: Industry Codes Against Form 499 (891 Records / 339 Events)',
    9: 'Gradient Across the Corrected-Data Specification Grid',
    7: 'The Misclassified Group, Per Record (2 Records, Industry-Code Baseline)',
    8: 'Group Comparisons (891 Records)',
    6: 'The Q1 Transition (Prior Market-Capitalization Partition)',
    10: 'Variable Construction and Identifier Collisions (Panels A, B, C)',
    11: 'Missingness Before the Complete-Case Restriction (Base 355)',
    12: 'Form 499 Registry Matches for Treated Parent Entities (12 '
        'Parents, 104 Events)',
    13: 'Adjudications', 14: 'Industry-Code Conventions Against Form 499 '
    'Registration (346 Testable Events)',
    15: 'Classification Errors by Named Organization',
    17: 'Compustat sich Against the Curated sic Column',
    16: 'Treated Events Outside the Classification Comparison',
    18: 'Nested Models M1-M4 (N = 333)',
    19: 'Inference Ladder (N = 333; G = 82)',
    20: 'Design Resolution: SESOI, MDE, TOST, Required Parents',
    22: 'Disclosure Delay (N = 333)',
    21: 'Channel Tests (Panels A through D)',
    28: 'Program-Wide Test Enumeration (62 Tests, One Row Per Test)', 23: 'Size Quartiles, Canonical Specification '
    '(ln Total Assets, N = 333)',
    24: 'Pre-Rule Observations',
    25: 'Specification Curve (Panels A and B)',
    26: 'Cluster Deletion, Pre-Rule, and Influence',
    27: 'Fixed-Effects Specifications (N = 333)',
}


def table12_display():
    df = load('form499_registry_matches.csv')
    rows = []
    for cik, g in df.groupby('parent_cik'):
        named = g[g['evidence_named'] == 'YES']
        typed_open = g[(g['type'] != '') & (g['end'] == 'open')]
        pick = named.iloc[0] if len(named) else (
            typed_open.iloc[0] if len(typed_open) else g.iloc[0])
        n_defect = int((g['end_before_start'] == 'DEFECT').sum())
        rows.append(dict(
            parent_cik=cik,
            filer=pick['legal_name'],
            FRN=pick['FRN'],
            basis=('evidence FRN' if len(named) else 'adjudicated'),
            start=pick['start'], end=pick['end'],
            type=pick['type'], USF=pick['usf'],
            events=pick['events_in_sample'],
            event_span=pick['event_span'],
            coverage='OK (verified 9/2/2026; re-verified 9/4/2026)',
            flags=('FRN differs from service-typed filer'
                   if cik == '1447669' else '')
            + (f'; {n_defect} registry end<start' if n_defect else '')))
    out = pd.DataFrame(rows)
    assert out['events'].astype(int).sum() == 104
    assert len(out) == 12
    return out


def build():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title.add_run('ESSAY 2 APPENDIX: MANDATORY DISCLOSURE TIMING AND '
                       'INFORMATION ASYMMETRY')
    tr.font.size = Pt(14)
    tr.font.bold = True
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub.add_run('Analytical sample N = 333 (104 treated, 229 '
                     'control); inferential frame CV3; commit lineage '
                     '6e0fbb9')
    sr.font.size = Pt(12)
    sr.font.italic = True
    doc.add_paragraph()

    global FILES_STATIC
    FILES = {
        1: [('sample_attrition.csv', None)],
        2: [('descriptives_by_treatment.csv', None),
            ('descriptives_differences.csv', None)],
        3: [('dv_correlations.csv', None)],
        4: [('events_by_year.csv', None)],
        5: [('four_panel_decomposition.csv', None)],
        9: [('gradient_grid.csv', None)],
        7: [('misclassified_records.csv', None)],
        8: [('misclassified_group_comparisons.csv', None),
            ('misclassified_group_contrasts.csv', None)],
        6: [('q1_transition_components.csv', None),
            ('q1_transition_records.csv', None)],
        10: [('size_variable_reconciliation.csv', None),
             ('identifier_collisions.csv', None),
             ('identifier_collisions_recycled_tickers.csv', None)],
        11: [('missingness_precase.csv', None)],
        12: 'SPECIAL',
        13: [('treatment_adjudications.csv', None)],
        14: [('sic_conventions_vs_form499.csv', None)],
        15: [('sic_convention_errors.csv', None)],
        17: [('sich_vs_curated_sic.csv', None)],
        16: [('sich_unavailable_treated.csv', None)],
        18: [('nested_models.csv', None)],
        19: [('inference_ladder.csv', None)],
        20: [('design_resolution.csv', None)],
        22: [('disclosure_delay.csv', None),
             ('delay_distribution_by_group.csv', None),
             ('delay_quantiles.csv', None)],
        21: [('channel_microstructure.csv', None),
             ('channel_announcement_differential.csv', None),
             ('channel_elevation_calibration.csv', None),
             ('channel_announcement_buildup.csv', None)],
        28: [('program_test_enumeration.csv', None)],
        23: [('size_quartiles.csv',
              [['quartile', 'coef_cv3', 'se_cv3', 'ci_lo', 'ci_hi',
                'p_cv3', 'G_cell', 'mde80_cv3', 'tost_p', 'verdict',
                'bh_adjusted_p'],
               ['quartile', 'cellN', 'treatedN', 't_orgs', 't_parents',
                'se_hc3_bound', 'p_hc3_bound', 'hc3_cell_df',
                'dropped_in_cv3']])],
        24: [('prerule_events.csv', None)],
        25: [('specification_curve.csv', None),
             ('specification_curve_permutation.csv', None)],
        26: [('cluster_deletion_prerule.csv', None)],
        27: [('fixed_effects.csv',
              [['spec', 'coef', 'se_cv3', 'ci_lo', 'ci_hi', 'p_cv3', 'G',
                'N', 'R2', 'se_hc3_bound', 'p_hc3_bound'],
               ['spec', 'rank', 'warnings',
                'effective_identifying_sample']])],
    }
    FILES_STATIC = FILES
    for sec_title, nums in SECTIONS:
        doc.add_heading(sec_title, level=1)
        for n in nums:
            doc.add_heading(f'TABLE {n}: {TITLES[n]}', level=2)
            if FILES[n] == 'SPECIAL':
                add_table(doc, table12_display(), font_pt=8)
            else:
                multi = len(FILES[n]) > 1
                for pi, (fname, colsets) in enumerate(FILES[n]):
                    if multi:
                        cap = doc.add_paragraph()
                        cr = cap.add_run(f'Panel {chr(65 + pi)}')
                        cr.font.bold = True
                        cr.font.size = Pt(9)
                    df = load(fname)
                    if colsets is None:
                        fp = 8 if len(df.columns) > 9 else 9
                        add_table(doc, df, font_pt=fp)
                        doc.add_paragraph()
                    else:
                        for cols in colsets:
                            add_table(doc, df[cols], font_pt=9)
                            doc.add_paragraph()
            add_notes(doc, NOTES[n])
    doc.add_heading('SOURCE MANIFEST', level=1)
    add_table(doc, load('manifest.csv'), font_pt=8)
    add_notes(doc, 'All tables regenerate from '
              'outputs/tables/essay2_appendix/ via the committed Essay 2 '
              'chain (scripts/163-177) and this script. Full-precision '
              'values live in the CSVs; printed values follow manuscript '
              'rounding.')
    doc.save(OUT_PATH)
    write_markdown()
    print(f'[OK] {OUT_PATH} written '
          f'({sum(len(v) if isinstance(v, list) else 1 for v in FILES.values())} tables rendered)')



MD_PATH = 'outputs/ESSAY2_APPENDIX.md'
FILES_STATIC = None


def write_markdown():
    """Plain-markdown twin of the docx, for checking."""
    L = ['# Essay 2 Appendix', '',
         'Analytical sample N = 333 (104 treated, 229 control; G = 82 '
         'parent filer entities, G1 = 12). All tables from '
         'outputs/tables/essay2_appendix/*.csv via the committed Essay '
         '2 chain.', '']
    for sec_title, nums in SECTIONS:
        L += [f'## {sec_title}', '']
        for n in nums:
            L += [f'### TABLE {n}: {TITLES[n]}', '']
            if FILES_STATIC[n] == 'SPECIAL':
                dfs = [table12_display()]
            else:
                dfs = [load(f) for f, _ in FILES_STATIC[n]]
            for pi, df in enumerate(dfs):
                if len(dfs) > 1:
                    L.append(f'**Panel {chr(65 + pi)}**')
                    L.append('')
                L.append('| ' + ' | '.join(str(c) for c in df.columns)
                         + ' |')
                L.append('|' + '---|' * len(df.columns))
                for _, r in df.iterrows():
                    L.append('| ' + ' | '.join(str(v) for v in r) + ' |')
                L.append('')
            L += [f'Notes: {NOTES[n]}', '']
    md = chr(10).join(L) + chr(10)
    assert chr(8212) not in md
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(md)

if __name__ == '__main__':
    for num, txt in NOTES.items():
        assert chr(8212) not in txt, f'em dash in note {num}'
    build()
