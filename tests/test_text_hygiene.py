"""Adapted from Enrico Frumento's Humanizer package under its MIT terms.

See skills/humanizer/LICENSE.upstream. Only the script location is changed.
"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).parents[1] / "skills/humanizer/scripts/text_hygiene.py"
spec = importlib.util.spec_from_file_location("text_hygiene", SCRIPT)
text_hygiene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(text_hygiene)


class SanitizerTests(unittest.TestCase):
    def test_default_scan_preserves_candidates_and_reports_uncertainty(self):
        text = "zero\u200b word\u2060 bom\ufeff soft\u00ad tag\U000e0020"
        cleaned, report = text_hygiene.sanitize(text)
        self.assertEqual(cleaned, text)
        self.assertEqual(report["mode"], "scan")
        self.assertFalse(report["changed"])
        self.assertEqual({item["action"] for item in report["findings"]}, {"uncertain"})

    def test_remove_safe_removes_plain_candidates_but_preserves_protected_text(self):
        text = 'plain\u200b\n"quoted\u200b"\n    code\u200b\n| table\u200b |'
        cleaned, report = text_hygiene.sanitize(text, "remove-safe")
        self.assertTrue(cleaned.startswith("plain\n"))
        self.assertIn('"quoted\u200b"', cleaned)
        self.assertIn("code\u200b", cleaned)
        self.assertIn("table\u200b", cleaned)
        self.assertIn("removed", {item["action"] for item in report["findings"]})
        self.assertIn("preserved", {item["action"] for item in report["findings"]})

    def test_preserves_bidi_shaping_spacing_and_emoji(self):
        text = "a\u202eb\u202c\u00a0x\u200c\u200d❤️ e\u0301"
        cleaned, report = text_hygiene.sanitize(text, "remove-safe")
        self.assertEqual(cleaned, text)
        classes = {item["class"] for item in report["findings"]}
        self.assertTrue({"bidi-control", "typographic-spacing", "contextual-shaping", "variation-selector", "combining-mark"} <= classes)

    def test_preserves_subdivision_flag_tags_but_removes_standalone_tag(self):
        england = "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"
        standalone = "\U000e0020"
        cleaned, report = text_hygiene.sanitize(england + standalone, "remove-safe")
        self.assertEqual(cleaned, england)
        england_findings = report["findings"][:6]
        self.assertEqual({item["action"] for item in england_findings}, {"preserved"})
        self.assertEqual(report["findings"][-1]["codepoint"], "U+E0020")
        self.assertEqual(report["findings"][-1]["action"], "removed")

    def test_nfc_is_opt_in_and_not_applied_to_rtl_text(self):
        decomposed = "cafe\u0301"
        self.assertEqual(text_hygiene.sanitize(decomposed)[0], decomposed)
        self.assertEqual(text_hygiene.sanitize(decomposed, normalize=True)[0], "café")
        rtl = "مرحبا e\u0301"
        self.assertEqual(text_hygiene.sanitize(rtl, normalize=True)[0], rtl)
        self.assertEqual(text_hygiene.sanitize("مرحبا\u200b", "remove-safe")[0], "مرحبا\u200b")

    def test_invalid_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            text_hygiene.sanitize("text", "remove-everything")


class CliTests(unittest.TestCase):
    def run_cli(self, text, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=text, text=True, encoding="utf-8", capture_output=True, check=False)

    def test_default_cli_is_streaming_non_destructive_with_utf8_report(self):
        result = self.run_cli("Ciao\u200b 🙂")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Ciao\u200b 🙂")
        report = json.loads(result.stderr)
        self.assertEqual(report["mode"], "scan")
        self.assertEqual(report["findings"][0]["codepoint"], "U+200B")

    def test_cli_modes_empty_input_and_help(self):
        self.assertEqual(self.run_cli("", "--safe").stdout, "")
        self.assertEqual(self.run_cli("A\u200bB", "--remove-safe").stdout, "AB")
        help_result = subprocess.run([sys.executable, str(SCRIPT), "--help"], text=True, capture_output=True, check=False)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--remove-safe", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
