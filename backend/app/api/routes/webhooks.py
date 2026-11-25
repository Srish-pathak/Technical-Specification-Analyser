"""GitHub Webhook and Repository Monitoring API Routes.

Implements:
1. POST /api/webhooks/github:
   - HMAC-SHA256 signature verification (X-Hub-Signature-256) with constant-time comparison
   - Event validation (X-GitHub-Event: push, ping, safe ignore for others)
   - Idempotency & duplicate delivery tracking (X-GitHub-Delivery)
   - Background asynchronous execution via FastAPI BackgroundTasks
   - Auto-analysis and connected repository verification
2. Repository Connection Management:
   - POST /api/github/connect & POST /api/github/repositories
   - GET /api/github/repositories & GET /api/github/repositories/{repo_id}
   - DELETE /api/github/repositories/{repo_id}
   - PATCH /api/github/repositories/{repo_id}
   - GET /api/github/repositories/{repo_id}/pushes
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional
import httpx

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.models.database import Database, utcnow
from app.schemas.analysis import GithubRepoConnectRequest, GithubRepoUpdateRequest
from app.services import github_service as gh_svc
from app.services.file_manager import InputValidationError

logger = logging.getLogger("techspecanalyser.webhooks")

router = APIRouter(tags=["webhooks", "github"])


def handle_webhook_verification_and_payload(
    raw_body: bytes,
    event: str,
    signature_header: Optional[str],
    delivery_id: Optional[str],
    settings: Settings,
    db: Database,
) -> Dict[str, Any]:
    """Synchronous core logic for webhook event validation, HMAC signature check, and idempotency."""
    clean_event = (event or "push").lower().strip()

    # 1. Handle Ping Event
    if clean_event == "ping":
        if settings.github_webhook_secret and signature_header:
            if not gh_svc.verify_webhook_signature(raw_body, signature_header, settings.github_webhook_secret):
                raise HTTPException(status_code=401, detail="Invalid webhook signature on ping.")
        return {
            "status": "pong",
            "message": "TechSpecAnalyser Webhook connection active and verified.",
            "timestamp": gh_svc.utcnow(),
        }

    # 2. Safely Ignore Non-Push Events
    if clean_event != "push":
        logger.info(f"Ignored non-push event '{clean_event}' on webhook endpoint.")
        return {
            "status": "ignored",
            "event": clean_event,
            "message": f"Event '{clean_event}' safely ignored. Only 'push' events initiate automated code quality analysis.",
            "timestamp": gh_svc.utcnow(),
        }

    # 3. Parse and Validate JSON Payload
    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        raise InputValidationError("invalid_json", "Webhook request payload must be valid JSON.", status=400)

    if not isinstance(payload, dict):
        raise InputValidationError("malformed_payload", "Webhook payload must be a JSON object.", status=400)

    repo_obj = payload.get("repository") or {}
    full_name = (repo_obj.get("full_name") or "").strip().lower()
    if not full_name:
        raise InputValidationError("missing_repository", "Webhook payload missing required 'repository' metadata.", status=400)

    # 4. Lookup Connected Repository and Resolve Webhook Secret
    connected_repo = db.get_repository_by_full_name(full_name)
    repo_secret = (connected_repo.get("webhook_secret") if connected_repo else None) or settings.github_webhook_secret

    # 5. Mandatory Signature Verification (HMAC-SHA256 with constant-time comparison)
    if repo_secret:
        if not signature_header:
            logger.warning(f"Rejecting webhook for {full_name}: missing X-Hub-Signature-256 header.")
            raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header.")
        if not gh_svc.verify_webhook_signature(raw_body, signature_header, repo_secret):
            logger.warning(f"Rejecting webhook for {full_name}: signature mismatch.")
            raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    # 6. Check Repository Active & Auto-Analysis Status
    if connected_repo:
        if not connected_repo.get("is_active", 1):
            logger.info(f"Webhook received for inactive repository '{full_name}'. Skipping analysis.")
            return {
                "status": "ignored",
                "repository": full_name,
                "message": f"Repository '{full_name}' is currently disconnected or inactive.",
            }
        if not connected_repo.get("auto_analysis", 1):
            logger.info(f"Automatic analysis disabled for '{full_name}'. Skipping push analysis.")
            return {
                "status": "ignored",
                "repository": full_name,
                "message": f"Automatic push analysis is disabled for repository '{full_name}'.",
            }
    else:
        # Auto-register newly detected repository with default configuration
        owner_name = repo_obj.get("owner", {}).get("name") or repo_obj.get("owner", {}).get("login") or full_name.split("/")[0]
        repo_name = repo_obj.get("name") or full_name.split("/")[1]
        connected_repo = db.save_repository({
            "id": full_name,
            "owner": owner_name,
            "name": repo_name,
            "full_name": full_name,
            "url": repo_obj.get("html_url") or f"https://github.com/{full_name}",
            "default_branch": repo_obj.get("default_branch") or "main",
            "is_active": 1,
            "auto_analysis": 1,
            "webhook_secret": repo_secret if repo_secret != settings.github_webhook_secret else None,
            "last_analysis_status": "waiting_for_push",
        })

    # 7. Idempotency & Duplicate Delivery Protection
    delivery_guid = delivery_id or f"del_{uuid.uuid4().hex[:12]}"
    existing_delivery = db.get_webhook_delivery(delivery_guid)
    if existing_delivery and existing_delivery.get("status") in ("completed", "queued", "processing"):
        logger.info(f"Duplicate delivery ID '{delivery_guid}' for {full_name}. Returning idempotent success.")
        return {
            "status": "duplicate",
            "delivery_id": delivery_guid,
            "repository": full_name,
            "message": "Webhook delivery already processed.",
            "analysis_id": existing_delivery.get("analysis_id"),
        }

    # 8. Extract Commit SHA and Check for Branch Deletion / Empty Push
    head_commit = payload.get("head_commit") or {}
    commit_sha = head_commit.get("id") or payload.get("after")
    if not commit_sha or commit_sha == "0000000000000000000000000000000000000000":
        return {
            "status": "ignored",
            "repository": full_name,
            "message": "Branch deletion or empty commit ref received. Analysis skipped.",
        }

    # 9. Record Delivery as Queued & Update Repository Status
    db.record_webhook_delivery(
        delivery_id=delivery_guid,
        event_type="push",
        repository_full_name=full_name,
        commit_sha=commit_sha,
        status="queued",
    )
    db.update_repository_status(full_name, status="processing")

    ref_str = payload.get("ref", "")
    branch_name = ref_str.replace("refs/heads/", "") if ref_str.startswith("refs/heads/") else ref_str

    return {
        "status": "queued",
        "delivery_id": delivery_guid,
        "repository": full_name,
        "commit_sha": commit_sha,
        "branch": branch_name,
        "author": head_commit.get("author", {}).get("name") or payload.get("pusher", {}).get("name"),
        "commit_message": head_commit.get("message", "Commit update"),
        "payload": payload,
        "message": f"Push received for '{full_name} @ {commit_sha[:7]}'. Analysis initiated in background.",
        "timestamp": gh_svc.utcnow(),
    }


@router.post("/api/webhooks/github")
async def github_webhook_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None, alias="x-github-event"),
    x_hub_signature_256: Optional[str] = Header(None, alias="x-hub-signature-256"),
    x_github_delivery: Optional[str] = Header(None, alias="x-github-delivery"),
):
    """FastAPI Webhook endpoint for GitHub push events."""
    s = get_settings()
    db = get_db()
    raw_body = await request.body()
    event = x_github_event or request.headers.get("x-github-event", "push")
    sig = x_hub_signature_256 or request.headers.get("x-hub-signature-256")
    del_id = x_github_delivery or request.headers.get("x-github-delivery")

    result = handle_webhook_verification_and_payload(
        raw_body=raw_body,
        event=event,
        signature_header=sig,
        delivery_id=del_id,
        settings=s,
        db=db,
    )

    if result.get("status") == "queued":
        payload = result.pop("payload", {})
        # Enqueue background task
        background_tasks.add_task(
            gh_svc.execute_push_analysis_job,
            delivery_id=result["delivery_id"],
            payload=payload,
            settings=s,
            db=db,
        )
        return JSONResponse(status_code=202, content=result)

    return result


# -----------------------------------------------------------------------------
# Repository Connection & Management Endpoints
# -----------------------------------------------------------------------------
@router.post("/api/github/connect")
@router.post("/api/github/repositories")
async def connect_github_repository(req: GithubRepoConnectRequest):
    """Connect a GitHub repository for automated push tracking and quality monitoring."""
    s = get_settings()
    db = get_db()
    owner, repo = gh_svc.parse_github_url(req.url)
    full_name = f"{owner}/{repo}".lower()

    # Verify repo exists on GitHub if accessible
    headers = gh_svc._get_auth_headers(s.github_token)
    default_branch = req.default_branch or "main"
    try:
        with httpx.Client(timeout=8.0) as client:
            meta, _ = gh_svc.fetch_repository_metadata(owner, repo, headers, client)
            default_branch = req.default_branch or meta.get("default_branch") or "main"
    except Exception as exc:
        logger.warning(f"Could not verify remote metadata for {full_name}: {exc}")

    repo_record = {
        "id": full_name,
        "owner": owner,
        "name": repo,
        "full_name": full_name,
        "url": req.url.strip(),
        "default_branch": default_branch,
        "is_active": 1,
        "auto_analysis": int(req.auto_analysis if req.auto_analysis is not None else 1),
        "webhook_secret": req.webhook_secret or (s.github_webhook_secret if s.github_webhook_secret else None),
        "last_analysis_status": "waiting_for_push",
    }
    saved = db.save_repository(repo_record)
    saved.pop("webhook_secret", None)
    return {
        "status": "connected",
        "repository": saved,
        "webhook_url": "/api/webhooks/github",
        "instructions": "Configure a Webhook in GitHub repo Settings -> Webhooks pointing to /api/webhooks/github with application/json",
    }


@router.get("/api/github/repositories")
async def list_connected_repositories(active_only: bool = False):
    """List all connected GitHub repositories and their monitoring status."""
    db = get_db()
    repos = db.list_repositories(active_only=active_only)
    return {"repositories": repos, "count": len(repos)}


@router.get("/api/github/repositories/{repo_owner}/{repo_name}")
async def get_repository_details(repo_owner: str, repo_name: str):
    """Get single repository connection status, latest push metrics, and recent push history."""
    db = get_db()
    full_name = f"{repo_owner}/{repo_name}".lower()
    repo = db.get_repository_by_full_name(full_name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{full_name}' is not connected.")

    pushes = db.list_push_analyses_for_repo(full_name, limit=10)
    repo.pop("webhook_secret", None)
    return {
        "repository": repo,
        "pushes": pushes,
    }


@router.patch("/api/github/repositories/{repo_owner}/{repo_name}")
async def update_repository_settings(repo_owner: str, repo_name: str, req: GithubRepoUpdateRequest):
    """Update connected repository settings (e.g. toggle auto_analysis, active state, or branch)."""
    db = get_db()
    full_name = f"{repo_owner}/{repo_name}".lower()
    repo = db.get_repository_by_full_name(full_name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{full_name}' is not connected.")

    if req.default_branch is not None:
        repo["default_branch"] = req.default_branch
    if req.auto_analysis is not None:
        repo["auto_analysis"] = int(req.auto_analysis)
    if req.is_active is not None:
        repo["is_active"] = int(req.is_active)
    if req.webhook_secret is not None:
        repo["webhook_secret"] = req.webhook_secret

    updated = db.save_repository(repo)
    updated.pop("webhook_secret", None)
    return {"status": "updated", "repository": updated}


@router.delete("/api/github/repositories/{repo_owner}/{repo_name}")
async def disconnect_repository(repo_owner: str, repo_name: str):
    """Disconnect a repository from automated monitoring."""
    db = get_db()
    full_name = f"{repo_owner}/{repo_name}".lower()
    success = db.delete_repository(full_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Repository '{full_name}' was not found.")
    return {"status": "disconnected", "repository": full_name}


@router.get("/api/github/repositories/{repo_owner}/{repo_name}/pushes")
async def get_repository_push_history(repo_owner: str, repo_name: str, limit: int = 20):
    """Retrieve push analysis audit records for a connected repository."""
    db = get_db()
    full_name = f"{repo_owner}/{repo_name}".lower()
    pushes = db.list_push_analyses_for_repo(full_name, limit=limit)
    return {"repository": full_name, "pushes": pushes, "count": len(pushes)}
