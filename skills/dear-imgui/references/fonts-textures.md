# Fonts, images, texture updates and DPI

Research baseline: v1.93.0, checked 2026-10-31. The 1.92 transition is a renderer
contract change, not just new font syntax. Preserve an intentionally supported
legacy integration rather than calling every historical recipe invalid.

## Font size and lifetime

With modern texture-capable backends, glyphs/sizes can bake dynamically and the
atlas can grow. Use explicit `PushFont(font, base_size)` arguments: a null font
keeps the face; zero keeps the current base size. `GetFontSize` includes global
scale, so feeding it back as an unscaled base size applies scaling twice. Use
`style.FontSizeBase` for relative base sizing. The old one-argument overload
still exists in v1.93.0 unless obsolete functions are disabled.

`AddFontFromMemoryTTF` takes ownership by default. If ownership is disabled,
keep bytes alive throughout font use, including a surviving shared atlas;
freeing a temporary buffer after font registration is invalid with dynamic
baking. Inspect compressed-font helpers' distinct ownership contract. Preserve
font asset licenses. Modern merging tries sources in order: diagnose unwanted
glyph overlap with Metrics and `GlyphExcludeRanges`, rather than assuming an
icon font always wins. The latter ranges are copied; legacy `GlyphRanges`
pointers have a different lifetime. Decode UTF-8 issues separately from missing
glyphs; supplementary codepoints require the matching character-width config.
Complex shaping/RTL and screen-reader access remain stack limitations to assess.

## Texture protocol and images

Only advertise `ImGuiBackendFlags_RendererHasTextures` after implementing its
contract. Process non-null `draw_data->Textures` before binding/resolving draw
command IDs; an advanced staged renderer can supply a separately owned queue.

| Requested status | Backend action |
| --- | --- |
| `WantCreate` | Allocate/upload the GPU resource, `SetTexID`, then `SetStatus(OK)` |
| `WantUpdates` | Upload requested pixel rectangles with the full source pitch and required synchronization, then `SetStatus(OK)` |
| `WantDestroy` | Retire/destroy when no in-flight use remains, clear the backend ID, then `SetStatus(Destroyed)` following the matching backend |

Use setters and the actual backend's recreation/sharing rules. Atlas growth can
need old and new textures/descriptors simultaneously. `UnusedFrames` is not a
universal GPU fence. Partial updates still need correct barriers, upload
alignment and staging lifetimes. Setting the capability flag while retaining
only a one-time fixed-atlas upload is an incomplete migration. Legacy paths
without that capability are a distinct compatibility choice.

ImGui does not decode/upload arbitrary application images. `ImTextureRef` may
hold an application ID or backend-managed indirection; resolve it with
`ImDrawCmd::GetTexID()` at the appropriate rendering stage, after texture work.
Use the selected backend's handle representation, not another renderer's cast;
current `ImTextureID` is not universally `void*`. Retain application textures
through GPU consumption and define UV orientation/alpha/color-space semantics.

For v1.93.0 Vulkan, the current registration is
`ImGui_ImplVulkan_AddTexture(VkImageView, VkImageLayout)` with the documented
sampled-image descriptor/sampler contract. A compatibility overload can still
exist; inspect local declarations rather than asserting it cannot compile.
DX12 uses `ImGui_ImplDX12_InitInfo` and descriptor-allocation callbacks; the old
positional initializer was removed. Do not invent missing descriptors/callbacks.

## DPI

Separate base font size, content/layout scale and framebuffer pixel density.
`DisplayFramebufferScale` is not a layout-scale replacement. Apply
`style.FontScaleMain` / `style.FontScaleDpi` deliberately and scale style sizes
from an unscaled baseline; repeated `ScaleAllSizes` compounds values. In the
inspected docking header, `ConfigDpiScaleFonts` / `ConfigDpiScaleViewports` are
experimental IO booleans, not the old config flags. They do not automatically
solve every per-window padding/style issue. Use appropriate OS high-density
setup and test sharpness, geometry and monitor transitions independently.

Sources: [font docs](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FONTS.md),
[header](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[Vulkan](https://github.com/ocornut/imgui/blob/v1.93.0/backends/imgui_impl_vulkan.h),
[DX12](https://github.com/ocornut/imgui/blob/v1.93.0/backends/imgui_impl_dx12.h),
[changes](https://github.com/ocornut/imgui/blob/v1.93.0/docs/CHANGELOG.txt).
