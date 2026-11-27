import { WASI } from 'node:wasi';
import { bindCore } from './counter.mjs';

function createHost() {
    return new WASI({ version: 'preview1', args: [], env: {}, preopens: {}, returnOnExit: true });
}

export async function openCounter(module) {
    const host = createHost();
    const instance = await WebAssembly.instantiate(module, host.getImportObject());
    host.initialize(instance);
    return bindCore(instance.exports);
}

export async function runCommand(module) {
    const host = createHost();
    const instance = await WebAssembly.instantiate(module, host.getImportObject());
    return host.start(instance);
}
