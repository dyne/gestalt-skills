# Build and repair

## Select the build

Prefer the project's configured build command. Inspect its actual root,
engine, output/auxiliary directories, bibliography backend, and generated
assets. `fontspec` requires XeLaTeX or LuaLaTeX. `biblatex` can use different
backends; inspect its options instead of assuming Biber. Do not run a backend
on a project that has no bibliography step.

For a conventional root document, the bundled Python 3.10+ standard-library
helper is standalone. From this skill's directory, with an unused output path:

```sh
python3 scripts/check_build.py /path/to/paper.tex --output /path/to/new-build --until-stable --require-resolved
python3 scripts/check_build.py /path/to/paper.tex --output /path/to/new-bib-build --engine xelatex --backend biber --until-stable --require-resolved --watch-input references.bib
```

Use the actual installed script path when the working directory is elsewhere.
The selected engine/backend must already be on `PATH`. The helper does not
install dependencies, infer configuration, or support every custom build.
Keep the existing build system for generated assets, glossaries, MakeIndex,
split auxiliary directories, or projects requiring shell escape. Do not enable
shell escape as an incidental error repair; follow the actual execution policy.
The helper disables it but is not a sandbox for TeX input.

## Interpret retained evidence

The helper refuses an existing output directory. It records fresh PDF output,
per-step transcripts/native logs in `logs/`, and `build-report.json` (schema 3)
with commands, exits, diagnostics, PDF hash, and observed input fingerprints.
Engine steps run from the root's directory. No source is copied or edited.

- Exit 0: requested processes succeeded, recognized errors are absent, and the
  last engine pass produced a PDF header. Layout warnings can remain.
- Exit 1: attempted build failed, timed out, did not settle with `--until-stable`,
  or failed another requested evidence check. Inspect `failure`, `failed_step`,
  `diagnostic_step`, and complete referenced logs. A partial PDF is not success.
- Exit 2: invalid arguments, missing tools, or an I/O failure prevented completion.

Default passes are two, or engine/backend/two further engine passes with a
backend. `--until-stable` bounds settling to five engine passes by default;
`--passes 1-5` sets the count or maximum. The backend runs once.
`--require-resolved` fails recognized unresolved-reference or rerun messages.
`--timeout` is per process, default 60 seconds. Run `--help` for argument details.

Recorder-listed local inputs are fingerprinted after available engine passes
and at the end. Repeated `--watch-input` paths are relative to the root source's
directory and additionally checked before and after steps; use them for known
local bibliography/style resources. Changed or unreadable observed inputs fail
an otherwise successful build. Missing recorders, unselected backend resources,
external fonts/packages, changes before the first observation, or reverted
changes between observations remain provenance limits. Explicit relative BibTeX
resources may be staged inside output without modifying their originals.
This evidence is not a frozen environment or a content-correctness guarantee.

## Diagnose the first cause

1. Reproduce with the selected build and retain the exit and logs. Read the
   earliest causal diagnostic and source context; later errors may cascade.
   File-line errors can appear as `file.tex:line:` rather than starting with `!`.
2. Inspect macro definitions and package load order before replacing an unknown
   command. Check real argument/environment balance, accounting for comments,
   escapes, and verbatim; global brace/dollar counts are unreliable.
3. Make the smallest semantic-preserving fix. Missing math delimiters, ambiguous
   glyphs, or table cells may require an author decision. Never delete an
   equation, disable a section, or invent a reference just to make TeX pass.
4. Rebuild and distinguish compiler errors, unresolved keys, duplicate labels,
   and layout warnings. For persistent failure, revise the diagnosis rather
   than patching new symptoms. After three attempts without progress, report
   the exact blocker and needed evidence.
5. Inspect the fresh PDF's affected pages. In Overleaf-only work, distinguish
   proposed source changes from a fresh observed Overleaf build.
