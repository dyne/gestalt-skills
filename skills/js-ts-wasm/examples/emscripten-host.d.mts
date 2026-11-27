import type { CountByte } from './counter.mjs';

export interface CounterOptions {
    wasmBinary?: Uint8Array;
    locateFile?: (path: string, prefix: string) => string;
}

export function openCounter(options?: CounterOptions): Promise<CountByte>;
