# Headless harness execution record

Executed 2026-11-15 on Linux with GCC 14.2.0, CMake 3.31.6, Ninja and Debug
builds. This record concerns `examples/headless/`, not the older automation
fixture or the whole upstream ImKit test suite. No upstream source was patched.

## Dependency combinations

| Configuration | Dear ImGui commit | Test Engine commit | ImKit commit |
| --- | --- | --- | --- |
| Core only | `c1aaac65e896a45f81f47a4d68f9959e0f86c859` (v1.93.0) | `7c808483d6f0a69b9d0843d5f4a141f0a9f74a58` | None |
| ImKit consumer | `367b2c24f399988ddafc0bb4628da0106bcc09be` (19297 docking) | `7c808483d6f0a69b9d0843d5f4a141f0a9f74a58` | `986d8d286a74fb7b2f724b9ef5d008af139aa887` (4.1.0) |

Both built `ui_tests` and `model_tests` using the local-source configure recipe
in `references/headless-testing.md` (paths relative to the skill root). Command after build:

```sh
ctest --test-dir <build-directory> -C Debug -R '^headless\.' --output-on-failure --no-tests=error
```

Core-only: exit 0, **5/5 CTest checks passed**, 0 failed, 0.05 s observed.
ImKit consumer: exit 0, **7/7 CTest checks passed**, 0 failed, 0.07 s observed.
These timings exclude compilation and are observations, not performance targets.

## Executed coverage

| CTest case | Observed contract |
| --- | --- |
| `headless.model` | Five context-free model checks, including invalid drafts leaving committed state unchanged. |
| `headless.core.settings` | One engine test: text/scalar input, staged edits, mouse Save, disabled invalid Save, keyboard Cancel, model assertions. |
| `headless.imkit.settings` | One engine test: click a real SettingToggleRow, observe a rejected request without mutation, accept a second request, edit a scalar, keyboard Save, disabled invalid Save and mouse Cancel. |
| `headless.imkit.theme` | One engine test: theme parsing warns for an unknown key, Touch/reduced-motion settings are retained, nested scopes do not compound frame height, selected style fields restore. |
| `headless.runner.failure_probe` | One intentional assertion failure; child exit 1, tested 1, passed 0, queue drained. |
| `headless.runner.no_such_case` | Child exit 1, tested 0, passed 0; no matching test cannot pass. |
| `headless.runner.count_mismatch` | Core interaction succeeds, but expected 2 versus tested/passed 1 gives child exit 1. |

The last three are successful checks of rejection behavior, not additional
passing GUI scenarios. Parsed JUnit reports confirmed the active test names
and outcomes. Each selected ImKit-build report contained three other skipped
tests (the empty selection contained four); core-build reports contained one
other skipped test (the empty selection contained two). Skipped registrations
were excluded from executed counts.

## Corrections established during validation

- The original fixture's `IMGUI_DISABLE_OBSOLETE_FUNCTIONS` made ImKit's
  compatibility AddRect/PathStroke calls fail compilation. The new shared
  `config.h` retains these overloads while keeping version guards, test hooks
  and assertions. The complete consumer then built successfully.
- A setting-row toggle lives under `enabled/row/##value`, including its table
  scope at this ImKit pin. The source-confirmed path passed the real interaction
  test; no wildcard or substitute widget was used.

## Limits

The backend was `imgui_impl_null`, with capture disabled. No GPU pixels,
physical OS input, IME, screen reader, native-window, device, editor-suite
transaction, background-worker, or Windows/macOS acceptance is established.
Reduced motion was checked as configuration, not animated pixels. The frame
budget and process timeout are configured; an actual hung callback was not
injected. Revalidate after changing dependency pins or the harness contracts.
