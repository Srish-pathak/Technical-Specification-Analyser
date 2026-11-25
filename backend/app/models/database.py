"""SQLite persistence (stdlib sqlite3). One short-lived connection per operation (thread-safe).

Only derived results are stored (findings with short evidence lines, structure, metrics),
never the full uploaded source text. Retention is enforced via purge_older_than().
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY, input_type TEXT NOT NULL, input_name TEXT, language TEXT,
  status TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT,
  issues_total INTEGER DEFAULT 0, critical_count INTEGER DEFAULT 0, high_count INTEGER DEFAULT 0,
  function_count INTEGER DEFAULT 0, complexity_sum INTEGER DEFAULT 0,
  doc_items INTEGER DEFAULT 0, doc_documented INTEGER DEFAULT 0,
  error TEXT, result_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);

CREATE TABLE IF NOT EXISTS connected_repositories (
  id TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  name TEXT NOT NULL,
  full_name TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL,
  default_branch TEXT DEFAULT 'main',
  is_active INTEGER DEFAULT 1,
  auto_analysis INTEGER DEFAULT 1,
  webhook_secret TEXT,
  last_received_push_at TEXT,
  last_commit_sha TEXT,
  last_commit_message TEXT,
  last_commit_author TEXT,
  last_analysis_id TEXT,
  last_analysis_status TEXT,
  last_quality_score INTEGER,
  last_gate_status TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_connected_repos_active ON connected_repositories(is_active);

CREATE TABLE IF NOT EXISTS webhook_deliveries (
  delivery_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  repository_full_name TEXT,
  commit_sha TEXT,
  status TEXT NOT NULL,
  analysis_id TEXT,
  error TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_repo ON webhook_deliveries(repository_full_name);
"""
_LIST_COLS = ("id, input_type, input_name, language, status, created_at, completed_at, issues_total, "
              "critical_count, high_count, error")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def save(self, rec: dict[str, Any]) -> None:
        m = rec.get("metrics", {})
        sev = m.get("severity_counts", {})
        with self._conn() as c:
            c.execute(
                """INSERT OR REPLACE INTO analyses (id,input_type,input_name,language,status,created_at,completed_at,
                   issues_total,critical_count,high_count,function_count,complexity_sum,doc_items,doc_documented,error,result_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rec["analysis_id"], rec["input_type"], rec.get("input_name"), rec.get("language"), rec["status"],
                 rec["created_at"], rec.get("completed_at"), m.get("total_findings", 0), sev.get("Critical", 0),
                 sev.get("High", 0), m.get("function_count", 0), m.get("complexity_sum", 0),
                 m.get("doc_items", 0), m.get("doc_documented", 0), rec.get("error"), json.dumps(rec)))

    def get(self, analysis_id: str) -> Optional[dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT result_json FROM analyses WHERE id=?", (analysis_id,)).fetchone()
        return json.loads(row["result_json"]) if row and row["result_json"] else None

    def list(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute(f"SELECT {_LIST_COLS} FROM analyses ORDER BY created_at DESC, rowid DESC LIMIT ? OFFSET ?",
                             (max(1, min(limit, 200)), max(0, offset))).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> dict[str, Any]:
        with self._conn() as c:
            t = c.execute("""SELECT COUNT(*) n, SUM(status='completed') done, SUM(status='failed') failed,
                             COALESCE(SUM(issues_total),0) issues, COALESCE(SUM(critical_count+high_count),0) crit_high,
                             COALESCE(SUM(function_count),0) fn, COALESCE(SUM(complexity_sum),0) cx,
                             COALESCE(SUM(doc_items),0) di, COALESCE(SUM(doc_documented),0) dd FROM analyses""").fetchone()
            recent = c.execute(f"SELECT {_LIST_COLS} FROM analyses ORDER BY created_at DESC, rowid DESC LIMIT 5").fetchall()
        return {
            "total_analyses": t["n"], "completed": t["done"] or 0, "failed": t["failed"] or 0,
            "total_issues": t["issues"], "critical_high": t["crit_high"],
            "avg_complexity": round(t["cx"] / t["fn"], 2) if t["fn"] else None,
            "documentation_coverage": round(100 * t["dd"] / t["di"], 1) if t["di"] else None,
            "recent": [dict(r) for r in recent], "empty": t["n"] == 0,
        }

    def purge_older_than(self, days: int) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        with self._conn() as c:
            return c.execute("DELETE FROM analyses WHERE created_at < ?", (cutoff,)).rowcount

    # -------------------------------------------------------------------------
    # Repository Monitoring & Webhook Persistence
    # -------------------------------------------------------------------------
    def save_repository(self, repo: dict[str, Any]) -> dict[str, Any]:
        now = utcnow()
        full_name = repo["full_name"].strip().lower()
        owner = repo.get("owner") or full_name.split("/")[0]
        name = repo.get("name") or full_name.split("/")[1]
        repo_id = repo.get("id") or full_name

        with self._conn() as c:
            existing = c.execute("SELECT created_at, webhook_secret FROM connected_repositories WHERE full_name=?", (full_name,)).fetchone()
            created_at = existing["created_at"] if existing else now
            # Only update secret if explicitly passed; preserve existing secret if not provided
            secret = repo.get("webhook_secret") if repo.get("webhook_secret") is not None else (existing["webhook_secret"] if existing else None)

            c.execute(
                """INSERT OR REPLACE INTO connected_repositories (
                   id, owner, name, full_name, url, default_branch, is_active, auto_analysis,
                   webhook_secret, last_received_push_at, last_commit_sha, last_commit_message,
                   last_commit_author, last_analysis_id, last_analysis_status, last_quality_score,
                   last_gate_status, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    repo_id,
                    owner,
                    name,
                    full_name,
                    repo.get("url", f"https://github.com/{full_name}"),
                    repo.get("default_branch", "main"),
                    int(repo.get("is_active", 1)),
                    int(repo.get("auto_analysis", 1)),
                    secret,
                    repo.get("last_received_push_at"),
                    repo.get("last_commit_sha"),
                    repo.get("last_commit_message"),
                    repo.get("last_commit_author"),
                    repo.get("last_analysis_id"),
                    repo.get("last_analysis_status", "connected"),
                    repo.get("last_quality_score"),
                    repo.get("last_gate_status"),
                    created_at,
                    now,
                )
            )
        return self.get_repository(repo_id) or repo

    def get_repository(self, repo_id: str) -> Optional[dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM connected_repositories WHERE id=? OR full_name=?", (repo_id, repo_id.lower())).fetchone()
        if not row:
            return None
        d = dict(row)
        # Never return plaintext secret to external consumers
        d["webhook_configured"] = bool(d.get("webhook_secret"))
        return d

    def get_repository_by_full_name(self, full_name: str) -> Optional[dict[str, Any]]:
        return self.get_repository(full_name.lower())

    def list_repositories(self, active_only: bool = False) -> list[dict[str, Any]]:
        query = "SELECT * FROM connected_repositories"
        params: tuple[Any, ...] = ()
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY updated_at DESC"
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["webhook_configured"] = bool(d.get("webhook_secret"))
            d.pop("webhook_secret", None)
            result.append(d)
        return result

    def delete_repository(self, repo_id: str) -> bool:
        with self._conn() as c:
            res = c.execute("DELETE FROM connected_repositories WHERE id=? OR full_name=?", (repo_id, repo_id.lower()))
            return res.rowcount > 0

    def update_repository_status(self, full_name: str, status: str, analysis_id: Optional[str] = None) -> None:
        now = utcnow()
        with self._conn() as c:
            if analysis_id:
                c.execute(
                    "UPDATE connected_repositories SET last_analysis_status=?, last_analysis_id=?, updated_at=? WHERE full_name=?",
                    (status, analysis_id, now, full_name.lower())
                )
            else:
                c.execute(
                    "UPDATE connected_repositories SET last_analysis_status=?, updated_at=? WHERE full_name=?",
                    (status, now, full_name.lower())
                )

    def update_repository_push(self, full_name: str, push_info: dict[str, Any]) -> None:
        now = utcnow()
        with self._conn() as c:
            c.execute(
                """UPDATE connected_repositories SET
                   last_received_push_at=?,
                   last_commit_sha=?,
                   last_commit_message=?,
                   last_commit_author=?,
                   last_analysis_id=?,
                   last_analysis_status=?,
                   last_quality_score=?,
                   last_gate_status=?,
                   updated_at=?
                   WHERE full_name=?""",
                (
                    push_info.get("pushed_at") or now,
                    push_info.get("commit_sha"),
                    push_info.get("commit_message"),
                    push_info.get("author"),
                    push_info.get("analysis_id"),
                    push_info.get("status", "completed"),
                    push_info.get("quality_score"),
                    push_info.get("gate_status"),
                    now,
                    full_name.lower(),
                )
            )

    def record_webhook_delivery(
        self,
        delivery_id: str,
        event_type: str,
        repository_full_name: str,
        commit_sha: Optional[str],
        status: str,
        analysis_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        now = utcnow()
        with self._conn() as c:
            c.execute(
                """INSERT OR REPLACE INTO webhook_deliveries (
                   delivery_id, event_type, repository_full_name, commit_sha, status, analysis_id, error, created_at
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (delivery_id, event_type, repository_full_name.lower() if repository_full_name else None,
                 commit_sha, status, analysis_id, error, now)
            )

    def get_webhook_delivery(self, delivery_id: str) -> Optional[dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM webhook_deliveries WHERE delivery_id=?", (delivery_id,)).fetchone()
        return dict(row) if row else None

    def list_push_analyses_for_repo(self, repo_full_name: str, limit: int = 20) -> list[dict[str, Any]]:
        target = f"%{repo_full_name.lower()}%"
        with self._conn() as c:
            rows = c.execute(
                """SELECT id, input_name, status, created_at, completed_at, issues_total,
                          critical_count, high_count, result_json
                   FROM analyses
                   WHERE input_type = 'github_push' AND lower(input_name) LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (target, max(1, min(limit, 100)))
            ).fetchall()
        res = []
        for r in rows:
            row_dict = dict(r)
            if row_dict.get("result_json"):
                try:
                    parsed = json.loads(row_dict["result_json"])
                    push_ev = parsed.get("push_event", {})
                    metrics = parsed.get("metrics", {})
                    res.append({
                        "analysis_id": row_dict["id"],
                        "repository": parsed.get("input_name"),
                        "status": row_dict["status"],
                        "created_at": row_dict["created_at"],
                        "commit_sha": push_ev.get("commit_sha"),
                        "short_sha": push_ev.get("short_sha"),
                        "branch": parsed.get("branch"),
                        "commit_message": push_ev.get("message"),
                        "author": push_ev.get("author_name"),
                        "changed_files_count": len(push_ev.get("files", [])),
                        "quality_score": metrics.get("push_quality_score"),
                        "gate_status": metrics.get("push_status"),
                        "analysis_type": parsed.get("analysis_type", "Incremental Analysis"),
                    })
                except Exception:
                    res.append(row_dict)
            else:
                res.append(row_dict)
        return res
