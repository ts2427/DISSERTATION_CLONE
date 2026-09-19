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
Scripts, by parsed leading number only, 210 <= n <= 249:  scripts/<n>_*.py
Documents, by exact path:
    docs/claude/REBUILD_V4_QUERY.md, docs/claude/REPRODUCE_ESSAY3_V4.md
Prefix matching is deliberately NOT used for scripts: "scripts/21" would also admit
scripts/21_foo.py and scripts/2199_foo.py.
"""
import argparse
import csv
import hashlib
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
)
V4_DOCS = (
    "docs/claude/REBUILD_V4_QUERY.md",
    "docs/claude/REPRODUCE_ESSAY3_V4.md",
    # The v4 settled-state document. v3's ESSAY3_POST_RERUN_STATE.md is NOT listed and
    # must stay frozen: this file supersedes parts of it by pointer, never by edit.
    "docs/claude/ESSAY3_V4_STATE.md",
    # The post-freeze change rule. Tagged essay3-v4-final.
    "docs/claude/POST_DEFENSE.md",
)
SCRIPT_RE = re.compile(r"^scripts/(\d+)_[^/]*\.py$")
SCRIPT_LO, SCRIPT_HI = 210, 249


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


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def filtered_baseline(commit, path):
    """Baseline content as it would be written to the working tree (eol + LFS filters)."""
    return git("cat-file", "--filters", f"{commit}:{path}", binary=True)


def create():
    commit = baseline_commit()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for p, blob in sorted(baseline_tree(commit).items()):
        fp = Path(p)
        size, sha = (fp.stat().st_size, sha256_file(fp)) if fp.exists() else (-1, "MISSING")
        row = dict(path=p, size=size, sha256=sha, blob_id=blob,
                   append_only=int(p in APPEND_ONLY), prefix_size="", prefix_sha256="")
        if p in APPEND_ONLY:
            base = filtered_baseline(commit, p)
            row["prefix_size"] = len(base)
            row["prefix_sha256"] = sha256_bytes(base)
        rows.append(row)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size", "sha256", "blob_id",
                                          "append_only", "prefix_size", "prefix_sha256"])
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
    if not fp.exists():
        return False, "deleted"
    cur = fp.read_bytes()
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

    for p, rec in base.items():
        if int(rec["append_only"]):
            ok, why = check_prefix(p, int(rec["prefix_size"]), rec["prefix_sha256"])
            notes.append(f"{p}: {why}")
            if not ok:
                sha_bad.append((p, "prefix-test", why))
            continue

        fp = Path(p)
        if not fp.exists():
            if rec["sha256"] != "MISSING":
                deleted.append(p)
            continue

        cur_blob = now.get(p)
        if cur_blob is None:
            deleted.append(f"{p} (untracked now)")
        elif cur_blob != rec["blob_id"]:
            blob_bad.append((p, rec["blob_id"][:12], cur_blob[:12]))

        cur_sha = sha256_file(fp)
        if cur_sha != rec["sha256"]:
            if git_rc("diff", "--quiet", commit, "--", p) == 0:
                eol_artifacts.append(p)      # git sees no difference: representation only
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
        for p in eol_artifacts:
            blob_ok = now.get(p) == base[p]["blob_id"]
            rc = git_rc("diff", "--quiet", commit, "--", p)
            print(f"   {p}\n      blob matches baseline: {blob_ok}   "
                  f"git diff --quiet exit: {rc}")
    print(f"\nSHA256 CHANGED (real content)  : {len(sha_bad)}")
    for p, a, b in sha_bad[:25]:
        print(f"   {p}\n      was {a}  now {b}")
    print(f"BLOB ID CHANGED (git object)   : {len(blob_bad)}")
    for p, a, b in blob_bad[:25]:
        print(f"   {p}\n      was {a}  now {b}")
    print(f"DELETED / UNTRACKED            : {len(deleted)}")
    for p in deleted[:25]:
        print(f"   {p}")
    print(f"ADDED outside v4 allowlist     : {len(added_bad)}")
    for p in added_bad[:25]:
        print(f"   {p}")
    print(f"ADDED inside v4 allowlist (ok) : {len(added_ok)}")
    for p in added_ok[:25]:
        print(f"   {p}")

    fail = bool(sha_bad or blob_bad or deleted or added_bad)
    print("\nRESULT: " + ("FAIL - v3 baseline changed" if fail else "PASS - v3 baseline intact"))
    return 1 if fail else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true", help="write the manifest instead of verifying")
    a = ap.parse_args()
    sys.exit(create() if a.create else verify())
