---
name: js-ts-wasm
description: "Write modern JavaScript and TypeScript for Node.js and browsers. Use for module and async design, typed API boundaries, or compiling, loading and calling WebAssembly through WASI, WIT components or Emscripten."
---

# JavaScript, TypeScript and WebAssembly

Start from a caller and one observable result. Identify the runtime and minimum version, package manager, module format and build entry point. For a JS/TS task, go directly to [language and Node patterns](references/language.md). Introduce Wasm when a native dependency, portable guest contract or measured workload warrants it.

**Choose WASI first for portable native code.** Read the artifact's imports and exports and identify who provides I/O and owns initialization. Choose a different build when the dependency or deployment host calls for it.

| What must run | Start here |
| --- | --- |
| A CLI with stdin/stdout or repeated calls to a C/C++ library | [WASI command or reactor](references/wasi.md) |
| JS/TS authored as a portable guest, or a host requiring a versioned WIT interface | [Component Model and JS guest](references/components.md) |
| A dependency graph relying on Emscripten ports, browser APIs, its virtual filesystem or generated bindings | [emsdk builds and native dependencies](references/emscripten.md) |
| An existing binary, browser/worker embedding, typed arrays, memory growth, missing imports or deployment failures | [Host and ABI contracts](references/hosting.md) |

The examples share a byte counter across backends. Start with the [WASI build](references/wasi.md) for the exact commands. Test from a clean output directory with the assets that consumers receive. Check an ordinary call, a boundary case and the initialization or failure path that distinguishes the chosen host.
