"""Application settings, read from environment variables (optionally backend/.env).

No secrets are hardcoded. The AI key is only read from the environment and is
excluded from repr() so it cannot leak into logs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_dotenv(path: Path) -> None:
    """Tiny .env loader (no dependency). Real environment variables win."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    max_upload_bytes: int = 1_000_000          # single pasted/uploaded source file
    max_zip_bytes: int = 20_000_000            # compressed archive size
    max_file_bytes: int = 1_000_000            # any single extracted file
    max_extracted_files: int = 500
    max_extracted_bytes: int = 50_000_000      # total uncompressed bytes kept
    max_compression_ratio: int = 200           # zip-bomb guard per member
    db_path: Path = BACKEND_DIR / "data" / "techspecanalyser.db"
    retention_days: int = 90
    tool_timeout_seconds: int = 60
    ai_provider: str = ""
    ai_model: str = ""
    ai_api_key: str = field(default="", repr=False)
    ai_timeout_seconds: int = 60

    @property
    def ai_configured(self) -> bool:
        return bool(self.ai_provider and self.ai_api_key)


def get_settings() -> Settings:
    _load_dotenv(BACKEND_DIR / ".env")
    d = Settings()
    return Settings(
        max_upload_bytes=_int("TSA_MAX_UPLOAD_BYTES", d.max_upload_bytes),
        max_zip_bytes=_int("TSA_MAX_ZIP_BYTES", d.max_zip_bytes),
        max_file_bytes=_int("TSA_MAX_FILE_BYTES", d.max_file_bytes),
        max_extracted_files=_int("TSA_MAX_EXTRACTED_FILES", d.max_extracted_files),
        max_extracted_bytes=_int("TSA_MAX_EXTRACTED_BYTES", d.max_extracted_bytes),
        max_compression_ratio=_int("TSA_MAX_COMPRESSION_RATIO", d.max_compression_ratio),
        db_path=Path(os.environ.get("TSA_DB_PATH", str(d.db_path))),
        retention_days=_int("TSA_RETENTION_DAYS", d.retention_days),
        tool_timeout_seconds=_int("TSA_TOOL_TIMEOUT_SECONDS", d.tool_timeout_seconds),
        ai_provider=os.environ.get("TSA_AI_PROVIDER", ""),
        ai_model=os.environ.get("TSA_AI_MODEL", ""),
        ai_api_key=os.environ.get("TSA_AI_API_KEY", ""),
        ai_timeout_seconds=_int("TSA_AI_TIMEOUT_SECONDS", d.ai_timeout_seconds),
    )
