# Headless behavior tests

Use the bundled `examples/headless/CMakeLists.txt` when a
project needs an initial interaction-test setup. Reuse an existing application
test runner when one already works. No display server, GPU, screenshot tool or
network download is needed to configure and run this fixture with local sources.

## Configure once, then run one target

Prerequisites: CMake 3.20+, a C++20 compiler, threads and compatible local
Dear ImGui/Test Engine checkouts. ImKit is optional. Consult the Test Engine's
separate license before adoption; it is not covered by Dear ImGui's MIT license.

From the `modern-imgui` skill directory, use an application-owned build path
**outside the installed skill**:

```sh
cmake -S examples/headless -B /path/to/app/build/ui-tests \
  -DCMAKE_BUILD_TYPE=Debug \
  -DIMGUI_DIR=/path/to/imgui \
  -DIMGUI_TEST_ENGINE_DIR=/path/to/imgui_test_engine \
  -DIMKIT_DIR=/path/to/imgui-modern-kit
cmake --build /path/to/app/build/ui-tests --config Debug --target ui_tests model_tests
ctest --test-dir /path/to/app/build/ui-tests -C Debug \
  -R '^headless\.' --output-on-failure --no-tests=error
```

Omit `IMKIT_DIR` for core-only tests. A new build directory prevents stale
dependency/configuration objects. The project downloads nothing and uses the
host test ImGui target when embedding ImKit. Build only the named targets;
there is no need to build the Gallery or every optional editor module.

| Purpose | Source baseline |
| --- | --- |
| ImKit | `986d8d286a74fb7b2f724b9ef5d008af139aa887` (4.1.0) |
| Its required ImGui | `367b2c24f399988ddafc0bb4628da0106bcc09be` (19297, docking) |
| Test Engine | `7c808483d6f0a69b9d0843d5f4a141f0a9f74a58` |

See `evals/headless-validation.md` for tested combinations
and limitations. Other pins need their own build/run; version guards alone do
not establish compatibility. The older `automation_main.cpp` remains a separate
v1.93.0 example. Do not reuse its obsolete-function-disable setting for ImKit
4.1, which uses compatibility drawing overloads at its required core revision.

## Add an application journey

1. Keep model validation/commands testable without ImGui. Share the production
   drawing function with `GuiFunc`; include its actual source in the test target.
   Replace the example panel with that function rather than duplicating its UI.
2. In `examples/headless/tests.cpp`, register a test and put fresh
   model/panel state in `SetVarsDataType<T>`. Use stable `###` IDs and model keys.
3. Drive actions through `TestFunc`, then assert committed state or a fake
   service's observed request. Direct model assignment is setup, not evidence
   that an interaction worked. Use observable completion with bounded waits for
   asynchronous operations; the runner's fixed frame time is not a worker clock.
4. Add a CTest case selecting the intended category with the exact expected
   executed count. Keep reports unique per test/process. The example
   `add_ui_case` expects one test in each category; adjust deliberately when
   extending it.

```cpp
ctx->SetRef("###settings");
ctx->ItemInputValue("###amount", 42);
IM_CHECK_EQ(state.model.commits, 0);
ctx->ItemClick("###save");
IM_CHECK_EQ(state.model.saved.amount, 42);
IM_CHECK_EQ(state.model.commits, 1);
```

Keep `examples/headless/runner.cpp` as infrastructure. Its
`FILTER REPORT.xml EXPECTED_COUNT` arguments are this fixture's interface,
not automatic flags supported by every ImGui application. Build all core,
backend, engine, ImKit and drawing units with the same `config.h`, including
test hooks and the application's layout-affecting ImGui defines. Do not link
production objects built with a different configuration. Assertions remain
enabled, captures are disabled, and the null backend services texture requests
without producing pixels. Per-run ini persistence is disabled.

## Check the right contracts

| Layer | Representative assertions |
| --- | --- |
| Model | Invalid data leaves committed state unchanged; commands reject independently of disabled UI. |
| Core UI | Type, click, keyboard activation, selection, Save and Cancel change the intended application state. |
| ImKit controls | Requests are observed and applied by the host; pointer-based inputs edit drafts; custom controls use click/nav plus model assertions unless checkable test metadata exists. |
| ImKit editors | Complete batches, revision rejection, Begin/Update drafts, Commit/Cancel, one undo record and explicit overflow handling. Add cases for the module actually used. |
| Theme | Parse warnings, density/token projection, repeated scaling and scope restoration; assert reduced-motion policy separately from rendered animation. |

The fixture includes model checks, core Save/Cancel, ImKit toggle requests and
Save/Cancel, plus theme parsing/nested-scope checks. It does not exercise every
editor, widget or theme state. See [automation](automation.md) for action APIs
and [component contracts](modern-kit-components.md) for adoption-specific traps.

## Keep results small and failures inspectable

CTest prints a short success summary and expands failed cases. Each runner
prints selected filter, executed/passed/expected counts, remaining queue,
frame count and report path. Engine failure logs identify actions/assertions;
JUnit XML and CTest's `Testing/Temporary/LastTest.log` retain detail.
Use the failing CTest name with `-R` for diagnosis, not the full suite each time.

The runner returns nonzero for failures, count mismatch, an empty selection,
an undrained queue or a missing report. A 5,000-frame limit and CTest's 30-second
process timeout cover different stalls. When invoking the binary directly,
supply an outer process timeout too. JUnit includes unselected tests as skipped:
count executed identities and outcomes, not every `testcase` element.

Five CTest harness checks run a failing assertion, an unknown filter, a
successful selection with the wrong expected count, an undrained queue and a
held callback stopped by a real outer wall-clock timeout. The first four pass
only when the child returns exit1 with the exact expected counts and a report;
the timeout probe additionally requires its callback-entry marker and observed
process timeout. These are
failure-handling checks, not successful GUI
journeys. Keep them when adapting the runner so CI cannot silently pass zero
tests, accept incomplete selection or swallow a failure. Queue counts are read
before aborting the engine. The runner's optional final `undrained` argument is
a negative-test seam, not a production execution mode. The example omits the
unused `imgui_demo.cpp` compilation unit.

Headless results establish simulated interaction and application contracts.
Use rendered/platform tests separately for appearance, OS input, IME, screen
readers, multi-monitor DPI, native windows and devices. These tests neither
need nor claim a framebuffer.

Use the separate [native starter](native-testing.md) for actual Linux window,
renderer, teardown and capture evidence; it does not replace these model tests.
