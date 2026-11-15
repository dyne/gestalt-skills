#!/usr/bin/env python3
"""Bounded literal lookup across a selected Dear ImGui source tree.

Prints source locations and context as JSON. Standard library only, no network.
Inspect declarations, implementation and demo together. No generated ABI claims.
"""
import argparse
import json
from pathlib import Path
import sys


def local_glob(directory, pattern):
    """Do not traverse a linked directory outside the selected source tree."""
    return [] if directory.is_symlink() else sorted(directory.glob(pattern))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Literal, case-sensitive text; not a regex")
    parser.add_argument("--imgui-dir", required=True, type=Path)
    parser.add_argument("--context", type=int, default=2)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--area", choices=["public", "demo", "implementation", "docs", "backends", "all"], default="all")
    args = parser.parse_args()
    try:
        root = args.imgui_dir.resolve(strict=True)
        if not (root / "imgui.h").is_file():
            raise ValueError("--imgui-dir must contain imgui.h")
        if not args.query or not 0 <= args.context <= 20 or not 1 <= args.limit <= 500:
            raise ValueError("Use a nonempty query, context 0..20, and limit 1..500")
        areas = {
            "public": [root / "imgui.h", root / "imconfig.h"],
            "demo": [root / "imgui_demo.cpp"],
            "implementation": [root / x for x in ["imgui.cpp", "imgui_widgets.cpp", "imgui_tables.cpp", "imgui_draw.cpp"]],
            "docs": local_glob(root / "docs", "*"),
            "backends": local_glob(root / "backends", "imgui_impl_*"),
        }
        selected = list(areas) if args.area == "all" else [args.area]
        hits = []
        total = 0
        for area in selected:
            for path in areas[area]:
                if not path.is_file() or path.is_symlink() or path.suffix not in {".h", ".cpp", ".mm", ".md", ".txt"}:
                    continue
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                for index, line in enumerate(lines):
                    if args.query not in line:
                        continue
                    total += 1
                    if len(hits) < args.limit:
                        low, high = max(0, index - args.context), min(len(lines), index + args.context + 1)
                        hits.append({"area": area, "file": str(path.relative_to(root)),
                                     "line": index + 1, "context_start_line": low + 1,
                                     "context": lines[low:high]})
        print(json.dumps({"query": args.query, "imgui_dir": str(root), "match_count": total,
                          "returned_count": len(hits), "truncated": total > len(hits), "matches": hits},
                         indent=2, ensure_ascii=False))
        return 0 if total else 1
    except (OSError, ValueError) as exc:
        print(f"lookup_imgui: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
