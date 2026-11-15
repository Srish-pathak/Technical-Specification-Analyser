import ast
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from app.services import analysis_service as svc
from app.services.file_manager import InputValidationError
from tests.helpers import SAMPLE_BAD, make_settings, make_zip, temp_db

APP_DIR = Path(__file__).resolve().parents[1] / "app"


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = temp_db()

    def test_code_analysis_end_to_end(self):
        r = svc.submit_code(self.db, SAMPLE_BAD, "python", "bad.py", use_external_tools=False)
        self.assertEqual(r["status"], "completed")
        rules = {f["rule_id"] for f in r["findings"]}
        self.assertTrue({"TSA-SEC-001", "TSA-SEC-004", "TSA-QLT-002", "TSA-CPX-003"} <= rules)
        m = r["metrics"]
        self.assertEqual(m["function_count"], 2)
        self.assertEqual(m["total_findings"], len(r["findings"]))
        self.assertEqual(sum(m["severity_counts"].values()), len(r["findings"]))
        self.assertIsNotNone(self.db.get(r["analysis_id"]))

    def test_every_finding_has_full_schema(self):
        r = svc.submit_code(self.db, SAMPLE_BAD, "python", "bad.py", use_external_tools=False)
        keys = {"finding_id", "rule_id", "category", "severity", "file_path", "line_number", "column_number",
                "description", "evidence", "recommended_correction", "source", "confidence"}
        for f in r["findings"]:
            self.assertTrue(keys <= set(f), f)
            self.assertIn(f["source"], {"static_analyzer", "deterministic_rule", "ai_agent", "human_verification"})

    def test_line_numbers_point_at_real_evidence(self):
        r = svc.submit_code(self.db, SAMPLE_BAD, "python", "bad.py", use_external_tools=False)
        lines = SAMPLE_BAD.splitlines()
        for f in r["findings"]:
            if f["category"] == "security" and f["rule_id"] != "TSA-SEC-004":
                self.assertEqual(lines[f["line_number"] - 1].strip(), f["evidence"])

    def test_syntax_error_reported_not_crashed(self):
        r = svc.submit_code(self.db, "def broken(:\n", "python", "x.py", use_external_tools=False)
        self.assertEqual(r["status"], "completed")
        self.assertEqual([f["rule_id"] for f in r["findings"]], ["TSA-SYN-001"])
        self.assertTrue(any("No parsable Python" in l for l in r["limitations"]))

    def test_non_python_is_inventoried_not_faked(self):
        r = svc.submit_code(self.db, "function f() { return 1; }", "javascript", "a.js", use_external_tools=False)
        self.assertEqual(r["findings"], [])
        self.assertTrue(any("javascript" in l for l in r["limitations"]))
        self.assertFalse(r["files"][0]["analyzed"])

    def test_zip_project_multi_file(self):
        z = make_zip({"pkg/__init__.py": "", "pkg/a.py": SAMPLE_BAD, "pkg/b.py": "def broken(:\n",
                      "README.md": "# x", "app.js": "var a=1;"})
        r = svc.submit_zip(self.db, "proj.zip", z, "application/zip", use_external_tools=False)
        paths = {f["file_path"] for f in r["findings"]}
        self.assertEqual(paths, {"pkg/a.py", "pkg/b.py"})
        self.assertIn("pkg/a.py", r["structure"])
        self.assertNotIn("pkg/b.py", r["structure"])
        self.assertEqual(r["language"], "mixed")
        self.assertIn("skipped", r["inventory"])

    def test_documentation_coverage_is_measured(self):
        src = '"""m"""\ndef a():\n    """d"""\ndef b():\n    pass\nclass C:\n    pass\n'
        m = svc.submit_code(self.db, src, "python", "d.py", use_external_tools=False)["metrics"]
        self.assertEqual((m["doc_items"], m["doc_documented"]), (4, 2))
        self.assertEqual(m["documentation_coverage"], 50.0)

    def test_invalid_input_raises_validation_error(self):
        with self.assertRaises(InputValidationError):
            svc.submit_code(self.db, "", "python", None)
        with self.assertRaises(InputValidationError):
            svc.submit_zip(self.db, "a.zip", b"junk", None)
        self.assertEqual(self.db.stats()["total_analyses"], 0)   # rejected input is not recorded as an analysis

    def test_tool_status_is_honest(self):
        r = svc.submit_code(self.db, "x = 1\n", "python", "a.py")
        for t in r["tools"]:
            if not t["available"]:
                self.assertFalse(t["ran"], t)
        self.assertTrue(any(t["name"] == "builtin-ast" and t["ran"] for t in r["tools"]))

    def test_ai_block_never_claims_a_run(self):
        r = svc.submit_code(self.db, "x = 1\n", "python", "a.py", use_external_tools=False)
        self.assertFalse(r["ai"]["ran"])
        self.assertFalse(any(f["source"] == "ai_agent" for f in r["findings"]))

    def test_unexpected_failure_is_persisted(self):
        orig = svc.analyze_files
        svc.analyze_files = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            r = svc.submit_code(self.db, "x = 1\n", "python", "a.py")
        finally:
            svc.analyze_files = orig
        self.assertEqual(r["status"], "failed")
        self.assertEqual(self.db.stats()["failed"], 1)


class FakeToolTests(unittest.TestCase):
    """Exercise the tool-runner path with *fake* executables (NOT real Ruff/Bandit)."""

    def setUp(self):
        self.bin = tempfile.mkdtemp()
        self.old_path = os.environ["PATH"]
        os.environ["PATH"] = self.bin + os.pathsep + self.old_path

    def tearDown(self):
        os.environ["PATH"] = self.old_path

    def fake(self, name, body):
        p = Path(self.bin) / name
        p.write_text("#!/bin/sh\n" + body)
        p.chmod(p.stat().st_mode | stat.S_IEXEC)

    def test_fake_ruff_findings_mapped_back_to_original_paths(self):
        self.fake("ruff", 'if [ "$1" = "--version" ]; then echo "ruff 0.0-fake"; exit 0; fi\n'
                          'echo \'[{"code":"F401","message":"unused","filename":"f0.py","location":{"row":1,"column":8}}]\'\nexit 1\n')
        r = svc.submit_code(temp_db(), "import os\n", "python", "my file.py")
        ruff = next(t for t in r["tools"] if t["name"] == "ruff")
        self.assertTrue(ruff["ran"])
        self.assertEqual(ruff["version"], "ruff 0.0-fake")
        f = [x for x in r["findings"] if x["rule_id"] == "ruff:F401"][0]
        self.assertEqual((f["file_path"], f["source"]), ("my file.py", "static_analyzer"))
        # Ruff ran, so the built-in quality fallback must not double-report
        self.assertFalse(any(x["rule_id"].startswith("TSA-QLT") for x in r["findings"]))

    def test_tool_timeout_is_reported_not_hidden(self):
        self.fake("ruff", 'if [ "$1" = "--version" ]; then echo fake; exit 0; fi\nsleep 5\n')
        r = svc.submit_code(temp_db(), "import os\n", "python", "a.py", make_settings(tool_timeout_seconds=1))
        ruff = next(t for t in r["tools"] if t["name"] == "ruff")
        self.assertFalse(ruff["ran"])
        self.assertIn("timed out", ruff["note"])
        self.assertTrue(any(f["rule_id"] == "TSA-QLT-001" for f in r["findings"]))  # fallback used

    def test_tool_garbage_output_handled(self):
        self.fake("bandit", 'if [ "$1" = "--version" ]; then echo fake; exit 0; fi\necho "<html>not json"\n')
        r = svc.submit_code(temp_db(), "x = 1\n", "python", "a.py")
        b = next(t for t in r["tools"] if t["name"] == "bandit")
        self.assertFalse(b["ran"])
        self.assertIn("invalid JSON", b["note"])


class DatabaseTests(unittest.TestCase):
    def test_empty_state(self):
        s = temp_db().stats()
        self.assertTrue(s["empty"])
        self.assertEqual((s["total_analyses"], s["total_issues"]), (0, 0))
        self.assertIsNone(s["avg_complexity"])
        self.assertIsNone(s["documentation_coverage"])
        self.assertEqual(s["recent"], [])

    def test_stats_come_from_stored_records(self):
        db = temp_db()
        a = svc.submit_code(db, SAMPLE_BAD, "python", "a.py", use_external_tools=False)
        b = svc.submit_code(db, "def f():\n    return 1\n", "python", "b.py", use_external_tools=False)
        s = db.stats()
        self.assertEqual(s["total_analyses"], 2)
        self.assertEqual(s["total_issues"], a["metrics"]["total_findings"] + b["metrics"]["total_findings"])
        self.assertEqual(s["critical_high"], a["metrics"]["severity_counts"]["High"])
        total_fn = a["metrics"]["function_count"] + b["metrics"]["function_count"]
        cx = a["metrics"]["complexity_sum"] + b["metrics"]["complexity_sum"]
        self.assertEqual(s["avg_complexity"], round(cx / total_fn, 2))
        self.assertEqual(s["recent"][0]["id"], b["analysis_id"])   # newest first

    def test_history_list_and_pagination(self):
        db = temp_db()
        ids = [svc.submit_code(db, "x = 1\n", "python", f"{i}.py", use_external_tools=False)["analysis_id"] for i in range(3)]
        listed = db.list(limit=2)
        self.assertEqual([r["id"] for r in listed], ids[::-1][:2])
        self.assertEqual(len(db.list(limit=10, offset=2)), 1)
        self.assertIsNone(db.get("A-doesnotexist"))

    def test_source_text_is_not_stored(self):
        db = temp_db()
        secret_src = 'x = 1  # UNIQUE_SOURCE_MARKER_9f3a\n'
        r = svc.submit_code(db, secret_src, "python", "a.py", use_external_tools=False)
        import sqlite3
        raw = sqlite3.connect(db.path).execute("SELECT result_json FROM analyses WHERE id=?", (r["analysis_id"],)).fetchone()[0]
        self.assertNotIn("UNIQUE_SOURCE_MARKER_9f3a", raw)

    def test_secret_value_not_stored(self):
        db = temp_db()
        r = svc.submit_code(db, 'password = "hunter2-very-secret"\n', "python", "a.py", use_external_tools=False)
        self.assertTrue(any(f["rule_id"] == "TSA-SEC-004" for f in r["findings"]))
        import sqlite3
        raw = sqlite3.connect(db.path).execute("SELECT result_json FROM analyses").fetchone()[0]
        self.assertNotIn("hunter2", raw)

    def test_retention_purge(self):
        db = temp_db()
        svc.submit_code(db, "x = 1\n", "python", "a.py", use_external_tools=False)
        self.assertEqual(db.purge_older_than(30), 0)
        self.assertEqual(db.purge_older_than(-1), 1)
        self.assertTrue(db.stats()["empty"])


class SafetyTests(unittest.TestCase):
    """Critical rule: uploaded code is parsed, never executed or imported."""

    def test_uploaded_code_is_never_executed(self):
        tmp = tempfile.mkdtemp()
        m1, m2, m3 = (os.path.join(tmp, n) for n in ("toplevel.flag", "system.flag", "import.flag"))
        canary = Path(tmp) / "tsa_canary_mod.py"
        canary.write_text(f"open({m3!r}, 'w').write('imported')\n")
        sys.path.insert(0, tmp)
        evil = (f"import os, tsa_canary_mod\n"
                f"open({m1!r}, 'w').write('executed')\n"
                f"os.system('touch {m2}')\n"
                f"class Boom:\n    def __init__(self):\n        raise SystemExit(1)\n"
                f"Boom()\nexit()\n")
        try:
            db = temp_db()
            svc.submit_code(db, evil, "python", "evil.py")
            svc.submit_zip(db, "evil.zip", make_zip({"evil.py": evil, "setup.py": evil}), "application/zip")
            svc.submit_file(db, "evil.py", evil.encode(), "text/plain")
        finally:
            sys.path.remove(tmp)
        for flag in (m1, m2, m3):
            self.assertFalse(os.path.exists(flag), f"uploaded code executed: {flag}")
        self.assertNotIn("tsa_canary_mod", sys.modules)

    def test_app_contains_no_dynamic_execution(self):
        banned_names = {"eval", "exec", "compile", "__import__", "execfile"}
        banned_attr = {"import_module", "run_path", "run_module", "system", "popen", "spawn", "spawnl", "execv", "execl"}
        offenders = []
        for py in APP_DIR.rglob("*.py"):
            tree = ast.parse(py.read_text(encoding="utf-8"))
            for n in ast.walk(tree):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Name) and n.func.id in banned_names:
                        offenders.append((py.name, n.lineno, n.func.id))
                    if isinstance(n.func, ast.Attribute) and n.func.attr in banned_attr:
                        offenders.append((py.name, n.lineno, n.func.attr))
        self.assertEqual(offenders, [])

    def test_subprocess_confined_to_tool_runner(self):
        users = []
        for py in APP_DIR.rglob("*.py"):
            tree = ast.parse(py.read_text(encoding="utf-8"))
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) \
                        and n.func.value.id == "subprocess":
                    users.append(py.name)
                    kws = {k.arg: getattr(k.value, "value", None) for k in n.keywords}
                    self.assertIs(kws.get("shell"), False, f"{py.name} must pass shell=False")
        self.assertEqual(set(users), {"tool_runner.py"})


if __name__ == "__main__":
    unittest.main()
