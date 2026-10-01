"""
REBUILD V4 — STAGE 1: WRDS PULL, CUSIP ROUTE (run locally by Tim)
=====================================================================================
The CCM route is unavailable on this subscription. Run 1 died with

    psycopg2.errors.InsufficientPrivilege: permission denied for schema crsp_a_ccm

and scripts/216 confirmed that no gvkey -> permno link table is reachable anywhere
(wrdssec is blocked too; the wrdsapps.*link tables are bond/short/FactSet/TAQ/patent
bridges, not CCM). Reachable: comp.company, comp.security, crsp.stocknames,
crsp.dsenames, crsp.msenames, crsp.dsf, crsp.dsi.

So the chain is:

    CIK -> gvkey            comp.company.cik   (zero-padded 10-char; confirmed run 1)
    gvkey -> CUSIP          comp.security.cusip
    CUSIP -> permno         crsp.stocknames, on ncusip (historical) or cusip (header)
    permno -> daily         crsp.dsf

    python scripts/211_wrds_pull_v4.py                       # first pull
    python scripts/211_wrds_pull_v4.py --extra-ciks FILE     # later top-up

TWO TRAPS THIS SCRIPT IS BUILT AROUND
-------------------------------------
1. CUSIP LENGTH. Compustat stores a 9-character CUSIP including the check digit; CRSP
   stores 8. Matching 9 against 8 returns nothing and looks exactly like "these
   securities are not in CRSP". Every CUSIP is trimmed to cusip[:8], uppercased, and
   the trim is logged with a sample.
2. ONE COMPANY, SEVERAL SECURITIES. A gvkey can carry several issues (share classes).
   Hit rates are therefore measured as DISTINCT KEYS REACHED, never row counts, or a
   one-to-many join reads as >100%.

FAILS LOUDLY
------------
Each step asserts before the next begins; any failure writes the log and exits nonzero.

  comp.company      empty aborts; CIK hit rate must be >= 50%
  comp.security     empty aborts; gvkey -> CUSIP hit rate reported
  crsp.stocknames   empty aborts; CUSIP -> permno hit rate reported
  crsp.dsf          empty aborts; permno -> daily hit rate reported
  crsp.dsi          empty aborts (Stage 2's market adjustment needs it)

SENTINELS RUN THE WHOLE CHAIN. 1283699 T-Mobile, 732717 AT&T, 101830 Sprint must each
reach a gvkey AND a CUSIP AND a permno. Checking only the gvkey step would let the
CUSIP-length failure through silently, since comp.company would still look healthy.
The abort names the step that broke. Skipped in top-up mode, where the CIK list is
arbitrary.

Any unhandled exception becomes an abort() so the log is always written (the run-1
defect), and scrub() redacts password-shaped text from driver messages.

comp.company is pulled with SELECT *, so priusa survives if the subscription exposes
it; Stage 2 uses it to pick the primary US issue. Whether it is present is logged.

OUTPUTS
-------
    Data/wrds_v4/comp_company.csv       CIK -> gvkey, all columns (priusa if present)
    Data/wrds_v4/comp_security.csv      gvkey -> cusip/tic/exchg, plus cusip8
    Data/wrds_v4/crsp_stocknames.csv    permno, namedt, nameenddt, ncusip, cusip,
                                        ticker, comnam, shrcd, exchcd
    Data/wrds_v4/crsp_dsf.csv           permno, date, ret, retx, prc, vol, shrout
    Data/wrds_v4/crsp_dsi.csv           date, vwretd, ewretd
    outputs/rebuild_v4/211_pull_log.md  timestamp, username, hit rates, sentinel trace,
                                        date ranges, sha256 of every file

RECORD THE CRSP END DATE. If max(dsf.date) runs past 2024-12-31, events the v3 chain
lost as "past-extract" may re-enter; Stage 5 reports those separately from events
recovered by relinking.

READ-ONLY with respect to every v3 path.
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
# The committed copy, not outputs/essay3_q2/ (which stays untracked). Missing ABORTS.
NOMS = Path("outputs/rebuild_v4/inputs/crsp_drop_nominations.csv")

SENTINEL_CIKS = {1283699: "T-Mobile", 732717: "AT&T", 101830: "Sprint"}
MIN_HIT_RATE = 0.50

LOG = []
HIT_RATES = []
SUFFIX = ""
TOPUP = False


def reset_state(suffix="", topup=False):
    global LOG, HIT_RATES, SUFFIX, TOPUP
    LOG, HIT_RATES, SUFFIX, TOPUP = [], [], suffix, topup


def log(msg=""):
    print(msg, flush=True)
    LOG.append(str(msg))


def scrub(text):
    """Never let a credential reach the log."""
    t = str(text)
    return re.sub(r"(?i)\b(password|pwd|passwd)\s*=\s*\S+", r"\1=***REDACTED***", t)


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
    log("## Hit rates (distinct keys reached, never row counts)")
    log("")
    log("| step | reached | requested | rate |")
    log("|---|---:|---:|---:|")
    for label, got, want, rate in HIT_RATES:
        log(f"| {label} | {got:,} | {want:,} | {100 * rate:.1f}% |")


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
    """Any exception becomes an abort(), so the log is always written."""
    try:
        return run_pull(db, ciks)
    except SystemExit:
        raise
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


def check_sentinels(step, reached, cik_form):
    """reached: cik -> set of keys at this step. Aborts naming the step that broke."""
    if TOPUP:
        return
    missing = [f"{n} ({c})" for c, n in SENTINEL_CIKS.items()
               if c in reached and not reached[c]]
    if missing:
        abort(f"sentinel CIKs reached no {step}: {', '.join(missing)} "
              f"(CIK form: {cik_form}). The chain breaks at the {step} step - "
              f"earlier steps looked healthy, which is exactly the failure a "
              f"gvkey-only sentinel would have missed.")
    ok = ", ".join(f"{SENTINEL_CIKS[c]}={len(v)}" for c, v in sorted(reached.items()))
    log(f"  sentinels reached a {step}: {ok}")


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
    """sql_template may contain {values} more than once; str.format fills every one."""
    frames = []
    for part in chunked(values):
        frames.append(db.raw_sql(sql_template.format(values=formatter(part))))
    frames = [f for f in frames if f is not None and len(f)]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates()


def write(df, name):
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
    for raw in p.read_text(encoding="utf-8").splitlines():
        # Strip INLINE comments as well as whole-line ones. 213 writes a commented header
        # and one CIK per line, but a CIK annotated with its company name -
        # "718877   # Activision Blizzard, Inc." - used to raise ValueError and kill the
        # pull, which is a poor reward for documenting the file.
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            out.add(int(line))
        except ValueError:
            sys.exit(f"--extra-ciks: cannot read a CIK from line {raw!r} in {p}")
    return out


def cusip8(series):
    """Compustat 9-char (with check digit) -> CRSP 8-char, uppercased."""
    return series.astype(str).str.strip().str.upper().str[:8]


def fetch_company(db, ciks):
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
    files = []
    cikset = set(ciks)

    # ---- 1. comp.company: CIK -> gvkey -------------------------------------
    log("## 1. comp.company (filtered by CIK)  ->  gvkey")
    comp, cik_form = fetch_company(db, ciks)
    require_nonempty(comp, "comp.company")
    comp = comp.copy()
    comp["_cik_int"] = pd.to_numeric(comp.get("cik"), errors="coerce")
    log(f"  priusa column present: {'priusa' in comp.columns}"
        f"{'' if 'priusa' in comp.columns else '  (Stage 2 falls back to all US common issues)'}")
    matched = {int(c) for c in comp["_cik_int"].dropna()}
    check_hit_rate("CIK -> gvkey", len(matched & cikset), len(ciks), MIN_HIT_RATE)
    gv_by_cik = {c: set(comp.loc[comp["_cik_int"] == c, "gvkey"].dropna())
                 for c in SENTINEL_CIKS if c in cikset}
    check_sentinels("gvkey", gv_by_cik, cik_form)
    gvkeys = sorted({g for g in comp["gvkey"].dropna()}) if "gvkey" in comp.columns else []
    log(f"  gvkeys reached: {len(gvkeys)}")
    files.append(write(comp.drop(columns=["_cik_int"]), "comp_company.csv"))

    # ---- 2. comp.security: gvkey -> CUSIP -----------------------------------
    log("\n## 2. comp.security (filtered by gvkey)  ->  CUSIP")
    sec = fetch_chunked(db, "select * from comp.security where gvkey in ({values})",
                        gvkeys, quote_list) if gvkeys else pd.DataFrame()
    require_nonempty(sec, "comp.security")
    sec = sec.copy()
    if "cusip" not in sec.columns:
        abort("comp.security has no cusip column; the CUSIP route cannot proceed")
    raw_len = sec["cusip"].astype(str).str.strip().str.len()
    sec["cusip8"] = cusip8(sec["cusip"])
    log(f"  security rows: {len(sec):,}   raw cusip lengths: "
        f"{sorted(set(raw_len.dropna().astype(int)))} -> trimmed to 8")
    sample = sec[["cusip", "cusip8"]].dropna().head(3).values.tolist()
    log(f"  trim sample: {sample}")
    # one gvkey can carry several issues: count COMPANIES reached, not rows
    gv_with_cusip = {g for g in sec.loc[sec["cusip8"].str.len() == 8, "gvkey"].dropna()}
    check_hit_rate("gvkey -> CUSIP", len(gv_with_cusip & set(gvkeys)), len(gvkeys))
    cu_by_cik = {c: {u for g in gv for u in
                     sec.loc[sec["gvkey"] == g, "cusip8"].dropna()}
                 for c, gv in gv_by_cik.items()}
    check_sentinels("CUSIP", cu_by_cik, cik_form)
    cusips = sorted({u for u in sec["cusip8"].dropna() if len(u) == 8})
    log(f"  distinct 8-char CUSIPs reached: {len(cusips)}")
    files.append(write(sec, "comp_security.csv"))

    # ---- 3. crsp.stocknames: CUSIP -> permno --------------------------------
    log("\n## 3. crsp.stocknames (filtered by 8-char CUSIP, ncusip OR cusip)  ->  permno")
    names = fetch_chunked(
        db,
        "select permno, namedt, nameenddt, ncusip, cusip, ticker, comnam, shrcd, exchcd "
        "from crsp.stocknames where ncusip in ({values}) or cusip in ({values})",
        cusips, quote_list)
    require_nonempty(names, "crsp.stocknames")
    names = names.copy()
    hit_nc = set(names["ncusip"].dropna().astype(str).str.upper())
    hit_hd = set(names["cusip"].dropna().astype(str).str.upper())
    reached = (hit_nc | hit_hd) & set(cusips)
    log(f"  name rows: {len(names):,}   matched via ncusip: {len(hit_nc & set(cusips))}, "
        f"via header cusip: {len(hit_hd & set(cusips))}")
    check_hit_rate("CUSIP -> permno", len(reached), len(cusips))
    pm_by_cik = {}
    for c, cu in cu_by_cik.items():
        m = names[names["ncusip"].astype(str).str.upper().isin(cu)
                  | names["cusip"].astype(str).str.upper().isin(cu)]
        pm_by_cik[c] = {int(p) for p in m["permno"].dropna()}
    check_sentinels("permno", pm_by_cik, cik_form)
    permnos = sorted({int(p) for p in names["permno"].dropna()})
    log(f"  permnos reached: {len(permnos)}")
    files.append(write(names, "crsp_stocknames.csv"))

    # ---- 4. crsp.dsf --------------------------------------------------------
    log("\n## 4. crsp.dsf (filtered by permno; the dominant payload)")
    dsf = fetch_chunked(
        db,
        "select permno, date, ret, retx, prc, vol, shrout from crsp.dsf "
        f"where date >= '{START_DATE}' and permno in ({{values}})",
        permnos, int_list)
    require_nonempty(dsf, "crsp.dsf")
    log(f"  daily rows: {len(dsf):,}   range: {date_range(dsf)}")
    check_hit_rate("permno -> daily returns", dsf["permno"].nunique(), len(permnos))
    files.append(write(dsf, "crsp_dsf.csv"))

    # ---- 5. crsp.dsi --------------------------------------------------------
    log("\n## 5. crsp.dsi (market index, date range only)")
    dsi = db.raw_sql(
        f"select date, vwretd, ewretd from crsp.dsi where date >= '{START_DATE}'")
    require_nonempty(dsi, "crsp.dsi")
    log(f"  index rows: {len(dsi):,}   range: {date_range(dsi)}")
    files.append(write(dsi, "crsp_dsi.csv"))

    # ---- CRSP end date ------------------------------------------------------
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


def issuer_codes():
    """6-char CUSIP issuer codes from every comp.security pulled so far.

    Compustat's security-level CUSIP names a specific ISSUE; CRSP's ncusip names the
    issue its permno carries. They share the 6-char issuer stem but often differ in the
    issue digits - Carnival's comp.security cusip is 143658938 while CRSP carries
    14365830 for the same company - so an 8-char match misses where a 6-char one hits.
    """
    paths = ([OUT_DATA / "comp_security.csv"]
             + sorted(OUT_DATA.glob("comp_security_topup_*.csv")))
    frames = [pd.read_csv(x, low_memory=False) for x in paths if x.exists()]
    if not frames:
        abort("no comp_security file found; run the base pull before the issuer top-up")
    sec = pd.concat(frames, ignore_index=True)
    if not {"tpci", "excntry", "cusip"} <= set(sec.columns):
        abort("comp_security lacks tpci/excntry/cusip; cannot derive issuer codes")
    us = sec[(sec["tpci"].astype(str) == "0") & (sec["excntry"] == "USA")]
    codes = sorted({str(x).strip().upper()[:6] for x in us["cusip"].dropna()
                    if len(str(x).strip()) >= 6})
    if not codes:
        abort("no US-common issuer codes derived from comp.security")
    return codes


NAMES_COLS = ("select permno, permco, namedt, nameenddt, ncusip, cusip, ticker, "
              "comnam, shrcd, exchcd from crsp.stocknames ")


def run_issuer_permco_pull(db):
    """Stocknames by 6-char issuer code, then by every permco reached, then dsf.

    permco is selected HERE and not in the base pull, so the permco fallback is
    impossible until this runs.
    """
    global SUFFIX
    # Distinct from the CIK top-up's suffix: when both run in one invocation they would
    # otherwise write the same filenames and the no-clobber guard would abort halfway.
    # The name still matches 212's *_topup_*.csv glob, so both sets are read as one.
    SUFFIX = f"{SUFFIX}_issuer" if SUFFIX else "_issuer"
    files = []
    log("")
    log("## ISSUER / PERMCO TOP-UP")
    log(f"  output suffix: `{SUFFIX}`")
    codes = issuer_codes()
    log(f"  6-char issuer codes from comp.security (US common): {len(codes)}")
    names = fetch_chunked(
        db,
        NAMES_COLS + "where substr(ncusip,1,6) in ({values}) "
                     "or substr(cusip,1,6) in ({values})",
        codes, quote_list)
    require_nonempty(names, "crsp.stocknames (issuer codes)")
    if "permco" not in names.columns:
        abort("crsp.stocknames returned no permco column; the permco fallback needs it")
    permcos = sorted({int(x) for x in names["permco"].dropna()})
    log(f"  issuer pass: rows {len(names):,}  permnos {names['permno'].nunique()}  "
        f"permcos {len(permcos)}")
    more = fetch_chunked(db, NAMES_COLS + "where permco in ({values})",
                         permcos, int_list)
    require_nonempty(more, "crsp.stocknames (permco expansion)")
    allnames = pd.concat([names, more], ignore_index=True).drop_duplicates()
    log(f"  after permco expansion: rows {len(allnames):,}  "
        f"permnos {allnames['permno'].nunique()}")
    files.append(write(allnames, "crsp_stocknames.csv"))

    pulled = set()
    for x in [OUT_DATA / "crsp_dsf.csv"] + sorted(OUT_DATA.glob("crsp_dsf_topup_*.csv")):
        if x.exists():
            pulled |= {int(v) for v in
                       pd.read_csv(x, usecols=["permno"])["permno"].dropna()}
    reached = {int(v) for v in allnames["permno"].dropna()}
    new = sorted(reached - pulled)
    log(f"  permnos already pulled: {len(pulled)}   newly reached: {len(new)}")
    if new:
        dsf = fetch_chunked(
            db,
            "select permno, date, ret, retx, prc, vol, shrout from crsp.dsf "
            f"where date >= '{START_DATE}' and permno in ({{values}})",
            new, int_list)
        require_nonempty(dsf, "crsp.dsf (new permnos)")
        log(f"  daily rows: {len(dsf):,}   range: {date_range(dsf)}")
        check_hit_rate("new permno -> daily returns", dsf["permno"].nunique(), len(new))
        files.append(write(dsf, "crsp_dsf.csv"))
    else:
        log("  no new permnos; crsp.dsf not re-pulled")
    return files


def safe_run_issuer_permco(db):
    """Any exception becomes an abort(), so the log is always written."""
    try:
        return run_issuer_permco_pull(db)
    except SystemExit:
        raise
    except BaseException as exc:
        abort(f"unhandled {type(exc).__name__} during the issuer/permco pull: "
              f"{scrub(exc)}")


def load_base_ciks():
    """CANONICAL_V3 CIKs plus nominated parent CIKs -> (ciks, n_canon, n_nom).

    BOTH inputs are required. A missing nomination file used to be tolerated, which meant
    a clean clone would quietly pull a smaller CIK universe than the one behind the
    committed outputs - a silent, invisible difference. It now aborts.
    """
    missing = [str(p) for p in (CANON, NOMS) if not p.exists()]
    if missing:
        sys.exit("missing input file(s); refusing to pull with partial inputs:\n  "
                 + "\n  ".join(missing))
    ciks = {int(c) for c in pd.read_csv(CANON, low_memory=False)["final_cik"].dropna()}
    n_canon = len(ciks)
    pc = pd.to_numeric(pd.read_csv(NOMS)["parent_cik"], errors="coerce").dropna()
    nom = {int(c) for c in pc}
    return ciks | nom, n_canon, len(nom - ciks)


def main():
    ap = argparse.ArgumentParser(description="REBUILD V4 Stage 1 WRDS pull (CUSIP route)")
    ap.add_argument("--extra-ciks", metavar="FILE",
                    help="TOP-UP MODE. One CIK per line, or a CSV with a cik/final_cik/"
                         "parent_cik/outcome_cik column. Pulls ONLY these CIKs and writes "
                         "new files suffixed _topup_<stamp>; the first pull is never "
                         "overwritten.")
    ap.add_argument("--issuer-permco", action="store_true",
                    help="ISSUER/PERMCO TOP-UP. Pulls crsp.stocknames by the 6-char CUSIP "
                         "issuer code (Compustat's issue CUSIP and CRSP's often differ in "
                         "the issue digits), then by every permco reached, then crsp.dsf "
                         "for any new permno. Selects permco, which the base pull does "
                         "not. Combine with --extra-ciks to do both in one run.")
    args = ap.parse_args()

    topup = bool(args.extra_ciks) or bool(args.issuer_permco)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reset_state(suffix=f"_topup_{stamp}" if topup else "", topup=topup)

    try:
        import wrds
    except ImportError:
        sys.exit("The `wrds` package is not installed. pip install wrds")

    n_canon = n_nom = 0
    ciks = []
    if args.extra_ciks:
        ciks = read_extra_ciks(args.extra_ciks)
        if not ciks:
            sys.exit("--extra-ciks resolved to an empty CIK list")
    elif not args.issuer_permco:
        ciks, n_canon, n_nom = load_base_ciks()
    ciks = sorted(ciks)

    started = datetime.now(timezone.utc)
    if topup:
        log(f"\n---\n\n# REBUILD V4 — Stage 1 TOP-UP pull, CUSIP route ({stamp})")
        log("")
        log(f"- top-up source: `{args.extra_ciks or '(issuer/permco pull; no CIK list)'}`")
        log(f"- issuer/permco pull: {bool(args.issuer_permco)}")
        log(f"- CIK filter list: {len(ciks)} CIKs (top-up only; the first pull is untouched)")
        log(f"- output suffix: `{SUFFIX}`")
    else:
        log("# REBUILD V4 — Stage 1 WRDS pull log (CUSIP route)")
        log("")
        log(f"- CIK filter list: {len(ciks)} CIKs "
            f"({n_canon} from CANONICAL_V3, +{n_nom} nominated parents not already present)")
    log(f"- route: CIK -> gvkey -> CUSIP(8) -> permno   (CCM is blocked; see scripts/216)")
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
        files = []
        if ciks:
            files += safe_run_pull(db, ciks)
        if args.issuer_permco:
            files += safe_run_issuer_permco(db)
        if not files:
            abort("nothing to pull: give --extra-ciks, --issuer-permco, or neither "
                  "(for the full base pull)")
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
    log(f"- total written: {total/1e6:,.1f} MB")
    hit_rate_table()
    log("")
    log(f"- pull finished (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(flush_log())
    print("Next: return the log. Do not run scripts/212 until Stage 1 is reviewed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
