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

    def __post_init__(self) -> None:
        if not self.finding_id:
            key = f"{self.rule_id}|{self.file_path}|{self.line_number}|{self.column_number}"
            self.finding_id = "F-" + hashlib.sha1(key.encode()).hexdigest()[:10]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
