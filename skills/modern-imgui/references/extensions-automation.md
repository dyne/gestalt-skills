# Extensions, frameworks and semantic automation

Snapshot: 2026-10-31. The 18 records in [extensions.json](extensions.json) retain
upstream/release pins and research scope; they are candidates to investigate,
not installed dependencies or runtime compatibility certificates. Do not import
every extension into an application or create an instruction module for an
unadopted library merely because it appears in the catalog.

The later [Modern Kit snapshot](modern-kit.md) is separate from those 18
historical records. Prefer its suitable, compatible components when available;
use the [component map](modern-kit-components.md) before selecting another
library or writing a replacement. This preference does not change the host's
dependency pin or turn an optional module into an application framework.

| Need | Starting candidates and distinction |
| --- | --- |
| Design system, styled widgets, settings, shell, compact charts and editor building blocks | imgui-modern-kit (ImKit); explicit themes and host-owned state, with a strict ImGui pin. See the adoption guide. |
| Plotting | ImPlot; ImPlot3D for the distinct 3D scope. Check their contexts, headers and exact compatibility pins. |
| Scene transforms | ImGuizmo; verify matrix conventions, input ownership and one undo gesture. |
| Node editing | Prefer ImKit's optional node editor when available and suitable; otherwise assess imnodes or imgui-node-editor against interactions, persistence and coupling. These are separate APIs, not interchangeable namespaces. |
| Application runner | Hello ImGui; its lifecycle/configuration APIs are framework APIs. |
| Coordinated C++/Python ecosystem | Dear ImGui Bundle; check its selected components, bindings and fork. |
| File dialogs/editor/bindings/remote UI | Consult the relevant catalog record and its own API/lifetime/license before adopting. |
| Semantic interaction tests | Official Dear ImGui Test Engine, with its distinct integration and licensing. |

Inspect current source, release history, maintenance evidence, patches, internal
API use and the actual feature requirement. A recent commit is not a successful
integration test. Record upstream URL, full commit, license path, owner, tested
core/backend combination and regression checks for an adopted component.
Avoid unsupported cross-version examples: released ImPlot v1.1 has `ImPlotSpec`
styling; resolve that extension's headers instead of pasting older style calls.
Bundle `BeginHorizontal` / `Spring` / StackLayout functionality is fork-specific,
not evidence that upstream ImGui exports it. Prefer ordinary compatible layout
or an explicit adopted fork rather than silently changing the dependency.

## Test Engine

Use the dedicated [UI automation guide](automation.md) for setup/lifecycle,
named paths, simulated actions, synchronization, assertions, CI and captures.
The engine's own license is distinct from core MIT. Confirm the actual
core/engine/backend combination and usage terms before adoption; the guide's
headless example tests behavior without certifying pixels or OS event delivery.

Sources: [official extension directory](https://github.com/ocornut/imgui/wiki/Useful-Extensions),
[Test Engine](https://github.com/ocornut/imgui_test_engine),
[ImPlot](https://github.com/epezent/implot),
[ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo),
[Bundle](https://github.com/pthom/imgui_bundle).
