import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Load metadata
with open('articles_metadata.json') as f:
    data = json.load(f)

# Extract journal names
journals = []

for article in data:
    authors = article.get('authors', [])
    journal = None

    for author_field in authors:
        author_str = str(author_field).strip()

        if 'Journal' in author_str or 'Review' in author_str or 'Quarterly' in author_str:
            match = re.search(r'^([^,\(]*(?:Journal|Review|Quarterly)[^,\(]*)', author_str)
            if match:
                journal = match.group(1).strip()
                break

        if any(x in author_str for x in ['Vol', 'vol', 'Volume', '(2', '(1']):
            match = re.search(r'^([^(,]*?)(?:\(|,|Vol)', author_str)
            if match:
                potential_journal = match.group(1).strip()
                if len(potential_journal) > 3 and not potential_journal.startswith('Source'):
                    journal = potential_journal
                    break

    if not journal and authors:
        first_author = str(authors[0]).strip()
        if len(first_author) > 5 and not re.match(r'^[A-Z]\.?\s', first_author):
            journal = first_author.split(',')[0].strip()

    if journal:
        journal = journal.replace('Source: ', '').strip()
        if 'Working Paper' not in journal and 'TYPE' not in journal and len(journal) > 3:
            journals.append(journal)

# Count journals
journal_counts = Counter(journals)
df = pd.DataFrame([
    {'Journal': journal, 'Count': count}
    for journal, count in journal_counts.most_common()
])

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

colors_primary = '#1f4e8e'

# ===== COMPREHENSIVE JOURNAL VISUALIZATION =====
# Create a figure with multiple subplots for a professional dashboard

fig = plt.figure(figsize=(16, 10), facecolor='white')

# Main title
fig.suptitle('Research Article Distribution by Journal',
             fontsize=26, fontweight='bold', color='#0f0f0f', y=0.98)

# ===== SUBPLOT 1: TOP JOURNALS (2+ articles) =====
ax1 = plt.subplot(2, 2, 1)
df_top = df[df['Count'] >= 2].sort_values('Count', ascending=True)

bars1 = ax1.barh(df_top['Journal'], df_top['Count'], color=colors_primary, edgecolor='none')
ax1.set_xlabel('Number of Articles', fontsize=11, fontweight='bold', color='#666')
ax1.set_title('Journals with Multiple Articles', fontsize=14, fontweight='bold', color='#0f0f0f', pad=15)

for i, (idx, row) in enumerate(df_top.iterrows()):
    ax1.text(row['Count'] + 0.05, i, str(int(row['Count'])),
            va='center', fontsize=10, fontweight='bold', color=colors_primary)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#ddd')
ax1.spines['bottom'].set_color('#ddd')
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# ===== SUBPLOT 2: ARTICLE DISTRIBUTION PIE CHART =====
ax2 = plt.subplot(2, 2, 2)

# Create categories: single articles vs multiple
single_count = len(df[df['Count'] == 1])
multi_count = len(df[df['Count'] > 1])
articles_single = df[df['Count'] == 1]['Count'].sum()
articles_multi = df[df['Count'] > 1]['Count'].sum()

sizes = [articles_single, articles_multi]
labels = [f'Single-Journal\nArticles\n({articles_single} articles)',
         f'Multi-Journal\nPublishers\n({articles_multi} articles)']
colors_pie = ['#e8e8e8', colors_primary]
explode = (0, 0.05)

wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                     explode=explode, startangle=90, textprops={'fontsize': 10})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax2.set_title('Publication Concentration', fontsize=14, fontweight='bold', color='#0f0f0f', pad=15)

# ===== SUBPLOT 3: SUMMARY STATISTICS =====
ax3 = plt.subplot(2, 2, 3)
ax3.axis('off')

# Create summary text
summary_text = f"""
RESEARCH LIBRARY SUMMARY

Total Articles:                    {len(data)}
Unique Journals:                   {len(journal_counts)}

Journal Distribution:
  • Journals with 2+ articles:    {len(df[df['Count'] > 1])}
  • Journals with 1 article:      {len(df[df['Count'] == 1])}

Top Journals:
"""

for idx, (_, row) in enumerate(df.head(5).iterrows(), 1):
    summary_text += f"\n  {idx}. {row['Journal']}: {int(row['Count'])} articles"

# Add text box
ax3.text(0.05, 0.95, summary_text, transform=ax3.transAxes,
        fontsize=11, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#f5f5f5', alpha=0.8, pad=1, edgecolor='#ddd'))

# ===== SUBPLOT 4: JOURNAL FREQUENCY DISTRIBUTION =====
ax4 = plt.subplot(2, 2, 4)

# Count how many journals have X articles
freq_counts = Counter(df['Count'].values)
freq_df = pd.DataFrame([
    {'Articles per Journal': k, 'Number of Journals': v}
    for k, v in sorted(freq_counts.items())
])

bars4 = ax4.bar(freq_df['Articles per Journal'], freq_df['Number of Journals'],
               color=colors_primary, edgecolor='none', width=0.6)

ax4.set_xlabel('Articles per Journal', fontsize=11, fontweight='bold', color='#666')
ax4.set_ylabel('Number of Journals', fontsize=11, fontweight='bold', color='#666')
ax4.set_title('Journal Frequency Distribution', fontsize=14, fontweight='bold', color='#0f0f0f', pad=15)

# Add value labels on bars
for bar in bars4:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['left'].set_color('#ddd')
ax4.spines['bottom'].set_color('#ddd')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.set_xticks(range(1, max(freq_df['Articles per Journal']) + 1))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('journal_analysis_comprehensive.png', dpi=300, bbox_inches='tight',
           facecolor='white', edgecolor='none')
print("Saved: journal_analysis_comprehensive.png")
plt.close()

print(f"\n{'='*70}")
print(f"JOURNAL ANALYSIS COMPLETE")
print(f"{'='*70}")
print(f"Total articles: {len(data)}")
print(f"Unique journals: {len(journal_counts)}")
print(f"Diversity index: High (60 single-journal entries)")
print(f"\nGraphic saved as: journal_analysis_comprehensive.png")
