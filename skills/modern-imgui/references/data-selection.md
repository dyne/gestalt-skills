# Tables, large views and selection

Baseline: v1.93.0, checked 2026-10-31; multi-select APIs arrived in 1.91.

Use Tables for new tabular layouts; do not mechanically rewrite valid legacy
Columns during a small fix. Check `BeginTable` before submitting or ending it.
Configure columns, then enter each row/cell explicitly. Skip expensive content
for nonvisible columns when supported by the table API. Keep table identity and
settings stable; preserve user resize/order/visibility choices unless the task
requires resetting them.

Model identity, view order, widget identity and selection storage are separate.
Build a dense filtered/sorted view when its inputs change, then run the clipper
over that view's indices. Filtering after clipping the full model breaks index
and row-count assumptions. Re-sort on application data/filter changes as well
as dirty table sort specifications; the latter only describe UI sort changes.
Do not retain pointers invalidated by vector growth or deletion.

`ImGuiListClipper` needs a valid height strategy. Uniform single-line rows can
use the normal fixed-height path; arbitrary wrapped/variable-height rows cannot
be made correct by guessing an average height. Use a height-aware indexing
strategy or a suitable view design. Retain text offsets for large log buffers
when appropriate, and distinguish expensive filtering/model work from the cost
of submitting visible rows.

## Multi-select request flow

Keep persistent selection in application storage keyed by stable object IDs.
Use the dense view's indices as range coordinates, with an explicit mapping to
storage IDs. Follow the matching demo's request protocol:

1. `BeginMultiSelect` with the intended flags/counts; apply its initial requests.
2. Build the clipper over view indices and include a valid `RangeSrcItem` using
   `IncludeItemByIndex`, so an offscreen anchor is submitted when required.
3. Set `SetNextItemSelectionUserData` before each selection item and render its
   selected state from application storage.
4. `EndMultiSelect` and apply the resulting requests too.

Skipping either request phase, mixing persistent IDs with range indices, or
clipping away the range source breaks interactions that simple mouse tests may
miss. If using `ImGuiSelectionBasicStorage`, set its view adapter/UserData only
for a valid view lifetime. Define what happens to anchor/focus when filtering,
reordering or deleting records during an active gesture; the supplied examples
assume a stable view for that gesture and are not a full selection controller.

Verify sorted and renamed records, insertion/removal, a filtered view, a range
anchor outside the viewport, keyboard range navigation and empty data. The
supplied semantic harness tests a nonzero anchor and Shift+End across a clipped
101-record view; it does not establish every dynamic-view policy.

Sources: [table and selection demo](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp),
[public selection contracts](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[multi-select guide](https://github.com/ocornut/imgui/wiki/Multi-Select).
