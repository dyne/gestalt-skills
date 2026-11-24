# Self-hosting with Docker Compose

## Install a persistent instance

Use Docker Engine with Compose v2 and at least 2 GB of RAM. Start with the official release's paired `docker-compose.yml` and `.env.example`. In a Twenty checkout these live under `packages/twenty-docker/`. Keep a stable deployment directory and Compose project name so subsequent starts reuse the volumes.

For a first install, run from the root of a checkout at the chosen release tag. Supply a **new** deployment directory. The restrictive umask protects the environment file when it later holds credentials.

```sh
umask 077
mkdir "${TWENTY_DEPLOY_DIR:?Set a new deployment directory}" &&
  cp packages/twenty-docker/docker-compose.yml "$TWENTY_DEPLOY_DIR/" &&
  cp packages/twenty-docker/.env.example "$TWENTY_DEPLOY_DIR/.env"
```

In that directory, edit `.env` before starting the stack:

| Setting | Value and effect |
| --- | --- |
| `TAG` | Pin the exact published image tag for the Compose files you selected. Server and worker use the same Twenty image. |
| `SERVER_URL` | Set the origin the browser will use, including scheme and port. Use the public HTTPS origin behind a reverse proxy. For a host-local trial the default is `http://localhost:3000`. |
| `PG_DATABASE_PASSWORD` | Set a fresh password before the first database startup. `openssl rand -hex 32` produces a value suitable for the interpolated connection URL. An initialized PostgreSQL volume retains its database credentials when `.env` changes. |
| `ENCRYPTION_KEY` | Generate a separate value with `openssl rand -base64 32`. Keep it recoverable with your deployment secrets. Encrypted credentials in a restored database require the original key. Preserve `APP_SECRET` on installations that rely on it. |
| `STORAGE_TYPE` | With `local`, server and worker share the `server-local-data` volume. With `S_3`, configure the bucket, region and appropriate credentials or identity on both services. |

On the documented Compose version, port `3000:3000` publishes on the host interfaces. For a host-local preview or a reverse proxy running on the same host, bind `127.0.0.1:3000:3000`. For a containerized proxy, route it to the server over the shared Docker network. Configure TLS and forwarding for the browser-facing origin. Keep PostgreSQL and Redis internal.

```sh
cd "$TWENTY_DEPLOY_DIR"
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=80 server worker
docker compose exec -T server curl -fsS http://localhost:3000/healthz
```

The default services are `server`, `worker`, `db` (PostgreSQL 16) and `redis`. Server startup handles migrations. The worker waits for server health and handles queued jobs. Open the configured origin, complete initial workspace setup, then verify the paths the deployment needs: sign in, create and reopen a test record, retrieve an uploaded file, or trigger a background workflow and observe completion.

## Configure or diagnose

Many settings are editable under **Settings → Admin Panel → Configuration Variables**. Infrastructure settings such as database connectivity, server URL and encryption keys come from the environment. Compose uses `.env` for substitution. To pass a new setting to containers, declare it in the affected service environments and run `docker compose up -d` to recreate them. Match server and worker connection, storage and encryption settings.

- **Failed login, redirects or callbacks:** compare the browser's external origin with `SERVER_URL` and proxy forwarding.
- **Jobs queued indefinitely:** inspect `docker compose logs --tail=100 worker`, then check its Redis and database connectivity.
- **A workflow reports function execution is disabled:** inspect the active logic-function driver in the admin configuration. Production defaults to `DISABLED`. For hosted execution, configure `LOGIC_FUNCTION_TYPE=LAMBDA`, its region, execution role and AWS credentials. Set `LOGIC_FUNCTION_LAMBDA_LAYER_BUCKET` to a bucket in the function region, or configure the documented `STORAGE_S3_NAME` fallback. The local driver runs trusted development code without process isolation.
- **Uploads fail:** check the shared volume and its ownership or the S3 bucket settings for both services. An empty `STORAGE_S3_NAME` reaches the application as an empty bucket name.

## Back up and upgrade

Back up PostgreSQL, uploaded files (volume snapshot or S3 backup), the Compose configuration and the encryption keys as one recoverable set. Quiesce writes for a consistent recovery point and verify restoration in a separate deployment. With the bundled DB and default user, `docker compose exec -T db pg_dumpall -U postgres > databases.sql` captures PostgreSQL. Use the configured DB user or the managed provider's backup mechanism when applicable.

Check the source and target release's database requirements and upgrade path. On the supported cross-version path (from v1.23), the server runs migrations on startup; earlier releases need their version-specific upgrade steps. With a verified backup, stop the stack with `docker compose down`, reconcile the target release's Compose and environment changes, set the new `TAG`, then run `docker compose pull` and `docker compose up -d`. Preserve the existing project name and volumes. The `-v` option to `down` removes named volumes.

Check `docker compose exec -T server yarn command:prod upgrade:status`, service health, an existing record, an uploaded file and one queued job. If a migration fails, preserve logs and volumes. Reverting the image tag alone cannot reverse a migrated database. Recovery uses the matching pre-upgrade data, configuration, keys and image.
