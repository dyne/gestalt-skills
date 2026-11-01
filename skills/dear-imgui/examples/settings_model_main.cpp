// Run without ImGui: validation must also hold when a command bypasses the UI.
#include "settings_panel.h"
#include <cstdio>

int main()
{
    using namespace dear_imgui_examples;
    SettingsModel model;
    Settings draft;
    int checks = 0;
    auto check = [&checks](bool passed) { ++checks; return passed; };
    if (!check(CommitSettings(model, draft) && model.commits == 1))
        return 1;
    draft.amount = 42;
    draft.enabled = true;
    std::strcpy(draft.name, "updated");
    if (!check(CommitSettings(model, draft) && model.commits == 2 &&
        model.saved.amount == 42 && model.saved.enabled &&
        std::strcmp(model.saved.name, "updated") == 0))
        return 1;
    draft.amount = -1;
    if (!check(!CommitSettings(model, draft) && model.commits == 2 && model.saved.amount == 42))
        return 1;
    draft.amount = 42;
    draft.name[0] = '\0';
    if (!check(!CommitSettings(model, draft) && model.commits == 2 &&
        std::strcmp(model.saved.name, "updated") == 0))
        return 1;
    std::memset(draft.name, 'x', sizeof(draft.name));
    if (!check(!CommitSettings(model, draft) && model.commits == 2 &&
        std::strcmp(model.saved.name, "updated") == 0))
        return 1;
    std::printf("PASS: %d context-free settings command checks.\n", checks);
    return 0;
}
