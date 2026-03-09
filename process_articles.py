#!/usr/bin/env python3
"""
Process 74 research article PDFs and create comprehensive documentation.
Extracts metadata, summaries, and creates organized reference guide.
"""

import os
import sys
from pathlib import Path
import re
from collections import defaultdict

# Try multiple PDF processing approaches
try:
    import PyPDF2
    PDF_LIB = "PyPDF2"
except ImportError:
    try:
        import pdfplumber
        PDF_LIB = "pdfplumber"
    except ImportError:
        try:
            import pypdf
            PDF_LIB = "pypdf"
        except ImportError:
            PDF_LIB = None

def extract_pdf_text(pdf_path, max_pages=3):
    """Extract text from PDF file."""
    try:
        if PDF_LIB == "pdfplumber":
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages[:max_pages]:
                    text += page.extract_text() or ""
                return text
        elif PDF_LIB == "PyPDF2":
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages[:max_pages]:
                text += page.extract_text() or ""
            return text
        elif PDF_LIB == "pypdf":
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages[:max_pages]:
                text += page.extract_text() or ""
            return text
        else:
            return None
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def extract_title_from_filename(filename):
    """Extract title from PDF filename."""
    # Remove .pdf extension
    title = filename.replace('.pdf', '')
    return title

def analyze_text_for_metadata(text, filename):
    """Extract metadata from PDF text."""
    # Always include title even if text extraction fails
    metadata = {
        'title': extract_title_from_filename(filename),
        'authors': [],
        'year': None,
        'abstract': None,
        'keywords': [],
    }

    if not text:
        return metadata

    # Limit text for analysis
    text_sample = text[:3000]

    # Update with extracted data
    metadata.update({
        'authors': extract_authors(text_sample),
        'year': extract_year(text_sample),
        'abstract': extract_abstract(text_sample),
        'keywords': extract_keywords(text_sample),
    })

    return metadata

def extract_authors(text):
    """Try to extract author names from text."""
    # Look for common author patterns
    lines = text.split('\n')[:20]  # First 20 lines usually have authors
    authors = []

    for line in lines:
        # Skip lines that are likely titles or other content
        if len(line) > 100 or line.isupper():
            continue
        # Look for email-like patterns or capitalized names
        if '@' in line or (line and line[0].isupper()):
            authors.append(line.strip())

    return authors[:3] if authors else []  # Return first 3 author-like lines

def extract_year(text):
    """Extract publication year from text."""
    # Look for 4-digit years between 1990-2030
    years = re.findall(r'\b(19[89]\d|20\d{2})\b', text[:2000])
    if years:
        # Return the most recent year found (likely publication year)
        return max(years)
    return None

def extract_abstract(text):
    """Extract abstract from text."""
    # Look for abstract section
    abstract_match = re.search(r'(?:ABSTRACT|Abstract)(.*?)(?:INTRODUCTION|Introduction|1\.|KEYWORDS|Keywords)',
                               text, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        # Clean up and limit length
        abstract_text = ' '.join(abstract_text.split())[:500]
        return abstract_text
    return None

def extract_keywords(text):
    """Extract keywords from text."""
    # Look for keywords section
    keywords_match = re.search(r'(?:KEYWORDS|Keywords)[:=]?\s*(.*?)(?:\n\n|INTRODUCTION|Introduction)',
                               text, re.IGNORECASE | re.DOTALL)
    if keywords_match:
        keywords_text = keywords_match.group(1).strip()
        # Split by comma or semicolon
        keywords = [k.strip() for k in re.split(r'[,;]', keywords_text)]
        return keywords[:10]  # Return first 10 keywords
    return []

def categorize_article(title, text_sample='', keywords=None):
    """Categorize article by research theme."""
    keywords = keywords or []
    combined_text = (title + ' ' + text_sample).lower()

    themes = []

    # Define theme keywords
    theme_keywords = {
        'Cybersecurity Risk': ['cybersecurity', 'cyber attack', 'data breach', 'information security', 'security'],
        'Market Reactions': ['stock market', 'stock price', 'market reaction', 'returns', 'abnormal returns', 'event study'],
        'Information Asymmetry': ['information asymmetry', 'disclosure', 'transparency', 'information environment', 'informed trading'],
        'Governance': ['corporate governance', 'board', 'governance structure', 'firm governance', 'management'],
        'Financial Impact': ['cost', 'economic', 'financial impact', 'firm value', 'shareholder'],
        'Regulation/Policy': ['regulation', 'policy', 'legal', 'compliance', 'disclosure requirement', 'notification law', 'fcc'],
        'Crisis Management': ['crisis', 'crisis management', 'reputation', 'stakeholder'],
        'Machine Learning': ['machine learning', 'neural network', 'algorithm', 'classification', 'prediction'],
        'Behavioral': ['behavioral', 'behavior', 'human factor', 'employee', 'biases'],
        'Platforms/Digital': ['platform', 'digital', 'ecosystem'],
    }

    for theme, keywords_list in theme_keywords.items():
        if any(keyword in combined_text for keyword in keywords_list):
            themes.append(theme)

    return themes if themes else ['General']

def determine_methodology(title, text_sample=''):
    """Determine research methodology."""
    combined_text = (title + ' ' + text_sample).lower()

    methodologies = []

    if any(word in combined_text for word in ['event study', 'empirical', 'regression', 'analysis', 'quantitative']):
        methodologies.append('Empirical')
    if any(word in combined_text for word in ['review', 'survey', 'literature']):
        methodologies.append('Literature Review')
    if any(word in combined_text for word in ['case study', 'case']):
        methodologies.append('Case Study')
    if any(word in combined_text for word in ['theory', 'theoretical', 'framework']):
        methodologies.append('Theoretical')
    if any(word in combined_text for word in ['machine learning', 'neural', 'algorithm', 'model']):
        methodologies.append('Machine Learning')

    return methodologies if methodologies else ['Not Specified']

def determine_relevance_to_essays(title, text_sample='', keywords=None):
    """Determine relevance to each dissertation essay."""
    keywords = keywords or []
    combined_text = (title + ' ' + text_sample).lower()

    relevance = {
        'Essay 1 (Market Reactions)': [],
        'Essay 2 (Information Asymmetry)': [],
        'Essay 3 (Governance Response)': [],
    }

    # Essay 1: Market reactions to breaches
    essay1_keywords = ['stock', 'market', 'price', 'returns', 'event study', 'announcement', 'reaction']
    if any(kw in combined_text for kw in essay1_keywords):
        relevance['Essay 1 (Market Reactions)'].append('Relevant')

    # Essay 2: Information asymmetry and disclosure
    essay2_keywords = ['information asymmetry', 'disclosure', 'transparency', 'information environment', 'timing']
    if any(kw in combined_text for kw in essay2_keywords):
        relevance['Essay 2 (Information Asymmetry)'].append('Relevant')

    # Essay 3: Governance response
    essay3_keywords = ['governance', 'board', 'management', 'response', 'policy', 'regulation', 'compliance']
    if any(kw in combined_text for kw in essay3_keywords):
        relevance['Essay 3 (Governance Response)'].append('Relevant')

    return relevance

def main():
    """Main processing function."""
    # Try different path formats for cross-platform compatibility
    pdf_dir = Path('/c/Users/mcobp/DISSERTATION_CLONE/Data/articles')
    if not pdf_dir.exists():
        pdf_dir = Path('/home/user/DISSERTATION_CLONE/Data/articles')
    if not pdf_dir.exists():
        pdf_dir = Path('Data/articles')
    if not pdf_dir.exists():
        # Try Windows path
        import subprocess
        result = subprocess.run(['pwd'], capture_output=True, text=True)
        cwd = result.stdout.strip()
        pdf_dir = Path(cwd) / 'Data' / 'articles'

    if not pdf_dir.exists():
        print(f"Error: Directory not found. Checked:")
        print(f"  /c/Users/mcobp/DISSERTATION_CLONE/Data/articles")
        print(f"  /home/user/DISSERTATION_CLONE/Data/articles")
        print(f"  Data/articles")
        print(f"  {pdf_dir}")
        return

    pdf_files = sorted([f for f in pdf_dir.glob('*.pdf')])
    print(f"Found {len(pdf_files)} PDF files")
    print(f"PDF Library available: {PDF_LIB}\n")

    if not PDF_LIB:
        print("Warning: No PDF extraction library available. Using filename-based processing.\n")

    # Process articles
    articles = []

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"Processing [{i:2d}/{len(pdf_files)}] {pdf_file.name[:60]}")

        # Extract text from PDF
        text = extract_pdf_text(pdf_file) if PDF_LIB else ""

        # Analyze metadata
        metadata = analyze_text_for_metadata(text, pdf_file.name)

        # Categorize
        text_sample = text[:2000] if text else ""
        themes = categorize_article(pdf_file.name, text_sample, metadata.get('keywords', []))
        methodology = determine_methodology(pdf_file.name, text_sample)
        relevance = determine_relevance_to_essays(pdf_file.name, text_sample, metadata.get('keywords', []))

        article = {
            'index': i,
            'filename': pdf_file.name,
            'title': metadata['title'],
            'authors': metadata.get('authors', []),
            'year': metadata.get('year'),
            'abstract': metadata.get('abstract'),
            'keywords': metadata.get('keywords', []),
            'themes': themes,
            'methodology': methodology,
            'relevance': relevance,
            'file_size_mb': pdf_file.stat().st_size / (1024 * 1024),
        }

        articles.append(article)

    print(f"\nProcessed {len(articles)} articles successfully\n")

    # Save results to JSON for further processing
    import json
    output_file = Path('articles_metadata.json')
    with open(output_file, 'w') as f:
        # Convert to serializable format
        articles_serializable = []
        for article in articles:
            article_copy = article.copy()
            articles_serializable.append(article_copy)
        json.dump(articles_serializable, f, indent=2)

    print(f"Metadata saved to: {output_file}\n")

    # Create summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total articles: {len(articles)}")
    print(f"Articles with years: {sum(1 for a in articles if a['year'])}")
    print(f"Articles with abstracts: {sum(1 for a in articles if a['abstract'])}")
    print(f"Articles with keywords: {sum(1 for a in articles if a['keywords'])}")

    # Theme distribution
    theme_counts = defaultdict(int)
    for article in articles:
        for theme in article['themes']:
            theme_counts[theme] += 1

    print(f"\n=== RESEARCH THEMES ===")
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{theme}: {count}")

    # Methodology distribution
    method_counts = defaultdict(int)
    for article in articles:
        for method in article['methodology']:
            method_counts[method] += 1

    print(f"\n=== METHODOLOGIES ===")
    for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{method}: {count}")

    # Essay relevance
    essay1_relevant = sum(1 for a in articles if 'Relevant' in a['relevance']['Essay 1 (Market Reactions)'])
    essay2_relevant = sum(1 for a in articles if 'Relevant' in a['relevance']['Essay 2 (Information Asymmetry)'])
    essay3_relevant = sum(1 for a in articles if 'Relevant' in a['relevance']['Essay 3 (Governance Response)'])

    print(f"\n=== ESSAY RELEVANCE ===")
    print(f"Essay 1 (Market Reactions): {essay1_relevant} articles")
    print(f"Essay 2 (Information Asymmetry): {essay2_relevant} articles")
    print(f"Essay 3 (Governance Response): {essay3_relevant} articles")

if __name__ == '__main__':
    main()
