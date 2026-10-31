# Documentation and validation

## Use the available Svelte tools

Prefer an already connected Svelte MCP server or project-installed compatible
tooling. Inspect live schemas rather than assuming tool names/arguments.
Otherwise, the official `@sveltejs/mcp` CLI exposes the same documentation and
autofixer operations. Use an available/pinned version where the project has one;
`npx` may fetch a package, so honor the environment's network/cache permissions.

```sh
npx --yes @sveltejs/mcp list-sections
npx --yes @sveltejs/mcp get-documentation 'svelte/$state,svelte/$derived,svelte/$effect'
npx --yes @sveltejs/mcp svelte-autofixer ./src/lib/Counter.svelte --svelte-version 5
```

Discover relevant section paths with `list-sections` before requesting them;
fetch only what the task needs. Prefer a file path for validation, checking it
exists first: a nonexistent path can be interpreted as inline code. Supply the
installed full Svelte version when the tool supports it, otherwise the supported
major. Pass `--async` only when the project's async compiler mode is enabled.
Read `--help` when local CLI options differ from these examples.

In POSIX shells, single quotes preserve literal runes; do not add a backslash
before `$` inside single-quoted code. Double-quoted `$state`/`$derived` expand as
shell variables unless escaped. Prefer files or structured tool arguments to
embedding source in a shell command.

## Validate in layers

1. Run `svelte-autofixer` for changed `.svelte` components and supported reactive
   modules. It reports issues/suggestions; inspect the current file and apply
   relevant fixes yourself. A successful process exit can still contain
   findings. Re-run after corrections and inspect any request for another call.
   Preserve intentional, version-compatible code when a suggestion would
   expand scope; explain unresolved findings rather than suppressing them.
2. Run the project's configured `svelte-check`, type-check, lint and build
   commands as appropriate. Inspect `package.json` instead of inventing script
   names or changing configuration to make the checks pass. Use the project's
   Svelte compiler for module checks if an external tool only parses components.
3. Exercise the affected behavior with the existing test stack: changing props,
   events/bindings, keyed list identity, subscription cleanup, async race/error
   handling, or SSR/hydration as relevant. Await Svelte updates before asserting
   DOM state; use native browser verification when behavior depends on layout,
   focus or browser APIs. Add focused regression coverage when warranted.

If the MCP/CLI is unavailable, unsupported or cannot use the pinned version,
continue with project compiler/type/behavior checks and official docs. Report
the missing autofixer coverage; do not install or reconfigure a service just to
make a validation claim. If corrections stop producing new evidence, inspect
the root cause or report the remaining limitation instead of repeating the
same invocation indefinitely.

Sources: [official CLI](https://svelte.dev/docs/ai/cli),
[Svelte tooling](https://svelte.dev/docs/ai/tools),
[testing](https://svelte.dev/docs/svelte/testing).
