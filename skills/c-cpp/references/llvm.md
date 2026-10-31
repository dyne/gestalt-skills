# LLVM IR and pass pipelines

Use this reference for IR tooling and existing passes. For a custom pass,
inspect the pinned LLVM checkout's plugin/API examples and test conventions;
LLVM C++ APIs and plugin compatibility vary by release.

## Preserve toolchain and target identity

Check `clang`, `opt`, `llc` and related tools' versions; use a compatible release
set. Preserve target triple, data layout, CPU/features, optimization level and
source compile flags. Bitcode/IR syntax and pass names are not interchangeable
across arbitrary releases; modern IR commonly uses opaque `ptr` types.

For a small C reproducer (use `clang++` and the actual standard for C++):

```sh
clang -O1 -S -emit-llvm example.c -o example.ll
clang -O2 -c -emit-llvm example.c -o example.bc
llvm-dis example.bc -o decoded.ll
opt -passes='default<O2>' -verify-each -S example.ll -o optimized.ll
llc -filetype=obj optimized.ll -o example.o
```

These commands isolate stages; they do not reproduce a project's full build
unless its flags and dependencies are retained. `llc` produces assembly or
objects; use the appropriate compiler driver for the final link and runtimes.

## Inspect only the relevant transformation

- Use `opt --print-passes` for available passes and the new-pass-manager
  `-passes=` syntax. Respect nesting/adaptors for function and loop passes.
  Run the verifier on changed IR; structural validity does not prove semantic
  equivalence.
- `-O0` frontend output commonly carries `optnone`, which makes most
  transformations skip a function. For a deliberate raw-IR experiment, check
  support for `-O0 -Xclang -disable-O0-optnone`; do not silently strip attributes
  from a production reproducer. `mem2reg` promotes eligible allocas, not
  arbitrary heap memory or all stack objects.
- Start missed-vectorization work with the actual optimized compile plus
  `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize
  -Rpass-analysis=loop-vectorize`. Scope before/after IR dumps to the suspect
  pass/function rather than dumping every pass by default. Preserve evidence
  of aliasing, alignment, trip-count or floating-point constraints.
- Treat `getelementptr` as address calculation, not a memory read; `phi` values
  correspond to predecessor edges. Distinguish `undef`, poison and `freeze`.
  Flags such as `inbounds`, `nsw`/`nuw` and fast-math are semantic promises;
  adding them without proof can introduce undefined behavior.
- For custom transformations, add a reduced IR regression under the checkout's
  `lit`/`FileCheck` conventions and test verifier success plus intended behavior.
  Compare representative executable behavior and performance when relevant;
  fewer IR instructions alone do not prove a speedup.

Use `llvm-nm`/`llvm-objdump` for symbol/object inspection, and `llvm-mca` only as
a target-specific scheduling estimate alongside measurements. For PGO/coverage,
match profiles to the instrumented binary and compatible `llvm-profdata` /
`llvm-cov`; stale profiles are not evidence for the current build.

Sources: [opt](https://llvm.org/docs/CommandGuide/opt.html),
[IR semantics](https://llvm.org/docs/LangRef.html),
[new pass manager](https://llvm.org/docs/NewPassManager.html),
[optimization remarks](https://clang.llvm.org/docs/UsersManual.html#options-to-emit-optimization-reports).
