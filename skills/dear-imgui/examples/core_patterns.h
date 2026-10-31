#pragma once

// Original examples for Dear ImGui v1.93.0. Application state is owned here.
// Include these helpers in an existing frame between NewFrame() and Render().
#include "imgui.h"
#include <string>
#include <vector>

namespace dear_imgui_examples {

struct Record {
    int id; // Stable positive application ID; never a current row index.
    std::string name;
    bool enabled = true;
    float gain = 0.5f;
};

struct GainEdit {
    bool active = false;
    int record_id = -1;
    float before = 0.0f;
};

struct GainUndo {
    int record_id;
    float before;
    float after;
};

void DrawWindowAndChild(bool& open);
void DrawRecordRows(std::vector<Record>& records);
void DrawDynamicWindow(Record& record, bool& open);
bool DrawValidatedName(std::string& name);
void DrawGainWithUndo(Record& record, GainEdit& edit, std::vector<GainUndo>& undo);
void DrawPropertyTable(Record& record);
void DrawFilteredList(const std::vector<Record*>& view, int& selected_id);
void DrawMultiSelect(const std::vector<Record*>& view, ImGuiSelectionBasicStorage& selection);
bool DrawDeleteConfirmation(bool& request_open);
bool DrawToggle(const char* stable_id, bool& value);
void DrawDragDropRecord(const Record& record, int& delivered_id);
bool DrawCommands(bool& open);

} // namespace dear_imgui_examples
