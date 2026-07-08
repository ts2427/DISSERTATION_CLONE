import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['font.size'] = 10

colors = {
    'bg': '#ffffff',
    'text': '#0f0f0f',
    'text_light': '#707070',
    'accent_blue': '#1f4e8e',
    'accent_red': '#c73333',
    'accent_green': '#38a84f',
}

# ===== GRAPHIC 1: TIMING =====
fig = plt.figure(figsize=(11, 8), facecolor=colors['bg'])
ax = fig.add_subplot(111, facecolor=colors['bg'])

# Title
fig.text(0.5, 0.88, 'Disclosure Timing ≠ Market Impact',
         ha='center', fontsize=22, fontweight='bold', color=colors['text'])

# Big number
fig.text(0.5, 0.70, '0.57%', ha='center', fontsize=80, fontweight='bold',
         color=colors['accent_blue'])

# Stat line
fig.text(0.5, 0.60, 'p-value: 0.539 (not significant)',
         ha='center', fontsize=11, color=colors['text_light'], style='italic')

# Thin line
ax.plot([0.2, 0.8], [0.55, 0.55], color='#d0d0d0', linewidth=1, transform=ax.transAxes)

# Finding
fig.text(0.5, 0.48, 'Markets price the breach itself, not when it\'s disclosed.',
         ha='center', fontsize=13, fontweight='600', color=colors['text'])

# Metadata
fig.text(0.5, 0.40, 'Sample: 898 firms | Period: 2004–2025 | Method: Event study with TOST equivalence test',
         ha='center', fontsize=9, color=colors['text_light'])

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.savefig('linkedin_graphic_1_timing_v2.png', dpi=300, bbox_inches='tight',
            facecolor=colors['bg'], edgecolor='none', pad_inches=0.4)
print("Graphic 1 done")
plt.close()

# ===== GRAPHIC 2: REGULATION PENALTY =====
fig = plt.figure(figsize=(11, 8), facecolor=colors['bg'])
ax = fig.add_subplot(111, facecolor=colors['bg'])

# Title
fig.text(0.5, 0.88, 'Regulation & Market Valuation',
         ha='center', fontsize=22, fontweight='bold', color=colors['text'])

# Two bars with labels above
# Non-regulated: 0%
rect1 = plt.Rectangle((0.25, 0.40), 0.08, 0.0, facecolor=colors['accent_green'],
                       edgecolor='none', transform=ax.transAxes)
ax.add_patch(rect1)
fig.text(0.29, 0.42, '0.00%', ha='center', fontsize=16, fontweight='bold', color=colors['text'])
fig.text(0.29, 0.32, 'Non-Regulated\nFirms', ha='center', fontsize=11, fontweight='600', color=colors['text'])

# Regulated: -2.30%
bar_height = 0.25  # Scaled visualization
rect2 = plt.Rectangle((0.67, 0.40 - bar_height), 0.08, bar_height, facecolor=colors['accent_red'],
                       edgecolor='none', transform=ax.transAxes)
ax.add_patch(rect2)
fig.text(0.71, 0.38, '-2.30%', ha='center', fontsize=16, fontweight='bold', color='white')
fig.text(0.71, 0.08, 'FCC-Regulated\nFirms', ha='center', fontsize=11, fontweight='600', color=colors['text'])

# Baseline
ax.plot([0.15, 0.85], [0.40, 0.40], color='#d0d0d0', linewidth=1.5, transform=ax.transAxes)
fig.text(0.13, 0.40, '0%', ha='right', fontsize=9, color=colors['text_light'], va='center')

# Key insight box
box = FancyBboxPatch((0.12, 0.50), 0.76, 0.10, boxstyle="round,pad=0.008",
                     edgecolor=colors['accent_red'], facecolor='none', linewidth=2,
                     transform=ax.transAxes)
ax.add_patch(box)

fig.text(0.5, 0.56, 'Stricter regulations correlate with larger market penalties.',
         ha='center', fontsize=12, fontweight='600', color=colors['accent_red'], transform=ax.transAxes)
fig.text(0.5, 0.51, 'N=898 | p=0.010 (significant)',
         ha='center', fontsize=9, color=colors['text_light'], transform=ax.transAxes)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.savefig('linkedin_graphic_2_regulation_v2.png', dpi=300, bbox_inches='tight',
            facecolor=colors['bg'], edgecolor='none', pad_inches=0.4)
print("Graphic 2 done")
plt.close()

# ===== GRAPHIC 3: FIRM SIZE =====
fig = plt.figure(figsize=(11, 8), facecolor=colors['bg'])
ax = fig.add_subplot(111, facecolor=colors['bg'])

# Title
fig.text(0.5, 0.88, 'Mandatory Disclosure: Asymmetric Impact',
         ha='center', fontsize=22, fontweight='bold', color=colors['text'])

# Four bars
categories = ['Q1\nSmall', 'Q2\nMid-Small', 'Q3\nMid-Large', 'Q4\nLarge']
values = [7.31, 3.64, -0.54, -3.39]
x_positions = [0.18, 0.38, 0.58, 0.78]
colors_bars = [colors['accent_red'], colors['accent_red'], colors['accent_green'], colors['accent_green']]

# Scale for visualization
scale = 0.03  # 1% = 3% of height

for i, (cat, val, x, col) in enumerate(zip(categories, values, x_positions, colors_bars)):
    if val >= 0:
        rect = plt.Rectangle((x - 0.04, 0.40), 0.08, val * scale, facecolor=col,
                            edgecolor='none', transform=ax.transAxes)
    else:
        rect = plt.Rectangle((x - 0.04, 0.40 + val * scale), 0.08, abs(val) * scale, facecolor=col,
                            edgecolor='none', transform=ax.transAxes)
    ax.add_patch(rect)

    # Value label
    y_label = 0.42 + val * scale if val >= 0 else 0.38 + val * scale
    fig.text(x, y_label, f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold', color=colors['text'])

    # Category
    fig.text(x, 0.25, cat, ha='center', fontsize=10, fontweight='600', color=colors['text'])

# Baseline
ax.plot([0.1, 0.9], [0.40, 0.40], color='#d0d0d0', linewidth=1.5, transform=ax.transAxes)
fig.text(0.08, 0.40, '0%', ha='right', fontsize=9, color=colors['text_light'], va='center')

# Key finding
fig.text(0.5, 0.56, 'Small firms experience 2X the volatility impact of large firms.',
         ha='center', fontsize=12, fontweight='600', color=colors['accent_red'])

fig.text(0.5, 0.50, 'Volatility shock following FCC 7-day disclosure mandate',
         ha='center', fontsize=10, color=colors['text_light'])

fig.text(0.5, 0.43, 'N=891 | ** p<0.01, * p<0.05',
         ha='center', fontsize=9, color=colors['text_light'])

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.savefig('linkedin_graphic_3_volatility_v2.png', dpi=300, bbox_inches='tight',
            facecolor=colors['bg'], edgecolor='none', pad_inches=0.4)
print("Graphic 3 done")
plt.close()

print("\nAll 3 polished graphics generated.")
