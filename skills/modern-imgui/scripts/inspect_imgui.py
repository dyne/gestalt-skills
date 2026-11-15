#!/usr/bin/env python3
"""Read-only Dear ImGui profile and advisory source scan.

Python 3.9+, standard library only. This is a lexical discovery tool, not a C++
parser, control-flow checker, ABI verifier, or substitute for runtime tests.
No network requests, builds, installations, or source modifications are made.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SKIP_DIRS = {".git", ".svn", ".cache", "__pycache__", "node_modules", "build", "out"}
VENDOR_DIRS = {"vendor", "third_party", "third-party", "external", "_deps"}
SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".mm"}
RULES = [
    ("internal_header", r'\binclude\s*[<\"](?:[^\"<>]*/)?imgui_internal\.h[>\"]',
     "review", "Internal API dependency: isolate it and pin/test upgrades."),
    ("legacy_columns", r'\bImGui::Columns\s*\(', "review",
     "Legacy Columns API: prefer Tables for new layouts; existing code may still be valid."),
    ("legacy_key_array", r'\b(?:KeysDown|KeyMap|NavInputs)\s*\[', "review",
     "Historical direct input-array access: inspect event-queue migration and the local header."),
    ("legacy_key_index", r'\bGetKeyIndex\s*\(', "review",
     "Historical key-index API: check named ImGuiKey values and current event APIs."),
    ("font_global_scale", r'\bFontGlobalScale\b', "review",
     "Old font scaling recipe: inspect current FontScaleMain/FontScaleDpi support before changing."),
    ("window_font_scale", r'\bSetWindowFontScale\s*\(', "review",
     "Old per-window scaling API: review current font-size policy and version compatibility."),
    ("old_overlap", r'\bSetItemAllowOverlap\s*\(', "review",
     "Obsolete overlap API: current code uses SetNextItemAllowOverlap before the item."),
    ("fork_layout", r'\bImGui::(?:BeginHorizontal|EndHorizontal|BeginVertical|EndVertical|Spring)\s*\(',
     "review", "Possible StackLayout fork API: verify the selected fork; this is not upstream core."),
    ("dock_builder", r'\bImGui::DockBuilder\w*\s*\(', "review",
     "DockBuilder is an internal API: isolate, pin, and avoid rebuilding user layouts every frame."),
    ("framebuffer_typo", r'\bDisplayFrameBufferSize\b', "review",
     "This is not the v1.93 public IO field; inspect DisplaySize and DisplayFramebufferScale."),
    ("old_draw_flags", r'\b(?:ImDrawListFlags_AntiAliased\w*|ImDrawFlags_RoundCorners\w*)\b',
     "review", "Older draw-flag names: consult 1.93 migration notes if upgrading."),
    ("old_tessellation", r'\bCurveTessellationTol\b', "review",
     "Old squared-unit tolerance: 1.93 uses CurveTessellationMaxError in pixel units."),
    ("backend_capabilities", r'\bBackendFlags\s*[|=]', "info",
     "Capability flags must describe implemented backend support, not enable unimplemented features."),
    ("draw_data_lifetime", r'\bGetDrawData\s*\(', "info",
     "If output crosses a frame/thread boundary, inspect snapshots, texture requests and ownership."),
    ("font_memory", r'\bFontDataOwnedByAtlas\s*=\s*false', "review",
     "Caller-owned font bytes must remain available for the font lifetime under dynamic baking."),
]
FEATURES = ["IMGUI_HAS_DOCK", "IMGUI_HAS_VIEWPORT", "IMGUI_HAS_TABLE", "IMGUI_HAS_TEXTURES"]


def git_value(root, *args):
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                text=True, timeout=5, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def mask_cpp(text, mask_literals=False):
    """Mask comments, optionally literals, without changing source offsets.

    Recognize raw strings and escaped line endings in // comments. The
    character-literal guard keeps C++ digit separators from swallowing later
    comments. This remains a lexical aid, not a preprocessor or C++ parser.
    """
    token = re.compile(
        r'R"([^\s()\\]{0,16})\(.*?\)\1"|"(?:\\.|[^"\\\n])*"|'
        r"(?<![\w])(?:u8|u|U|L)?'(?:\\.|[^'\\\n])*'|"
        r'//(?:\\\r?\n|[^\n])*|/\*.*?(?:\*/|\Z)', re.S)
    return token.sub(lambda m: re.sub(r'[^\n]', ' ', m.group())
                     if mask_literals or m.group().startswith(("//", "/*"))
                     else m.group(), text)


def remove_comments(text):
    """Keep literals and newlines while masking lexical comments."""
    return mask_cpp(text)


def profile(root):
    header = root / "imgui.h"
    if not header.is_file():
        raise ValueError("--imgui-dir must contain imgui.h")
    text = remove_comments(header.read_text(encoding="utf-8", errors="replace"))
    directives = mask_cpp(text, mask_literals=True)

    def define_value(name):
        match = re.search(r'^[ \t]*#[ \t]*define[ \t]+' + re.escape(name) + r'\b',
                          directives, re.M)
        if match is None:
            return None
        # Literal masking prevents a raw-string example from impersonating a
        # directive; read its value from the same offsets in the original text.
        return text[match.end():].split('\n', 1)[0].strip()

    version_value = define_value("IMGUI_VERSION")
    number_value = define_value("IMGUI_VERSION_NUM")
    version = re.match(r'"([^"\n]+)"', version_value or "")
    number = re.match(r'\d+', number_value or "")
    core = {}
    for name in ["imgui.h", "imgui.cpp", "imgui_draw.cpp", "imgui_tables.cpp",
                 "imgui_widgets.cpp", "imgui_demo.cpp", "imconfig.h"]:
        path = root / name
        if path.is_file():
            data = path.read_bytes()
            first = data.decode("utf-8", errors="replace").splitlines()[:3]
            core[name] = {"sha256": hashlib.sha256(data).hexdigest(), "opening_lines": first}
        else:
            core[name] = {"missing": True}
    # A checkout may be vendored inside another repository. The enclosing Git
    # revision is reported explicitly and is not claimed to be the upstream SHA.
    return {
        "imgui_dir": str(root), "version": version.group(1) if version else None,
        "version_num": int(number.group()) if number else None,
        "feature_macros": {x: define_value(x) is not None for x in FEATURES},
        "enclosing_git_root": git_value(root, "rev-parse", "--show-toplevel"),
        "enclosing_git_head": git_value(root, "rev-parse", "HEAD"),
        "enclosing_git_branch": git_value(root, "symbolic-ref", "--short", "HEAD"),
        "core_files": core,
        "backend_files": sorted(p.name for p in (root / "backends").glob("imgui_impl_*.h")),
    }


def source_paths(root, imgui_root, include_vendor, max_files):
    count = 0
    skipped = []
    paths = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        here = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and (include_vendor or d not in VENDOR_DIRS)
                         and not (here / d).is_symlink()
                         and (here / d).resolve() != imgui_root)
        if here.resolve() == imgui_root:
            dirs[:] = []
            continue
        for name in sorted(names):
            path = here / name
            if path.suffix.lower() not in SUFFIXES or path.is_symlink():
                continue
            if count >= max_files:
                raise ValueError("File limit reached; narrow --project-dir or increase --max-files")
            count += 1
            if path.stat().st_size > 3 * 1024 * 1024:
                skipped.append({"file": str(path.relative_to(root)), "reason": "larger than 3 MiB"})
            else:
                paths.append(path)
    return paths, skipped


def scan(root, imgui_root, include_vendor, max_files):
    findings = []
    paths, skipped = source_paths(root, imgui_root, include_vendor, max_files)
    for path in paths:
        text = remove_comments(path.read_text(encoding="utf-8", errors="replace"))
        for code, expression, severity, message in RULES:
            for match in re.finditer(expression, text):
                findings.append({"code": code, "severity": severity,
                                 "file": str(path.relative_to(root)),
                                 "line": text.count("\n", 0, match.start()) + 1,
                                 "message": message})
    return {"files_scanned": len(paths), "files_skipped": skipped, "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imgui-dir", required=True, type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--include-vendor", action="store_true")
    parser.add_argument("--max-files", type=int, default=10000)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    try:
        if args.max_files < 1:
            raise ValueError("--max-files must be positive")
        imgui_root = args.imgui_dir.resolve(strict=True)
        result = {"schema_version": 1, "profile": profile(imgui_root),
                  "limitations": ["Advisory lexical findings are not proven bugs.",
                                   "Comments are ignored; string-literal examples can still match.",
                                   "Conditional compilation, macros, pairing and runtime behavior are not analyzed.",
                                   "A Git revision may belong to an enclosing application repository."]}
        if args.project_dir:
            root = args.project_dir.resolve(strict=True)
            if not root.is_dir():
                raise ValueError("--project-dir must be a directory")
            result["scan"] = scan(root, imgui_root, args.include_vendor, args.max_files)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            p = result["profile"]
            print(f"Dear ImGui {p['version']} ({p['version_num']})")
            print("Features:", ", ".join(k for k, v in p["feature_macros"].items() if v))
            for f in result.get("scan", {}).get("findings", []):
                print(f"{f['file']}:{f['line']}: {f['severity']} [{f['code']}] {f['message']}")
            print("Advisory scan only; no finding or absence of findings proves correctness.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"inspect_imgui: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
