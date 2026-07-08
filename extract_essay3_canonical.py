"""
Essay 3 - Canonical governance-regression results
--------------------------------------------------
Persists the H6 logistic models to ONE CSV so every downstream doc
(tables, deck, intro) traces to a single source.

MATCHES: 91_essay3_governance_regressions.py exactly
- Controls: firm_size_log, leverage, roa (no moderators in main model)
- Dependent variables: executive_change_30d, executive_change_90d, executive_change_180d
- Key variables: immediate_disclosure, fcc_reportable
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

# --------- CONFIG: match 91_essay3_governance_regressions.py exactly ---------
DATA_PATH = "Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv"
OUT_PATH  = "outputs/tables/essay3/essay3_canonical_h6_results.csv"

DV_BY_WINDOW = {
    "30d":  "executive_change_30d",
    "90d":  "executive_change_90d",
    "180d": "executive_change_180d",
}
KEY_VARS = ["immediate_disclosure", "fcc_reportable"]
CONTROLS = ['firm_size_log', 'leverage', 'roa']  # from controls_base in original script
# ---------------------------------------------------------------------------


def discrete_ame_pp(res, data, var):
    """Average marginal effect (probability scale, in percentage points).
    Sets var=0 for everyone, then var=1, averages the pred-prob change.
    This is the '+5.3pp' style number."""
    d0 = data.copy()
    d0[var] = 0
    d1 = data.copy()
    d1[var] = 1
    return 100.0 * (res.predict(d1) - res.predict(d0)).mean()


def main():
    print("=" * 80)
    print("EXTRACTING ESSAY 3 CANONICAL H6 RESULTS")
    print("=" * 80)

    # Load data
    print(f"\n[Step 1] Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Total breaches: {len(df):,}")

    # Filter to CRSP-matched sample (matches 91_essay3_governance_regressions.py)
    analysis_df = df[df['has_crsp_data'] == True].copy()
    print(f"  CRSP-matched: {len(analysis_df):,}")

    # Prepare
    bool_cols = analysis_df.select_dtypes(include=['bool']).columns
    for col in bool_cols:
        analysis_df[col] = analysis_df[col].astype(int)

    # Turnover sample (matches script line 91-95)
    print(f"\n[Step 2] Building turnover analysis sample...")
    turnover_df = analysis_df[
        (analysis_df['executive_change_30d'].notna()) &
        (analysis_df['immediate_disclosure'].notna()) &
        (analysis_df['fcc_reportable'].notna())
    ].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

    print(f"  Turnover sample: {len(turnover_df):,}")
    print(f"    - 30d events: {(turnover_df['executive_change_30d'] == 1).sum():,}")
    print(f"    - 90d events: {(turnover_df['executive_change_90d'] == 1).sum():,}")
    print(f"    - 180d events: {(turnover_df['executive_change_180d'] == 1).sum():,}")

    # Run regressions
    print(f"\n[Step 3] Running logistic regressions by window...")
    rows = []

    for w, dv in DV_BY_WINDOW.items():
        print(f"\n  Processing {w} window...")

        needed = [dv] + KEY_VARS + CONTROLS
        model_data = turnover_df[needed].dropna().copy()
        model_data[dv] = model_data[dv].astype(int)

        print(f"    Sample: {len(model_data):,}")
        print(f"    Events: {(model_data[dv] == 1).sum()}")

        # Sanity check: KEY_VARS must be binary
        for v in KEY_VARS:
            assert set(model_data[v].dropna().unique()) <= {0, 1}, f"{v} is not binary"

        # Build formula (no FE - matches original script which doesn't use FE)
        formula = f"{dv} ~ " + " + ".join(KEY_VARS + CONTROLS)

        # Fit model
        try:
            res = smf.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

            # Get marginal effects
            me = res.get_margeff(at="overall", method="dydx")
            exog_names = [n for n in res.model.exog_names if n != "Intercept"]
            me_df = pd.DataFrame(
                {"ame": me.margeff, "ame_se": me.margeff_se, "ame_p": me.pvalues},
                index=exog_names,
            )

            # Extract for each KEY_VAR
            for v in KEY_VARS:
                discrete_pp = discrete_ame_pp(res, model_data, v)

                rows.append({
                    "window": w,
                    "variable": v,
                    "n": int(res.nobs),
                    "events": int((model_data[dv] == 1).sum()),
                    "event_pct": round(100.0 * (model_data[dv] == 1).sum() / len(model_data), 1),
                    "pseudo_r2": round(res.prsquared, 4),
                    "logit_coef": round(res.params[v], 4),
                    "logit_se": round(res.bse[v], 4),
                    "logit_z": round(res.tvalues[v], 3),
                    "logit_p": round(res.pvalues[v], 4),
                    "ame_dydx": round(me_df.loc[v, "ame"], 4),
                    "ame_se": round(me_df.loc[v, "ame_se"], 4),
                    "ame_p": round(me_df.loc[v, "ame_p"], 4),
                    "ame_discrete_pp": round(discrete_pp, 2),
                })

                print(f"      {v:22s}: coef={res.params[v]:+.4f} (p={res.pvalues[v]:.4f})   "
                      f"AME={discrete_pp:+.2f}pp (p={me_df.loc[v, 'ame_p']:.4f})")

        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    # Save results
    print(f"\n[Step 4] Saving results...")
    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    print(f"  Saved: {OUT_PATH}")

    # Summary table
    print(f"\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)

    for w in ["30d", "90d", "180d"]:
        print(f"\n[{w.upper()} WINDOW]")
        for _, r in out[out.window == w].iterrows():
            print(f"  {r['variable']:22s}  "
                  f"logit={r['logit_coef']:+.4f} (p={r['logit_p']:.4f})   "
                  f"AME={r['ame_discrete_pp']:+.2f}pp (p={r['ame_p']:.4f})   "
                  f"N={int(r['n'])}")

    # Key findings
    print(f"\n" + "=" * 80)
    print("KEY FINDINGS FOR H6")
    print("=" * 80)

    # Which variable owns +5.3pp at 30d?
    fcc_30d = out[(out.window == "30d") & (out.variable == "fcc_reportable")]['ame_discrete_pp'].values
    imm_30d = out[(out.window == "30d") & (out.variable == "immediate_disclosure")]['ame_discrete_pp'].values

    if len(fcc_30d) > 0:
        print(f"\nAt 30d:")
        print(f"  fcc_reportable:       {fcc_30d[0]:+.2f}pp")
        print(f"  immediate_disclosure: {imm_30d[0]:+.2f}pp")

        if abs(fcc_30d[0] - 5.3) < 1.0:
            print(f"  -> +5.3pp BELONGS TO: fcc_reportable ✓ (intro is aimed correctly)")
        elif abs(imm_30d[0] - 5.3) < 1.0:
            print(f"  -> +5.3pp BELONGS TO: immediate_disclosure (intro needs updating)")
        else:
            print(f"  -> Neither is near +5.3pp (data conflict?)")

    # Temporal pattern (decay vs strengthen)
    print(f"\nTemporal pattern for fcc_reportable (decay vs strengthen):")
    if len(out[out.variable == "fcc_reportable"]) >= 3:
        ame_30 = out[(out.window == "30d") & (out.variable == "fcc_reportable")]['ame_discrete_pp'].values[0]
        ame_90 = out[(out.window == "90d") & (out.variable == "fcc_reportable")]['ame_discrete_pp'].values[0]
        ame_180 = out[(out.window == "180d") & (out.variable == "fcc_reportable")]['ame_discrete_pp'].values[0]

        print(f"  30d: {ame_30:+.2f}pp")
        print(f"  90d: {ame_90:+.2f}pp")
        print(f"  180d: {ame_180:+.2f}pp")

        if ame_180 < ame_90 < ame_30:
            print(f"  -> DECAYS over time ✓ (supports urgency-decay prediction)")
        elif ame_180 > ame_90 > ame_30:
            print(f"  -> STRENGTHENS over time (urgency-decay prediction needs rethinking)")
        else:
            print(f"  -> Pattern is FLAT or MIXED")

    # Sign check
    print(f"\nSign consistency check (logit_coef vs ame must agree):")
    sign_errors = out[
        (out['logit_coef'] * out['ame_discrete_pp']) < 0
    ]
    if len(sign_errors) == 0:
        print(f"  ✓ All signs consistent")
    else:
        print(f"  ✗ SIGN MISMATCH FOUND (data problem):")
        print(sign_errors[['window', 'variable', 'logit_coef', 'ame_discrete_pp']])

    print(f"\n" + "=" * 80)


if __name__ == "__main__":
    main()
