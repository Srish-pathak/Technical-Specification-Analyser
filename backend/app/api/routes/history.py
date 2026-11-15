from fastapi import APIRouter, Query

from app.api.deps import get_db

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def history(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return {"items": get_db().list(limit, offset)}


@router.get("/dashboard/stats")
def dashboard_stats():
    return get_db().stats()
