#!/usr/bin/env python3
"""
Diagnose table structure to find correct patterns
"""

from docx import Document

doc = Document('ESSAY2_FINAL_APPENDIX_UPDATED.docx')

print("=" * 70)
print("TABLE STRUCTURE DIAGNOSIS")
print("=" * 70)

for table_idx, table in enumerate(doc.tables):
    if len(table.rows) > 0:
        first_cell = table.rows[0].cells[0].text if table.rows[0].cells else ""
        print(f"\nTable {table_idx}: First cell text = '{first_cell[:60]}'")

        # Show first 3 rows of first column
        for row_idx in range(min(3, len(table.rows))):
            row_text = table.rows[row_idx].cells[0].text if table.rows[row_idx].cells else ""
            print(f"  Row {row_idx}: '{row_text[:60]}'")

        # Show structure (how many columns)
        if len(table.rows) > 0:
            num_cols = len(table.rows[0].cells)
            print(f"  Structure: {len(table.rows)} rows x {num_cols} columns")
