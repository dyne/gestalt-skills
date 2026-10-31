"""Observable contracts of the optional Dear ImGui inspection helpers."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/dear-imgui/scripts"
# Import without leaving bytecode artifacts in the canonical skill tree.
inspector = types.ModuleType("inspect_imgui")
source = SCRIPTS / "inspect_imgui.py"
exec(compile(source.read_bytes(), str(source), "exec"), inspector.__dict__)


class ImGuiHelpers(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.imgui = self.root / "imgui"
        self.imgui.mkdir()
        self.header = self.imgui / "imgui.h"
        self.header.write_text('#define IMGUI_VERSION "1.93.0"\n#define IMGUI_VERSION_NUM 19300\n#define IMGUI_HAS_TEXTURES\n')
        self.app = self.root / "app"
        self.app.mkdir()

    def invoke(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              text=True, capture_output=True, timeout=10)

    def lookup(self, query, *args):
        return self.invoke("lookup_imgui.py", query, "--imgui-dir", self.imgui, *args)

    def test_profile_version_features_and_missing_files(self):
        result = inspector.profile(self.imgui)
        self.assertEqual((result["version"], result["version_num"]), ("1.93.0", 19300))
        self.assertTrue(result["feature_macros"]["IMGUI_HAS_TEXTURES"])
        self.assertFalse(result["feature_macros"]["IMGUI_HAS_DOCK"])
        self.assertTrue(result["core_files"]["imgui.cpp"]["missing"])
        self.assertEqual(len(result["core_files"]["imgui.h"]["sha256"]), 64)

    def test_commented_and_raw_string_defines_do_not_override_profile(self):
        self.header.write_text('/* #define IMGUI_VERSION "fake" */\n'
                               'auto example = R"tag(\n#define IMGUI_VERSION "raw"\n)tag";\n'
                               '# define IMGUI_VERSION "1.93.0" // real\n'
                               '#define IMGUI_VERSION_NUM 19300 /* real */\n')
        self.assertEqual(inspector.profile(self.imgui)["version"], "1.93.0")

    def test_missing_version_is_unknown(self):
        self.header.write_text("// no version definitions\n")
        result = inspector.profile(self.imgui)
        self.assertIsNone(result["version"])
        self.assertIsNone(result["version_num"])

    def test_comment_mask_preserves_offsets_newlines_and_literals(self):
        source = 'auto s = "// literal"; /* comment\ncontinued */\nImGui::Columns(2);\n'
        masked = inspector.remove_comments(source)
        self.assertEqual(len(masked), len(source))
        self.assertEqual(masked.count("\n"), source.count("\n"))
        self.assertIn('"// literal"', masked)
        self.assertNotIn("continued", masked)

    def test_digit_separators_and_continued_comments(self):
        source = "int x = 1'000; // hidden\\\nImGui::Columns(2);\nImGui::Columns(3);\n"
        masked = inspector.remove_comments(source)
        self.assertNotIn("Columns(2)", masked)
        self.assertIn("Columns(3)", masked)

    def test_scan_reports_real_call_location_and_masks_comment(self):
        (self.app / "main.cpp").write_text('// ImGui::Columns(1);\nImGui::Columns(2);\n')
        result = inspector.scan(self.app, self.imgui, False, 20)
        findings = [f for f in result["findings"] if f["code"] == "legacy_columns"]
        self.assertEqual([(f["file"], f["line"]) for f in findings], [("main.cpp", 2)])

    def test_scan_vendor_opt_in_and_build_exclusion(self):
        for directory in ("vendor", "build"):
            p = self.app / directory
            p.mkdir()
            (p / "x.cpp").write_text("ImGui::Columns(2);\n")
        self.assertEqual(inspector.scan(self.app, self.imgui, False, 20)["files_scanned"], 0)
        self.assertEqual(inspector.scan(self.app, self.imgui, True, 20)["files_scanned"], 1)

    def test_scan_file_limit_is_an_error_not_clean_result(self):
        for name in ("a.cpp", "b.cpp"):
            (self.app / name).write_text("// source\n")
        with self.assertRaisesRegex(ValueError, "File limit"):
            inspector.scan(self.app, self.imgui, False, 1)

    def test_large_source_is_reported_skipped(self):
        (self.app / "large.cpp").write_bytes(b" " * (3 * 1024 * 1024 + 1))
        result = inspector.scan(self.app, self.imgui, False, 20)
        self.assertEqual(result["files_scanned"], 0)
        self.assertEqual(result["files_skipped"][0]["file"], "large.cpp")

    def test_scan_does_not_follow_file_or_directory_links(self):
        external = self.root / "outside"
        external.mkdir()
        source = external / "x.cpp"
        source.write_text("ImGui::Columns(2);\n")
        (self.app / "linked.cpp").symlink_to(source)
        (self.app / "linked").symlink_to(external, target_is_directory=True)
        self.assertEqual(inspector.scan(self.app, self.imgui, False, 20)["files_scanned"], 0)

    def test_inspector_cli_json_and_read_only(self):
        before = self.header.read_bytes()
        result = self.invoke("inspect_imgui.py", "--imgui-dir", self.imgui)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["profile"]["version_num"], 19300)
        self.assertEqual(self.header.read_bytes(), before)

    def test_inspector_errors(self):
        for args in (("--max-files", 0), ("--project-dir", self.header)):
            with self.subTest(args=args):
                result = self.invoke("inspect_imgui.py", "--imgui-dir", self.imgui, *args)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(result.stdout)

    def test_lookup_literal_context_location_and_read_only(self):
        self.header.write_text("first\nBeginTable()\nlast\n")
        before = self.header.read_bytes()
        result = self.lookup("BeginTable", "--area", "public", "--context", 1)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["match_count"], 1)
        match = data["matches"][0]
        self.assertEqual((match["file"], match["line"], match["context_start_line"]), ("imgui.h", 2, 1))
        self.assertEqual(match["context"], ["first", "BeginTable()", "last"])
        self.assertEqual(self.header.read_bytes(), before)

    def test_lookup_truncation_keeps_total_count(self):
        self.header.write_text("Target\nTarget\nTarget\n")
        data = json.loads(self.lookup("Target", "--limit", 1).stdout)
        self.assertEqual((data["match_count"], data["returned_count"], data["truncated"]), (3, 1, True))

    def test_lookup_no_match_and_case_sensitivity(self):
        result = self.lookup("imgui_version")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["matches"], [])

    def test_lookup_validation(self):
        for query, args in (("", ()), ("x", ("--context", -1)),
                            ("x", ("--context", 21)), ("x", ("--limit", 0)),
                            ("x", ("--limit", 501))):
            with self.subTest(query=query, args=args):
                self.assertEqual(self.lookup(query, *args).returncode, 2)

    def test_lookup_area_and_symlink_exclusion(self):
        (self.imgui / "imgui_demo.cpp").write_text("Needle\n")
        (self.imgui / "docs").symlink_to(self.app, target_is_directory=True)
        (self.app / "outside.md").write_text("Needle\n")
        data = json.loads(self.lookup("Needle", "--area", "demo").stdout)
        self.assertEqual([m["file"] for m in data["matches"]], ["imgui_demo.cpp"])
        self.assertEqual(self.lookup("Needle", "--area", "docs").returncode, 1)

    def test_missing_checkout_errors(self):
        self.header.unlink()
        for script, extra in (("inspect_imgui.py", ()), ("lookup_imgui.py", ("x",))):
            with self.subTest(script=script):
                result = self.invoke(script, *extra, "--imgui-dir", self.imgui)
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
