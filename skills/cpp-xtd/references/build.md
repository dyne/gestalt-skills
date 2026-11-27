# Consume the project's xtd SDK

| Dependency in the project | Consequence |
| --- | --- |
| `v0.1.2-beta` | Upstream describes a C++17/20 framework. For example, `src/xtd.core/include/xtd/io/file.h` declares operations using `xtd::ustring`. Consult the tag's examples for include names, strings and build switches. |
| Reviewed development commit, CMake project version 1.0 | The public version check requires C++20. The CMake helper defaults to C++23, and accepts `-DXTD_BUILD_CPP_STANDARD=20` for a C++20 build. `<xtd/string>` defines `xtd::string`. The project's version field also exists on unreleased commits. |

Use the installed SDK's headers and binaries together. Upstream's `<xtd/xtd>` umbrella is generated for the configured platform. In a public header, include the individual type you use, such as `<xtd/io/file>` or `<xtd/forms/button>`. Upstream examples often rely on `XTD_ENABLE_IMPLICIT_USING_NAMESPACES`, which the CMake helpers enable by default. Use qualified names or local using-declarations. At the reviewed pin the tunit umbrella itself uses an unqualified type in `expressions/args.hpp` when implicit namespaces are off. The tunit recipe uses focused headers that compile in that configuration.

For a beta maintenance patch, open the tagged example before copying a newer recipe. For instance, `hello_world_label` at `v0.1.2-beta` adds its form member with `controls().push_back(label)`; the development collection supports `controls().add(label)`. Both revisions' console examples use `find_package(xtd REQUIRED)` and `target_type(CONSOLE_APPLICATION)`.

## One consumer target

With an installed development SDK, place this file beside `main.cpp`. The target takes the project name. For a small interactive desktop app choose `GUI_APPLICATION`, and for a tunit executable choose `TEST_APPLICATION`.

```cmake
cmake_minimum_required(VERSION 3.20)
project(line_count LANGUAGES CXX)
find_package(xtd REQUIRED)
add_sources(main.cpp)
target_type(CONSOLE_APPLICATION)
```

```sh
cmake -S . -B build -Dxtd_DIR=/path/to/installed/prefix/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

`xtd_DIR` is the directory **containing** `xtdConfig.cmake`. Omit it when the package is already found. The config loads exported targets and `xtd_commands.cmake`. The latter sets directory-wide options. In an existing multi-target build, keep package setup in the consuming subdirectory if sibling targets need different settings. The helper creates the executable and links the `xtd` target. Put `add_sources`, `add_references` and `target_*` settings before `target_type`. Give each helper-managed executable its own project directory. A plain CMake application with its own target can link the installed target, e.g. `target_link_libraries(my_app PRIVATE xtd.core)`, after package discovery. Verify the export in that SDK. Plain targets own their entry point, resources and test registration.

For a new project with the tool installed, `xtdc new gui my_app` creates a desktop starter. Run `xtdc new --help` to select another template. In an existing project read its CMake files before considering generation. Keep one entry point per executable. Both a normal C++ `main` and a class function registered through `startup_(...)` appear in examples.

## What a source build needs

Check `src/CMakeLists.txt` and the selected native component's CMake files at the pin. On development Linux, even `xtd.core.native.linux` requires the GTK 3 development module (`pkg-config --modversion gtk+-3.0`) and links ALSA. Desktop drawing requires wxWidgets 3.2 at this revision. The wxWidgets toolkit is the supported desktop backend. Qt, GTK, FLTK, AppKit and Win32 backend directories include development work. Native-looking controls can still use wxWidgets.

Desktop builds include core, drawing, forms and tunit. The source build excludes the drawing/forms projects on Android, iOS, Haiku and SerenityOS at this revision. Check the specific target toolchain and upstream CI for core/tunit availability. Some beta-only build switches such as `XTD_BUILD_LIBRARIES_XTD_FORMS` are absent from the development root. A CLI target type in a consumer does not switch off the SDK's own build dependencies.

## Resources, settings and installation

The helper reads `properties/resources.cmake` for named assets, `properties/resource_strings.cmake` for localizable strings and `properties/settings.cmake` for typed settings. It generates C++ accessors on configuration. Edit the definitions and reconfigure. For example, `resource(logo "resources/logo.png")` registers an asset, while `setting(scale int USER "2")` defines a user setting. Use the generated namespace and accessor names from your project. In the settings example the application updates `settings::default_settings()` and calls `.save()` to persist changes. Package resources and locales through the project's install rules, then open an asset and reload a setting from an installed launch outside the source directory.

Consult `examples/xtd.cmake.examples/project_commands/{resources_command,settings_command}` for the CMake inputs and consuming code together. The implementation of target creation, generated files and installation lives in [xtd_commands.cmake](https://github.com/gammasoft71/xtd/blob/3ea373359f7a92885d8abd88d397fc23fa1cad7e/scripts/cmake/xtd_commands.cmake).
