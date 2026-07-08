"""
LinkedIn Research Graphics Generator
Creates eye-catching visuals for dissertation findings
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']

# Color palette
COLOR_NEGATIVE = '#d62728'  # Red
COLOR_POSITIVE = '#2ca02c'  # Green
COLOR_NEUTRAL = '#1f77b4'   # Blue
COLOR_HIGHLIGHT = '#ff7f0e' # Orange

# ============================================================================
# GRAPHIC 1: H1 TIMING DOESN'T MATTER (Counterintuitive Finding)
# ============================================================================

fig1, ax1 = plt.subplots(figsize=(12, 8))
fig1.patch.set_facecolor('white')

# Title
ax1.text(0.5, 0.95, 'When Does Timing Matter for Stock Prices?',
         fontsize=28, fontweight='bold', ha='center', va='top',
         transform=ax1.transAxes)

# Subtitle
ax1.text(0.5, 0.87, 'Testing if immediate breach disclosure affects market valuation',
         fontsize=14, ha='center', va='top', style='italic', color='gray',
         transform=ax1.transAxes)

# Key Finding Box
finding_box = FancyBboxPatch((0.05, 0.60), 0.9, 0.20,
                              boxstyle="round,pad=0.02",
                              facecolor=COLOR_NEUTRAL, alpha=0.15,
                              edgecolor=COLOR_NEUTRAL, linewidth=2,
                              transform=ax1.transAxes)
ax1.add_patch(finding_box)

ax1.text(0.5, 0.75, 'Disclosure Timing: NO EFFECT on Returns',
         fontsize=18, fontweight='bold', ha='center', va='center',
         transform=ax1.transAxes, color=COLOR_NEUTRAL)

ax1.text(0.5, 0.67, 'Effect: 0.57% | p-value: 0.539 (NOT significant)',
         fontsize=14, ha='center', va='center',
         transform=ax1.transAxes, color='black')

# Implications
implications_y = 0.55
ax1.text(0.5, implications_y, 'Market Implications:',
         fontsize=14, fontweight='bold', ha='center', va='top',
         transform=ax1.transAxes)

implications = [
    '• Markets don\'t penalize delay—they price the breach itself',
    '• WHO discloses matters more than WHEN (regulation, firm type)',
    '• Mandatory 7-day rules may not protect investor interests as intended'
]

y_pos = implications_y - 0.05
for impl in implications:
    ax1.text(0.5, y_pos, impl, fontsize=12, ha='center', va='top',
             transform=ax1.transAxes)
    y_pos -= 0.06

# Data citation
ax1.text(0.5, 0.08, 'N=898 publicly-traded firms | 2004-2025 | TOST Equivalence Test',
         fontsize=10, ha='center', va='bottom', style='italic', color='gray',
         transform=ax1.transAxes)

ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis('off')

plt.tight_layout()
plt.savefig(r'C:\Users\mcobp\DISSERTATION_CLONE\linkedin_graphic_1_timing.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("Saved: linkedin_graphic_1_timing.png")
plt.close()

# ============================================================================
# GRAPHIC 2: REGULATION PENALTY (FCC Effect)
# ============================================================================

fig2, ax2 = plt.subplots(figsize=(12, 8))
fig2.patch.set_facecolor('white')

# Title
ax2.text(0.5, 0.95, 'Regulatory Compliance = Market Penalty?',
         fontsize=28, fontweight='bold', ha='center', va='top',
         transform=ax2.transAxes)

# Subtitle
ax2.text(0.5, 0.87, 'How FCC breach notification rules affect stock prices',
         fontsize=14, ha='center', va='top', style='italic', color='gray',
         transform=ax2.transAxes)

# Bar comparison
categories = ['FCC\nRegulated\nFirms', 'Non-Regulated\nFirms']
effects = [-2.30, 0.0]  # -2.30% for FCC, effectively 0 for non-regulated
colors_bar = [COLOR_NEGATIVE, COLOR_NEUTRAL]

y_pos_bar = np.arange(len(categories))
bars = ax2.barh(y_pos_bar, effects, color=colors_bar, alpha=0.7,
                 edgecolor='black', linewidth=2, height=0.4)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, effects)):
    label_x = val - 0.3 if val < 0 else val + 0.1
    ax2.text(label_x, bar.get_y() + bar.get_height()/2,
             f'{val:+.2f}%', fontsize=16, fontweight='bold',
             va='center', ha='right' if val < 0 else 'left')

ax2.set_yticks(y_pos_bar)
ax2.set_yticklabels(categories, fontsize=13, fontweight='bold')
ax2.set_xlabel('Stock Price Change (30-day CAR)', fontsize=12, fontweight='bold')
ax2.set_xlim(-3, 0.5)
ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax2.grid(axis='x', alpha=0.3)

# Key insight
insight_y = 0.45
ax2.text(0.5, insight_y, 'The Puzzle:',
         fontsize=14, fontweight='bold', ha='center', va='top',
         transform=ax2.transAxes)

ax2.text(0.5, insight_y - 0.07, 'Stricter regulations correlate with LARGER market penalties',
         fontsize=13, ha='center', va='top',
         transform=ax2.transAxes, style='italic')

insights = [
    '- Markets may view regulation as a negative signal about risk',
    '- FCC rules could increase costs (litigation, disclosure liability)',
    '- Or: markets punish sector concentration in regulated industries'
]

y_pos_insight = insight_y - 0.15
for insight in insights:
    ax2.text(0.5, y_pos_insight, insight, fontsize=11, ha='center', va='top',
             transform=ax2.transAxes)
    y_pos_insight -= 0.05

# Data citation
ax2.text(0.5, 0.02, 'N=898 | p=0.010 (significant) | Controls: firm size, leverage, ROA',
         fontsize=10, ha='center', va='bottom', style='italic', color='gray',
         transform=ax2.transAxes)

ax2.set_xlim(-3, 0.5)
ax2.set_ylim(-0.5, 1.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(r'C:\Users\mcobp\DISSERTATION_CLONE\linkedin_graphic_2_regulation.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("Saved: linkedin_graphic_2_regulation.png")
plt.close()

# ============================================================================
# GRAPHIC 3: VOLATILITY SHOCK BY FIRM SIZE
# ============================================================================

fig3, ax3 = plt.subplots(figsize=(12, 8))
fig3.patch.set_facecolor('white')

# Title
ax3.text(0.5, 0.95, 'Does Mandatory Disclosure Trigger Information Asymmetry?',
         fontsize=26, fontweight='bold', ha='center', va='top',
         transform=ax3.transAxes)

# Subtitle
ax3.text(0.5, 0.88, 'Volatility increase when FCC 7-day rule forces immediate disclosure',
         fontsize=14, ha='center', va='top', style='italic', color='gray',
         transform=ax3.transAxes)

# Data from H5 heterogeneity
firm_sizes = ['Small Firms\n(Q1)', 'Mid-Small\n(Q2)', 'Mid-Large\n(Q3)', 'Large Firms\n(Q4)']
volatility_increase = [7.31, 3.64, -0.54, -3.39]  # percentage points
p_values = [0.0032, 0.0138, 0.67, 0.0149]  # p-values
significant = [p < 0.05 for p in p_values]

# Color by significance and direction
colors_vol = []
for vol, sig in zip(volatility_increase, significant):
    if vol > 0 and sig:
        colors_vol.append(COLOR_NEGATIVE)  # Significant increase = red
    elif vol > 0 and not sig:
        colors_vol.append('#ffcccc')  # Non-sig increase = light red
    elif vol < 0 and sig:
        colors_vol.append(COLOR_POSITIVE)  # Significant decrease = green
    else:
        colors_vol.append('#ccffcc')  # Non-sig decrease = light green

x_pos = np.arange(len(firm_sizes))
bars = ax3.bar(x_pos, volatility_increase, color=colors_vol, alpha=0.8,
               edgecolor='black', linewidth=2, width=0.6)

# Add significance stars
for i, (bar, sig) in enumerate(zip(bars, significant)):
    height = bar.get_height()
    label = '**' if sig else 'ns'
    ax3.text(bar.get_x() + bar.get_width()/2, height + (0.5 if height > 0 else -0.5),
             label, fontsize=14, fontweight='bold', ha='center',
             va='bottom' if height > 0 else 'top')

ax3.set_xticks(x_pos)
ax3.set_xticklabels(firm_sizes, fontsize=12, fontweight='bold')
ax3.set_ylabel('Volatility Increase (percentage points)', fontsize=12, fontweight='bold')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
ax3.set_ylim(-5, 10)
ax3.grid(axis='y', alpha=0.3)

# Key finding
finding_y = 0.48
ax3.text(0.5, finding_y, 'Small Firms Most Affected:',
         fontsize=14, fontweight='bold', ha='center', va='top',
         transform=ax3.transAxes)

ax3.text(0.5, finding_y - 0.06, '+7.31% volatility shock for smallest firms (p=0.003)',
         fontsize=13, ha='center', va='top',
         transform=ax3.transAxes, color=COLOR_NEGATIVE, fontweight='bold')

findings_text = [
    '- Small firms face 2x the volatility impact of large firms',
    '- Mandatory disclosure creates asymmetric information costs',
    '- Policy trade-off: transparency vs. market stability'
]

y_pos_find = finding_y - 0.14
for txt in findings_text:
    ax3.text(0.5, y_pos_find, txt, fontsize=11, ha='center', va='top',
             transform=ax3.transAxes)
    y_pos_find -= 0.05

# Data citation
ax3.text(0.5, 0.02, 'N=891 | FCC × Immediate Disclosure Interaction | Controls: firm fundamentals + timing',
         fontsize=10, ha='center', va='bottom', style='italic', color='gray',
         transform=ax3.transAxes)

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(r'C:\Users\mcobp\DISSERTATION_CLONE\linkedin_graphic_3_volatility.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("Saved: linkedin_graphic_3_volatility.png")
plt.close()

print("")
print("="*70)
print("LinkedIn Graphics Generated Successfully!")
print("="*70)
