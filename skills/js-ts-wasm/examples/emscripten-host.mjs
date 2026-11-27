import createModule from './count-em.mjs';
import { bindCounter } from './counter.mjs';

export async function openCounter(options = {}) {
    const mod = await createModule(options);
    return bindCounter({
        heap: () => mod.HEAPU8,
        allocate: mod._malloc,
        release: mod._free,
        count: mod._count_byte,
    });
}
