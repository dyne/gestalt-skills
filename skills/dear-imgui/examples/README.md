# Dear ImGui core examples

These twelve original examples target **Dear ImGui v1.93.0**. They demonstrate API contracts and application state ownership, and are intended to be adapted inside an existing Dear ImGui integration.

| Example | Main contract |
|---|---|
| `DrawWindowAndChild` | `Begin` and `BeginChild` always need matching ends |
| `DrawRecordRows` | Repeated labels scoped by persistent object identity |
| `DrawDynamicWindow` | A changing title with a stable `###` window ID |
| `DrawValidatedName` | Official `std::string` adapter and explicit live-edit policy |
| `DrawGainWithUndo` | One undo record per completed edit gesture |
| `DrawPropertyTable` | Tables and explicit cell entry |
| `DrawFilteredList` | Clip a precomputed dense view, keep persistent selection IDs |
| `DrawMultiSelect` | Both request phases, persistent storage IDs, unclipped range anchor |
| `DrawDeleteConfirmation` | Event-based open and explicit modal actions |
| `DrawToggle` | Public custom widget with keyboard navigation and focus visuals |
| `DrawDragDropRecord` | Copied handle payload and validated size |
| `DrawCommands` | Shortcut routing independent of whether the menu is open |

## Integration assumptions

Include `core_patterns.h` and compile `core_patterns.cpp` in the host application. The existing Dear ImGui checkout must also provide the official `misc/cpp/imgui_stdlib.cpp` adapter used by the text-input examples. Call drawing functions between `NewFrame()` and `Render()`; functions that do not create their own window belong within an existing window scope. Use an additional `PushID` scope when the same helper appears more than once in one parent.

The sample record IDs are stable positive `int` values. The filtered and multi-select views contain valid pointers for the duration of drawing; changing vector storage or deleting objects requires rebuilding those pointers. Names in the fixed-height selection examples are single-line. The selection sample deliberately separates view indices from object IDs, but the host must define anchor/focus behavior when a view is reordered, filtered or deleted during an active selection gesture. It is not a full selection controller.

The undo sample covers a completed visible widget gesture. Use separate `GainEdit` state for each simultaneously submitted logical editor. The host must finalize or cancel a pending edit when the object or panel disappears. `DrawValidatedName` controls when typed text reaches the backing string; it does not validate application-specific naming rules. The custom toggle reports an edit using its return value; it does not attempt to emulate every internal edit-marking behavior of a built-in value widget. Its caller should provide a visible label.

`DrawDeleteConfirmation` returns application intent so model deletion can happen at a safe point outside iteration. A real application should identify the object being confirmed and hold that identity stable while the dialog is open. It should not simply act on whatever selection happens to exist later.

## Headless smoke exercise

`smoke_main.cpp` uses Dear ImGui's official `imgui_impl_null` backend to submit eight frames, exercise the helpers, collapse/reopen a window and open a modal. It disables ini file loading/saving. This is a context/frame/scope/API smoke check. It does **not** inject clicks or key events, validate undo or selection behavior, inspect pixels, or exercise a GPU renderer.

For a local checkout of the stated release, one compile/run command is:

```sh
imgui_source=/absolute/path/to/imgui
c++ -std=c++17 -O1 -g -Wall -Wextra -Wpedantic \
  -DIMGUI_DISABLE_OBSOLETE_FUNCTIONS \
  -I"$imgui_source" -I"$imgui_source/backends" \
  core_patterns.cpp smoke_main.cpp \
  "$imgui_source/imgui.cpp" "$imgui_source/imgui_draw.cpp" \
  "$imgui_source/imgui_widgets.cpp" "$imgui_source/imgui_tables.cpp" \
  "$imgui_source/misc/cpp/imgui_stdlib.cpp" \
  "$imgui_source/backends/imgui_impl_null.cpp" \
  -o imgui_core_smoke
./imgui_core_smoke
```

Expected output:

```text
PASS: 8 headless frames; no graphics or interaction validation.
```

The actual research validation compiled these examples against the fetched v1.93.0 sources with obsolete APIs disabled and executed this null-backend smoke exercise successfully. Real usage still needs the relevant interactive and rendering checks described in the dossier.

## Targeted semantic checks

`semantic_main.cpp` adds two narrow behavioral checks with synthetic input through the same null backend. It activates `DrawToggle` with a mouse press/release, then selects the second row in a 101-item list and uses Shift+End to select the remaining 100 rows through the clipped multi-select view. It verifies the persistent application IDs in selection storage, including exclusion of the first row. The range source starts at a nonzero index and must remain correctly handled when navigation scrolls toward the final row.

Compile it with the same command above, replacing `smoke_main.cpp` with `semantic_main.cpp` and choosing a different output executable. The recorded result is:

```text
PASS: mouse toggle; stable selection ID; Shift+End selects 100 rows from a nonzero anchor.
No GPU, pixel, docking or real-platform input validation.
```

These checks passed against v1.93.0 with obsolete APIs disabled. They validate these specific synthetic-input scenarios, not the complete behavior of every example. In particular, they do not validate the undo helper, changing selection views, real keyboard layouts, OS input delivery, visual appearance or GPU rendering.

## Primary references

- [Public API and comments](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h)
- [Executable demo patterns](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp)
- [Official stdlib adapter](https://github.com/ocornut/imgui/blob/v1.93.0/misc/cpp/imgui_stdlib.cpp)
- [Official null backend](https://github.com/ocornut/imgui/blob/v1.93.0/backends/imgui_impl_null.cpp)
- [Multi-select tutorial](https://github.com/ocornut/imgui/wiki/Multi-Select)
- [Custom widget guidance](https://github.com/ocornut/imgui/issues/2992)
