# CMake

## Configure the intended variant

Prefer existing configure/build/test presets. Check the installed CMake version
against both project features and preset schema; schema version 6 requires
CMake 3.25, not merely the first release with preset support.

Without presets, a single-configuration example is:

```sh
cmake -S . -B build-debug -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build-debug --parallel
ctest --test-dir build-debug --output-on-failure
```

When `ccache` is found and no launcher has been explicitly selected or disabled,
append `-DCMAKE_C_COMPILER_LAUNCHER=ccache` and
`-DCMAKE_CXX_COMPILER_LAUNCHER=ccache` to the configure command for the enabled
languages. Prefer the equivalent cache variables in an existing preset when
appropriate. Keep the actual compilers unchanged; these are launcher settings,
not `CFLAGS`/`CXXFLAGS` or linker flags. Check verbose compilation for the
`ccache` invocation; use a launcher-capable generator such as Ninja or Makefiles.

For multi-configuration generators, select `--config Debug` at build time and
`-C Debug` for CTest; `CMAKE_BUILD_TYPE` does not select their configuration.
Verify tests actually ran. Request verbose build output to inspect failed
commands. Compilation-database export works with Makefile and Ninja generators;
other generators can ignore it, and unity builds need special care.

## Model requirements on targets

- Keep the existing minimum CMake version unless a needed feature requires a
  deliberate change. Declare the actual project languages. Prefer target-level
  compile features/properties, include directories, definitions and options over
  global flags. Gate compiler-specific options by compiler and language.
- Use `PRIVATE` for implementation requirements, `PUBLIC` for requirements
  shared with consumers, and `INTERFACE` for consumer-only requirements. A
  library's public headers determine what must propagate; linking successfully
  inside the source tree does not prove consumers can use it.
- Prefer imported targets from `find_package`, including `Threads::Threads`,
  over manually reconstructed include paths and library lists. With pkg-config,
  use `pkg_check_modules(... IMPORTED_TARGET ...)` and its `PkgConfig::` target.
  Keep dependency versions and fetch policy explicit; pin fetched revisions.
- For sanitizer variants, instrument the code under test at compilation and
  link its final executable/shared library with the corresponding runtime.
  Use project options or an explicit instrumentation target; avoid leaking
  diagnostic flags into installed usage requirements.

## Cross builds and installation

Choose `CMAKE_TOOLCHAIN_FILE` on initial configuration in a separate build
directory. Check target system, compilers, sysroot and package search roots;
build-machine tools must remain executable on the build machine. Do not satisfy
a target dependency accidentally with a host library. Run target tests only
with a supported runner/emulator or on the target.

For reusable packages, use relocatable build/install include interfaces,
`GNUInstallDirs`, exported namespaced targets and a package config that resolves
public dependencies. Stage an install with the project's prefix/`DESTDIR`
convention and build a small external consumer against it. Check relocation
when promised; do not embed source-tree or build-machine paths in exports.

Sources: [presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html),
[build systems](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html),
[compile commands](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html),
[packages](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html).
