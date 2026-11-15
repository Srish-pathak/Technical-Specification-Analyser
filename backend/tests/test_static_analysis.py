import ast
import unittest

from app.analyzers.ast_analyzer import extract_structure
from app.analyzers.complexity_analyzer import analyze_complexity, mccabe
from app.analyzers.quality_analyzer import builtin_quality, parse_ruff_json, ruff_severity
from app.analyzers.security_analyzer import builtin_security, merge_security, parse_bandit_json
from app.analyzers.syntax_analyzer import parse_python
from app.schemas.findings import Finding
from tests.helpers import SAMPLE_BAD


def prep(src, path="m.py"):
    tree = ast.parse(src)
    return tree, extract_structure(tree, src, path)


class SyntaxTests(unittest.TestCase):
    def test_valid(self):
        tree, err = parse_python("x = 1\n", "a.py")
        self.assertIsNotNone(tree)
        self.assertIsNone(err)

    def test_invalid_syntax_reports_line(self):
        tree, err = parse_python("def f(:\n    pass\n", "a.py")
        self.assertIsNone(tree)
        self.assertEqual(err.rule_id, "TSA-SYN-001")
        self.assertEqual(err.line_number, 1)
        self.assertEqual(err.severity, "High")

    def test_nul_byte_handled(self):
        tree, err = parse_python("x = 1\x00", "a.py")
        self.assertIsNone(tree)
        self.assertIsNotNone(err)

    def test_empty_source_parses(self):
        tree, err = parse_python("", "a.py")
        self.assertIsNotNone(tree)


class AstTests(unittest.TestCase):
    SRC = '''"""Module doc."""
import os
from a.b import c as d

class Base:
    """Doc."""
    def m(self, x: int) -> int:
        return x

def top(a, b=1, *args, **kw):
    """Doc."""
    helper()
    return os.path.join(a, b)

async def helper():
    pass
'''

    def setUp(self):
        _, self.st = prep(self.SRC)

    def test_functions_found(self):
        names = {f.qualname for f in self.st.functions}
        self.assertEqual(names, {"Base.m", "top", "helper"})

    def test_class_found_with_methods(self):
        self.assertEqual(self.st.classes[0].name, "Base")
        self.assertEqual(self.st.classes[0].methods, ["m"])
        self.assertTrue(self.st.classes[0].has_docstring)

    def test_params_returns_and_untyped(self):
        top = next(f for f in self.st.functions if f.name == "top")
        self.assertEqual(top.params, ["a", "b", "*args", "**kw"])
        self.assertEqual(top.untyped_params, ["a", "b", "args", "kw"])
        m = next(f for f in self.st.functions if f.name == "m")
        self.assertEqual(m.returns, "int")
        self.assertTrue(m.is_method)

    def test_imports_and_lines(self):
        self.assertEqual(self.st.imports[0].names, ["os"])
        self.assertEqual(self.st.imports[1].module, "a.b")
        self.assertEqual(self.st.imports[1].lineno, 3)

    def test_docstrings_calls_relationships(self):
        top = next(f for f in self.st.functions if f.name == "top")
        self.assertTrue(top.has_docstring)
        self.assertIn("os.path.join", top.calls)
        self.assertIn("helper", top.calls_local)
        self.assertTrue(self.st.has_docstring)

    def test_async_flag(self):
        self.assertTrue(next(f for f in self.st.functions if f.name == "helper").is_async)


class ComplexityTests(unittest.TestCase):
    def test_mccabe_known_value(self):
        src = "def f(a,b):\n    if a and b or a:\n        for i in a:\n            while b:\n                pass\n    return [x for x in a if x]\n"
        fn = ast.parse(src).body[0]
        self.assertEqual(mccabe(fn), 8)  # 1 + if + 2 boolops + for + while + comprehension(1+1)

    def test_simple_function_is_one(self):
        self.assertEqual(mccabe(ast.parse("def f():\n    return 1\n").body[0]), 1)

    def test_nested_function_not_counted_in_parent(self):
        src = "def outer():\n    def inner(x):\n        if x:\n            return 1\n    return inner\n"
        tree, st = prep(src)
        analyze_complexity(tree, st, src, use_radon=False)
        by = {f.name: f.complexity for f in st.functions}
        self.assertEqual(by["outer"], 1)
        self.assertEqual(by["inner"], 2)

    def test_deep_function_findings_and_metrics(self):
        tree, st = prep(SAMPLE_BAD)
        findings, metrics, _ = analyze_complexity(tree, st, SAMPLE_BAD, use_radon=False)
        rules = {f.rule_id for f in findings}
        self.assertIn("TSA-CPX-003", rules)   # nesting 6 > 4
        self.assertIn("TSA-CPX-004", rules)   # 6 params > 5
        self.assertEqual(metrics["tool"], "builtin-mccabe")
        self.assertIsNone(metrics["maintainability_index"])  # honest: not computed without radon
        self.assertEqual(metrics["functions"], 2)

    def test_high_complexity_flagged(self):
        body = "\n".join(f"    if a == {i}:\n        return {i}" for i in range(15))
        src = f"def big(a):\n{body}\n    return 0\n"
        tree, st = prep(src)
        findings, _, _ = analyze_complexity(tree, st, src, use_radon=False)
        f = next(x for x in findings if x.rule_id == "TSA-CPX-001")
        self.assertIn("16", f.description)
        self.assertEqual(f.severity, "Low")


class QualityTests(unittest.TestCase):
    def rules(self, src):
        tree = ast.parse(src)
        return {f.rule_id: f for f in builtin_quality(tree, src, "m.py")}

    def test_unused_import(self):
        r = self.rules("import os\nimport sys\nprint(sys.argv)\n")
        self.assertIn("TSA-QLT-001", r)
        self.assertIn("'os'", r["TSA-QLT-001"].description)

    def test_used_import_not_flagged(self):
        self.assertNotIn("TSA-QLT-001", self.rules("import os\nos.getcwd()\n"))

    def test_all_export_not_flagged(self):
        self.assertNotIn("TSA-QLT-001", self.rules("from x import y\n__all__ = ['y']\n"))

    def test_bare_except_and_mutable_default(self):
        r = self.rules("def f(a=[]):\n    try:\n        pass\n    except:\n        pass\n")
        self.assertIn("TSA-QLT-002", r)
        self.assertIn("TSA-QLT-003", r)

    def test_unused_local(self):
        r = self.rules("def f():\n    x = 1\n    y = 2\n    return y\n")
        self.assertIn("'x'", r["TSA-QLT-006"].description)

    def test_naming(self):
        r = self.rules("def BadName():\n    pass\nclass bad_class:\n    pass\n")
        self.assertIn("TSA-QLT-005", r)

    def test_clean_code_no_findings(self):
        self.assertEqual(self.rules('import os\n\n\ndef f(a):\n    return os.path.join(a, "b")\n'), {})

    def test_ruff_json_parsing_and_severity(self):
        sample = '[{"code":"F401","message":"`os` imported but unused","filename":"/tmp/x/f0.py","location":{"row":1,"column":8},"fix":{"applicability":"safe"}}]'
        out = parse_ruff_json(sample, {"f0.py": "pkg/a.py"}, {"pkg/a.py": "import os\n"})
        self.assertEqual(out[0].file_path, "pkg/a.py")
        self.assertEqual(out[0].rule_id, "ruff:F401")
        self.assertEqual(out[0].source, "static_analyzer")
        self.assertEqual(out[0].evidence, "import os")
        self.assertEqual(ruff_severity("E902"), "High")  # E9 family
        self.assertEqual(ruff_severity("B006"), "Medium")

    def test_ruff_malformed_json_raises(self):
        with self.assertRaises(ValueError):
            parse_ruff_json("not json", {}, {})


class SecurityTests(unittest.TestCase):
    def findings(self, src):
        tree, st = prep(src)
        return builtin_security(tree, src, st)

    def rule_ids(self, src):
        return {f.rule_id for f in self.findings(src)}

    def test_known_issues_in_sample(self):
        ids = self.rule_ids(SAMPLE_BAD)
        self.assertTrue({"TSA-SEC-001", "TSA-SEC-002", "TSA-SEC-003", "TSA-SEC-004", "TSA-SEC-006"} <= ids)

    def test_secret_value_never_in_evidence(self):
        for f in self.findings(SAMPLE_BAD):
            self.assertNotIn("sk_live", f.evidence)
            self.assertNotIn("sk_live", f.description)

    def test_alias_resolution(self):
        src = "import subprocess as sp\nfrom os import system\nsp.run(x, shell=True)\nsystem(x)\n"
        fs = self.findings(src)
        self.assertEqual(sorted(f.line_number for f in fs), [3, 4])

    def test_shell_false_not_flagged(self):
        self.assertEqual(self.rule_ids("import subprocess\nsubprocess.run(['ls'], shell=False)\n"), set())

    def test_yaml_safe_vs_unsafe(self):
        self.assertIn("TSA-SEC-003", self.rule_ids("import yaml\nyaml.load(x)\n"))
        self.assertNotIn("TSA-SEC-003", self.rule_ids("import yaml\nyaml.load(x, Loader=yaml.SafeLoader)\n"))
        self.assertNotIn("TSA-SEC-003", self.rule_ids("import yaml\nyaml.safe_load(x)\n"))

    def test_sql_injection_pattern(self):
        self.assertIn("TSA-SEC-007", self.rule_ids('cur.execute(f"SELECT * FROM t WHERE id={x}")\n'))
        self.assertNotIn("TSA-SEC-007", self.rule_ids('cur.execute("SELECT * FROM t WHERE id=?", (x,))\n'))

    def test_verify_false(self):
        self.assertIn("TSA-SEC-005", self.rule_ids("import requests\nrequests.get(u, verify=False)\n"))

    def test_placeholder_and_non_secret_names_ignored(self):
        self.assertEqual(self.rule_ids('password = "changeme"\nmax_tokens = "abcdefgh"\ntoken_url = "https://x.y/z"\n'), set())

    def test_literal_eval_is_not_flagged(self):
        self.assertEqual(self.rule_ids("import ast\nast.literal_eval(x)\n"), set())

    def test_confirmed_findings_carry_deterministic_source(self):
        for f in self.findings(SAMPLE_BAD):
            self.assertEqual(f.source, "deterministic_rule")

    def test_bandit_json_parsing(self):
        sample = ('{"results":[{"test_id":"B307","test_name":"blacklist","issue_text":"Use of possibly insecure function - eval.",'
                  '"issue_severity":"MEDIUM","issue_confidence":"HIGH","filename":"./f0.py","line_number":2,"col_offset":0}]}')
        out = parse_bandit_json(sample, {"f0.py": "a.py"}, {"a.py": "x=1\neval(y)\n"})
        self.assertEqual((out[0].rule_id, out[0].severity, out[0].source), ("bandit:B307", "Medium", "static_analyzer"))
        self.assertEqual(out[0].evidence, "eval(y)")

    def test_merge_drops_equivalent_builtin_duplicate(self):
        src = "eval(x)\n"
        tree, st = prep(src, "a.py")
        built = builtin_security(tree, src, st)
        bandit = [Finding("bandit:B307", "security", "Medium", "a.py", 1, 1, "d", "e", "r", "static_analyzer", tool="bandit")]
        merged = merge_security(built, bandit)
        self.assertEqual([f.rule_id for f in merged], ["bandit:B307"])

    def test_bandit_malformed_json_raises(self):
        with self.assertRaises(ValueError):
            parse_bandit_json("{oops", {}, {})


if __name__ == "__main__":
    unittest.main()
