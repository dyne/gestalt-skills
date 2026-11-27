---
name: clay-tui
description: "Design and build terminal UIs using Clay layout with libterm or termbox2. Use for split panes, responsive sidebars, keyboard and mouse navigation, multi-select lists, tree views, or porting Clay’s termbox2 renderer to libterm."
---

# Clay terminal interfaces

Start with a user action: “find two files in different folders, mark them, then review the batch.” Decide what the cursor points to, what Space changes, how to reach the review pane, and what survives a resize. Sketch the wide and narrow screens in terminal cells. Use [interaction and layout patterns](references/design.md) for focus, ranges, tree behavior and viewports.

**For a new libterm browser**, adapt the [working C11 starter](examples/browser.c). Clay divides the terminal into integer-cell panes. The application draws a tree and a detail view into those rectangles with native `lt_*` calls. It includes click-to-focus, keyboard navigation, fold/unfold, individual and range marking, scrolling and narrow-screen pane switching. Its small fixed ASCII dataset makes the interaction easy to change. [Build and exercise it](references/build.md).

**For an existing Clay render-command UI**, keep the renderer when the project needs Clay text, borders or images. The upstream termbox2 demo uses virtual pixels and has different input and build assumptions. Follow the [tested renderer port](references/renderer.md) before substituting libterm's compatibility header. For direct widget reuse, see the [termbox-widgets integration](references/widgets.md).

For each change:

1. Give rows stable IDs. Keep focus, marks, expansion, range anchor and viewport state in the application. Derive visible rows in display order.
2. Let Clay resolve dimensions. Use the same half-open cell rectangles to paint, clip and hit-test. Give each input event to one focus owner. Update the model, lay out, paint the back buffer, then present once.
3. Verify the user's action on a real terminal or PTY. Check the visible cursor, marked rows, redraw after shrinking and growing, and normal terminal restoration on exit. The [tmux check](examples/check_browser.py) exercises the starter and provides an example of asserting the resulting screen.
