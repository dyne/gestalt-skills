# Optional VitePress

Read this only for a site that uses VitePress or when the user has chosen it.
VitePress combines Markdown routing, Vue, and Vite with static HTML generation
and client navigation. Its documentation theme is optional; custom front pages
can share its build and content system. Follow the installed release's docs:
the public documentation may describe a newer prerelease. For VitePress 1.x,
use the [versioned documentation](https://vuejs.github.io/vitepress/v1/).

## Project ownership

Locate the CLI root from scripts (for example, `vitepress build docs`). Config is
resolved from that root's `.vitepress/config.*`; `srcDir` can move the content
root without moving the config. Inspect theme entry, source pages, public assets,
navigation/sidebar configuration, and any existing shared theme package.

Use `defineConfig` from `vitepress` for site config. Site options such as `base`,
`srcDir`, `outDir`, `rewrites`, and `locales` live at the top level; Vite overrides
go inside `vite`, theme options inside `themeConfig`. VitePress already supplies
Vue support. Do not add another Vue plugin or assume it reads an adjacent
`vite.config.ts` as an independent Vite app would.

Use the existing scripts for `vitepress dev <root>`, `vitepress build <root>`,
and `vitepress preview <root>`. The default build output is `<root>/.vitepress/dist`;
check configured `outDir` before selecting deployment artifacts.

## Content, routes, and themes

- Markdown files map to pages; `index.md` represents its directory. Preserve
  published URLs when using `srcDir`, exclusions, or rewrites. Link to source
  Markdown pages in Markdown; check anchors and generated routes after rewrites.
- Set top-level `base` for subpath hosting. For URLs constructed in custom Vue
  components use `withBase` from `vitepress`. Imported/relative assets receive
  build processing; public assets retain filenames. Do not double-prefix URLs
  already handled by VitePress's Markdown/theme pipeline.
- Enable `cleanUrls` only when hosting resolves extensionless requests to the
  emitted HTML. Test nested direct loads and 404s on the intended host; do not
  rely on an SPA fallback to mask missing generated pages.
- Use frontmatter for page metadata/layout. Vue components can be imported in
  Markdown's `<script setup>` or registered in the theme's `enhanceApp`.
  Use supported Markdown containers, includes, and snippet imports as needed;
  verify relative source paths and included content in the built page.
- Extend the current theme with CSS variables, slots, or component registration
  before replacing its layout. A custom theme layout must render `<Content />`
  where Markdown belongs and handle not-found pages. For custom home layouts,
  read [Front pages](frontpages.md).
- Keep nav/sidebar links, local or Algolia search, locale routes and translations
  consistent with generated pages. Enable only the search service the project
  chooses. Keep locale-specific theme/search options under the matching locale.

## Data and server rendering

Use `.data.ts`/`.data.js` loaders for build-time data. Import their named `data`
export; use `createContentLoader` for Markdown collections and `watch` for local
inputs that should trigger dev reloads. Serialize only needed public fields:
loader results enter the client bundle. Data changes after deployment need a
rebuild or an explicit runtime fetching strategy. Dynamic page generation uses
`[param].md` with its matching `.paths.*` loader; verify every generated URL.

Build-time pre-rendering executes components in Node. Access browser APIs in
`onMounted` or another browser-only boundary. `<ClientOnly>` prevents rendering
its subtree on the server, but does not make a browser-only static import safe:
load that dependency dynamically on the client. Keep essential copy and links
in server-rendered HTML; avoid random, time-dependent, or browser-dependent
initial markup. Clean up listeners and animation resources when leaving a page.

Build with dead-link checking intact. Preview custom pages and a representative
doc, direct nested loads, search, theme switching, and hydration. Fix source
links instead of globally enabling `ignoreDeadLinks` to obtain a green build.

Official references: [Site config](https://vitepress.dev/reference/site-config),
[Routing](https://vitepress.dev/guide/routing),
[Assets](https://vitepress.dev/guide/asset-handling),
[Markdown](https://vitepress.dev/guide/markdown),
[Data](https://vitepress.dev/guide/data-loading),
[Dynamic routes](https://vitepress.dev/guide/routing#dynamic-routes),
[SSR compatibility](https://vitepress.dev/guide/ssr-compat),
[Deployment](https://vitepress.dev/guide/deploy).
