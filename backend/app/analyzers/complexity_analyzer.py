"""Complexity metrics.

Uses Radon when installed (cyclomatic complexity + maintainability index). Otherwise falls back to
a built-in McCabe counter, clearly labelled "builtin-mccabe" (similar to, but not guaranteed
identical with, Radon). Decision points counted by the built-in: if/elif, ternary, for, while,
except, assert, each extra operand of and/or, each comprehension generator and its ifs, and match
cases. Nested functions are measured separately.

Severity rationale (complexity is a maintainability signal, not a defect, so severities are low):
  CC 11-20 Low (Radon grade C) | 21-30 Medium (D) | >30 High (E/F)
  length >50 lines Low, >100 Medium | nesting >4 Low, >6 Medium | >5 parameters Low
"""
from __future__ import annotations

import ast
from typing import Optional

from app.analyzers.ast_analyzer import FUNC_TYPES, ModuleStructure, walk_shallow
from app.schemas.findings import CAT_COMPLEXITY, HIGH, LOW, MEDIUM, SRC_RULE, SRC_TOOL, Finding

CC_LOW, CC_MED, CC_HIGH = 10, 20, 30
LEN_LOW, LEN_MED = 50, 100
NEST_LOW, NEST_MED = 4, 6
PARAM_MAX = 5


def mccabe(func: ast.AST) -> int:
    score = 1
    for n in walk_shallow(func):
        if isinstance(n, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.Assert)):
            score += 1
        elif isinstance(n, ast.BoolOp):
            score += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            score += 1 + len(n.ifs)
        elif hasattr(ast, "match_case") and isinstance(n, ast.match_case):
            score += 1
    return score


def _fn_nodes(tree: ast.AST) -> dict[tuple[str, int], ast.AST]:
    return {(n.name, n.lineno): n for n in ast.walk(tree) if isinstance(n, FUNC_TYPES)}


def _radon(source: str):
    """Return (cc_by_(name,lineno), mi) or raise; imports radon lazily."""
    from radon.complexity import cc_visit  # type: ignore
    from radon.metrics import mi_visit  # type: ignore
    cc = {(b.name, b.lineno): b.complexity for b in cc_visit(source) if hasattr(b, "complexity")}
    return cc, float(mi_visit(source, multi=True))


def _line(lines: list[str], n: int) -> str:
    return lines[n - 1].strip()[:200] if 0 < n <= len(lines) else ""


def analyze_complexity(tree: ast.AST, structure: ModuleStructure, source: str, use_radon: bool = True
                       ) -> tuple[list[Finding], dict, Optional[str]]:
    """Fill FunctionInfo.complexity in place; return (findings, file metrics, radon_error)."""
    nodes = _fn_nodes(tree)
    radon_cc, mi, tool, radon_error = {}, None, "builtin-mccabe", None
    if use_radon:
        try:
            radon_cc, mi = _radon(source)
            tool = "radon"
        except ImportError:
            radon_error = None
        except Exception as exc:  # radon failed on this file; fall back honestly
            radon_error = f"radon failed ({type(exc).__name__}); built-in McCabe used for this file"
    findings: list[Finding] = []
    lines = source.splitlines()
    fp = structure.path
    for f in structure.functions:
        key = (f.name, f.lineno)
        if tool == "radon" and key in radon_cc:
            f.complexity, f.complexity_tool = int(radon_cc[key]), "radon"
        else:
            f.complexity, f.complexity_tool = mccabe(nodes[key]), "builtin-mccabe"
        src = SRC_TOOL if f.complexity_tool == "radon" else SRC_RULE

        def add(rule, sev, desc, fix, ev):
            findings.append(Finding(rule_id=rule, category=CAT_COMPLEXITY, severity=sev, file_path=fp,
                                    line_number=f.lineno, column_number=None, description=desc,
                                    evidence=ev, recommended_correction=fix, source=src,
                                    confidence="high", tool=f.complexity_tool))
        sig = _line(lines, f.lineno)
        if f.complexity > CC_LOW:
            sev = HIGH if f.complexity > CC_HIGH else MEDIUM if f.complexity > CC_MED else LOW
            add("TSA-CPX-001", sev, f"Function '{f.qualname}' has cyclomatic complexity {f.complexity} (threshold {CC_LOW}).",
                "Split into smaller functions or simplify branching.", f"{sig}  # CC={f.complexity}")
        if f.length > LEN_LOW:
            add("TSA-CPX-002", MEDIUM if f.length > LEN_MED else LOW,
                f"Function '{f.qualname}' is {f.length} lines long (threshold {LEN_LOW}).",
                "Extract cohesive blocks into helper functions.", f"{sig}  # {f.length} lines")
        if f.max_nesting > NEST_LOW:
            add("TSA-CPX-003", MEDIUM if f.max_nesting > NEST_MED else LOW,
                f"Function '{f.qualname}' nests control structures {f.max_nesting} levels deep (threshold {NEST_LOW}).",
                "Use early returns/guard clauses or extract inner blocks.", f"{sig}  # nesting={f.max_nesting}")
        if len([p for p in f.params if p not in ("self", "cls")]) > PARAM_MAX:
            add("TSA-CPX-004", LOW,
                f"Function '{f.qualname}' takes {len(f.params)} parameters (threshold {PARAM_MAX}).",
                "Group related parameters into a dataclass or object.", sig)
    ccs = [f.complexity for f in structure.functions]
    metrics = {
        "functions": len(ccs), "complexity_sum": sum(ccs), "max_complexity": max(ccs, default=0),
        "avg_complexity": round(sum(ccs) / len(ccs), 2) if ccs else None,
        "maintainability_index": round(mi, 2) if mi is not None else None, "tool": tool,
    }
    return findings, metrics, radon_error
