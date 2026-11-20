# Windows and macOS ports

Keep shared ImGui/ImKit panels, commands and test fixtures. Put platform
services such as clipboard, file dialogs and accessibility behind the host
boundary. Keep the existing working backend pair available while adding a
target. Bring up one window using the [frame and backend contract](integration.md),
then build, stage and smoke-test a package on the target OS before extending
desktop integrations.

For release builds, pass the same release version into every native build and
check it in the extracted package. Record the actual compiler, architecture,
renderer and platform capabilities exercised by each smoke test.

## Windows

- Choose one compiler, architecture and runtime for the app and its libraries.
  Roots GUI used native x64 MSYS2 UCRT64 GCC with GLFW/OpenGL. Run the actual
  Windows build early to expose POSIX-only sources and dependency assumptions.
  If an offline input verifier fails only on Windows, compare the checked-out
  bytes first. Preserve hash-checked text files and patches through Git line
  ending conversion.
- Resolve resources from the executable location. Stage the DLLs required by
  the app and its dependencies, fonts and notices. Launch the staged app
  from an unrelated directory with the build toolchain removed from `PATH`.
  Include a path with spaces and non-ASCII characters. Check window close and
  a Unicode clipboard round trip or file dialog if supported. Keep a
  CI-only software driver outside the shipping package.

See the [Roots GUI Windows build and smoke tests](https://github.com/LuganoPlanB/bitcoin-roots-gui/blob/43027d0e5f6e12fd4a4bae8d7aa93e8305d6803c/docs/windows-build.md).

## macOS

- Choose the architecture and minimum supported macOS version at configure
  time. Roots GUI kept GLFW for window/input and put Metal submission in a
  small Objective-C++ adapter. Start from the stock ImGui Metal renderer and
  check drawable resize and teardown on the target host.
- Stage a `.app` with assets under `Contents/Resources`. Extract the
  distributable to a new location before testing. Check the executable with
  `lipo -archs`, inspect linkage with `otool -L`, and verify the staged
  signature when applicable. Review non-system dependencies, including
  transitive libraries and build-machine absolute paths. Roots GUI's first
  linked app pulled in optional Homebrew libraries despite linking its primary
  dependencies statically. Make optional dependency choices explicit.
- Check actual Metal frame submission and a clean close in a graphical
  session. A missing Metal device leaves rendering unverified even when the
  bundle and command-line checks pass. Track Developer ID signing and
  notarization separately from ad hoc CI signing.

See the [Roots GUI Apple Silicon build and bundle checks](https://github.com/LuganoPlanB/bitcoin-roots-gui/blob/43027d0e5f6e12fd4a4bae8d7aa93e8305d6803c/docs/macos-build.md).
