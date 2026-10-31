# Language, data ownership and package design

## Idioms that affect correctness

- Use `gofmt` and existing import/lint conventions; prefer clear guard clauses,
  useful names and focused functions over rigid line/parameter counts. Export
  only deliberate APIs and document their contracts. Keep acronym casing and
  package names consistent; avoid redundant package-name prefixes on exports.
- Make zero values useful when practical. Nil slices support `append`, `len`
  and `range`; nil maps support reads but not writes. Choose nil versus empty
  slices deliberately when JSON/API output distinguishes `null` from `[]`.
  Allocate maps before mutation and preallocate only when size is meaningful.
- Slices share backing arrays; copying a slice descriptor does not copy data,
  and `append` may mutate shared capacity or allocate a new backing array.
  Clone at ownership boundaries, not on every call. Map/slice clones are
  shallow when elements contain pointers or other reference-like values.
  Avoid returning a tiny subslice that unintentionally retains a huge buffer.
- Map iteration order is unspecified. Sort explicitly when output order is a
  contract. A `range` element is a copy; mutate `items[i]` when the original
  element must change. Go 1.22+ per-iteration variables apply under the new
  language semantics to variables declared by the loop, not shared variables
  assigned with `=`. Do not mechanically add/remove closure copies without
  checking the package language version and capture.
- Strings contain bytes; `len` measures bytes, `range` decodes runes, and a rune
  is not necessarily a user-perceived character. Define invalid UTF-8 behavior
  before writing Unicode transformations or fuzz properties. Explicitly check
  numeric conversions/size arithmetic when parsing untrusted lengths.

## APIs and architecture

Define small interfaces where consumed when they decouple a real dependency;
do not create an interface for every concrete type. Accept a concrete type when
no abstraction is needed. Use composition and explicit constructors/wiring.
Choose a simple parameter list or config struct first; functional options help
when independently optional settings justify them. Validate configuration at
construction and return an error when it can fail. Avoid hidden I/O or mutable
service globals in `init`; retain deliberate registration/embedding conventions.

Choose pointer receivers for mutation, noncopyable state or a stable identity;
otherwise assess semantics and measured cost. Pointer/value method sets differ
when satisfying an interface. Never copy used mutexes, wait groups, pools or
structs containing them. An interface holding a typed nil pointer is non-nil;
return an actual `nil` error on success. Prefer keyed literals for evolving
structs and keep invariants behind methods when callers must not bypass them.

Preserve an established flat, layered, hexagonal or domain-oriented layout.
Introduce package boundaries around cohesive responsibilities and avoid import
cycles. Use `internal` for implementation packages where appropriate; keep
domain rules independent of HTTP/SQL details when those boundaries exist.
Generics fit algorithms with shared type-safe behavior; they do not justify a
framework, reflection or `any` where an ordinary function works. Prefer available
standard `slices`/`maps` helpers and lazy iterators only within supported versions.

Sources: [review comments](https://go.dev/wiki/CodeReviewComments),
[Effective Go](https://go.dev/doc/effective_go),
[nil interfaces](https://go.dev/doc/faq#nil_error),
[loop semantics](https://go.dev/blog/loopvar-preview),
[module layout](https://go.dev/doc/modules/layout).
