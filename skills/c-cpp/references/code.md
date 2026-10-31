# Code, ownership and interfaces

## C

- Keep C translation units valid for the project's C standard; do not introduce
  C++ syntax or change their compiler to silence errors.
- Make ownership, buffer length/capacity and error conventions explicit at
  interfaces. Pair each resource with its matching release function; use a
  cleanup path when several acquisitions can fail, releasing only acquired
  resources in reverse order.
- Check size arithmetic before allocation or indexing, including multiplication
  and room for terminators. Keep a temporary pointer for `realloc` so failure
  does not lose the original allocation; handle zero-size requests explicitly.
  Check return values and distinguish truncation, EOF and errors.
- Inspect signed/unsigned conversions, overflow, shifts, alignment, aliasing and
  object lifetime before treating a compiler optimization as a miscompile.
  `volatile` does not provide thread synchronization.

## C++

- Prefer value semantics and RAII. Use `unique_ptr` for exclusive dynamic
  ownership, `shared_ptr` only for actual shared lifetime, and non-owning
  references/pointers/views for borrowing. Track the owner's lifetime and
  container invalidation; `string_view` and `span` do not extend lifetime.
- Prefer the Rule of Zero. When custom resource management requires special
  members, decide copy/move/destruction behavior together. Do not add
  `std::move` to a named return value when it prevents NRVO, or assume a moved
  object retains its previous value.
- Match exception guarantees to the interface. Release resources on every exit,
  avoid throwing destructors, and mark `noexcept` only when its contract holds.
  Respect projects that disable exceptions rather than introducing throws.
- Select algorithms, containers, ranges, concepts and `constexpr` only within
  the supported standard. Constrain template interfaces at the point of use;
  use forwarding references and `std::forward` only for deliberate forwarding.
  Prefer a clear ordinary function to unnecessary metaprogramming.

## Boundaries, concurrency and performance

- Keep public headers self-contained with include guards or the project's
  equivalent. Preserve ABI/layout, calling conventions and visibility where
  compatibility matters. Use guarded `extern "C"` declarations for C-facing
  entrypoints, C-compatible types and explicit ownership/error rules; keep C++
  exceptions from escaping into C callers.
- Prefer scoped locking and explicit thread ownership/shutdown. Establish the
  lock order and wait predicates; join workers before destroying captured
  state. Use atomics with a stated happens-before argument. Weaker memory
  ordering needs justification; an atomic pointer alone does not solve memory
  reclamation or ABA. Do not assume atomics are always lock-free or faster.
- Profile before changing data structures, allocation or synchronization.
  Compare representative optimized builds with equivalent inputs, compiler
  flags and hardware conditions. Retain behavioral tests alongside benchmarks;
  sanitizer timings do not establish production performance.

For detailed language decisions, consult the applicable standard and
[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).
