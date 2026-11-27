// One public API for the wasm32 C ABI used by both builds.
export interface ByteKernel {
    heap(): Uint8Array;
    allocate(size: number): number;
    release(ptr: number): void;
    count(ptr: number, size: number, needle: number): number;
}

export type CountByte = (bytes: Uint8Array, needle: number) => number;

export function bindCounter(kernel: ByteKernel): CountByte {
    return function countByte(bytes: Uint8Array, needle: number): number {
        if (!(bytes instanceof Uint8Array)) throw new TypeError("Expected Uint8Array");
        if (!Number.isInteger(needle) || needle < 0 || needle > 255) {
            throw new RangeError("Expected an integer byte");
        }
        const size = bytes.byteLength;
        if (size === 0) return 0;
        if (size > 0xffff_ffff) throw new RangeError("Input exceeds wasm32 size");

        // malloc may grow memory and invalidate a caller's view into this instance.
        const source = bytes.buffer === kernel.heap().buffer ? Uint8Array.from(bytes) : bytes;
        const ptr = kernel.allocate(size) >>> 0;
        if (ptr === 0) throw new Error("Guest allocation failed");
        try {
            kernel.heap().set(source, ptr);
            return kernel.count(ptr, size, needle) >>> 0;
        } finally {
            kernel.release(ptr);
        }
    };
}

export function bindCore(exports: WebAssembly.Exports) {
    const { memory, malloc, free, count_byte } = exports;
    if (!(memory instanceof WebAssembly.Memory) || typeof malloc !== "function" ||
        typeof free !== "function" || typeof count_byte !== "function") {
        throw new TypeError("Expected memory, malloc, free and count_byte exports");
    }
    return bindCounter({
        heap: () => new Uint8Array(memory.buffer),
        allocate: size => malloc(size),
        release: ptr => free(ptr),
        count: (ptr, size, needle) => count_byte(ptr, size, needle),
    });
}
