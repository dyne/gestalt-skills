"""Run the compiled browser in its own tmux PTY and check the visible cells."""

import argparse
from pathlib import Path
import shlex
import subprocess
import time
import uuid


def check(binary):
    socket = "clay-tui-" + uuid.uuid4().hex

    def tmux(*args, required=True):
        return subprocess.run(["tmux", "-L", socket, "-f", "/dev/null", *args],
                              check=required, capture_output=True, text=True, timeout=5).stdout

    def until(description, read, predicate):
        deadline = time.monotonic() + 5
        while True:
            value = read()
            if predicate(value):
                print("PASS", description)
                return
            if time.monotonic() >= deadline:
                raise AssertionError(f"{description}\nLast observation:\n{value}")
            time.sleep(0.03)

    def screen(description, predicate):
        until(description, lambda: tmux("capture-pane", "-p"), predicate)

    def keys(*names):
        tmux("send-keys", *names)

    try:
        tmux("new-session", "-d", "-s", "browser", "-x", "78", "-y", "12",
             "exec " + shlex.quote(str(binary.resolve(strict=True))))
        tmux("set-option", "-w", "remain-on-exit", "on")
        screen("wide sidebar, detail and footer", lambda s:
               s.splitlines()[0].startswith("> Files") and "Details" in s.splitlines()[0][26:]
               and "q quit" in s.splitlines()[-1])
        keys("Down", "Right", "Space")
        screen("first child marked", lambda s: "Item: app.c" in s and "Marked: 1" in s)
        keys("v", "Down", "v")
        screen("additive visible range", lambda s: "Item: layout.c" in s and "Marked: 2" in s)
        keys("Left", "Left")
        screen("hidden descendants retain marks", lambda s: "Item: Sources" in s and
               "Marked: 2" in s and not any("app.c" in row[:25] for row in s.splitlines()))
        # Xterm SGR button 0 at column 2, row 2 (one-based on the wire).
        tmux("send-keys", "-l", "\x1b[<0;2;2M\x1b[<0;2;2m")
        screen("mouse hits the rendered tree row", lambda s: "Item: Workspace" in s)
        keys("v")
        screen("range owner shows apply and cancel", lambda s: "v apply | Esc cancel" in s)
        tmux("send-keys", "-l", "\x1b[<0;35;2M\x1b[<0;35;2m")
        screen("changing pane by mouse cancels pending range", lambda s:
               "> Details" in s and "Tab files" in s and "Esc cancel" not in s)
        keys("Tab")
        screen("focus returns to Files", lambda s: s.startswith("> Files"))
        tmux("resize-window", "-x", "30", "-y", "5")
        screen("narrow screen keeps focused pane", lambda s:
               s.startswith("> Files") and "Details" not in s and len(s.splitlines()) == 5
               and "v range" in s.splitlines()[-1] and "Tab  q quit" in s.splitlines()[-1])
        keys("Down", "Down", "Down", "Down")
        screen("cursor scrolls into the small viewport", lambda s:
               any(r.startswith("> [ ] + Archive") for r in s.splitlines()))
        keys("Tab")
        screen("detail screen preserves state", lambda s: s.startswith("> Details") and
               "Marked: 2" in s and "Item: Archive" in s)
        tmux("resize-window", "-x", "6", "-y", "1")
        screen("one-row terminal", lambda s: s.splitlines() == ["> Deta"])
        tmux("resize-window", "-x", "78", "-y", "12")
        screen("wide layout restored", lambda s: "Files" in s and "> Details" in s and "Marked: 2" in s)
        keys("q")
        until("clean exit", lambda: tmux("display-message", "-p", "#{pane_dead}:#{pane_dead_status}").strip(),
              lambda status: status == "1:0")
    finally:
        tmux("kill-server", required=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    check(parser.parse_args().binary)
