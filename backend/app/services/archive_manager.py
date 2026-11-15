"""Safe ZIP handling.

Design decision: archives are read *in memory* and never written to disk, so ZIP-slip and file
overwrite are impossible by construction. Member paths are still validated and normalised because
they become identifiers in reports. Nothing inside the archive is imported or executed.
"""
from __future__ import annotations

import io
import stat
import zipfile
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import Settings, get_settings
from app.core.security import UnsafePathError, has_ignored_dir, looks_binary, normalize_member_path
from app.services.file_manager import InputValidationError, SourceFile, classify_path, zip_mime_allowed

_CHUNK = 64 * 1024


@dataclass
class ProjectInventory:
    files: list[SourceFile] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)      # [{path, reason}]
    total_bytes: int = 0

    def to_dict(self) -> dict:
        return {
            "files": [{"path": f.path, "language": f.language, "kind": f.kind,
                       "size": f.size, "lines": f.line_count} for f in self.files],
            "skipped": self.skipped,
            "total_bytes": self.total_bytes,
        }


def _read_limited(zf: zipfile.ZipFile, info: zipfile.ZipInfo, limit: int) -> Optional[bytes]:
    """Read up to `limit` bytes of the *actual* decompressed stream (declared sizes can lie)."""
    out = bytearray()
    with zf.open(info) as fh:
        while True:
            chunk = fh.read(_CHUNK)
            if not chunk:
                return bytes(out)
            out += chunk
            if len(out) > limit:
                return None


def read_zip_project(data: bytes, content_type: Optional[str] = None,
                     settings: Optional[Settings] = None) -> ProjectInventory:
    s = settings or get_settings()
    if not zip_mime_allowed(content_type):
        raise InputValidationError("unsupported_mime", f"MIME type '{content_type}' is not a ZIP type.", 415)
    if len(data) == 0:
        raise InputValidationError("empty_file", "The archive is empty.")
    if len(data) > s.max_zip_bytes:
        raise InputValidationError("zip_too_large", f"Archive exceeds the {s.max_zip_bytes:,}-byte limit.", 413)
    if not data.startswith((b"PK\x03\x04", b"PK\x05\x06")):
        raise InputValidationError("malformed_zip", "File is not a ZIP archive (bad signature).")
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        infos = zf.infolist()
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, EOFError, ValueError) as exc:
        raise InputValidationError("malformed_zip", f"Malformed ZIP archive: {exc}")

    if len(infos) > s.max_extracted_files * 4:
        raise InputValidationError("too_many_entries", "Archive contains too many entries.", 413)

    inv = ProjectInventory()
    seen: set[str] = set()
    with zf:
        for info in infos:
            raw = info.filename
            if info.is_dir():
                continue
            try:
                path = normalize_member_path(raw)
            except UnsafePathError as exc:
                # Hostile archive: reject it entirely rather than "skip and continue".
                raise InputValidationError("zip_path_traversal", f"Unsafe path in archive: {exc}")
            if stat.S_ISLNK(info.external_attr >> 16):
                inv.skipped.append({"path": path, "reason": "symlink"})
                continue
            if info.flag_bits & 0x1:
                inv.skipped.append({"path": path, "reason": "encrypted"})
                continue
            if has_ignored_dir(path):
                inv.skipped.append({"path": path, "reason": "ignored_directory"})
                continue
            cls = classify_path(path)
            if cls is None:
                inv.skipped.append({"path": path, "reason": "unsupported_type"})
                continue
            if path in seen:
                inv.skipped.append({"path": path, "reason": "duplicate_path"})  # never overwrite
                continue
            if info.file_size > s.max_file_bytes:
                inv.skipped.append({"path": path, "reason": "file_too_large"})
                continue
            if info.compress_size and info.file_size / max(info.compress_size, 1) > s.max_compression_ratio:
                inv.skipped.append({"path": path, "reason": "suspicious_compression_ratio"})
                continue
            if len(inv.files) >= s.max_extracted_files:
                inv.skipped.append({"path": path, "reason": "file_count_limit"})
                continue
            remaining = s.max_extracted_bytes - inv.total_bytes
            try:
                blob = _read_limited(zf, info, min(s.max_file_bytes, remaining))
            except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, NotImplementedError):
                inv.skipped.append({"path": path, "reason": "unreadable_member"})
                continue
            if blob is None:
                inv.skipped.append({"path": path, "reason": "file_too_large_or_total_limit"})
                continue
            if not blob.strip():
                inv.skipped.append({"path": path, "reason": "empty_file"})
                continue
            if looks_binary(blob):
                inv.skipped.append({"path": path, "reason": "binary_content"})
                continue
            try:
                text = blob.decode("utf-8-sig")
            except UnicodeDecodeError:
                inv.skipped.append({"path": path, "reason": "not_utf8"})
                continue
            seen.add(path)
            inv.total_bytes += len(blob)
            inv.files.append(SourceFile(path=path, content=text, language=cls[0], kind=cls[1]))

    if not inv.files:
        raise InputValidationError("empty_archive", "The archive contains no supported, readable files.")
    inv.files.sort(key=lambda f: f.path)
    return inv
