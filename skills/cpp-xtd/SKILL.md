---
name: cpp-xtd
description: "Build or maintain modern C++ projects that use Gammasoft xtd. Use for xtd.core, xtd.drawing, xtd.forms, xtd.tunit, xtdc, or an xtd CMake consumer, including choosing APIs supported by the project's version and platform."
---

# C++ with xtd

1. Find the dependency the target actually builds against. Check its CMake configuration, installed prefix or source pin, C++ standard, OS and GUI toolkit. An installed `xtdc --info` describes that tool's installation. Compare it with the package CMake resolved. Keep an existing project's entry point, STL types and build conventions where they already fit.
2. Select the narrowest relevant reference below. For an unfamiliar API, find its public declaration, an example of the operation, and the implementation or test for the target backend. Upstream's status tables distinguish **Usable** and **Complete** from planned features. They describe types, can lag the code and sometimes link to old filenames.
3. In a matching source checkout, run the optional read-only lookup from the skill directory. It finds declarations, status rows, example projects and tests, including names shared by several namespaces.

   ```sh
   python3 scripts/lookup.py /path/to/xtd xtd::forms::horizontal_layout_panel
   ```

   Without a checkout, start with the installed headers and package examples. For a member, look up its enclosing type and read the overload, including the return type and ownership. A header or progress icon alone cannot establish runtime support. If a feature is incomplete, use an implemented xtd primitive or an existing project dependency that meets the requirement.
4. Exercise the change through the project's normal target. Check the CLI's output and exit code, the GUI action and repaint, the image produced, or the named tunit cases as appropriate.

| Task | Read |
| --- | --- |
| Choose a revision, consume the SDK, scaffold with xtdc, generate resources or settings | [Build and version compatibility](references/build.md) |
| Text and Unicode, collections, LINQ and ranges, files, console, diagnostics, threading, sockets | [Core library](references/core.md) |
| Desktop controls, ownership, events, layout, dialogs, UI dispatch, graphics and themes | [Forms and drawing](references/desktop.md) |
| Fixtures, checks, filters, runner exit status and CTest | [tunit](references/tunit.md) |

The recipes use the [reviewed 1.0 development revision](https://github.com/gammasoft71/xtd/tree/3ea373359f7a92885d8abd88d397fc23fa1cad7e). For a project pinned to the [0.1.2 beta](https://github.com/gammasoft71/xtd/tree/v0.1.2-beta), use that tag's headers and examples.
