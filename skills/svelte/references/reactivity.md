# Reactivity and ownership

## Choose the right mechanism

| Need | Use |
| --- | --- |
| Mutable data that must update consumers | `$state` |
| Value computed from reactive inputs | `$derived(expression)` or `$derived.by(() => ...)` |
| Work caused by a user's action | Event handler or an appropriate function binding |
| Synchronize with an external system | An attachment for an element; otherwise a scoped `$effect` |
| Observe an external subscription | An existing store or `createSubscriber` when supported |
| Diagnose unexpected dependencies | `$inspect` / `$inspect.trace` in development |

Keep nonreactive bookkeeping as ordinary variables. `$state` deeply proxies
plain objects and arrays, not every class instance or built-in. Use supported
reactive built-ins such as `SvelteMap` when needed. For large data replaced as a
whole, consider `$state.raw`; update it by reassignment, not hidden mutation.
Use `$state.snapshot` when an external API requires an unproxied snapshot.

## Derived values and props

Read changing props in a derived expression, template or handler rather than
capturing a one-time computed value at component creation. Keep derived
expressions free of side effects; `$derived(fn)` derives the function itself,
whereas `$derived.by(fn)` computes its return value. Derived objects are not
automatically made deeply reactive. Local overrides of derived values require
Svelte 5.25+ and are replaced when their dependencies change.

```svelte
<script lang="ts">
  let { step = 1 }: { step?: number } = $props();
  let count = $state(0);
  let next = $derived(count + step);
</script>

<button onclick={() => count += step}>Add {step}</button>
<p>Count: {count}; next: {next}</p>
```

Treat props as parent-owned. Prefer callbacks for updates, or `$bindable` for a
deliberate two-way interface; do not mutate a borrowed state proxy to bypass
its owner. Destructuring a reactive object into ordinary local values can lose
reactivity; preserve property reads or use deliberate derived destructuring.

## Effects and shared modules

Effects track synchronous reactive reads, including called functions; reads
after `await` or inside later callbacks are not ordinary tracked dependencies.
Keep setup synchronous so it can return cleanup. Release subscriptions,
observers, timers and library instances before rerun/unmount. Avoid effects
that copy derived state or form feedback loops. Effects run only in the browser;
adding a `browser` guard inside an effect does not make it run during SSR.

Put reusable runes in `.svelte.js` / `.svelte.ts`, not ordinary JS/TS modules.
Do not export a reassigned rune binding directly; expose a stable reactive
object, class fields or getters/methods. Preserve existing store subscription
contracts where they are useful. Diagnose stale closures and copied values
before changing the state architecture. `$inspect.trace` must be the first
statement in the traced function and is a development aid, not production logic.

Sources: [state](https://svelte.dev/docs/svelte/$state),
[derived](https://svelte.dev/docs/svelte/$derived),
[props](https://svelte.dev/docs/svelte/$props),
[effects](https://svelte.dev/docs/svelte/$effect),
[reactive built-ins](https://svelte.dev/docs/svelte/svelte-reactivity),
[inspection](https://svelte.dev/docs/svelte/$inspect).
