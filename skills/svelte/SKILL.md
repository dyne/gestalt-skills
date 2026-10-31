---
name: svelte
description: "Create, review, debug, and refactor Svelte components and reactive modules (.svelte, .svelte.js, .svelte.ts). Use for runes, props, events, bindings, snippets, scoped styles, DOM integrations, SSR/hydration, and Svelte-specific documentation and validation tooling."
---

# Svelte

1. Inspect the installed Svelte/SvelteKit versions, lockfile, component mode,
   compiler options, package scripts and affected call sites. Preserve the
   project's package manager, supported APIs and public component contracts.
   Prefer runes for new Svelte 5 components; keep existing legacy components
   compatible unless migration is part of the task. Do not enable experimental
   async or replace working stores/actions merely to modernize a small change.
2. Read the relevant reference and current source before editing. Resolve
   uncertain syntax and version-sensitive behavior through official Svelte
   documentation, using the available tools described in the tooling reference.

   | Task | Reference |
   | --- | --- |
   | State, derived values, effects, props, shared reactive modules | [Reactivity](references/reactivity.md) |
   | Events, bindings, snippets, lists, styling, DOM libraries | [Components](references/components.md) |
   | Context isolation, server rendering, hydration, asynchronous work | [SSR and async](references/ssr-async.md) |
   | Documentation lookup, autofixer, compiler/type checks, test selection | [Tooling](references/tooling.md) |

3. Trace the failing update or interaction to its owner and dependencies.
   Compute values with `$derived`; put user-triggered work in handlers; reserve
   effects for external synchronization with cleanup. Preserve server/client
   boundaries and accessible native control behavior. Make the smallest change
   that fixes the observable contract, including affected callers when an
   interface changes.
4. Run the available Svelte autofixer on changed components and supported
   reactive modules, then inspect its findings and apply relevant corrections.
   Recheck changed code and run project compiler/type checks plus meaningful
   tests for the affected behavior. A quiet autofixer is not proof that an
   interaction, hydration or cleanup works. Use the tooling reference's fallback
   when a tool is unavailable or cannot parse the project's syntax.
5. Report the behavior changed, commands/results and any remaining warnings or
   untested rendering paths. Keep compiler, autofixer, automated behavior and
   browser evidence distinct; do not claim browser verification from static
   checks alone.
