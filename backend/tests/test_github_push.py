import io
import json
import unittest
from unittest.mock import MagicMock, patch

from app.api.routes.analysis import get_github_commits, process_webhook_push
from app.services import github_service as gh_svc
from app.services.file_manager import InputValidationError, SourceFile


class TestGithubPushAnalysis(unittest.TestCase):

    def test_parse_github_url(self):
        owner, repo = gh_svc.parse_github_url("https://github.com/octocat/Hello-World.git")
        self.assertEqual(owner, "octocat")
        self.assertEqual(repo, "Hello-World")

        with self.assertRaises(InputValidationError):
            gh_svc.parse_github_url("https://notgithub.com/bad/url")

    def test_fetch_recent_commits(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "sha": "1b907c2a45e652abcdef1234567890abcdef1234",
                "commit": {
                    "message": "feat: implement push analysis\n\nFull details here",
                    "author": {"name": "Srish", "date": "2026-11-24T12:00:00Z"},
                },
                "author": {"login": "srish-p", "avatar_url": "https://example.com/avatar.png"},
                "html_url": "https://github.com/octocat/Hello-World/commit/1b907c2",
            }
        ]

        mock_http = MagicMock()
        mock_http.get.return_value = mock_response

        commits = gh_svc.fetch_recent_commits("octocat", "Hello-World", {}, mock_http, limit=5)
        self.assertEqual(len(commits), 1)
        c = commits[0]
        self.assertEqual(c["short_sha"], "1b907c2")
        self.assertEqual(c["message"], "feat: implement push analysis")
        self.assertEqual(c["author_name"], "Srish")
        self.assertEqual(c["author_login"], "srish-p")

    def test_fetch_commit_diff(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sha": "1b907c2a45e652abcdef1234567890abcdef1234",
            "commit": {
                "message": "clean: remove old reports",
                "author": {"name": "Srish", "date": "2026-11-24T12:00:00Z"},
            },
            "stats": {"total": 4289, "additions": 10, "deletions": 4279},
            "files": [
                {
                    "filename": "backend/app/main.py",
                    "status": "modified",
                    "additions": 10,
                    "deletions": 0,
                    "patch": "@@ -1,3 +1,13 @@",
                },
                {
                    "filename": "old_report.pdf",
                    "status": "removed",
                    "additions": 0,
                    "deletions": 4279,
                },
            ],
        }

        mock_http = MagicMock()
        mock_http.get.return_value = mock_response

        diff = gh_svc.fetch_commit_diff("octocat", "Hello-World", "1b907c2", {}, mock_http)
        self.assertEqual(diff["short_sha"], "1b907c2")
        self.assertEqual(diff["stats"]["additions"], 10)
        self.assertIn("backend/app/main.py", diff["files_modified"])
        self.assertIn("old_report.pdf", diff["files_removed"])

    @patch("app.services.github_service.fetch_repository_metadata")
    @patch("app.services.github_service.fetch_commit_diff")
    @patch("app.services.github_service.fetch_repository_tree")
    @patch("app.services.github_service.download_repository_source_files")
    def test_analyze_github_push_clean(self, mock_dl, mock_tree, mock_diff, mock_meta):
        mock_meta.return_value = (
            {
                "full_name": "octocat/Hello-World",
                "name": "Hello-World",
                "description": "Clean repo",
                "primary_language": "Python",
                "default_branch": "main",
                "private": False,
            },
            {"Python": 1000},
        )
        mock_diff.return_value = {
            "sha": "1b907c2a45e652abcdef1234567890abcdef1234",
            "short_sha": "1b907c2",
            "message": "chore: documentation update",
            "full_message": "chore: documentation update",
            "author_name": "Srish",
            "author_login": "srish",
            "author_avatar": "",
            "date": "2026-11-24T12:00:00Z",
            "html_url": "https://github.com/octocat/Hello-World/commit/1b907c2",
            "stats": {"total": 5, "additions": 5, "deletions": 0},
            "files": [{"filename": "app.py", "status": "modified", "additions": 5, "deletions": 0}],
            "files_added": [],
            "files_modified": ["app.py"],
            "files_removed": [],
        }
        mock_tree.return_value = (["app.py"], 0, 1)

        clean_code = "def add(a: int, b: int) -> int:\n    \"\"\"Add two numbers.\"\"\"\n    return a + b\n"
        mock_dl.return_value = ([SourceFile("app.py", clean_code, "python")], ["app.py"], 0, 1)

        result = gh_svc.analyze_github_push(
            url="https://github.com/octocat/Hello-World",
            commit_sha="1b907c2",
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["input_type"], "github_push")
        self.assertEqual(result["metrics"]["push_status"], "PASSED")
        self.assertEqual(result["metrics"]["push_quality_score"], 100)
        self.assertEqual(len(result["push_findings"]), 0)
        self.assertTrue(result["analysis_id"].startswith("push_"))

    @patch("app.services.github_service.fetch_repository_metadata")
    @patch("app.services.github_service.fetch_commit_diff")
    @patch("app.services.github_service.fetch_repository_tree")
    @patch("app.services.github_service.download_repository_source_files")
    def test_analyze_github_push_detects_introduced_vulnerability(self, mock_dl, mock_tree, mock_diff, mock_meta):
        mock_meta.return_value = (
            {
                "full_name": "octocat/Hello-World",
                "name": "Hello-World",
                "description": "Vulnerable push repo",
                "primary_language": "Python",
                "default_branch": "main",
                "private": False,
            },
            {"Python": 1000},
        )
        mock_diff.return_value = {
            "sha": "bad1234a45e652abcdef1234567890abcdef1234",
            "short_sha": "bad1234",
            "message": "feat: dangerous dynamic execution",
            "full_message": "feat: dangerous dynamic execution",
            "author_name": "BadActor",
            "author_login": "badactor",
            "author_avatar": "",
            "date": "2026-11-24T12:00:00Z",
            "html_url": "https://github.com/octocat/Hello-World/commit/bad1234",
            "stats": {"total": 5, "additions": 5, "deletions": 0},
            "files": [{"filename": "calculator.py", "status": "modified", "additions": 5, "deletions": 0}],
            "files_added": [],
            "files_modified": ["calculator.py"],
            "files_removed": [],
        }
        mock_tree.return_value = (["calculator.py"], 0, 1)

        vulnerable_code = "def run_calc(expr: str):\n    return eval(expr)\n"
        mock_dl.return_value = ([SourceFile("calculator.py", vulnerable_code, "python")], ["calculator.py"], 0, 1)

        result = gh_svc.analyze_github_push(
            url="https://github.com/octocat/Hello-World",
            commit_sha="bad1234",
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["metrics"]["push_status"], "BLOCKED")
        self.assertLess(result["metrics"]["push_quality_score"], 80)
        self.assertGreater(result["metrics"]["push_critical_count"], 0)
        self.assertTrue(any(f.get("is_push_diff") for f in result["findings"]))

    @patch("app.api.routes.analysis.gh_svc.analyze_github_push")
    def test_process_webhook_push(self, mock_push_fn):
        mock_db = MagicMock()
        mock_push_fn.return_value = {
            "analysis_id": "push_test123",
            "status": "completed",
            "input_type": "github_push",
            "input_name": "octocat/Hello-World @ 1b907c2",
            "created_at": "2026-11-24T12:00:00Z",
            "push_event": {"commit_sha": "1b907c2"},
            "metrics": {
                "push_status": "PASSED",
                "push_quality_score": 100,
                "push_critical_count": 0,
                "push_issues_total": 0,
            },
        }

        payload = {
            "ref": "refs/heads/main",
            "after": "1b907c2",
            "repository": {
                "full_name": "octocat/Hello-World",
                "html_url": "https://github.com/octocat/Hello-World",
            },
            "head_commit": {
                "id": "1b907c2",
                "message": "test push",
                "added": [],
                "modified": ["README.md"],
                "removed": [],
            },
        }

        res = process_webhook_push(payload, db=mock_db)
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["event"], "push")
        self.assertEqual(res["push_status"], "PASSED")
        self.assertEqual(res["push_quality_score"], 100)
        mock_db.save.assert_called_once()
