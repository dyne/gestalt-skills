# Native starter validation — 2026-11-16

This is an executed development record, not a release or cross-platform claim.
The source examples/scripts were built and run from the working skill tree;
builds and raw evidence remained outside it. No dependencies were installed,
downloaded or upgraded. Original Plan-B MIT attribution is retained.

## Selected inputs

| Input | Executed identity |
| --- | --- |
| ImGui docking | `367b2c24f399988ddafc0bb4628da0106bcc09be`, header19297 (`1.93.0 WIP`) |
| ImKit | `986d8d286a74fb7b2f724b9ef5d008af139aa887`,4.1.0 |
| GLFW | `d9d6f0f1f967807ffade6598ea9a631ebaf37a56`,3.5.1 source snapshot |
| Test Engine | `7c808483d6f0a69b9d0843d5f4a141f0a9f74a58` for headless checks only |
| Native platform | Linux X11, authenticated Xvfb, Marco/private D-Bus, software OpenGL |
| Font | ImGui built-in font; no external font asset bundled |

The local pinned production ImGui subset was combined with the matching pinned
null backend for headless validation. The initial configure correctly rejected
the missing null-backend source. An unused `imgui_demo.cpp` requirement was
removed from the headless target; its actual panels require no demo unit.
Native builds used supplied local X11 SDK headers; the starter does not supply
or install a platform SDK.

## Executed checks

| Check | Result |
| --- | --- |
| Core-only native CMake/Ninja build | Built `native_example`, Debug, `-j2` |
| ImKit-enabled native CMake/Ninja build | Built `native_example`, Debug, `-j2`, one shared core target |
| `native.lifecycle`, both builds |2/2 executions passed: actual framebuffer/font texture, resize, hidden-window recovery, font scaling and native resource teardown |
| `native.relocated_entry`, both builds |2/2 executions passed: copied actual binary, unrelated cwd, decorated window, real WM close and process settlement |
| Extended ImKit headless CTest |9/9 wrappers passed, including five rejection probes; executed registrations counted separately from unselected XML entries |
| Python native/capture helpers |13 tests passed with real native tests opted in; none skipped in this run |
| Native build isolation | Actual compiler commands and executable symbols contain no test configuration or Test Engine hooks |
| Capture utility | Actual core/ImKit framebuffers encoded, viewed and fingerprinted; explicit baseline acceptance, exact positive comparison and wrong-image rejection exercised |
| Collection checks |57/57 repository tests passed with native tests opted in; package integrity, standalone archive contents/reproducibility and structural skill validation passed |

The Python checks include malformed/missing/wrong-count captures, exact PNG RGB
round trip, raw-baseline hash drift, candidate approval boundaries, same-directory
baseline rejection and installed-skill output rejection. Real process checks
exercise a failed child with a live descendant, a held child stopped by a wall
timeout, WM startup rejection and an injected failure after observing the
actual application window. All owned groups/app processes settled; failure
counts retain `executed = passed + failed`.

Actual native source/configuration/binary hashes, JUnit, full logs, process
receipts and captures were retained at the execution workspace's
`.gestalt/evidence/modern-imgui-integration/`. Native evidence uses unique
`run-*` directories so later tests retain earlier failures. The initial core
capture exposed an undersized default panel after font scaling; explicit core
window geometry and the ImKit panel's scale parameter corrected it. Both final
captures were viewed with all controls reachable. Earlier captures/logs remain.
The positive comparison utility check uses a copied exact framebuffer; it is
not represented as a separate native repeat/determinism qualification.

## Limits

The two native cases validate this starter, not an arbitrary application's
business behavior or visual design. Save changes only the example model in
memory. The headless ImKit request/model assertions remain separate from native
renderer/window-close delivery. No arbitrary renderer/pin compatibility,
screen-reader/IME, OS drag gesture, physical GPU/monitor/mixed-DPI, Wayland,
multi-window or macOS/Windows qualification is established.

Required missing native capabilities fail; only the repository's explicitly
opt-in helper tests skip when not requested. Baseline acceptance requires a
separate explicit action after image inspection. No auto-baseline update or
third-party implementation/font redistribution is introduced.

The collection's existing path validator requires a canonical temporary path;
an earlier run through a short symlink alias produced two packaging errors.
The same managed owner directory's canonical path passed all57 tests. The
external `skills@1.5.0` discovery CLI was not cached and was not fetched; that
separate CLI discovery check remains unexecuted. Collection version0.7.0 is
retained for this local development update; no release or installation was
performed.
