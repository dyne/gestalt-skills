"""Mutate a distributable copy to exercise the package trust boundary."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("package", Path(__file__).resolve().parents[1] / "scripts/package.py")
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackageContract(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(package.ROOT / "skills", self.root / "skills")
        shutil.copyfile(package.ROOT / "manifest.json", self.root / "manifest.json")
        self.original = json.loads((self.root / "manifest.json").read_text())

    def write(self, data):
        (self.root / "manifest.json").write_text(json.dumps(data))

    def reject(self, data=None):
        if data is not None:
            self.write(data)
        with self.assertRaises((ValueError, OSError)):
            package.check(self.root)

    def test_valid_distribution_and_reproducible_generation(self):
        version = self.original["version"]
        self.assertEqual(package.check(self.root), self.original)
        self.assertEqual(package.build(self.root, version), self.original)
        self.assertEqual(package.build(self.root, version), package.build(self.root, version))

    def test_drift(self):
        with (self.root / "skills/nuklear-gui/SKILL.md").open("a") as file:
            file.write("\nChanged instructions.\n")
        self.reject()

    def test_missing_file(self):
        (self.root / "skills/nuklear-gui/references/integration.md").unlink()
        self.reject()

    def test_extra_unlisted_file(self):
        (self.root / "skills/nuklear-gui/extra.txt").write_text("unlisted")
        self.reject()

    def test_duplicate_paths(self):
        data = copy.deepcopy(self.original)
        data["skills"][0]["files"].append(data["skills"][0]["files"][0])
        self.reject(data)

    def test_duplicate_skills(self):
        data = copy.deepcopy(self.original)
        data["skills"].append(data["skills"][0])
        self.reject(data)

    def test_malformed_json_and_duplicate_keys(self):
        for text in ("{", '{"schemaVersion":1,"schemaVersion":1}', "null", "[]"):
            with self.subTest(text=text):
                (self.root / "manifest.json").write_text(text)
                self.reject()

    def test_invalid_schema(self):
        for key, value in (("schemaVersion", True), ("schemaVersion", 2),
                           ("source", "https://example.org/fork"), ("repository", "other/skills"),
                           ("version", "01.0.0"), ("skills", None)):
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(self.original)
                data[key] = value
                self.reject(data)
        data = copy.deepcopy(self.original)
        data["unknown"] = 1
        self.reject(data)

    def test_escaping_and_noncanonical_paths(self):
        for path in ("../outside", "/etc/passwd", "skills/nuklear-gui/../outside",
                     "skills//nuklear-gui/SKILL.md", "./skills/nuklear-gui/SKILL.md",
                     "skills\\nuklear-gui\\SKILL.md", "skills/other/SKILL.md",
                     "skills/nuklear-gui/line\nbreak", None):
            with self.subTest(path=path):
                data = copy.deepcopy(self.original)
                data["skills"][0]["files"][0]["path"] = path
                self.reject(data)

    def test_entry_must_belong_to_named_skill(self):
        data = copy.deepcopy(self.original)
        data["skills"][0]["entry"] = "../SKILL.md"
        self.reject(data)

    def test_invalid_name(self):
        for name in ("gestalt:nuklear-gui", "Nuklear", "../escape", None):
            with self.subTest(name=name):
                data = copy.deepcopy(self.original)
                data["skills"][0]["name"] = name
                self.reject(data)

    def test_invalid_digest(self):
        for digest in ("0" * 64, "A" * 64, None):
            with self.subTest(digest=digest):
                data = copy.deepcopy(self.original)
                data["skills"][0]["files"][0]["sha256"] = digest
                self.reject(data)

    def test_file_symlink_inside_and_outside(self):
        linked = self.root / "skills/nuklear-gui/linked.md"
        for target in (self.root / "skills/nuklear-gui/SKILL.md", self.root / "manifest.json"):
            with self.subTest(target=target):
                linked.symlink_to(target)
                self.reject()
                with self.assertRaises(ValueError):
                    package.build(self.root, "0.1.0")
                linked.unlink()

    def test_directory_symlink(self):
        (self.root / "skills/nuklear-gui/nested").symlink_to(self.root, target_is_directory=True)
        self.reject()

    def test_skill_root_symlink(self):
        (self.root / "skills").rename(self.root / "actual")
        (self.root / "skills").symlink_to(self.root / "actual", target_is_directory=True)
        self.reject()

    def test_manifest_symlink(self):
        (self.root / "manifest.json").rename(self.root / "actual.json")
        (self.root / "manifest.json").symlink_to(self.root / "actual.json")
        self.reject()

    def test_metadata_mismatch_and_broken_reference(self):
        entry = self.root / "skills/nuklear-gui/SKILL.md"
        text = entry.read_text()
        entry.write_text(text.replace("name: nuklear-gui", "name: other"))
        with self.assertRaises(ValueError):
            package.build(self.root, "0.1.0")
        entry.write_text(text + "\n[Missing](references/missing.md)\n")
        with self.assertRaises(ValueError):
            package.build(self.root, "0.1.0")


if __name__ == "__main__":
    unittest.main()
