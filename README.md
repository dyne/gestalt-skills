# Gestalt skills

Optional, maintained agent skills from Dyne.org. Original content is MIT licensed.
This is an independent collection, separate from the `gestalt-agents`
infrastructure plugin and its third-party `--extra-skills` bundle.

The canonical tree is `skills/<name>/`. The collection contains:

- `c-cpp`: C/C++ implementation, CMake/Meson/Make builds, GDB debugging,
  static analysis, sanitizers and LLVM tooling. A short shared workflow loads
  focused references only for the task at hand.
- `clay-tui` designs terminal layouts with Clay and libterm. It includes a
  runnable split-pane tree browser, selection and viewport patterns, a PTY
  interaction check, and a tested port of Clay's termbox2 demo documented
  against specific upstream revisions.
- `cpp-xtd` covers modern C++ projects using Gammasoft xtd, from CMake and
  xtd.core to desktop forms, drawing and tunit. Its local source lookup finds
  headers, implementation status, examples and tests for the project's revision.
- `golang`: Go implementation, design, errors/resources, concurrency, secure
  I/O, testing, performance and module/toolchain workflows. Adapted guidance
  retains its upstream MIT notice inside the skill.
- `inno-setup` stamps Windows executables with product metadata and an optional
  icon, builds a normal wizard or silent WinGet installer, and wires a
  `win-installer` target into CI. Executable, setup and manifest generation
  share one product record.
- `modern-imgui` uses Clay for responsive pane layouts and ImKit for widgets
  and themes on Dear ImGui. Includes a working sidebar/editor example and
  headless interaction tests. It replaces the standalone `dear-imgui` skill.
- `nuklear-gui`: Nuklear C/C++ graphical interfaces and SDL2 integration.
- `svelte`: Svelte components and reactive modules, with focused guidance for
  reactivity, templates/DOM integration, SSR/async and documentation/validation.
- `twenty-crm` covers Twenty SDK apps, workspace integrations, live previews,
  isolated tests, core development, Docker Compose and bare-metal Linux hosting.
- `vite`: Vite configuration, assets/env, plugins, builds, SSR and migrations,
  with optional VitePress guidance for content, themes and custom front pages
  sharing a VitePress build or deployed alongside a separate Vite app. Adapted
  guidance retains its upstream MIT notice inside the skill.

Skills supply instructions, not compilers, libraries, fonts or application
assets. No runtime downloads or Python dependencies are required.

## Installation and activation

### Standalone ZIPs for ChatGPT and Codex

Download `<skill>-v<version>.zip` from
[GitHub releases](https://github.com/dyne/gestalt-skills/releases). Each skill
is published separately using the collection version. Each ZIP
contains one unversioned `<skill>/` directory with `SKILL.md`, all its resources
and upstream notices, and the root license as `LICENSE.collection`.

Use the ZIP with ChatGPT's standalone skill import where available. For local
Codex installation, extract it into `~/.agents/skills` or a project's
`.agents/skills`, producing `<skills-directory>/<skill>/SKILL.md`. See the
[OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) for
supported clients and discovery. Review an existing skill directory before
replacing it. If Gestalt already manages the same skill, use that installation
instead of adding a duplicate.

Release assets include `SHA256SUMS`; download it beside the ZIPs to verify their
digests. With all ZIPs present, run `sha256sum -c SHA256SUMS`. Tools and libraries
used by a skill remain external prerequisites.

### Gestalt-managed collection

The planned Gestalt integration installs this collection during `gestalt install`
and `gestalt update`; targeted maintenance uses `gestalt skills install`,
`gestalt skills update`, and `gestalt skills status` once that integration ships.
The intended upstream is `https://github.com/dyne/gestalt-skills`; publication
and those CLI commands must be available before using them.

The managed location is `$CODEX_HOME/gestalt-skills` (default
`~/.codex-gestalt/gestalt-skills`), with discovery links from
`$CODEX_HOME/skills/<name>` to this repository's `skills/<name>` directories.
Maintain one canonical copy. Do not overwrite existing user skills or `.system`,
or install a second copy under `~/.agents/skills`.

Select skills in the existing skill-profile dialog. Installation makes them
available for normal triggering; it does not load them on every task. Saved
complete selections continue to govern activation, including newly installed
skills absent from the selection. Updates preserve profile choices.

The planned “Gestalt verified” badge describes maintained collection provenance
and current file integrity. Only the installer/catalog can establish that from
the canonical source, resolved revision, manifest digest, and installed files.
The manifest and skill metadata cannot grant that badge themselves. Local edits
or noncanonical sources remain usable ordinary skills without the badge.
Checksums do not protect against someone able to replace both files and receipts.

## Package contract, version 1

`manifest.json` is UTF-8 JSON with these exact fields:

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Integer `1`; reject unsupported formats. |
| `repository` | Repository identity `dyne/gestalt-skills`. |
| `source` | Canonical URL `https://github.com/dyne/gestalt-skills`. |
| `version` | Release version in `MAJOR.MINOR.PATCH` form. |
| `skills` | Sorted records with `name`, `entry`, and `files`. |
| `skills[].name` | Ordinary lowercase hyphenated folder name, never `gestalt:`. |
| `skills[].entry` | Repository-relative `skills/<name>/SKILL.md`. |
| `skills[].files` | Sorted `{ "path": ..., "sha256": ... }` records for every file beneath that skill, including references and agent metadata if added. |

Paths use canonical forward slashes, are relative to the repository, and stay
within the owning skill. No symlinks, traversal, duplicate JSON keys, duplicate
skills/paths, missing files, extra files, or mismatched digests are accepted.
No root documentation or validator is installed as skill content; the manifest
does not hash itself. Installers must validate before promotion and independently
record actual source URL, immutable revision and manifest SHA-256 outside the
discovery tree. Treat downloaded code as untrusted: implement these checks in
the installer rather than executing this repository's validator during install.

## Maintenance

Python 3.10+ suffices for local package checks:

```sh
python3 scripts/package.py check
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output dist
```

The builder requires a new output directory and a valid manifest. It includes
exactly the manifest files for each skill plus `LICENSE.collection`, preserves
executable modes, and fixes timestamps and file order for reproducible ZIPs.
Archive tests verify delivered bytes, paths, checksums, licenses, and extraction
of each skill independently of the collection.

After editing skill files, update the release version intentionally and generate
the deterministic manifest (same inputs produce identical bytes):

```sh
python3 scripts/package.py generate --version VERSION
python3 scripts/package.py check
```

Run the available Codex `skill-creator/scripts/quick_validate.py` against each
`skills/<name>` directory, then run `python3 scripts/discovery.py`. It copies the
distribution to an empty temporary tree and runs
`npx --cache <temporary-cache> --yes skills@1.5.0 add <absolute-copy-path> --list`.
This development check may fetch its pinned discovery tool; installed skills do
not fetch anything. It strips terminal control codes and asserts that every
manifest skill is discovered exactly once, with no extra names. Inspect all
local links and release changes before committing.
Publish only after an immutable upstream revision is retrievable. Preserve any
separate upstream license if imported material is introduced later.

## Releases

Push conventional commits to `main`, or dispatch the release workflow on `main`.
With no semantic release tag yet, the first release uses the committed manifest
version. Later releases use `ietf-tools/semver-action`: `feat` bumps the
minor version; `fix`, `perf`, `refactor`, and `test` bump the patch version;
`BREAKING CHANGE` bumps the major version. Commits without a version bump run
validation without publishing a new release.

Before merging a release-worthy change, regenerate and commit the manifest
with the version selected by the bump. The workflow checks that this committed
version matches the planned tag, runs the Python suite, and publishes the
standalone ZIPs and `SHA256SUMS` from that same commit.
