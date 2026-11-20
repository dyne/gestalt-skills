# Native accessibility

When the app needs a screen reader or OS-level automation, pick the target OS
and test one production dialog before extending the UI. Reuse a compatible
adapter if the stack supplies one. Check the roles, actions and keyboard
behavior the app actually needs.

1. Publish semantics from the same drawing path that submits the controls.
   Use stable model IDs and include role, name, relevant value/state, bounds
   and supported actions. If using ImKit, start with
   [semantic publication](modern-kit-themes.md#check-the-resulting-design)
   and account for custom controls.
2. Give the native adapter an owned, immutable snapshot per publication so it
   can serve queries without touching the render thread's ImGui state. Route
   actions to the UI owner and revalidate identity and current state. Report
   success after the UI owner applies the action. Retire unavailable controls
   and handle stale actions when the dialog closes or content is replaced.
3. On the intended platform, use an independent accessibility client to find
   the control, inspect its state, invoke an action and verify the application
   result. Test focus, dismissal and stale actions. For a screen-reader claim,
   run the installed reader and check its actual output and navigation.

Record the renderer, window backend, accessibility API and client separately.
For example, Linux AT-SPI checks exercise the tested Linux adapter and build.
Windows UI Automation and macOS accessibility each need their own adapter and
native checks. Rerun the relevant checks for a renderer or host change that
affects focus, coordinate conversion or event delivery.

See the [Roots GUI AT-SPI and Orca evidence](https://github.com/LuganoPlanB/bitcoin-roots-gui/blob/43027d0e5f6e12fd4a4bae8d7aa93e8305d6803c/docs/linux-accessibility.md).
