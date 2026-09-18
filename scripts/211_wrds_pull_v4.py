"""
REBUILD V4 — STAGE 1: WRDS PULL (run locally by Tim; never run in the sandbox)
=====================================================================================
Pulls the point-in-time Compustat/CRSP link tables and daily returns needed by the
Stage 2 linker (scripts/212). Every pull is FILTERED — by the CIK list, then by the
gvkeys those CIKs reach, then by the permnos those gvkeys reach. No table is pulled
whole. That is the amended Stage 1 spec and it cuts the payload from ~64-146 MB to
~33-53 MB.

    python scripts/211_wrds_pull_v4.py

CREDENTIALS
-----------
Handled entirely by the `wrds` package against your local configuration. This script
never accepts a password argument, never prints one, never writes one to disk, and
never records one in the log. It logs only the username the connection reports.
If wrds offers to create a ~/.pgpass file, that is your local decision; nothing here
creates, reads, or copies it.

INPUTS (read-only)
------------------
    Data/processed/rebuild/CANONICAL_V3.csv            final_cik  (489 events)
    outputs/essay3_q2/crsp_drop_nominations.csv        parent_cik (nominated parents)

OUTPUTS (all new paths; Data/wrds_v4/** is LFS-tracked by .gitattributes)
-------------------------------------------------------------------------
    Data/wrds_v4/comp_company.csv          gvkey, conm, cik, + available date/status
    Data/wrds_v4/ccmxpf_lnkhist.csv        gvkey, lpermno, lpermco, linktype,
                                           linkprim, linkdt, linkenddt
    Data/wrds_v4/sec_cik_gvkey.csv         SEC Analytics link table, IF subscribed
    Data/wrds_v4/crsp_stocknames.csv       permno, namedt, nameenddt, ticker, comnam,
                                           shrcd, exchcd
    Data/wrds_v4/crsp_dsf.csv              permno, date, ret, retx, prc, vol, shrout
    Data/wrds_v4/crsp_dsi.csv              date, vwretd, ewretd
    outputs/rebuild_v4/211_pull_log.md     timestamp, username, row counts, date
                                           ranges, sha256 of every file

WHY THE ORDER MATTERS
---------------------
1  cik  -> gvkey   comp.company.cik is a zero-padded 10-character string, not an int.
2  gvkey-> permno  ccmxpf_lnkhist, unfiltered by linktype here on purpose: Stage 2
                   applies the linktype/linkprim/date rules. Pulling every link row
                   for our gvkeys keeps that decision auditable in scripts/212
                   rather than silently pre-filtering it here.
3  permno-> names  crsp.stocknames for exactly those permnos.
4  permno-> daily  crsp.dsf for exactly those permnos, 2005-01-01 onward.

RECORD THE CRSP END DATE. If max(dsf.date) extends past 2024-12-31, events the v3
chain lost as "past-extract" (National Presto 2025-03-01, iHeartMedia 2025-04-30, and
the five fallback-prior 2025 cases) may re-enter. The Stage 5 ledger must show this.

This script is READ-ONLY with respect to every v3 path. It writes only under
Data/wrds_v4/ and outputs/rebuild_v4/.
"""
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT_DATA = Path("Data/wrds_v4")
OUT_LOG = Path("outputs/rebuild_v4/211_pull_log.md")
START_DATE = "2005-01-01"
CHUNK = 500                      # keep IN-lists well inside server limits

CANON = Path("Data/processed/rebuild/CANONICAL_V3.csv")
NOMS = Path("outputs/essay3_q2/crsp_drop_nominations.csv")

LOG = []


def log(msg=""):
    print(msg, flush=True)
    LOG.append(str(msg))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def chunked(seq, n=CHUNK):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def quote_list(vals):
    """SQL literal list of strings, single quotes doubled."""
    return ", ".join("'" + str(v).replace("'", "''") + "'" for v in vals)


def int_list(vals):
    return ", ".join(str(int(v)) for v in vals)


def fetch_chunked(db, sql_template, values, formatter):
    """Run sql_template once per chunk of values and concatenate."""
    frames = []
    for part in chunked(values):
        frames.append(db.raw_sql(sql_template.format(values=formatter(part))))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates()


def write(df, name):
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    p = OUT_DATA / name
    df.to_csv(p, index=False)
    sha = sha256_file(p)
    size = p.stat().st_size
    log(f"  wrote {p}  rows={len(df):,}  {size/1e6:,.1f} MB  sha256={sha}")
    return dict(path=str(p), rows=len(df), bytes=size, sha256=sha)


def date_range(df, col="date"):
    if col not in df.columns or df.empty:
        return "n/a"
    s = pd.to_datetime(df[col], errors="coerce")
    return f"{s.min().date()} .. {s.max().date()}"


def main():
    try:
        import wrds
    except ImportError:
        sys.exit("The `wrds` package is not installed. pip install wrds")

    # ---- CIK list -------------------------------------------------------------
    if not CANON.exists():
        sys.exit(f"missing input: {CANON}")
    ciks = set(int(c) for c in pd.read_csv(CANON, low_memory=False)["final_cik"].dropna())
    n_canon = len(ciks)
    n_nom = 0
    if NOMS.exists():
        pc = pd.to_numeric(pd.read_csv(NOMS)["parent_cik"], errors="coerce").dropna()
        nom = set(int(c) for c in pc)
        n_nom = len(nom - ciks)
        ciks |= nom
    ciks = sorted(ciks)
    cik10 = [f"{c:010d}" for c in ciks]

    started = datetime.now(timezone.utc)
    log("# REBUILD V4 — Stage 1 WRDS pull log")
    log("")
    log(f"- pull started (UTC): {started.isoformat(timespec='seconds')}")
    log(f"- CIK filter list: {len(ciks)} CIKs "
        f"({n_canon} from CANONICAL_V3, +{n_nom} nominated parents not already present)")
    log(f"- daily data from: {START_DATE}")
    log("")

    db = wrds.Connection()                      # credentials via local wrds config/prompt
    try:
        user = getattr(db, "_username", None) or getattr(db, "username", None) or "(not reported)"
        log(f"- WRDS username: {user}   (no password is stored, printed, or logged)")
        log("")
        files = []

        # ---- 1. comp.company, filtered by CIK ---------------------------------
        log("## 1. comp.company (filtered by CIK)")
        comp = fetch_chunked(
            db,
            "select * from comp.company where cik in ({values})",
            cik10, quote_list)
        if comp.empty:
            log("  WARNING: no comp.company rows matched the CIK list")
        gvkeys = sorted(set(comp["gvkey"].dropna())) if "gvkey" in comp.columns else []
        log(f"  CIKs matched: {comp['cik'].nunique() if 'cik' in comp.columns else 0} "
            f"of {len(ciks)}   gvkeys reached: {len(gvkeys)}")
        files.append(write(comp, "comp_company.csv"))

        # ---- 2. ccmxpf_lnkhist, filtered by gvkey -----------------------------
        log("\n## 2. crsp.ccmxpf_lnkhist (filtered by gvkey)")
        lnk = fetch_chunked(
            db,
            "select gvkey, lpermno, lpermco, linktype, linkprim, linkdt, linkenddt "
            "from crsp.ccmxpf_lnkhist where gvkey in ({values})",
            gvkeys, quote_list) if gvkeys else pd.DataFrame()
        log(f"  link rows: {len(lnk):,}   linktypes: "
            f"{sorted(lnk['linktype'].dropna().unique()) if not lnk.empty else []}")
        files.append(write(lnk, "ccmxpf_lnkhist.csv"))

        permnos = sorted({int(p) for p in lnk["lpermno"].dropna()}) if not lnk.empty else []
        log(f"  permnos reached via CCM: {len(permnos)}")

        # ---- 3. SEC Analytics CIK-GVKEY link, if subscribed -------------------
        log("\n## 3. SEC Analytics CIK-GVKEY link (optional)")
        sec = pd.DataFrame()
        for table in ("wrdssec.wciklink_gvkey", "wrdssec_midas.wciklink_gvkey"):
            try:
                sec = fetch_chunked(
                    db,
                    f"select * from {table} where cik in ({{values}})",
                    cik10, quote_list)
                log(f"  pulled from {table}: {len(sec):,} rows")
                break
            except Exception as e:
                log(f"  {table} unavailable ({type(e).__name__}: {str(e)[:90]})")
        if sec.empty:
            log("  no SEC Analytics link table available; continuing (Stage 2 falls back to CCM only)")
        files.append(write(sec, "sec_cik_gvkey.csv"))
        if not sec.empty and "gvkey" in sec.columns:
            extra = sorted(set(sec["gvkey"].dropna()) - set(gvkeys))
            if extra:
                log(f"  NOTE {len(extra)} gvkeys appear only in the SEC link table")

        # ---- 4. crsp.stocknames, filtered by permno ---------------------------
        log("\n## 4. crsp.stocknames (filtered by permno)")
        names = fetch_chunked(
            db,
            "select permno, namedt, nameenddt, ticker, comnam, shrcd, exchcd "
            "from crsp.stocknames where permno in ({values})",
            permnos, int_list) if permnos else pd.DataFrame()
        log(f"  name rows: {len(names):,}   distinct permnos: "
            f"{names['permno'].nunique() if not names.empty else 0}")
        files.append(write(names, "crsp_stocknames.csv"))

        # ---- 5. crsp.dsf, filtered by permno ----------------------------------
        log("\n## 5. crsp.dsf (filtered by permno; the dominant payload)")
        dsf = fetch_chunked(
            db,
            "select permno, date, ret, retx, prc, vol, shrout from crsp.dsf "
            f"where date >= '{START_DATE}' and permno in ({{values}})",
            permnos, int_list) if permnos else pd.DataFrame()
        log(f"  daily rows: {len(dsf):,}   permnos: "
            f"{dsf['permno'].nunique() if not dsf.empty else 0}   range: {date_range(dsf)}")
        files.append(write(dsf, "crsp_dsf.csv"))

        # ---- 6. crsp.dsi ------------------------------------------------------
        log("\n## 6. crsp.dsi (market index, date range only)")
        dsi = db.raw_sql(
            f"select date, vwretd, ewretd from crsp.dsi where date >= '{START_DATE}'")
        log(f"  index rows: {len(dsi):,}   range: {date_range(dsi)}")
        files.append(write(dsi, "crsp_dsi.csv"))

        # ---- CRSP end date ----------------------------------------------------
        log("\n## CRSP coverage end date")
        end = None
        if not dsf.empty:
            end = pd.to_datetime(dsf["date"], errors="coerce").max()
        log(f"- max(crsp.dsf.date) = {end.date() if end is not None else 'n/a'}")
        log("- v3 committed extract ended 2024-12-31")
        if end is not None and end.date() > pd.Timestamp("2024-12-31").date():
            log(f"- **EXTENDS PAST v3 by {(end - pd.Timestamp('2024-12-31')).days} days.** "
                "Events lost to \"past-extract\" may re-enter; the Stage 5 ledger must show this.")
        else:
            log("- does not extend past v3; the past-extract exclusions stand")

        # ---- summary ----------------------------------------------------------
        total = sum(f["bytes"] for f in files)
        log("\n## Files written")
        log("")
        log("| file | rows | MB | sha256 |")
        log("|---|---:|---:|---|")
        for f in files:
            log(f"| `{f['path']}` | {f['rows']:,} | {f['bytes']/1e6:,.1f} | `{f['sha256']}` |")
        log("")
        log(f"- total written: {total/1e6:,.1f} MB "
            f"(Stage 0 estimate was 33-53 MB; LFS budget 3.4/10 GB used)")
        log(f"- pull finished (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    finally:
        try:
            db.close()
        except Exception:
            pass

    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOG.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nWROTE {OUT_LOG}")
    print("Next: return the log. Do not run scripts/212 until Stage 1 is reviewed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
