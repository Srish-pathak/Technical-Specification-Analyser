"""
Chapters 1, 2, and 3 builder:
- Chapter 1: Introduction (Background, Motivation, Problem Statement, Scope & Limitations, Objectives)
- Chapter 2: Review of Literature (Static analysis, MSR, LLMs in SE, Traceability, Research gap)
- Chapter 3: Theoretical Consideration (McCabe CC, Halstead, Coleman MI, Scoring models Eqn 3.1-3.7, Grounded dual-engine paradigm)
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from report_style_helpers import (
    FONT_NAME, set_run_font, add_body_p, add_chapter_title,
    add_heading_1, add_heading_2, add_heading_3, add_bullet_p,
    add_equation, add_table_with_borders
)

def build_chapters_1_to_3(doc):
    # =============================================================
    # CHAPTER 1: INTRODUCTION
    # =============================================================
    add_chapter_title(doc, "1", "Introduction")
    
    add_heading_1(doc, "1.1 Background of the Study")
    add_body_p(
        doc,
        "Software engineering in modern enterprise and open-source domains has evolved into a highly distributed, rapid-iteration discipline. The advent of continuous integration and continuous deployment (CI/CD) pipelines, microservices architectures, and cloud-native computing has accelerated delivery velocity to unprecedented levels. However, this acceleration has exacerbated a chronic structural challenge known as technical debt. As software systems expand, codebases frequently deviate from their foundational architectural designs, accumulating hidden vulnerabilities, inefficient control flow patterns, and maintainability deficits. In parallel, software requirements specifications (SRS), design documents, and interface contracts are rarely maintained in synchrony with live code implementations. This phenomenon—commonly termed specification drift—leads to severe communication disconnects between software architects, developers, security auditors, and business stakeholders."
    )
    add_body_p(
        doc,
        "Static program analysis has long stood as the primary defensive paradigm against technical debt and code degradation. By analyzing source code without executing it, static analysis engines evaluate syntactic abstract syntax trees (AST), compute cyclomatic complexity, and detect anti-patterns or security flaws deterministically. Traditional static tools—such as Radon, Bandit, Ruff, and ESLint—provide indispensable, reproducible metrics. Nonetheless, these tools operate under rigid syntactic rules; they possess zero comprehension of high-level semantic intent, business logic coherence, or functional completeness. A linter can verify that a Python function follows PEP-8 style guidelines and contains no unhandled exceptions, but it cannot determine whether that function actually fulfills the performance constraints or business requirements outlined in the project's software specification."
    )
    add_body_p(
        doc,
        "Recently, the emergence of Large Language Models (LLMs) and generative artificial intelligence has introduced powerful capabilities for natural language reasoning, code summarization, and automated software critique. Models such as Google Gemini can digest extensive technical documentation, reason across natural language requirements, and propose nuanced refactoring solutions. However, deploying pure LLMs for software quality assurance introduces significant risks. Generative models are inherently non-deterministic, prone to semantic hallucinations, and susceptible to generating fabricated citations or misleading severity ratings. Without grounded numerical boundaries and rule-based verification, pure AI-based assessments cannot be trusted for critical engineering decisions."
    )
    add_body_p(
        doc,
        "Therefore, there is an urgent scientific and practical imperative to formulate an integrated, dual-engine software verification paradigm. By combining the unyielding determinism of static program analysis with the semantic intelligence of modern generative AI, software engineering teams can achieve both mathematically grounded code auditing and context-aware specification validation. The overall objective of this study is to design, develop, empirically evaluate, and deploy TechSpecAnalyser—an integrated full-stack platform combining deterministic static program analysis with Google Gemini generative AI to provide automated multi-file code auditing, remote GitHub repository health evaluation, and technical specification verification."
    )
    
    add_heading_1(doc, "1.2 Motivation")
    add_body_p(
        doc,
        "The motivation behind TechSpecAnalyser arises directly from observed bottlenecks in real-world software development lifecycles. Software engineering audits, peer code reviews, and compliance certifications are notoriously labour-intensive and error-prone when conducted manually. Security engineers spend hours parsing through multi-file repositories to trace data flow paths and uncover injection risks. Project managers struggle to determine whether the committed software artifact adheres to the functional and non-functional requirements negotiated with clients in formal SRS documents."
    )
    add_body_p(
        doc,
        "Furthermore, existing software quality portals suffer from fragmentation. An engineering team must typically configure and juggle disparate tools: SonarQube for static metrics, Snyk for dependency vulnerabilities, GitHub Actions for repository checks, and standalone chat interfaces (such as ChatGPT or Gemini) for ad-hoc code explanation. This fragmentation results in cognitive overload, high infrastructure costs, and lack of unified traceability. More critically, generic chat interfaces lack direct integration with deterministic analysis pipelines, meaning that recommendations provided by an LLM are frequently disconnected from the true cyclomatic complexity or AST structure of the code under examination."
    )
    add_body_p(
        doc,
        "TechSpecAnalyser addresses this gap by synthesizing these fragmented capabilities into a single, cohesive, futuristic portal. By providing instant multi-file code inspection, remote GitHub repository hygiene checks, and document-specific PDF specification analysis within a unified interface, the platform empowers developers to identify code smells, architectural vulnerabilities, and specification discrepancies before software is released into production."
    )
    
    add_heading_1(doc, "1.3 Problem Statement")
    add_body_p(
        doc,
        "The fundamental research and engineering problem addressed in this project can be stated as follows: Existing automated software quality assurance systems either rely strictly on deterministic syntactic rules—failing to capture high-level semantic intent, requirement traceability, and natural language specification alignment—or rely naively on generative large language models, which introduce hallucinations, non-deterministic scoring, and lack formal grounding in empirical software metrics."
    )
    add_body_p(
        doc,
        "Consequently, there is an absence of an open, extensible, full-stack platform capable of simultaneously: (1) extracting deterministic structural and security metrics from multi-file source code across different programming languages; (2) crawling and evaluating remote repository health and testing hygiene; (3) parsing complex, multi-page technical specification PDFs into structured requirement hierarchies; and (4) binding these findings through calibrated, mathematically bounded scoring algorithms that constrain and ground generative AI synthesis."
    )
    
    add_heading_1(doc, "1.4 Scope and Limitations")
    add_body_p(
        doc,
        "The scope of this project encompasses the design, implementation, automated verification, and cloud deployment of the TechSpecAnalyser platform. Specifically, the scope includes:"
    )
    add_bullet_p(doc, "Multi-Language Static Analysis: ", "Parsing, metric computation, and vulnerability detection for Python (via AST, Radon, Bandit, Ruff) and JavaScript/Node.js (via ESLint and syntax tree parsing).")
    add_bullet_p(doc, "Remote Repository Review: ", "Automated ingestion of public GitHub repositories via GitHub REST API v3, tree traversal, automated test detection, and repository health computation.")
    add_bullet_p(doc, "Technical Specification Parsing: ", "Multi-stage digital PDF text extraction (PyMuPDF, pdfplumber, pypdf) supporting SRS documents, architecture descriptions, API documentation, and engineering proposals, preserving section structures and page numbers.")
    add_bullet_p(doc, "Grounded AI Integration: ", "Structured JSON prompting of Google Gemini models (gemini-2.5-flash and gemini-1.5-flash) to generate executive summaries, gap analyses, and refactoring recommendations.")
    add_bullet_p(doc, "Galactic Portal Frontend: ", "A high-performance, single-page application built on pure ECMAScript 2022 and modern CSS3, featuring dark navy futuristic themes, glowing accents, and dynamic visual analytics without third-party frameworks.")
    
    add_body_p(
        doc,
        "The project operates under the following recognized technical limitations:"
    )
    add_bullet_p(doc, "Digital PDF Dependency: ", "The current extraction pipeline is engineered for digitally authored vector PDFs. Image-only, scanned, or non-text PDFs require an upstream Optical Character Recognition (OCR) preprocessor (e.g., Tesseract), which is not bundled into the lightweight production container.")
    add_bullet_p(doc, "GitHub Public Scope: ", "Remote repository ingestion operates seamlessly on public GitHub repositories. Private enterprise repositories require custom OAuth personal access token configuration.")
    add_bullet_p(doc, "AI Gateway Connectivity: ", "Semantic synthesis and natural language report generation require active outbound HTTPS access to Google Gemini API endpoints; during network partitioning, the system gracefully falls back to deterministic static rules.")
    
    add_heading_1(doc, "1.5 Objectives")
    add_body_p(
        doc,
        "The specific objectives formulated to realize the overall objective of this project are structured as follows:"
    )
    add_bullet_p(doc, "Objective 1: ", "To engineer a deterministic multi-file static analysis engine that computes cyclomatic complexity, Halstead metrics, maintainability index, and security vulnerabilities across Python and JavaScript codebases.")
    add_bullet_p(doc, "Objective 2: ", "To formulate and implement rigorous, mathematically bounded scoring models for Code Quality Score (bounded in [3.0, 9.8]), Repository Health Score (bounded in [10, 100]), and PDF Specification Quality Score (bounded in [25, 98]).")
    add_bullet_p(doc, "Objective 3: ", "To construct a resilient, multi-library digital PDF parsing and text extraction engine (leveraging PyMuPDF, pdfplumber, and pypdf) that extracts requirement blocks, system architectures, and interface constraints while preserving page traceability.")
    add_bullet_p(doc, "Objective 4: ", "To integrate Google Gemini generative artificial intelligence via strictly validated JSON schema contracts, synthesizing natural language executive summaries, gap analyses, and actionable remediation advice without factual hallucination.")
    add_bullet_p(doc, "Objective 5: ", "To design and build an intuitive, responsive single-page user interface adhering to the custom 'Galactic Portal' aesthetic, utilizing pure modern web standards without heavy external framework overhead.")
    add_bullet_p(doc, "Objective 6: ", "To validate system correctness through an automated test suite comprising 93 unit and integration tests, evaluate real-world production deployment on Render, and conduct root-cause analyses of deployment incidents.")
    
    # =============================================================
    # CHAPTER 2: REVIEW OF LITERATURE
    # =============================================================
    add_chapter_title(doc, "2", "Review of Literature")
    
    add_heading_1(doc, "2.1 Evolution of Static Program Analysis")
    add_body_p(
        doc,
        "Static program analysis has constituted a cornerstone of software quality assurance for nearly five decades. In a seminal contribution, McCabe (1976) introduced the graph-theoretic concept of cyclomatic complexity, demonstrating that the number of linearly independent paths through a program's control-flow graph serves as a direct indicator of testing effort, defect probability, and cognitive maintainability. McCabe established that procedures exhibiting cyclomatic complexity exceeding 10 are significantly more error-prone and arduous to test thoroughly. Concurrently, Halstead (1977) formulated the foundation of software science, proposing empirical measures of program volume, difficulty, and implementation effort derived purely from operator and operand counts."
    )
    add_body_p(
        doc,
        "Building upon these foundations, Coleman et al. (1994) synthesized cyclomatic complexity, Halstead volume, and lines of code into a single, unified metric known as the Maintainability Index (MI). Adopted extensively by the Software Engineering Institute (SEI) and modern integrated development environments (IDEs), the Maintainability Index provides a polynomial composite metric ranging from 0 to 100 that quantifies the long-term maintainability of a software module. Subsequent empirical investigations by Oman and Hagemeister (1994) corroborated that MI serves as an effective predictor of software maintenance costs in enterprise systems."
    )
    add_body_p(
        doc,
        "In the realm of security-oriented static analysis, Chess and McGraw (2004) emphasized the paradigm of 'building security in', demonstrating that uncovering security anti-patterns (such as hardcoded credentials, insecure deserialization, and dangerous eval statements) during static inspection is orders of magnitude cheaper than addressing vulnerabilities post-deployment. Modern static analysis frameworks—such as Bandit for Python security auditing and Ruff for high-speed AST linting—operationalize these concepts by traversing Abstract Syntax Trees (AST) to detect patterns matching known Common Weakness Enumerations (CWE)."
    )
    
    add_heading_1(doc, "2.2 Mining Software Repositories and Repository Health")
    add_body_p(
        doc,
        "The proliferation of open-source software collaboration platforms has fostered the academic field of Mining Software Repositories (MSR). Nagappan and Ball (2005) investigated static analysis defect prediction across industrial codebases, demonstrating that code churn, module dependencies, and defect density are strongly correlated with post-release failures. Their findings validated that static rule violations provide actionable early warnings of systemic architectural decay."
    )
    add_body_p(
        doc,
        "In a comprehensive analysis of GitHub workflows, Vasilescu et al. (2015) examined the impact of continuous integration (CI) and automated testing on software quality. Their empirical findings demonstrated that projects incorporating automated test suites, pull request code review gates, and explicit documentation achieve significantly higher code stability and lower regression rates than unmanaged repositories. Similarly, Kalliamvakou et al. (2014) articulated the perils and promises of mining GitHub repositories, highlighting that thousands of public repositories suffer from poor hygiene, missing test suites, and abandoned documentation. These empirical insights underscore the vital importance of automated repository health scoring mechanisms that penalize missing automated tests and unhandled issue backlogs."
    )
    
    add_heading_1(doc, "2.3 Natural Language Processing and LLMs in Software Engineering")
    add_body_p(
        doc,
        "Over the past five years, the application of Natural Language Processing (NLP) to software engineering has transitioned from statistical n-gram models to Transformer-based Large Language Models. Feng et al. (2020) pioneered CodeBERT, a bimodal pre-trained model for natural language and programming languages, demonstrating that joint representations of source code and natural language docstrings significantly improve code search, documentation generation, and defect detection."
    )
    add_body_p(
        doc,
        "More recently, Hou et al. (2023) conducted an exhaustive survey on Large Language Models for software engineering, detailing how contemporary autoregressive foundation models (such as GPT-4 and Google Gemini) excel at complex tasks including automated program repair, code explanation, test case generation, and architectural summarization. They observed that LLMs possess unprecedented capacity for semantic reasoning across diverse software artifacts."
    )
    add_body_p(
        doc,
        "However, as articulated by White et al. (2023) in their catalog of prompt engineering patterns for software engineering, foundation models exhibit distinct failure modes when applied in unconstrained settings. Chief among these vulnerabilities is hallucination—the generation of syntactically plausible but factually incorrect assertions, non-existent API references, or distorted security risk classifications. Furthermore, LLMs lack an intrinsic mathematical anchor; when asked to rate code quality on a numerical scale, stochastic sampling causes identical code inputs to receive wildly fluctuating scores across consecutive queries. This fundamental instability highlights why state-of-the-art software engineering systems must decouple quantitative metric calculation from qualitative natural language synthesis."
    )
    
    add_heading_1(doc, "2.4 Requirements Engineering and Specification Traceability")
    add_body_p(
        doc,
        "Requirements engineering forms the bedrock of predictable software delivery. In their seminal work, Gotel and Finkelstein (1994) defined requirements traceability as the ability to describe and follow the life of a requirement in both forward and backward directions through all phases of system development. They revealed that lack of traceability is a primary contributor to project cost overruns and system failures. When software requirements cannot be tied to specific implementation modules or test cases, software architects cannot verify compliance."
    )
    add_body_p(
        doc,
        "Addressing this challenge, Borg et al. (2014) investigated automated traceability recovery using Information Retrieval (IR) and natural language parsing techniques. While traditional IR methods (such as vector space models and Latent Semantic Indexing) succeeded in matching keyword distributions between requirement texts and source files, they struggled with subtle conceptual shifts, synonyms, and architectural abstraction levels. The recent application of advanced LLMs to requirements engineering provides the semantic flexibility needed to understand high-level specifications; however, preserving page-level traceability to original source documents remains vital to ensure human auditability and regulatory compliance."
    )
    
    add_heading_1(doc, "2.5 Synthesis and Research Gap")
    add_body_p(
        doc,
        "A rigorous synthesis of published literature and existing commercial platforms reveals significant operational gaps. Table 2.1 presents a comparative synthesis of existing paradigms against the design requirements of modern software engineering teams."
    )
    
    # Table 2.1 Literature Synthesis
    headers_21 = ["System / Tool", "Analysis Paradigm", "Deterministic Metrics", "Semantic AI Reasoning", "PDF Specification Auditing", "Unified Scoring Engine"]
    rows_21 = [
        ["SonarQube", "Static Rules / AST", "Yes (CC, Duplication)", "Limited / Commercial add-on", "No (Source code only)", "Yes (Quality Gate)"],
        ["Snyk Code", "Static Security / SAST", "Yes (CWE, CVE)", "Narrow (Vulnerability explanation)", "No", "No (Binary pass/fail)"],
        ["GitHub CodeQL", "Semantic Code Querying", "Yes (Data flow graph)", "No", "No", "No (Alert listing)"],
        ["Generic ChatGPT / Gemini", "Pure Generative LLM", "No (Stochastic hallucination)", "Yes (Extensive reasoning)", "Ad-hoc (Context window limits)", "No (Arbitrary ratings)"],
        ["TechSpecAnalyser (Proposed)", "Hybrid Dual-Engine", "Yes (Radon, Bandit, Ruff, ESLint)", "Yes (Google Gemini via JSON)", "Yes (PyMuPDF + Traceability)", "Yes (Calibrated Bounded Models)"]
    ]
    col_w_21 = [Inches(1.2), Inches(1.1), Inches(0.9), Inches(1.1), Inches(1.0), Inches(1.0)]
    add_table_with_borders(doc, headers_21, rows_21, col_w_21, "Comparative synthesis of existing software quality paradigms and identified research gaps", "2.1")
    
    add_body_p(
        doc,
        "As established in Table 2.1, conventional enterprise tools excel at deterministic metric extraction but remain blind to natural language specifications and high-level architectural intent. Conversely, pure generative AI interfaces offer rich semantic discourse but lack deterministic grounding, reproducible scoring, and structured multi-stage PDF traceability. TechSpecAnalyser bridges this precise research gap by architecting a hybrid dual-engine platform where deterministic static analysis anchors and bounds generative AI reasoning."
    )
    
    # =============================================================
    # CHAPTER 3: THEORETICAL CONSIDERATION
    # =============================================================
    add_chapter_title(doc, "3", "Theoretical Consideration")
    
    add_heading_1(doc, "3.1 Mathematical Foundations of Software Metrics")
    add_body_p(
        doc,
        "To guarantee that software quality assessments remain objective, repeatable, and independent of stochastic variance, TechSpecAnalyser grounds its analysis in established mathematical and algorithmic formulations from software science and graph theory."
    )
    
    add_heading_2(doc, "3.1.1 Cyclomatic complexity")
    add_body_p(
        doc,
        "Cyclomatic complexity is grounded in graph theory and models the control-flow structure of a program module as a directed graph G = (V, E), where V is the set of program blocks (nodes) and E is the set of directed control-flow transfers (edges). Following the classical formulation of McCabe (1976), the cyclomatic complexity M is defined as:"
    )
    add_equation(doc, "M = E - N + 2P", "3.1")
    add_body_p(
        doc,
        "where, E = number of edges in the control-flow graph; N = number of nodes (basic blocks); and P = number of connected components (typically P = 1 for a single subroutine or function). From Eqn. (3.1), it is evident that M corresponds directly to the dimension of the cycle space of the control-flow graph, representing the exact number of linearly independent paths required to achieve complete branch coverage during testing."
    )
    add_body_p(
        doc,
        "In modern static analyzers such as Radon, cyclomatic complexity is computed by traversing the Python AST and counting decision points (predicate nodes) that cause control-flow branching (such as if, elif, for, while, except, with, and boolean expressions). For a module containing k decision points, the cyclomatic complexity simplifies to M = k + 1."
    )
    
    add_heading_2(doc, "3.1.2 Maintainability index formulation")
    add_body_p(
        doc,
        "The Maintainability Index (MI) is a composite software metric designed to provide a single, normalized measure of relative software maintainability. Following the Software Engineering Institute (SEI) polynomial formulation with log-scale Halstead and cyclomatic parameters (Coleman et al., 1994), the raw maintainability index MI_raw is expressed as:"
    )
    add_equation(doc, "MI_{raw} = 171 - 5.2 \\ln(V) - 0.23 \\cdot G - 16.2 \\ln(L)", "3.2")
    add_body_p(
        doc,
        "where, V = Halstead Volume of the module (representing the total bit size of the program implementation); G = Cyclomatic Complexity M as defined in Eqn. (3.1); and L = total Lines of Code (LOC) or Source Lines of Code (SLOC). To prevent negative values and provide an intuitive percentage-based scale, the raw index is normalized onto a [0, 100] continuum:"
    )
    add_equation(doc, "MI_{norm} = \\max\\left(0, \\frac{MI_{raw}}{171} \\times 100\\right)", "3.3")
    add_body_p(
        doc,
        "From Eqn. (3.2) and Eqn. (3.3), it is clear that higher values of Halstead volume, cyclomatic complexity, or sheer lines of code depress the maintainability index, signaling that a software unit is becoming excessively monolithic and requires decomposition."
    )
    
    add_heading_1(doc, "3.2 Scoring Methodologies and Normalisation")
    add_body_p(
        doc,
        "A central contribution of TechSpecAnalyser is the derivation and calibration of bounded scoring models across all operational modules. Rather than allowing generative LLMs to invent arbitrary scores, the system calculates quantitative scores through deterministic mathematical formulas that evaluate critical flaws, warnings, structural complexity, and testing hygiene."
    )
    
    add_heading_2(doc, "3.2.1 Code quality scoring model")
    add_body_p(
        doc,
        "The Code Quality Score S_code is calibrated on a base scale from 3.0 to 9.8, subsequently mapped to a normalized 0-100 scale. The formulation starts from an ideal baseline score of 9.5 and systematically applies weighted penalties for detected static vulnerabilities, code smells, and excessive cyclomatic complexity:"
    )
    add_equation(doc, "S_{code} = \\text{clamp}\\left(9.5 - (2.5 \\cdot C_{code}) - (0.8 \\cdot W_{code}) - \\left[0.5 \\cdot \\max(0, \\overline{CC} - 3)\\right], 3.0, 9.8\\right)", "3.4")
    add_body_p(
        doc,
        "where, C_code = count of critical security issues (e.g., hardcoded passwords, SQL injection patterns, unsafe shell execution); W_code = count of warning-level code smells (e.g., broad exception catching, unused imports, high parameter counts); CC_bar = average cyclomatic complexity across all analyzed functions in the codebase; and clamp(x, a, b) restricts the value to min(max(x, a), b). To display the result in the user interface as a standard percentage grade, the normalized score is computed as:"
    )
    add_equation(doc, "S_{norm} = 10 \\cdot S_{code}", "3.5")
    add_body_p(
        doc,
        "From Eqn. (3.4) and Eqn. (3.5), it is established that a clean codebase with zero critical issues, zero warnings, and an average cyclomatic complexity below 3 receives an exemplary score of 95.0% (9.5/10), capped at a maximum of 98.0%, while code burdened with multiple critical vulnerabilities is bounded above a floor of 30.0% (3.0/10), ensuring mathematical stability and meaningful differentiation."
    )
    
    add_heading_2(doc, "3.2.2 Repository health scoring algorithm")
    add_body_p(
        doc,
        "The Repository Health Score H_repo evaluates the overarching engineering hygiene, stability, and testing maturity of a GitHub repository. The scoring model starts at a perfect score of 100 and applies tiered penalties based on issue severity, modulated by an automated testing reward/penalty term:"
    )
    add_equation(doc, "H_{repo} = \\text{clamp}\\left(100 - (20 \\cdot C_{repo} + 4 \\cdot W_{repo} + 0.5 \\cdot I_{repo}) + \\Delta_{test}, 10, 100\\right)", "3.6")
    add_body_p(
        doc,
        "where, C_repo = number of critical architectural or security flaws detected in the repository files; W_repo = number of warning-level anti-patterns; I_repo = number of informational notices or style violations; and Delta_test represents the testing hygiene modifier defined as:"
    )
    add_equation(doc, "\\Delta_{test} = \\begin{cases} +5, & \\text{if automated test suite is detected (e.g., pytest, jest, unittest)} \\\\ -5, & \\text{if no automated test suite is detected} \\end{cases}", "3.7")
    add_body_p(
        doc,
        "From Eqn. (3.6) and Eqn. (3.7), the presence of automated testing infrastructure provides an immediate 10-point relative advantage over unverified codebases, directly reflecting the empirical findings of Vasilescu et al. (2015) regarding the impact of continuous testing on software defect containment."
    )
    
    add_heading_2(doc, "3.2.3 Technical specification quality scoring framework")
    add_body_p(
        doc,
        "Evaluating a Software Requirements Specification (SRS) requires assessing multidimensional attributes including completeness, architectural clarity, security definitions, and testability. TechSpecAnalyser establishes an 8-dimensional weighted specification quality model. Let d_i in [0, 100] represent the score assigned to dimension i, and w_i represent its normalized weight. The raw specification score Q_raw is defined as:"
    )
    add_equation(doc, "Q_{raw} = \\sum_{i=1}^{8} w_i \\cdot d_i", "3.8")
    add_body_p(
        doc,
        "Table 3.1 details the weight distribution w_i and evaluation criteria established for each of the eight specification dimensions."
    )
    
    # Table 3.1 Specification Quality Dimensions
    headers_31 = ["Index (i)", "Specification Dimension", "Weight (wi)", "Key Evaluation Focus"]
    rows_31 = [
        ["1", "Completeness", "0.20", "Coverage of functional requirements, user stories, and acceptance criteria"],
        ["2", "Clarity and Unambiguity", "0.15", "Absence of vague descriptors (e.g., 'fast', 'user-friendly', 'scalable')"],
        ["3", "Internal Consistency", "0.10", "Coherence between data schemas, interface models, and module boundaries"],
        ["4", "Security Requirements", "0.15", "Specification of authentication, authorization, encryption, and audit logs"],
        ["5", "Performance Metrics", "0.10", "Quantifiable latency thresholds, throughput targets, and concurrency limits"],
        ["6", "System Architecture", "0.15", "Structural definition of components, databases, network tiers, and protocols"],
        ["7", "Testability and Traceability", "0.10", "Presence of verifiable assertions and mapping to verification procedures"],
        ["8", "Constraints and Assumptions", "0.05", "Explicit documentation of hardware, software, and dependency bounds"]
    ]
    col_w_31 = [Inches(1.0), Inches(1.8), Inches(1.0), Inches(2.5)]
    add_table_with_borders(doc, headers_31, rows_31, col_w_31, "Weight distribution and criteria for the 8-dimensional specification quality framework", "3.1")
    
    add_body_p(
        doc,
        "To ensure that missing critical security provisions or contradictory requirements severely penalize the final rating, the final Specification Quality Score Q_spec incorporates deduction penalties for detected requirement defects:"
    )
    add_equation(doc, "Q_{spec} = \\text{clamp}\\left(Q_{raw} - (12 \\cdot C_{spec} + 3 \\cdot W_{spec}), 25, 98\\right)", "3.9")
    add_body_p(
        doc,
        "where, C_spec = count of critical specification gaps (such as unaddressed authentication models, missing error recovery, or undefined database transactions); and W_spec = count of ambiguous or weak requirement formulations. Clamping in [25, 98] guarantees that even heavily flawed documents retain a non-zero diagnostic rating, while flawless specifications are capped realistically below 100%."
    )
    
    add_heading_1(doc, "3.3 Grounded Dual-Engine Paradigm")
    add_body_p(
        doc,
        "The theoretical cornerstone of TechSpecAnalyser is the Grounded Dual-Engine Paradigm. In conventional software tools, static analysis and AI reasoning are treated as mutually exclusive alternatives. TechSpecAnalyser formalizes their relationship as a cooperative, two-phase pipeline where the deterministic engine acts as an objective epistemic ground for the generative AI engine."
    )
    add_body_p(
        doc,
        "In Phase 1 (Deterministic Extraction), the system applies rule-based AST visitors, regex pattern matchers, and static analyzers to construct an invariant feature vector: exact line numbers, cyclomatic complexity counts, maintainability indices, and raw PDF text spans. This phase is 100% reproducible and free from stochastic variation."
    )
    add_body_p(
        doc,
        "In Phase 2 (Bounded Generative Synthesis), this invariant feature vector—alongside the extracted source code or specification text—is injected into a strictly typed JSON prompt schema for Google Gemini. The LLM is explicitly instructed that it must not invent metrics, fabricate file names, or alter the computed quality scores. Instead, its role is restricted to semantic contextualization: synthesizing executive summaries, translating raw AST anomalies into developer-friendly refactoring advice, and explaining the architectural implications of specification gaps. If the AI service fails or times out, the deterministic metrics remain fully intact and are presented to the user without interruption. This ensures that TechSpecAnalyser achieves both mathematical dependability and natural language explainability."
    )
    
    doc.add_page_break()

print("report_sections_ch1_ch3 loaded.")
