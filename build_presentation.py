"""
Main script to generate the complete 23-slide official B.Tech presentation for TechSpecAnalyser (CodeLens AI).
Incorporates:
- Central University of Jharkhand (CUJ) official logo
- Student Name: Srishti Pathak (Roll No. 23190503052)
- Program: Integrated B.Tech & M.Tech in CSE (AI & Data Science), 7th Semester Project | 2026
- Faculty Guide: Dr. Prashant Prashun, Assistant Professor, Department of CSE, CUJ
- Institution: Central University of Jharkhand, Ranchi (CUJ, Ranchi)
- All 23 slides with exact data, tables, cards, workflows, and screenshots
"""

import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Widescreen 16:9 dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette (Dark Futuristic Theme)
COLOR_BG = RGBColor(11, 15, 25)          # #0B0F19 Deep Midnight Navy
COLOR_CARD = RGBColor(22, 31, 48)        # #161F30 Card fill
COLOR_CARD_BORDER = RGBColor(46, 61, 86) # #2E3D56 Subtle border
COLOR_CARD_ALT = RGBColor(17, 24, 39)    # #111827 Darker card fill
COLOR_GOLD = RGBColor(245, 158, 11)      # #F59E0B Amber / Gold Accent
COLOR_GOLD_LIGHT = RGBColor(251, 191, 36)# #FBBF24 Bright Gold
COLOR_GOLD_BG = RGBColor(45, 35, 18)     # Dark Gold badge background
COLOR_WHITE = RGBColor(255, 255, 255)    # #FFFFFF
COLOR_TEXT_LIGHT = RGBColor(226, 232, 240)# #E2E8F0 Soft White
COLOR_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Slate Muted
COLOR_GREEN = RGBColor(16, 185, 129)     # #10B981 Success / Passed
COLOR_RED = RGBColor(239, 68, 68)        # #EF4444 Warning / Gap
COLOR_CYAN = RGBColor(56, 189, 248)      # #38BDF8 Info / Accent Cyan

FONT_NAME = "Segoe UI"

def set_slide_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.fill.background()
    return bg

def add_header(slide, tracker_text, title_text, subtitle_text=None, logo_path="cuj_logo.png"):
    set_slide_background(slide)
    
    # Top-right watermark/badge
    if os.path.exists(logo_path):
        slide.shapes.add_picture(logo_path, Inches(12.3), Inches(0.35), height=Inches(0.75))
    
    tb_badge = slide.shapes.add_textbox(Inches(9.2), Inches(0.4), Inches(3.0), Inches(0.6))
    tf_badge = tb_badge.text_frame
    tf_badge.word_wrap = True
    p_b = tf_badge.paragraphs[0]
    p_b.alignment = PP_ALIGN.RIGHT
    r_b = p_b.add_run()
    r_b.text = "Central University of Jharkhand\nTechSpecAnalyser • 2026"
    r_b.font.name = FONT_NAME
    r_b.font.size = Pt(9.5)
    r_b.font.color.rgb = COLOR_MUTED
    
    # Tracker / Category
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(1.3))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    
    p_tr = tf_title.paragraphs[0]
    p_tr.space_after = Pt(2)
    r_tr = p_tr.add_run()
    r_tr.text = tracker_text.upper()
    r_tr.font.name = FONT_NAME
    r_tr.font.size = Pt(11)
    r_tr.font.bold = True
    r_tr.font.color.rgb = COLOR_GOLD
    
    # Title
    p_t = tf_title.add_paragraph()
    p_t.space_after = Pt(2)
    r_t = p_t.add_run()
    r_t.text = title_text
    r_t.font.name = FONT_NAME
    r_t.font.size = Pt(22)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_WHITE
    
    # Subtitle
    if subtitle_text:
        p_st = tf_title.add_paragraph()
        r_st = p_st.add_run()
        r_st.text = subtitle_text
        r_st.font.name = FONT_NAME
        r_st.font.size = Pt(12)
        r_st.font.color.rgb = COLOR_MUTED

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card

def main():
    print("Beginning 23-Slide Presentation Generation...")
    workspace_dir = os.path.abspath(os.path.dirname(__file__))
    logo_path = os.path.join(workspace_dir, "cuj_logo.png")
    code_img = os.path.join(workspace_dir, "report_images", "code_analysis.png")
    gh_img = os.path.join(workspace_dir, "report_images", "github_review.png")
    output_pptx = os.path.join(workspace_dir, "TechSpecAnalyser_Presentation.pptx")
    
    prs = pptx.Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    
    # Import slide builders
    from slide_builders_part1 import (
        build_slide_1, build_slide_2, build_slide_3, build_slide_4,
        build_slide_5, build_slide_6, build_slide_7, build_slide_8
    )
    from slide_builders_part2 import (
        build_slide_9, build_slide_10, build_slide_11, build_slide_12,
        build_slide_13, build_slide_14, build_slide_15, build_slide_16
    )
    from slide_builders_part3 import (
        build_slide_17, build_slide_18, build_slide_19, build_slide_20,
        build_slide_21, build_slide_22, build_slide_23
    )
    
    print("Building Slides 1 to 8 (Title, Agenda, Problem, Background, Review, Gap, Objectives, Methodology Flow)...")
    build_slide_1(prs, logo_path)
    build_slide_2(prs)
    build_slide_3(prs)
    build_slide_4(prs)
    build_slide_5(prs)
    build_slide_6(prs)
    build_slide_7(prs)
    build_slide_8(prs)
    
    print("Building Slides 9 to 16 (Step-by-Step, Architecture, Layers, GitHub Review, Stack, Feasibility, Features, Code Review Dashboard)...")
    build_slide_9(prs)
    build_slide_10(prs)
    build_slide_11(prs)
    build_slide_12(prs)
    build_slide_13(prs)
    build_slide_14(prs)
    build_slide_15(prs)
    build_slide_16(prs, code_img)
    
    print("Building Slides 17 to 23 (Progress, GitHub Dashboard, Testing 34/34, Limitations, Expected Outcomes, Conclusion, Thank You)...")
    build_slide_17(prs)
    build_slide_18(prs, gh_img)
    build_slide_19(prs)
    build_slide_20(prs)
    build_slide_21(prs)
    build_slide_22(prs, logo_path)
    build_slide_23(prs, logo_path)
    
    prs.save(output_pptx)
    file_size = os.path.getsize(output_pptx)
    print(f"Presentation saved successfully to: {output_pptx}")
    print(f"Total Slides: {len(prs.slides)}, File Size: {file_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()
