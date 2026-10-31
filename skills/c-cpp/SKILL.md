---
name: c-cpp
description: "Implement, review, debug, and optimize C/C++ code and native builds. Use for C/C++ ownership, templates, concurrency, CMake, Meson, GNU Make, GDB, sanitizers, clang-tidy, cppcheck, scan-build, and LLVM IR or pass pipelines."
---

# C and C++

## Workflow

1. Establish the language and supported standard, compiler/version, target ABI,
   build system, configuration and relevant tests from current source and CI.
   Preserve existing presets, dependency pins, allocator conventions and
   restrictions on exceptions, RTTI or threading. Do not upgrade the standard,
   migrate build systems or introduce a framework merely to apply this skill.
2. Load only the reference needed for the task; combine references when the
   failure crosses layers.

   | Task | Reference |
   | --- | --- |
   | C/C++ implementation, ownership, interfaces, templates, concurrency, performance | [Code](references/code.md) |
   | CMake targets, presets, dependencies, exports, cross-compilation | [CMake](references/cmake.md) |
   | Meson options, dependencies, wraps, cross files | [Meson](references/meson.md) |
   | GNU Make rules, header dependencies, incremental or parallel builds | [Make](references/make.md) |
   | Crashes, hangs, core dumps, GDB, remote or reverse debugging | [Debugging](references/debugging.md) |
   | Compilation databases, static analysis, sanitizer runs | [Analysis](references/analysis.md) |
   | IR inspection, opt/llc, pass pipelines, missed optimizations | [LLVM](references/llvm.md) |

3. Reproduce the symptom or establish a focused baseline with the project's
   actual commands. Distinguish configuration, preprocessing, compilation,
   linking and runtime failures. Inspect the failing command before changing
   flags; preserve the failing binary and configuration when investigating it.
4. Make the smallest coherent change. Express build requirements through
   targets/dependencies. Use separate build directories for incompatible
   compiler, generator, sysroot or instrumentation variants; do not repair a
   stale configuration by deleting an unrelated build tree.
5. Run the affected build and meaningful tests. For a fix, rerun the reproducer;
   add the regression case to the existing test framework when warranted.
   Select analysis or instrumentation that can expose the suspected defect.
   Measure performance changes with representative workloads and equivalent
   optimized builds. Do not treat a successful compile or a quiet analyzer as
   proof of runtime correctness.
6. Report the change, exact configuration/commands, observed results and
   untested variants. If a required compiler, dependency, target runtime or
   debugger capability is unavailable, report that limit and continue checks
   that remain meaningful; do not invent successful verification.

## Compiler caching

Check `command -v ccache` (or the platform equivalent) before configuring or
building C/C++ code. Whenever found, enable it by default for cache-compatible
compilation, including debug and sanitizer builds. Preserve an explicitly
disabled cache or a project/user-selected launcher; do not double-wrap a
compiler. If unavailable, continue without it rather than requiring installation.
Use the reference's CMake launcher flags, Meson autodetection or explicit
machine-file configuration, and Make compile-only launcher. Confirm the actual
compile commands use the selected cache; finding the executable is not enough.
Do not wrap link commands or `opt`/`llc`. For compiler-interception analysis or
compilation-database capture, keep the analysis wrapper outermost, bypass
caching when it hides compilation, and ensure translation units actually
rebuild. Also bypass caching when diagnosing the compiler/cache itself.
