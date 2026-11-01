# Custom front pages with optional documentation

Choose ownership before changing routing or builds:

| Project need | Approach |
| --- | --- |
| Vite site without VitePress | Keep the existing Vite/framework entry and routing |
| VitePress with a simple themed home | Use default `layout: home` and its hero/features |
| VitePress with a distinct designed front page | Render custom Vue components within the VitePress build |
| Independently built Vite app plus VitePress docs | Keep separate entry points, routes, and output directories |

## One VitePress build, custom Vite/Vue front page

A VitePress page can be a bespoke Vue interface compiled by Vite. It does not
need a second app, Vite server, router, or build. Keep the documentation theme's
navigation, search, and content layouts where useful.

With the default theme, choose `layout: page` for custom content without
documentation typography; disable the sidebar explicitly when it should be
absent. Use `layout: false` for a page owning its entire shell, including nav and
footer. `layout: home` is the standard home template, not a prerequisite for
custom front pages. Preserve any existing custom theme's layout contract.

For example, with content at the VitePress root `docs/`, use `docs/index.md`:

```md
---
layout: page
sidebar: false
outline: false
title: Project
description: A short description of the project.
---

<script setup>
import LandingPage from './.vitepress/theme/components/LandingPage.vue'
</script>

<LandingPage />
```

Then `docs/.vitepress/theme/components/LandingPage.vue` can contain ordinary
SSR-compatible Vue code:

```vue
<script setup>
import { withBase } from 'vitepress'
</script>

<template>
  <section class="project-landing" aria-labelledby="project-title">
    <h1 id="project-title">Project</h1>
    <p>The project's purpose and next step.</p>
    <a :href="withBase('/guide/')">Read the guide</a>
  </section>
</template>

<style scoped>
.project-landing { max-width: 72rem; margin: auto; padding: 4rem 1.5rem; }
</style>
```

This assumes a `guide/index.md` page. Adjust imports if `srcDir` changes the
content root. A local import needs no global component registration. If extending
the theme, preserve its existing hooks, components, and CSS imports rather than
replacing the entry file with a minimal example. For a fully custom shared
layout, render not-found state first, then the chosen home layout, then the
documentation/content fallback.

Scope landing-page CSS beneath a dedicated class or component styles. Use theme
variables for shared colors and deliberate light/dark variants. Avoid global
`h1`, `main`, or `.vp-doc` overrides that unintentionally restyle docs. Keep
headings, core copy, and navigation in pre-rendered HTML; defer canvas, WebGL,
and other browser-only enhancements with cleanup and reduced-motion support.

The [Quietproof](https://plan-b.foundation/quietproof/) and
[Bitcoin Roots](https://plan-b.foundation/bitcoin-roots/) sites illustrate this
shared-build pattern. Their source themes register custom home components:
[Quietproof theme](https://github.com/LuganoPlanB/quietproof/tree/main/docs/.vitepress/theme),
[Bitcoin Roots theme](https://github.com/LuganoPlanB/bitcoin-roots/tree/main/doc/website/.vitepress/theme).
Use these as design/integration references, not mandatory dependencies or
templates to copy wholesale; inspect current source before borrowing details.

## Separate Vite landing build and VitePress docs build

Use this when the front page already has an independent app/framework or needs
an independent lifecycle. For a site at `/project/` with docs at `/project/docs/`:

- Set Vite's `base: '/project/'` and VitePress's top-level
  `base: '/project/docs/'`. Align each router and hosting mount with those URLs.
- Build into disjoint directories, such as `.build/landing` and `.build/docs`.
  After both succeed, assemble a publish tree with landing output at its root
  and documentation output under `docs/`. Do not have either build empty the
  other's output or recursively copy the combined output into itself.
- Cross the app/docs boundary with normal links and full page navigation unless
  an explicit integration handles it. Route docs requests before any landing
  app's SPA fallback. Keep docs' generated HTML/404 behavior intact.
- Share source assets or design tokens intentionally. Do not import another
  build's hashed filenames; deploy each output's assets under its own base.

For either approach, preview the assembled output at the real prefix. Check
home-to-docs and docs-to-home navigation, deep-page reloads, images/fonts, 404s,
and hydration. A successful root-only dev session cannot verify subpath hosting.

Official references: [Default-theme layouts](https://vitepress.dev/reference/default-theme-layout),
[Extending the theme](https://vitepress.dev/guide/extending-default-theme),
[Custom themes](https://vitepress.dev/guide/custom-theme),
[Vite public base](https://vite.dev/guide/build#public-base-path).
