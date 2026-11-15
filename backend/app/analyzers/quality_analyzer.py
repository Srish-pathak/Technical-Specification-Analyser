"""Code-quality analysis.

* Ruff (external tool) is used when installed; its output is parsed from JSON.
* Built-in AST rules (TSA-QLT-*) are the *fallback* when Ruff is unavailable, so the two never
  double-report. Built-in rules are labelled source="deterministic_rule", Ruff's "static_analyzer".
"""
from __future__ import annotations

import ast
import json
import re
from typing import Optional

from app.analyzers.ast_analyzer import FUNC_TYPES, walk_shallow
from app.analyzers import tool_runner as tr
from app.schemas.findings import (CAT_QUALITY, HIGH, INFO, LOW, MEDIUM, SRC_RULE, SRC_TOOL, Finding, ToolStatus)

_SNAKE = re.compile(r"^(_*[a-z][a-z0-9_]*|__\w+__)$")
_CAPS = re.compile(r"^_*[A-Z][A-Za-z0-9]*$")


def _ev(lines: list[str], n: Optional[int]) -> str:
    return lines[n - 1].strip()[:200] if n and 0 < n <= len(lines) else ""


def builtin_quality(tree: ast.AST, source: str, path: str) -> list[Finding]:
    lines = source.splitlines()
    out: list[Finding] = []

    def add(rule, sev, node, desc, fix, conf="high"):
        ln = getattr(node, "lineno", None)
        out.append(Finding(rule_id=rule, category=CAT_QUALITY, severity=sev, file_path=path, line_number=ln,
                           column_number=(getattr(node, "col_offset", None) or 0) + 1 if ln else None,
                           description=desc, evidence=_ev(lines, ln), recommended_correction=fix,
                           source=SRC_RULE, confidence=conf, tool="builtin-ast"))

    # unused imports
    if not path.endswith("__init__.py"):
        bound: dict[str, ast.AST] = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    bound.setdefault(a.asname or a.name.split(".")[0], n)
            elif isinstance(n, ast.ImportFrom) and n.module != "__future__":
                for a in n.names:
                    if a.name != "*":
                        bound.setdefault(a.asname or a.name, n)
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        for n in ast.walk(tree):  # names exported via __all__
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets):
                used |= {e.value for e in ast.walk(n.value) if isinstance(e, ast.Constant) and isinstance(e.value, str)}
        for name, node in bound.items():
            if name not in used:
                add("TSA-QLT-001", LOW, node, f"Import '{name}' is never used.",
                    "Remove the unused import.", "medium")

    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
            add("TSA-QLT-004", LOW, n, f"Star import from '{n.module}' pollutes the namespace.",
                "Import the specific names you need.")
        elif isinstance(n, ast.ExceptHandler) and n.type is None:
            add("TSA-QLT-002", MEDIUM, n, "Bare 'except:' also catches SystemExit and KeyboardInterrupt.",
                "Catch specific exceptions (or 'except Exception').")
        elif isinstance(n, ast.ClassDef) and not _CAPS.match(n.name):
            add("TSA-QLT-005", INFO, n, f"Class '{n.name}' does not follow CapWords naming.", "Rename to CapWords.")
        elif isinstance(n, FUNC_TYPES):
            if not _SNAKE.match(n.name):
                add("TSA-QLT-005", INFO, n, f"Function '{n.name}' does not follow snake_case naming.", "Rename to snake_case.")
            defaults = list(n.args.defaults) + [d for d in n.args.kw_defaults if d is not None]
            for d in defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)) or (
                        isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id in ("list", "dict", "set")):
                    add("TSA-QLT-003", MEDIUM, d, f"Mutable default argument in '{n.name}' is shared across calls.",
                        "Use None as the default and create the object inside the function.")
            # unused local variables
            declared = {x for g in ast.walk(n) if isinstance(g, (ast.Global, ast.Nonlocal)) for x in g.names}
            if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in ("locals", "vars")
                   for c in ast.walk(n)):
                continue
            loads = {x.id for x in ast.walk(n) if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}
            seen = set()
            for s in walk_shallow(n):
                tgts = s.targets if isinstance(s, ast.Assign) else [s.target] if isinstance(s, ast.AnnAssign) and s.value else []
                for t in tgts:
                    if isinstance(t, ast.Name) and t.id not in loads and t.id not in declared \
                            and not t.id.startswith("_") and t.id not in seen:
                        seen.add(t.id)
                        add("TSA-QLT-006", LOW, s, f"Local variable '{t.id}' is assigned but never used.",
                            "Remove it or use '_' if the value is intentionally ignored.", "medium")
    return out


# --- Ruff adapter -----------------------------------------------------------------------------
_RUFF_HIGH = ("E9", "F63", "F7", "F82")


def ruff_severity(code: str) -> str:
    if code.startswith(_RUFF_HIGH):
        return HIGH
    if code in ("F401", "F841") or code.startswith(("E", "W", "N")):
        return LOW
    return MEDIUM  # other F* (pyflakes) and B* (bugbear)


def parse_ruff_json(text: str, mapping: dict[str, str], sources: dict[str, str]) -> list[Finding]:
    """Convert `ruff check --output-format json` output to Findings. Raises ValueError on bad JSON."""
    try:
        items = json.loads(text) if text.strip() else []
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ruff returned invalid JSON: {exc}")
    out = []
    for it in items:
        base = str(it.get("filename", "")).replace("\\", "/").split("/")[-1]
        path = mapping.get(base)
        if path is None:
            continue
        loc = it.get("location") or {}
        row, col = loc.get("row"), loc.get("column")
        code = it.get("code") or "RUFF"
        lines = sources.get(path, "").splitlines()
        out.append(Finding(rule_id=f"ruff:{code}", category=CAT_QUALITY, severity=ruff_severity(code), file_path=path,
                           line_number=row, column_number=col, description=str(it.get("message", ""))[:300],
                           evidence=_ev(lines, row), recommended_correction=(
                               "Apply Ruff's suggested fix." if it.get("fix") else f"See Ruff rule {code}."),
                           source=SRC_TOOL, confidence="high", tool="ruff"))
    return out


def run_ruff(files: list[tuple[str, str]], timeout: int) -> tuple[list[Finding], ToolStatus]:
    status, path = tr.cli_status("ruff")
    if not path:
        return [], status
    try:
        with tr.materialize(files) as (root, mapping):
            _, out, err = tr.run_tool([path, "check", "--isolated", "--no-cache", "--output-format", "json",
                                       "--select", "E,F,W,B,N", "."], root, timeout)
            findings = parse_ruff_json(out, mapping, dict(files))
        status.ran = True
        return findings, status
    except (tr.ToolTimeout, ValueError, OSError) as exc:
        status.note = f"Ruff failed: {exc}"
        return [], status
