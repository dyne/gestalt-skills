# Modern Kit adoption scenario review

Author walkthrough, 2026-11-15, against ImKit commit
`986d8d286a74fb7b2f724b9ef5d008af139aa887` and the revised skill.
These are review scenarios, not executed UI tests or an independent model
evaluation. Original core/runtime evidence in `validation.json` is unchanged
and does not certify Modern Kit. References below are under `references/`.

| Prompt / risk | Expected decision or action | Guidance |
| --- | --- | --- |
| Build settings in an app already linking compatible ImKit | Prefer setting rows, toggle rows, inspector cards and semantic actions; apply requests to host drafts/commands. | modern-kit.md; modern-kit-components.md |
| Build a control covered by ImKit, but only a nearby checkout exists | Verify build/include integration first; consider adoption only within dependency scope. | modern-kit.md |
| ImKit is absent and a backend-only bug needs fixing | Fix the backend without adding a UI dependency. | SKILL.md task routing; modern-kit.md |
| Host uses the skill's core v1.93.0 baseline | Identify the different required docking commit; do not bypass guards or silently upgrade. | modern-kit.md; profile.md |
| Need advanced plotting beyond compact charts | State the missing capability and retain/select a suitable plotting extension. | modern-kit-components.md |
| Theme picker selection disappears on restart | Persist stable preset ID in host settings; resolve with fallback and apply outside the frame. | modern-kit-themes.md |
| Theme update erases manual ImGuiStyle changes or doubles scale | Edit semantic/layout tokens, ResolveTheme, use one unscaled baseline and explicit host UI scale. | modern-kit-themes.md |
| Skin/shadow does not reach a component | Pass the Theme through ComponentOptions and preserve borrowed skin lifetime. | modern-kit-themes.md |
| Reload a theme after deleting a key | Parse into a fresh base, inspect warnings, keep file I/O and nonserialized assets in the host. | modern-kit-themes.md |
| False Begin return for card versus setting row | Always end card/inspector scopes; conditionally end setting/collapsible inspector rows. | modern-kit-components.md |
| Combo undo relies only on IsItemEdited | Use the wrapper's change return; test the actual host transaction. | modern-kit-components.md |
| Node drag overflows or races an external model edit | Consume whole operation batches, validate revision, preview drafts, atomically commit or reject; handle terminal retry. | modern-kit-components.md |
| Large table or tree redraw scans every record | Host maintains flattened visible index and bounds provider calls to clipped ranges. | modern-kit-components.md |
| Loading toast never disappears after successful work | Host updates the same ID to terminal/message state and handles expiry/removal events; avoid double time advancement. | modern-kit-components.md |
| Icons missing after renderer/context replacement | Rebind the host atlas textures per renderer/context; keep textures through draw consumption. | modern-kit-themes.md |
| User asks for screen-reader, RTL or physical camera acceptance | Distinguish partial semantic/pseudo-RTL/simulated coverage from actual platform/device tests. | modern-kit.md; modern-kit-themes.md |

Review outcome: the skill states a conditional preference, explicit fallback,
source/version checks, architecture and state ownership, theme/asset lifetime,
component discovery and adoption-specific verification. No runtime, visual,
hardware or installed-skill adoption result is implied by this author review.

Source cross-checks resolved details that overview prose can obscure:
`BeginPin` returns void and always needs `EndPin`; `ThemePicker` writes through
a host preset pointer and returns bool changed; window chrome entry points are
`LayoutWindowFrame`/`DrawWindowFrame`; `cmake/imkitNodeEditor.cmake` adds the
node target to the editor-suite aggregate. Prefer these declarations over
conceptual component names when implementing a consumer.
