"""
RUN_ALL_ANALYSIS.py - Complete Dissertation Analytics Pipeline
================================================================

Executes the entire dissertation workflow with comprehensive logging:
1. Summary Statistics (Table 1)
2. Essay 2: Main Regression Analysis (Tables 2-5, Firm-Clustered SEs + TOST + VIF)
3. FCC Causal Identification (TABLE B8: Post-2007 Interaction Test)
4. Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)
5. Essay 3: Main Regression Analysis (Tables 2-3)
6. ML Model Training & Validation (Optional)
7. Recommendation Scripts (Scripts 91-95: Mediation, Heterogeneity, Window Sensitivity, Falsification, Low R²)
8. Robustness Checks (9 checks including alternative windows, timing, samples, SEs, fixed effects)

All output is captured to timestamped log file.

Key Enhancements (Phase 3):
- Firm-clustered standard errors as main specification
- TOST equivalence test for H1 null hypothesis validation
- VIF multicollinearity diagnostics
- Post-2007 interaction test for FCC causal identification
- Comprehensive robustness comparisons

Author: Timothy D. Spivey
Dissertation: Data Breach Disclosure Timing and Market Reactions
University of South Alabama
Date: February 2026

DATA PIPELINE ROOT
==================
  -> Data/processed/rebuild/CANONICAL_V3.csv, built by scripts/150-157.

Treatment variable: fcc_form499 (Form 499 filer at breach date), which replaced the
SIC-based fcc_reportable proxy. The 7/28/2026 membership adjudications still hold
(Cricket treated, Boost treated, DISH untreated, Aero Charter excluded); the DISH
adjudication was revisited 2026-09-04 and is date-conditional.

HISTORY, NOT CURRENT: this block previously named
Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv as the source of truth,
with 118 treated / 37 firms in the CRSP sample and 115 treated in an N = 648 regression
sample. Those are PRE-REBUILD figures, superseded by the v3 rebuild (1,054 notification
records -> 758 -> 524 -> 489 events). The live sample sizes are not restated here, so
that this docstring cannot go stale again: read them from
outputs/rebuild/constants_v3.json (Essay 1) and outputs/tables/essay2_v2/ (Essay 2).
Note that constants_v3.json is itself STALE against today's CANONICAL_V3 pending the
rebaseline; scripts/247 prints both values and says so.

The old regeneration chain named here was 46 -> 53 -> 99 -> 98 -> 121a-c -> 122.
Scripts 46 and 99 were retired on 2026-09-29 (Part H): both read the pre-rebuild dataset
and feed nothing cited. 53 still runs, merging 46's committed output.

ESSAY 3 OUTCOME — CURRENT (v4 chain, 2026-09-29 ruling)
=======================================================
AUTHORITATIVE: the v4 chain, scripts 212-246, with its baseline in
outputs/essay3_v4/constants_essay3_v4.json and its appendix in outputs/essay3_appendix/.
v4 changes the SAMPLE, not the method: the classifier functions are byte-identical to
scripts/195 by AST and the estimator is identical line for line, but the point-in-time
CRSP relink moves the sample to N = 405 with 109 treated events across 13 parent CIKs
(G = 119). Six steps in the chain assert against their own outputs.

The Query 2 chain below is RETIRED (2026-09-29). It stays staged only because its
outputs are the v3 side of the scripts/239 side-by-side. Its description follows.

Executive departure reported under Item 5.02(b), coded from the filing text by the
final deterministic classifier scripts/195 (v2, commit 6f7be7a; validated in two blind
rounds + a stratified recall audit; stopping rule in outputs/ESSAY3_QUERY2_REPORT.md).
Chain: 187 (text fetch, cached) -> 195 (classifier) -> 199 (sample) -> 202 (estimation,
asserts vs outputs/essay3_q2/constants_essay3_q2.json) -> 190/191 (T-Mobile data) -> 203.
RETIRED 2026-09-11: script 46's any-Item-5.02 flags as the Essay 3 outcome (Item 5.02
covers appointments, elections and pay, not only departures). Script 46 itself was
retired 2026-09-29 (Part H); script 53 continues to merge its committed output,
Data/enrichment/executive_changes.csv, which stays tracked.

IF YOU ARE RUNNING THIS FOR THE FIRST TIME, READ THIS
=====================================================
What the dissertation's current results are, and where they come from:

  Essay 1 (market reaction)      canonical v3 chain, scripts 150-158
                                 -> outputs/rebuild/constants_v3.json (assertion baseline)
                                 -> outputs/rebuild/appendix_v3/ (16 tables; Word build scripts/160)
  Essay 2 (information asymmetry) canonical chain, scripts 163-182
                                 -> outputs/tables/essay2_v2/ and the outputs/ESSAY2_*.md reports
  Essay 3 (governance response)  v4 chain, scripts 212-246 (AUTHORITATIVE, 2026-09-29)
                                 -> outputs/essay3_v4/ and outputs/essay3_appendix/
                                 -> its own baseline, outputs/essay3_v4/constants_essay3_v4.json.
                                    Essay 3 results do NOT come from scripts/158 or constants_v3.json;
                                    since 2026-09-29 scripts/158 writes no Essay 3 value at all.
                                    The Query 2 chain (187/195/199/202/190/191/203/204) is RETIRED.

All three essays report NULL results. The design is post-2007 cross-sectional: there are no treated
events before the rule took effect, so nothing here supports a causal or natural-experiment claim.
Inference is CV3 (cluster jackknife) plus a wild cluster bootstrap; HC3 is reported for comparison
only and is DISQUALIFIED as a significance test. Start from README.md and, for Essay 3,
outputs/essay3_q2/ESSAY3_STARTING_POINT.md.

WHAT THIS PIPELINE DOES NOT REGENERATE (know this before trusting a clean run):
  1. Git LFS. FIXED 2026-09-29 (Part I3): the filter=lfs attribute was dropped for 87 committed
     pointer files in 5f5c950, so a clean clone wrote 130-byte placeholders with NO error and every
     reader of them degraded silently. All 87 rules are restored in .gitattributes, and Part I1 adds
     an executable guard that scans for placeholder content before any step runs and aborts. A
     placeholder begins "version https://git-lfs.github.com/spec/v1"; the fix is `git lfs pull`.
  2. outputs/tables/essay2_appendix/*.csv (41 files) have NO committed generator. scripts/178 only
     renders them into ESSAY2_APPENDIX.docx (itself gitignored). They are committed artifacts only.
  3. Data/wrds/crsp_quotes_topup.csv is CRSP-licensed and gitignored, so scripts/167 (microstructure
     channel) and scripts/170 (intent-scope restriction and equivalence bounds) cannot be reproduced
     from a clean clone without a WRDS login. 167 is not staged; 170 is staged and FAILS loudly.
  4. scripts/173 and scripts/179 are one-time licensed WRDS pulls. Their outputs ARE committed
     (Data/wrds/q6_*.csv, Data/wrds/crsp_daily_topup_dish.csv), so do NOT re-run them.
  5. The Essay 3 validation and audit scripts (196, 197, 198, 200, 201) draw blind samples once and
     are not staged here; their outputs are committed under outputs/essay3_q2/.
  6. Retired chains are kept for provenance, not for citation: see outputs/RETIREMENT_LEDGER.md and
     outputs/STALE_RESULTS_MANIFEST.txt. Files marked TOMBSTONE must not be cited.

CANONICAL RESULTS (AUDIT CLOSED 7/28/2026)
==========================================
See ESSAY_RESULTS_SUMMARY_CORRECTED.md for the authoritative figures.
Summary: Essay 1 H1-H3 bounded nulls (TOST .045/.013/<.001 at +-2.10pp),
H4 inconclusive; Essay 2 H5 bounded null (main +0.12pp p=.914, TOST .044),
quartile pattern = noise. Essay 3: the 7/28-chain H6 figures are RETIRED
(2026-09-11), and the Query 2 chain that replaced them is retired in turn
(2026-09-29); current Essay 3 results are the v4 chain
(outputs/essay3_v4/constants_essay3_v4.json, outputs/essay3_appendix/).
First stage 16.71pp: RETIRED (no computed source; outputs/ESSAY3_QUERY1_REPORT.md C1).
Superseded values are listed in outputs/STALE_RESULTS_MANIFEST.txt.
"""

import sys
import os
import subprocess
from pathlib import Path
import time
from datetime import datetime
import io

# Force UTF-8 encoding for entire script
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set stdout to UTF-8 (for Windows terminal support)
if sys.stdout.encoding.lower() != 'utf-8':
    # Recreate stdout with UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_section(title):
    """Print formatted section header"""
    separator = "\n" + "=" * 80
    print(f"{separator}\n  {title}\n{'=' * 80}\n")

def print_to_both(message, log_file):
    """Print to both console and log file"""
    print(message)
    log_file.write(message + "\n")
    log_file.flush()

# Scripts that legitimately need more than the default 10-minute timeout
LONG_RUNNING_SCRIPTS = {
    'scripts/46_executive_changes_item5_02_with_cache.py': 2400,  # SEC 8-K download, 20-30 min first run
    'scripts/187_essay3_q2_fetch_502_text.py': 3600,  # Item 5.02 text; skips documents already on disk
    'scripts/191_essay3_q2_tmobile_proxy_periodic.py': 2400,  # T-Mobile DEF 14A/10-K/10-Q; skips cached files
    'scripts/202_essay3_q2_estimation.py': 3600,  # wild cluster bootstrap, B = 99,999
    'scripts/163_essay2_rerun_form499.py': 3600,  # Essay 2 ground truth: full DV rebuild + nested models
    'scripts/166_essay2_spec_grid.py': 3600,  # 193-specification measurement grid
    'scripts/181_essay2_spec_curve_permutation.py': 3600,  # permutation null across the 193-spec grid
    'scripts/182_essay2_test_ledger.py': 3600,  # re-executes six Essay 2 scripts via runpy
}

def run_script(script_path, description, log_file, script_args=None):
    """
    Run a Python script and capture output to log.
    Returns True if successful.

    script_args (added 2026-10-01): optional command-line arguments, supplied by a step's
    third tuple element. Defaults to none, so every two-element step is invoked exactly as
    before. This exists because scripts/219 needs --assemble-only to build its covariates
    from the committed Compustat pull instead of attempting a WRDS pull; without it the
    script aborts rather than overwrite committed data, which is what made the clean-clone
    run fail.
    """
    script_args = list(script_args or [])
    shown = script_path + (' ' + ' '.join(script_args) if script_args else '')
    header = f"\nRunning: {description}\nScript: {shown}\n" + "-" * 80
    print_to_both(header, log_file)

    start_time = time.time()

    # Set environment
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    script_timeout = LONG_RUNNING_SCRIPTS.get(script_path.replace('\\', '/'), 600)

    try:
        result = subprocess.run(
            [sys.executable, script_path] + script_args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=script_timeout,
            env=env
        )

        elapsed = time.time() - start_time

        # Write output to log
        if result.stdout:
            log_file.write(result.stdout)
            print(result.stdout)

        if result.stderr:
            log_file.write("\nSTDERR:\n" + result.stderr)
            if result.returncode != 0:
                print(result.stderr)

        # Check result
        if result.returncode == 0:
            status = f"[OK] Completed in {elapsed:.1f} seconds\n"
            print_to_both(status, log_file)
            return True
        else:
            status = f"[ERROR] Script failed (return code {result.returncode}) after {elapsed:.1f} seconds\n"
            print_to_both(status, log_file)
            return False

    except subprocess.TimeoutExpired:
        status = f"[ERROR] Script timeout (>{script_timeout//60} minutes)\n"
        print_to_both(status, log_file)
        return False

    except Exception as e:
        status = f"[ERROR] Exception: {str(e)}\n"
        print_to_both(status, log_file)
        return False

LFS_PLACEHOLDER_MAGIC = "version https://git-lfs"

# Inputs no step can supply for itself. A missing one, or one that is still an LFS
# placeholder, stops the pipeline before step 1 rather than degrading some regression
# 40 minutes in. Each is annotated with what needs it, so the list can be maintained.
REQUIRED_INPUTS = [
    ("Data/processed/rebuild/CANONICAL_V3.csv",
     "the canonical event table; 18 live steps read it, including 156-158 and the v4 chain"),
    ("outputs/rebuild/constants_v3.json",
     "the Essay 1 assertion baseline; 7 live steps read it (156, 158, 163, 199, 202, 210, 247)"),
    ("outputs/essay3_v4/constants_essay3_v4.json",
     "the Essay 3 assertion baseline; scripts/227 asserts every ladder value against it"),
    # RETIRED 2026-10-01 (publish-ready prune): the two pre-rebuild inputs below were
    # required only by steps that the prune retired. FINAL_DISSERTATION_DATASET_FORM499_
    # CORRECTED.csv was read by 122, 86c, 90b, 143 and 144, and executive_changes.csv was
    # merged by 53 - all six are now commented out, so no live step reads either file and
    # the guard no longer enforces them. Both remain committed.
    ("Data/wrds/crsp_daily_returns.csv", "returns for every market-model step"),
    ("Data/wrds/market_indices.csv", "the market index for every market-model step"),
]


# Steps whose declared input is licensed and cannot ship in the repository. When the input
# is absent the step is recorded as SKIPPED - not failed - because a clean clone is EXPECTED
# not to have it. Each entry names the missing file and the document that declares it, and
# both are printed, so a skip can never be mistaken for a silent pass. If the input IS
# present the step runs normally, so a licensed checkout gets the full pipeline.
DECLARED_SKIPS = {
    'scripts/170_essay2_scope_and_bounds.py': (
        'Data/wrds/crsp_quotes_topup.csv',
        'docs/claude/REPRODUCE_ESSAY2.md',
        'intraday quotes for the effective-spread measure; WRDS licence required'),
}


def _declared_skip(script_path):
    """(missing_input, doc, why) if this step must be skipped, else None."""
    ent = DECLARED_SKIPS.get(script_path.replace(chr(92), '/'))
    if ent and not Path(ent[0]).exists():
        return ent
    return None


def _is_lfs_placeholder(path):
    """True if the file on disk is a git-lfs pointer rather than its content.

    A pointer is ~130 bytes of text beginning with the magic line. The size test keeps
    this cheap enough to run over the whole tree.
    """
    try:
        if path.stat().st_size > 1024:
            return False
        with open(path, "rb") as fh:
            return fh.read(len(LFS_PLACEHOLDER_MAGIC)).decode("ascii", "ignore") == LFS_PLACEHOLDER_MAGIC
    except OSError:
        return False


def _live_step_sources():
    """The text of every step declared live in this file, for the reference check."""
    import re
    out = {}
    for line in Path(__file__).read_text(encoding="utf-8", errors="replace").split("\n"):
        if line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*\(\s*'(scripts/[^']+\.py)'\s*,", line)
        if m and Path(m.group(1)).exists():
            out[m.group(1)] = Path(m.group(1)).read_text(encoding="utf-8", errors="replace")
    return out


def verify_data(log_file):
    """Fail loudly on a missing input, or on one that is still a Git LFS placeholder.

    Added 2026-09-29 (Part I1). Until then this function checked a single pre-rebuild
    file for existence. That was the wrong test twice over: it named a dataset the v3
    rebuild had superseded, and existence says nothing about content. 87 committed files
    lost their filter=lfs attribute in 5f5c950, so a clean clone wrote 130-byte
    placeholders in their place with NO error, and every script that read one carried on
    with a column of nonsense. Part I3 restored the attributes; this guard is what makes
    the failure loud if it ever happens again - a placeholder here stops the run instead
    of producing a plausible number.
    """
    print_section("STEP 0: DATA VERIFICATION AND LFS GUARD")
    log_file.write("\n" + "=" * 80 + "\nSTEP 0: DATA VERIFICATION AND LFS GUARD\n" + "=" * 80 + "\n\n")

    missing, placeholder, ok = [], [], []
    for rel, why in REQUIRED_INPUTS:
        path = Path(rel)
        if not path.exists():
            missing.append((rel, why))
        elif _is_lfs_placeholder(path):
            placeholder.append((rel, why))
        else:
            ok.append((rel, path.stat().st_size / (1024 * 1024)))

    msg = "Required inputs\n"
    for rel, mb in ok:
        msg += "  [OK]      %-62s %8.1f MB\n" % (rel, mb)
    for rel, why in missing:
        msg += "  [MISSING] %-62s %s\n" % (rel, why)
    for rel, why in placeholder:
        msg += "  [LFS]     %-62s %s\n" % (rel, why)
    print_to_both(msg, log_file)

    # Every other placeholder in the tree. Not fatal on its own - some belong to retired
    # chains - but fatal if a live step names the file, which is the silent-degradation case.
    others, sources = [], _live_step_sources()
    for base in ("Data", "outputs"):
        root = Path(base)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(r == str(path).replace("\\", "/") for r, _ in REQUIRED_INPUTS):
                continue
            if _is_lfs_placeholder(path):
                others.append(path.as_posix())

    read_by = {}
    for rel in others:
        name = rel.rsplit("/", 1)[-1]
        users = sorted(step for step, text in sources.items() if name in text)
        if users:
            read_by[rel] = users

    if others:
        msg = "\nGit LFS placeholders elsewhere in the tree: %d\n" % len(others)
        for rel in sorted(others)[:20]:
            msg += "  [~] %s%s\n" % (rel, "   <- READ BY A LIVE STEP" if rel in read_by else "")
        if len(others) > 20:
            msg += "  ... and %d more\n" % (len(others) - 20)
        msg += "  These are pointer text, not data. Fix with: git lfs pull\n"
        print_to_both(msg, log_file)

    fatal = missing or placeholder or read_by
    if fatal:
        msg = "\n[FATAL] The pipeline will not start.\n"
        if missing:
            msg += "  %d required input(s) are missing.\n" % len(missing)
        if placeholder:
            msg += "  %d required input(s) are Git LFS placeholders, not data.\n" % len(placeholder)
        if read_by:
            msg += "  %d placeholder file(s) are read by a live step:\n" % len(read_by)
            for rel, users in sorted(read_by.items()):
                msg += "      %s  <- %s\n" % (rel, ", ".join(users))
        msg += ("\n  Run `git lfs pull` and start again. Do NOT run individual scripts to work\n"
                "  around this: a placeholder read as data produces a plausible wrong number\n"
                "  rather than an error.\n")
        print_to_both(msg, log_file)
        return False

    print_to_both("  [OK] %d required inputs present, none a placeholder. Ready to proceed.\n"
                  % len(ok), log_file)
    return True

def verify_outputs(log_file, run_start=None):
    """Verify critical output files exist AND were written by this run.

    run_start: epoch seconds recorded when the pipeline began. A required file whose mtime predates
    it is reported STALE - it exists only because it is committed in the repository, not because this
    run produced it. Until 2026-09-11 this function tested existence alone, so a clean-clone run in
    which six scripts failed (including the Stage 8 assertion) still reported SUCCESS on files that
    had come straight from git. Passing run_start=None restores the old existence-only behaviour.
    """
    print_section("OUTPUT VERIFICATION")
    log_file.write("\n" + "=" * 80 + "\nOUTPUT VERIFICATION\n" + "=" * 80 + "\n\n")

    # Define critical output files
    critical_files = [
        # Form 499 Corrected (PRIMARY)
        Path('outputs/h1_h4_form499_corrected_summary.csv'),
        Path('outputs/h1_h4_form499_corrected_regression_results.txt'),
        Path('outputs/h5_form499_corrected_heterogeneity.csv'),
        Path('outputs/h5_form499_corrected_regression_results.txt'),
        # RETIRED 2026-09-11 (Essay 3 Query 2 Part H): 7/28-chain H6 outputs of script 91m
        # Path('outputs/h6_form499_corrected_power_analysis.csv'),
        # Path('outputs/h6_form499_corrected_regression_results.txt'),
        # Essay 3 — Query 2 chain (CURRENT)
        Path('outputs/essay3_q2/c2_outcomes_events.csv'),
        Path('outputs/essay3_q2/e_analysis_sample.csv'),
        Path('outputs/essay3_q2/f1_ladder.csv'),
        Path('outputs/essay3_q2/constants_essay3_q2.json'),
        Path('outputs/essay3_q2/tmobile_timeline.csv'),
        Path('outputs/essay3_q2/f1_se_diagnostics.csv'),
        # Essay 1 — canonical v3 chain (CURRENT)
        Path('outputs/rebuild/constants_v3.json'),
        Path('outputs/rebuild/appendix_v3/table_1.csv'),
        # Essay 2 — canonical chain, scripts 163-182 (CURRENT)
        Path('outputs/tables/essay2_v2/t51_elevation_calibration.csv'),
        Path('outputs/tables/essay2_v2/t52_spec_curve_permutation.csv'),
        Path('outputs/tables/essay2_v2/t53_test_ledger.csv'),
        # COMMITTED BUT NOT REGENERATED, so deliberately not required here:
        #   outputs/tables/essay2_appendix/*.csv (no committed generator) and ESSAY2_APPENDIX.docx (gitignored).
        # LEGACY / REFERENCE (SIC-based and 7/28-era chains; retained for the old-vs-new exhibit, NOT current results)
        Path('outputs/tables/TABLE1_COMBINED.txt'),
        Path('outputs/tables/essay2/TABLE2_baseline_disclosure.txt'),
        Path('outputs/tables/essay2/TABLE3_fcc_regulation.txt'),
        Path('outputs/tables/essay2/TABLE4_prior_breaches.txt'),
        Path('outputs/tables/essay2/TABLE5_breach_severity.txt'),
        Path('outputs/H1_timing_fcc_interaction_results.csv'),
        Path('outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt'),
        Path('outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt'),
        Path('outputs/tables/essay2/H1_TOST_Equivalence_Test.txt'),
        Path('outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt'),
        # RETIRED 2026-09-11 (Essay 3 Query 2 Part H): legacy essay3_governance outputs (7/28 and
        # SIC-era chains; scripts 91, 91b, 91c, 91e, 91f, 91g, 91h, 91j, 91k) — see outputs/RETIREMENT_LEDGER.md
        Path('outputs/tables/essay3/TABLE2_volatility_changes.txt'),
        Path('outputs/tables/essay3/TABLE3_information_asymmetry.txt'),
        Path('outputs/economic_significance/economic_impact_summary.csv'),
        Path('outputs/economic_significance/economic_significance_report.txt'),
        Path('outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv'),
        # RETIRED 8/4/2026: Path('outputs/tables/TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv'),
        Path('outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv'),
        # RETIRED 2026-09-11: Path('outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv'),  (script 102)
        Path('outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv'),
    ]

    present_files = []
    missing_files = []
    stale_files = []

    for filepath in critical_files:
        if not filepath.exists():
            missing_files.append(str(filepath))
        elif run_start is not None and filepath.stat().st_mtime < run_start:
            stale_files.append(str(filepath))
        else:
            present_files.append(str(filepath))

    # Report results
    msg = f"\nCritical Output Files:\n"
    msg += f"  Written by this run: {len(present_files)}/{len(critical_files)}\n"
    msg += f"  Stale (pre-existing, NOT written by this run): {len(stale_files)}/{len(critical_files)}\n"
    msg += f"  Missing: {len(missing_files)}/{len(critical_files)}\n"

    if present_files:
        msg += f"\n[OK] Files found:\n"
        for f in sorted(present_files):
            msg += f"  [+] {f}\n"

    if missing_files:
        msg += f"\n[!] Files missing:\n"
        for f in sorted(missing_files):
            msg += f"  [-] {f}\n"
        msg += f"\nNote: Some expected files may not be present if certain scripts were skipped.\n"

    if stale_files:
        msg += f"\n[!] Files NOT written by this run (they exist only because they are committed):\n"
        for f in sorted(stale_files):
            msg += f"  [~] {f}\n"
        msg += ("\nA stale file means the script that produces it failed or did not run. Do NOT read these\n"
                "as results of this run - check the [FAILED] list above.\n")

    print_to_both(msg, log_file)

    return len(missing_files) == 0 and len(stale_files) == 0

def run_all():
    """Execute complete dissertation analytics pipeline"""
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path('outputs/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f'analysis_log_{timestamp}.txt'
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        
        # Header
        header = f"""
{'=' * 80}
  DISSERTATION ANALYTICS PIPELINE
  Data Breach Disclosure Timing and Market Reactions
  Timothy D. Spivey - University of South Alabama
  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

Log file: {log_path}
"""
        print_to_both(header, log_file)
        
        start_time = time.time()
        
        # Define pipeline
        pipeline = [
            {
                'category': 'DATA PREPARATION - OUTCOME EXTRACTION',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET and
                    # feeds nothing cited. Its committed output Data/enrichment/executive_changes.csv
                    # (779 rows, executive_change_180d sum 521) stays on disk, so scripts/53 still runs
                    # without it - the check the ledger left open is now closed.
                    # ('scripts/46_executive_changes_item5_02_with_cache.py', 'Essay 3 Outcome: Executive Turnover from 8-K Item 5.02 (cached; 20-30 min on first run, 2-5 min after) [MUST RUN BEFORE SCRIPT 53]'),
                ]
            },
            {
                'category': 'DATA PREPARATION - ENRICHMENTS',
                'scripts': [
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild enrichment merge
                    # ('scripts/53_merge_CONFIRMED_enrichments.py', 'Merge All Enrichments (Prior breaches, breach severity, media coverage, Item 5.02 executive turnover, enforcement) → FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/99_add_cpni_hhi_variables.py', 'Add CPNI & HHI Variables (Essay 1 Alternative Explanations)'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild governance merge + heterogeneity table
                    # ('scripts/98_sox404_heterogeneity.py', 'Governance Enrichment: SOX 404 proxy → FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv (required by 121c)'),
                ]
            },
            {
                'category': 'REBUILD DIRECTIVE V2 — CANONICAL V3 CHAIN (8/4/2026; supersedes the pre-audit base)',
                'scripts': [
                    ('scripts/150_rebuild_s2_entity_resolution.py', 'Stages 1-2: universe assertion + fresh exact-and-abstain entity resolution (placeholder reasoning-pass excluded; CORP/INCORPORATED normalizer fix) → Gate 1 ledger'),
                    ('scripts/151_rebuild_gate1_apply.py', 'Gate 1 signed verdicts (52 rules; ticker-file authoritative; Sprint-era=101830 SEC-verified) → stage2_signed'),
                    ('scripts/152_rebuild_s3_dedup.py', 'Stage 3: CIK+date always-collapse (758→524) + adjacency chains → Gate 2 sheet'),
                    ('scripts/153_rebuild_gate2_apply.py', 'Gate 2 signed verdicts (31 chains collapsed; Fox→News Corp; TALX→EFX) → 489 events'),
                    ('scripts/154_rebuild_s4_treatment.py', 'Stage 4: Form 499 from committed snapshot (clause-b adjudicated never mechanized; family rules for "-CONSOLIDATED" suffix; equity-parent maps) → 116 treated'),
                    ('scripts/159_wrds_coverage_topup.py', 'WRDS coverage top-up (pre-specified amendment; IDEMPOTENT — skips when the three *_topup.csv artifacts exist; needs WRDS pgpass only on re-pull) → Sprint/CenturyLink daily returns + fundamentals'),
                    ('scripts/155_rebuild_s5_outcomes.py', 'Stage 5: all market outcomes, recovered script-20 conventions; PERMNO date-aware with share-class volume rule'),
                    ('scripts/156_rebuild_s6_assembly.py', 'Stage 6: keyed covariates (NO positional joins); Item 5.02 from live EDGAR (cached) → CANONICAL_V3.csv'),
                    ('scripts/157_rebuild_s7_verification.py', 'Stage 7: disclosure-date armor, OCR health check (bounded), CRSP-attrition balance'),
                    ('scripts/158_rebuild_s8_regenerate.py', 'Stage 8: all three essays + ROA amendment + appendix v3 + CONSTANTS BLOCK V3 (assertion baseline)'),
                    ('scripts/160_appendix_v3_to_word.py', 'Essay 1 appendix v3 -> Word: renders the 16 tables 158 writes (must follow 158)'),
                    ('scripts/247_essay1_ledger_attrition_v3.py', 'Essay 1 attrition ledger, computed live from the v3 chain (10 assertions). EXITS NONZERO while constants_v3.json is stale against CANONICAL_V3 - that failure is the pending rebaseline, and the ledger is written either way'),
                ]
            },
            {
                'category': 'ESSAY 3 — QUERY 2 CHAIN (RETIRED 2026-09-29; superseded by the v4 chain below. Kept staged because its outputs are the v3 side of the 239 side-by-side; its constants file is NOT authoritative)',
                'scripts': [
                    ('scripts/187_essay3_q2_fetch_502_text.py', 'Essay 3 B: Item 5.02 filing text for the scope events (cached; asserts the fixed validation/dev draws reproduce)'),
                    ('scripts/195_essay3_q2_classifier_v2.py', 'Essay 3 C: FINAL classifier v2 (6f7be7a) -> c2_* codes, one-departure-per-person events, outcomes'),
                    ('scripts/199_essay3_q2_sample_e.py', 'Essay 3 E: outcome-data requirement, CIK fixes, prior-return control, ledger (asserts its outcome helper reproduces v2 for every T-Mobile event)'),
                    ('scripts/202_essay3_q2_estimation.py', 'Essay 3 F/I: H6 inference ladder, placebo, sensitivities, tests (asserts against outputs/essay3_q2/constants_essay3_q2.json)'),
                    ('scripts/190_essay3_q2_tmobile_sprint_case.py', 'Essay 3 G1/G2/G5: T-Mobile and Sprint data collection (cached)'),
                    ('scripts/191_essay3_q2_tmobile_proxy_periodic.py', 'Essay 3 G3/G4: T-Mobile DEF 14A / 10-K / 10-Q passages (cached)'),
                    ('scripts/203_essay3_q2_tmobile_case_timeline.py', 'Essay 3 G6: T-Mobile case table on the notification anchor + dated timeline'),
                    ('scripts/204_essay3_q2_se_diagnostics.py', 'Essay 3 F1 diagnostics: SE at each inference rung, CV3 jackknife variance shares, leave-one-cluster-out ranges, base rates (asserts against f1_ladder.csv)'),
                    # NOT STAGED - one-off blind validation draws; outputs committed under outputs/essay3_q2/:
                    #   196 (round-2 sheet), 197 (round-2 scoring), 198 (differential recall),
                    #   200 (recall-audit sheet), 201 (recall-audit scoring).
                    # scripts/195 is FROZEN (commit 6f7be7a). Do not edit it: any revision invalidates the
                    # blind validation and requires a fresh round.
                ]
            },
            {
                'category': 'ESSAY 3 — v4 CHAIN (AUTHORITATIVE, 2026-09-29 ruling; point-in-time CRSP relink; '
                            'constants in outputs/essay3_v4/constants_essay3_v4.json)',
                'scripts': [
                    # Order is REPRODUCE_ESSAY3_V4.md's, which diverges from numeric order in two
                    # places: 232 must precede 224 (224's ledger reads the censoring result) and
                    # 233 must precede 224 (224 aborts unless every reconciliation row says agree).
                    # 212 runs TWICE, by design - see commit 218d3d9, which introduced the
                    # --canonical and --out-prefix arguments for exactly this.
                    #
                    # PASS 1 reads CANONICAL_V3 and writes the UNPREFIXED 212_*.csv, including
                    # stage3_candidates.csv - the worklist scripts/213 verifies and the evidence
                    # the re-parenting in 214 is built on. It must therefore run BEFORE 214.
                    ('scripts/212_pit_linker_v4.py', 'v4 Stage 2 PASS 1 of 2: point-in-time CIK->gvkey->CUSIP->permno linker on CANONICAL_V3; writes the unprefixed 212_* files and the Stage 3 worklist 213 verifies'),
                    ('scripts/214_corrections_v4.py', 'v4 correction ledger -> CANONICAL_V4 (Sprint anchor, Carnival, CIK re-parenting, Gate-2 notification anchor, health indicator)'),
                    # PASS 2 reads CANONICAL_V4, whose final_cik is the RE-PARENTED registrant,
                    # and writes the v4_-prefixed files. 13 live steps read v4_212_links.csv -
                    # among them 227, which writes constants_essay3_v4.json - so without this
                    # pass the v4 linkage is never derived and that file is only ever a committed
                    # artefact. 214's own rule says why the order is this way: a subsidiary's CIK
                    # has no Compustat gvkey, so re-parenting points the event at the registrant
                    # 'so the second linker pass can find it'. The v4_ prefix keeps pass 2 from
                    # overwriting stage3_candidates.csv, which is 213's evidence base.
                    ('scripts/212_pit_linker_v4.py', 'v4 Stage 2 PASS 2 of 2: re-link on CANONICAL_V4 (re-parented CIKs) -> v4_212_* files, the linkage 13 live steps read', ['--canonical', 'Data/processed/rebuild_v4/CANONICAL_V4.csv', '--out-prefix', 'v4_']),
                    ('scripts/215_ledger_v4.py', 'v4 linkage ledger and symmetry report'),
                    # --assemble-only is REQUIRED (REPRODUCE_ESSAY3_V4.md:30). Without it
                    # 219 attempts the WRDS pull and aborts at 219:181 rather than
                    # overwrite Data/wrds_v4/comp_funda.csv, which is committed.
                    ('scripts/219_wrds_funda_v4.py', 'v4 covariates from the committed Compustat pull (gvkey-joined; 550-day staleness rule verbatim from 156)', ['--assemble-only']),
                    ('scripts/234_outcome_cik_v4.py', 'v4 outcome filer resolved by rule (the CIK whose Form 8-K filings are read)'),
                    ('scripts/233_resolve_reconciliation.py', 'PREREQUISITE of 224: reconciles outcome_cik against the v3 patch list; every row must say agree'),
                    ('scripts/230_outcome_gap_v4.py', 'v4 outcome-CIK gap and the fetch window per event'),
                    ('scripts/235_fetch_completeness_v4.py', 'v4 fetch completeness; also writes the b_* scope files 220 and 224 read'),
                    ('scripts/237_validation_draw_v4.py', 'v4 out-of-sample validation draw (pool = documents v4 added, against the v3-frozen tree; seed 20260919)'),
                    ('scripts/220_essay3_v4_classifier_v2.py', 'v4 classifier: byte-identical METHOD to scripts/195; only the data sources move. Slow (~1,500 filings)'),
                    ('scripts/238_score_new_documents_v4.py', 'v4 new-document accuracy against the blind reference codes'),
                    ('scripts/232_censoring_report_v4.py', 'MUST PRECEDE 224: censoring report on the outcome filer last filing'),
                    ('scripts/224_essay3_v4_sample_e.py', 'v4 sample E: censoring rule, 8-K activity, 150-return rule, ledger (asserts its ledger closes)'),
                    ('scripts/227_essay3_v4_estimation.py', 'v4 F/I: H6 ladder, placebo, 27 sensitivities, BH (ASSERTS against outputs/essay3_v4/constants_essay3_v4.json). Slow (B = 99,999)'),
                    ('scripts/229_essay3_v4_se_diagnostics.py', 'v4 SE diagnostics (ASSERTS its recomputed HC3/CV1/CV3 equal f1_ladder.csv at all three windows)'),
                    ('scripts/228_essay3_v4_tmobile_case_timeline.py', 'v4 T-Mobile case timeline'),
                    ('scripts/239_v3_vs_v4_sidebyside.py', 'v3-overlap sensitivity and the v3-vs-v4 constants side-by-side'),
                    ('scripts/242_essay3_q3_results_pull.py', 'Results-section pull (ASSERTS t and p reproduce f1_ladder.csv within its stored precision)'),
                    ('scripts/243_essay3_q4_readouts.py', 'Control coefficients and logit diagnostics (ASSERTS both reproduce f1_ladder.csv and f1_logit_ame.csv)'),
                    ('scripts/244_essay3_q4_tables.py', 'The eleven table CSVs (24 assertions: ledger closure, subgroup sums, 27 sensitivity rows, 26 T-Mobile events)'),
                    ('scripts/246_essay3_descriptive_counts.py', 'Descriptive counts the appendix cites (ASSERTS all 14 against the Results figures)'),
                    ('scripts/245_essay3_appendix.py', 'Renders the appendix, .md and .docx (36 assertions incl. label, title, note-text and case integrity)'),
                    ('scripts/217_v4_offline_tests.py', 'v4 offline test suite; must be all-pass'),
                    ('scripts/210_verify_v3_frozen.py', 'v3 freeze gate; must be PASS. Run it AFTER staging, or it cannot see newly added files'),
                    # NOT STAGED, and deliberately so:
                    #   211, 216 (WRDS pulls: subscription), 213, 231 (SEC fetches: network + declared
                    #   User-Agent). Their outputs are committed and are treated as inputs.
                    #   221, 222, 223, 225, 226 (one-off blind validation and audit draws; outputs
                    #   committed under outputs/essay3_v4/).
                    #   236 (loader) and 218 (common) are imported, not run.
                    #   241 was a targeted re-estimation under freeze exception 1; 227 supersedes it.
                    # scripts/220 is FROZEN and byte-identical in METHOD to scripts/195.
                ]
            },
            {
                'category': 'ESSAY 2 — CANONICAL CHAIN (volatility / information asymmetry; CURRENT, scripts 163-182)',
                'scripts': [
                    ('scripts/163_essay2_rerun_form499.py', 'Essay 2 ground truth on CANONICAL_V3: DV (e2_vol_change), sample ledger, nested models, diagnostics -> outputs/tables/essay2_v2/'),
                    ('scripts/164_essay2_rule_delay_classification.py', 'Rule text (47 CFR 64.2011), disclosure-delay tests, classification audits, census'),
                    ('scripts/165_essay2_inference_ladder.py', 'Inference ladder on parent CIK: CV1/CV3, wild cluster bootstrap, G/G1/G* diagnostics'),
                    ('scripts/166_essay2_spec_grid.py', 'Measurement grid (193 specifications) + gradient decomposition'),
                    ('scripts/169_essay2_spec_repairs.py', 'Abnormal-volatility DV, leakage tests, calendar clustering, balance'),
                    ('scripts/170_essay2_scope_and_bounds.py', 'Intent-scope restriction (64.2011(e)) and equivalence bounds — REQUIRES the licensed Data/wrds/crsp_quotes_topup.csv (same file as 167); FAILS in a clean clone without a WRDS login'),
                    ('scripts/171_essay2_figures.py', 'Specification-curve and power-curve figures'),
                    ('scripts/175_essay2_announcement_contrast.py', 'Announcement-window contrast — the rescoped primary Essay 2 result'),
                    ('scripts/176_q7_composition_check.py', 'Composition check on the announcement-window differential'),
                    ('scripts/177_q7_damping_anatomy.py', 'Descriptive anatomy of the control-side damping'),
                    ('scripts/180_essay2_elevation_calibration.py', 'Elevation calibration: c4(n) bias correction, placebo dates, earnings benchmark'),
                    ('scripts/181_essay2_spec_curve_permutation.py', 'Permutation null for the specification curve (treatment permuted at parent-entity level)'),
                    ('scripts/174_q6_closeout.py', 'Query 6 closeout: T-Mobile focal case, carrier denominator, Sprint seam, earnings control (parts needing the uncommitted quotes top-up skip loudly)'),
                    ('scripts/182_essay2_test_ledger.py', 'Program-wide test ledger -> outputs/tables/essay2_v2/t53_test_ledger.csv (re-executes 164/169/170/174/175/176 via runpy to collect their N_TESTS ledgers)'),
                    # scripts/172_essay2_run_all.py is a standalone Essay 2 runner covering 163-171 only; it
                    # predates 174-182. It is not staged here to avoid running those scripts twice.
                    # NOT STAGED - licensed WRDS pulls whose outputs are already committed; do NOT re-run:
                    #   scripts/173_q6_wrds_pull.py    -> Data/wrds/q6_{gics,gics_hist,rdq,stocknames}.csv
                    #   scripts/179_dish_crsp_topup.py -> Data/wrds/crsp_daily_topup_dish.csv
                    # BLOCKED - scripts/167_essay2_microstructure.py needs Data/wrds/crsp_quotes_topup.csv
                    #   (CRSP-licensed, gitignored). The microstructure channel cannot be reproduced from a
                    #   clean clone without a WRDS login.
                    # NOT REGENERABLE - outputs/tables/essay2_appendix/*.csv has no committed generator;
                    #   scripts/178 only renders those CSVs into ESSAY2_APPENDIX.docx.
                ]
            },
            {
                'category': 'DATA PREPARATION - FORM 499 CLASSIFICATION',
                'scripts': [
                    # --assemble-only is REQUIRED from a clean clone: the live FCC endpoint
                    # returns HTTP 403, so the step parses the committed registry snapshot
                    # Data/edgar/form499_registry.xml instead (docs/claude/REPRODUCE_ESSAY2.md).
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Form 499 entity matching
                    # ('scripts/121a_form499_entity_matching.py', 'Form 499 Entity Matching: Exact-string match (normalized) PRC firms to FCC registry (107/779 matched)', ['--assemble-only']),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Form 499 coverage validation
                    # ('scripts/121b_form499_coverage_validation.py', 'Form 499 Coverage Validation: Validate matches against start/end dates (88 date-valid)'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Form 499 classification merge
                    # ('scripts/121c_merge_form499_classification.py', 'Merge Form 499 Classification: Add fcc_form499 binary to dataset (79 treated in regression sample)'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Form 499 manual corrections
                    # ('scripts/122_manual_form499_corrections.py', 'Manual Form 499 Corrections: Apply two-clause rule to SIC-flagged firms (add +36 treated via parent-brand rule) → FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv'),
                ]
            },
            {
                'category': 'FORM 499 CORRECTED ANALYSES [LEGACY — superseded 8/4/2026 by the CANONICAL V3 chain above; retained to regenerate the old base for the old-vs-new data-quality comparison exhibit]',
                'scripts': [
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Essay 1 H1-H4 regressions
                    # ('scripts/86c_essay1_h1_h4_form499_corrected.py', 'H1-H4 Re-estimation with Form 499 Corrected Classification (n=115 treated, authoritative regulatory status)'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Essay 2 H5 heterogeneity
                    # ('scripts/90b_essay2_h5_form499_corrected.py', 'H5 Volatility Re-estimation with Form 499 Corrected (First real result, post-deduplication)'),
                    # RETIRED 2026-09-11 (Essay 3 Query 2 Part H): 7/28-chain H6 on the any-5.02 outcome; superseded by the Query 2 chain
                    # ('scripts/91m_essay3_h6_form499_corrected.py', 'H6 Executive Turnover Re-estimation with Form 499 Corrected (First real result, MDE/TOST)'),
                    # RETIRED 2026-08-30 (Query 5 Part F): 7/28-vintage chain superseded by appendix_v3 (scripts/158/160).
                    # The script itself was DELETED in 0e75740; the entry below is provenance only. The current
                    # Essay 1 appendix is outputs/rebuild/appendix_v3/ (scripts/158, Word build scripts/160).
                    # RETIRED 2026-08-30 (Query 5 Part F): 7/28-vintage chain; v3 ledger lives in CANONICAL_V3_LINEAGE.md + ESSAY2 ledgers.
                    # The script itself was DELETED in 0e75740; the entry below is provenance only. Do not revive it:
                    # outputs/SAMPLE_ATTRITION_LEDGER.md is now a TOMBSTONE and regenerating it would overwrite that.
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Essay 1 results supplements
                    # ('scripts/143_essay1_results_supplements.py', 'Essay 1 Results Supplements (timing x FCC interaction, 5-day CAR, TOST min bounds, overlap share, 60/90d horizons under uniform convention; CONTAINS car_30d provenance finding - stored column inherits pre-audit computation) → outputs/ESSAY1_RESULTS_SUPPLEMENTS.md'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild residual duplicate audit
                    # ('scripts/144_residual_duplicate_audit.py', 'Residual-Duplicate Audit (name-variant twins defeating exact-key dedup: 26 groups/30 excess rows → 754-event candidate set; ±3-day adjacency candidates reported not collapsed; NOTHING canonical overwritten) → outputs/RESIDUAL_DUPLICATE_AUDIT.md + FINAL_DATASET_DEDUP_V2_CANDIDATE.csv'),
                ]
            },
            {
                'category': 'MAIN ANALYSIS (REFERENCE)',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/70_summary_statistics.py', 'Summary Statistics (Table 1)'),
                    # RETIRED 2026-10-01 (publish-ready prune): pre-rebuild Essay 1 CAR regressions
                    # ('scripts/80_essay1_car_regressions.py', 'Essay 1 Main Regressions (H1-H4: CAR on disclosure/FCC/reputation/severity) - HC3 robust SEs as primary [REFERENCE - SIC-BASED]'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/h1_timing_fcc_interaction.py', 'H1 Theoretical Test: Timing × FCC Interaction (formal test of differential effects by regulatory status, canonical specification)'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/81_post_2007_interaction_test.py', 'FCC Causal Identification (TABLE B8: Post-2007 Interaction Test - Market Returns)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/82_clustered_vs_hc3_comparison.py', 'Standard Errors Robustness (TABLE B9: Clustered vs HC3 Comparison)'),
                    # RETIRED 2026-08-30 (Query 5 Part G): Rule-37.3/DiD-era content; no causal-identification claim survives zero treated pre-rule observations
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/90_essay2_volatility_regressions.py', 'Essay 2 Volatility Analysis (FCC effect on post-breach volatility, Tables 2-3) [COMPLETE]'),
                    # ARCHIVED: Pre-2007 causal ID replaced by SCM. Runs as robustness check only.
                    # ('scripts/84_essay2_post_2007_interaction_test_volatility.py', 'Essay 2 Volatility Causal ID (TABLE B8: Post-2007 Test)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/86_essay3_fcc_causal_identification.py', 'Essay 2 Volatility Causal ID (Industry FE, Size Sensitivity)'),
                    # RETIRED 2026-09-11 (Essay 3 Query 2 Part H): legacy Essay 3 scripts on the SIC treatment and the
                    # any-Item-5.02 outcome (91, 91b, 91c, 91e, 91f, 91g, 91k, 91j) and the 7/28 Cox (91h); superseded by the
                    # Query 2 chain. The TOST description "confirms FCC effect is economically negligible" is withdrawn.
                    # See outputs/RETIREMENT_LEDGER.md.
                ]
            },
            {
                'category': 'CAUSAL IDENTIFICATION: SYNTHETIC CONTROL METHOD',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/scm_mahalanobis_distance.py', 'Essay 1 H2 Causal Identification: Mahalanobis Distance Weighted SCM (Abadie et al. 2010) - breach-event level matching with 500 permutations'),
                ]
            },
            {
                'category': 'NATURAL EXPERIMENT VALIDATION (ARCHIVED: Pre-2007 tests replaced by SCM)',
                'scripts': [
                    # ARCHIVED: Parallel trends and balance test used pre-2007/post-2007 comparison.
                    # Causal ID now uses Synthetic Control Matching. These run as archived checks only.
                ]
            },
            {
                'category': 'PUBLICATION READINESS: DATA INTEGRITY & CAUSAL ROBUSTNESS',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/00_data_validation_checks.py', 'Data Validation Checks (logical consistency, duplicates, outliers, missing data)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/99_firm_fixed_effects_analysis.py', 'Firm Fixed Effects (H1-H4 within-firm variation, controls unobserved heterogeneity)'),
                    # RETIRED 8/4/2026 (Rebuild Directive v2, data decision 3): enforcement columns are
                    # pre-audit provenance; enforcement enters as prose citation-armor only.
                    # ('scripts/92_enforcement_analysis.py', 'H6 Enforcement Analysis (regulatory enforcement prevalence and predictors)'),
                ]
            },
            {
                'category': 'MACHINE LEARNING',
                'scripts': [
                    # RETIRED 2026-10-01 (publish-ready prune): ML feature-importance models and figures
                    # ('scripts/60_train_ml_model.py', 'Train ML Model'),
                    # RETIRED 2026-10-01 (publish-ready prune): ML validation figures and robustness text
                    # ('scripts/61_ml_validation.py', 'ML Validation & Robustness Text'),
                ]
            },
            {
                'category': 'ECONOMIC SIGNIFICANCE & COMPREHENSIVE HETEROGENEITY ANALYSIS',
                'scripts': [
                    # RETIRED 2026-10-01 (publish-ready prune): economic-significance figures
                    # ('scripts/96_economic_significance.py', 'Economic Significance Analysis: FCC costs, volatility impact, governance disruption in dollar terms'),
                    # RETIRED 2026-10-01 (publish-ready prune): heterogeneous-mechanism figures
                    # ('scripts/97_heterogeneous_mechanisms.py', 'Heterogeneous Mechanisms: Effects vary by firm size, breach type, prior history'),
                    # J1 2026-09-29: DUPLICATE declaration removed (the step is already staged
                    # earlier in the DATA PREPARATION category, where 121c needs it). It was
                    # running twice per pipeline.
                    # ('scripts/98_sox404_heterogeneity.py', 'HETEROGENEITY PHASE 1: Governance Quality (SOX 404 proxy) - FCC x Governance interaction'),
                    # RETIRED 8/4/2026 (Rebuild Directive v2, data decision 1): NVD/CVSS variables are
                    # vendor-level threat-environment measures, not breach severity; belong to no hypothesis.
                    # ('scripts/99_cvss_complexity_heterogeneity.py', 'HETEROGENEITY PHASE 2: CVSS Technical Complexity - FCC x Complexity interaction [RETIRED - SIC-era +6.27% claim stale-manifested]'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/100_ransomware_heterogeneity.py', 'HETEROGENEITY ANALYSIS #3: Ransomware Attack Vector - FCC x Ransomware interaction'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/101_media_coverage_heterogeneity.py', 'HETEROGENEITY ANALYSIS #4: Media Coverage Moderation - FCC x Media interaction (+7.08%**)'),
                    # RETIRED 2026-09-11 (Essay 3 Query 2 Part H): script 102 is entirely Essay 3 (any-5.02 outcome, SIC treatment)
                    # ('scripts/102_extended_governance_windows.py', 'HETEROGENEITY ANALYSIS #5: Extended Governance Time Windows - 30d/90d/180d comparison'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/103_breach_type_diversity.py', 'HETEROGENEITY ANALYSIS #6: Breach Type Diversity - Multi-type complexity'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/104_restatement_summary.py', 'HETEROGENEITY ANALYSIS #7: Restatement Prediction - Data limitation documentation'),
                    # RETIRED 8/4/2026 (Rebuild Directive v2, data decision 1): CVE-based complexity index retired with NVD.
                    # ('scripts/105_complexity_index_heterogeneity.py', 'HETEROGENEITY ANALYSIS #8: Complexity Index - Unified severity/CVE/type complexity mechanism'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/106_information_environment_composite.py', 'HETEROGENEITY ANALYSIS #9: Information Environment Composite - Media attention & reputation interaction (Spec A/B/C)'),
                ]
            },
            {
                'category': 'ROBUSTNESS CHECKS',
                'scripts': [
                    # RETIRED 2026-09-11 (Essay 3 Query 2 Part H; decision L3: no mediation analysis)
                    # ('scripts/91_essay3_mediation_analysis.py', 'Mediation Analysis (Essay 3): Does volatility mediate timing→turnover relationship?'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/92_heterogeneity_analysis.py', 'Heterogeneity Analysis: CAR/volatility effects vary by firm size quartiles?'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/93_market_model_sensitivity.py', 'Event Window Sensitivity: Robustness across 5d, 10d, 30d, 60d, 90d CARs'),
                    # RETIRED 2026-08-30 (Query 5 Part G): Rule-37.3-era content
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/95_low_r2_sensitivity.py', 'Low R² Sensitivity: Model adequacy with alternative specifications'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/robustness_1_alternative_windows.py', 'Alternative Event Windows: CAR across multiple breach-to-event intervals'),
                    # RETIRED 2026-10-01 (publish-ready prune): robustness figure set R02
                    # ('scripts/robustness_2_timing_thresholds.py', 'Timing Thresholds: Disclosure timing effects (1d, 3d, 7d, 14d, 30d)'),
                    # RETIRED 2026-10-01 (publish-ready prune): robustness figure set R03
                    # ('scripts/robustness_3_sample_restrictions.py', 'Sample Restrictions: Results stratified by FCC, data type, firm size'),
                    # RETIRED 2026-10-01 (publish-ready prune): robustness figure set R04
                    # ('scripts/robustness_4_standard_errors.py', 'Standard Errors: HC3, Clustered, Bootstrap comparison'),
                    # RETIRED 2026-10-01 (publish-ready prune): robustness figure set R05
                    # ('scripts/robustness_5_fixed_effects.py', 'Fixed Effects: Industry 2-digit, 4-digit SIC, Year, and Firm FE'),
                    # RETIRED 2026-09-29 (Part H): reads no data at all - it hardcodes the pre-rebuild
                    # n = 653 (line 19) and computes an MDE from it. Feeds nothing; output untracked.
                    # ('scripts/power_analysis_h3_h4.py', 'Power Sensitivity Analysis: H3/H4 null hypothesis assessment (MDE at 80% power)'),
                ]
            },
            {
                'category': 'LONG-HORIZON ANALYSIS & MITCHELL-STAFFORD ROBUSTNESS',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/overlap_audit_fcc_clustering.py', 'Overlap Audit: Quantify event clustering in FCC sample (72.7% overlap at 90d) - diagnose Mitchell-Stafford problem severity'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/corrected_longrun_car_clustering.py', 'Corrected Long-Horizon CAR: Compute CAR at 60d/90d (not BHAR), test with calendar-month clustering and non-overlapping sample'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/calendar_month_clustering_60_90.py', 'Calendar-Month Clustering Test: Check whether 60d/90d results survive clustering correction for overlapping events'),
                ]
            },
            {
                'category': 'FACTOR MODEL & PERSISTENCE TESTING',
                'scripts': [
                    # RETIRED 2026-09-29 (Part H): builds Data/wrds/fama_french_factors.csv, which stays
                    # committed. Every script that reads that file is itself retired here, so no live
                    # step consumes it.
                    # ('scripts/extract_merge_fama_french.py', 'Extract and Merge Fama-French Factors: Process Ken French data files (FF3, Momentum, FF5) locally with proper header handling'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/sample_composition_diagnostic.py', 'Sample Composition Diagnostic: Isolate model choice effects from sample loss (critical: market-adjusted remains p=0.058 on restricted N=519 sample)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/ff3_simple_merge.py', 'FF3 Simple Merge Robustness: Test H1-H4 under FF3 specification (N=519, coefficient stable -2.12%, p-value inflation from factor adjustment, not sample loss)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/factor_model_carhart_ff5.py', 'Factor Model Robustness: Test H1-H4 under market model, Carhart 4-factor, FF5 (coefficient stable across all specifications)'),
                    # RETIRED 2026-09-29 (Part H): reads the pre-rebuild FINAL_DISSERTATION_DATASET*
                    # and feeds no constants key, appendix table, ledger or cited figure.
                    # ('scripts/extended_bhar_60d_90d.py', 'Extended BHAR Windows: Compute 60-day and 90-day BHAR from daily returns, test persistence vs mean reversion (Mitchell-Stafford test)'),
                ]
            },
            {
                'category': 'DEFENSE PREPARATION',
                'scripts': [
                    # RETIRED 2026-10-01 (publish-ready prune): defense-prep text
                    # ('scripts/defense_prep_all_tasks.py', 'Pre-Defense Preparation: Five critical tasks - FCC economic significance, deduplication summary, H2 stability, power analysis, SCM vs OLS comparison'),
                ]
            }
        ]
        
        # Track results
        results = {}
        
        # Step 0: Verify data
        if not verify_data(log_file):
            msg = "\n[FATAL] Cannot proceed without data file\n"
            print_to_both(msg, log_file)
            return False

        # Run all scripts
        for section in pipeline:
            category = section['category']
            scripts = section['scripts']
            
            # Category header
            cat_header = f"\n{'=' * 80}\n{category}\n{'=' * 80}\n"
            print_to_both(cat_header, log_file)
            
            for step in scripts:
                # A step is (path, description) or, since 2026-10-01, an optional third
                # element: a list of command-line arguments. Two-element steps are
                # unaffected - they resolve to an empty argument list and the invocation
                # is byte-identical to before.
                script_path, description = step[0], step[1]
                script_args = list(step[2]) if len(step) > 2 else []

                # Check if script exists
                if not Path(script_path).exists():
                    msg = f"\n[SKIP] Script not found: {script_path}\n"
                    print_to_both(msg, log_file)
                    results[description] = False
                    continue

                # A declared skip: the licensed input is absent, which is the expected
                # state of a clean clone. Recorded as SKIPPED, not as a failure.
                skip = _declared_skip(script_path)
                if skip:
                    missing_input, doc, why = skip
                    msg = (f"\n[SKIPPED] {script_path}\n"
                           f"  declared exception: {missing_input} is not present\n"
                           f"  reason            : {why}\n"
                           f"  declared in       : {doc}\n"
                           f"  This is NOT a failure. Supply the licensed input to run it.\n")
                    print_to_both(msg, log_file)
                    results[description] = 'SKIPPED'
                    continue

                # Run script
                success = run_script(script_path, description, log_file, script_args)
                results[description] = success
        
        # Calculate timing
        total_time = time.time() - start_time
        
        # Summary
        summary_header = f"\n{'=' * 80}\nPIPELINE SUMMARY\n{'=' * 80}\n"
        print_to_both(summary_header, log_file)
        
        # Identity comparisons, so the SKIPPED marker cannot be counted as a success
        # by truthiness nor as a failure by falsiness.
        successful = [name for name, st in results.items() if st is True]
        skipped = [name for name, st in results.items() if st == 'SKIPPED']
        failed = [name for name, st in results.items() if st is False]

        summary = f"""
Results:
  [OK] Successful: {len(successful)}/{len(results)}
  [--] Skipped:    {len(skipped)}/{len(results)} (declared exceptions; not failures)
  [XX] Failed:     {len(failed)}/{len(results)}

Total Execution Time: {total_time/60:.1f} minutes
"""
        print_to_both(summary, log_file)

        if successful:
            success_list = "\n[SUCCESS] Completed:\n" + "\n".join([f"  [+] {s}" for s in successful]) + "\n"
            print_to_both(success_list, log_file)

        if skipped:
            skip_list = ("\n[SKIPPED] Declared exceptions (not failures):\n"
                         + "\n".join([f"  [~] {s_}" for s_ in skipped]) + "\n")
            print_to_both(skip_list, log_file)

        if failed:
            fail_list = "\n[FAILED] Incomplete:\n" + "\n".join([f"  [-] {f}" for f in failed]) + "\n"
            print_to_both(fail_list, log_file)
        
        # Output locations
        outputs = f"""
{'=' * 80}
OUTPUT LOCATIONS
{'=' * 80}

Summary Statistics:
  outputs/tables/TABLE1_PANEL_A_full_sample.csv
  outputs/tables/TABLE1_PANEL_B_crsp_sample.csv
  outputs/tables/TABLE1_PANEL_C_by_fcc.csv
  outputs/tables/TABLE1_PANEL_D_by_timing.csv
  outputs/tables/TABLE1_COMBINED.txt

ARCHIVED (Pre-2007 comparison):
  outputs/figures/FIGURE_PARALLEL_TRENDS.png (Archived: Parallel trends, 2004-2010)
  outputs/tables/TABLE_BALANCE_TEST.csv (Archived: Pre-2007 balance test)

Essay 2 Regression Tables (Firm-Clustered SEs):
  outputs/tables/essay2/TABLE2_baseline_disclosure.txt
  outputs/tables/essay2/TABLE3_fcc_regulation.txt
  outputs/tables/essay2/TABLE4_prior_breaches.txt
  outputs/tables/essay2/TABLE5_breach_severity.txt
  outputs/tables/essay2/TABLE_APPENDIX_alternative_explanations.txt (CPNI & HHI robustness)

Essay 1 - Synthetic Control Matching (PRIMARY CAUSAL ID for H2):
  outputs/scm_crsp_with_sprint/scm_crsp_sprint_proxy_results.csv (SCM results: n=41 FCC firms, -4.03% effect, p=0.003)
  outputs/scm_crsp_with_sprint/consolidated_by_company.csv (Aggregate by company)
  outputs/ESSAY1_SCM_CAUSAL_ID_SUMMARY.txt (Complete summary of SCM methodology and results)

Essay 2 Robustness Checks (Post-2007 sample restriction test):
  outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt (Robustness: FCC effect in post-2007 sample)
  outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt (Robustness: FCC effect with industry FE)
  outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt (Robustness: FCC effect by firm size)
  outputs/tables/essay2/FCC_Causal_ID_Summary.txt (Robustness summary)
  outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt (Standard errors robustness)
  outputs/tables/essay2/H1_TOST_Equivalence_Test.txt (H1 null hypothesis equivalence test)
  outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt (Multicollinearity diagnostics)

Essay 3 — CURRENT (Query 2 chain): outputs/ESSAY3_QUERY2_REPORT.md, outputs/essay3_q2/
  (f1_ladder.csv, f4_placebo.csv, f3_sensitivities.csv, constants_essay3_q2.json, tmobile_timeline.csv)

Essay 3 Governance Response — RETIRED 2026-09-11 (legacy outputs, kept on disk; not regenerated):
  outputs/tables/essay3_governance/reduced_form_h6_results.csv (Reduced form: FCC effect on turnover, N=651)
  outputs/tables/essay3_governance/mediator_first_stage_results.csv (First stage; the 14.52pp figure is RETIRED — no computed source)
  outputs/tables/essay3_governance/with_mediator_model_coefficients.csv (Mediation model: FCC + immediate_disclosure)
  outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv (Bootstrap indirect effects, 1,000 iterations)
  outputs/tables/essay3_governance/h6_tost_equivalence_results.csv (TOST equivalence test, N=651, ±10pp bounds)
  outputs/tables/essay3_governance/H6_TOST_Equivalence_Test.txt (TOST interpretation and results)
  outputs/tables/essay3_governance/h6_reduced_form_all_coefficients.csv (Control variable significance: which predictors reach p<.10)
  outputs/tables/essay3_governance/h6_firm_size_heterogeneity_full.csv (Heterogeneity by firm size: 30d/90d/180d quartile analysis)
  outputs/tables/essay3_governance/CAUSAL_ID_COVARIATE_BALANCE.csv (Balance test: FCC vs non-FCC firms)
  outputs/tables/essay3_governance/CAUSAL_ID_PLACEBO_TESTS.csv (Placebo tests: alternative governance outcomes)
  outputs/tables/essay3_governance/CAUSAL_ID_DOSE_RESPONSE.csv (Dose-response: FCC effect by severity)
  outputs/tables/essay3_governance/cox_model_all_turnover.csv (Cox PH: FCC HR=1.127, p=.702; Schoenfeld p=.020 for FCC)
  outputs/tables/essay3_governance/H6_Cox_Model_Results.txt (Cox interpretation: PH violation noted, logistic regression is primary spec)
  outputs/tables/essay3_governance/ols_lpm_h6_results.csv (OLS LPM: FCC effects 0.024pp, 0.0015pp, -0.0138pp; all p>.63)
  outputs/tables/essay3_governance/negative_binomial_h6_results.csv (Neg Binomial: FCC IRR=1.220, p=.069; marginally NS)
  outputs/tables/essay3_governance/robustness_check2_disclosure_thresholds.csv (Alternative thresholds 5/10/14-day: FCC all null p>.35)
  outputs/tables/essay3_governance/robustness_check3_restricted_samples.csv (Restricted samples: unambiguous dates, large firms, complete data all N=651, identical results)

Essay 3 Robustness Checks (Volatility):
  outputs/tables/essay3/TABLE2_volatility_changes.txt
  outputs/tables/essay3/TABLE3_information_asymmetry.txt
  outputs/tables/essay3/TABLE_B8_post_2007_interaction_volatility.txt (Robustness: FCC volatility effect in post-2007 sample)
  outputs/tables/essay3/TABLE_FCC_Industry_FE_Comparison_Volatility.txt (Robustness: FCC volatility effect with industry FE)
  outputs/tables/essay3/TABLE_FCC_Size_Sensitivity_Volatility.txt (Robustness: FCC volatility effect by firm size)
  outputs/tables/essay3/FCC_Causal_ID_Summary_Volatility.txt (Robustness summary)

Heterogeneity Analysis Results (Publication Appendix Tables B11-B17):
  outputs/tables/TABLE_GOVERNANCE_HETEROGENEITY_RESULTS.csv (Phase 1: Governance quality, B11)
  outputs/tables/TABLE_CVSS_COMPLEXITY_HETEROGENEITY_RESULTS.csv (Phase 2: CVSS complexity, B12) [BREAKTHROUGH: +6.27%**]
  outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv (Analysis #3: Ransomware, B13)
  outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv (Analysis #4: Media coverage, B14) [+7.08%**]
  outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv (Analysis #5: Time windows, B15)
  outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv (Analysis #6: Type diversity)
  outputs/tables/TABLE_COMPLEXITY_INDEX_VOLATILITY_RESULTS.csv (Analysis #8: Complexity index, Essay 2 mechanism)
  outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv (Analysis #9: Information environment, Essay 2 mechanism - Spec A/B/C)

Enriched Datasets:
  Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv (Phase 1)
  Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv (Phase 2, used by Analyses #3-7)

ML Outputs:
  outputs/ml_models/ml_model_summary.csv
  outputs/ml_models/feature_importance_car30d.csv
  outputs/ml_models/feature_importance_car30d.png
  outputs/validation/dissertation_robustness_section.txt

Robustness Tables:
  outputs/robustness/tables/R01_alternative_windows_summary.csv
  outputs/robustness/tables/R02_timing_thresholds_summary.csv
  outputs/robustness/tables/R03_sample_restrictions_summary.csv
  outputs/robustness/tables/R04_standard_errors_summary.csv
  outputs/robustness/tables/R05_fixed_effects_summary.csv

Robustness Figures:
  outputs/robustness/figures/R02_timing_thresholds.png
  outputs/robustness/figures/R03_sample_restrictions.png
  outputs/robustness/figures/R04_standard_errors.png
  outputs/robustness/figures/R05_fixed_effects.png

{'=' * 80}
CANONICAL RESULTS (AUDIT CLOSED 7/28/2026)
{'=' * 80}

Authoritative figures live in ESSAY_RESULTS_SUMMARY_CORRECTED.md - read that,
not this log, when drafting. Superseded values: outputs/STALE_RESULTS_MANIFEST.txt.

Essay 1 (N=648, treated 115, Form 499 classification):
  H1 +0.61pp p=.482, TOST .045  -> BOUNDED NULL
  H2 -0.42pp p=.575, TOST .013  -> BOUNDED NULL
  H3 +0.03pp p=.645, TOST <.001 -> BOUNDED NULL
  H4 -0.39pp p=.811, TOST .148  -> INCONCLUSIVE (underpowered)
  Frame: three bounded nulls and one underpowered.
  First stage 16.71pp: RETIRED 2026-09-11 (no computed source; outputs/ESSAY3_QUERY1_REPORT.md C1).

Essay 2 (H5, N=644, spec includes return_volatility_pre, R2=.42):
  Main +0.12pp p=.914, MDE 3.23pp, TOST +-2.10pp p=.044 -> BOUNDED NULL
  Quartiles: only Q2 significant (one cell of four, no gradient) -> noise.

Essay 3 (H6, Query 2 chain; see outputs/ESSAY3_QUERY2_REPORT.md): executive departure
  (Item 5.02(b), classifier v2), notification anchor, N=338 (107 treated / 12 parent CIKs).
  The 7/28-chain figures (N=646, any-5.02 outcome, AMEs, Cox HR 1.43) are RETIRED.

Membership (final, 7/28 adjudications): Cricket treated (caught defect),
Boost treated (clause b), DISH untreated, Aero Charter excluded.
118 treated / 37 firms CRSP; 115 in regression.

Data-quality contribution: four documented failure modes
(DATA_QUALITY_DOCUMENTATION.md) - CIK duplicates, name-token collisions,
SIC-as-regulatory-proxy, silent Item 5.02 extraction failure.

Open questions (Dr. Johnson): identification path (descriptive vs state-law
staggered adoption) and Essay 2 / job-talk center. SCM: rebuild under scpi
with Form 499 membership or drop (pending Lambert) - not committee-locked.

Complete log saved to: {log_path}

{'=' * 80}
"""
        print_to_both(outputs, log_file)
        
        # RETIRED 2026-10-01: the Form 499 "critical keys" gate. It named the descriptions
        # of scripts 86c and 90b, the pre-rebuild H1-H4 and H5 re-estimations - both retired
        # by the publish-ready prune. Left in place it would have failed every run from now
        # on: results.get() on a step that no longer exists is False, so a run with zero
        # failures still fell through to the "[WARNING] Primary Form 499 analyses did not
        # all succeed" branch and returned False. The rule that replaced it on 2026-09-11 -
        # any failure fails the pipeline - already covers what this was for, across all
        # live steps rather than two hand-picked pre-rebuild ones.

        # Verify critical outputs exist regardless of status
        outputs_verified = verify_outputs(log_file, run_start=start_time)

        # 2026-09-11: ANY script failure now fails the pipeline. Previously this returned True whenever
        # the two Form 499 "critical keys" succeeded, so a clean-clone run with six failed scripts -
        # including scripts/158, whose assertion caught a stale baseline - still exited 0 and printed
        # SUCCESS. Exit status must reflect the whole run, not two hand-picked scripts.
        if failed:
            final = (f"\n[FAILED] {len(failed)} of {len(results)} scripts did not complete. This is NOT a clean run.\n"
                     + "\n".join(f"  [-] {f}" for f in failed)
                     + f"\n{'=' * 80}\n")
            print_to_both(final, log_file)
            return False

        if not outputs_verified:
            final = ("\n[FAILED] Every script ran, but required outputs are missing or were not written by this\n"
                     f"run - see OUTPUT VERIFICATION above.\n{'=' * 80}\n")
            print_to_both(final, log_file)
            return False

        note = ("" if not skipped else
                f"  {len(skipped)} declared exception(s) skipped; see the SKIPPED list above.\n")
        final = (f"\n[***] [SUCCESS] Core dissertation analysis complete and outputs verified.\n"
                 + note + f"{'=' * 80}\n")
        print_to_both(final, log_file)
        return True

def main():
    """Main entry point"""
    try:
        success = run_all()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n[FATAL ERROR] Pipeline crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()