# Desktop forms and drawing

## A form owns its interactive controls

In this `GUI_APPLICATION`, the button lives as long as the form. Clicking it changes the title. The layout follows the client area during a resize.

```cpp
#include <xtd/forms/application>
#include <xtd/forms/button>
#include <xtd/forms/form>

class counter_window : public xtd::forms::form {
public:
  counter_window() {
    text("Count 0");
    increment_.text("Increment");
    increment_.dock(xtd::forms::dock_style::fill);
    increment_.parent(*this);
    increment_.click += [this] {
      text(xtd::string::format("Count {}", ++count_));
    };
  }

private:
  int count_ = 0;
  xtd::forms::button increment_;
};

int main() {
  counter_window window;
  xtd::forms::application::run(window);
}
```

Set properties through member functions, e.g. `text()` to read and `text(value)` to write. Attach a child through `parent(container)` or `container.controls().add(child)`. The collection holds control references. Keep dynamic children in owning storage with stable addresses, especially when inserting more children. Keep a reusable delegate for `-=` when an event publisher can outlive its subscriber. Direct lambdas work for many controls; use the event's declared parameter types when you need its data, such as a mutable `paint_event_args&` for painting.

**Layout.** Start with docking for a full-width toolbar or fill panel, and anchors for controls that track particular edges. For rows and columns use `horizontal_layout_panel` and `vertical_layout_panel`. Their `control_layout_style` supports absolute, proportional and automatic sizing. See `examples/xtd.forms.examples/containers/horizontal_layout_panel` for the exact overloads and child order. On the reviewed revision the status table marks horizontal layout Complete, `flow_layout_panel` and `table_layout_panel` Started, and `data_grid_view` and `binding_source` Not started. For a small editable list, a `list_box`, editor and explicit model update may already do what a proposed bound grid would have done.

**Dialogs, menus and settings.** Give modal dialogs an owning window. For an `open_file_dialog`, set the filter, compare `show_dialog(window)` with `xtd::forms::dialog_result::ok`, then read `file_name()`. Preserve the current selection on Cancel. Share model commands between buttons and menu items. The `dialogs/open_file_dialog`, `menus_and_toolbars` and `components/application_settings` examples show working entry points.

**Workers and shutdown.** Run the message loop on the UI thread. Move blocking work off that thread, including file operations that can stall. Copy the worker's inputs before launch. Dispatch a result through the live control's `invoke`, or use `background_worker`'s completion/progress events. Keep the form, worker, captured arguments and dispatch target alive through completion. During close, request cancellation and defer destruction until completion. Joining a worker in a UI callback can deadlock if the worker needs synchronous `invoke` to finish. See `tasks/form_and_task` and `components/background_worker`. Choose `xtd::forms::timer` for UI ticks.

**Appearance.** Start with system colors/fonts and built-in controls. The sample `user_controls/button_with_style_sheet` applies `style_sheet(...)` to one control. Check supported selectors, states and properties in `docs/style_sheets_reference.md` before using web CSS syntax. Test focus, disabled state, light/dark appearance and resizing when styling affects them. `themes/application_enable_dark_mode` sets application appearance before starting the loop.

## Paint a view or produce an image

For an on-screen control, update model state, call `invalidate()`, then reconstruct the affected region in the paint event using `e.graphics()` and `e.clip_rectangle()`. Keep the event's graphics object within the callback. `events/form_paint` and `user_controls/graph_control` show form- and control-level painting.

For a PNG, create a bitmap and its drawing context. This function has no viewer or file-launch side effect.

```cpp
#include <xtd/drawing/bitmap>
#include <xtd/drawing/brushes>
#include <xtd/drawing/graphics>
#include <xtd/drawing/imaging/image_format>

void save_swatch(const xtd::string& filename) {
  using namespace xtd::drawing;
  bitmap image{48, 32};
  {
    auto canvas = graphics::from_image(image);
    canvas.clear(color::white);
    canvas.fill_rectangle(brushes::red(), rectangle{4, 4, 40, 24});
  }
  image.save(filename, imaging::image_format::png());
}
```

Use pens for outlines and brushes for filled areas. Choose the integer or floating-point geometry overload deliberately. The `graphics`, `brushes`, `fonts`, `images` and `points` groups contain minimal examples. For transforms, paths, codecs or printing, check both the public API and the selected backend. An off-screen drawing path may still require GUI toolkit initialization and a display. To verify this swatch, reload the file on the supported backend, check its 48×32 dimensions and sample a white corner and a red interior pixel. For the counter, exercise a click and a resize on an actual event loop.

Source examples for this revision are grouped under [xtd.forms](https://github.com/gammasoft71/xtd/tree/3ea373359f7a92885d8abd88d397fc23fa1cad7e/examples/xtd.forms.examples) and [xtd.drawing](https://github.com/gammasoft71/xtd/tree/3ea373359f7a92885d8abd88d397fc23fa1cad7e/examples/xtd.drawing.examples).
