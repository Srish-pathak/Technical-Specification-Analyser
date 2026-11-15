"""Security analysis.

Two layers, kept separate by `source`:
  * built-in deterministic AST rules (TSA-SEC-*), source="deterministic_rule"
  * Bandit (external tool, when installed), source="static_analyzer"
Nothing here is an AI judgement. Secret values are never echoed into evidence.
"""
from __future__ import annotations

import ast
import json
import re
from typing import Optional

from app.analyzers.ast_analyzer import ModuleStructure, dotted_name
from app.analyzers import tool_runner as tr
from app.schemas.findings import (CAT_SECURITY, HIGH, LOW, MEDIUM, SRC_RULE, SRC_TOOL, Finding, ToolStatus)

_SECRET_NAME = re.compile(r"(^|_)(password|passwd|pwd|secret|api_?key|apikey|token|private_?key|access_?key|auth_?key)($|_)", re.I)
_NOT_SECRET_SUFFIX = ("_url", "_path", "_file", "_name", "_type", "_field", "_header", "_env", "_var")
_PLACEHOLDER = re.compile(r"(change.?me|your[_-]|xxx|example|placeholder|<.*>|\$\{|%\(|^\s*$|^none$|^null$)", re.I)
_SUBPROCESS = {"subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output", "subprocess.Popen"}
_UNSAFE_DESER = {"pickle.load", "pickle.loads", "cPickle.load", "cPickle.loads", "marshal.load", "marshal.loads",
                 "dill.load", "dill.loads", "shelve.open", "yaml.unsafe_load"}
_REQUESTS = {f"requests.{m}" for m in ("get", "post", "put", "delete", "head", "patch", "request")} | {
    "httpx.get", "httpx.post", "httpx.request"}

# Which Bandit tests duplicate a built-in rule (used to drop the built-in duplicate).
BANDIT_EQUIVALENTS = {
    "TSA-SEC-001": {"B307", "B102"}, "TSA-SEC-002": {"B602", "B603", "B604", "B605", "B606", "B607"},
    "TSA-SEC-003": {"B301", "B302", "B506"}, "TSA-SEC-004": {"B105", "B106", "B107"},
    "TSA-SEC-005": {"B501"}, "TSA-SEC-006": {"B303", "B324"}, "TSA-SEC-007": {"B608"}, "TSA-SEC-008": {"B306"},
}


def _aliases(structure: ModuleStructure) -> dict[str, str]:
    m: dict[str, str] = {}
    for imp in structure.imports:
        m.update(imp.alias_map)
    return m


def _canon(name: Optional[str], aliases: dict[str, str]) -> Optional[str]:
    if not name:
        return None
    head, _, rest = name.partition(".")
    if head in aliases:
        return aliases[head] + ("." + rest if rest else "")
    return name


def _kw(call: ast.Call, key: str) -> Optional[ast.expr]:
    return next((k.value for k in call.keywords if k.arg == key), None)


def _is_const(n: Optional[ast.AST]) -> bool:
    return isinstance(n, ast.Constant)


def _dynamic_sql(arg: ast.AST) -> bool:
    if isinstance(arg, ast.JoinedStr):
        return any(isinstance(v, ast.FormattedValue) for v in arg.values)
    if isinstance(arg, ast.BinOp) and isinstance(arg.op, (ast.Mod, ast.Add)):
        return not (_is_const(arg.left) and _is_const(arg.right))
    return isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "format" and _is_const(arg.func.value)


def builtin_security(tree: ast.AST, source: str, structure: ModuleStructure) -> list[Finding]:
    path, lines, aliases = structure.path, source.splitlines(), _aliases(structure)
    out: list[Finding] = []

    def add(rule, sev, node, desc, fix, conf="high", evidence=None):
        ln = getattr(node, "lineno", None)
        ev = evidence if evidence is not None else (lines[ln - 1].strip()[:200] if ln and ln <= len(lines) else "")
        out.append(Finding(rule_id=rule, category=CAT_SECURITY, severity=sev, file_path=path, line_number=ln,
                           column_number=(getattr(node, "col_offset", 0) or 0) + 1 if ln else None,
                           description=desc, evidence=ev, recommended_correction=fix,
                           source=SRC_RULE, confidence=conf, tool="builtin-ast"))

    def secret_check(name: str, value: Optional[ast.AST], node: ast.AST):
        low = name.lower()
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            return
        v = value.value
        if (_SECRET_NAME.search(low) and not low.endswith(_NOT_SECRET_SUFFIX) and len(v) >= 6
                and not _PLACEHOLDER.search(v) and not v.lower().startswith(("http://", "https://"))):
            add("TSA-SEC-004", MEDIUM, node, f"Possible hardcoded secret assigned to '{name}'.",
                "Load secrets from environment variables or a secrets manager.", "medium",
                evidence=f"{name} = <string literal redacted>")

    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    secret_check(t.id, n.value, n)
                elif isinstance(t, ast.Attribute):
                    secret_check(t.attr, n.value, n)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
            secret_check(n.target.id, n.value, n)
        elif isinstance(n, ast.Call):
            for k in n.keywords:
                if k.arg:
                    secret_check(k.arg, k.value, n)
            raw = dotted_name(n.func)
            name = _canon(raw, aliases)
            arg0 = n.args[0] if n.args else None
            if name in ("eval", "exec") and raw not in aliases:
                lit = _is_const(arg0)
                add("TSA-SEC-001", MEDIUM if lit else HIGH, n, f"Use of {name}() can execute arbitrary code.",
                    "Avoid eval/exec; use ast.literal_eval or explicit dispatch.", "medium" if lit else "high")
            elif name in ("os.system", "os.popen"):
                add("TSA-SEC-002", MEDIUM if _is_const(arg0) else HIGH, n, f"{name}() runs a command through the shell.",
                    "Use subprocess with an argument list and shell=False.")
            elif name in _SUBPROCESS:
                sh = _kw(n, "shell")
                if isinstance(sh, ast.Constant) and sh.value is True:
                    add("TSA-SEC-002", MEDIUM if _is_const(arg0) else HIGH, n,
                        f"{name}(..., shell=True) enables shell injection when input is not fully trusted.",
                        "Pass an argument list and omit shell=True.")
            elif name in _UNSAFE_DESER:
                add("TSA-SEC-003", MEDIUM, n, f"{name}() can execute code while deserialising untrusted data.",
                    "Use a safe format (JSON) or verify data origin.")
            elif name == "yaml.load":
                loader = _kw(n, "Loader") or (n.args[1] if len(n.args) > 1 else None)
                lname = dotted_name(loader) if loader is not None else None
                if not lname or lname.split(".")[-1] not in ("SafeLoader", "CSafeLoader"):
                    add("TSA-SEC-003", MEDIUM, n, "yaml.load() without SafeLoader can construct arbitrary objects.",
                        "Use yaml.safe_load().")
            elif name in _REQUESTS:
                v = _kw(n, "verify")
                if isinstance(v, ast.Constant) and v.value is False:
                    add("TSA-SEC-005", MEDIUM, n, "TLS certificate verification is disabled (verify=False).",
                        "Remove verify=False or supply a CA bundle path.")
            elif name in ("hashlib.md5", "hashlib.sha1"):
                uf = _kw(n, "usedforsecurity")
                if not (isinstance(uf, ast.Constant) and uf.value is False):
                    add("TSA-SEC-006", LOW, n, f"{name} is a weak hash; unsuitable for security purposes.",
                        "Use SHA-256 or better (or pass usedforsecurity=False for non-security checksums).", "medium")
            elif name == "tempfile.mktemp":
                add("TSA-SEC-008", LOW, n, "tempfile.mktemp() is race-prone.", "Use tempfile.mkstemp() or NamedTemporaryFile().")
            if isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany") and arg0 is not None \
                    and _dynamic_sql(arg0):
                add("TSA-SEC-007", MEDIUM, n, "SQL query built with string formatting may allow SQL injection.",
                    "Use parameterised queries (placeholders) instead.", "medium")
    return out


# --- Bandit adapter ---------------------------------------------------------------------------
_BANDIT_SEV = {"HIGH": HIGH, "MEDIUM": MEDIUM, "LOW": LOW}


def parse_bandit_json(text: str, mapping: dict[str, str], sources: dict[str, str]) -> list[Finding]:
    try:
        data = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"Bandit returned invalid JSON: {exc}")
    out = []
    for it in data.get("results", []):
        base = str(it.get("filename", "")).replace("\\", "/").split("/")[-1]
        path = mapping.get(base)
        if path is None:
            continue
        ln = it.get("line_number")
        lines = sources.get(path, "").splitlines()
        tid = it.get("test_id", "B000")
        out.append(Finding(
            rule_id=f"bandit:{tid}", category=CAT_SECURITY,
            severity=_BANDIT_SEV.get(str(it.get("issue_severity", "")).upper(), LOW), file_path=path,
            line_number=ln, column_number=(it.get("col_offset") + 1) if isinstance(it.get("col_offset"), int) else None,
            description=str(it.get("issue_text", ""))[:300],
            evidence=lines[ln - 1].strip()[:200] if ln and 0 < ln <= len(lines) else "",
            recommended_correction=str(it.get("more_info") or f"See Bandit test {tid} ({it.get('test_name', '')})."),
            source=SRC_TOOL, confidence=str(it.get("issue_confidence", "medium")).lower(), tool="bandit"))
    return out


def run_bandit(files: list[tuple[str, str]], timeout: int) -> tuple[list[Finding], ToolStatus]:
    status, path = tr.cli_status("bandit")
    if not path:
        return [], status
    try:
        with tr.materialize(files) as (root, mapping):
            _, out, _ = tr.run_tool([path, "-r", ".", "-f", "json", "-q"], root, timeout)  # exit 1 == issues found
            findings = parse_bandit_json(out, mapping, dict(files))
        status.ran = True
        return findings, status
    except (tr.ToolTimeout, ValueError, OSError) as exc:
        status.note = f"Bandit failed: {exc}"
        return [], status


def merge_security(builtin: list[Finding], bandit: list[Finding]) -> list[Finding]:
    """Drop a built-in finding when Bandit reported the equivalent test on the same line."""
    keep = []
    for f in builtin:
        equiv = BANDIT_EQUIVALENTS.get(f.rule_id, set())
        dup = any(b.file_path == f.file_path and b.line_number == f.line_number and b.rule_id.split(":")[-1] in equiv
                  for b in bandit)
        if not dup:
            keep.append(f)
    return keep + bandit
