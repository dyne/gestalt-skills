"""Small loading surfaces and self-contained writing-skill resources."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("academic", "humanizer", "latex")
HELPERS = {
    "latex/scripts/check_build.py": "dbf341b66c351e99e21e13fd027d7b87a02fde34e820db7f2dba39527b34df17",
    "humanizer/scripts/text_hygiene.py": "30cf54572336fc13bab63a4e3b534af59adb0c7898363c4b23de9bbcfc1cb093",
}


class WritingResources(unittest.TestCase):
    def test_entrypoint_loading_budget_and_reference_reachability(self):
        for name in NAMES:
            with self.subTest(skill=name):
                skill = ROOT / "skills" / name
                entry = skill / "SKILL.md"
                self.assertLessEqual(len(entry.read_bytes()), 6000)
                pending, visited = [entry], set()
                while pending:
                    path = pending.pop()
                    if path in visited:
                        continue
                    visited.add(path)
                    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                            continue
                        linked = (path.parent / target.split("#", 1)[0]).resolve()
                        self.assertTrue(linked.is_relative_to(skill.resolve()), target)
                        self.assertTrue(linked.is_file(), target)
                        if linked.suffix == ".md":
                            pending.append(linked)
                self.assertTrue(set(p.resolve() for p in skill.rglob("*.md")) <=
                                set(p.resolve() for p in visited), "orphan Markdown resource")

    def test_imported_helpers_retain_upstream_bytes_and_are_documented(self):
        for relative, digest in HELPERS.items():
            with self.subTest(helper=relative):
                path = ROOT / "skills" / relative
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                skill = path.parents[1]
                docs = "\n".join(p.read_text() for p in skill.rglob("*.md"))
                self.assertIn(f"scripts/{path.name}", docs)

    def test_hygiene_runs_from_an_isolated_installed_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            installed = directory / "installed"
            shutil.copytree(ROOT / "skills/humanizer", installed)
            command = [sys.executable, str(installed / "scripts/text_hygiene.py")]
            original = 'Ciao\u200b\n"quoted\u200b"'
            scan = subprocess.run(command, cwd=directory, input=original, text=True,
                                  capture_output=True, check=False, timeout=10)
            self.assertEqual(scan.returncode, 0, scan.stderr)
            self.assertEqual(scan.stdout, original)
            cleaned = subprocess.run(command + ["--remove-safe"], cwd=directory,
                                     input=original, text=True, capture_output=True,
                                     check=False, timeout=10)
            self.assertEqual(cleaned.returncode, 0, cleaned.stderr)
            self.assertEqual(cleaned.stdout, 'Ciao\n"quoted\u200b"')

    def test_build_checker_reports_missing_engine_in_an_isolated_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            installed = directory / "installed"
            shutil.copytree(ROOT / "skills/latex", installed)
            source = directory / "paper.tex"
            source.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
            environment = os.environ.copy()
            environment["PATH"] = ""
            output = directory / "new-build"
            result = subprocess.run(
                [sys.executable, str(installed / "scripts/check_build.py"), str(source),
                 "--output", str(output)], cwd=directory, env=environment,
                text=True, capture_output=True, check=False, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Required tool is not on PATH", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
