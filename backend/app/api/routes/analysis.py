from typing import Optional

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.analysis import CodeAnalysisRequest, GithubAnalysisRequest
from app.services import analysis_service as svc
from app.services import github_service as gh_svc
from app.services import pdf_service as pdf_svc
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


@router.post("/pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    s = get_settings()
    name = file.filename or "document.pdf"
    if not name.lower().endswith(".pdf"):
        raise InputValidationError("invalid_file_type", "Only PDF (.pdf) documents are supported.", 400)

    # 20 MB bounded limit for PDF technical documents
    limit = s.max_upload_bytes * 20
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise InputValidationError("file_too_large", f"PDF exceeds the {limit:,}-byte limit.", 413)

    db = get_db()
    result = await run_in_threadpool(pdf_svc.process_and_analyze_pdf, data, name, s)
    db.save(result)
    return result


@router.post("/pdf/sample")
@router.get("/pdf/sample")
async def analyze_sample_pdf():
    s = get_settings()
    db = get_db()
    sample_bytes = pdf_svc.generate_sample_pdf_bytes()
    result = await run_in_threadpool(
        pdf_svc.process_and_analyze_pdf,
        sample_bytes,
        "Enterprise_Cloud_Analytics_Specification.pdf",
        s,
    )
    db.save(result)
    return result


@router.get("/pdf/sample/download")
def download_sample_pdf():
    pdf_bytes = pdf_svc.generate_sample_pdf_bytes()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="TechSpecAnalyser_Sample_Specification.pdf"'
        },
    )


@router.get("/pdf/{analysis_id}/report")
async def export_pdf_analysis_report(analysis_id: str):
    db = get_db()
    rec = db.get(analysis_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    report_pdf_bytes = await run_in_threadpool(pdf_svc.generate_analysis_report_pdf, rec)
    safe_name = rec.get("input_name", "analysis").replace(".pdf", "").replace(" ", "_")
    return Response(
        content=report_pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="TechSpec_Report_{safe_name}.pdf"'
        },
    )


@router.post("/pdf/sample-unsupported")
@router.get("/pdf/sample-unsupported")
async def analyze_sample_unsupported_pdf():
    s = get_settings()
    db = get_db()
    sample_bytes = pdf_svc.generate_sample_unsupported_pdf_bytes()
    result = await run_in_threadpool(
        pdf_svc.process_and_analyze_pdf,
        sample_bytes,
        "Artisanal_Sourdough_Guide_NonTechnical.pdf",
        s,
    )
    db.save(result)
    return result


@router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    rec: Optional[dict] = get_db().get(analysis_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return rec
