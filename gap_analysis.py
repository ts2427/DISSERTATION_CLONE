import pdfplumber
import os
from collections import defaultdict

# Articles directory
ARTICLES_DIR = r"C:\Users\mcobp\DISSERTATION_CLONE\data\Articles"

# Essay focuses (from analysis)
ESSAY_FOCUS_TOPICS = {
    'Market Reaction': 44,
    'Information Asymmetry': 21,
    'Disclosure Timing': 19,
    'FCC Regulation': 13,
    'Breach Severity': 8,
    'Prior Breaches': 5,
    'Crisis Communication': 3,
    'Data Type': 2,
}

# Topics that are mentioned minimally in essay but might need coverage
UNDEREXPLORED_IN_ESSAY = [
    'Firm Heterogeneity',
    'Organizational Response',
    'Regulatory Compliance',
    'Reputational Damage',
    'Stakeholder Response',
    'Long-term Effects',
    'Heterogeneous Treatment Effects',
]

# Key theories referenced in essay
ESSAY_THEORIES = [
    'information asymmetry',
    'signaling theory',
    'adverse selection',
    'event study',
    'institutional theory',
    'crisis communication',
]

# Check what articles cover that might be missing from essay focus
POTENTIAL_GAPS = {
    'Heterogeneous Effects': [
        'heterogeneity', 'heterogeneous treatment effects', 'subsample analysis',
        'interaction effects', 'moderation'
    ],
    'Firm Characteristics': [
        'firm size', 'firm age', 'firm reputation', 'financial health',
        'prior performance', 'board composition', 'CEO characteristics'
    ],
    'Breach Characteristics': [
        'breach type', 'breach scope', 'breach detection', 'investigation time',
        'number of records', 'sensitive data'
    ],
    'Stakeholder Reactions': [
        'customer response', 'employee turnover', 'supplier reaction',
        'regulatory response', 'analyst coverage'
    ],
    'Long-term Effects': [
        'long-term abnormal returns', 'persistent effects', 'recovery trajectory',
        'multi-year analysis', 'post-event performance'
    ],
    'Disclosure Content': [
        'disclosure completeness', 'tone analysis', 'sentiment', 'vagueness',
        'information content', 'credibility'
    ],
    'Comparative Regulation': [
        'GDPR', 'state laws', 'SOX', 'regulatory differences',
        'international comparison', 'regulatory arbitrage'
    ],
    'Mechanism Analysis': [
        'information processing', 'cognitive load', 'time pressure',
        'investigation completion', 'uncertainty resolution'
    ],
}

def extract_pdf_content(pdf_path, max_chars=5000):
    """Extract limited text from PDF for analysis"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:2]:  # Only first 2 pages for quick scan
                text += page.extract_text() or ""
            return text[:max_chars]
    except:
        return ""

def analyze_article_coverage(articles_dir):
    """Analyze which topics from potential gaps are covered by articles"""

    gap_coverage = {gap: {'articles': [], 'count': 0} for gap in POTENTIAL_GAPS}

    pdf_files = sorted([f for f in os.listdir(articles_dir) if f.endswith('.pdf')])

    print("ANALYZING ARTICLE COVERAGE OF POTENTIAL GAPS...")
    print("=" * 80)

    for idx, filename in enumerate(pdf_files, 1):
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{len(pdf_files)}")

        filepath = os.path.join(articles_dir, filename)
        content = extract_pdf_content(filepath)
        content_lower = (content + filename).lower()

        for gap_area, keywords in POTENTIAL_GAPS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if filename not in gap_coverage[gap_area]['articles']:
                        gap_coverage[gap_area]['articles'].append(filename)
                    gap_coverage[gap_area]['count'] += 1
                    break

    return gap_coverage

# Run analysis
print("DISSERTATION ESSAY 1 - GAP ANALYSIS")
print("=" * 80)
print("\nESSAY FOCUS (topic frequency in essay):")
print("-" * 80)
for topic, freq in sorted(ESSAY_FOCUS_TOPICS.items(), key=lambda x: x[1], reverse=True):
    print(f"  {topic:<25} {freq:>3} mentions")

print("\n\nTOPICS MENTIONED MINIMALLY IN ESSAY:")
print("-" * 80)
for topic in UNDEREXPLORED_IN_ESSAY:
    print(f"  - {topic}")

print("\n\nANALYZING ARTICLE LIBRARY FOR COVERAGE OF POTENTIAL GAPS...")
print("-" * 80)

gap_coverage = analyze_article_coverage(ARTICLES_DIR)

print("\n\nGAP ANALYSIS RESULTS:")
print("=" * 80)

covered_gaps = []
uncovered_gaps = []

for gap_area, data in sorted(gap_coverage.items(), key=lambda x: len(x[1]['articles']), reverse=True):
    num_articles = len(data['articles'])
    if num_articles > 0:
        covered_gaps.append((gap_area, num_articles))
        print(f"\n[COVERED] {gap_area}")
        print(f"  Articles addressing this: {num_articles}")
        print(f"  Examples:")
        for article in data['articles'][:3]:
            print(f"    - {article[:70]}")
    else:
        uncovered_gaps.append(gap_area)

print("\n\n[POTENTIAL GAPS] Topics not well covered by articles:")
print("-" * 80)
for gap in uncovered_gaps:
    print(f"  - {gap}")

print("\n\nRECOMMENDATIONS:")
print("=" * 80)
print(f"""
1. MAJOR GAPS (Missing from both essay and articles):
   {len(uncovered_gaps)} topic areas have limited coverage

2. AREAS FOR ESSAY EXPANSION:
   - Firm Heterogeneity: Essay mentions only 1x, but critical for understanding variation
   - Organizational Response: Essay mentions only 1x, but important context
   - Reputational Damage: Consider adding more emphasis on non-market impacts

3. STRENGTHENING WITH ARTICLES:
   - Use articles on {covered_gaps[0][0]} to deepen analysis
   - Consider incorporating {covered_gaps[-1][0]} perspectives

4. CITATION GAPS:
   - Essay has 49 citations; expand with high-relevance articles not yet cited
   - Focus on articles covering: {', '.join([x[0] for x in covered_gaps[:3]])}
""")

print(f"\nAnalysis complete. {len(pdf_files)} articles analyzed.")
