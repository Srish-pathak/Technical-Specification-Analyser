"""
Front matter builder: Top Page, Cover Page (Grey), Approval Page, Acknowledgements, Table of Contents, Abstract.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_style_helpers import (
    FONT_NAME, set_run_font, add_placeholder_run, add_body_p
)

def build_front_matter(doc):
    # -------------------------------------------------------------
    # 1. TOP PAGE
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("TECHSPECANALYSER: AN INTEGRATED DUAL-ENGINE STATIC ANALYSIS AND GENERATIVE AI PLATFORM FOR AUTOMATED SOURCE CODE AUDITING, REPOSITORY HEALTH ASSESSMENT, AND SOFTWARE SPECIFICATION VERIFICATION")
    set_run_font(r, name=FONT_NAME, size_pt=16, bold=True)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("A Project Report Submitted in Partial Fulfillment of the Requirements\nfor the Award of the Degree of")
    set_run_font(r, name=FONT_NAME, size_pt=12, italic=True)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("BACHELOR OF TECHNOLOGY\nin\n")
    set_run_font(r, name=FONT_NAME, size_pt=13, bold=True)
    add_placeholder_run(p, "<DEPARTMENT_NAME>", size_pt=13, bold=True)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Submitted by:\n")
    set_run_font(r, name=FONT_NAME, size_pt=12, bold=True)
    add_placeholder_run(p, "<STUDENT_NAME>", size_pt=12, bold=True)
    r2 = p.add_run("\n(Roll / Enrolment No.: ")
    set_run_font(r2, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p, "<ENROLMENT_NUMBER>", size_pt=12, bold=True)
    r3 = p.add_run(")")
    set_run_font(r3, name=FONT_NAME, size_pt=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Under the Guidance of:\n")
    set_run_font(r, name=FONT_NAME, size_pt=12, bold=True)
    add_placeholder_run(p, "<SUPERVISOR_NAME>", size_pt=12, bold=True)
    r2 = p.add_run("\nDesignation: Associate Professor / Assistant Professor")
    set_run_font(r2, name=FONT_NAME, size_pt=11, italic=True)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(48)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("DEPARTMENT OF ")
    set_run_font(r, name=FONT_NAME, size_pt=12, bold=True)
    add_placeholder_run(p, "<DEPARTMENT_NAME>", size_pt=12, bold=True)
    p.add_run("\n")
    add_placeholder_run(p, "<INSTITUTE_NAME>", size_pt=13, bold=True)
    p.add_run("\n")
    add_placeholder_run(p, "<DATE>", size_pt=11, bold=True)
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 2. COVER PAGE (UG PROJECT = GREY BACKGROUND, BLACK LETTERS)
    # -------------------------------------------------------------
    tbl_cover = doc.add_table(rows=1, cols=1)
    tbl_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_cover = tbl_cover.rows[0].cells[0]
    cell_cover.width = Inches(5.97)
    
    # Grey background shading (#D9D9D9)
    tcPr = cell_cover._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9D9D9"/>')
    tcPr.append(shd)
    
    # Padding
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="720" w:type="dxa"/><w:bottom w:w="720" w:type="dxa"/><w:left w:w="432" w:type="dxa"/><w:right w:w="432" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)
    
    p = cell_cover.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("TECHSPECANALYSER: AN INTEGRATED DUAL-ENGINE STATIC ANALYSIS AND GENERATIVE AI PLATFORM FOR AUTOMATED SOURCE CODE AUDITING, REPOSITORY HEALTH ASSESSMENT, AND SOFTWARE SPECIFICATION VERIFICATION")
    set_run_font(r, name=FONT_NAME, size_pt=16, bold=True, color_rgb=RGBColor(0, 0, 0))
    
    p = cell_cover.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("UNDERGRADUATE MAJOR PROJECT REPORT")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True, color_rgb=RGBColor(0, 0, 0))
    
    p = cell_cover.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Submitted in partial fulfillment of the requirements for the award of the degree of")
    set_run_font(r, name=FONT_NAME, size_pt=12, italic=True, color_rgb=RGBColor(0, 0, 0))
    
    p = cell_cover.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(36)
    r = p.add_run("BACHELOR OF TECHNOLOGY\nin\n")
    set_run_font(r, name=FONT_NAME, size_pt=13, bold=True, color_rgb=RGBColor(0, 0, 0))
    add_placeholder_run(p, "<DEPARTMENT_NAME>", size_pt=13, bold=True)
    
    p = cell_cover.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("By\n")
    set_run_font(r, name=FONT_NAME, size_pt=12, bold=True, color_rgb=RGBColor(0, 0, 0))
    add_placeholder_run(p, "<STUDENT_NAME>", size_pt=12, bold=True)
    r = p.add_run(" (")
    set_run_font(r, name=FONT_NAME, size_pt=12, color_rgb=RGBColor(0, 0, 0))
    add_placeholder_run(p, "<ENROLMENT_NUMBER>", size_pt=12, bold=True)
    r = p.add_run(")")
    set_run_font(r, name=FONT_NAME, size_pt=12, color_rgb=RGBColor(0, 0, 0))
    
    p = cell_cover.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(48)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("DEPARTMENT OF ")
    set_run_font(r, name=FONT_NAME, size_pt=12, bold=True, color_rgb=RGBColor(0, 0, 0))
    add_placeholder_run(p, "<DEPARTMENT_NAME>", size_pt=12, bold=True)
    p.add_run("\n")
    add_placeholder_run(p, "<INSTITUTE_NAME>", size_pt=13, bold=True)
    p.add_run("\n")
    add_placeholder_run(p, "<DATE>", size_pt=11, bold=True)
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 3. APPROVAL PAGE
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("CERTIFICATE OF APPROVAL")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    add_body_p(
        doc,
        "This is to certify that the project entitled \"TECHSPECANALYSER: AN INTEGRATED DUAL-ENGINE STATIC ANALYSIS AND GENERATIVE AI PLATFORM FOR AUTOMATED SOURCE CODE AUDITING, REPOSITORY HEALTH ASSESSMENT, AND SOFTWARE SPECIFICATION VERIFICATION\", submitted by "
    )
    p_cert = doc.paragraphs[-1]
    add_placeholder_run(p_cert, "<STUDENT_NAME>")
    r = p_cert.add_run(" (Enrolment Number: ")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p_cert, "<ENROLMENT_NUMBER>")
    r2 = p_cert.add_run("), in partial fulfillment of the requirements for the award of the Degree of Bachelor of Technology in ")
    set_run_font(r2, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p_cert, "<DEPARTMENT_NAME>")
    r3 = p_cert.add_run(" at ")
    set_run_font(r3, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p_cert, "<INSTITUTE_NAME>")
    r4 = p_cert.add_run(", is a bonafide record of the research and development work carried out by them under our supervision and guidance.")
    set_run_font(r4, name=FONT_NAME, size_pt=12)
    
    add_body_p(
        doc,
        "The results and findings embodied in this project report have not been submitted, in part or in full, to any other University or Institute for the award of any degree or diploma. The software system, automated verification pipelines, and empirical evaluations described herein represent original engineering and research work conducted in accordance with institutional academic integrity standards."
    )
    
    # Approval signatures table
    tbl_appr = doc.add_table(rows=2, cols=2)
    tbl_appr.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1, c2 = tbl_appr.rows[0].cells
    c1.width = Inches(3.0)
    c2.width = Inches(2.97)
    
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.paragraph_format.space_before = Pt(48)
    p1.paragraph_format.space_after = Pt(4)
    r = p1.add_run("_______________________________\nSupervisor:\n")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p1, "<SUPERVISOR_NAME>", size_pt=12, bold=True)
    r = p1.add_run("\nDepartment of ")
    set_run_font(r, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p1, "<DEPARTMENT_NAME>", size_pt=11)
    r = p1.add_run("\n")
    set_run_font(r, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p1, "<INSTITUTE_NAME>", size_pt=11)
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.paragraph_format.space_before = Pt(48)
    p2.paragraph_format.space_after = Pt(4)
    r = p2.add_run("_______________________________\nHead of Department (HOD):\n")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p2, "<HOD_NAME>", size_pt=12, bold=True)
    r = p2.add_run("\nDepartment of ")
    set_run_font(r, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p2, "<DEPARTMENT_NAME>", size_pt=11)
    r = p2.add_run("\n")
    set_run_font(r, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p2, "<INSTITUTE_NAME>", size_pt=11)
    
    # Remove borders from approval table
    tblPr = tbl_appr._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)
    
    p_date = doc.add_paragraph()
    p_date.paragraph_format.space_before = Pt(36)
    p_date.paragraph_format.space_after = Pt(12)
    r = p_date.add_run("Place: ")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p_date, "<INSTITUTE_NAME>")
    r = p_date.add_run("\nDate: ")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p_date, "<DATE>")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 4. ACKNOWLEDGEMENTS
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("ACKNOWLEDGEMENTS")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    p = add_body_p(doc, "I express my deepest gratitude and sincere appreciation to my project supervisor, ")
    add_placeholder_run(p, "<SUPERVISOR_NAME>")
    r = p.add_run(", for their invaluable guidance, constructive critique, and continuous technical encouragement throughout the course of this B.Tech major project. Their profound insights into software metrics, static program analysis, and academic research methodology were fundamental in steering the development of TechSpecAnalyser from an initial design concept into an empirically validated, production-ready platform.")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    
    p = add_body_p(doc, "I also extend my heartfelt thanks to ")
    add_placeholder_run(p, "<HOD_NAME>")
    r = p.add_run(", Head of the Department of ")
    set_run_font(r, name=FONT_NAME, size_pt=12)
    add_placeholder_run(p, "<DEPARTMENT_NAME>")
    r2 = p.add_run(", for providing exemplary departmental infrastructure, computational laboratories, and administrative support that facilitated uninterrupted experimentation, server deployment, and rigorous testing.")
    set_run_font(r2, name=FONT_NAME, size_pt=12)
    
    add_body_p(
        doc,
        "I am grateful to all faculty members of the Department for their thoughtful recommendations during interim project reviews and technical seminars. Their critical evaluations helped refine our scoring normalisation formulas, static analysis boundaries, and automated test strategies. Special thanks are also due to the technical and laboratory staff for maintaining the cloud computing facilities and server clusters necessary for containerized test runs."
    )
    
    add_body_p(
        doc,
        "Finally, I would like to express my profound debt of gratitude to my family and peers for their unceasing patience, moral support, and enthusiasm during the demanding development cycles of this project. Their faith has been my greatest source of inspiration and perseverance."
    )
    
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_before = Pt(36)
    p_sig.paragraph_format.space_after = Pt(6)
    add_placeholder_run(p_sig, "<STUDENT_NAME>", size_pt=12, bold=True)
    r = p_sig.add_run("\nRoll / Enrolment No.: ")
    set_run_font(r, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p_sig, "<ENROLMENT_NUMBER>", size_pt=11, bold=True)
    r2 = p_sig.add_run("\nDepartment of ")
    set_run_font(r2, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p_sig, "<DEPARTMENT_NAME>", size_pt=11)
    r3 = p_sig.add_run("\n")
    set_run_font(r3, name=FONT_NAME, size_pt=11)
    add_placeholder_run(p_sig, "<INSTITUTE_NAME>", size_pt=11)
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 5. TABLE OF CONTENTS
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("TABLE OF CONTENTS")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    # Table of contents listing
    toc_items = [
        ("Approval Page", "iii"),
        ("Acknowledgements", "iv"),
        ("Table of Contents", "v"),
        ("Abstract", "vii"),
        ("CHAPTER 1: INTRODUCTION", "1"),
        ("    1.1 Background of the Study", "1"),
        ("    1.2 Motivation", "2"),
        ("    1.3 Problem Statement", "3"),
        ("    1.4 Scope and Limitations", "3"),
        ("    1.5 Objectives", "4"),
        ("CHAPTER 2: REVIEW OF LITERATURE", "5"),
        ("    2.1 Evolution of Static Program Analysis", "5"),
        ("    2.2 Mining Software Repositories and Repository Health", "6"),
        ("    2.3 Natural Language Processing and LLMs in Software Engineering", "6"),
        ("    2.4 Requirements Engineering and Specification Traceability", "7"),
        ("    2.5 Synthesis and Research Gap", "8"),
        ("CHAPTER 3: THEORETICAL CONSIDERATION", "9"),
        ("    3.1 Mathematical Foundations of Software Metrics", "9"),
        ("        3.1.1 Cyclomatic complexity", "9"),
        ("        3.1.2 Maintainability index formulation", "10"),
        ("    3.2 Scoring Methodologies and Normalisation", "10"),
        ("        3.2.1 Code quality scoring model", "10"),
        ("        3.2.2 Repository health scoring algorithm", "11"),
        ("        3.2.3 Technical specification quality scoring framework", "11"),
        ("    3.3 Grounded Dual-Engine Paradigm", "12"),
        ("CHAPTER 4: MATERIALS AND METHOD", "14"),
        ("    4.1 Overall System Architecture", "14"),
        ("    4.2 Technology Stack and Environment Specifications", "15"),
        ("    4.3 Module Design and Implementation", "16"),
        ("        4.3.1 Source code analysis engine", "16"),
        ("        4.3.2 GitHub repository review engine", "17"),
        ("        4.3.3 PDF technical specification analysis engine", "17"),
        ("        4.3.4 Historical audit trail and reporting service", "18"),
        ("        4.3.5 Dashboard and visual analytics portal", "19"),
        ("    4.4 Application Programming Interfaces and Routing", "19"),
        ("    4.5 Deployment Architecture and Continuous Delivery", "20"),
        ("CHAPTER 5: RESULTS AND DISCUSSION", "21"),
        ("    5.1 Automated Test Suite Verification and Code Quality", "21"),
        ("    5.2 User Interface and Functional Walkthrough", "22"),
        ("    5.3 Deployment Incidents, Root Cause Analysis, and Remediation", "27"),
        ("        5.3.1 Blank screen incident during frontend modernization", "27"),
        ("        5.3.2 PDF analysis prototype limitation on live deployment", "28"),
        ("    5.4 Performance Latency and Computational Overhead", "29"),
        ("    5.5 Comparative Evaluation Against State-of-the-Art Tools", "30"),
        ("CHAPTER 6: SUMMARY AND CONCLUSIONS", "30"),
        ("    6.1 Summary of Work Done", "30"),
        ("    6.2 Key Conclusions", "31"),
        ("    6.3 Future Work and Research Directions", "32"),
        ("REFERENCES", "34"),
        ("APPENDIX A: COMPLETE REST API SPECIFICATION", "36"),
        ("APPENDIX B: DATABASE SCHEMAS AND PYDANTIC DATA MODELS", "38"),
        ("APPENDIX C: AUTOMATED TEST SUITE CATALOG AND TRACE LOG", "40"),
    ]
    
    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc.autofit = False
    
    for idx, (title, pg) in enumerate(toc_items):
        c_title, c_pg = tbl_toc.rows[idx].cells
        c_title.width = Inches(5.1)
        c_pg.width = Inches(0.87)
        
        p_t = c_title.paragraphs[0]
        p_t.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_t.paragraph_format.space_before = Pt(2)
        p_t.paragraph_format.space_after = Pt(2)
        p_t.paragraph_format.line_spacing = 1.15
        is_major = title.startswith("CHAPTER") or title in ("REFERENCES", "APPENDIX A: COMPLETE REST API SPECIFICATION", "APPENDIX B: DATABASE SCHEMAS AND PYDANTIC DATA MODELS", "APPENDIX C: AUTOMATED TEST SUITE CATALOG AND TRACE LOG", "Abstract", "Table of Contents")
        r_t = p_t.add_run(title)
        set_run_font(r_t, name=FONT_NAME, size_pt=11, bold=is_major)
        
        p_p = c_pg.paragraphs[0]
        p_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_before = Pt(2)
        p_p.paragraph_format.space_after = Pt(2)
        p_p.paragraph_format.line_spacing = 1.15
        r_p = p_p.add_run(pg)
        set_run_font(r_p, name=FONT_NAME, size_pt=11, bold=is_major)
    
    # Remove borders from TOC table
    tblPr = tbl_toc._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 6. ABSTRACT (MAX 1 PAGE, 1.2 LINE SPACING, 5-6 KEYWORDS)
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("ABSTRACT")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    # Guidelines specify 1.2 line spacing for abstract
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(0)
    p_abs.paragraph_format.space_after = Pt(8)
    p_abs.paragraph_format.line_spacing = 1.2
    r_abs = p_abs.add_run(
        "Modern software engineering workflows grapple with an acute tension between rapid source code iteration and the rigorous preservation of architectural integrity, security posture, and documentation fidelity. While traditional static program analysis tools enforce deterministic syntactic rules and compute cyclomatic complexity, they lack semantic awareness of high-level project intent and natural language requirements. Conversely, emergent Large Language Models (LLMs) demonstrate remarkable semantic reasoning but suffer from hallucinations, non-deterministic scoring, and an inability to ground recommendations in formal software science. This project presents TechSpecAnalyser, an integrated, production-grade dual-engine platform designed to bridge this divide by unifying deterministic static program analysis with grounded generative artificial intelligence. TechSpecAnalyser orchestrates a multi-tier pipeline encompassing multi-file source code inspection across Python and JavaScript, remote GitHub repository hygiene assessment, and document-specific Software Requirements Specification (SRS) verification. Static code analysis integrates Python Abstract Syntax Tree (AST) visitation, Radon, Bandit, Ruff, and ESLint to deterministically quantify cyclomatic complexity (CC), maintainability indices (MI), and security vulnerabilities. To evaluate specifications, a multi-stage PDF ingestion engine couples PyMuPDF, pdfplumber, and pypdf to extract section hierarchies with page-level traceability, followed by structured, JSON-governed Gemini LLM reasoning (gemini-2.5-flash and gemini-1.5-flash) to identify requirement ambiguities, security vulnerabilities, and architectural gaps. Mathematically bounded and calibrated scoring formulations are introduced for Code Quality Score (3.0-9.8), Repository Health Score (10-100), and PDF Specification Quality Score (25-98). The user interface is delivered via a responsive, single-page application built on pure ECMAScript 2022 with a custom futuristic Galactic Portal visual identity, operating without external client-side frameworks. Rigorous automated verification across 93 test cases demonstrates a 100% pass rate with zero regressions. In addition, this report provides a transparent post-mortem analysis of production deployment incidents on Render—specifically resolving a frontend blank-screen incident caused by stray merge markup and browser cache staleness, and rectifying a prototype-notice limitation on live deployment. TechSpecAnalyser establishes that coupling rule-based static bounds with generative semantic critique provides software engineering teams with an automated, explainable, and highly trustworthy audit ecosystem."
    )
    set_run_font(r_abs, name=FONT_NAME, size_pt=12)
    
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(12)
    p_kw.paragraph_format.line_spacing = 1.2
    r_kw_lbl = p_kw.add_run("Keywords: ")
    set_run_font(r_kw_lbl, name=FONT_NAME, size_pt=12, bold=True)
    r_kw = p_kw.add_run("Static Code Analysis, Software Requirements Specification (SRS), Large Language Models, Cyclomatic Complexity, Repository Health Scoring, Automated Verification.")
    set_run_font(r_kw, name=FONT_NAME, size_pt=12, italic=True)
    
    doc.add_page_break()

print("report_sections_frontmatter loaded.")
