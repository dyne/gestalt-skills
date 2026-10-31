#!/usr/bin/env python3
"""Deterministic collection manifest; no third-party dependencies."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/dyne/gestalt-skills"
REPOSITORY = "dyne/gestalt-skills"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def object_keys(value, expected):
    require(type(value) is dict and set(value) == set(expected),
            f"expected object fields: {', '.join(expected)}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def relative_path(value):
    require(type(value) is str and value and "\\" not in value,
            "path must be a nonempty POSIX string")
    path = PurePosixPath(value)
    require(not path.is_absolute() and path.as_posix() == value
            and all(part not in (".", "..") for part in path.parts),
            f"noncanonical or escaping path: {value}")
    require(not any(ord(char) < 32 or ord(char) == 127 for char in value),
            "control character in path")
    return path


def regular_tree(root):
    """Never follow symlinks, even when they point inside the package."""
    tree = root / "skills"
    require(tree.is_dir() and not tree.is_symlink(), "skills must be a real directory")
    files = []
    for path in sorted(tree.rglob("*")):
        require(not path.is_symlink(), f"symlink prohibited: {path.relative_to(root)}")
        require(path.is_dir() or path.is_file(), f"nonregular file: {path}")
        if path.is_file():
            relative_path(path.relative_to(root).as_posix())
            files.append(path)
    return files


def metadata(entry, name):
    text = entry.read_text(encoding="utf-8")
    lines = text.splitlines()
    require(lines and lines[0] == "---", f"missing frontmatter: {entry}")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"unterminated frontmatter: {entry}") from error
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        require(separator and key in ("name", "description") and key not in fields,
                f"unsupported or duplicate frontmatter field: {line}")
        value = value.strip()
        # The package uses a deliberately small YAML subset: plain names and
        # JSON-quoted strings (also valid YAML). Reject rather than misparse YAML.
        fields[key] = json.loads(value) if value.startswith('"') else value
    require(fields.get("name") == name, f"frontmatter name mismatch: {entry}")
    description = fields.get("description")
    require(type(description) is str and len(description.strip()) >= 20,
            f"missing discovery description: {entry}")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        target = target.split("#", 1)[0]
        relative_path(target)
        linked = entry.parent / target
        require(linked.is_file() and not linked.is_symlink(), f"broken local link: {target}")
        require(linked.resolve().is_relative_to(entry.parent.resolve()),
                f"escaping local link: {target}")


def build(root, version):
    require(type(version) is str and VERSION.fullmatch(version), "invalid release version")
    files = regular_tree(root)
    children = sorted((root / "skills").iterdir())
    require(children, "empty collection")
    records = []
    for directory in children:
        name = directory.name
        require(directory.is_dir() and NAME.fullmatch(name) and len(name) < 64,
                f"invalid skill directory: {name}")
        entry = directory / "SKILL.md"
        require(entry.is_file(), f"missing entry: {entry}")
        metadata(entry, name)
        records.append({"name": name, "entry": entry.relative_to(root).as_posix(),
                        "files": [{"path": path.relative_to(root).as_posix(),
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                  for path in files if path.is_relative_to(directory)]})
    # Check links in every Markdown reference as well as the entrypoint.
    for path in files:
        if path.suffix == ".md" and path.name != "SKILL.md":
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                relative_path(target.split("#", 1)[0])
                linked = path.parent / target.split("#", 1)[0]
                require(linked.is_file() and linked.resolve().is_relative_to(root / "skills"),
                        f"broken or escaping link: {path}: {target}")
    return {"schemaVersion": 1, "repository": REPOSITORY, "source": SOURCE,
            "version": version, "skills": records}


def check(root):
    manifest = root / "manifest.json"
    require(manifest.is_file() and not manifest.is_symlink(), "manifest must be a regular file")
    data = json.loads(manifest.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    object_keys(data, ("schemaVersion", "repository", "source", "version", "skills"))
    require(type(data["schemaVersion"]) is int and data["schemaVersion"] == 1,
            "unsupported schema version")
    require(data["repository"] == REPOSITORY and data["source"] == SOURCE, "source mismatch")
    require(type(data["skills"]) is list and data["skills"], "skills must be a nonempty array")
    names, paths = set(), set()
    for skill in data["skills"]:
        object_keys(skill, ("name", "entry", "files"))
        name = skill["name"]
        require(type(name) is str and NAME.fullmatch(name) and len(name) < 64,
                "invalid skill name")
        require(name not in names, f"duplicate skill: {name}")
        names.add(name)
        require(skill["entry"] == f"skills/{name}/SKILL.md", "invalid skill entry")
        require(type(skill["files"]) is list and skill["files"], "files must be a nonempty array")
        for file in skill["files"]:
            object_keys(file, ("path", "sha256"))
            path = relative_path(file["path"])
            require(path.parts[:2] == ("skills", name) and len(path.parts) >= 3,
                    "file outside owning skill")
            require(file["path"] not in paths, f"duplicate path: {file['path']}")
            paths.add(file["path"])
            require(type(file["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", file["sha256"]),
                    "invalid SHA-256")
    expected = build(root, data["version"])
    require(data == expected, "manifest differs from canonical tree (coverage, order, metadata or digest)")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "check"))
    parser.add_argument("--version", help="explicit release version for generation")
    args = parser.parse_args()
    try:
        if args.command == "generate":
            require(args.version is not None, "generation requires --version")
            data = build(ROOT, args.version)
            require(not (ROOT / "manifest.json").is_symlink(), "symlink manifest prohibited")
            (ROOT / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        else:
            require(args.version is None, "--version applies only to generation")
            data = check(ROOT)
        print(f"{args.command}: {len(data['skills'])} skills, "
              f"{sum(len(s['files']) for s in data['skills'])} files, version {data['version']}")
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(f"package: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
