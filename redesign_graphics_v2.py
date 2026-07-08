import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import matplotlib.patches as mpatches

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']

# Color palette - muted, professional
colors = {
    'bg': '#ffffff',
    'light_bg': '#fafafa',
    'text_dark': '#1a1a1a',
    'text_light': '#666666',
    'accent': '#2c5aa0',
    'accent2': '#c74444',
    'neutral': '#cccccc',
}

# GRAPHIC 1: TIMING PARADOX - Minimal, tight
fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['bg'])
ax.set_facecolor(colors['bg'])

# Title only
ax.text(0.5, 0.92, 'Disclosure Timing ≠ Market Impact',
        ha='center', fontsize=24, fontweight='700', color=colors['text_dark'],
        transform=ax.transAxes)

# Large finding - center focus
ax.text(0.5, 0.75, '0.57%',
        ha='center', fontsize=72, fontweight='700', color=colors['accent'],
        transform=ax.transAxes)
ax.text(0.5, 0.65, 'p = 0.539 (not significant)',
        ha='center', fontsize=12, color=colors['text_light'],
        transform=ax.transAxes, style='italic')

# Clean divider
ax.plot([0.15, 0.85], [0.60, 0.60], color=colors['neutral'], linewidth=1.5, transform=ax.transAxes)

# Key finding - tight
ax.text(0.5, 0.50, 'Markets price the breach, not when it\'s disclosed.',
        ha='center', fontsize=14, fontweight='600', color=colors['text_dark'],
        transform=ax.transAxes)

ax.text(0.5, 0.42, 'N=898 firms | 2004-2025 | Event study',
        ha='center', fontsize=10, color=colors['text_light'],
        transform=ax.transAxes)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('linkedin_graphic_1_timing_v2.png', dpi=300, bbox_inches='tight', facecolor=colors['bg'], edgecolor='none', pad_inches=0.5)
print("Graphic 1 saved")
plt.close()

# GRAPHIC 2: REGULATION PENALTY - Bar focus, minimal text
fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['bg'])
ax.set_facecolor(colors['light_bg'])

ax.text(0.5, 0.92, 'Regulation & Market Valuation',
        ha='center', fontsize=24, fontweight='700', color=colors['text_dark'],
        transform=ax.transAxes)

# Simple comparison bars
x = [0.3, 0.7]
y = [0, -2.30]
colors_bar = ['#4CAF50', colors['accent2']]

bars = ax.bar(x, y, 0.15, color=colors_bar, edgecolor='none', transform=ax.transAxes)

# Value labels
ax.text(0.3, 0.08, '0.00%', ha='center', fontsize=20, fontweight='700', color=colors['text_dark'], transform=ax.transAxes)
ax.text(0.7, -0.05, '-2.30%', ha='center', fontsize=20, fontweight='700', color='white', transform=ax.transAxes)

# Category labels
ax.text(0.3, 0.35, 'Non-Regulated\nFirms', ha='center', fontsize=11, fontweight='600', color=colors['text_dark'], transform=ax.transAxes)
ax.text(0.7, 0.35, 'FCC-Regulated\nFirms', ha='center', fontsize=11, fontweight='600', color=colors['text_dark'], transform=ax.transAxes)

# Key insight - clean box
box = FancyBboxPatch((0.1, 0.02), 0.8, 0.12, boxstyle="round,pad=0.01",
                     edgecolor=colors['accent2'], facecolor='none', linewidth=2,
                     transform=ax.transAxes)
ax.add_patch(box)

ax.text(0.5, 0.09, 'Stricter rules correlate with larger penalties.',
        ha='center', fontsize=12, fontweight='600', color=colors['accent2'],
        transform=ax.transAxes)
ax.text(0.5, 0.04, 'N=898 | p=0.010',
        ha='center', fontsize=9, color=colors['text_light'],
        transform=ax.transAxes)

# Y-axis baseline
ax.plot([0, 1], [0.20, 0.20], color=colors['neutral'], linewidth=1, transform=ax.transAxes)

ax.set_xlim(-0.1, 1.1)
ax.set_ylim(-0.3, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('linkedin_graphic_2_regulation_v2.png', dpi=300, bbox_inches='tight', facecolor=colors['bg'], edgecolor='none', pad_inches=0.5)
print("Graphic 2 saved")
plt.close()

# GRAPHIC 3: FIRM SIZE HETEROGENEITY - Stacked/minimal
fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['bg'])
ax.set_facecolor(colors['light_bg'])

ax.text(0.5, 0.92, 'Mandatory Disclosure: Size Matters',
        ha='center', fontsize=24, fontweight='700', color=colors['text_dark'],
        transform=ax.transAxes)

# Data
categories = ['Q1\nSmall', 'Q2\nMid-Small', 'Q3\nMid-Large', 'Q4\nLarge']
values = [7.31, 3.64, -0.54, -3.39]
colors_bar = [colors['accent2'] if v > 0 else '#4CAF50' for v in values]
x_pos = np.array([0.15, 0.35, 0.55, 0.75])

bars = ax.bar(x_pos, np.array(values)/10, 0.12, color=colors_bar, edgecolor='none', transform=ax.transAxes)

# Value labels tight
for i, (bar, val) in enumerate(zip(bars, values)):
    y_offset = 0.03 if val > 0 else -0.02
    ax.text(x_pos[i], val/10 + y_offset, f'{val:.1f}%', ha='center', fontsize=11, fontweight='700',
            color=colors['text_dark'], transform=ax.transAxes)

# Category labels
for i, cat in enumerate(categories):
    ax.text(x_pos[i], -0.08, cat, ha='center', fontsize=10, fontweight='600', color=colors['text_dark'], transform=ax.transAxes)

# Key finding
ax.text(0.5, 0.15, 'Small firms face 2X the volatility impact of large firms',
        ha='center', fontsize=13, fontweight='600', color=colors['accent2'],
        transform=ax.transAxes)
ax.text(0.5, 0.08, 'N=891 | Volatility shock post-FCC 7-day rule',
        ha='center', fontsize=9, color=colors['text_light'],
        transform=ax.transAxes)

# Baseline
ax.plot([0, 1], [0.35, 0.35], color=colors['neutral'], linewidth=1, transform=ax.transAxes)

ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.12, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('linkedin_graphic_3_volatility_v2.png', dpi=300, bbox_inches='tight', facecolor=colors['bg'], edgecolor='none', pad_inches=0.5)
print("Graphic 3 saved")
plt.close()

print("\nPolished, minimal graphics created!")
