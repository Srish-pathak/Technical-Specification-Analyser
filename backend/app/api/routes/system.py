from fastapi import APIRouter

from app.analyzers import tool_runner as tr
from app.core.config import get_settings
from app.services.file_manager import ANALYZABLE_LANGUAGES, EXT_INFO

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/settings/status")
def settings_status():
    """Read-only status for the Settings page. Never returns secrets."""
    s = get_settings()
    ruff, _ = tr.cli_status("ruff")
    bandit, _ = tr.cli_status("bandit")
    return {
        "ai": {"configured": s.ai_configured, "provider": s.ai_provider or None, "model": s.ai_model or None,
               "note": "" if s.ai_configured else "AI provider not configured: static analysis only."},
        "tools": [tr.radon_status().to_dict(), ruff.to_dict(), bandit.to_dict()],
        "limits": {"max_upload_bytes": s.max_upload_bytes, "max_zip_bytes": s.max_zip_bytes,
                   "max_extracted_files": s.max_extracted_files, "retention_days": s.retention_days},
        "supported_extensions": sorted(EXT_INFO),
        "deterministic_analysis_languages": sorted(ANALYZABLE_LANGUAGES),
        "features_unavailable": ["pdf_analysis", "github_repository_review", "ai_agents", "reports", "documentation_generation"],
    }
