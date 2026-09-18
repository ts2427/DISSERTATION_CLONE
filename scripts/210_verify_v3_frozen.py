"""
REBUILD V4 — STAGE 0: V3 FREEZE CHECK
=====================================================================================
Proves that nothing in the v3 baseline changed while v4 work proceeds on branch
rebuild-v4.

Scope (tracked files only, via `git ls-files`):
    Data/**, outputs/** (excluding outputs/rebuild_v4/ and outputs/essay3_v4/),
    scripts/**, docs/**, plus run_all.py and .gitattributes.

Usage:
    python scripts/210_verify_v3_frozen.py --create   # write the manifest (once)
    python scripts/210_verify_v3_frozen.py            # verify; nonzero exit on drift

Manifest: outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv  (path, size, sha256)

VERDICT RULES
-------------
FAIL  a manifest file whose sha256 changed
FAIL  a manifest file that is gone
FAIL  a newly tracked file OUTSIDE the v4 allowlist  (an addition to v3 territory)
PASS  a newly tracked file INSIDE the v4 allowlist
PASS  .gitattributes grown by appending only — the manifest-era bytes must still be
      an exact prefix of the current file (checked byte-wise, not by hash alone)

DESIGN NOTE (flagged for Tim, Stage 0 report)
---------------------------------------------
The directive says "the only permitted difference is appended lines in
.gitattributes; exit nonzero on any other difference." Read literally that makes the
check fail from Stage 1 onward, because Stages 1-6 add scripts 211-229 and new output
trees -- which would contradict "every stage ends with the freeze check passing."
This implementation therefore treats ADDITIONS inside the v4 allowlist as permitted
and everything else (modification, deletion, addition outside the allowlist) as a
failure. That enforces "v3 does not change" without blocking v4. Confirm or override.

Hashing note: files are hashed AS THEY EXIST ON DISK, not as stored in the index.
Several tracked paths are Git-LFS pointers in the index but real content in the
working tree (the missing filter=lfs rule on 87 files, plus
Data/enrichment/regulatory_enforcement.csv). On-disk hashing is the stable choice:
it answers "did the bytes a script would read change?", which is what the freeze is for.
"""
import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv")

# Tracked paths in scope for the freeze.
INCLUDE_DIRS = ("Data/", "outputs/", "scripts/", "docs/")
INCLUDE_FILES = ("run_all.py", ".gitattributes")
EXCLUDE_PREFIXES = ("outputs/rebuild_v4/", "outputs/essay3_v4/")

# New tracked files are permitted only under these prefixes (v4 work).
V4_ALLOW = (
    "scripts/21", "scripts/22",                 # scripts 210-229
    "Data/wrds_v4/",
    "Data/processed/rebuild_v4/",
    "Data/edgar/ex21_cache_v4/",
    "outputs/rebuild_v4/",
    "outputs/essay3_v4/",
    "docs/claude/REBUILD_V4_QUERY.md",
    "docs/claude/REPRODUCE_ESSAY3_V4.md",
)

GITATTRIBUTES = ".gitattributes"


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def in_scope(p):
    if any(p.startswith(x) for x in EXCLUDE_PREFIXES):
        return False
    return p.startswith(INCLUDE_DIRS) or p in INCLUDE_FILES


def tracked_files():
    return sorted(p for p in git("ls-files").splitlines() if p and in_scope(p))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot():
    rows = []
    for p in tracked_files():
        fp = Path(p)
        if not fp.exists():          # tracked but absent from the working tree
            rows.append({"path": p, "size": -1, "sha256": "MISSING"})
            continue
        rows.append({"path": p, "size": fp.stat().st_size, "sha256": sha256(fp)})
    return rows


def create():
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    rows = snapshot()
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size", "sha256"])
        w.writeheader()
        w.writerows(rows)
    total = sum(r["size"] for r in rows if r["size"] > 0)
    print(f"WROTE {MANIFEST}")
    print(f"  files hashed : {len(rows):,}")
    print(f"  total bytes  : {total:,} ({total/1e6:,.1f} MB)")
    print(f"  manifest sha : {sha256(MANIFEST)}")
    missing = [r['path'] for r in rows if r['sha256'] == 'MISSING']
    if missing:
        print(f"  NOTE tracked-but-absent on disk: {len(missing)} -> {missing[:5]}")
    return 0


def gitattributes_append_only(old_size, old_sha):
    """True iff the manifest-era bytes are still an exact prefix of the file."""
    p = Path(GITATTRIBUTES)
    if not p.exists():
        return False, "deleted"
    cur = p.read_bytes()
    if len(cur) < old_size:
        return False, f"shrank ({len(cur)} < {old_size} bytes)"
    prefix = cur[:old_size]
    if hashlib.sha256(prefix).hexdigest() != old_sha:
        return False, "manifest-era bytes were modified, not merely appended to"
    added = len(cur) - old_size
    return True, f"append-only (+{added} bytes)"


def verify():
    if not MANIFEST.exists():
        sys.exit(f"FAIL: manifest not found at {MANIFEST}. Run with --create first.")
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        base = {r["path"]: r for r in csv.DictReader(f)}

    modified, deleted, added_ok, added_bad, notes = [], [], [], [], []

    for p, rec in base.items():
        fp = Path(p)
        if not fp.exists():
            if rec["sha256"] == "MISSING":
                continue                      # absent then, absent now
            deleted.append(p)
            continue
        cur = sha256(fp)
        if cur == rec["sha256"]:
            continue
        if p == GITATTRIBUTES:
            ok, why = gitattributes_append_only(int(rec["size"]), rec["sha256"])
            notes.append(f".gitattributes: {why}")
            if ok:
                continue
        modified.append((p, rec["sha256"][:12], cur[:12]))

    for p in tracked_files():
        if p in base:
            continue
        (added_ok if p.startswith(V4_ALLOW) else added_bad).append(p)

    print("=" * 78)
    print("V3 FREEZE CHECK — scripts/210")
    print("=" * 78)
    print(f"manifest        : {MANIFEST} ({len(base):,} files)")
    print(f"tracked in scope: {len(tracked_files()):,}")
    for n in notes:
        print(f"note            : {n}")
    print(f"\nMODIFIED (v3 changed)          : {len(modified)}")
    for p, a, b in modified[:25]:
        print(f"   {p}\n      manifest {a}  now {b}")
    print(f"DELETED  (v3 file gone)        : {len(deleted)}")
    for p in deleted[:25]:
        print(f"   {p}")
    print(f"ADDED outside v4 allowlist     : {len(added_bad)}")
    for p in added_bad[:25]:
        print(f"   {p}")
    print(f"ADDED inside v4 allowlist (ok) : {len(added_ok)}")
    for p in added_ok[:25]:
        print(f"   {p}")

    fail = bool(modified or deleted or added_bad)
    print("\nRESULT: " + ("FAIL — v3 baseline changed" if fail else "PASS — v3 baseline intact"))
    return 1 if fail else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true", help="write the manifest instead of verifying")
    a = ap.parse_args()
    sys.exit(create() if a.create else verify())
