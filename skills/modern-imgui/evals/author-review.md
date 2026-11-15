# Acceptance scenario author review

Reviewed 2026-10-31 against the consolidated skill and supplied 40 scenarios.
This is an author walkthrough of the required decision/action, not an independent
model evaluation or 40 executed UI tests. Reference names below are under
`references/`. Runtime results must be reported from actual current runs.

| Case | Response/action following the skill | Primary reference |
| --- | --- | --- |
| IMGUI-01 | Submit `End` outside the successful-content branch so collapsed windows remain balanced. | core-interaction.md |
| IMGUI-02 | Arrange `EndChild` before every exit after a begun child, including a false return. | core-interaction.md |
| IMGUI-03 | End a table only inside the successful `BeginTable` path. | core-interaction.md |
| IMGUI-04 | Add `EndDisabled`; false still pushes a scope and cannot undo an outer disabled scope. | core-interaction.md |
| IMGUI-05 | Inspect `NoTreePushOnOpen` explicitly; a leaf alone may still need `TreePop`. | core-interaction.md |
| IMGUI-06 | Scope controls by stable object ID, keeping the sorted row index as a separate view coordinate. | data-selection.md |
| IMGUI-07 | Retain a stable window ID with `###` while changing the visible title. | core-interaction.md |
| IMGUI-08 | Render log bytes with `TextUnformatted` or a fixed format, never as the format string. | core-interaction.md |
| IMGUI-09 | Use the official std::string adapter or an owned mutable buffer; remove the `c_str()` cast. | core-interaction.md |
| IMGUI-10 | Deliver events to ImGui unconditionally; use capture flags only for the application's reactions. | integration.md |
| IMGUI-11 | Track ownership across Return press/release so changed text focus does not leak the release. | integration.md |
| IMGUI-12 | Register a real routed shortcut outside the menu-open branch, in the intended focus scope. | core-interaction.md |
| IMGUI-13 | Match popup opening and submission under the same effective ID stack. | core-interaction.md |
| IMGUI-14 | Make opening a one-shot action and continue submitting popup contents while open. | core-interaction.md |
| IMGUI-15 | Identify the actual branch and adopt a deliberate matching docking pin if required, without assuming master exports docking. | profile.md; integration.md |
| IMGUI-16 | Initialize default layouts conditionally; preserve the user's existing layout/settings afterward. | integration.md |
| IMGUI-17 | Explain the observed Wayland viewport limitation, check current backend support and retain single-window docking. | integration.md |
| IMGUI-18 | Retain borrowed font bytes through dynamic baking and surviving shared-atlas lifetime. | fonts-textures.md |
| IMGUI-19 | Implement texture request processing before advertising RendererHasTextures, or remove that claim. | fonts-textures.md |
| IMGUI-20 | Distinguish deliberate legacy atlas support from a modern renderer falsely advertising texture updates. | fonts-textures.md |
| IMGUI-21 | Resolve the chosen backend's representation and lifetime instead of copying a foreign renderer's cast. | fonts-textures.md |
| IMGUI-22 | Read the matching Vulkan header and use the current image-view/layout API; recognize any compatibility overload. | fonts-textures.md |
| IMGUI-23 | Populate the matching DX12 InitInfo and descriptor callbacks rather than using the removed positional initializer. | fonts-textures.md |
| IMGUI-24 | Subtract DisplayPos, apply FramebufferScale, clamp and honor the backend scissor origin. | integration.md |
| IMGUI-25 | Verify implemented VtxOffset support or the application's consistent index-width configuration. | integration.md |
| IMGUI-26 | Stage owned draw buffers plus texture requests/resources and synchronize their use across frame/thread boundaries. | integration.md |
| IMGUI-27 | Build a dense filtered view before clipping, retaining stable model IDs separately. | data-selection.md |
| IMGUI-28 | Use a correct height/index strategy for wrapped variable rows instead of an invented uniform height. | data-selection.md |
| IMGUI-29 | Re-sort when application data/filter/view inputs change as well as when UI sort specs become dirty. | data-selection.md |
| IMGUI-30 | Include the valid range-source item in clipping and apply requests before and after item submission. | data-selection.md |
| IMGUI-31 | Use a real interactive item with navigation enabled and a visible focus state, then test keyboard activation. | core-interaction.md |
| IMGUI-32 | Check the local 1.93 stroke/signature changes and compare rendered integer/fractional shapes before changing offsets. | integration.md |
| IMGUI-33 | Apply the scalar text-edit/live-edit policy from the selected header rather than expecting every intermediate character to write. | core-interaction.md |
| IMGUI-34 | Use the pinned ImPlot header and its ImPlotSpec styling contract, not a historical snippet. | extensions-automation.md |
| IMGUI-35 | Identify StackLayout as fork-only and choose public composition or an explicit fork adoption. | extensions-automation.md |
| IMGUI-36 | Compare required behavior, current revisions, maintenance and internal coupling rather than stars or a wiki year. | extensions-automation.md |
| IMGUI-37 | Report headless scope/frame evidence only; run a renderer/capture for visual claims. | testing-debugging.md |
| IMGUI-38 | Inspect the engine's own terms and separate component licenses from core MIT. | extensions-automation.md |
| IMGUI-39 | Mark an unmerged API as proposed/branch-only and find a supported local alternative. | profile.md |
| IMGUI-40 | Compose a public interactive item and draw list instead of adding an unnecessary internal header. | core-interaction.md |

At the original review date, the supplied harnesses exercised API/frame/scope
paths and specific synthetic toggle/clipped-range scenarios. They did not
runtime-test every case above, the Test Engine, GPU pixels, physical DPI, IME,
docking or all extensions. Later execution is recorded in `validation.json`.

## Workflow and styling review, 2026-11-01

These additional author judgments supplement the original 40 prose acceptance
scenarios. Neither set is an independent model evaluation or a runtime suite.

| Request or risk | Response/action | Evidence or limit |
| --- | --- | --- |
| Build a new editor and its tests | Keep validation/commit independent; host the same drawing function in the app and UI test. | Shared settings panel: five model checks and two engine tests executed. |
| Save invalid data through a non-UI caller | Command rejects it without modifying committed data; a disabled button alone is insufficient. | Negative amount, empty name and unterminated-buffer rejection executed; disabled appearance not visually inspected. |
| Reskin a tool and change scale repeatedly | Use theme tokens and reconstruct from unscaled metrics; retain semantic IDs and interaction states. | Style snippet compiled; three reconstruction checks executed; no rendered baseline. |
| Custom drawn toggle fails ItemCheck | Checkable metadata is a separate contract; use built-in controls or click and assert model state. | Current engine/context and core internal declarations reviewed; no new custom metadata integration tested. |
| Async Save appears complete when merely queued | Wait for observable service completion, expose failure/retry and isolate test services. | Workflow guidance only; no service or persistence integration supplied. |
| Product requires screen readers or complex-script text | Assess actual stack support before promising accessibility or full internationalization. | Official toolkit scope reviewed; no accessibility certification. |
