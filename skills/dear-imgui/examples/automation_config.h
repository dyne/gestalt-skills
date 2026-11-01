#pragma once
// Use this same configuration for core, backend, engine and example objects.
// This fixture intentionally has no framebuffer or capture encoder.
#define IMGUI_ENABLE_TEST_ENGINE
#define IMGUI_DISABLE_OBSOLETE_FUNCTIONS
#define IMGUI_TEST_ENGINE_ENABLE_COROUTINE_STDTHREAD_IMPL 1
#define IMGUI_TEST_ENGINE_ENABLE_CAPTURE 0
#define IMGUI_TEST_ENGINE_ENABLE_IMPLOT 0
