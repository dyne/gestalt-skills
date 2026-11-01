# Styling without losing interaction

Checked 2026-11-01 against v1.93.0. Preserve the application's visual direction;
the sample palette below is an API example, not a required design.

## Choose the least expensive customization

| Desired change | Mechanism |
| --- | --- |
| Palette, density, padding, borders, rounding, alignment | Owned `ImGuiStyle`; prototype with `ShowStyleEditor` |
| Local emphasis or state | Balanced `PushStyleColor` / `PushStyleVar` and matching pops |
| Typography, icons, images, display scale | [Fonts/textures/DPI](fonts-textures.md), with licensed assets and correct lifetimes |
| Toolbar, inspector, responsive panel structure | Groups, children, tables, content-region sizing and width constraints |
| Distinct visual control | Built-in interaction plus draw-list painting; see [custom widget contracts](core-interaction.md) |
| Entirely different widget behavior, complex shaping or native accessibility | Assess explicit extensions/integration work against actual product requirements |

Dear ImGui has no built-in browser CSS cascade or HTML layout engine. Palette
and metric changes can go far; arbitrary skins, animations or novel controls
require application code, assets or explicit extensions. A drawn decoration
does not supply hit-testing, focus, keyboard behavior, editing or automation
metadata. Keep public item composition before introducing internal APIs/forks.

## Make a theme repeatable

Keep semantic tokens for surface/text/accent/danger, spacing, corner size and
font sizes in one place. Define normal, hovered, active, disabled, selected and
keyboard-focus states. Prefer existing built-in controls so navigation and
editing remain intact. Do not use color alone for validation or destructive
actions; preserve readable labels, focus indication and usable hit targets.

Apply an owned global theme outside UI submission, normally at initialization
or a settings/DPI change. Use push/pop overrides during a frame. Start from a
fresh **unscaled** baseline on each rebuild; repeatedly scaling the current
style compounds sizes. In the following single-context example, `scale` is the
chosen application content scale, not framebuffer pixel density:

```cpp
#include "imgui.h"

ImGuiStyle MakeExampleTheme(float scale)
{
    IM_ASSERT(scale > 0.0f);
    ImGuiStyle theme;
    ImGui::StyleColorsDark(&theme);
    theme.WindowPadding = ImVec2(12.0f, 12.0f);
    theme.FramePadding = ImVec2(8.0f, 5.0f);
    theme.ItemSpacing = ImVec2(8.0f, 6.0f);
    theme.FrameRounding = 4.0f;
    theme.Colors[ImGuiCol_Button] = ImVec4(0.12f, 0.30f, 0.48f, 1.0f);
    theme.Colors[ImGuiCol_ButtonHovered] = ImVec4(0.16f, 0.40f, 0.62f, 1.0f);
    theme.Colors[ImGuiCol_ButtonActive] = ImVec4(0.10f, 0.25f, 0.40f, 1.0f);
    theme.ScaleAllSizes(scale); // Metrics only; does not scale fonts.
    theme.FontScaleMain = scale;
    return theme;
}
```

At initialization, assign `ImGui::GetStyle() = MakeExampleTheme(scale)` after
creating the context. This example owns the whole style. In an existing app,
merge intentional overrides and preserve separately managed font/DPI settings;
avoid applying the same scale again through another font or backend setting.
Do not reset user preferences each frame. Save theme settings through the
application's configuration; the ImGui ini file does not serialize arbitrary
application design tokens.

Size controls relative to font/frame metrics and available content. Wrap or
reflow long/translatable text and provide constrained scrolling when needed.
Keep stable IDs and hit areas independent of decorative text/icons. For custom
widgets, verify disabled, clipped and keyboard activation as well as hover;
raw drawing or manual mouse tests alone omit these contracts.

## Test behavior and appearance separately

Keep semantic action paths stable across palettes and geometry changes. Named
actions can still find an awkward or unreadable button, so they cannot certify
design quality. Inspect the actual rendered view at representative minimum and
normal sizes, text lengths, density/font scales and interaction states.

For visual regression, pin renderer, fonts/assets, theme, scale and window
geometry; isolate ini state and freeze time-dependent data/animations. Define
expected regions/tolerance deliberately and mask only known nondeterminism.
Capture through a real framebuffer, inspect a baseline before accepting it,
and review diffs; never regenerate baselines merely to silence a failure.
GPU/font rasterization can vary across platforms: select controlled baselines
or platform-specific checks. Reuse [automation capture prerequisites](automation.md).

Sources: [style API](https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h),
[interactive style editor](https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp),
[FAQ: reskinning limits](https://github.com/ocornut/imgui/blob/v1.93.0/docs/FAQ.md#q-can-you-reskin-the-look-of-dear-imgui).
