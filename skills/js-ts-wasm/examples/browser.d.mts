import type { CountByte } from './counter.mjs';

export function openCounter(url?: string | URL): Promise<CountByte>;
