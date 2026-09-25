"""
ESSAY 3 APPENDIX — TABLES 1-11
=============================================================================
    python scripts/245_essay3_appendix.py

FORMATTING ONLY. No estimation, no new statistic, no edit to any existing script or
output. Every numeric cell is read from a committed CSV and then rounded, converted to
percentage points / percent, or printed as a ratio the source CSV already carries.
Counts are summed only for total rows, and every total is asserted against a committed
total.

Document shape follows outputs/ESSAY2_APPENDIX.md and scripts/178 (a .md for the
repository record plus a .docx for the dissertation, title -> sections -> tables ->
Notes). Cell conventions follow Query 5's APA 7 rules, which supersede Essay 2's
unrounded cells: p to three decimals with no leading zero, coefficients and SEs and CIs
and MDEs in percentage points to two decimals, rates in percent to one decimal, counts
with thousands separators, U+2212 for minus.

Reads  : outputs/essay3_q4/*.csv, outputs/essay3_q3/*.csv,
         outputs/essay3_appendix/descriptive_counts.csv (scripts/246),
         outputs/essay3_q4/tmobile_502_text.md,
         Data/processed/rebuild/stage2_signed.csv (Table 1 Panel B grades)
Writes : outputs/essay3_appendix/ESSAY3_APPENDIX_TABLES.md
         outputs/essay3_appendix/ESSAY3_APPENDIX_TABLES.docx
         outputs/essay3_appendix/text_figures_check.csv
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Q3 = Path("outputs/essay3_q3")
Q4 = Path("outputs/essay3_q4")
OUT = Path("outputs/essay3_appendix")
OUT.mkdir(parents=True, exist_ok=True)

MINUS = "−"
ASSERT, NOTREG, MD = [], [], []


def check(name, ok, detail=""):
    ASSERT.append((name, bool(ok), detail))


def notreg(where, what):
    NOTREG.append((where, what))


def need(p):
    p = Path(p)
    if not p.exists():
        sys.exit("ABORT 245: missing committed input " + str(p))
    return p


# ------------------------------------------------------------------ formatters
def m(s):
    return str(s).replace("-", MINUS)


def pp(x, nd=2):
    """proportion -> percentage points, nd decimals, U+2212 minus."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)) or pd.isna(x):
        return ""
    return m(("%." + str(nd) + "f") % (float(x) * 100.0))


def pct(x, nd=1):
    if x is None or pd.isna(x):
        return ""
    return m(("%." + str(nd) + "f") % (float(x) * 100.0))


def p3(x):
    """three decimals, no leading zero."""
    if x is None or pd.isna(x):
        return ""
    s = "%.3f" % float(x)
    return s[1:] if s.startswith("0.") else m(s)


def k3(x):
    return p3(x)


def n0(x):
    if x is None or pd.isna(x) or str(x) == "":
        return ""
    return "{:,}".format(int(float(x)))


def f2(x, nd=2):
    if x is None or pd.isna(x):
        return ""
    return m(("%." + str(nd) + "f") % float(x))


def pct_from(num, den, nd=1):
    """Percent computed from the COUNT and its DENOMINATOR, never from a stored,
    already-rounded proportion. table04/table06 store proportions to 4 dp, and
    re-rounding those to 1 dp loses the third digit (0.2905 -> 29.0, where the raw
    86/296 = 29.0541 -> 29.1). Counts are exact, so this reproduces the Results text."""
    if num is None or den in (None, 0) or pd.isna(num) or pd.isna(den):
        return ""
    return m(("%." + str(nd) + "f") % (100.0 * float(num) / float(den)))


def ci_pp(lo, hi):
    if pd.isna(lo) or pd.isna(hi):
        return ""
    return "[%s, %s]" % (pp(lo), pp(hi))


def ci_str(s):
    """'[0.822, 0.999]' -> '[.822, .999]' with U+2212 handling."""
    if pd.isna(s) or not str(s).strip() or str(s).startswith("n/a"):
        return ""
    t = str(s).strip()
    out = []
    for tok in re.findall(r"-?\d*\.?\d+", t):
        v = float(tok)
        out.append(p3(v) if abs(v) < 1 else f2(v, 3))
    return "[%s, %s]" % (out[0], out[1]) if len(out) == 2 else t


# ------------------------------------------------------------------ sources
T01 = pd.read_csv(need(Q4 / "table01.csv"))
T02 = pd.read_csv(need(Q4 / "table02.csv"))
T03 = pd.read_csv(need(Q4 / "table03.csv"))
T04 = pd.read_csv(need(Q4 / "table04.csv"))
T05 = pd.read_csv(need(Q4 / "table05.csv"))
T06 = pd.read_csv(need(Q4 / "table06.csv"))
T07 = pd.read_csv(need(Q4 / "table07.csv"))
T08 = pd.read_csv(need(Q4 / "table08.csv"))
T09 = pd.read_csv(need(Q4 / "table09.csv"))
T10 = pd.read_csv(need(Q4 / "table10.csv"))
T11 = pd.read_csv(need(Q4 / "table11.csv"))
BCC = pd.read_csv(need(Q4 / "b_control_coefficients.csv"))
CLG = pd.read_csv(need(Q4 / "c_logit_diagnostics.csv"))
LAD = pd.read_csv(need("outputs/essay3_v4/f1_ladder.csv"))
S2 = pd.read_csv(need("Data/processed/rebuild/stage2_signed.csv"), low_memory=False)
ATTR = pd.read_csv(need(Q3 / "attrition.csv"))
DC = pd.read_csv(need(OUT / "descriptive_counts.csv")).set_index("key")["value"].to_dict()
SUB = ATTR[ATTR["step"].str.strip().str.startswith("of which", na=False)].rename(
    columns={"treated": "treated_events", "control": "control_events"})
TMTXT = re.sub(r"\s+", " ", need(Q4 / "tmobile_502_text.md").read_text(encoding="utf-8"))

TABLES = []          # (number, title, [(kind, payload)])


def add(num, title, blocks, note):
    TABLES.append(dict(num=num, title=title, blocks=blocks, note=note))


# =============================================================== TABLE 1
lead = T01[T01["treated_events"].notna() | T01["step"].str.startswith("PRC", na=False)]
rows1a, prevN = [], None
for _, r in T01.iterrows():
    if str(r["step"]).startswith("  of which"):
        continue
    rows1a.append([str(r["step"]), n0(r["N"]), n0(r.get("treated_events")),
                   n0(r.get("control_events")), n0(r.get("treated_parent_ciks")),
                   n0(r.get("pre_rule_treated")), n0(r.get("pre_rule_control"))])
    if "CRSP" in str(r["step"]):
        sub = SUB
        for _, s in sub.iterrows():
            lab = ("Identity-gate rejections" if "identity" in str(s["step"]).lower()
                   else "No acceptable security link")
            rows1a.append(["    " + lab, n0(s["N"]), n0(s["treated_events"]),
                           n0(s["control_events"]), "", "", ""])
T1A = pd.DataFrame(rows1a, columns=["Step", "N", "Treated events", "Control events",
                                    "Treated parent CIKs", "Pre-rule treated",
                                    "Pre-rule control"])
GRADE_LABEL = {
    "VERIFIED": "Verified",
    "VERIFIED-GATE1": "Verified at Gate 1",
    "VERIFIED-REASONING": "Verified by reasoning",
    "ADJUDICATED": "Adjudicated",
    "AMBIGUOUS": "Unresolved ambiguity",
    "EXCLUDED-UNRESOLVED": "No matching registrant or unresolved",
    "EXCLUDED-PRIVATE": "Private company",
    "EXCLUDED-PRIVATE-WINDOW": "Private during the breach window",
    "EXCLUDED-PRE-IPO": "Pre-IPO",
    "EXCLUDED-NO-US-LISTING": "No U.S. listing",
}
g = S2["final_grade"].value_counts()
T1B = pd.DataFrame([[GRADE_LABEL.get(k, k), n0(v)]
                    for k, v in g.items()] + [["Total", n0(g.sum())]],
                   columns=["Final resolution grade", "Records"])
check("T1 Panel B totals 1,054", int(g.sum()) == 1054, "got %d" % int(g.sum()))
ev = T01.dropna(subset=["treated_events"])
ev = ev[~ev["step"].str.startswith("  of which", na=False)]
check("T1 ledger closes (N never rises)",
      bool((T01[~T01["step"].str.startswith('  of which', na=False)]["N"].diff().dropna() <= 0).all()))
check("T1 treated + control == N at every populated step",
      bool((ev["treated_events"] + ev["control_events"] == ev["N"]).all()))
add(1, "Sample Construction From Notification Records to the Analysis Sample",
    [("Panel A: Attrition ledger", T1A), ("Panel B: Record resolution grades", T1B)],
    "*Note.* Panel A rows above the canonical-event line are at the RECORD level, where "
    "treatment is undefined; rows from the canonical event set down are at the EVENT level. "
    "Parent CIKs are the clustering unit. Records per event have a mean of "
    + DC["records_per_event_mean"] + " and a "
    "maximum of %s (%s, %s). Pre-rule is defined relative to the "
    % (DC["records_per_event_max"], DC["records_per_event_max_org"],
       DC["records_per_event_max_date"]) +
    "December 8, 2007 effective date of 47 CFR 64.2011. The two indented sub-rows decompose "
    "the 75 events lost at the security-link step. Sources: outputs/essay3_q4/table01.csv "
    "(Panel A, from outputs/essay3_v4/e_ledger.csv and outputs/rebuild_v4/"
    "v4_212_identity_review.csv); Data/processed/rebuild/stage2_signed.csv (Panel B); "
    "outputs/essay3_appendix/descriptive_counts.csv (records per event).")

# =============================================================== TABLE 2
t2 = T02.sort_values("treated_events", ascending=False)
T2A = pd.DataFrame([[n0(r["final_cik"]), str(r["org_name"]), n0(r["treated_events_clause1"]),
                     n0(r["treated_events_clause2"]), n0(r["treated_events"]),
                     n0(r["control_events_same_cik"])] for _, r in t2.iterrows()]
                   + [["Total", "", n0(t2["treated_events_clause1"].sum()),
                       n0(t2["treated_events_clause2"].sum()), n0(t2["treated_events"].sum()),
                       n0(t2["control_events_same_cik"].sum())]],
                   columns=["CIK", "Name", "Clause 1 events", "Clause 2 events",
                            "Total treated", "Control events on same CIK"])
check("T2 treated total == 109", int(t2["treated_events"].sum()) == 109)
check("T2 clause totals == 70 / 39",
      int(t2["treated_events_clause1"].sum()) == 70 and int(t2["treated_events_clause2"].sum()) == 39)
lad30 = LAD[LAD["window"] == 30].iloc[0]
mixed = t2[t2["control_events_same_cik"] > 0]["org_name"].tolist()
tm = int(t2[t2["final_cik"] == 1283699]["treated_events"].iloc[0])
sp = int(t2[t2["final_cik"] == 101830]["treated_events"].iloc[0])
T2B = pd.DataFrame([
    ["Parent CIKs (G)", n0(lad30["G"])],
    ["Treated clusters (G1)", n0(lad30["G1"])],
    ["Effective clusters (G*)", f2(lad30["G_star"], 1)],
    ["Cluster-size coefficient of variation", f2(lad30["cluster_size_cv"], 3)],
    ["Singleton clusters", DC["singleton_clusters"]],
    ["Largest cluster", "%s (CIK %s): %s events (%s%%)"
     % (DC["largest_cluster_name"], DC["largest_cluster_cik"],
        DC["largest_cluster_events"], DC["largest_cluster_share"])],
    ["Mixed clusters (hold treated and control events)", "; ".join(mixed)],
    ["T-Mobile share of treated events", "%s of %s (%s%%)" % (tm, 109, pct(tm / 109))],
    ["T-Mobile and Sprint share of treated events",
     "%s of %s (%s%%)" % (tm + sp, 109, pct((tm + sp) / 109))]],
    columns=["Cluster statistic", "Value"])
add(2, "Treated Parent CIKs and Cluster Structure",
    [("Panel A: Treated parent CIKs", T2A), ("Panel B: Cluster structure", T2B)],
    "*Note.* Sample level is EVENTS within parent CIKs; inference clusters on parent CIK. "
    "Clause 1 is a direct Form 499 registry match; clause 2 is an adjudicated holding or "
    "parent-brand relationship. Eight CIKs carry clause 1 events and eight carry clause 2 "
    "events; three carry both (AT&T, Sprint, Comcast), so the two counts reconcile to 13 "
    "CIKs. T-Mobile (1283699) and Sprint (101830) are SEPARATE parent CIKs and are clustered "
    "separately; they are one corporate family only in the entity count (12). Twilio and "
    "GoDaddy enter by direct registry match, not by the network-operator criterion. Both "
    "DISH events postdate July 1, 2020, the Boost Mobile divestiture that the date-conditional "
    "rule turns on. G* is the effective number of clusters. Sources: "
    "outputs/essay3_q4/table02.csv; outputs/essay3_v4/f1_ladder.csv; "
    "outputs/essay3_appendix/descriptive_counts.csv (singleton and largest-cluster rows).")

# =============================================================== TABLE 3
BT = {"HACK": "Hacking or malware", "INSD": "Insider", "PHYS": "Physical records",
      "PORT": "Portable device", "DISC": "Unintended disclosure",
      "HACK+INSD": "Hacking and insider", "HACK+PORT": "Hacking and portable device",
      "DISC+HACK": "Unintended disclosure and hacking"}
t3 = T03.sort_values("treated_events", ascending=False)
_t3T, _t3C = t3["treated_events"].sum(), t3["control_events"].sum()
T3 = pd.DataFrame([[str(r["breach_type"]), n0(r["treated_events"]),
                    pct_from(r["treated_events"], _t3T), n0(r["control_events"]),
                    pct_from(r["control_events"], _t3C)] for _, r in t3.iterrows()]
                  + [["Total", n0(t3["treated_events"].sum()), "100.0",
                      n0(t3["control_events"].sum()), "100.0"]],
                  columns=["PRC breach type", "Treated n", "Treated %", "Control n", "Control %"])
check("T3 totals == 109 / 296",
      int(t3["treated_events"].sum()) == 109 and int(t3["control_events"].sum()) == 296)
add(3, "Breach Type by Treatment Group",
    [("", T3)],
    "*Note.* Sample level is EVENTS (109 treated, 296 control). Breach types are the Privacy "
    "Rights Clearinghouse's own labels, carried through unchanged: HACK = "
    + "; ".join("%s = %s" % (k, v) for k, v in BT.items())
    + ". Combined codes arise where an event collapses source records of more than one type. "
      "Column percentages sum to 100 within group. No test is performed. Source: "
      "outputs/essay3_q4/table03.csv.")

# =============================================================== TABLE 4
VLAB = {"prior_breaches_1yr": "Prior breaches, 1 year", "health_breach": "Health information",
        "firm_size_log": "Firm size (log total assets)", "leverage": "Leverage", "roa": "Return on assets",
        "baseline_exec_rate_py_rd": "Baseline departure rate (per year)",
        "prior12m_mktadj_ret_rd": "Prior 12-month market-adjusted return"}
c3 = T04[T04["part"] == "C3"]
rows = []
for v in VLAB:
    t = c3[(c3["variable"] == v) & (c3["group"] == "treated")].iloc[0]
    c = c3[(c3["variable"] == v) & (c3["group"] == "control")].iloc[0]
    rows.append([VLAB[v], "%s (%s)" % (f2(t["mean"], 4), f2(t["sd"], 4)),
                 "%s (%s)" % (f2(c["mean"], 4), f2(c["sd"], 4)), f2(t["std_diff"], 3)])
T4A = pd.DataFrame(rows, columns=["Covariate", "Treated M (SD)", "Control M (SD)",
                                  "Standardized difference"])
ft = c3[(c3["variable"] == "firm_size_log") & (c3["group"] == "treated")].iloc[0]
fc = c3[(c3["variable"] == "firm_size_log") & (c3["group"] == "control")].iloc[0]
T4B = pd.DataFrame([
    ["Treated range", "[%s, %s]" % (f2(ft["min"], 4), f2(ft["max"], 4))],
    ["Control range", "[%s, %s]" % (f2(fc["min"], 4), f2(fc["max"], 4))],
    ["Control events inside the treated range",
     "%s of %s (%s%%)" % (DC["control_in_treated_range_n"],
                          DC["control_in_treated_range_denom"],
                          DC["control_in_treated_range_pct"])],
    ["Treated events inside the control range",
     "%s of %s (%s%%)" % (DC["treated_in_control_range_n"],
                          DC["treated_in_control_range_denom"],
                          DC["treated_in_control_range_pct"])]],
    columns=["Common support, log total assets", "Value"])
c2 = T04[T04["part"] == "C2"]
ct, cc = c2[c2["group"] == "treated"].iloc[0], c2[c2["group"] == "control"].iloc[0]
T4C = pd.DataFrame([
    ["Breach date equals notification date",
     "%s%% (%s)" % (pct_from(ct["same_day"], ct["n"]), n0(ct["same_day"])),
     "%s%% (%s)" % (pct_from(cc["same_day"], cc["n"]), n0(cc["same_day"]))],
    ["Notification lag, median days", n0(ct["lag_median"]), n0(cc["lag_median"])],
    ["Notification lag, IQR days", "[%s, %s]" % (n0(ct["lag_q25"]), n0(ct["lag_q75"])),
     "[%s, %s]" % (n0(cc["lag_q25"]), n0(cc["lag_q75"]))],
    ["Breach-anchored 180-day window closes before notification",
     "%s%% (%s)" % (pct_from(ct["bd180_before_rd"], ct["n"]), n0(ct["bd180_before_rd"])),
     "%s%% (%s)" % (pct_from(cc["bd180_before_rd"], cc["n"]), n0(cc["bd180_before_rd"]))]],
    columns=["Anchor statistic", "Treated", "Control"])
add(4, "Covariate Balance, Common Support, and Date Anchors",
    [("Panel A: Covariates", T4A), ("Panel B: Common support", T4B),
     ("Panel C: Date anchors", T4C)],
    "*Note.* Sample level is EVENTS (109 treated, 296 control). The standardized difference is "
    "the treated mean minus the control mean divided by the pooled standard deviation; the 0.1 "
    "benchmark follows Austin (2009). No balance tests are reported, because they would add "
    "unplanned hypothesis tests to the ledger. Panel B shows that common support is "
    "substantial: the imbalance in firm size is a shift in means, not a failure of overlap. "
    "Sources: outputs/essay3_q4/table04.csv, from outputs/essay3_q3/descriptives.csv; "
    "outputs/essay3_appendix/descriptive_counts.csv (Panel B).")

# =============================================================== TABLE 5
FLD = {"exec_departure": "Executive departure", "exec departure (A)": "Executive departure",
       "exec departure (A: any)": "Executive departure",
       "ceo_departure": "Chief executive departure", "CEO departure": "Chief executive departure",
       "CEO departure (A: any)": "Chief executive departure",
       "director_only_departure": "Director-only departure",
       "director-only departure": "Director-only departure"}
RLAB = {"round 1 (80 = 50 calibration + 30 random)": "Round 1 (earlier classifier version)",
        "round 2 (30 out-of-sample)": "Round 2 (out-of-sample)",
        "recall audit (80 stratified 40/40)": "Stratified recall audit",
        "v4 final (30 new documents)": "Final round (new documents)"}
rows = []
for rnd, lab in RLAB.items():
    g = T05[(T05["round"] == rnd) & (T05["panel"] == "agreement")]
    if rnd.startswith("round 1"):
        g = g[(g.get("variant") == "A") & (g.get("sample") == "all 80")]
    if rnd.startswith("recall"):
        g = g[g["scoring"] == "PRIMARY (verified)"]
    if rnd.startswith("v4"):
        g = g[g["field"].astype(str).str.startswith("PRIMARY (verified) | ")]
    for _, r in g.iterrows():
        raw = str(r["field"]).replace("PRIMARY (verified) | ", "")
        if raw not in FLD:
            continue
        rows.append([lab, n0(r["n"]), FLD[raw], k3(r["kappa"]),
                     ("%s %s" % (p3(r["precision"]), ci_str(r.get("precision_ci95", "")))).strip(),
                     ("%s %s" % (p3(r["recall"]), ci_str(r.get("recall_ci95", "")))).strip()])
T5A = pd.DataFrame(rows, columns=["Round", "N scored", "Field", "κ",
                                  "Precision [95% CI]", "Recall [95% CI]"])
sp_ = T05[(T05["panel"] == "stratified recall") & (T05["field"] == "exec departure (A)")
          & (T05["scoring"] == "PRIMARY (verified)")]
T5B = pd.DataFrame([[str(r["stratum"]).title(), n0(r["ref_Y"]), n0(r["tp"]), n0(r["fp"]), n0(r["fn"]),
                     "%s %s" % (p3(r["precision"]), ci_str(r["precision_ci95"])),
                     "%s %s" % (p3(r["recall"]), ci_str(r["recall_ci95"]))] for _, r in sp_.iterrows()],
                   columns=["Stratum", "Reference departures", "TP", "FP", "FN",
                            "Precision [95% CI]", "Recall [95% CI]"])
add(5, "Classifier Validation",
    [("Panel A: Four validation rounds", T5A),
     ("Panel B: Stratified recall audit, by treatment group", T5B)],
    "*Note.* Sample level is FILINGS. κ = Cohen's kappa; TP, FP, FN = true positives, false "
    "positives, false negatives. Reference codes were produced blind to the classifier: in "
    "rounds 1, 2 and the stratified audit the classifier's answers were sealed in a committed "
    "file before coding; in the final round the classifier had never been run on those "
    "documents and the reference codes were committed first. Round 1 scored an earlier "
    "classifier version. Confidence intervals are Clopper-Pearson. Unresolved rows are "
    "excluded under the primary scoring; the alternative scoring that forces them positive is "
    "in the source CSV. An empty cell means the field had no reference positives and no "
    "classifier positives, so the statistic is undefined. Sources: "
    "outputs/essay3_q4/table05.csv; outputs/essay3_q2/d3_audit_recall_by_stratum.csv.")

# =============================================================== TABLE 6
rows = []
for w in (30, 90, 180):
    for grp in ("treated", "control"):
        r = T06[(T06["window"] == w) & (T06["group"] == grp)].iloc[0]
        rows.append([n0(w), grp.title(), n0(r["n"]),
                     "%s (%s%%)" % (n0(r["any_502"]), pct_from(r["any_502"], r["n"])),
                     "%s (%s%%)" % (n0(r["exec_departure"]), pct_from(r["exec_departure"], r["n"])),
                     "%s (%s%%)" % (n0(r["ceo_departure"]), pct_from(r["ceo_departure"], r["n"])),
                     "%s (%s%%)" % (n0(r["director_only"]), pct_from(r["director_only"], r["n"]))])
T6A = pd.DataFrame(rows, columns=["Window (days)", "Group", "N", "Any Item 5.02 filing",
                                  "Executive departure", "Chief executive departure",
                                  "Director-only departure"])
rows = []
for w in (30, 90, 180):
    for grp in ("treated", "control", "POOLED"):
        r = T06[(T06["window"] == w) & (T06["group"] == grp)].iloc[0]
        rows.append([n0(w), "Pooled" if grp == "POOLED" else grp.title(),
                     n0(r["filing_no_exec"]),
                     "%s%% (%s of %s)" % (pct_from(r["filing_no_exec"], r["n"]),
                                          n0(r["filing_no_exec"]), n0(r["n"])),
                     "%s%% (%s of %s)" % (pct_from(r["filing_no_exec"], r["any_502"]),
                                          n0(r["filing_no_exec"]), n0(r["any_502"]))])
T6B = pd.DataFrame(rows, columns=["Window (days)", "Group", "Filing, no executive departure",
                                  "Over all events", "Over events with a filing"])
for w in (30, 90, 180):
    s = T06[T06["window"] == w]
    t_, c_, p_ = (s[s["group"] == g].iloc[0] for g in ("treated", "control", "POOLED"))
    check("T6 %3dd treated + control == pooled on every count" % w,
          all(int(t_[k]) + int(c_[k]) == int(p_[k]) for k in
              ("n", "any_502", "exec_departure", "ceo_departure", "director_only", "filing_no_exec")))
add(6, "Item 5.02 Filings and Disclosed Departures by Window",
    [("Panel A: Rates by window and group", T6A), ("Panel B: Crosswalk", T6B)],
    "*Note.* Sample level is EVENTS (109 treated, 296 control). The notification anchor is used "
    "throughout; a window is (t0, t0 + w] and excludes a filing dated on t0 itself. An Item 5.02 "
    "filing is NOT a departure: Item 5.02 also covers appointments, elections and compensatory "
    "arrangements, and Panel B shows how often a filing in the window reports no executive "
    "departure at all. The chief executive model requires at least 10 events in each group and "
    "is therefore not estimated at any window; the counts are reported for description only. "
    "Sources: outputs/essay3_q4/table06.csv; outputs/essay3_q4/_d5_crosswalk.csv.")

# =============================================================== TABLE 7
lad = T07[T07["panel"] == "ladder (treatment)"]
rows = []
for w in (30, 90, 180):
    r = lad[lad["window"] == w].iloc[0]
    rows.append([n0(w), "HC3 (disqualified; reported per the analysis plan)", pp(r["coef"]),
                 pp(r["se_hc3"]), p3(r["p_hc3"]), ""])
    rows.append(["", "CV1", pp(r["coef"]), pp(r["se_cv1"]), p3(r["p_cv1"]), ""])
    rows.append(["", "CV3", pp(r["coef"]), pp(r["se_cv3"]), p3(r["p_cv3"]),
                 ci_pp(r["ci_cv3_lo"], r["ci_cv3_hi"])])
    rows.append(["", "Wild cluster restricted bootstrap", pp(r["coef"]), "", p3(r["p_wcr"]),
                 ci_pp(r["ci_wcr_lo"], r["ci_wcr_hi"])])
    rows.append(["", "Control departure rate", pp(r["control_rate"]), "", "", ""])
    rows.append(["", "MDE (80% power, two-sided 5%)", pp(r["mde80"]), "", "", ""])
    rows.append(["", "MDE ÷ control rate", f2(r["mde_over_control"]), "", "", ""])
T7A = pd.DataFrame(rows, columns=["Window (days)", "Estimator", "β (pp)", "SE (pp)", "p",
                                  "95% CI (pp)"])
ok = True
for w in (30, 90, 180):
    a = lad[lad["window"] == w].iloc[0]
    b = LAD[LAD["window"] == w].iloc[0]
    ok &= (pp(a["coef"]) == pp(b["coef"]) and pp(a["se_cv3"]) == pp(b["se_cv3"])
           and p3(a["p_cv3"]) == p3(b["p_cv3"]))
check("T7 Panel A CV3 rows equal f1_ladder.csv", ok)
rows = []
for w in (30, 90, 180):
    c = CLG[CLG["window"] == w].iloc[0]
    if not bool(c["converged"]):
        rows.append([n0(w), "did not converge", "did not converge",
                     "%s iterations; ConvergenceWarning" % n0(c["iterations"])])
    else:
        rows.append([n0(w), pp(c["ame"]), pp(c["se_cluster"]),
                     "converged in %s iterations" % n0(c["iterations"])])
T7B = pd.DataFrame(rows, columns=["Window (days)", "AME (pp)", "SE (pp)", "Convergence"])
TLAB = dict(VLAB); TLAB["(intercept)"] = "(Intercept)"; TLAB["fcc_form499"] = "Form 499 filer (treatment)"
rows = []
for w in (30, 90, 180):
    for _, r in BCC[BCC["window"] == w].iterrows():
        rows.append([n0(w), TLAB.get(r["term"], r["term"]), pp(r["coef"]), pp(r["se_cv3"]),
                     p3(r["p_cv3"])])
T7C = pd.DataFrame(rows, columns=["Window (days)", "Term", "β (pp)", "CV3 SE (pp)", "p"])
add(7, "Primary Estimates: Inference Ladder, Minimum Detectable Effects, Logit Check, and Controls",
    [("Panel A: Inference ladder, minimum detectable effects", T7A),
     ("Panel B: Logit average marginal effects", T7B),
     ("Panel C: All terms, CV3", T7C)],
    "*Note.* N = 405 events; G = 119 parent CIKs. Standard errors are clustered by parent CIK. "
    "β, SE, CI and MDE are in PERCENTAGE POINTS. HC3 ignores within-cluster correlation and "
    "is DISQUALIFIED as an inferential rung; it is shown because the analysis plan specified the "
    "full ladder, and its p must never be read as significance. CV3 uses the t distribution with "
    "G − 1 = 118 degrees of freedom. The wild cluster restricted bootstrap uses B = 99,999 "
    "for p and B = 9,999 for confidence-interval inversion; it yields no standard error. The "
    "30-day logit failed to converge (35 iterations, ConvergenceWarning), so its average marginal "
    "effect is not reported; there was no separation and no dropped observation at any window. "
    "Panel C coefficients are DESCRIPTIVE: they are not hypothesis tests and are outside the "
    "31-test ledger. Sources: outputs/essay3_q4/table07.csv; b_control_coefficients.csv; "
    "c_logit_diagnostics.csv; outputs/essay3_v4/f1_ladder.csv.")

# =============================================================== TABLE 8
pl = T08[T08["panel"] == "placebo ladder"].iloc[0]
rows = [["HC3 (disqualified; reported per the analysis plan)", pp(pl["coef"]), pp(pl["se_hc3"]),
         p3(pl["p_hc3"]), ""],
        ["CV1", pp(pl["coef"]), pp(pl["se_cv1"]), p3(pl["p_cv1"]), ""],
        ["CV3", pp(pl["coef"]), pp(pl["se_cv3"]), p3(pl["p_cv3"]), ci_pp(pl["ci_cv3_lo"], pl["ci_cv3_hi"])],
        ["Wild cluster restricted bootstrap", pp(pl["coef"]), "", p3(pl["p_wcr"]),
         ci_pp(pl["ci_wcr_lo"], pl["ci_wcr_hi"])]]
for grp in ("treated", "control"):
    r = T08[(T08["panel"] == "placebo window rate") & (T08["group"] == grp)].iloc[0]
    rows.append(["%s departure rate in the placebo window" % grp.title(),
                 pct_from(r["events_with_departure"], r["n"]), "", "",
                 "%s of %s events" % (n0(r["events_with_departure"]), n0(r["n"]))])
T8 = pd.DataFrame(rows, columns=["Estimator", "β (pp) or rate (%)", "SE (pp)", "p", "95% CI (pp) / n"])
add(8, "Pre-Disclosure Placebo",
    [("", T8)],
    "*Note.* N = 405 events; G = 119 parent CIKs. The placebo outcome is an executive departure "
    "in (t0 − 180d, t0], the 180 days ENDING at notification. The interval is closed at t0, "
    "so a departure dated ON the notification date falls in the placebo window and not in any "
    "outcome window. β, SE and CI are in percentage points. HC3 is disqualified as above. "
    "Sources: outputs/essay3_q4/table08.csv, from outputs/essay3_v4/f4_placebo.csv.")

# =============================================================== TABLE 9
s9 = T09[T09["panel"] == "sensitivities"].copy()
order = ["year FE (reported year)", "two-digit SIC FE", "breach_date anchor",
         "excluding pre-announced departures", "excluding the F2 baseline control",
         "restatement-dated outcome (rs)"]
s9["_k"] = s9["sensitivity"].apply(lambda s: order.index(s) if s in order else 90 + len(s))
s9 = s9.sort_values(["_k", "window"])
rows = []
for _, r in s9.iterrows():
    lab = str(r["sensitivity"])
    if "recall-corrected" in lab:
        lab += " [bounding exercise]" if "BOUNDING" in str(r["row_type"]) else ""
    rows.append([lab, n0(r["window"]), pp(r["coef"]), pp(r["se_cv3"]), p3(r["p_cv3"]),
                 p3(r["p_wcr"]), p3(r["p_bh"]), n0(r["n"])])
T9A = pd.DataFrame(rows, columns=["Sensitivity", "Window (days)", "β (pp)", "CV3 SE (pp)",
                                  "CV3 p", "Bootstrap p", "BH-adjusted p", "N"])
check("T9 Panel A has 27 rows", len(T9A) == 27, "got %d" % len(T9A))
sic = T09[T09["panel"] == "SIC cells"].copy()
sic["sic2"] = sic["sic2"].astype(str)
s48 = sic[sic["sic2"] == "48"].iloc[0]
s73 = sic[sic["sic2"] == "73"].iloc[0]
rest = sic[~sic["sic2"].isin(["48", "73"])]
T9B = pd.DataFrame([
    ["48 (communications)", n0(s48["events"]), n0(s48["treated"]), n0(s48["control"])],
    ["73 (business services)", n0(s73["events"]), n0(s73["treated"]), n0(s73["control"])],
    ["%d cells, no treated events" % len(rest), n0(rest["events"].sum()), "0",
     n0(rest["control"].sum())],
    ["Total", n0(sic["events"].sum()), n0(sic["treated"].sum()), n0(sic["control"].sum())]],
    columns=["Two-digit SIC cell", "Events", "Treated", "Control"])
check("T9 Panel B events total 405", int(sic["events"].sum()) == 405)
add(9, "Sensitivity Analyses",
    [("Panel A: All 27 sensitivity specifications", T9A),
     ("Panel B: Two-digit SIC cells", T9B)],
    "*Note.* Sample level is EVENTS; every row retains all N = 405, so no specification drops a "
    "fixed-effect singleton or a missing SIC cell. β and SE are in percentage points. "
    "Benjamini-Hochberg is applied WITHIN the 27-test sensitivity family. HC3 does not appear: "
    "it is disqualified, and its standard error is not finite for the SIC fixed-effects rows, "
    "whose design is rank-deficient. The recall-corrected rows divide the outcome by the "
    "measured stratum recall; that correction is UNCAPPED and corrects missed departures only, "
    "with no adjustment for false positives, and the two CI-endpoint rows are bounding exercises "
    "rather than estimates. The complete test ledger is 31 tests (3 primary, 1 placebo, 27 "
    "sensitivities); the chief executive family contributes 0 tests because its 10-event gate "
    "failed at every window. The full 36-cell SIC list is in outputs/essay3_v4/f3_sic2_cells.csv. "
    "Sources: outputs/essay3_q4/table09.csv; outputs/essay3_v4/i_tests.csv.")

# =============================================================== TABLE 10
lo = T10[T10["panel"] == "LOCO range"]
var = T10[T10["panel"] == "top-ten variance shares"]
rows = []
for w in (30, 90, 180):
    r = lo[lo["window"] == w].iloc[0]
    rev = var[(var["window"] == w) & (var["sign_flip"] == 1)]
    rows.append([n0(w), pp(r["full_coef"]),
                 "[%s, %s]" % (pp(r["loco_min"]), pp(r["loco_max"])), n0(r["sign_flips"]),
                 "; ".join("%s (%s)" % (x["name"], pp(x["coef_without"])) for _, x in rev.iterrows()),
                 pp(r["without_TMobile"]), pp(r["without_Sprint"])])
T10A = pd.DataFrame(rows, columns=["Window (days)", "Full-sample β (pp)",
                                   "Range across deletions (pp)", "Sign reversals",
                                   "Reversing clusters (β without)", "T-Mobile deleted (pp)",
                                   "Sprint deleted (pp)"])
rows = []
for w in (30, 90, 180):
    for _, r in var[var["window"] == w].iterrows():
        rows.append([n0(w), n0(r["final_cik"]), str(r["name"]),
                     "Treated" if int(r["treated_cluster"]) == 1 else "Control",
                     n0(r["n_events"]), pct(r["share"]), pp(r["coef_without"])])
T10B = pd.DataFrame(rows, columns=["Window (days)", "CIK", "Cluster", "Group", "Events",
                                   "Share of CV3 jackknife variance (%)", "β without (pp)"])
ov = T10[T10["panel"] == "overlap restriction"]
rows = []
for w in (30, 90, 180):
    for s in ("v3-overlap", "full v4"):
        r = ov[(ov["window"] == w) & (ov["sample"] == s)].iloc[0]
        rows.append([n0(w), "CCM-based overlap restriction" if s == "v3-overlap" else "Full sample",
                     n0(r["n"]), n0(r["G"]), pp(r["coef"]), p3(r["p_cv3"]), p3(r["p_wcr"])])
T10C = pd.DataFrame(rows, columns=["Window (days)", "Sample", "N", "G", "β (pp)",
                                   "CV3 p", "Bootstrap p"])
add(10, "Cluster Concentration",
    [("Panel A: Leave-one-cluster-out", T10A),
     ("Panel B: Top ten clusters by share of CV3 jackknife variance", T10B),
     ("Panel C: CCM-based overlap restriction", T10C)],
    "*Note.* Sample level is EVENTS within parent CIKs; G = 119 clusters. β is in percentage "
    "points. A sign reversal is a cluster whose deletion changes the sign of β. Panel C "
    "restricts to events that were ALSO linked by the earlier CCM-based security link, which v4 "
    "replaced with a rebuilt CUSIP-to-permno link; it is a CCM-BASED OVERLAP RESTRICTION and is "
    "NOT a ticker match. All 58 events removed in Panel C are CONTROL events across 37 parent "
    "CIKs; no treated event turns on the linker rebuild. Sources: outputs/essay3_q4/table10.csv; "
    "outputs/essay3_v4/f1_cv3_variance_shares.csv; outputs/essay3_v4/239_v3_overlap_sensitivity.csv.")

# =============================================================== TABLE 11
CLAUSE = {}
for _, r in T02.iterrows():
    CLAUSE[int(r["final_cik"])] = ("1 and 2" if r["treated_events_clause1"] > 0 and r["treated_events_clause2"] > 0
                                   else ("1" if r["treated_events_clause1"] > 0 else "2"))
YN = lambda v: "Y" if int(v) == 1 else "N"
T11A = pd.DataFrame([[str(r["breach_date"]), str(r["reported_date"]),
                      CLAUSE.get(1283699, ""), YN(r["placebo_exec"]), YN(r["exec_30"]),
                      YN(r["exec_90"]), YN(r["exec_180"])] for _, r in T11.iterrows()],
                    columns=["Breach date", "Notification date", "Treatment clause",
                             "Placebo", "30 days", "90 days", "180 days"])
check("T11 Panel A has 26 rows", len(T11A) == 26, "got %d" % len(T11A))
TITLES = [
    ("Gary A. King", "Executive Vice President and Chief Information Officer", "2016-02-19",
     "0001193125-16-470124", "Outcome window"),
    ("David A. Miller", "Executive Vice President, General Counsel and Secretary", "2021-09-16",
     "0001193125-21-275230", "Outcome window"),
    ("Neville Ray", "President, Technology", "2023-02-13", "0001193125-23-035719", "Outcome window"),
    ("Peter Ewens", "Executive Vice President, Corporate Strategy & Development", "2023-09-08",
     "0001193125-23-231377", "Outcome window"),
    ("John Legere", "Chief Executive Officer", "2019-11-18", "0001193125-19-294093", "Placebo window"),
    ("J. Braxton Carter", "Executive Vice President and Chief Financial Officer", "2019-11-18",
     "0001193125-19-294093", "Placebo window")]
served = {}
for _, r in T11.iterrows():
    for col in ("outcome_accessions", "placebo_accessions"):
        for a in str(r.get(col, "") or "").split(";"):
            a = a.strip()
            if a:
                served[a] = served.get(a, 0) + 1
rows = []
for nm, ti, fd, acc, win in TITLES:
    if ti not in TMTXT:
        notreg("Table 11, Panel B", "title for %s not found verbatim in tmobile_502_text.md" % nm)
    rows.append([nm, ti, fd, acc, win, n0(served.get(acc, 0))])
T11B = pd.DataFrame(rows, columns=["Name", "Title as stated in the filing", "Filing date",
                                   "Accession", "Window placement", "Events served"])
add(11, "T-Mobile Events and Executive Departures",
    [("Panel A: The 26 T-Mobile events", T11A), ("Panel B: The departures", T11B)],
    "*Note.* Sample level is EVENTS in Panel A (all 26 T-Mobile events in the analysis sample, "
    "CIK 1283699) and PERSONS in Panel B. Y/N marks whether at least one executive departure "
    "falls in that window. The health-information flag is OMITTED: it is a known false positive "
    "arising from benefit-continuation language in separation agreements. The 13 events with a "
    "180-day departure resolve to only FOUR distinct departures, because several breach records "
    "fall within 180 days of the same filing; \"Events served\" counts how many events each "
    "filing serves. Legere and Carter fall in the PLACEBO window of the 2019-11-26 event: their "
    "8-K was filed 2019-11-18, eight days BEFORE that breach date and 105 days before the "
    "2020-03-02 notification, so neither can be a response to either. Titles and context are "
    "taken VERBATIM from the filings; no filing links any departure to a breach. Sources: "
    "outputs/essay3_q4/table11.csv; outputs/essay3_q4/tmobile_502_text.md.")

check("Tables numbered 1-11 in order", [t["num"] for t in TABLES] == list(range(1, 12)))
bad = []
for t in TABLES:
    for lab, df in t["blocks"]:
        for c in df.columns:
            for v in df[c].astype(str):
                if re.search(r"\b(inf|nan|NaN)\b", v) or re.search(r"(?<=[\s\[])-\d", v) or v.startswith("-"):
                    bad.append("Table %d / %s / %s: %r" % (t["num"], lab, c, v))
check("No cell contains inf, nan, or a hyphen used as a minus sign", not bad,
      "; ".join(bad[:5]))

# =============================================================== PART C
CHK = []


def fig(f, tab, pan, src, val):
    CHK.append(dict(figure_as_written=str(f), table=tab, panel=pan, source_cell=src,
                    value_after_formatting=str(val),
                    result="MATCH" if str(f).strip() == str(val).strip() else "MISMATCH"))


def L1(sub):
    return T01[T01["step"].str.contains(sub, na=False, regex=False)].iloc[0]


def L6(w, g, col):
    return T06[(T06["window"] == w) & (T06["group"] == g)].iloc[0][col]


def LA(w, col):
    return lad[lad["window"] == w].iloc[0][col]


def CV(v, g, col):
    return c3[(c3["variable"] == v) & (c3["group"] == g)].iloc[0][col]


def V10(w, cik, col):
    r = var[(var["window"] == w) & (var["final_cik"] == cik)]
    return r.iloc[0][col] if len(r) else None


def OVL(w, col):
    return ov[(ov["window"] == w) & (ov["sample"] == "v3-overlap")].iloc[0][col]


def F5(field, rnd=None, scoring=None):
    g = T05[(T05["panel"] == "agreement") & (T05["field"] == field)]
    if rnd:
        g = g[g["round"].astype(str).str.startswith(rnd)]
    if scoring:
        g = g[g["scoring"] == scoring]
    return g.iloc[0]


gate = SUB[SUB["step"].str.contains("identity-gate", na=False)].iloc[0]
nolink = SUB[SUB["step"].str.contains("no acceptable", case=False, na=False)].iloc[0]

# ---- sample ----
for lbl, sub in [("1,054", "PRC notification"), ("758", "Gate 1"), ("524", "Stage 3"),
                 ("491", "Gate 2"), ("489", "CANONICAL_V4"), ("405", "Prior 12-month")]:
    fig(lbl, 1, "A", "table01.csv step '" + sub + "' -> N", n0(L1(sub)["N"]))
fin = L1("Prior 12-month")
fig("109", 1, "A", "table01.csv final step -> treated_events", n0(fin["treated_events"]))
fig("296", 1, "A", "table01.csv final step -> control_events", n0(fin["control_events"]))
fig("13", 1, "A", "table01.csv final step -> treated_parent_ciks", n0(fin["treated_parent_ciks"]))
fig("119", 2, "B", "f1_ladder.csv 30d -> G", n0(lad30["G"]))
fig("9", 1, "A", "table01.csv identity-gate sub-row -> N", n0(gate["N"]))
fig("6", 1, "A", "table01.csv identity-gate sub-row -> treated_events", n0(gate["treated_events"]))
fig("66", 1, "A", "table01.csv no-link sub-row -> N", n0(nolink["N"]))
fig("2", 1, "A", "table01.csv 414 minus 412 at the Compustat step",
    n0(int(L1("CRSP")["N"]) - int(L1("Compustat")["N"])))
fig("7", 1, "A", "table01.csv 412 minus 405 at the 150-return step",
    n0(int(L1("Outcome-data")["N"]) - int(fin["N"])))
fig("0", 1, "A", "table01.csv final step -> pre_rule_treated", n0(fin["pre_rule_treated"]))
fig("7", 1, "A", "table01.csv final step -> pre_rule_control", n0(fin["pre_rule_control"]))
fig("1.55", 1, "Note", "descriptive_counts.csv records_per_event_mean",
    DC["records_per_event_mean"])
fig("31", 1, "Note", "descriptive_counts.csv records_per_event_max",
    DC["records_per_event_max"])

# ---- treated firms ----
fig("70", 2, "A", "table02.csv sum treated_events_clause1", n0(t2["treated_events_clause1"].sum()))
fig("39", 2, "A", "table02.csv sum treated_events_clause2", n0(t2["treated_events_clause2"].sum()))
fig("26", 2, "B", "table02.csv CIK 1283699 -> treated_events", n0(tm))
fig("23.9", 2, "B", "table02.csv 1283699 / 109", pct(tm / 109.0))
fig("38", 2, "B", "table02.csv 1283699 + 101830", n0(tm + sp))
fig("34.9", 2, "B", "table02.csv (1283699 + 101830) / 109", pct((tm + sp) / 109.0))
fig("24", 2, "A", "table02.csv CIK 732717 -> treated_events",
    n0(t2[t2["final_cik"] == 732717]["treated_events"].iloc[0]))
fig("10", 2, "A", "table02.csv CIK 732712 -> treated_events",
    n0(t2[t2["final_cik"] == 732712]["treated_events"].iloc[0]))
fig("5", 2, "A", "table02.csv CIK 1447669 + 1609711 -> treated_events",
    n0(t2[t2["final_cik"].isin([1447669, 1609711])]["treated_events"].sum()))
fig("24.5", 2, "B", "f1_ladder.csv 30d -> G_star", f2(lad30["G_star"], 1))
fig("61", 2, "B", "descriptive_counts.csv singleton_clusters", DC["singleton_clusters"])
fig("78", 2, "B", "descriptive_counts.csv largest_cluster_events", DC["largest_cluster_events"])
fig("19.3", 2, "B", "descriptive_counts.csv largest_cluster_share", DC["largest_cluster_share"])

# ---- composition ----
for code, tv, cvv in [("HACK", "58.7", "76.0"), ("INSD", "20.2", "8.5"), ("PHYS", "11.0", "1.4")]:
    r = T03[T03["breach_type"] == code].iloc[0]
    fig(tv, 3, "", "table03.csv " + code + " treated_events / 109",
        pct_from(r["treated_events"], _t3T))
    fig(cvv, 3, "", "table03.csv " + code + " control_events / 296",
        pct_from(r["control_events"], _t3C))
fig("11.58", 4, "A", "table04.csv firm_size_log treated mean", f2(CV("firm_size_log", "treated", "mean")))
fig("9.69", 4, "A", "table04.csv firm_size_log control mean", f2(CV("firm_size_log", "control", "mean")))
fig("1.45", 4, "A", "table04.csv firm_size_log std_diff", f2(CV("firm_size_log", "treated", "std_diff")))
fig("97.0", 4, "B", "descriptive_counts.csv control_in_treated_range_pct",
    DC["control_in_treated_range_pct"])
fig("85.3", 4, "B", "descriptive_counts.csv treated_in_control_range_pct",
    DC["treated_in_control_range_pct"])
fig("0.49", 4, "A", "table04.csv leverage std_diff", f2(CV("leverage", "treated", "std_diff")))
fig("−0.56", 4, "A", "table04.csv roa std_diff", f2(CV("roa", "treated", "std_diff")))
fig("1.66", 4, "A", "table04.csv prior_breaches_1yr treated mean", f2(CV("prior_breaches_1yr", "treated", "mean")))
fig("4.16", 4, "A", "table04.csv prior_breaches_1yr control mean", f2(CV("prior_breaches_1yr", "control", "mean")))
fig("2", 4, "A", "table04.csv health_breach treated mean x 109",
    n0(round(float(CV("health_breach", "treated", "mean")) * 109)))
fig("38.5", 4, "C", "table04.csv C2 treated same_day / n", pct_from(ct["same_day"], ct["n"]))
fig("29.1", 4, "C", "table04.csv C2 control same_day / n", pct_from(cc["same_day"], cc["n"]))
fig("22", 4, "C", "table04.csv C2 treated lag_median", n0(ct["lag_median"]))
fig("27", 4, "C", "table04.csv C2 control lag_median", n0(cc["lag_median"]))
fig("11.9", 4, "C", "table04.csv C2 treated bd180_before_rd / n",
    pct_from(ct["bd180_before_rd"], ct["n"]))
fig("14.5", 4, "C", "table04.csv C2 control bd180_before_rd / n",
    pct_from(cc["bd180_before_rd"], cc["n"]))

# ---- validation ----
aud = F5("exec departure (A)", scoring="PRIMARY (verified)")
fin5 = F5("PRIMARY (verified) | exec departure (A: any)")
r2 = F5("exec departure (A: any)", rnd="round 2")
fig(".787", 5, "A", "table05.csv audit exec departure kappa", k3(aud["kappa"]))
fig(".870", 5, "A", "table05.csv final-round exec departure kappa", k3(fin5["kappa"]))
fig(".966 [.822, .999]", 5, "A", "table05.csv audit precision + CI",
    p3(aud["precision"]) + " " + ci_str(aud["precision_ci95"]))
fig("1.000 [.398, 1.000]", 5, "A", "table05.csv final-round precision + CI",
    f2(fin5["precision"], 3) + " " + ci_str(fin5["precision_ci95"]))
fig(".800 [.631, .916]", 5, "A", "table05.csv audit recall + CI",
    p3(aud["recall"]) + " " + ci_str(aud["recall_ci95"]))
fig(".800 [.284, .995]", 5, "A", "table05.csv final-round recall + CI",
    p3(fin5["recall"]) + " " + ci_str(fin5["recall_ci95"]))
fig(".600 [.147, .947]", 5, "A", "table05.csv round-2 recall + CI",
    p3(r2["recall"]) + " " + ci_str(r2["recall_ci95"]))
st_t = sp_[sp_["stratum"] == "treated"].iloc[0]
st_c = sp_[sp_["stratum"] == "control"].iloc[0]
fig(".842 [.604, .966]", 5, "B", "stratified treated recall + CI",
    p3(st_t["recall"]) + " " + ci_str(st_t["recall_ci95"]))
fig("19", 5, "B", "stratified treated ref_Y", n0(st_t["ref_Y"]))
fig(".750 [.476, .927]", 5, "B", "stratified control recall + CI",
    p3(st_c["recall"]) + " " + ci_str(st_c["recall_ci95"]))
fig("16", 5, "B", "stratified control ref_Y", n0(st_c["ref_Y"]))
fig("1.000", 5, "B", "stratified treated precision", f2(st_t["precision"], 3))
fig(".923", 5, "B", "stratified control precision", p3(st_c["precision"]))
ceo_a = F5("CEO departure", scoring="PRIMARY (verified)")
fig(".530", 5, "A", "table05.csv audit CEO kappa", k3(ceo_a["kappa"]))
fig(".571", 5, "A", "table05.csv audit CEO precision", p3(ceo_a["precision"]))
fig(".571", 5, "A", "table05.csv audit CEO recall", p3(ceo_a["recall"]))
dir_a = F5("director-only departure", scoring="PRIMARY (verified)")
fig(".746", 5, "A", "table05.csv audit director-only kappa", k3(dir_a["kappa"]))

# ---- outcomes ----
fig("75.2", 6, "A", "table06.csv 180d treated any_502 / n",
    pct_from(L6(180, "treated", "any_502"), L6(180, "treated", "n")))
fig("66.6", 6, "A", "table06.csv 180d control any_502 / n",
    pct_from(L6(180, "control", "any_502"), L6(180, "control", "n")))
for w, tv, cvv in [(30, "3.7", "4.4"), (90, "10.1", "14.5"), (180, "30.3", "24.7")]:
    fig(tv, 6, "A", "table06.csv %dd treated exec_departure / n" % w,
        pct_from(L6(w, "treated", "exec_departure"), L6(w, "treated", "n")))
    fig(cvv, 6, "A", "table06.csv %dd control exec_departure / n" % w,
        pct_from(L6(w, "control", "exec_departure"), L6(w, "control", "n")))
fig("49 of 82", 6, "B", "table06.csv 180d treated filing_no_exec of any_502",
    n0(L6(180, "treated", "filing_no_exec")) + " of " + n0(L6(180, "treated", "any_502")))
fig("124 of 197", 6, "B", "table06.csv 180d control filing_no_exec of any_502",
    n0(L6(180, "control", "filing_no_exec")) + " of " + n0(L6(180, "control", "any_502")))
fig("173 of 279", 6, "B", "table06.csv 180d pooled filing_no_exec of any_502",
    n0(L6(180, "POOLED", "filing_no_exec")) + " of " + n0(L6(180, "POOLED", "any_502")))
fig("62.0", 6, "B", "table06.csv 180d pooled filing_no_exec / any_502",
    pct_from(L6(180, "POOLED", "filing_no_exec"), L6(180, "POOLED", "any_502")))
for w, tv, cvv in [(30, "0", "1"), (90, "3", "8"), (180, "8", "24")]:
    fig(tv, 6, "A", "table06.csv %dd treated ceo_departure" % w, n0(L6(w, "treated", "ceo_departure")))
    fig(cvv, 6, "A", "table06.csv %dd control ceo_departure" % w, n0(L6(w, "control", "ceo_departure")))
for w, tv, cvv in [(30, "8", "4"), (90, "18", "20"), (180, "21", "56")]:
    fig(tv, 6, "A", "table06.csv %dd treated director_only" % w, n0(L6(w, "treated", "director_only")))
    fig(cvv, 6, "A", "table06.csv %dd control director_only" % w, n0(L6(w, "control", "director_only")))

# ---- primary ----
for w, b, pc, pw, mde, ratio, cr in [
        (30, "0.40", ".906", ".889", "9.44", "2.15", "4.39"),
        (90, "−4.10", ".605", ".514", "22.34", "1.54", "14.53"),
        (180, "2.33", ".816", ".790", "28.15", "1.14", "24.66")]:
    fig(b, 7, "A", "table07.csv %dd coef -> pp" % w, pp(LA(w, "coef")))
    fig(pc, 7, "A", "table07.csv %dd p_cv3" % w, p3(LA(w, "p_cv3")))
    fig(pw, 7, "A", "table07.csv %dd p_wcr" % w, p3(LA(w, "p_wcr")))
    fig(mde, 7, "A", "table07.csv %dd mde80 -> pp" % w, pp(LA(w, "mde80")))
    fig(ratio, 7, "A", "table07.csv %dd mde_over_control" % w, f2(LA(w, "mde_over_control")))
    fig(cr, 7, "A", "table07.csv %dd control_rate -> pp" % w, pp(LA(w, "control_rate")))
fig("[−17.40, 22.06]", 7, "A", "table07.csv 180d CV3 CI -> pp",
    ci_pp(LA(180, "ci_cv3_lo"), LA(180, "ci_cv3_hi")))
fig("[−15.76, 20.11]", 7, "A", "table07.csv 180d WCR CI -> pp",
    ci_pp(LA(180, "ci_wcr_lo"), LA(180, "ci_wcr_hi")))
for w, ub in [(30, "7.02"), (90, "11.56"), (180, "22.06")]:
    fig(ub, 7, "A", "table07.csv %dd ci_cv3_hi -> pp" % w, pp(LA(w, "ci_cv3_hi")))
c90 = CLG[CLG["window"] == 90].iloc[0]
c180 = CLG[CLG["window"] == 180].iloc[0]
fig("−4.20", 7, "B", "c_logit_diagnostics.csv 90d ame -> pp", pp(c90["ame"]))
fig("4.68", 7, "B", "c_logit_diagnostics.csv 90d se_cluster -> pp", pp(c90["se_cluster"]))
fig("1.97", 7, "B", "c_logit_diagnostics.csv 180d ame -> pp", pp(c180["ame"]))
fig("7.75", 7, "B", "c_logit_diagnostics.csv 180d se_cluster -> pp", pp(c180["se_cluster"]))
fig("17", 7, "B", "table06.csv 30d pooled exec_departure", n0(L6(30, "POOLED", "exec_departure")))

# ---- placebo ----
prt = T08[(T08["panel"] == "placebo window rate") & (T08["group"] == "treated")].iloc[0]
prc = T08[(T08["panel"] == "placebo window rate") & (T08["group"] == "control")].iloc[0]
fig("22.9", 8, "", "table08.csv placebo treated events_with_departure / n",
    pct_from(prt["events_with_departure"], prt["n"]))
fig("23.6", 8, "", "table08.csv placebo control events_with_departure / n",
    pct_from(prc["events_with_departure"], prc["n"]))
fig("−8.62", 8, "", "table08.csv placebo coef -> pp", pp(pl["coef"]))
fig(".312", 8, "", "table08.csv placebo p_cv3", p3(pl["p_cv3"]))
fig(".231", 8, "", "table08.csv placebo p_wcr", p3(pl["p_wcr"]))
fig("[−25.43, 8.18]", 8, "", "table08.csv placebo CV3 CI -> pp",
    ci_pp(pl["ci_cv3_lo"], pl["ci_cv3_hi"]))

# ---- sensitivities ----
_it = pd.read_csv("outputs/essay3_v4/i_tests.csv")
fig(".113", 9, "A", "table09.csv min p_cv3 across the 27", p3(s9["p_cv3"].min()))
fig(".986", 9, "A", "table09.csv min p_bh across the 27", p3(s9["p_bh"].min()))
fig("31", 9, "Note", "i_tests.csv row count", n0(len(_it)))
fig("above .31", 9, "Note", "i_tests.csv min p_bh across all families",
    "above .31" if float(_it["p_bh"].min()) > 0.31 else "NOT above .31 (" + p3(_it["p_bh"].min()) + ")")
fig("104", 9, "B", "table09.csv SIC 48 treated", n0(s48["treated"]))
fig("40", 9, "B", "table09.csv SIC 48 control", n0(s48["control"]))
fig("5", 9, "B", "table09.csv SIC 73 treated", n0(s73["treated"]))
fig("141", 9, "B", "table09.csv SIC 73 control", n0(s73["control"]))
fig("34", 9, "B", "table09.csv cells with zero treated", n0(len(rest)))

# ---- concentration ----
for w, rv, tmd in [(30, "3", "−1.64"), (90, "1", "−6.87"), (180, "1", "−3.49")]:
    r = lo[lo["window"] == w].iloc[0]
    fig(rv, 10, "A", "table10.csv %dd sign_flips" % w, n0(r["sign_flips"]))
    fig(tmd, 10, "A", "table10.csv %dd without_TMobile -> pp" % w, pp(r["without_TMobile"]))
fig("59.2", 10, "B", "table10.csv 90d FIS share", pct(V10(90, 1136893, "share")))
fig("36.9", 10, "B", "table10.csv 30d T-Mobile share", pct(V10(30, 1283699, "share")))
fig("33.9", 10, "B", "table10.csv 180d T-Mobile share", pct(V10(180, 1283699, "share")))
fig("18.3", 10, "B", "table10.csv 30d Corebridge share", pct(V10(30, 1889539, "share")))
fig("58", 10, "C", "table10.csv 405 minus overlap n", n0(405 - int(OVL(30, "n"))))
fig("347", 10, "C", "table10.csv overlap n", n0(OVL(30, "n")))
fig("83", 10, "C", "table10.csv overlap G", n0(OVL(30, "G")))
for w, b, pv in [(30, "1.77", ".585"), (90, "−3.45", ".731"), (180, "2.08", ".852")]:
    fig(b, 10, "C", "table10.csv overlap %dd coef -> pp" % w, pp(OVL(w, "coef")))
    fig(pv, 10, "C", "table10.csv overlap %dd p_cv3" % w, p3(OVL(w, "p_cv3")))

# ---- T-Mobile ----
for w, v in [(30, "3"), (90, "5"), (180, "13")]:
    fig(v, 11, "A", "table11.csv sum exec_%d" % w, n0(T11["exec_%d" % w].sum()))
fig("26", 11, "A", "table11.csv row count", n0(len(T11)))
fig("8", 11, "A", "table11.csv sum placebo_exec", n0(T11["placebo_exec"].sum()))
fig("13 of 33", 11, "A", "table11.csv exec_180 vs table06 180d treated exec_departure",
    n0(T11["exec_180"].sum()) + " of " + n0(L6(180, "treated", "exec_departure")))

CK = pd.DataFrame(CHK)
CK.to_csv(OUT / "text_figures_check.csv", index=False)
MIS = CK[CK["result"] == "MISMATCH"]

# =============================================================== WRITE .md
LINES = ["# Essay 3 Appendix", "",
         "Analysis sample N = 405 events (109 treated, 296 control; G = 119 parent CIKs, "
         "G1 = 13 treated clusters, 12 treated parent entities). Tables are numbered in "
         "the order the Results section first mentions them. Every cell is read from a "
         "committed CSV under `outputs/essay3_q4/` or `outputs/essay3_q3/` and then "
         "formatted; nothing here is estimated. Built by `scripts/245_essay3_appendix.py`.",
         "",
         "Conventions: coefficients, standard errors, confidence intervals and minimum "
         "detectable effects are in PERCENTAGE POINTS to two decimals; rates are percent "
         "to one decimal; p, kappa, precision and recall carry three decimals with no "
         "leading zero; counts use thousands separators; the minus sign is U+2212.", ""]
SECTIONS = {1: "SAMPLE AND TREATMENT", 5: "MEASUREMENT", 6: "OUTCOMES",
            7: "ESTIMATES", 10: "ROBUSTNESS", 11: "CASE EVIDENCE"}
for t in TABLES:
    if t["num"] in SECTIONS:
        LINES += ["## " + SECTIONS[t["num"]], ""]
    LINES += ["**Table %d**" % t["num"], "", "*%s*" % t["title"], ""]
    for lab, df in t["blocks"]:
        if lab:
            LINES += ["**%s**" % lab, ""]
        LINES += ["| " + " | ".join(str(c) for c in df.columns) + " |",
                  "|" + "|".join(["---"] * len(df.columns)) + "|"]
        for _, rr in df.iterrows():
            LINES.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in rr) + " |")
        LINES.append("")
    LINES += [t["note"], ""]
LINES += ["---", "", "## ASSERTIONS", ""]
for nm, ok, det in ASSERT:
    LINES.append("- " + nm + " **" + ("PASS" if ok else "FAIL") + "**"
                 + (("  " + det) if det and not ok else ""))
LINES += ["", "## NOT REGENERABLE", ""]
LINES += (["- **" + w + "** " + x for w, x in NOTREG] or ["- none"])
LINES += ["", "## TEXT-TO-TABLE CHECK", "",
          "%d figures checked; %d MISMATCH. Full listing in `text_figures_check.csv`."
          % (len(CK), len(MIS)), ""]
if len(MIS):
    LINES += ["| Figure as written | Table | Panel | Source cell | Value after formatting |",
              "|---|---|---|---|---|"]
    for _, rr in MIS.iterrows():
        LINES.append("| %s | %s | %s | %s | %s |" % (rr["figure_as_written"], rr["table"],
                                                     rr["panel"], rr["source_cell"],
                                                     rr["value_after_formatting"]))
    LINES.append("")
(OUT / "ESSAY3_APPENDIX_TABLES.md").write_text("\n".join(LINES) + "\n", encoding="utf-8")

# =============================================================== WRITE .docx
docx_ok = True
try:
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 1.0
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(1)
        s.top_margin = s.bottom_margin = Inches(1)

    def para(text, bold=False, italic=False, size=12, align=None, sa=6):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.bold, r.italic = bold, italic
        p.paragraph_format.space_after = Pt(sa)
        p.paragraph_format.line_spacing = 1.0
        if align is not None:
            p.alignment = align
        return p

    para("Essay 3 Appendix", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    para("Tables 1 to 11, numbered in the order the Results section first mentions them. "
         "Analysis sample N = 405 events (109 treated, 296 control; G = 119 parent CIKs). "
         "Coefficients, standard errors, confidence intervals and minimum detectable "
         "effects are in percentage points.", size=11)
    WIDE = {7, 9, 10}
    for t in TABLES:
        if t["num"] in WIDE:
            s = doc.add_section()
            s.orientation = WD_ORIENT.LANDSCAPE
            s.page_width, s.page_height = s.page_height, s.page_width
            s.left_margin = s.right_margin = Inches(1)
            s.top_margin = s.bottom_margin = Inches(1)
        else:
            doc.add_page_break()
        para("Table %d" % t["num"], bold=True, sa=0)
        para(t["title"], italic=True, sa=8)
        for lab, df in t["blocks"]:
            if lab:
                para(lab, bold=True, size=11, sa=4)
            tb = doc.add_table(rows=1, cols=len(df.columns))
            tb.style = "Table Grid"
            for i, c in enumerate(df.columns):
                cell = tb.rows[0].cells[i]
                cell.text = ""
                run = cell.paragraphs[0].add_run(str(c))
                run.bold = True
                run.font.size = Pt(9)
                run.font.name = "Times New Roman"
                cell.paragraphs[0].paragraph_format.line_spacing = 1.0
            for _, row in df.iterrows():
                cells = tb.add_row().cells
                for i, v in enumerate(row):
                    cells[i].text = ""
                    run = cells[i].paragraphs[0].add_run("" if pd.isna(v) else str(v))
                    run.font.size = Pt(9)
                    run.font.name = "Times New Roman"
                    cells[i].paragraphs[0].paragraph_format.line_spacing = 1.0
            para("", sa=4)
        note = t["note"]
        if note.startswith("*Note.*"):
            note = note[len("*Note.*"):].strip()
        p = doc.add_paragraph()
        r0 = p.add_run("Note. ")
        r0.italic = True
        r0.font.size = Pt(9)
        r0.font.name = "Times New Roman"
        r1 = p.add_run(note)
        r1.font.size = Pt(9)
        r1.font.name = "Times New Roman"
        p.paragraph_format.line_spacing = 1.0
    doc.save(str(OUT / "ESSAY3_APPENDIX_TABLES.docx"))
except Exception as exc:
    docx_ok = False
    print("DOCX FAILED: %s" % exc)

print("=" * 96)
print("PART B ASSERTIONS")
print("=" * 96)
for nm, ok, det in ASSERT:
    print("  %-62s %s%s" % (nm, "PASS" if ok else "*** FAIL ***",
                            ("  " + det) if det and not ok else ""))
print()
print("NOT REGENERABLE: %d" % len(NOTREG))
for w, x in NOTREG:
    print("  %s: %s" % (w, x))
print()
print("PART C: %d figures checked, %d MISMATCH" % (len(CK), len(MIS)))
for _, rr in MIS.iterrows():
    print("  MISMATCH | written %-24s | formatted %-24s | T%s %s | %s"
          % (rr["figure_as_written"], rr["value_after_formatting"], rr["table"],
             rr["panel"], rr["source_cell"]))
print()
print("written ESSAY3_APPENDIX_TABLES.md, text_figures_check.csv"
      + (", ESSAY3_APPENDIX_TABLES.docx" if docx_ok else " (DOCX FAILED)"))
