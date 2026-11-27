// Optional null-backend exercise for the same pane adapter used by the app.
#include "clay_workspace.h"
#include "imgui_impl_null.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#ifdef CHECK_IMKIT
#include <imkit/widgets.h>
#endif

static void require(bool condition, const char* reason)
{
    if (!condition) { std::fprintf(stderr, "%s\n", reason); std::exit(1); }
}

int main()
{
    std::vector<char> arena(Clay_MinMemorySize());
    auto* clay = Clay_Initialize(Clay_CreateArenaWithCapacityAndMemory(arena.size(), arena.data()),
        {800, 400}, {[](Clay_ErrorData e) {
            std::fprintf(stderr, "%.*s\n", e.errorText.length, e.errorText.chars);
            std::exit(1);
        }, nullptr});
    require(clay != nullptr, "Clay initialization failed");
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    require(ImGui_ImplNull_Init(), "null backend initialization failed");

    ImVec2 host(800, 400), nav, doc, footer, checkbox_pos, input_pos;
    bool enabled = false, editing = false, sidebar = false;
    float document_scroll = 0, navigation_scroll = 0, outer_scroll = 0;
    char name[32] = {};
    auto frame = [&] {
        ImGui_ImplNull_NewFrame();
        ImGui::NewFrame();
        ImGui::SetNextWindowPos({90, 60});
        ImGui::SetNextWindowSize(host);
        if (ImGui::Begin("Layout check")) {
            ImGui::TextUnformatted("Project settings");
            modern_imgui_examples::DrawClayWorkspace("project", *clay, [&](bool wide) {
                sidebar = wide;
                nav = ImGui::GetWindowPos();
                navigation_scroll = ImGui::GetScrollY();
                ImGui::TextUnformatted("Navigation");
            }, [&] {
                doc = ImGui::GetWindowPos();
                document_scroll = ImGui::GetScrollY();
#ifdef CHECK_IMKIT
                imkit::Checkbox("Enabled", &enabled);
#else
                ImGui::Checkbox("Enabled", &enabled);
#endif
                ImVec2 corner = ImGui::GetItemRectMin();
                checkbox_pos = {corner.x + 5, corner.y + 5};
                ImGui::InputText("Name", name, sizeof(name));
                corner = ImGui::GetItemRectMin();
                input_pos = {corner.x + 5, corner.y + 5};
                editing = ImGui::IsItemActive();
                for (int row = 0; row < 100; ++row) ImGui::Text("Record %d", row);
            }, [&] {
                footer = ImGui::GetWindowPos();
                ImGui::TextUnformatted("Ready");
            });
            outer_scroll = ImGui::GetScrollY();
        }
        ImGui::End();
        ImGui::Render();
        ImGui_ImplNullRender_RenderDrawData(ImGui::GetDrawData());
    };
    auto click = [&](ImVec2 at) {
        io.AddMousePosEvent(at.x, at.y);
        frame();
        io.AddMouseButtonEvent(0, true);
        frame();
        io.AddMouseButtonEvent(0, false);
        frame();
    };
    frame(); frame();
    require(sidebar && nav.x >= 90 && nav.y > 60 && doc.x > nav.x && doc.y == nav.y &&
            footer.x == nav.x && footer.y > doc.y, "wide pane placement");
    click(checkbox_pos);
    require(enabled, "checkbox missed in the offset host window");
    click(input_pos);
    io.AddInputCharactersUTF8("A");
    frame();
    require(editing && std::strcmp(name, "A") == 0, "native text edit");
    host.x = 320;
    frame(); frame();
    require(!sidebar && doc.x == nav.x && doc.y > nav.y && footer.y > doc.y, "narrow pane placement");
    io.AddInputCharactersUTF8("B");
    frame();
    require(editing && std::strcmp(name, "AB") == 0, "active editor lost during reflow");
    io.AddMousePosEvent(doc.x + 50, doc.y + 100);
    frame();
    io.AddMouseWheelEvent(0, -3);
    frame(); frame();
    require(document_scroll > 0 && navigation_scroll == 0 && outer_scroll == 0,
            "wheel did not scroll only the document");
    ImGui_ImplNull_Shutdown();
    ImGui::DestroyContext();
    Clay_SetCurrentContext(nullptr);
    std::puts("PASS: pane placement, click, text focus across reflow, document scrolling");
}
