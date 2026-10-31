# Sources, baseline and optional tools

Checked 2026-10-31 against core v1.93.0, commit
`c1aaac65e896a45f81f47a4d68f9959e0f86c859`. The matching docking tag
v1.93.0-docking resolves to `b916186e66aa3c02b72c6ca17455516512ed8049`.
These are reproducible research baselines, not a permanent latest-version claim.

## Inspect the actual dependency

Find the copy used by the application's include paths and build, not merely a
nearby checkout. Record `IMGUI_VERSION`, `IMGUI_VERSION_NUM`, pin/patches,
`imconfig.h` or user configuration, backend pair and implemented capabilities.
Check matching `ImTextureID`, `ImDrawIdx`, `IMGUI_USE_WCHAR32`, test hooks and
obsolete-function policy across core/backends/bindings/extensions.
`IMGUI_CHECKVERSION()` helps detect selected layout/version mismatches; it is
not a complete ABI or compatibility proof. A source file's presence does not
prove that it is compiled, initialized or enabled.

Use this precedence when evidence disagrees:

1. Actual local headers, implementation, configuration and dependency pins.
2. Matching upstream `imgui.h` comments, `imgui_demo.cpp`, examples and backend
   implementations; inspect the declaration **and** its relevant usage.
3. API-breaking changes and changelog for the version transition.
4. Focused official docs/wiki and maintainer issue resolutions, with dates.
5. Extension-owned documentation for its own API; third-party examples as ideas
   to verify. An extension directory listing is not compatibility certification.

Use [sources.json](sources.json) for the supplied 156-URL evidence inventory
and [extensions.json](extensions.json) for 18 dated project snapshots. Load only
the relevant records. Do not treat development branches, unmerged proposals or
fork APIs as upstream public declarations. Recheck version-sensitive guidance
when a pin, backend/platform or observed behavior changes.

## Optional read-only helpers

Python 3.9+ and its standard library suffice. From the skill directory:

```sh
python3 scripts/inspect_imgui.py --imgui-dir /path/to/imgui --project-dir /path/to/app
python3 scripts/lookup_imgui.py BeginTable --imgui-dir /path/to/imgui --area public --limit 8
```

The inspector reports header macros, core hashes, available backend filenames,
enclosing Git identity and optional lexical findings. Its Git HEAD may belong
to a parent application repository; header feature macros are not preprocessed
configuration or enabled runtime features. Comments are masked, but string
examples and inactive conditional code can still produce findings. It does not
prove ID stability, stack balance, ABI compatibility or correct input/rendering.
The project scan skips build/vendor trees by default, caps files and skips
files over 3 MiB; narrow scope rather than treating incomplete coverage as clean.

Lookup is case-sensitive literal search with bounded returned matches/context,
counts and a truncation flag. Exit codes: 0 matches, 1 no matches, 2 invalid
input/read error; inspector uses 0/2. No match is not proof an API is absent
until the actual dependency/include path and relevant source are checked.
Neither helper edits files, installs tools, downloads dependencies or builds.
Use existing source-navigation tools when they already answer the question.

Primary entry points: [header](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[demo](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp),
[backends](https://github.com/ocornut/imgui/blob/v1.93.0/docs/BACKENDS.md),
[FAQ](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md),
[changes](https://github.com/ocornut/imgui/blob/v1.93.0/docs/CHANGELOG.txt).
