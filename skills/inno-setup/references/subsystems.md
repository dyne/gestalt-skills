# Keep Start menu and finish-page launches console-free

Trace both launch targets to the installed GUI binary. Inspect a real shortcut's TargetPath and WorkingDirectory, then use Finish to launch the installed app. A CLI launcher or a desktop EXE linked with the console subsystem can flash a console even when the shortcut's icon looks correct.

```cmake
add_executable(viewer WIN32 desktop.cpp)
add_executable(viewer-cli cli.cpp)
if(MINGW)
  target_link_options(viewer PRIVATE -municode)
endif()
```

On Windows implement `int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)`. Forward Unicode arguments to the same application dispatcher as the console build. For example, use `CommandLineToArgvW(GetCommandLineW(), &argc)`, check for failure and release the result with `LocalFree`; link `shell32` on the desktop target. Keep the ordinary console entry point for the CLI and the platform's regular `main` on other operating systems. In GNU Make, apply `-mwindows -municode` only on the MinGW GUI link, and `-mconsole` on the CLI link (add `-municode` there only with a wide console entry point). With MSVC select `/SUBSYSTEM:WINDOWS` or `/SUBSYSTEM:CONSOLE` per target.

Verify the PE optional-header subsystem using `dumpbin /headers` or `llvm-readobj --file-headers`: GUI is 2 and console is 3. Keep inherited or redirected standard handles intact. A GUI launched from Explorer can report startup failures in its UI; a diagnostic invocation must still return the correct exit code and write to the caller's pipes. From outside the checkout use a subprocess with captured output to assert `--version` on each supported executable, pipe representative input, check stderr and the exit code on an invalid option, and run the existing smoke command. For Bitcoin Viz this includes `bitcoin-viz-desktop.exe --smoke-test` and the supported `--smoke-test --regtest` JSON-on-stdin path in its matching test environment. [Released GUI entry point](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/src/desktop/desktop.cpp) · [CMake subsystem and linker settings](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/src/desktop/CMakeLists.txt)
