"""
REBUILD V4 - STAGE 6: SHARED LOADER AND GUARDS FOR 220-229 / 232
=============================================================================
Every Essay 3 v4 script loads its event table through load_canonical() here,
and none of them reads Data/processed/rebuild_v4/CANONICAL_V4.csv directly.
That is enforced, not merely documented (see assert_no_direct_canonical_read).

WHY THE INDIRECTION EXISTS
--------------------------
CANONICAL_V4 still carries columns INHERITED from v3 that are NOT v4 results:

    has_crsp_data, permno     v3's link. v4's link lives in v4_212_links.csv.
                              Nokia is the tell: CANONICAL_V4 says
                              has_crsp_data=1, permno=87128, while v4 does not
                              link it at all.
    firm_size_log, leverage,  v3's ticker-joined Compustat covariates. v4's are
    roa, op_margin            gvkey-joined and refreshed by scripts/219
                              (coverage 346 -> 438).

Reading any of those would silently score the v3 sample while every label in
the output said v4. So load_canonical() DROPS them from the raw file and then
re-attaches the v4 values from their real sources. A script that wants
has_crsp_data gets v4's answer or nothing.

    linkage   outputs/rebuild_v4/v4_212_links.csv      permno, v4_linked
    covariates outputs/rebuild_v4/219_covariates_v4.csv
    filings   outputs/rebuild_v4/234_outcome_cik.csv   outcome_cik

OUTCOME CIK
-----------
final_cik is the EQUITY link; outcome_cik is the entity whose Form 8-Ks are
read. They diverge for 7 events (Disney, Google, Paramount x2, Sinclair x3).
Anything that opens a filing must use outcome_cik.

RESOLVE
-------
scripts/199 hard-coded a RESOLVE dict of outcome-CIK corrections. v4 reaches
those corrections by rule instead, and scripts/233 reconciles the two. Where
233 says 'agree', RESOLVE must NOT be re-applied - doing so corrects the same
event twice. require_resolve_settled() aborts on any 'disagree' or 'pending'
row, so a downstream script cannot run against an unsettled reconciliation.

Offline. No network, no WRDS.
"""
import sys
from pathlib import Path

import pandas as pd

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
COVAR = Path("outputs/rebuild_v4/219_covariates_v4.csv")
OUTCOME = Path("outputs/rebuild_v4/234_outcome_cik.csv")
RECON = Path("outputs/rebuild_v4/resolve_reconciliation.csv")

KEY = ["final_cik", "breach_date"]
# v3 values that must never reach a v4 result.
INHERITED = ("has_crsp_data", "permno", "permno_match",
             "firm_size_log", "leverage", "roa", "op_margin")
COVARS = ("firm_size_log", "leverage", "roa", "op_margin")


def abort(msg):
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p) + " (no graceful fallback)")
    return Path(p)


def _key(df):
    df = df.copy()
    df["breach_date"] = df["breach_date"].astype(str).str[:10]
    return df


def load_canonical(with_outcome=True):
    """CANONICAL_V4 with v3's inherited columns removed and v4's merged in."""
    ev = _key(pd.read_csv(require(CANON), low_memory=False))
    ev = ev.drop(columns=[c for c in INHERITED if c in ev.columns])

    lk = _key(pd.read_csv(require(LINKS), low_memory=False)).drop_duplicates(KEY)
    lk = lk.set_index(KEY)
    idx = ev.set_index(KEY).index
    linked = idx.map(lk["v4_linked"]) if "v4_linked" in lk.columns else None
    if linked is None:
        abort(str(LINKS) + " has no v4_linked column")
    ev["has_crsp_data"] = [0 if pd.isna(v) else int(v) for v in linked]
    perm = idx.map(lk["permno"]) if "permno" in lk.columns else None
    ev["permno"] = [float("nan") if (p is None or pd.isna(p)) else p for p in perm]
    # A permno that v4 did not actually link must not travel with the row.
    ev.loc[ev["has_crsp_data"] != 1, "permno"] = float("nan")

    cov = _key(pd.read_csv(require(COVAR), low_memory=False)).drop_duplicates(KEY)
    cov = cov.set_index(KEY)
    for c in COVARS:
        ev[c] = idx.map(cov[c]) if c in cov.columns else float("nan")

    if with_outcome:
        oc = _key(pd.read_csv(require(OUTCOME), low_memory=False)).drop_duplicates(KEY)
        oc = oc.set_index(KEY)
        ev["outcome_cik"] = idx.map(oc["outcome_cik"])
        ev["outcome_rule"] = idx.map(oc["outcome_rule"])
    return ev


def require_resolve_settled():
    """scripts/233 must show no 'disagree' and no 'pending' row. -> agreed keys."""
    r = pd.read_csv(require(RECON), low_memory=False)
    bad = r[r["verdict"].isin(["disagree", "pending"])]
    if len(bad):
        rows = "; ".join(str(x["resolve_cik"]) + " " + str(x["org_name"]) + " "
                         + str(x["breach_date"]) + " [" + str(x["verdict"]) + "]"
                         for _, x in bad.iterrows())
        abort("scripts/233 is unsettled - " + str(len(bad)) + " row(s) not 'agree': "
              + rows + ". Rule on each before running this script.")
    return {(x["v4_final_cik"], str(x["breach_date"])[:10])
            for _, x in r.iterrows() if str(x["verdict"]) == "agree"}


def assert_no_direct_canonical_read(path):
    """A v4 Essay 3 script must not open CANONICAL_V4 itself. -> list of offending lines.

    Structural, not stylistic: a direct read restores has_crsp_data and permno from
    v3 under their v4 names, and nothing downstream would look wrong.
    """
    import ast
    text = Path(path).read_text(encoding="utf-8", errors="replace")

    # Skip DOCSTRINGS precisely, via the parse tree - a prefix heuristic mistakes an
    # indented docstring line for code. Only docstrings are skipped, never all string
    # literals: the path in a real read lives inside a string literal too.
    skip = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                     ast.AsyncFunctionDef)):
                continue
            body = getattr(node, "body", None) or []
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                d = body[0]
                skip.update(range(d.lineno, (d.end_lineno or d.lineno) + 1))

    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if i in skip:
            continue
        if "CANONICAL_V4.csv" not in line and "CANONICAL_V3.csv" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        out.append((i, stripped))
    return out
