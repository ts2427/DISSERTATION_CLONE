"""
Update README.md with corrected H1 values
"""

readme_path = r'C:\Users\mcobp\DISSERTATION_CLONE\README.md'

# Read the file
with open(readme_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements (old → new)
replacements = [
    # H1 coefficient: 0.57% → 0.649%
    ('+0.57%', '+0.649%'),
    ('0.57%', '0.649%'),

    # H1 p-value: 0.539 → 0.443
    ('p=0.539', 'p=0.443'),
    ('(p=0.539', '(p=0.443'),
    ('(p = 0.539', '(p = 0.443'),

    # Also handle 0.373 if it appears
    ('p=0.373', 'p=0.443'),
]

# Apply replacements
updated_content = content
changes_made = 0

for old, new in replacements:
    if old in updated_content:
        count = updated_content.count(old)
        updated_content = updated_content.replace(old, new)
        changes_made += count
        print(f"Replaced: {old} to {new} ({count} instances)")

# Write back
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print()
print("=" * 80)
print(f"README.md updated: {changes_made} total changes")
print("=" * 80)
