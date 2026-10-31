# Static analysis and sanitizers

## Establish the actual compilation context

Use `compile_commands.json` from the current build variant: CMake export with
a supported generator, Meson's Ninja build, or `bear -- <actual-build-command>`
for Make when Bear is already available. For intercepted capture, arrange a
real rebuild with cache bypass as needed. A successful no-op build records no
new translation units. Check source paths, working directories, compiler,
language standard, defines, generated headers and target/sysroot flags.
Generate required headers first. Avoid a repository-root symlink that silently
points analysis at a different variant; pass the database directory explicitly.

## Choose and scope the tool

| Tool | Use |
| --- | --- |
| Compiler warnings | Fast feedback using the project's supported warning policy |
| clang-tidy | Selected source checks with the real compilation database |
| cppcheck | Complementary bug, portability and configuration analysis |
| Clang Static Analyzer / scan-build | Path-sensitive analysis of modeled execution paths |
| ASan / UBSan | Runtime memory errors / selected undefined behavior |
| TSan | Runtime data races in a separate supported build |

Start with existing `.clang-tidy` settings and changed translation units:

```sh
clang-tidy -p build-debug src/example.cpp
cppcheck --project=build-debug/compile_commands.json --enable=warning,performance,portability --error-exitcode=1
```

Adapt filenames and options to available versions. For a configured whole-tree
run, use an available `run-clang-tidy -p build-debug` helper. Without a database,
use `clang-tidy file -- <actual-compile-flags>` only after reconstructing those
flags faithfully; invented include paths can produce misleading results.

## Triage before fixing

- Trace each finding to the code path, ownership or invariant it alleges.
  Resolve configuration errors before treating them as code bugs. Choose
  `bugprone-*`/`clang-analyzer-*` for defect discovery; use modernize,
  performance, guideline or style categories only when they fit the task and
  supported language. Do not enable every check or impose blanket `-Werror`.
- Scope third-party filtering and baseline policy to the repository. Header
  filtering controls reported locations, not all analysis work. Do not silence
  missing includes until the tool's dependency model is understood.
- Apply automatic fixes in a reviewable batch; inspect the diff, rebuild and
  rerun relevant tests. Suppress demonstrated false positives narrowly with a
  reason, for example `NOLINTNEXTLINE(check-name)`; do not use a compiler
  attribute as a universal clang-tidy suppression mechanism.
- `scan-build` must observe compilation, not just linking. Use a dedicated
  uncached analysis build with the wrapper active during configuration when
  compiler selection is cached. Confirm files were analyzed and preserve
  reports; a zero exit code alone does not imply zero findings. Configure
  finding-based CI failure deliberately (for example `--status-bugs`).

Instrument the affected code and final link with matching sanitizer options;
run representative tests that reach the suspected defect. ASan and UBSan can
often be combined; keep TSan separate from ASan. Check compiler/platform/runtime
support, preserve symbolization, and investigate the first relevant report.
Instrumented runs and static analysis cover different failure modes; neither
establishes that unexecuted paths or other build variants are correct.

Sources: [clang-tidy](https://clang.llvm.org/extra/clang-tidy/),
[scan-build](https://clang.llvm.org/docs/analyzer/user-docs/CommandLineUsage.html),
[cppcheck](https://cppcheck.sourceforge.io/manual.html),
[sanitizer options](https://clang.llvm.org/docs/UsersManual.html#controlling-code-generation).
