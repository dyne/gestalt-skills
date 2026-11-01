# Vite core

## Configuration and modes

- Locate the root and selected config from package scripts; `index.html` is a
  source entry, not a file to place in `public/`. Prefer `defineConfig` for typed
  configuration. Use its callback when options depend on `command` or `mode`.
- Resolve filesystem aliases to absolute paths, e.g.
  `fileURLToPath(new URL('./src', import.meta.url))`. Keep TypeScript/editor
  resolution aligned; a TS path declaration alone is not a portable Vite alias.
- `.env` files are not automatically available while config is being evaluated.
  Use `loadEnv(mode, envDir, prefix)` if config needs them, resolving `envDir`
  from the actual project. Parse numbers/booleans deliberately. Expose only
  intended public values; never spread loaded env or `process.env` into `define`.
- Client `import.meta.env.VITE_*` values are public strings embedded at build
  time. `define` also performs compile-time replacement; use
  `JSON.stringify(value)` for string literals. Neither is a secret store or a
  runtime deployment configuration service.
- `--mode staging` selects mode-specific env files; it does not itself make a
  production build a development build. Distinguish `MODE`, `PROD`/`DEV`, and
  `NODE_ENV`. Restart the dev server after changing env files.
- `server.proxy` handles development requests only. Configure the production
  API URL or hosting proxy separately. Bind/expose the dev server and configure
  allowed hosts only as needed; avoid broad host/CORS allowances as a quick fix.

## Assets and imports

| Need | Mechanism and constraint |
| --- | --- |
| Hashed, processed asset | Import a URL from source or use a static relative URL in supported markup/CSS |
| Unchanged filename | Use `public/`; reference it from the public URL, without `/public/` |
| Raw text or explicit URL | Use `?raw` or `?url` |
| Static module discovery | Use literal patterns in `import.meta.glob`; imports are lazy unless `{ eager: true }` |
| Worker | Use `new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })` where supported |

Vite must be able to analyze asset paths. Arbitrary runtime strings do not
automatically enter the build graph. `new URL(..., import.meta.url)` patterns
that work in browser builds are not a general SSR asset resolver. Check the
framework's asset mechanism for server rendering.

Set `base` to the real deployment prefix, such as `/project/`. Imported assets,
CSS URLs, and HTML asset references are adjusted during builds. For dynamically
assembled public paths use `import.meta.env.BASE_URL`; avoid root-only literals
that escape the deployment prefix. Application-router base and host rewrites
must agree with Vite's asset base.

## Build and performance

Use existing `dev`, `build`, and `preview` scripts; their flags and framework
wrappers may be significant. Keep browser targets driven by requirements;
syntax transforms do not supply missing runtime APIs or all polyfills.

For a regression, separate cold dependency optimization, HMR, production build
time, and delivered page weight. Measure the affected stage before tuning.
Prefer smaller imports, lazy loading at useful boundaries, and less expensive
plugin work before chunk configuration. `optimizeDeps` concerns development
dependency optimization, not production chunk splitting. Recheck both dev and
build when changing dependency resolution, CSS handling, or plugins.

Official references: [Config](https://vite.dev/config/),
[Env and modes](https://vite.dev/guide/env-and-mode),
[Assets](https://vite.dev/guide/assets),
[Features](https://vite.dev/guide/features),
[Build](https://vite.dev/guide/build),
[Performance](https://vite.dev/guide/performance).
