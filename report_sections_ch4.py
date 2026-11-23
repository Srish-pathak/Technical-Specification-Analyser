"""
Chapter 4: Materials and Method builder:
- 4.1 Overall System Architecture (includes Fig. 4.1 architecture_diagram.png)
- 4.2 Technology Stack and Specifications (Table 4.1)
- 4.3 Module Design and Implementation (Code Analysis, GitHub Review, PDF Analysis, History & Reports, Dashboard)
- 4.4 Application Programming Interfaces and Routing (Table 4.2)
- 4.5 Deployment Architecture and Continuous Delivery
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from report_style_helpers import (
    FONT_NAME, set_run_font, add_body_p, add_chapter_title,
    add_heading_1, add_heading_2, add_heading_3, add_bullet_p,
    add_table_with_borders, add_figure
)

def build_chapter_4(doc, report_images_dir):
    add_chapter_title(doc, "4", "Materials and Method")
    
    add_heading_1(doc, "4.1 Overall System Architecture")
    add_body_p(
        doc,
        "TechSpecAnalyser is engineered following a modular, asynchronous multi-tier architecture designed to decouple high-speed deterministic static analysis from external large language model API interactions. The platform is architected around five distinct architectural tiers: (1) Presentation Layer, (2) Application & API Gateway Tier, (3) Deterministic Analysis Engine, (4) Generative AI Service Gateway, and (5) Persistence & Export Layer. Fig. 4.1 illustrates the overarching system architecture, communication pathways, and subsystem dependencies."
    )
    
    # Embed Fig. 4.1 Architecture Diagram
    arch_img_path = os.path.join(report_images_dir, "architecture_diagram.png")
    add_figure(
        doc,
        arch_img_path,
        "High-level system architecture of TechSpecAnalyser illustrating the dual-engine pipeline, static toolchain, and Gemini AI gateway.",
        fig_num="4.1",
        width=Inches(5.7)
    )
    
    add_body_p(
        doc,
        "As depicted in Fig. 4.1, client requests originating from the Galactic Portal web interface communicate with the backend through RESTful JSON endpoints managed by FastAPI. Incoming source files or PDF specification documents are routed immediately to the Deterministic Analysis Engine. In this tier, language-specific AST parsers and PDF text extraction drivers execute locally within isolated, resource-constrained sub-processes to produce grounded metrics without external network dependency. Once deterministic extraction is complete, the structured telemetry is dispatched concurrently to the Generative AI Gateway, where Google Gemini synthesizes contextual summaries and refactoring advice under strict JSON response contracts. Finally, results are persisted into the local audit datastore and rendered dynamically on the frontend interface."
    )
    
    add_heading_1(doc, "4.2 Technology Stack and Specifications")
    add_body_p(
        doc,
        "The implementation of TechSpecAnalyser relies on production-hardened open-source software libraries, asynchronous network clients, and industry-standard static analysis tools. Table 4.1 provides a detailed inventory of the technology stack, library versions, and architectural responsibilities."
    )
    
    # Table 4.1 Technology Stack
    headers_41 = ["Technology / Library", "Version", "Category", "Architectural Role and Responsibility"]
    rows_41 = [
        ["Python", "3.11+", "Core Runtime", "High-performance backend runtime with native asynchronous event loop support"],
        ["FastAPI", "0.104.1", "Web Framework", "Asynchronous ASGI REST API framework providing Pydantic request validation and OpenAPI docs"],
        ["Uvicorn", "0.24.0", "ASGI Server", "Lightning-fast ASGI web server implementation utilizing uvloop and httptools"],
        ["Pydantic", "2.5.0+", "Data Validation", "Strict data parsing, schema enforcement, and type serialization across API boundaries"],
        ["PyMuPDF (fitz)", "1.23.8", "PDF Extraction", "High-speed C-based PDF rendering and text stream extraction preserving font and page tags"],
        ["pdfplumber", "0.10.3", "PDF Extraction", "Secondary PDF fallback parser specialized in tabular data extraction and visual layout"],
        ["pypdf", "3.17.1", "PDF Extraction", "Pure-Python tertiary fallback parser ensuring extraction resiliency during native library faults"],
        ["Radon", "6.0.1", "Static Metrics", "Deterministic computation of Cyclomatic Complexity, Halstead metrics, and Maintainability Index"],
        ["Bandit", "1.7.5", "Security SAST", "AST-based security vulnerability and Common Weakness Enumeration (CWE) scanner for Python"],
        ["Ruff", "0.1.6+", "AST Linter", "Extremely fast Rust-based Python linter enforcing PEP-8, flake8, and code quality invariants"],
        ["ESLint / Node.js", "18+ / 8.53+", "JS Linter", "Deterministic syntax checking, complexity auditing, and anti-pattern detection for JavaScript"],
        ["httpx", "0.25.1", "HTTP Client", "Asynchronous HTTP/1.1 and HTTP/2 client for non-blocking Gemini and GitHub REST calls"],
        ["Google Gemini API", "2.5 / 1.5", "Foundation AI", "Multimodal generative foundation models used for semantic synthesis and gap analysis"],
        ["ReportLab", "4.0.7", "PDF Generation", "Dynamic vector PDF report generation engine producing downloadable audit certifications"],
        ["Vanilla JS / CSS3", "ES2022", "Frontend", "Galactic Portal single-page application with zero external runtime framework overhead"]
    ]
    col_w_41 = [Inches(1.2), Inches(0.7), Inches(1.1), Inches(3.0)]
    add_table_with_borders(doc, headers_41, rows_41, col_w_41, "Technology stack and library specifications for the TechSpecAnalyser platform", "4.1")
    
    add_heading_1(doc, "4.3 Module Design and Implementation")
    add_body_p(
        doc,
        "TechSpecAnalyser is partitioned into five tightly decoupled, cohesive functional modules: Source Code Analysis, GitHub Repository Review, PDF Specification Analysis, Historical Audit Logging, and Dashboard Visual Analytics."
    )
    
    add_heading_2(doc, "4.3.1 Source code analysis engine")
    add_body_p(
        doc,
        "The Source Code Analysis Engine provides comprehensive static analysis across multi-file software projects, specializing in Python and JavaScript. When a source code snippet or archive is submitted, the module initiates a multi-stage deterministic pipeline. For Python codebases, the module invokes Python's internal ast module to build an in-memory Abstract Syntax Tree. Custom AST visitor classes traverse the tree to extract structural telemetry: number of function definitions, class declarations, average line lengths, and docstring coverage."
    )
    add_body_p(
        doc,
        "Simultaneously, the engine executes Radon over the codebase to compute the cyclomatic complexity of every function and method. Functions exhibiting cyclomatic complexity above 10 are flagged as warnings, while those exceeding 20 are categorized as critical cognitive hazards. Maintainability index calculations are derived using Eqn. (3.2) and Eqn. (3.3). In parallel, Bandit scans the AST for dangerous patterns—such as insecure string formatting in SQL queries, unvalidated deserialization via pickle, or the invocation of os.system(). For JavaScript files, the engine delegates parsing to Node.js and ESLint, extracting syntax errors, undeclared variables, and cyclomatic branches."
    )
    add_body_p(
        doc,
        "Once deterministic extraction concludes, the aggregated issues and complexity metrics are passed to the scoring algorithm defined in Eqn. (3.4) and Eqn. (3.5) to produce the Code Quality Score. The findings are then wrapped into a structured JSON payload and dispatched to Google Gemini (gemini-2.5-flash), which generates a concise executive summary, highlights the most severe architectural risks, and outlines concrete code refactoring diffs."
    )
    
    add_heading_2(doc, "4.3.2 GitHub repository review engine")
    add_body_p(
        doc,
        "The GitHub Repository Review Engine automates the evaluation of remote software repositories. Given a repository URL (e.g., https://github.com/owner/repo), the service parses the owner and repository identifiers and executes asynchronous HTTPS requests to the GitHub REST API v3 using httpx. The engine inspects repository metadata—including star count, fork ratio, open issue count, default branch, and primary programming languages."
    )
    add_body_p(
        doc,
        "Next, the engine fetches the recursive Git tree (/repos/{owner}/{repo}/git/trees/{branch}?recursive=1) to construct a full hierarchical directory map without cloning the entire physical repository to disk. This approach reduces network bandwidth consumption by over 90%. The engine inspects the file tree for critical engineering hygiene markers: presence of automated test directories (tests/, test/, spec/), continuous integration configurations (.github/workflows/, .travis.yml), dependency manifests (requirements.txt, package.json, pyproject.toml), and documentation (README.md, LICENSE, CONTRIBUTING.md). Representative source files from the default branch are sampled and piped through the static analysis engine, culminating in the calculation of the Repository Health Score using Eqn. (3.6) and Eqn. (3.7)."
    )
    
    add_heading_2(doc, "4.3.3 PDF technical specification analysis engine")
    add_body_p(
        doc,
        "The PDF Technical Specification Analysis Engine is engineered to parse, categorize, and verify formal software engineering documents—including Software Requirements Specifications (SRS), Software Design Documents (SDD), System Architecture Documents, and API Specifications. Digital PDFs frequently contain complex typography, multi-column layouts, tables, and varying character encodings that cause single-library extractors to fail. To achieve industrial-grade resiliency, TechSpecAnalyser implements a multi-library cascading fallback extraction pipeline."
    )
    add_body_p(
        doc,
        "The primary extractor utilizes PyMuPDF (fitz), which offers C-level execution speed, font property detection, and precise page boundary mapping. If PyMuPDF encounters stream corruption or encrypted fragments, the pipeline falls back sequentially to pdfplumber (which excels at geometric bounding box and table detection) and finally to pypdf. Each extracted text chunk is tagged with its originating page number (e.g., [Page 3]), ensuring complete forward and backward requirements traceability."
    )
    add_body_p(
        doc,
        "The extracted text stream is then partitioned into structural specification domains using regex pattern matching and semantic section headers. These domains include: (1) Project Overview, (2) Functional Requirements, (3) Non-Functional Requirements, (4) System Architecture, (5) Technical Stack and Dependencies, (6) Database and Data Models, (7) Security and Privacy Constraints, and (8) Potential Risks and Missing Requirements."
    )
    add_body_p(
        doc,
        "The structured text is subsequently transmitted to Google Gemini via a carefully engineered prompt with strict response schemas. The prompt enforces that the AI model must analyze actual document content only, identify missing or ambiguous requirements, evaluate IEEE 830 compliance, compute dimensional scores using the criteria in Table 3.1, and return a validated JSON payload. If the uploaded document is identified as non-technical (e.g., a cooking recipe or general novel), the system flags the document as unsupported rather than manufacturing misleading software metrics. Furthermore, users can download a professionally formatted, multi-page vector PDF report generated via ReportLab containing the complete audit trail and quality certificates."
    )
    
    add_heading_2(doc, "4.3.4 Historical audit trail and reporting service")
    add_body_p(
        doc,
        "To ensure compliance with corporate governance and academic audit standards, all completed code analyses, repository evaluations, and PDF specification audits are archived by the Historical Audit Trail Service. Each audit record encapsulates: a unique cryptographic UUID, timestamp, target identifier (file name or repository URL), computed quality scores, severity breakdown (critical, warning, informational, passed), raw static tool telemetry, and AI-generated executive summaries. The service exposes search and filtering endpoints allowing users to query past reviews by date range, technology stack, or quality score threshold. In addition, the reporting service provides on-demand serialization of historical records into structured JSON and downloadable PDF formats."
    )
    
    add_heading_2(doc, "4.3.5 Dashboard and visual analytics portal")
    add_body_p(
        doc,
        "The Galactic Portal Dashboard serves as the central visual operational cockpit for TechSpecAnalyser. Built with vanilla ECMAScript 2022 and modern CSS3, the frontend adheres to a futuristic Galactic Portal theme: dark navy/space background (#0B0F19 to #0F172A), vibrant violet-to-cyan gradient accents (#7C3AED to #06B6D4), translucent glassmorphism cards with subtle border glows, and an animated HTML5 canvas starfield."
    )
    add_body_p(
        doc,
        "The dashboard aggregates telemetry from all subsystems, displaying live KPI metric cards (Total Analyses Conducted, Average Code Quality Score, Average Repository Health Score, and Active PDF Audits). Interactive radar charts and horizontal stacked bar graphs—rendered via Chart.js—visualize the distribution of cyclomatic complexity, maintainability indices, and defect severities across recent analyses. The single-page application router dynamically swaps module views without full browser reloads, providing a desktop-class user experience."
    )
    
    add_heading_1(doc, "4.4 Application Programming Interfaces and Routing")
    add_body_p(
        doc,
        "All client-server communications in TechSpecAnalyser are mediated through a RESTful API exposed by FastAPI. The API implements CORS middleware, strict Pydantic payload models, and standardized HTTP status codes. Table 4.2 documents the primary REST API endpoints, HTTP methods, request bodies, and functional descriptions."
    )
    
    # Table 4.2 REST API Endpoints
    headers_42 = ["HTTP Method", "Endpoint Route", "Input Payload", "Response Type", "Functional Description"]
    rows_42 = [
        ["POST", "/api/analyze-code", "JSON {code, language, filename}", "JSON (CodeAnalysisResult)", "Executes AST parsing, Radon, Bandit, Ruff/ESLint, computes score, queries Gemini"],
        ["POST", "/api/analyze-repo", "JSON {repo_url, branch, auth_token}", "JSON (RepoReviewResult)", "Traverses GitHub tree, detects tests/CI, audits sampled files, computes health score"],
        ["POST", "/api/pdf/upload-and-analyze", "Multipart Form (PDF File)", "JSON (PDFAnalysisResult)", "Extracts text via fitz/pdfplumber, categorizes SRS sections, computes Q_spec via Gemini"],
        ["GET", "/api/pdf/download-report/{id}", "Path Parameter {id}", "Binary (application/pdf)", "Generates and streams downloadable ReportLab PDF audit report with page references"],
        ["GET", "/api/history", "Query {limit, offset, filter_type}", "JSON (List[AuditRecord])", "Retrieves paginated audit history records with sorting and search capabilities"],
        ["GET", "/api/dashboard/stats", "None", "JSON (DashboardStats)", "Aggregates global analytics: total scans, mean quality scores, and severity distribution"],
        ["GET", "/api/health", "None", "JSON {status, version, uptime}", "Performs operational health probe checking Gemini API and local engine availability"]
    ]
    col_w_42 = [Inches(0.9), Inches(1.8), Inches(1.4), Inches(1.3), Inches(2.0)]
    add_table_with_borders(doc, headers_42, rows_42, col_w_42, "REST API endpoints and routing specifications for the TechSpecAnalyser platform", "4.2")
    
    add_heading_1(doc, "4.5 Deployment Architecture and Continuous Delivery")
    add_body_p(
        doc,
        "TechSpecAnalyser is configured for continuous delivery and containerized cloud hosting on the Render Platform as a Service (PaaS). The deployment specification is codified in render.yaml, designating an environment with Python 3.11+, Node.js runtime bindings, and pre-compiled C libraries required for PyMuPDF. The application entry point is managed by Uvicorn running app.main:app bound to 0.0.0.0 with dynamic port allocation."
    )
    add_body_p(
        doc,
        "Production deployment security is maintained through environment variable segregation: GEMINI_API_KEY and GITHUB_TOKEN are injected at runtime via encrypted secrets managers rather than being baked into the repository. Static frontend assets (HTML, CSS, JavaScript, icons) are served directly by FastAPI's StaticFiles middleware with explicit Cache-Control headers to ensure zero-downtime updates and prevent client browser cache corruption."
    )
    
    doc.add_page_break()

print("report_sections_ch4 loaded.")
