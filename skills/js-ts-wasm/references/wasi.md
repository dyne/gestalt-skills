# WASI Preview 1 from C/C++ to a JS caller

A command owns `main` and exits. A reactor exposes library functions that a host can call repeatedly after initialization. Decide which contract the consumer wants before linking. Node's `node:wasi` host in this example implements Preview 1. A WIT component uses a [different loader](components.md).

## Build and run both contracts

Use Node with `WASI.getImportObject()` (20.1+ on the 20.x line), TypeScript with NodeNext support and a WASI SDK with a Preview 1 sysroot. The following commands run in an empty build directory. Set `SKILL` to the absolute installed skill directory and `WASI_SDK_PATH` to the SDK root. Use the project's pinned `tsc`.

```sh
cp "$SKILL"/examples/* .
tsc --strict --declaration --target ES2022 --module NodeNext counter.mts
"$WASI_SDK_PATH/bin/clang" --target=wasm32-wasip1 -std=c11 -O2 \
  -mexec-model=reactor -Wl,--export=count_byte -Wl,--export=malloc \
  -Wl,--export=free count.c -o count.wasm
node check.mjs wasi

"$WASI_SDK_PATH/bin/clang" --target=wasm32-wasip1 -std=c11 -O2 \
  -DCOUNT_COMMAND count.c -o count-cli.wasm
printf 'one\ntwo\n' | node check.mjs command
```

The command prints `2` and returns zero. The library check covers empty input, a NUL, a subarray, a 24 MiB allocation, a rejected byte value and a second call. `counter.mts` emits the ESM wrapper `counter.mjs` and its `counter.d.mts` declarations. Each JS loader has a companion declaration for strict TypeScript callers. In C++, compile with the SDK's `clang++` and declare C ABI exports with `extern "C"`. For CMake select the toolchain file shipped with the SDK for the intended preview, in a fresh build directory. Cross-compile every linked native object and archive for that target.

## Activate the artifact

The bundled `examples/wasi-node.mjs` compiles neither code nor types on import. Its caller compiles bytes once and passes a `WebAssembly.Module` to a factory. Each call constructs a fresh WASI context and instance.

| Artifact contract | Activation in Node |
| --- | --- |
| Exports memory and `_start` | Instantiate with `host.getImportObject()`, call `host.start(instance)` once, propagate the exit status. Supply stdin/stdout/args as needed. |
| Exports memory and library functions, optionally `_initialize` | Instantiate with the imports, call `host.initialize(instance)` once, then call the exports. The host handles the optional initializer. |

Pass only the env values and preopened guest-to-host directory mappings the program actually needs. The sample inherits standard I/O and uses empty args, env and preopens. A missing preopen is a host configuration issue when the guest expects that path. Node documents its WASI implementation as experimental and unsuitable as a security boundary for untrusted code.

The sample reactor's optimized binary has no imports at the tested SDK revision, so the browser loader in `examples/browser.mjs` can instantiate it directly and call its initializer. Adding file I/O can change the import list. Inspect the built bytes again after changing dependencies. [Browser deployment and ABI](hosting.md)

[WASI SDK build and targets](https://github.com/WebAssembly/wasi-sdk) · [Node WASI lifecycle](https://nodejs.org/api/wasi.html)
