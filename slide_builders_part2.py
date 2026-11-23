"""
Slide Builders Part 2: Slides 9 to 16
- Slide 9: 06 · Proposed Methodology (Step by Step)
- Slide 10: 07 · Technical Design (System Architecture)
- Slide 11: 07 · Technical Design (Analysis & AI Layers)
- Slide 12: 07 · Technical Design (GitHub Repository Review)
- Slide 13: 07 · Technical Design (Technology Stack)
- Slide 14: 08 · Feasibility
- Slide 15: 09 · Preliminary Progress (Core Features)
- Slide 16: 09 · Preliminary Progress (Dashboard: Code Review)
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

def build_slide_9(prs):
    # -------------------------------------------------------------
    # SLIDE 9: 06 · METHODOLOGY STEP BY STEP
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "06 · Proposed Methodology", "Methodology: Step by Step", "How a review is produced, from input to dashboard")
    
    steps = [
        ("01", "Input", "Source code file or a public GitHub repository URL provided by developer."),
        ("02", "Local checks", "Empty input detection, file-size limits, and local syntax error handling."),
        ("03", "Static analysis", "AST traversal inspecting call arguments, anti-patterns, and security smells."),
        ("04", "Complexity", "Radon computation of Cyclomatic Complexity (CC) and Maintainability Index (MI)."),
        ("05", "AI review", "Structured JSON-only prompt dispatched to Gemini or DeepSeek API."),
        ("06", "Normalise", "Responses parsed and strictly validated against one unified review schema."),
        ("07", "Display", "Static metrics, AI insights, and provider status rendered in isolation."),
        ("08", "Isolation", "Files processed independently; one file failure never halts remaining reviews.")
    ]
    
    card_w = Inches(5.6)
    card_h = Inches(1.1)
    
    for i, (num, title, desc) in enumerate(steps):
        col = i // 4
        row = i % 4
        x = Inches(0.8) if col == 0 else Inches(6.8)
        y = Inches(1.8) + (row * Inches(1.25))
        
        c = add_card(slide, x, y, card_w, card_h)
        
        # Number badge
        nb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), y + Inches(0.15), Inches(0.7), Inches(0.8))
        nb.fill.solid()
        nb.fill.fore_color.rgb = COLOR_GOLD_BG
        nb.line.color.rgb = COLOR_GOLD
        p_n = nb.text_frame.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        r_n = p_n.add_run()
        r_n.text = num
        r_n.font.name = FONT_NAME
        r_n.font.size = Pt(14)
        r_n.font.bold = True
        r_n.font.color.rgb = COLOR_GOLD_LIGHT
        
        # Text
        tb = slide.shapes.add_textbox(x + Inches(0.95), y + Inches(0.1), card_w - Inches(1.05), card_h - Inches(0.2))
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
        p_d.space_before = Pt(2)
        r_d = p_d.add_run()
        r_d.text = desc
        r_d.font.name = FONT_NAME
        r_d.font.size = Pt(10.5)
        r_d.font.color.rgb = COLOR_MUTED

def build_slide_10(prs):
    # -------------------------------------------------------------
    # SLIDE 10: 07 · SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "07 · Technical Design", "System Architecture", "Logical view of the current application design")
    
    layers = [
        ("🖥️", "User Interface Layer", "Streamlit / Galactic Portal dashboard • code input editor • GitHub repository URL • provider toggle"),
        ("⚙️", "Application Layer", "Review orchestration • file handling & validation • provider routing • result coordination & error handling"),
        ("🔍", "Analysis Layer", "Python AST & syntax checking • Radon complexity metrics • deterministic findings & security SAST"),
        ("🤖", "AI Providers Gateway", "Gemini integration (gemini-2.5-flash) • DeepSeek integration (live credentials pending) • schema enforcement"),
        ("💾", "Output & Storage Layer", "Structured review cards • before/after code diffs • persistent review history & PDF export")
    ]
    
    card_w = Inches(11.733)
    card_h = Inches(0.9)
    top_start = Inches(1.8)
    
    for i, (icon, title, desc) in enumerate(layers):
        y = top_start + (i * Inches(1.05))
        c = add_card(slide, Inches(0.8), y, card_w, card_h,
                     bg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER)
        
        # Left accent icon box
        ib = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), y + Inches(0.12), Inches(0.65), Inches(0.65))
        ib.fill.solid()
        ib.fill.fore_color.rgb = RGBColor(28, 38, 58)
        ib.line.fill.background()
        p_i = ib.text_frame.paragraphs[0]
        p_i.alignment = PP_ALIGN.CENTER
        r_i = p_i.add_run()
        r_i.text = icon
        r_i.font.size = Pt(16)
        
        # Text
        tb = slide.shapes.add_textbox(Inches(1.75), y + Inches(0.08), Inches(10.6), Inches(0.74))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title
        r1.font.name = FONT_NAME
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_11(prs):
    # -------------------------------------------------------------
    # SLIDE 11: 07 · ANALYSIS & AI LAYERS
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "07 · Technical Design", "Analysis & AI Layers", "Modules, provider integration and the review schema")
    
    # 3 Column Cards
    col_w = Inches(3.7)
    col_h = Inches(4.8)
    
    # Col 1: Static Analysis
    c1 = add_card(slide, Inches(0.8), Inches(1.8), col_w, col_h)
    tb1 = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), col_h - Inches(0.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "🔍  Static Analysis"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD_LIGHT
    
    static_items = [
        ("syntax_checker.py", "ast.parse() execution for zero-tolerance syntax checks and line offset mapping."),
        ("static_analysis.py", "AST visitor checking call arguments, dangerous functions (eval, exec) and insecure patterns."),
        ("complexity.py", "Radon integration computing Cyclomatic Complexity (CC) and Maintainability Index (MI).")
    ]
    for fn, fd in static_items:
        p_fn = tf1.add_paragraph()
        p_fn.space_before = Pt(10)
        r_fn = p_fn.add_run()
        r_fn.text = f"• {fn}"
        r_fn.font.name = "Consolas"
        r_fn.font.size = Pt(11)
        r_fn.font.bold = True
        r_fn.font.color.rgb = COLOR_WHITE
        
        p_fd = tf1.add_paragraph()
        r_fd = p_fd.add_run()
        r_fd.text = f"  {fd}"
        r_fd.font.name = FONT_NAME
        r_fd.font.size = Pt(10.5)
        r_fd.font.color.rgb = COLOR_MUTED
    
    # Col 2: AI Providers
    c2 = add_card(slide, Inches(4.8), Inches(1.8), col_w, col_h)
    tb2 = slide.shapes.add_textbox(Inches(5.0), Inches(2.0), col_w - Inches(0.4), col_h - Inches(0.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    r = p.add_run()
    r.text = "🤖  AI Providers"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD_LIGHT
    
    p = tf2.add_paragraph()
    p.space_before = Pt(10)
    r = p.add_run()
    r.text = "• Google Gemini"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    p = tf2.add_paragraph()
    r = p.add_run()
    r.text = "  Default provider using gemini-2.5-flash for rapid, grounded contextual review."
    r.font.name = FONT_NAME
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_MUTED
    
    p = tf2.add_paragraph()
    p.space_before = Pt(10)
    r = p.add_run()
    r.text = "• DeepSeek Integration"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    p = tf2.add_paragraph()
    r = p.add_run()
    r.text = "  deepseek-chat via OpenAI-compatible client. Used when API key is provided; otherwise Gemini."
    r.font.name = FONT_NAME
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_MUTED
    
    p = tf2.add_paragraph()
    p.space_before = Pt(10)
    r = p.add_run()
    r.text = "• Failure Isolation"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    p = tf2.add_paragraph()
    r = p.add_run()
    r.text = "  If AI API times out, deterministic static findings remain fully visible on the dashboard."
    r.font.name = FONT_NAME
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Col 3: Review Schema JSON
    c3 = add_card(slide, Inches(8.8), Inches(1.8), col_w, col_h, bg_color=RGBColor(14, 20, 32))
    tb3 = slide.shapes.add_textbox(Inches(9.0), Inches(2.0), col_w - Inches(0.4), col_h - Inches(0.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    
    p = tf3.paragraphs[0]
    r = p.add_run()
    r.text = "📋  Review Schema (JSON)"
    r.font.name = FONT_NAME
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD_LIGHT
    
    json_text = (
        "{\n"
        '  "summary": "...",\n'
        '  "bugs": [\n'
        '    {\n'
        '      "line": 12,\n'
        '      "severity": "critical",\n'
        '      "message": "..."\n'
        '    }\n'
        "  ],\n"
        '  "improvements": [\n'
        '    "..."\n'
        "  ],\n"
        '  "complexity_notes": "...",\n'
        '  "improved_code": "...",\n'
        '  "overall_score": 8.5\n'
        "}"
    )
    p_code = tf3.add_paragraph()
    p_code.space_before = Pt(10)
    r_code = p_code.add_run()
    r_code.text = json_text
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(9.5)
    r_code.font.color.rgb = COLOR_CYAN

def build_slide_12(prs):
    # -------------------------------------------------------------
    # SLIDE 12: 07 · GITHUB REPOSITORY REVIEW
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "07 · Technical Design", "GitHub Repository Review", "Review supported source files from a repository URL")
    
    steps = [
        ("1", "Repository input", "Developer provides a public GitHub repository URL and selects the analysis workflow."),
        ("2", "File discovery", "The fetcher queries GitHub git trees to discover supported files, applying size & file-count safeguards."),
        ("3", "Analysis & review", "Each supported file is routed through static analysis and the configured AI review pipeline.")
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(2.6)
    
    for i, (num, title, desc) in enumerate(steps):
        x = Inches(0.8) + (i * Inches(4.0))
        c = add_card(slide, x, Inches(1.8), card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(2.0), card_w - Inches(0.4), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"Step {num}: {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(10)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Bottom callout box
    card_bot = add_card(slide, Inches(0.8), Inches(4.7), Inches(11.733), Inches(2.0),
                        bg_color=RGBColor(24, 20, 14), border_color=COLOR_GOLD)
    tb_bot = slide.shapes.add_textbox(Inches(1.0), Inches(4.85), Inches(11.333), Inches(1.7))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True
    
    p = tf_b.paragraphs[0]
    r = p.add_run()
    r.text = "⚙️  Key Engineering Safeguards & Considerations:"
    r.font.name = FONT_NAME
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    bullets = [
        "Exclude heavy dependency and binary folders (e.g. node_modules, .venv, dist, build, .git).",
        "Enforce file-count (max 20 sampled files) and byte-size limits to avoid memory overflows and API rate limits.",
        "Preserve original directory hierarchy and file names for clear developer traceability.",
        "Process files with error isolation: a single corrupted file or API failure never halts the remaining repository audit."
    ]
    for b in bullets:
        p_b = tf_b.add_paragraph()
        p_b.space_before = Pt(3)
        r_b = p_b.add_run()
        r_b.text = f"•  {b}"
        r_b.font.name = FONT_NAME
        r_b.font.size = Pt(11)
        r_b.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_13(prs):
    # -------------------------------------------------------------
    # SLIDE 13: 07 · TECHNOLOGY STACK
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "07 · Technical Design", "Technology Stack", "Tools and libraries used in the implementation")
    
    stack = [
        ("🐍", "Python", "Core application and review logic"),
        ("🖥️", "Streamlit", "Interactive web dashboard and controls"),
        ("🌳", "Python AST", "Syntax-tree based static inspection"),
        ("📊", "Radon", "Cyclomatic complexity & maintainability"),
        ("🤖", "Gemini API", "Primary AI-assisted code review provider"),
        ("🔑", "DeepSeek API", "Secondary AI provider (credentials pending)"),
        ("🐙", "GitHub API", "Repository file retrieval and tree crawl"),
        ("🧪", "Pytest", "Automated tests and regression checks")
    ]
    
    card_w = Inches(2.75)
    card_h = Inches(2.1)
    
    for i, (icon, name, role) in enumerate(stack):
        col = i % 4
        row = i // 4
        x = Inches(0.8) + (col * Inches(2.99))
        y = Inches(1.8) + (row * Inches(2.4))
        
        c = add_card(slide, x, y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = icon
        r.font.size = Pt(24)
        
        p_name = tf.add_paragraph()
        p_name.space_before = Pt(4)
        r_n = p_name.add_run()
        r_n.text = name
        r_n.font.name = FONT_NAME
        r_n.font.size = Pt(13.5)
        r_n.font.bold = True
        r_n.font.color.rgb = COLOR_WHITE
        
        p_role = tf.add_paragraph()
        p_role.space_before = Pt(4)
        r_r = p_role.add_run()
        r_r.text = role
        r_r.font.name = FONT_NAME
        r_r.font.size = Pt(10.5)
        r_r.font.color.rgb = COLOR_MUTED

def build_slide_14(prs):
    # -------------------------------------------------------------
    # SLIDE 14: 08 · FEASIBILITY
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "08 · Feasibility", "Feasibility", "Technical, financial and practical")
    
    cols = [
        ("⚙️", "Technical Feasibility", [
            "Mature open-source software stack (Python 3.11, ast, Radon).",
            "Static analysis runs 100% locally with zero external API calls.",
            "Mocked test fixtures enable complete offline testing.",
            "Modular architecture decouples static engine from AI gateway."
        ]),
        ("💰", "Financial Feasibility", [
            "Built entirely on free and open-source tools with zero license fees.",
            "AI usage is optional and metered strictly on free/developer tiers.",
            "34/34 automated regression tests consume zero paid API quota.",
            "Low deployment footprint runs on standard cloud free tiers."
        ]),
        ("💻", "Practical Feasibility", [
            "Runs seamlessly on a standard developer laptop and web browser.",
            "Inspects public repositories with strict size and file limits.",
            "API keys stored safely in environment variables or secrets.",
            "Clean web dashboard requires zero client-side installation."
        ])
    ]
    
    col_w = Inches(3.7)
    col_h = Inches(3.4)
    
    for i, (icon, title, points) in enumerate(cols):
        x = Inches(0.8) + (i * Inches(4.0))
        c = add_card(slide, x, Inches(1.8), col_w, col_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(2.0), col_w - Inches(0.4), col_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        for pt in points:
            p_pt = tf.add_paragraph()
            p_pt.space_before = Pt(6)
            r_pt = p_pt.add_run()
            r_pt.text = f"•  {pt}"
            r_pt.font.name = FONT_NAME
            r_pt.font.size = Pt(11)
            r_pt.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Bottom Callout
    bot_c = add_card(slide, Inches(0.8), Inches(5.5), Inches(11.733), Inches(1.3),
                     bg_color=RGBColor(24, 20, 14), border_color=COLOR_GOLD)
    tb_b = slide.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.333), Inches(1.1))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    
    p = tf_b.paragraphs[0]
    r = p.add_run()
    r.text = "🛡️  Operational Risk Mitigation:"
    r.font.name = FONT_NAME
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    p2 = tf_b.add_paragraph()
    p2.space_before = Pt(2)
    r2 = p2.add_run()
    r2.text = "Main risk: AI-provider rate limits or temporary service outages. This is mitigated by architecting the static analysis engine to operate completely independently from the AI path, ensuring continuous availability of core metrics."
    r2.font.name = FONT_NAME
    r2.font.size = Pt(11)
    r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_15(prs):
    # -------------------------------------------------------------
    # SLIDE 15: 09 · CORE FEATURES IMPLEMENTED
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Core Features Implemented", "Review outputs are organised for practical use")
    
    features = [
        ("📋", "Overview", "High-level summary of the review, project metadata, and executive takeaways."),
        ("🛡️", "Issues", "Bug and security findings tagged with severity levels, lines, and grounded evidence."),
        ("💡", "Improvements", "Actionable, concrete recommendations to improve code maintainability and structure."),
        ("📈", "Complexity", "Radon cyclomatic complexity metrics and natural-language explanatory analysis."),
        ("⭐", "Score", "Calibrated quality score (0-10 or 0-100) with supporting mathematical rationale."),
        ("🔄", "Before / After", "Suggested corrected code diffs with line-by-line explanation of changes."),
        ("🕒", "History", "Access to previous review sessions, historical score trends, and audit exports.")
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(1.4)
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(4.8), Inches(1.8)),
        (Inches(8.8), Inches(1.8)),
        (Inches(0.8), Inches(3.4)),
        (Inches(4.8), Inches(3.4)),
        (Inches(8.8), Inches(3.4)),
        (Inches(0.8), Inches(5.0))
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        x, y = coords[i]
        w = card_w if i < 6 else Inches(7.7) # Make 7th card span 2 cols
        c = add_card(slide, x, y, w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.12), w - Inches(0.3), card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_TEXT_LIGHT
    
    # 8th box: summary badge in bottom right
    c8 = add_card(slide, Inches(8.8), Inches(5.0), card_w, card_h,
                  bg_color=RGBColor(24, 30, 24), border_color=COLOR_GREEN)
    tb8 = slide.shapes.add_textbox(Inches(8.95), Inches(5.12), card_w - Inches(0.3), card_h - Inches(0.24))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    p8 = tf8.paragraphs[0]
    r8 = p8.add_run()
    r8.text = "✔  7 Unified Sections"
    r8.font.name = FONT_NAME
    r8.font.size = Pt(13.5)
    r8.font.bold = True
    r8.font.color.rgb = COLOR_GREEN
    p8_2 = tf8.add_paragraph()
    p8_2.space_before = Pt(3)
    r8_2 = p8_2.add_run()
    r8_2.text = "Organized for immediate developer action and academic software verification."
    r8_2.font.name = FONT_NAME
    r8_2.font.size = Pt(11)
    r8_2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_16(prs, img_path="report_images/code_analysis.png"):
    # -------------------------------------------------------------
    # SLIDE 16: 09 · DASHBOARD: CODE REVIEW
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Dashboard: Code Review", "Paste code, pick a language, review in one click")
    
    # Left Column: Real Application Screenshot
    left_x = Inches(0.8)
    top_y = Inches(1.8)
    img_w = Inches(7.5)
    img_h = Inches(4.8)
    
    if os.path.exists(img_path):
        c_frame = add_card(slide, left_x, top_y, img_w, img_h, bg_color=RGBColor(14, 20, 30), border_color=COLOR_GOLD)
        slide.shapes.add_picture(img_path, left_x + Inches(0.1), top_y + Inches(0.1), width=img_w - Inches(0.2))
    else:
        c_frame = add_card(slide, left_x, top_y, img_w, img_h)
        tb = slide.shapes.add_textbox(left_x + Inches(0.5), top_y + Inches(2.0), img_w - Inches(1.0), Inches(1.0))
        tb.text_frame.paragraphs[0].text = "[Code Review Dashboard Screenshot]"
    
    # Right Column: Workflow Steps
    right_x = Inches(8.6)
    right_w = Inches(3.933)
    
    steps = [
        ("1", "Paste code", "Input Python or JS code directly into the editor, or choose from pre-loaded templates."),
        ("2", "Review", "Click 'Review My Code' to trigger parallel AST traversal and AI contextual review."),
        ("3", "Results", "Receive instant bugs, code smell alerts, complexity scores, and before/after code remedies.")
    ]
    
    for i, (num, title, desc) in enumerate(steps):
        sy = top_y + (i * Inches(1.6))
        c_s = add_card(slide, right_x, sy, right_w, Inches(1.45))
        
        tb = slide.shapes.add_textbox(right_x + Inches(0.15), sy + Inches(0.12), right_w - Inches(0.3), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"Step {num}: {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

print("slide_builders_part2 loaded successfully.")
