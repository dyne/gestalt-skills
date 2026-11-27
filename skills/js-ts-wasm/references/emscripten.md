# Emscripten for a dependency-rich build

A large pure C/C++ library can still work with WASI. Choose emsdk when an existing port, JS library, Embind API, browser event loop, graphics backend or virtual filesystem makes it the better fit. Pin the tested emsdk release. In a development shell with that SDK installed and activated, source its `emsdk_env.sh` and confirm `emcc --version`. This activates the *compiler*. The async factory initializes the *application*.

## Reuse the byte counter

In an empty output directory copy the contents of `examples/` and run the TypeScript compilation from the [WASI build](wasi.md). This time link and start the Emscripten flavor:

```sh
emcc -std=c11 -O2 count.c --no-entry -sMODULARIZE=1 -sEXPORT_ES6=1 \
  -sALLOW_MEMORY_GROWTH=1 -sEXPORTED_FUNCTIONS=_count_byte,_malloc,_free \
  -sEXPORTED_RUNTIME_METHODS=HEAPU8 -o count-em.mjs
node check.mjs em
```

Deploy `count-em.mjs` and `count-em.wasm` from the same link. The bundled `emscripten-host.mjs` awaits the factory before reading `HEAPU8` or calling `_count_byte`. Export the symbols consumed by JS at final link so optimization retains them. For C++ use an `extern "C"` facade for this ABI. If callers need rich C++ types, use Embind and document which JS handles require `.delete()`. Direct numeric calls need no `ccall` or `cwrap`; export those runtime helpers explicitly if the application uses them.

## Link a real native dependency

For a CMake library start with a fresh target build directory, e.g. for a local zlib v1.3.1 checkout at `ZLIB_SRC`:

```sh
emcmake cmake -S "$ZLIB_SRC" -B zlib-wasm -DCMAKE_BUILD_TYPE=Release -DZLIB_BUILD_EXAMPLES=OFF
cmake --build zlib-wasm --target zlibstatic
emcc -O2 --no-entry zlib-wasm/libz.a -sMODULARIZE=1 -sEXPORT_ES6=1 \
  -sEXPORTED_FUNCTIONS=_crc32,_malloc,_free -sEXPORTED_RUNTIME_METHODS=HEAPU8 -o zlib.mjs
```

Run with the emitted module and its sibling Wasm file. The known checksum exercises a symbol pulled from the archive:

```js
import assert from 'node:assert/strict';
import createZlib from './zlib.mjs';
const lib = await createZlib();
const input = new TextEncoder().encode('123456789');
const ptr = lib._malloc(input.length);
assert.ok(ptr);
try {
    lib.HEAPU8.set(input, ptr);
    assert.equal(lib._crc32(0, ptr, input.length) >>> 0, 0xcbf43926);
} finally {
    lib._free(ptr);
}
```

Keep native build tools (such as a code generator) on the build machine. Compile linked libraries for the guest. Use `emconfigure` and `emmake` for suitable configure/make projects, `emar` for archives, and `em++` to link the C++ runtime when required. Check configure probes that try to execute a cross-built target. Match compile/link options across dependencies for threads, exceptions and ABI-affecting features. Consult the port's documented flags when using an Emscripten port.

## Select runtime features deliberately

- For bundled read-only assets use `--preload-file hostdir@/guestdir` where appropriate and ship the generated data sidecar. Confirm the virtual path. In-memory writes disappear with the instance; browser persistence needs an explicit backing store and synchronization.
- Split blocking loops into event-driven work for the web. If the native stack really must suspend on host I/O, choose a supported Asyncify or JSPI configuration and verify the resulting async calling convention. Returning a JS promise from an ordinary synchronous import does not suspend a core call.
- For pthreads, build all affected code with compatible thread flags, serve the required worker assets, and check `crossOriginIsolated`, shared memory support and deployment headers in the browser. Provide a separate single-threaded build when targeting hosts without shared memory.
- Verify shipped sidecars, initialization, known output and resource teardown in the intended host. Node smoke tests cover the computation; browser integration also needs its actual asset URLs, response headers and event loop.

[Emscripten build systems](https://emscripten.org/docs/compiling/Building-Projects.html) · [Modularized output](https://emscripten.org/docs/compiling/Modularized-Output.html) · [JS interop](https://emscripten.org/docs/porting/connecting_cpp_and_javascript/Interacting-with-code.html) · [Pthreads](https://emscripten.org/docs/porting/pthreads.html)
