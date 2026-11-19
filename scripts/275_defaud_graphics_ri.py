"""
DEFENSE AUDIT — DECK GRAPHICS G8: RANDOMIZATION-INFERENCE DRAW HISTOGRAMS (script 275)
=====================================================================================
Script 250 computed the 9,999 parent-CIK randomization draws for Essay 3 v4 but wrote only summary
statistics. This script re-runs 250's own code (its module source up to the variant runs is exec'd
unchanged: sample asserts, reproduction assert against f1_ladder/f4_placebo, fast path) and then
repeats 250's run_variant draw loop for variant C1 with the same seed (default_rng(250)), the same
pool (all 119 parent CIKs) and B = 9,999.

Asserts before writing: the RI p-values for the coefficient reproduce the committed
outputs/defense_supplement/e3_randomization_inference.csv (C1 rows) exactly to 4 dp
(.9037 / .5961 / .8455 at 30 / 90 / 180 days), and coef_obs matches to 6 dp.

Writes ONLY outputs/defense_audit/graphics/g8_ri_histograms.csv (40-bin counts per window, with
edges and the observed coefficient) and g8_ri_histograms.log. No draws are written.
Reads nothing new; changes no committed file.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC250 = Path('scripts/250_defsup_e3_randomization_inference.py')
OUT = Path('outputs/defense_audit/graphics')
MARK = "rows = run_variant('C1 all parents', np.arange(G))"
NBINS = 40

src = SRC250.read_text(encoding='utf-8')
if src.count(MARK) != 1:
    sys.exit('script 250 layout changed: variant marker not found once')
NS = {'__name__': 'defaud_250', '__file__': str(SRC250)}
exec(compile(src.split(MARK)[0], str(SRC250), 'exec'), NS)   # 250's setup + reproduction assert, unchanged

G, B, SEED, G1 = NS['G'], NS['B'], NS['SEED'], NS['G1']
assert (SEED, B, G, G1) == (250, 9_999, 119, 13)
rng = np.random.default_rng(SEED)                    # as in 250 run_variant
idx = NS['draw_sets'](rng, np.arange(G), B)
T = NS['to_T'](idx)
Bs = np.vstack([NS['fast_stats'](T[lo:lo + 500])[0] for lo in range(0, B, 500)])
b_obs = NS['b_obs']

ref = pd.read_csv('outputs/defense_supplement/e3_randomization_inference.csv')
ref = ref[ref.variant == 'C1 all parents'].set_index('outcome')
expect = {'exec_departure_30_rd': .9037, 'exec_departure_90_rd': .5961, 'exec_departure_180_rd': .8455}
rows, L = [], []
for j, (y, w) in enumerate(NS['OUTCOMES']):
    if y not in expect:
        continue
    p_b = (np.sum(np.abs(Bs[:, j]) >= abs(b_obs[j]) - 1e-12) + 1) / (B + 1)
    ok = (round(p_b, 4) == expect[y] == float(ref.loc[y, 'ri_p_coef'])
          and round(b_obs[j], 6) == float(ref.loc[y, 'coef_obs'])
          and abs(Bs[:, j].std() - float(ref.loc[y, 'draw_coef_sd'])) < 5e-7)
    msg = (f'{y}: RI p {p_b:.4f} (committed {ref.loc[y, "ri_p_coef"]}, expected {expect[y]}); '
           f'coef_obs {b_obs[j]:+.6f} (committed {ref.loc[y, "coef_obs"]}); draw sd {Bs[:, j].std():.6f} '
           f'(committed {ref.loc[y, "draw_coef_sd"]}) -> {"PASS" if ok else "FAIL"}')
    print(msg)
    L.append(msg)
    assert ok, 'headline RI values do not reproduce; nothing written'
    counts, edges = np.histogram(Bs[:, j], bins=NBINS)
    for k in range(NBINS):
        rows.append(dict(window_days=w, outcome=y, variant='C1 all parents', bin=k + 1, bin_lo=round(edges[k], 6),
                         bin_hi=round(edges[k + 1], 6), count=int(counts[k]), draws=B, seed=SEED,
                         coef_obs=round(b_obs[j], 6), ri_p_coef=round(p_b, 4),
                         obs_bin=int(np.clip(np.searchsorted(edges, b_obs[j], side='right'), 1, NBINS)),
                         source='scripts/275 re-run of scripts/250 C1 draw loop; headline check vs '
                                'outputs/defense_supplement/e3_randomization_inference.csv row ' + y))
    assert sum(counts) == B

OUT.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(OUT / 'g8_ri_histograms.csv', index=False, lineterminator='\n')
(OUT / 'g8_ri_histograms.log').write_text('\n'.join(NS['L'] + [''] + L) + '\n', encoding='utf-8')
print(f'wrote {OUT / "g8_ri_histograms.csv"} ({len(rows)} rows)')
