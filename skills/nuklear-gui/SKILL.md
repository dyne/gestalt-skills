---
name: nuklear-gui
description: "Build, debug, review, and package Nuklear C/C++ graphical interfaces, especially SDL2 backends, with native layout and installed-application verification."
---

# Nuklear GUI

1. Inspect the pinned toolchain, compatible Nuklear/backend revisions, SDL
   version, supported build variants, themes and platform constraints. Preserve
   the user's dependency choices. Apply the configuration and optional-target
   boundary in the [integration reference](references/integration.md).
2. Establish the shared `NK_*` configuration, single implementation ownership,
   window/logical/framebuffer transforms, actual control bounds and consistent
   application state before changing behavior. Follow the reference's coordinate
   and layout checks for pointer, focus and synthetic-event failures.
3. Implement with SDL events/Nuklear rendering on the main thread, isolated
   worker jobs and dedicated bounded secret buffers. Apply the reference's
   cancellation, generation, queue and erasure rules where those features exist.
4. Package licensed fonts/assets with deliberate installed paths and fallback
   behavior. Launch the installed GUI outside the source tree using an isolated
   profile; add no runtime dependency or asset downloads.
5. State and execute the reference's native test matrix using the project's
   supported settings: themes, default/minimum/portrait/landscape windows,
   100%/150% font scale and 1x/2x density. Inspect screenshots, including minimum
   width + 150% font + 2x density. Combine focused model tests with real SDL event
   automation and a GUI-disabled build.
6. Report exact commands, observed behavior, inspected screenshot paths and
   untested cells. Separate model, software/Xvfb, simulated-density and physical
   display evidence. If required dependencies, assets, mapping or display access
   cannot be established, stop the affected verification and report the missing
   prerequisite; continue independent checks. Never claim native testing from
   authoring this skill or promise complete secret erasure across library/OS
   copies.
