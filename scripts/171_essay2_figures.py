"""
ESSAY 2 QUERY 5 — PART C FIGURES (C3 specification curve, C4 power curve)
==========================================================================
Static print exhibits (matplotlib, single hue + neutral grays, one axis,
recessive grid, direct labels; no legend needed — single series per panel).
C3: sorted treatment coefficients with 95% CIs across the 193-spec grid
    (t29), decision dashboard beneath (Simonsohn-style layout, framed as a
    non-standard-error decomposition); breach-anchored (Type N) specs in
    lighter ink per the Del Giudice-Gangestad classification.
C4: MDE at 80% power (annualized pp) vs number of treated parent firms,
    cluster-mean approximation calibrated to the CV3 SE (scripts/165),
    control group and variance structure held fixed; companion table t27.
Outputs: outputs/figures/essay2_v2/fig_C3_spec_curve.png, fig_C4_power_curve.png
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/figures/essay2_v2')
OUTDIR.mkdir(parents=True, exist_ok=True)
INK = '#1a1a2e'
BLUE = '#2c5f8a'
LIGHT = '#a8bfd0'
GRAY = '#8a8a94'

# ----------------------------- C3: spec curve ------------------------------
g = pd.read_csv('outputs/tables/essay2_v2/t29_spec_grid.csv')
g = g.sort_values('coef').reset_index(drop=True)
g['lo'] = g['coef'] - 1.96 * g['se']
g['hi'] = g['coef'] + 1.96 * g['se']
is_breach = (g['anchor'] == 'breach')
draft = ((g.anchor == 'notification') & (g.basis == 'trading') & (g.L == 21)
         & (g.gap == 5) & (g.returns == 'log') & (g.winsor == 'raw')
         & (g.estimator == 'SD'))

NODES = [('anchor', ['notification', 'breach']),
         ('basis', ['trading', 'calendar']),
         ('L', [21, 31, 42]), ('gap', [0, 1, 3, 5]),
         ('returns', ['log', 'simple']), ('winsor', ['raw', 'w199'])]
n_dash = sum(len(v) for _, v in NODES)
fig = plt.figure(figsize=(10.5, 7.5), dpi=200)
gs = fig.add_gridspec(2, 1, height_ratios=[2.1, 1.6], hspace=0.06)
ax = fig.add_subplot(gs[0])
x = np.arange(len(g))
# equivalence band: quarter-SD reference SESOI (±0.2742 daily pp); nothing
# in the program is bounded inside it (Query 5 Part A) — the shading lets
# the reader see the whole program against its bounds in one image.
ax.axhspan(-0.2742, 0.2742, color='#f0f2f5', zorder=0)
ax.text(len(g) - 1, -0.255, 'equivalence region (±0.274 daily pp, quarter-SD '
        'reference SESOI) — no estimate is bounded inside it',
        fontsize=7.5, color=GRAY, ha='right', va='bottom')
ax.vlines(x, g['lo'], g['hi'], color=LIGHT, lw=0.7, zorder=1)
# greyscale-safe: notification-anchored = filled; breach-anchored (Type N)
# = hollow, so the distinction survives print.
ax.scatter(x[~is_breach], g.loc[~is_breach, 'coef'], s=7, color=BLUE,
           zorder=3, label=None)
ax.scatter(x[is_breach], g.loc[is_breach, 'coef'], s=9, facecolor='white',
           edgecolor=GRAY, lw=0.7, zorder=2)
xi = x[draft.values]
if len(xi):
    ax.scatter(xi, g.loc[draft, 'coef'], s=48, facecolor='white',
               edgecolor=INK, lw=1.4, zorder=4)
    ax.annotate('registered specification\n(+0.158, p = .43 CV1)',
                (xi[0], float(g.loc[draft, 'coef'].iloc[0])),
                xytext=(xi[0] - 68, 0.95), fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle='-', color=GRAY, lw=0.8))
ax.axhline(0, color=INK, lw=0.9)
ax.set_ylabel('Treatment coefficient (daily pp)\nwith 95% CI (CV1, parent CIK)',
              fontsize=9)
ax.set_xticks([])
ax.set_xlim(-2, len(g) + 1)
ax.spines[['top', 'right', 'bottom']].set_visible(False)
ax.grid(axis='y', color='#e6e6ea', lw=0.6)
ax.set_axisbelow(True)
ax.set_title('Treatment coefficient across 193 measurement specifications — '
             '0 of 193 significant at 5%; all positive',
             fontsize=10.5, loc='left', color=INK)
ax.text(1, ax.get_ylim()[1] * 0.92,
        'hollow points: breach-anchored specifications (Type N — construct-'
        'invalid, shown as documentation, not pooled)',
        fontsize=8, color=GRAY)
axd = fig.add_subplot(gs[1], sharex=ax)
ypos = 0
ylabels = []
for node, opts in NODES:
    for opt in opts:
        m = (g[node] == opt).values
        axd.scatter(x[m], np.full(m.sum(), ypos), marker='|', s=22,
                    color=np.where(is_breach[m], GRAY, BLUE), lw=0.7)
        ylabels.append(f'{node} = {opt}')
        ypos += 1
    ypos += 0.6
yt = []
ypos = 0
for node, opts in NODES:
    for _ in opts:
        yt.append(ypos)
        ypos += 1
    ypos += 0.6
axd.set_yticks(yt)
axd.set_yticklabels(ylabels, fontsize=7.5)
axd.invert_yaxis()
axd.set_xticks([])
axd.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
axd.set_xlabel('Specifications, sorted by coefficient', fontsize=9)
fig.text(0.01, 0.005,
         'Framed as a non-standard-error decomposition (Menkveld et al. 2024; '
         'Mitton 2022); no joint permutation test (Semken & Rossell 2022).',
         fontsize=7.5, color=GRAY)
fig.savefig(OUTDIR / 'fig_C3_spec_curve.png', bbox_inches='tight')
plt.close(fig)
print('saved fig_C3_spec_curve.png')

# ----------------------------- C4: power curve -----------------------------
G1, Gc = 11, 70
se_cv3 = 0.2331
sigma_c = se_cv3 / np.sqrt(1 / G1 + 1 / Gc)
ks = np.arange(2, 301)
mde = np.array([(stats.t.ppf(.975, k + Gc - 1) + stats.t.ppf(.80, k + Gc - 1))
                * sigma_c * np.sqrt(1 / k + 1 / Gc) for k in ks]) * np.sqrt(252)
asym = 2.8 * sigma_c * np.sqrt(1 / Gc) * np.sqrt(252)
fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=200)
ax.plot(ks, mde, color=BLUE, lw=2)
ax.axhline(asym, color=GRAY, lw=1, ls='--')
ax.text(300, asym + 0.12, f'variance floor {asym:.1f} pp\n(control side; unreachable below)',
        fontsize=8, color=GRAY, ha='right')
ax.axvline(G1, color=INK, lw=1, ls=':')
ax.text(G1 + 3, mde.max() * 0.97, '11 treated parents exist', fontsize=8.5,
        color=INK)
for tgt, k_req in [(5, 102), (4, 751)]:
    ax.axhline(tgt, color='#e0e0e6', lw=0.8)
    ax.text(2.5, tgt + 0.12, f'{tgt} pp target — requires ~{k_req} parents',
            fontsize=8, color=GRAY)
ax.set_xscale('log')
ax.set_xlabel('Number of treated parent firms (log scale)', fontsize=9)
ax.set_ylabel('Minimum detectable effect at 80% power\n(annualized pp, CV3-calibrated)',
              fontsize=9)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='y', color='#eeeef2', lw=0.6)
ax.set_axisbelow(True)
ax.set_title('Design resolution vs treated-parent count — a 3 pp effect is '
             'unreachable at any treated count',
             fontsize=10.5, loc='left', color=INK)
fig.text(0.01, 0.005,
         'Cluster-mean approximation holding the control group and variance '
         'structure fixed (scripts/165, t27); companion table t27_required_parents.csv.',
         fontsize=7.5, color=GRAY)
fig.savefig(OUTDIR / 'fig_C4_power_curve.png', bbox_inches='tight')
plt.close(fig)
print('saved fig_C4_power_curve.png')
