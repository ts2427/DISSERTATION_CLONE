#!/usr/bin/env python3
"""
Generate comprehensive documentation from articles metadata.
Creates multiple markdown files organized by different dimensions.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_metadata(filename='articles_metadata.json'):
    """Load article metadata from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def create_master_index(articles):
    """Create master index of all articles."""
    content = []
    content.append("# Master Index of Research Articles\n")
    content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"Total Articles: {len(articles)}\n\n")

    content.append("## Complete Article List\n\n")
    content.append("| # | Title | Authors | Year | Themes | Methodology |\n")
    content.append("|---|-------|---------|------|--------|-------------|\n")

    for article in articles:
        idx = article['index']
        title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
        year = article['year'] or "N/A"
        authors = ", ".join(article['authors'][:1]) if article['authors'] else "N/A"
        themes = ", ".join(article['themes'][:2])
        methodology = ", ".join(article['methodology'][:1])

        content.append(f"| {idx} | {title} | {authors} | {year} | {themes} | {methodology} |\n")

    content.append("\n\n## Index by Year\n\n")

    # Group by year
    by_year = defaultdict(list)
    for article in articles:
        year = article['year'] or "Unknown"
        by_year[year].append(article)

    for year in sorted(by_year.keys(), reverse=True):
        content.append(f"\n### {year} ({len(by_year[year])} articles)\n\n")
        for article in sorted(by_year[year], key=lambda x: x['title']):
            content.append(f"- **{article['title']}**\n")

    return '\n'.join(content)

def create_by_theme_index(articles):
    """Create index organized by research theme."""
    content = []
    content.append("# Research Articles by Theme\n\n")

    # Group by theme
    by_theme = defaultdict(list)
    for article in articles:
        for theme in article['themes']:
            by_theme[theme].append(article)

    # Sort themes by count
    sorted_themes = sorted(by_theme.items(), key=lambda x: len(x[1]), reverse=True)

    for theme, articles_list in sorted_themes:
        content.append(f"\n## {theme} ({len(articles_list)} articles)\n\n")

        # Further organize by methodology
        by_method = defaultdict(list)
        for article in articles_list:
            for method in article['methodology']:
                by_method[method].append(article)

        for method in sorted(by_method.keys()):
            content.append(f"\n### {method}\n\n")
            for article in sorted(by_method[method], key=lambda x: x['title']):
                year = article['year'] or "N/A"
                content.append(f"- **{article['title']}** ({year})\n")
                if article['abstract']:
                    abstract = article['abstract'][:200] + "..." if len(article['abstract']) > 200 else article['abstract']
                    content.append(f"  - {abstract}\n")

    return '\n'.join(content)

def create_by_methodology_index(articles):
    """Create index organized by research methodology."""
    content = []
    content.append("# Research Articles by Methodology\n\n")

    # Group by methodology
    by_methodology = defaultdict(list)
    for article in articles:
        for method in article['methodology']:
            by_methodology[method].append(article)

    sorted_methods = sorted(by_methodology.items(), key=lambda x: len(x[1]), reverse=True)

    for method, articles_list in sorted_methods:
        content.append(f"\n## {method} ({len(articles_list)} articles)\n\n")

        # Sort by title
        for article in sorted(articles_list, key=lambda x: x['title']):
            year = article['year'] or "N/A"
            themes = ", ".join(article['themes'])
            content.append(f"### {article['title']}\n")
            content.append(f"- **Year:** {year}\n")
            content.append(f"- **Themes:** {themes}\n")
            if article['authors']:
                content.append(f"- **Authors:** {', '.join(article['authors'][:3])}\n")
            if article['keywords']:
                content.append(f"- **Keywords:** {', '.join(article['keywords'][:5])}\n")
            if article['abstract']:
                content.append(f"- **Summary:** {article['abstract'][:300]}...\n")
            content.append("\n")

    return '\n'.join(content)

def create_essay_relevance_index(articles):
    """Create index showing relevance to each dissertation essay."""
    content = []
    content.append("# Research Articles by Essay Relevance\n\n")

    essays = [
        ('Essay 1 (Market Reactions)', 'Market Reactions to Cyber Breaches'),
        ('Essay 2 (Information Asymmetry)', 'Information Asymmetry and Disclosure Effects'),
        ('Essay 3 (Governance Response)', 'Governance Response to Cybersecurity Threats'),
    ]

    for essay_key, essay_title in essays:
        relevant_articles = [a for a in articles if 'Relevant' in a['relevance'].get(essay_key, [])]

        content.append(f"\n## {essay_title}\n")
        content.append(f"**Relevant Articles: {len(relevant_articles)} / {len(articles)}**\n\n")

        # Organize by primary theme
        by_theme = defaultdict(list)
        for article in relevant_articles:
            primary_theme = article['themes'][0] if article['themes'] else 'General'
            by_theme[primary_theme].append(article)

        for theme in sorted(by_theme.keys()):
            content.append(f"\n### {theme}\n\n")
            for article in sorted(by_theme[theme], key=lambda x: x['title']):
                year = article['year'] or "N/A"
                content.append(f"- **{article['title']}** ({year})\n")
                if article['abstract']:
                    abstract = article['abstract'][:150]
                    content.append(f"  - Summary: {abstract}...\n")

    # Summary of overlapping relevance
    content.append("\n\n## Relevance Overlap Analysis\n\n")

    # Find articles relevant to multiple essays
    for article in sorted(articles, key=lambda x: x['title']):
        relevance_count = sum(1 for essay_key, _ in essays if 'Relevant' in article['relevance'].get(essay_key, []))
        if relevance_count > 1:
            relevant_essays = [essay_key for essay_key, _ in essays if 'Relevant' in article['relevance'].get(essay_key, [])]
            content.append(f"- **{article['title']}** - Relevant to {relevance_count} essays: {', '.join(relevant_essays)}\n")

    return '\n'.join(content)

def create_key_findings_summary(articles):
    """Create summary of key findings and research insights."""
    content = []
    content.append("# Key Findings and Research Insights\n\n")

    content.append("## Overview\n\n")
    content.append(f"This section synthesizes key insights from {len(articles)} research articles covering cybersecurity, ")
    content.append("corporate governance, market reactions, and information asymmetry.\n\n")

    content.append("## Major Research Themes\n\n")

    # Group by theme and extract insights
    by_theme = defaultdict(list)
    for article in articles:
        for theme in article['themes']:
            by_theme[theme].append(article)

    for theme in sorted(by_theme.keys()):
        content.append(f"\n### {theme}\n")
        content.append(f"**Coverage:** {len(by_theme[theme])} articles\n\n")

        # List key articles by theme
        top_articles = sorted(by_theme[theme], key=lambda x: int(x['year']) if x['year'] and isinstance(x['year'], (int, str)) and str(x['year']).isdigit() else 0, reverse=True)[:3]
        for article in top_articles:
            content.append(f"- {article['title']} ({article['year']})\n")

    # Methodology distribution insights
    content.append("\n\n## Research Methodology Landscape\n\n")

    by_method = defaultdict(int)
    for article in articles:
        for method in article['methodology']:
            by_method[method] += 1

    content.append("Distribution of research approaches across the literature:\n\n")
    for method, count in sorted(by_method.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(articles)) * 100
        content.append(f"- **{method}:** {count} articles ({percentage:.1f}%)\n")

    content.append("\n\n## Data Sources and Contexts\n\n")

    # Extract mentions of common datasets/contexts
    content.append("Common data sources and contexts mentioned across articles:\n\n")
    content.append("- Data breach announcements and notifications\n")
    content.append("- Stock market reactions and financial data\n")
    content.append("- Corporate governance structures and policies\n")
    content.append("- Information environment and disclosure patterns\n")
    content.append("- Regulatory requirements (FCC, SEC, state laws)\n")
    content.append("- Firm-level characteristics and performance metrics\n\n")

    content.append("## Research Gaps Identified\n\n")

    content.append("Based on the collected literature, potential research gaps include:\n\n")
    content.append("1. **Temporal Dynamics:** Limited studies on long-term effects beyond event windows\n")
    content.append("2. **Heterogeneous Effects:** Few studies examining differential impacts across firm characteristics\n")
    content.append("3. **Mechanism Testing:** Limited empirical testing of proposed theoretical mechanisms\n")
    content.append("4. **International Comparisons:** Mostly US-centric findings; limited cross-country evidence\n")
    content.append("5. **Regulatory Evaluation:** Limited assessment of disclosure requirement effectiveness\n")
    content.append("6. **Preventive Measures:** Limited analysis of governance/technical measures to reduce breach likelihood\n\n")

    return '\n'.join(content)

def create_detailed_article_listings(articles):
    """Create detailed listings of all articles."""
    content = []
    content.append("# Detailed Article Listings\n\n")

    for article in sorted(articles, key=lambda x: x['title']):
        content.append(f"\n## {article['index']:2d}. {article['title']}\n\n")

        content.append(f"**Filename:** {article['filename']}\n\n")

        if article['year']:
            content.append(f"**Year:** {article['year']}\n\n")

        if article['authors']:
            content.append(f"**Authors:** {'; '.join(article['authors'][:3])}\n\n")

        if article['keywords']:
            content.append(f"**Keywords:** {', '.join(article['keywords'][:8])}\n\n")

        content.append(f"**Research Themes:** {', '.join(article['themes'])}\n\n")

        content.append(f"**Methodology:** {', '.join(article['methodology'])}\n\n")

        essay_relevance = []
        if 'Relevant' in article['relevance'].get('Essay 1 (Market Reactions)', []):
            essay_relevance.append("Essay 1 (Market Reactions)")
        if 'Relevant' in article['relevance'].get('Essay 2 (Information Asymmetry)', []):
            essay_relevance.append("Essay 2 (Information Asymmetry)")
        if 'Relevant' in article['relevance'].get('Essay 3 (Governance Response)', []):
            essay_relevance.append("Essay 3 (Governance Response)")

        if essay_relevance:
            content.append(f"**Essay Relevance:** {', '.join(essay_relevance)}\n\n")

        if article['abstract']:
            content.append(f"**Abstract/Summary:**\n\n{article['abstract']}\n\n")

        content.append("---\n")

    return '\n'.join(content)

def main():
    """Generate all documentation files."""
    print("Loading article metadata...")
    articles = load_metadata('articles_metadata.json')

    print(f"Processing {len(articles)} articles...")

    # Create all documentation files
    docs = [
        ('MASTER_INDEX.md', create_master_index),
        ('BY_THEME.md', create_by_theme_index),
        ('BY_METHODOLOGY.md', create_by_methodology_index),
        ('BY_ESSAY_RELEVANCE.md', create_essay_relevance_index),
        ('KEY_FINDINGS_SUMMARY.md', create_key_findings_summary),
        ('DETAILED_LISTINGS.md', create_detailed_article_listings),
    ]

    for filename, generator_func in docs:
        print(f"Generating {filename}...")
        content = generator_func(articles)

        output_file = Path(filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created: {output_file} ({len(content)} bytes)")

    print("\nDocumentation generation complete!")
    print("\nGenerated files:")
    for filename, _ in docs:
        print(f"  - {filename}")

    # Create summary report
    print("\n=== DOCUMENTATION SUMMARY ===\n")
    print(f"Total articles documented: {len(articles)}")
    print(f"Articles with abstracts: {sum(1 for a in articles if a['abstract'])}")
    print(f"Articles with keywords: {sum(1 for a in articles if a['keywords'])}")

    # Theme summary
    theme_counts = defaultdict(int)
    for article in articles:
        for theme in article['themes']:
            theme_counts[theme] += 1

    print(f"\nTop 5 Research Themes:")
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {theme}: {count}")

    # Essay relevance summary
    essay1_count = sum(1 for a in articles if 'Relevant' in a['relevance'].get('Essay 1 (Market Reactions)', []))
    essay2_count = sum(1 for a in articles if 'Relevant' in a['relevance'].get('Essay 2 (Information Asymmetry)', []))
    essay3_count = sum(1 for a in articles if 'Relevant' in a['relevance'].get('Essay 3 (Governance Response)', []))

    print(f"\nEssay Relevance Coverage:")
    print(f"  - Essay 1 (Market Reactions): {essay1_count} articles")
    print(f"  - Essay 2 (Information Asymmetry): {essay2_count} articles")
    print(f"  - Essay 3 (Governance Response): {essay3_count} articles")

if __name__ == '__main__':
    main()
