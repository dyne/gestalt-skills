# Diagnostics, validation and evidence

Research baseline v1.93.0, checked 2026-10-31. Use the real application's
revision/backend for acceptance; the supplied harnesses are bounded examples.

## Diagnose the failing layer

Keep assertions enabled. Use the matching demo plus Metrics/Debugger, ID Stack
Tool, item picker, Debug Log and font/UTF-8 tools before adding ad hoc state.
For an unresponsive widget, inspect identity, clipping, disabled/modal/focus
state and input forwarding. For a missing image, separate texture identity,
upload/status and GPU state. For a misplaced widget/scissor, inspect coordinate
space and framebuffer scale. Check exact names in local headers; diagnostic
entrypoints themselves can change.

Measure application/model work, ImGui submission, renderer preparation, GPU
execution and presentation separately. Clip dense views and avoid repeated
data rebuilding where measurements justify it. A frame-rate number cannot
identify the bottleneck; an idle/redraw strategy must still support input,
animation and pending texture/platform work.

## Choose evidence that addresses the contract

| Check | What it establishes |
| --- | --- |
| Compile with selected headers/config, optionally obsolete APIs disabled | API/configuration compatibility for that build |
| Context + null-backend frames | Exercised frame/scope paths without GPU output |
| Synthetic input | Specific state transitions under the injected event sequence |
| Test Engine | Semantic actions/assertions on the configured application |
| Rendered captures | Actual inspected pixels for the captured renderer/scale/theme |
| Real platform tests | Observed focus, IME, input, windowing/DPI/device behavior on that platform |

Use stable object identity assertions and explicit preconditions. Test rename,
sort/filter/delete, hidden/collapsed windows, popup cancellation, edit completion
and disappearance, keyboard activation and clipped range anchors as relevant.
For rendered changes, inspect representative normal/minimum sizes, fonts/DPI,
focus/disabled/selection states and the actual renderer. Renderer upgrades need
texture create/update/destroy, clipping/offsets, resize/device-loss and in-flight
resource-lifetime checks. Do not require this whole matrix for a tooltip edit.

The skill's `examples/README.md` gives compile/run commands for 12
original patterns and two harnesses. The research reports eight smoke frames
plus toggle/selection checks; rerun those against the selected checkout before
claiming current results. Neither harness validates all twelve interactions,
undo behavior, pixels, docking, IME, physical DPI or all extension combinations.
The examples' fixed-view and buffer/record-lifetime assumptions are contracts
to preserve or deliberately replace, not production completeness guarantees.

## Acceptance cases and maintenance

Evaluate all 40 cases in `evals/acceptance_cases.json` when revising the overall
skill; select relevant cases for narrow changes. Record the answer/action and
evidence separately. An author review of expected behavior is not an independent
model evaluation, and a prose scenario is not a runtime test. Keep coverage
gaps visible instead of passing a case solely because its keywords occur.

Refresh version-sensitive references and catalog records when dependencies or
platform support change. Use full commits and source paths for durable claims;
living wiki/issues also need a checked date and final-resolution context.
For an upstream reproduction, isolate the issue against a matching official
example/demo, retain backend/OS/version/configuration details and a minimal
reproducer, and distinguish observed behavior from the hypothesis. Publishing
an issue or sending a report requires the user's instruction.

Sources: [demo diagnostics](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp),
[FAQ debugging](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md),
[Test Engine wiki](https://github.com/ocornut/imgui_test_engine/wiki).
