# Port the Clay termbox2 renderer

Libterm implements its own terminal backend. Its `compat/termbox2.h` translates a substantial subset of termbox2's source API to the compiled libterm library. Having a function named `tb_set_cell` does not imply identical cell structs, attribute bits or keyboard behavior. Choose one terminal owner per executable.

| Integration | Headers and linkage | Coordinates |
| --- | --- | --- |
| Native libterm widgets with Clay layout | `clay.h`, `libterm/libterm.h`, link libterm. The starter reads the bounding boxes of named elements. | Clay units are cells. Mouse columns and rows already match. |
| Clay's termbox2 renderer with original termbox2 | Use upstream `termbox2.h` with `TB_IMPL` in one translation unit, or link a matching prebuilt termbox2. The renderer expects 32-bit color attributes. Match `TB_OPT_ATTR_W` throughout. | The renderer defaults to 9×21 virtual pixels per cell. Use its current cell width and height for Clay dimensions, mouse and text metrics. |
| Same renderer through libterm | Put libterm's `compat/` first for `termbox2.h`, expose `include/`, link libterm, and apply the version-specific adjustments below. | Same virtual-pixel contract. Convert a bounding box to cell edges once. |

## Reproducing the Linux renderer check

At the reviewed commits the unmodified upstream demo fails to compile even with the original termbox2 header. Its `component_text_pair` stores a pointer where this Clay version expects a text-config value, and the header requires a delta-time argument to `Clay_EndLayout`. Fix those two call sites on both backends before diagnosing libterm. The published demo's CMake also fetches two dependencies. This procedure uses local source trees and the static library from the [build guide](build.md).

Set `STB` to the directory containing `stb_image.h` and `stb_image_resize2.h` at the [demo's stb pin](https://github.com/nothings/stb/tree/fede005abaf93d9d7f3a679d1999b2db341b360f). Keep `CLAY`, `LIBTERM` and `STB` absolute. From the directory containing `libterm.a`:

```sh
demo="$CLAY/examples/termbox2-demo"
sed -e 's/Clay_TextElementConfig \*textconfig/Clay_TextElementConfig textconfig/' \
    -e 's/Clay_EndLayout()/Clay_EndLayout(0.0f)/' \
    "$demo/main.c" > demo-current.c

sed '/^#define TB_IMPL$/d' demo-current.c > demo-libterm.c
cc -std=gnu11 -include limits.h -include string.h -include errno.h -include sys/select.h \
   -DTB_HI_BLACK=LT_HI_BLACK -DTB_BRIGHT=0 \
   -I"$LIBTERM/compat" -I"$LIBTERM/include" -I"$demo" -I"$STB" \
   demo-libterm.c libterm.a -lm -o demo-libterm
binary="$PWD/demo-libterm"
(cd "$demo" && CLAY_TB_COLOR_MODE=256 "$binary")
```

The working directory supplies the demo's JPEGs. The fixed zero delta is suitable for this static check; measure elapsed time for animated layouts. For a control build set `TERMBOX2` to the [tested original header checkout](https://github.com/termbox/termbox2/tree/3a955d360f13f53a6c549d3a3ca3109fc9e8ae7f), and build `demo-current.c` with `cc -std=gnu11 -I"$TERMBOX2" -I"$demo" -I"$STB" demo-current.c -lm -o demo-original`. Launch from the same resource directory. In a 120×45 tmux pane both binaries displayed the Clay demo, changed the rendered border after an `h` keypress and exited on `q`. The demo's settings panel was clipped at other tested sizes on both backends. Use the starter's responsive layout for a narrow terminal.

**Color.** The shim omits `TB_HI_BLACK`; use libterm's actual `LT_HI_BLACK` sentinel. The shim also lacks `TB_BRIGHT`. The zero mapping above deliberately folds the bright half of the renderer's **normal-mode** color table into the base eight. The demo runs in 256-color mode. For a design that requires 16 distinct colors choose explicit palette entries in 256 mode or implement a tested normal-mode fallback. Copying termbox2's numeric masks can select unrelated libterm styles. Libterm applies style bits on foreground.

**Input and cell access.** The renderer's POSIX wait helper calls `select` on two file descriptors. Replace it with libterm's polling/timeout loop for a Win32 port. Check init first and consume an event once. Libterm's shim implements `tb_get_cell` with a snapshot of the **back** buffer that expires on the next call. Features that access the termbox2 live cell buffer or write through its pointer need an explicit read/modify/write path. Consult the [shim](https://github.com/rizukirr/libterm/blob/70ea507b2a51a595863cf06e0fb830330c26832b/compat/termbox2.h) for unmapped functions.

**Command coverage.** Feed render commands to the renderer in returned order before the next layout. This pin draws rectangles, borders, text and images; its custom-command case does nothing. A single active scissor box is overwritten on START and disabled on END. For nested scroll panes or custom widgets inside overlays, implement a clip stack intersected with ancestor bounds and screen bounds, or paint each widget in its own clipped pane. Test overlap and border clipping at the edges. Giving the app and the renderer independent scroll offsets for the same list makes hit targets drift.

The [renderer source](https://github.com/nicbarker/clay/blob/e6cc36941ab2af5d81107617039d6f527a1c660b/renderers/termbox2/clay_renderer_termbox2.c) carries its own zlib-style notice. Keep it when redistributing that source and identify modifications. The supplied skill starter implements its own cell-painting path.
