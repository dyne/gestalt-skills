#include "imkit_panel.h"
#include <imkit/imkit.h>

namespace modern_imgui_examples {
void DrawSettingsPanel(dear_imgui_examples::SettingsModel& model, PanelState& panel, float scale)
{
    imkit::ThemeScope theme_scope(panel.theme, scale);
    ImGui::SetNextWindowSize(ImVec2(480*scale, 320*scale), ImGuiCond_Always);
    if (ImGui::Begin("Settings###imkit-settings", nullptr, ImGuiWindowFlags_NoSavedSettings))
    {
        auto& draft = panel.editor.draft;
        if (imkit::SettingToggleRow("enabled", "Enabled", "Use this configuration",
                                   draft.enabled, false, "", {&panel.theme}))
        {
            ++panel.toggle_requests;
            if (panel.apply_requests)
                draft.enabled = !draft.enabled;
        }
        imkit::InputInt("Amount###amount", &draft.amount);
        imkit::InputText("Name###name", draft.name, sizeof(draft.name));
        const char* error = dear_imgui_examples::SettingsError(draft);
        imkit::ValidationMessage(error ? error : "", error != nullptr, {&panel.theme});
        ImGui::BeginDisabled(error != nullptr);
        if (imkit::ActionButton("Save###save", imkit::ActionVariant::Primary, {}, {&panel.theme}))
            dear_imgui_examples::CommitSettings(model, draft);
        ImGui::EndDisabled();
        ImGui::SameLine();
        if (imkit::ActionButton("Cancel###cancel", imkit::ActionVariant::Secondary, {}, {&panel.theme}))
            draft = model.saved;
    }
    ImGui::End();
}
}
