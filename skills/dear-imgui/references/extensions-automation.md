# Extensions, frameworks and semantic automation

Snapshot: 2026-10-31. The 18 records in [extensions.json](extensions.json) retain
upstream/release pins and research scope; they are candidates to investigate,
not installed dependencies or runtime compatibility certificates. Do not import
every extension into an application or create an instruction module for an
unadopted library merely because it appears in the catalog.

| Need | Starting candidates and distinction |
| --- | --- |
| Plotting | ImPlot; ImPlot3D for the distinct 3D scope. Check their contexts, headers and exact compatibility pins. |
| Scene transforms | ImGuizmo; verify matrix conventions, input ownership and one undo gesture. |
| Node editing | imnodes or imgui-node-editor; compare actual interactions/persistence/internal coupling, not stars or old wiki labels. |
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

Inspect the engine's matching checkout/configuration before integration. Keep
core test hooks/configuration consistent; create, start, drive and destroy the
engine in the lifecycle order its example requires. Register tests after their
UI functions are available, and execute them through the engine's frame/yield
model rather than issuing unsynchronized clicks from arbitrary worker code.
Use stable semantic item paths, bring items into view and establish focus,
popup and window state before actions. A screen-coordinate click or a sleep
alone is not a reliable semantic test. Follow local headers for captures,
coroutine dependencies and application integration; do not invent APIs.

The engine's license is distinct from the core library's MIT license. Check
the exact engine, test-suite, helper and asset notices and the user's usage
terms before adoption; do not infer eligibility from core licensing or make
unnecessary dependency/licensing changes as part of a small UI task.

Sources: [official extension directory](https://github.com/ocornut/imgui/wiki/Useful-Extensions),
[Test Engine](https://github.com/ocornut/imgui_test_engine),
[ImPlot](https://github.com/epezent/implot),
[ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo),
[Bundle](https://github.com/pthom/imgui_bundle).
