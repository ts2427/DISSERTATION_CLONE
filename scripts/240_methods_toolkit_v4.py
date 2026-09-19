"""
REBUILD V4 - METHODS TOOLKIT
=============================================================================
    python scripts/240_methods_toolkit_v4.py facts
    python scripts/240_methods_toolkit_v4.py check
    python scripts/240_methods_toolkit_v4.py lint <draft.md|.txt|.docx>

Offline. Reads only committed outputs. NOTHING here is typed by hand: every value in
METHODS_FACTS.md carries the file and the field it was read from, so a number that
moves in the pipeline moves here too, and a number that appears in the essay but not
here has no source.

facts  -> outputs/essay3_v4/methods/METHODS_FACTS.md
          key | value (prose-formatted) | source file | source field/row
          p-values as "p = .047" (no leading zero); counts with thousands commas.

check  -> the ledger closes step to step; treated + control == N at every step;
          subgroup tables sum to their totals. PASS/FAIL per check, nonzero exit on
          any FAIL.

lint   -> flags, with line numbers, the phrasings that have been wrong before, and
          EVERY number in the draft that does not appear in METHODS_FACTS.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

OUT = Path("outputs/essay3_v4")
V3 = Path("outputs/essay3_q2")
METH = OUT / "methods"
FACTS = METH / "METHODS_FACTS.md"

ROWS = []


def abort(msg):
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p))
    return Path(p)


# ------------------------------------------------------------------ formatting
def fmt_p(v):
    """p = .047 — no leading zero, three decimals, and never '< .001' silently."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    v = float(v)
    if v < 0.001:
        return "p < .001"
    return "p = " + ("%.3f" % v).lstrip("0")


def fmt_n(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:,}".format(int(v))


def fmt_f(v, nd=4):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return ("%." + str(nd) + "f") % float(v)


def fmt_pct(v, nd=1):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return ("%." + str(nd) + "f") % (100 * float(v)) + "%"


def add(key, value, src, field):
    ROWS.append(dict(key=key, value=value, source_file=str(src), source_field=field))


# ------------------------------------------------------------------ facts
def build_facts():
    METH.mkdir(parents=True, exist_ok=True)

    # ---- ledger ----
    led = pd.read_csv(require(OUT / "e_ledger.csv"))
    for _, r in led.iterrows():
        step = str(r["step"])
        add("ledger / " + step + " / N", fmt_n(r["N"]), "e_ledger.csv",
            "row '" + step + "', N")
        for col, lab in (("treated", "treated"), ("control", "control"),
                         ("treated_parent_ciks", "treated parent CIKs"),
                         ("treated_corporate_families", "treated corporate families"),
                         ("pre_rule_treated", "pre-rule treated"),
                         ("pre_rule_control", "pre-rule control")):
            if col in led.columns and pd.notna(r.get(col)):
                add("ledger / " + step + " / " + lab, fmt_n(r[col]),
                    "e_ledger.csv", "row '" + step + "', " + col)

    # ---- breach-type composition ----
    ev = pd.read_csv(require(OUT / "b_scope_events.csv"), low_memory=False)
    if "breach_type" in ev.columns:
        for bt, g in ev.groupby(ev["breach_type"].fillna("(missing)")):
            add("breach type / " + str(bt) + " / events", fmt_n(len(g)),
                "b_scope_events.csv", "breach_type == '" + str(bt) + "'")
            if "fcc_form499" in g.columns:
                add("breach type / " + str(bt) + " / treated",
                    fmt_n(int(g["fcc_form499"].sum())), "b_scope_events.csv",
                    "breach_type == '" + str(bt) + "', fcc_form499 == 1")

    # ---- analysis sample, T-Mobile share, anchor diagnostic ----
    d0 = pd.read_csv(require(OUT / "e_analysis_sample.csv"), low_memory=False)
    a = d0[d0["in_analysis_sample"] == 1]
    add("analysis sample / N", fmt_n(len(a)), "e_analysis_sample.csv",
        "in_analysis_sample == 1")
    tre = a[a["fcc_form499"] == 1]
    add("analysis sample / treated", fmt_n(len(tre)), "e_analysis_sample.csv",
        "fcc_form499 == 1")
    add("analysis sample / control", fmt_n(len(a) - len(tre)),
        "e_analysis_sample.csv", "fcc_form499 == 0")
    TM, SPRINT = 1283699, 101830
    ntm = int((tre["final_cik"] == TM).sum())
    nsp = int((tre["final_cik"] == SPRINT).sum())
    add("T-Mobile / events in the treated set", fmt_n(ntm),
        "e_analysis_sample.csv", "final_cik == 1283699, treated")
    add("T-Mobile / share of treated events", fmt_pct(ntm / max(1, len(tre))),
        "e_analysis_sample.csv", "computed from final_cik == 1283699")
    add("T-Mobile + Sprint / share of treated events",
        fmt_pct((ntm + nsp) / max(1, len(tre))), "e_analysis_sample.csv",
        "final_cik in (1283699, 101830)")
    if "bd180_before_rd" in a.columns:
        for g, lab in ((1, "treated"), (0, "control")):
            x = a[a["fcc_form499"] == g]
            add("anchor diagnostic / breach+180d ends before reported_date / " + lab,
                fmt_pct(x["bd180_before_rd"].mean()), "e_analysis_sample.csv",
                "bd180_before_rd mean, fcc_form499 == " + str(g))

    # ---- censoring margin ----
    cen = pd.read_csv(require(OUT / "232_censoring.csv"), low_memory=False)
    ok = cen[cen["status"] == "ok"].copy()
    for w in (30, 90, 180):
        col = "censored_%d_rd" % w
        if col in ok.columns:
            add("censoring / events censored at %dd (rd anchor)" % w,
                fmt_n(int(ok[col].sum())), "232_censoring.csv", col + " == 1")
    ok["_slack"] = (pd.to_datetime(ok["last_filing"], errors="coerce")
                    - (pd.to_datetime(ok["t0_rd"], errors="coerce")
                       + pd.Timedelta(days=180))).dt.days
    add("censoring / minimum margin (days)", fmt_n(ok["_slack"].min()),
        "232_censoring.csv", "min(last_filing - (t0_rd + 180d))")
    add("censoring / median margin (days)", fmt_n(ok["_slack"].median()),
        "232_censoring.csv", "median(last_filing - (t0_rd + 180d))")
    tight = ok.loc[ok["_slack"].idxmin()]
    add("censoring / tightest event",
        str(tight["org_name"]) + " " + str(tight["breach_date"])[:10],
        "232_censoring.csv", "argmin of the margin")

    # ---- inference ladder: G, G1, G*, CV, MDE, base rates ----
    F1 = pd.read_csv(require(OUT / "f1_ladder.csv"))
    for _, r in F1.iterrows():
        w = int(r["window"])
        for col, lab, f in (("G", "clusters G", fmt_n), ("G1", "treated clusters G1", fmt_n),
                            ("G_star", "effective clusters G*", lambda v: fmt_f(v, 1)),
                            ("cluster_size_cv", "cluster-size CV", lambda v: fmt_f(v, 3)),
                            ("coef", "coefficient", lambda v: fmt_f(v, 4)),
                            ("se_cv3", "CV3 SE", lambda v: fmt_f(v, 4)),
                            ("mde80_cv3", "MDE80", lambda v: fmt_f(v, 4)),
                            ("control_mean", "control base rate", lambda v: fmt_f(v, 4)),
                            ("treated_mean", "treated rate", lambda v: fmt_f(v, 4))):
            if col in F1.columns:
                add("F1 %dd / %s" % (w, lab), f(r[col]), "f1_ladder.csv",
                    "window == %d, %s" % (w, col))
        add("F1 %dd / CV3 p" % w, fmt_p(r["p_cv3"]), "f1_ladder.csv",
            "window == %d, p_cv3" % w)
        add("F1 %dd / WCR p" % w, fmt_p(r["p_wcr"]), "f1_ladder.csv",
            "window == %d, p_wcr" % w)

    # ---- placebo ----
    pl = pd.read_csv(require(OUT / "f4_placebo.csv"))
    add("placebo / coefficient", fmt_f(pl.iloc[0]["coef"], 4), "f4_placebo.csv", "coef")
    add("placebo / CV3 p", fmt_p(pl.iloc[0]["p_cv3"]), "f4_placebo.csv", "p_cv3")
    add("placebo / WCR p", fmt_p(pl.iloc[0]["p_wcr"]), "f4_placebo.csv", "p_wcr")

    # ---- outcome counts ----
    for fn, lab in (("f5_ceo.csv", "CEO-only"), ("f6_director.csv", "director-only")):
        p = OUT / fn
        if not p.exists():
            continue
        t = pd.read_csv(p)
        for _, r in t.iterrows():
            w = int(r["window"])
            for col, sub in (("treated_events", "treated"), ("control_events", "control")):
                if col in t.columns:
                    add("%s / %dd / %s events" % (lab, w, sub), fmt_n(r[col]), fn,
                        "window == %d, %s" % (w, col))

    # ---- validation: v3 rounds, the recall audit, and the v4 round ----
    # A validation key must name the ROUND, the CLASSIFIER VERSION, the SUBSET, the
    # VARIANT (A = any departure, B = new only) and, for the stratified audit, the
    # STRATUM. Without all five the keys collide across rounds - "exec departure /
    # recall" alone describes four different numbers - and a collision in a fact sheet
    # is worse than a missing row, because it silently resolves to whichever was written
    # last.
    def variant_of(row, field):
        v = str(row.get("variant", "") or "").strip()
        if v:
            return "variant " + v
        if re.search(r"\(A[:)]", field):
            return "variant A (any departure)"
        if re.search(r"\(B[:)]", field):
            return "variant B (new only)"
        return "variant n/a"

    def val_rows(path, rnd, clf_version, default_subset):
        p = Path(path)
        if not p.exists():
            return
        t = pd.read_csv(p)
        for _, r in t.iterrows():
            field = str(r.get("field", "") or "")
            # the v4 file embeds the scoring in the field: "PRIMARY (verified) | ..."
            scoring = str(r.get("scoring", "") or "")
            if "|" in field and not scoring:
                scoring, field = [x.strip() for x in field.split("|", 1)]
            subset = str(r.get("sample", "") or "") or default_subset
            stratum = str(r.get("stratum", "") or "") or "combined"
            parts = ["validation", rnd, "classifier " + clf_version, "subset " + subset,
                     variant_of(r, field), "stratum " + stratum]
            if scoring:
                parts.append(scoring)
            parts.append(field if field else "(all fields)")
            lab = " / ".join(x for x in parts if x)
            src_row = ("round=" + rnd + "; classifier=" + clf_version + "; subset="
                       + subset + "; stratum=" + stratum
                       + ("; scoring=" + scoring if scoring else "")
                       + "; field=" + field)
            for col, sub, f in (("n", "n", fmt_n),
                                ("agreement", "agreement", lambda v: fmt_f(v, 4)),
                                ("kappa", "kappa", lambda v: fmt_f(v, 4)),
                                ("ref_positives", "reference positives", fmt_n),
                                ("ref_Y", "reference positives", fmt_n),
                                ("clf_positives", "classifier positives", fmt_n),
                                ("clf_Y", "classifier positives", fmt_n),
                                ("precision", "precision", lambda v: fmt_f(v, 4)),
                                ("recall", "recall", lambda v: fmt_f(v, 4))):
                if col in t.columns and pd.notna(r.get(col)):
                    add(lab + " / " + sub, f(r[col]), p.name, src_row + "; " + col)
            for col, sub in (("precision_ci95", "precision 95% CI"),
                             ("recall_ci95", "recall 95% CI")):
                if col in t.columns and pd.notna(r.get(col)):
                    add(lab + " / " + sub + " (Clopper-Pearson)", str(r[col]),
                        p.name, src_row + "; " + col)

    val_rows(V3 / "d3_agreement.csv", "v3 round 1", "v1 (d39bc6d)",
             "calibration 50 + random 30")
    val_rows(V3 / "d3_r2_agreement.csv", "v3 round 2", "v2 (6f7be7a)", "random 30")
    val_rows(V3 / "d3_audit_recall_by_stratum.csv", "v3 recall audit", "v2 (6f7be7a)",
             "stratified 80")
    val_rows(OUT / "238_new_document_agreement.csv", "v4 new documents", "v2 (6f7be7a)",
             "random 30 of 450 v4-added")

    # ---- covariates: definitions and coverage ----
    DEFS = {"firm_size_log": "ln(at)", "leverage": "lt / at", "roa": "ni / at",
            "op_margin": "(sale - cogs - xsga) / sale"}
    cov = pd.read_csv(require(OUT.parent / "rebuild_v4" / "219_covariates_v4.csv"),
                      low_memory=False)
    for c, d in DEFS.items():
        add("covariate / " + c + " / definition", d,
            "scripts/219_wrds_funda_v4.py", "covars(), reproducing scripts/156")
        if c in cov.columns:
            add("covariate / " + c + " / events covered",
                fmt_n(int(cov[c].notna().sum())), "219_covariates_v4.csv",
                c + " non-missing")
    add("covariate / fiscal-year rule",
        "latest datadate strictly before breach_date, at most 550 days stale",
        "scripts/219_wrds_funda_v4.py", "covars(), STALE_DAYS")

    # ---- Gate 1: records lost, by reason ----
    g1 = Path("outputs/rebuild/GATE1_APPLIED_LEDGER.csv")
    if g1.exists():
        G1 = pd.read_csv(g1, low_memory=False)
        by = G1.groupby("final_grade")["n"].sum().sort_values(ascending=False)
        add("Gate 1 / records considered", fmt_n(int(G1["n"].sum())),
            g1.name, "sum of n")
        for grade, n in by.items():
            add("Gate 1 / records by grade / " + str(grade), fmt_n(n), g1.name,
                "final_grade == '" + str(grade) + "', sum of n")
        lost = by[[str(i).startswith(("EXCLUDED", "AMBIGUOUS")) for i in by.index]]
        add("Gate 1 / records lost (EXCLUDED or AMBIGUOUS)", fmt_n(int(lost.sum())),
            g1.name, "sum of n over EXCLUDED*/AMBIGUOUS grades")

    # ---- Gate 2: the adjacency-collapse rule AS CODED ----
    g2 = Path("outputs/rebuild/GATE2_ADJACENCY_SHEET.csv")
    if g2.exists():
        G2 = pd.read_csv(g2, low_memory=False)
        if "rule" in G2.columns:
            main_rule = G2["rule"].value_counts().idxmax()
            add("Gate 2 / adjacency-collapse rule as coded", str(main_rule), g2.name,
                "modal value of the rule column")
            for rule, n in G2["rule"].value_counts().items():
                add("Gate 2 / chains under rule / " + str(rule)[:60],
                    fmt_n(n), g2.name, "rule == that text")
        if "PROPOSED" in G2.columns:
            for k, n in G2["PROPOSED"].value_counts().items():
                add("Gate 2 / chains by disposition / " + str(k), fmt_n(n), g2.name,
                    "PROPOSED == '" + str(k) + "'")
        add("Gate 2 / adjacency chains examined", fmt_n(len(G2)), g2.name, "row count")

    # ---- CRSP step: events lost, by reason and group ----
    le = OUT.parent / "rebuild_v4" / "215_lost_events.csv"
    if le.exists():
        LE = pd.read_csv(le, low_memory=False)
        add("CRSP step / events lost (v3 linked, v4 not)", fmt_n(len(LE)),
            le.name, "row count")
        for cat, g in LE.groupby("category"):
            add("CRSP step / lost by reason / " + str(cat), fmt_n(len(g)), le.name,
                "category == '" + str(cat) + "'")
            if "group" in g.columns:
                for grp, gg in g.groupby(g["group"].fillna("(unstated)")):
                    add("CRSP step / lost by reason / " + str(cat) + " / " + str(grp),
                        fmt_n(len(gg)), le.name,
                        "category == '" + str(cat) + "', group == '" + str(grp) + "'")
        if "sub_cause" in LE.columns:
            for sc, g in LE.groupby(LE["sub_cause"].fillna("(unstated)")):
                add("CRSP step / lost by sub-cause / " + str(sc), fmt_n(len(g)),
                    le.name, "sub_cause == '" + str(sc) + "'")

    # ---- identity gate: T-Mobile exclusions ----
    lk = OUT.parent / "rebuild_v4" / "v4_212_links.csv"
    if lk.exists():
        LK = pd.read_csv(lk, low_memory=False)
        if "gate_excluded" in LK.columns:
            ge = LK[LK["gate_excluded"].astype(str).str.lower() == "true"]
            add("identity gate / events excluded (all firms)", fmt_n(len(ge)),
                lk.name, "gate_excluded is True")
            tm = ge[ge["final_cik"] == 1283699]
            add("identity gate / T-Mobile events excluded", fmt_n(len(tm)),
                lk.name, "gate_excluded is True, final_cik == 1283699")
            for cik, g in ge.groupby("final_cik"):
                add("identity gate / events excluded / CIK " + str(int(cik)),
                    fmt_n(len(g)), lk.name,
                    "gate_excluded is True, final_cik == " + str(int(cik)))

    # ---- outcome_cik divergence ----
    oc = OUT.parent / "rebuild_v4" / "234_outcome_cik.csv"
    if oc.exists():
        OC = pd.read_csv(oc, low_memory=False)
        if "differs_from_final" in OC.columns:
            add("outcome_cik / events where outcome_cik differs from final_cik",
                fmt_n(int(OC["differs_from_final"].sum())), oc.name,
                "sum of differs_from_final")
        if "outcome_rule" in OC.columns:
            for rule, g in OC.groupby(OC["outcome_rule"].fillna("(none)")):
                add("outcome_cik / events resolved by rule / " + str(rule),
                    fmt_n(len(g)), oc.name, "outcome_rule == '" + str(rule) + "'")

    # ---- breach-type composition on the ANALYSIS sample (405), not only scope (412) ----
    if "breach_type" in ev.columns:
        key = ["final_cik", "breach_date"]
        _ev = ev.copy()
        _ev["breach_date"] = _ev["breach_date"].astype(str).str[:10]
        _a = a.copy()
        _a["breach_date"] = _a["breach_date"].astype(str).str[:10]
        bt = _a.set_index(key).index.map(
            _ev.drop_duplicates(key).set_index(key)["breach_type"])
        _a = _a.assign(_bt=[str(x) if pd.notna(x) else "(missing)" for x in bt])
        for b, g in _a.groupby("_bt"):
            add("breach type (analysis sample) / " + str(b) + " / events",
                fmt_n(len(g)), "e_analysis_sample.csv + b_scope_events.csv",
                "in_analysis_sample == 1, breach_type == '" + str(b) + "'")
            add("breach type (analysis sample) / " + str(b) + " / treated",
                fmt_n(int(g["fcc_form499"].sum())),
                "e_analysis_sample.csv + b_scope_events.csv",
                "in_analysis_sample == 1, breach_type == '" + str(b)
                + "', fcc_form499 == 1")

    # ---- test counts by family ----
    it = pd.read_csv(require(OUT / "i_tests.csv"))
    for fam, g in it.groupby("family"):
        add("tests / " + str(fam), fmt_n(len(g)), "i_tests.csv",
            "family == '" + str(fam) + "'")
    add("tests / total", fmt_n(len(it)), "i_tests.csv", "row count")

    df = pd.DataFrame(ROWS, columns=["key", "value", "source_file", "source_field"])
    # A duplicate key silently resolves to whichever row was written last, so refuse to
    # emit the sheet at all rather than publish an ambiguous one.
    dup = df[df.duplicated("key", keep=False)].sort_values("key")
    if len(dup):
        for _, r in dup.head(20).iterrows():
            print("  DUPLICATE KEY: %s  <- %s" % (r["key"], r["source_file"]))
        abort("%d duplicate fact key(s) across %d distinct keys; every key must be unique"
              % (len(dup), dup["key"].nunique()))
    df.to_csv(METH / "METHODS_FACTS.csv", index=False)
    lines = ["# Essay 3 v4 — methods facts", "",
             "Generated by `scripts/240_methods_toolkit_v4.py facts`. Every value is read",
             "from a committed output; none is typed by hand. A number that is not in this",
             "table has no source, and `lint` will flag it.", "",
             "| key | value | source file | source field/row |",
             "|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r[c]).replace("|", "\\|")
                                       for c in df.columns) + " |")
    FACTS.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    print("wrote %s (%d facts)" % (FACTS, len(df)))
    return df


# ------------------------------------------------------------------ check
def run_check():
    results = []

    def rec(name, ok, detail=""):
        results.append((name, bool(ok), detail))
        print("  %s | %s%s" % ("PASS" if ok else "FAIL", name,
                               ("" if ok else "  -> " + detail)))

    led = pd.read_csv(require(OUT / "e_ledger.csv"))
    # 1. the ledger never grows step to step
    prev = None
    bad = []
    for _, r in led.iterrows():
        n = int(r["N"])
        if prev is not None and n > prev:
            bad.append("%s rises %d -> %d" % (r["step"], prev, n))
        prev = n
    rec("ledger closes step to step (N never rises)", not bad, "; ".join(bad))

    # 2. treated + control == N wherever both are recorded
    bad2 = []
    for _, r in led.iterrows():
        if pd.isna(r.get("treated")) or pd.isna(r.get("control")):
            continue
        if int(r["treated"]) + int(r["control"]) != int(r["N"]):
            bad2.append("%s: %d + %d != %d" % (r["step"], r["treated"], r["control"],
                                               r["N"]))
    rec("treated + control == N at every step", not bad2, "; ".join(bad2))

    # 3. the analysis sample matches the ledger's last step
    d0 = pd.read_csv(require(OUT / "e_analysis_sample.csv"), low_memory=False)
    a = d0[d0["in_analysis_sample"] == 1]
    last = led.iloc[-1]
    rec("analysis sample equals the ledger's final step",
        len(a) == int(last["N"]),
        "sample %d vs ledger %d" % (len(a), int(last["N"])))

    # 4. subgroup tables sum to their totals
    bad4 = []
    F1 = pd.read_csv(require(OUT / "f1_ladder.csv"))
    for _, r in F1.iterrows():
        if int(r["n"]) != len(a):
            bad4.append("F1 %dd n=%d vs sample %d" % (r["window"], r["n"], len(a)))
    se = OUT / "f1_se_diagnostics.csv"
    if se.exists():
        S = pd.read_csv(se)
        for _, r in S.iterrows():
            if int(r["treated_n"]) + int(r["control_n"]) != len(a):
                bad4.append("SE diag %dd: %d + %d != %d" % (
                    r["window"], r["treated_n"], r["control_n"], len(a)))
    rec("subgroup tables sum to the analysis sample", not bad4, "; ".join(bad4))

    # 5. the test ledger matches its family counts
    it = pd.read_csv(require(OUT / "i_tests.csv"))
    rec("test ledger total equals the sum of its families",
        len(it) == int(it.groupby("family").size().sum()), "")

    # 6. every fact carries a source
    if FACTS.exists():
        fdf = pd.read_csv(METH / "METHODS_FACTS.csv")
        miss = fdf[fdf["source_file"].isna() | (fdf["source_file"].astype(str) == "")]
        rec("every methods fact names a source file", len(miss) == 0,
            "%d without a source" % len(miss))
    else:
        rec("METHODS_FACTS.csv exists (run `facts` first)", False, str(FACTS))

    # every fact key unique
    if (METH / "METHODS_FACTS.csv").exists():
        fdf2 = pd.read_csv(METH / "METHODS_FACTS.csv")
        d2 = fdf2[fdf2.duplicated("key", keep=False)]
        rec("every methods fact key is unique", len(d2) == 0,
            "%d duplicated row(s): %s" % (len(d2),
                                          "; ".join(d2["key"].unique()[:3])))

    failed = [n for n, ok, _ in results if not ok]
    print("\n%d check(s), %d failed" % (len(results), len(failed)))
    return 1 if failed else 0


# ------------------------------------------------------------------ lint
PHRASES = [
    (r"Rule\s*37\.3", "Rule 37.3"),
    (r"September\s+28,\s*2007", "September 28, 2007"),
    (r"1,?054\s+breaches", "'1,054 breaches' (they are notification records, not breaches)"),
    (r"\bturnover\b", "'turnover' (the outcome is executive-officer departure)"),
    (r"natural\s+experiment", "'natural experiment'"),
    (r"\bcausal(ly)?\b", "'causal'/'causally'"),
    (r"5\.02\(b\)", "'5.02(b)'"),
    (r"\bBoardEx\b", "BoardEx"),
]
NUM_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+\.\d+|\.\d+|\d+)(?![\w])")


def read_draft(path):
    p = require(path)
    if p.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError:
            abort("reading .docx needs python-docx; convert to .md or .txt instead")
        return [para.text for para in Document(str(p)).paragraphs]
    return p.read_text(encoding="utf-8", errors="replace").splitlines()


def known_numbers():
    if not (METH / "METHODS_FACTS.csv").exists():
        abort("run `facts` first: " + str(METH / "METHODS_FACTS.csv") + " is missing")
    fdf = pd.read_csv(METH / "METHODS_FACTS.csv")
    out = set()
    for v in fdf["value"].astype(str):
        for m in NUM_RE.finditer(v):
            out.add(m.group(1))
            out.add(m.group(1).replace(",", ""))
            out.add(m.group(1).lstrip("0") or "0")
    return out


def run_lint(path):
    lines = read_draft(path)
    known = known_numbers()
    hits = []
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        for rx, lab in PHRASES:
            if re.search(rx, ln, re.I):
                hits.append((i, "PHRASE", lab, ln.strip()[:110]))
        # June 8, 2007 is only acceptable with "published"
        if re.search(r"June\s+8,\s*2007", ln, re.I) and "publish" not in low:
            hits.append((i, "PHRASE", "June 8, 2007 without 'published'",
                         ln.strip()[:110]))
        # "deadline" within 20 words of 64.2011
        if "64.2011" in ln and "deadline" in low:
            toks = re.findall(r"\S+", low)
            pos_d = [k for k, t in enumerate(toks) if "deadline" in t]
            pos_r = [k for k, t in enumerate(toks) if "64.2011" in t]
            if any(abs(x - y) <= 20 for x in pos_d for y in pos_r):
                hits.append((i, "PHRASE", "'deadline' within 20 words of 64.2011",
                             ln.strip()[:110]))
        # HC3 in a governing role
        if re.search(r"\bHC3\b", ln) and not re.search(
                r"disqualif|not\s+the\s+frame|never|anticonserv|do\s+not\s+read", low):
            hits.append((i, "PHRASE", "HC3 in a governing role", ln.strip()[:110]))
        # numbers with no source
        for m in NUM_RE.finditer(ln):
            tok = m.group(1)
            if tok in known or tok.replace(",", "") in known:
                continue
            if re.fullmatch(r"(19|20)\d{2}", tok):      # plain years
                continue
            if tok in {"30", "90", "180", "1", "2", "3", "4", "5"}:   # windows, small ordinals
                continue
            hits.append((i, "NUMBER", "'%s' is not in METHODS_FACTS.md" % tok,
                         ln.strip()[:110]))
    print("linted %s (%d lines)" % (path, len(lines)))
    if not hits:
        print("  no flags")
        return 0
    for i, kind, lab, ctx in hits:
        print("  line %-5d %-6s %s" % (i, kind, lab))
        print("        %s" % ctx)
    print("\n%d flag(s): %d phrase, %d number"
          % (len(hits), sum(1 for h in hits if h[1] == "PHRASE"),
             sum(1 for h in hits if h[1] == "NUMBER")))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Essay 3 v4 methods toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("facts")
    sub.add_parser("check")
    lp = sub.add_parser("lint")
    lp.add_argument("draft")
    a = ap.parse_args()
    if a.cmd == "facts":
        build_facts()
        return 0
    if a.cmd == "check":
        return run_check()
    return run_lint(a.draft)


if __name__ == "__main__":
    sys.exit(main())
