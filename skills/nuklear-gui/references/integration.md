# Nuklear integration and evidence

Use the sections relevant to the requested change. Resolve failures using the
project's pinned code and build settings; do not silently upgrade dependencies,
invent settings or replace the user's product to make a check pass.

## 1. Configuration and implementation ownership

Inventory all translation units and build variants that include Nuklear or its
backend. Put shared `NK_*` feature options in one configuration header included
before every Nuklear include. Keep `NK_IMPLEMENTATION` in exactly one C/C++
implementation translation unit and give the backend's implementation guards
exactly one owner too; inspect the pinned backend for their actual names. Do not
place implementation guards in the shared configuration header.

Record compatible Nuklear and backend revisions, local patches and licenses.
Check include order and effective definitions across debug/release, GUI variants
and supported compilers; use compile commands/preprocessor output when build
flags obscure them. Duplicate symbols, missing symbols or mismatched structures
require fixing configuration drift before trusting runtime results. The
[Nuklear upstream instructions](https://github.com/Immediate-Mode-UI/Nuklear)
describe the single-header implementation arrangement; project pins govern the
actual integration.

## 2. Coordinate mapping

Name the spaces before writing automation:

| Space | Establish from the running application |
| --- | --- |
| Window/event | Window dimensions and the coordinate semantics of actual incoming SDL events. |
| Logical UI | Nuklear layout bounds, renderer logical size, scale and viewport/letterboxing. |
| Framebuffer | Actual renderer output or drawable dimensions in pixels, including density. |

Trace one point through rendering, SDL event handling, backend input conversion,
Nuklear hit testing, focus bounds and synthetic event injection. Record where
each transform occurs. SDL renderer logical-size handling and a backend may
already transform event coordinates; do not convert them a second time. A named
control ID only identifies a target; it does not prove its transform is correct.

For an SDL2 renderer using logical UI coordinates, take the visible target's
current logical bounds and choose an interior point. First establish the injection
route: native window events may pass through SDL filtering, while direct
`SDL_PushEvent` injection may bypass that route. Inspect and test the project's
actual path; do not assume all synthetic events expect window coordinates.
When the injection route expects window coordinates, use the pinned backend's
mapping and `SDL_RenderLogicalToWindow` where available; verify headers and linked SDL
version support it (introduced in SDL 2.0.18). Its inverse is
`SDL_RenderWindowToLogical`. Inspect
[logical-to-window API details](https://wiki.libsdl.org/SDL2/SDL_RenderLogicalToWindow)
and [logical renderer behavior](https://wiki.libsdl.org/SDL2/SDL_RenderSetLogicalSize)
against the installed version. Other backends, such as OpenGL, require their own
drawable/viewport mapping; do not apply SDL_Renderer functions indiscriminately.

At 2x density, compare pointer placement, measured control bounds and the
rendered screenshot. Repeat after resizing, scrolling and scale changes. Account
for viewport offsets as well as scale; multiplying coordinates by two alone is
insufficient. If the pinned version lacks the conversion API, inspect and test
its equivalent transform or report the unsupported automation path before
claiming a hit-test pass.

## 3. Layout and focus

Measure actual control rectangles from the current layout, after font selection,
scrolling and resizing. Bind automation and keyboard focus/navigation to these
bounds and current visibility; rebuild stale targets after layout changes.
Portrait content must scroll with every primary action reachable. Scroll a
target into view before activation and verify focus visibility and order.

If an action is clipped, overlapped or unreachable, fix layout/scrolling and
repeat the failing cell. Moving a synthetic click onto an invisible target does
not establish usable layout. Inspect focused controls and action reachability
in screenshots, rather than treating event delivery as visual evidence.

## 4. Combined visual matrix

State concrete settings and enumerate the Cartesian product for the supported
platforms/builds; record each cell's outcome and screenshot path.

| Axis | Required settings |
| --- | --- |
| Theme | Both supported themes; use their real project names. If fewer exist, record that constraint rather than inventing a second theme. |
| Window | Default, minimum supported dimensions, portrait and landscape; record sizes. |
| Font scale | At least 100% and 150%, using the application's settings. |
| Density | 1x and 2x; record window, logical and framebuffer sizes and how density was obtained. |

With two themes these axes yield 32 cells before platform/build variants. Include
minimum width + 150% font + 2x density explicitly for both themes. For every cell,
capture and actually inspect clipping, overlap, focus indication, text and primary
action reachability. Record inspected screenshot artifacts and failures. If time
or hardware prevents the full matrix, label the untested cells and keep the
acceptance claim limited to the executed subset; do not replace combined cells
with isolated axis checks.

## 5. Work ownership and responsiveness

Keep SDL event processing and Nuklear state/rendering on the main thread. Move
expensive sequential RPC, proof or computation chains to workers. Capture an
immutable job snapshot of inputs/settings when submitted; do not let workers
read mutable UI objects or write Nuklear/SDL state.

Attach request and settings generations to jobs and results. Only the main thread
applies results whose generations still match the active request/settings. Bound
queue sizes, message payloads and per-frame result draining; define overflow and
backpressure behavior. Keep secrets out of generic queued messages. Errors and
cancellation need explicit terminal states, not silent loss of a pending job.

Define cancellation and shutdown ownership: stop accepting work, signal workers,
settle/stop pending jobs and join or safely retire workers before freeing their
resources. Avoid a blocking UI-thread wait on noncancelable I/O; use bounded I/O
and a shutdown path with clear lifetime ownership. Late callbacks must never
access destroyed UI state. Exercise cancellation and close while work is pending,
settings changes, stale/late completion, worker errors and event/result saturation.
Observe that input/rendering remain responsive and only current results appear.
If a job cannot be interrupted, state that limit and ensure its completion cannot
touch released state before claiming shutdown is safe.

## 6. Password and secret state

Use a dedicated bounded password buffer and masked display; avoid a generic
text editor's undo/history. Define byte capacity, terminator space, UTF-8 input
validation and codepoint-aware truncation/deletion so a full buffer cannot split
an encoding sequence or overrun. Set an explicit clipboard copy/paste policy.
Masking the screen does not remove plaintext from memory.

Do not put plaintext in logs, diagnostics, editor history or generic queued
events. Trace the native input/backend path: SDL text input or OS input methods
may transiently carry plaintext. Consume it without making extra retained copies;
do not promise that every library, input-method or OS copy can be erased. Give
secret-bearing worker inputs dedicated ownership and lifetimes rather than
embedding them in generic job snapshots/messages.

Erase owned buffers on submit completion, clear, cancel, error and destruction as
appropriate to their lifetime. Use a supported clearing primitive that the
compiler cannot optimize away; check platform availability and generated code or
documented guarantees rather than relying on ordinary `memset`. Inspect test
diagnostics for accidental secret echo. Test boundary-length/multibyte input and
each cleanup path with dummy secrets, and report unerasable external-copy limits.

## 7. Installed assets

Bundle deliberately chosen fonts/assets with licenses and provenance. Resolve
them from the installed layout instead of the source-tree current directory.
Install to a temporary prefix/package, launch from an unrelated directory with
an isolated user profile, and verify the actual selected font and resolved asset
paths (using nonsensitive diagnostics or inspection). Confirm the installed
runtime needs no dependency, font or asset downloads.

Exercise missing/corrupt assets and the intended fallback or clear error. A
source-tree launch or a visually similar system font cannot prove the bundled
font was selected. If the installed path/fallback fails, correct packaging and
repeat the installed launch; report installation/display prerequisites that
prevent that check.

## 8. Native verification and display limits

Combine focused tests of transforms, state transitions, worker generations and
secret-buffer boundaries with real SDL event automation and screenshots of
focus, scrolling, clipping, input mapping and renderer behavior. An internal
direct call to a button handler does not test SDL input conversion.

Keep separate records for model-only tests, native software-renderer/Xvfb runs,
simulated 2x density and physical displays. Record OS, compiler, SDL/backend
revision, renderer, display mode and actual dimensions with exact commands and
pass/fail/skip counts. Software/Xvfb and simulated density are useful regressions;
neither establishes physical hardware HiDPI behavior. If physical hardware is
unavailable, state that limitation explicitly and retain it as unverified.

## 9. Consistent state and actions

Derive readiness, status messages, footers and enabled actions from a consistent
state model/snapshot. Specify transitions such as idle, loading, ready, running,
canceled, failed and completed only where applicable. Check invariants across
views after settings changes, reconnects, errors and worker completion.

For example, a Node footer must not say proving is unavailable while a Request
view can approve. Adapt that invariant to the actual product; do not invent
those view names in another application. Exercise both successful and failed
transitions and confirm the displayed explanation agrees with the action state.

## 10. Optional GUI build boundary

Keep GUI targets and dependencies optional and away from core/CLI/WASI builds.
Do not expose SDL/Nuklear headers or GUI assets as unconditional core/public
dependencies. Inspect dependency edges and package rules, not just feature flags.
Build supported GUI-disabled variants without GUI dependencies, then build and
test the installed GUI. If disabling the GUI still requires SDL or its assets,
fix the dependency boundary before declaring optional builds supported.
