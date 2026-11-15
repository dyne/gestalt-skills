# Modern Kit component selection and contracts

Apply the [adoption checks](modern-kit.md), then prefer a suitable component
below over rebuilding it. These are discovery names for the 4.1.0 snapshot;
read the exact local overload, options, implementation and matching example
before calling it. All base rows link `imkit::imkit` unless stated otherwise.

## Match the task to a component

| Need | Prefer / source header | Decision or boundary |
| --- | --- | --- |
| Styled native controls | `widgets.h`, `native.h`: Button, Checkbox, RadioButton, Selectable, tree/tab, Slider/Drag/Input, Combo | Keep native ID/focus/editing semantics; aliases and decorated wrappers are distinct. No namespace-wide search/replace. |
| Actions and state | `components.h`: ActionButton, IconActionButton, CompactIconActionButton, Toggle/Switch, IndeterminateCheckbox, Segmented, StatusBadge, CompactActionRow | Use action variants and semantic status; provide visible labels or accessible descriptions. |
| Search and numeric settings | SearchableCombo, InputScalarWithUnit, DragFloatWithUnit, InputVector3WithUnit, DragVector3WithUnit, AxisVector3Field, BeginSettingRow, ValidationMessage | Host edit buffers; native parsing; axis fields stack when narrow. AxisVector3Interaction can report edit lifecycle. |
| Commands, forms and overlays | `patterns.h`: CommandPalette, SearchField, Breadcrumbs, SplitButton, Toolbar/ResponsiveToolbar, Dialog/AlertDialog, Popover, Menu, FormField | Host commands, validation and focus state. Check keyboard/semantic coverage for the chosen pattern. |
| Large data | `patterns.h`: VirtualList, DataTable, TreeDataGrid, Pagination | Host supplies flattened visible indexes, stable IDs, clipped queries and result handling. |
| Responsive workspace | `workflow.h`: WorkspaceTabs, StepNavigator, NavigationRail, ChoiceGroup, HierarchyGroupHeader/HierarchyRow, inspector cards, SettingToggleRow, FilterChip, SectionHeader | Apply returned selection/toggle/action requests; tabs can collapse to a combo. |
| Application chrome | `shell.h`: AppBar, WorkspaceHeader, InspectorSection, AdvancedSection, BottomActionBar, BeginDiagnosticsDrawer/EndDiagnosticsDrawer, ThemePicker | Host documents, commands, fold state and saved theme choice; no docking/workspace manager. |
| Feedback and empty states | NotificationCard, InlineAlert, PersistentBanner, EmptyState, UnavailableState, RetryState, MultiSelectionBar, HelpCallout, ValidationSummary | Status and action/dismiss requests; no validation engine. |
| Progress and toasts | ProgressTrack, Progress, StageProgress, TaskProgressCard, CircularProgress; `toast.h`: ToastViewport | One host progress model, explicit cancellation/completion, owned queue and time. Prefer current APIs to deprecated overloads. |
| Compact charts | `charts.h`: DonutChart, BarChart, Gauge, Sparkline | Small summaries. Keep ImPlot/another established extension for plotting requirements these do not meet. |
| Camera and range controls | `ptz.h`: PtzControl; `range_slider.h`: RangeSlider/RangeSliderInt | Camera capabilities and commands are host supplied; range inputs edit low/high in place. |
| Side panels and image tools | ResolveRightSidePanelLayout, RightSidePanelHandle, PreviewTile, ResizableTileStrip, BeginImageViewport, ZoomToolbar, DrawOverlay | Image viewport also needs `imkit/editor_canvas.h` and `imkit::editor_core`; textures, geometry, tile sizes and shortcuts are host-owned. |
| Custom window chrome | `window_frame.h`: LayoutWindowFrame/DrawWindowFrame plus explicit style/metrics/features/content/state | Typed host requests; OS adapters are separate `imkit::window_frame_win32` / `imkit::window_frame_macos` targets. |

## Preserve the non-obvious control contracts

| Operation | Contract at the snapshot |
| --- | --- |
| BeginToolbar, BeginCard, BeginInspectorCard, BeginImageViewport | Always call the matching End, even when Begin returns false. |
| BeginSettingRow, BeginCollapsibleInspectorCard, BeginDiagnosticsDrawer | Call the matching End only when Begin returns true. |
| Native aliases / other Begin functions | Follow their own declaration; do not generalize from the pairs above. |
| `imkit::Combo` | Use its return value for changes; it does not mark the item edited, so `IsItemEdited()` is not the change signal. |
| Toggle, scalar inputs, RangeSlider | Pointer-based APIs edit host buffers. Keep staged values separate when Save/Cancel is required. |
| SettingToggleRow, ChoiceGroup, command/selection requests | Host applies the requested change. A returned request is not committed domain state. |
| ThemePicker | Edits the host's ThemePreset through a pointer and returns bool changed; the host applies/persists the new theme separately. |
| RangeSlider | Maintains low <= high, with optional minGap/step. Focused handles use +/- (Shift multiplies); arrows remain navigation. Check current headers for semantic roles where docs differ. |

For data views, rebuild sorting/filtering/expansion indexes on model events,
not by scanning all rows each draw. Providers receive a clipped range; `id`
and `cell` access should stay inside it. IDs must be stable and nonzero, text
must live through the frame, and selection ranges can remain intervals. Native
tables supply column sizing/visibility. Keep selection identity separate from
visible positions and inspect provider `apply` callbacks for synchronous edits.

Use a single `ProgressTrackView` for stage, status, fraction/value text and
supplemental text. Negative/nonfinite fractions mean indeterminate; animate
only appropriate Running states, with supplied animation and reduced-motion
policy. TaskProgressCard returns a command ID (zero means none).

For `ToastViewport`, retain queue and state per viewport/context, reset event
counts each frame, and pass monotonic time. Draw once per frame; do not also
advance that same state with UpdateToastViewport. Loading persists; success/info
default to five seconds, warning/error persist, hover/focus pauses expiry and
waiting cards do not age. Update the same ID for completion instead of creating
a second toast. Apply Action, Dismiss and Expired separately. Inspect both state
and event overflow: expiry can retry, dropped activation needs another action.
Use unique IDs even though the last duplicate wins. It draws ordinary ImGui
windows without stealing focus; covering host windows may need
`ImGuiWindowFlags_NoBringToFrontOnFocus` to keep existing toasts visible.

Chart values and labels are borrowed; a click returns an index for DonutChart
or BarChart, not a domain action. Use few labelled categories, zero-based bar
axes, and text/table alternatives for exact values. Sparkline draws at most 256
points at this revision. Charts do not publish per-segment keyboard navigation.
Gauge/CircularProgress use an unavailable ring for negative/nonfinite fractions.

PtzControl reports moving/velocity/zoom, stop, home and preset requests. Route
them through the host device layer and handle stop on release/disconnection.
Populate capabilities so unavailable axes/actions are absent. The component
does not communicate with or certify a real camera.

## Optional editor modules

| Task | Target / header | Contract |
| --- | --- | --- |
| Canvas, selection, time ruler, curves, property grid, asset browser | `imkit::editor_core`, `<imkit/editor_core.h>` | Non-owning providers, stable IDs and bounded event/scratch buffers. |
| Timeline, clip edits, monitor, mixer, colour controls | `imkit::video`, `<imkit/video.h>` | Host media, providers and transactions; UI does not decode/play/seek media itself. |
| Viewport navigation, affine gizmos, outliner, dope sheet, UV editor | `imkit::cg`, `<imkit/cg.h>` | Host scene and transforms; apply scale and affine/shear terms together. |
| Graphs, sockets, links, groups, graph layout and previews | `imkit::node_editor`, `<imkit/node_editor.h>` | Independent development API; graph snapshots and complete revisioned request batches. |
| Combined editor modules | `imkit::editor_suite` | Aggregate includes Core, Video, CG and node editor at this snapshot; inspect CMake for optional GPU previews. |
| Offscreen GPU preview | `imkit::preview_opengl3` / `imkit::preview_metal`, `<imkit/preview.h>` | Host context/device/submission; renderer owns only offscreen resources. |

Continuous editor gestures use Begin/Update/Commit/Cancel with original and
proposed values and revisions. Keep preview separate, accept only complete
valid operations, and group one gesture into one undo entry. Handle stale
revisions and overflow. Editor time uses integer Tick (705,600,000 per second)
and rational FrameRate; do not substitute accumulated floating-point seconds.
TimelineEditingProvider enables additional fades, transitions and validated
track moves. Clipboard, linked edits and track changes need atomic host policy.

For node editing, namespace is `imkit::node_editor`, not `ax::NodeEditor` or
imnodes. The library does not depend on those implementations. Keep graph
spans immutable through drawing/inspectors. Each simultaneous view/context
needs its own EditorState; there is no global current editor. Always pair
BeginEditor/EndEditor, even when clipped/invalid. EndNode and EndNodePanel
follow successful Begin calls; BeginPin returns void and always needs EndPin.
Do not nest node scopes or copy an active frame.

Prefer PinRow/PinAddRow for ordinary socket/property rows. Submit rows even at
low zoom; the component hides fine editors as needed. DrawLinks schedules
links for EndEditor after measured row positions; explicit Link calls draw
immediately and must follow relevant rows. Use MakeNodeStyle(theme),
Theme::node, Classic/Studio/Logic presets and drawing hooks for appearance
while retaining editor-owned hit areas and interaction.

Consume `operationSize` request records together, check graph identity and
revision, then accept or reject the batch. Commit changes the model/revision;
Begin/Update do not. Socket type changes/deletes do not silently repair links.
Host callbacks decide conversions/cycles and final validation; cycles are not
forbidden by default. Alignment/distribution/arrangement utilities return
proposed layout, never unsolicited persistent changes. Preview callbacks borrow
textures and report demand; the host schedules evaluation/rendering. Draw
detached previews for relevant offscreen nodes to retain their views.

DrawList mesh previews approximate occlusion. Optional GPU previews need their
own integration tests; for OpenGL, supply the current context/function table,
restore host pipeline state and Shutdown before destroying the context.

## Show, media-server and control-surface UI

Link `imkit::show` and include `<imkit/show.h>` explicitly. It depends on Editor
Core for timecode and is not included by the base umbrella header.

| Need | `imkit::show` candidates |
| --- | --- |
| Console controls | Fader, Knob, XYPad, PadGrid, MeterBar/PeakHold, HoldButton, ArmSwitch, StatusLed, ConsoleButton, ScribbleStrip |
| Live operation | CueList, GoBar, MasterBar, ClipLauncher, Mixer, TransitionBar, EffectRack, MappingTable, MessageMonitor, DeviceHealth |
| Picture buttons / custom console | ImageButton, ImageCropEditor, ControlSurface, SurfacePalette |
| LEDs and addressing | LedColorPicker, GradientEditor, PixelPreview, BudgetBar, TileMap, AddressMap, ChannelMonitor |
| Rules and schedules | RuleBuilder, VariableTable, RuleTrace, Calendar, ResourceTimeline, RecurrenceEditor, CronEditor, SolarTriggerEditor, date/time fields |
| Beats and sequences | BeatClock/TapTempo, Deck, waveforms, HotCuePads, DjChannelStrip, PitchFader, StepSequencer, Spectrum |
| Script/import tools | ScriptPastePanel, DiagnosticList, ParameterPanel, PasteImportWizard, LogView |

Handle ValueEdit started/changed/finished/cancelled phases and fixed-buffer
edits. The host owns device I/O, files, picture textures, layout, playback,
analysis and persistence. Schedule time is UTC seconds with an explicit
time-zone callback, distinct from editor Tick time. Pure rule/recurrence/cron/
geometry helpers can be tested without an ImGui context; script UI does not
execute scripts. ControlSurface operates or edits a host model, with a bounded
selection; real device/touch/OS-drop acceptance needs separate tests.

Primary sources at the [research revision](modern-kit.md):
[component documentation](https://github.com/AokiMotohide/imgui-modern-kit/tree/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/components),
[tutorials](https://github.com/AokiMotohide/imgui-modern-kit/tree/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/tutorials),
[headers](https://github.com/AokiMotohide/imgui-modern-kit/tree/986d8d286a74fb7b2f724b9ef5d008af139aa887/include/imkit),
[migration exceptions](https://github.com/AokiMotohide/imgui-modern-kit/blob/986d8d286a74fb7b2f724b9ef5d008af139aa887/docs/reference/migration-v4.md).
