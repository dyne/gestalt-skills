import type { CountByte } from './counter.mjs';

export function openCounter(module: WebAssembly.Module): Promise<CountByte>;
export function runCommand(module: WebAssembly.Module): Promise<number>;
