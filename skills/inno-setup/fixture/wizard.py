"""Drive visible Win32 controls in the fixture's uniquely titled Inno wizard."""

import ctypes as C
from ctypes import wintypes as W
from pathlib import Path
import subprocess
import time


ui = C.WinDLL("user32", use_last_error=True)
callback = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
ui.SendMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
ui.SendMessageW.restype = W.LPARAM
ui.GetWindowLongW.argtypes = [W.HWND, C.c_int]


def windows(parent=None):
    result = []
    def visit(hwnd, unused):
        if ui.IsWindowVisible(hwnd):
            buf = C.create_unicode_buffer(1024)
            ui.SendMessageW(hwnd, 13, len(buf), C.addressof(buf))  # WM_GETTEXT
            result.append((hwnd, buf.value.replace("&", "")))
        return True
    if parent:
        ui.EnumChildWindows(parent, callback(visit), 0)
    else:
        ui.EnumWindows(callback(visit), 0)
    return result


def until(probe, description):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        value = probe()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for " + description)


def control(parent, caption):
    return until(lambda: next((h for h, text in windows(parent) if text == caption), None),
                 f"{caption!r}; visible controls {windows(parent)}")


def click(hwnd):
    if not ui.IsWindowEnabled(hwnd):
        raise RuntimeError(f"Control {hwnd} is disabled")
    ui.PostMessageW(hwnd, 0xF5, 0, 0)  # BM_CLICK


def screenshot(hwnd, file):
    rect = W.RECT()
    ui.GetWindowRect(hwnd, C.byref(rect))
    ui.SetForegroundWindow(hwnd)
    width, height = rect.right - rect.left, rect.bottom - rect.top
    command = (
        "Add-Type -AssemblyName System.Drawing; "
        f"$b=[Drawing.Bitmap]::new({width},{height}); $g=[Drawing.Graphics]::FromImage($b); "
        f"$g.CopyFromScreen({rect.left},{rect.top},0,0,$b.Size); "
        "$b.Save($env:FIXTURE_SCREEN,[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b.Dispose()"
    )
    import os
    subprocess.run(["powershell", "-NoProfile", "-Command", command],
                   env=dict(os.environ, FIXTURE_SCREEN=str(file)), check=True, timeout=25)


def exercise(exe, dest, log, title, launch, shortcut, previously_linked=False, capture=False):
    proc = subprocess.Popen([exe, "/CURRENTUSER", "/SP-", "/NORESTART", f"/DIR={dest}", f"/LOG={log}"])
    wizard = until(lambda: next((h for h, text in windows() if text == "Setup - " + title), None), title)
    link = until(lambda: next((h for h, text in windows(wizard) if "Project homepage" in text), None),
                 "welcome page project link")
    if not ui.GetWindowLongW(link, -16) & 0x10000:  # WS_TABSTOP
        raise RuntimeError("Project link is outside the tab order")
    if capture:
        screenshot(wizard, Path(log).with_suffix(".png"))
    click(control(wizard, "Next >"))
    accept = control(wizard, "I accept the agreement")
    click(accept)
    forward = control(wizard, "Next >")
    until(lambda: ui.IsWindowEnabled(forward), "accepted license")
    click(forward)
    control(wizard, str(dest))
    click(control(wizard, "Install"))
    launch_box = control(wizard, "Launch the application")
    shortcut_box = control(wizard, "Add a Start menu shortcut")
    for hwnd, expected, desired in ((launch_box, False, launch), (shortcut_box, previously_linked, shortcut)):
        checked = lambda: bool(ui.SendMessageW(hwnd, 0xF0, 0, 0))  # BM_GETCHECK
        if checked() != expected:
            raise RuntimeError("Unexpected finish-page default")
        if expected != desired:
            click(hwnd)
            until(lambda: checked() == desired, "finish-page selection")
    click(control(wizard, "Finish"))
    if proc.wait(timeout=30):
        raise RuntimeError(f"Interactive Setup failed; see {log}")
    pages = [line.split("fixture page ", 1)[1].strip() for line in Path(log).read_text(
        encoding="utf-8-sig", errors="replace").splitlines() if "fixture page " in line]
    if pages != ["welcome", "license", "destination", "installing", "finish"]:
        raise RuntimeError(f"Unexpected wizard pages {pages}")
