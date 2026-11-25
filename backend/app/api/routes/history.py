from fastapi import APIRouter, HTTPException, Query

from app.api.deps import get_db

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def history(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return {"items": get_db().list(limit, offset)}


@router.get("/history/{analysis_id}")
def get_analysis_detail(analysis_id: str):
    res = get_db().get(analysis_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    return res


@router.get("/dashboard/stats")
def dashboard_stats():
    return get_db().stats()
