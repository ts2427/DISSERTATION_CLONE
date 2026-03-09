import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

# ============================================================================
# VISUALIZATION 1: FCC EFFECT ON BREACH-TO-TURNOVER PATHWAY
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('FCC Regulation Reweights the Breach → Executive Turnover Pathway',
             fontsize=14, fontweight='bold', y=0.98)

# NON-FCC FIRM
ax1.set_title('Non-FCC Regulated Firm', fontsize=12, fontweight='bold')
ax1.set_xlim(-0.5, 4.5)
ax1.set_ylim(-0.5, 3.5)
ax1.axis('off')

# Nodes for non-FCC
breach_pos_1 = (2, 3)
stakeholder_pos_1 = (2, 2)
board_pos_1 = (2, 1)
exec_pos_1 = (2, 0)

# Draw nodes
for pos, label, color in [
    (breach_pos_1, 'Data Breach\nEvent', '#FF6B6B'),
    (stakeholder_pos_1, 'Stakeholder\nActivation', '#4ECDC4'),
    (board_pos_1, 'Board\nPressure', '#FFE66D'),
    (exec_pos_1, 'Executive\nDeparture\n(46.4%)', '#95E1D3'),
]:
    circle = plt.Circle(pos, 0.35, color=color, ec='black', linewidth=2, zorder=3)
    ax1.add_patch(circle)
    ax1.text(pos[0], pos[1], label, ha='center', va='center', fontsize=9, fontweight='bold')

# Draw edges with weights
edges_1 = [
    (breach_pos_1, stakeholder_pos_1, 'High', '#444444'),
    (stakeholder_pos_1, board_pos_1, 'Medium', '#666666'),
    (board_pos_1, exec_pos_1, 'Base:\n46.4%', '#888888'),
]

for start, end, label, color in edges_1:
    arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=25,
                           color=color, linewidth=2.5, zorder=2)
    ax1.add_patch(arrow)
    mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    ax1.text(mid_x + 0.6, mid_y, label, fontsize=8, style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8))

# FCC FIRM
ax2.set_title('FCC-Regulated Firm (Treatment)', fontsize=12, fontweight='bold')
ax2.set_xlim(-0.5, 4.5)
ax2.set_ylim(-0.5, 3.5)
ax2.axis('off')

# Add FCC regulator node
fcc_pos_2 = (0.5, 2)
breach_pos_2 = (2, 3)
stakeholder_pos_2 = (2, 2)
board_pos_2 = (2, 1)
exec_pos_2 = (2, 0)

# Draw FCC node
fcc_circle = plt.Circle(fcc_pos_2, 0.35, color='#FF1744', ec='black', linewidth=2, zorder=3)
ax2.add_patch(fcc_circle)
ax2.text(fcc_pos_2[0], fcc_pos_2[1], 'FCC\nRule 37.3', ha='center', va='center',
        fontsize=8, fontweight='bold', color='white')

# Draw nodes
for pos, label, color in [
    (breach_pos_2, 'Data Breach\nEvent', '#FF6B6B'),
    (stakeholder_pos_2, 'Stakeholder\nActivation', '#4ECDC4'),
    (board_pos_2, 'Board\nPressure', '#FFE66D'),
    (exec_pos_2, 'Executive\nDeparture\n(51.7%)', '#95E1D3'),
]:
    circle = plt.Circle(pos, 0.35, color=color, ec='black', linewidth=2, zorder=3)
    ax2.add_patch(circle)
    ax2.text(pos[0], pos[1], label, ha='center', va='center', fontsize=9, fontweight='bold')

# Draw FCC -> Firm edge (modulating effect)
fcc_arrow = FancyArrowPatch(fcc_pos_2, (breach_pos_2[0] - 0.4, breach_pos_2[1]),
                           arrowstyle='->', mutation_scale=20, color='#FF1744',
                           linewidth=2, linestyle='dashed', zorder=2)
ax2.add_patch(fcc_arrow)
ax2.text(0.8, 2.7, 'Mandatory\nTiming\nPressure', fontsize=7, style='italic', color='#FF1744', fontweight='bold')

# Draw edges with heavier weights
edges_2 = [
    (breach_pos_2, stakeholder_pos_2, 'Higher', '#FF1744'),
    (stakeholder_pos_2, board_pos_2, 'Higher', '#FF1744'),
    (board_pos_2, exec_pos_2, '+5.3pp\nFCC Effect', '#FF1744'),
]

for start, end, label, color in edges_2:
    arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=25,
                           color=color, linewidth=3, zorder=2)
    ax2.add_patch(arrow)
    mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    ax2.text(mid_x + 0.6, mid_y, label, fontsize=8, style='italic', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE6E6', edgecolor='#FF1744', linewidth=1.5))

plt.tight_layout()
plt.savefig('outputs/figures/GRAPH_FCC_Turnover_Mechanism.png', dpi=300, bbox_inches='tight')
print("Created: GRAPH_FCC_Turnover_Mechanism.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: TEMPORAL DECAY OF FCC EFFECT
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 8))
fig.suptitle('Temporal Decay: FCC Effect on Executive Turnover Over Time',
             fontsize=14, fontweight='bold', y=0.97)

# Three time windows
time_windows = ['30 Days', '90 Days', '180 Days']
fcc_effects = [3.71, 2.31, 1.19]
baseline = [46.4, 46.4, 46.4]

y_positions = [2.5, 1.5, 0.5]

for i, (window, effect, base, y_pos) in enumerate(zip(time_windows, fcc_effects, baseline, y_positions)):
    # Baseline rate
    baseline_circle = plt.Circle((1, y_pos), 0.25, color='#95E1D3', ec='black', linewidth=2, zorder=3)
    ax.add_patch(baseline_circle)
    ax.text(1, y_pos, f'{base:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(0.5, y_pos, f'Baseline:', ha='right', va='center', fontsize=10, fontweight='bold')

    # FCC effect
    fcc_circle = plt.Circle((2.5, y_pos), 0.25, color='#FF1744', ec='black', linewidth=2, zorder=3)
    ax.add_patch(fcc_circle)
    ax.text(2.5, y_pos, f'+{effect:.2f}pp', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

    # Total (baseline + effect)
    total = base + effect
    total_circle = plt.Circle((4, y_pos), 0.25, color='#FF6B6B', ec='black', linewidth=2, zorder=3)
    ax.add_patch(total_circle)
    ax.text(4, y_pos, f'{total:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(4.5, y_pos, f'Total:', ha='left', va='center', fontsize=10, fontweight='bold')

    # Time label
    ax.text(0.2, y_pos, window, ha='center', va='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE66D', edgecolor='black', linewidth=1.5))

    # Draw connecting arrows
    arrow1 = FancyArrowPatch((1.25, y_pos), (2.25, y_pos), arrowstyle='<->', mutation_scale=15,
                            color='#666', linewidth=1.5, zorder=2)
    ax.add_patch(arrow1)

    arrow2 = FancyArrowPatch((2.75, y_pos), (3.75, y_pos), arrowstyle='->', mutation_scale=15,
                            color='#666', linewidth=1.5, zorder=2)
    ax.add_patch(arrow2)

# Title box
title_box = FancyBboxPatch((0.2, 3.2), 3.8, 0.6, boxstyle='round,pad=0.1',
                           facecolor='#E8F4F8', edgecolor='#4ECDC4', linewidth=2)
ax.add_patch(title_box)
ax.text(2.1, 3.5, 'Mechanism: Stakeholder Salience Decay', ha='center', va='center',
       fontsize=11, fontweight='bold', style='italic')

# Add interpretation box
interp_text = ('The FCC effect is immediate and strong at 30 days (+3.71pp)\n'
               'but decays over 90 and 180 days as stakeholder pressure fades.\n'
               'This pattern is consistent with stakeholder salience theory:\n'
               'regulatory shock activates, then dissipates.')
ax.text(2.1, -0.3, interp_text, ha='center', va='top', fontsize=9,
       bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFFACD', edgecolor='#FFE66D', linewidth=1.5))

ax.set_xlim(0, 5)
ax.set_ylim(-1.2, 4.2)
ax.axis('off')

plt.tight_layout()
plt.savefig('outputs/figures/GRAPH_Temporal_Decay_FCC_Effect.png', dpi=300, bbox_inches='tight')
print("Created: GRAPH_Temporal_Decay_FCC_Effect.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: FULL ECOSYSTEM (ALL THREE ESSAYS)
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))
fig.suptitle('Dissertation Ecosystem: Three Pathways from Data Breach',
             fontsize=14, fontweight='bold', y=0.98)

# Central breach node
breach_pos = (2, 5)
breach_circle = plt.Circle(breach_pos, 0.4, color='#FF6B6B', ec='black', linewidth=2.5, zorder=3)
ax.add_patch(breach_circle)
ax.text(breach_pos[0], breach_pos[1], 'Data\nBreach', ha='center', va='center',
       fontsize=11, fontweight='bold', color='white')

# ESSAY 1 PATH: Breach -> Investor -> Stock Price
investor_pos = (0.5, 3.5)
stock_pos = (0.5, 1.5)

investor_circle = plt.Circle(investor_pos, 0.35, color='#4ECDC4', ec='black', linewidth=2, zorder=3)
ax.add_patch(investor_circle)
ax.text(investor_pos[0], investor_pos[1], 'Investor\nReaction', ha='center', va='center', fontsize=9, fontweight='bold')

stock_circle = plt.Circle(stock_pos, 0.35, color='#95E1D3', ec='black', linewidth=2, zorder=3)
ax.add_patch(stock_circle)
ax.text(stock_pos[0], stock_pos[1], 'CAR\n(Essay 1)', ha='center', va='center', fontsize=9, fontweight='bold')

# Essay 1 arrows
essay1_arr1 = FancyArrowPatch(breach_pos, investor_pos, arrowstyle='->', mutation_scale=20,
                             color='#4ECDC4', linewidth=2.5, zorder=2)
ax.add_patch(essay1_arr1)
essay1_arr2 = FancyArrowPatch(investor_pos, stock_pos, arrowstyle='->', mutation_scale=20,
                             color='#4ECDC4', linewidth=2.5, zorder=2)
ax.add_patch(essay1_arr2)

ax.text(0, 4.3, 'Market\nValuation', fontsize=10, fontweight='bold', style='italic', color='#4ECDC4')
ax.text(-0.5, 2.5, 'Finding: H1 null\n(+0.57%, NS)\nH2 significant:\n-2.20%**',
       fontsize=8, bbox=dict(boxstyle='round,pad=0.4', facecolor='#E0F7F6', edgecolor='#4ECDC4'))

# ESSAY 2 PATH: Breach -> Uncertainty -> Volatility
uncertainty_pos = (2, 3.5)
volatility_pos = (2, 1.5)

uncertainty_circle = plt.Circle(uncertainty_pos, 0.35, color='#FFD93D', ec='black', linewidth=2, zorder=3)
ax.add_patch(uncertainty_circle)
ax.text(uncertainty_pos[0], uncertainty_pos[1], 'Market\nUncertainty', ha='center', va='center', fontsize=9, fontweight='bold')

volatility_circle = plt.Circle(volatility_pos, 0.35, color='#FF8C42', ec='black', linewidth=2, zorder=3)
ax.add_patch(volatility_circle)
ax.text(volatility_pos[0], volatility_pos[1], 'Volatility\n(Essay 2)', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

# Essay 2 arrows
essay2_arr1 = FancyArrowPatch(breach_pos, uncertainty_pos, arrowstyle='->', mutation_scale=20,
                             color='#FFD93D', linewidth=2.5, zorder=2)
ax.add_patch(essay2_arr1)
essay2_arr2 = FancyArrowPatch(uncertainty_pos, volatility_pos, arrowstyle='->', mutation_scale=20,
                             color='#FF8C42', linewidth=2.5, zorder=2)
ax.add_patch(essay2_arr2)

ax.text(2, 4.3, 'Information\nAsymmetry', fontsize=10, fontweight='bold', style='italic', color='#FFD93D')
ax.text(2.5, 2.5, 'Finding: H5\nFCC increases vol\n+1.83%**',
       fontsize=8, bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF4E0', edgecolor='#FFD93D'))

# ESSAY 3 PATH: Breach -> Stakeholder -> Executive
stakeholder_pos = (3.5, 3.5)
executive_pos = (3.5, 1.5)

stakeholder_circle = plt.Circle(stakeholder_pos, 0.35, color='#95E1D3', ec='black', linewidth=2, zorder=3)
ax.add_patch(stakeholder_circle)
ax.text(stakeholder_pos[0], stakeholder_pos[1], 'Stakeholder\nPressure', ha='center', va='center', fontsize=9, fontweight='bold')

executive_circle = plt.Circle(executive_pos, 0.35, color='#FF1744', ec='black', linewidth=2, zorder=3)
ax.add_patch(executive_circle)
ax.text(executive_pos[0], executive_pos[1], 'Turnover\n(Essay 3)', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

# Essay 3 arrows
essay3_arr1 = FancyArrowPatch(breach_pos, stakeholder_pos, arrowstyle='->', mutation_scale=20,
                             color='#95E1D3', linewidth=2.5, zorder=2)
ax.add_patch(essay3_arr1)
essay3_arr2 = FancyArrowPatch(stakeholder_pos, executive_pos, arrowstyle='->', mutation_scale=20,
                             color='#FF1744', linewidth=2.5, zorder=2)
ax.add_patch(essay3_arr2)

ax.text(4, 4.3, 'Governance\nResponse', fontsize=10, fontweight='bold', style='italic', color='#95E1D3')
ax.text(3.5, 0.3, 'Finding: H6\nFCC increases turnover\n+5.3pp**\nDecays: 30d->90d->180d',
       fontsize=8, bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFE6E6', edgecolor='#FF1744'))

# FCC modulation (applies to all three)
fcc_pos = (2, 6.5)
fcc_circle = plt.Circle(fcc_pos, 0.4, color='#FF1744', ec='black', linewidth=2.5, zorder=3)
ax.add_patch(fcc_circle)
ax.text(fcc_pos[0], fcc_pos[1], 'FCC\nRule\n37.3', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

# FCC modulation arrows (dashed)
for target_pos, label in [(investor_pos, 'H2:\n-2.20%'),
                          (uncertainty_pos, 'H5:\n+1.83%'),
                          (stakeholder_pos, 'H6:\n+5.3pp')]:
    fcc_mod_arrow = FancyArrowPatch(fcc_pos, target_pos, arrowstyle='->', mutation_scale=18,
                                   color='#FF1744', linewidth=2, linestyle='dashed', zorder=2)
    ax.add_patch(fcc_mod_arrow)

ax.text(2, 7.2, 'Modulates all pathways', fontsize=9, style='italic', color='#FF1744', fontweight='bold')

# Bottom summary
summary_text = ('Unified Finding: Markets price firm characteristics, not disclosure speed.\n'
               'FCC regulation imposes simultaneous costs across market valuation, information quality, and governance.\n'
               'Aggregate economic cost: $1.15B across all three mechanisms.')
ax.text(2, -0.8, summary_text, ha='center', va='top', fontsize=9,
       bbox=dict(boxstyle='round,pad=0.8', facecolor='#F0F0F0', edgecolor='black', linewidth=2))

ax.set_xlim(-1, 5)
ax.set_ylim(-1.5, 7.5)
ax.axis('off')

plt.tight_layout()
plt.savefig('outputs/figures/GRAPH_Dissertation_Ecosystem.png', dpi=300, bbox_inches='tight')
print("Created: GRAPH_Dissertation_Ecosystem.png")
plt.close()

print("\nAll three graph visualizations created successfully!")
print("Files saved to outputs/figures/")
