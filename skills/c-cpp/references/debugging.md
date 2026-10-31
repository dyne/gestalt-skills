# GDB and runtime diagnosis

## Match evidence to the failure

Preserve the failing executable, libraries, inputs and build configuration.
Load matching debug symbols and source; a rebuilt binary is not necessarily
compatible with an old core. Start with the failing optimized build when the
bug depends on optimization. For a diagnostic rebuild, `-g -Og` or `-g -O0`
often improves inspection, but optimized-out values are not proof of corruption.

```sh
gdb --args ./build-debug/app argument
gdb ./saved-app ./core
gdb -q -batch -ex 'set pagination off' -ex run -ex 'thread apply all bt full' --args ./build-debug/app argument
```

At the relevant stop, gather evidence before resuming or mutating state:

| Need | Commands |
| --- | --- |
| Crash or hang context | `info threads`, `thread apply all bt full` |
| Suspect frame | `frame N`, `info args`, `info locals`, `print expression` |
| Break at a cause | `break file.c:line`, `break function if condition` |
| Find a write | `watch expression` after the watched storage is valid |
| Inspect instructions/memory | `x/i $pc`, `disassemble /s`, `x/16bx address` |
| Follow execution | `next`, `step`, `finish`, `continue` |

A watchpoint observes storage with a finite lifetime; hardware slots and watched
width are limited. For a hang, distinguish blocked I/O, a wait predicate,
deadlock and active spinning from all-thread stacks. Scheduler locking changes
thread behavior and can itself prevent progress. Calling functions, assigning
variables or forcing returns in GDB alters the inferior; label such experiments.

## Remote, reverse and scripted sessions

- Attach only to the intended process; attaching pauses it. For remote work,
  use a target-compatible GDB with the matching local executable and libraries,
  plus `set sysroot`/`set substitute-path` when needed. Start `gdbserver` through
  the existing secured channel; its connection is not an authentication layer.
  Avoid exposing a new public listener. After `target remote`, use `continue`
  for an already-started inferior.
- Start the inferior before recording: `start`, `record full`, `continue`,
  then `reverse-next` or `reverse-continue` within the recorded interval.
  Software recording has instruction/platform limits. `record btrace pt`
  requires supported Intel tracing; it records control flow and does not
  provide historical data state like full recording. Check support before
  promising reverse debugging.
- Use scoped command files or `-ex` arguments for repeatable capture; avoid
  changing global `.gdbinit`. Use matching, trusted C++ pretty-printers before
  reverse-engineering container internals. Load Python helpers only when needed
  for repeated inspection, and preserve GDB's auto-load trust settings.

Sources: [GDB manual](https://sourceware.org/gdb/current/onlinedocs/gdb.html/),
[record/replay](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Process-Record-and-Replay.html).
