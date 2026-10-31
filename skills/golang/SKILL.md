---
name: golang
description: "Write, review, debug, test, and optimize Go code. Use for .go files, package/interface design, errors and resource lifetimes, contexts/goroutines/channels, HTTP/SQL and secure I/O, modules/toolchains, fuzzing, race detection, benchmarks, and profiling."
---

# Go

1. Inspect `go.mod`, any `go.work`, the selected Go version, build tags, target
   OS/architecture, cgo settings, CI and existing package/test conventions.
   Identify the requested behavior and affected callers. Preserve supported
   toolchains, dependency pins and public contracts; do not upgrade Go, add a
   framework or impose an architecture merely to apply this skill.
2. Read only the references relevant to the task; combine them when a defect
   crosses package, resource or concurrency boundaries.

   | Task | Reference |
   | --- | --- |
   | Idioms, types, interfaces, package/API design, data ownership | [Language and design](references/language-design.md) |
   | Error chains, logging, cleanup, transactions, shutdown | [Errors and resources](references/errors-resources.md) |
   | Contexts, goroutines, channels, locks, cancellation | [Concurrency](references/concurrency.md) |
   | HTTP, SQL, files, decoding, cryptography, untrusted data | [I/O and security](references/io-security.md) |
   | Unit/integration tests, fuzzing, race and leak checks | [Testing](references/testing.md) |
   | Benchmarks, profiles, allocations, caches, runtime tuning | [Performance](references/performance.md) |
   | Modules/workspaces, version gates, build and analysis commands | [Tooling](references/tooling.md) |

3. Reproduce a bug or establish the affected packages' baseline before changing
   behavior. Trace ownership of mutable data, resources and goroutines. Prefer
   explicit dependencies and the smallest useful interface; keep expected
   failures as returned errors and establish how cancellation reaches every
   blocking operation.
4. Implement the smallest coherent change, following the repository's formatting
   and naming conventions. Use the standard library where it fits. Handle
   failures that affect the result, bound external work and keep cleanup owned
   by the acquiring scope. Apply security checks to the touched trust boundary;
   undertake broad security or architecture audits only when requested.
5. Format changed Go files and run the affected checks/tests. Verify the
   reproducer, error paths and relevant cancellation/shutdown behavior. Use
   race detection, fuzzing or benchmarks when they can test the suspected
   failure or improvement; do not infer correctness from coverage, a quiet
   scanner, or one benchmark sample.
6. Report the change, commands, selected toolchain/build configuration and
   observed results. Distinguish cached tests, fresh execution and untested
   platforms/integrations. If a tool, dependency or target runtime is missing,
   continue meaningful independent checks and state the remaining limit.

Condensed and adapted from the six `golang-*` skills in
[samber/cc-skills-golang](https://github.com/samber/cc-skills-golang), with
additional Go guidance. Preserve the [upstream MIT notice](LICENSE.upstream).
