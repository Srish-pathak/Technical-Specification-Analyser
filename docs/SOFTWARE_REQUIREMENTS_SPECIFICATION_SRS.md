# Software Requirements Specification (SRS)
## for TechSpecAnalyser
### A Static-Analysis-Grounded Multi-Agent Code Review & Technical Specification Intelligence Platform

---

**Document Identifier:** `TSA-SRS-2026-V1.0`  
**Version:** `1.0.0`  
**Status:** `Approved / Implementation Baseline`  
**Standard Compliance:** `IEEE Std 830-1998` / `ISO/IEC/IEEE 29148:2018`  
**Author:** TechSpecAnalyser Core Engineering Group  
**Date:** November 18, 2026  

---

## Table of Contents
1. [Introduction](#1-introduction)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Document Conventions](#12-document-conventions)
   - 1.3 [Intended Audience & Reading Suggestions](#13-intended-audience--reading-suggestions)
   - 1.4 [Project Scope & Core Value Proposition](#14-project-scope--core-value-proposition)
   - 1.5 [References & Standards](#15-references--standards)
2. [Overall Description](#2-overall-description)
   - 2.1 [Product Perspective](#21-product-perspective)
   - 2.2 [Product Features Summary](#22-product-features-summary)
   - 2.3 [User Classes & Personas](#23-user-classes--personas)
   - 2.4 [Operating Environment & Infrastructure](#24-operating-environment--infrastructure)
   - 2.5 [Design & Implementation Constraints](#25-design--implementation-constraints)
   - 2.6 [Assumptions & Dependencies](#26-assumptions--dependencies)
3. [System Architecture & Modules](#3-system-architecture--modules)
   - 3.1 [Architectural Decomposition](#31-architectural-decomposition)
   - 3.2 [Core Technology Stack](#32-core-technology-stack)
4. [Functional Requirements](#4-functional-requirements)
   - 4.1 [Module 1: Secure Ingestion & Input Processing (FR-001 to FR-003)](#41-module-1-secure-ingestion--input-processing)
   - 4.2 [Module 2: Deterministic Static Code Analysis (FR-004 to FR-006)](#42-module-2-deterministic-static-code-analysis)
   - 4.3 [Module 3: Remote GitHub Repository Review (FR-007 to FR-009)](#43-module-3-remote-github-repository-review)
   - 4.4 [Module 4: PDF Engineering Specification Intelligence (FR-010 to FR-015)](#44-module-4-pdf-engineering-specification-intelligence)
   - 4.5 [Module 5: Multi-Agent AI Review & Synthesis (FR-016)](#45-module-5-multi-agent-ai-review--synthesis)
   - 4.6 [Module 6: Report Generation & Export Engine (FR-017)](#46-module-6-report-generation--export-engine)
   - 4.7 [Module 7: Persistence & Historical Audit Trail (FR-018)](#47-module-7-persistence--historical-audit-trail)
   - 4.8 [Module 8: Galactic Portal User Interface (FR-019 to FR-020)](#48-module-8-galactic-portal-user-interface)
5. [Non-Functional Requirements & Performance SLAs](#5-non-functional-requirements--performance-slas)
   - 5.1 [Performance & Latency Budgets (NFR-001, NFR-002)](#51-performance--latency-budgets)
   - 5.2 [Security & Zero-Execution Policy (NFR-003, NFR-004)](#52-security--zero-execution-policy)
   - 5.3 [Reliability & Fault Tolerance (NFR-005, NFR-006)](#53-reliability--fault-tolerance)
   - 5.4 [Data Durability & Retention (NFR-007)](#54-data-durability--retention)
   - 5.5 [Portability & Cloud Compatibility (NFR-008)](#55-portability--cloud-compatibility)
   - 5.6 [Testability & Quality Verification (NFR-009, NFR-010)](#56-testability--quality-verification)
6. [Security, Safety & Integrity Architecture](#6-security-safety--integrity-architecture)
7. [Requirement Traceability Matrix](#7-requirement-traceability-matrix)
8. [Appendix & Glossary](#8-appendix--glossary)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) establishes the complete, authoritative technical requirements for **TechSpecAnalyser**, an enterprise-grade platform combining deterministic static code analysis, remote repository auditing, and AI-grounded technical specification intelligence.

### 1.2 Document Conventions
- **Requirement Identifiers:**
  - `FR-XXX`: Functional Requirement
  - `NFR-XXX`: Non-Functional Requirement
  - `SEC-XXX`: Security Specification
- **Requirement Priority:** Categorized into **High** (mandatory for baseline operation), **Medium** (core enhancement), and **Low** (supplementary).
- **Verification Criteria:** Each requirement specifies its formal method of verification (`Test`, `Inspection`, `Demonstration`, `Analysis`).

### 1.3 Intended Audience & Reading Suggestions
- **Software Architects & Engineers:** Review Sections 3, 4, and 5 for structural components, interfaces, and SLAs.
- **Security & Quality Assurance Auditors:** Review Section 6 for defense-in-depth guarantees and Section 7 for requirement traceability.
- **System Evaluators & Academic Reviewers:** Review Section 2 for product perspective and Section 5 for zero-hallucination governance.

### 1.4 Project Scope & Core Value Proposition
Conventional automated code review and documentation tools frequently suffer from two critical failure modes:
1. **Unreliable LLM Hallucinations:** AI code reviewers invent non-existent security flaws, miscalculate complexity, or cite hallucinated line numbers when operating without static grounding.
2. **Insecure Code Execution:** Many online linters or sandboxes execute user code, exposing infrastructure to remote code execution (RCE) and zip-slip attacks.

**TechSpecAnalyser resolves these challenges through a strict Two-Phase Grounded Architecture:**
- **Phase 1 (Deterministic Static Analysis):** Uploaded source code is parsed exclusively in-memory into Abstract Syntax Trees (AST). Syntactic defects, McCabe cyclomatic complexity, maintainability indices, and security flaws (Bandit/AST rules) are extracted deterministically without ever running the code.
- **Phase 2 (Grounded AI Synthesis):** AI agents (Gemini AI) receive verified deterministic findings as factual evidence, interpreting and explaining them without the ability to invent defects or fake line references.
- **Specification Intelligence:** Analyzes software engineering specifications (SRS, SDD, Architecture, Database Design, API Docs), categorizes requirements, detects missing gaps, computes a 0–100 Specification Quality Score, and generates professional PDF reports.

### 1.5 References & Standards
- **IEEE Std 830-1998:** Recommended Practice for Software Requirements Specifications.
- **ISO/IEC/IEEE 29148:2018:** Systems and software engineering — Life cycle processes — Requirements engineering.
- **RFC 7807:** Problem Details for HTTP APIs.
- **PEP 8 / PEP 484:** Style Guide & Type Annotations for Python Code.
- **NIST SP 800-218:** Secure Software Development Framework (SSDF).

---

## 2. Overall Description

### 2.1 Product Perspective
TechSpecAnalyser is a self-contained, cloud-deployable full-stack application. It operates as an asynchronous FastAPI backend paired with a zero-dependency Galactic Portal frontend, packaged as an OCI-compliant Docker container designed for deployment on Render, Kubernetes, or on-premises servers.

```
+-------------------------------------------------------------------------+
|                         TECHSPECANALYSER PLATFORM                       |
+-------------------------------------------------------------------------+
|                                                                         |
|  +--------------------+   +---------------------+   +----------------+  |
|  |   Code Analysis    |   | GitHub Repo Review  |   |  PDF Spec AI   |  |
|  | (Snippet/File/ZIP) |   | (REST API / ESLint) |   | (SRS/SDD/Arch) |  |
|  +---------+----------+   +----------+----------+   +-------+--------+  |
|            |                         |                      |           |
|            v                         v                      v           |
|  +-------------------------------------------------------------------+  |
|  |                     SECURE INGESTION GATEWAY                      |  |
|  |       (In-memory decompression, MIME checks, zero-execution)      |  |
|  +-----------------------------------+-------------------------------+  |
|                                      |                                  |
|                                      v                                  |
|  +-------------------------------------------------------------------+  |
|  |               DETERMINISTIC STATIC ANALYSIS ENGINE                |  |
|  |       ast.parse | Radon/McCabe | Ruff Quality | Bandit Security   |  |
|  +-----------------------------------+-------------------------------+  |
|                                      |                                  |
|                                      v                                  |
|  +-------------------------------------------------------------------+  |
|  |            GEMINI MULTI-AGENT SPECIFICATION INTELLIGENCE          |  |
|  |      (Grounding, fact/interpretation separation, quality scoring) |  |
|  +-----------------------------------+-------------------------------+  |
|                                      |                                  |
|                                      v                                  |
|  +--------------------+   +---------------------+   +----------------+  |
|  |  SQLite Database   |   | ReportLab PDF Export|   |Galactic UI View|  |
|  +--------------------+   +---------------------+   +----------------+  |
+-------------------------------------------------------------------------+
```

### 2.2 Product Features Summary
1. **Interactive Code Analysis:** Paste raw code, upload single source files, or drop ZIP archives to extract AST structures, cyclomatic complexity, code quality, and security vulnerabilities.
2. **GitHub Repository Review:** Connect to any public or private GitHub repository via REST API, traverse recursive branch trees, calculate language statistics, run multi-language static analysis, and synthesize architecture reviews.
3. **PDF Engineering Specification Analyzer:** Extract text preserving page numbers, classify document type (SRS, SDD, Architecture, Database, API), reject non-engineering content, compute a 0–100 Quality Score, build a Traceability Matrix, and detect requirement gaps.
4. **Professional PDF Audit Generation:** Generate multi-page executive PDF audit reports with two-pass running headers, footers, tables, and quality scorecards.
5. **Historical Auditing & Dashboards:** Store analysis records with timestamps, metrics, and severity distributions in SQLite for historical review.

### 2.3 User Classes & Personas
- **Software Engineers:** Analyze code snippets and pull-request payloads for immediate complexity bottlenecks, security vulnerabilities, and suggested refactorings.
- **Lead Architects & Tech Leads:** Audit system architecture documents, verify requirements coverage against acceptance criteria, and evaluate third-party GitHub repositories.
- **QA & Compliance Engineers:** Validate Software Requirements Specifications (SRS), inspect requirement traceability matrices, and audit security compliance.
- **Academic Researchers & Students:** Study static analysis grounding vs LLM hallucination trade-offs and evaluate software engineering project reports.

### 2.4 Operating Environment & Infrastructure
- **Server OS:** Linux (Debian/Ubuntu containerized) or Windows 10/11 (PowerShell/CMD).
- **Backend Runtime:** Python 3.12+ (FastAPI 0.111+, Uvicorn 0.30+, AnyIO, pypdf 5.0+, ReportLab 4.0+, httpx 0.27+).
- **Frontend Environment:** Standard modern web browsers (Chrome, Edge, Firefox, Safari) running ECMAScript 2020+ with zero external framework dependencies.
- **Container Infrastructure:** Docker OCI-compliant container bound to dynamic `$PORT` with health-probing support.

### 2.5 Design & Implementation Constraints
- **Zero-Code Execution:** User-submitted code or scripts must never be executed via `eval()`, `exec()`, or sub-shell invocation. Analysis is limited to structural parsing and static inspection.
- **In-Memory Archive Traversal:** Uploaded ZIP archives are decompressed and traversed in-memory only. No temporary directory extraction is permitted, mitigating ZIP-slip vulnerabilities by design.
- **Token Security:** GitHub Personal Access Tokens and Gemini API keys are processed in-memory or through secure backend environment variables; they are never exposed in frontend code or echoed in database logs.
- **Non-Technical Guard:** Non-engineering PDF uploads must be detected and rejected rather than fabricating fake technical metrics.

### 2.6 Assumptions & Dependencies
- Backend environment has outbound network connectivity when GitHub fetching or Gemini AI reviews are enabled.
- Deterministic static analysis operates fully offline without requiring an active AI API key.

---

## 3. System Architecture & Modules

### 3.1 Architectural Decomposition
1. **File & Archive Manager (`app.services.file_manager`):** Handles stream buffering, MIME validation, file size limits (1MB code, 20MB archives/PDFs), and in-memory ZIP traversal.
2. **Static Analysis Service (`app.services.analysis_service`):** Orchestrates AST parsing, complexity calculation (Radon/McCabe), quality checks (Ruff), and security analysis (Bandit).
3. **GitHub Review Service (`app.services.github_service`):** Interfaces with GitHub REST API, fetches repository metadata, branches, and trees, and manages language-specific analyzers.
4. **PDF Intelligence Service (`app.services.pdf_service`):** Extracts multi-page text with `pypdf`, classifies document domain, maps 10 specification categories, builds traceability matrices, and compiles ReportLab PDF reports.
5. **AI Review Service (`app.services.ai_service`):** Queries Gemini AI using structured JSON schemas and falls back seamlessly to deterministic synthesis.
6. **Persistence Layer (`app.services.database`):** Manages local SQLite storage for historical analyses, metrics tracking, and export caching.

### 3.2 Core Technology Stack
- **Backend Framework:** FastAPI / Uvicorn (ASGI)
- **Deterministic Analyzers:** Python `ast`, `radon`, `ruff`, `bandit`
- **Document Processing:** `pypdf` (extraction), `reportlab` (PDF generation)
- **AI Intelligence:** Google Gemini API (`gemini-2.5-flash` / `gemini-3.8-flash`) via `httpx`
- **Database:** SQLite 3 (WAL mode)
- **Frontend:** HTML5, CSS3, Vanilla Modern JavaScript (Galactic Portal cosmic dark theme)

---

## 4. Functional Requirements

### 4.1 Module 1: Secure Ingestion & Input Processing
- **FR-001 (Raw Code Ingestion):** The system shall accept direct raw source code input via HTTP POST (`/api/analysis/code`), validating text encoding (UTF-8) and length constraints (up to 1,000,000 bytes).
- **FR-002 (Single File Upload):** The system shall accept single file uploads via multipart form data (`/api/analysis/upload`), validating file extension and MIME type.
- **FR-003 (Archive Decompression Guard):** The system shall traverse ZIP archives entirely in-memory, enforcing a maximum compressed size of 20MB, maximum uncompressed footprint of 50MB, and rejecting path traversal strings (`../`).

### 4.2 Module 2: Deterministic Static Code Analysis
- **FR-004 (AST Syntax Parsing):** The system shall parse Python code into an Abstract Syntax Tree using `ast.parse`, capturing syntax errors, line numbers, and column offsets without code execution.
- **FR-005 (Cyclomatic Complexity Measurement):** The system shall calculate McCabe Cyclomatic Complexity per function and class, determining average complexity and maintainability index.
- **FR-006 (Security & Quality Auditing):** The system shall detect dangerous constructs (e.g. `eval()`, hardcoded credentials, insecure deserialization) through AST rules and integrated Bandit/Ruff scanners, removing duplicate findings.

### 4.3 Module 3: Remote GitHub Repository Review
- **FR-007 (Repository Metadata Ingestion):** The system shall query the GitHub REST API (`/api/analysis/github`) to extract repository name, owner, description, default branch, stars, forks, open issues, license, and size.
- **FR-008 (Recursive Branch Tree & Language Audit):** The system shall recursively fetch git tree hierarchies for the target branch, calculate directory counts, and detect language distributions.
- **FR-009 (Multi-Language Static Inspection):** The system shall execute appropriate linters (ESLint for JavaScript/TypeScript, Bandit/Ruff for Python) based on actual detected repository languages.

### 4.4 Module 4: PDF Engineering Specification Intelligence
- **FR-010 (Multi-Page Text Extraction):** The system shall extract text across all PDF pages via `pypdf>=5.0`, preserving source page numbers (`📄 Page X`) and tracking total word counts.
- **FR-011 (Domain Classification & Non-Technical Rejection):** The system shall analyze document vocabulary. If a document lacks software engineering markers, the system shall flag it as `UNSUPPORTED DOCUMENT TYPE` (`is_software_engineering_doc: False`), providing an explanation and excerpt without fabricating technical findings.
- **FR-012 (Supported Document Categorization):** For engineering PDFs, the system shall classify the document into: Software Requirements Specification (SRS), Software Design Document (SDD), System Architecture, Database Design, API Documentation, Project Proposals, Engineering Reports, or UML Design.
- **FR-013 (Specification Quality Scorecard):** The system shall compute an objective 0–100 Quality Score evaluated across 8 dimensions: Completeness, Clarity, Consistency, Security, Performance, Architecture, Testability, and Constraints.
- **FR-014 (Requirement Traceability Matrix):** The system shall extract discrete requirements (`REQ-*`, `FR-*`, `NFR-*`, `SEC-*`), mapping priority, coverage status, and source page references into a searchable table.
- **FR-015 (Missing Requirements & Gap Analysis):** The system shall identify unstated acceptance criteria, absent disaster recovery plans, undefined authentication protocols, missing observability, and deployment gaps.

### 4.5 Module 5: Multi-Agent AI Review & Synthesis
- **FR-016 (Grounded Gemini AI Review):** When configured with an AI key, the system shall query Gemini AI to generate an executive architectural review. Output must explicitly separate **Extracted Facts** from **AI Architectural Interpretations** and **Actionable Recommendations**.

### 4.6 Module 6: Report Generation & Export Engine
- **FR-017 (ReportLab Professional PDF Audit Export):** The system shall generate a multi-page, executive ReportLab PDF report (`GET /api/analysis/pdf/{analysis_id}/report`) containing all 10 analysis sections, color-coded severity badges, structured tables, and running headers/footers with two-pass page numbers (`Page X of Y`).

### 4.7 Module 7: Persistence & Historical Audit Trail
- **FR-018 (SQLite Persistence & Query):** The system shall store every analysis record (ID, timestamp, document metadata, quality score, findings, traceability rows) in SQLite, supporting retrieval via `GET /api/history` and `GET /api/analysis/{analysis_id}`.

### 4.8 Module 8: Galactic Portal User Interface
- **FR-019 (Galactic Portal Dark Cosmic UI):** The interface shall render in a dark navy/cosmic purple aesthetic with glowing accents, responsive sidebar navigation, and mobile-friendly layouts.
- **FR-020 (Interactive Accordions & Filter Controls):** The UI shall display results in 10 expandable accordions with severity filter buttons (`All`, `Critical`, `Warning`, `Informational`, `Passed`) and instant keyword search.

---

## 5. Non-Functional Requirements & Performance SLAs

### 5.1 Performance & Latency Budgets
- **NFR-001 (Deterministic Analysis Latency):** Static AST parsing, cyclomatic complexity, and quality auditing for source files (< 1MB) shall complete in less than 500 milliseconds.
- **NFR-002 (PDF Ingestion & Scoring Throughput):** Multi-page PDF text extraction, domain classification, and 10-section analysis shall complete in under 2.0 seconds for documents up to 25 pages.

### 5.2 Security & Zero-Execution Policy
- **NFR-003 (Zero-Code Execution Guarantee):** Uploaded source code and specification files shall never be compiled or executed. Analysis is strictly constrained to read-only string and AST inspection.
- **NFR-004 (Bounded Payload Protection):** Uploads exceeding bounded limits (1MB for single code files, 20MB for archives/PDFs) shall be rejected with HTTP 413 (Payload Too Large).

### 5.3 Reliability & Fault Tolerance
- **NFR-005 (Service Uptime SLA):** The deployed containerized web service shall maintain a continuous service availability uptime SLA of 99.95%, verified via automated `/health` probes.
- **NFR-006 (Graceful Offline Fallback):** The system shall operate with 100% functionality even when AI API keys are unavailable, executing deterministic synthesis without error.

### 5.4 Data Durability & Retention
- **NFR-007 (Audit History Retention):** Analysis records stored in SQLite shall persist for a configurable retention window (default: 90 days) with database WAL journaling.

### 5.5 Portability & Cloud Compatibility
- **NFR-008 (OCI Container Portability):** The application shall package as a Docker image runnable across any OCI-compliant runtime (Render, AWS ECS, Google Cloud Run, Kubernetes, local Docker) binding dynamically to `$PORT`.

### 5.6 Testability & Quality Verification
- **NFR-009 (Test Coverage):** All service functions, route handlers, zip-slip mitigations, and report generators shall maintain 100% automated test pass rates across the test suite.
- **NFR-010 (Document Authenticity Verification):** Non-engineering documents shall be rejected with `status: "unsupported"`, verified by automated tests to guarantee zero fabricated requirements.

---

## 6. Security, Safety & Integrity Architecture

| Defense Layer | Threat Addressed | Implementation Mechanism |
|---|---|---|
| **Archive Ingestion** | Zip-slip, directory traversal, overwrite | In-memory decompression only; rejection of relative traversal strings (`../`). |
| **Code Parser** | Remote Code Execution (RCE) | Built-in `ast.parse` inspection only. No `eval()`, `exec()`, or sub-shell invocation. |
| **PDF Extraction** | Malicious / Encrypted payloads | Password checks with `reader.is_encrypted` and stream bounds checking. |
| **Domain Rejection** | LLM Hallucination on non-technical content | Multi-point technical vocabulary classifier; non-technical content flagged with zero generated specs. |
| **Credential Hygiene** | Secret exfiltration | GitHub PATs and Gemini API keys processed in-memory, excluded from database and repr() logs. |

---

## 7. Requirement Traceability Matrix

| Requirement ID | Category | Description | Source Module | Verification Method | Status |
|---|---|---|---|---|---|
| **FR-001** | Ingestion | Raw code input validation | `file_manager.py` | Test / Route | Covered |
| **FR-002** | Ingestion | File upload validation | `file_manager.py` | Test / Route | Covered |
| **FR-003** | Ingestion | In-memory ZIP decompression | `file_manager.py` | Test / Unit | Covered |
| **FR-004** | Static Analysis | AST syntax inspection | `analysis_service.py` | Test / AST | Covered |
| **FR-005** | Static Analysis | Cyclomatic complexity | `complexity.py` | Test / McCabe | Covered |
| **FR-006** | Static Analysis | Security & quality auditing | `quality.py` / `security.py` | Test / Bandit | Covered |
| **FR-007** | GitHub Review | Repository metadata fetching | `github_service.py` | Test / API | Covered |
| **FR-008** | GitHub Review | Recursive branch tree traversal | `github_service.py` | Test / API | Covered |
| **FR-009** | GitHub Review | Multi-language static analysis | `github_service.py` | Test / ESLint | Covered |
| **FR-010** | PDF Intelligence | Multi-page text extraction | `pdf_service.py` | Test / pypdf | Covered |
| **FR-011** | PDF Intelligence | Non-technical document rejection | `pdf_service.py` | Test / Unit | Covered |
| **FR-012** | PDF Intelligence | Document type classification | `pdf_service.py` | Test / Unit | Covered |
| **FR-013** | PDF Intelligence | Specification Quality Score (0–100) | `pdf_service.py` | Test / Scoring | Covered |
| **FR-014** | PDF Intelligence | Requirement Traceability Matrix | `pdf_service.py` | Test / Matrix | Covered |
| **FR-015** | PDF Intelligence | Missing gap detection | `pdf_service.py` | Test / Gaps | Covered |
| **FR-016** | AI Intelligence | Grounded Gemini review | `ai_service.py` / `pdf_service.py` | Test / JSON | Covered |
| **FR-017** | Reporting | ReportLab multi-page PDF generation | `pdf_service.py` | Test / PDF | Covered |
| **FR-018** | Persistence | SQLite audit trail & history | `database.py` | Test / DB | Covered |
| **FR-019** | User Interface | Galactic Portal dark cosmic UI | `index.html` | Demonstration | Covered |
| **FR-020** | Operations | Health probe & uptime reporting | `main.py` | Test / Health | Covered |
| **NFR-001** | Performance | Sub-second analysis latency | `analysis_service.py` | Benchmark | Covered |
| **NFR-002** | Performance | PDF throughput < 2.0s | `pdf_service.py` | Benchmark | Covered |
| **NFR-003** | Security | Zero-code execution guarantee | Architecture Core | Inspection | Covered |
| **NFR-004** | Security | Bounded payload protection | `file_manager.py` | Test / Limits | Covered |
| **NFR-005** | Reliability | 99.95% availability SLA | Cloud Container | Demonstration | Covered |
| **NFR-006** | Fault Tolerance | Graceful offline AI fallback | `ai_service.py` | Test / Fallback | Covered |
| **NFR-007** | Durability | 90-day SQLite retention policy | `database.py` | Inspection | Covered |
| **NFR-008** | Portability | OCI Docker container compliance | `Dockerfile` | Demonstration | Covered |
| **NFR-009** | Quality | 100% automated test suite pass rate | `backend/tests/` | Test / Pytest | Covered |
| **NFR-010** | Integrity | Zero hallucination on non-technical content | `pdf_service.py` | Test / Unit | Covered |

---

## 8. Appendix & Glossary

- **AST (Abstract Syntax Tree):** A tree representation of the abstract syntactic structure of source code written in a programming language.
- **SRS (Software Requirements Specification):** A comprehensive description of the intended purpose and environment for software under development.
- **SDD (Software Design Document):** High-level or low-level technical architectural design describing software decomposition and dataflow.
- **NFR (Non-Functional Requirement):** A requirement that specifies criteria that can be used to judge the operation of a system rather than specific behaviors.
- **McCabe Cyclomatic Complexity:** A software metric used to indicate the complexity of a program by measuring the number of linearly independent paths.
- **Zip-Slip:** A form of directory traversal vulnerability where malicious archive files overwrite sensitive files during decompression.
- **WORM (Write Once, Read Many):** A data storage technology that allows information to be written to a storage medium a single time and prevents it from being modified or deleted.
- **ReportLab:** An enterprise Python library for generating dynamic, professional PDF documents.
