# Adopt imgui-modern-kit

Use [imgui-modern-kit](https://github.com/AokiMotohide/imgui-modern-kit), also
called ImKit, as the preferred component and design-system layer when a suitable
API is available for the assigned Dear ImGui task. It is a C++20 static library,
not a renderer or application runner. Start with the smallest matching module;
do not convert unrelated UI simply to standardize namespaces.

## Establish availability and compatibility

1. Inspect the application's dependency declarations, actual include paths,
   `imkit::` link targets and `IMKIT_IMGUI_TARGET`. A checkout nearby does not
   mean the app consumes it. Find `include/imkit/version.h` and the component's
   header, implementation and matching example/API compile fixture.
2. Compare the host's ImGui commit, configuration and backend capabilities with
   that ImKit revision. At the snapshot below, `IMGUI_VERSION_NUM == 19297` plus
   `IMGUI_HAS_DOCK`, `IMGUI_HAS_VIEWPORT` and `IMGUI_HAS_TEXTURES` are mandatory.
   The required commit is stricter than those guards; the skill's v1.93.0 core
   examples use a different revision. Do not remove guards, substitute another
   1.93 build or enable unsupported renderer capabilities to make it compile.
3. Look up the requirement in the [component map](modern-kit-components.md).
   Prefer an existing ImKit composition, then its native-compatible widgets,
   then public ImGui composition for gaps. Preserve explicit project/user
   constraints and required interaction semantics. Record why a fallback is
   needed rather than forcing a superficially similar widget.
4. If ImKit is absent and dependency adoption is in scope, assess and pin it
   using the project's dependency mechanism. Otherwise continue with the
   available controls and identify the adoption constraint. A task to style one
   panel does not imply permission to upgrade its whole UI stack.

### Embed in an existing application

Create/reuse the host ImGui target first. For an already acquired, compatible
source dependency, adapt these target and path names:

```cmake
set(IMKIT_IMGUI_TARGET host_imgui)
set(IMKIT_BUILD_GALLERY OFF)
set(IMKIT_BUILD_DESIGN_GALLERY OFF)
set(IMKIT_BUILD_TESTS OFF)
add_subdirectory(external/imgui-modern-kit)
target_link_libraries(your_app PRIVATE imkit::imkit)
```

CMake 3.20+ and C++20 are required. Embedded mode consumes the existing target
and does not fetch or compile a second ImGui. Standalone mode can fetch pinned
dependencies; it is not the integration recipe for an existing host. Keep the
host's frame loop and backend initialization. `<imkit/imkit.h>` includes the
base widgets, themes, patterns, workflow, toast, charts, PTZ, shell and window
frame core; editor and show modules need explicit headers/targets.

For an installed SDK, follow its `find_package(imkit 4.1 CONFIG REQUIRED)`
contract and confirm architecture, compiler/toolset, CRT, ImGui revision,
defines and `imconfig.h` before setting `IMKIT_SDK_ABI_CONFIRMED=ON`.
Rebuild every consumer/static library after public structure changes,
including 4.0 to 4.1; source compatibility does not imply binary compatibility.
Do not infer Linux, another binding, or another backend's acceptance from the
published Windows/macOS packages.

## Preserve the architecture

| Layer | Use and boundary |
| --- | --- |
| `theme.h` | Host-owned copyable Theme; semantic tokens project into palette, metrics and ImGuiStyle. See [themes](modern-kit-themes.md). |
| `native.h` | Imports overloads from the pinned public ImGui header. Context/frame/debug/renderer services remain host responsibilities. |
| `widgets.h` | Styled native-compatible wrappers. Check documented exceptions, particularly Combo, instead of assuming every wrapper is a transparent alias. |
| `components.h`, `patterns.h`, `workflow.h`, `shell.h` | Reusable compositions with explicit options/state, native input and public DrawList decoration. |
| Editor and show modules | Borrowed model views/providers, retained host UI state and returned requests/events. No automatic model persistence or undo. |
| Optional platform/preview adapters | Separate targets. Borrow native windows/devices; preview renderers own only their offscreen resources. |

Keep the model, validation, selection, drafts, undo, files, workers, fonts,
textures, contexts and backend lifecycle in the application. Borrowed labels,
spans, callbacks and resources must survive the documented draw/publication
period; GPU resources must also survive draw-data consumption. Pointer-based
inputs may edit host-owned buffers directly. Request-based composites need
explicit application handling; drawing a Save action does not save anything.

Give instances stable IDs and their own state. Reset per-frame request/event
counts, handle overflow, and do not discard a terminal gesture silently. For
transactional editors, preview Begin/Update separately, validate revisions and
apply Commit atomically as one undo entry; discard Cancel. Never reallocate a
borrowed model view inside a drawing callback. Keep large buffers off the stack.

Use native interaction plus semantic tokens for missing components. Keep input,
focus, disabled behavior, clipping and IDs intact; decoration must not submit a
replacement item. Do not add a global theme/model registry or host-specific
services to a reusable widget. Skins customize painting, not input semantics.

## Verify an adopted slice

Use the [headless harness](headless-testing.md) for an initial consumer test
target; its separate execution record covers the pinned core/engine/ImKit
combination and representative interactions, not the entire component catalog.

Compile/link with the real host target and selected module headers. Test the
host's application of requests, invalid/cancel/stale-revision paths and buffer
overflow where relevant. For views, verify clipped provider calls and stable
selection; for controls, check keyboard activation, focus, disabled state and
actual change semantics. Reuse the [GUI test workflow](gui-workflow.md).

Inspect rendered output at representative widths, light/dark/high-contrast
themes, density and scale, long/translatable labels and reduced motion. Test
native windows, IME, mixed DPI, screen readers or devices when the product
depends on them. Upstream Gallery captures and synthetic IO checks are useful
examples, not evidence that this application passes. Partial accessibility
emission, pseudo RTL and a contrast check are not full accessibility acceptance.

## Source snapshot and documentation routes

Studied 2026-11-15 at commit
[`986d8d286a74fb7b2f724b9ef5d008af139aa887`](https://github.com/AokiMotohide/imgui-modern-kit/tree/986d8d286a74fb7b2f724b9ef5d008af139aa887),
reporting **ImKit 4.1.0**. Its required Dear ImGui commit is
`367b2c24f399988ddafc0bb4628da0106bcc09be` (1.93.0 WIP docking).
ImKit code/artwork is MIT; optional Inter/Noto fonts carry separate OFL notices.
This skill ships guidance, not those libraries or assets. Retain applicable
upstream notices when distributing them.

Use the pinned tree above for these paths; refresh the relevant contracts when
the consumer pin changes. The [documentation catalog](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/reference/documentation-catalog.md)
maps English/Japanese counterparts and headers. Do not copy upstream's local
maintainer build paths or repository policies into consumer applications.

| Question | Upstream paths under the pinned tree |
| --- | --- |
| Setup, ownership, frame loop, Gallery and recipes | `README.md`, `docs/getting-started/{getting-started,how-it-works,guide,gallery,examples-recipes}.md` |
| Architecture, dependencies, tokens, presets, branding, icons | `docs/architecture/{architecture,dependencies,design-system,themes,make-your-own-look,icons}.md` |
| Building a complete slice | `docs/tutorials/{build-first-app,build-settings-screen,build-node-editor,build-timeline,custom-component}.md` |
| Component contracts | `docs/components/`: basic components, workflow, shell, toasts, charts, PTZ, node editor, timeline, editor suite, show and window frame |
| API signatures and inventories | `docs/reference/{api-coverage,editor-api,widget-inventory,v3.2-api,v3.3-api,v4.0-api,v4.1-api}.md`, API JSON inventories, `include/imkit/`, `tests/*api_compile.cpp` |
| Migration, failures, evidence | `docs/reference/{migration-v3,migration-v4,troubleshooting,validation}.md`, `CHANGELOG.md`, `THIRD_PARTY_NOTICES.md` |
| Historical design intent | `docs/archive/`, `docs/proposals/`: rationale, not current API promises |

Research covered the documentation catalog, indexed guides/tutorials/components,
reference and historical documentation, and source checks of key build, theme
and widget contracts. Some pages retain earlier-version numbers or semantics;
prefer the current header/implementation and migration notes. This was source
research, not a Modern Kit build, Gallery run or consumer integration test.
