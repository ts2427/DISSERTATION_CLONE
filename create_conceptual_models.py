#!/usr/bin/env python3
"""
Create 4 professional conceptual models for dissertation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os
from pathlib import Path

# Set output directory
output_dir = Path.cwd()

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'stimulus': '#1f77b4',      # Blue
    'mechanism': '#ff7f0e',     # Orange
    'outcome': '#2ca02c',       # Green
    'moderator': '#d62728',     # Red
    'control': '#9467bd'        # Purple
}

# ============================================================================
# MODEL 1: ESSAY 1 - MARKET REACTIONS
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'Essay 1: Market Reactions to Data Breaches',
        fontsize=18, fontweight='bold', ha='center')
ax.text(5, 9, 'How do disclosure timing and regulatory status affect stock market returns?',
        fontsize=12, ha='center', style='italic', color='#555')

# Boxes
boxes = [
    {'xy': (0.5, 6), 'width': 1.5, 'height': 1, 'label': 'Data Breach\nDisclosure', 'color': colors['stimulus']},
    {'xy': (3, 6), 'width': 1.5, 'height': 1, 'label': 'Timing Decision\n(Days to Disclosure)', 'color': colors['mechanism']},
    {'xy': (5.5, 6), 'width': 1.5, 'height': 1, 'label': 'Information\nQuality', 'color': colors['mechanism']},
    {'xy': (8, 6), 'width': 1.5, 'height': 1, 'label': 'Market\nValuation\n(CAR -0.74%)', 'color': colors['outcome']},
]

for box in boxes:
    fancy_box = FancyBboxPatch(box['xy'], box['width'], box['height'],
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=box['color'],
                              alpha=0.7, linewidth=2)
    ax.add_patch(fancy_box)
    ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2,
           box['label'], ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Arrows
arrow_props = dict(arrowstyle='->', lw=2.5, color='#333')
ax.annotate('', xy=(3, 6.5), xytext=(2, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(5.5, 6.5), xytext=(4.5, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(8, 6.5), xytext=(7, 6.5), arrowprops=arrow_props)

# Moderators and Controls
ax.text(5, 4.8, 'Key Finding: Timing does NOT affect returns (+0.57%, p=0.539, NS)',
        fontsize=12, ha='center', bbox=dict(boxstyle='round', facecolor='#ffffcc', alpha=0.8))

ax.text(5, 4, 'What DOES matter:', fontsize=11, fontweight='bold', ha='center')
moderators = ['FCC Status (-2.20%***)', 'Health Breach (-2.51%***)', 'Prior Breaches (-0.22%*** per breach)']
for i, mod in enumerate(moderators):
    ax.text(5, 3.5 - i*0.4, f'• {mod}', fontsize=10, ha='center')

ax.text(5, 1.5, 'Controls: Firm size, leverage, ROA, industry FE, year FE | Sample: 926 breaches with CRSP data',
        fontsize=9, ha='center', style='italic', color='#555')

plt.tight_layout()
plt.savefig(str(output_dir / 'Conceptual_Model_1_Essay1_MarketReactions.png'), dpi=300, bbox_inches='tight')
plt.close()

print('[OK] Model 1 created: Essay 1 - Market Reactions')

# ============================================================================
# MODEL 2: ESSAY 2 - INFORMATION ASYMMETRY
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'Essay 2: Information Asymmetry & Cost of Capital',
        fontsize=18, fontweight='bold', ha='center')
ax.text(5, 9, 'Does mandatory disclosure timing affect market uncertainty and cost of capital?',
        fontsize=12, ha='center', style='italic', color='#555')

# Boxes
boxes = [
    {'xy': (0.5, 6), 'width': 1.5, 'height': 1, 'label': 'Data Breach\nOccurrence', 'color': colors['stimulus']},
    {'xy': (3, 6), 'width': 1.5, 'height': 1, 'label': 'Timing\nRequirement\n(FCC: 7 days)', 'color': colors['mechanism']},
    {'xy': (5.5, 6), 'width': 1.5, 'height': 1, 'label': 'Investigation\nIncompleteness', 'color': colors['mechanism']},
    {'xy': (8, 6), 'width': 1.5, 'height': 1, 'label': 'Market\nUncertainty\n(Volatility +1.68-5.02%)', 'color': colors['outcome']},
]

for box in boxes:
    fancy_box = FancyBboxPatch(box['xy'], box['width'], box['height'],
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=box['color'],
                              alpha=0.7, linewidth=2)
    ax.add_patch(fancy_box)
    ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2,
           box['label'], ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Arrows
arrow_props = dict(arrowstyle='->', lw=2.5, color='#333')
ax.annotate('', xy=(3, 6.5), xytext=(2, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(5.5, 6.5), xytext=(4.5, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(8, 6.5), xytext=(7, 6.5), arrowprops=arrow_props)

# Key Finding
ax.text(5, 4.8, 'Key Finding: Timing DOES affect uncertainty (paradoxical effect)',
        fontsize=12, ha='center', bbox=dict(boxstyle='round', facecolor='#ffffcc', alpha=0.8))

ax.text(5, 4, 'Mechanism:', fontsize=11, fontweight='bold', ha='center')
mechanisms = ['Forced early disclosure → incomplete information → higher uncertainty',
              'Volatility increase = cost of capital increase (~0.75bps per 1% volatility)',
              'Regulatory constraint reduces investigation quality']
for i, mech in enumerate(mechanisms):
    ax.text(5, 3.5 - i*0.4, f'• {mech}', fontsize=9.5, ha='center')

ax.text(5, 1.5, 'Controls: Pre-breach volatility, firm size, leverage, ROA | Sample: 916 breaches with volatility data',
        fontsize=9, ha='center', style='italic', color='#555')

plt.tight_layout()
plt.savefig(str(output_dir / 'Conceptual_Model_2_Essay2_InformationAsymmetry.png'), dpi=300, bbox_inches='tight')
plt.close()

print('[OK] Model 2 created: Essay 2 - Information Asymmetry')

# ============================================================================
# MODEL 3: ESSAY 3 - GOVERNANCE RESPONSE
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'Essay 3: Governance Response & Executive Turnover',
        fontsize=18, fontweight='bold', ha='center')
ax.text(5, 9, 'Does mandatory disclosure activate stakeholder pressure and governance changes?',
        fontsize=12, ha='center', style='italic', color='#555')

# Boxes
boxes = [
    {'xy': (0.5, 6), 'width': 1.5, 'height': 1, 'label': 'Data Breach\nEvent', 'color': colors['stimulus']},
    {'xy': (3, 6), 'width': 1.5, 'height': 1, 'label': 'Mandatory\nDisclosure\n(Public announcement)', 'color': colors['mechanism']},
    {'xy': (5.5, 6), 'width': 1.5, 'height': 1, 'label': 'Stakeholder\nActivation\n(Pressure)', 'color': colors['mechanism']},
    {'xy': (8, 6), 'width': 1.5, 'height': 1, 'label': 'Governance\nResponse\n(Turnover +5.3pp)', 'color': colors['outcome']},
]

for box in boxes:
    fancy_box = FancyBboxPatch(box['xy'], box['width'], box['height'],
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=box['color'],
                              alpha=0.7, linewidth=2)
    ax.add_patch(fancy_box)
    ax.text(box['xy'][0] + box['width']/2, box['xy'][1] + box['height']/2,
           box['label'], ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Arrows
arrow_props = dict(arrowstyle='->', lw=2.5, color='#333')
ax.annotate('', xy=(3, 6.5), xytext=(2, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(5.5, 6.5), xytext=(4.5, 6.5), arrowprops=arrow_props)
ax.annotate('', xy=(8, 6.5), xytext=(7, 6.5), arrowprops=arrow_props)

# Key Finding
ax.text(5, 4.8, 'Key Finding: Timing DOES affect governance (transient but significant)',
        fontsize=12, ha='center', bbox=dict(boxstyle='round', facecolor='#ffffcc', alpha=0.8))

ax.text(5, 4, 'Mechanism:', fontsize=11, fontweight='bold', ha='center')
mechanisms = ['Public disclosure triggers investor/regulator scrutiny',
              'Pressure activates board action → executive changes',
              'Effect peaks at 30 days (+3.71pp) then decays → crisis response, not reform']
for i, mech in enumerate(mechanisms):
    ax.text(5, 3.5 - i*0.4, f'• {mech}', fontsize=9.5, ha='center')

ax.text(5, 1.5, 'Outcome: Executive changes extracted from SEC 8-K filings | Sample: 896 breaches with governance data',
        fontsize=9, ha='center', style='italic', color='#555')

plt.tight_layout()
plt.savefig(str(output_dir / 'Conceptual_Model_3_Essay3_GovernanceResponse.png'), dpi=300, bbox_inches='tight')
plt.close()

print('[OK] Model 3 created: Essay 3 - Governance Response')

# ============================================================================
# MODEL 4: OVERALL DISSERTATION FRAMEWORK
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(8, 9.5, 'Dissertation Framework: Three Parallel Mechanisms',
        fontsize=20, fontweight='bold', ha='center')
ax.text(8, 9, 'How disclosure regulation affects firms through multiple independent channels',
        fontsize=13, ha='center', style='italic', color='#555')

# Central stimulus
center_box = FancyBboxPatch((6.5, 7.5), 3, 1,
                           boxstyle="round,pad=0.15",
                           edgecolor='black', facecolor=colors['stimulus'],
                           alpha=0.8, linewidth=2.5)
ax.add_patch(center_box)
ax.text(8, 8, 'FCC Data Breach\nNatural Experiment\n(Rule 37.3, 2007)',
       ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Three branches
branches = [
    {
        'title': 'ESSAY 1:\nMarket Valuation',
        'finding': 'Timing: NO effect\nFCC: -2.20%***',
        'outcome': 'CAR -0.74%',
        'x': 1.5,
        'color': colors['outcome']
    },
    {
        'title': 'ESSAY 2:\nInformation Asymmetry',
        'finding': 'Delay: +0.39bps/day\nFCC: +1.83%',
        'outcome': 'Volatility +1.68-5.02%',
        'x': 8,
        'color': colors['outcome']
    },
    {
        'title': 'ESSAY 3:\nGovernance Response',
        'finding': 'Timing: +5.3pp\nTransient: peaks 30d',
        'outcome': 'Executive Turnover',
        'x': 14.5,
        'color': colors['outcome']
    }
]

for branch in branches:
    # Arrow from center
    arrow = FancyArrowPatch((6.5, 8), (branch['x'] + 1.5, 5.5),
                          arrowstyle='->', mutation_scale=30, lw=2.5, color='#333')
    ax.add_patch(arrow)

    # Branch box
    branch_box = FancyBboxPatch((branch['x'], 3.5), 3, 1.8,
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=branch['color'],
                              alpha=0.7, linewidth=2)
    ax.add_patch(branch_box)

    # Content
    ax.text(branch['x'] + 1.5, 5, branch['title'],
           ha='center', fontsize=11, fontweight='bold', color='white')
    ax.text(branch['x'] + 1.5, 4.3, branch['finding'],
           ha='center', fontsize=9, color='white', style='italic')
    ax.text(branch['x'] + 1.5, 3.8, branch['outcome'],
           ha='center', fontsize=10, fontweight='bold', color='white')

# Unifying theory box
theory_box = FancyBboxPatch((1.5, 0.5), 13, 2.3,
                           boxstyle="round,pad=0.15",
                           edgecolor='#d62728', facecolor='#fff8dc',
                           alpha=0.9, linewidth=2.5, linestyle='--')
ax.add_patch(theory_box)

ax.text(8, 2.5, 'UNIFYING THEORY: Expectation-Based Market Pricing',
       ha='center', fontsize=12, fontweight='bold', color='#d62728')

ax.text(8, 2, 'FCC Penalty = f(Expected_Investigation_Time - Actual_Disclosure_Speed)',
       ha='center', fontsize=11, family='monospace', color='#333')

ax.text(8, 1.3,
       '• Markets do not reward disclosure speed (Essay 1: null)\n'
       '• But mandatory timing increases uncertainty if premature (Essay 2: +volatility)\n'
       '• And forced disclosure activates governance response (Essay 3: +turnover)\n'
       '• One-size-fits-all regulation creates differential distributional effects',
       ha='center', fontsize=9, color='#333', va='center')

plt.tight_layout()
plt.savefig(str(output_dir / 'Conceptual_Model_4_DissertationFramework.png'), dpi=300, bbox_inches='tight')
plt.close()

print('[OK] Model 4 created: Dissertation Framework')

print('\n' + '='*80)
print('ALL 4 CONCEPTUAL MODELS CREATED SUCCESSFULLY')
print('='*80)
print(f'\nLocation: {output_dir}')
print('\nFiles created:')
print('  1. Conceptual_Model_1_Essay1_MarketReactions.png')
print('  2. Conceptual_Model_2_Essay2_InformationAsymmetry.png')
print('  3. Conceptual_Model_3_Essay3_GovernanceResponse.png')
print('  4. Conceptual_Model_4_DissertationFramework.png')
print('\nAll saved at 300 DPI for professional presentations/proposals')
