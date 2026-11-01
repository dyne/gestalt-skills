// Original headless automation fixture: ImGui v1.93.0 and the engine pin in
// references/automation.md. This is not a GPU or OS-input test.
#include "imgui.h"
#include "imgui_impl_null.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_exporters.h"
#include "settings_panel.h"
#include <cstdio>

struct SettingsFixture
{
    dear_imgui_examples::SettingsModel model;
    dear_imgui_examples::SettingsPanelState panel;
    bool enabled = false;
    bool confirmed = false;
    bool open_confirmation = false;
};

static void RegisterAutomationExample(ImGuiTestEngine* engine)
{
    ImGuiTest* test = IM_REGISTER_TEST(engine, "skill_demo", "click_and_edit");
    test->SetVarsDataType<SettingsFixture>();
    test->GuiFunc = [](ImGuiTestContext* ctx) {
        SettingsFixture& state = ctx->GetVars<SettingsFixture>();
        dear_imgui_examples::DrawSettingsPanel(state.model, state.panel);
    };
    test->TestFunc = [](ImGuiTestContext* ctx) {
        SettingsFixture& state = ctx->GetVars<SettingsFixture>();
        ctx->SetRef("###settings");
        ctx->ItemCheck("###enabled");
        IM_CHECK(state.panel.draft.enabled);
        ctx->ItemUncheck("###enabled");
        IM_CHECK(!state.panel.draft.enabled);
        ctx->ItemInputValue("###amount", 42);
        ctx->ItemInputValue("###name", "updated");
        IM_CHECK_EQ(state.model.saved.amount, 5); // Editing must remain staged.
        IM_CHECK_STR_EQ(state.model.saved.name, "original");
        ctx->ItemClick("###save");
        IM_CHECK_EQ(state.model.commits, 1);
        IM_CHECK_EQ(state.model.saved.amount, 42);
        IM_CHECK_STR_EQ(state.model.saved.name, "updated");
        ctx->ItemInputValue("###amount", 43);
        ctx->ItemNavActivate("###save");
        IM_CHECK_EQ(state.model.commits, 2);
        IM_CHECK_EQ(state.model.saved.amount, 43);
        ctx->ItemInputValue("###amount", -1);
        ctx->ItemInputValue("###name", "temporary");
        ctx->ItemClick("###cancel");
        IM_CHECK_EQ(state.panel.draft.amount, 43);
        IM_CHECK_STR_EQ(state.panel.draft.name, "updated");
        IM_CHECK_EQ(state.model.commits, 2);
        IM_CHECK_EQ(state.model.saved.amount, 43);
    };

    test = IM_REGISTER_TEST(engine, "skill_demo", "stable_paths_and_popup");
    test->SetVarsDataType<SettingsFixture>();
    test->GuiFunc = [](ImGuiTestContext* ctx) {
        SettingsFixture& state = ctx->GetVars<SettingsFixture>();
        if (ImGui::Begin("Automation identities", nullptr, ImGuiWindowFlags_NoSavedSettings))
        {
            ImGui::PushID(42);
            ImGui::Checkbox("Localized label###enabled", &state.enabled);
            ImGui::PopID();
            if (ImGui::Button("Open confirmation"))
                state.open_confirmation = true;
            if (state.open_confirmation)
            {
                ImGui::OpenPopup("Confirm action");
                state.open_confirmation = false;
            }
            if (ImGui::BeginPopupModal("Confirm action", nullptr, ImGuiWindowFlags_AlwaysAutoResize))
            {
                if (ImGui::Button("Confirm"))
                {
                    state.confirmed = true;
                    ImGui::CloseCurrentPopup();
                }
                ImGui::EndPopup();
            }
        }
        ImGui::End();
    };
    test->TestFunc = [](ImGuiTestContext* ctx) {
        SettingsFixture& state = ctx->GetVars<SettingsFixture>();
        ctx->SetRef("Automation identities");
        ctx->ItemCheck("$$42/###enabled");
        IM_CHECK(state.enabled);
        ctx->ItemClick("Open confirmation");
        ctx->SetRef("//$FOCUSED");
        ctx->ItemClick("Confirm");
        IM_CHECK(state.confirmed);
    };

    // Separate category: deliberately fail to verify the runner/CI failure path.
    test = IM_REGISTER_TEST(engine, "skill_negative", "expected_failure");
    test->TestFunc = [](ImGuiTestContext* ctx) {
        IM_UNUSED(ctx);
        const int actual = 1;
        IM_CHECK_EQ(actual, 2);
    };
}

int main(int argc, char** argv)
{
    const char* filter = argc > 1 ? argv[1] : "skill_demo";
    const char* report = argc > 2 ? argv[2] : "automation-results.xml";
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    if (!ImGui_ImplNull_Init())
    {
        ImGui::DestroyContext();
        return 1;
    }
    ImGuiTestEngine* engine = ImGuiTestEngine_CreateContext();
    ImGuiTestEngineIO& test_io = ImGuiTestEngine_GetIO(engine);
    test_io.ConfigSavedSettings = false;
    test_io.ConfigBreakOnError = false;
    test_io.ConfigCaptureEnabled = false;
    test_io.ConfigLogToTTY = true;
    test_io.ConfigRunSpeed = ImGuiTestRunSpeed_Fast;
    test_io.ConfigFixedDeltaTime = 1.0f / 60.0f;
    test_io.ExportResultsFilename = report; // argv/literal lifetime covers Stop.
    test_io.ExportResultsFormat = ImGuiTestEngineExportFormat_JUnitXml;
    RegisterAutomationExample(engine);
    ImGuiTestEngine_Start(engine, ImGui::GetCurrentContext());
    ImGuiTestEngine_QueueTests(engine, ImGuiTestGroup_Unknown, filter);

    constexpr int frame_budget = 5000;
    int frames = 0;
    while (!ImGuiTestEngine_IsTestQueueEmpty(engine) && frames < frame_budget)
    {
        ImGui_ImplNull_NewFrame();
        ImGui::NewFrame();
        ImGui::Render();
        ImGui_ImplNullRender_RenderDrawData(ImGui::GetDrawData());
        ImGuiTestEngine_PreSwap(engine);
        // Null backend: there is no real framebuffer swap or capture here.
        ImGuiTestEngine_PostSwap(engine);
        ++frames;
    }
    const bool drained = ImGuiTestEngine_IsTestQueueEmpty(engine);
    if (!drained)
        ImGuiTestEngine_TryAbortEngine(engine);
    ImGuiTestEngineResultSummary result;
    ImGuiTestEngine_GetResultSummary(engine, &result);
    const bool passed = drained && result.CountTested > 0 &&
        result.CountTested == result.CountSuccess && result.CountInQueue == 0;
    std::printf("tested=%d success=%d remaining=%d frames=%d\n",
        result.CountTested, result.CountSuccess, result.CountInQueue, frames);
    ImGuiTestEngine_Stop(engine); // Exports configured JUnit and joins coroutine.
    ImGui_ImplNull_Shutdown();
    ImGui::DestroyContext();
    ImGuiTestEngine_DestroyContext(engine);
    std::puts("Headless engine interaction only; no pixels or OS-input verification.");
    return passed ? 0 : 1;
}
