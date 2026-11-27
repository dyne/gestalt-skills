# Inspect, embed and call a Wasm artifact

## Check the actual deployment target

Trace declared dependencies **and** the code paths that run during import, startup and a representative call. Record the host, target triple/ABI, enabled Wasm features and assets. Check transitive native archives and npm packages with native addons or install-time platform binaries. For each required facility (files, env, clock, randomness, network, threads or subprocesses), identify the host implementation or move that part outside the guest. A working host-native build establishes the algorithm, but the target build and its imports establish portability.

For **core** bytes, inspect before guessing at a loader. This Node ESM fragment takes a filename as its first argument:

```js
import { readFile } from 'node:fs/promises';
const module = await WebAssembly.compile(await readFile(process.argv[2]));
console.table(WebAssembly.Module.imports(module));
console.table(WebAssembly.Module.exports(module));
```

These lists give names and kinds. Use the guest header, WIT or generated declarations for signatures, and a known-answer call to check agreement. Inspect WIT components with component tools such as `jco wit`. Supply the imports required by a core module under their exact module/name keys. Side effects such as writes and randomness require real implementations.

## Deliver and activate

- **Static site or worker.** Deploy the binary as a versioned asset. Resolve its URL relative to the importing module with `new URL('./count.wasm', import.meta.url)` or use the bundler's emitted URL. Serve HTTP success, CORS where needed and `Content-Type: application/wasm`. The bundled browser loader checks status, compiles the response stream, instantiates the trusted import-free reactor and runs its initializer. A real WASI import requires a preview-compatible browser shim implementing those calls or a different guest build.
- **Load on demand.** Activate at the point the feature is needed, await readiness before enabling calls, and surface load errors. With known incorrect MIME on a host you cannot change, compile `await response.arrayBuffer()` instead of streaming. Decide before consuming the response body. Preserve HTTP and linking errors rather than retrying every error as a MIME problem.
- **Server/worker sharing.** Cache a compiled core module by build identity. Instantiate separately for independent heaps, WASI capabilities or tenant state. Workers can receive a compiled module through structured clone. Transfer owned buffers deliberately because transfer relinquishes the sender's buffer. For a UI, test the packaged worker and asset URL under the real deployment base path.
- **Bundled bytes.** When network fetch is unavailable, pass a `Uint8Array` of the exact binary to `WebAssembly.compile`. A Node Buffer may be a slice of a larger allocation. Passing the view preserves its offset and length. For an Emscripten build, pass `wasmBinary` to its factory when embedding bytes, or use `locateFile` for external sidecars. A WIT component needs its component loader.
- **Measure the complete path.** Compare equivalent JS and guest implementations on realistic data. Measure fetch, compilation and instantiation separately from warmed calls, including copies and worker messaging. Coarse-grained operations amortize crossings.

### Publish the example for a browser

Ship `browser.mjs`, the emitted `counter.mjs` and `count.wasm` together. Include `browser.d.mts` and the emitted `counter.d.mts` when publishing a typed package. From an ES module served with the application:

```js
import { openCounter } from './lib/browser.mjs';
const countByte = await openCounter();
const matches = countByte(new TextEncoder().encode('café'), 0x63); // 1
```

A strict TS service uses the same callable type. Import `openCounter` from `wasi-node.mjs`, compile the bytes with `WebAssembly.compile`, then pass that module to the factory. Publish the matching entry-point declaration beside its JS file and expose it through the package's exports when applicable.

## Define the memory contract

For a wasm32 core ABI, record the exported symbol, parameter widths, signedness, pointer ownership, length unit, result/error and who releases it. JS represents i32 as a Number and i64 as BigInt at the raw boundary. Normalize an unsigned i32 with `>>> 0` when needed. A pointer belongs to one instance. For strings, use `TextEncoder` and the encoded byte count; pass a terminator only when required. Use little-endian `DataView` access for multi-byte fields and verify the C layout or serialize explicitly.

Allocate in the guest, get a **fresh** view after allocation, then copy/call/release in a `finally` block. For a guest-owned result, validate offset and length against the current memory, copy out before freeing or allowing another call, and follow the guest's destructor contract. A view is borrowed. Growth can detach an ordinary buffer; with shared memory a previously obtained view can retain its old length. At callbacks or async boundaries, recheck lifetime. Copy caller input first when it aliases a heap that allocation could grow. The example wrapper exposes a number and keeps the pointer private.

| Observed stage | First check |
| --- | --- |
| Fetch/compile | HTTP status, asset URL, MIME for streaming, binary vs HTML fallback, core vs component and engine feature support |
| Instantiate/link | Required import module/name/kind, memory or table limits, host adapter version and matching sidecars |
| Initialize | Command vs reactor, single activation, constructors, missing preopens, generated factory readiness |
| Wrong result or trap on call | Actual symbol/signature, signedness, byte vs element length, stale views, ownership and state from earlier calls |

[WebAssembly JS API](https://webassembly.github.io/spec/js-api/) · [WebAssembly Web API](https://webassembly.github.io/spec/web-api/) · [Emscripten module options](https://emscripten.org/docs/api_reference/module.html)
