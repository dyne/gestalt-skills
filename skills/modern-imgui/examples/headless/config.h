#pragma once
#define IMGUI_ENABLE_TEST_ENGINE
#define IMGUI_TEST_ENGINE_ENABLE_COROUTINE_STDTHREAD_IMPL 1
#define IMGUI_TEST_ENGINE_ENABLE_CAPTURE 0
#define IMGUI_TEST_ENGINE_ENABLE_IMPLOT 0
// ImKit 4.1 uses the pinned core's compatibility drawing overloads.
// Do not reuse automation_config.h's IMGUI_DISABLE_OBSOLETE_FUNCTIONS here.
