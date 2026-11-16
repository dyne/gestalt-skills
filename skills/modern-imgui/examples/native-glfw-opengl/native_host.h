// Copyright (c) 2026 Plan-B Foundation
// Copyright (c) 2026 Dyne.org foundation (adaptation)
// SPDX-License-Identifier: MIT
#pragma once
#include "imgui.h"
#if IMGUI_VERSION_NUM < 19297
#error This example requires the selected 19297-or-newer public font/texture APIs; verify newer pins independently.
#endif
#include <filesystem>
#include <functional>
#include <memory>
#include <span>
#include <string>
struct GLFWwindow;
namespace modern_imgui_native {
struct NativeOptions {
    int width{960}, height{640};
    bool dark{false};
    float font_scale{1};
    std::filesystem::path font_file; // Empty uses the core built-in font.
};
struct NativeFrame {
    int iteration{}, rendered_frames{}, width{}, height{}, framebuffer_width{}, framebuffer_height{};
    float dpi_x{1}, dpi_y{1}, effective_scale{1};
    bool iconified{}, decorated{}, should_close{}, space_down{}, mouse_down{}, capture_keyboard{}, capture_mouse{};
    int frame_left{}, frame_top{}, frame_right{}, frame_bottom{};
    int frame_extents_queries{};
    int texture_creates{}, texture_updates{}, live_textures{};
    unsigned int font_texture{};
    unsigned int gl_error{};
    std::span<const unsigned char> rgba; // Borrowed bottom-up framebuffer; callback lifetime only.
};
struct NativeTeardown {
    bool renderer_cleared{}, platform_cleared{}, textures_released{}, imgui_cleared{}, context_cleared{};
};
class NativeHost;
class NativeObserver {
public:
    virtual ~NativeObserver() = default;
    virtual bool CaptureFramebuffer() const { return false; }
    virtual void Idle(NativeHost&, const NativeFrame&) {}
    virtual void Frame(NativeHost&, const NativeFrame&) {}
    virtual void Teardown(const NativeTeardown&) {}
};
class NativeHost {
public:
    // Host-thread composition inside the actual backend frame. The application callback shares its real panel with tests;
    // components never own contexts or backends.
    using Draw = std::function<void(float scale)>;
    explicit NativeHost(NativeOptions options, NativeObserver* observer = nullptr, Draw draw = {});
    ~NativeHost();
    NativeHost(const NativeHost&) = delete;
    NativeHost& operator=(const NativeHost&) = delete;
    int Run();
    GLFWwindow* Window(); // Borrowed host-thread-only handle, never transferred.
    void RequestClose();
    void SetFontScale(float scale);
    void RecreateRendererResources(); // Must be outside frame submission on the owning thread.
    const std::string& Renderer() const;
private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

}
