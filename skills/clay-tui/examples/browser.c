/* C11. Clay computes cell rectangles; libterm paints and delivers events. */
#define CLAY_IMPLEMENTATION
#include "clay.h"
#include <libterm/libterm.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

/* Immutable fixture in preorder. Each index is a stable node ID, even when
   its row disappears. For mutable data use IDs independent of storage order. */
static const struct { int parent; const char *label; } nodes[] = {
    {-1, "Workspace"}, {0, "Sources"}, {1, "app.c"}, {1, "layout.c"},
    {0, "Tests"}, {4, "input.c"}, {4, "layout_test.c"}, {0, "README.md"},
    {-1, "Archive"}, {8, "Earlier build"}
};
enum { COUNT = sizeof nodes / sizeof nodes[0] };
typedef struct { int x, y, w, h; } Rect;
typedef struct { Rect tree, detail, footer; } Panes;
typedef struct {
    int cursor, anchor, first, detail_first;
    bool detail_focus, open[COUNT], marked[COUNT];
} Browser;
typedef struct { int ids[COUNT], count, current; } Rows;

static int clamp(int n, int lo, int hi) {
    return n < lo ? lo : n > hi ? hi : n;
}

static bool branch(int id) {
    return id + 1 < COUNT && nodes[id + 1].parent == id;
}

static Rows visible(const Browser *b) {
    Rows rows = {0};
    bool shown[COUNT];
    for (int id = 0; id < COUNT; ++id) {
        int p = nodes[id].parent;
        shown[id] = p < 0 || (shown[p] && b->open[p]);
        if (shown[id]) {
            if (id == b->cursor) rows.current = rows.count;
            rows.ids[rows.count++] = id;
        }
    }
    return rows;
}

static void mark_range(Browser *b, Rows rows) {
    for (int i = 0; i < rows.count; ++i) {
        if (rows.ids[i] != b->anchor) continue;
        int lo = i < rows.current ? i : rows.current;
        int hi = i > rows.current ? i : rows.current;
        for (int j = lo; j <= hi; ++j) b->marked[rows.ids[j]] = true;
        b->anchor = -1;
        return;
    }
    b->anchor = b->cursor;
}

static Rect bounds(Clay_ElementId id) {
    Clay_ElementData data = Clay_GetElementData(id);
    if (!data.found) return (Rect){0};
    Clay_BoundingBox box = data.boundingBox;
    int x = (int)(box.x + 0.5f), y = (int)(box.y + 0.5f);
    int right = (int)(box.x + box.width + 0.5f);
    int bottom = (int)(box.y + box.height + 0.5f);
    return (Rect){x, y, right - x, bottom - y};
}

static Panes layout(int width, int height, bool detail_focus) {
    bool split = width >= 50;
    Clay_SetLayoutDimensions((Clay_Dimensions){(float)width, (float)height});
    Clay_BeginLayout();
    CLAY(CLAY_ID("screen"), {.layout = {.layoutDirection = CLAY_TOP_TO_BOTTOM,
              .sizing = {CLAY_SIZING_GROW(0), CLAY_SIZING_GROW(0)}}}) {
        CLAY(CLAY_ID("body"), {.layout = {.childGap = split ? 1 : 0,
                  .sizing = {CLAY_SIZING_GROW(0), CLAY_SIZING_GROW(0)}}}) {
            if (split || !detail_focus) {
                Clay_SizingAxis sidebar = split ? CLAY_SIZING_FIXED(25) : CLAY_SIZING_GROW(0);
                CLAY(CLAY_ID("tree"), {.layout = {.sizing = {sidebar, CLAY_SIZING_GROW(0)}}}) {}
            }
            if (split || detail_focus) {
                CLAY(CLAY_ID("detail"), {.layout = {
                    .sizing = {CLAY_SIZING_GROW(0), CLAY_SIZING_GROW(0)}}}) {}
            }
        }
        if (height >= 3) {
            CLAY(CLAY_ID("footer"), {.layout = {
                .sizing = {CLAY_SIZING_GROW(0), CLAY_SIZING_FIXED(1)}}}) {}
        }
    }
    (void)Clay_EndLayout(0.0f); /* No animations; widgets paint their own bounds. */
    Panes p = {0};
    if (split || !detail_focus) p.tree = bounds(CLAY_ID("tree"));
    if (split || detail_focus) p.detail = bounds(CLAY_ID("detail"));
    if (height >= 3) p.footer = bounds(CLAY_ID("footer"));
    return p;
}

/* All fixture labels are ASCII, one byte per cell. Pads the whole row so
   shorter labels and full-row focus styles render consistently. */
static void line(Rect pane, int row, const char *s, lt_attr style) {
    if (row < 0 || row >= pane.h) return;
    for (int col = 0; col < pane.w; ++col) {
        unsigned char ch = *s ? (unsigned char)*s++ : ' ';
        lt_set_cell(pane.x + col, pane.y + row, ch, style, LT_DEFAULT);
    }
}

static int marked_count(const Browser *b) {
    int count = 0;
    for (int i = 0; i < COUNT; ++i) count += b->marked[i];
    return count;
}

static void paint(Browser *b, Panes p) {
    char buf[128];
    Rows rows = visible(b);
    int capacity = p.tree.h > 1 ? p.tree.h - 1 : 0;
    if (capacity > 0) {
        b->first = clamp(b->first, rows.current - capacity + 1, rows.current);
        b->first = clamp(b->first, 0, rows.count > capacity ? rows.count - capacity : 0);
    }
    line(p.tree, 0, b->detail_focus ? "  Files" : "> Files", LT_BOLD);
    for (int r = 0; r < capacity && b->first + r < rows.count; ++r) {
        int id = rows.ids[b->first + r], depth = 0;
        for (int parent = nodes[id].parent; parent >= 0; parent = nodes[parent].parent) ++depth;
        char disclosure = branch(id) ? (b->open[id] ? '-' : '+') : ' ';
        snprintf(buf, sizeof buf, "%c [%c] %*s%c %s", id == b->cursor ? '>' : ' ',
                 b->marked[id] ? 'x' : ' ', depth * 2, "", disclosure, nodes[id].label);
        line(p.tree, r + 1, buf, id == b->cursor && !b->detail_focus ? LT_REVERSE : LT_DEFAULT);
    }
    line(p.detail, 0, b->detail_focus ? "> Details" : "  Details", LT_BOLD);
    snprintf(buf, sizeof buf, "Item: %s", nodes[b->cursor].label);
    line(p.detail, 1, buf, LT_DEFAULT);
    int n = marked_count(b);
    snprintf(buf, sizeof buf, "Marked: %d", n);
    line(p.detail, 2, buf, LT_BOLD);
    int slots = p.detail.h > 3 ? p.detail.h - 3 : 0;
    b->detail_first = clamp(b->detail_first, 0, n > slots ? n - slots : 0);
    int seen = 0;
    for (int id = 0; id < COUNT; ++id) {
        if (b->marked[id] && seen++ >= b->detail_first)
            line(p.detail, 3 + seen - b->detail_first - 1, nodes[id].label, LT_DEFAULT);
    }
    const char *keys = b->detail_focus ? "Up/Down scroll | Tab files | q quit" :
        "Arrows move/fold | Space mark | v range | Tab details | q quit";
    if (p.footer.w < 62)
        keys = b->detail_focus ? "Tab files | q quit" : "Spc mark  v range  Tab  q quit";
    if (b->anchor >= 0) {
        snprintf(buf, sizeof buf, "v apply | Esc cancel | From %s", nodes[b->anchor].label);
        keys = buf;
    }
    line(p.footer, 0, keys, LT_REVERSE);
}

static bool inside(Rect r, int x, int y) {
    return x >= r.x && y >= r.y && x < r.x + r.w && y < r.y + r.h;
}

static bool handle(Browser *b, Panes p, struct lt_event ev) {
    Rows rows = visible(b);
    if (ev.type == LT_EVENT_MOUSE && ev.key == LT_KEY_MOUSE_LEFT && !(ev.mod & LT_MOD_MOTION)) {
        if (inside(p.tree, ev.x, ev.y)) {
            b->detail_focus = false;
            int row = ev.y - p.tree.y - 1 + b->first;
            if (ev.y > p.tree.y && row < rows.count) b->cursor = rows.ids[row];
        } else if (inside(p.detail, ev.x, ev.y)) {
            b->detail_focus = true;
            b->anchor = -1;
        }
        return true;
    }
    if (ev.type != LT_EVENT_KEY || ev.action == LT_KEY_RELEASE) return true;
    bool arrow = ev.key == LT_KEY_ARROW_UP || ev.key == LT_KEY_ARROW_DOWN ||
                 ev.key == LT_KEY_ARROW_LEFT || ev.key == LT_KEY_ARROW_RIGHT;
    if (ev.action == LT_KEY_REPEAT && !arrow) return true;
    if (ev.ch == 'q' || ev.key == LT_KEY_CTRL_C || (ev.ch == 'c' && (ev.mod & LT_MOD_CTRL))) return false;
    if (ev.key == LT_KEY_TAB) {
        b->detail_focus = !b->detail_focus;
        b->anchor = -1;
        return true;
    }
    int step = (ev.key == LT_KEY_ARROW_DOWN) - (ev.key == LT_KEY_ARROW_UP);
    if (b->detail_focus) b->detail_first += step;
    else if (step) b->cursor = rows.ids[clamp(rows.current + step, 0, rows.count - 1)];
    else if (ev.key == LT_KEY_ARROW_RIGHT && branch(b->cursor)) {
        if (b->open[b->cursor]) ++b->cursor; /* First child in preorder. */
        else b->open[b->cursor] = true;
    } else if (ev.key == LT_KEY_ARROW_LEFT) {
        if (branch(b->cursor) && b->open[b->cursor]) {
            b->open[b->cursor] = false;
            b->anchor = -1;
        } else if (nodes[b->cursor].parent >= 0) b->cursor = nodes[b->cursor].parent;
    } else if (ev.ch == ' ' || ev.key == LT_KEY_SPACE) b->marked[b->cursor] = !b->marked[b->cursor];
    else if (ev.ch == 'v') mark_range(b, rows);
    else if (ev.key == LT_KEY_ESC) b->anchor = -1;
    return true;
}

static bool layout_failed;
static void clay_error(Clay_ErrorData error) {
    (void)error;
    layout_failed = true;
}

int main(void) {
    size_t size = Clay_MinMemorySize();
    void *memory = malloc(size);
    if (!memory) return 1;
    int rc = lt_init();
    if (rc != LT_OK) {
        fprintf(stderr, "Terminal initialization: %s\n", lt_strerror(rc));
        free(memory);
        return 1;
    }
    Clay_Initialize(Clay_CreateArenaWithCapacityAndMemory(size, memory),
                    (Clay_Dimensions){(float)lt_width(), (float)lt_height()},
                    (Clay_ErrorHandler){clay_error, NULL});
    lt_set_input_mode(LT_INPUT_ESC | LT_INPUT_MOUSE);
    lt_hide_cursor();
    Browser browser = {.anchor = -1, .open = {true, true}};
    while (!layout_failed) {
        Panes panes = layout(lt_width(), lt_height(), browser.detail_focus);
        if (layout_failed) break;
        lt_clear();
        paint(&browser, panes);
        rc = lt_present();
        if (rc != LT_OK) break;
        struct lt_event ev;
        do { rc = lt_poll_event(&ev); }
        while (rc == LT_ERR_NO_EVENT || (rc == LT_ERR_POLL && lt_last_errno() == EINTR));
        if (rc != LT_OK || !handle(&browser, panes, ev)) break;
    }
    lt_shutdown();
    free(memory);
    if (layout_failed) fputs("Clay layout failed\n", stderr);
    else if (rc != LT_OK) fprintf(stderr, "Terminal I/O: %s\n", lt_strerror(rc));
    return layout_failed || rc != LT_OK;
}
