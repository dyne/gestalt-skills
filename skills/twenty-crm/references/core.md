# Core development

Use this workflow inside the Twenty source monorepo. The app CLI's local server runs a packaged image. To see an edit to core, start the services from the checkout containing that edit.

## Start the source preview

Use the Node version in `.nvmrc` and the Yarn version in the root `packageManager`. Install dependencies from the root. For a fresh development checkout with a local Docker engine:

```sh
corepack enable
yarn install --immutable
bash packages/twenty-utils/setup-dev-env.sh --docker
yarn start
```

The setup script provisions PostgreSQL and Redis, prepares the frontend/server environment and initializes the development schema. On an existing setup, check the package `.env` files and database target before running setup. Use `yarn start` directly when infrastructure is ready. Reserve `--reset` and `database:reset` for disposable data.

The root start script runs the React frontend on port 3001, the NestJS API on 3000 and the background worker. Open `http://localhost:3001` for the UI and check `http://localhost:3000/healthz` for the API. Use the development workspace's login. For a workflow change, trigger a job and inspect its result. A responding API does not exercise the worker.

## Choose a check for the change

| Changed area | Focused command from repository root |
| --- | --- |
| Server or frontend behavior | `npx jest --config packages/twenty-server/jest.config.mjs --runTestsByPath path/to/file.spec.ts` (use the front config for frontend tests). For the whole package, `npx nx test twenty-server` or `npx nx test twenty-front`. |
| Shared types and helpers | Rebuild with `npx nx build twenty-shared --skip-nx-cache` after edits or branch switches, then rerun the dependent package's test or typecheck. |
| GraphQL schema | Run `npx nx run twenty-front:graphql:generate` against the development server. Use `--configuration=metadata` for the metadata schema. Check generated callers and the owning package. |
| Server integration with a disposable test DB | `npx nx run twenty-server:test:integration:with-db-reset` initializes test state and runs the integration suite. Inspect the test DB configuration before invoking it. |
| Core UI component | Read the checkout's `DESIGN.md`. Preview the story with `npx nx run twenty-ui:storybook:serve:dev` (6008) or `npx nx run twenty-front:storybook:serve:dev` (6006). For a UI unit test use `npx vitest run --root packages/twenty-ui --project unit <file>`. |
| User journey across UI and API | Use a seeded, disposable instance and a running source frontend. In a fresh checkout `npx nx setup twenty-e2e-testing` installs Playwright browsers and copies the package's example environment. Check `FRONTEND_BASE_URL` and test credentials, then run `npx nx test twenty-e2e-testing` or `npx nx test:ui twenty-e2e-testing`. |

Use the package's `project.json` or `npx nx show project <package>` to resolve target differences between revisions. When a dependent package reports a surprising stale pass, run its TypeScript check directly in that package with `npx tsgo -p tsconfig.json --noEmit`.
