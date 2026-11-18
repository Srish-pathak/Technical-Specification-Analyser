"""Shared structured finding schema (spec section 9.5)."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Optional

# Severity levels and the rationale behind them (documented per spec 9.5).
CRITICAL, HIGH, MEDIUM, LOW, INFO = "Critical", "High", "Medium", "Low", "Informational"
SEVERITY_ORDER = [CRITICAL, HIGH, MEDIUM, LOW, INFO]
SEVERITY_RATIONALE = {
    CRITICAL: "Certain to break the program or directly exploitable; fix before release.",
    HIGH: "Code cannot be parsed, or a recognised dangerous construct (eval/exec, shell=True) is present.",
    MEDIUM: "Likely defect, risky pattern, or substantially hard-to-maintain code.",
    LOW: "Maintainability or style concern with limited immediate risk.",
    INFO: "Observation only; no action strictly required.",
}

# Finding sources (spec 9.5)
SRC_TOOL = "static_analyzer"        # output of an external static tool (ruff, bandit)
SRC_RULE = "deterministic_rule"     # built-in AST rule implemented in this project
SRC_AI = "ai_agent"
SRC_HUMAN = "human_verification"

CAT_SYNTAX, CAT_QUALITY, CAT_COMPLEXITY, CAT_SECURITY = "syntax", "quality", "complexity", "security"

RULE_TITLES = {
    "bandit:B307": "Use of possibly insecure function (eval/exec)",
    "bandit:B101": "Use of assert detected in production code",
    "bandit:B602": "Subprocess call with shell=True",
    "bandit:B603": "Subprocess call without shell=True but with untrusted input",
    "bandit:B105": "Hardcoded password string detected",
    "bandit:B106": "Hardcoded password parameter detected",
    "bandit:B108": "Hardcoded temporary file path",
    "bandit:B311": "Standard pseudo-random generator not suitable for cryptographic use",
    "bandit:B404": "Import of subprocess module",
    "bandit:B110": "Try, Except, Pass detected (silent error suppression)",
    "bandit:B112": "Try, Except, Continue detected",
    "ruff:E501": "Line length exceeds maximum threshold",
    "ruff:F401": "Unused import statement",
    "ruff:F841": "Local variable defined but never used",
    "ruff:W292": "No newline at end of file",
    "ruff:W293": "Blank line contains trailing whitespace",
    "ruff:E711": "Comparison to None using equality operator instead of 'is'",
    "ruff:E712": "Comparison to True/False using equality operator instead of 'is'",
    "ruff:E722": "Bare except clause used",
    "ruff:E402": "Module level import not at top of file",
    "ruff:F403": "Star import used (wildcard import)",
    "TSA-CPX-001": "Excessive Cyclomatic Complexity",
    "TSA-SYN-001": "Python Syntax Error",
    "TSA-SEC-001": "Arbitrary Code Execution via eval() or exec()",
    "eslint:no-eval": "Arbitrary Code Execution via eval()",
    "eslint:no-implied-eval": "Implied eval via String in Timer Function",
    "eslint:no-unsafe-innerhtml": "Direct innerHTML Assignment (XSS Risk)",
    "eslint:no-debugger": "Unexpected 'debugger' Statement",
    "eslint:no-alert": "Synchronous UI Dialog (alert/confirm/prompt)",
    "eslint:eqeqeq": "Loose Equality Comparison (eqeqeq)",
    "eslint:no-var": "Unexpected 'var' Declaration",
    "eslint:no-console": "Unexpected Console Statement in Production Code",
    "eslint:complexity": "Function has Excessive Cyclomatic Complexity",
    "eslint:syntax-error": "JavaScript Syntax Parsing Error",
}

WHY_BY_CATEGORY = {
    "security": "Executing untrusted dynamic expressions or using insecure functions can allow arbitrary code execution, unauthorized data access, or privilege escalation.",
    "complexity": "Functions with high cyclomatic complexity have many execution branches, making them error-prone, difficult to understand, and hard to unit test thoroughly.",
    "quality": "Violating standard code quality and style guidelines increases technical debt, degrades maintainability, and can hide subtle bugs in production.",
    "syntax": "Syntax errors prevent the Python bytecode compiler from executing or analyzing the file.",
}


@dataclass
class Finding:
    rule_id: str
    category: str
    severity: str
    file_path: str
    line_number: Optional[int]
    column_number: Optional[int]
    description: str
    evidence: str
    recommended_correction: str
    source: str
    confidence: str = "high"           # high | medium | low
    tool: str = "builtin"              # which engine produced it (extra field beyond spec list)
    finding_id: str = ""
    title: str = ""
    why: str = ""
    reference: str = ""

    def __post_init__(self) -> None:
        if not self.finding_id:
            key = f"{self.rule_id}|{self.file_path}|{self.line_number}|{self.column_number}"
            self.finding_id = "F-" + hashlib.sha1(key.encode()).hexdigest()[:10]

        if not self.title:
            if self.rule_id in RULE_TITLES:
                self.title = RULE_TITLES[self.rule_id]
            elif self.description:
                first = self.description.split(".")[0].strip()
                self.title = (first[:70] + "...") if len(first) > 70 else (first + "." if not first.endswith(".") else first)
            else:
                self.title = f"{self.rule_id} Finding"

        if not self.why:
            cat = self.category.lower() if self.category else "quality"
            self.why = WHY_BY_CATEGORY.get(cat, WHY_BY_CATEGORY["quality"])

        if not self.reference:
            if self.rule_id.startswith("bandit:"):
                tid = self.rule_id.split(":")[-1].lower()
                self.reference = f"https://bandit.readthedocs.io/en/latest/plugins/{tid}.html"
            elif self.rule_id.startswith("ruff:"):
                code = self.rule_id.split(":")[-1].lower()
                self.reference = f"https://docs.astral.sh/ruff/rules/{code}/"
            elif self.rule_id.startswith("eslint:"):
                code = self.rule_id.split(":")[-1].lower()
                self.reference = f"https://eslint.org/docs/latest/rules/{code}"
            elif "cpx" in self.rule_id.lower() or "complexity" in self.category.lower():
                self.reference = "https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["rule"] = self.rule_id
        d["file"] = self.file_path
        d["line"] = self.line_number
        d["code"] = self.evidence
        d["fix"] = self.recommended_correction
        d["ref"] = self.reference
        d["explanation"] = self.description
        d["title"] = self.title
        d["why"] = self.why
        return d


@dataclass
class ToolStatus:
    """Honest record of whether a tool was available and actually ran."""
    name: str
    available: bool
    ran: bool = False
    version: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return counts
