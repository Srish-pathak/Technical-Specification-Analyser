"""Detection and safe invocation of external *static* tools (ruff, bandit).

Tools are run on a private temporary copy of the files with numbered names (so user-supplied file
names never reach the filesystem), via an argument list (no shell), with a timeout and a minimal
environment. The analysed code itself is never imported or executed.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from app.schemas.findings import ToolStatus


class ToolTimeout(Exception):
    pass


def find_tool(name: str) -> Optional[str]:
    return shutil.which(name)


def tool_version(path: str) -> str:
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10, shell=False)
        return (r.stdout or r.stderr).strip().splitlines()[0][:80] if (r.stdout or r.stderr) else ""
    except Exception:
        return ""


def radon_status() -> ToolStatus:
    try:
        import radon  # noqa: F401
        return ToolStatus("radon", True, False, getattr(radon, "__version__", ""), "")
    except Exception:
        return ToolStatus("radon", False, False, "", "Not installed; using built-in McCabe fallback, no maintainability index.")


def cli_status(name: str) -> tuple[ToolStatus, Optional[str]]:
    path = find_tool(name)
    if not path:
        return ToolStatus(name, False, False, "", f"{name} is not installed; it was not run."), None
    return ToolStatus(name, True, False, tool_version(path), ""), path


@contextmanager
def materialize(files: list[tuple[str, str]]) -> Iterator[tuple[Path, dict[str, str]]]:
    """Write (path, content) pairs to a private temp dir as f0.py, f1.py ... ; yield (dir, name->orig)."""
    with tempfile.TemporaryDirectory(prefix="tsa_") as tmp:
        root = Path(tmp)
        os.chmod(root, 0o700)
        mapping: dict[str, str] = {}
        for i, (orig, content) in enumerate(files):
            name = f"f{i}.py"
            (root / name).write_text(content, encoding="utf-8")
            mapping[name] = orig
        yield root, mapping


def run_tool(args: list[str], cwd: Path, timeout: int) -> tuple[int, str, str]:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": str(cwd), "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env, shell=False)
    except subprocess.TimeoutExpired:
        raise ToolTimeout(f"{args[0]} timed out after {timeout}s")
    return r.returncode, r.stdout, r.stderr


def check_node_syntax(source: str, filename: str) -> Optional[tuple[int, str, str]]:
    """Run `node --check` in a temp dir via run_tool without directly invoking subprocess."""
    node_bin = find_tool("node")
    if not node_bin:
        return None
    with tempfile.TemporaryDirectory(prefix="tsa_node_") as tmp:
        p = Path(tmp) / filename
        p.write_text(source, encoding="utf-8")
        try:
            return run_tool([node_bin, "--check", str(p)], Path(tmp), timeout=5)
        except Exception:
            return None
