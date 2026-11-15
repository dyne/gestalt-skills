// Original Dear ImGui patterns, baseline v1.93.0, 2026-10-31.
// These are small examples, not a framework or a complete application.
// Application rendering/backends remain the host application's responsibility.
// API sources: https://github.com/ocornut/imgui/blob/v1.93.0/imgui.h
// Demo reference: https://github.com/ocornut/imgui/blob/v1.93.0/imgui_demo.cpp

#include "core_patterns.h"
#include "misc/cpp/imgui_stdlib.h"
#include <cstring>

namespace dear_imgui_examples {

// 1. Begin and BeginChild need their matching End even when returning false.
void DrawWindowAndChild(bool& open)
{
    if (!open)
        return;
    ImGui::SetNextWindowSize(ImVec2(420.0f, 280.0f), ImGuiCond_FirstUseEver);
    if (ImGui::Begin("Scope example", &open))
    {
        ImGui::TextUnformatted("A separately scrolling child follows.");
        if (ImGui::BeginChild("body", ImVec2(0.0f, 0.0f), ImGuiChildFlags_Borders))
            ImGui::TextUnformatted("Child content");
        ImGui::EndChild();
    }
    ImGui::End();
}

// 2. Repeated labels are safe when scoped by stable model identity.
void DrawRecordRows(std::vector<Record>& records)
{
    for (Record& record : records)
    {
        ImGui::PushID(record.id);
        ImGui::Checkbox("Enabled", &record.enabled);
        ImGui::SameLine();
        ImGui::TextUnformatted(record.name.c_str());
        ImGui::PopID();
    }
}

// 3. A changing visible title retains its window identity after ###.
void DrawDynamicWindow(Record& record, bool& open)
{
    if (!open)
        return;
    const std::string title = record.name + "###record-" + std::to_string(record.id);
    if (ImGui::Begin(title.c_str(), &open))
        ImGui::Text("Application record ID: %d", record.id);
    ImGui::End();
}

// 4. The official stdlib adapter supplies a resizable mutable string.
// v1.92.9+: turning live edit off commits on validation or loss of focus.
// This controls editing policy, not domain validation of a proposed name.
bool DrawValidatedName(std::string& name)
{
    ImGui::PushItemFlag(ImGuiItemFlags_LiveEditOnInputText, false);
    const bool changed = ImGui::InputText("Name", &name);
    ImGui::PopItemFlag();
    return changed;
}

// 5. One undo record per completed drag/text-edit gesture.
// The host must explicitly finalize/cancel edit if this object/panel disappears.
void DrawGainWithUndo(Record& record, GainEdit& edit, std::vector<GainUndo>& undo)
{
    ImGui::PushID(record.id);
    const float before_this_call = record.gain;
    ImGui::SliderFloat("Gain", &record.gain, 0.0f, 1.0f, "%.3f",
                       ImGuiSliderFlags_AlwaysClamp);
    if (ImGui::IsItemActivated())
    {
        edit.active = true;
        edit.record_id = record.id;
        edit.before = before_this_call;
    }
    if (ImGui::IsItemDeactivatedAfterEdit() && edit.active && edit.record_id == record.id)
    {
        if (edit.before != record.gain)
            undo.push_back(GainUndo{record.id, edit.before, record.gain});
        edit.active = false;
    }
    else if (ImGui::IsItemDeactivated())
    {
        edit.active = false;
    }
    ImGui::PopID();
}

// 6. A property table: explicitly enter each cell and conditionally end.
void DrawPropertyTable(Record& record)
{
    ImGui::PushID(record.id);
    if (ImGui::BeginTable("properties", 2, ImGuiTableFlags_Resizable))
    {
        ImGui::TableSetupColumn("Property", ImGuiTableColumnFlags_WidthFixed, 110.0f);
        ImGui::TableSetupColumn("Value", ImGuiTableColumnFlags_WidthStretch);

        ImGui::TableNextRow();
        ImGui::TableSetColumnIndex(0);
        ImGui::AlignTextToFramePadding();
        ImGui::TextUnformatted("Name");
        ImGui::TableSetColumnIndex(1);
        ImGui::SetNextItemWidth(-FLT_MIN);
        ImGui::InputText("##name", &record.name);

        ImGui::TableNextRow();
        ImGui::TableSetColumnIndex(0);
        ImGui::TextUnformatted("Enabled");
        ImGui::TableSetColumnIndex(1);
        ImGui::Checkbox("##enabled", &record.enabled);
        ImGui::EndTable();
    }
    ImGui::PopID();
}

// Helper: stable hidden widget ID, independent text, fixed one-line row height.
// Embedded newlines in names are deliberately not supported by this example.
static bool DrawSelectionRow(const Record& record, bool selected)
{
    ImGui::PushID(record.id);
    const ImVec2 text_pos = ImGui::GetCursorScreenPos();
    const bool pressed = ImGui::Selectable("##row", selected, 0,
                                          ImVec2(0.0f, ImGui::GetTextLineHeight()));
    ImGui::GetWindowDrawList()->AddText(text_pos, ImGui::GetColorU32(ImGuiCol_Text),
                                      record.name.c_str());
    ImGui::PopID();
    return pressed;
}

// 7. The view was already filtered/sorted by the host when its data changed.
// Clip the dense view index space, while selection uses a persistent record ID.
// Record pointers must remain valid for the entire call.
void DrawFilteredList(const std::vector<Record*>& view, int& selected_id)
{
    if (ImGui::BeginChild("filtered_records", ImVec2(0.0f, 180.0f), ImGuiChildFlags_Borders))
    {
        ImGuiListClipper clipper;
        clipper.Begin(static_cast<int>(view.size()));
        while (clipper.Step())
            for (int i = clipper.DisplayStart; i < clipper.DisplayEnd; ++i)
                if (DrawSelectionRow(*view[i], selected_id == view[i]->id))
                    selected_id = view[i]->id;
    }
    ImGui::EndChild();
}

// 8. Multi-select uses view indices for ranges and record IDs for storage.
// This example assumes the view order stays fixed during the interaction.
// Dynamic reorder/filter/deletion needs the host's anchor/focus policy.
void DrawMultiSelect(const std::vector<Record*>& view, ImGuiSelectionBasicStorage& selection)
{
    selection.UserData = const_cast<std::vector<Record*>*>(&view);
    selection.AdapterIndexToStorageId = [](ImGuiSelectionBasicStorage* self, int index) {
        const auto& rows = *static_cast<const std::vector<Record*>*>(self->UserData);
        return static_cast<ImGuiID>(rows[index]->id);
    };
    if (ImGui::BeginChild("multi_records", ImVec2(0.0f, 180.0f), ImGuiChildFlags_Borders))
    {
        const int count = static_cast<int>(view.size());
        ImGuiMultiSelectIO* ms = ImGui::BeginMultiSelect(
            ImGuiMultiSelectFlags_BoxSelect1d | ImGuiMultiSelectFlags_ClearOnEscape,
            selection.Size, count);
        selection.ApplyRequests(ms);

        ImGuiListClipper clipper;
        clipper.Begin(count);
        if (ms->RangeSrcItem >= 0 && ms->RangeSrcItem < count)
            clipper.IncludeItemByIndex(static_cast<int>(ms->RangeSrcItem));
        while (clipper.Step())
        {
            for (int i = clipper.DisplayStart; i < clipper.DisplayEnd; ++i)
            {
                ImGui::SetNextItemSelectionUserData(i);
                DrawSelectionRow(*view[i], selection.Contains(static_cast<ImGuiID>(view[i]->id)));
            }
        }
        ms = ImGui::EndMultiSelect();
        selection.ApplyRequests(ms);
    }
    ImGui::EndChild();
    // Keep accidental later access from depending on this view's lifetime.
    selection.UserData = nullptr;
}

// 9. Open is an event; content submission is repeated while the popup is open.
// nullptr omits the title-bar close button. Explicit Cancel closes the modal.
// Return an intent; the host can perform deletion after its model iteration.
bool DrawDeleteConfirmation(bool& request_open)
{
    if (request_open)
    {
        ImGui::OpenPopup("Confirm deletion");
        request_open = false;
    }
    bool accepted = false;
    if (ImGui::BeginPopupModal("Confirm deletion", nullptr, ImGuiWindowFlags_AlwaysAutoResize))
    {
        ImGui::TextUnformatted("Delete the selected record?");
        if (ImGui::Button("Delete"))
        {
            accepted = true;
            ImGui::CloseCurrentPopup();
        }
        ImGui::SameLine();
        if (ImGui::Button("Cancel"))
            ImGui::CloseCurrentPopup();
        ImGui::EndPopup();
    }
    return accepted;
}

// 10. Public custom widget: layout/interaction from InvisibleButton, own visuals.
// The caller supplies a stable ID and a visible textual label alongside it.
bool DrawToggle(const char* stable_id, bool& value)
{
    const float height = ImGui::GetFrameHeight();
    const ImVec2 size(height * 1.8f, height);
    const bool pressed = ImGui::InvisibleButton(stable_id, size, ImGuiButtonFlags_EnableNav);
    const bool hovered = ImGui::IsItemHovered();
    const bool focused = ImGui::IsItemFocused();
    if (pressed)
        value = !value;
    const ImVec2 lo = ImGui::GetItemRectMin();
    const ImVec2 hi = ImGui::GetItemRectMax();
    ImDrawList* draw = ImGui::GetWindowDrawList();
    const ImGuiCol background = value ? ImGuiCol_ButtonActive
                                     : (hovered ? ImGuiCol_ButtonHovered : ImGuiCol_Button);
    draw->AddRectFilled(lo, hi, ImGui::GetColorU32(background), height * 0.5f);
    const float center_x = value ? hi.x - height * 0.5f : lo.x + height * 0.5f;
    draw->AddCircleFilled(ImVec2(center_x, lo.y + height * 0.5f), height * 0.32f,
                          ImGui::GetColorU32(ImGuiCol_Text));
    if (focused)
        draw->AddRect(lo, hi, ImGui::GetColorU32(ImGuiCol_NavCursor), height * 0.5f,
                      2.0f, ImDrawFlags_StrokeInside); // 1.93 signature/flags.
    return pressed;
}

// 11. A copied integer handle avoids exporting an object pointer in a payload.
// Resolve/validate the delivered handle in the application before acting on it.
void DrawDragDropRecord(const Record& record, int& delivered_id)
{
    DrawSelectionRow(record, false);
    if (ImGui::BeginDragDropSource())
    {
        ImGui::SetDragDropPayload("RECORD_ID", &record.id, sizeof(record.id));
        ImGui::TextUnformatted(record.name.c_str());
        ImGui::EndDragDropSource();
    }
    if (ImGui::BeginDragDropTarget())
    {
        if (const ImGuiPayload* payload = ImGui::AcceptDragDropPayload("RECORD_ID"))
            if (payload->DataSize == static_cast<int>(sizeof(delivered_id)))
                std::memcpy(&delivered_id, payload->Data, sizeof(delivered_id));
        ImGui::EndDragDropTarget();
    }
}

// 12. Register the shortcut whenever its window is submitted, not only when
// the menu happens to be open. The MenuItem shortcut string is display only.
bool DrawCommands(bool& open)
{
    if (!open)
        return false;
    bool save_requested = false;
    if (ImGui::Begin("Command example", &open, ImGuiWindowFlags_MenuBar))
    {
        save_requested = ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_S);
        if (ImGui::BeginMenuBar())
        {
            if (ImGui::BeginMenu("File"))
            {
                save_requested |= ImGui::MenuItem("Save", "Ctrl+S");
                ImGui::EndMenu();
            }
            ImGui::EndMenuBar();
        }
        ImGui::TextUnformatted("Focus this window to use its Save shortcut.");
    }
    ImGui::End();
    return save_requested;
}

} // namespace dear_imgui_examples
