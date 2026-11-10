#!/usr/bin/env python3
"""Build one deterministic, standalone skill ZIP per manifest entry."""

import argparse
import hashlib
from pathlib import Path
import stat
import sys
import tempfile
import zipfile

from package import ROOT, check, require


def write_entry(bundle, name, payload, executable=False):
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    entry.compress_type = zipfile.ZIP_DEFLATED
    bundle.writestr(entry, payload)


def build_release(root, output):
    """Validate before staging; publish only a complete set to a new directory."""
    root, output = Path(root).resolve(), Path(output).absolute()
    require(not output.exists() and not output.is_symlink(),
            f"output path already exists: {output}")
    require(not output.resolve().is_relative_to(root / "skills"),
            "output must be outside the skills tree")
    manifest = check(root)
    license_path = root / "LICENSE"
    require(license_path.is_file() and not license_path.is_symlink(),
            "LICENSE must be a regular file")
    license_bytes = license_path.read_bytes()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".release-", dir=output.parent) as temporary:
        stage = Path(temporary) / "dist"
        stage.mkdir()
        checksums = []
        for skill in manifest["skills"]:
            name = skill["name"]
            archive = stage / f"{name}-v{manifest['version']}.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                for record in skill["files"]:
                    source = root / record["path"]
                    payload = source.read_bytes()
                    require(hashlib.sha256(payload).hexdigest() == record["sha256"],
                            f"source changed while packaging: {record['path']}")
                    target = Path(record["path"]).relative_to("skills").as_posix()
                    require(target != f"{name}/LICENSE.collection",
                            "LICENSE.collection is reserved for the collection license")
                    write_entry(bundle, target, payload, bool(source.stat().st_mode & 0o111))
                # Keep the collection license beside all original upstream notices.
                write_entry(bundle, f"{name}/LICENSE.collection", license_bytes)
            checksums.append(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n")
        (stage / "SHA256SUMS").write_text("".join(checksums), encoding="utf-8")
        stage.rename(output)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"),
                        help="new output directory (default: dist)")
    args = parser.parse_args()
    try:
        manifest = build_release(ROOT, args.output)
    except (ValueError, OSError, UnicodeError) as error:
        print(f"release: {error}", file=sys.stderr)
        return 1
    print(f"built {len(manifest['skills'])} skill ZIPs and SHA256SUMS "
          f"for v{manifest['version']} in {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
