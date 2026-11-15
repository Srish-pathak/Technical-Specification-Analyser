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
