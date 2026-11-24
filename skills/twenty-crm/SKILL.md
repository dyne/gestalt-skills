---
name: twenty-crm
description: Build, test and preview TypeScript apps for Twenty CRM, integrate workspace REST and GraphQL APIs or webhooks, develop the Twenty core monorepo, and self-host or upgrade Twenty with Docker Compose.
---

# Build with Twenty CRM

Start from the artifact the user wants to change. An installable app has `twenty-sdk` definitions and its own package manifest. An external integration needs the target workspace's schema and credentials. A core change lives in the Twenty Nx monorepo. A persistent deployment has its own Compose project and data volumes.

| Task | Open this local guide |
| --- | --- |
| Scaffold an app, model objects and relations, add logic or a UI surface | [App development](references/apps.md) |
| Preview a metadata change or a live screen, run unit and integration tests, diagnose sync or ship a version | [Preview, test and ship an app](references/app-lifecycle.md) |
| Integrate an external service with workspace records, schema, OAuth or webhooks | [Workspace APIs](references/integrations.md) |
| Change the CRM itself, start the frontend and worker, run package tests, Storybook or Playwright | [Core development](references/core.md) |
| Install or operate a persistent instance, verify workers and storage, back up or upgrade | [Self-hosting](references/self-host.md) |

Identify the target before applying a change. Use the app directory and a named development remote for app work, a disposable workspace for integration tests, or the intended Compose project for operations. Match verification to the result requested. For a new record widget, for example, inspect the metadata plan, open the widget on a real test record, then exercise the action it exposes.

These guides use the Twenty source snapshot `7a76ca89b73` (CLI and SDK 2.63.0). For another release, use its installed CLI help, SDK types, package scripts and Compose configuration to resolve differences.
