"""Run on disposable Windows: python -B run.py ISCC.exe NEW_EVIDENCE_DIR."""

import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import os
import re
from pathlib import Path
import struct
import subprocess
import sys
import urllib.request
import uuid

from wizard import exercise, until

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
FLAGS = ["/SP-", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
ART = {
    "bitcoin-roots.ico": "9b6e087a3b1c3c30cc2faff1009dddb957827b8e40c80491f60c236004356517",
    "installer-branding.bmp": "07c21f016ff98a19df1305c5ad99ba205487ef150e942a7d27d6961432e324a9",
}


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def command(*args, **kwargs):
    return subprocess.run(args, check=True, timeout=90, **kwargs)


def payload(root, title):
    stage = root / "stage"
    stage.mkdir()
    (stage / "bin").mkdir()
    (stage / "LICENSE.txt").write_text("Fixture payload for installer verification.\n")
    (stage / "data").mkdir()
    (stage / "data" / "palette.json").write_text('{"color":"gold"}')
    for name, digest in ART.items():
        url = ("https://raw.githubusercontent.com/LuganoPlanB/bitcoin-viz/"
               "10a244c5c5588c6936ca20194f5492335589e51d/" + "ci/release/" + name)
        (root / name).write_bytes(urllib.request.urlopen(url, timeout=30).read())
        check(sha(root / name) == digest, f"Unexpected artwork {name}")
    config = dict(name=title, publisher="Installer Fixture", homepage="https://example.org/fixture",
                  description="Disposable installer fixture", license="MIT", licenseFile="stage/LICENSE.txt",
                  executable="probe-cli.exe", guiExecutable="probe-gui.exe", binaryDirectory="bin", iconFile="bitcoin-roots.ico",
                  wizardImage="installer-branding.bmp", welcomeCredit="Built for the installer fixture.",
                  silentShortcut="create")
    (root / "product.json").write_text(json.dumps(config))
    for name, subsystem in (("probe-cli.exe", 3), ("probe-gui.exe", 2)):
        flags = ["-ldflags=-H windowsgui"] if subsystem == 2 else []
        command("go", "build", *flags, "-o", stage / "bin" / name, HERE / "probe.go")
        data = (stage / "bin" / name).read_bytes()
        pe = struct.unpack_from("<I", data, 60)[0]
        check(struct.unpack_from("<H", data, pe + 24 + 68)[0] == subsystem, f"{name} subsystem")
    return stage


def compile_setup(root, compiler, stage, version, winget=False):
    manifest = {"version": version, "files": {p.relative_to(stage).as_posix(): sha(p)
                for p in sorted(stage.rglob("*")) if p.is_file() and p.name != "MANIFEST.json"}}
    (stage / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    inc = root / "product.iss"
    command(sys.executable, "-B", ASSETS / "product_metadata.py", "inno", "--product",
            root / "product.json", "--version", version, "--output", inc)
    label = "winget" if winget else "classic"
    build_log = root / f"compile-{version}-{label}.log"
    with build_log.open("wb") as log:
        command(compiler, f"/DMyAppVersion={version}", f"/DProductInclude={inc}", f"/DStageDir={stage}",
                "/DFixtureTrace", *(["/DStreamlined"] if winget else []), f"/O{root}", f"/F{version}-{label}",
                root / "installer.iss", stdout=log, stderr=subprocess.STDOUT)
    check(re.search(rb"Compiler engine version:[^\r\n]*\b6\.4\.3\b", build_log.read_bytes()),
          f"Unexpected compiler engine; inspect {build_log}")
    return root / f"{version}-{label}.exe", manifest


def verify_install(dest, expected):
    check(json.loads((dest / "MANIFEST.json").read_bytes()) == expected, "Installed manifest mismatch")
    for name, digest in expected["files"].items():
        check(sha(dest / name) == digest, f"Installed payload differs: {name}")
    for name in ("probe-cli.exe", "probe-gui.exe"):
        exe = dest / "bin" / name
        check(command(exe, "--version", capture_output=True).stdout.strip() == b"fixture diagnostic", name)
        check(command(exe, "--echo", input=b"piped input", capture_output=True).stdout == b"piped input", name)


def uninstall(root, label, dest, link):
    uninstaller, = dest.glob("unins*.exe")
    command(uninstaller, *FLAGS, f"/LOG={root / (label + '-uninstall.log')}")
    until(lambda: not (dest / "bin/probe-cli.exe").exists() and not link.exists(), "uninstall cleanup")
    for name in ("bin/probe-gui.exe", "MANIFEST.json", "LICENSE.txt", "data/palette.json"):
        check(not (dest / name).exists(), f"Leftover owned file {name}")


def run(compiler, root):
    identity = uuid.uuid4()
    title = "Inno Fixture " + identity.hex[:8]
    script = (ASSETS / "installer.iss.in").read_text(encoding="utf-8").replace(
        "@APP_GUID@", str(identity)).replace("@INSTALL_FOLDER@", title).replace("@SLUG@", "fixture")
    (root / "installer.iss").write_text(script, encoding="utf-8-sig")
    stage = payload(root, title)
    dest = root / "Installed app Ω"
    marker = dest / "bin/launch.txt"
    link = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs" / title / (title + ".lnk")
    classic, v1 = compile_setup(root, compiler, stage, "1.0.0")
    exercise(classic, dest, root / "fresh.log", title, False, False, capture=True)
    verify_install(dest, v1)
    check(not link.exists() and not marker.exists(), "Unchecked finish option was applied")
    exercise(classic, dest, root / "launch-only.log", title, True, False)
    until(lambda: marker.is_file(), "GUI launch")
    check(marker.read_text() == "probe-gui.exe", "Launched wrong executable")
    check(not link.exists(), "Launch-only choice created a shortcut")
    marker.unlink()
    exercise(classic, dest, root / "shortcut-only.log", title, False, True)
    check(not marker.exists(), "Selecting only the shortcut launched the GUI")
    check(link.is_file(), f"Missing shortcut: {link}")
    os.startfile(link)
    until(lambda: marker.is_file(), "Start menu shortcut launched installed application")
    check(marker.read_text() == "probe-gui.exe", "Start menu shortcut launched wrong EXE")
    marker.unlink()
    exercise(classic, dest, root / "remove.log", title, False, False, previously_linked=True)
    check(not link.exists(), "Clearing shortcut left the link installed")
    uninstall(root, "interactive", dest, link)
    command(classic, *FLAGS, "/CURRENTUSER", f"/DIR={dest}", f"/LOG={root / 'silent.log'}")
    verify_install(dest, v1)
    check(link.is_file() and not marker.exists(), "Silent defaults")
    (dest / "user.txt").write_text("Keep my settings")
    winget, v2 = compile_setup(root, compiler, stage, "2.0.0", winget=True)
    command(winget, *FLAGS, "/CURRENTUSER", f"/DIR={dest}", f"/LOG={root / 'upgrade.log'}")
    verify_install(dest, v2)
    check((dest / "user.txt").read_text() == "Keep my settings", "Upgrade lost user data")
    check(link.exists() and not marker.exists(), "WinGet defaults")
    uninstall(root, "upgrade", dest, link)
    check((dest / "user.txt").read_text() == "Keep my settings", "Uninstall removed user data")
    print("ISCC 6.4.3: interactive, silent, WinGet, upgrade, uninstall and GUI/CLI checks passed")


def contained(compiler, root):
    # Assign the waiting worker to a job before giving it permission to launch Setup.
    # Closing the last job handle terminates surviving loader, .tmp and uninstaller processes.
    kernel = C.WinDLL("kernel32", use_last_error=True)
    class Limits(C.Structure):
        _fields_ = [("times", C.c_longlong * 2), ("flags", W.DWORD), ("minimum", C.c_size_t),
                    ("maximum", C.c_size_t), ("active", W.DWORD), ("affinity", C.c_size_t),
                    ("priority", W.DWORD), ("scheduling", W.DWORD)]
    class Extended(C.Structure):
        _fields_ = [("basic", Limits), ("io", C.c_ulonglong * 6), ("memory", C.c_size_t * 4)]
    kernel.CreateJobObjectW.restype = W.HANDLE
    job = W.HANDLE(kernel.CreateJobObjectW(None, None))
    if not job:
        raise C.WinError(C.get_last_error())
    try:
        limits = Extended()
        limits.basic.flags = 0x2000
        if not kernel.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)):
            raise C.WinError(C.get_last_error())
        with subprocess.Popen([sys.executable, "-B", __file__, compiler, root, "--worker"],
                              stdin=subprocess.PIPE) as worker:
            try:
                if not kernel.AssignProcessToJobObject(job, W.HANDLE(worker._handle)):
                    raise C.WinError(C.get_last_error())
                worker.communicate(b"1", timeout=420)
                check(worker.returncode == 0, "Fixture failed; inspect evidence in " + str(root))
            finally:
                if worker.poll() is None:
                    worker.kill()
    finally:
        kernel.CloseHandle(job)


if __name__ == "__main__":
    compiler, root = (Path(s).resolve() for s in sys.argv[1:3])
    if sys.argv[3:] == ["--worker"]:
        check(sys.stdin.buffer.read(1) == b"1", "Missing process containment")
        run(compiler, root)
    else:
        root.mkdir(parents=True, exist_ok=False)
        contained(compiler, root)
