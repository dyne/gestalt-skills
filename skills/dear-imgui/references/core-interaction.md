# Core contracts and interaction

Research baseline: v1.93.0, checked 2026-10-31. Resolve flags/signatures in the
project's header before adapting these rules to another version.

## Identity and scopes

Application code owns model values, buffers and selection; ImGui retains focus,
active IDs, window placement and other interaction state. Submit UI during a
valid frame without rebuilding the application model each frame. Use persistent
object IDs for repeated labels. Row indices change under sorting/filtering;
addresses change when containers move. Either is an ID only if its lifetime and
identity actually match the widget contract.

`Visible##suffix` hides the suffix but uses the full label in identity;
`Changing title###stable` keeps identity independent of its visible prefix.
Use explicit `PushID`/`PopID` scopes around repeated controls, including multiple
instances of one helper. Keep window and popup identities stable across frames.

| Open operation | Close policy |
| --- | --- |
| `Begin`, `BeginChild` | Always `End` / `EndChild`, even when false |
| `BeginTable`, menu/bar, popup/modal, tab bar/item, combo, drag/drop source/target | End only if the corresponding begin succeeds |
| `TreeNode[Ex]` | `TreePop` on true unless `NoTreePushOnOpen` |
| `CollapsingHeader` | No `TreePop` |
| `BeginGroup`, `BeginDisabled`, `BeginMultiSelect` | Always their matching end |
| `Push*` stacks | Pop exactly what was pushed, including early exits |

`BeginDisabled(false)` still opens a scope, and cannot re-enable an enclosing
disabled region. A `Leaf` tree node does not imply `NoTreePushOnOpen`. Read the
exact contract for new API families instead of generalizing all `Begin*` calls.

## Editing, text and actions

Keep pending text separate from committed model values when validation/cancel is
part of the UX. Use `misc/cpp/imgui_stdlib.h` plus its implementation for mutable
`std::string` input, or a correctly sized mutable buffer; never cast `c_str()`.
Use `TextUnformatted(begin, end)` or a fixed format for external text; treating
user/log text as a format string is unsafe.

Query activation/edit/deactivation immediately after the relevant item. For one
undo operation per gesture, retain the before-value at activation and commit on
the intended completed edit, often `IsItemDeactivatedAfterEdit()`. Explicitly
finalize/cancel when the object or panel disappears; a missing widget cannot
deliver its usual final item event. Keep edit state per logical editor.
Since 1.92.9, scalar text entry does not live-write every intermediate value by
default; distinguish its return/change policy from a drag. Inspect
`ImGuiItemFlags_LiveEditOnInputText` and local comments before changing it.

`MenuItem` shortcut text is display-only. Register an actual routed `Shortcut`
in the intended focus scope even when the menu is closed. Match `OpenPopup`
and popup submission's effective ID scope; open from an event once, then submit
contents while open. Reopening every frame prevents normal dismissal. Hold the
confirmed object ID stable, and apply destructive model changes at a safe point.
Drag/drop payloads are copied bytes: use a stable handle or owned serializable
value, validate type/size on acceptance, and resolve the delivered handle safely.
Copying a pointer or `std::string` object representation does not transfer its
referent's lifetime.

## Layout and custom widgets

Use layout cursor, groups, children, tables and available content size before
manual placement. Window-local cursor positions and screen-space draw-list
coordinates are different; test moved/scrolled/docked windows. Set next-window
defaults before `Begin`, generally with first-use conditions when preserving user
placement. Size controls using font/frame/style metrics and meaningful width
constraints rather than fixed display pixels.

Prefer a public interactive item plus draw-list rendering for a custom widget:
an `InvisibleButton` can establish hit area, layout and item state; configure
keyboard navigation (including `EnableNav` where supported) and visible focus.
A painted rectangle alone is not an interactive/navigation-aware control.
Do not include `imgui_internal.h` simply to position or draw a shape. Isolate a
necessary internal dependency and pin/test it explicitly.

Sources: matching [header](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[demo](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp),
[FAQ](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md), and
[custom-widget guidance](https://github.com/ocornut/imgui/issues/2992).
