// Targeted semantic checks for two original examples, Dear ImGui v1.93.0.
// Uses the official null backend plus synthetic input. No GPU/pixel validation.
#include "core_patterns.h"
#include "imgui_impl_null.h"
#include <cstdio>

int main()
{
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    ImGui_ImplNull_Init();

    using namespace dear_imgui_examples;
    std::vector<Record> records;
    records.reserve(101);
    for (int i = 0; i < 101; ++i)
        records.push_back(Record{1001 + 3 * i, "Row " + std::to_string(i)});
    std::vector<Record*> view;
    for (Record& record : records)
        view.push_back(&record);
    ImGuiSelectionBasicStorage selection;
    bool toggle = false;
    ImVec2 toggle_center, anchor_center;

    const auto frame = [&] {
        ImGui_ImplNull_NewFrame();
        ImGui::NewFrame();
        ImGui::SetNextWindowPos(ImVec2(20.0f, 20.0f), ImGuiCond_Always);
        ImGui::SetNextWindowSize(ImVec2(420.0f, 340.0f), ImGuiCond_Always);
        if (ImGui::Begin("Semantic examples"))
        {
            DrawToggle("toggle", toggle);
            const ImVec2 lo = ImGui::GetItemRectMin();
            const ImVec2 hi = ImGui::GetItemRectMax();
            toggle_center = ImVec2((lo.x + hi.x) * 0.5f, (lo.y + hi.y) * 0.5f);

            DrawMultiSelect(view, selection);
            // EndChild exposes the child rectangle as the last item. This
            // fixed test fixture uses ordinary child padding and single lines.
            const ImVec2 child = ImGui::GetItemRectMin();
            const ImVec2 padding = ImGui::GetStyle().WindowPadding;
            anchor_center = ImVec2(child.x + padding.x + 30.0f,
                                  child.y + padding.y + ImGui::GetTextLineHeightWithSpacing() +
                                  ImGui::GetTextLineHeight() * 0.5f);
        }
        ImGui::End();
        ImGui::Render();
        ImGui_ImplNullRender_RenderDrawData(ImGui::GetDrawData());
    };

    frame();
    frame();

    io.AddMousePosEvent(toggle_center.x, toggle_center.y);
    io.AddMouseButtonEvent(ImGuiMouseButton_Left, true);
    frame();
    io.AddMouseButtonEvent(ImGuiMouseButton_Left, false);
    frame();
    const bool toggle_ok = toggle;

    io.AddMousePosEvent(anchor_center.x, anchor_center.y);
    io.AddMouseButtonEvent(ImGuiMouseButton_Left, true);
    frame();
    io.AddMouseButtonEvent(ImGuiMouseButton_Left, false);
    frame();
    const bool anchor_id_ok = selection.Size == 1 &&
                             selection.Contains(static_cast<ImGuiID>(records[1].id));

    // End navigation targets an offscreen row in the clipped 180-pixel child.
    // Shift turns that navigation into a range-selection request.
    io.AddKeyEvent(ImGuiMod_Shift, true);
    io.AddKeyEvent(ImGuiKey_End, true);
    frame();
    frame();
    io.AddKeyEvent(ImGuiKey_End, false);
    io.AddKeyEvent(ImGuiMod_Shift, false);
    frame();
    frame();
    bool range_ok = selection.Size == static_cast<int>(records.size()) - 1 &&
                    !selection.Contains(static_cast<ImGuiID>(records[0].id));
    for (std::size_t i = 1; i < records.size(); ++i)
        range_ok = range_ok && selection.Contains(static_cast<ImGuiID>(records[i].id));

    ImGui_ImplNull_Shutdown();
    ImGui::DestroyContext();
    if (!toggle_ok || !anchor_id_ok || !range_ok)
    {
        std::fprintf(stderr, "FAIL: toggle=%d anchor_stable_id=%d offscreen_shift_range=%d\n",
                     toggle_ok, anchor_id_ok, range_ok);
        return 1;
    }
    std::puts("PASS: mouse toggle; stable selection ID; Shift+End selects 100 rows from a nonzero anchor.");
    std::puts("No GPU, pixel, docking or real-platform input validation.");
    return 0;
}
