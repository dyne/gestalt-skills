---
name: modern-imgui
description: "Design and test C++ Dear ImGui screens with Clay layouts and imgui-modern-kit (ImKit) widgets and themes. Use for responsive workspaces, panels, or changes to an existing ImGui interface."
---

# Modern ImGui

**Use Clay to arrange panes and ImKit to build what goes inside them.** ImKit runs on Dear ImGui, which handles input, focus, scrolling and rendering through the application's existing backends. When adding ImKit to a project, connect it to the host's compatible ImGui target. [ImKit setup](references/modern-kit.md)

1. **Shape the screen around the primary task.** Set the visual hierarchy, then adapt the panes to the available width. For a sidebar, editor and action bar, start with the [Clay workspace adapter](examples/clay_workspace.h). It gives each pane an ImGui child window. A single form or toolbar can use its component's own layout. [Layout example](references/clay-layout.md)
2. **Choose controls.** Use ImKit widgets and semantic tokens for emphasis, spacing and density. Fill gaps with public ImGui widgets. Keep selection and drafts in application state and give editors stable IDs so resizing or reordering preserves the active edit. [Component map](references/modern-kit-components.md) · [Themes](references/modern-kit-themes.md)
3. **Exercise one user journey.** For example, select a record, type into its editor, narrow the window and finish the edit. Check the saved value. Use the application's UI runner or the [headless harness](references/headless-testing.md). Check the real window for changes that depend on rendering or OS input.

For design feedback such as “quieter” or “distill,” see [styling](references/styling.md). For maintenance, see [tables and multi-selection](references/data-selection.md) · [Backends and docking](references/integration.md) · [Testing and debugging](references/testing-debugging.md)
