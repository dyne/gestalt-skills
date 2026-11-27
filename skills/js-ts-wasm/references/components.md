# A JS guest with a WIT contract

Browser and Node applications normally run their JS directly and import a guest. When the **deliverable itself** must be a portable Wasm component, define a WIT world and use a component toolchain. Plain `tsc` produces JavaScript. A componentizer can bundle the JS and a runtime engine into the guest, with startup and size costs to measure. For TS, type-check and emit ESM before componentizing unless the selected tool explicitly supports the project's TS syntax.

The following example uses a synchronous WIT export and no host services. Use a scratch ESM package (`"type": "module"`) with a project-local `jco` on PATH. These commands were exercised with `@bytecodealliance/jco` 1.42.0 and its default StarlingMonkey backend.

In `counter.wit`:

```wit
package example:bytes;
world counter {
    export count-byte: func(data: list<u8>, needle: u8) -> u32;
}
```

In `guest.js`:

```js
export function countByte(data, needle) {
    let total = 0;
    for (const byte of data) if (byte === needle) ++total;
    return total;
}
```

Build the component, inspect its exported world, then generate bindings for a JS consumer:

```sh
jco componentize guest.js --wit counter.wit -n counter --disable all -o component.wasm
jco wit component.wasm
jco transpile component.wasm -o bindings
```

The disabled features are optional runtime services that this guest does not use. For a guest that needs clocks, files or other interfaces, resolve its actual imports in the component host. Lock the componentizer and generated bindings to the same contract. A JS host can call the exported camel-case binding directly:

```js
import assert from 'node:assert/strict';
import { countByte } from './bindings/component.js';
assert.equal(countByte(Uint8Array.of(1, 3, 3), 3), 2);
```

Ship all emitted assets and the shim dependencies referenced by those bindings. A component-aware runtime can consume the original component with implementations of its imports. Node's Preview 1 `WASI.start` and a browser's core `instantiate` serve other artifact types. For an existing Preview 1 binary that needs a component wrapper, choose an adapter matching command vs reactor and the intended WIT world, then inspect and test the resulting component. A change of filename does not supply an adapter.

For richer interfaces, describe records, variants, lists, results and resource ownership in WIT, regenerate host/guest bindings, and specify when a handle is released. Test a nontrivial value on both sides and an interface-defined failure. Keep raw linear-memory pointers inside the component implementation.

[JS components and WIT](https://component-model.bytecodealliance.org/language-support/building-a-simple-component/javascript.html) · [jco tooling](https://github.com/bytecodealliance/jco)
