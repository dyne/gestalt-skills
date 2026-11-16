#include "settings_panel.h"
#include "imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include <chrono>
#include <thread>
#include <cstdio>
#ifdef HEADLESS_WITH_IMKIT
#include "imkit_panel.h"
#include <cmath>
#endif

struct CoreFixture {
    dear_imgui_examples::SettingsModel model;
    dear_imgui_examples::SettingsPanelState panel;
};

void RegisterHeadlessTests(ImGuiTestEngine* engine)
{
    ImGuiTest* test = IM_REGISTER_TEST(engine, "core.settings", "save_cancel");
    test->SetVarsDataType<CoreFixture>();
    test->GuiFunc = [](ImGuiTestContext* ctx) {
        auto& s = ctx->GetVars<CoreFixture>();
        dear_imgui_examples::DrawSettingsPanel(s.model, s.panel);
    };
    test->TestFunc = [](ImGuiTestContext* ctx) {
        auto& s = ctx->GetVars<CoreFixture>();
        ctx->SetRef("###settings");
        ctx->ItemInputValue("###amount", 42);
        ctx->ItemInputValue("###name", "updated");
        IM_CHECK_EQ(s.model.commits, 0);
        IM_CHECK_EQ(s.model.saved.amount, 5);
        ctx->ItemClick("###save");
        IM_CHECK_EQ(s.model.commits, 1);
        IM_CHECK_EQ(s.model.saved.amount, 42);
        IM_CHECK_STR_EQ(s.model.saved.name, "updated");
        ctx->ItemInputValue("###amount", -1);
        ctx->ItemClick("###save");
        IM_CHECK_EQ(s.model.commits, 1); // Invalid/disabled Save must have no effect.
        ctx->ItemNavActivate("###cancel");
        IM_CHECK_EQ(s.panel.draft.amount, 42);
        IM_CHECK_EQ(s.model.commits, 1);
    };

#ifdef HEADLESS_WITH_IMKIT
    struct ImKitFixture {
        dear_imgui_examples::SettingsModel model;
        modern_imgui_examples::PanelState panel;
    };
    test = IM_REGISTER_TEST(engine, "imkit.settings", "requests_save_cancel");
    test->SetVarsDataType<ImKitFixture>();
    test->GuiFunc = [](ImGuiTestContext* ctx) {
        auto& s = ctx->GetVars<ImKitFixture>();
        modern_imgui_examples::DrawSettingsPanel(s.model, s.panel);
    };
    test->TestFunc = [](ImGuiTestContext* ctx) {
        auto& s = ctx->GetVars<ImKitFixture>();
        ctx->SetRef("###imkit-settings");
        s.panel.apply_requests = false;
        ctx->ItemClick("enabled/row/##value"); // ImKit's pinned setting row includes a table scope.
        IM_CHECK_EQ(s.panel.toggle_requests, 1);
        IM_CHECK(!s.panel.editor.draft.enabled); // Component did not mutate the input.
        s.panel.apply_requests = true;
        ctx->ItemClick("enabled/row/##value");
        IM_CHECK_EQ(s.panel.toggle_requests, 2);
        IM_CHECK(s.panel.editor.draft.enabled);
        ctx->ItemInputValue("###amount", 17);
        IM_CHECK_EQ(s.model.commits, 0);
        ctx->ItemNavActivate("###save");
        IM_CHECK_EQ(s.model.commits, 1);
        IM_CHECK_EQ(s.model.saved.amount, 17);
        IM_CHECK(s.model.saved.enabled);
        ctx->ItemInputValue("###amount", -1);
        ctx->ItemClick("###save");
        IM_CHECK_EQ(s.model.commits, 1);
        ctx->ItemClick("###cancel");
        IM_CHECK_EQ(s.panel.editor.draft.amount, 17);
        IM_CHECK_EQ(s.model.commits, 1);
    };

    // Nonvisual theme contracts can be checked on the runner's live context.
    test = IM_REGISTER_TEST(engine, "imkit.theme", "parse_scope_restore");
    test->GuiFunc = [](ImGuiTestContext*) {};
    test->TestFunc = [](ImGuiTestContext* ctx) {
        auto theme = imkit::MakeTheme(imkit::ThemePreset::PrecisionDark);
        const auto parsed = imkit::ParseTheme("density = touch\nmotion.reduced = true\ninvalid.key = 3\n", theme);
        IM_CHECK_EQ(parsed.ignored, 1);
        IM_CHECK(!parsed.warnings.empty());
        IM_CHECK(theme.density == imkit::Density::Touch);
        IM_CHECK(theme.motion.reducedMotion);
        const auto before = ImGui::GetStyle();
        float first_height = 0, second_height = 0;
        {
            imkit::ThemeScope scope(theme, 1.5f);
            first_height = ImGui::GetFrameHeight();
            // Nesting must derive from unscaled tokens, not compound the scale.
            imkit::ThemeScope nested(theme, 1.5f);
            second_height = ImGui::GetFrameHeight();
        }
        IM_CHECK(std::fabs(first_height - second_height) < 0.001f);
        IM_CHECK_EQ(ImGui::GetStyle().FramePadding.y, before.FramePadding.y);
        IM_CHECK_EQ(ImGui::GetStyle().FontScaleMain, before.FontScaleMain);
        IM_CHECK_EQ(ImGui::GetStyle().Alpha, before.Alpha);
    };
#endif

    test = IM_REGISTER_TEST(engine, "failure_probe", "intentional_failure");
    test->TestFunc = [](ImGuiTestContext* ctx) {
        IM_CHECK_EQ(1, 2); // Harness regression only; not part of a positive UI selection.
    };
    test = IM_REGISTER_TEST(engine, "timeout_probe", "held_callback");
    test->GuiFunc = [](ImGuiTestContext*) {
        std::puts("TIMEOUT_PRECONDITION_ENTERED");
        std::fflush(stdout);
        std::this_thread::sleep_for(std::chrono::seconds(60)); // Outer process timeout must stop this.
    };
}
