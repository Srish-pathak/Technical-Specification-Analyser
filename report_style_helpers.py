"""
Shared styling helpers and document builder utilities for the TechSpecAnalyser B.Tech Report.
Strictly conforms to Format_Dissertation_Int_BTech_and_MTech_2022.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

FONT_NAME = "Times New Roman"

def set_run_font(run, name=FONT_NAME, size_pt=12, bold=False, italic=False, color_rgb=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    # Ensure XML rFonts element is set for complex scripts/eastAsia
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{name}" w:hAnsi="{name}" w:cs="{name}"/>')
    rPr.append(rFonts)
    return run

def add_placeholder_run(p, placeholder_text, name=FONT_NAME, size_pt=12, bold=True):
    run = p.add_run(placeholder_text)
    set_run_font(run, name=name, size_pt=size_pt, bold=bold)
    rPr = run._r.get_or_add_rPr()
    highlight = parse_xml(f'<w:highlight {nsdecls("w")} w:val="yellow"/>')
    rPr.append(highlight)
    return run

def add_body_p(doc, text="", space_before=0, space_after=6, line_spacing=1.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        set_run_font(run, name=FONT_NAME, size_pt=12)
    return p

def add_chapter_title(doc, chapter_num, title_text):
    # Chapter Title: 14pt bold centered or left aligned
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(f"CHAPTER {chapter_num}\n{title_text.upper()}")
    set_run_font(run, name=FONT_NAME, size_pt=14, bold=True)
    return p

def add_heading_1(doc, text):
    # Title Case, Bold, left aligned, space before 12, space after 6
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run, name=FONT_NAME, size_pt=12, bold=True)
    return p

def add_heading_2(doc, text):
    # Sentence case, Bold, left aligned, space before 10, space after 4
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run, name=FONT_NAME, size_pt=12, bold=True)
    return p

def add_heading_3(doc, text):
    # Sub-sub-heading: Sentence case, Bold, left aligned, space before 8, space after 3
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run, name=FONT_NAME, size_pt=12, bold=True, italic=True)
    return p

def add_bullet_p(doc, bold_prefix, text, space_after=4):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        set_run_font(r1, name=FONT_NAME, size_pt=12, bold=True)
    r2 = p.add_run(text)
    set_run_font(r2, name=FONT_NAME, size_pt=12)
    return p

def add_equation(doc, math_str, eq_num_str):
    """
    Renders equation in a 2-column table with no borders:
    Left column (width 5.0 in): centered mathematical formulation.
    Right column (width 0.97 in): right-aligned (X.Y) citation.
    """
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    c1, c2 = tbl.rows[0].cells
    c1.width = Inches(5.0)
    c2.width = Inches(0.97)
    
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(4)
    p1.paragraph_format.space_after = Pt(4)
    p1.paragraph_format.line_spacing = 1.15
    r1 = p1.add_run(math_str)
    set_run_font(r1, name=FONT_NAME, size_pt=12, italic=True)
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.paragraph_format.space_before = Pt(4)
    p2.paragraph_format.space_after = Pt(4)
    p2.paragraph_format.line_spacing = 1.15
    r2 = p2.add_run(f"({eq_num_str})")
    set_run_font(r2, name=FONT_NAME, size_pt=12)
    
    # Remove borders from equation table
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    # Add spacing paragraph after equation
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_table_with_borders(doc, headers, data_rows, col_widths=None, table_title=None, table_num=None):
    """
    Table with full borders, header shaded light grey (#F2F2F2).
    Title above in Sentence case without period: 'Table X.Y Title text'
    """
    if table_title and table_num:
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_title.paragraph_format.space_before = Pt(10)
        p_title.paragraph_format.space_after = Pt(4)
        p_title.paragraph_format.line_spacing = 1.15
        r_num = p_title.add_run(f"Table {table_num} ")
        set_run_font(r_num, name=FONT_NAME, size_pt=11, bold=True)
        r_t = p_title.add_run(table_title)
        set_run_font(r_t, name=FONT_NAME, size_pt=11, italic=True)
    
    num_rows = len(data_rows) + 1
    num_cols = len(headers)
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Table borders: full horizontal and vertical borders
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    # Format header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        if col_widths and i < len(col_widths):
            hdr_cells[i].width = col_widths[i]
        # Shading
        tcPr = hdr_cells[i]._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E6E6E6"/>')
        tcPr.append(shd)
        
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        set_run_font(r, name=FONT_NAME, size_pt=10, bold=True)
    
    # Format data rows
    for r_idx, row_data in enumerate(data_rows):
        row_cells = tbl.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            if col_widths and c_idx < len(col_widths):
                row_cells[c_idx].width = col_widths[c_idx]
            p = row_cells[c_idx].paragraphs[0]
            # align first column left, numbers/others center/left
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(val))
            set_run_font(r, name=FONT_NAME, size_pt=10)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

def add_figure(doc, img_path, caption_text, fig_num=None, width=Inches(5.6)):
    """
    Centered figure image, followed by caption below in Sentence case ending with period:
    'Fig. X.Y Caption text.'
    """
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=width)
    
    if caption_text and fig_num:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.line_spacing = 1.15
        
        # Ensure caption ends with a period as per guidelines
        cap = caption_text.strip()
        if not cap.endswith('.'):
            cap += '.'
        
        r_num = p_cap.add_run(f"Fig. {fig_num} ")
        set_run_font(r_num, name=FONT_NAME, size_pt=10, bold=True)
        r_t = p_cap.add_run(cap)
        set_run_font(r_t, name=FONT_NAME, size_pt=10, italic=True)

print("report_style_helpers loaded.")
