import { bindCore } from './counter.mjs';

// For a trusted, import-free reactor produced by the WASI build in this skill.
export async function openCounter(url = new URL('./count.wasm', import.meta.url)) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status} loading ${url}`);
    const module = await WebAssembly.compileStreaming(response);
    const imports = WebAssembly.Module.imports(module);
    if (imports.length) throw new Error(`A host adapter is required for ${imports[0].module}.${imports[0].name}`);
    const instance = await WebAssembly.instantiate(module, {});
    instance.exports._initialize();
    return bindCore(instance.exports);
}
