import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const mode = process.argv[2];
async function compileFile(name) {
    return WebAssembly.compile(await readFile(new URL(name, import.meta.url)));
}

if (mode === 'command') {
    const { runCommand } = await import('./wasi-node.mjs');
    process.exitCode = await runCommand(await compileFile('count-cli.wasm'));
} else {
    let count;
    if (mode === 'wasi') {
        const { openCounter } = await import('./wasi-node.mjs');
        count = await openCounter(await compileFile('count.wasm'));
    } else if (mode === 'em') {
        const { openCounter } = await import('./emscripten-host.mjs');
        count = await openCounter();
    } else {
        throw new Error('Choose wasi, command or em');
    }

    assert.equal(count(new Uint8Array(), 0), 0);
    const encoded = new TextEncoder().encode('a\0éa');
    assert.equal(count(encoded, 0), 1);
    assert.equal(count(encoded.subarray(1), 97), 1);
    assert.equal(count(new Uint8Array(24 * 1024 * 1024), 0), 24 * 1024 * 1024);
    assert.throws(() => count(encoded, 256), RangeError);
    assert.equal(count(encoded, 97), 2);
    console.log(`PASS ${mode}: empty, binary, subview, large allocation, invalid byte, repeat call`);
}
