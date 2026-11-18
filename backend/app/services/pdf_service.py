"""AI-Powered PDF Technical Specification Analyzer Service for TechSpecAnalyser.

Comprehensive engineering intelligence for:
- Software Requirements Specification (SRS)
- Technical Specification Documents
- Software Design Documents (SDD)
- System Architecture Documents
- Database Design Documents
- API Documentation
- Project Proposals (Software / IT)
- Software Engineering Project Reports
- UML and System Design Documents
- General Technical Documents

Analyzes actual document content using text extraction and Gemini AI.
Detects and rejects non-technical documents gracefully without hallucinating fake technical data.
Produces an executive 10-section structured analysis and downloadable ReportLab PDF audit report.
"""
from __future__ import annotations

import io
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pypdf
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import Settings, get_settings
from app.services.file_manager import InputValidationError

logger = logging.getLogger("techspecanalyser.pdf")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# =========================================================================
# 1. Supported Document Types & Technical Classification Rules
# =========================================================================

SUPPORTED_DOC_TYPES = {
    "srs": {
        "label": "Software Requirements Specification (SRS)",
        "icon": "📋",
        "keywords": [
            r"software requirements specification", r"\bsrs\b", r"functional requirements",
            r"use case", r"user stories", r"system requirements", r"software requirement",
            r"acceptance criteria", r"user role", r"ieee 830", r"ieee 29148"
        ],
    },
    "sdd": {
        "label": "Software Design Document (SDD)",
        "icon": "📐",
        "keywords": [
            r"software design document", r"\bsdd\b", r"low-level design", r"high-level design",
            r"lld", r"hld", r"module design", r"class diagram", r"design specification",
            r"component design", r"software architecture design"
        ],
    },
    "system_architecture": {
        "label": "System Architecture Document",
        "icon": "🏛️",
        "keywords": [
            r"system architecture", r"architectural design", r"microservice", r"microservices",
            r"component diagram", r"infrastructure architecture", r"c4 model", r"layer architecture",
            r"event-driven architecture", r"cloud architecture", r"service-oriented"
        ],
    },
    "database_design": {
        "label": "Database Design Document",
        "icon": "🗄️",
        "keywords": [
            r"database design", r"data dictionary", r"entity relationship", r"\berd\b",
            r"relational schema", r"table structure", r"database schema", r"normalization",
            r"sql schema", r"foreign keys", r"nosql model"
        ],
    },
    "api_documentation": {
        "label": "API Documentation & Specification",
        "icon": "🔌",
        "keywords": [
            r"api documentation", r"api specification", r"openapi", r"swagger", r"rest api",
            r"graphql schema", r"endpoints", r"api reference", r"post /api", r"get /api",
            r"webhook", r"request payload", r"response schema"
        ],
    },
    "project_proposal": {
        "label": "Software Project Proposal",
        "icon": "💡",
        "keywords": [
            r"project proposal", r"software proposal", r"technical proposal", r"project charter",
            r"system proposal", r"feasibility study", r"scope of work", r"deliverables"
        ],
    },
    "engineering_report": {
        "label": "Software Engineering Project Report",
        "icon": "📊",
        "keywords": [
            r"project report", r"software engineering report", r"final report", r"technical report",
            r"capstone project", r"system implementation report", r"evaluation report"
        ],
    },
    "uml_system_design": {
        "label": "UML and System Design Document",
        "icon": "🔄",
        "keywords": [
            r"uml", r"sequence diagram", r"activity diagram", r"state machine", r"class diagram",
            r"deployment diagram", r"use case diagram", r"interaction diagram"
        ],
    },
    "tech_spec": {
        "label": "Technical Specification Document",
        "icon": "⚙️",
        "keywords": [
            r"technical specification", r"tech spec", r"engineering spec", r"system specification",
            r"functional specification", r"product requirements document", r"\bprd\b"
        ],
    },
}

# Core vocabulary indicating genuine software / systems engineering context
TECHNICAL_CORE_VOCABULARY = [
    r"\bsoftware\b", r"\bsystem\b", r"\brequirement\b", r"\brequirements\b", r"\barchitecture\b",
    r"\bdatabase\b", r"\bapi\b", r"\bapis\b", r"\bendpoint\b", r"\bendpoints\b", r"\bmodule\b",
    r"\bmodules\b", r"\bfunction\b", r"\binterface\b", r"\bserver\b", r"\bclient\b", r"\bdata\b",
    r"\bcomponent\b", r"\bframework\b", r"\bprotocol\b", r"\bsecurity\b", r"\bencryption\b",
    r"\bfrontend\b", r"\bbackend\b", r"\blatency\b", r"\bthroughput\b", r"\bperformance\b",
    r"\balgorithm\b", r"\btesting\b", r"\bdeployment\b", r"\bdocker\b", r"\bkubernetes\b",
    r"\bcloud\b", r"\bservice\b", r"\bschema\b", r"\bquery\b", r"\bauthentication\b",
    r"\bauthorization\b", r"\btoken\b", r"\bjson\b", r"\bhttp\b", r"\brest\b", r"\boauth\b"
]


def classify_document_domain_and_type(
    full_text: str,
    meta: Dict[str, Any]
) -> Tuple[bool, str, str, str, Optional[str]]:
    """Determine whether the PDF is a software/technical document and classify its exact type.

    Returns:
        (is_supported, doc_type, doc_type_label, doc_type_icon, rejection_reason)
    """
    text_lower = full_text.lower()
    words = text_lower.split()
    total_words = len(words)

    if total_words < 20:
        return (
            False,
            "unsupported_empty_text",
            "Unsupported Document",
            "⚠️",
            "The uploaded PDF contains insufficient selectable text. It may be a scanned image or empty document.",
        )

    # 1. Count occurrences of core technical software engineering markers
    tech_matches = 0
    for pattern in TECHNICAL_CORE_VOCABULARY:
        if re.search(pattern, text_lower):
            tech_matches += 1

    # Ratio of technical markers to determine domain relevance
    if tech_matches < 4:
        return (
            False,
            "unsupported_non_technical",
            "Unsupported Non-Engineering Document",
            "⚠️",
            (
                "The uploaded document does not appear to be a software engineering specification, "
                "architecture document, or technical report. TechSpecAnalyser is designed specifically "
                "for software systems, SRS, SDDs, and API designs. Non-technical content is flagged "
                "to prevent generating misleading reviews."
            ),
        )

    first_page_intro = text_lower[:800]
    # 2. Score against supported document types
    type_scores: Dict[str, int] = {}
    for doc_type, info in SUPPORTED_DOC_TYPES.items():
        score = 0
        for kw in info["keywords"]:
            # Title / first-page occurrences get massive priority
            if re.search(kw, first_page_intro):
                score += 50
            matches = len(re.findall(kw, text_lower))
            if matches > 0:
                score += matches * 2
        type_scores[doc_type] = score

    # Find highest matching document type
    best_type = max(type_scores, key=type_scores.get)
    best_score = type_scores[best_type]

    if best_score > 0:
        info = SUPPORTED_DOC_TYPES[best_type]
        return (True, best_type, info["label"], info["icon"], None)

    # Fallback to general technical specification
    return (
        True,
        "general_technical",
        "Technical Specification Document",
        "⚙️",
        None,
    )


# =========================================================================
# 2. PDF Extraction & Multi-Page Traversal
# =========================================================================

def extract_pdf_pages(pdf_bytes: bytes, filename: str = "document.pdf") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract text from a PDF while tracking page numbers and document metadata.

    Supports PyMuPDF (fitz), pdfplumber, and pypdf in order of availability.
    Validates PDF format, size, encryption, and readability.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise InputValidationError("pdf_empty", "The uploaded PDF file is empty (0 bytes).", 400)

    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise InputValidationError("pdf_too_large", "The uploaded PDF exceeds the 20MB limit.", 400)

    # Magic byte validation (%PDF-)
    if not (pdf_bytes.startswith(b"%PDF-") or b"%PDF-" in pdf_bytes[:1024]):
        raise InputValidationError(
            "pdf_invalid_format",
            "Invalid file format: uploaded file does not contain a valid PDF signature (%PDF-).",
            400,
        )

    pages: List[Dict[str, Any]] = []
    total_chars = 0
    total_words = 0
    num_pages = 0
    extractor = "pypdf"
    extracted = False

    # 1. Try PyMuPDF (fitz) if installed
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.is_encrypted:
            raise InputValidationError(
                "pdf_encrypted",
                "This PDF is password-protected or encrypted. Please upload an unprotected document.",
                400,
            )
        num_pages = len(doc)
        if num_pages == 0:
            raise InputValidationError("pdf_empty", "The uploaded PDF contains no pages.", 400)

        for idx, page in enumerate(doc, start=1):
            raw_text = page.get_text("text") or ""
            cleaned = re.sub(r"\r\n", "\n", raw_text)
            cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
            words = len(cleaned.split()) if cleaned else 0
            chars = len(cleaned)
            pages.append({
                "page_number": idx,
                "text": cleaned,
                "word_count": words,
                "char_count": chars,
            })
            total_chars += chars
            total_words += words
        extractor = "pymupdf"
        extracted = True
    except InputValidationError:
        raise
    except Exception as e:
        logger.debug("PyMuPDF extraction not used: %s", e)

    # 2. Try pdfplumber if fitz not available
    if not extracted:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                num_pages = len(pdf.pages)
                if num_pages == 0:
                    raise InputValidationError("pdf_empty", "The uploaded PDF contains no pages.", 400)
                for idx, page in enumerate(pdf.pages, start=1):
                    raw_text = page.extract_text() or ""
                    cleaned = re.sub(r"\r\n", "\n", raw_text)
                    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
                    words = len(cleaned.split()) if cleaned else 0
                    chars = len(cleaned)
                    pages.append({
                        "page_number": idx,
                        "text": cleaned,
                        "word_count": words,
                        "char_count": chars,
                    })
                    total_chars += chars
                    total_words += words
                extractor = "pdfplumber"
                extracted = True
        except InputValidationError:
            raise
        except Exception as e:
            logger.debug("pdfplumber extraction not used: %s", e)

    # 3. Standard fallback: pypdf
    if not extracted:
        try:
            stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(stream)
        except Exception as exc:
            logger.warning("Failed to parse PDF stream: %s", exc)
            raise InputValidationError("pdf_invalid", f"Invalid or corrupted PDF file: {exc}", 400) from exc

        if reader.is_encrypted:
            raise InputValidationError(
                "pdf_encrypted",
                "This PDF is password-protected or encrypted. Please upload an unprotected document.",
                400,
            )

        num_pages = len(reader.pages)
        if num_pages == 0:
            raise InputValidationError("pdf_empty", "The uploaded PDF contains no pages.", 400)

        for idx, page in enumerate(reader.pages, start=1):
            try:
                raw_text = page.extract_text() or ""
            except Exception as e:
                logger.warning("Error extracting text on page %d: %s", idx, e)
                raw_text = ""

            cleaned = re.sub(r"\r\n", "\n", raw_text)
            cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
            words = len(cleaned.split()) if cleaned else 0
            chars = len(cleaned)

            pages.append({
                "page_number": idx,
                "text": cleaned,
                "word_count": words,
                "char_count": chars,
            })
            total_chars += chars
            total_words += words
        extractor = "pypdf"

    has_text = total_words > 15
    meta = {
        "filename": filename,
        "page_count": num_pages,
        "total_words": total_words,
        "total_characters": total_chars,
        "has_text": has_text,
        "file_size_bytes": len(pdf_bytes),
        "extractor": extractor,
    }

    return pages, meta


# =========================================================================
# 3. Categorized Specification Extraction (10 Domains)
# =========================================================================

def _extract_section_blocks(pages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Parse structural content into technical categories with source page tags."""
    categories: Dict[str, List[Dict[str, Any]]] = {
        "overview": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "architecture": [],
        "modules": [],
        "tech_stack": [],
        "api_integrations": [],
        "database": [],
        "performance": [],
        "security": [],
        "constraints": [],
    }

    keywords_map = {
        "functional_requirements": [
            r"functional requirement", r"feature", r"user story", r"workflow",
            r"user shall", r"system shall", r"must provide", r"shall allow", r"REQ-\d+", r"FR-\d+",
            r"use case", r"actor", r"functional specification"
        ],
        "non_functional_requirements": [
            r"non-functional", r"nfr", r"reliability", r"availability", r"scalability",
            r"maintainability", r"disaster recovery", r"sla", r"uptime", r"durability"
        ],
        "architecture": [
            r"architecture", r"system design", r"data flow", r"microservice",
            r"monolith", r"client-server", r"pipeline", r"component diagram", r"layers",
            r"c4 model", r"high-level architecture", r"subsystem"
        ],
        "modules": [
            r"module", r"subsystem", r"service", r"worker", r"frontend", r"backend",
            r"controller", r"gateway", r"handler", r"interface", r"package", r"class"
        ],
        "tech_stack": [
            r"technology stack", r"tech stack", r"framework", r"python", r"javascript",
            r"typescript", r"react", r"fastapi", r"node", r"docker", r"kubernetes", r"redis",
            r"golang", r"java", r"c#", r"rust", r"postgresql", r"mongodb"
        ],
        "api_integrations": [
            r"api", r"rest", r"graphql", r"endpoint", r"webhook", r"http", r"json",
            r"grpc", r"integration", r"oauth", r"jwt", r"post /", r"get /"
        ],
        "database": [
            r"database", r"schema", r"table", r"sql", r"postgres", r"mysql", r"sqlite",
            r"mongodb", r"nosql", r"query", r"migration", r"data model", r"foreign key",
            r"entity relationship", r"erd"
        ],
        "performance": [
            r"performance", r"latency", r"throughput", r"response time", r"concurrency",
            r"benchmark", r"load", r"caching", r"qps", r"rpm", r"millisecond"
        ],
        "security": [
            r"security", r"authentication", r"authorization", r"encryption", r"ssl", r"tls",
            r"vulnerability", r"sanitize", r"rbac", r"xss", r"csrf", r"secret", r"token",
            r"compliance", r"gdpr", r"hipaa"
        ],
        "constraints": [
            r"constraint", r"dependency", r"limitation", r"hardware", r"compliance",
            r"standard", r"prerequisite", r"browser support", r"os requirement", r"deployment"
        ],
    }

    header_pattern = re.compile(r'^(?:\d+(?:\.\d+)*\.?\s+[A-Z]|(?:REQ|FR|NFR|SEC|ARCH|API|DB)-\d+|[-*•]\s+)')

    for page in pages:
        p_num = page["page_number"]
        lines = page["text"].split("\n")

        current_para = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_para:
                    block = " ".join(current_para)
                    _classify_block(block, p_num, categories, keywords_map)
                    current_para = []
                continue
            if header_pattern.match(line_str) and current_para:
                block = " ".join(current_para)
                _classify_block(block, p_num, categories, keywords_map)
                current_para = [line_str]
            else:
                current_para.append(line_str)

        if current_para:
            block = " ".join(current_para)
            _classify_block(block, p_num, categories, keywords_map)

    # Ensure overview has context if empty
    if not categories["overview"] and pages:
        first_page_text = pages[0]["text"][:600]
        if first_page_text:
            categories["overview"].append({
                "title": "Document Introduction & Scope",
                "text": first_page_text,
                "page": 1,
                "type": "Explicit",
            })

    return categories


def _classify_block(
    block: str,
    page_num: int,
    categories: Dict[str, List[Dict[str, Any]]],
    keywords_map: Dict[str, List[str]]
) -> None:
    if len(block) < 20:
        return

    block_lower = block.lower()
    first_chunk = block[:120].lower()

    # Priority 1: Check section headings and title prefixes
    header_rules = [
        ("security", [r"security", r"compliance", r"authentication", r"authorization", r"sec-\d+"]),
        ("performance", [r"performance", r"sla", r"latency", r"throughput", r"bandwidth"]),
        ("non_functional_requirements", [r"non-functional", r"nfr", r"nfr-\d+"]),
        ("functional_requirements", [r"functional requirement", r"features", r"req-\d+", r"fr-\d+", r"use case"]),
        ("database", [r"database", r"data model", r"schema", r"persistence", r"data dictionary"]),
        ("architecture", [r"architecture", r"modular design", r"system design", r"c4 model"]),
        ("tech_stack", [r"technology stack", r"tech stack", r"frameworks"]),
        ("constraints", [r"constraint", r"dependencies", r"deployment strategy"]),
        ("api_integrations", [r"api specification", r"rest api", r"endpoints", r"webhooks", r"graphql"]),
    ]

    matched = False
    for target_cat, keywords in header_rules:
        for kw in keywords:
            if re.search(r"\b" + kw + r"\b", first_chunk):
                title = block.split(". ")[0][:80]
                categories[target_cat].append({
                    "title": title,
                    "text": block,
                    "page": page_num,
                    "type": "Explicit",
                    "keyword_matched": kw,
                })
                matched = True
                break
        if matched:
            break

    # Priority 2: General keyword search if heading didn't match
    if not matched:
        for cat_name, patterns in keywords_map.items():
            for pat in patterns:
                if re.search(r"\b" + pat + r"\b", block_lower):
                    title = block.split(". ")[0][:80]
                    categories[cat_name].append({
                        "title": title,
                        "text": block,
                        "page": page_num,
                        "type": "Explicit",
                        "keyword_matched": pat,
                    })
                    matched = True
                    break
            if matched:
                break


# =========================================================================
# 4. Traceability Matrix Builder (FR, NFR, SEC, ARCH, DB, API)
# =========================================================================

def _build_traceability_matrix(categories: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Build a verifiable traceability matrix connecting requirements to pages."""
    matrix: List[Dict[str, Any]] = []
    counter = 1

    # Functional Requirements
    for item in categories.get("functional_requirements", []):
        matrix.append({
            "req_id": f"FR-{counter:03d}",
            "category": "Functional",
            "description": item["text"][:240],
            "priority": "High" if counter <= 3 else "Medium",
            "source_page": item["page"],
            "status": "Covered" if len(item["text"]) > 60 else "Ambiguous",
        })
        counter += 1

    # Non-Functional Requirements
    nfr_counter = 1
    for item in categories.get("non_functional_requirements", []):
        matrix.append({
            "req_id": f"NFR-{nfr_counter:03d}",
            "category": "Non-Functional",
            "description": item["text"][:240],
            "priority": "High" if any(k in item["text"].lower() for k in ["latency", "uptime", "security", "sla"]) else "Medium",
            "source_page": item["page"],
            "status": "Covered" if any(c in item["text"] for c in ["%", "ms", "s", "qps", "99"]) else "Needs Benchmark",
        })
        nfr_counter += 1

    # Security Requirements
    sec_counter = 1
    for item in categories.get("security", []):
        matrix.append({
            "req_id": f"SEC-{sec_counter:03d}",
            "category": "Security",
            "description": item["text"][:240],
            "priority": "High",
            "source_page": item["page"],
            "status": "Covered",
        })
        sec_counter += 1

    # Architecture & API / DB Requirements if matrix is sparse
    if len(matrix) < 4:
        for cat in ["architecture", "database", "api_integrations", "performance"]:
            for item in categories.get(cat, [])[:2]:
                matrix.append({
                    "req_id": f"ARCH-{len(matrix)+1:03d}",
                    "category": cat.replace("_", " ").title(),
                    "description": item["text"][:240],
                    "priority": "Medium",
                    "source_page": item["page"],
                    "status": "Covered",
                })

    return matrix


# =========================================================================
# 5. Risk, Severity & Gap Analysis
# =========================================================================

def _evaluate_risks_and_findings(
    categories: Dict[str, List[Dict[str, Any]]],
    meta: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Classify technical risks into Critical, Warning, Informational, and Passed."""
    findings: List[Dict[str, Any]] = []

    has_security = len(categories.get("security", [])) > 0
    has_perf = len(categories.get("performance", [])) > 0
    has_db = len(categories.get("database", [])) > 0

    # 1. Security Risk
    if not has_security:
        findings.append({
            "title": "Missing Security & Authentication Specification",
            "severity": "Critical",
            "source": "spec_analyzer",
            "source_page": "N/A",
            "description": "The specification does not define user authentication, authorization boundaries, RBAC, or data encryption standards.",
            "why_it_matters": "Systems designed without explicit security and authorization controls are susceptible to unauthorized access, data exfiltration, and privilege escalation vulnerabilities.",
            "recommended_action": "Add an explicit Security section defining identity providers (e.g. OAuth2/OIDC, JWT), encryption at rest/in-transit, and role-based permissions.",
        })
    else:
        sec_text = " ".join(s["text"].lower() for s in categories["security"])
        if not any(k in sec_text for k in ["oauth", "jwt", "token", "password", "hash", "argon2", "bcrypt"]):
            findings.append({
                "title": "Abstract Authentication Mechanism",
                "severity": "Warning",
                "source": "spec_analyzer",
                "source_page": str(categories["security"][0]["page"]),
                "description": "Security is mentioned, but exact cryptographic algorithms, token lifecycles, and credential storage methods are omitted.",
                "why_it_matters": "Ambiguous authentication specifications leave engineers without guidance on password hashing cost factors or token refresh mechanisms.",
                "recommended_action": "Specify token expiration windows, refresh token rotation policies, and password hashing standards.",
            })

    # 2. Performance & SLA Evaluation
    if not has_perf:
        findings.append({
            "title": "Missing Performance SLAs & Latency Budgets",
            "severity": "Warning",
            "source": "spec_analyzer",
            "source_page": "N/A",
            "description": "No measurable latency budgets (e.g. P99 < 250ms), concurrency limits, or throughput requirements are specified.",
            "why_it_matters": "Without measurable performance benchmarks, acceptance testing cannot validate whether the system scales adequately under production load.",
            "recommended_action": "Define quantified service level objectives (SLOs) for API response times and maximum concurrent active users.",
        })
    else:
        perf_text = " ".join(p["text"] for p in categories["performance"])
        if not re.search(r"\d+\s*(?:ms|second|qps|rpm|%)", perf_text, re.IGNORECASE):
            findings.append({
                "title": "Non-Measurable Performance Descriptions",
                "severity": "Warning",
                "source": "spec_analyzer",
                "source_page": str(categories["performance"][0]["page"]),
                "description": "Performance statements use subjective terms (e.g. 'fast', 'scalable', 'efficient') rather than numeric targets.",
                "why_it_matters": "Subjective performance criteria cannot be verified during automated load testing or QA sign-off.",
                "recommended_action": "Replace qualitative statements with concrete numbers: target P95 latency (ms) and peak query throughput (QPS).",
            })

    # 3. Database Schema
    if not has_db:
        findings.append({
            "title": "Omitted Database Persistence Specification",
            "severity": "Informational",
            "source": "spec_analyzer",
            "source_page": "N/A",
            "description": "The specification does not elaborate on persistence schemas, database engine choice, or indexing strategies.",
            "why_it_matters": "Unspecified database models lead to ad-hoc table schemas, missing relational integrity constraints, and unindexed queries.",
            "recommended_action": "Document entity relationship diagrams (ERD), primary/foreign keys, and data retention policies.",
        })

    # 4. Error Handling & Recovery
    full_text = " ".join(p.get("text", "") for cat in categories.values() for p in cat).lower()
    if not any(k in full_text for k in ["error handling", "exception", "retry", "fallback", "circuit breaker", "timeout"]):
        findings.append({
            "title": "Unspecified Error Handling & Resiliency Strategy",
            "severity": "Warning",
            "source": "spec_analyzer",
            "source_page": "N/A",
            "description": "The document lacks guidance on how services handle network timeouts, third-party API outages, and client input validation errors.",
            "why_it_matters": "Missing error handling specifications often result in unhandled exceptions, cascaded failures, and poor user feedback during partial outages.",
            "recommended_action": "Define standard HTTP error response schemas (RFC 7807), retry backoff algorithms, and timeout parameters.",
        })

    # 5. Passed Checks
    if meta["page_count"] > 0:
        findings.append({
            "title": "Document Ingestion & Multi-Page Traversal",
            "severity": "Passed",
            "source": "pdf_engine",
            "source_page": f"Pages 1-{meta['page_count']}",
            "description": f"Successfully parsed {meta['page_count']} page(s) and extracted {meta['total_words']} words of technical content.",
            "why_it_matters": "Verifies document readability, format integrity, and complete page coverage.",
            "recommended_action": "No action required; document parsed cleanly.",
        })

    if categories.get("architecture") or categories.get("modules"):
        first_arch_p = (categories.get("architecture") or categories.get("modules"))[0]["page"]
        findings.append({
            "title": "System Architecture & Modular Decomposition",
            "severity": "Passed",
            "source": "spec_analyzer",
            "source_page": f"Page {first_arch_p}",
            "description": "Identified architectural components and functional modular boundaries.",
            "why_it_matters": "Clear architectural separation allows independent module development, testing, and deployment.",
            "recommended_action": "Maintain architectural boundaries during implementation.",
        })

    return findings


def _detect_missing_gaps(
    categories: Dict[str, List[Dict[str, Any]]],
    meta: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Detect missing, vague, or insufficiently defined technical requirements."""
    gaps: List[Dict[str, Any]] = []
    full_text = " ".join(p.get("text", "") for cat in categories.values() for p in cat).lower()

    if not any(k in full_text for k in ["acceptance criteria", "definition of done", "verification criteria", "given when then"]):
        gaps.append({
            "issue": "Missing Measurable Acceptance Criteria",
            "severity": "Warning",
            "explanation": "Requirements outline desired behaviors but omit verifiable 'Given/When/Then' acceptance tests.",
            "suggested_improvement": "Add concrete acceptance criteria to each functional requirement detailing expected inputs and outputs.",
            "related_requirement": "Functional Requirements",
            "source_page": "Global",
        })

    if not categories.get("security"):
        gaps.append({
            "issue": "Undefined Authentication & Authorization Protocols",
            "severity": "Critical",
            "explanation": "The specification fails to define user identity verification, permission matrix, or API token issuance.",
            "suggested_improvement": "Detail the authentication workflow (e.g. JWT with short TTL, OAuth2 authorization code flow) and define RBAC roles.",
            "related_requirement": "Security Specification",
            "source_page": "Global",
        })

    if not any(k in full_text for k in ["backup", "disaster recovery", "failover", "rto", "rpo", "replication"]):
        gaps.append({
            "issue": "Omitted Backup & Disaster Recovery (DR) Plan",
            "severity": "Warning",
            "explanation": "No Recovery Time Objective (RTO) or Recovery Point Objective (RPO) is established for persistent databases.",
            "suggested_improvement": "Define daily snapshot schedules, multi-region replication, and automated disaster failover procedures.",
            "related_requirement": "Database & Infrastructure",
            "source_page": "Global",
        })

    if not any(k in full_text for k in ["logging", "monitoring", "telemetry", "prometheus", "opentelemetry", "datadog", "grafana", "health check"]):
        gaps.append({
            "issue": "Missing Observability, Logging, & Health Checks",
            "severity": "Informational",
            "explanation": "The specification does not mention structured audit logging, metrics collection, or service health check endpoints.",
            "suggested_improvement": "Specify standardized JSON log formatting, Prometheus metrics export, and `/health` probe endpoints.",
            "related_requirement": "Operations & Deployment",
            "source_page": "Global",
        })

    if not any(k in full_text for k in ["ci/cd", "pipeline", "docker", "kubernetes", "deploy", "staging", "production"]):
        gaps.append({
            "issue": "Undefined Deployment Targets & CI/CD Strategy",
            "severity": "Informational",
            "explanation": "Hosting environments (cloud provider, container runtime, Kubernetes cluster) and automation workflows are not defined.",
            "suggested_improvement": "Specify Dockerfile containerization requirements, staging/production environments, and automated pull-request validation pipelines.",
            "related_requirement": "DevOps & Infrastructure",
            "source_page": "Global",
        })

    return gaps


# =========================================================================
# 6. Quality Score Calculation (0-100)
# =========================================================================

def _calculate_quality_score(
    categories: Dict[str, List[Dict[str, Any]]],
    findings: List[Dict[str, Any]],
    gaps: List[Dict[str, Any]],
    meta: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate an objective 0-100 Specification Quality Score across 8 dimensions."""
    scores: Dict[str, int] = {}

    # 1. Completeness
    c_sections = [
        len(categories.get("overview", [])) > 0,
        len(categories.get("functional_requirements", [])) > 0,
        len(categories.get("architecture", [])) > 0 or len(categories.get("modules", [])) > 0,
        len(categories.get("tech_stack", [])) > 0,
        len(categories.get("security", [])) > 0,
        len(categories.get("database", [])) > 0 or len(categories.get("api_integrations", [])) > 0,
    ]
    scores["completeness"] = int(round((sum(c_sections) / len(c_sections)) * 100))

    # 2. Clarity
    full_text = " ".join(p.get("text", "") for cat in categories.values() for p in cat).lower()
    ambiguous_words = ["etc", "tbd", "todo", "fast", "easy", "soon", "appropriate", "optimal"]
    amb_count = sum(len(re.findall(r"\b" + w + r"\b", full_text)) for w in ambiguous_words)
    scores["clarity"] = max(40, min(100, 100 - (amb_count * 5)))

    # 3. Consistency
    scores["consistency"] = 88 if scores["completeness"] > 60 else 72

    # 4. Security
    if len(categories.get("security", [])) >= 2:
        scores["security"] = 92
    elif len(categories.get("security", [])) == 1:
        scores["security"] = 75
    else:
        scores["security"] = 38

    # 5. Performance
    if len(categories.get("performance", [])) > 0:
        perf_text = " ".join(p["text"] for p in categories["performance"])
        has_numbers = bool(re.search(r"\d+\s*(?:ms|second|qps|rpm|%)", perf_text, re.IGNORECASE))
        scores["performance"] = 88 if has_numbers else 65
    else:
        scores["performance"] = 45

    # 6. Architecture
    if len(categories.get("architecture", [])) > 0 and len(categories.get("modules", [])) > 0:
        scores["architecture"] = 92
    elif len(categories.get("architecture", [])) > 0 or len(categories.get("modules", [])) > 0:
        scores["architecture"] = 78
    else:
        scores["architecture"] = 50

    # 7. Testability
    reqs = categories.get("functional_requirements", [])
    if reqs:
        scores["testability"] = min(95, 65 + (len(reqs) * 5))
    else:
        scores["testability"] = 52

    # 8. Constraints & Dependencies
    if len(categories.get("constraints", [])) > 0:
        scores["constraints"] = 85
    else:
        scores["constraints"] = 60

    weights = {
        "completeness": 0.20,
        "clarity": 0.15,
        "consistency": 0.10,
        "security": 0.15,
        "performance": 0.10,
        "architecture": 0.15,
        "testability": 0.10,
        "constraints": 0.05,
    }
    overall = sum(scores[k] * weights[k] for k in weights)

    crit_count = sum(1 for f in findings if f["severity"] == "Critical")
    warn_count = sum(1 for f in findings if f["severity"] == "Warning")
    overall -= (crit_count * 12) + (warn_count * 3)

    final_score = int(max(25, min(98, round(overall))))

    if final_score >= 85:
        level = "Excellent"
        level_desc = "Production-grade technical specification with high architectural clarity and thorough requirement coverage."
    elif final_score >= 70:
        level = "Good"
        level_desc = "Well-structured specification suitable for implementation with minor gaps in operational SLOs or security."
    elif final_score >= 50:
        level = "Needs Improvement"
        level_desc = "Fundamental concepts defined, but missing key acceptance criteria, security specifications, or performance budgets."
    else:
        level = "Poor"
        level_desc = "High degree of ambiguity, missing architectural boundaries, and insufficient technical specifications."

    strengths = []
    if scores["completeness"] >= 75:
        strengths.append("Broad coverage of functional modules and core system overview.")
    if scores["architecture"] >= 75:
        strengths.append("Clear component boundaries and modular architectural separation.")
    if scores["security"] >= 70:
        strengths.append("Proactive attention to security boundaries and access permissions.")
    if not strengths:
        strengths.append(f"Successfully processed {meta['page_count']} pages of technical documentation.")

    weaknesses = []
    if scores["security"] < 60:
        weaknesses.append("Insufficiently specified authentication protocols and data encryption standards.")
    if scores["performance"] < 60:
        weaknesses.append("Lack of quantified performance budgets, response time SLOs, or throughput benchmarks.")
    if len(gaps) > 2:
        weaknesses.append(f"Identified {len(gaps)} requirement gaps requiring clarification before development sign-off.")
    if not weaknesses:
        weaknesses.append("Edge-case error handling and automated disaster recovery failover can be further detailed.")

    return {
        "overall_score": final_score,
        "quality_level": level,
        "description": level_desc,
        "category_scores": scores,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


# =========================================================================
# 7. Gemini AI Integration & Grounded Synthesis
# =========================================================================

def _call_gemini_pdf_review(
    full_text: str,
    doc_type_label: str,
    meta: Dict[str, Any],
    api_key: str,
    model: str = "gemini-2.5-flash"
) -> Optional[Dict[str, Any]]:
    """Query Gemini AI for architectural review and recommendations distinguishing facts vs AI insights."""
    if not api_key:
        return None

    prompt = f"""You are a Principal Software Architect reviewing a {doc_type_label}.
Analyze this actual technical document text (no hallucinations, no fabricated facts).
Preserve exact quotes or source details where available.

Document Excerpt ({meta['page_count']} pages, {meta['total_words']} words):
```
{full_text[:12000]}
```

Respond with ONLY valid JSON (no markdown fences, no formatting outside JSON):
{{
  "executive_summary": "Professional 3-4 sentence architectural executive summary.",
  "extracted_facts": [
    "Explicit fact 1 stated directly in document",
    "Explicit fact 2 stated directly in document",
    "Explicit fact 3 stated directly in document"
  ],
  "ai_architecture_evaluation": "2-3 sentence AI evaluation of architectural patterns, modularity, and cohesion.",
  "security_assessment": "Concrete evaluation of security boundaries, encryption, and authentication protocols.",
  "clarity_rating": "High",
  "recommendations": [
    {{
      "priority": "High",
      "category": "Architecture",
      "title": "Actionable Recommendation Title",
      "detail": "Clear, technical guidance on how to implement this."
    }}
  ],
  "conclusion": "Final professional conclusion assessing implementation feasibility and readiness."
}}
"""
    models = [model, "gemini-2.5-flash", "gemini-1.5-flash"]
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidate = data.get("candidates", [{}])[0]
                    text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                    raw = text.strip()
                    if raw.startswith("```"):
                        raw = re.sub(r"^```(?:json)?\s*", "", raw)
                        raw = re.sub(r"\s*```$", "", raw)
                    return json.loads(raw)
        except Exception as e:
            logger.debug("Gemini call for model %s failed: %s", m, e)
            continue

    return None


def _generate_ai_insights(
    categories: Dict[str, List[Dict[str, Any]]],
    meta: Dict[str, Any],
    quality_score: Dict[str, Any],
    doc_type_label: str,
    full_text: str,
    settings: Settings
) -> Dict[str, Any]:
    """Synthesize executive technical review and actionable recommendations."""
    overview_text = ""
    if categories.get("overview"):
        overview_text = categories["overview"][0]["text"]
    elif categories.get("functional_requirements"):
        overview_text = categories["functional_requirements"][0]["text"]

    score_num = quality_score["overall_score"]
    level_str = quality_score["quality_level"]

    # Try Gemini AI review
    api_key = (
        getattr(settings, "ai_api_key", "")
        or os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("TSA_AI_API_KEY", "")
    )
    ai_model = getattr(settings, "ai_model", "") or "gemini-2.5-flash"
    gemini_data = None
    if api_key:
        try:
            gemini_data = _call_gemini_pdf_review(full_text, doc_type_label, meta, api_key, ai_model)
        except Exception as exc:
            logger.warning("Gemini AI PDF review failed, falling back to grounded synthesizer: %s", exc)

    # Base extracted facts
    extracted_facts = [
        f"Document Classification: Verified as {doc_type_label} spanning {meta['page_count']} page(s) and {meta['total_words']} words.",
        f"Extracted Specifications: {sum(len(v) for v in categories.values())} specification blocks across {sum(1 for v in categories.values() if len(v) > 0)} technical categories.",
    ]
    if categories.get("tech_stack"):
        stack_str = ", ".join(item["title"] for item in categories["tech_stack"][:3])
        extracted_facts.append(f"Declared Tech Stack: {stack_str}")
    if categories.get("functional_requirements"):
        extracted_facts.append(f"Functional Requirements: {len(categories['functional_requirements'])} discrete functional requirement(s) extracted.")
    if categories.get("security"):
        sec_sample = categories["security"][0]["title"]
        extracted_facts.append(f"Security Policy: Document specifies {sec_sample}.")

    proj_overview = (
        (gemini_data and gemini_data.get("project_overview"))
        or (overview_text if len(overview_text) > 40 else f"This {doc_type_label} defines an enterprise software system spanning {meta['page_count']} page(s) and {meta['total_words']} words.")
    )

    if gemini_data and gemini_data.get("executive_summary"):
        exec_summary = gemini_data["executive_summary"]
        if gemini_data.get("extracted_facts"):
            extracted_facts = gemini_data["extracted_facts"]
        arch_eval = gemini_data.get("ai_architecture_evaluation", "Modular decomposition aligns with enterprise engineering principles.")
        sec_eval = gemini_data.get("security_assessment", "Security specifications address foundational protocols.")
        clarity_rating = gemini_data.get("clarity_rating", "High")
        conclusion = gemini_data.get("conclusion", f"The {doc_type_label} achieves a Quality Score of {score_num}/100 ({level_str}) and is well-grounded for implementation.")
        recommendations = gemini_data.get("recommendations") or []
        ai_engine = "Gemini AI Multi-Agent Specification Review"
    else:
        exec_summary = (
            f"This {doc_type_label} defines a software system spanning {meta['page_count']} page(s) and {meta['total_words']} words. "
            f"The specification scored {score_num}/100 ({level_str}) on the Technical Specification Quality Index. "
            + (f"Document Scope: {overview_text[:280]}... " if len(overview_text) > 40 else "The specification focuses on functional workflow definitions and technical module integrations. ")
            + f"Core architectural components demonstrate structured decomposition, with {len(categories.get('functional_requirements', []))} functional feature(s) and {len(categories.get('non_functional_requirements', []))} non-functional constraint(s) extracted."
        )
        arch_eval = f"Architectural components show clear modular boundaries across {len(categories.get('architecture', []))} architectural blocks and {len(categories.get('modules', []))} service modules."
        sec_eval = f"Security review identified {len(categories.get('security', []))} explicit security specification blocks."
        clarity_rating = "High" if quality_score["category_scores"]["clarity"] >= 80 else ("Moderate" if quality_score["category_scores"]["clarity"] >= 60 else "Low")
        conclusion = f"The {doc_type_label} achieves a Quality Score of {score_num}/100 ({level_str}). It provides a grounded foundation for sprint planning and implementation once the identified gaps are addressed."
        recommendations = [
            {
                "priority": "High",
                "category": "Requirements Engineering",
                "title": "Establish Quantified Acceptance Criteria",
                "detail": "Attach verifiable Given/When/Then acceptance criteria to each functional specification to streamline QA test automation.",
            },
            {
                "priority": "High",
                "category": "Security Engineering",
                "title": "Document Authentication & Secret Management Protocols",
                "detail": "Specify token lifecycles, hashing algorithms (Argon2id/bcrypt), and vault/KMS integration for environment secrets.",
            },
            {
                "priority": "Medium",
                "category": "Performance & SRE",
                "title": "Define Quantified Latency & Throughput Budgets",
                "detail": "Specify P95 and P99 latency budgets (e.g. < 200ms) and establish continuous load testing targets in the CI/CD pipeline.",
            },
            {
                "priority": "Medium",
                "category": "Data Architecture",
                "title": "Formalize Data Schema & Migration Governance",
                "detail": "Provide entity relationship diagrams (ERD) with primary/foreign keys and automated migration versioning policies.",
            },
        ]
        ai_engine = "TechSpecAnalyser Deterministic Specification Intelligence"

    return {
        "model": ai_engine,
        "executive_summary": exec_summary,
        "project_overview": proj_overview,
        "extracted_facts": extracted_facts,
        "key_observations": extracted_facts,
        "ai_architecture_evaluation": arch_eval,
        "security_assessment": sec_eval,
        "clarity_rating": clarity_rating,
        "clarity_assessment": {
            "rating": clarity_rating,
            "detail": f"Clarity rating is {clarity_rating} based on technical vocabulary and clear requirement structures."
        },
        "recommendations": recommendations,
        "conclusion": conclusion,
    }


# =========================================================================
# 8. Main Analysis Orchestrator
# =========================================================================

def process_and_analyze_pdf(
    pdf_bytes: bytes,
    filename: str,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """Complete end-to-end processing and AI analysis of a technical specification PDF."""
    if settings is None:
        settings = get_settings()

    analysis_id = f"A-pdf-{uuid.uuid4().hex[:12]}"
    created_at = _utcnow()

    # 1. Extract Pages & Text
    pages, meta = extract_pdf_pages(pdf_bytes, filename)
    full_text = " ".join(p["text"] for p in pages)

    # 2. Document Domain & Relevance Classification
    is_supported, doc_type, doc_type_label, doc_type_icon, rejection_reason = classify_document_domain_and_type(
        full_text, meta
    )

    # If the document is non-technical or unrelated to software engineering, return unsupported state
    if not is_supported:
        completed_at = _utcnow()
        sample_preview = full_text[:400] + ("..." if len(full_text) > 400 else "")
        return {
            "analysis_id": analysis_id,
            "input_type": "pdf",
            "input_name": filename,
            "status": "unsupported",
            "is_software_engineering_doc": False,
            "document_type": doc_type,
            "document_type_label": doc_type_label,
            "document_type_icon": doc_type_icon,
            "rejection_reason": rejection_reason,
            "content_sample": sample_preview,
            "created_at": created_at,
            "completed_at": completed_at,
            "document_metadata": meta,
            "quality_score": {
                "overall_score": 0,
                "quality_level": "Unsupported",
                "description": rejection_reason,
                "category_scores": {},
                "strengths": [],
                "weaknesses": ["Non-software/engineering document detected."],
            },
            "extracted_specifications": {},
            "traceability_matrix": [],
            "findings": [],
            "missing_gaps": [],
            "ai_insights": {
                "model": "TechSpecAnalyser Domain Classifier",
                "executive_summary": rejection_reason,
                "extracted_facts": [f"Document text contains {meta['total_words']} words, but does not match software engineering patterns."],
                "ai_architecture_evaluation": "N/A - Non-technical document.",
                "security_assessment": "N/A",
                "clarity_rating": "N/A",
                "recommendations": [
                    {
                        "priority": "High",
                        "category": "Document Selection",
                        "title": "Upload a Software Engineering Specification",
                        "detail": "Please upload a Software Requirements Specification (SRS), Software Design Document (SDD), Architecture Document, API Specification, or Database Design Document."
                    }
                ],
                "conclusion": "Analysis halted to avoid generating misleading technical ratings on unrelated content."
            },
            "sections": {},
            "metrics": {
                "total_findings": 0,
                "severity_counts": {"Critical": 0, "Warning": 0, "High": 0, "Informational": 0, "Passed": 0},
                "quality_score": 0,
                "page_count": meta["page_count"],
                "word_count": meta["total_words"],
                "requirement_count": 0,
                "gap_count": 0,
            },
        }

    # 3. Extract Structural Categories (10 Domains)
    categories = _extract_section_blocks(pages)

    # 4. Build Traceability Matrix
    traceability = _build_traceability_matrix(categories)

    # 5. Evaluate Risks & Severity Findings
    findings = _evaluate_risks_and_findings(categories, meta)

    # 6. Missing Requirements & Gap Detection
    gaps = _detect_missing_gaps(categories, meta)

    # 7. Calculate 0-100 Quality Score
    quality = _calculate_quality_score(categories, findings, gaps, meta)

    # 8. AI Synthesis & Insights
    ai_insights = _generate_ai_insights(categories, meta, quality, doc_type_label, full_text, settings)

    completed_at = _utcnow()

    # Metrics for database summary
    crit_count = sum(1 for f in findings if f["severity"] == "Critical")
    warn_count = sum(1 for f in findings if f["severity"] == "Warning")
    info_count = sum(1 for f in findings if f["severity"] == "Informational")
    passed_count = sum(1 for f in findings if f["severity"] == "Passed")

    # 9. Organize the 10 Professional Report Sections
    sections = {
        "1_executive_summary": {
            "title": "1. Executive Summary",
            "document_type": doc_type_label,
            "icon": doc_type_icon,
            "summary": ai_insights["executive_summary"],
            "conclusion": ai_insights["conclusion"],
        },
        "2_extracted_specifications": {
            "title": "2. Extracted Technical Specifications",
            "categories": categories,
        },
        "3_requirements_analysis": {
            "title": "3. Functional & Non-Functional Requirements",
            "functional": categories.get("functional_requirements", []),
            "non_functional": categories.get("non_functional_requirements", []),
        },
        "4_architecture_and_tech": {
            "title": "4. Architecture & Technology Analysis",
            "architecture": categories.get("architecture", []),
            "modules": categories.get("modules", []),
            "tech_stack": categories.get("tech_stack", []),
            "ai_evaluation": ai_insights["ai_architecture_evaluation"],
        },
        "5_security_and_risk": {
            "title": "5. Security & Risk Assessment",
            "security_specs": categories.get("security", []),
            "ai_security_evaluation": ai_insights["security_assessment"],
            "findings": findings,
        },
        "6_gap_analysis": {
            "title": "6. Missing Requirements & Gap Analysis",
            "gaps": gaps,
        },
        "7_ai_insights": {
            "title": "7. AI-Generated Insights (Facts vs Recommendations)",
            "model": ai_insights["model"],
            "extracted_facts": ai_insights["extracted_facts"],
            "clarity_rating": ai_insights["clarity_rating"],
            "ai_architecture_evaluation": ai_insights["ai_architecture_evaluation"],
            "security_assessment": ai_insights["security_assessment"],
        },
        "8_quality_score": {
            "title": "8. Specification Quality Scorecard",
            "score": quality["overall_score"],
            "level": quality["quality_level"],
            "description": quality["description"],
            "category_scores": quality["category_scores"],
            "strengths": quality["strengths"],
            "weaknesses": quality["weaknesses"],
        },
        "9_traceability_matrix": {
            "title": "9. Requirement Traceability Matrix",
            "matrix": traceability,
        },
        "10_recommendations_and_conclusion": {
            "title": "10. Recommendations & Engineering Conclusion",
            "recommendations": ai_insights["recommendations"],
            "conclusion": ai_insights["conclusion"],
        },
    }

    result: Dict[str, Any] = {
        "analysis_id": analysis_id,
        "input_type": "pdf",
        "input_name": filename,
        "status": "completed",
        "is_software_engineering_doc": True,
        "document_type": doc_type,
        "document_type_label": doc_type_label,
        "document_type_icon": doc_type_icon,
        "rejection_reason": None,
        "created_at": created_at,
        "completed_at": completed_at,
        "document_metadata": meta,
        "quality_score": quality,
        # Direct user specification sections
        "executive_summary": ai_insights["executive_summary"],
        "project_overview": ai_insights.get("project_overview") or "Software engineering technical specification.",
        "functional_requirements": categories.get("functional_requirements", []),
        "non_functional_requirements": categories.get("non_functional_requirements", []),
        "technical_architecture": {
            "evaluation": ai_insights["ai_architecture_evaluation"],
            "blocks": categories.get("architecture", []),
            "modules": categories.get("modules", []),
        },
        "technology_stack": categories.get("tech_stack", []),
        "security_requirements": {
            "evaluation": ai_insights["security_assessment"],
            "specifications": categories.get("security", []),
        },
        "potential_risks_and_issues": findings,
        "missing_or_ambiguous_requirements": gaps,
        "recommendations": ai_insights.get("recommendations", []),
        "conclusion": ai_insights["conclusion"],
        # Complete structured data models
        "extracted_specifications": categories,
        "traceability_matrix": traceability,
        "findings": findings,
        "missing_gaps": gaps,
        "ai_insights": ai_insights,
        "sections": sections,
        "metrics": {
            "total_findings": len(findings),
            "severity_counts": {
                "Critical": crit_count,
                "Warning": warn_count,
                "High": crit_count,
                "Informational": info_count,
                "Passed": passed_count,
            },
            "quality_score": quality["overall_score"],
            "page_count": meta["page_count"],
            "word_count": meta["total_words"],
            "requirement_count": len(traceability),
            "gap_count": len(gaps),
        },
    }

    return result


# =========================================================================
# 9. Professional ReportLab PDF Report Generator
# =========================================================================

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to draw exact 'Page X of Y' headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 755, "TechSpecAnalyser — Professional Technical Specification Audit")
            self.drawRightString(572, 755, "Confidential Document")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)

        # Running Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.drawString(40, 30, "Generated by TechSpecAnalyser Specification Intelligence")
        self.restoreState()


def generate_analysis_report_pdf(data: Dict[str, Any]) -> bytes:
    """Generate a multi-page, executive ReportLab PDF report containing all 10 analysis sections."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50,
    )
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "RepTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        alignment=0,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "RepSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "RepH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#312E81"),
        spaceBefore=14,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "RepH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "RepBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5,
    )
    cell_style = ParagraphStyle(
        "RepCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )
    cell_bold = ParagraphStyle(
        "RepCellB",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A"),
    )

    story: List[Any] = []

    # Title Banner
    meta = data.get("document_metadata", {})
    doc_type_label = data.get("document_type_label", "Technical Specification")
    story.append(Paragraph(f"<b>Technical Specification Audit Report</b>", title_style))
    story.append(Paragraph(
        f"<b>Document:</b> {data.get('input_name')} | <b>Type:</b> {doc_type_label} | "
        f"<b>Audit ID:</b> {data.get('analysis_id')} | <b>Pages:</b> {meta.get('page_count', 0)} | <b>Date:</b> {data.get('completed_at', '')[:10]}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=10))

    # Quality Scorecard Banner
    qs = data.get("quality_score", {})
    score_val = qs.get("overall_score", 0)
    score_bg = colors.HexColor("#ECFDF5") if score_val >= 80 else (colors.HexColor("#FFFBEB") if score_val >= 50 else colors.HexColor("#FEF2F2"))
    score_border = colors.HexColor("#10B981") if score_val >= 80 else (colors.HexColor("#F59E0B") if score_val >= 50 else colors.HexColor("#EF4444"))

    score_card_data = [
        [
            Paragraph(f"<font size=24><b>{score_val}/100</b></font><br/><b>{qs.get('quality_level', 'N/A')}</b>", ParagraphStyle('Score', parent=cell_bold, alignment=1)),
            Paragraph(f"<b>Executive Quality Appraisal:</b><br/>{qs.get('description', '')}", body_style),
        ]
    ]
    st = Table(score_card_data, colWidths=[130, 402])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), score_bg),
        ("BOX", (0, 0), (-1, -1), 1, score_border),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(st)
    story.append(Spacer(1, 8))

    # Section 1: Executive Summary
    ai = data.get("ai_insights", {})
    specs = data.get("extracted_specifications", {})
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(data.get("executive_summary") or ai.get("executive_summary", "Technical audit completed successfully."), body_style))

    # Section 2: Project Overview
    story.append(Paragraph("2. Project Overview & Scope", h1_style))
    proj_ov = data.get("project_overview") or ai.get("project_overview", "")
    story.append(Paragraph(proj_ov, body_style))

    # Section 3: Functional Requirements
    story.append(Paragraph("3. Functional Requirements", h1_style))
    fr_list = specs.get("functional_requirements", [])
    if fr_list:
        fr_rows = [
            [Paragraph("<b>Req ID / Title</b>", cell_bold), Paragraph("<b>Functional Specification</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold)]
        ]
        for idx, fr in enumerate(fr_list[:8], start=1):
            fr_rows.append([
                Paragraph(f"<b>FR-{idx:03d}</b><br/>{fr.get('title', '')[:40]}", cell_style),
                Paragraph(fr.get("text", "")[:150], cell_style),
                Paragraph(f"Page {fr.get('page', 1)}", cell_style),
            ])
        fr_table = Table(fr_rows, colWidths=[100, 362, 70])
        fr_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(fr_table)
    else:
        story.append(Paragraph("No functional requirement items isolated.", body_style))
    story.append(Spacer(1, 6))

    # Section 4: Non-Functional Requirements
    story.append(Paragraph("4. Non-Functional Requirements & Quality Attributes", h1_style))
    nfr_list = specs.get("non_functional_requirements", [])
    if nfr_list:
        nfr_rows = [
            [Paragraph("<b>Req ID / Title</b>", cell_bold), Paragraph("<b>Quality Attribute / SLA</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold)]
        ]
        for idx, nfr in enumerate(nfr_list[:6], start=1):
            nfr_rows.append([
                Paragraph(f"<b>NFR-{idx:03d}</b><br/>{nfr.get('title', '')[:40]}", cell_style),
                Paragraph(nfr.get("text", "")[:150], cell_style),
                Paragraph(f"Page {nfr.get('page', 1)}", cell_style),
            ])
        nfr_table = Table(nfr_rows, colWidths=[100, 362, 70])
        nfr_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(nfr_table)
    else:
        story.append(Paragraph("No non-functional SLAs isolated.", body_style))
    story.append(Spacer(1, 6))

    # Section 5: Technical Architecture
    story.append(Paragraph("5. Technical Architecture & Modularity", h1_style))
    story.append(Paragraph(f"<b>Architectural Appraisal:</b> {ai.get('ai_architecture_evaluation', 'Architecture demonstrates modular decomposition.')}", body_style))
    arch_items = specs.get("architecture", []) + specs.get("modules", [])
    if arch_items:
        arch_rows = [
            [Paragraph("<b>Component / Module</b>", cell_bold), Paragraph("<b>Architectural Responsibility</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold)]
        ]
        for a in arch_items[:6]:
            arch_rows.append([
                Paragraph(a.get("title", "")[:45], cell_bold),
                Paragraph(a.get("text", "")[:150], cell_style),
                Paragraph(f"Page {a.get('page', 1)}", cell_style),
            ])
        at = Table(arch_rows, colWidths=[130, 332, 70])
        at.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(at)
    story.append(Spacer(1, 6))

    # Section 6: Technology Stack
    story.append(Paragraph("6. Technology Stack & Integrations", h1_style))
    tech_items = specs.get("tech_stack", []) + specs.get("api_integrations", [])
    if tech_items:
        tech_rows = [
            [Paragraph("<b>Framework / Technology</b>", cell_bold), Paragraph("<b>Role & Integration Usage</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold)]
        ]
        for t in tech_items[:6]:
            tech_rows.append([
                Paragraph(t.get("title", "")[:45], cell_bold),
                Paragraph(t.get("text", "")[:150], cell_style),
                Paragraph(f"Page {t.get('page', 1)}", cell_style),
            ])
        tt = Table(tech_rows, colWidths=[130, 332, 70])
        tt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tt)
    else:
        story.append(Paragraph("Technology stack not explicitly enumerated in extracted specifications.", body_style))
    story.append(Spacer(1, 6))

    # Section 7: Security Requirements
    story.append(Paragraph("7. Security Requirements & Threat Assessment", h1_style))
    story.append(Paragraph(f"<b>Security Profile:</b> {ai.get('security_assessment', 'Security specifications analyzed.')}", body_style))
    sec_items = specs.get("security", [])
    if sec_items:
        sec_rows = [
            [Paragraph("<b>Security Control / Policy</b>", cell_bold), Paragraph("<b>Specification Detail</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold)]
        ]
        for s in sec_items[:5]:
            sec_rows.append([
                Paragraph(s.get("title", "")[:45], cell_bold),
                Paragraph(s.get("text", "")[:150], cell_style),
                Paragraph(f"Page {s.get('page', 1)}", cell_style),
            ])
        st_sec = Table(sec_rows, colWidths=[130, 332, 70])
        st_sec.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(st_sec)
    story.append(Spacer(1, 6))

    # Section 8: Potential Risks and Issues
    story.append(Paragraph("8. Potential Risks and Issues", h1_style))
    findings = data.get("findings", [])
    if findings:
        f_rows = [
            [Paragraph("<b>Severity</b>", cell_bold), Paragraph("<b>Identified Risk / Issue</b>", cell_bold), Paragraph("<b>Page</b>", cell_bold), Paragraph("<b>Actionable Guidance</b>", cell_bold)]
        ]
        for f in findings[:8]:
            sev = f.get("severity", "Info")
            sev_color = "#DC2626" if sev == "Critical" else ("#D97706" if sev == "Warning" else ("#059669" if sev == "Passed" else "#2563EB"))
            f_rows.append([
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", cell_style),
                Paragraph(f.get("title", ""), cell_bold),
                Paragraph(str(f.get("source_page", "N/A")), cell_style),
                Paragraph(f.get("recommended_action", "")[:120], cell_style),
            ])
        ft = Table(f_rows, colWidths=[65, 145, 62, 260])
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(ft)
    story.append(Spacer(1, 6))

    # Section 9: Missing or Ambiguous Requirements
    gaps = data.get("missing_gaps", [])
    if gaps:
        story.append(Paragraph("9. Missing or Ambiguous Requirements (Gap Analysis)", h1_style))
        gap_rows = [
            [Paragraph("<b>Identified Gap</b>", cell_bold), Paragraph("<b>Severity</b>", cell_bold), Paragraph("<b>Suggested Engineering Improvement</b>", cell_bold)]
        ]
        for g in gaps[:6]:
            gap_rows.append([
                Paragraph(g.get("issue", ""), cell_bold),
                Paragraph(g.get("severity", "Warning"), cell_style),
                Paragraph(g.get("suggested_improvement", "")[:140], cell_style),
            ])
        gt = Table(gap_rows, colWidths=[160, 62, 310])
        gt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(gt)
    story.append(Spacer(1, 6))

    # Section 7: AI-Generated Insights (Facts vs AI Interpretations)
    story.append(Paragraph("7. AI-Generated Insights & Document Facts", h1_style))
    facts = ai.get("extracted_facts", [])
    if facts:
        story.append(Paragraph("<b>Extracted Concrete Document Facts:</b>", h2_style))
        for fact in facts[:5]:
            story.append(Paragraph(f"• {fact}", body_style))
    story.append(Paragraph(f"<b>Specification Clarity Rating:</b> {ai.get('clarity_rating', 'High')}", body_style))
    story.append(Spacer(1, 6))

    # Section 8: Quality Scorecard Breakdown
    story.append(Paragraph("8. Specification Quality Score Breakdown", h1_style))
    cat_scores = qs.get("category_scores", {})
    if cat_scores:
        cat_rows = [
            [Paragraph("<b>Engineering Dimension</b>", cell_bold), Paragraph("<b>Score</b>", cell_bold), Paragraph("<b>Benchmark Status</b>", cell_bold)]
        ]
        for dim, sc in cat_scores.items():
            status_text = "Satisfactory" if sc >= 75 else ("Acceptable" if sc >= 50 else "Action Required")
            cat_rows.append([
                Paragraph(dim.title(), cell_bold),
                Paragraph(f"{sc}/100", cell_style),
                Paragraph(status_text, cell_style),
            ])
        cst = Table(cat_rows, colWidths=[180, 80, 272])
        cst.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(cst)
    story.append(Spacer(1, 6))

    # Section 9: Requirement Traceability Matrix
    tm = data.get("traceability_matrix", [])
    if tm:
        story.append(Paragraph("9. Requirement Traceability Matrix", h1_style))
        tm_rows = [
            [Paragraph("<b>Req ID</b>", cell_bold), Paragraph("<b>Category</b>", cell_bold), Paragraph("<b>Description</b>", cell_bold), Paragraph("<b>Source Page</b>", cell_bold), Paragraph("<b>Status</b>", cell_bold)]
        ]
        for req in tm[:10]:
            tm_rows.append([
                Paragraph(req.get("req_id", ""), cell_bold),
                Paragraph(req.get("category", ""), cell_style),
                Paragraph(req.get("description", "")[:120], cell_style),
                Paragraph(f"Page {req.get('source_page', 1)}", cell_style),
                Paragraph(req.get("status", "Covered"), cell_style),
            ])
        tmt = Table(tm_rows, colWidths=[65, 80, 267, 65, 55])
        tmt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tmt)
    story.append(Spacer(1, 6))

    # Section 10: Recommendations & Conclusion
    story.append(Paragraph("10. Actionable Recommendations & Engineering Conclusion", h1_style))
    recs = ai.get("recommendations", [])
    for rec in recs[:4]:
        prio = rec.get("priority", "Medium")
        story.append(Paragraph(f"• <b>[{prio} Priority] {rec.get('title', '')}:</b> {rec.get('detail', '')}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Final Architectural Conclusion:</b> {ai.get('conclusion', 'Ready for engineering implementation.')}", body_style))

    # Build the PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()


# =========================================================================
# 10. Sample Specification PDF Generators (Supported & Unsupported)
# =========================================================================

def generate_sample_pdf_bytes() -> bytes:
    """Generate a realistic 3-page enterprise technical specification PDF for instant demo testing."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10,
    )
    h1_style = ParagraphStyle(
        "DocH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#4338CA"),
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    story = [
        # Page 1
        Paragraph("Enterprise Cloud Analytics Platform — Software Requirements Specification (SRS)", title_style),
        Paragraph("<b>Document Version:</b> 2.4 | <b>Classification:</b> Confidential | <b>Author:</b> Cloud Engineering Architecture", body_style),
        Spacer(1, 8),
        Paragraph("1. Executive Overview & System Scope", h1_style),
        Paragraph("The Cloud Analytics Platform is an enterprise-grade telemetry ingestion, aggregation, and real-time visualization service. The system processes streaming logs, security telemetry, and user engagement metrics across multi-region edge nodes, providing sub-second analytical reporting.", body_style),
        Paragraph("2. System Architecture & Modular Design", h1_style),
        Paragraph("The platform employs a microservices architecture organized into four primary functional layers: (1) An Edge Ingress API Gateway responsible for SSL/TLS termination, request rate limiting, and client authentication. (2) An Event Ingestion Pipeline utilizing Kafka streaming topics with partitioned log ingestion. (3) An Analytics & Query Engine implementing distributed aggregation. (4) A Web Dashboard client built with React and WebSocket telemetry visualization.", body_style),
        Paragraph("3. Technology Stack & Runtime Infrastructure", h1_style),
        Paragraph("Core backend services are implemented in Python 3.12 utilizing the FastAPI framework with Uvicorn async ASGI workers. Persistent analytics data is stored in PostgreSQL 16 with TimescaleDB hypertables, while Redis 7 provides distributed session caching. All services are packaged as OCI-compliant Docker containers deployed on managed Kubernetes clusters.", body_style),
        PageBreak(),

        # Page 2
        Paragraph("4. Functional Requirements", h1_style),
        Paragraph("<b>REQ-01 (User Authentication):</b> The system shall provide single sign-on (SSO) authentication integrating with enterprise Okta and Azure AD via OAuth 2.0 and OpenID Connect (OIDC).", body_style),
        Paragraph("<b>REQ-02 (Telemetry Stream Ingestion):</b> The system shall ingest high-throughput JSON metric payloads over HTTPS POST endpoints with payload verification.", body_style),
        Paragraph("<b>REQ-03 (Automated Anomaly Detection):</b> The system shall evaluate metrics against dynamic deviation baselines and trigger notification webhooks within 5 seconds of threshold violation.", body_style),
        Paragraph("<b>REQ-04 (Role-Based Access Control):</b> The system shall enforce granular permissions distinguishing between System Administrator, Data Analyst, and Read-Only Observer roles.", body_style),
        Paragraph("5. Non-Functional Requirements & Performance SLAs", h1_style),
        Paragraph("<b>NFR-01 (Latency Budget):</b> P95 API response times for analytical query endpoints shall not exceed 250 milliseconds under standard operating loads of 5,000 requests per second.", body_style),
        Paragraph("<b>NFR-02 (System Availability):</b> The multi-region platform shall maintain a continuous service availability uptime SLA of 99.95% excluding scheduled maintenance windows.", body_style),
        Paragraph("<b>NFR-03 (Data Durability & Retention):</b> Raw telemetry streams shall be persisted in cold object storage with write-once-read-many (WORM) policies for a minimum of 90 days.", body_style),
        PageBreak(),

        # Page 3
        Paragraph("6. Security & Compliance Protocol", h1_style),
        Paragraph("All incoming network traffic must be encrypted using TLS 1.3 encryption. At-rest persistent volumes and PostgreSQL tables must utilize AES-256 encryption. Client authentication tokens must utilize asymmetric RS256 JWT tokens with a maximum lifespan of 15 minutes, accompanied by secure, httpOnly refresh tokens rotated upon each usage.", body_style),
        Paragraph("7. Database Schemas & Data Modeling", h1_style),
        Paragraph("The relational data model consists of tenant_organizations, user_accounts, telemetry_streams, anomaly_alerts, and audit_logs. Foreign key relational constraints are enforced on tenant IDs, and B-tree indexes are created on timestamp and metric_type columns to guarantee sub-second indexed queries.", body_style),
        Paragraph("8. Constraints, Dependencies & Deployment Strategy", h1_style),
        Paragraph("The system requires Kubernetes 1.28+ with Horizontal Pod Autoscaling (HPA) configured to scale between 3 and 50 replicas based on 70% CPU/Memory utilization thresholds. Outbound notification webhooks depend on third-party Slack and PagerDuty endpoints with exponential backoff retry algorithms.", body_style),
    ]

    doc.build(story)
    return buf.getvalue()


def generate_sample_unsupported_pdf_bytes() -> bytes:
    """Generate a non-technical PDF sample (culinary gastronomy) to test detection of unsupported documents."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("Artisanal Sourdough & French Pastry Masterclass", styles["Title"]),
        Paragraph("A culinary journey through flour hydration, wild yeast cultivation, and butter lamination techniques.", styles["Normal"]),
        Spacer(1, 14),
        Paragraph("Section 1: The Chemistry of Flour and Water", styles["Heading2"]),
        Paragraph("Bread making begins with organic unbleached wheat flour and room temperature spring water. Autolyse allows gluten development naturally over 45 minutes. Mix gently by hand and maintain dough temperature at 78 degrees Fahrenheit.", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Section 2: Croissant Lamination and Oven Baking", styles["Heading2"]),
        Paragraph("High-fat cultured European butter is rolled into a chilled dough block. Perform three envelope folds with 30-minute refrigeration intervals between turns. Bake in a deck oven at 400 degrees Fahrenheit until golden brown and flaky.", styles["Normal"]),
    ]

    doc.build(story)
    return buf.getvalue()
