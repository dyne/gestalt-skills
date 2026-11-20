# Native Linux starter and capture checks

Use this optional starter when a project needs its first GLFW/OpenGL host or
real Linux rendering/lifecycle tests. Reuse an existing working host instead
of introducing another context owner. This is a single-window example, not a
framework or a screen-reader/IME/multi-window qualification.

The example shares `examples/settings_panel.cpp` with the headless runner.
Supplying `IMKIT_DIR` uses the existing ImKit panel and one shared core target.
It uses local sources only, never downloads or installs dependencies, and
keeps test hooks out of its native executable. Check the actual headers/pins;
the source uses the public font/texture API at ImGui19297. A minimum version
guard does not prove compatibility with every newer fork.

## Check prerequisites before building

From the skill directory:

```sh
python3 -B scripts/run_owned_display.py --probe
```

This read-only diagnostic starts no display. The default Linux runner needs
Xvfb, Marco, xrdb, dbus-run-session, X11, OpenGL and XTest. It returns2 for
missing capabilities; it never installs them or converts a required native
test into a successful skip. Another available EWMH window manager can be
selected with `--wm-command '["openbox"]'`. Its argv runs under a private
D-Bus session; a successful executable lookup is not window-manager readiness.
The actual run checks `_NET_SUPPORTING_WM_CHECK` on its authenticated display.

CMake additionally needs C/C++20 compilers, OpenGL development files and
GLFW's platform SDK headers. Supply an existing GLFW source checkout with
`GLFW_DIR`, or leave it empty to use a configured glfw3 package. Missing SDK
files are a prerequisite limitation, not permission to install or vendor them.

## Build and run

Use a fresh application-owned build directory outside the installed skill:

```sh
cmake -S examples/native-glfw-opengl -B /path/to/app/build/native \
  -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DIMGUI_DIR=/path/to/compatible/imgui -DGLFW_DIR=/path/to/glfw \
  -DIMKIT_DIR=/path/to/compatible/imgui-modern-kit
cmake --build /path/to/app/build/native --target native_example -j 2
ctest --test-dir /path/to/app/build/native -R '^native\.' \
  --output-on-failure --no-tests=error
```

Omit `IMKIT_DIR` for the core panel. Build only needed targets; keep stable
source/configuration fingerprints and reuse an unchanged build/cache for
iteration. A changed pin, configuration or backend needs renewed checks.
Never relink the executable while a test is using it. The generic starter
does not require another application's legacy build matrix.

`native.lifecycle` observes real font textures/readback, resize, font scale,
hidden-window event pumping and resource shutdown. It caches frame extents
while mapped and never queries them while hidden/minimized: some X11 window
managers cannot answer that query for an unmapped window. The smoke deadline
is a real wall-clock bound, independent of UI presentation time.

`native.relocated_entry` copies the actual executable, starts it from a working
directory unrelated to the build and copied binary, observes its decorated
window, and sends a real WM close gesture. The example uses the built-in font;
an application using external fonts/assets must copy those assets and retain
executable-relative lookup plus a separate missing-asset test.

## Owned process and artifact boundaries

The runner owns a fresh authenticated X server, ephemeral cookie, isolated XDG
directories, private D-Bus/WM group and command group. It preserves inherited
TMPDIR/TMP/TEMP and validates a managed scratch owner when that context is
supplied. If the environment supplies a validated short alias for the same
scratch owner, keep that spelling: Unix-domain socket paths have finite limits.
Do not silently fall back to another session's directory. Ordinary unmanaged
execution uses Python's standard temporary-directory selection.

Each invocation creates a unique `run-*` directory under `--output`. `{output}`
in command arguments expands to that run directory, so reruns preserve prior
logs/captures. Give the outer test invocation a fresh directory too. Put CTest
or Test Engine JUnit and the runner output under that directory. For CTest use
`--output-junit <attempt-dir>/ctest.xml` and save console output there before
the next invocation replaces `Testing/Temporary/LastTest.log`. Summarize the
intended and executed cases, result, and first failure path. Keep the full
attempt for follow-up inspection. `processes.json` records command/exit,
timeout, owned PIDs and remaining live group members. Keep cookie bytes out of
logs. Failure, startup rejection and timeout must still settle owned processes.
Native CTest cases run serially. Independent jobs can choose disjoint `--display-start`
ranges; a startup collision is failure, not evidence of another job's display.

```sh
python3 -B scripts/run_owned_display.py --output /path/to/app/evidence \
  -- /path/to/app/build/native/native_example --smoke '{output}/captures'
```

The final JSON names the retained run directory. Missing tools return2;
ordinary child exit codes propagate; killed/timed-out children return nonzero.
The runner never uses an existing user's display or changes desktop settings.

## Capture candidates and compare inspected baselines

The host's smoke writes an actual OpenGL RGB framebuffer and renderer facts.
`capture_native.py` encodes P6 RGB data losslessly as PNG and records raw/PNG
hashes. Supply actual binary and font/source/config inputs when making an
identity-bound claim; omitted identities remain unknown.

```sh
python3 -B scripts/capture_native.py /path/to/candidate/captures --expected 1 \
  --binary /path/to/app/build/native/native_example \
  --input /path/to/compatible/imgui/imgui.h
```

This produces a candidate, never an automatically approved baseline. Inspect
the actual images first. Only then explicitly mark the intended baseline:

```sh
python3 -B scripts/capture_native.py /path/to/inspected/captures \
  --expected 1 --accept-baseline
python3 -B scripts/capture_native.py /path/to/new/captures --expected 1 \
  --baseline /path/to/inspected/captures
```

Candidate and baseline directories must differ. Comparisons verify the prior
raw hashes, exact case identities/dimensions and every RGB channel, without
overwriting baseline pixels or ignoring regions. Wrong/missing images and
changed baseline bytes fail. Deterministic fonts, theme, geometry and time
remain the caller's responsibility. Parameterize the needed scenario matrix;
do not hardcode another application's counts or claim physical GPU/mixed-DPI
coverage from a software-rendered Xvfb capture.

## Adaptation and evidence limits

Replace the shared settings drawing function with the application's actual
panel. Keep application effects behind explicit model/service acknowledgement;
the example's Save is in-memory only. Retain context/thread ownership, input
forwarding through stock backends, zero/hidden drawable handling and teardown.
Choose the application's minimum size, fonts, theme and required states.

The lifecycle test establishes rendering/resource behavior; the relocated
entry test establishes OS window creation/close delivery. Neither establishes
every widget interaction. Use the headless Test Engine for intended model
outcomes, and add native input journeys where required. Native IME, Orca/AT-SPI,
physical GPU/monitor moves, Wayland, macOS and Windows remain unqualified until
their actual paths run. No third-party engine/library/font implementation is
bundled by these examples.

The native host/display/smoke/capture patterns are adapted from the MIT-licensed
Plan-B Foundation Roots GUI foundation, commit
`213e33a0f5040efe5888f23c38c4c874a24d7c83`; original file notices are retained.
See `evals/native-validation.md` from the skill root for tested identities,
commands, counts and remaining limitations.
