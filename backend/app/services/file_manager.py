"""Validation of pasted code and single-file uploads. Content is only read, never executed."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Optional

from app.core.config import Settings, get_settings
from app.core.security import looks_binary, sanitize_filename

# extension -> (language, kind). kind "source" = code; "support" = docs/config kept for documentation.
EXT_INFO: dict[str, tuple[str, str]] = {
    ".py": ("python", "source"), ".js": ("javascript", "source"), ".ts": ("typescript", "source"),
    ".java": ("java", "source"), ".c": ("c", "source"), ".cpp": ("cpp", "source"),
    ".cs": ("csharp", "source"), ".go": ("go", "source"), ".rs": ("rust", "source"),
    ".php": ("php", "source"),
    ".txt": ("text", "support"), ".md": ("markdown", "support"), ".rst": ("text", "support"),
    ".toml": ("toml", "support"), ".cfg": ("config", "support"), ".ini": ("config", "support"),
    ".json": ("json", "support"), ".yml": ("yaml", "support"), ".yaml": ("yaml", "support"),
}
LANG_EXT = {"python": ".py", "javascript": ".js", "typescript": ".ts", "java": ".java", "c": ".c",
            "cpp": ".cpp", "csharp": ".cs", "go": ".go", "rust": ".rs", "php": ".php"}
# Languages with a deterministic analyzer implemented. Others are inventoried only.
ANALYZABLE_LANGUAGES = frozenset({"python"})

_ALLOWED_MIME = {
    "application/octet-stream", "application/json", "application/javascript", "application/x-javascript",
    "application/xml", "application/x-yaml", "application/toml", "application/x-httpd-php",
    "application/x-python-code", "application/typescript", "application/x-sh",
}
_ZIP_MIME = {"application/zip", "application/x-zip-compressed", "application/x-zip", "application/octet-stream"}


class InputValidationError(Exception):
    """A user-input problem with a stable machine code (maps to HTTP 4xx)."""

    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


@dataclass
class SourceFile:
    path: str
    content: str
    language: str
    kind: str = "source"

    @property
    def size(self) -> int:
        return len(self.content.encode("utf-8", errors="replace"))

    @property
    def line_count(self) -> int:
        return len(self.content.splitlines())


def extension_of(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""


def classify_path(path: str) -> Optional[tuple[str, str]]:
    return EXT_INFO.get(extension_of(path))


def mime_allowed(content_type: Optional[str]) -> bool:
    if not content_type:
        return True  # browsers often omit it; extension + content checks still apply
    ct = content_type.split(";")[0].strip().lower()
    return ct.startswith("text/") or ct in _ALLOWED_MIME


def zip_mime_allowed(content_type: Optional[str]) -> bool:
    return not content_type or content_type.split(";")[0].strip().lower() in _ZIP_MIME


def decode_text(data: bytes) -> str:
    """Strict UTF-8 (BOM tolerated). Raises InputValidationError otherwise."""
    if looks_binary(data):
        raise InputValidationError("binary_content", "File looks binary (contains NUL bytes); only text source is accepted.")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InputValidationError("not_utf8", "File is not valid UTF-8 text.")


def detect_language(filename: str, content: str) -> str:
    info = classify_path(filename) if filename else None
    if info and info[1] == "source":
        return info[0]
    c = content
    if re.search(r"^\s*(def|class)\s+\w+.*:\s*$", c, re.M) or re.search(
            r"^\s*(import\s+[\w.]+(\s+as\s+\w+)?\s*$|from\s+[\w.]+\s+import\s)", c, re.M):
        return "python"
    if "<?php" in c:
        return "php"
    if re.search(r"^\s*#include\s*<", c, re.M):
        return "cpp" if re.search(r"std::|class\s+\w+\s*\{|template\s*<", c) else "c"
    if re.search(r"^\s*package\s+main\b", c, re.M):
        return "go"
    if re.search(r"\bfn\s+\w+\s*\(|\blet\s+mut\b", c):
        return "rust"
    if re.search(r"\b(public|private)\s+(static\s+)?(class|void)\b", c):
        return "csharp" if re.search(r"\busing\s+System\b|\bnamespace\b", c) else "java"
    if re.search(r"\b(function\s+\w+\s*\(|const\s+\w+\s*=|=>)", c):
        return "typescript" if re.search(r":\s*(string|number|boolean)\b|\binterface\s+\w+", c) else "javascript"
    try:
        ast.parse(c)
        return "python" if c.strip() else "unknown"
    except (SyntaxError, ValueError, RecursionError):
        return "unknown"


def _check_text(data: bytes, limit: int) -> str:
    if len(data) == 0:
        raise InputValidationError("empty_file", "The file is empty.")
    if len(data) > limit:
        raise InputValidationError("file_too_large", f"File exceeds the {limit:,}-byte limit.", 413)
    text = decode_text(data)
    if not text.strip():
        raise InputValidationError("empty_file", "The file contains only whitespace.")
    return text


def validate_upload(filename: str, data: bytes, content_type: Optional[str] = None,
                    settings: Optional[Settings] = None) -> SourceFile:
    """Validate one uploaded source file (extension, MIME, size, binary, encoding)."""
    s = settings or get_settings()
    safe = sanitize_filename(filename)
    if not safe:
        raise InputValidationError("bad_filename", "Missing or invalid file name.")
    info = classify_path(safe)
    if info is None:
        raise InputValidationError("unsupported_extension",
                                   f"Unsupported file type '{extension_of(safe) or safe}'.", 415)
    if not mime_allowed(content_type):
        raise InputValidationError("unsupported_mime", f"MIME type '{content_type}' is not accepted.", 415)
    text = _check_text(data, s.max_upload_bytes)
    return SourceFile(path=safe, content=text, language=info[0], kind=info[1])


def build_pasted_source(code: str, language: Optional[str] = None, filename: Optional[str] = None,
                        settings: Optional[Settings] = None) -> SourceFile:
    """Validate pasted code. `language` may be None/'auto' to detect."""
    s = settings or get_settings()
    text = _check_text((code or "").encode("utf-8"), s.max_upload_bytes)
    lang = (language or "auto").strip().lower()
    if lang in ("auto", ""):
        lang = detect_language(filename or "", text)
    if lang not in LANG_EXT and lang not in ("unknown", "text"):
        raise InputValidationError("unsupported_language", f"Unsupported language '{lang}'.", 415)
    name = sanitize_filename(filename or "") or ("pasted_code" + LANG_EXT.get(lang, ".txt"))
    return SourceFile(path=name, content=text, language=lang, kind="source")
