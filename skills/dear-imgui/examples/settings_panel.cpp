#include "settings_panel.h"
#include "imgui.h"

namespace dear_imgui_examples {

void DrawSettingsPanel(SettingsModel& model, SettingsPanelState& panel, const char* window_title)
{
    if (ImGui::Begin(window_title, nullptr, ImGuiWindowFlags_NoSavedSettings))
    {
        ImGui::Checkbox("Enabled###enabled", &panel.draft.enabled);
        ImGui::InputInt("Amount###amount", &panel.draft.amount);
        ImGui::InputText("Name###name", panel.draft.name, sizeof(panel.draft.name));
        const char* error = SettingsError(panel.draft);
        if (error != nullptr)
            ImGui::TextUnformatted(error);
        ImGui::BeginDisabled(error != nullptr);
        if (ImGui::Button("Save###save"))
            CommitSettings(model, panel.draft);
        ImGui::EndDisabled();
        ImGui::SameLine();
        if (ImGui::Button("Cancel###cancel"))
            panel.draft = model.saved;
    }
    ImGui::End();
}

} // namespace dear_imgui_examples
