"""Deterministic static analyzer for JavaScript and TypeScript source files."""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from app.analyzers.tool_runner import check_node_syntax
from app.schemas.findings import (
    CAT_COMPLEXITY,
    CAT_QUALITY,
    CAT_SECURITY,
    CAT_SYNTAX,
    CRITICAL,
    HIGH,
    INFO,
    LOW,
    MEDIUM,
    Finding,
    ToolStatus,
)


def _check_syntax_with_node(content: str, rel_path: str) -> Optional[Finding]:
    """Run `node --check` via tool_runner to detect syntax errors safely."""
    fname = "temp.ts" if rel_path.endswith((".ts", ".tsx")) else "temp.js"
    res = check_node_syntax(content, fname)
    if not res:
        return None
    ret, stdout, stderr = res
    err_out = stderr or stdout or ""
    # Only report when there is an actual SyntaxError from the JavaScript engine
    if ret != 0 and "SyntaxError" in err_out:
        line_match = re.search(r":(\d+)(?::(\d+))?", err_out)
        lineno = int(line_match.group(1)) if line_match else 1
        colno = int(line_match.group(2)) if line_match and line_match.group(2) else None
        lines = content.splitlines()
        evidence = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
        err_summary = err_out.strip().splitlines()[-1] if err_out.strip() else "JavaScript syntax error"
        return Finding(
            rule_id="eslint:syntax-error",
            category=CAT_SYNTAX,
            severity=CRITICAL,
            file_path=rel_path,
            line_number=lineno,
            column_number=colno,
            description=f"JavaScript syntax parsing error: {err_summary}",
            evidence=evidence,
            recommended_correction="Fix JavaScript syntax error, unclosed brackets, or invalid tokens.",
            source="static_analyzer",
            tool="node-syntax",
            title="JavaScript Syntax Parsing Error",
            why="Syntax errors prevent JavaScript execution in the runtime environment or browser engine.",
            reference="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors",
        )
    return None


def analyze_javascript_file(content: str, rel_path: str) -> Tuple[List[Finding], dict]:
    """Analyze a single JavaScript/TypeScript file using deterministic static rules."""
    findings: List[Finding] = []

    # 1. Syntax check via node --check
    syntax_err = _check_syntax_with_node(content, rel_path)
    if syntax_err:
        findings.append(syntax_err)
        return findings, {
            "functions": 0,
            "complexity_sum": 0,
            "max_complexity": 0,
            "maintainability_index": 20.0,
            "tool": "node-syntax",
        }

    lines = content.splitlines()
    in_block_comment = False

    # Counters for complexity estimation
    branch_count = 0
    fn_count = 0

    for idx, raw_line in enumerate(lines, 1):
        line = raw_line.strip()

        # Handle multiline comments /* ... */
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
                line = line.split("*/", 1)[1].strip()
            else:
                continue

        if "/*" in line:
            if "*/" in line:
                line = re.sub(r"/\*.*?\*/", "", line).strip()
            else:
                in_block_comment = True
                line = line.split("/*", 1)[0].strip()

        # Strip single-line comments // ...
        if "//" in line:
            line = line.split("//", 1)[0].strip()

        if not line:
            continue

        # Count functions
        if re.search(r"\bfunction\b|\b=>\b|\b(async\s+)?function\*", line):
            fn_count += 1

        # Count branches for complexity
        branches_in_line = len(re.findall(r"\b(if|else\s+if|for|while|catch|case)\b|(?<!=)==(?!=)|(?<!\!)!=(?!=)|&&|\|\||\?", line))
        branch_count += branches_in_line

        # 1. Rule: eslint:no-eval (CRITICAL Security)
        if re.search(r"\beval\s*\(", line):
            findings.append(Finding(
                rule_id="eslint:no-eval",
                category=CAT_SECURITY,
                severity=CRITICAL,
                file_path=rel_path,
                line_number=idx,
                column_number=line.find("eval") + 1,
                description="eval() introduces remote code execution and arbitrary script execution risks.",
                evidence=raw_line.strip()[:200],
                recommended_correction="Replace eval() with JSON.parse() or a safe parser.",
                source="static_analyzer",
                tool="eslint-rules",
                title="Arbitrary Code Execution via eval()",
                why="eval() can execute untrusted user strings with full script privileges, leading to DOM-based XSS or remote execution.",
                reference="https://eslint.org/docs/latest/rules/no-eval",
            ))

        # 2. Rule: eslint:no-implied-eval (CRITICAL Security)
        if re.search(r"\b(setTimeout|setInterval)\s*\(\s*[\"']", line):
            findings.append(Finding(
                rule_id="eslint:no-implied-eval",
                category=CAT_SECURITY,
                severity=CRITICAL,
                file_path=rel_path,
                line_number=idx,
                column_number=1,
                description="Passing a string to setTimeout/setInterval introduces implied eval execution.",
                evidence=raw_line.strip()[:200],
                recommended_correction="Pass a function or arrow callback instead: () => { ... }",
                source="static_analyzer",
                tool="eslint-rules",
                title="Implied eval via String in Timer Function",
                why="Passing strings to timer functions evaluates dynamically similarly to eval(), creating injection vectors.",
                reference="https://eslint.org/docs/latest/rules/no-implied-eval",
            ))

        # 3. Rule: eslint:no-unsafe-innerhtml (WARNING Security)
        # Exclude safe innerHTML clears like `el.innerHTML = ""` or `el.innerHTML = ''`
        if re.search(r"\.(innerHTML|outerHTML)\s*=", line):
            is_clear = bool(re.search(r"\.(innerHTML|outerHTML)\s*=\s*([\"']\s*[\"']|null|undefined);?", line))
            if not is_clear:
                findings.append(Finding(
                    rule_id="eslint:no-unsafe-innerhtml",
                    category=CAT_SECURITY,
                    severity=MEDIUM,
                    file_path=rel_path,
                    line_number=idx,
                    column_number=line.find("innerHTML") + 1 if "innerHTML" in line else line.find("outerHTML") + 1,
                    description="Direct assignment to innerHTML/outerHTML with dynamic content can cause Cross-Site Scripting (XSS).",
                    evidence=raw_line.strip()[:200],
                    recommended_correction="Use element.textContent or element.replaceChildren(), or sanitize with DOMPurify.",
                    source="static_analyzer",
                    tool="eslint-rules",
                    title="Direct innerHTML Assignment (XSS Risk)",
                    why="Assigning untrusted or unsanitized strings directly to innerHTML bypasses HTML encoding and enables XSS attacks.",
                    reference="https://owasp.org/www-community/attacks/xss/",
                ))

        # 4. Rule: eslint:no-debugger (WARNING Quality)
        if re.search(r"\bdebugger\b", line):
            findings.append(Finding(
                rule_id="eslint:no-debugger",
                category=CAT_QUALITY,
                severity=MEDIUM,
                file_path=rel_path,
                line_number=idx,
                column_number=line.find("debugger") + 1,
                description="Unexpected 'debugger' statement detected.",
                evidence=raw_line.strip()[:200],
                recommended_correction="Remove debugger statement prior to production deployment.",
                source="static_analyzer",
                tool="eslint-rules",
                title="Unexpected 'debugger' Statement",
                why="debugger statements force developer devtools to pause and freeze page execution in production.",
                reference="https://eslint.org/docs/latest/rules/no-debugger",
            ))

        # 5. Rule: eslint:no-alert (WARNING Quality)
        if re.search(r"\b(alert|confirm|prompt)\s*\(", line):
            findings.append(Finding(
                rule_id="eslint:no-alert",
                category=CAT_QUALITY,
                severity=LOW,
                file_path=rel_path,
                line_number=idx,
                column_number=1,
                description="Synchronous UI dialog (alert/confirm/prompt) detected.",
                evidence=raw_line.strip()[:200],
                recommended_correction="Replace blocking modal alerts with custom UI toast notifications or modal components.",
                source="static_analyzer",
                tool="eslint-rules",
                title="Synchronous UI Dialog (alert/confirm/prompt)",
                why="Modal dialogs like alert() block the browser main thread and create poor user experience.",
                reference="https://eslint.org/docs/latest/rules/no-alert",
            ))

        # 6. Rule: eslint:eqeqeq (WARNING Quality)
        # Avoid matching arrow functions '=>' or comments
        if re.search(r"(?<!=)==(?!=)", line) or re.search(r"(?<!\!)!=(?!=)", line):
            # Verify it's not part of an arrow or regex
            eq_match = re.search(r"(?<!=)==(?!=)|(?<!\!)!=(?!=)", line)
            if eq_match:
                findings.append(Finding(
                    rule_id="eslint:eqeqeq",
                    category=CAT_QUALITY,
                    severity=LOW,
                    file_path=rel_path,
                    line_number=idx,
                    column_number=eq_match.start() + 1,
                    description="Expected strict equality operator ('===' or '!==') instead of loose comparison.",
                    evidence=raw_line.strip()[:200],
                    recommended_correction="Replace '==' with '===' or '!=' with '!==' to avoid implicit type coercion.",
                    source="static_analyzer",
                    tool="eslint-rules",
                    title="Loose Equality Comparison (eqeqeq)",
                    why="Implicit type coercion with loose equality operators causes subtle truthiness bugs and unexpected conversions.",
                    reference="https://eslint.org/docs/latest/rules/eqeqeq",
                ))

        # 7. Rule: eslint:no-var (INFORMATIONAL Quality)
        if re.search(r"\bvar\s+[a-zA-Z_$][a-zA-Z0-9_$]*\b", line):
            findings.append(Finding(
                rule_id="eslint:no-var",
                category=CAT_QUALITY,
                severity=INFO,
                file_path=rel_path,
                line_number=idx,
                column_number=line.find("var") + 1,
                description="Variable declared with 'var'; modern JavaScript recommends 'let' or 'const'.",
                evidence=raw_line.strip()[:200],
                recommended_correction="Replace 'var' with 'const' (for immutable bindings) or 'let' (for re-assigned variables).",
                source="static_analyzer",
                tool="eslint-rules",
                title="Unexpected 'var' Declaration",
                why="'var' is function-scoped and hoisted, which frequently causes scope leakage and accidental variable shadowing.",
                reference="https://eslint.org/docs/latest/rules/no-var",
            ))

    # Metrics calculation
    total_lines = len(lines)
    avg_complexity = max(1.0, round((branch_count + fn_count) / max(1, fn_count), 1))
    # Maintainability index approximation: 100 - (0.5 * lines/10) - (2 * avg_complexity)
    mi = max(20.0, min(100.0, round(100.0 - (total_lines * 0.05) - (avg_complexity * 2.5), 1)))

    return findings, {
        "functions": max(1, fn_count),
        "complexity_sum": branch_count,
        "max_complexity": int(avg_complexity * 2),
        "avg_complexity": avg_complexity,
        "maintainability_index": mi,
        "tool": "eslint-rules",
    }
