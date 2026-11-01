# Automated interaction tests

Reviewed 2026-11-01: engine `7c808483d6f0a69b9d0843d5f4a141f0a9f74a58`, wiki
`99193c163b8fdf1f9b13e57c4981866ef3dab5e5`; core example baseline v1.93.0.
See [documentation review](automation-sources.json) for scope and fingerprints.
The engine is version-sensitive; matching local headers outrank wiki snippets.

## Select the test layer

- Use an already integrated **Test Engine** for repeatable named-widget actions,
  scrolling, typing, menus, drag/drop and assertions on application behavior.
  It normally injects ImGui input, sometimes using internals to reach targets;
  it does not test OS event delivery simply by clicking a named item.
- Use direct `ImGuiIO::Add*Event` injection for a small isolated regression or
  event-queue test. Submit position, press, a frame, release, another frame;
  preserve focus and sufficient warm-up frames. Derive coordinates from actual
  item bounds. The existing `semantic_main.cpp` exercises this route.
- Add rendering/capture for pixel assertions and actual platform tests for OS
  focus, IME, mixed-monitor DPI or detached windows. A null renderer cannot
  capture a real framebuffer. Do not install the engine just to rename a label.

## Integrate once, then drive the existing UI

For a new panel, start with the [GUI-to-tests workflow](gui-workflow.md).
`examples/settings_panel.cpp` is shared application drawing code; the fixture's
`GuiFunc` calls it rather than reproducing its controls. Context-free command
checks complement its interaction tests.

1. Pin compatible core/engine revisions and check the engine's license. Build
   the engine sources and **all relevant core/application units** with the same
   configuration, including `IMGUI_ENABLE_TEST_ENGINE`. The wiki's 1.87+ minimum
   and event-queue requirement are not a compatibility guarantee for every pin.
   A missing core hook define is not fixed by defining it only in the test file.
2. Supply a coroutine interface or enable
   `IMGUI_TEST_ENGINE_ENABLE_COROUTINE_STDTHREAD_IMPL=1` consistently. The default
   implementation alternates the test coroutine and app thread; it does not
   run them in parallel. This does not synchronize unrelated application workers.
3. After core/backend initialization, create the engine, configure IO, register
   tests with `IM_REGISTER_TEST` (retains source locations), and `Start` it with
   the intended ImGui context. The minimal upstream app also permits registering
   after start. Do not manually duplicate hooks already installed by `Start`.
4. Continue ordinary backend and ImGui frames. `NewFrame` dispatches test hooks.
   A `TestFunc` drives the real app; add `GuiFunc` only for an isolated fixture.
   Put per-test state in `SetVarsDataType<T>` / `GetVars<T>` or stable application
   data through `test->UserData`; avoid cross-test mutable statics. Keep the
   engine's `PreSwap` before present and `PostSwap` after present, particularly
   for captures; neither call replaces rendering or presentation.
5. Stop the engine (joins its test coroutine), shut down backends, destroy the
   ImGui context, then destroy the engine context. The order preserves engine
   settings serialization. Do not destroy data still referenced by a test.

## Target stable semantic identities

| Reference/action | Meaning or trap |
| --- | --- |
| `SetRef("Window")`, then `ItemClick("Save")` | Base path plus item. `SetRef` itself is absolute, never relative to its old base. |
| `"//Other/Save"` | Absolute item path; ignores the current base. |
| `"/Save"` | Window-root relative, not filesystem-root or parent-directory syntax. |
| `"//$FOCUSED/OK"` | Current focused window. `SetRef("//$FOCUSED")` freezes its resolved value; establish focus before relying on it. |
| `"Rows/$$42/Enabled"` | An integer `PushID(42)` scope; prefer stable model IDs over row numbers or pointer addresses. |
| `"###save"` / `"Save##suffix"` | Retain `###` for a stable changing/localized identifier; with `##`, the visible prefix remains part of identity. |
| `"A\\/B"` in C++ source | Escaped slash inside one label. Respect both C++ and path escaping. |
| `"**/Save"` | Full-label wildcard for visible/unclipped items, not partial text or a guarantee to find offscreen rows. |

Resolve child windows through `WindowInfo(...).Window` and set that window as
the base; do not guess internally mangled names. Current headers return an
`ImGuiTestItemInfo` value; some wiki examples still use pointer syntax. Avoid
ambiguous wildcards. The TODO records limitations for nested-child wildcard
scrolling and items clipped by table columns: open/scroll/resize the correct
container and keep its identity explicit. Do not bypass the behavior being
tested with direct model writes or forced internal state changes.

## Actions, assertions and synchronization

| Intent | Starting API |
| --- | --- |
| Click / double-click / activate by navigation | `ItemClick`, `ItemDoubleClick`, `ItemNavActivate` |
| Set a check/tree/menu state deterministically | `ItemCheck` / `ItemUncheck`, `ItemOpen` / `ItemClose`, `MenuCheck` |
| Edit a scalar/text field through UI | `ItemInputValue(ref, value)`; then assert the model's committed value |
| Raw keys versus Unicode text | `KeyPress` / paired `KeyDown`-`KeyUp`; `KeyChars` / `KeyCharsReplaceEnter` for text |
| Drag/drop or scrolling | `ItemDragAndDrop`, `ItemDragWithDelta`, `ScrollToItemY`, `ScrollToPosY` |
| Inspect state without an action | `ItemExists`, `ItemIsChecked`, `ItemInfo`, `ItemReadAsInt/String` where supported |

Prefer idempotent state actions to a toggle when setting up a test. Actions
yield as needed; use `ctx->Yield()` or bounded condition-driven frame loops
for additional application work. Simulation-time `Sleep` may be skipped in
Fast mode and is not a barrier for background threads. Keep fake-time and
wall-clock deadlines distinct; make worker completion observable. `ItemInfo`
failure is an empty/error result, not necessarily a null pointer.

Use `IM_CHECK`, operand checks such as `IM_CHECK_EQ`, and `IM_CHECK_STR_EQ` for
strings. Failed checks mark the test and normally return from the current
function; they do not necessarily unwind a caller helper. Inspect
`ctx->IsError()` after fallible helpers. Use current `_NO_RET` / `_RETV` variants
deliberately, not misspelled wiki forms. Assertions on the app model establish
business results; item visibility alone does not prove that Save persisted data.

A custom toggle built on `InvisibleButton` is not automatically a checkable
item to the engine. `ItemCheck`/`ItemIsChecked` require reported checkable/checked
status. Prefer a built-in control; otherwise click/activate and assert the
application value, or deliberately maintain the matching internal test-info
hooks. Do not add internal dependencies merely to make one helper checkable.

## CI, failures and captures

Queue a specific registered pointer with `QueueTest`, or use `QueueTests` with a
group/filter. Filters support comma terms, exclusion `-`, anchors `^`/`$`, and
special `tests`/`perfs`/`all` keywords; they are **not** general regexes. An empty
filter selects nothing. Bound process time and frames, detect abort/remaining
queue, and require intended test identities/counts. Check
`GetResultSummary`: nonzero `CountTested`, expected successes, zero `CountInQueue`;
zero failures plus zero executed tests must not pass. The older `GetResult`
wrapper disappears with obsolete functions disabled.

Set `ExportResultsFilename` and `ExportResultsFormat=...JUnitXml` before running;
keep filename storage alive. `Stop` exports configured results; preserve logs,
process exit and XML together. JUnit includes registered, unselected tests as
skipped cases; verify
executed identities/statuses, not just the total number of `testcase` elements.
Set `ConfigBreakOnError=false` for unattended
runs while keeping assertions; intentional core-assert tests in the upstream
test suite may require a debugger. `ConfigStopOnError`, watchdogs and an outer
process timeout cover different failures. Do not treat suite CLI flags as
automatic flags of an arbitrary host app. Fast/max-speed headless execution
can skip rendering only when no capture/render check depends on it.

For crash reporting, wire `ImGuiTestEngine_CrashHandler` into an existing crash
handler, or use `InstallDefaultCrashHandler` when appropriate for the host.
Configured exports enable this path; abrupt termination still needs external
timeout/exit monitoring. `ExportEx` permits an explicit export without stopping.

For screenshots enable capture support, provide the renderer's real
`ScreenCaptureFunc`, and service `PostSwap` after all relevant framebuffers.
Start with `CaptureScreenshotWindow`; stitching/hiding the cursor are capture
options, not pixel comparisons. Fix scale/fonts/theme/viewport for visual
baselines and inspect or compare the output. Video additionally needs an
available configured FFmpeg encoder and actual rendered frames. Use current
`CaptureAddWindow`, `CaptureBeginVideo()` / `CaptureEndVideo()` signatures;
older wiki examples pass obsolete arguments. Do not download an encoder or
claim captures from the supplied capture-disabled fixture.

## Scope and licenses

The public wiki's language-binding page currently points to Julia; it is not
evidence that the native engine has a supported Python/JS API. Check a chosen
binding and pin independently. [Engine license v1.04](https://github.com/ocornut/imgui_test_engine/blob/7c808483d6f0a69b9d0843d5f4a141f0a9f74a58/imgui_test_engine/LICENSE.txt) is distinct from MIT core,
suite and minimal-app code; consult its exact eligibility/distribution terms,
not a blanket claim that all ImGui tooling is MIT. The skill bundles only its
own example caller, not the engine implementation. Contribution/CLA rules apply
to upstream submissions; a coding task does not authorize publishing one.

Sources: [wiki index](https://github.com/ocornut/imgui_test_engine/wiki),
[engine/context/config headers](https://github.com/ocornut/imgui_test_engine/tree/7c808483d6f0a69b9d0843d5f4a141f0a9f74a58/imgui_test_engine),
[minimal app](https://github.com/ocornut/imgui_test_engine/tree/7c808483d6f0a69b9d0843d5f4a141f0a9f74a58/app_minimal).
