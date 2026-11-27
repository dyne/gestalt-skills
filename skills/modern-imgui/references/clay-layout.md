# Responsive workspace layout with Clay

Use Clay when several regions must resize together. A project browser can put
navigation beside the document on a wide window, move it above the document on a
narrow window and reserve one action row below both. Editing a field should survive
that change. The adapter in `examples/clay_workspace.h` expresses this
as one Clay tree and submits ordinary Dear ImGui or ImKit widgets in each region.

For a form, use ImGui's normal flow and tables. For a toolbar or tab strip, first
check the existing [ImKit components](modern-kit-components.md). For panes the user
can undock or rearrange, give ImGui docking ownership of the window arrangement.
A Clay workspace can live inside a docked window and use its available space.

## Use the adapter

Compile the Clay implementation once in the program. Initialize a Clay context
with `Clay_MinMemorySize`, `Clay_CreateArenaWithCapacityAndMemory` and
`Clay_Initialize`. Keep the arena allocated at the same address for the lifetime
of the context. The runnable check in `examples/clay_workspace_check.cpp`
includes initialization and an error handler.

Call the adapter inside a visible ImGui window, after any heading or toolbar.
In this example, the tree and compact picker share the application's project
selection. The document callback submits the same editor at either width.

```cpp
modern_imgui_examples::DrawClayWorkspace("project", *layout,
    [&] (bool sidebar) {
        if (sidebar) DrawProjectTree(projects, selection);
        else DrawProjectPicker(projects, selection);
    },
    [&] { DrawDocumentEditor(selection, edit_buffer); },
    [&] { if (ImGui::Button("Apply")) ApplyChanges(selection, edit_buffer); });
```

The adapter switches at 40 font heights, sizes the sidebar to 12 font heights
and uses the current frame height for each compact strip. In a very short host it
gives the document the full area. These are example design choices. If a hidden
action is essential, expose it in the host menu or through a shortcut. If an
editor can disappear, decide when to commit or retain its draft in application state.

## Keep geometry and interaction consistent

- Measure from `GetContentRegionAvail()` and anchor Clay's local boxes to
  `GetCursorScreenPos()`. Both use ImGui logical coordinates, including inside
  a moved or scrolled host. Add the origin once. Framebuffer scale belongs to
  the renderer. Round shared edges consistently and skip collapsed rectangles
  before calling `BeginChild`, where a zero dimension means “use available space.”
- Use an idle Clay context for each layout pass. Set its dimensions, declare the
  tree between `Clay_BeginLayout` and `Clay_EndLayout`, then copy each named
  pane's bounding box. The adapter restores the previous Clay context before
  invoking application widgets. Pane geometry alone requires no Clay renderer,
  text measurement callback or pointer-event forwarding.
- Give each workspace instance a stable ImGui ID. Keep each child's name and the
  editor's ID path stable through reflow. Call `EndChild` even when `BeginChild`
  returns false. Native children handle clipping, wheel input and keyboard
  navigation. Scope repeated widget labels by the persistent record ID as usual.
  For a long tree or document list, apply clipping *inside* its pane.

## Reproduce the interaction check

Use a C11 compiler and C++20 compiler. Set `CLAY` and `IMGUI` to the absolute
paths of the source checkouts and `SKILL` to the installed modern-imgui directory.
Run in a temporary build directory with the tested [Clay revision](https://github.com/nicbarker/clay/tree/e6cc36941ab2af5d81107617039d6f527a1c660b)
and [Dear ImGui revision](https://github.com/ocornut/imgui/tree/c1aaac65e896a45f81f47a4d68f9959e0f86c859).

```sh
cc -std=c11 -DCLAY_IMPLEMENTATION -x c -c "$CLAY/clay.h" -o clay.o
c++ -std=c++20 -I"$CLAY" -I"$IMGUI" -I"$IMGUI/backends" \
  "$SKILL/examples/clay_workspace_check.cpp" "$IMGUI/imgui.cpp" \
  "$IMGUI/imgui_draw.cpp" "$IMGUI/imgui_widgets.cpp" "$IMGUI/imgui_tables.cpp" \
  "$IMGUI/backends/imgui_impl_null.cpp" clay.o -lm -o workspace-check
./workspace-check
```

The check clicks a checkbox in an offset host, types into the same active editor
before and after a resize, and scrolls a long document while its neighbors stay
still. For [ImKit](modern-kit.md), build the same check with `CHECK_IMKIT`, link
`imkit::imkit` and use the matching ImGui host and null backend. This exercises
an ImKit checkbox through the same adapter. The null backend covers interaction
and pane positions. Inspect font scaling, visual clipping and platform viewports
in the application's real renderer when those matter to the design.
