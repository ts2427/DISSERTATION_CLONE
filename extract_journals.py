import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Load metadata
with open('articles_metadata.json') as f:
    data = json.load(f)

# Extract journal names more intelligently
journals = []

for article in data:
    title = article.get('title', '').strip()
    authors = article.get('authors', [])
    year = article.get('year', '')

    journal = None

    # Strategy 1: Look for common journal keywords in authors
    for author_field in authors:
        author_str = str(author_field).strip()

        # Pattern: "Journal Name, Volume X, etc"
        if 'Journal' in author_str or 'Review' in author_str or 'Quarterly' in author_str:
            # Extract before comma or volume number
            match = re.search(r'^([^,\(]*(?:Journal|Review|Quarterly)[^,\(]*)', author_str)
            if match:
                journal = match.group(1).strip()
                break

        # Pattern: "Publication Name (YYYY) Volume No"
        if any(x in author_str for x in ['Vol', 'vol', 'Volume', '(2', '(1']):
            # Extract the publication name before volume/year
            match = re.search(r'^([^(,]*?)(?:\(|,|Vol)', author_str)
            if match:
                potential_journal = match.group(1).strip()
                if len(potential_journal) > 3 and not potential_journal.startswith('Source'):
                    journal = potential_journal
                    break

    # Strategy 2: Check if first author field looks like a journal
    if not journal and authors:
        first_author = str(authors[0]).strip()
        # Remove institutional affiliations
        if len(first_author) > 5 and not re.match(r'^[A-Z]\.?\s', first_author):
            journal = first_author.split(',')[0].strip()

    # Clean up common issues
    if journal:
        # Remove "Source:" prefix
        journal = journal.replace('Source: ', '').strip()
        # Remove working paper markers
        if 'Working Paper' not in journal and 'TYPE' not in journal and len(journal) > 3:
            journals.append(journal)

# Count journals
journal_counts = Counter(journals)

# Create DataFrame and sort by count
df = pd.DataFrame([
    {'Journal': journal, 'Count': count}
    for journal, count in journal_counts.most_common()
])

print(f"Total articles: {len(data)}")
print(f"Unique journals identified: {len(journal_counts)}")
print(f"\nJournals with articles:")
print(df.to_string(index=False))

# Save for reference
df.to_csv('journals_by_count.csv', index=False)
print(f"\nSaved to journals_by_count.csv")

# ===== VISUALIZATION: TOP JOURNALS =====
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

colors_primary = '#1f4e8e'

# Filter to journals with 2+ articles for cleaner viz
df_filtered = df[df['Count'] >= 2].sort_values('Count', ascending=True)

if len(df_filtered) > 0:
    fig, ax = plt.subplots(figsize=(12, max(7, len(df_filtered) * 0.4)), facecolor='white')
    ax.set_facecolor('white')

    bars = ax.barh(df_filtered['Journal'], df_filtered['Count'],
                   color=colors_primary, edgecolor='none')

    ax.set_xlabel('Number of Articles', fontsize=12, fontweight='bold', color='#707070')
    ax.set_title('Research Articles by Journal (2+ articles)',
                fontsize=22, fontweight='bold', color='#0f0f0f', pad=20)

    # Add value labels on bars
    for i, (idx, row) in enumerate(df_filtered.iterrows()):
        ax.text(row['Count'] + 0.05, i, str(int(row['Count'])),
               va='center', fontsize=10, fontweight='bold', color=colors_primary)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ddd')
    ax.spines['bottom'].set_color('#ddd')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('articles_by_journal.png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    print(f"\nSaved: articles_by_journal.png")
    plt.close()

# Print summary
print(f"\n{'='*70}")
print(f"JOURNAL BREAKDOWN")
print(f"{'='*70}")
print(f"Journals with 2+ articles: {len(df_filtered)}")
print(f"Journals with 1 article: {len(df[df['Count'] == 1])}")
print(f"\nMost cited journals:")
for idx, row in df.head(10).iterrows():
    print(f"  • {row['Journal']}: {int(row['Count'])} articles")
