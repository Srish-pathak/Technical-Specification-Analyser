"""
Main script to assemble the complete B.Tech Project Report: TechSpecAnalyser_BTech_Project_Report.docx.
Strictly adheres to Format_Dissertation_Int_BTech_and_MTech_2022 guidelines.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.enum.text import WD_ALIGN_PARAGRAPH

from report_style_helpers import FONT_NAME
from report_sections_frontmatter import build_front_matter
from report_sections_ch1_ch3 import build_chapters_1_to_3
from report_sections_ch4 import build_chapter_4
from report_sections_ch5_ch6 import build_chapters_5_and_6
from report_sections_ref_app import build_references_and_appendices

def generate_report():
    print("Beginning B.Tech Report document generation...")
    workspace_dir = os.path.abspath(os.path.dirname(__file__))
    report_images_dir = os.path.join(workspace_dir, "report_images")
    output_docx_path = os.path.join(workspace_dir, "TechSpecAnalyser_BTech_Project_Report.docx")
    
    doc = docx.Document()
    
    # -------------------------------------------------------------
    # SECTION 1: FRONT MATTER (ROMAN NUMERALS i, ii, iii, ...)
    # -------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.27)
    sec1.page_height = Inches(11.69)
    sec1.left_margin = Inches(1.3)
    sec1.right_margin = Inches(1.0)
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.header_distance = Inches(0.5)
    sec1.footer_distance = Inches(0.5)
    
    # Roman numeral page numbering
    sectPr1 = sec1._sectPr
    pgNumType1 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>')
    sectPr1.append(pgNumType1)
    
    footer1 = sec1.footer
    p_f1 = footer1.paragraphs[0]
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld1 = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
    p_f1._p.append(fld1)
    
    print("Building Front Matter (Top Page, Grey Cover Page, Approval, Acknowledgements, TOC, Abstract)...")
    build_front_matter(doc)
    
    # -------------------------------------------------------------
    # SECTION 2: MAIN BODY (ARABIC NUMERALS -1-, -2-, -3-, ...)
    # -------------------------------------------------------------
    sec2 = doc.add_section()
    sec2.page_width = Inches(8.27)
    sec2.page_height = Inches(11.69)
    sec2.left_margin = Inches(1.3)
    sec2.right_margin = Inches(1.0)
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.header_distance = Inches(0.5)
    sec2.footer_distance = Inches(0.5)
    
    # Decouple footer from section 1
    sec2.footer.is_linked_to_previous = False
    sectPr2 = sec2._sectPr
    pgNumType2 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sectPr2.append(pgNumType2)
    
    footer2 = sec2.footer
    p_f2 = footer2.paragraphs[0]
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_before = parse_xml(f'<w:r {nsdecls("w")}><w:t xml:space="preserve">- </w:t></w:r>')
    p_f2._p.append(run_before)
    fld2 = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
    p_f2._p.append(fld2)
    run_after = parse_xml(f'<w:r {nsdecls("w")}><w:t xml:space="preserve"> -</w:t></w:r>')
    p_f2._p.append(run_after)
    
    print("Building Chapters 1 to 3 (Introduction, Review of Literature, Theoretical Consideration)...")
    build_chapters_1_to_3(doc)
    
    print("Building Chapter 4 (Materials and Method with Architecture Diagram & Tables)...")
    build_chapter_4(doc, report_images_dir)
    
    print("Building Chapters 5 and 6 (Results & Discussion with Real Screenshots & Incidents, Summary & Conclusions)...")
    build_chapters_5_and_6(doc, report_images_dir)
    
    print("Building References and Appendices (Appendix A, B, C with 93 Tests)...")
    build_references_and_appendices(doc)
    
    print(f"Saving final Word document to {output_docx_path}...")
    doc.save(output_docx_path)
    file_size = os.path.getsize(output_docx_path)
    print(f"Document saved successfully! Size: {file_size / 1024:.2f} KB")

if __name__ == "__main__":
    generate_report()
