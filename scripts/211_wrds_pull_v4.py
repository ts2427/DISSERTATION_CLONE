"""
REBUILD V4 — STAGE 1: WRDS PULL (run locally by Tim; never run in the sandbox)
=====================================================================================
Pulls the point-in-time Compustat/CRSP link tables and daily returns needed by the
Stage 2 linker (scripts/212). Every pull is FILTERED — by the CIK list, then by the
gvkeys those CIKs reach, then by the permnos those gvkeys reach. No table is pulled
whole.

    python scripts/211_wrds_pull_v4.py                       # first pull
    python scripts/211_wrds_pull_v4.py --extra-ciks FILE     # later top-up

FAILS LOUDLY
------------
A silent partial pull is the worst outcome here: Stage 2 would link a subset and the
v3-to-v4 comparison would read as "events lost" when the truth is "rows never
arrived." So every step asserts before continuing, and any failure writes the log and
aborts with a nonzero exit:

  comp.company      hit rate (CIKs matched / CIKs requested) must be >= 50%;
                    the sentinel CIKs below must each return a gvkey;
                    empty result aborts
  ccmxpf_lnkhist    empty result aborts; gvkey and permno reach reported
  crsp.stocknames   empty result aborts; permno reach reported
  crsp.dsf          empty result aborts; permno reach reported
  crsp.dsi          empty result aborts (Stage 2's market adjustment depends on it)

Every hit rate is written to 211_pull_log.md, pass or fail.

CIK LITERAL FORM
----------------
comp.company.cik is a character column. This script tries the zero-padded 10-character
form first (Compustat's stored form) and, if that matches nothing at all, retries
unpadded. The form that worked is logged. A wrong guess here would look exactly like
"these firms are not in Compustat," which is why it retries rather than assumes.

SENTINELS
---------
1283699 T-Mobile, 732717 AT&T, 101830 Sprint. All three are large listed registrants
present in CANONICAL_V3 and known to have CRSP securities. If any returns no gvkey,
the join key or the CIK form is wrong and the pull aborts rather than producing a
plausible-looking subset. Skipped in top-up mode, where the CIK list is arbitrary.

TOP-UP MODE (--extra-ciks)
--------------------------
For Stage 3, once Exhibit 21 verifies additional parent CIKs. FILE is one CIK per
line, or a CSV carrying a cik / final_cik / parent_cik / outcome_cik column. A top-up
pulls ONLY those CIKs and writes files suffixed `_topup_<UTC stamp>`; write() refuses
to clobber an existing path, and the log gains a new section rather than being
replaced. Stage 2 reads the first pull plus any top-ups as a set.

CREDENTIALS
-----------
Handled entirely by the `wrds` package against your local configuration. This script
never accepts a password argument, never prints one, never writes one to disk, and
never records one in the log. It logs only the username the connection reports.

INPUTS (read-only)
------------------
    Data/processed/rebuild/CANONICAL_V3.csv            final_cik  (489 events)
    outputs/essay3_q2/crsp_drop_nominations.csv        parent_cik (nominated parents)

OUTPUTS
-------
    Data/wrds_v4/comp_company.csv          gvkey, conm, cik, + available date/status
    Data/wrds_v4/ccmxpf_lnkhist.csv        gvkey, lpermno, lpermco, linktype,
                                           linkprim, linkdt, linkenddt
    Data/wrds_v4/sec_cik_gvkey.csv         SEC Analytics link table, IF subscribed
    Data/wrds_v4/crsp_stocknames.csv       permno, namedt, nameenddt, ticker, comnam,
                                           shrcd, exchcd
    Data/wrds_v4/crsp_dsf.csv              permno, date, ret, retx, prc, vol, shrout
    Data/wrds_v4/crsp_dsi.csv              date, vwretd, ewretd
    outputs/rebuild_v4/211_pull_log.md     timestamp, username, row counts, hit rates,
                                           date ranges, sha256 of every file

linktype/linkprim are deliberately NOT filtered in the pull. Stage 2 applies the LU/LC
and P/C rules, so pulling every link row for our gvkeys keeps that decision auditable
in scripts/212 rather than silently pre-filtering it here.

RECORD THE CRSP END DATE. If max(dsf.date) extends past 2024-12-31, events the v3 chain
lost as "past-extract" may re-enter; the Stage 5 ledger reports those separately from
events recovered by relinking.

READ-ONLY with respect to every v3 path. Writes only under Data/wrds_v4/ and
outputs/rebuild_v4/.
"""
import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT_DATA = Path("Data/wrds_v4")
OUT_LOG = Path("outputs/rebuild_v4/211_pull_log.md")
START_DATE = "2005-01-01"
CHUNK = 500

CANON = Path("Data/processed/rebuild/CANONICAL_V3.csv")
NOMS = Path("outputs/essay3_q2/crsp_drop_nominations.csv")

SENTINEL_CIKS = {1283699: "T-Mobile", 732717: "AT&T", 101830: "Sprint"}
MIN_HIT_RATE = 0.50

# Module state. SUFFIX/TOPUP are set once by main(); tests set them directly.
LOG = []
HIT_RATES = []
SUFFIX = ""
TOPUP = False


def reset_state(suffix="", topup=False):
    """Used by main() and by the offline tests so each run starts clean."""
    global LOG, HIT_RATES, SUFFIX, TOPUP
    LOG, HIT_RATES, SUFFIX, TOPUP = [], [], suffix, topup


def log(msg=""):
    print(msg, flush=True)
    LOG.append(str(msg))


def flush_log():
    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(LOG) + "\n"
    if TOPUP and OUT_LOG.exists():
        with open(OUT_LOG, "a", encoding="utf-8") as f:
            f.write(body)
        return f"APPENDED top-up section to {OUT_LOG}"
    OUT_LOG.write_text(body, encoding="utf-8")
    return f"WROTE {OUT_LOG}"


def hit_rate_table():
    if not HIT_RATES:
        return
    log("")
    log("## Hit rates")
    log("")
    log("| step | reached | requested | rate |")
    log("|---|---:|---:|---:|")
    for label, got, want, rate in HIT_RATES:
        log(f"| {label} | {got:,} | {want:,} | {100 * rate:.1f}% |")


def scrub(text):
    """Never let a credential reach the log.

    A driver-level exception can carry the connection string, and psycopg2 messages
    are pasted verbatim into the abort record. Redact anything password-shaped before
    it is written.
    """
    t = str(text)
    t = re.sub(r"(?i)\b(password|pwd|passwd)\s*=\s*\S+", r"\1=***REDACTED***", t)
    return t


def abort(msg):
    msg = scrub(msg)
    log("")
    log("## ABORTED")
    log("")
    log(f"**{msg}**")
    log("")
    log("No further pulls were attempted. Nothing downstream should read this pull.")
    hit_rate_table()
    print(flush_log())
    sys.exit(f"ABORT: {msg}")


def safe_run_pull(db, ciks):
    """run_pull, but ANY exception becomes an abort() so the log is always written.

    Run 1 (2026-10) failed here: psycopg2 raised InsufficientPrivilege on
    crsp.ccmxpf_lnkhist and the traceback bypassed abort() entirely, so no log was
    produced and the only evidence was a half-written comp_company.csv. Anticipated
    conditions are not the only way a pull dies.
    """
    try:
        return run_pull(db, ciks)
    except SystemExit:
        raise                      # abort() already flushed the log
    except BaseException as e:
        abort(f"unhandled {type(e).__name__} during the pull: {scrub(e)}")


def require_nonempty(df, label):
    if df is None or len(df) == 0:
        abort(f"{label} returned no rows")


def check_hit_rate(label, got, want, minimum=None):
    rate = (got / want) if want else 0.0
    HIT_RATES.append((label, got, want, rate))
    log(f"  {label}: {got:,} / {want:,} = {100 * rate:.1f}%")
    if minimum is not None and rate < minimum:
        abort(f"{label} hit rate {100 * rate:.1f}% is below the "
              f"{100 * minimum:.0f}% floor ({got} of {want})")
    return rate


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
    return ", ".join("'" + str(v).replace("'", "''") + "'" for v in vals)


def int_list(vals):
    return ", ".join(str(int(v)) for v in vals)


def fetch_chunked(db, sql_template, values, formatter):
    frames = []
    for part in chunked(values):
        frames.append(db.raw_sql(sql_template.format(values=formatter(part))))
    frames = [f for f in frames if f is not None and len(f)]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates()


def write(df, name):
    """Write to OUT_DATA/<stem><SUFFIX><ext>; never clobber."""
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    p = OUT_DATA / f"{Path(name).stem}{SUFFIX}{Path(name).suffix}"
    if p.exists():
        abort(f"refusing to overwrite an existing file: {p}")
    df.to_csv(p, index=False)
    sha, size = sha256_file(p), p.stat().st_size
    log(f"  wrote {p}  rows={len(df):,}  {size/1e6:,.1f} MB  sha256={sha}")
    return dict(path=str(p), rows=len(df), bytes=size, sha256=sha)


def date_range(df, col="date"):
    if col not in getattr(df, "columns", []) or len(df) == 0:
        return "n/a"
    s = pd.to_datetime(df[col], errors="coerce")
    return f"{s.min().date()} .. {s.max().date()}"


def read_extra_ciks(path):
    p = Path(path)
    if not p.exists():
        sys.exit(f"--extra-ciks file not found: {p}")
    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p)
        for col in ("cik", "final_cik", "parent_cik", "outcome_cik"):
            if col in df.columns:
                return {int(c) for c in pd.to_numeric(df[col], errors="coerce").dropna()}
        sys.exit(f"--extra-ciks CSV has no cik/final_cik/parent_cik/outcome_cik column: {p}")
    out = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(int(line))
    return out


def fetch_company(db, ciks):
    """comp.company filtered by CIK. Zero-padded form first, then unpadded."""
    sql = "select * from comp.company where cik in ({values})"
    df = fetch_chunked(db, sql, [f"{c:010d}" for c in ciks], quote_list)
    form = "zero-padded 10-char"
    if len(df) == 0:
        log("  zero-padded CIK form matched nothing - retrying unpadded")
        df = fetch_chunked(db, sql, [str(c) for c in ciks], quote_list)
        form = "unpadded"
    log(f"  CIK literal form that matched: {form}")
    return df, form


def run_pull(db, ciks):
    """The six filtered pulls, with assertions. Takes an open db so tests can mock it."""
    files = []

    # ---- 1. comp.company --------------------------------------------------
    log("## 1. comp.company (filtered by CIK)")
    comp, cik_form = fetch_company(db, ciks)
    require_nonempty(comp, "comp.company")
    log(f"  CIK literal form recorded: {cik_form}")
    comp = comp.copy()
    comp["_cik_int"] = pd.to_numeric(comp.get("cik"), errors="coerce")
    matched = {int(c) for c in comp["_cik_int"].dropna()}
    check_hit_rate("comp.company CIK -> gvkey", len(matched & set(ciks)), len(ciks),
                   MIN_HIT_RATE)
    if not TOPUP:
        missing = [f"{n} ({c})" for c, n in SENTINEL_CIKS.items()
                   if c in ciks and len(comp.loc[comp["_cik_int"] == c, "gvkey"].dropna()) == 0]
        if missing:
            abort("sentinel CIKs returned no gvkey: " + ", ".join(missing) +
                  f" (CIK form tried: {cik_form}) - the join key or CIK form is wrong")
        log(f"  sentinels OK: {', '.join(SENTINEL_CIKS.values())} each returned a gvkey")
    gvkeys = sorted({g for g in comp["gvkey"].dropna()}) if "gvkey" in comp.columns else []
    log(f"  gvkeys reached: {len(gvkeys)}")
    files.append(write(comp.drop(columns=["_cik_int"]), "comp_company.csv"))

    # ---- 2. ccmxpf_lnkhist ------------------------------------------------
    log("\n## 2. crsp.ccmxpf_lnkhist (filtered by gvkey)")
    lnk = fetch_chunked(
        db,
        "select gvkey, lpermno, lpermco, linktype, linkprim, linkdt, linkenddt "
        "from crsp.ccmxpf_lnkhist where gvkey in ({values})",
        gvkeys, quote_list) if gvkeys else pd.DataFrame()
    require_nonempty(lnk, "crsp.ccmxpf_lnkhist")
    log(f"  link rows: {len(lnk):,}   linktypes: {sorted(lnk['linktype'].dropna().unique())}")
    check_hit_rate("gvkey -> CCM link", lnk["gvkey"].nunique(), len(gvkeys))
    permnos = sorted({int(p) for p in lnk["lpermno"].dropna()})
    log(f"  permnos reached: {len(permnos)}")
    files.append(write(lnk, "ccmxpf_lnkhist.csv"))

    # ---- 3. SEC Analytics link (optional) ---------------------------------
    log("\n## 3. SEC Analytics CIK-GVKEY link (optional)")
    sec = pd.DataFrame()
    for table in ("wrdssec.wciklink_gvkey", "wrdssec_midas.wciklink_gvkey"):
        try:
            sec = fetch_chunked(db, f"select * from {table} where cik in ({{values}})",
                                [f"{c:010d}" for c in ciks], quote_list)
            log(f"  pulled from {table}: {len(sec):,} rows")
            break
        except Exception as e:
            log(f"  {table} unavailable ({type(e).__name__}: {str(e)[:90]})")
    if len(sec) == 0:
        log("  no SEC Analytics link table available; continuing (Stage 2 uses CCM only)")
    files.append(write(sec, "sec_cik_gvkey.csv"))

    # ---- 4. crsp.stocknames -----------------------------------------------
    log("\n## 4. crsp.stocknames (filtered by permno)")
    names = fetch_chunked(
        db,
        "select permno, namedt, nameenddt, ticker, comnam, shrcd, exchcd "
        "from crsp.stocknames where permno in ({values})",
        permnos, int_list)
    require_nonempty(names, "crsp.stocknames")
    log(f"  name rows: {len(names):,}")
    check_hit_rate("permno -> stocknames", names["permno"].nunique(), len(permnos))
    files.append(write(names, "crsp_stocknames.csv"))

    # ---- 5. crsp.dsf -------------------------------------------------------
    log("\n## 5. crsp.dsf (filtered by permno; the dominant payload)")
    dsf = fetch_chunked(
        db,
        "select permno, date, ret, retx, prc, vol, shrout from crsp.dsf "
        f"where date >= '{START_DATE}' and permno in ({{values}})",
        permnos, int_list)
    require_nonempty(dsf, "crsp.dsf")
    log(f"  daily rows: {len(dsf):,}   range: {date_range(dsf)}")
    check_hit_rate("permno -> daily returns", dsf["permno"].nunique(), len(permnos))
    files.append(write(dsf, "crsp_dsf.csv"))

    # ---- 6. crsp.dsi -------------------------------------------------------
    log("\n## 6. crsp.dsi (market index, date range only)")
    dsi = db.raw_sql(
        f"select date, vwretd, ewretd from crsp.dsi where date >= '{START_DATE}'")
    require_nonempty(dsi, "crsp.dsi")
    log(f"  index rows: {len(dsi):,}   range: {date_range(dsi)}")
    files.append(write(dsi, "crsp_dsi.csv"))

    # ---- CRSP end date -----------------------------------------------------
    log("\n## CRSP coverage end date")
    end = pd.to_datetime(dsf["date"], errors="coerce").max()
    log(f"- max(crsp.dsf.date) = {end.date()}")
    log("- v3 committed extract ended 2024-12-31")
    if end.date() > pd.Timestamp("2024-12-31").date():
        log(f"- **EXTENDS PAST v3 by {(end - pd.Timestamp('2024-12-31')).days} days.** "
            "Stage 5 must report events recovered by relinking separately from events "
            "added by the longer extract.")
    else:
        log("- does not extend past v3; the past-extract exclusions stand")

    return files


def main():
    ap = argparse.ArgumentParser(description="REBUILD V4 Stage 1 WRDS pull (filtered)")
    ap.add_argument("--extra-ciks", metavar="FILE",
                    help="TOP-UP MODE. One CIK per line, or a CSV with a cik/final_cik/"
                         "parent_cik/outcome_cik column. Pulls ONLY these CIKs and writes "
                         "new files suffixed _topup_<stamp>; the first pull is never "
                         "overwritten. Intended for Stage 3 verified parents.")
    args = ap.parse_args()

    topup = bool(args.extra_ciks)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reset_state(suffix=f"_topup_{stamp}" if topup else "", topup=topup)

    try:
        import wrds
    except ImportError:
        sys.exit("The `wrds` package is not installed. pip install wrds")

    n_canon = n_nom = 0
    if topup:
        ciks = read_extra_ciks(args.extra_ciks)
        if not ciks:
            sys.exit("--extra-ciks resolved to an empty CIK list")
    else:
        if not CANON.exists():
            sys.exit(f"missing input: {CANON}")
        ciks = {int(c) for c in pd.read_csv(CANON, low_memory=False)["final_cik"].dropna()}
        n_canon = len(ciks)
        if NOMS.exists():
            pc = pd.to_numeric(pd.read_csv(NOMS)["parent_cik"], errors="coerce").dropna()
            nom = {int(c) for c in pc}
            n_nom = len(nom - ciks)
            ciks |= nom
    ciks = sorted(ciks)

    started = datetime.now(timezone.utc)
    if topup:
        log(f"\n---\n\n# REBUILD V4 — Stage 1 TOP-UP pull ({stamp})")
        log("")
        log(f"- top-up source: `{args.extra_ciks}`")
        log(f"- CIK filter list: {len(ciks)} CIKs (top-up only; the first pull is untouched)")
        log(f"- output suffix: `{SUFFIX}` — no file from the first pull is overwritten")
    else:
        log("# REBUILD V4 — Stage 1 WRDS pull log")
        log("")
        log(f"- CIK filter list: {len(ciks)} CIKs "
            f"({n_canon} from CANONICAL_V3, +{n_nom} nominated parents not already present)")
    log(f"- pull started (UTC): {started.isoformat(timespec='seconds')}")
    log(f"- daily data from: {START_DATE}")
    log("")

    try:
        db = wrds.Connection()
    except SystemExit:
        raise
    except BaseException as e:
        abort(f"WRDS connection failed: {type(e).__name__}: {scrub(e)}")

    try:
        user = (getattr(db, "_username", None) or getattr(db, "username", None)
                or "(not reported)")
        log(f"- WRDS username: {user}   (no password is stored, printed, or logged)")
        log("")
        files = safe_run_pull(db, ciks)
    finally:
        try:
            db.close()
        except Exception:
            pass

    total = sum(f["bytes"] for f in files)
    log("\n## Files written")
    log("")
    log("| file | rows | MB | sha256 |")
    log("|---|---:|---:|---|")
    for f in files:
        log(f"| `{f['path']}` | {f['rows']:,} | {f['bytes']/1e6:,.1f} | `{f['sha256']}` |")
    log("")
    log(f"- total written: {total/1e6:,.1f} MB (Stage 0 estimate 33-53 MB)")
    hit_rate_table()
    log("")
    log(f"- pull finished (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(flush_log())
    print("Next: return the log. Do not run scripts/212 until Stage 1 is reviewed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
