import os
import struct
import unittest
import zipfile
import io

from app.services.archive_manager import read_zip_project
from app.services.file_manager import (InputValidationError, build_pasted_source, detect_language, validate_upload)
from tests.helpers import make_settings, make_zip


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except InputValidationError as e:
        return e.code
    return None


class UploadTests(unittest.TestCase):
    def test_valid_upload(self):
        f = validate_upload("../../evil/app.py", b"x = 1\n", "text/x-python")
        self.assertEqual((f.path, f.language), ("app.py", "python"))  # path stripped to basename

    def test_utf8_bom_ok(self):
        self.assertEqual(validate_upload("a.py", b"\xef\xbb\xbfx=1", None).content, "x=1")

    def test_invalid_extension(self):
        self.assertEqual(code_of(validate_upload, "a.exe", b"MZ"), "unsupported_extension")
        self.assertEqual(code_of(validate_upload, "noext", b"x"), "unsupported_extension")

    def test_bad_mime(self):
        self.assertEqual(code_of(validate_upload, "a.py", b"x=1", "image/png"), "unsupported_mime")

    def test_empty_and_whitespace(self):
        self.assertEqual(code_of(validate_upload, "a.py", b""), "empty_file")
        self.assertEqual(code_of(validate_upload, "a.py", b"  \n\n"), "empty_file")

    def test_oversized(self):
        s = make_settings(max_upload_bytes=10)
        self.assertEqual(code_of(validate_upload, "a.py", b"x" * 11, None, s), "file_too_large")

    def test_binary_and_non_utf8(self):
        self.assertEqual(code_of(validate_upload, "a.py", b"ab\x00cd"), "binary_content")
        self.assertEqual(code_of(validate_upload, "a.py", b"caf\xe9 = 1"), "not_utf8")

    def test_pasted_code_and_detection(self):
        self.assertEqual(build_pasted_source("def f():\n    pass\n", "auto").language, "python")
        self.assertEqual(build_pasted_source("<?php echo 1;", None).language, "php")
        self.assertEqual(code_of(build_pasted_source, "x", "cobol"), "unsupported_language")
        self.assertEqual(code_of(build_pasted_source, "   "), "empty_file")

    def test_detect_by_extension_wins(self):
        self.assertEqual(detect_language("a.go", "whatever"), "go")


class ZipTests(unittest.TestCase):
    def test_valid_zip_inventory(self):
        z = make_zip({"pkg/a.py": "x = 1\n", "README.md": "# hi", "img.png": "PNGDATA", "node_modules/x.js": "1"})
        inv = read_zip_project(z)
        self.assertEqual([f.path for f in inv.files], ["README.md", "pkg/a.py"])
        reasons = {s["path"]: s["reason"] for s in inv.skipped}
        self.assertEqual(reasons["img.png"], "unsupported_type")
        self.assertEqual(reasons["node_modules/x.js"], "ignored_directory")

    def test_path_traversal_rejects_whole_archive(self):
        self.assertEqual(code_of(read_zip_project, make_zip({"../../etc/evil.py": "x=1"})), "zip_path_traversal")
        self.assertEqual(code_of(read_zip_project, make_zip({"a/../../evil.py": "x=1"})), "zip_path_traversal")
        self.assertEqual(code_of(read_zip_project, make_zip({"/abs/evil.py": "x=1"})), "zip_path_traversal")
        self.assertEqual(code_of(read_zip_project, make_zip({"C:\\win\\evil.py": "x=1"})), "zip_path_traversal")
        self.assertEqual(code_of(read_zip_project, make_zip({"..\\evil.py": "x=1"})), "zip_path_traversal")

    def test_malformed_zip(self):
        self.assertEqual(code_of(read_zip_project, b"not a zip at all"), "malformed_zip")
        good = make_zip({"a.py": "x=1"})
        self.assertEqual(code_of(read_zip_project, good[: len(good) // 2]), "malformed_zip")
        self.assertEqual(code_of(read_zip_project, b""), "empty_file")

    def test_empty_archive_variants(self):
        self.assertEqual(code_of(read_zip_project, make_zip({})), "empty_archive")
        self.assertEqual(code_of(read_zip_project, make_zip({"only.png": "x", "dir/": ""})), "empty_archive")

    def test_wrong_mime(self):
        self.assertEqual(code_of(read_zip_project, make_zip({"a.py": "x=1"}), "image/png"), "unsupported_mime")

    def test_zip_size_limit(self):
        z = make_zip({"a.py": "x=1"})
        self.assertEqual(code_of(read_zip_project, z, None, make_settings(max_zip_bytes=10)), "zip_too_large")

    def test_file_count_limit_skips_extras(self):
        z = make_zip({f"f{i}.py": "x=1" for i in range(5)})
        inv = read_zip_project(z, None, make_settings(max_extracted_files=3))
        self.assertEqual(len(inv.files), 3)
        self.assertEqual(sum(s["reason"] == "file_count_limit" for s in inv.skipped), 2)

    def test_oversized_member_and_total_limit(self):
        z = make_zip({"big.py": "x=1\n" * 1000, "small.py": "y=2"})
        inv = read_zip_project(z, None, make_settings(max_file_bytes=100))
        self.assertEqual([f.path for f in inv.files], ["small.py"])
        inv2 = read_zip_project(make_zip({"a.py": "a" * 60, "b.py": "b" * 60}), None, make_settings(max_extracted_bytes=100))
        self.assertEqual(len(inv2.files), 1)

    def test_zip_bomb_ratio_guard(self):
        z = make_zip({"bomb.py": "0" * 500_000, "ok.py": "x=1"})
        inv = read_zip_project(z, None, make_settings(max_compression_ratio=50, max_file_bytes=10_000_000))
        self.assertEqual([f.path for f in inv.files], ["ok.py"])
        self.assertEqual(next(s for s in inv.skipped if s["path"] == "bomb.py")["reason"], "suspicious_compression_ratio")

    def test_declared_size_lie_is_caught(self):
        z = bytearray(make_zip({"liar.py": "x" * 5000, "ok.py": "y=1"}, zipfile.ZIP_STORED))
        # patch the declared uncompressed size in the central directory down to 10 bytes
        idx = z.index(b"PK\x01\x02")
        z[idx + 24: idx + 28] = struct.pack("<I", 10)
        inv = read_zip_project(bytes(z), None, make_settings(max_file_bytes=100))
        self.assertEqual([f.path for f in inv.files], ["ok.py"])
        self.assertEqual(next(s for s in inv.skipped if s["path"] == "liar.py")["reason"], "unreadable_member")

    def test_duplicate_names_never_overwrite(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("a.py", "first = 1")
            zf.writestr("a.py", "second = 2")
        inv = read_zip_project(buf.getvalue())
        self.assertEqual(len(inv.files), 1)
        self.assertEqual(inv.files[0].content, "first = 1")

    def test_symlink_skipped(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zi = zipfile.ZipInfo("link.py")
            zi.external_attr = (0o120777 << 16)
            zf.writestr(zi, "/etc/passwd")
            zf.writestr("ok.py", "x=1")
        inv = read_zip_project(buf.getvalue())
        self.assertEqual([f.path for f in inv.files], ["ok.py"])
        self.assertEqual(inv.skipped[0]["reason"], "symlink")

    def test_binary_and_non_utf8_members_skipped(self):
        z = make_zip({"b.py": b"ab\x00cd", "good.py": "x=1"})
        inv = read_zip_project(z)
        self.assertEqual([f.path for f in inv.files], ["good.py"])

    def test_no_files_written_to_disk(self):
        before = set(os.listdir("."))
        read_zip_project(make_zip({"x/y/z.py": "a=1"}))
        self.assertEqual(before, set(os.listdir(".")))


if __name__ == "__main__":
    unittest.main()
