from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.analysis import CodeAnalysisRequest, GithubAnalysisRequest
from app.services import analysis_service as svc
from app.services import github_service as gh_svc
from app.services.file_manager import InputValidationError

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/code")
async def analyze_code(req: CodeAnalysisRequest):
    return await run_in_threadpool(svc.submit_code, get_db(), req.code, req.language, req.filename)


@router.post("/github")
async def analyze_github(req: GithubAnalysisRequest):
    s = get_settings()
    db = get_db()
    result = await run_in_threadpool(
        gh_svc.analyze_github_repository,
        url=req.url,
        branch=req.branch,
        token=req.token,
        settings=s,
    )
    db.save(result)
    return result


@router.post("/upload")
async def analyze_upload(file: UploadFile = File(...)):
    s = get_settings()
    name = file.filename or ""
    is_zip = name.lower().endswith(".zip")
    limit = s.max_zip_bytes if is_zip else s.max_upload_bytes
    data = await file.read(limit + 1)          # bounded read: never buffer an unbounded upload
    if len(data) > limit:
        raise InputValidationError("file_too_large", f"Upload exceeds the {limit:,}-byte limit.", 413)
    fn = svc.submit_zip if is_zip else svc.submit_file
    return await run_in_threadpool(fn, get_db(), name, data, file.content_type)


@router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    rec: Optional[dict] = get_db().get(analysis_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return rec
