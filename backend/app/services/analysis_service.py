"""Static-analysis orchestration for submitted source (Phase 4).

Pipeline per request:  parse -> structure -> complexity -> quality -> security -> metrics.
Source is only parsed (ast.parse) or handed to *static* tools; it is never imported or executed.
The AI-agent stage is added in a later phase and is reported honestly as 'not_run' until then.
"""
from __future__ import annotations

import ast
import uuid
from typing import Optional

from app.analyzers import quality_analyzer as qa
from app.analyzers import security_analyzer as sa
from app.analyzers import tool_runner as tr
from app.analyzers.ast_analyzer import extract_structure
from app.analyzers.complexity_analyzer import analyze_complexity
from app.analyzers.syntax_analyzer import parse_python
from app.core.config import Settings, get_settings
from app.models.database import Database, utcnow
from app.schemas.findings import SEVERITY_ORDER, SEVERITY_RATIONALE, Finding, ToolStatus, severity_counts
from app.services.archive_manager import read_zip_project
from app.services.file_manager import (ANALYZABLE_LANGUAGES, InputValidationError, SourceFile,
                                       build_pasted_source, validate_upload)


def analyze_files(files: list[SourceFile], input_type: str, input_name: str, language: str,
                  settings: Optional[Settings] = None, use_external_tools: bool = True) -> dict:
    s = settings or get_settings()
    findings: list[Finding] = []
    limitations: list[str] = []
    file_rows, structures = [], {}
    parsed: list[tuple[SourceFile, ast.Module]] = []

    # Pass 1: syntax. Files that fail to parse get a finding and skip deeper analysis.
    for f in files:
        row = {"path": f.path, "language": f.language, "kind": f.kind, "lines": f.line_count, "analyzed": False, "note": ""}
        file_rows.append(row)
        if f.kind != "source":
            row["note"] = "Support file (documentation/config); not code-analysed."
        elif f.language not in ANALYZABLE_LANGUAGES:
            row["note"] = f"No deterministic analyzer for {f.language}; inventoried only."
        else:
            tree, err = parse_python(f.content, f.path)
            if err:
                findings.append(err)
                row["note"] = "Syntax error; deeper analysis skipped for this file."
            else:
                parsed.append((f, tree))
                row["analyzed"] = True
    unsupported = sorted({f.language for f in files if f.kind == "source" and f.language not in ANALYZABLE_LANGUAGES})
    if unsupported:
        limitations.append("Deterministic analysis is implemented for Python only; these languages were inventoried "
                           f"but not analysed: {', '.join(unsupported)}.")
    if not parsed:
        limitations.append("No parsable Python source was found, so no AST, complexity, quality or security analysis ran.")

    # External tools (static only), over parsable files.
    pairs = [(f.path, f.content) for f, _ in parsed]
    tools: list[ToolStatus] = []
    ruff_findings: list[Finding] = []
    bandit_findings: list[Finding] = []
    if use_external_tools and pairs:
        ruff_findings, rs = qa.run_ruff(pairs, s.tool_timeout_seconds)
        bandit_findings, bs = sa.run_bandit(pairs, s.tool_timeout_seconds)
    else:
        rs, _ = tr.cli_status("ruff")
        bs, _ = tr.cli_status("bandit")
        if not use_external_tools:
            rs.note = bs.note = "External tools disabled for this run."
    tools += [rs, bs]
    if not rs.ran:
        limitations.append("Ruff did not run (" + (rs.note or "unavailable") + "); built-in AST quality rules were used as the fallback.")
    if not bs.ran:
        limitations.append("Bandit did not run (" + (bs.note or "unavailable") + "); only built-in security rules were applied.")

    # Pass 2: per-file analysis.
    radon_used, radon_msgs = False, set()
    cc_sum = fn_count = max_cc = 0
    mis: list[float] = []
    doc_items = doc_documented = 0
    builtin_security: list[Finding] = []
    for f, tree in parsed:
        st = extract_structure(tree, f.content, f.path)
        cf, cm, rerr = analyze_complexity(tree, st, f.content)
        findings += cf
        radon_used |= cm["tool"] == "radon"
        if rerr:
            radon_msgs.add(rerr)
        fn_count += cm["functions"]
        cc_sum += cm["complexity_sum"]
        max_cc = max(max_cc, cm["max_complexity"])
        if cm["maintainability_index"] is not None:
            mis.append(cm["maintainability_index"])
        if not rs.ran:
            findings += qa.builtin_quality(tree, f.content, f.path)
        builtin_security += sa.builtin_security(tree, f.content, st)
        structures[f.path] = st.to_dict()
        items = [st.has_docstring] + [c.has_docstring for c in st.classes] + [fn.has_docstring for fn in st.functions]
        doc_items += len(items)
        doc_documented += sum(items)
    findings += ruff_findings
    findings += sa.merge_security(builtin_security, bandit_findings)

    rad = tr.radon_status()
    rad.ran = radon_used
    if radon_msgs:
        rad.note = "; ".join(sorted(radon_msgs))
    tools.insert(0, rad)
    if not radon_used:
        limitations.append("Radon was not used; complexity came from the built-in McCabe counter and the "
                           "maintainability index was not computed.")
    tools.append(ToolStatus("builtin-ast", True, True, "", "Built-in deterministic AST rules (quality + security)."))

    order = {sv: i for i, sv in enumerate(SEVERITY_ORDER)}
    findings.sort(key=lambda x: (order.get(x.severity, 9), x.file_path, x.line_number or 0, x.rule_id))
    sev = severity_counts(findings)
    by_source: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for x in findings:
        by_source[x.source] = by_source.get(x.source, 0) + 1
        by_category[x.category] = by_category.get(x.category, 0) + 1

    metrics = {
        "files_total": len(files), "files_analyzed": len(parsed),
        "total_lines": sum(f.line_count for f in files),
        "total_findings": len(findings), "severity_counts": sev, "by_source": by_source, "by_category": by_category,
        "function_count": fn_count, "class_count": sum(len(st["classes"]) for st in structures.values()),
        "complexity_sum": cc_sum, "avg_complexity": round(cc_sum / fn_count, 2) if fn_count else None,
        "max_complexity": max_cc, "maintainability_index_avg": round(sum(mis) / len(mis), 2) if mis else None,
        "doc_items": doc_items, "doc_documented": doc_documented,
        "documentation_coverage": round(100 * doc_documented / doc_items, 1) if doc_items else None,
    }
    return {
        "analysis_id": "A-" + uuid.uuid4().hex[:12], "input_type": input_type, "input_name": input_name,
        "language": language, "status": "completed", "created_at": utcnow(), "completed_at": utcnow(),
        "files": file_rows, "structure": structures, "findings": [x.to_dict() for x in findings],
        "metrics": metrics, "tools": [t.to_dict() for t in tools], "limitations": limitations,
        "severity_rationale": SEVERITY_RATIONALE,
        "ai": {"available": s.ai_configured, "ran": False,
               "note": "AI agent review is not part of the static-analysis phase; no AI output is included in this result."},
        "error": None,
    }


def _failed(input_type: str, name: str, language: str, error: str) -> dict:
    now = utcnow()
    return {"analysis_id": "A-" + uuid.uuid4().hex[:12], "input_type": input_type, "input_name": name,
            "language": language, "status": "failed", "created_at": now, "completed_at": now,
            "metrics": {}, "findings": [], "error": error}


def _run_and_store(db: Database, files: list[SourceFile], input_type: str, name: str, language: str,
                   settings: Settings, use_external_tools: bool = True) -> dict:
    try:
        rec = analyze_files(files, input_type, name, language, settings, use_external_tools)
    except Exception as exc:  # never lose a submission silently: persist the failure
        rec = _failed(input_type, name, language, f"{type(exc).__name__}: {exc}")
    db.save(rec)
    return rec


def submit_code(db: Database, code: str, language: Optional[str], filename: Optional[str],
                settings: Optional[Settings] = None, use_external_tools: bool = True) -> dict:
    s = settings or get_settings()
    src = build_pasted_source(code, language, filename, s)
    return _run_and_store(db, [src], "code", src.path, src.language, s, use_external_tools)


def submit_file(db: Database, filename: str, data: bytes, content_type: Optional[str],
                settings: Optional[Settings] = None, use_external_tools: bool = True) -> dict:
    s = settings or get_settings()
    src = validate_upload(filename, data, content_type, s)
    return _run_and_store(db, [src], "file", src.path, src.language, s, use_external_tools)


def submit_zip(db: Database, filename: str, data: bytes, content_type: Optional[str],
               settings: Optional[Settings] = None, use_external_tools: bool = True) -> dict:
    s = settings or get_settings()
    inv = read_zip_project(data, content_type, s)
    langs = sorted({f.language for f in inv.files if f.kind == "source"})
    rec_lang = langs[0] if len(langs) == 1 else ("mixed" if langs else "unknown")
    rec = _run_and_store(db, inv.files, "zip", filename or "archive.zip", rec_lang, s, use_external_tools)
    if rec.get("status") == "completed":
        rec["inventory"] = {"skipped": inv.skipped, "total_bytes": inv.total_bytes}
        db.save(rec)
    return rec
