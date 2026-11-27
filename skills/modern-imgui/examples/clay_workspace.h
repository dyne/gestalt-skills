// Optional C++20 example. Link Clay's implementation once in the host.
#pragma once
#include "clay.h"
#include "imgui.h"
#include <cmath>

namespace modern_imgui_examples {

// Call inside a visible ImGui window. The three callbacks submit normal
// ImGui or ImKit widgets. "layout" is an initialized, idle Clay context.
template<class Navigation, class Document, class Actions>
void DrawClayWorkspace(const char* instance_id, Clay_Context& layout,
                       Navigation navigation, Document document, Actions actions)
{
    const ImVec2 origin = ImGui::GetCursorScreenPos();
    const ImVec2 area = ImGui::GetContentRegionAvail();
    if (area.x < 4 || area.y < 4) return;

    const float em = ImGui::GetFontSize();
    const float bar = ImGui::GetFrameHeight();
    const bool wide = area.x >= 40 * em;
    const bool show_chrome = area.y >= 3 * bar + 2 * em;
    const auto grow = CLAY_SIZING_GROW(0);
    const auto fixed_bar = CLAY_SIZING_FIXED(bar);
    const auto gap = static_cast<uint16_t>(std::round(em * 0.5f));

    Clay_Context* previous = Clay_GetCurrentContext();
    Clay_SetCurrentContext(&layout);
    Clay_SetLayoutDimensions({area.x, area.y});
    Clay_BeginLayout();
    CLAY(CLAY_ID("Workspace"), {.layout = {.sizing = {grow, grow},
             .childGap = gap, .layoutDirection = CLAY_TOP_TO_BOTTOM}}) {
        CLAY(CLAY_ID("Body"), {.layout = {.sizing = {grow, grow}, .childGap = gap,
                 .layoutDirection = wide ? CLAY_LEFT_TO_RIGHT : CLAY_TOP_TO_BOTTOM}}) {
            if (show_chrome) {
                CLAY(CLAY_ID("Navigation"), {.layout = {.sizing = {
                    wide ? CLAY_SIZING_FIXED(12 * em) : grow, wide ? grow : fixed_bar}}}) {}
            }
            CLAY(CLAY_ID("Document"), {.layout = {.sizing = {grow, grow}}}) {}
        }
        if (show_chrome) {
            CLAY(CLAY_ID("Actions"), {.layout = {.sizing = {grow, fixed_bar}}}) {}
        }
    }
    (void)Clay_EndLayout(ImGui::GetIO().DeltaTime);
    const auto nav_box = Clay_GetElementData(CLAY_ID("Navigation"));
    const auto doc_box = Clay_GetElementData(CLAY_ID("Document"));
    const auto bar_box = Clay_GetElementData(CLAY_ID("Actions"));
    Clay_SetCurrentContext(previous);

    const auto pane = [&](const char* id, Clay_ElementData data, auto& draw) {
        if (!data.found) return;
        const auto b = data.boundingBox;
        const ImVec2 pos(std::floor(origin.x + b.x), std::floor(origin.y + b.y));
        const ImVec2 size(std::floor(origin.x + b.x + b.width) - pos.x,
                          std::floor(origin.y + b.y + b.height) - pos.y);
        if (size.x < 4 || size.y < 4) return;
        ImGui::SetCursorScreenPos(pos);
        if (ImGui::BeginChild(id, size)) draw();
        ImGui::EndChild();
    };

    ImGui::PushID(instance_id);
    ImGui::BeginGroup();
    auto draw_navigation = [&] { navigation(wide); };
    if (show_chrome) pane("navigation", nav_box, draw_navigation);
    pane("document", doc_box, document);
    if (show_chrome) pane("actions", bar_box, actions);
    ImGui::EndGroup();
    ImGui::PopID();
}
} // namespace modern_imgui_examples
