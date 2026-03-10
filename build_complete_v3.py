#!/usr/bin/env python3
"""
Build complete summaries - version 3
Improved extraction with better heuristics and fallbacks
"""

import os
import re
from pathlib import Path

ARTICLES_DIR = r"C:\Users\mcobp\DISSERTATION_CLONE\Data\Articles"
SUMMARY_FILE = r"C:\Users\mcobp\DISSERTATION_CLONE\COMPREHENSIVE_ARTICLE_SUMMARIES.txt"
OUTPUT_FILE = r"C:\Users\mcobp\DISSERTATION_CLONE\COMPREHENSIVE_ARTICLE_SUMMARIES_COMPLETE.txt"

def smart_extract(text, section_name):
    """Extract sections with improved heuristics."""

    text = text if text else ""

    # RESEARCH OBJECTIVE / PURPOSE
    if 'objective' in section_name.lower() or 'purpose' in section_name.lower():
        # Look for executive summary or introduction
        patterns = [
            r'(?:EXECUTIVE\s+SUMMARY|Executive\s+Summary)(.*?)(?:\n\n[A-Z\d]|KEY\s+FINDINGS)',
            r'(?:INTRODUCTION|Introduction)(.*?)(?:\n\n(?:LITERATURE|BACKGROUND|METHODOLOGY|STUDY|RESEARCH)|METHODS)',
            r'(?:ABSTRACT|Abstract)(.*?)(?:\n\nINTRO|KEYWORDS|KEY)',
            r'This(?:\s+\w+){1,5}(?:study|research|paper|aims|examines|investigates|explores).*?\.(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(0) if 'study|research|paper' in pattern else match.group(1))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # THEORETICAL FRAMEWORK
    elif 'framework' in section_name.lower() or 'theory' in section_name.lower():
        patterns = [
            r'(?:THEORETICAL|CONCEPTUAL)\s+(?:FRAMEWORK|MODEL|APPROACH)(.*?)(?:\n\n[A-Z]{2}|METHOD)',
            r'(?:THEORETICAL|Theory|Framework)(.*?)(?:\n\n(?:HYPOTHESIS|DATA|METHODOLOGY))',
            r'(?:built|based|grounded)\s+(?:on|in|upon)\s+(?:theory|theories|framework|literature).*?\.(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1) if len(match.groups()) > 1 else match.group(0))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # BACKGROUND & LITERATURE REVIEW
    elif 'background' in section_name.lower() or 'literature' in section_name.lower():
        patterns = [
            r'(?:LITERATURE\s+REVIEW|Related\s+Work)(.*?)(?:\n\n(?:METHODOLOGY|METHOD|DATA|HYPOTHESIS))',
            r'(?:BACKGROUND|Background)(.*?)(?:\n\n(?:LITERATURE|METHODOLOGY|RESEARCH))',
            r'Prior\s+(?:research|studies|work).*?(?:\.|:)(.*?)(?:\n\n|\nOur|This)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1) if len(match.groups()) > 1 else match.group(0))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # DISCUSSION & INTERPRETATION
    elif 'discussion' in section_name.lower():
        patterns = [
            r'(?:DISCUSSION|Discussion)(.*?)(?:\n\n(?:CONCLUSION|LIMITATIONS|IMPLICATIONS|FUTURE))',
            r'(?:FINDINGS.*?DISCUSSION|RESULTS.*?INTERPRETATION)(.*?)(?:\n\n(?:CONCLUSION|LIMITATIONS))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # POLICY & PRACTICAL IMPLICATIONS
    elif 'implication' in section_name.lower() or 'practical' in section_name.lower():
        patterns = [
            r'(?:IMPLICATIONS|PRACTICAL|POLICY)(.*?)(?:\n\n(?:LIMITATIONS|FUTURE|CONCLUSION|REFERENCES))',
            r'(?:implication|imply|suggest|recommend).*?(?:for|that|is).*?\.(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1) if len(match.groups()) > 1 else match.group(0))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # LIMITATIONS
    elif 'limitation' in section_name.lower():
        patterns = [
            r'(?:LIMITATIONS|Limitations)(.*?)(?:\n\n(?:FUTURE|CONCLUSION|REFERENCES))',
            r'(?:limitation|constraint|weakness).*?\.(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1) if len(match.groups()) > 1 else match.group(0))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    # FUTURE RESEARCH
    elif 'future' in section_name.lower():
        patterns = [
            r'(?:FUTURE\s+(?:RESEARCH|WORK|DIRECTIONS|STUDIES))(.*?)(?:\n\n(?:CONCLUSION|REFERENCES))',
            r'(?:future|further).*?(?:research|study|work|investigation).*?\.(?:\s|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = re.sub(r'\s+', ' ', match.group(1) if len(match.groups()) > 1 else match.group(0))
                if len(content) > 60:
                    return content[:400].rstrip() + ("..." if len(content) > 400 else "")

    return None

def extract_from_article(filepath, filename):
    """Extract content from article."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except:
        return {}

    result = {}

    # Try each section type
    sections = {
        'RESEARCH OBJECTIVE / PURPOSE': smart_extract(text, 'objective'),
        'THEORETICAL FRAMEWORK': smart_extract(text, 'framework'),
        'BACKGROUND & LITERATURE REVIEW SUMMARY': smart_extract(text, 'background'),
        'DISCUSSION & INTERPRETATION': smart_extract(text, 'discussion'),
        'POLICY AND PRACTICAL IMPLICATIONS': smart_extract(text, 'implications'),
        'LIMITATIONS': smart_extract(text, 'limitations'),
        'FUTURE RESEARCH SUGGESTIONS': smart_extract(text, 'future'),
    }

    return {k: v for k, v in sections.items() if v}

def is_placeholder(text):
    """Check if text is placeholder."""
    if not text:
        return True
    text_str = str(text).strip()
    return (len(text_str) < 40 or
            'to be extracted' in text_str.lower() or
            text_str.startswith('[') or
            text_str.endswith(']') or
            'will be extracted' in text_str.lower())

def process_file():
    """Main processing."""

    print("Step 1: Extracting content from all article files...")
    article_files = sorted([f for f in os.listdir(ARTICLES_DIR) if f.endswith('.txt')])
    extractions = {}

    for i, filename in enumerate(article_files, 1):
        filepath = os.path.join(ARTICLES_DIR, filename)
        result = extract_from_article(filepath, filename)
        if result:
            extractions[filename] = result
            print(f"  [{i:2d}/{len(article_files)}] {filename}: {len(result)} sections")

    print(f"\nStep 2: Reading and updating summary file...")
    with open(SUMMARY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    print(f"  Read {len(lines)} lines from summary file")

    print(f"\nStep 3: Processing and replacing placeholder sections...")
    output_lines = []
    current_filename = None
    i = 0
    sections_updated = 0

    while i < len(lines):
        line = lines[i]

        # Track current filename
        if line.startswith('File:'):
            current_filename = line.replace('File:', '').strip()

        output_lines.append(line)

        # Check if this is a section header that might need updating
        section_found = False
        for section_name in ['RESEARCH OBJECTIVE / PURPOSE', 'THEORETICAL FRAMEWORK',
                            'BACKGROUND & LITERATURE REVIEW', 'DISCUSSION & INTERPRETATION',
                            'POLICY AND PRACTICAL IMPLICATIONS', 'LIMITATIONS',
                            'FUTURE RESEARCH SUGGESTIONS']:
            if section_name in line and current_filename in extractions:
                section_found = True
                # Look ahead to get the content
                j = i + 1
                section_content_lines = []

                # Collect content until next section or end
                while j < len(lines):
                    next_line = lines[j]
                    # Check if this is a new section
                    if (next_line.startswith(('RESEARCH', 'THEORETICAL', 'BACKGROUND',
                                             'METHODOLOGY', 'KEY FINDINGS', 'DISCUSSION',
                                             'POLICY', 'LIMITATIONS', 'FUTURE', 'RELEVANCE',
                                             'NOTABLE', '=')) and
                        j > i + 1):
                        break
                    section_content_lines.append(next_line)
                    j += 1

                # Check if content is placeholder
                content_text = ''.join(section_content_lines).strip()
                if is_placeholder(content_text) and section_name in extractions[current_filename]:
                    # Replace with extracted content
                    extracted = extractions[current_filename][section_name]
                    output_lines.append(extracted + '\n\n')
                    sections_updated += 1
                    # Skip the old content
                    i = j - 1
                break

        i += 1

    print(f"  Updated {sections_updated} placeholder sections")

    print(f"\nStep 4: Writing output file...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f"  Wrote to {OUTPUT_FILE}")
    print("\nComplete!")

if __name__ == '__main__':
    process_file()
