#!/usr/bin/env python3
"""Development-only clean distribution discovery check; may fetch skills@1.5.0."""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from package import check

ROOT = Path(__file__).resolve().parents[1]


def main():
    expected = [skill["name"] for skill in check(ROOT)["skills"]]
    with tempfile.TemporaryDirectory(prefix="gestalt-skills-discovery-") as temporary:
        root = Path(temporary)
        distribution = root / "distribution"
        distribution.mkdir()
        for name in ("LICENSE", "README.md", "manifest.json"):
            shutil.copyfile(ROOT / name, distribution / name)
        shutil.copytree(ROOT / "skills", distribution / "skills")
        command = ["npx", "--cache", str(root / "npm-cache"), "--yes", "skills@1.5.0",
                   "add", str(distribution), "--list"]
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
        output = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(f"discovery command exited {result.returncode}: {output[-2000:]}")
        # In the pinned tool's list format, names have four spaces after the
        # vertical bar; descriptions have six. Never infer names from prose.
        names = re.findall(r"^│ {4}(\S+)\s*$", output, flags=re.MULTILINE)
        if sorted(names) != expected:
            raise SystemExit(f"unexpected discovered names: {names!r}; {output[-2000:]}")
        print(f"skills@1.5.0 clean distribution discovery: {sorted(names)!r}; 1 passed, 0 failed")


if __name__ == "__main__":
    main()
