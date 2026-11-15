"""Input-safety helpers. Everything here is pure string handling: nothing is executed."""
from __future__ import annotations

import posixpath
import re

IGNORED_DIRS = frozenset({
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".idea", ".vscode",
})


class UnsafePathError(ValueError):
    """Raised when an archive member path is absolute, escapes the root, or is malformed."""


def sanitize_filename(name: str) -> str:
    """Return a safe basename (no directories, no control chars)."""
    name = (name or "").replace("\\", "/").split("/")[-1]
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip().strip(".")
    name = re.sub(r"[^\w.\- ]", "_", name)
    return name[:120]


def normalize_member_path(raw: str) -> str:
    """Validate and normalise a ZIP member path; raise UnsafePathError if unsafe.

    Rejects NUL bytes, absolute paths, Windows drive letters and any '..' component.
    """
    if not raw or "\x00" in raw:
        raise UnsafePathError("empty or NUL-containing path")
    p = raw.replace("\\", "/")
    if p.startswith("/") or re.match(r"^[A-Za-z]:", p):
        raise UnsafePathError(f"absolute path not allowed: {raw!r}")
    parts = [seg for seg in p.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in parts):
        raise UnsafePathError(f"path traversal not allowed: {raw!r}")
    if not parts:
        raise UnsafePathError("empty path")
    return posixpath.join(*parts)


def has_ignored_dir(path: str) -> bool:
    return any(seg in IGNORED_DIRS for seg in path.split("/")[:-1])


def looks_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]
