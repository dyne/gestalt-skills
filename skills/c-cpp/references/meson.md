# Meson

## Configure, build and test

Read `project()`, the existing native/cross files and options before setup. Use
the supported `meson.options` or legacy `meson_options.txt` format for the
project's minimum Meson version.

```sh
meson setup build-debug --buildtype=debug
meson compile -C build-debug
meson test -C build-debug --print-errorlogs
```

When `ccache` is found, ensure the new build uses it. Meson normally autodetects
it during initial setup, but explicit `CC`/`CXX` can bypass that detection and
another installed cache can take priority. Inspect verbose compile commands.
For explicit selection, add `--native-file ccache.ini` to `meson setup`, with
the following compiler entries (replace `cc`/`c++` with the actual toolchain):

```ini
[binaries]
c = ['ccache', 'cc']
cpp = ['ccache', 'c++']
```

Merge into the appropriate existing machine file rather than replacing its
toolchain settings or a selected wrapper. For cross compilation, put the host
compiler entries in the cross file selected by `--cross-file`; a native file
configures build-machine compilers. There is no generic `-Dccache=true` switch.
Use a fresh build directory when changing a cached compiler selection.

Use `meson configure build-debug` to inspect options and
`meson configure build-debug -Doption=value` to change an existing option.
Use `meson setup --reconfigure build-debug` when setup must be rerun. A compiler
or machine-file change warrants a separate directory rather than assuming the
cached compiler changed. The Ninja backend supplies `compile_commands.json`;
verify that it describes the intended variant before analysis.

Treat optimization, debug symbols and assertions as distinct settings.
`release` does not by itself guarantee `NDEBUG`; inspect `b_ndebug`. Select a
supported `b_sanitize` value for a separate instrumented build, preserving
project settings and runtime compatibility.

## Targets and dependencies

- Declare only required languages and supported `c_std`/`cpp_std`. Prefer
  target `dependencies`, `link_with`, include directories and arguments to
  global compiler flags. Export a reusable in-tree library interface through
  `declare_dependency()` where appropriate.
- Use `dependency()` with the required version and required/optional behavior.
  Keep tests and optional features behind existing project options; verify the
  disabled configuration when touching those boundaries.
- A `fallback: ['subproject', 'dependency_variable']` is a fallback, not a force
  switch. `default_options` configures that subproject; it does not force its
  selection. Use `--wrap-mode=forcefallback` or `--force-fallback-for=<name>`
  when deliberately testing fallbacks. Use `--wrap-mode=nofallback` to require
  external dependencies, or `nodownload` to prevent new downloads while still
  allowing already available subprojects.
- Preserve wrap revision/hash pins and existing offline policy. Updating all
  wraps is a dependency update, not a routine missing-library fix.

## Cross builds and installation

Use `--cross-file` for the host machine (where the built program runs), and
`--native-file` for build-machine configuration as needed. Verify compiler and
binutils, host machine description, sysroot and pkg-config search paths.
`sys_root` alone does not configure every compiler's sysroot flags. Keep host
libraries out of target dependency resolution. Set `exe_wrapper` only to a
working runner; report target tests as unrun when execution is unavailable.

Stage installation with `DESTDIR` and inspect installed paths and assets;
`meson install --dry-run` reports actions but does not validate the installed
program. Use the configured prefix rather than rewriting it during packaging.

Sources: [built-in options](https://mesonbuild.com/Builtin-options.html),
[cache autodetection](https://mesonbuild.com/Feature-autodetection.html),
[machine files](https://mesonbuild.com/Machine-files.html),
[subprojects](https://mesonbuild.com/Subprojects.html),
[cross compilation](https://mesonbuild.com/Cross-compilation.html).
