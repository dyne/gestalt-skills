# Context, SSR and asynchronous work

## Isolate state by owner

Do not put per-user/request state in a shared server module singleton. Create
it per component tree/request and pass it through props or context. Defining a
context key/accessor at module scope is fine; sharing the mutable user value
there is the problem. Prefer type-safe `createContext` on Svelte 5.40+; preserve
`setContext`/`getContext` with a shared key for earlier versions. Initialize and
read context during component initialization, not in later callbacks.

Keep a reactive context object's identity stable; replacing a local variable
does not update children holding the original object. For shared primitives,
expose getters rather than capturing their initial value. In SvelteKit, keep
load functions free of writes to shared state and preserve server-only data
boundaries; use the framework's existing data-loading contract.

## Keep server output hydratable

Computed markup needed on the server must not depend on effects. Browser globals
and DOM-bound libraries belong in client lifetimes, or in guarded/dynamic imports
where required; a guard around use cannot rescue an import that already touches
`window`. Ensure initial server/client markup agrees, including locale, dates,
random values and IDs. Do not disable SSR merely to hide a hydration defect.

Test both server output and client hydration when changing their boundary.
For reused route/components, check that changed props/data update without a
remount; initialization-only state can become stale during navigation.

## Use async features deliberately

Check the installed version and configured compiler/framework support before
using component top-level `await`, awaited derived values or template await
expressions. These features arrived in Svelte 5.36 behind
`compilerOptions.experimental.async`; verify the option/status for the target
release. Do not enable it implicitly. Ordinary async handlers and `{#await}`
blocks do not by themselves require this experimental mode.

Start independent asynchronous work without accidental waterfalls; preserve
ordering for dependent operations. Handle cancellation, stale responses and
errors at the owner. For async Svelte, distinguish a boundary's initial
`pending` snippet from later pending work (`$effect.pending()` when supported).
Use `tick()` for pending synchronous DOM updates, or supported `settled()` when
the assertion must wait for resulting async work too. Check the framework's
async SSR support and error handling rather than assuming synchronous render
calls can handle awaited components.

Prefer framework-provided loading/hydration integration. When low-level
`hydratable` is actually needed, check its version/experimental requirements,
use collision-free stable keys and serializable values, and ensure server data
is present during hydration. Transferred data is client-visible; keep secrets
and server-only operations outside it. Do not repeat slow work on the client
when its server result should be reused.

Sources: [context](https://svelte.dev/docs/svelte/context),
[SvelteKit state](https://svelte.dev/docs/kit/state-management),
[await expressions](https://svelte.dev/docs/svelte/await-expressions),
[hydratable data](https://svelte.dev/docs/svelte/hydratable),
[lifecycle](https://svelte.dev/docs/svelte/lifecycle-hooks).
