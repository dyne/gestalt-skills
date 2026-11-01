# Frames, backends, drawing and platforms

Checked 2026-10-31 against v1.93.0; docking notes use the separately pinned
docking revision in the profile reference. Verify the actual backend pair.

Prefer the working stock platform/renderer backends and matching official
example before rewriting either layer. Platform code owns events, focus, IME,
cursor/window/DPI integration; renderer code owns GPU uploads, state and draw
submission. Available backend source files do not prove feature parity.
Compile matching core `imgui.cpp`, `imgui_draw.cpp`, `imgui_widgets.cpp` and
`imgui_tables.cpp`, the selected backends, and any used official adapters.
Keep configuration/type-layout macros consistent across every translation unit.

Initialize resources/context, then backends. Each UI update forwards events,
calls the example's backend `NewFrame` hooks and `ImGui::NewFrame`, submits UI,
calls `Render`, renders draw data, then presents. `Render` ends the frame;
`EndFrame` alone ends submission without requesting normal render output.
Use a current context for context-dependent calls. Follow the example for
minimized/zero-framebuffer handling and reverse ownership order during shutdown.

## Input and ownership

Enable keyboard navigation through `io.ConfigFlags |=
ImGuiConfigFlags_NavEnableKeyboard` when required. Gamepad navigation also
needs the selected backend's actual gamepad input support. A custom item's
navigation flag alone does not enable navigation for the whole application.

Always forward relevant input/focus/text events through the selected backend,
even if capture is false. `WantCaptureMouse` / `WantCaptureKeyboard` gate the
underlying application's reactions, not input delivery to ImGui. Hover tests
are not capture substitutes. Follow the header/FAQ's timing guidance, including
capture state available before the next `NewFrame`; do not assume it is only
meaningful after submission. Preserve press/release ownership when Return ends
text focus before key-up. Keyboard events and Unicode character/IME input are
different streams. Custom backends use current event-queue APIs and named keys.

One thread owns a context unless explicitly synchronized; separate contexts do
not make shared atlases/state automatically safe. `GetDrawData` remains valid
only until the next `NewFrame`. A shallow `ImDrawData` copy is insufficient for
asynchronous rendering: stage command/vertex/index data, texture requests and
resource references with explicit synchronization and GPU retirement. Dynamic
font measurement can bake glyphs and mutate state; do not assume it is read-only.

## Renderer correctness

Handle modern texture requests before resolving command texture IDs (see the
font/texture reference). Transform each clip rectangle by subtracting
`DisplayPos` and multiplying `FramebufferScale`, clamp to framebuffer bounds,
and apply the renderer's scissor origin convention. Respect index width,
`IdxOffset`, `VtxOffset`, callbacks and reset-render-state requests. Advertise
`RendererHasVtxOffset` only when implemented. Preserve/restablish the GPU state
required by the host and use the backend's documented blending/color-space path.

For custom draw primitives, check the local trailing argument order: signatures
changed around 1.92.8. In 1.93, stroke placement/antialiasing and line offsets
changed; review stroke flags and tessellation controls instead of adding old
half-pixel corrections. Validate integer/fractional coordinates, thickness,
rounding and scaling with rendered comparisons, not merely compilation.

## Docking versus OS viewports

Docking requires a supporting branch/fork and matching backends/configuration.
Submit the dockspace host consistently, including required keep-alive behavior
when its contents are hidden. Create default layouts conditionally and preserve
user `.ini` settings. `DockBuilder` is internal, not an API to rebuild user
layouts every frame. Multiple OS viewports are an additional opt-in capability,
requiring both platform and renderer support plus per-window rendering/context
restoration as shown in the example. Core docking inside one window does not
require detachable OS windows.

The research snapshot records Wayland limitations for OS viewports and problems
with some X11 window managers. Verify the actual backend/window-system support
before enabling them; retain supported single-window docking. Test focus, IME,
window movement, secondary displays and resource shutdown on the real platform.

Sources: [backends](https://github.com/ocornut/imgui/blob/v1.93.0/docs/BACKENDS.md),
[FAQ](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md),
[header](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[docking](https://github.com/ocornut/imgui/wiki/Docking),
[viewports](https://github.com/ocornut/imgui/wiki/Multi-Viewports).
