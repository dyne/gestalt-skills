# Build a GUI that can be tested

Use this workflow for a new panel or a substantial interaction. For a local
fix, apply only the affected steps. Backend setup remains in [integration](integration.md);
widget contracts in [core interaction](core-interaction.md).

## Define behavior before widgets

Write one concrete journey with initial state, action and observable result.
For example: edit a record, reject invalid input, Save once, reopen the saved
value; Cancel restores the original without writing. Decide when changes are
live, staged, committed, persisted and undoable. Distinguish an in-memory
commit from successful disk/network persistence. Specify relevant empty,
loading, unavailable, error and recovery states, plus keyboard/focus behavior.
Choose minimum usable sizes and the required theme, fonts and DPI range.

## Keep the rendering boundary small

| State or operation | Owner and test seam |
| --- | --- |
| Records, validation, commands and undo | Application/model functions callable without an ImGui context |
| Drafts, validation messages, selection and popup intent | Explicit panel state retained across frames, scoped to the edited object |
| Widget submission and item events | A drawing function used by both the app and its UI tests |
| Disk/network/worker effects | Existing service boundary; controllable result/completion in tests |
| Theme, fonts, textures and backend lifecycle | Host integration with separate visual/platform checks |

Small tools can pass structs and call ordinary functions; no mandatory view
model hierarchy or dependency injection framework. Avoid mutable static panel
state and business rules hidden exclusively inside widget conditionals. Drawing
the same frame again must not repeat a Save/delete request. Issue work from the
activation event; report completion back to owned state. Synchronize worker
results before the UI reads them, keep the context on its owner thread, and
define pending/duplicate/cancel behavior when asynchronous effects matter.

Keep identity independent of display text, theme and current row index. Use
stable `###` IDs and model-key scopes; give repeated panel instances their own
window/parent identity. Expose visible labels, focus and activation states even
when icons or custom painting are used. Reuse built-in interactive items where
possible. A theme change should not require rewriting semantic test paths.

## Implement one complete journey, then test its boundaries

1. Implement and exercise validation/commands independently. A disabled Save
   button communicates validity; the command must still reject invalid data.
2. Draw the real panel against that model and retained draft. Balance scopes,
   use available-size layout, and preserve the selected identity through
   filtering or reopening. Add [styling](styling.md) through an owned theme and
   scoped overrides while retaining interaction contracts.
3. Drive **the same drawing function** through the [Test Engine](automation.md).
   `GuiFunc` can host that function; avoid a copied test-only version of the
   production panel. An existing running app can instead use only `TestFunc`.
   Seed models through setup seams, then perform the behavior under test through
   UI actions. Assert the committed model or service result, not only the draft.
4. Use deterministic fixtures: fresh panel/model state, isolated ini/settings,
   controlled data/services/time, known window geometry and bounded waits for
   observable completion. Never overwrite a user's real settings or records.
   Release held workers/resources on failure. Include relevant invalid/cancel,
   keyboard, reopen, duplicate-action and service-error paths; do not test every
   matrix combination for a cosmetic edit.
5. Compile and run the selected tests with intended identities/counts, failure
   propagation and reports. Inspect rendered output for styling/layout changes;
   exercise actual platform focus/IME/DPI/window behavior where required.
   Report each evidence layer and remaining gaps separately.

## Worked slice and limits

`examples/settings_panel.h` contains context-free validation and commit logic;
`settings_panel.cpp` draws a reusable staged editor. `settings_model_main.cpp`
checks model acceptance/rejection without ImGui. `automation_main.cpp` hosts
that panel and checks edits, commit, keyboard Save and Cancel against its model.
The command only stores in memory: persistence, undo, service failures and
multi-editor conflicts remain application responsibilities. Initializing the
draft from a changed record, and resolving external edits while it is dirty,
also require an explicit host policy.

Keyboard support does not establish screen-reader accessibility. Core lacks
full accessibility and complex text shaping/RTL support; assess these product
requirements before committing to the stack. A compile or headless interaction
test cannot establish usability or visual quality.

Sources: [core model/identity contracts](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md),
[current toolkit scope](https://github.com/ocornut/imgui#the-pitch),
[official automation integration](https://github.com/ocornut/imgui_test_engine/wiki/Setting-Up).
