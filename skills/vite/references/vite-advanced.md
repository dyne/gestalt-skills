# Advanced Vite

## Plugins and HMR

Use built-in features or the framework's maintained plugin first. For custom
plugins, return a named, typed `Plugin`; scope transforms to the intended files
and return source maps when changing source. `enforce: 'pre' | 'post'` controls
ordering; `apply: 'serve' | 'build'` controls applicability. A dev-only hook is
not a production transform.

- Use `config` to contribute options and `configResolved` to read the resolved
  configuration. Plugins added from `config` are not a way to extend the already
  resolved plugin list.
- Use `resolveId` and `load` for virtual modules. Expose `virtual:name` to users
  and resolve it internally to `\0virtual:name` to avoid filesystem resolution.
- Use `transformIndexHtml` for HTML, `configureServer` for dev middleware, and
  build hooks for emitted output. Avoid assuming that output-generation hooks
  execute on every dev request.
- Check the installed Vite version's HMR hooks before implementing invalidation.
  For modules owning browser side effects, clean them up through
  `import.meta.hot.dispose`; avoid duplicate listeners or resources after HMR.
  Verify the affected dependency updates and production behavior separately.

## Libraries, multiple entries, and SSR

For a library, use `build.lib`, externalize intended peer dependencies, and keep
`package.json` exports aligned with actual formats and emitted files. Generate
type declarations separately when required; Vite does not emit them merely
because the entry is TypeScript. Check CSS exports and `sideEffects` so consumers
do not accidentally tree-shake required styles. Exercise a consumer import.

For a multi-page website, use HTML entries and the bundler input option supported
by the installed major. Do not apply library mode merely to obtain multiple
pages. Confirm all output URLs and assets at the deployed base.

Prefer the existing framework's SSR lifecycle. For a low-level integration,
development middleware, HTML transforms and server-module loading are distinct
from production's client and server builds. Preserve request isolation: do not
store per-user state in shared module singletons. Guard browser APIs and defer
browser-only imports; match server markup to the first client render. Investigate
the specific dependency before changing `ssr.external` or `ssr.noExternal`.
Verify both the Node/runtime entry and browser hydration.

The Environment API is intended for multi-environment/framework integrations.
Check its stability and exact API in the installed version. In relevant plugin
hooks use environment-specific configuration/module graphs; do not assume a
single global client/server graph. Do not rewrite an ordinary app integration
to adopt this API without a task-specific reason.

## Version changes

Read the installed and target majors' migration guides before editing options.
For a requested Vite 7-to-8 migration:

| Area | Vite 7 | Vite 8 |
| --- | --- | --- |
| Production bundler | Rollup | Rolldown |
| JS transforms / dependency optimizer | esbuild | Oxc / Rolldown |
| Preferred build customization | `build.rollupOptions` | `build.rolldownOptions` |
| Preferred transform / optimizer options | `esbuild` / `optimizeDeps.esbuildOptions` | `oxc` / `optimizeDeps.rolldownOptions` |

Compatibility aliases exist in Vite 8, but option shapes and plugin behavior
are not universally interchangeable. Verify JSX, minification, browser targets,
Node requirements, native dependencies, and plugin peer ranges. Keep framework
and VitePress dependency constraints intact; do not force a transitive Vite major
with an override just to follow this table. Compare relevant output and runtime
behavior after migration, not just configuration parsing.

Official references: [Plugin API](https://vite.dev/guide/api-plugin),
[HMR](https://vite.dev/guide/api-hmr),
[Libraries and multiple pages](https://vite.dev/guide/build),
[SSR](https://vite.dev/guide/ssr),
[Environment API](https://vite.dev/guide/api-environment),
[Migration](https://vite.dev/guide/migration).
