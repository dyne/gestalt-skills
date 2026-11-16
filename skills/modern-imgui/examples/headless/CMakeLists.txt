cmake_minimum_required(VERSION 3.20)
project(modern_imgui_headless LANGUAGES CXX)
enable_testing()
find_package(Threads REQUIRED)

set(IMGUI_DIR "" CACHE PATH "Local Dear ImGui source checkout")
set(IMGUI_TEST_ENGINE_DIR "" CACHE PATH "Local imgui_test_engine checkout")
set(IMKIT_DIR "" CACHE PATH "Optional local imgui-modern-kit checkout")
foreach(required IN ITEMS
    "${IMGUI_DIR}/imgui.cpp"
    "${IMGUI_DIR}/backends/imgui_impl_null.cpp"
    "${IMGUI_TEST_ENGINE_DIR}/imgui_test_engine/imgui_te_engine.cpp")
    if(NOT EXISTS "${required}")
        message(FATAL_ERROR "Missing dependency source: ${required}. Supply compatible local checkouts; this project downloads nothing.")
    endif()
endforeach()

# Every core, backend, engine, ImKit and panel unit uses the same test config.
# Keep these targets separate from production objects built without test hooks.
add_library(headless_config INTERFACE)
target_compile_features(headless_config INTERFACE cxx_std_20)
target_compile_definitions(headless_config INTERFACE
    IMGUI_USER_CONFIG="${CMAKE_CURRENT_SOURCE_DIR}/config.h")
if(MSVC)
    target_compile_options(headless_config INTERFACE /UNDEBUG)
else()
    target_compile_options(headless_config INTERFACE -UNDEBUG)
endif()

add_library(headless_imgui STATIC
    "${IMGUI_DIR}/imgui.cpp" "${IMGUI_DIR}/imgui_draw.cpp"
    "${IMGUI_DIR}/imgui_widgets.cpp" "${IMGUI_DIR}/imgui_tables.cpp"
    "${IMGUI_DIR}/backends/imgui_impl_null.cpp")
target_include_directories(headless_imgui PUBLIC "${IMGUI_DIR}" "${IMGUI_DIR}/backends")
target_link_libraries(headless_imgui PUBLIC headless_config)

file(GLOB engine_sources CONFIGURE_DEPENDS "${IMGUI_TEST_ENGINE_DIR}/imgui_test_engine/*.cpp")
add_library(headless_engine STATIC ${engine_sources})
target_include_directories(headless_engine PUBLIC "${IMGUI_TEST_ENGINE_DIR}")
target_link_libraries(headless_engine PUBLIC headless_imgui Threads::Threads)

add_executable(ui_tests runner.cpp tests.cpp ../settings_panel.cpp)
target_include_directories(ui_tests PRIVATE ..)
target_link_libraries(ui_tests PRIVATE headless_engine)
if(IMKIT_DIR)
    if(NOT EXISTS "${IMKIT_DIR}/include/imkit/version.h")
        message(FATAL_ERROR "IMKIT_DIR must point to an imgui-modern-kit source checkout")
    endif()
    set(IMKIT_IMGUI_TARGET headless_imgui)
    set(IMKIT_BUILD_GALLERY OFF CACHE BOOL "" FORCE)
    set(IMKIT_BUILD_DESIGN_GALLERY OFF CACHE BOOL "" FORCE)
    set(IMKIT_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    add_subdirectory("${IMKIT_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/imkit")
    target_sources(ui_tests PRIVATE imkit_panel.cpp)
    target_compile_definitions(ui_tests PRIVATE HEADLESS_WITH_IMKIT)
    target_link_libraries(ui_tests PRIVATE imkit::imkit)
endif()

add_executable(model_tests ../settings_model_main.cpp)
target_compile_features(model_tests PRIVATE cxx_std_20)
add_test(NAME headless.model COMMAND model_tests)
set_tests_properties(headless.model PROPERTIES TIMEOUT 30)

function(add_ui_case category)
    # One category contains one intended test. Each process owns its report.
    add_test(NAME "headless.${category}" COMMAND ui_tests "${category}"
        "${CMAKE_CURRENT_BINARY_DIR}/${category}.xml" 1)
    set_tests_properties("headless.${category}" PROPERTIES TIMEOUT 30)
endfunction()
add_ui_case(core.settings)
if(IMKIT_DIR)
    add_ui_case(imkit.settings)
    add_ui_case(imkit.theme)
endif()

# Check exit AND result counts. WILL_FAIL alone can conceal unrelated failures.
foreach(probe IN ITEMS failure_probe no_such_case count_mismatch undrained timeout_probe)
    add_test(NAME "headless.runner.${probe}" COMMAND "${CMAKE_COMMAND}"
        "-DRUNNER=$<TARGET_FILE:ui_tests>" "-DCASE=${probe}"
        "-DREPORT=${CMAKE_CURRENT_BINARY_DIR}/${probe}.xml"
        -P "${CMAKE_CURRENT_SOURCE_DIR}/check_rejection.cmake")
    set_tests_properties("headless.runner.${probe}" PROPERTIES TIMEOUT 30)
endforeach()
