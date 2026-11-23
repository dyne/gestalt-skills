"""Exercise the adopted packaging helpers with a different publisher."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ASSETS = Path(__file__).resolve().parents[1] / "skills/inno-setup/assets"


class ProductMetadata(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="Windows release ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.product = self.root / "product.json"
        self.metadata = json.loads((ASSETS / "product.json").read_text())
        self.metadata.update(name="Métronome", publisher='Studio "Or" & Co',
                             license="BSD-2-Clause", licenseFile="LICENSE.txt")
        self.product.write_text(json.dumps(self.metadata))
        (self.root / "LICENSE.txt").write_text("License fixture")

    def generate(self, kind, *extra, check=True):
        output = self.root / kind
        result = subprocess.run(
            [sys.executable, "-B", ASSETS / "product_metadata.py", kind,
             "--product", self.product, "--version", "2.4.7-beta.2", "--output", output, *extra],
            check=check, capture_output=True, text=True)
        return output if check else result

    def test_one_record_supplies_three_release_formats(self):
        rc = self.generate("rc").read_text()
        self.assertIn('VALUE "CompanyName", L"Studio ""Or"" & Co"', rc)
        self.assertIn("FILEVERSION 2,4,7,0", rc)
        self.assertIn('VALUE "ProductVersion", L"2.4.7-beta.2"', rc)
        self.assertIn('VALUE "ProductName", L"Métronome"', rc)
        inc = self.generate("inno").read_text(encoding="utf-8-sig")
        self.assertIn('ProductPublisher "Studio ""Or"" & Co"', inc)
        self.assertIn((self.root / "LICENSE.txt").as_posix(), inc)
        self.assertNotIn("ProductIcon", inc)
        self.assertNotIn(" ICON ", rc)
        installer = self.root / "installer fixture.exe"
        installer.write_bytes(b"installer fixture")
        folder = subprocess.check_output([
            sys.executable, "-B", ASSETS / "render-winget.py", "--product", self.product,
            "--templates", ASSETS / "winget", "--version", "2.4.7-beta.2", "--installer",
            installer, "--url", "https://example.org/releases/2.4.7-beta.2/setup.exe",
            "--output", self.root / "manifests"], text=True).strip()
        locale = (Path(folder) / "Example.Dial.locale.en-US.yaml").read_text()
        for field, key in (("Publisher", "publisher"), ("PackageName", "name"),
                           ("PackageUrl", "homepage"), ("License", "license")):
            self.assertIn(f"{field}: {json.dumps(self.metadata[key])}", locale)

    def test_companion_version_override_and_failed_rebuild(self):
        resource = self.generate("rc", "--exe", "helper.exe", "--file-version", "2.4.7.19")
        original = resource.read_bytes()
        self.assertIn(b'VALUE "OriginalFilename", L"helper.exe"', original)
        self.assertIn(b"FILEVERSION 2,4,7,19", original)
        self.assertNotEqual(self.generate("rc", "--file-version", "65536", check=False).returncode, 0)
        self.assertEqual(resource.read_bytes(), original)
        self.metadata["iconFile"] = "missing.ico"
        self.product.write_text(json.dumps(self.metadata))
        self.assertNotEqual(self.generate("rc", check=False).returncode, 0)
        self.assertEqual(resource.read_bytes(), original)
