"""
ESSAY 3 — QUERY 3: RESULTS-SECTION DATA PULL
=============================================================================
    python scripts/242_essay3_q3_results_pull.py

Read-and-print. Estimates NOTHING. Every statistic here is either

  (a) copied verbatim from a committed artefact of the authoritative v4 build, or
  (b) a DESCRIPTIVE count / rate / quantile over the committed analysis sample,
      which involves no model and changes no verdict, or
  (c) an ASSERTION (Part F5) that recomputes t and p FROM the committed
      coefficient and SE and checks internal consistency. It fits nothing.

Authoritative build (Query 3 Part A2): outputs/essay3_v4/, constants_essay3_v4.json
at commit 609a898. Nothing in outputs/essay3_v4/ or outputs/rebuild_v4/ is written.

Writes ONLY under outputs/essay3_q3/:
    attrition.csv treated_parents.csv descriptives.csv validation.csv
    outcomes.csv primary.csv sensitivities.csv loo.csv tmobile_case.csv
    242_pull.log
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

V4 = Path("outputs/essay3_v4")
RB = Path("outputs/rebuild_v4")
Q2 = Path("outputs/essay3_q2")
OUT = Path("outputs/essay3_q3")
OUT.mkdir(parents=True, exist_ok=True)

TREAT = "fcc_form499"
CTRL7 = ["prior_breaches_1yr", "health_breach", "firm_size_log", "leverage", "roa",
         "baseline_exec_rate_py_rd", "prior12m_mktadj_ret_rd"]
L = []


def log(m=""):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log("")
    log("=" * 100)
    log(t)
    log("=" * 100)


def need(p):
    p = Path(p)
    if not p.exists():
        sys.exit("ABORT 242: missing input " + str(p))
    return p


# ------------------------------------------------------------------ inputs
CAN = pd.read_csv(need("Data/processed/rebuild_v4/CANONICAL_V4.csv"), low_memory=False)
SAMP = pd.read_csv(need(V4 / "e_analysis_sample.csv"), low_memory=False)
A = SAMP[SAMP["in_analysis_sample"] == 1].copy()
LED = pd.read_csv(need(V4 / "e_ledger.csv"))
CON = json.loads(need(V4 / "constants_essay3_v4.json").read_text())
F1 = pd.read_csv(need(V4 / "f1_ladder.csv"))
F3 = pd.read_csv(need(V4 / "f3_sensitivities.csv"))
F4 = pd.read_csv(need(V4 / "f4_placebo.csv"))
F5 = pd.read_csv(need(V4 / "f5_ceo.csv"))
SED = pd.read_csv(need(V4 / "f1_se_diagnostics.csv"))
LOCO = pd.read_csv(need(V4 / "f3_loco.csv"))
VAR = pd.read_csv(need(V4 / "f1_cv3_variance_shares.csv"))
IT = pd.read_csv(need(V4 / "i_tests.csv"))
SIC = pd.read_csv(need(V4 / "f3_sic2_cells.csv"))
LINKS = pd.read_csv(need(RB / "v4_212_links.csv"), low_memory=False)
IDREV = pd.read_csv(need(RB / "v4_212_identity_review.csv"), low_memory=False)

for d in (CAN, A):
    d["_k"] = d["final_cik"].astype(str) + "|" + d["breach_date"].astype(str).str[:10]
IN405 = set(A["_k"])
CS = CAN[CAN["_k"].isin(IN405)].copy()          # canonical rows for the 405
A = A.merge(CS[["_k", "breach_type", "treatment_evidence", "n_source_records",
                "chain_note", "org_name"]].rename(columns={"org_name": "org_canon"}),
            on="_k", how="left")
A["bdt"] = pd.to_datetime(A["breach_date"])
A["rdt"] = pd.to_datetime(A["reported_date"])
T = A[A[TREAT] == 1]
C = A[A[TREAT] == 0]


def grp(df):
    return [("treated", df[df[TREAT] == 1]), ("control", df[df[TREAT] == 0])]


# =============================================================== PART B
hdr("PART B — sample construction (authoritative build)")
log("B1/B2 attrition — copied verbatim from e_ledger.csv, NOT recomputed:")
log(LED[[c for c in LED.columns if c != "note"]].to_string(index=False))

att = LED.copy()
att["source"] = "outputs/essay3_v4/e_ledger.csv (scripts/224)"
# the identity-gate split, which the ledger does not carry as its own line
gate_k = set(IDREV["final_cik"].astype(str) + "|" + IDREV["breach_date"].astype(str).str[:10])
nop = LINKS[LINKS["permno"].isna()].copy()
nop["_k"] = nop["final_cik"].astype(str) + "|" + nop["breach_date"].astype(str).str[:10]
tmap = dict(zip(CAN["_k"], CAN[TREAT]))
gate_t = sum(1 for k in gate_k if tmap.get(k) == 1)
gate_c = sum(1 for k in gate_k if tmap.get(k) == 0)
other = set(nop["_k"]) - gate_k
oth_t = sum(1 for k in other if tmap.get(k) == 1)
oth_c = sum(1 for k in other if tmap.get(k) == 0)
log("")
log("B2 CRSP step, split (scripts/212 outputs; the ledger carries it as one line):")
log("   identity-gate rejections        : %3d  (treated %d / control %d)" % (len(gate_k), gate_t, gate_c))
log("   no acceptable CUSIP -> permno   : %3d  (treated %d / control %d)" % (len(other), oth_t, oth_c))
log("   total lost at the CRSP step     : %3d   [489 -> 414]" % len(nop))
att = pd.concat([att, pd.DataFrame([
    dict(step="  of which: identity-gate rejection (scripts/212)", N=len(gate_k),
         treated=gate_t, control=gate_c,
         source="outputs/rebuild_v4/v4_212_identity_review.csv"),
    dict(step="  of which: no acceptable CUSIP->permno", N=len(other),
         treated=oth_t, control=oth_c,
         source="outputs/rebuild_v4/v4_212_links.csv (permno isna)")])], ignore_index=True)
att.to_csv(OUT / "attrition.csv", index=False)

log("")
log("B1 records per canonical event (CANONICAL_V4.n_source_records):")
n = CAN["n_source_records"]
log("   events %d | source records %d | mean %.3f | median %.1f | max %d"
    % (len(CAN), int(n.sum()), n.mean(), n.median(), n.max()))
big = CAN.loc[n.idxmax()]
log("   largest single event: %s %s (n=%d)" % (big["org_name"], str(big["breach_date"])[:10], n.max()))
byp = CAN.groupby("final_cik")["n_source_records"].sum().sort_values(ascending=False)
nmz = CAN.drop_duplicates("final_cik").set_index("final_cik")["org_name"]
log("   largest-contributing parent: CIK %s (%s), %d source records across %d events"
    % (byp.index[0], nmz.get(byp.index[0]), byp.iloc[0], int((CAN["final_cik"] == byp.index[0]).sum())))

hdr("PART B3 — treatment and the pre-rule count at every level")
log("Pre-rule effective date: 2007-12-08 (scripts/224:63, RULE = pd.Timestamp('2007-12-08'))")
log(LED[["step", "N", "treated", "control", "treated_parent_ciks",
         "treated_corporate_families", "pre_rule_treated", "pre_rule_control"]].to_string(index=False))
log("")
log("control parent CIKs at the analysis sample: %d   (G %d minus treated clusters %d)"
    % (CS[CS[TREAT] == 0]["final_cik"].nunique(), CS["final_cik"].nunique(),
       CS[CS[TREAT] == 1]["final_cik"].nunique()))

hdr("PART B4 — treatment classification")


def clause(x):
    x = str(x)
    if x.startswith("Clause (a)"):
        return "clause 1 (direct registry match)"
    if x.startswith("Clause (b)"):
        return "clause 2 (adjudicated to treated)"
    if "CLAUSE-B CANDIDATE" in x:
        return "clause 2 candidate, NOT treated"
    if any(s in x for s in ("NOT treated", "Adjudicated untreated", "Excluded",
                            "No registry match", "Artifact system entities")):
        return "adjudication withheld treatment"
    return "no registry match (untreated default)"


for lbl, df in [("ALL 489 canonical", CAN), ("the 405 analysis events", CS)]:
    d = df.copy()
    d["_cl"] = d["treatment_evidence"].map(clause)
    log("")
    log("%s:" % lbl)
    log(pd.crosstab(d["_cl"], d[TREAT]).to_string())

tp = CS[CS[TREAT] == 1].groupby("final_cik").agg(
    org_name=("org_name", lambda s: s.mode().iloc[0]),
    treated_events=("org_name", "size"),
    name_variants=("org_name", "nunique"),
    evidence=("treatment_evidence", "first")).reset_index()
allp = CS.groupby("final_cik").agg(all_events=(TREAT, "size"),
                                   treated=(TREAT, "sum")).reset_index()
tp = tp.merge(allp, on="final_cik")
tp["control_events_same_cik"] = tp["all_events"] - tp["treated"]
tp["clause"] = tp["evidence"].map(clause)
tp = tp.sort_values("treated_events", ascending=False)
tp.to_csv(OUT / "treated_parents.csv", index=False)
log("")
log("Treated parent CIKs in the 405 (treated_parents.csv):")
log(tp[["final_cik", "org_name", "treated_events", "control_events_same_cik",
        "name_variants", "clause"]].to_string(index=False))

dish = CS[CS["org_name"].astype(str).str.contains("DISH", na=False)].copy()
dish_all = CAN[CAN["org_name"].astype(str).str.contains("DISH", na=False)].copy()
log("")
log("DISH line (gate 2020-07-01, scripts/154:129 date-conditional):")
for lbl, d in [("all canonical", dish_all), ("in the 405", dish)]:
    d = d.copy()
    d["bdt"] = pd.to_datetime(d["breach_date"])
    pre = d[d["bdt"] < pd.Timestamp("2020-07-01")]
    post = d[d["bdt"] >= pd.Timestamp("2020-07-01")]
    log("   %-14s before 2020-07-01: %d event(s), treated %d | on/after: %d event(s), treated %d"
        % (lbl, len(pre), int(pre[TREAT].sum()), len(post), int(post[TREAT].sum())))
if len(dish_all):
    log(dish_all[["org_name", "breach_date", TREAT]].to_string(index=False))

hdr("PART B5 — cluster structure")
g = CS.groupby("final_cik").size().sort_values(ascending=False)
G = CS["final_cik"].nunique()
G1 = CS[CS[TREAT] == 1]["final_cik"].nunique()
log("G = %d | G1 (clusters holding >=1 treated event) = %d | cluster-size CV = %.3f"
    % (G, G1, g.std(ddof=0) / g.mean()))
log("constants_essay3_v4.json F1_30_cluster_size_cv = %s (verbatim); G* = %s "
    "(f1_se_diagnostics.csv, verbatim)" % (CON.get("F1_30_cluster_size_cv"),
                                           SED["G_star"].iloc[0]))
log("events per cluster: mean %.2f median %.1f max %d | singleton clusters %d"
    % (g.mean(), g.median(), g.max(), int((g == 1).sum())))
tr = set(CS[CS[TREAT] == 1]["final_cik"])
log("")
log("clusters with >= 5 events:")
nm2 = CS.drop_duplicates("final_cik").set_index("final_cik")["org_name"]
for c, k in g[g >= 5].items():
    log("   %-9s %-38s %3d events  %s" % (c, str(nm2.get(c))[:38], k,
                                          "TREATED" if c in tr else "control"))
mix = allp[(allp["treated"] > 0) & (allp["all_events"] > allp["treated"])]
log("")
log("MIXED clusters (hold both treated and control events): %d" % len(mix))
for _, r in mix.iterrows():
    sub = CS[(CS["final_cik"] == r["final_cik"]) & (CS[TREAT] == 0)]
    log("   %-9s %-30s %2d treated / %2d control  (untreated: %s)"
        % (r["final_cik"], str(nm2.get(r["final_cik"]))[:30], r["treated"],
           r["all_events"] - r["treated"], "; ".join(sorted(set(sub["org_name"].astype(str))))[:60]))
nt = len(CS[CS[TREAT] == 1])
for cik, lab in [(1283699, "T-Mobile"), (101830, "Sprint")]:
    k = int(((CS["final_cik"] == cik) & (CS[TREAT] == 1)).sum())
    log("%s (%d): %d treated events = %.1f%% of the %d treated" % (lab, cik, k, 100 * k / nt, nt))
comb = int(((CS["final_cik"].isin([1283699, 101830])) & (CS[TREAT] == 1)).sum())
log("combined: %d = %.1f%% of treated" % (comb, 100 * comb / nt))

# =============================================================== PART C
hdr("PART C1 — breach-type mix (PRC labels), counts and column shares")
bt = pd.crosstab(CS["breach_type"], CS[TREAT])
bt.columns = ["control", "treated"]
bt["control_share"] = (bt["control"] / bt["control"].sum()).round(4)
bt["treated_share"] = (bt["treated"] / bt["treated"].sum()).round(4)
log(bt.sort_values("treated", ascending=False).to_string())
log("(no test performed)")

hdr("PART C2 — anchors")
rows_c2 = []
for lbl, d in grp(A):
    same = int((d["bdt"] == d["rdt"]).sum())
    lag = (d["rdt"] - d["bdt"]).dt.days
    bd180 = int((d["bdt"] + pd.Timedelta(days=180) < d["rdt"]).sum())
    log("%-8s n=%3d | breach==notification %3d (%.3f) | lag median %5.1f IQR [%.0f, %.0f] max %5d "
        "| breach-anchored 180d window closes before notification %3d (%.3f)"
        % (lbl, len(d), same, same / len(d), lag.median(), lag.quantile(.25),
           lag.quantile(.75), lag.max(), bd180, bd180 / len(d)))
    rows_c2.append(dict(part="C2", group=lbl, n=len(d), same_day=same,
                        same_day_share=round(same / len(d), 4),
                        lag_median=lag.median(), lag_q25=lag.quantile(.25),
                        lag_q75=lag.quantile(.75), lag_max=int(lag.max()),
                        bd180_before_rd=bd180, bd180_share=round(bd180 / len(d), 4)))
log("(cross-check: 224's E3 anchor diagnostic prints the same two shares)")

hdr("PART C3 — covariates by group (no balance tests, by instruction)")
rows_c3 = []
for v in CTRL7:
    t_, c_ = A.loc[A[TREAT] == 1, v].astype(float), A.loc[A[TREAT] == 0, v].astype(float)
    sp = np.sqrt((t_.var(ddof=1) + c_.var(ddof=1)) / 2)
    std = (t_.mean() - c_.mean()) / sp if sp > 0 else np.nan
    log("%-26s treated  mean %9.4f sd %8.4f med %9.4f min %9.4f max %9.4f"
        % (v, t_.mean(), t_.std(ddof=1), t_.median(), t_.min(), t_.max()))
    log("%-26s control  mean %9.4f sd %8.4f med %9.4f min %9.4f max %9.4f  | std.diff %+.4f"
        % ("", c_.mean(), c_.std(ddof=1), c_.median(), c_.min(), c_.max(), std))
    for lbl, s in (("treated", t_), ("control", c_)):
        rows_c3.append(dict(part="C3", variable=v, group=lbl, n=len(s), mean=round(s.mean(), 6),
                            sd=round(s.std(ddof=1), 6), median=round(s.median(), 6),
                            min=round(s.min(), 6), max=round(s.max(), 6),
                            std_diff=round(std, 6)))
log("")
for lbl, d in grp(A):
    b = d["baseline_exec_rate_py_rd"].astype(float)
    log("baseline departure rate, %-7s: mean %.4f median %.4f | share at zero %.4f (%d of %d)"
        % (lbl, b.mean(), b.median(), (b == 0).mean(), int((b == 0).sum()), len(b)))
    rows_c3.append(dict(part="C3-baseline", variable="baseline_exec_rate_py_rd", group=lbl,
                        n=len(b), mean=round(b.mean(), 6), median=round(b.median(), 6),
                        share_zero=round((b == 0).mean(), 4)))

hdr("PART C4 — two-digit SIC cells (Compustat header SIC, freeze exception 1)")
log("f3_sic2_cells.csv, verbatim (not recomputed):")
log(SIC.to_string(index=False))
log("")
log("cells containing >=1 treated event: %d of %d" % (int((SIC["treated"] > 0).sum()), len(SIC)))
unc = A[A["sic2"].astype(str).isin(["unclassified", "nan"])]
log("events with no Compustat header SIC ('unclassified'): %d (treated %d / control %d)"
    % (len(unc), int(unc[TREAT].sum()), int((unc[TREAT] == 0).sum())))
pd.DataFrame(rows_c2 + rows_c3).to_csv(OUT / "descriptives.csv", index=False)

# =============================================================== PART E
hdr("PART E1/E2/E3 — outcome descriptives, notification anchor")
rows_e = []
for w in (30, 90, 180):
    log("")
    log("--- %d days ---" % w)
    for lbl, d in grp(A):
        n = len(d)
        any5 = int(d["any_502_%d_rd" % w].sum())
        ex = int(d["exec_departure_%d_rd" % w].sum())
        ceo = int(d["ceo_departure_%d_rd" % w].sum())
        dir_ = int(d["director_departure_%d_rd" % w].sum())
        both = int(((d["any_502_%d_rd" % w] == 1) & (d["exec_departure_%d_rd" % w] == 0)).sum())
        log("  %-8s n=%3d | any 5.02 %3d (%.4f) | exec %3d (%.4f) | CEO %2d (%.4f) | "
            "director-only %2d (%.4f) | 5.02 but NO exec %3d (%.4f of n)"
            % (lbl, n, any5, any5 / n, ex, ex / n, ceo, ceo / n, dir_, dir_ / n, both, both / n))
        rows_e.append(dict(part="E1/E2", window=w, group=lbl, n=n, any_502=any5,
                           any_502_rate=round(any5 / n, 4), exec_dep=ex,
                           exec_rate=round(ex / n, 4), ceo_dep=ceo, ceo_rate=round(ceo / n, 4),
                           director_only=dir_, director_rate=round(dir_ / n, 4),
                           filing_no_exec=both, filing_no_exec_share_of_n=round(both / n, 4),
                           filing_no_exec_share_of_filers=round(both / any5, 4) if any5 else np.nan))
log("")
log("E3 CEO-only against the pre-specified 10-event rule — f5_ceo.csv, verbatim:")
log(F5.to_string(index=False))

hdr("PART E4 — days from notification to first executive departure")
for w_lbl, col in [("180d window", "days_to_first_exec_departure_rd")]:
    for lbl, d in grp(A):
        s = d[col].dropna().astype(float)
        if not len(s):
            log("%-8s: none" % lbl)
            continue
        log("%-8s n with a departure %3d | min %4.0f p25 %5.1f median %5.1f p75 %5.1f max %4.0f mean %6.2f"
            % (lbl, len(s), s.min(), s.quantile(.25), s.median(), s.quantile(.75), s.max(), s.mean()))
        rows_e.append(dict(part="E4", window=180, group=lbl, n=len(s),
                           days_min=s.min(), days_p25=s.quantile(.25), days_median=s.median(),
                           days_p75=s.quantile(.75), days_max=s.max(), days_mean=round(s.mean(), 3)))
pd.DataFrame(rows_e).to_csv(OUT / "outcomes.csv", index=False)

# =============================================================== PART F
hdr("PART F1 — inference ladder, verbatim from f1_ladder.csv + f1_se_diagnostics.csv")
log(F1.to_string(index=False))
log("")
log("HC3 is DISQUALIFIED as an inferential rung (it ignores within-parent clustering); "
    "CV3 and the restricted wild cluster bootstrap are the frame.")

hdr("PART F2 — scale: beta against the control rate, and the MDE")
rows_f = []
for w in (30, 90, 180):
    r = F1[F1["window"] == w].iloc[0]
    sd = SED[SED["window"] == w].iloc[0]
    cr = float(A.loc[A[TREAT] == 0, "exec_departure_%d_rd" % w].mean())
    mde = float(sd["mde80"])
    log("%3dd | beta %+.4f | control rate %.4f | beta/control %+.3f | MDE80 %.4f | "
        "MDE/control %.2f | MDE exceeds control rate: %s"
        % (w, r["coef"], cr, r["coef"] / cr, mde, mde / cr, "YES" if mde > cr else "no"))
    rows_f.append(dict(part="F2", window=w, coef=r["coef"], control_rate=round(cr, 4),
                       coef_over_control=round(r["coef"] / cr, 4), mde80=mde,
                       mde_over_control=round(mde / cr, 4), mde_exceeds_control=bool(mde > cr)))

hdr("PART F5 — internal consistency assertions (NEW; assertion only, fits nothing)")
# f1_ladder.csv stores coef and se_cv3 ROUNDED to 4 dp, so recomputing t = coef/se from
# them cannot reproduce p to better than the precision those roundings allow. The honest
# assertion is therefore an INTERVAL test: take the half-ulp box around the printed coef
# and SE, propagate it to p, and require the committed p to lie inside. A committed p
# outside that box is a real inconsistency; one inside is arithmetic, not error.
ok = True
for w in (30, 90, 180):
    r = F1[F1["window"] == w].iloc[0]
    df = G - 1
    t_calc = r["coef"] / r["se_cv3"]
    p_calc = 2 * (1 - stats.t.cdf(abs(t_calc), df))
    dp = abs(p_calc - r["p_cv3"])
    hb, hs = 5e-5, 5e-5                     # half of the last printed digit
    ts = [abs(b) / s for b in (r["coef"] - hb, r["coef"] + hb)
          for s in (r["se_cv3"] - hs, r["se_cv3"] + hs)]
    ps = sorted(2 * (1 - stats.t.cdf(t, df)) for t in ts)
    inside = ps[0] - 1e-9 <= r["p_cv3"] <= ps[-1] + 1e-9
    log("%3dd | t = beta/SE = %+.4f | p from t (df=%d) = %.4f vs committed %.4f | dp = %.5f"
        % (w, t_calc, df, p_calc, r["p_cv3"], dp))
    log("       rounding box on (coef, SE) implies p in [%.4f, %.4f]; committed p inside: %s"
        % (ps[0], ps[-1], inside))
    if not inside:
        ok = False
        log("   *** committed p lies OUTSIDE the rounding box - real inconsistency ***")
    lo, hi = r.get("ci_wcr_lo"), r.get("ci_wcr_hi")
    if pd.notna(lo) and pd.notna(hi):
        excl = (lo > 0) or (hi < 0)
        sig = r["p_wcr"] < .05
        log("   WCR CI [%+.4f, %+.4f] excludes zero: %s | p_wcr %.4f < .05: %s | agree: %s"
            % (lo, hi, excl, r["p_wcr"], sig, excl == sig))
        if excl != sig:
            ok = False
            log("   *** bootstrap CI / p disagreement ***")
    rows_f.append(dict(part="F5", window=w, t_recomputed=round(t_calc, 6),
                       p_recomputed=round(p_calc, 6), p_committed=r["p_cv3"],
                       abs_diff=round(dp, 8), df=df))
log("")
log("F5 RESULT: %s" % ("all assertions hold" if ok else "AT LEAST ONE ASSERTION FAILED"))
pd.DataFrame(rows_f).to_csv(OUT / "primary.csv", index=False)

# =============================================================== PART G
hdr("PART G1 — placebo (t0-180d, t0], verbatim from f4_placebo.csv")
log(F4.to_string(index=False))
log("")
for lbl, d in grp(A):
    p = d["placebo_exec_departure_rd"].astype(float)
    log("placebo rate, %-7s: %d of %d = %.4f" % (lbl, int(p.sum()), len(p), p.mean()))

hdr("PART G2/G3 — 27 sensitivities and the test ledger, verbatim")
S3 = F3.merge(IT[IT["family"] == "sensitivities"][["test", "p_bh"]].assign(
    window=lambda x: [int(t.split()[-1].rstrip("d")) for t in x["test"]],
    sensitivity=lambda x: [" ".join(t.split()[1:-1]) for t in x["test"]]),
    on=["window", "sensitivity"], how="left")
log(S3[["window", "sensitivity", "n", "coef", "se_cv3", "p_cv3", "p_wcr", "p_bh",
        "row_type"]].to_string(index=False))
S3.to_csv(OUT / "sensitivities.csv", index=False)
log("")
log("Test ledger by family (i_tests.csv, verbatim):")
for fam, gg in IT.groupby("family"):
    log("  %-14s %2d test(s) | raw CV3 p min %.4f max %.4f | BH min %.4f"
        % (fam, len(gg), gg["p"].min(), gg["p"].max(), gg["p_bh"].min()))
log("  TOTAL %d tests (constants n_tests = %s)" % (len(IT), CON.get("n_tests")))

hdr("PART G4 — leave-one-cluster-out, verbatim from f3_loco.csv + f1_cv3_variance_shares.csv")
log(LOCO.to_string(index=False))
log("")
for w in (30, 90, 180):
    v = VAR[VAR["window"] == w].sort_values("share", ascending=False).head(10) \
        if "share" in VAR.columns else VAR.head(0)
    log("top CV3 jackknife variance shares, %dd:" % w)
    log(v.to_string(index=False))
LOCO.to_csv(OUT / "loo.csv", index=False)

# =============================================================== PART H
hdr("PART H — T-Mobile case rows (CIK 1283699); health flag omitted by instruction")
TM = A[A["final_cik"] == 1283699].copy().sort_values("bdt")
cols = ["org_canon", "breach_date", "reported_date", TREAT, "permno",
        "placebo_exec_departure_rd", "exec_departure_30_rd", "exec_departure_90_rd",
        "exec_departure_180_rd", "ceo_departure_180_rd", "director_departure_180_rd",
        "exec_departure_nopre_180_rd", "days_to_first_exec_departure_rd",
        "baseline_exec_departures_rd", "any_502_180_rd"]
TMc = TM[[c for c in cols if c in TM.columns]]
log("T-Mobile events in the 405: %d" % len(TM))
log(TMc.to_string(index=False))
TMc.to_csv(OUT / "tmobile_case.csv", index=False)
log("")
log("HEALTH FLAG OMITTED from tmobile_case.csv by instruction (known false positive "
    "from benefit-continuation language).")
log("")
log("T-Mobile totals on this build:")
for w in (30, 90, 180):
    log("  %3dd: events with an exec departure %2d of %d | CEO %d | pre-announced-excluded exec %d"
        % (w, int(TM["exec_departure_%d_rd" % w].sum()), len(TM),
           int(TM["ceo_departure_%d_rd" % w].sum()),
           int(TM["exec_departure_nopre_%d_rd" % w].sum())))
log("  placebo window (t0-180d, t0]: %d of %d events carry an exec departure"
    % (int(TM["placebo_exec_departure_rd"].sum()), len(TM)))

(OUT / "242_pull.log").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\nwritten: " + ", ".join(sorted(p.name for p in OUT.glob("*"))))

# =============================================================== PART D (validation)
hdr("PART D3 — four validation rounds, stacked verbatim from their committed agreement files")
SRC = [("round 1 (80 = 50 calibration + 30 random)", Q2 / "d3_agreement.csv"),
       ("round 2 (30 out-of-sample)", Q2 / "d3_r2_agreement.csv"),
       ("recall audit (80 stratified 40/40)", Q2 / "d3_audit_agreement.csv"),
       ("v4 final (30 new documents)", V4 / "238_new_document_agreement.csv")]
frames = []
for lbl, p in SRC:
    if not Path(p).exists():
        log("%-42s MISSING: %s" % (lbl, p))
        continue
    d = pd.read_csv(p)
    d.insert(0, "round", lbl)
    d.insert(1, "source_file", str(p).replace("\\", "/"))
    frames.append(d)
    log("")
    log("--- %s   [%s] ---" % (lbl, p))
    log(d.drop(columns=["round", "source_file"]).to_string(index=False))
if frames:
    VALL = pd.concat(frames, ignore_index=True)
    VALL.to_csv(OUT / "validation.csv", index=False)
    log("")
    log("validation.csv: %d rows across %d rounds" % (len(VALL), len(frames)))

log("")
log("Stratified round, recall by stratum (d3_audit_recall_by_stratum.csv, verbatim):")
RS = pd.read_csv(Q2 / "d3_audit_recall_by_stratum.csv")
log(RS[RS["field"] == "exec departure (A)"].to_string(index=False))

hdr("PART D4 — the exact recall values fed to the three recall-corrected sensitivities")
rr = RS[(RS["field"] == "exec departure (A)") & (RS["scoring"] == "PRIMARY (verified)")].set_index("stratum")
log("source: outputs/essay3_q2/d3_audit_recall_by_stratum.csv, selected at scripts/227:239-240,248")
for g in ("treated", "control"):
    log("   %-8s recall %.4f  CI95 %s" % (g, rr.loc[g, "recall"], rr.loc[g, "recall_ci95"]))
log("")
log("   row 1 (point)        r_T = %.3f  r_C = %.3f" % (rr.loc["treated", "recall"], rr.loc["control", "recall"]))
lo_t, hi_t = [float(x) for x in rr.loc["treated", "recall_ci95"].strip("[]").split(", ")]
lo_c, hi_c = [float(x) for x in rr.loc["control", "recall_ci95"].strip("[]").split(", ")]
log("   row 2 (T low/C high) r_T = %.3f  r_C = %.3f   BOUNDING EXERCISE" % (lo_t, hi_c))
log("   row 3 (T high/C low) r_T = %.3f  r_C = %.3f   BOUNDING EXERCISE" % (hi_t, lo_c))
log("   applied at scripts/227:269 as y_corr = y / r_group; NO cap at 1; NO precision adjustment.")

(OUT / "242_pull.log").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\nvalidation section appended")
