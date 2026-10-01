"""
ESSAY 3 — DESCRIPTIVE COUNTS THE APPENDIX TABLES CITE
=============================================================================
    python scripts/246_essay3_descriptive_counts.py

Three groups of figures appear in the Results text and in the appendix notes but are
emitted by no committed CSV, so scripts/245 had to leave them blank or flag them
NOT REGENERABLE. This script computes them from committed inputs, names every input
file and prints each input's commit hash, and asserts every value against the figure as
the Results text writes it.

These are DESCRIPTIVE counts over the committed analysis sample: a mean, a maximum, a
count of singleton clusters, and four range-membership counts. No model is fitted, no
estimate is produced, and no verdict can move.

ON A MISMATCH the computed value is reported and KEPT. The Results figure is never
written into the output in place of what the data says.

Inputs (committed):
    Data/processed/rebuild_v4/CANONICAL_V4.csv     n_source_records, org_name, breach_date
    outputs/essay3_v4/e_analysis_sample.csv        the 405, final_cik, firm_size_log
Output:
    outputs/essay3_appendix/descriptive_counts.csv
"""
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
SAMP = Path("outputs/essay3_v4/e_analysis_sample.csv")
OUT = Path("outputs/essay3_appendix")
OUT.mkdir(parents=True, exist_ok=True)
ROWS, FAILED = [], []


def need(p):
    if not Path(p).exists():
        sys.exit("ABORT 246: missing committed input " + str(p))
    return Path(p)


def commit_of(p):
    r = subprocess.run(["git", "log", "--format=%h %ad", "--date=short", "-1", "--", str(p)],
                       capture_output=True, text=True)
    return (r.stdout or "").strip() or "(uncommitted)"


def emit(key, label, value, source_file, source_field, results_text):
    """Record one figure and assert it against the Results text."""
    got = str(value)
    want = str(results_text)
    ok = got == want
    if not ok:
        FAILED.append((key, want, got))
    ROWS.append(dict(key=key, label=label, value=got, results_text=want,
                     assertion="MATCH" if ok else "MISMATCH",
                     source_file=source_file, source_field=source_field))
    return ok


CAN = pd.read_csv(need(CANON), low_memory=False)
A = pd.read_csv(need(SAMP), low_memory=False)
A = A[A["in_analysis_sample"] == 1].copy()

print("=" * 94)
print("INPUTS AND THEIR COMMITS")
print("=" * 94)
for p in (CANON, SAMP):
    print("  %-46s %s" % (str(p).replace("\\", "/"), commit_of(p)))
print("  %-46s %s" % ("scripts/246_essay3_descriptive_counts.py",
                      commit_of("scripts/246_essay3_descriptive_counts.py")))

# ------------------------------------------------------------ records per event
n = CAN["n_source_records"].astype(float)
big = CAN.loc[n.idxmax()]
bdt = pd.to_datetime(big["breach_date"])
emit("records_per_event_mean", "Records per canonical event, mean",
     "%.2f" % n.mean(), str(CANON).replace("\\", "/"), "n_source_records", "1.55")
emit("records_per_event_max", "Records per canonical event, maximum",
     "%d" % int(n.max()), str(CANON).replace("\\", "/"), "n_source_records", "31")
emit("records_per_event_max_org", "Organisation of the maximum event",
     str(big["org_name"]), str(CANON).replace("\\", "/"), "org_name", "Cencora, Inc.")
emit("records_per_event_max_date", "Breach month of the maximum event",
     bdt.strftime("%B %Y"), str(CANON).replace("\\", "/"), "breach_date", "February 2024")
ROWS.append(dict(key="records_per_event_max_breach_date",
                 label="Breach date of the maximum event", value=str(big["breach_date"])[:10],
                 results_text="", assertion="",
                 source_file=str(CANON).replace("\\", "/"), source_field="breach_date"))

# ------------------------------------------------------------ cluster structure
g = A.groupby("final_cik").size().sort_values(ascending=False)
names = A.drop_duplicates("final_cik").set_index("final_cik")["org_name"]
top_cik = g.index[0]
emit("singleton_clusters", "Clusters holding exactly one analysis event",
     "%d" % int((g == 1).sum()), str(SAMP).replace("\\", "/"), "final_cik", "61")
emit("largest_cluster_name", "Largest cluster, name", str(names.get(top_cik)),
     str(SAMP).replace("\\", "/"), "org_name", "Intuit, Inc.")
emit("largest_cluster_events", "Largest cluster, events", "%d" % int(g.iloc[0]),
     str(SAMP).replace("\\", "/"), "final_cik", "78")
emit("largest_cluster_share", "Largest cluster, share of the 405",
     "%.1f" % (100.0 * g.iloc[0] / len(A)), str(SAMP).replace("\\", "/"),
     "final_cik", "19.3")
ROWS.append(dict(key="largest_cluster_cik", label="Largest cluster, CIK", value="%d" % int(top_cik),
                 results_text="", assertion="", source_file=str(SAMP).replace("\\", "/"),
                 source_field="final_cik"))
ROWS.append(dict(key="clusters_total", label="Parent CIKs in the analysis sample (G)",
                 value="%d" % A["final_cik"].nunique(), results_text="", assertion="",
                 source_file=str(SAMP).replace("\\", "/"), source_field="final_cik"))

# ------------------------------------------------------------ common support
t = A.loc[A["fcc_form499"] == 1, "firm_size_log"].astype(float)
c = A.loc[A["fcc_form499"] == 0, "firm_size_log"].astype(float)
c_in = int(((c >= t.min()) & (c <= t.max())).sum())
t_in = int(((t >= c.min()) & (t <= c.max())).sum())
SF = str(SAMP).replace("\\", "/")
for k, lab, v in [("support_treated_min", "firm_size_log, treated minimum", "%.4f" % t.min()),
                  ("support_treated_max", "firm_size_log, treated maximum", "%.4f" % t.max()),
                  ("support_control_min", "firm_size_log, control minimum", "%.4f" % c.min()),
                  ("support_control_max", "firm_size_log, control maximum", "%.4f" % c.max())]:
    ROWS.append(dict(key=k, label=lab, value=v, results_text="", assertion="",
                     source_file=SF, source_field="firm_size_log"))
emit("control_in_treated_range_n", "Control events inside the treated range, count",
     "%d" % c_in, SF, "firm_size_log", "287")
emit("control_in_treated_range_denom", "Control events, total", "%d" % len(c), SF,
     "fcc_form499", "296")
emit("control_in_treated_range_pct", "Control events inside the treated range, percent",
     "%.1f" % (100.0 * c_in / len(c)), SF, "firm_size_log", "97.0")
emit("treated_in_control_range_n", "Treated events inside the control range, count",
     "%d" % t_in, SF, "firm_size_log", "93")
emit("treated_in_control_range_denom", "Treated events, total", "%d" % len(t), SF,
     "fcc_form499", "109")
emit("treated_in_control_range_pct", "Treated events inside the control range, percent",
     "%.1f" % (100.0 * t_in / len(t)), SF, "firm_size_log", "85.3")

D = pd.DataFrame(ROWS)
D.to_csv(OUT / "descriptive_counts.csv", index=False)

print()
print("=" * 94)
print("FIGURES, AND THE ASSERTION AGAINST THE RESULTS TEXT")
print("=" * 94)
for _, r in D.iterrows():
    tag = "" if not r["assertion"] else ("  %s" % r["assertion"])
    want = "" if not r["results_text"] else ("   (Results text: %s)" % r["results_text"])
    print("  %-34s %-28s%s%s" % (r["key"], r["value"], tag, want))
print()
print("ASSERTIONS: %d checked, %d MISMATCH" % (int((D["assertion"] != "").sum()), len(FAILED)))
for k, want, got in FAILED:
    print("  MISMATCH %-34s Results text %-18s computed %s" % (k, want, got))
if not FAILED:
    print("  every figure reproduces the Results text exactly")
print()
print("written " + str(OUT / "descriptive_counts.csv").replace("\\", "/"))
