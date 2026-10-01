"""
REBUILD V4 - STAGE 6: COMPUSTAT FUNDAMENTALS (run locally by Tim; WRDS)
=============================================================================
Refreshes the Essay 3 covariates against v4's verified gvkeys.

    python scripts/219_wrds_funda_v4.py                  # pull (WRDS) + assemble
    python scripts/219_wrds_funda_v4.py --assemble-only  # offline, from the
                                                         # committed pull file

WHAT IS AND IS NOT ALLOWED TO CHANGE
------------------------------------
v3 built these covariates in scripts/156.  Its FISCAL-YEAR RULE is reproduced
here verbatim and must not drift:

    the latest comp.funda datadate STRICTLY BEFORE breach_date,
    and no more than 550 days stale;
    at > 0 gates firm_size_log, leverage and roa;
    op_margin needs sale > 0 and cogs present, missing xsga coerced to 0;
    every value rounded to 4 decimal places.

    firm_size_log = ln(at)      leverage = lt / at      roa = ni / at
    op_margin     = (sale - cogs - xsga) / sale

What DOES change, per Tim's ruling, is the JOIN KEY.  v3 joined Compustat by
TICKER (156: by_tic[matched_ticker]) because it had no verified gvkey.  v4's
linker produces one, so the join is by gvkey.  Because that is a substantive
change and not merely a refreshed source, the script also computes the
covariates the v3 way (by ticker) and writes a ticker-vs-gvkey AGREEMENT TABLE,
so the change is measured rather than assumed.  The ticker arm is diagnostic
only; the gvkey arm is the v4 covariate.

NOTE ON scripts/168: v3's prose describes firm_size_log as log MARKET CAP from
CRSP, while v3's code computes ln(total assets).  Per ruling, v4 replicates the
CODE.  The mismatch is v3 documentation debt and is flagged in the side-by-side,
not fixed here.

FAILS LOUDLY
------------
Missing input ABORTS - no graceful fallback.  An empty query result ABORTS.  The
script refuses to overwrite an existing pull file.  Any unhandled exception
becomes an abort() so the log is always written.

THE TRAP THIS SCRIPT IS BUILT AROUND
------------------------------------
comp.funda.gvkey is a 6-character ZERO-PADDED STRING; v4_212_links.csv stores
gvkey as float64.  str(1440.0).zfill(6) == '1440.0' - already six characters, so
zfill does nothing and the literal matches no row.  Run 1 died exactly there:
140 gvkeys sent, 0 rows back, which reads identically to "Compustat has no
fundamentals for these firms".  Three guards now separate those cases:

  * every gvkey goes through int(float(.)) and is formatted %06d;
  * the first three literals actually sent are logged, so a format regression is
    visible in the log rather than looking like empty coverage;
  * the sentinels (T-Mobile, AT&T, Sprint) must each return comp.funda rows, so
    a partial result from other gvkeys cannot mask a broken chain;
  * on zero rows, ONE unfiltered probe runs to say whether the failure is the key
    format or the filter values.  Probe rows are counted and discarded - never
    kept, since indfmt/datafmt/popsrc/consol define the covariates.

OUTPUTS
-------
    Data/wrds_v4/comp_funda.csv                       raw pull, all years
    outputs/rebuild_v4/219_covariates_v4.csv          per event, gvkey + ticker arms
    outputs/rebuild_v4/219_covariate_deltas.csv       old (v3-inherited) vs new
    outputs/rebuild_v4/219_ticker_gvkey_agreement.csv agreement summary
    outputs/rebuild_v4/219_funda_log.md
"""
import argparse
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
OUT_DATA = Path("Data/wrds_v4")
OUT = Path("outputs/rebuild_v4")
FUNDA = OUT_DATA / "comp_funda.csv"

FIELDS = ["gvkey", "tic", "datadate", "fyear", "at", "lt", "ni", "sale", "cogs", "xsga"]
STALE_DAYS = 550              # scripts/156, verbatim
COVARS = ["firm_size_log", "leverage", "roa", "op_margin"]
CHUNK = 500
MIN_HIT_RATE = 0.50
# Same three firms scripts/211 uses. Each must run CIK -> gvkey -> comp.funda.
SENTINEL_CIKS = {1283699: "T-Mobile", 732717: "AT&T", 101830: "Sprint"}

L = []


def log(msg=""):
    print(msg)
    L.append(str(msg))


def flush_log():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "219_funda_log.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("## ABORTED")
    log("ABORT: " + str(msg))
    flush_log()
    sys.exit("ABORT: " + str(msg))


def require(path):
    if not path.exists():
        abort("missing input: " + str(path) + " (no graceful fallback)")
    return path


def norm_gvkey(v):
    """comp.funda.gvkey is a 6-character ZERO-PADDED STRING.  v4_212_links.csv stores
    gvkey as float64, so str(1440.0).zfill(6) yields '1440.0' - already 6 characters,
    so zfill does nothing, and the literal matches no row.  Run 1 of this script died
    exactly that way: 140 gvkeys sent, 0 rows back, indistinguishable at a glance from
    "Compustat has no fundamentals for these firms".  Always go through int(float(.))."""
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return ""
    try:
        return "{:06d}".format(int(float(s)))
    except (TypeError, ValueError):
        return s.zfill(6)


# --------------------------------------------------------------- 156's rule, verbatim
def covars(g, bdt):
    """g: one firm's funda rows sorted by datadate. Reproduces scripts/156 covars()."""
    if g is None or not len(g):
        return {}
    prior = g[(g["datadate"] < bdt) & (g["datadate"] >= bdt - timedelta(days=STALE_DAYS))]
    if len(prior) == 0:
        return {}
    r = prior.iloc[-1]
    out = {}
    if pd.notna(r["at"]) and r["at"] > 0:
        out["firm_size_log"] = round(np.log(r["at"]), 4)
        if pd.notna(r["lt"]):
            out["leverage"] = round(r["lt"] / r["at"], 4)
        if pd.notna(r["ni"]):
            out["roa"] = round(r["ni"] / r["at"], 4)
    if pd.notna(r["sale"]) and r["sale"] > 0 and pd.notna(r["cogs"]):
        xs = r["xsga"] if pd.notna(r["xsga"]) else 0
        out["op_margin"] = round((r["sale"] - r["cogs"] - xs) / r["sale"], 4)
    return out


def sql_values(batch):
    quoted = []
    for g in batch:
        quoted.append("'" + str(g).replace("'", "''") + "'")
    return ", ".join(quoted)


# --------------------------------------------------------------- WRDS pull
def sentinel_gvkeys(links):
    """The sentinels run the whole CIK -> gvkey -> funda chain, as in scripts/211.
    Checking only the row count would let a key-format failure through whenever some
    OTHER gvkey happened to return rows."""
    out = {}
    for cik, name in SENTINEL_CIKS.items():
        got = {norm_gvkey(x) for x in links.loc[links["final_cik"] == cik,
                                                "gvkey"].dropna().unique()}
        got = {g for g in got if g}
        if not got:
            abort("sentinel " + name + " (CIK " + str(cik) + ") reached no gvkey in "
                  + str(LINKS) + " - the CIK -> gvkey step broke")
        out[name] = got
    return out


def run_pull():
    import wrds
    if FUNDA.exists():
        abort("refusing to overwrite an existing pull file: " + str(FUNDA))
    links = pd.read_csv(require(LINKS), low_memory=False)
    if "gvkey" not in links.columns:
        abort(str(LINKS) + " has no gvkey column")
    gvkeys = sorted({norm_gvkey(g) for g in links["gvkey"].dropna()
                     if str(g).strip() not in ("", "nan")})
    gvkeys = [g for g in gvkeys if g]
    if not gvkeys:
        abort("no gvkeys reached in v4 - nothing to pull")
    sent = sentinel_gvkeys(links)
    log("gvkeys to pull: " + str(len(gvkeys)))
    # The exact literal form matters more than the count - log it, so a future
    # format regression is visible in the log instead of looking like empty coverage.
    log("first 3 gvkey literals sent: "
        + ", ".join(repr(g) for g in gvkeys[:3]))
    log("sentinel gvkeys: "
        + "; ".join(n + " " + ", ".join(sorted(g)) for n, g in sorted(sent.items())))

    db = wrds.Connection()
    try:
        frames = []
        cols = ", ".join(FIELDS)
        for i in range(0, len(gvkeys), CHUNK):
            batch = gvkeys[i:i + CHUNK]
            sql = ("select " + cols + " from comp.funda where indfmt='INDL' and "
                   "datafmt='STD' and popsrc='D' and consol='C' and gvkey in ("
                   + sql_values(batch) + ")")
            frames.append(db.raw_sql(sql))
            log("  chunk " + str(i // CHUNK + 1) + ": gvkeys " + str(len(batch))
                + ", rows " + str(len(frames[-1])))
        df = pd.concat(frames, ignore_index=True).drop_duplicates()

        if not len(df):
            # Zero rows has two very different causes and the abort must name which.
            # Probe ONCE without the filters; the probe rows are counted and thrown
            # away - they are never kept, since indfmt/datafmt/popsrc/consol define
            # the covariates.
            log("")
            log("comp.funda returned 0 rows with the standard filters - "
                "running one unfiltered diagnostic probe")
            probe = db.raw_sql("select gvkey, datadate from comp.funda where gvkey in ("
                               + sql_values(gvkeys[:CHUNK]) + ") limit 100")
            log("  unfiltered probe rows: " + str(len(probe)) + " (discarded)")
            if len(probe):
                abort("the gvkey literals DO match comp.funda, but "
                      "indfmt='INDL'/datafmt='STD'/popsrc='D'/consol='C' returned "
                      "nothing - a FILTER-VALUE failure, not a key-format failure")
            abort("comp.funda returned no rows even unfiltered - a KEY-FORMAT "
                  "failure; literals sent were "
                  + ", ".join(repr(g) for g in gvkeys[:3]))
    finally:
        db.close()

    df["gvkey"] = df["gvkey"].map(norm_gvkey)
    reached = set(df["gvkey"])
    missing = sorted(n for n, gs in sent.items() if not (gs & reached))
    if missing:
        abort("sentinel gvkeys returned no comp.funda rows: " + ", ".join(missing)
              + " - the gvkey -> funda step broke (a partial result from other "
                "gvkeys is not evidence the chain works)")
    rate = len(reached) / len(gvkeys)
    log("comp.funda: " + str(len(df)) + " rows; gvkeys reached "
        + str(len(reached)) + "/" + str(len(gvkeys)) + " = "
        + format(100 * rate, ".1f") + "%")
    log("sentinels reached funda: " + ", ".join(sorted(sent)))
    if rate < MIN_HIT_RATE:
        abort("gvkey hit rate " + format(100 * rate, ".1f") + "% is below the 50% floor")
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    df.to_csv(FUNDA, index=False)
    log("written " + str(FUNDA))


# --------------------------------------------------------------- assembly
def build_covariates(canon, links, funda):
    """Pure function so the offline suite can drive it with fixtures."""
    funda = funda.copy()
    funda["gvkey"] = funda["gvkey"].map(norm_gvkey)
    funda["datadate"] = pd.to_datetime(funda["datadate"])
    funda = funda.dropna(subset=["at"])
    by_gv = {k: g.sort_values("datadate") for k, g in funda.groupby("gvkey")}
    by_tic = {}
    if "tic" in funda.columns:
        by_tic = {k: g.sort_values("datadate")
                  for k, g in funda.dropna(subset=["tic"]).groupby("tic")}

    canon = canon.copy()
    canon["bdt"] = pd.to_datetime(canon["breach_date"])
    canon["breach_date"] = canon["breach_date"].astype(str).str[:10]
    key = ["final_cik", "breach_date"]

    lk = links.copy()
    lk["breach_date"] = lk["breach_date"].astype(str).str[:10]
    gv = (lk.dropna(subset=["gvkey"])
          .assign(gvkey=lambda d: d["gvkey"].map(norm_gvkey))
          .drop_duplicates(key).set_index(key)["gvkey"])
    canon["gvkey"] = canon.set_index(key).index.map(gv)

    rows = []
    for _, e in canon.iterrows():
        g_arm = covars(by_gv.get(e["gvkey"]), e["bdt"])
        t_arm = covars(by_tic.get(e.get("matched_ticker")), e["bdt"])
        rec = dict(final_cik=e["final_cik"], breach_date=e["breach_date"],
                   org_name=e.get("org_name", ""),
                   treated=int(e.get("fcc_form499", 0) or 0),
                   gvkey=e["gvkey"], matched_ticker=e.get("matched_ticker", ""))
        for c in COVARS:
            rec[c] = g_arm.get(c, np.nan)
            rec[c + "_tic"] = t_arm.get(c, np.nan)
            rec[c + "_v3"] = e.get(c, np.nan)
        rows.append(rec)
    return pd.DataFrame(rows)


def agreement_table(cov):
    ag = []
    for c in COVARS:
        both = cov[cov[c].notna() & cov[c + "_tic"].notna()]
        same = int((both[c] == both[c + "_tic"]).sum())
        ag.append(dict(variable=c, both_present=len(both), identical=same,
                       differ=len(both) - same,
                       gvkey_only=int((cov[c].notna() & cov[c + "_tic"].isna()).sum()),
                       ticker_only=int((cov[c].isna() & cov[c + "_tic"].notna()).sum()),
                       max_abs_diff=(round(float((both[c] - both[c + "_tic"]).abs().max()), 4)
                                     if len(both) else np.nan)))
    return pd.DataFrame(ag)


def delta_table(cov):
    d = []
    for _, r in cov.iterrows():
        for c in COVARS:
            old, new = r[c + "_v3"], r[c]
            if pd.isna(old) and pd.isna(new):
                continue
            if pd.notna(old) and pd.notna(new) and old == new:
                kind = "identical"
            elif pd.isna(old):
                kind = "gained"
            elif pd.isna(new):
                kind = "lost"
            else:
                kind = "changed"
            d.append(dict(final_cik=r["final_cik"], breach_date=r["breach_date"],
                          org_name=r["org_name"], treated=r["treated"], gvkey=r["gvkey"],
                          variable=c, v3_value=old, v4_value=new, change=kind,
                          delta=(round(new - old, 4)
                                 if pd.notna(old) and pd.notna(new) else np.nan)))
    return pd.DataFrame(d)


def run_assemble():
    canon = pd.read_csv(require(CANON), low_memory=False)
    links = pd.read_csv(require(LINKS), low_memory=False)
    funda = pd.read_csv(require(FUNDA), low_memory=False)

    cov = build_covariates(canon, links, funda)
    OUT.mkdir(parents=True, exist_ok=True)
    cov.to_csv(OUT / "219_covariates_v4.csv", index=False)

    log("")
    log("## Coverage (gvkey arm)")
    for c in COVARS:
        log("- " + c + ": " + str(int(cov[c].notna().sum())) + " of " + str(len(cov))
            + " (v3 inherited " + str(int(cov[c + "_v3"].notna().sum())) + ")")

    AG = agreement_table(cov)
    AG.to_csv(OUT / "219_ticker_gvkey_agreement.csv", index=False)
    log("")
    log("## Ticker vs gvkey agreement (ticker arm is diagnostic only)")
    log(AG.to_string(index=False))

    D = delta_table(cov)
    D.to_csv(OUT / "219_covariate_deltas.csv", index=False)
    log("")
    log("## Covariate deltas, v3-inherited vs v4-refreshed")
    if len(D):
        log(D.groupby(["variable", "change"]).size().unstack(fill_value=0).to_string())
        log("")
        log("By treated/control (non-identical only):")
        nd = D[D["change"] != "identical"]
        if len(nd):
            log(nd.groupby(["treated", "change"]).size().unstack(fill_value=0).to_string())
        else:
            log("(none)")
    else:
        log("(no rows)")
    log("")
    log("written 219_covariates_v4.csv, 219_covariate_deltas.csv, "
        "219_ticker_gvkey_agreement.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assemble-only", action="store_true",
                    help="skip the WRDS pull; assemble from the committed comp_funda.csv")
    a = ap.parse_args()
    log("# REBUILD V4 - Stage 6 Compustat fundamentals (scripts/219)")
    log("")
    try:
        if not a.assemble_only:
            run_pull()
        run_assemble()
    except SystemExit:
        raise
    except Exception as e:
        abort("unhandled " + type(e).__name__ + ": " + str(e))
    flush_log()


if __name__ == "__main__":
    main()
