#pragma once
#include "settings_panel.h"
#include <imkit/theme.h>

namespace modern_imgui_examples {
// Same host model as the core example. The app may call this drawing function too.
struct PanelState {
    dear_imgui_examples::SettingsPanelState editor;
    imkit::Theme theme = imkit::MakeTheme(imkit::ThemePreset::PrecisionDark);
    bool apply_requests = true; // Host policy, also permits observing a rejected request.
    int toggle_requests = 0;
};
void DrawSettingsPanel(dear_imgui_examples::SettingsModel& model, PanelState& panel, float scale=1.0f);
}
