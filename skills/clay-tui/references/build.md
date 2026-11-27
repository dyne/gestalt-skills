# Build the starter

The primary example is a native libterm consumer. It uses Clay only to solve the layout. The terminal renderer, stb and termbox-widgets are optional alternatives for other designs. Use absolute paths for `CLAY` (the checkout containing `clay.h`), `LIBTERM` (the libterm checkout) and `SKILL` (this skill directory).

## Installed SDK or source checkout

With installed libterm and its pkg-config file on the search path:

```sh
cc -std=c11 -I"$CLAY" "$SKILL/examples/browser.c" \
   $(pkg-config --cflags --libs libterm) -lm -o browser
./browser
```

For CMake consumers use `find_package(Libterm CONFIG REQUIRED)`, add the Clay include directory to the app, and link `Libterm::libterm`. When building libterm itself with CMake the reviewed version requires 3.32+. Its CMake build supports runtime-dispatched SIMD. The following Linux scalar build also works with a C11 compiler and archiver. Run it in a new build directory; it writes object files there.

```sh
cc -std=c11 -O2 -I"$LIBTERM/include" -I"$LIBTERM/src" -c \
   "$LIBTERM"/src/shared/*.c "$LIBTERM"/src/platform/posix/*.c \
   "$LIBTERM"/src/intrinsics/scalar.c
ar rcs libterm.a ./*.o
cc -std=c11 -O2 -I"$CLAY" -I"$LIBTERM/include" \
   "$SKILL/examples/browser.c" libterm.a -lm -o browser
python3 "$SKILL/examples/check_browser.py" ./browser
```

The last command needs tmux and Python 3. It creates an isolated server, drives the real binary, reads terminal cells, resizes the PTY, checks the exit status and closes the server. For a manual run, use arrows to navigate, Space to mark, `v` twice around an inclusive range, Tab to review, and `q` to quit. The selected items remain visible in Details after their branch collapses.

## Terminal lifecycle

- Define `CLAY_IMPLEMENTATION` in one translation unit. Allocate at least `Clay_MinMemorySize()` and keep that arena alive through every layout. Keep dynamic text alive until Clay has finished using it and the renderer has consumed the frame. The starter's geometry-only layouts need no Clay text measurement function.
- Check `lt_init()`, hide the hardware cursor while browsing, paint the first frame before waiting, and use `lt_shutdown()` on normal exit and error paths after successful init. Write diagnostics after restoring the terminal. For an editable text field, position and show the hardware cursor inside its focused viewport.
- Use `lt_poll_event` for idle screens. Use `lt_peek_event` with a deadline for timers or animations, passing elapsed seconds to the matching Clay API. Process events only on `LT_OK`. A resize can wake the POSIX wait with `LT_ERR_NO_EVENT` before the resize event arrives. Retry; also retry an interrupted poll (`LT_ERR_POLL` and `EINTR`). On resize read the new dimensions, recompute layout and redraw. A worker can enqueue model updates, while the UI thread owns terminal and Clay calls.
- `lt_event.ch` holds text; `key` holds special keys and `mod` carries modifiers. For native libterm use its modern key model. For a port expecting legacy control bytes, select `LT_INPUT_COMPAT` with the desired ESC/ALT and mouse flags. Releases are suppressed by default. `lt_get_fds` is POSIX-specific in practice; the Windows backend returns `LT_ERR_UNSUPPORTED_TERM`. The native polling API is the portable route.
- `lt_clear()` rebuilds the frame from blank cells. Draw the panes into the back buffer, then `lt_present()` once. Preserve old geometry only for hit-testing that displayed frame. A complete repaint after terminal damage can also use `lt_invalidate()`. Keep ordinary stdout logging out of the live TUI.

The example and tmux checks were exercised on Linux with [libterm at 70ea507](https://github.com/rizukirr/libterm/tree/70ea507b2a51a595863cf06e0fb830330c26832b) and [Clay at e6cc369](https://github.com/nicbarker/clay/tree/e6cc36941ab2af5d81107617039d6f527a1c660b). Test native Win32 and the intended terminal emulator separately when claiming support there.
