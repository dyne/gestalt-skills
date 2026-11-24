# Bare-metal Linux hosting

Twenty documents native PostgreSQL and Redis in its contributor setup. Its production self-host guide describes [Docker Compose](self-host.md). The procedure below adapts the production build and startup sequence from release `twenty/v2.62.2` (commit `52b5e4525f5f`) to ordinary Linux processes. It was checked against source. A complete native deployment still needs validation on the target host.

## Prepare the host and release

- Provision PostgreSQL 16, its client and contributed extensions, and Redis with `maxmemory-policy noeviction`. Create a dedicated database owned by the Twenty database role. Initialization creates schemas and uses `uuid-ossp`, `unaccent` and `citext`. Have the database administrator provision those extensions if the role cannot. Keep the database and Redis on private addresses.
- Build in a fresh checkout of the selected Twenty release. Use its `.nvmrc` and pinned Yarn via Corepack (Node 26.13.1 and Yarn 4.18.1 at this tag). On Node 26 install Corepack if needed, then enable its Yarn shim. Use a build host with enough RAM for the frontend build and the same architecture and compatible system libraries as the runtime host.
- From the checkout root, build the translations, backend and browser bundle, then place the bundle where the production server serves it. Stop at the first failed command.

```sh
set -e
yarn install --immutable
for package in twenty-server twenty-emails twenty-front; do
  yarn nx run "${package}:lingui:extract"
  yarn nx run "${package}:lingui:compile"
done
yarn nx run twenty-server:build
NODE_OPTIONS=--max-old-space-size=8192 yarn nx build twenty-front
mkdir -p packages/twenty-server/dist/front
cp -a packages/twenty-front/build/. packages/twenty-server/dist/front/
test -s packages/twenty-server/dist/front/index.html
```

Keep the built workspace with its dependencies, workspace symlinks, compiled shared packages and generated assets. The server's `dist` directory alone is insufficient. For another tag compare its `packages/twenty-docker/twenty/Dockerfile`, sibling `entrypoint.sh` and `packages/twenty-server/package.json` with these steps. Those files specify how Twenty assembles and starts that release.

## Configure and initialize

Give the maintenance commands, web service and worker the same protected environment. Set `NODE_ENV=production`, `APP_VERSION=2.62.2` (match the deployed release), `PG_DATABASE_URL`, `REDIS_URL`, the external HTTPS origin in `SERVER_URL`, and `NODE_PORT=3000`. Generate a new installation's `ENCRYPTION_KEY` with `openssl rand -base64 32` and retain it for restores. For local files, set `STORAGE_TYPE=local` and `STORAGE_LOCAL_PATH` to the same persistent absolute directory writable by both services, outside the release tree.

Run the following as the service account from `packages/twenty-server`, with the production environment loaded. Only on a **new, empty Twenty database**, run `yarn database:init:prod` first. When adopting an existing installation, verify its identity and migration state before touching it. The release entrypoint uses the presence of the `core` schema to distinguish an initialized database.

```sh
set -e
yarn command:prod cache:flush
yarn command:prod upgrade
yarn command:prod cache:flush
yarn command:prod cron:register:all
yarn command:prod upgrade:status
```

Run that sequence once per deployment. Inspect migration status and resolve failures before serving traffic.

## Run and verify

Supervise two foreground processes as an unprivileged account. Both use the built release's `packages/twenty-server` as their working directory. For systemd, give each unit that `WorkingDirectory`, the same `EnvironmentFile`, a `User`, and `Restart=on-failure`. Use an absolute path to the release-compatible Node executable in each `ExecStart`. Make Node and the pinned Yarn available on the service account's PATH as well.

| Process | Command from the server package |
| --- | --- |
| Web UI and API | `node dist/main` (the `yarn start:prod` script) |
| Queue worker | `node dist/queue-worker/queue-worker` (the `yarn worker:prod` script) |

After database preparation, start the web service. Check `curl -fsS http://127.0.0.1:3000/healthz`, then start the worker. Put a TLS reverse proxy in front of port 3000 and restrict direct network access to that port. Open the configured origin, sign in, save and reopen a record, upload and retrieve a file, and trigger a queued job. A passing health probe with a blank UI points to the frontend artifact or proxy. A pending job calls for checking the worker journal and its Redis and database settings.

## Upgrade or restore

Build the new release alongside the old one. Quiesce writes and stop the worker and web process. Back up PostgreSQL, uploads, service configuration and encryption keys together, and verify a restore on a separate host or database. With the target release's environment and `APP_VERSION`, run its upgrade sequence once. Start both processes on that same release and repeat the record, file and queue checks. A rollback after a schema migration requires a compatible database and file backup as well as the previous code and keys.
