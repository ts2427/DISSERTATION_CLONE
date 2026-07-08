import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import altair as alt
import pandas as pd
import numpy as np

# Data for all graphics (using Graphic 1: Timing Paradox)
finding = 0.57
pvalue = 0.539

print("Generating 4 versions of Graphic 1 (Timing Paradox)...\n")

# ===== VERSION 1: PLOTLY =====
print("1. Plotly version...")
fig1 = go.Figure()

# Add a simple bar for visual interest (effect size)
fig1.add_trace(go.Bar(
    x=['Effect Size'],
    y=[finding],
    marker=dict(color='#1f4e8e', line=dict(color='#1f4e8e', width=0)),
    text=[f'{finding}%'],
    textposition='outside',
    textfont=dict(size=48, color='#1f4e8e', family='Arial Black'),
    showlegend=False,
    hoverinfo='skip'
))

fig1.update_layout(
    title={
        'text': 'Disclosure Timing ≠ Market Impact',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 28, 'color': '#0f0f0f', 'family': 'Arial'}
    },
    xaxis=dict(showgrid=False, showline=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, showline=False, zeroline=False, showticklabels=False),
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode=False,
    margin=dict(l=50, r=50, t=120, b=80),
    height=700,
    width=1000
)

# Add annotation for p-value
fig1.add_annotation(
    text=f'p-value: {pvalue} (not significant)',
    x=0.5, y=0.5,
    xref='paper', yref='paper',
    showarrow=False,
    font=dict(size=14, color='#666', family='Arial'),
    xanchor='center'
)

# Add finding text
fig1.add_annotation(
    text='Markets price the breach itself, not when it\'s disclosed.',
    x=0.5, y=0.15,
    xref='paper', yref='paper',
    showarrow=False,
    font=dict(size=14, color='#0f0f0f', family='Arial'),
    xanchor='center'
)

fig1.write_html('graphic_1_plotly.html')
fig1.write_image('graphic_1_plotly.png', width=1000, height=700)
print("   Saved: graphic_1_plotly.png")

# ===== VERSION 2: ALTAIR =====
print("2. Altair version...")
data_alt = pd.DataFrame({
    'Metric': ['Effect Size'],
    'Value': [finding]
})

chart = alt.Chart(data_alt).mark_bar(color='#1f4e8e').encode(
    x=alt.X('Metric:N', axis=None),
    y=alt.Y('Value:Q', axis=None)
).properties(
    width=600,
    height=500,
    title='Disclosure Timing ≠ Market Impact'
).configure_title(
    fontSize=24,
    fontWeight='bold',
    anchor='middle',
    color='#0f0f0f'
).configure_view(
    strokeWidth=0
).configure_axis(
    labelFontSize=0
)

chart.save('graphic_1_altair.html')
print("   Saved: graphic_1_altair.html")

# ===== VERSION 3: SEABORN + MATPLOTLIB ADVANCED =====
print("3. Seaborn + advanced matplotlib...")
sns.set_style("whitegrid")
sns.set_palette("husl")

fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
ax.set_facecolor('white')

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Big number
ax.text(0.5, 0.70, f'{finding}%', fontsize=120, fontweight='bold',
        color='#1f4e8e', ha='center', va='center', transform=ax.transAxes,
        family='sans-serif')

# Title
ax.text(0.5, 0.92, 'Disclosure Timing ≠ Market Impact',
        fontsize=26, fontweight='bold', color='#0f0f0f', ha='center',
        transform=ax.transAxes, family='sans-serif')

# Subtitle
ax.text(0.5, 0.62, f'p-value: {pvalue} (not significant)',
        fontsize=13, color='#666', ha='center', style='italic',
        transform=ax.transAxes, family='sans-serif')

# Finding
ax.text(0.5, 0.48, 'Markets price the breach itself, not when it\'s disclosed.',
        fontsize=14, fontweight='600', color='#0f0f0f', ha='center',
        transform=ax.transAxes, family='sans-serif')

# Metadata
ax.text(0.5, 0.38, 'Sample: 898 firms | Period: 2004–2025 | Method: Event study',
        fontsize=10, color='#888', ha='center',
        transform=ax.transAxes, family='sans-serif')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('graphic_1_seaborn.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("   Saved: graphic_1_seaborn.png")
plt.close()

# ===== VERSION 4: BOKEH =====
print("4. Bokeh version...")
from bokeh.plotting import figure, output_file, save
from bokeh.models import Title

output_file('graphic_1_bokeh.html')

p = figure(
    toolbar_location=None,
    width=1000,
    height=700,
    x_range=['Effect Size'],
    background_fill_color='white',
    border_fill_color='white'
)

p.vbar(x=['Effect Size'], top=[finding], width=0.3, fill_color='#1f4e8e', line_color='#1f4e8e')

p.title = Title(text='Disclosure Timing ≠ Market Impact', text_font_size='24pt', text_color='#0f0f0f')

p.xaxis.visible = False
p.yaxis.visible = False
p.grid.visible = False

save(p)
print("   Saved: graphic_1_bokeh.html")

print("\n✓ All 4 versions generated!")
print("\nCompare these files:")
print("  - graphic_1_plotly.png (Plotly)")
print("  - graphic_1_seaborn.png (Seaborn + matplotlib)")
print("  - graphic_1_altair.html (Altair)")
print("  - graphic_1_bokeh.html (Bokeh)")
print("\nWhich style looks most professional to you?")
