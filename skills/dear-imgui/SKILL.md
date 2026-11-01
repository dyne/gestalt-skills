---
name: dear-imgui
description: "Build, style, debug, review, and test Dear ImGui interfaces and integrations. Use for testable panels, stable widget IDs, editing/undo, tables and clipped selection, input capture, custom widgets, themes/fonts/DPI, renderer backends, docking/viewports, extensions, and UI automation."
---

# Dear ImGui

1. Establish the project's actual ImGui include/source paths, version/pin,
   configuration macros, branch/fork, platform/renderer pair, context/thread
   owner and adopted extensions. Follow [sources and profiling](references/profile.md).
   Resolve declarations, nearby contract comments and matching demo/backend
   code from that revision before using an unfamiliar API. Public, internal,
   extension, framework and fork-only APIs are distinct contracts.
2. State the observable interaction or integration contract. Keep application
   model, edit buffers, selection and undo ownership explicit. For a new panel,
   follow the [GUI-to-tests workflow](references/gui-workflow.md): share the
   drawing function with UI tests and keep validation/commands independently
   testable. Make the smallest
   compatible change; do not introduce a framework, change backend or upgrade
   dependencies merely to follow this skill. Leave general C/C++/build work to
   the existing C/C++ workflow; keep ImGui-specific source/configuration
   consistency in scope.
3. Load only the needed references; consult examples for a matching pattern.

   | Task | Reference |
   | --- | --- |
   | Source precedence, baseline, optional inspection/lookup helpers | [Profile](references/profile.md) |
   | New panel, staged state, shared drawing function, model and UI tests | [Build-to-test workflow](references/gui-workflow.md) |
   | Visual direction, theme tokens, style scopes, layout and visual regression | [Styling](references/styling.md) |
   | IDs, scopes, text, editing, popups, shortcuts, custom widgets | [Core interaction](references/core-interaction.md) |
   | Tables, filtering, clipping, sorting, multi-selection | [Large data and selection](references/data-selection.md) |
   | Frames, input, rendering, threads, docking and OS viewports | [Integration](references/integration.md) |
   | Font lifetime/sizing, dynamic textures, images and DPI | [Fonts and textures](references/fonts-textures.md) |
   | Extension/framework choice and compatibility | [Extensions](references/extensions-automation.md) |
   | Simulated clicks/typing, Test Engine setup, named paths, CI and captures | [UI automation](references/automation.md) |
   | Diagnostics, test layers, evaluation and evidence | [Verification](references/testing-debugging.md) |

4. Preserve stable IDs through reorder/rename/filtering, balance scopes by their
   actual contracts, query an item's state adjacent to its submission, and use
   safe text formatting. Forward platform input to ImGui regardless of capture;
   use capture to gate application reactions. Keep texture/draw-data lifetimes
   valid through consumption. Prefer public composition to incidental internals.
5. Build against the selected revision and test the changed behavior at the
   appropriate layer. Prefer stable named-widget actions in an existing Test
   Engine integration; use direct input injection for focused regressions.
   Require actual intended test execution and assertions on application results.
   Use the [original examples](examples/README.md) and
   [40 acceptance cases](evals/acceptance_cases.json) where relevant. Compiled,
   null-backend, synthetic-input, Test Engine, pixel and real-platform checks
   establish different facts. Never replace a required rendered/platform check
   with a claim based on headless frames.
6. Report the exact tested revision/backend, commands, observed results and
   untested conditions. Preserve assertions and explain missing prerequisites;
   continue useful independent checks without inventing success.

Research snapshot: 2026-10-31, supplied engineering handbook/package; baseline
v1.93.0. This is evidence to refresh when relevant pins/platforms change, not an
instruction to install that version. Catalogs retain source and extension pins.
The [scenario review](evals/author-review.md) and
[validation record](evals/validation.json) distinguish author judgments from
executed tests and retain uploaded-artifact fingerprints.
