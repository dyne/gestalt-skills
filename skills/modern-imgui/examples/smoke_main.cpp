// Headless smoke exercise for the original patterns, against Dear ImGui v1.93.0.
// Uses the official null backend. It does not test GPU output or interaction.
#include "core_patterns.h"
#include "imgui_impl_null.h"
#include <cstdio>

int main()
{
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = nullptr; // Keep this exercise from reading/writing user layout.
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    if (!ImGui_ImplNull_Init())
        return 1;

    using namespace dear_imgui_examples;
    std::vector<Record> records{{101, "Alpha"}, {205, "Beta"}, {319, "Gamma"}};
    std::vector<Record*> view{&records[2], &records[0]}; // A precomputed view.
    ImGuiSelectionBasicStorage selection;
    GainEdit edit;
    std::vector<GainUndo> undo;
    int selected_id = records[0].id;
    int delivered_id = -1;
    bool shell_open = true, title_open = true, commands_open = true;
    bool toggle = false, popup_requested = false;

    for (int frame = 0; frame < 8; ++frame)
    {
        ImGui_ImplNull_NewFrame();
        ImGui::NewFrame();

        ImGui::SetNextWindowCollapsed(frame == 2, ImGuiCond_Always);
        DrawWindowAndChild(shell_open);
        DrawDynamicWindow(records[0], title_open);
        DrawCommands(commands_open);

        ImGui::SetNextWindowSize(ImVec2(720.0f, 920.0f), ImGuiCond_Always);
        if (ImGui::Begin("Patterns smoke"))
        {
            ImGui::PushID("record_rows");
            DrawRecordRows(records);
            ImGui::PopID();

            ImGui::PushID("string_input");
            DrawValidatedName(records[0].name);
            ImGui::PopID();

            ImGui::PushID("gain_undo");
            DrawGainWithUndo(records[0], edit, undo);
            ImGui::PopID();

            ImGui::PushID("properties");
            DrawPropertyTable(records[0]);
            ImGui::PopID();

            DrawFilteredList(view, selected_id);
            DrawMultiSelect(view, selection);
            DrawToggle("##feature", toggle);
            ImGui::SameLine();
            ImGui::TextUnformatted("Feature");

            ImGui::PushID("drag_drop");
            DrawDragDropRecord(records[0], delivered_id);
            ImGui::PopID();

            if (frame == 4)
                popup_requested = true;
            DrawDeleteConfirmation(popup_requested);
        }
        ImGui::End();

        ImGui::Render();
        ImGui_ImplNullRender_RenderDrawData(ImGui::GetDrawData());
    }

    ImGui_ImplNull_Shutdown();
    ImGui::DestroyContext();
    std::puts("PASS: 8 headless frames; no graphics or interaction validation.");
    return 0;
}
