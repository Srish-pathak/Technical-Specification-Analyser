import os
from PIL import Image, ImageDraw, ImageFont

img_w, img_h = 2400, 1600
img = Image.new("RGB", (img_w, img_h), color="#FFFFFF")
draw = ImageDraw.Draw(img)

# Try loading Windows system fonts
def get_font(size, bold=False):
    font_names = [
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
    ]
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()

title_font = get_font(42, bold=True)
header_font = get_font(34, bold=True)
body_font = get_font(26, bold=False)
sub_font = get_font(22, bold=False)
mono_font = get_font(26, bold=True)

# Helper to draw rounded rectangle with border
def draw_card(xy, fill, border, radius=20, border_w=3):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=border, width=border_w)

# 1. UI Layer
draw_card((100, 80, 2300, 320), "#F8FAFC", "#6366F1", 24, 4)
draw.text((1200, 130), "Client Presentation Layer (Galactic Portal UI)", font=header_font, fill="#1E1B4B", anchor="mm")
draw.text((1200, 195), "Single Page Application (SPA) | Pure Vanilla JavaScript (ES6+) | CSS3 Galactic Glassmorphism Theme", font=body_font, fill="#475569", anchor="mm")
draw.text((1200, 255), "Modules: Dashboard | Code Analysis | GitHub Repository Review | PDF Specification Analyzer | History | Reports", font=sub_font, fill="#6366F1", anchor="mm")

# Arrow UI to API
draw.line([(1200, 320), (1200, 420)], fill="#6366F1", width=6)
draw.polygon([(1185, 410), (1215, 410), (1200, 435)], fill="#6366F1")
draw.text((1220, 370), "HTTP / REST (JSON & Multipart Form-Data)", font=sub_font, fill="#4F46E5")

# 2. API Gateway & Routing Layer
draw_card((100, 440, 2300, 680), "#EEF2FF", "#4F46E5", 24, 4)
draw.text((1200, 490), "Backend API & Routing Gateway (FastAPI / Starlette / Uvicorn)", font=header_font, fill="#312E81", anchor="mm")
draw.text((1200, 560), "POST /api/analysis/code  |  POST /api/analysis/github  |  POST /api/analysis/pdf  |  GET /api/analysis/pdf/{id}/report", font=mono_font, fill="#4338CA", anchor="mm")
draw.text((1200, 625), "Asynchronous Concurrency (run_in_threadpool) | Bounded Streaming Input Validation | CORS & Cache-Control Middleware", font=sub_font, fill="#475569", anchor="mm")

# Arrows to 3 Core Services
coords = [
    (450, 680, 450, 780),
    (1200, 680, 1200, 780),
    (1950, 680, 1950, 780)
]
for x0, y0, x1, y1 in coords:
    draw.line([(x0, y0), (x1, y1)], fill="#4338CA", width=5)
    draw.polygon([(x0 - 12, y1 - 10), (x0 + 12, y1 - 10), (x0, y1 + 15)], fill="#4338CA")

# 3. Core Processing Engines
# Engine 1: Static Code Analyzer
draw_card((100, 800, 800, 1220), "#F1F5F9", "#64748B", 20, 3)
draw.text((450, 850), "Static Code Analysis Engine", font=get_font(30, bold=True), fill="#0F172A", anchor="mm")
e1_text = [
    "• Python AST Lexical Syntax Parser",
    "• Radon Cyclomatic Complexity (CC)",
    "• Radon Maintainability Index (MI)",
    "• Bandit Security AST (CWE / OWASP)",
    "• Ruff PEP 8 Linter & Rule Engine",
    "• ESLint / Node.js JS Analyzer",
    "• Built-in Quality Fallback (TSA-QLT)"
]
for i, line in enumerate(e1_text):
    draw.text((150, 910 + i * 42), line, font=body_font, fill="#334155")

# Engine 2: GitHub Repository Review Engine
draw_card((850, 800, 1550, 1220), "#F1F5F9", "#64748B", 20, 3)
draw.text((1200, 850), "GitHub Repository Reviewer", font=get_font(30, bold=True), fill="#0F172A", anchor="mm")
e2_text = [
    "• GitHub REST API Tree Traversal",
    "• Language Breakdown by Byte Count",
    "• In-Memory Source Stream Ingestion",
    "• Multi-Language File Identification",
    "• Automated Test Suite Detection",
    "• Deterministic Health Scoring (0-100)",
    "• Token Header Authentication (PAT)"
]
for i, line in enumerate(e2_text):
    draw.text((900, 910 + i * 42), line, font=body_font, fill="#334155")

# Engine 3: PDF Specification Intelligence Engine
draw_card((1600, 800, 2300, 1220), "#F1F5F9", "#64748B", 20, 3)
draw.text((1950, 850), "PDF Specification Analyzer", font=get_font(30, bold=True), fill="#0F172A", anchor="mm")
e3_text = [
    "• Multi-Engine (PyMuPDF / pdfplumber)",
    "• 10-Domain Spec Block Categorizer",
    "• Traceability Matrix (Page Mappings)",
    "• Non-Technical Rejection Guard",
    "• 8-Dimensional Quality Index (0-100)",
    "• ReportLab Executive PDF Exporter",
    "• NumberedCanvas Page X of Y Decorator"
]
for i, line in enumerate(e3_text):
    draw.text((1650, 910 + i * 42), line, font=body_font, fill="#334155")

# Arrows from Engines to Bottom Tiers
draw.line([(450, 1220), (450, 1270), (650, 1270), (650, 1310)], fill="#8B5CF6", width=4)
draw.line([(1200, 1220), (1200, 1270), (650, 1270), (650, 1310)], fill="#8B5CF6", width=4)
draw.line([(1950, 1220), (1950, 1270), (650, 1270), (650, 1310)], fill="#8B5CF6", width=4)

draw.line([(450, 1220), (450, 1285), (1750, 1285), (1750, 1310)], fill="#10B981", width=4)
draw.line([(1200, 1220), (1200, 1285), (1750, 1285), (1750, 1310)], fill="#10B981", width=4)
draw.line([(1950, 1220), (1950, 1285), (1750, 1310)], fill="#10B981", width=4)

# 4. Intelligence & Persistence Tiers
# Tier 1: AI Integration Tier
draw_card((100, 1310, 1180, 1530), "#F5F3FF", "#8B5CF6", 20, 3)
draw.text((640, 1355), "AI Intelligence Tier (Google Gemini)", font=get_font(28, bold=True), fill="#5B21B6", anchor="mm")
draw.text((640, 1410), "Models: gemini-2.5-flash | gemini-1.5-flash | gemini-3.8-flash", font=body_font, fill="#4C1D95", anchor="mm")
draw.text((640, 1465), "Role: Grounded Architectural Synthesis | Code Reviews | Risk Assessment | Recommendations", font=sub_font, fill="#6D28D9", anchor="mm")

# Tier 2: Persistence Tier
draw_card((1220, 1310, 2300, 1530), "#F0FDF4", "#10B981", 20, 3)
draw.text((1760, 1355), "Persistence Tier (SQLite Embedded Database)", font=get_font(28, bold=True), fill="#065F46", anchor="mm")
draw.text((1760, 1410), "Schema: JSON Audit Store | Indices on Analysis ID & Timestamp", font=body_font, fill="#047857", anchor="mm")
draw.text((1760, 1465), "Policies: 90-Day Retention Pruning | Zero PII / PAT Secret Logging Guarantee", font=sub_font, fill="#059669", anchor="mm")

out_path = r"C:\Users\patha\.gemini\antigravity\scratch\Technical-Specification-Analyser\report_images\architecture_diagram.png"
img.save(out_path, quality=95)
print("Saved high-res architecture diagram to:", out_path)
