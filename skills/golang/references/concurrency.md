# Contexts, goroutines and synchronization

Give every goroutine an owner, a termination condition and a way for the owner
to observe completion/errors. Bound worker counts, fan-out, queue depth and
retained work. Starting a goroutine does not make a blocking operation
cancelable, and canceling a context does not wait for goroutines to finish.

## Propagate cancellation to the work

- Pass `context.Context` first for request-scoped operations and propagate the
  caller's context. Do not replace it with `Background` mid-request, store it
  as ordinary long-lived struct state, or use context values as optional config.
  Derive timeouts from the request budget and call their cancel function on all
  paths. Use request-aware HTTP/SQL operations and deadlines for blocking I/O.
- Every channel send/receive that may outlive its peer needs a shutdown path,
  often `select` with `ctx.Done()`. Cancellation selection is not priority:
  if work is also ready, either case may win. Define whether already-started
  work may finish and avoid promising a stronger cutoff than implemented.
- Use `errgroup` when an existing compatible dependency helps coordinate errors,
  cancellation and bounded work; otherwise a small `WaitGroup` plus explicit
  error ownership can suffice. With `Add`/`Done`, add before launching and defer
  `Done` in the worker. `WaitGroup.Go` requires Go 1.25+ and does not itself
  collect errors or impose a concurrency limit.

## Choose synchronization by ownership

Prefer a mutex for a simple shared invariant and channels for transferring work
or ownership. Protect maps and compound state consistently; unrelated atomic
fields do not automatically preserve a multi-field invariant. Keep critical
sections short and avoid holding a lock over unknown callbacks or slow I/O.
Document lock order when several locks interact. Never copy used sync values.

The sender/coordinator closes a channel once all sends are complete; receivers
do not close it merely to stop a producer. Sending on a closed channel panics.
Receive from a closed channel returns immediately, so inspect `ok` when closure
must terminate a loop. A nil channel blocks forever and disables its `select`
case; use that deliberately rather than mistaking it for an empty channel.

Transferring a slice/map/pointer over a channel does not clone its underlying
data. State whether ownership transfers or the value becomes immutable; copying
the descriptor alone does not prevent a race. Reusing pooled buffers is unsafe
until all consumers have finished. A result channel buffer may avoid one blocked
send, but it does not prove cancellation or leak freedom.

## Verify lifetimes

Test success, early error, canceled input, a blocked peer, and shutdown with work
in flight. Use handshakes to establish test preconditions and wait for every
started goroutine to settle. Bound test waits to expose failures without hanging
the suite; sleeps are not synchronization. Run `-race` for exercised paths and
use the repository's leak checks where present. A quiet race detector does not
prove deadlock freedom, correct ordering or the absence of unexecuted races.
Use supported `testing/synctest` for appropriate in-process concurrent/time tests;
it does not make external I/O deterministic or enumerate every schedule.

Sources: [context](https://pkg.go.dev/context),
[pipelines and cancellation](https://go.dev/blog/pipelines),
[memory model](https://go.dev/ref/mem),
[sync](https://pkg.go.dev/sync),
[race detector](https://go.dev/doc/articles/race_detector),
[synctest](https://pkg.go.dev/testing/synctest).
