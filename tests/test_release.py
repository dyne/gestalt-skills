"""Verify the delivered archive contract using copies of current skill content."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# Import this collection's builder and package validator.
sys.path.insert(0, str(ROOT / "scripts"))
from package import build, metadata

SPEC = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseArchives(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source with spaces"
        self.root.mkdir()
        shutil.copytree(ROOT / "skills", self.root / "skills",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("manifest.json", "LICENSE"):
            shutil.copyfile(ROOT / name, self.root / name)
        self.manifest = json.loads((self.root / "manifest.json").read_text())
        self.output = self.base / "release with spaces"

    def test_each_zip_is_complete_installable_and_checksummed(self):
        release.build_release(self.root, self.output)
        expected_archives = {
            f"{skill['name']}-v{self.manifest['version']}.zip"
            for skill in self.manifest["skills"]
        }
        self.assertEqual({p.name for p in self.output.iterdir()},
                         expected_archives | {"SHA256SUMS"})
        checksums = {}
        for line in (self.output / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split("  ", 1)
            checksums[name] = digest
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), digest)
        self.assertEqual(set(checksums), expected_archives)
        for skill in self.manifest["skills"]:
            name = skill["name"]
            with self.subTest(skill=name):
                path = self.output / f"{name}-v{self.manifest['version']}.zip"
                with zipfile.ZipFile(path) as bundle:
                    self.assertIsNone(bundle.testzip())
                    expected = {Path(f["path"]).relative_to("skills").as_posix(): f
                                for f in skill["files"]}
                    entries = bundle.infolist()
                    self.assertEqual(len(entries), len(expected) + 1)
                    self.assertEqual(set(bundle.namelist()), set(expected) | {f"{name}/LICENSE.collection"})
                    for entry in entries:
                        relative = PurePosixPath(entry.filename)
                        self.assertFalse(relative.is_absolute())
                        self.assertNotIn("..", relative.parts)
                        self.assertEqual(relative.parts[0], name)
                        self.assertTrue(stat.S_ISREG(entry.external_attr >> 16))
                        self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                        if entry.filename in expected:
                            source = self.root / expected[entry.filename]["path"]
                            self.assertEqual(bundle.read(entry), source.read_bytes())
                            mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
                            self.assertEqual(stat.S_IMODE(entry.external_attr >> 16), mode)
                    self.assertEqual(bundle.read(f"{name}/LICENSE.collection"),
                                     (self.root / "LICENSE").read_bytes())
                    # Simulate installing this ZIP alone, without the source
                    # repository, collection manifest, or other skills.
                    target = self.base / "installed" / name / ".agents/skills"
                    bundle.extractall(target)
                    self.assertEqual({p.name for p in target.iterdir()}, {name})
                    self.assertEqual((target / name / "SKILL.md").read_bytes(),
                                     (self.root / skill["entry"]).read_bytes())
                    metadata(target / name / "SKILL.md", name)
                    for record in skill["files"]:
                        relative = Path(record["path"]).relative_to("skills")
                        self.assertEqual(hashlib.sha256((target / relative).read_bytes()).hexdigest(),
                                         record["sha256"])

    def test_reproducible_despite_source_mtimes(self):
        release.build_release(self.root, self.output)
        for path in (self.root / "skills").rglob("*"):
            if path.is_file():
                os.utime(path, (1700000000, 1700000000))
        other = self.base / "second"
        release.build_release(self.root, other)
        for path in self.output.iterdir():
            self.assertEqual(path.read_bytes(), (other / path.name).read_bytes())

    def test_invalid_inputs_do_not_publish_partial_release(self):
        entry = self.root / self.manifest["skills"][0]["entry"]
        entry.write_bytes(entry.read_bytes() + b"\\nchanged")
        with self.assertRaises(ValueError):
            release.build_release(self.root, self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.base.glob(".release-*")))

    def test_symlinks_are_rejected(self):
        entry = self.root / self.manifest["skills"][0]["entry"]
        original = self.base / "original.md"
        entry.rename(original)
        entry.symlink_to(original)
        with self.assertRaises(ValueError):
            release.build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("keep")
        with self.assertRaises(ValueError):
            release.build_release(self.root, self.output)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_missing_license_is_rejected(self):
        (self.root / "LICENSE").unlink()
        with self.assertRaises(ValueError):
            release.build_release(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_output_inside_skill_tree_is_rejected(self):
        output = self.root / "skills" / "dist"
        with self.assertRaises(ValueError):
            release.build_release(self.root, output)
        self.assertFalse(output.exists())

    def test_late_failure_cleans_staging_and_publishes_nothing(self):
        name = self.manifest["skills"][-1]["name"]
        (self.root / "skills" / name / "LICENSE.collection").write_text("collision")
        manifest = build(self.root, self.manifest["version"])
        (self.root / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "reserved"):
            release.build_release(self.root, self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.base.glob(".release-*")))

    def test_cli_builds_default_dist_from_current_directory(self):
        # Run the real public command outside the checkout, with spaces.
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_release.py")],
            cwd=self.base, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.base / "dist/SHA256SUMS").is_file())


if __name__ == "__main__":
    unittest.main()
