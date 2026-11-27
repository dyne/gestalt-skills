#!/usr/bin/env python3
"""Locate evidence about a named public API in a local xtd source checkout."""

import argparse
from pathlib import Path
import re


MODULES = ("core", "drawing", "forms", "tunit")
RATINGS = {"0": "Not started", "25": "Started", "50": "In progress",
           "75": "Usable", "100": "Complete", "_ina": "Not applicable"}


def matches(name, query):
    return name == query if "::" in query else name.split("::")[-1] == query


def report_paths(label, paths, limit=5, preferred=()):
    ordered = sorted(set(paths), key=lambda path: (path.name not in preferred, len(path.parts), str(path)))
    for path in ordered[:limit]:
        print(f"  {label}: {path}")
    if len(ordered) > limit:
        print(f"  {len(ordered) - limit} more {label} matches")


def lookup(root, query):
    leaf = query.split("::")[-1]
    found = False
    for module in MODULES:
        component = f"xtd.{module}"
        include = root / "src" / component / "include"
        headers = []
        definitions = set()
        example_names = set()
        for path in sorted(include.rglob(leaf + "*")):
            if path.name not in (leaf, leaf + ".hpp", leaf + ".h") or not path.is_file():
                continue
            parts = path.relative_to(include).with_suffix("").parts
            if "internal" in parts or not matches("::".join(parts), query):
                continue
            headers.append(path.relative_to(root))
            definitions.add(path.relative_to(include).with_suffix(""))
            if path.suffix:
                example_names.update(re.findall(r"@include\s+([\w.-]+\.cpp)\b",
                                                path.read_text(encoding="utf-8", errors="replace")))

        status = root / "docs" / f"development_status_xtd_{module}.md"
        rows = []
        if status.is_file():
            namespace = ""
            for number, line in enumerate(status.read_text(encoding="utf-8").splitlines(), 1):
                if line.startswith("## "):
                    namespace = line[3:].strip()
                entry = re.match(r"\|\s*\[([^\]]+)\]", line)
                rating = re.search(r"pictures/progress(\w+)\.png", line)
                if entry and rating and matches(f"{namespace}::{entry[1]}", query):
                    label = RATINGS.get(rating[1], rating[1])
                    rows.append(f"  status: {namespace}::{entry[1]} — {label} ({status.relative_to(root)}:{number})")

        if not headers and not rows:
            continue
        found = True
        print(component)
        report_paths("header", headers, limit=15)
        source_dir = root / "src" / component / "src"
        for definition in sorted(definitions):
            for suffix in (".cpp", ".mm"):
                source = source_dir / definition.with_suffix(suffix)
                if source.is_file():
                    print(f"  implementation: {source.relative_to(root)}")
        for row in rows:
            print(row)
        if not rows:
            print("  status: unlisted")
        if not headers:
            print("  no matching public header by filename")

        examples = root / "examples" / f"{component}.examples"
        sources = [path for path in examples.rglob("*.cpp") if path.name in example_names
                   or path.stem == leaf or path.stem.startswith(leaf + "_")]
        report_paths("example candidate", [p.relative_to(root) for p in sources],
                     preferred=example_names | {leaf + ".cpp"})
        tests = root / "tests" / f"{component}.unit_tests"
        report_paths("test candidate", [p.relative_to(root) for p in tests.rglob(leaf + "_tests.cpp")])
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("symbol", help="type or header basename, optionally qualified with xtd::")
    args = parser.parse_args()
    if not (args.checkout / "src/xtd.core/include/xtd").is_dir():
        parser.error("expected the root of an xtd source checkout")
    if not re.fullmatch(r"(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*", args.symbol):
        parser.error("use a C++ name such as xtd::io::file")
    if not lookup(args.checkout, args.symbol):
        parser.exit(1, "No matching public header filename or status row. Search declarations for aliases and members.\n")


if __name__ == "__main__":
    main()
