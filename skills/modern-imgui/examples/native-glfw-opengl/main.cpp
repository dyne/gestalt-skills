// Copyright (c) 2026 Dyne.org foundation
// SPDX-License-Identifier: MIT
#include "native_host.h"
#include "settings_panel.h"
#ifdef NATIVE_WITH_IMKIT
#include "imkit_panel.h"
#endif
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <algorithm>

namespace n=modern_imgui_native;
struct Smoke final:n::NativeObserver {
    std::filesystem::path output;
    bool hidden{},restored{},captured{},cleaned{};
    int hidden_pumps{},queries_at_hide{};
    const std::chrono::steady_clock::time_point start=std::chrono::steady_clock::now();
    bool CaptureFramebuffer() const override { return true; }
    void Idle(n::NativeHost&,const n::NativeFrame&) override;
    void Frame(n::NativeHost&,const n::NativeFrame&) override;
    void Teardown(const n::NativeTeardown& t) override {
        cleaned=t.renderer_cleared && t.platform_cleared && t.textures_released && t.imgui_cleared && t.context_cleared;
    }
};
#include <GLFW/glfw3.h>
void Smoke::Idle(n::NativeHost& host,const n::NativeFrame& f) {
    if(std::chrono::steady_clock::now()-start>std::chrono::seconds(10))throw std::runtime_error("native smoke wall-clock deadline");
    if(hidden && !restored) {
        if(f.frame_extents_queries!=queries_at_hide)throw std::runtime_error("frame extents queried while hidden");
        if(++hidden_pumps==3){glfwShowWindow(host.Window());restored=true;}
    }
}
void Smoke::Frame(n::NativeHost& host,const n::NativeFrame& f) {
    if(f.gl_error || !f.font_texture)throw std::runtime_error("actual renderer/font texture unavailable");
    if(f.rendered_frames==3)glfwSetWindowSize(host.Window(),1000,700);
    if(f.rendered_frames==5){queries_at_hide=f.frame_extents_queries;hidden=true;glfwHideWindow(host.Window());}
    if(f.rendered_frames==8)host.SetFontScale(1.5F);
    if(f.rendered_frames==12) {
        if(!restored || f.effective_scale<1.5F || f.rgba.size()!=size_t(f.framebuffer_width)*f.framebuffer_height*4)throw std::runtime_error("lifecycle/readback contract failed");
        std::filesystem::create_directories(output);
        std::ofstream image(output/"native.ppm",std::ios::binary);image<<"P6\n"<<f.framebuffer_width<<' '<<f.framebuffer_height<<"\n255\n";
        for(int y=f.framebuffer_height-1;y>=0;--y)for(int x=0;x<f.framebuffer_width;++x)image.write(reinterpret_cast<const char*>(f.rgba.data()+(size_t(y)*f.framebuffer_width+x)*4),3);
        if(!image)throw std::runtime_error("capture write failed");
        std::ofstream(output/"renderer.json")<<"{\"renderer\":\""<<host.Renderer()<<"\",\"imguiVersion\":\""<<IMGUI_VERSION<<"\",\"frames\":"<<f.rendered_frames<<",\"effectiveScale\":"<<f.effective_scale<<",\"hiddenRestored\":true}\n";
        captured=true;host.RequestClose();
    }
}
int main(int argc,char** argv) {
    Smoke smoke;
    try {
        const bool test=argc==3 && std::string_view(argv[1])=="--smoke";
        if(argc!=1 && !test)throw std::runtime_error("usage: native_example [--smoke OUTPUT_DIRECTORY]");
        if(test)smoke.output=argv[2];
        dear_imgui_examples::SettingsModel model;
#ifdef NATIVE_WITH_IMKIT
        modern_imgui_examples::PanelState panel;
#else
        dear_imgui_examples::SettingsPanelState panel;
#endif
        { n::NativeHost host({},test?&smoke:nullptr,[&](float scale) {
            ImGui::SetNextWindowPos({20,20},ImGuiCond_Always);
#ifdef NATIVE_WITH_IMKIT
            modern_imgui_examples::DrawSettingsPanel(model,panel,scale);
#else
            const auto available=ImGui::GetMainViewport()->WorkSize;
            ImGui::SetNextWindowSize({std::min(480*scale,std::max(100.F,available.x-40)),std::min(320*scale,std::max(100.F,available.y-40))},ImGuiCond_Always);
            dear_imgui_examples::DrawSettingsPanel(model,panel);
#endif
          });host.Run(); }
        if(test && (!smoke.captured || !smoke.cleaned))throw std::runtime_error("native capture/teardown incomplete");
        if(test)std::cout<<"native smoke passed: real framebuffer, hide/restore, resize, scale, resource teardown\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
