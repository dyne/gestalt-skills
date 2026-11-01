---
name: vite
description: "Build, configure, debug, and optimize Vite projects: dev/HMR, assets, environment variables, plugins, production builds, libraries, SSR, and version migrations. Also use for VitePress sites when present or requested, including Markdown, themes, and custom Vite/Vue front pages alongside documentation. VitePress is optional."
---

# Vite

1. Inspect `package.json`, the lockfile, Node requirements, package scripts,
   framework integration, Vite configuration, and deployment URL/output. Use
   the installed versions and package manager. A framework may own Vite as a
   dependency; preserve its supported configuration and build commands.
2. Choose the path from the actual project and request. Vite is the base build
   tool and works with vanilla HTML/JS, Vue, React, Svelte, and other supported
   frameworks. Use VitePress only if the site already uses it or the user
   chooses it; a website or documentation request alone does not require it.
   A VitePress site can have a fully custom front page built with Vite/Vue
   while retaining Markdown documentation and the default documentation theme.

   | Task | Read when needed |
   | --- | --- |
   | Config, env/modes, assets, imports, dev/build differences | [Vite core](references/vite-core.md) |
   | Plugins/HMR, library builds, SSR, Environment API, migrations | [Advanced Vite](references/vite-advanced.md) |
   | Existing or explicitly chosen VitePress site | [Optional VitePress](references/vitepress.md) |
   | Custom VitePress front page or separate Vite landing page with docs | [Front pages](references/frontpages.md) |

3. Trace the affected entry point, config owner, module graph, and deployed
   route before editing. Keep the smallest configuration that solves the task;
   prefer ESM for new configs, respecting the existing project's conventions.
   Preserve supported browsers and public URLs. Do not set `target: 'esnext'`,
   add plugins, replace the site's theme, or upgrade dependencies merely to
   apply this skill. Resolve version-sensitive options against installed types
   and the matching official documentation, rather than copying newer APIs.
4. Implement the change at its owner. Keep browser code, server/build code,
   and public build-time values separate. For VitePress, put Vite overrides in
   its config's `vite` field and keep custom front-page styling scoped so
   documentation remains usable.
5. Run project scripts for the affected checks and a production build. Vite
   transpilation does not type-check TypeScript; run the project's type checker
   separately. For changed routing/assets, serve the output at its deployment
   base and check direct page loads, navigation, and asset requests. For SSR or
   VitePress, also check pre-rendering and client hydration; dev success alone
   does not establish production correctness. Use browser checks when available
   for changed interactions, responsive layouts, and console errors.
6. Report the behavior changed, versions and commands checked, and remaining
   limits. Distinguish a successful build from browser or deployed-site
   verification. `vite preview` and `vitepress preview` serve local build output;
   they are not production servers.

Condensed and adapted from the Vite and VitePress skills in
[antfu/skills](https://github.com/antfu/skills), with current official guidance
and custom-front-page workflows. Preserve the [upstream MIT notice](LICENSE.upstream).
