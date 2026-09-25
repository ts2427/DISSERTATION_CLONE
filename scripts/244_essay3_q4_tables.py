"""
ESSAY 3 — QUERY 4, PART F: ONE SOURCE CSV PER TABLE (locked Results order 1-11)
=============================================================================
    python scripts/244_essay3_q4_tables.py

Reads only committed inputs plus the Query 3 (outputs/essay3_q3/) and Query 4
(outputs/essay3_q4/) outputs. Writes table01.csv .. table11.csv and
table_provenance.csv under outputs/essay3_q4/. Estimates nothing.

Conventions fixed by the query:
  * infinite HC3 SEs are written BLANK with an explanatory note column; never `inf`
  * T-Mobile passages are cited by ACCESSION only; the health flag is omitted
  * recall-corrected rows keep their BOUNDING EXERCISE label
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

V4 = Path("outputs/essay3_v4")
RB = Path("outputs/rebuild_v4")
Q2 = Path("outputs/essay3_q2")
Q3 = Path("outputs/essay3_q3")
OUT = Path("outputs/essay3_q4")
OUT.mkdir(parents=True, exist_ok=True)
TREAT = "fcc_form499"
PROV, FAIL, L = [], [], []


def log(m=""):
    print(m, flush=True)
    L.append(str(m))


def prov(table, panel, column, source, key, script):
    PROV.append(dict(table=table, panel=panel, column=column, source_file=source,
                     source_line_or_key=key, emitting_script=script))


def check(name, ok, detail=""):
    log("  %-62s %s%s" % (name, "PASS" if ok else "*** FAIL ***",
                          ("  " + detail) if detail else ""))
    if not ok:
        FAIL.append(name + (" :: " + detail if detail else ""))


def need(p):
    if not Path(p).exists():
        sys.exit("ABORT 244: missing input " + str(p))
    return Path(p)


CAN = pd.read_csv(need("Data/processed/rebuild_v4/CANONICAL_V4.csv"), low_memory=False)
A = pd.read_csv(need(V4 / "e_analysis_sample.csv"), low_memory=False)
A = A[A["in_analysis_sample"] == 1].copy()
for d in (CAN, A):
    d["_k"] = d["final_cik"].astype(str) + "|" + d["breach_date"].astype(str).str[:10]
CS = CAN[CAN["_k"].isin(set(A["_k"]))].copy()
A = A.merge(CS[["_k", "breach_type"]], on="_k", how="left")
A["bdt"] = pd.to_datetime(A["breach_date"])
A["rdt"] = pd.to_datetime(A["reported_date"])
FAM = {101830: 1283699}


def clause(x):
    x = str(x)
    return 1 if x.startswith("Clause (a)") else (2 if x.startswith("Clause (b)") else 0)


# ---------------------------------------------------------------- TABLE 1
log("TABLE 1 — attrition ledger")
t1 = pd.read_csv(need(V4 / "e_ledger.csv")).copy()
t1 = t1.rename(columns={"treated": "treated_events", "control": "control_events",
                        "treated_corporate_families": "treated_parent_entities"})
IDREV = pd.read_csv(need(RB / "v4_212_identity_review.csv"), low_memory=False)
LINKS = pd.read_csv(need(RB / "v4_212_links.csv"), low_memory=False)
gate = set(IDREV["final_cik"].astype(str) + "|" + IDREV["breach_date"].astype(str).str[:10])
nop = LINKS[LINKS["permno"].isna()].copy()
nop["_k"] = nop["final_cik"].astype(str) + "|" + nop["breach_date"].astype(str).str[:10]
tm = dict(zip(CAN["_k"], CAN[TREAT]))
other = set(nop["_k"]) - gate
t1["identity_gate_split"] = ""
i_crsp = t1.index[t1["step"].str.contains("CRSP", na=False)]
if len(i_crsp):
    t1.loc[i_crsp[0], "identity_gate_split"] = (
        "of the %d lost: %d identity-gate rejections (treated %d / control %d); "
        "%d no acceptable CUSIP->permno (treated %d / control %d)"
        % (len(nop), len(gate), sum(1 for k in gate if tm.get(k) == 1),
           sum(1 for k in gate if tm.get(k) == 0), len(other),
           sum(1 for k in other if tm.get(k) == 1), sum(1 for k in other if tm.get(k) == 0)))
t1.to_csv(OUT / "table01.csv", index=False)
prov(1, "ledger", "N/treated_events/control_events/treated_parent_ciks/treated_parent_entities/pre_rule_*",
     "outputs/essay3_v4/e_ledger.csv", "all rows", "scripts/224")
prov(1, "identity split", "identity_gate_split",
     "outputs/rebuild_v4/v4_212_identity_review.csv + v4_212_links.csv", "permno isna", "scripts/212")
ev = t1.dropna(subset=["treated_events"])
check("T1 closes arithmetically (N never rises)", bool((t1["N"].diff().dropna() <= 0).all()))
check("T1 treated + control == N at every populated step",
      bool((ev["treated_events"] + ev["control_events"] == ev["N"]).all()))
check("T1 final step N == 405", int(t1["N"].iloc[-1]) == 405)

# ---------------------------------------------------------------- TABLE 2
log("TABLE 2 — treated parent CIKs")
t = CS[CS[TREAT] == 1].copy()
t["clause"] = t["treatment_evidence"].map(clause)
g = t.groupby("final_cik")
rows = []
for cik, gg in g:
    allg = CS[CS["final_cik"] == cik]
    rows.append(dict(final_cik=cik, org_name=gg["org_name"].mode().iloc[0],
                     treated_events=len(gg),
                     treated_events_clause1=int((gg["clause"] == 1).sum()),
                     treated_events_clause2=int((gg["clause"] == 2).sum()),
                     control_events_same_cik=int((allg[TREAT] == 0).sum()),
                     name_variants=gg["org_name"].nunique(),
                     corporate_family_cik=FAM.get(cik, cik),
                     corporate_family_name=("T-Mobile USA, Inc. (Sprint folded in, scripts/224:361)"
                                            if FAM.get(cik, cik) == 1283699 and cik != 1283699
                                            else gg["org_name"].mode().iloc[0]),
                     clause2_rules="; ".join(sorted({str(x)[:90] for x in
                                                     gg.loc[gg["clause"] == 2, "treatment_evidence"]})),
                     clause1_rules="; ".join(sorted({str(x)[:90] for x in
                                                     gg.loc[gg["clause"] == 1, "treatment_evidence"]}))))
t2 = pd.DataFrame(rows).sort_values("treated_events", ascending=False)
t2.to_csv(OUT / "table02.csv", index=False)
prov(2, "clause split", "treated_events_clause1/2", "Data/processed/rebuild_v4/CANONICAL_V4.csv",
     "treatment_evidence prefix", "scripts/154 via scripts/214")
prov(2, "family", "corporate_family_cik", "scripts/224", "line 361 FAM = {101830: 1283699}", "scripts/224")
check("T2 clause columns sum to treated_events per CIK",
      bool((t2["treated_events_clause1"] + t2["treated_events_clause2"] == t2["treated_events"]).all()))
check("T2 treated events sum to 109", int(t2["treated_events"].sum()) == 109)
check("T2 rows == 13 treated parent CIKs", len(t2) == 13)
check("T2 corporate families == 12", t2["corporate_family_cik"].nunique() == 12)

# ---------------------------------------------------------------- TABLE 3
log("TABLE 3 — breach-type mix")
bt = pd.crosstab(CS["breach_type"], CS[TREAT]).rename(columns={0: "control_events", 1: "treated_events"})
for c in ("control_events", "treated_events"):
    if c not in bt.columns:
        bt[c] = 0
bt["control_share"] = (bt["control_events"] / bt["control_events"].sum()).round(4)
bt["treated_share"] = (bt["treated_events"] / bt["treated_events"].sum()).round(4)
t3 = bt.reset_index().sort_values("treated_events", ascending=False)
t3.to_csv(OUT / "table03.csv", index=False)
prov(3, "mix", "all", "Data/processed/rebuild_v4/CANONICAL_V4.csv", "breach_type x fcc_form499", "scripts/244")
check("T3 subgroup Ns sum to 109 / 296",
      int(t3["treated_events"].sum()) == 109 and int(t3["control_events"].sum()) == 296)

# ---------------------------------------------------------------- TABLE 4
log("TABLE 4 — covariates and anchors")
D3 = pd.read_csv(need(Q3 / "descriptives.csv"))
t4 = D3.copy()
t4.to_csv(OUT / "table04.csv", index=False)
prov(4, "covariates", "mean/sd/median/min/max/std_diff", "outputs/essay3_q3/descriptives.csv",
     "part == C3", "scripts/242")
prov(4, "anchors", "same_day/lag_*/bd180_*", "outputs/essay3_q3/descriptives.csv",
     "part == C2", "scripts/242")
c3 = t4[t4["part"] == "C3"]
check("T4 covariate group Ns are 109 / 296",
      set(c3[c3["group"] == "treated"]["n"]) == {109} and set(c3[c3["group"] == "control"]["n"]) == {296})

# ---------------------------------------------------------------- TABLE 5
log("TABLE 5 — validation, four rounds + stratified panel")
t5 = pd.read_csv(need(Q3 / "validation.csv"))
RS = pd.read_csv(need(Q2 / "d3_audit_recall_by_stratum.csv"))
RS2 = RS.copy()
RS2.insert(0, "round", "recall audit (80 stratified 40/40)")
RS2.insert(1, "source_file", "outputs/essay3_q2/d3_audit_recall_by_stratum.csv")
RS2["panel"] = "stratified recall"
t5["panel"] = "agreement"
t5 = pd.concat([t5, RS2], ignore_index=True)
t5.to_csv(OUT / "table05.csv", index=False)
prov(5, "agreement", "kappa/precision/recall/CI", "outputs/essay3_q3/validation.csv",
     "one block per round", "scripts/194/197/201/238")
prov(5, "stratified recall", "recall/recall_ci95 by stratum",
     "outputs/essay3_q2/d3_audit_recall_by_stratum.csv", "field == exec departure (A)", "scripts/201")
check("T5 carries all four rounds", t5["round"].nunique() >= 4)

# ---------------------------------------------------------------- TABLE 6
log("TABLE 6 — outcome rates and the crosswalk")
rows = []
for w in (30, 90, 180):
    for lbl, d in [("treated", A[A[TREAT] == 1]), ("control", A[A[TREAT] == 0]), ("POOLED", A)]:
        f = int(d["any_502_%d_rd" % w].sum())
        x = int(((d["any_502_%d_rd" % w] == 1) & (d["exec_departure_%d_rd" % w] == 0)).sum())
        rows.append(dict(window=w, group=lbl, n=len(d),
                         any_502=f, any_502_rate=round(f / len(d), 4),
                         exec_departure=int(d["exec_departure_%d_rd" % w].sum()),
                         exec_rate=round(d["exec_departure_%d_rd" % w].mean(), 4),
                         ceo_departure=int(d["ceo_departure_%d_rd" % w].sum()),
                         ceo_rate=round(d["ceo_departure_%d_rd" % w].mean(), 4),
                         director_only=int(d["director_departure_%d_rd" % w].sum()),
                         director_rate=round(d["director_departure_%d_rd" % w].mean(), 4),
                         filing_no_exec=x,
                         filing_no_exec_over_all_events=round(x / len(d), 4),
                         filing_no_exec_over_filers=round(x / f, 4) if f else np.nan))
t6 = pd.DataFrame(rows)
t6.to_csv(OUT / "table06.csv", index=False)
prov(6, "rates + crosswalk", "all", "outputs/essay3_v4/e_analysis_sample.csv",
     "any_502_*_rd, exec/ceo/director_departure_*_rd", "scripts/220 via scripts/224")
for w in (30, 90, 180):
    s = t6[t6["window"] == w]
    tr = s[s["group"] == "treated"].iloc[0]
    co = s[s["group"] == "control"].iloc[0]
    po = s[s["group"] == "POOLED"].iloc[0]
    check("T6 %3dd treated+control == pooled on every count" % w,
          all(int(tr[k]) + int(co[k]) == int(po[k])
              for k in ("n", "any_502", "exec_departure", "ceo_departure",
                        "director_only", "filing_no_exec")))

# ---------------------------------------------------------------- TABLE 7
log("TABLE 7 — inference ladder, logit AME, control coefficients")
F1 = pd.read_csv(need(V4 / "f1_ladder.csv"))
SED = pd.read_csv(need(V4 / "f1_se_diagnostics.csv"))
lad = F1.copy()
lad["panel"] = "ladder (treatment)"
lad = lad.merge(SED[["window", "mde80", "G_star"]], on="window", how="left")
lad["control_rate"] = [round(float(A.loc[A[TREAT] == 0, "exec_departure_%d_rd" % w].mean()), 4)
                       for w in lad["window"]]
lad["mde_over_control"] = (lad["mde80"] / lad["control_rate"]).round(4)
lad["mde_exceeds_control_rate"] = lad["mde80"] > lad["control_rate"]
AMEF = pd.read_csv(need(V4 / "f1_logit_ame.csv")).copy()
AMEF["panel"] = "logit AME"
CC = pd.read_csv(need(OUT / "b_control_coefficients.csv")).copy()
CC["panel"] = "control coefficients (CV3; DESCRIPTIVE, not tests, not in BH)"
try:
    CD = pd.read_csv(OUT / "c_logit_diagnostics.csv")[
        ["window", "converged", "iterations", "max_fitted_p", "separation_flag", "warnings_verbatim"]]
    AMEF = AMEF.merge(CD, on="window", how="left")
except Exception:
    pass
t7 = pd.concat([lad, AMEF, CC], ignore_index=True)
t7.to_csv(OUT / "table07.csv", index=False)
prov(7, "ladder", "coef/se_*/p_*/ci_*", "outputs/essay3_v4/f1_ladder.csv", "one row per window", "scripts/227")
prov(7, "ladder", "mde80/G_star", "outputs/essay3_v4/f1_se_diagnostics.csv", "one row per window", "scripts/229")
prov(7, "logit AME", "ame/se_cluster + convergence", "outputs/essay3_v4/f1_logit_ame.csv + q4 c_logit_diagnostics.csv",
     "one row per window", "scripts/227 / scripts/243")
prov(7, "control coefficients", "coef/se_cv3/t/p_cv3/ci_*", "outputs/essay3_q4/b_control_coefficients.csv",
     "one row per term per window", "scripts/243")
tr7 = t7[(t7["panel"] == "ladder (treatment)")]
ok = True
for w in (30, 90, 180):
    r7, rf = tr7[tr7["window"] == w].iloc[0], F1[F1["window"] == w].iloc[0]
    ok &= (round(float(r7["coef"]), 4) == round(float(rf["coef"]), 4)
           and round(float(r7["se_cv3"]), 4) == round(float(rf["se_cv3"]), 4)
           and round(float(r7["p_cv3"]), 4) == round(float(rf["p_cv3"]), 4))
check("T7 treatment rows equal f1_ladder.csv (coef, se_cv3, p_cv3)", ok)
ccrow = CC[(CC["is_treatment"]) & (CC["window"] == 180)].iloc[0]
check("T7 control panel's treatment term matches the ladder at 180d",
      round(float(ccrow["coef"]), 4) == round(float(F1[F1["window"] == 180]["coef"].iloc[0]), 4))

# ---------------------------------------------------------------- TABLE 8
log("TABLE 8 — placebo")
F4 = pd.read_csv(need(V4 / "f4_placebo.csv")).copy()
F4["panel"] = "placebo ladder"
prows = [dict(panel="placebo window rate", group=lbl, n=len(d),
              events_with_departure=int(d["placebo_exec_departure_rd"].sum()),
              rate=round(d["placebo_exec_departure_rd"].mean(), 4))
         for lbl, d in [("treated", A[A[TREAT] == 1]), ("control", A[A[TREAT] == 0]), ("POOLED", A)]]
t8 = pd.concat([F4, pd.DataFrame(prows)], ignore_index=True)
t8.to_csv(OUT / "table08.csv", index=False)
prov(8, "placebo ladder", "all", "outputs/essay3_v4/f4_placebo.csv", "single row", "scripts/227")
prov(8, "window rates", "events_with_departure/rate", "outputs/essay3_v4/e_analysis_sample.csv",
     "placebo_exec_departure_rd", "scripts/220")
pr = pd.DataFrame(prows)
check("T8 placebo treated+control == pooled",
      int(pr.iloc[0]["events_with_departure"]) + int(pr.iloc[1]["events_with_departure"])
      == int(pr.iloc[2]["events_with_departure"]))

# ---------------------------------------------------------------- TABLE 9
log("TABLE 9 — 27 sensitivities with BH, plus the SIC-cell panel")
S3 = pd.read_csv(need(Q3 / "sensitivities.csv")).copy()
S3["panel"] = "sensitivities"
inf_mask = ~np.isfinite(pd.to_numeric(S3["se_hc3"], errors="coerce"))
S3["se_hc3_note"] = np.where(
    inf_mask, "HC3 SE is not finite: the two-digit SIC FE design is rank-deficient and "
              "227 fits it by pseudoinverse. HC3 is DISQUALIFIED regardless; read CV3/WCR.", "")
S3["se_hc3"] = np.where(inf_mask, "", S3["se_hc3"].astype(str))
SICP = pd.read_csv(need(V4 / "f3_sic2_cells.csv")).copy()
SICP["panel"] = "SIC cells"
t9 = pd.concat([S3, SICP], ignore_index=True)
t9.to_csv(OUT / "table09.csv", index=False)
prov(9, "sensitivities", "coef/se_cv3/p_cv3/p_wcr/p_bh/row_type", "outputs/essay3_q3/sensitivities.csv",
     "27 rows", "scripts/227 + scripts/242")
prov(9, "SIC cells", "sic2/events/treated/control", "outputs/essay3_v4/f3_sic2_cells.csv", "all rows", "scripts/227")
check("T9 sensitivity rows == 27", int((t9["panel"] == "sensitivities").sum()) == 27)
check("T9 no literal 'inf' written anywhere",
      not t9.astype(str).apply(lambda c: c.str.lower().eq("inf")).any().any())
check("T9 every sensitivity row has N == 405",
      bool((pd.to_numeric(t9.loc[t9["panel"] == "sensitivities", "n"], errors="coerce") == 405).all()))
check("T9 SIC panel events sum to 405",
      int(pd.to_numeric(t9.loc[t9["panel"] == "SIC cells", "events"], errors="coerce").sum()) == 405)

# ---------------------------------------------------------------- TABLE 10
log("TABLE 10 — LOCO, variance shares, v3-overlap panel")
LO = pd.read_csv(need(Q3 / "loo.csv")).copy()
LO["panel"] = "LOCO range"
VARS = pd.read_csv(need(V4 / "f1_cv3_variance_shares.csv")).copy()
top = (VARS.sort_values(["window", "share"], ascending=[True, False])
       .groupby("window").head(10).copy())
top["panel"] = "top-ten variance shares"
OV = pd.read_csv(need(V4 / "239_v3_overlap_sensitivity.csv")).copy()
OV["panel"] = "overlap restriction"
OV["panel_note"] = ("OVERLAP restriction: events also linked under v3. NOT a ticker match. "
                    "All 58 dropped events are CONTROL; 0 treated.")
t10 = pd.concat([LO, top, OV], ignore_index=True)
t10.to_csv(OUT / "table10.csv", index=False)
prov(10, "LOCO range", "full_coef/loco_min/loco_max/sign_flips", "outputs/essay3_q3/loo.csv", "3 rows", "scripts/227")
prov(10, "variance shares", "final_cik/name/share/sign_flip", "outputs/essay3_v4/f1_cv3_variance_shares.csv",
     "top 10 per window", "scripts/229")
prov(10, "overlap restriction", "coef/p_cv3/p_wcr", "outputs/essay3_v4/239_v3_overlap_sensitivity.csv",
     "all rows", "scripts/239")
check("T10 top-ten panel has <= 10 rows per window",
      bool((top.groupby("window").size() <= 10).all()))

# ---------------------------------------------------------------- TABLE 11
log("TABLE 11 — T-Mobile case rows (health flag omitted; accession citations only)")
TM = A[A["final_cik"] == 1283699].copy().sort_values("bdt")
E = pd.read_csv(need(V4 / "c2_departure_events.csv"), dtype={"first_accession": str, "accessions": str})
F = pd.read_csv(need(V4 / "c2_filing_codes.csv"), dtype={"accession": str})
fdate = dict(zip(F["accession"], F["filing_date"]))
ex = E[(E["cik"] == 1283699) & (E["grp"] == "exec")].copy()
ex["fd"] = pd.to_datetime(ex["first_date"])
rows = []
for _, r in TM.iterrows():
    t0 = r["rdt"]
    w = ex[(ex["fd"] > t0) & (ex["fd"] <= t0 + pd.Timedelta(days=180))]
    pl = ex[(ex["fd"] > t0 - pd.Timedelta(days=180)) & (ex["fd"] <= t0)]
    rows.append(dict(
        org_name=r["org_name"], breach_date=str(r["breach_date"])[:10],
        reported_date=str(r["reported_date"])[:10], treated=int(r[TREAT]),
        placebo_exec=int(r["placebo_exec_departure_rd"]),
        exec_30=int(r["exec_departure_30_rd"]), exec_90=int(r["exec_departure_90_rd"]),
        exec_180=int(r["exec_departure_180_rd"]), ceo_180=int(r["ceo_departure_180_rd"]),
        director_180=int(r["director_departure_180_rd"]),
        exec_nopre_180=int(r["exec_departure_nopre_180_rd"]),
        days_to_first=r["days_to_first_exec_departure_rd"],
        outcome_persons="; ".join(w["persons"].astype(str)),
        outcome_accessions="; ".join(w["first_accession"].astype(str)),
        outcome_filing_dates="; ".join(str(fdate.get(a, "")) for a in w["first_accession"]),
        outcome_is_ceo="; ".join(w["is_ceo"].astype(str)),
        outcome_restated_only="; ".join(w["restated_only"].astype(str)),
        outcome_vacancy_only="; ".join(w["vacancy_only"].astype(str)),
        placebo_persons="; ".join(pl["persons"].astype(str)),
        placebo_accessions="; ".join(pl["first_accession"].astype(str))))
t11 = pd.DataFrame(rows)
t11["health_flag"] = "OMITTED BY INSTRUCTION (known false positive: benefit-continuation language)"
t11.to_csv(OUT / "table11.csv", index=False)
prov(11, "case rows", "windows + flags", "outputs/essay3_v4/e_analysis_sample.csv", "final_cik == 1283699", "scripts/224")
prov(11, "persons/accessions", "outcome_*/placebo_*", "outputs/essay3_v4/c2_departure_events.csv",
     "cik == 1283699 & grp == exec", "scripts/220")
check("T11 event count == 26", len(t11) == 26)
check("T11 carries no health column other than the omission note",
      [c for c in t11.columns if "health" in c.lower()] == ["health_flag"])
check("T11 180d exec-departure events == 13", int(t11["exec_180"].sum()) == 13)

pd.DataFrame(PROV).to_csv(OUT / "table_provenance.csv", index=False)
log("")
log("table_provenance.csv: %d cell-group rows" % len(PROV))
log("")
log("ASSERTION SUMMARY: %d failure(s)" % len(FAIL))
for f in FAIL:
    log("   FAILED: " + f)
(OUT / "244_tables.log").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\nwritten table01..table11 + table_provenance.csv")
