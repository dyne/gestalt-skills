# Gestalt skills

Optional, maintained agent skills from Dyne.org. Original content is MIT licensed.
Adapted material retains the licenses identified in each skill's notices.
This is an independent collection, separate from the `gestalt-agents`
infrastructure plugin and its third-party `--extra-skills` bundle.

The canonical tree is `skills/<name>/`; collection version `0.8.0` contains:

- `academic`: Scholarly arguments, section structure, literature synthesis,
  claim–evidence alignment, citations, and research limitations.

- `c-cpp`: C/C++ implementation, CMake/Meson/Make builds, GDB debugging,
  static analysis, sanitizers and LLVM tooling. A short shared workflow loads
  focused references only for the task at hand.
- `dear-imgui`: Testable panels, styling, Dear ImGui interaction, version-aware
  backend/font/texture integration, extension selection and UI automation, with
  optional read-only helpers and headless input-injection/Test Engine examples.
- `golang`: Go implementation, design, errors/resources, concurrency, secure
  I/O, testing, performance and module/toolchain workflows. Adapted guidance
  retains its upstream MIT notice inside the skill.
- `humanizer`: Drafting and editing clear English or Italian prose, with
  reader-oriented composition, grammar, idiom, voice, and semantic fidelity.
  An optional Unicode hygiene helper preserves its upstream MIT attribution.
- `latex`: Mathematical paper exposition, TeX formatting, venue conversion,
  build repair, PDF reconstruction, and rendered checks. An optional standalone
  build checker is included; MIT and CC BY 4.0 adaptations retain their notices.
- `nuklear-gui`: Nuklear C/C++ graphical interfaces and SDL2 integration.
- `svelte`: Svelte components and reactive modules, with focused guidance for
  reactivity, templates/DOM integration, SSR/async and documentation/validation.
- `vite`: Vite configuration, assets/env, plugins, builds, SSR and migrations,
  with optional VitePress guidance for content, themes and custom front pages
  sharing a VitePress build or deployed alongside a separate Vite app. Adapted
  guidance retains its upstream MIT notice inside the skill.

Skills supply instructions, not compilers, libraries, fonts or application
assets. Optional Python helpers use only the standard library; the LaTeX build
helper additionally needs the project's selected TeX engine/backend on `PATH`.
No runtime downloads or third-party Python dependencies are required.

The writing skills have separate responsibilities: `academic` owns research
argument and evidence, `humanizer` owns English/Italian prose quality, and
`latex` owns mathematical exposition and TeX source/rendering. Each works on its
own; a mixed task can use the relevant skills without a chain of prerequisites.
Entrypoints route to focused references instead of loading every source guide.
See [writing-skill maintenance and evaluation](tests/writing-skills.md).

## Installation and activation

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
```

After editing skill files, update the release version intentionally and generate
the deterministic manifest (same inputs produce identical bytes):

```sh
python3 scripts/package.py generate --version 0.8.0
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
