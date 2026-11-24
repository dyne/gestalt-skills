# Stage vcpkg dependencies for Windows Setup

Use this when the Windows release already consumes vcpkg. Classic Setup, unattended installation and the WinGet profile can all package the same verified stage.

## Identify the build that produced the binaries

Read the release job, presets, CMake cache or Make invocation. Record the vcpkg revision, installed directory, target and host triplets, and release configuration. In manifest mode, trace the selected features, baseline, overrides, registries and overlay ports or triplets to the checked-out candidate. In classic vcpkg mode, obtain the installed port versions and triplets from the build that linked the application. A host tool may be x64 even when the product is ARM64. Follow the target triplet to the customer files.

Inspect the effective triplet. `VCPKG_LIBRARY_LINKAGE` expresses the preferred library linkage and individual ports can differ. `VCPKG_CRT_LINKAGE` controls the C runtime separately. Inspect the resulting PE files even for a static triplet. For a dynamically linked MSVC runtime, verify the project's supported redistributable or permitted app-local deployment on its minimum supported Windows image. [Triplet variables](https://learn.microsoft.com/en-us/vcpkg/users/triplets) · [Visual C++ redistribution](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)

## Build a release inventory

- Inspect the GUI, CLI and shipped plug-ins with `dumpbin /DEPENDENTS` or `llvm-readobj --coff-imports`. Follow imports recursively through app-private DLLs. Verify the PE machine type. Resolve release DLLs against the chosen target prefix and identify Windows-provided libraries separately.
- Check application and port install rules for plug-ins loaded by name, codecs, translations, certificates and other data. Preserve the installed paths their loaders expect. Import tables alone cannot identify these files.
- Collect the required notices for every redistributed dependency, including statically linked and transitive libraries. Keep each port's `share/<port>/copyright` and any required accompanying files under distinct names or directories. Exclude host build tools, debug binaries, headers, import libraries and unrelated ports from the installer. [vcpkg installation tree](https://learn.microsoft.com/en-us/vcpkg/reference/installation-tree-layout)

Bitcoin Viz v0.8.1 used a release-only x64 triplet with static library and CRT linkage. Its packaging script recorded the manifest baseline and checked for the curl, OpenSSL, SQLite and ZeroMQ notices. Apply those checks even when a port contributes no DLL. [Release triplet](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/ci/triplets/x64-windows-release.cmake) · [Release packaging script](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/ci/release/package.cmake)

## Add the files to the existing install rules

In this example the release EXEs live in `bin/` and import `sqlite3.dll`. Substitute the actual dependency inventory. For static SQLite, keep the notice rule and omit the DLL copy once the PE inspection confirms it. Keep Setup's input pointed at the project's fresh stage. [Installer build target](build.md)

For CMake, add these rules to the Windows release install rules alongside `install(TARGETS ...)`. The vcpkg toolchain supplies the installed root and target triplet at configure time. Stage with `cmake --install out --config Release --prefix "<stage>"`. Match the configuration name if the release job uses another one.

```cmake
set(deps "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}")
install(FILES "${deps}/bin/sqlite3.dll"
        DESTINATION bin CONFIGURATIONS Release)
install(FILES "${deps}/share/sqlite3/copyright"
        DESTINATION share/dial/third-party/sqlite3 CONFIGURATIONS Release)
```

For GNU Make on MSYS, add this target and change the staging call inside `win-installer` to `$(MAKE) install install-vcpkg-runtime DESTDIR="$$stage" prefix=/`. Pass the release build's installed root and target triplet as Make variables, using paths the shell can read.

```make
deps = $(VCPKG_INSTALLED_DIR)/$(VCPKG_TARGET_TRIPLET)
stage_root = $(DESTDIR)$(prefix)

.PHONY: install-vcpkg-runtime
install-vcpkg-runtime:
	@test -n "$(DESTDIR)" && test -n "$(VCPKG_INSTALLED_DIR)" && test -n "$(VCPKG_TARGET_TRIPLET)"
	install -d "$(stage_root)/bin" "$(stage_root)/share/dial/third-party/sqlite3"
	install -m 644 "$(deps)/bin/sqlite3.dll" "$(stage_root)/bin/sqlite3.dll"
	install -m 644 "$(deps)/share/sqlite3/copyright" "$(stage_root)/share/dial/third-party/sqlite3/copyright"
```

Compare the stage to the release inventory before compiling Setup. Fail on missing required files or files from another triplet or configuration. List the selected target triplet, dependency baseline or installed versions, and shipped notices in the project's release manifest or internal receipt.

## Exercise the installed copy

Install the final Setup on a disposable Windows image with the project's documented prerequisites. From an empty directory outside the checkout, run the installed binaries by absolute path. Limit the child process's `PATH` to Windows system directories and clear any project-specific plug-in or data path overrides. This catches imports that a developer shell resolves from vcpkg. For example, this Python check takes the absolute install directory and expected version string as arguments. Substitute the actual executable names, version output and a supported feature probe.

```python
import os
from pathlib import Path
import subprocess
import sys
import tempfile

bin_dir = Path(sys.argv[1]).resolve(strict=True) / "bin"
windows = Path(os.environ["SystemRoot"])
env = {**os.environ, "PATH": os.pathsep.join(map(str, (windows / "System32", windows)))}
with tempfile.TemporaryDirectory() as cwd:
    for exe in ("dial.exe", "dial-cli.exe"):
        result = subprocess.run([bin_dir / exe, "--version"], cwd=cwd, env=env,
                                capture_output=True, text=True, check=True, timeout=30)
        if result.stdout.strip() != sys.argv[2]:
            raise SystemExit(f"{exe}: unexpected version {result.stdout!r}")
    subprocess.run([bin_dir / "dial.exe", "--smoke-test"], cwd=cwd, env=env,
                   check=True, timeout=60)
```

Choose a probe that actually opens the database, decodes a sample through the shipped plug-in, or renders using installed data. Check its expected output or result. A version check exercises process startup only. For a GUI without diagnostic switches, launch it through its installed shortcut and exercise the feature there. Verify the installed notices and manifest as well. [Bitcoin Viz installed-copy probe](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/ci/desktop/installed.py)

For changes to vcpkg itself, consult the upstream [vcpkg skill](https://github.com/github/awesome-copilot/tree/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/vcpkg) and its references on [registries and overlays](https://github.com/github/awesome-copilot/blob/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/vcpkg/references/registries.md), [CI caching](https://github.com/github/awesome-copilot/blob/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/vcpkg/references/ci.md) and [build troubleshooting](https://github.com/github/awesome-copilot/blob/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/vcpkg/references/troubleshooting.md).
