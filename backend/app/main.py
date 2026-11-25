"""TechSpecAnalyser FastAPI application.  Run from backend/:  uvicorn app.main:app --reload"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import analysis, history, system, webhooks
from app.services.file_manager import InputValidationError

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="TechSpecAnalyser", version="0.1.0",
              description="Static-analysis-grounded multi-agent code review and documentation platform.")


@app.exception_handler(InputValidationError)
async def validation_handler(_: Request, exc: InputValidationError):
    return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}})


@app.get("/health")
def root_health():
    return {"status": "ok"}


@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in ("/", "/index.html") or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


app.include_router(system.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(webhooks.router)

if FRONTEND_DIR.is_dir():   # mounted last so /api/* routes win
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
