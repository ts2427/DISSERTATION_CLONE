import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

# Load metadata
with open('articles_metadata.json') as f:
    data = json.load(f)

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

colors = {
    'primary': '#1f4e8e',
    'accent': '#c73333',
    'neutral': '#707070',
}

# ===== ANALYSIS 1: BY THEME =====
all_themes = []
for article in data:
    themes = article.get('themes', [])
    all_themes.extend(themes)

theme_counts = Counter(all_themes)
theme_df = pd.DataFrame([
    {'Theme': theme, 'Count': count}
    for theme, count in theme_counts.most_common()
]).sort_values('Count', ascending=True)

# ===== ANALYSIS 2: BY YEAR =====
years = [int(article['year']) for article in data if article.get('year')]
year_counts = Counter(years)
year_df = pd.DataFrame([
    {'Year': year, 'Count': count}
    for year, count in sorted(year_counts.items())
])

# ===== VISUALIZATION 1: THEME DISTRIBUTION =====
fig, ax = plt.subplots(figsize=(12, 7), facecolor='white')
ax.set_facecolor('white')

bars = ax.barh(theme_df['Theme'], theme_df['Count'], color=colors['primary'], edgecolor='none')
ax.set_xlabel('Number of Articles', fontsize=12, fontweight='bold', color=colors['neutral'])
ax.set_title('Research Articles by Theme', fontsize=22, fontweight='bold', color='#0f0f0f', pad=20)

# Add value labels on bars
for i, (idx, row) in enumerate(theme_df.iterrows()):
    ax.text(row['Count'] + 0.1, i, str(int(row['Count'])), va='center', fontsize=11, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#ddd')
ax.spines['bottom'].set_color('#ddd')
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('article_distribution_by_theme.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("Saved: article_distribution_by_theme.png")
plt.close()

# ===== VISUALIZATION 2: PUBLICATION TIMELINE =====
fig, ax = plt.subplots(figsize=(14, 7), facecolor='white')
ax.set_facecolor('white')

ax.plot(year_df['Year'], year_df['Count'], marker='o', linewidth=2.5, markersize=8,
        color=colors['primary'], markerfacecolor=colors['primary'], markeredgecolor='white', markeredgewidth=1.5)

# Fill under curve
ax.fill_between(year_df['Year'], year_df['Count'], alpha=0.2, color=colors['primary'])

ax.set_xlabel('Publication Year', fontsize=12, fontweight='bold', color=colors['neutral'])
ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold', color=colors['neutral'])
ax.set_title('Articles Over Time', fontsize=22, fontweight='bold', color='#0f0f0f', pad=20)

# Add value labels on points
for idx, row in year_df.iterrows():
    ax.text(row['Year'], row['Count'] + 0.15, str(int(row['Count'])), ha='center',
            fontsize=10, fontweight='bold', color=colors['primary'])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#ddd')
ax.spines['bottom'].set_color('#ddd')
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_xticks(range(int(year_df['Year'].min()), int(year_df['Year'].max()) + 1, 2))

plt.tight_layout()
plt.savefig('article_distribution_by_year.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("Saved: article_distribution_by_year.png")
plt.close()

# ===== ANALYSIS SUMMARY =====
print(f"\n{'='*60}")
print(f"ARTICLE ANALYSIS SUMMARY")
print(f"{'='*60}")
print(f"Total articles: {len(data)}")
print(f"Years covered: {int(year_df['Year'].min())} - {int(year_df['Year'].max())}")
print(f"Unique themes: {len(theme_counts)}")
print(f"\nMost common themes:")
for theme, count in theme_counts.most_common(5):
    print(f"  • {theme}: {count} articles")

print(f"\nPublication timeline:")
print(f"  • Earliest: {int(year_df['Year'].min())}")
print(f"  • Latest: {int(year_df['Year'].max())}")
print(f"  • Peak year: {year_df.loc[year_df['Count'].idxmax(), 'Year']} ({int(year_df['Count'].max())} articles)")
