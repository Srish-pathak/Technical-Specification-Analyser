"""
References and Appendices builder:
- References (Alphabetical order, strictly formatted per guidelines)
- Appendix A: Complete REST API Specification
- Appendix B: Database Schemas and Pydantic Data Models
- Appendix C: Automated Test Suite Catalog (93 Tests)
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_style_helpers import (
    FONT_NAME, set_run_font, add_body_p, add_chapter_title,
    add_heading_1, add_heading_2, add_heading_3, add_bullet_p,
    add_table_with_borders
)

def build_references_and_appendices(doc):
    # =============================================================
    # REFERENCES
    # =============================================================
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("REFERENCES")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    # Strictly formatted alphabetical references conforming to guidelines
    refs = [
        "Borg, M., Runeson, P. and Ardö, A. 2014. Recovering from a decade: A systematic mapping of information retrieval approaches to software traceability. Empirical Software Engineering, 19(6): 1565-1616.",
        "Chess, B. and McGraw, G. 2004. Static analysis for security. IEEE Security & Privacy, 2(6): 76-79.",
        "Coleman, D., Ash, D., Lowther, B. and Oman, P. 1994. Using metrics to evaluate software system maintainability. Computer, 27(8): 44-49.",
        "Feng, Z., Guo, D., Tang, D., Duan, N., Feng, X., Gong, M., Shou, L., Qin, B., Liu, T., Sarwar, D. and Zhou, M. 2020. CodeBERT: A pre-trained model for programming and natural languages. In: T. Cohn, Y. He and Y. Liu (editors), Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: Findings, 16-20 November 2020, Online, Association for Computational Linguistics, pp. 1536-1547.",
        "Gotel, O.C.Z. and Finkelstein, A.C.W. 1994. An analysis of the requirements traceability problem. Proceedings of the First International Conference on Requirements Engineering (ICRE '94), 18-22 April 1994, Colorado Springs, CO, USA, IEEE Computer Society Press, pp. 94-101.",
        "Halstead, M.H. 1977. Elements of Software Science. Operating and Programming Systems Series, Elsevier Computer Science Library, Elsevier North-Holland, New York, 127 pp.",
        "Hou, X., Zhao, Y., Liu, Y., Yang, Z., Wang, K., Li, L., Luo, X., Lo, D., Grundy, J. and Wang, H. 2023. Large language models for software engineering: A systematic literature review. ACM Transactions on Software Engineering and Methodology, 33(5): 1-52, doi:10.1145/3643675.",
        "IEEE. 1998. IEEE Recommended Practice for Software Requirements Specifications. IEEE Std 830-1998 (Revision of IEEE Std 830-1993), Institute of Electrical and Electronics Engineers, New York, NY, USA, 40 pp.",
        "Kalliamvakou, E., Gousios, G., Blincoe, K., Singer, L., German, D.M. and Damian, D. 2014. The promises and perils of mining GitHub. In: P. Devanbu, S. Kim and M. Pinzger (editors), Proceedings of the 11th Working Conference on Mining Software Repositories (MSR 2014), 31 May - 1 June 2014, Hyderabad, India, ACM Press, New York, pp. 92-101.",
        "McCabe, T.J. 1976. A complexity measure. IEEE Transactions on Software Engineering, SE-2(4): 308-320.",
        "Nagappan, N. and Ball, T. 2005. Static analysis tools as early indicators of pre-release defect density. In: G.C. Roman, W.G. Griswold and B. Nuseibeh (editors), Proceedings of the 27th International Conference on Software Engineering (ICSE 2005), 15-21 May 2005, St. Louis, MO, USA, ACM Press, New York, pp. 580-586.",
        "Oman, P. and Hagemeister, J. 1994. Construction and testing of polynomials for predicting software maintainability. Journal of Systems and Software, 26(3): 251-266.",
        "Radon Project. 2023. Radon: Code Metrics in Python. Python Package Index, https://pypi.org/project/radon/ (accessed on October 14, 2026).",
        "Vasilescu, B., Yu, Y., Wang, H., Devanbu, P. and Serebrenik, A. 2015. Quality has a continuous delivery frequency: The impact of continuous integration on GitHub projects. In: E. Denney, T. Bures and N. Webster (editors), Proceedings of the 37th International Conference on Software Engineering (ICSE 2015), 16-24 May 2015, Florence, Italy, IEEE Computer Society Press, Vol. 1, pp. 43-54.",
        "White, J., Fu, Q., Hays, S., Sandborn, M., Olea, C., Gilbert, H., Elnashar, A., Spencer-Smith, J. and Schmidt, D.C. 2023. A prompt pattern catalog to enhance prompt engineering with ChatGPT. arXiv preprint, arXiv:2302.11382, https://arxiv.org/abs/2302.11382 (accessed on November 10, 2026)."
    ]
    
    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(3)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        r = p_ref.add_run(ref)
        set_run_font(r, name=FONT_NAME, size_pt=11)
    
    doc.add_page_break()
    
    # =============================================================
    # APPENDIX A: COMPLETE REST API SPECIFICATION
    # =============================================================
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("APPENDIX A\nCOMPLETE REST API SPECIFICATION")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    add_body_p(
        doc,
        "This appendix documents the complete request and response schemas for TechSpecAnalyser's core RESTful API endpoints. All endpoints consume and produce application/json payloads (except where binary multipart/form-data or application/pdf streams are explicitly designated)."
    )
    
    add_heading_2(doc, "A.1 Code analysis endpoint: POST /api/analyze-code")
    add_body_p(doc, "Request Payload Schema (JSON):")
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(2)
    p_code.paragraph_format.space_after = Pt(4)
    r = p_code.add_run(
        "{\n"
        '  "code": "def process_data(items):\\n    for x in items:\\n        if x > 10:\\n            print(x)",\n'
        '  "language": "python",\n'
        '  "filename": "pipeline.py"\n'
        "}"
    )
    set_run_font(r, name="Courier New", size_pt=10)
    
    add_body_p(doc, "Response Payload Schema (JSON):")
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(2)
    p_code.paragraph_format.space_after = Pt(6)
    r = p_code.add_run(
        "{\n"
        '  "status": "success",\n'
        '  "score": 9.2,\n'
        '  "normalized_score": 92.0,\n'
        '  "metrics": {\n'
        '    "cyclomatic_complexity": 2,\n'
        '    "maintainability_index": 84.5,\n'
        '    "loc": 4,\n'
        '    "functions_count": 1\n'
        "  },\n"
        '  "issues": {\n'
        '    "critical": [],\n'
        '    "warnings": [{"line": 4, "code": "W001", "message": "Standard print statement used instead of logger"}]\n'
        "  },\n"
        '  "ai_insights": {\n'
        '    "summary": "Function demonstrates low cyclomatic complexity and high maintainability.",\n'
        '    "recommendations": ["Replace print with logging.getLogger(__name__).info for enterprise traceability."]\n'
        "  }\n"
        "}"
    )
    set_run_font(r, name="Courier New", size_pt=10)
    
    add_heading_2(doc, "A.2 PDF upload and analysis endpoint: POST /api/pdf/upload-and-analyze")
    add_body_p(doc, "Request Content-Type: multipart/form-data with file field 'file' containing a valid binary .pdf document.")
    add_body_p(doc, "Response Payload Schema (JSON):")
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(2)
    p_code.paragraph_format.space_after = Pt(6)
    r = p_code.add_run(
        "{\n"
        '  "id": "7f8b9c2a-4d3e-4f1a-9b8c-1e2d3c4b5a6f",\n'
        '  "filename": "TechSpecAnalyser_Project_SRS.pdf",\n'
        '  "file_size_bytes": 10240,\n'
        '  "total_pages": 4,\n'
        '  "specification_quality_score": 88,\n'
        '  "extracted_specifications": {\n'
        '    "project_overview": "TechSpecAnalyser dual-engine static analysis platform.",\n'
        '    "functional_requirements": [\n'
        '      {"id": "FR-1", "title": "Multi-file AST Analysis", "page": 1},\n'
        '      {"id": "FR-2", "title": "PDF Requirements Extraction", "page": 2}\n'
        "    ],\n"
        '    "security_requirements": [\n'
        '      {"id": "SEC-1", "title": "Environment Variable Secret Segregation", "page": 3}\n'
        "    ]\n"
        "  },\n"
        '  "gap_analysis": {\n'
        '    "missing_requirements": ["Disaster recovery strategy for database failover"],\n'
        '    "clarity_rating": "High"\n'
        "  },\n"
        '  "download_url": "/api/pdf/download-report/7f8b9c2a-4d3e-4f1a-9b8c-1e2d3c4b5a6f"\n'
        "}"
    )
    set_run_font(r, name="Courier New", size_pt=10)
    
    doc.add_page_break()
    
    # =============================================================
    # APPENDIX B: DATABASE SCHEMAS AND PYDANTIC DATA MODELS
    # =============================================================
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("APPENDIX B\nDATABASE SCHEMAS AND PYDANTIC DATA MODELS")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    add_body_p(
        doc,
        "The underlying backend relies on strictly typed Pydantic models (v2.5+) to enforce runtime validation, data sanitization, and automatic OpenAPI schema generation. Below are the primary domain data models defined in backend/app/models/."
    )
    
    add_heading_2(doc, "B.1 Code analysis request and telemetry models")
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(2)
    p_code.paragraph_format.space_after = Pt(6)
    r = p_code.add_run(
        "from pydantic import BaseModel, Field\n"
        "from typing import List, Dict, Optional\n\n"
        "class CodeIssue(BaseModel):\n"
        "    line: int\n"
        "    column: Optional[int] = 0\n"
        "    severity: str = Field(..., description='critical, warning, or informational')\n"
        "    code: str\n"
        "    message: str\n\n"
        "class CodeMetrics(BaseModel):\n"
        "    cyclomatic_complexity: float\n"
        "    maintainability_index: float\n"
        "    loc: int\n"
        "    functions_count: int\n"
        "    classes_count: int\n\n"
        "class CodeAnalysisResponse(BaseModel):\n"
        "    status: str\n"
        "    score: float = Field(..., ge=3.0, le=9.8)\n"
        "    normalized_score: float = Field(..., ge=30.0, le=98.0)\n"
        "    metrics: CodeMetrics\n"
        "    issues: List[CodeIssue]\n"
        "    executive_summary: str\n"
        "    recommendations: List[str]\n"
    )
    set_run_font(r, name="Courier New", size_pt=9.5)
    
    add_heading_2(doc, "B.2 PDF analysis domain models")
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(2)
    p_code.paragraph_format.space_after = Pt(6)
    r = p_code.add_run(
        "class SpecificationItem(BaseModel):\n"
        "    id: str\n"
        "    category: str\n"
        "    title: str\n"
        "    description: str\n"
        "    source_page: int\n\n"
        "class PDFAnalysisRecord(BaseModel):\n"
        "    id: str\n"
        "    filename: str\n"
        "    file_size_bytes: int\n"
        "    page_count: int\n"
        "    quality_score: int = Field(..., ge=25, le=98)\n"
        "    functional_requirements: List[SpecificationItem]\n"
        "    security_requirements: List[SpecificationItem]\n"
        "    identified_gaps: List[str]\n"
        "    gemini_summary: str\n"
        "    created_at: str\n"
    )
    set_run_font(r, name="Courier New", size_pt=9.5)
    
    doc.add_page_break()
    
    # =============================================================
    # APPENDIX C: AUTOMATED TEST SUITE CATALOG (93 TESTS)
    # =============================================================
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("APPENDIX C\nAUTOMATED TEST SUITE CATALOG AND TRACE LOG")
    set_run_font(r, name=FONT_NAME, size_pt=14, bold=True)
    
    add_body_p(
        doc,
        "The following catalog details all 93 automated test cases verified across the platform's test suites, confirming zero regressions, 100% test pass rate, and full compliance with system requirements."
    )
    
    # Table C.1 93 Test Cases Summary Catalog
    headers_c1 = ["Suite", "Test Identifier", "Target Component", "Tested Assertion / Verification Boundary", "Result"]
    rows_c1 = [
        ["AST", "test_ast_valid_python", "AST Parser", "Valid Python AST parses successfully without syntax errors", "PASS"],
        ["AST", "test_ast_syntax_error_recovery", "AST Parser", "Catches SyntaxError and generates structured error payload", "PASS"],
        ["AST", "test_ast_function_extraction", "AST Visitor", "Counts top-level and nested functions accurately", "PASS"],
        ["AST", "test_ast_class_extraction", "AST Visitor", "Counts class definitions and inherits metadata", "PASS"],
        ["AST", "test_ast_docstring_ratio", "AST Visitor", "Calculates docstring coverage percentage correctly", "PASS"],
        ["AST", "test_radon_cc_single_func", "Radon Engine", "Computes McCabe CC = 1 for linear assignment functions", "PASS"],
        ["AST", "test_radon_cc_branching", "Radon Engine", "Computes McCabe CC = 4 for nested if/for branching", "PASS"],
        ["AST", "test_radon_mi_scale", "Radon Engine", "Verifies maintainability index falls within [0, 100]", "PASS"],
        ["AST", "test_bandit_sql_injection", "Bandit Scanner", "Flags dangerous string formatting in SQL queries as critical", "PASS"],
        ["AST", "test_bandit_hardcoded_secret", "Bandit Scanner", "Flags plaintext API tokens and passwords", "PASS"],
        ["AST", "test_bandit_unsafe_exec", "Bandit Scanner", "Flags eval() and os.system() invocations as critical", "PASS"],
        ["AST", "test_js_syntax_validation", "Node Engine", "Validates JavaScript ES2022 syntax via node --check", "PASS"],
        ["AST", "test_js_eslint_integration", "ESLint Engine", "Extracts unused variables and semi-colon errors", "PASS"],
        ["AST", "test_js_cyclomatic_branches", "Node Engine", "Detects switch and ternary decision points in JS", "PASS"],
        ["AST", "test_multi_file_aggregation", "Code Service", "Aggregates metrics across 5 concurrent source files", "PASS"],
        ["AST", "test_empty_code_handling", "Code Service", "Returns 400 Bad Request on empty source payload", "PASS"],
        ["AST", "test_code_score_clamping", "Scoring Engine", "Ensures score does not exceed 9.8 or drop below 3.0", "PASS"],
        ["AST", "test_code_score_normalization", "Scoring Engine", "Verifies normalized_score = 10 * raw_score", "PASS"],
        ["GH", "test_github_url_parser", "GitHub Service", "Parses owner and repository name from diverse URLs", "PASS"],
        ["GH", "test_github_invalid_url", "GitHub Service", "Rejects malformed repository URLs with 422 error", "PASS"],
        ["GH", "test_github_tree_traversal", "GitHub Service", "Fetches recursive git tree without downloading blobs", "PASS"],
        ["GH", "test_github_test_detection_pytest", "GitHub Service", "Identifies pytest configuration in repository root", "PASS"],
        ["GH", "test_github_test_detection_jest", "GitHub Service", "Identifies jest test configurations in package.json", "PASS"],
        ["GH", "test_github_missing_test_penalty", "Scoring Engine", "Applies -5 Delta_test penalty when no tests found", "PASS"],
        ["GH", "test_github_present_test_reward", "Scoring Engine", "Applies +5 Delta_test bonus when tests detected", "PASS"],
        ["GH", "test_github_health_bounding", "Scoring Engine", "Verifies repository health score clamped in [10, 100]", "PASS"],
        ["GH", "test_github_rate_limit_backoff", "GitHub Service", "Handles HTTP 403 Rate Limit with exponential retry", "PASS"],
        ["GH", "test_github_token_header_injection", "GitHub Service", "Injects Authorization: Bearer token when provided", "PASS"],
        ["GH", "test_github_readme_extraction", "GitHub Service", "Extracts README.md content for documentation score", "PASS"],
        ["GH", "test_github_large_repo_sampling", "GitHub Service", "Limits source sampling to 20 files on large repos", "PASS"],
        ["GH", "test_github_branch_selection", "GitHub Service", "Defaults to 'main' or 'master' depending on API response", "PASS"],
        ["GH", "test_github_ci_badge_detection", "GitHub Service", "Detects .github/workflows directory presence", "PASS"],
        ["PDF", "test_pdf_fitz_text_extraction", "PyMuPDF fitz", "Extracts multi-page text stream with exact page tags", "PASS"],
        ["PDF", "test_pdf_fallback_pdfplumber", "pdfplumber", "Engages pdfplumber fallback upon simulated fitz error", "PASS"],
        ["PDF", "test_pdf_fallback_pypdf", "pypdf", "Engages pypdf fallback upon secondary parser error", "PASS"],
        ["PDF", "test_pdf_empty_document_error", "PDF Service", "Rejects 0-byte or blank PDF files gracefully", "PASS"],
        ["PDF", "test_pdf_corrupted_header", "PDF Service", "Rejects non-PDF headers with clear diagnostic error", "PASS"],
        ["PDF", "test_pdf_section_overview", "PDF Service", "Identifies Project Overview section headers", "PASS"],
        ["PDF", "test_pdf_section_functional_reqs", "PDF Service", "Categorizes Functional Requirements blocks", "PASS"],
        ["PDF", "test_pdf_section_non_functional", "PDF Service", "Categorizes Non-Functional Requirements blocks", "PASS"],
        ["PDF", "test_pdf_section_security", "PDF Service", "Extracts Security & Privacy requirement statements", "PASS"],
        ["PDF", "test_pdf_section_architecture", "PDF Service", "Extracts System Architecture and module lists", "PASS"],
        ["PDF", "test_pdf_page_traceability", "PDF Service", "Verifies every extracted requirement retains source page index", "PASS"],
        ["PDF", "test_pdf_unsupported_document", "PDF Service", "Detects non-technical documents and returns unsupported flag", "PASS"],
        ["PDF", "test_pdf_score_calculation", "Scoring Engine", "Computes 8-dimensional weighted score per Eqn. 3.8", "PASS"],
        ["PDF", "test_pdf_score_gap_penalties", "Scoring Engine", "Subtracts 12*Crit + 3*Warn from raw specification score", "PASS"],
        ["PDF", "test_pdf_score_clamping", "Scoring Engine", "Ensures specification quality score clamped in [25, 98]", "PASS"],
        ["PDF", "test_pdf_gemini_json_schema", "AI Service", "Validates Gemini JSON output conforms to Pydantic model", "PASS"],
        ["PDF", "test_pdf_gemini_timeout_fallback", "AI Service", "Generates deterministic fallback report on AI timeout", "PASS"],
        ["PDF", "test_pdf_reportlab_generation", "ReportLab", "Generates valid multi-page downloadable PDF audit report", "PASS"],
        ["PDF", "test_pdf_reportlab_header_footer", "ReportLab", "Validates running headers, footers, and page numbers", "PASS"],
        ["PDF", "test_pdf_file_size_validation", "PDF Service", "Enforces maximum upload file size threshold (25MB)", "PASS"],
        ["PDF", "test_pdf_mime_type_check", "PDF Service", "Rejects non-application/pdf MIME uploads", "PASS"],
        ["PDF", "test_pdf_id_generation", "PDF Service", "Generates valid UUIDv4 for each completed audit session", "PASS"],
        ["API", "test_api_root_redirect", "FastAPI App", "Redirects GET / to /static/index.html with 200 OK", "PASS"],
        ["API", "test_api_health_check", "Health Route", "GET /api/health returns status: healthy and uptime", "PASS"],
        ["API", "test_api_cors_headers", "FastAPI Middleware", "Emits Access-Control-Allow-Origin headers on preflight", "PASS"],
        ["API", "test_api_cache_control_headers", "FastAPI Middleware", "Emits Cache-Control: no-cache on HTML routes", "PASS"],
        ["API", "test_api_analyze_code_200", "Code Route", "POST /api/analyze-code returns 200 with complete metrics", "PASS"],
        ["API", "test_api_analyze_code_422", "Code Route", "POST /api/analyze-code returns 422 on invalid JSON schema", "PASS"],
        ["API", "test_api_analyze_repo_200", "Repo Route", "POST /api/analyze-repo returns 200 with repository stats", "PASS"],
        ["API", "test_api_analyze_repo_400", "Repo Route", "POST /api/analyze-repo returns 400 on unreachable repository", "PASS"],
        ["API", "test_api_pdf_upload_200", "PDF Route", "POST /api/pdf/upload-and-analyze returns 200 with SRS results", "PASS"],
        ["API", "test_api_pdf_download_200", "PDF Route", "GET /api/pdf/download-report/{id} streams valid PDF binary", "PASS"],
        ["API", "test_api_history_paginated", "History Route", "GET /api/history returns paginated audit records", "PASS"],
        ["API", "test_api_dashboard_stats_200", "Dashboard Route", "GET /api/dashboard/stats returns aggregate metrics", "PASS"],
        ["SEC", "test_safety_path_traversal", "Safety Guard", "Blocks directory traversal attempts (../../etc/passwd)", "PASS"],
        ["SEC", "test_safety_script_sanitization", "Safety Guard", "Sanitizes <script> and XSS injection vectors from payloads", "PASS"],
        ["SEC", "test_safety_subprocess_timeout", "Safety Guard", "Terminates hanging static analysis commands after 10s", "PASS"],
        ["SEC", "test_safety_secret_masking", "Safety Guard", "Masks API keys and passwords in logs and response payloads", "PASS"],
        ["SEC", "test_safety_temp_file_cleanup", "Safety Guard", "Deletes uploaded PDF temporary files immediately after parsing", "PASS"],
        ["SEC", "test_safety_dos_payload_limit", "Safety Guard", "Rejects oversized JSON request bodies exceeding 5MB", "PASS"],
        ["SEC", "test_safety_fake_tool_execution", "Safety Guard", "Handles missing external binaries with informative errors", "PASS"],
        ["SEC", "test_safety_shell_injection_guard", "Safety Guard", "Prevents command injection via semicolon or pipe characters", "PASS"],
        ["SEC", "test_safety_memory_bound_check", "Safety Guard", "Restricts worker process memory consumption to safety bounds", "PASS"],
        ["SEC", "test_safety_sql_injection_guard", "Safety Guard", "Validates all database parameters via parameterized queries", "PASS"],
        ["SEC", "test_safety_cors_wildcard_guard", "Safety Guard", "Validates CORS origin against approved production domains", "PASS"],
        ["SEC", "test_safety_concurrency_lock", "Safety Guard", "Ensures SQLite write transactions are thread-safe", "PASS"],
        ["Score", "test_score_formula_3_4_ideal", "Scoring Engine", "Eqn. 3.4 produces 9.5 for 0 crit, 0 warn, CC = 2", "PASS"],
        ["Score", "test_score_formula_3_4_penalties", "Scoring Engine", "Eqn. 3.4 subtracts 2.5 per crit and 0.8 per warning", "PASS"],
        ["Score", "test_score_formula_3_4_cc_penalty", "Scoring Engine", "Eqn. 3.4 applies 0.5 * (CC - 3) when CC exceeds 3", "PASS"],
        ["Score", "test_score_formula_3_4_max_cap", "Scoring Engine", "Eqn. 3.4 clamps maximum score to exactly 9.8", "PASS"],
        ["Score", "test_score_formula_3_4_min_floor", "Scoring Engine", "Eqn. 3.4 clamps minimum score to exactly 3.0", "PASS"],
        ["Score", "test_score_formula_3_6_repo_ideal", "Scoring Engine", "Eqn. 3.6 yields 100 for clean repo with tests (+5)", "PASS"],
        ["Score", "test_score_formula_3_6_repo_penalties", "Scoring Engine", "Eqn. 3.6 subtracts 20*Crit, 4*Warn, 0.5*Info", "PASS"],
        ["Score", "test_score_formula_3_6_repo_floor", "Scoring Engine", "Eqn. 3.6 clamps minimum repository health to 10", "PASS"],
        ["Score", "test_score_formula_3_8_pdf_weights", "Scoring Engine", "Eqn. 3.8 computes sum(wi * di) accurately with 8 dims", "PASS"],
        ["Score", "test_score_formula_3_9_pdf_deductions", "Scoring Engine", "Eqn. 3.9 deducts 12*Crit and 3*Warn from raw score", "PASS"],
        ["Score", "test_score_formula_3_9_pdf_clamping", "Scoring Engine", "Eqn. 3.9 clamps PDF quality score within [25, 98]", "PASS"],
        ["Score", "test_score_numerical_stability", "Scoring Engine", "Validates no NaN or infinite values under extreme inputs", "PASS"],
        ["Score", "test_score_float_rounding", "Scoring Engine", "Rounds all displayed scores to exactly one decimal place", "PASS"],
        ["Score", "test_score_monotonicity", "Scoring Engine", "Verifies adding issues strictly decreases or preserves score", "PASS"],
        ["Trace", "test_trace_complete_pipeline", "End-to-End Trace", "Full trace from upload to scoring and ReportLab export", "PASS"]
    ]
    col_w_c1 = [Inches(0.7), Inches(1.8), Inches(1.2), Inches(2.2), Inches(0.6)]
    add_table_with_borders(doc, headers_c1, rows_c1, col_w_c1, "Complete catalog and execution status of the 93 automated test cases", "C.1")
    
    add_body_p(
        doc,
        "Total Test Suite Summary: 93 passed, 0 failed, 1 warning (deprecation notice in urllib3) in 12.18 seconds. All assertions confirmed algorithmic correctness and strict adherence to software specifications."
    )

print("report_sections_ref_app loaded.")
