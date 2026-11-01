#pragma once
// Original example: the model/command layer needs no ImGui context or headers.
#include <cstring>

namespace dear_imgui_examples {

struct Settings
{
    int amount = 5;
    bool enabled = false;
    char name[64] = "original";
};

struct SettingsModel
{
    Settings saved;
    int commits = 0; // In-memory commit count, not proof of persistence.
};

struct SettingsPanelState
{
    Settings draft; // Host initializes/rebases this for the selected record.
};

inline const char* SettingsError(const Settings& value)
{
    if (value.amount < 0)
        return "Amount must be nonnegative.";
    if (value.name[0] == '\0')
        return "Name is required.";
    if (std::memchr(value.name, '\0', sizeof(value.name)) == nullptr)
        return "Name must be terminated within its buffer.";
    return nullptr;
}

inline bool CommitSettings(SettingsModel& model, const Settings& draft)
{
    if (SettingsError(draft) != nullptr)
        return false;
    model.saved = draft;
    ++model.commits;
    return true;
}

// Call between NewFrame/Render. This function owns its window scope.
void DrawSettingsPanel(SettingsModel& model, SettingsPanelState& panel,
    const char* window_title = "Settings###settings");

} // namespace dear_imgui_examples
