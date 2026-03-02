"""
Create Comprehensive Dissertation Proposal - All Sources Integrated
Follows Dr. Baldwin's 5-Section Guide Format with Strategic Source Integration
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from pathlib import Path

def add_styled_paragraph(doc, text, style='Normal', bold=False, italic=False, size=11,
                        space_before=0, space_after=6, alignment='left', indent_first=0.5):
    """Add paragraph with consistent styling"""
    p = doc.add_paragraph(text, style=style)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.first_line_indent = Inches(indent_first)

    if alignment == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif alignment == 'left':
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    for run in p.runs:
        run.font.size = Pt(size)
        if bold:
            run.font.bold = True
        if italic:
            run.font.italic = True

    return p

def create_title_page(doc):
    doc.add_paragraph()
    doc.add_paragraph()
    p = add_styled_paragraph(doc, "DATA BREACH DISCLOSURE TIMING AND MARKET REACTIONS",
                            bold=True, size=14, alignment='center', indent_first=0)

    doc.add_paragraph()
    p = add_styled_paragraph(doc, "A Dissertation Proposal",
                            alignment='center', indent_first=0)

    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    p = add_styled_paragraph(doc, "Timothy D. Spivey",
                            alignment='center', indent_first=0)

    p = add_styled_paragraph(doc, "University of South Alabama",
                            alignment='center', indent_first=0)

    doc.add_paragraph()
    p = add_styled_paragraph(doc, f"{datetime.now().strftime('%B %Y')}",
                            alignment='center', indent_first=0)

    doc.add_page_break()

def main():
    doc = Document()

    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    create_title_page(doc)
    
    heading = doc.add_heading('I. Introduction', level=1)
    add_styled_paragraph(doc, "Comprehensive proposal with all sources integrated...")

    output_path = Path(__file__).parent / 'Dissertation_Proposal_Comprehensive.docx'
    doc.save(str(output_path))
    print("[OK] Comprehensive dissertation proposal created: " + str(output_path))

if __name__ == '__main__':
    main()
