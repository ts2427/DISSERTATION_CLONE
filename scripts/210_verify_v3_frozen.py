"""
REBUILD V4 — STAGE 0: V3 FREEZE CHECK
=====================================================================================
Proves that nothing in the v3 baseline changed while v4 work proceeds on branch
rebuild-v4.

Baseline is the annotated tag **v3-frozen**, resolved to its commit
(v3-frozen^{commit}) everywhere it is used or printed. The file list and the git blob
id of every file come from `git ls-tree -r <commit>`.

Scope (tracked at the baseline commit):
    Data/**, outputs/** (excluding outputs/rebuild_v4/ and outputs/essay3_v4/),
    scripts/**, docs/**, plus run_all.py, .gitattributes, .gitignore.

Usage:
    python scripts/210_verify_v3_frozen.py --create   # write the manifest (once)
    python scripts/210_verify_v3_frozen.py            # verify; nonzero exit on drift

Manifest: outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv
    path, size, sha256, blob_id, append_only, prefix_size, prefix_sha256

TWO IDENTITIES PER FILE
-----------------------
sha256   the bytes on disk — what a script would actually read. Several tracked paths
         are Git-LFS pointers in the index but real content in the working tree, so the
         on-disk hash is the one that answers "did the input change?"
blob_id  the git object id at the baseline commit — what history says the file is.

VERDICT RULES
-------------
FAIL  a baseline file whose blob id changed                     (UNCONDITIONAL)
Authorised exceptions (2026-09-29). docs/claude/V3_FREEZE_EXCEPTIONS.md may declare
  individual departures from the manifest, each pinned on BOTH the hash the file had and
  the hash it has now. The manifest itself is never rewritten. Consequences, deliberately:
  a FURTHER change to an excepted file fails (its new hash no longer matches), a change to
  any other baseline file fails, and if the manifest is ever re-created every exception
  stops matching and the gate fails closed. Exceptions are printed in full on every run.

FAIL  a baseline file whose on-disk sha256 changed AND
      `git diff --quiet <baseline> -- <path>` exits nonzero     (real content change)
PASS  a baseline file whose on-disk sha256 changed BUT
      `git diff --quiet <baseline> -- <path>` exits 0           (eol/representation
      artifact — git, applying its own normalisation, sees no difference; logged)
FAIL  a baseline file that is gone
FAIL  a newly tracked file OUTSIDE the v4 allowlist (an addition to v3 territory)
PASS  a newly tracked file INSIDE the v4 allowlist

"Blob id wins" is deliberately NOT adopted: a blob-id mismatch always fails, and a
sha mismatch is excused only when git itself reports the working tree identical to the
baseline. An eol artifact cannot mask a content edit, because a content edit makes
`git diff` nonzero.

APPEND-ONLY FILES (.gitattributes, .gitignore)
----------------------------------------------
These two may grow and only grow. They are judged SOLELY by the prefix test: the
baseline bytes must still be an exact byte-for-byte prefix of the current file.

The prefix baseline is taken with `git cat-file --filters <commit>:<path>`, which
applies the same checkout filters as a working-tree write (eol conversion under
core.autocrlf, LFS smudge). Taking it from the raw blob instead compares LF bytes
against a CRLF working tree and fails on every Windows checkout regardless of whether
anything changed. That was the defect in the first version of this script.

V4 ALLOWLIST (exact)
--------------------
Directories, matched at a path boundary only:
    Data/wrds_v4/, Data/processed/rebuild_v4/, Data/edgar/ex21_cache_v4/,
    Data/edgar/submissions_cache_v4/, Data/edgar/item5_02_text/,
    outputs/rebuild_v4/, outputs/essay3_v4/
Data/edgar/item5_02_text/ is shared with v3: v4 adds documents alongside v3's.
Only ADDITIONS are admitted - any change to a baseline file there still fails on
the sha256/blob comparison, which does not consult this list.
Scripts, by parsed leading number only, 210 <= n <= 256:  scripts/<n>_*.py
Documents, by exact path:
    docs/claude/REBUILD_V4_QUERY.md, docs/claude/REPRODUCE_ESSAY3_V4.md
Prefix matching is deliberately NOT used for scripts: "scripts/21" would also admit
scripts/21_foo.py and scripts/2199_foo.py.
"""
import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv")
BASELINE_TAG = "v3-frozen"

INCLUDE_DIRS = ("Data/", "outputs/", "scripts/", "docs/")
INCLUDE_FILES = ("run_all.py", ".gitattributes", ".gitignore")
EXCLUDE_PREFIXES = ("outputs/rebuild_v4/", "outputs/essay3_v4/")

APPEND_ONLY = (".gitattributes", ".gitignore")

# RUN ARTIFACTS (added 2026-10-01 by ruling). Files already in the baseline that a LIVE
# pipeline step rewrites every run: its own progress log. Checked for PRESENCE, never for
# content or blob id, because their bytes legitimately differ run to run (timestamps,
# fetched byte counts, elapsed seconds) while carrying no analytic result.
#
# This is the narrowest exemption that makes the gate stable across runs. It is NOT the v4
# allowlist, which admits only newly TRACKED files and so can never cover a baseline file
# that changes. Every entry is a progress log written by one of the eight live Query 2
# steps that log themselves; no analytic output is listed, and anything absent from this
# list is still compared byte for byte.
RUN_ARTIFACTS = (
    "outputs/essay3_q2/187_fetch.log",                   # scripts/187
    "outputs/essay3_q2/b_fetch_log.csv",                 # scripts/187, per-document fetch record
    "outputs/essay3_q2/188_classifier.log",              # scripts/195
    "outputs/essay3_q2/195_classifier.log",              # scripts/195
    "outputs/essay3_q2/190_case.log",                    # scripts/190
    "outputs/essay3_q2/191_tmobile_proxy_periodic.log",  # scripts/191
    "outputs/essay3_q2/199_sample.log",                  # scripts/199
    "outputs/essay3_q2/202_estimation.log",              # scripts/202
    "outputs/essay3_q2/203_case.log",                    # scripts/203
    "outputs/essay3_q2/b_exhibits_log.csv",              # scripts/203, per-exhibit record
    "outputs/essay3_q2/204_se_diagnostics.log",          # scripts/204
    # Figures (added 2026-10-01 by ruling). matplotlib PNGs are not byte-reproducible
    # across environments - font rasterisation and the PNG encoder differ - while the
    # numbers they plot come from CSVs this gate does compare byte for byte.
    "outputs/figures/essay2_v2/fig_C3_spec_curve.png",         # scripts/171
    "outputs/figures/essay2_v2/fig_C4_power_curve.png",        # scripts/171
    "outputs/figures/essay2_v2/fig_C5_carrier_denominator.png",  # scripts/174
    # Timestamp-only progress reports (added 2026-10-01 by ruling). Each differs between
    # runs ONLY on a "- run (UTC):" line. All five already fall under the
    # outputs/rebuild_v4/ prefix in EXCLUDE_PREFIXES, so they are not in the manifest and
    # these entries never match; they are listed anyway so the intent is on the record and
    # the rule survives any future change to that prefix.
    "outputs/rebuild_v4/212_link_report.md",             # scripts/212 pass 1
    "outputs/rebuild_v4/v4_212_link_report.md",          # scripts/212 pass 2
    "outputs/rebuild_v4/214_corrections.md",             # scripts/214
    "outputs/rebuild_v4/215_ledger.md",                  # scripts/215
    "outputs/rebuild_v4/237_validation_draw.md",         # scripts/237
)

# SKIP-DEPENDENT FILES (added 2026-10-01 by ruling). A file whose content legitimately
# differs when a DECLARED skip removed the step that supplies part of it - and which must
# still be compared when that step runs. The governing condition is the same one
# run_all.py's DECLARED_SKIPS tests: the licensed input's presence.
#
# ESSAY2_QUERY6_REPORT.md is scripts/174's umbrella report. Its CPQS and EDGE
# effective-spread channel lines come from the intraday quotes top-up that scripts/170 and
# 167 need, so on a machine without the WRDS licence those lines are absent. On a licensed
# checkout the file is compared byte for byte like anything else.
SKIP_DEPENDENT = {
    "outputs/ESSAY2_QUERY6_REPORT.md": (
        "Data/wrds/crsp_quotes_topup.csv",
        "scripts/174 effective-spread channels; needs the licensed quotes top-up "
        "(the scripts/170 declared exception)"),
}


def _skip_dependent_waived(path):
    """True if `path` is skip-dependent AND its governing input is absent."""
    ent = SKIP_DEPENDENT.get(path)
    return bool(ent) and not path_exists(Path(ent[0]))


# DOCX: compared on EXTRACTED TEXT, not container bytes (2026-10-01 ruling).
# A .docx is a ZIP. Every member carries a modification timestamp and the archive is
# rebuilt on each render, so two renders of identical content never match byte for byte.
# Comparing the text instead makes the check mean what it should: a text difference still
# FAILS. Covers all three tracked .docx files:
#     outputs/rebuild/APPENDIX_V3_TABLES.docx        (scripts/160, in the manifest)
#     outputs/rebuild/INTEXT_TABLES_3_14.docx        (in the manifest, no live writer)
#     outputs/essay3_appendix/ESSAY3_APPENDIX_TABLES.docx  (scripts/245, tracked, not in
#                                                     the manifest - covered if added)
# outputs/rebuild/INTEXT_TABLES_4_5.docx is written by scripts/160 but is untracked, so no
# gate applies to it.
def docx_text(data):
    """All visible text runs of a .docx, in order. -> str, or None if unreadable."""
    import io
    import zipfile
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return None
    return "\n".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))

V4_DIRS = (
    "Data/wrds_v4/",
    "Data/processed/rebuild_v4/",
    "Data/edgar/ex21_cache_v4/",
    "Data/edgar/submissions_cache_v4/",
    # SHARED with v3, and admitted deliberately. Tim ruled that scripts/231 writes
    # the v4 Item 5.02 documents into the EXISTING layout (187's convention) so the
    # two vintages interleave, which means v4 ADDS files to a v3 directory.
    #
    # This weakens nothing that matters. The allowlist governs only NEWLY TRACKED
    # files; modification or deletion of a file already in the baseline is caught by
    # the sha256/blob comparison, which the allowlist never consults. So v3's own
    # documents here remain as frozen as before - only additions alongside them pass.
    "Data/edgar/item5_02_text/",
    "outputs/rebuild_v4/",
    "outputs/essay3_v4/",
    # Essay 3 Query 3 and Query 4 read-and-print outputs (scripts/242-244). They read
    # the v4 artefacts and write only here; they touch no v3 path, so admitting them
    # costs the freeze nothing. Added 2026-09-25 after the Query 3/4 commit tripped
    # this gate with 27 additions and zero content or blob changes.
    "outputs/essay3_q3/",
    "outputs/essay3_q4/",
    # The rendered appendix (scripts/245-246). Formatting and descriptive counts read
    # from the q3/q4 CSVs; nothing here is estimated and no v3 path is touched.
    # Added 2026-09-25.
    "outputs/essay3_appendix/",
    # Defense supplement (2026-10-02, scripts 249-253). Supplementary estimates on the
    # frozen samples, written only here; no v3 path is touched by these steps.
    "outputs/defense_supplement/",
    # Repo cleanup (2026-10-03, Tim): superseded files moved here with their relative paths
    # (archive/ARCHIVE_MAP.csv). A move removes the baseline path (recorded MISSING when the
    # manifest is re-created) and adds the archive path, which this entry admits.
    "archive/",
    # R replication package for the committee (2026-10-04): exported estimation samples and
    # an R script that reproduces the headline estimates. New folder; touches no v3 path.
    "r_replication/",
)
V4_DOCS = (
    "docs/claude/REBUILD_V4_QUERY.md",
    "docs/claude/REPRODUCE_ESSAY3_V4.md",
    # The v4 settled-state document. v3's ESSAY3_POST_RERUN_STATE.md is NOT listed and
    # must stay frozen: this file supersedes parts of it by pointer, never by edit.
    "docs/claude/ESSAY3_V4_STATE.md",
    # The post-freeze change rule. Tagged essay3-v4-final.
    "docs/claude/POST_DEFENSE.md",
    # The Query 3 and Query 4 reports. Force-added (.gitignore:79 is *.md).
    "outputs/ESSAY3_QUERY3_REPORT.md",
    "outputs/ESSAY3_QUERY4_REPORT.md",
    # Run-All Follow-Up Stage 2 (2026-09-29). Both are NEW documents, not edits of frozen
    # ones: the Essay 1 attrition ledger written by scripts/247, and the tombstone that
    # withdraws the 41 ungenerated Essay 2 appendix CSVs from citation.
    "outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md",
    "outputs/tables/essay2_appendix/TOMBSTONE.md",
    "outputs/RUN_ALL_AUDIT_REPORT.md",
    "outputs/RUN_ALL_FOLLOWUP_REPORT.md",
    # The pinned freeze exceptions this script reads. New file, not an edit of a frozen one.
    "docs/claude/V3_FREEZE_EXCEPTIONS.md",
    # Part A5 (2026-10-01): newly tracked at the rebaseline. CONSTANTS_BLOCK_V3.md is
    # written by scripts/158 next to constants_v3.json and had never been committed
    # (outputs/*.md is gitignored); the alignment report is this query's deliverable.
    "outputs/rebuild/CONSTANTS_BLOCK_V3.md",
    "outputs/ALIGNMENT_REPORT.md",
    "outputs/TIMING_MEASUREMENT_REPORT.md",
    # Parts B3 and E of the alignment query. Both are NEW documentation, not edits of
    # frozen files: the Essay 2 reproduction exception and the known-limitations ledger.
    "docs/claude/REPRODUCE_ESSAY2.md",
    "docs/claude/KNOWN_LIMITATIONS.md",
    # Written by scripts/157 beside the stage-7 CSVs; never committed before the
    # 2026-10-01 stage-7 regeneration (outputs/*.md is gitignored).
    "outputs/rebuild/STAGE7_VERIFICATION.md",
    # Repo cleanup Stage 1 (2026-10-03): the inventory, its summary and the cleanup report.
    "outputs/REPO_INVENTORY.csv",
    "outputs/REPO_INVENTORY_SUMMARY.md",
    "outputs/REPO_CLEANUP_REPORT.md",
    # Newly tracked 2026-10-03: pipeline reports written by live steps 150-156, never committed
    # while *.md was ignored, each byte-identical across two clean-clone runs. Not tracked:
    # STAGE4_TREATMENT_REPORT.md, which prints the registry snapshot's file date.
    "outputs/rebuild/GATE1_APPLICATION_REPORT.md",
    "outputs/rebuild/GATE1_SUMMARY.md",
    "outputs/rebuild/GATE2_ADJACENCY_SHEET.md",
    "outputs/rebuild/STAGE5_REPORT.md",
    "outputs/rebuild/STAGE6_REPORT.md",
    # Reviewer guide for the committee's pipeline review (2026-10-03).
    "REVIEWER_GUIDE.md",
)
SCRIPT_RE = re.compile(r"^scripts/(\d+)_[^/]*\.py$")
SCRIPT_LO, SCRIPT_HI = 210, 256  # 250-253, 255: defense supplement; 254: CRSP loader; 256: Essay 3 appendix supplement


def git(*args, binary=False):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode("utf-8", errors="replace")


def git_rc(*args):
    """Return the exit code only; never aborts."""
    return subprocess.run(["git", *args], capture_output=True).returncode


def baseline_commit():
    return git("rev-parse", f"{BASELINE_TAG}^{{commit}}").strip()


def in_scope(p):
    if any(p.startswith(x) for x in EXCLUDE_PREFIXES):
        return False
    return p.startswith(INCLUDE_DIRS) or p in INCLUDE_FILES


def is_v4_allowed(p):
    if any(p.startswith(d) for d in V4_DIRS):
        return True
    if p in V4_DOCS:
        return True
    m = SCRIPT_RE.match(p)
    return bool(m and SCRIPT_LO <= int(m.group(1)) <= SCRIPT_HI)


def baseline_tree(commit):
    out = {}
    for line in git("ls-tree", "-r", "--full-name", commit).splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        _mode, otype, blob = meta.split()
        if otype == "blob" and in_scope(path):
            out[path] = blob
    return out


def tracked_now():
    out = {}
    for line in git("ls-files", "-s").splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        _mode, blob, _stage = meta.split()
        if in_scope(path):
            out[path] = blob
    return out


def lfs_oids():
    """path -> Git-LFS object id, from `git lfs ls-files -l`.

    Added 2026-10-01. The manifest's on-disk sha256 is MACHINE-STATE-DEPENDENT for LFS
    files: whether a path holds 136 bytes of pointer text or its real content depends on
    whether that machine has run `git lfs pull`. The authoring repository held pointers
    for 19 Data/JSON Files/*.json while a clean clone held the real 37 MB content, so 210
    reported 19 content changes that were nothing of the kind and could not pass in any
    clone. The oid comes from the index, not the working tree, so it is the same on every
    machine, and it is what actually identifies the content.
    """
    out = {}
    for line in git("lfs", "ls-files", "-l").splitlines():
        line = line.strip()
        if not line:
            continue
        # "<oid> <*|-> <path>"; the marker says whether the object is present locally,
        # which is exactly the machine-dependent fact being factored out.
        parts = line.split(" ", 2)
        if len(parts) == 3 and re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            out[parts[2].strip()] = parts[0]
    return out


EXCEPTIONS = Path("docs/claude/V3_FREEZE_EXCEPTIONS.md")

# One row of the exceptions table:
#   | `path` | `old sha256` | `new sha256` | `old blob` | `new blob` | commits | parts |
EXC_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*"
    r"\|\s*`([0-9a-f]{40})`\s*\|\s*`([0-9a-f]{40})`\s*\|([^|]*)\|([^|]*)\|\s*$")


def load_exceptions():
    """Authorised, individually pinned departures from the manifest.

    Added 2026-09-29 (Tim's ruling on Stage 2): the manifest must NOT be re-created,
    because rewriting it would record the new state as the baseline and erase the evidence
    that 13 baseline files moved. Instead each departure is declared with the hash it had
    AND the hash it has, so the override is spent as soon as the file changes again.
    """
    if not EXCEPTIONS.exists():
        return {}
    out = {}
    for line in EXCEPTIONS.read_text(encoding="utf-8").split("\n"):
        m = EXC_RE.match(line.strip())
        if not m:
            continue
        path, old_sha, new_sha, old_blob, new_blob, commits, parts = m.groups()
        assert path not in out, f"duplicate exception for {path}"
        assert old_sha != new_sha, f"exception for {path} pins the same hash twice"
        out[path] = dict(old_sha=old_sha, new_sha=new_sha, old_blob=old_blob,
                         new_blob=new_blob, commits=commits.split(), parts=parts.split(),
                         used_sha=False, used_blob=False)
    return out


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def long_path(path):
    """The extended-length form of a path, on Windows.

    Added 2026-10-01. Windows caps ordinary paths at 260 characters, and Python's stat and
    open obey that cap even when git was given core.longpaths=true and could create the
    file. In a clean clone at a deep directory, 13 literature PDFs under Data/Articles/
    with long filenames therefore existed on disk while Path.exists() returned False, so
    verify() reported them DELETED - which it treats as fatal - and the gate could not
    pass in any deep-path clone regardless of the pipeline. The \\\\?\\ prefix lifts the cap.
    """
    if os.name != "nt":
        return str(path)
    p = os.path.abspath(str(path))
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):                      # UNC share
        return "\\\\?\\UNC\\" + p.lstrip("\\")
    return "\\\\?\\" + p


def path_exists(path):
    """Presence, correct for paths over 260 characters on Windows."""
    if os.path.exists(str(path)):
        return True
    return os.path.exists(long_path(path))


def path_size(path):
    return os.stat(long_path(path)).st_size


def read_bytes(path):
    with open(long_path(path), "rb") as f:
        return f.read()


def sha256_file(path):
    h = hashlib.sha256()
    with open(long_path(path), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_bytes(blob_id):
    """Raw bytes of a git blob by object id. -> bytes, or None."""
    r = subprocess.run(["git", "cat-file", "blob", blob_id],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha256_file_eolnorm(path):
    """sha256 of the file with CRLF collapsed to LF.

    Added 2026-10-01. This is how EOL-versus-content is now adjudicated, replacing
    `git diff --quiet <v3-frozen> -- <path>`. That test compared the working tree against
    the FROZEN TAG while the sha256 it was explaining came from the MANIFEST, and after a
    re-freeze the two disagree: a file legitimately changed since the tag - which the
    current manifest records - fails the git test, so line-ending variance in a clone was
    reported as a content change. Three scripts edited on 2026-10-01 were misreported that
    way. Comparing normalised hashes keeps both sides of the comparison on the manifest.

    Read in one pass rather than chunked: chunking can split a CRLF across the boundary.
    """
    return hashlib.sha256(read_bytes(path).replace(b"\r\n", b"\n")).hexdigest()


def filtered_baseline(commit, path):
    """Baseline content as it would be written to the working tree (eol + LFS filters)."""
    return git("cat-file", "--filters", f"{commit}:{path}", binary=True)


def create():
    commit = baseline_commit()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    # Fixed 2026-10-01 (Part A5). This function refreshed sha256 from disk but copied
    # blob_id straight from the baseline tag's tree, while verify() compares blob_id
    # against `git ls-files -s` TODAY. So after a --create, every file whose git blob had
    # moved since v3-frozen still failed the blob test - 30 of them - and the gate could
    # never return PASS again. A re-freeze has to record the CURRENT blob, from the same
    # source verify() reads. The manifest's SCOPE still comes from the baseline tree,
    # which is deliberate and unchanged: a re-freeze re-records the bytes of the frozen
    # file set, it does not widen that set.
    now = tracked_now()
    oids = lfs_oids()
    rows = []
    for p, blob in sorted(baseline_tree(commit).items()):
        fp = Path(p)
        if path_exists(fp):
            size, sha, nsha = path_size(fp), sha256_file(fp), sha256_file_eolnorm(fp)
        else:
            size, sha, nsha = -1, "MISSING", "MISSING"
        row = dict(path=p, size=size, sha256=sha, sha256_eolnorm=nsha,
                   lfs_oid=oids.get(p, ""),
                   blob_id=now.get(p, blob),
                   append_only=int(p in APPEND_ONLY), prefix_size="", prefix_sha256="")
        if p in APPEND_ONLY:
            base = filtered_baseline(commit, p)
            row["prefix_size"] = len(base)
            row["prefix_sha256"] = sha256_bytes(base)
        rows.append(row)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size", "sha256", "sha256_eolnorm",
                                          "lfs_oid", "blob_id", "append_only",
                                          "prefix_size", "prefix_sha256"])
        w.writeheader()
        w.writerows(rows)
    total = sum(r["size"] for r in rows if r["size"] > 0)
    print(f"WROTE {MANIFEST}")
    print(f"  baseline      : {BASELINE_TAG}^{{commit}} = {commit[:8]}")
    print(f"  files hashed  : {len(rows):,}")
    print(f"  total bytes   : {total:,} ({total/1e6:,.1f} MB)")
    print(f"  manifest sha  : {sha256_file(MANIFEST)}")
    for r in rows:
        if r["append_only"]:
            print(f"  append-only   : {r['path']} prefix {r['prefix_size']} bytes "
                  f"(filtered) sha {r['prefix_sha256'][:12]}")
    missing = [r["path"] for r in rows if r["sha256"] == "MISSING"]
    if missing:
        print(f"  NOTE tracked-but-absent on disk: {len(missing)} -> {missing[:5]}")
    return 0


def check_prefix(path, prefix_size, prefix_sha):
    fp = Path(path)
    if not path_exists(fp):
        return False, "deleted"
    cur = read_bytes(fp)
    if len(cur) < prefix_size:
        return False, f"SHRANK ({len(cur)} < {prefix_size} bytes)"
    if sha256_bytes(cur[:prefix_size]) != prefix_sha:
        return False, "baseline bytes were MODIFIED, not merely appended to"
    return True, f"append-only OK (+{len(cur) - prefix_size} bytes)"


def verify():
    if not MANIFEST.exists():
        sys.exit(f"FAIL: manifest not found at {MANIFEST}. Run with --create first.")
    commit = baseline_commit()
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        base = {r["path"]: r for r in csv.DictReader(f)}

    now = tracked_now()
    sha_bad, blob_bad, deleted, added_ok, added_bad = [], [], [], [], []
    notes, eol_artifacts = [], []
    exc = load_exceptions()
    exc_hit = []
    cur_oids = lfs_oids()
    lfs_ok, lfs_bad = [], []
    run_art = []
    docx_same, skip_waived = [], []

    for p, rec in base.items():
        if int(rec["append_only"]):
            ok, why = check_prefix(p, int(rec["prefix_size"]), rec["prefix_sha256"])
            notes.append(f"{p}: {why}")
            if not ok:
                sha_bad.append((p, "prefix-test", why))
            continue

        fp = Path(p)
        if not path_exists(fp):
            if rec["sha256"] != "MISSING":
                deleted.append(p)
            continue

        # A run artifact: its presence was just confirmed above, and that is the whole
        # check. Content and blob id are deliberately not compared - a live step rewrites
        # this file on every run, so comparing either would fail the gate for doing its job.
        if p in RUN_ARTIFACTS:
            run_art.append(p)
            continue

        cur_blob = now.get(p)
        if cur_blob is None:
            deleted.append(f"{p} (untracked now)")
        elif cur_blob != rec["blob_id"]:
            e = exc.get(p)
            if e and e["old_blob"] == rec["blob_id"] and e["new_blob"] == cur_blob:
                e["used_blob"] = True
            else:
                blob_bad.append((p, rec["blob_id"][:12], cur_blob[:12]))

        # LFS paths are adjudicated by OID, not by on-disk bytes. Whether this machine
        # holds pointer text or real content is a smudge-state fact, not a content fact,
        # and the oid is identical on every machine.
        rec_oid = rec.get("lfs_oid") or ""
        if rec_oid:
            cur_oid = cur_oids.get(p, "")
            if cur_oid == rec_oid:
                lfs_ok.append(p)
            else:
                lfs_bad.append((p, rec_oid[:12], (cur_oid or "(not LFS now)")[:12]))
            continue

        cur_sha = sha256_file(fp)
        if cur_sha != rec["sha256"]:
            # A .docx differing in bytes: decide on TEXT. The manifest keeps no copy of the
            # old bytes, so the recorded blob supplies them - machine-independent and exact.
            if p.lower().endswith(".docx"):
                was = git_bytes(rec["blob_id"])
                a = docx_text(was) if was is not None else None
                b = docx_text(read_bytes(fp))
                if a is not None and b is not None and a == b:
                    docx_same.append(p)
                    continue
                sha_bad.append((p, "docx-text", "extracted text differs"))
                continue
            # A skip-dependent file whose governing input is absent.
            if _skip_dependent_waived(p):
                skip_waived.append(p)
                continue
            # EOL-versus-content, decided against the MANIFEST's normalised hash. Older
            # manifests carry no such column; those fall back to the git-diff test against
            # the baseline tag, which is what this replaced.
            rec_norm = rec.get("sha256_eolnorm") or ""
            if rec_norm:
                eol_only = sha256_file_eolnorm(fp) == rec_norm
            else:
                eol_only = git_rc("diff", "--quiet", commit, "--", p) == 0
            if eol_only:
                eol_artifacts.append(p)      # same bytes once line endings are normalised
            else:
                e = exc.get(p)
                if e and e["old_sha"] == rec["sha256"] and e["new_sha"] == cur_sha:
                    e["used_sha"] = True
                    exc_hit.append(p)
                else:
                    sha_bad.append((p, rec["sha256"][:12], cur_sha[:12]))

    for p in sorted(now):
        if p not in base:
            (added_ok if is_v4_allowed(p) else added_bad).append(p)

    print("=" * 78)
    print("V3 FREEZE CHECK - scripts/210")
    print("=" * 78)
    print(f"baseline        : {BASELINE_TAG}^{{commit}} = {commit[:8]}")
    print(f"manifest        : {MANIFEST} ({len(base):,} files)")
    print(f"tracked in scope: {len(now):,}")
    for n in notes:
        print(f"append-only     : {n}")
    # Ruling (Stage 0): zero eol artifacts is REQUIRED on the authoring machine. On
    # another platform -- the Stage 6 clean-clone test on Linux, where core.autocrlf
    # differs -- artifacts are permitted, but each must be counted and listed with its
    # blob match and its clean `git diff` shown, so a content change can never hide here.
    if eol_artifacts:
        print(f"eol artifacts   : {len(eol_artifacts)} file(s) -- disk bytes differ from "
              f"the manifest but git reports no difference. PERMITTED OFF-PLATFORM ONLY;")
        print("                  on the authoring machine this must be 0.")
        for p in eol_artifacts[:25]:
            blob_ok = now.get(p) == base[p]["blob_id"]
            nsha = base[p].get("sha256_eolnorm") or ""
            how = ("normalised hash matches the manifest" if nsha
                   else "git reports no difference from the baseline (legacy manifest)")
            print(f"   {p}\n      blob matches manifest: {blob_ok}   {how}")
        if len(eol_artifacts) > 25:
            print(f"   ... and {len(eol_artifacts) - 25} more")
    # Authorised exceptions are printed in full, every time. A PASS must never be able
    # to hide the fact that baseline files moved.
    print(f"\nAUTHORISED EXCEPTIONS ({EXCEPTIONS}) : {len(exc_hit)} of {len(exc)} declared")
    for pth in sorted(exc_hit):
        e = exc[pth]
        print(f"   {pth}")
        print(f"      sha  {e['old_sha'][:12]} -> {e['new_sha'][:12]}   "
              f"blob {e['old_blob'][:12]} -> {e['new_blob'][:12]}"
              f"{'' if e['used_blob'] else '   (blob still at baseline)'}")
        print(f"      {' '.join(e['commits'])}   parts: {' '.join(e['parts'])}")
    unused = sorted(k for k, e in exc.items() if not (e["used_sha"] or e["used_blob"]))
    if unused:
        print(f"   DECLARED BUT NOT MATCHED       : {len(unused)}")
        for pth in unused:
            print(f"      {pth} - the file no longer has the pinned new hash, or it is "
                  f"back at its baseline. Its exception is spent; remove the row or "
                  f"re-record it.")
    print(f"LFS paths by OID               : {len(lfs_ok)} match, {len(lfs_bad)} changed "
          f"(machine-independent; on-disk bytes not compared for these)")
    for p, a, b in lfs_bad[:25]:
        print(f"   {p}\n      oid was {a}  now {b}")
    print(f"\nSHA256 CHANGED (real content)  : {len(sha_bad)}")
    for p, a, b in sha_bad[:25]:
        print(f"   {p}\n      was {a}  now {b}")
    print(f"BLOB ID CHANGED (git object)   : {len(blob_bad)}")
    for p, a, b in blob_bad[:25]:
        print(f"   {p}\n      was {a}  now {b}")
    print(f"DELETED / UNTRACKED            : {len(deleted)}")
    for p in deleted[:25]:
        print(f"   {p}")
    print(f"RUN ARTIFACTS (logs, exempt)   : {len(run_art)} (present-checked; content not compared)")
    print(f"DOCX same text, new container  : {len(docx_same)} (compared on extracted text, not bytes)")
    print(f"WAIVED by a declared skip      : {len(skip_waived)}")
    for _p in skip_waived:
        print(f"   {_p} -- {SKIP_DEPENDENT[_p][1]}")
    print(f"ADDED outside v4 allowlist     : {len(added_bad)}")
    for p in added_bad[:25]:
        print(f"   {p}")
    print(f"ADDED inside v4 allowlist (ok) : {len(added_ok)}")
    for p in added_ok[:25]:
        print(f"   {p}")

    fail = bool(sha_bad or blob_bad or deleted or added_bad or lfs_bad)
    print("\nRESULT: " + ("FAIL - v3 baseline changed" if fail else "PASS - v3 baseline intact"))
    return 1 if fail else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true", help="write the manifest instead of verifying")
    a = ap.parse_args()
    sys.exit(create() if a.create else verify())
