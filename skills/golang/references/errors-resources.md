# Errors and resource lifetimes

## Preserve useful error contracts

Check failures that can affect correctness, durability or the caller's decision.
Return an existing error unchanged when more context adds nothing; otherwise
wrap meaningful operation context with `fmt.Errorf("read config: %w", err)`.
Wrapping exposes the cause as part of the API: decide deliberately whether an
implementation error should remain discoverable or be translated to a stable
domain error. Do not simply change `%w` to `%v` at every package boundary.

Use `errors.Is` for wrapped sentinels and `errors.As` for error types; use
`errors.AsType` only on a supported Go 1.26+ baseline. Avoid string matching.
Use sentinel errors for stable categories and typed errors for information a
caller actually needs. Prefer lowercase operation messages without punctuation
when composing errors; do not include secrets. On success return `nil`, not a
typed nil pointer boxed as `error`. `errors.Join` can preserve independent
primary/cleanup failures when both matter, without erasing their identities.

Handle/log a failure at the boundary that owns the response rather than logging
the same propagated error at each layer. Keep log messages stable and attach
identifiers as structured attributes, using the existing logger or `log/slog`.
Translate internal errors into the public protocol's safe error contract.
Return expected failures; reserve panics for violated invariants. `recover`
works only from a deferred function in the panicking goroutine; do not use it
to turn arbitrary broken state into apparent success. `log.Fatal` / `os.Exit`
bypass deferred cleanup and belong at a deliberate process boundary.

## Make acquisition and release match

- After successful acquisition, arrange the correct release immediately in the
  owning scope. Shorten that scope inside loops so deferred closes do not retain
  thousands of resources until the outer function returns. Do not close values
  that have no `Close` method (for example `bufio.Scanner`); own the underlying
  reader and check `Scanner.Err` and its token-size limit.
- Do not silently lose important `Write`, `Flush`, `Close`, rename or commit
  errors. A read-only cleanup failure may be irrelevant; explain deliberate
  ignores where non-obvious. Close alone does not promise storage durability;
  follow the required file/transaction contract.
- Reuse `sql.DB` as a pool. Close query rows and check `rows.Err()` after iteration.
  A transaction's queries must use its `sql.Tx`; arrange rollback for early
  exits and report commit failures. A deferred rollback after successful commit
  may return `sql.ErrTxDone` and need no further action.
- Runtime cleanups/finalizers do not replace deterministic release. Use explicit
  `Close` for correctness; consider supported `runtime.AddCleanup` only for a
  justified fallback lifetime, never a required flush or shutdown mechanism.

For process shutdown, stop accepting work, signal owned workers, drain or cancel
within a deadline, wait for completion, then release dependencies in order.
`http.Server.Shutdown` needs a fresh bounded context if the signal/request
context is already canceled. Handle `http.ErrServerClosed` as expected during
shutdown and explicitly manage hijacked/long-lived connections when present.

Sources: [error wrapping](https://go.dev/blog/go1.13-errors),
[errors](https://pkg.go.dev/errors),
[SQL transactions](https://go.dev/doc/database/execute-transactions),
[HTTP shutdown](https://pkg.go.dev/net/http#Server.Shutdown),
[runtime cleanups](https://pkg.go.dev/runtime#AddCleanup).
