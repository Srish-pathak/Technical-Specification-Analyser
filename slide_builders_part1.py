"""
Slide Builders Part 1: Slides 1 to 8
- Slide 1: Title Slide
- Slide 2: Agenda
- Slide 3: 01 · Problem Statement
- Slide 4: 02 · Background
- Slide 5: 03 · Product Review
- Slide 6: 04 · Research Gap / Opportunity
- Slide 7: 05 · Objectives
- Slide 8: 06 · Proposed Methodology (Flow)
"""

import os
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from build_presentation import (
    FONT_NAME, COLOR_BG, COLOR_CARD, COLOR_CARD_BORDER, COLOR_CARD_ALT,
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_BG, COLOR_WHITE, COLOR_TEXT_LIGHT,
    COLOR_MUTED, COLOR_GREEN, COLOR_RED, COLOR_CYAN,
    set_slide_background, add_header, add_card
)

def build_slide_1(prs, logo_path="cuj_logo.png"):
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    
    # Institution Header bar with Logo
    header_card = add_card(slide, Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.3),
                           bg_color=RGBColor(16, 24, 38), border_color=COLOR_CARD_BORDER)
    
    if os.path.exists(logo_path):
        slide.shapes.add_picture(logo_path, Inches(1.05), Inches(0.65), height=Inches(1.0))
    
    tb_inst = slide.shapes.add_textbox(Inches(2.2), Inches(0.65), Inches(7.0), Inches(1.0))
    tf_inst = tb_inst.text_frame
    tf_inst.word_wrap = True
    p1 = tf_inst.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "Central University of Jharkhand"
    r1.font.name = FONT_NAME
    r1.font.size = Pt(17)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_WHITE
    
    p2 = tf_inst.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Knowledge, Skills, Empowerment • Department of Computer Science & Engineering"
    r2.font.name = FONT_NAME
    r2.font.size = Pt(11)
    r2.font.color.rgb = COLOR_GOLD_LIGHT
    
    # Semester Tag
    tb_sem = slide.shapes.add_textbox(Inches(9.2), Inches(0.75), Inches(3.1), Inches(0.8))
    tf_sem = tb_sem.text_frame
    p_sem = tf_sem.paragraphs[0]
    p_sem.alignment = PP_ALIGN.RIGHT
    r_sem = p_sem.add_run()
    r_sem.text = "7th Semester Project  |  2026"
    r_sem.font.name = FONT_NAME
    r_sem.font.size = Pt(12)
    r_sem.font.bold = True
    r_sem.font.color.rgb = COLOR_GOLD
    
    # Main Title Container Card
    main_card = add_card(slide, Inches(0.8), Inches(2.0), Inches(11.733), Inches(2.5),
                         bg_color=COLOR_CARD, border_color=RGBColor(60, 80, 115))
    
    tb_main = slide.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(11.133), Inches(2.2))
    tf_main = tb_main.text_frame
    tf_main.word_wrap = True
    
    # Tag
    p_tag = tf_main.paragraphs[0]
    r_tag = p_tag.add_run()
    r_tag.text = "MAJOR PROJECT PRESENTATION"
    r_tag.font.name = FONT_NAME
    r_tag.font.size = Pt(11)
    r_tag.font.bold = True
    r_tag.font.color.rgb = COLOR_GOLD
    
    # Title
    p_t = tf_main.add_paragraph()
    r_t1 = p_t.add_run()
    r_t1.text = "TechSpecAnalyser "
    r_t1.font.name = FONT_NAME
    r_t1.font.size = Pt(28)
    r_t1.font.bold = True
    r_t1.font.color.rgb = COLOR_WHITE
    
    r_t2 = p_t.add_run()
    r_t2.text = "(CodeLens AI)"
    r_t2.font.name = FONT_NAME
    r_t2.font.size = Pt(24)
    r_t2.font.bold = True
    r_t2.font.color.rgb = COLOR_GOLD_LIGHT
    
    # Subtitle
    p_sub = tf_main.add_paragraph()
    p_sub.space_before = Pt(4)
    p_sub.space_after = Pt(8)
    r_sub = p_sub.add_run()
    r_sub.text = "A Static-Analysis-Grounded Multi-Agent System for Automated Code Review and Documentation Generation"
    r_sub.font.name = FONT_NAME
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Check badges
    badges = ["✔ Code Analysis", "✔ Security Check", "✔ Complexity", "✔ AI Review", "✔ Documentation"]
    p_bad = tf_main.add_paragraph()
    for idx, b in enumerate(badges):
        r_b = p_bad.add_run()
        r_b.text = f"  {b}  "
        r_b.font.name = FONT_NAME
        r_b.font.size = Pt(11)
        r_b.font.bold = True
        r_b.font.color.rgb = COLOR_GOLD_LIGHT
        if idx < len(badges) - 1:
            r_sep = p_bad.add_run()
            r_sep.text = "•"
            r_sep.font.color.rgb = COLOR_CARD_BORDER
    
    # 3 Bottom Meta Cards (Presented By, Faculty Guide, Institution)
    card_w = Inches(3.75)
    card_h = Inches(2.2)
    top_y = Inches(4.7)
    
    # 1. Presented By
    c1 = add_card(slide, Inches(0.8), top_y, card_w, card_h)
    tb1 = slide.shapes.add_textbox(Inches(0.95), top_y + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "🎓  PRESENTED BY"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    p = tf1.add_paragraph()
    p.space_before = Pt(4)
    r = p.add_run()
    r.text = "Srishti Pathak"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    
    p = tf1.add_paragraph()
    p.space_before = Pt(2)
    r = p.add_run()
    r.text = "Integrated B.Tech & M.Tech in CSE\n(AI & Data Science)\nRoll No.: 23190503052"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_MUTED
    
    # 2. Faculty Guide
    c2 = add_card(slide, Inches(4.791), top_y, card_w, card_h)
    tb2 = slide.shapes.add_textbox(Inches(4.941), top_y + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    r = p.add_run()
    r.text = "👨‍🏫  FACULTY GUIDE"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    p = tf2.add_paragraph()
    p.space_before = Pt(4)
    r = p.add_run()
    r.text = "Dr. Prashant Prashun"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    
    p = tf2.add_paragraph()
    p.space_before = Pt(2)
    r = p.add_run()
    r.text = "Assistant Professor\nDepartment of CSE\nCentral University of Jharkhand"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_MUTED
    
    # 3. Institution
    c3 = add_card(slide, Inches(8.783), top_y, card_w, card_h)
    tb3 = slide.shapes.add_textbox(Inches(8.933), top_y + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    r = p.add_run()
    r.text = "🏛️  INSTITUTION"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    p = tf3.add_paragraph()
    p.space_before = Pt(4)
    r = p.add_run()
    r.text = "CUJ, Ranchi"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    
    p = tf3.add_paragraph()
    p.space_before = Pt(2)
    r = p.add_run()
    r.text = "Central University of Jharkhand\nRanchi, Jharkhand, India\nSession: 2026"
    r.font.name = FONT_NAME
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_MUTED

def build_slide_2(prs):
    # -------------------------------------------------------------
    # SLIDE 2: AGENDA
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Agenda", "Presentation Roadmap", "Structured outline of project defense")
    
    items = [
        ("01", "Problem Statement", "Challenges in code review and documentation"),
        ("02", "Background", "Context, bottleneck, and need for grounding"),
        ("03", "Product Review", "Literature survey of existing review tools"),
        ("04", "Research Gap", "Identified limitations and our unique opportunity"),
        ("05", "Objectives", "Specific goals and evidence-based design"),
        ("06", "Proposed Methodology", "Hybrid deterministic + AI review pipeline"),
        ("07", "Technical Design", "System architecture, layers, stack & GitHub review"),
        ("08", "Feasibility", "Technical, financial and practical evaluation"),
        ("09", "Preliminary Progress", "Implemented features, dashboard & 34/34 tests"),
        ("10", "Expected Outcomes", "Target deliverables and project conclusion")
    ]
    
    card_w = Inches(5.6)
    card_h = Inches(0.85)
    start_x1 = Inches(0.8)
    start_x2 = Inches(6.8)
    start_y = Inches(1.8)
    gap_y = Inches(1.0)
    
    for i, (num, title, desc) in enumerate(items):
        col = i // 5
        row = i % 5
        x = start_x1 if col == 0 else start_x2
        y = start_y + (row * gap_y)
        
        c = add_card(slide, x, y, card_w, card_h)
        
        # Number badge
        nb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), y + Inches(0.15), Inches(0.65), Inches(0.55))
        nb.fill.solid()
        nb.fill.fore_color.rgb = COLOR_GOLD_BG
        nb.line.color.rgb = COLOR_GOLD
        p_n = nb.text_frame.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        r_n = p_n.add_run()
        r_n.text = num
        r_n.font.name = FONT_NAME
        r_n.font.size = Pt(13)
        r_n.font.bold = True
        r_n.font.color.rgb = COLOR_GOLD_LIGHT
        
        # Text
        tb = slide.shapes.add_textbox(x + Inches(0.9), y + Inches(0.08), card_w - Inches(1.0), card_h - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        r_t = p_t.add_run()
        r_t.text = title
        r_t.font.name = FONT_NAME
        r_t.font.size = Pt(13)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_WHITE
        
        p_d = tf.add_paragraph()
        r_d = p_d.add_run()
        r_d.text = desc
        r_d.font.name = FONT_NAME
        r_d.font.size = Pt(10)
        r_d.font.color.rgb = COLOR_MUTED

def build_slide_3(prs):
    # -------------------------------------------------------------
    # SLIDE 3: 01 · PROBLEM STATEMENT
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "01 · Problem Statement", "Problem Statement", "Why code review needs more than a quick visual inspection")
    
    cards = [
        ("⏱️", "Manual review takes time", "Developers must inspect syntax, logic, quality and maintainability across files. In fast-paced cycles, cognitive fatigue creates severe testing bottlenecks."),
        ("👁️", "Issues can be overlooked", "Subtle bugs, concurrency traps, anti-patterns, and edge cases frequently slip past human reviewers into staging and production branches."),
        ("💬", "Feedback is hard to act on", "A truly useful review must not merely point out flaws; it should clearly explain the root cause and provide practical, syntactically correct code remedies.")
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(3.4)
    start_x = Inches(0.8)
    gap_x = Inches(4.0)
    top_y = Inches(1.8)
    
    for i, (icon, heading, body) in enumerate(cards):
        x = start_x + (i * gap_x)
        c = add_card(slide, x, top_y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_i = tf.paragraphs[0]
        r_i = p_i.add_run()
        r_i.text = f"{icon}  {heading}"
        r_i.font.name = FONT_NAME
        r_i.font.size = Pt(14)
        r_i.font.bold = True
        r_i.font.color.rgb = COLOR_GOLD_LIGHT
        
        p_b = tf.add_paragraph()
        p_b.space_before = Pt(12)
        r_b = p_b.add_run()
        r_b.text = body
        r_b.font.name = FONT_NAME
        r_b.font.size = Pt(12)
        r_b.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Bottom callout banner
    banner = add_card(slide, Inches(0.8), Inches(5.5), Inches(11.733), Inches(1.3),
                      bg_color=RGBColor(28, 22, 12), border_color=COLOR_GOLD)
    tb_b = slide.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.333), Inches(1.1))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    
    p_b1 = tf_b.paragraphs[0]
    r_b1 = p_b1.add_run()
    r_b1.text = "🎯  Problem Addressed:"
    r_b1.font.name = FONT_NAME
    r_b1.font.size = Pt(12.5)
    r_b1.font.bold = True
    r_b1.font.color.rgb = COLOR_GOLD
    
    p_b2 = tf_b.add_paragraph()
    p_b2.space_before = Pt(3)
    r_b2 = p_b2.add_run()
    r_b2.text = "Code reviews and technical documentation are time-consuming, and consistent, actionable feedback is hard to obtain. Static findings and AI observations need one unified, structured, evidence-based workflow."
    r_b2.font.name = FONT_NAME
    r_b2.font.size = Pt(12)
    r_b2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_4(prs):
    # -------------------------------------------------------------
    # SLIDE 4: 02 · BACKGROUND
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "02 · Background", "Why This Problem Matters", "Background: the context behind automated code review")
    
    items = [
        ("⏱️", "Review is a bottleneck", "Developers spend a great deal of time reviewing peers' code (Li et al., 2022). Manual reviews slow down deployment velocity and create organizational drag."),
        ("🐛", "Defects reach production", "Missed bugs, risky patterns and high complexity make software harder to maintain and secure, leading to expensive downstream technical debt."),
        ("🤖", "AI needs grounding", "LLM reviews read fluently but can be incomplete, stochastic, or hallucinated, so findings strictly require verifiable, deterministic static evidence."),
        ("📄", "Explanations matter", "Students and junior engineers need clear educational explanations and documentation, not simply an opaque list of cryptic compiler warnings.")
    ]
    
    card_w = Inches(5.6)
    card_h = Inches(2.3)
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(6.8), Inches(1.8)),
        (Inches(0.8), Inches(4.5)),
        (Inches(6.8), Inches(4.5))
    ]
    
    for i, (icon, heading, text) in enumerate(items):
        x, y = coords[i]
        c = add_card(slide, x, y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {heading}"
        r.font.name = FONT_NAME
        r.font.size = Pt(14.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(8)
        r2 = p2.add_run()
        r2.text = text
        r2.font.name = FONT_NAME
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_5(prs):
    # -------------------------------------------------------------
    # SLIDE 5: 03 · PRODUCT REVIEW
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "03 · Product Review (Literature Survey)", "Product Review", "Existing products in automated code review")
    
    headers = ["Product", "Type", "What it offers", "Limitation for our use case"]
    rows = [
        ["SonarQube", "Rule-based analysis platform", "Quality and security analysis; AI CodeFix suggests LLM-generated fixes", "Needs platform setup; AI CodeFix is in higher-tier enterprise editions"],
        ["CodeRabbit", "AI pull-request reviewer", "Runs linters plus an LLM; inline comments and one-click fixes", "Centred strictly on pull requests; hosted proprietary subscription service"],
        ["GitHub Copilot code review", "AI review inside GitHub and IDEs", "Reviews pull requests and changes with suggested edits", "Premium feature with monthly quota; GitHub advises validating its feedback"],
        ["Pylint / Bandit", "Open-source Python linters", "Free, deterministic style, bug and security checks", "Rule output only; no contextual explanation, improved code diff or overall score"]
    ]
    
    col_w = [Inches(2.0), Inches(2.2), Inches(3.8), Inches(3.733)]
    
    t_shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.5))
    tbl = t_shape.table
    
    for j, w in enumerate(col_w):
        tbl.columns[j].width = w
    
    # Header row
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(28, 38, 58)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = h
        r.font.name = FONT_NAME
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
    
    # Rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if i % 2 == 0 else COLOR_CARD_ALT
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = val
            r.font.name = FONT_NAME
            r.font.size = Pt(11)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_WHITE
            elif j == 3:
                r.font.color.rgb = RGBColor(248, 113, 113) # Subtle red warning
            else:
                r.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Footnote
    tb_fn = slide.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.5))
    p_fn = tb_fn.text_frame.paragraphs[0]
    r_fn = p_fn.add_run()
    r_fn.text = "Sources: Sonar, CodeRabbit and GitHub documentation, reviewed November 2026."
    r_fn.font.name = FONT_NAME
    r_fn.font.size = Pt(9.5)
    r_fn.font.italic = True
    r_fn.font.color.rgb = COLOR_MUTED

def build_slide_6(prs):
    # -------------------------------------------------------------
    # SLIDE 6: 04 · RESEARCH GAP / OPPORTUNITY
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "04 · Research Gap / Opportunity", "Opportunity: What Is Missing", "Product-based project: where existing products leave room")
    
    # Left Column: Where existing products leave room (3 Warning cards)
    tb_l_hdr = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.6), Inches(0.4))
    p = tb_l_hdr.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "⚠️  CURRENT TOOL LIMITATIONS"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_RED
    
    gaps = [
        ("Setup and paid tiers", "Enterprise platforms require complex local setups; automated AI fix features sit behind expensive premium subscription editions."),
        ("Built around pull requests", "Automated reviewers focus almost exclusively on PR webhooks; a quick, ad-hoc paste-and-review view is less accessible."),
        ("Quotas and vendor models", "Hosted cloud reviewers lock users into vendor-specific models with rigid monthly rate limits and token quotas.")
    ]
    
    for i, (title, desc) in enumerate(gaps):
        y = Inches(2.1) + (i * Inches(1.6))
        c = add_card(slide, Inches(0.8), y, Inches(5.6), Inches(1.4),
                     bg_color=RGBColor(26, 18, 22), border_color=RGBColor(90, 30, 35))
        tb = slide.shapes.add_textbox(Inches(1.0), y + Inches(0.12), Inches(5.2), Inches(1.15))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"❌  {title}"
        r1.font.name = FONT_NAME
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_WHITE
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Right Column: OUR OPPORTUNITY (4 Gold/Green check cards)
    tb_r_hdr = slide.shapes.add_textbox(Inches(6.8), Inches(1.6), Inches(5.7), Inches(0.4))
    p = tb_r_hdr.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "⭐  OUR OPPORTUNITY & CONTRIBUTIONS"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD_LIGHT
    
    opps = [
        ("Ground AI in deterministic AST and Radon evidence", "Eliminate hallucinations by anchoring all natural-language feedback in factual static metrics."),
        ("Separate static and AI outputs", "Guarantees that an AI timeout or network error never conceals available deterministic findings."),
        ("Lightweight app with Gemini & DeepSeek choices", "Fast, responsive web portal giving engineers direct control over LLM provider selection."),
        ("Unified schema for code & GitHub repositories", "Consistent JSON schema for snippets, multi-file uploads, and full remote GitHub repos.")
    ]
    
    for i, (title, desc) in enumerate(opps):
        y = Inches(2.1) + (i * Inches(1.18))
        c = add_card(slide, Inches(6.8), y, Inches(5.733), Inches(1.05),
                     bg_color=RGBColor(20, 30, 24), border_color=RGBColor(35, 80, 50))
        tb = slide.shapes.add_textbox(Inches(7.0), y + Inches(0.1), Inches(5.333), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"✔  {title}"
        r1.font.name = FONT_NAME
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_7(prs):
    # -------------------------------------------------------------
    # SLIDE 7: 05 · OBJECTIVES
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "05 · Objectives", "Project Objectives", "The system is designed around evidence-based review")
    
    objs = [
        ("🐛", "Detect issues", "Identify syntax problems, likely bugs, dangerous execution calls, and risky coding patterns deterministically."),
        ("💬", "Explain findings", "Describe why an issue matters in clear, developer-friendly, educational language rather than opaque error codes."),
        ("💡", "Suggest improvements", "Recommend maintainable, production-ready fixes with clean before-and-after code diff comparisons."),
        ("📈", "Assess complexity", "Use static Radon metrics (CC, MI) alongside AI explanations to quantify and discuss code complexity."),
        ("🐙", "Review repositories", "Fetch, inspect, and evaluate supported source files directly from public GitHub repository URLs."),
        ("📋", "Present results", "Organise findings into structured review sections, maintain audit history, and generate exportable reports.")
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(2.3)
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(4.8), Inches(1.8)),
        (Inches(8.8), Inches(1.8)),
        (Inches(0.8), Inches(4.5)),
        (Inches(4.8), Inches(4.5)),
        (Inches(8.8), Inches(4.5))
    ]
    
    for i, (icon, heading, desc) in enumerate(objs):
        x, y = coords[i]
        c = add_card(slide, x, y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {heading}"
        r.font.name = FONT_NAME
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(8)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_8(prs):
    # -------------------------------------------------------------
    # SLIDE 8: 06 · PROPOSED METHODOLOGY (FLOW)
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "06 · Proposed Methodology", "Proposed Methodology", "A hybrid pipeline: deterministic analysis + AI-assisted review")
    
    steps = [
        ("📄", "Source code", "Upload or paste source code"),
        ("🔍", "Static analysis", "Syntax, AST & complexity"),
        ("🤖", "AI review", "Provider-based explanation"),
        ("📋", "Validation", "Check structured output"),
        ("📊", "Dashboard", "Issues, fixes & score")
    ]
    
    box_w = Inches(1.9)
    box_h = Inches(2.8)
    arrow_w = Inches(0.5)
    start_x = Inches(0.8)
    top_y = Inches(2.0)
    
    for i, (icon, title, desc) in enumerate(steps):
        x = start_x + (i * Inches(2.45))
        c = add_card(slide, x, top_y, box_w, box_h, bg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER)
        
        tb = slide.shapes.add_textbox(x + Inches(0.1), top_y + Inches(0.2), box_w - Inches(0.2), box_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        # Step number
        p0 = tf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = f"STEP {i+1}"
        r0.font.name = FONT_NAME
        r0.font.size = Pt(10)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_GOLD
        
        # Icon
        p_ic = tf.add_paragraph()
        p_ic.space_before = Pt(6)
        r_ic = p_ic.add_run()
        r_ic.text = icon
        r_ic.font.size = Pt(28)
        
        # Title
        p1 = tf.add_paragraph()
        p1.space_before = Pt(6)
        r1 = p1.add_run()
        r1.text = title
        r1.font.name = FONT_NAME
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_WHITE
        
        # Description
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(10)
        r2.font.color.rgb = COLOR_MUTED
        
        # Arrow connecting to next box
        if i < len(steps) - 1:
            arr_x = x + box_w + Inches(0.08)
            tb_arr = slide.shapes.add_textbox(arr_x, top_y + Inches(1.1), arrow_w, Inches(0.6))
            p_a = tb_arr.text_frame.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "➔"
            r_a.font.size = Pt(20)
            r_a.font.bold = True
            r_a.font.color.rgb = COLOR_GOLD
    
    # Bottom callout card
    bot_card = add_card(slide, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.5),
                        bg_color=RGBColor(18, 26, 42), border_color=COLOR_GOLD)
    tb_bot = slide.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.2))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True
    
    p_b1 = tf_b.paragraphs[0]
    r_b1 = p_b1.add_run()
    r_b1.text = "💡  Core Architectural Principle:"
    r_b1.font.name = FONT_NAME
    r_b1.font.size = Pt(12)
    r_b1.font.bold = True
    r_b1.font.color.rgb = COLOR_GOLD
    
    p_b2 = tf_b.add_paragraph()
    p_b2.space_before = Pt(4)
    r_b2 = p_b2.add_run()
    r_b2.text = "Static analysis provides an unyielding, deterministic baseline. The AI layer adds contextual explanations and recommendations; structured validation ensures that the final dashboard maintains complete consistency and trustworthiness."
    r_b2.font.name = FONT_NAME
    r_b2.font.size = Pt(12)
    r_b2.font.color.rgb = COLOR_TEXT_LIGHT

print("slide_builders_part1 loaded successfully.")
