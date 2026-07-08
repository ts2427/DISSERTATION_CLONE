import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']

colors = {
    'primary': '#1f77b4',
    'accent': '#d62728',
    'success': '#2ca02c',
    'neutral': '#7f7f7f',
    'light_bg': '#f8f9fa',
}

# GRAPHIC 1: TIMING PARADOX
fig = plt.figure(figsize=(14, 9), facecolor='white')
ax = fig.add_subplot(111, facecolor=colors['light_bg'])

fig.text(0.5, 0.95, 'Disclosure Timing: A Regulatory Paradox',
         ha='center', fontsize=28, fontweight='bold', color='#1a1a1a')
fig.text(0.5, 0.91, 'Does faster disclosure protect investors? The data says no.',
         ha='center', fontsize=14, style='italic', color='#666')

finding_box = FancyBboxPatch((0.1, 0.68), 0.8, 0.15,
                             boxstyle="round,pad=0.01",
                             edgecolor=colors['primary'],
                             facecolor='#e8f4f8', linewidth=2.5,
                             transform=fig.transFigure)
fig.patches.append(finding_box)

fig.text(0.5, 0.80, 'Market Impact of Disclosure Timing: 0.57% | p = 0.539',
         ha='center', fontsize=18, fontweight='bold', color=colors['primary'])
fig.text(0.5, 0.72, '(NOT statistically significant)',
         ha='center', fontsize=12, color='#666', style='italic')

insights_y = 0.60
fig.text(0.5, insights_y + 0.05, 'Key Insights',
         ha='center', fontsize=16, fontweight='bold', color='#1a1a1a')

insights = [
    '• Markets price the BREACH itself, not disclosure timing',
    '• Firm characteristics (regulated sector, prior breach history) matter far more',
    '• FCC 7-day rule may increase compliance costs without investor protection',
]

for i, insight in enumerate(insights):
    fig.text(0.12, insights_y - (i+1)*0.05, insight,
             ha='left', fontsize=11, color='#333')

impl_y = 0.30
fig.text(0.5, impl_y + 0.03, 'What This Means',
         ha='center', fontsize=14, fontweight='bold', color='#1a1a1a')

fig.text(0.12, impl_y - 0.03, 'For Policymakers:', fontsize=11, fontweight='bold', color=colors['accent'])
fig.text(0.12, impl_y - 0.07, 'Faster disclosure != Better protection. Redesign rules around actual market incentives.', fontsize=10, color='#555')

fig.text(0.12, impl_y - 0.13, 'For Security Leaders:', fontsize=11, fontweight='bold', color=colors['primary'])
fig.text(0.12, impl_y - 0.17, 'Focus on prevention & reputation, not disclosure timing. Markets care about WHO you are.', fontsize=10, color='#555')

fig.text(0.5, 0.02, 'Analysis: 898 publicly-traded firms, 2004-2025 | Event study methodology | TOST equivalence test',
         ha='center', fontsize=9, color='#999', style='italic')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('linkedin_graphic_1_timing_v2.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("Graphic 1 saved")
plt.close()

# GRAPHIC 2: REGULATION PENALTY
fig, ax = plt.subplots(figsize=(14, 9), facecolor='white')
ax.set_facecolor(colors['light_bg'])

fig.text(0.5, 0.95, 'Does Regulation Protect or Punish?',
         ha='center', fontsize=28, fontweight='bold', color='#1a1a1a')
fig.text(0.5, 0.91, 'How FCC data breach notification rules affect market valuation',
         ha='center', fontsize=14, style='italic', color='#666')

x_pos = [1, 3]
heights = [0.0, -2.30]
bar_colors = ['#90EE90', colors['accent']]
bar_width = 0.6

bars = ax.bar(x_pos, heights, bar_width, color=bar_colors, edgecolor='#333', linewidth=2.5)

ax.text(1, 0.15, '+0.00%', ha='center', fontsize=18, fontweight='bold', color='#333')
ax.text(3, -2.50, '-2.30%', ha='center', fontsize=18, fontweight='bold', color='white')

ax.text(1, 0.55, 'Non-Regulated\nFirms', ha='center', fontsize=12, fontweight='bold', color='#333')
ax.text(3, 0.55, 'FCC-Regulated\nFirms', ha='center', fontsize=12, fontweight='bold', color='#333')

ax.axhline(y=0, color='#333', linestyle='-', linewidth=2)
ax.set_ylabel('30-day CAR (%)', fontsize=12, fontweight='bold', color='#333')
ax.set_ylim(-3.5, 1)
ax.set_xlim(0, 4)
ax.set_xticks([])
ax.grid(axis='y', alpha=0.3, linestyle='--')

puzzle_box = FancyBboxPatch((0.05, -0.30), 0.9, 0.22,
                            boxstyle="round,pad=0.015",
                            edgecolor=colors['accent'],
                            facecolor='#ffe8e8', linewidth=2,
                            transform=ax.transAxes)
ax.add_patch(puzzle_box)

ax.text(0.5, 0.18, 'The Paradox', ha='center', fontsize=14, fontweight='bold',
        color=colors['accent'], transform=ax.transAxes)
ax.text(0.5, 0.10, 'Stricter regulations -> Larger market penalties', ha='center',
        fontsize=12, color='#333', transform=ax.transAxes)
ax.text(0.5, 0.03, 'Markets may view regulation as a negative signal, or compliance costs compound risk.',
        ha='center', fontsize=10, color='#555', transform=ax.transAxes, style='italic')

fig.text(0.5, 0.01, 'N=898 firms | p=0.010 (significant) | Controls: firm size, leverage, ROA',
         ha='center', fontsize=9, color='#999', style='italic')

plt.tight_layout()
plt.savefig('linkedin_graphic_2_regulation_v2.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("Graphic 2 saved")
plt.close()

# GRAPHIC 3: VOLATILITY BY FIRM SIZE
fig, ax = plt.subplots(figsize=(14, 9), facecolor='white')
ax.set_facecolor(colors['light_bg'])

fig.text(0.5, 0.95, 'Mandatory Disclosure Creates Winners and Losers',
         ha='center', fontsize=28, fontweight='bold', color='#1a1a1a')
fig.text(0.5, 0.91, 'Volatility impact of the FCC 7-day rule by firm size',
         ha='center', fontsize=14, style='italic', color='#666')

categories = ['Small\n(Q1)', 'Mid-Small\n(Q2)', 'Mid-Large\n(Q3)', 'Large\n(Q4)']
volatility = [7.31, 3.64, -0.54, -3.39]
colors_bars = [colors['accent'] if v > 0 else colors['success'] for v in volatility]
pvalues = ['p=0.003**', 'p=0.014*', 'ns', 'p=0.015*']

x_pos = np.arange(len(categories))
bars = ax.bar(x_pos, volatility, color=colors_bars, edgecolor='#333', linewidth=2.5, width=0.5)

for i, (bar, val, pval) in enumerate(zip(bars, volatility, pvalues)):
    height = bar.get_height()
    y_pos = height + (0.3 if height > 0 else -0.5)
    va = 'bottom' if height > 0 else 'top'
    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
            f'{val:.2f}%\n{pval}', ha='center', va=va,
            fontsize=11, fontweight='bold', color='#333')

ax.set_xticks(x_pos)
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')

ax.set_ylabel('Volatility Change (%)', fontsize=12, fontweight='bold', color='#333')
ax.axhline(y=0, color='#333', linestyle='-', linewidth=2)
ax.set_ylim(-5, 9)
ax.grid(axis='y', alpha=0.3, linestyle='--')

finding_box = FancyBboxPatch((0.05, -0.35), 0.9, 0.25,
                            boxstyle="round,pad=0.015",
                            edgecolor=colors['accent'],
                            facecolor='#ffe8e8', linewidth=2,
                            transform=ax.transAxes)
ax.add_patch(finding_box)

ax.text(0.5, -0.05, 'Small firms bear 2X the volatility cost of larger firms',
        ha='center', fontsize=13, fontweight='bold', color=colors['accent'], transform=ax.transAxes)
ax.text(0.5, -0.12, 'Mandatory immediate disclosure creates asymmetric burden:',
        ha='center', fontsize=11, color='#333', transform=ax.transAxes)
ax.text(0.5, -0.19, '• Less time to prepare disclosure | • Higher proportional legal costs | • Tighter cash constraints',
        ha='center', fontsize=10, color='#555', transform=ax.transAxes)

fig.text(0.5, 0.01, 'N=891 firms | ** p<0.01, * p<0.05, ns=not significant | Controls: firm fundamentals + timing effects',
         ha='center', fontsize=9, color='#999', style='italic')

plt.tight_layout()
plt.savefig('linkedin_graphic_3_volatility_v2.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("Graphic 3 saved")
plt.close()

print("\nAll 3 professional graphics redesigned!")
