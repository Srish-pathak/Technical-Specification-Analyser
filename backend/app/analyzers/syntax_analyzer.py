"""Syntax checking via ast.parse. Parsing never executes code."""
from __future__ import annotations

import ast
from typing import Optional

from app.schemas.findings import CAT_SYNTAX, HIGH, SRC_RULE, Finding


def parse_python(source: str, file_path: str) -> tuple[Optional[ast.AST], Optional[Finding]]:
    """Return (tree, None) on success or (None, syntax-finding) on failure."""
    try:
        return ast.parse(source, filename=file_path), None
    except SyntaxError as exc:
        line = exc.lineno
        lines = source.splitlines()
        evidence = lines[line - 1].strip()[:200] if line and 0 < line <= len(lines) else ""
        return None, Finding(
            rule_id="TSA-SYN-001", category=CAT_SYNTAX, severity=HIGH, file_path=file_path,
            line_number=line, column_number=exc.offset,
            description=f"Syntax error: {exc.msg}", evidence=evidence,
            recommended_correction="Fix the syntax error; the file cannot be parsed, so further analysis was skipped for it.",
            source=SRC_RULE, confidence="high", tool="python-ast")
    except (ValueError, RecursionError, MemoryError) as exc:
        return None, Finding(
            rule_id="TSA-SYN-002", category=CAT_SYNTAX, severity=HIGH, file_path=file_path,
            line_number=None, column_number=None,
            description=f"File could not be parsed ({type(exc).__name__}): {str(exc)[:120]}",
            evidence="", recommended_correction="Check for NUL characters or extreme nesting.",
            source=SRC_RULE, confidence="high", tool="python-ast")
