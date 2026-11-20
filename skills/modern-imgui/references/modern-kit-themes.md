# Modern Kit themes, skins and assets

Use with the [adoption and version checks](modern-kit.md). Contracts below are
from the 4.1.0 snapshot, not interchangeable with the core-only style example.

## Own one theme and derive the style

Keep a host-owned `imkit::Theme`. Start with `MakeTheme(ThemePreset)` or
`MakeTheme(ColorScheme, ContrastMode, Density)`; use `ThemePresets()` to build
a picker. The thirteen presets are PrecisionLight, PrecisionDark, Graphite,
Midnight, Ocean, Forest, WarmSand, Rose, Violet, Solar, HighContrastLight,
HighContrastDark and Slate. Preserve the product's visual direction when choosing.

Persist the stable lowercase preset ID, not the enum ordinal. Resolve it with
`ThemePresetFromId` and choose a fallback for unknown or differently cased IDs.
`ThemePicker` edits a host-owned ThemePreset and returns bool changed; the host
stores and applies it separately.

| Change | Mechanism |
| --- | --- |
| Brand colours | `MakeBrandTheme(BrandPalette)` from canvas, surface, text and accent; optional colours with alpha zero are derived. |
| Accent | `SetAccent` updates accent, contrasting foreground, focus and selection together. |
| Surface/control states and typography | Edit `semantic`, `typography`, `radius`, `stroke`, `elevation`, `opacity`, then `ResolveTheme`. |
| Density | `SetDensity`: Compact, Comfortable, Touch; current control heights are 24/30/44 design pixels. Typography stays separate. |
| Targeted sizes | Optional `Theme::layout` overrides apply after density. Leave unset values to follow density; do not pre-scale them. |
| Corners | `SetCornerStyle`: Sharp, Soft, Round, Pill. |
| Motion | `motion.enabled`, `motion.reducedMotion`, durations and easing; supply host-owned `AnimationState` when needed. |
| Editor look | `Theme::editor`, plus `Theme::node` and `node_editor::MakeNodeStyle` for graph-specific choices. |

`colors` and `metrics` are derived projections. Avoid editing them alongside
the semantic tokens: `ResolveTheme`/`SetDensity` rebuild them. In a deliberate
legacy migration, a final projection override is possible but must be reapplied
after rebuilding; prefer the current layout tokens for new code.

Apply with `ApplyTheme(theme, scale)` on the current context **before NewFrame**,
outside Begin/End windows, at initialization or when settings change. It
rebuilds from unscaled values and replaces ImGuiStyle except `Alpha` and
`FontScaleDpi`. Direct style edits will be overwritten by the next application.
The documented scale range is 0.50–2.50, default 1.25; pass the host's chosen UI
scale explicitly. Monitor DPI and renderer framebuffer scaling remain host
responsibilities. Do not also scale the same metrics/fonts elsewhere.

For a live interface-size preference, keep the user setting separate from OS
content scale and renderer framebuffer scale. Commit the requested setting
through the existing preference path. At the next frame boundary, rebuild the
theme from the same base tokens, apply the effective scale once and pass the
updated theme to the components. Keep layout flexible so the scale controls
remain reachable in the minimum supported window.

Test one native Preferences journey. Increase the size with the panel open and
assert that the font grows. At the largest supported scale, use the controls in
the minimum-size window and verify that the decrease control is reachable.
Relaunch with the same isolated settings to check persistence, then reset and
verify that the default scale and sizing apply on the next frame. Exercise
invalid stored values in a context-free test.

See the [Roots GUI native Preferences test](https://github.com/LuganoPlanB/bitcoin-roots-gui/blob/d5bad7318b31bbc305461b65085f8c9989d2cff7/tests/theme/native_preferences.cpp).

For temporary appearance during UI submission, use `ThemeScope` before Begin
or around a widget group. It restores style, font and component metrics, nests
on the same live context, and must be destroyed before that context. Keep all
font/style pushes balanced inside it.

`ApplyTheme` affects ordinary ImGui controls through ImGuiStyle. It does not
install a current Theme object for all components. Pass
`ComponentOptions{&theme}` (and animation/locale/accessibility when required)
for skins, semantic overrides and hard button shadows. A small application
wrapper can consistently pass those options without introducing a global registry.

## Store or reload a custom look

`ParseTheme(text, theme)` overlays `key = value` text on a base Theme. The host
reads files, watches timestamps and persists settings; ImKit does none of those.
Reparse from a fresh base for each reload so removed keys do not linger.

```text
preset = warm-sand
corner = round
stroke.border = 3
elevation.hard = true
elevation.offset = 0 3
semantic.shadow = #4a2a18
motion.reduced = true
```

Application order is preset, then brand colours, then other keys in source
order. All four required `brand.*` colours must be present together. Unknown
keys and invalid/out-of-range values are skipped with line warnings; inspect
`ThemeParseResult` instead of reporting an entirely successful load.
`SerializeTheme` exports parser-supported tokens. Fonts, skin pointers and
editor palette values are not a complete serialized application theme; preserve
their configuration separately. Consult the pinned theme-file key table for
`layout.*`, `node.*`, motion, typography and semantic state spellings.

## Skin and decorate without replacing interaction

Use a host-owned `Skin` callback through the borrowed `theme.skin` pointer.
Return true only for the parts painted by the callback; false retains the
default. `SkinFrame` describes Button, Badge or Card geometry, state, variant
and eased hover. Labels, icons, focus, tooltips, input, accessibility and return
values stay with the component. Preserve the skin and its user data through use.

`DrawNineSlice` stretches a host texture while preserving corners;
`NineSliceQuads` supplies pure geometry. `DrawBackdropPattern` provides Dots,
Stripes or Rays; bake expensive large patterns into a texture when appropriate.
Use `DrawShadow`/`OverlayDecoration` for theme-derived shadows. A border of at
least two design pixels requests a full-strength outline; divider/table lines
remain restrained. These drawing helpers provide no resource loading or input.

For animated artwork, `SpriteSheet` describes a borrowed texture and
`SpriteState` is per-instance host state. Pass monotonic time, respect
`motion.enabled && !motion.reducedMotion`, and supply a useful rest frame.
`SpriteFrameAt`/`SpriteFrameUV` can be tested without a context.
`ProgressTrackView::thumb` can draw at the fill head; reserve `thumbHeight` so
artwork does not cover the progress label.

## Fonts, icons and lifetime

`FontSet` borrows regular/emphasis/display pointers. Load the required glyphs
into the host atlas and keep it alive. `PushTextRole`/`PopTextRole` choose the
theme's Caption, Body, Heading, Title or Mono role; headings/titles prefer
display, then emphasis, then regular. The optional
`imkit_copy_font_assets` CMake helper copies Inter/Noto Sans JP files; it does
not load fonts or provide IME. Retain their OFL notices if distributing them.

Prefer the supplied icons when a matching glyph exists. The snapshot has 321
IDs in 21 categories; inspect `GetIconCatalog()` rather than hardcoding counts.
The host uploads `GetIconAtlasPixels(size)` for **12, 16, 20, 24, 32, 48, 64**
pixels and binds all seven via `IconAtlas::SetTexture`. Use RGBA8 straight
alpha, linear filtering, clamp-to-edge and no mipmaps. There is no icon-font
merge requirement or image decoder dependency.

`Icon`, `IconButton` and `IconLabelButton` select an atlas for logical icon
size times framebuffer scale. Sizes above 64 physical pixels enlarge the last
raster. Use stable IDs and meaningful labels; a tooltip is not an OS
accessibility bridge. Missing/unbound glyph data reserves space and disables
icon buttons. Keep a separate atlas for each renderer/independent context;
`Clear` only unbinds textures. Destroy GPU resources after rendering completes.

## Check the resulting design

Run `ValidateContrast` after customisation. It checks declared token pairs,
not every composed pixel or backdrop; standard-mode projected borders can be
softer than the semantic border it validates. Keep text, shape or icons alongside
status colours, visible focus, and useful disabled explanations. Test reduced
motion, narrow layouts, long labels and real font/DPI combinations separately.

For semantic publication, pass `accessibility::AccessibilityFrame` through
`ComponentOptions::accessibility`: Begin a generation, draw, then Publish.
Keep borrowed strings/children alive through publication, handle overflow and
serialize the host-owned action queue. Optional native adapters copy snapshots
but still need host lifecycle and action handling. Some composites/patterns
have incomplete semantic or navigation coverage. `LocaleContext` is explicit;
pseudo RTL ordering is not bidirectional shaping or complete RTL support.

Sources at the [research revision](modern-kit.md):
[theme API](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/include/imkit/theme.h),
[design system](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/architecture/design-system.md),
[presets](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/architecture/themes.md),
[custom looks](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/architecture/make-your-own-look.md),
[icons](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/architecture/icons.md).
