"""
Slide Builders Part 3: Slides 17 to 23
- Slide 17: 09 · Preliminary Progress (Progress at a Glance)
- Slide 18: 09 · Preliminary Progress (Dashboard: GitHub Analysis)
- Slide 19: 09 · Preliminary Progress (Testing & Verification)
- Slide 20: 09 · Preliminary Progress (Limitations & Future Work)
- Slide 21: 10 · Expected Outcomes
- Slide 22: Conclusion
- Slide 23: Questions & Answers / Thank You
"""

import os
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from build_presentation import (
    SLIDE_WIDTH, SLIDE_HEIGHT,
    FONT_NAME, COLOR_BG, COLOR_CARD, COLOR_CARD_BORDER, COLOR_CARD_ALT,
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_BG, COLOR_WHITE, COLOR_TEXT_LIGHT,
    COLOR_MUTED, COLOR_GREEN, COLOR_RED, COLOR_CYAN,
    set_slide_background, add_header, add_card
)

def build_slide_17(prs):
    # -------------------------------------------------------------
    # SLIDE 17: 09 · PROGRESS AT A GLANCE
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Progress at a Glance", "What has been accomplished so far")
    
    metrics = [
        ("5", "Architecture Layers", "From Streamlit UI to output & storage", "🖥️"),
        ("7", "Review Sections", "Overview to history in one dashboard", "📋"),
        ("2", "AI Providers", "Gemini and DeepSeek integrations", "🤖"),
        ("34 / 34", "Tests Passed", "Automated, with 0 test failures", "✔")
    ]
    
    card_w = Inches(2.75)
    card_h = Inches(3.2)
    top_y = Inches(1.8)
    
    for i, (stat, title, desc, icon) in enumerate(metrics):
        x = Inches(0.8) + (i * Inches(2.99))
        c = add_card(slide, x, top_y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.15), top_y + Inches(0.2), card_w - Inches(0.3), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_ic = tf.paragraphs[0]
        p_ic.alignment = PP_ALIGN.CENTER
        r_ic = p_ic.add_run()
        r_ic.text = icon
        r_ic.font.size = Pt(28)
        
        p_stat = tf.add_paragraph()
        p_stat.alignment = PP_ALIGN.CENTER
        p_stat.space_before = Pt(8)
        r_s = p_stat.add_run()
        r_s.text = stat
        r_s.font.name = FONT_NAME
        r_s.font.size = Pt(28)
        r_s.font.bold = True
        r_s.font.color.rgb = COLOR_GOLD_LIGHT if i < 3 else COLOR_GREEN
        
        p_t = tf.add_paragraph()
        p_t.alignment = PP_ALIGN.CENTER
        p_t.space_before = Pt(6)
        r_t = p_t.add_run()
        r_t.text = title
        r_t.font.name = FONT_NAME
        r_t.font.size = Pt(13.5)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_WHITE
        
        p_d = tf.add_paragraph()
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(4)
        r_d = p_d.add_run()
        r_d.text = desc
        r_d.font.name = FONT_NAME
        r_d.font.size = Pt(11)
        r_d.font.color.rgb = COLOR_MUTED
    
    # Bottom Callout
    bot_card = add_card(slide, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.5),
                        bg_color=RGBColor(24, 20, 14), border_color=COLOR_GOLD)
    tb_bot = slide.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.2))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True
    
    p = tf_b.paragraphs[0]
    r = p.add_run()
    r.text = "🎯  Core Engineering Foundation:"
    r.font.name = FONT_NAME
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_GOLD
    
    p2 = tf_b.add_paragraph()
    p2.space_before = Pt(4)
    r2 = p2.add_run()
    r2.text = "Core idea: deterministic static analysis grounds every AI-generated explanation, so reviews stay strictly evidence-based, reproducible, and actionable across all evaluation contexts."
    r2.font.name = FONT_NAME
    r2.font.size = Pt(12)
    r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_18(prs, img_path="report_images/github_review.png"):
    # -------------------------------------------------------------
    # SLIDE 18: 09 · DASHBOARD: GITHUB ANALYSIS
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Dashboard: GitHub Analysis", "Analyse a public repository from its URL")
    
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
        tb.text_frame.paragraphs[0].text = "[GitHub Review Dashboard Screenshot]"
    
    # Right Column: Workflow Steps
    right_x = Inches(8.6)
    right_w = Inches(3.933)
    
    steps = [
        ("1", "Enter URL", "Provide a link to any public GitHub repository (e.g. https://github.com/owner/repo)."),
        ("2", "Analyse", "Click 'Analyze Repository' to initiate file discovery, tree traversal, and batch review."),
        ("3", "Privacy", "Inspects supported files securely; files are processed via the configured AI provider.")
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

def build_slide_19(prs):
    # -------------------------------------------------------------
    # SLIDE 19: 09 · TESTING & VERIFICATION
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Testing & Verification", "Automated checks completed in the current development environment")
    
    # Left Big Metric Box
    c_left = add_card(slide, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.8),
                      bg_color=RGBColor(16, 26, 22), border_color=COLOR_GREEN)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(4.1), Inches(4.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    
    p = tf_l.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "34 / 34"
    r.font.name = FONT_NAME
    r.font.size = Pt(40)
    r.font.bold = True
    r.font.color.rgb = COLOR_GREEN
    
    p = tf_l.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Automated Tests Passed"
    r.font.name = FONT_NAME
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = COLOR_WHITE
    
    checklist = [
        "0 test failures across suites",
        "Python compilation & AST check passed",
        "Diff validation schema passed",
        "Local execution verified"
    ]
    p_sp = tf_l.add_paragraph()
    p_sp.space_before = Pt(16)
    for item in checklist:
        p_c = tf_l.add_paragraph()
        p_c.space_before = Pt(4)
        r_c = p_c.add_run()
        r_c.text = f"✔  {item}"
        r_c.font.name = FONT_NAME
        r_c.font.size = Pt(11)
        r_c.font.color.rgb = COLOR_TEXT_LIGHT
    
    # Right Column: 4 Detail Cards
    tests = [
        ("✔", "Unit / regression tests", "Passed in the available test environment, validating AST parsing, Radon metrics, and score clamping.", COLOR_GREEN),
        ("✔", "Repository tests", "Mocked repository tree crawling and provider regression coverage passed with 100% assertions.", COLOR_GREEN),
        ("✔", "Secret scan", "No tracked API keys, private tokens, or hardcoded credentials detected across repository files.", COLOR_GREEN),
        ("⚠️", "Live DeepSeek request", "Not yet verified: live authentication requires valid credentials configured in secrets.", COLOR_GOLD)
    ]
    
    for i, (badge, title, desc, col) in enumerate(tests):
        y = Inches(1.8) + (i * Inches(1.25))
        c = add_card(slide, Inches(5.6), y, Inches(6.933), Inches(1.1))
        
        tb = slide.shapes.add_textbox(Inches(5.8), y + Inches(0.1), Inches(6.533), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{badge}  {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_20(prs):
    # -------------------------------------------------------------
    # SLIDE 20: 09 · LIMITATIONS & FUTURE WORK
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · Preliminary Progress", "Limitations & Future Work", "Clear scope and next steps for a reliable engineering product")
    
    items = [
        ("⚠️", "Current verification gap", "A successful authenticated DeepSeek API call still needs to be tested using a configured Streamlit secret or environment token.", COLOR_GOLD),
        ("🔄", "Provider reliability", "Implement provider-specific diagnostics, bounded exponential retries, response schema validation, and automatic fallback behaviour.", COLOR_CYAN),
        ("🌐", "Broader language support", "Extend safe AST parsing and language-aware static analysis beyond Python to JavaScript, TypeScript, and compiled enterprise languages.", COLOR_GOLD_LIGHT),
        ("🧪", "Evaluation corpus", "Build a curated, labelled test corpus of code snippets and specification documents to measure precision, recall, and usefulness of AI-generated findings.", COLOR_GREEN)
    ]
    
    card_w = Inches(5.6)
    card_h = Inches(2.3)
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(6.8), Inches(1.8)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]
    
    for i, (icon, heading, desc, col) in enumerate(items):
        x, y = coords[i]
        c = add_card(slide, x, y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {heading}"
        r.font.name = FONT_NAME
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(8)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_NAME
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = COLOR_TEXT_LIGHT

def build_slide_21(prs):
    # -------------------------------------------------------------
    # SLIDE 21: 10 · EXPECTED OUTCOMES
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "10 · Expected Outcomes", "Expected Outcomes", "What should be achieved by the end of the project")
    
    outcomes = [
        ("✔", "Verified provider integration", "An authenticated live DeepSeek call tested alongside Gemini, with clearer diagnostics, circuit breakers, and bounded retries."),
        ("🧪", "Measured accuracy", "A labelled test corpus to measure precision, recall, and usefulness of AI-generated findings against verified human code reviews."),
        ("🌐", "Wider language support", "Language-aware analysis beyond Python, with robust repository-level review and automated test suite detection."),
        ("📋", "Complete review product", "A stable, production-grade dashboard with audit history, before/after code diffs, and downloadable PDF certification reports.")
    ]
    
    card_w = Inches(5.6)
    card_h = Inches(2.3)
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(6.8), Inches(1.8)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]
    
    for i, (badge, title, desc) in enumerate(outcomes):
        x, y = coords[i]
        c = add_card(slide, x, y, card_w, card_h)
        
        tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{badge}  {title}"
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

def build_slide_22(prs, logo_path="cuj_logo.png"):
    # -------------------------------------------------------------
    # SLIDE 22: CONCLUSION
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Conclusion", "Conclusion", "A practical hybrid approach to code quality")
    
    # Central Card with Logo
    center_card = add_card(slide, Inches(1.5), Inches(1.8), Inches(10.333), Inches(3.3),
                           bg_color=RGBColor(18, 26, 42), border_color=COLOR_GOLD)
    
    # CUJ Logo inside central card
    if os.path.exists(logo_path):
        slide.shapes.add_picture(logo_path, Inches(1.8), Inches(2.3), height=Inches(1.8))
    
    tb_c = slide.shapes.add_textbox(Inches(4.0), Inches(2.0), Inches(7.5), Inches(2.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    
    p1 = tf_c.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "TechSpecAnalyser combines deterministic static analysis with AI-assisted review to help developers understand code issues and act on them."
    r1.font.name = FONT_NAME
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_WHITE
    
    p2 = tf_c.add_paragraph()
    p2.space_before = Pt(10)
    r2 = p2.add_run()
    r2.text = "The project provides a structured, reproducible workflow for code inspection, repository-level input, and actionable review outputs, while keeping reliability, zero hallucinations, and evidence-based feedback as primary engineering goals."
    r2.font.name = FONT_NAME
    r2.font.size = Pt(12)
    r2.font.color.rgb = COLOR_TEXT_LIGHT
    
    # 3 Bottom Pillars
    pillars = [
        ("🔍", "Evidence-based", "All review insights are anchored in deterministic AST and Radon metrics."),
        ("🐙", "Repository-level input", "Seamless tree crawling and file evaluation across public GitHub repositories."),
        ("✔", "Actionable outputs", "Clear before-and-after code suggestions and structured audit reports.")
    ]
    
    col_w = Inches(3.2)
    for i, (icon, title, desc) in enumerate(pillars):
        x = Inches(1.5) + (i * Inches(3.56))
        c = add_card(slide, x, Inches(5.3), col_w, Inches(1.4))
        
        tb = slide.shapes.add_textbox(x + Inches(0.15), Inches(5.4), col_w - Inches(0.3), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"{icon}  {title}"
        r.font.name = FONT_NAME
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_GOLD_LIGHT
        
        p_d = tf.add_paragraph()
        p_d.space_before = Pt(2)
        r_d = p_d.add_run()
        r_d.text = desc
        r_d.font.name = FONT_NAME
        r_d.font.size = Pt(10)
        r_d.font.color.rgb = COLOR_MUTED

def build_slide_23(prs, logo_path="cuj_logo.png"):
    # -------------------------------------------------------------
    # SLIDE 23: THANK YOU & Q&A
    # -------------------------------------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    
    # Central Card
    center_w = Inches(8.5)
    center_h = Inches(5.8)
    center_x = (SLIDE_WIDTH - center_w) / 2
    center_y = (SLIDE_HEIGHT - center_h) / 2
    
    card = add_card(slide, center_x, center_y, center_w, center_h,
                    bg_color=RGBColor(16, 24, 38), border_color=COLOR_GOLD)
    
    # CUJ Logo centered
    if os.path.exists(logo_path):
        slide.shapes.add_picture(logo_path, center_x + (center_w - Inches(1.8)) / 2, center_y + Inches(0.4), height=Inches(1.8))
    
    tb = slide.shapes.add_textbox(center_x + Inches(0.5), center_y + Inches(2.3), center_w - Inches(1.0), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    # Heading
    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    r0 = p0.add_run()
    r0.text = "QUESTIONS & ANSWERS"
    r0.font.name = FONT_NAME
    r0.font.size = Pt(14)
    r0.font.bold = True
    r0.font.color.rgb = COLOR_GOLD
    
    # Thank You
    p1 = tf.add_paragraph()
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(6)
    r1 = p1.add_run()
    r1.text = "Thank You!"
    r1.font.name = FONT_NAME
    r1.font.size = Pt(36)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_WHITE
    
    # Project Title
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = "TechSpecAnalyser (CodeLens AI)"
    r2.font.name = FONT_NAME
    r2.font.size = Pt(16)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_GOLD_LIGHT
    
    # Student Details
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(8)
    r3 = p3.add_run()
    r3.text = "Srishti Pathak  |  Roll No. 23190503052\nIntegrated B.Tech & M.Tech in CSE (AI & Data Science)\nCentral University of Jharkhand, Ranchi"
    r3.font.name = FONT_NAME
    r3.font.size = Pt(12)
    r3.font.color.rgb = COLOR_TEXT_LIGHT

print("slide_builders_part3 loaded successfully.")
