# App development

## Start from the scaffold

Work on macOS, Linux or WSL 2. At the documented snapshot the SDK supports Node 24 from 24.5 and Node 26 from 26.5.1. Use Yarn 4 via Corepack. Node 26 needs Corepack installed separately if missing. For an existing app, use its lockfile and CLI pin from CI.

```sh
npm install -g twenty@2.62.0
corepack enable
twenty app init invoice-tools
cd invoice-tools
yarn install
twenty app add object --name invoice --name-plural invoices \
  --create-view --create-navigation-menu-item --create-page-layout --no-input
```

The initializer writes files locally. The object command gives the new record type a view, sidebar entry and record page to preview. To add an amount, take the generated object's UUID from source and pass it to `twenty app add field --name amount --type NUMBER --object "$invoice_uuid" --no-input`. Use `twenty app add --help` for supported generators. Write other entities with the installed SDK's `define*` helpers.

Keep `twenty-sdk`, `twenty-client-sdk` and `twenty-ui` on the same generated version in `devDependencies`. The standalone CLI is the `twenty` package and has its own version. Set `engines.twenty` to cover the server features the app uses.

## Model the app

- Start with `src/application-config.ts` and the scaffold's default role. Keep one default-exported `define*(...)` call per entity file, imported from `twenty-sdk/define`. The CLI discovers these calls. Generate each new entity's UUID v4 once and retain it across renames and releases. Changing identity can turn an update into a deletion and a creation.
- Extend Person, Company or another standard type with `defineField` and the corresponding `STANDARD_OBJECT_UNIVERSAL_IDENTIFIERS` entry. Use `defineObject` for a new type. Twenty supplies system fields such as `id` and `createdAt`. For a view referencing one, use `getFieldUniversalIdentifier` with the owning app ID, object ID and field name.
- For Invoice → Company, declare a many-to-one relation field on Invoice **and** a one-to-many reverse field on Company. Each field names its owning object, the target object and the other field's universal identifier. Keep these UUIDs together so both definitions can import them. A missing reverse definition fails sync even if Company already exists.
- Scope `defineApplicationRole` to the operations and fields the app needs. A client in a user-triggered function normally uses the intersection of user and app permissions. A cron run has only app permissions. Check both roles when the same operation works on a schedule but fails in the UI.

## Implement the behavior

| Requirement | Implementation |
| --- | --- |
| React panel, settings screen or record widget | Export `defineFrontComponent` and reference its UUID from a command menu item, settings item or layout widget. Use `twenty-ui` controls and call `useTheme()` inside the component. The host supplies theme and styles. The renderer runs in a Web Worker with a partial DOM. Use host SDK actions for dialogs and navigation. |
| Authenticated server action | Export `defineLogicFunction` with a handler and `httpRouteTriggerSettings`. Set `isAuthRequired: true` for a user action. From a front component, use `RestApiClient` from `twenty-client-sdk/rest` with the route under `/s/`. The client resolves the workspace's function host and supplies the token. |
| Respond to record changes, run on a schedule, or expose an action to a workflow or AI tool | Choose the matching event, cron, workflow-action or tool trigger on the logic function. Scope record-update triggers to the relevant fields, especially when the handler writes to the same object. Keep reusable logic separate from the trigger adapter for unit tests. |
| Query CRM data or configuration | Use `CoreApiClient` from `twenty-client-sdk/core` for records and `MetadataApiClient` from `twenty-client-sdk/metadata` for workspace definitions. Declare secrets as secret app variables and consume them in server-side functions. |

For the invoice example, verify that the sidebar opens the invoice list, a new record accepts an amount, and the company relation can be read back. Follow [the app lifecycle](app-lifecycle.md) to sync and exercise it.
