#!/usr/bin/env python
"""Debug SEC cik-lookup-data.txt format"""

with open('Data/edgar/cik-lookup-data.txt', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Remove trailing colon
        if line_stripped.endswith(':'):
            line_stripped = line_stripped[:-1]

        # Check format
        if ':' not in line_stripped:
            print(f"Line {i}: NO COLON: '{line_stripped[:80]}'")
            continue

        # Find last colon
        last_colon = line_stripped.rfind(':')
        name_part = line_stripped[:last_colon]
        cik_part = line_stripped[last_colon + 1:]

        if name_part and cik_part:
            print(f"Line {i}: name='{name_part[:50]:50s}' cik='{cik_part}'")

        if i >= 50:
            break
