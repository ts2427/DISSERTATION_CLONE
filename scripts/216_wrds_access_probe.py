"""
REBUILD V4 — WRDS ACCESS PROBE (run locally by Tim; read-only)
=====================================================================================
Run 1 of scripts/211 died at step 2 with

    psycopg2.errors.InsufficientPrivilege: permission denied for schema crsp_a_ccm

i.e. the subscription does not reach the CRSP/Compustat Merged link tables by that
path. Before the Stage 2 linker rule is chosen, this probe establishes exactly what
IS reachable, so the choice rests on evidence rather than another failed pull.

    python scripts/216_wrds_access_probe.py

WHAT IT DOES
------------
1. db.list_libraries()  -- every library the account can see.
2. For each candidate table below, `select * from <table> limit 1`, recording OK with
   the column list, or the exact exception type and message.
3. Discovery: any library whose name contains "ccm", and within the CCM-ish and
   wrdsapps libraries, any table whose name contains link / ccm / cik / gvkey.

Candidates probed explicitly:
    crsp.ccmxpf_lnkhist, crsp.ccmxpf_linktable,
    comp.company, comp.security,
    crsp.stocknames, crsp.msenames, crsp.dsenames,
    crsp.dsf, crsp.dsi,
    wrdssec.wciklink_gvkey, wrdssec_midas.wciklink_gvkey

WHAT IT DOES NOT DO
-------------------
Writes NO data files. Only outputs/rebuild_v4/216_access_probe.md. Every query is
LIMIT 1 and no result is retained beyond its column names and row count, so nothing
licensed leaves WRDS. It does not change the Stage 2 rule, and it does not pull.

WHY BOTH ROUTES MATTER
----------------------
If any CCM link table is reachable, Stage 2 uses the gvkey->permno link with
linktype/linkprim/date validity, as specified. If none is, the fallback is the CUSIP
route: comp.security.cusip -> a CRSP names file (stocknames / msenames / dsenames)
with date validity. This probe decides which, and the report names which tables
support each.

CREDENTIALS
-----------
Handled by the `wrds` package against your local configuration. No password argument,
never printed, never written. Driver messages are scrubbed of password-shaped text
before they reach the report.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("outputs/rebuild_v4/216_access_probe.md")

EXPLICIT = [
    ("crsp.ccmxpf_lnkhist", "CCM link history (Stage 2 primary)"),
    ("crsp.ccmxpf_linktable", "CCM link table (alternate name)"),
    ("comp.company", "Compustat company header (CIK -> gvkey)"),
    ("comp.security", "Compustat security (gvkey -> cusip; CUSIP-route source)"),
    ("crsp.stocknames", "CRSP names, permno/cusip/ticker with date validity"),
    ("crsp.msenames", "CRSP monthly names (CUSIP-route fallback)"),
    ("crsp.dsenames", "CRSP daily names (CUSIP-route fallback)"),
    ("crsp.dsf", "CRSP daily stock file"),
    ("crsp.dsi", "CRSP daily market index"),
    ("wrdssec.wciklink_gvkey", "SEC Analytics CIK-GVKEY link"),
    ("wrdssec_midas.wciklink_gvkey", "SEC Analytics CIK-GVKEY link (midas)"),
]

NAME_HINTS = ("link", "ccm", "cik", "gvkey")

LOG = []


def log(msg=""):
    print(msg, flush=True)
    LOG.append(str(msg))


def scrub(text):
    t = str(text)
    t = re.sub(r"(?i)\b(password|pwd|passwd)\s*=\s*\S+", r"\1=***REDACTED***", t)
    return t


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    return f"WROTE {OUT}"


def is_ccm_link(table):
    """True only for a CRSP/Compustat Merged gvkey -> permno link table.

    The first version of this probe tested `"ccm" in t or "lnk" in t or "link" in t`
    and reported "a link table IS reachable" on the strength of
    wrdsapps.bondcrsp_link, compeushortlink, fscrsplink, tclink and
    uspatents_gvkey_linking. None of those maps gvkey to permno: they are a bond-CRSP
    bridge, a European short-interest link, a FactSet-CRSP link, a TAQ-CRSP link and a
    patent-gvkey link respectively. A substring match on "link" is not a test of what
    a table links.

    The CCM family is identified structurally instead: the bare table name begins with
    `ccmxpf_` (ccmxpf_lnkhist, ccmxpf_linktable, ccmxpf_lnkused), or the library itself
    is CCM-family and the table name carries lnk/link.
    """
    lib, _, name = table.lower().rpartition(".")
    if name.startswith("ccmxpf_"):
        return True
    lib_is_ccm = "ccm" in lib
    return lib_is_ccm and ("lnk" in name or "link" in name)


def probe(db, table):
    """LIMIT 1 against one table. Returns (ok, detail)."""
    try:
        df = db.raw_sql(f"select * from {table} limit 1")
        cols = list(df.columns)
        return True, f"{len(cols)} cols, {len(df)} row: {', '.join(cols[:14])}" + \
                     ("..." if len(cols) > 14 else "")
    except BaseException as e:
        return False, f"{type(e).__name__}: {scrub(e).splitlines()[0][:180]}"


def main():
    try:
        import wrds
    except ImportError:
        sys.exit("The `wrds` package is not installed. pip install wrds")

    started = datetime.now(timezone.utc)
    log("# REBUILD V4 — WRDS access probe")
    log("")
    log(f"- run (UTC): {started.isoformat(timespec='seconds')}")
    log("- read-only: every query is LIMIT 1; no data file is written")
    log("")

    try:
        db = wrds.Connection()
    except BaseException as e:
        log(f"**WRDS connection failed: {type(e).__name__}: {scrub(e)}**")
        print(flush())
        sys.exit(1)

    try:
        user = (getattr(db, "_username", None) or getattr(db, "username", None)
                or "(not reported)")
        log(f"- WRDS username: {user}")
        log("")

        # ---- 1. libraries -------------------------------------------------
        log("## 1. Libraries visible to this account")
        log("")
        libs = []
        try:
            libs = sorted(db.list_libraries())
            log(f"{len(libs)} libraries.")
            log("")
            log("```")
            for i in range(0, len(libs), 6):
                log("  " + "  ".join(f"{x:<22}" for x in libs[i:i + 6]).rstrip())
            log("```")
        except BaseException as e:
            log(f"**list_libraries() failed: {type(e).__name__}: {scrub(e)}**")
        log("")
        ccm_libs = [x for x in libs if "ccm" in x.lower()]
        log(f"- libraries with 'ccm' in the name: {ccm_libs or 'none'}")
        log("")

        # ---- 2. explicit candidates ---------------------------------------
        log("## 2. Candidate tables (SELECT * LIMIT 1)")
        log("")
        log("| table | purpose | result | detail |")
        log("|---|---|---|---|")
        reachable, blocked = [], []
        for table, purpose in EXPLICIT:
            ok, detail = probe(db, table)
            (reachable if ok else blocked).append(table)
            log(f"| `{table}` | {purpose} | {'OK' if ok else 'FAIL'} | {detail} |")
        log("")

        # ---- 3. discovery --------------------------------------------------
        log("## 3. Discovered tables matching link / ccm / cik / gvkey")
        log("")
        search_libs = sorted(set(ccm_libs + [x for x in libs if x.lower() in
                                             ("wrdsapps", "wrdssec", "wrdssec_midas",
                                              "crsp", "comp")]))
        found = []
        for lib in search_libs:
            try:
                tables = sorted(db.list_tables(library=lib))
            except BaseException as e:
                log(f"- `{lib}`: list_tables failed ({type(e).__name__}: "
                    f"{scrub(e).splitlines()[0][:110]})")
                continue
            hits = [t for t in tables if any(h in t.lower() for h in NAME_HINTS)]
            if hits:
                log(f"- `{lib}`: {len(hits)} of {len(tables)} tables match -> "
                    + ", ".join(f"`{t}`" for t in hits[:25])
                    + (" ..." if len(hits) > 25 else ""))
                found += [f"{lib}.{t}" for t in hits]
        log("")
        if found:
            log("### Probing the discovered tables")
            log("")
            log("| table | result | detail |")
            log("|---|---|---|")
            for t in found:
                if t in dict(EXPLICIT):
                    continue
                ok, detail = probe(db, t)
                (reachable if ok else blocked).append(t)
                log(f"| `{t}` | {'OK' if ok else 'FAIL'} | {detail} |")
            log("")

        # ---- 4. verdict ----------------------------------------------------
        log("## 4. Verdict for the Stage 2 rule")
        log("")
        ccm_ok = [t for t in reachable if is_ccm_link(t)]
        log(f"- reachable tables: {len(reachable)}")
        log(f"- blocked tables  : {len(blocked)}")
        log("")
        other_links = [t for t in reachable
                       if not is_ccm_link(t)
                       and any(h in t.lower() for h in ("link", "lnk"))]
        if other_links:
            log(f"- reachable tables whose NAME contains link/lnk but which are NOT "
                f"gvkey->permno links, and so do not qualify: "
                f"{', '.join(f'`{t}`' for t in other_links)}")
            log("")
        if ccm_ok:
            log(f"**A CCM link table IS reachable:** {', '.join(f'`{t}`' for t in ccm_ok)}")
            log("Stage 2 can use the gvkey -> permno link with linktype/linkprim and "
                "date validity, as originally specified.")
        else:
            log("**No CCM/link table is reachable.** Stage 2 must fall back to the CUSIP "
                "route: comp.security.cusip -> a CRSP names file with date validity.")
            names_ok = [t for t in reachable
                        if t in ("crsp.stocknames", "crsp.msenames", "crsp.dsenames")]
            sec_ok = "comp.security" in reachable
            names_txt = ", ".join(names_ok) if names_ok else \
                "NONE - the CUSIP route is also blocked"
            log(f"- comp.security reachable: {sec_ok}")
            log(f"- CRSP names files reachable: {names_txt}")
            if not sec_ok or not names_ok:
                log("")
                log("**Both routes are blocked.** Stage 2 cannot proceed on this "
                    "subscription; the entitlement question goes back to WRDS support "
                    "before any further pull is attempted.")
        log("")
        log("Do not change the Stage 2 rule from this file alone; return it and the "
            "choice is made jointly.")
    finally:
        try:
            db.close()
        except Exception:
            pass

    log("")
    log(f"- finished (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(flush())
    return 0


if __name__ == "__main__":
    sys.exit(main())
