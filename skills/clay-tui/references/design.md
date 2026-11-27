# Design the screen in cells

## A split that still works at 30 columns

A tree/detail browser has two jobs: locating an item and inspecting it or the marked set. Try the following arrangement, then choose widths for the actual labels and actions.

```text
> Files                    Details
  [ ] - Workspace          Item: layout.c
  [ ]   - Sources          Marked: 2
  [x]       app.c          app.c
> [x]       layout.c       layout.c
  [ ]   + Tests
Arrows move/fold | Space mark | v range | Tab details | q quit
```

The first `>` in a heading identifies the pane receiving keys. The row marker and reverse-video style identify the cursor. A checkbox marks batch membership. Preserve all three meanings in monochrome and while focus is in another pane.

- **Wide.** Use a vertical Clay root containing a growing horizontal body and a one-row footer. In the body, give the sidebar a fixed or bounded width, a one-cell gap and the detail pane the remaining columns. Each pane owns its heading and viewport. The starter switches to two panes at 50 columns: 25 for files, one gap and at least 24 for details.
- **Adjustable splits.** Store a preferred ratio or width. Given body width `W`, gap `g`, and the two minimums, single-pane mode starts when `W < leftMin + g + rightMin`. Otherwise clamp the requested left width to `[leftMin, W - g - rightMin]` and give the right pane the remainder. For stacked panes apply the same rule to heights. Hit-test a draggable divider in its rendered gap. Preserve the preference across temporary narrow layouts.
- **Narrow.** Show the focused pane full width. Tab or an explicit Open/Back command changes panes and preserves each pane's cursor and offset. At very low height, give the current pane the last row before reserving chrome. Clip or abbreviate the hint line; keep the most important action discoverable in help. Include an empty-folder and a no-results state with a way back.
- **Screens and overlays.** Keep a navigation stack for list → detail → editor flows. A stack entry can hold the screen ID, filter, cursor ID and first visible row. Pop and restore it on Back. Capture the previous focus owner when opening a modal. Send Escape, Enter and pointer events to the modal until it closes, then restore the previous owner if it still exists.

## Model selection explicitly

| Gesture | State change |
| --- | --- |
| Up / Down | Move the cursor by one *visible* row. Preserve marks. Home / End and Page Up / Down can use the same operation with the first, last or viewport-sized step. |
| Space | Toggle the cursor ID in the marked set. Decide explicitly whether the cursor advances. Show the marked count and use marked IDs as batch-action input. |
| Range | Record an anchor ID. The starter uses `v`, movement, then `v` to add the inclusive visible interval. Escape cancels the pending anchor. For live Shift+arrow ranges, snapshot the baseline set at gesture start and recompute against that snapshot on every move so reversing direction shrinks the range. Provide an unmodified-key route on terminals that cannot report Shift. |
| Right / Left | Right expands a closed branch or enters the first child of an open one. Left collapses an open branch or moves to its parent. Leaves accept Left and ignore Right. |
| Click | Resolve the pane, subtract the content origin, then add its viewport offset. Reject the header, footer, gap and blank rows. If a checkbox or disclosure icon has its own action, test its cell span before the generic row action. |
| Filter, refresh or collapse | Rebuild visible IDs. Keep the cursor on its surviving ID, otherwise select a visible ancestor or nearest surviving neighbor. Remove marks for deleted IDs. The starter retains marks on hidden descendants and lists them in Details. Show the scope before a bulk action. Cancel or rebase an anchor that no longer appears. |

Plain mouse motion, button release and key release can arrive separately. Route movement repeats to navigation. Treat a one-shot operation such as toggling a mark as one press on protocols that report repeats. Legacy protocols can send repeated press events without identifying them.

## Scroll and hit-test the rendered rows

Keep `cursorId`, `expandedIds`, `markedIds`, and `firstVisible` separate. Build a preorder projection by visiting children only under expanded ancestors. A display row needs its ID, depth and branch state. Deep indentation consumes label width; cap it or switch to a breadcrumb/detail view when the remaining label area vanishes.

For one-cell rows and capacity `H > 0`, if cursor index `i` is above `first`, set `first = i`. If it is below the last visible row, set `first = i - H + 1`. Clamp to `[0, max(0, count - H)]`. Draw at most `H` items. For `count == 0` or `H == 0`, skip row lookup and movement. Recompute after resize, collapse, changes in filtering or changes in footer height. Wheel scrolling may move the viewport independently; choose whether the next keyboard move brings the cursor back into view. For wrapped or variable-height rows, map screen offsets to measured line spans rather than indexing one item per line.

The starter passes Clay a width and height measured in cells and reads pane bounds after `Clay_EndLayout(0.0f)`. Round shared left/right and top/bottom **edges** once. A point is inside when `left <= x < right` and `top <= y < bottom`. For nested views intersect child, ancestor clips and screen bounds. Derive pointer hits from this same geometry and the same visible projection used for the presented frame. For long trees, emit only visible rows to the cell buffer. Cache the projection when profiling justifies it and invalidate it on data, expansion or filter changes.

## Text and color

The starter's one-byte paint loop is for its ASCII fixtures. For arbitrary labels, segment UTF-8 into printable grapheme clusters and compute the terminal cell width with the same policy for measuring, painting, clipping and mouse-column mapping. A Clay string slice has an explicit byte length; it can end without a NUL. Bound decoding by that length, consume malformed bytes with a replacement glyph, and give control characters a visible representation. Never split a two-cell glyph across the edge or place a cursor on its continuation cell. Reserve the ellipsis width before truncating.

Libterm's `lt_print` handles wide codepoints and skips zero-width combining marks. Use `lt_set_cell_ex` for a multi-codepoint cell when the base and marks must be preserved. Terminal/font policy for ambiguous width and emoji can differ: test representative labels such as `界`, a decomposed accented letter and a joined emoji. In normal color mode use symbolic colors and foreground styles. For richer palettes select a corresponding output mode first. Explicit black and terminal-default color use different encodings. Keep focus and marking distinguishable when colors are unavailable.
