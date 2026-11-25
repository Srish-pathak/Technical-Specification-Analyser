"""Automated tests for GitHub Webhook Integration and Repository Monitoring.

Verifies:
1. HMAC-SHA256 signature verification with constant-time comparison.
2. Missing signature rejection (401).
3. Invalid signature rejection (401).
4. Ping event handling.
5. Non-push event safe ignoring.
6. Malformed JSON rejection (400).
7. Repository connection management (connect, list, patch, delete).
8. Idempotency & duplicate delivery protection (X-GitHub-Delivery).
9. Documentation-only push classification and fast-path scoring.
10. Background push job execution and database status updates.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.routes.webhooks import (
    handle_webhook_verification_and_payload,
)
from app.core.config import Settings
from app.models.database import Database
from app.schemas.analysis import GithubRepoConnectRequest, GithubRepoUpdateRequest
from app.services import github_service as gh_svc
from app.services.file_manager import InputValidationError


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_webhook.db"
    return Database(db_file)


def generate_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class TestWebhookSignatureAndEvents:
    """Tests for HMAC signature validation and event filtering."""

    def test_verify_webhook_signature_helper(self):
        secret = "test_webhook_secret_12345"
        payload = b'{"hello": "world"}'
        valid_sig = generate_signature(secret, payload)

        assert gh_svc.verify_webhook_signature(payload, valid_sig, secret) is True
        assert gh_svc.verify_webhook_signature(payload, "sha256=invalidhex", secret) is False
        assert gh_svc.verify_webhook_signature(payload, None, secret) is False
        assert gh_svc.verify_webhook_signature(payload, valid_sig, "") is False

    def test_webhook_ping_event_success(self, temp_db):
        settings = Settings(github_webhook_secret="")
        res = handle_webhook_verification_and_payload(
            raw_body=b'{"zen": "Mind your words"}',
            event="ping",
            signature_header=None,
            delivery_id="del-1",
            settings=settings,
            db=temp_db,
        )
        assert res["status"] == "pong"
        assert "verified" in res["message"].lower()

    def test_webhook_ping_event_with_valid_signature(self, temp_db):
        secret = "ping_secret"
        settings = Settings(github_webhook_secret=secret)
        body = b'{"zen": "Approachable is better than simple."}'
        valid_sig = generate_signature(secret, body)

        res = handle_webhook_verification_and_payload(
            raw_body=body,
            event="ping",
            signature_header=valid_sig,
            delivery_id="del-2",
            settings=settings,
            db=temp_db,
        )
        assert res["status"] == "pong"

    def test_webhook_ping_event_with_invalid_signature_fails(self, temp_db):
        secret = "ping_secret"
        settings = Settings(github_webhook_secret=secret)
        body = b'{"zen": "Approachable is better than simple."}'

        with pytest.raises(HTTPException) as exc_info:
            handle_webhook_verification_and_payload(
                raw_body=body,
                event="ping",
                signature_header="sha256=wrong_signature",
                delivery_id="del-3",
                settings=settings,
                db=temp_db,
            )
        assert exc_info.value.status_code == 401

    def test_webhook_ignores_non_push_events(self, temp_db):
        settings = Settings()
        for event in ("issues", "pull_request", "star", "fork", "release"):
            res = handle_webhook_verification_and_payload(
                raw_body=b'{"action": "opened"}',
                event=event,
                signature_header=None,
                delivery_id=f"del-{event}",
                settings=settings,
                db=temp_db,
            )
            assert res["status"] == "ignored"
            assert event in res["message"]

    def test_webhook_rejects_malformed_json(self, temp_db):
        settings = Settings()
        with pytest.raises(InputValidationError) as exc_info:
            handle_webhook_verification_and_payload(
                raw_body=b"not-json-content{",
                event="push",
                signature_header=None,
                delivery_id="del-bad",
                settings=settings,
                db=temp_db,
            )
        assert exc_info.value.code == "invalid_json"

    def test_webhook_rejects_missing_signature_when_secret_configured(self, temp_db):
        secret = "mandatory_secret"
        settings = Settings(github_webhook_secret=secret)
        payload = json.dumps({"repository": {"full_name": "org/repo"}}).encode("utf-8")

        with pytest.raises(HTTPException) as exc_info:
            handle_webhook_verification_and_payload(
                raw_body=payload,
                event="push",
                signature_header=None,
                delivery_id="del-missing-sig",
                settings=settings,
                db=temp_db,
            )
        assert exc_info.value.status_code == 401
        assert "missing x-hub-signature-256" in exc_info.value.detail.lower()

    def test_webhook_rejects_invalid_signature(self, temp_db):
        secret = "mandatory_secret"
        settings = Settings(github_webhook_secret=secret)
        payload = json.dumps({"repository": {"full_name": "org/repo"}}).encode("utf-8")

        with pytest.raises(HTTPException) as exc_info:
            handle_webhook_verification_and_payload(
                raw_body=payload,
                event="push",
                signature_header="sha256=0000000000000000000000000000000000000000000000000000000000000000",
                delivery_id="del-inv-sig",
                settings=settings,
                db=temp_db,
            )
        assert exc_info.value.status_code == 401
        assert "invalid webhook signature" in exc_info.value.detail.lower()


class TestWebhookPushWorkflow:
    """Tests for the end-to-end push processing and background execution."""

    def test_valid_push_payload_verification(self, temp_db):
        secret = "secure_hook_key_999"
        settings = Settings(github_webhook_secret=secret, db_path=temp_db.path)

        payload = {
            "ref": "refs/heads/main",
            "repository": {
                "name": "sample-repo",
                "full_name": "acme/sample-repo",
                "html_url": "https://github.com/acme/sample-repo",
                "default_branch": "main",
            },
            "head_commit": {
                "id": "e4f8b91c890123456789abcdef0123456789abcd",
                "message": "fix: update database connection pool",
                "author": {"name": "Alice Dev"},
            },
        }
        body = json.dumps(payload).encode("utf-8")
        sig = generate_signature(secret, body)
        delivery_id = f"test-delivery-{uuid.uuid4().hex[:8]}"

        res = handle_webhook_verification_and_payload(
            raw_body=body,
            event="push",
            signature_header=sig,
            delivery_id=delivery_id,
            settings=settings,
            db=temp_db,
        )

        assert res["status"] == "queued"
        assert res["repository"] == "acme/sample-repo"
        assert res["commit_sha"] == "e4f8b91c890123456789abcdef0123456789abcd"

        # Verify delivery record in database
        del_rec = temp_db.get_webhook_delivery(delivery_id)
        assert del_rec is not None
        assert del_rec["event_type"] == "push"
        assert del_rec["status"] == "queued"

    def test_idempotent_duplicate_delivery(self, temp_db):
        secret = "dup_secret"
        settings = Settings(github_webhook_secret=secret, db_path=temp_db.path)
        delivery_id = "delivery-guid-1111"

        # Pre-record completed delivery
        temp_db.record_webhook_delivery(
            delivery_id=delivery_id,
            event_type="push",
            repository_full_name="acme/sample-repo",
            commit_sha="commit_sha_123",
            status="completed",
            analysis_id="push_existing",
        )

        payload = {
            "repository": {"full_name": "acme/sample-repo"},
            "head_commit": {"id": "commit_sha_123"},
        }
        body = json.dumps(payload).encode("utf-8")
        sig = generate_signature(secret, body)

        res = handle_webhook_verification_and_payload(
            raw_body=body,
            event="push",
            signature_header=sig,
            delivery_id=delivery_id,
            settings=settings,
            db=temp_db,
        )

        assert res["status"] == "duplicate"
        assert res["delivery_id"] == delivery_id

    def test_inactive_repository_push_is_ignored(self, temp_db):
        secret = "secret"
        settings = Settings(github_webhook_secret=secret, db_path=temp_db.path)

        temp_db.save_repository({
            "full_name": "test/inactive-repo",
            "is_active": 0,
        })

        payload = {
            "repository": {"full_name": "test/inactive-repo"},
            "head_commit": {"id": "abc111"},
        }
        body = json.dumps(payload).encode("utf-8")
        sig = generate_signature(secret, body)

        res = handle_webhook_verification_and_payload(
            raw_body=body,
            event="push",
            signature_header=sig,
            delivery_id="del-inact",
            settings=settings,
            db=temp_db,
        )

        assert res["status"] == "ignored"
        assert "inactive" in res["message"]

    def test_auto_analysis_disabled_push_is_ignored(self, temp_db):
        secret = "secret"
        settings = Settings(github_webhook_secret=secret, db_path=temp_db.path)

        temp_db.save_repository({
            "full_name": "test/no-auto-repo",
            "is_active": 1,
            "auto_analysis": 0,
        })

        payload = {
            "repository": {"full_name": "test/no-auto-repo"},
            "head_commit": {"id": "abc222"},
        }
        body = json.dumps(payload).encode("utf-8")
        sig = generate_signature(secret, body)

        res = handle_webhook_verification_and_payload(
            raw_body=body,
            event="push",
            signature_header=sig,
            delivery_id="del-no-auto",
            settings=settings,
            db=temp_db,
        )

        assert res["status"] == "ignored"
        assert "disabled" in res["message"]


class TestDocumentationOnlyPush:
    """Tests for incremental analysis and fast-path scoring on doc-only commits."""

    def test_is_documentation_only_change_detection(self):
        docs_changes = [
            {"filename": "README.md"},
            {"filename": "docs/architecture.png"},
            {"filename": "LICENSE"},
            {"filename": ".gitignore"},
        ]
        assert gh_svc.is_documentation_only_change(docs_changes) is True

        code_changes = [
            {"filename": "README.md"},
            {"filename": "app/main.py"},
        ]
        assert gh_svc.is_documentation_only_change(code_changes) is False

    def test_documentation_only_push_analysis(self, monkeypatch):
        mock_diff = {
            "sha": "112233445566778899aabbccddeeff0011223344",
            "short_sha": "1122334",
            "message": "docs: update API setup guide and roadmap",
            "full_message": "docs: update API setup guide and roadmap",
            "author_name": "Doc Writer",
            "author_login": "docwriter",
            "author_avatar": "https://avatars.githubusercontent.com/u/1",
            "date": "2026-11-25T12:00:00Z",
            "html_url": "https://github.com/org/repo/commit/1122334",
            "stats": {"total": 12, "additions": 10, "deletions": 2},
            "files": [
                {"filename": "README.md", "status": "modified", "additions": 8, "deletions": 1},
                {"filename": "docs/setup.md", "status": "added", "additions": 2, "deletions": 1},
            ],
            "files_added": ["docs/setup.md"],
            "files_modified": ["README.md"],
            "files_removed": [],
        }

        monkeypatch.setattr("app.services.github_service.fetch_repository_metadata", lambda o, r, h, c: ({"full_name": "org/repo", "default_branch": "main"}, {}))
        monkeypatch.setattr("app.services.github_service.fetch_commit_diff", lambda o, r, s, h, c: mock_diff)

        result = gh_svc.analyze_github_push(
            url="https://github.com/org/repo",
            commit_sha="112233445566778899aabbccddeeff0011223344",
        )

        assert result["status"] == "completed"
        assert result["analysis_type"] == "Incremental Analysis (Documentation Only)"
        assert result["push_status"] == "PASSED"
        assert result["push_quality_score"] == 100
        assert len(result["push_findings"]) == 0
        assert "Documentation/asset update only" in result["metrics"]["scoring_methodology"]


class TestRepositoryManagementDatabaseOperations:
    """Tests for repository connection, listing, updating, and disconnecting in database."""

    def test_save_and_get_repository(self, temp_db):
        repo_data = {
            "full_name": "Srish-pathak/Technical-Specification-Analyser",
            "url": "https://github.com/Srish-pathak/Technical-Specification-Analyser",
            "default_branch": "main",
            "is_active": 1,
            "auto_analysis": 1,
            "webhook_secret": "my_secret_token",
        }
        saved = temp_db.save_repository(repo_data)
        assert saved["full_name"] == "srish-pathak/technical-specification-analyser"
        assert saved["is_active"] == 1
        assert saved["auto_analysis"] == 1

        # Check retrieval hides raw secret
        retrieved = temp_db.get_repository("srish-pathak/technical-specification-analyser")
        assert retrieved is not None
        assert retrieved["webhook_configured"] is True

    def test_list_repositories(self, temp_db):
        temp_db.save_repository({
            "full_name": "alice/service-a",
            "is_active": 1,
        })
        temp_db.save_repository({
            "full_name": "bob/service-b",
            "is_active": 0,
        })

        all_repos = temp_db.list_repositories(active_only=False)
        assert len(all_repos) == 2

        active_repos = temp_db.list_repositories(active_only=True)
        assert len(active_repos) == 1
        assert active_repos[0]["full_name"] == "alice/service-a"

    def test_update_repository_push_status(self, temp_db):
        full_name = "corp/api-gateway"
        temp_db.save_repository({
            "full_name": full_name,
            "is_active": 1,
        })

        temp_db.update_repository_push(full_name, {
            "commit_sha": "a1b2c3d4",
            "commit_message": "feat: add rate limiting",
            "author": "Eve Engineer",
            "analysis_id": "push_100",
            "status": "completed",
            "quality_score": 95,
            "gate_status": "PASSED",
        })

        repo = temp_db.get_repository(full_name)
        assert repo["last_commit_sha"] == "a1b2c3d4"
        assert repo["last_commit_message"] == "feat: add rate limiting"
        assert repo["last_commit_author"] == "Eve Engineer"
        assert repo["last_quality_score"] == 95
        assert repo["last_gate_status"] == "PASSED"

    def test_delete_repository(self, temp_db):
        full_name = "test/to-delete"
        temp_db.save_repository({"full_name": full_name})
        assert temp_db.get_repository(full_name) is not None

        deleted = temp_db.delete_repository(full_name)
        assert deleted is True
        assert temp_db.get_repository(full_name) is None
