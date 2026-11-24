# Preview, test and ship an app

## Connect a development workspace

From the app directory, with Docker running on a local socket, start the development instance. It serves the UI, API and worker on loopback. On first start the CLI selects an image compatible with `engines.twenty` if available. Existing instances retain their version and data.

```sh
twenty local start
twenty auth login --url http://localhost:2020 --name local
twenty auth status --remote local
```

Use the URL printed by the CLI if the port differs. For an existing development workspace, sign in to its actual URL and use its remote name. An explicit `--remote` takes precedence over the environment. For unattended commands choose either `TWENTY_REMOTE` or the pair `TWENTY_API_URL` and `TWENTY_API_KEY`. Otherwise the CLI uses the saved default.

## Check and preview

1. Run `yarn typecheck` in a scaffolded app to check source and tests. Run `twenty app build --json` for a local bundle and inspect `data.manifest` for the expected entities and UUIDs.
2. For a **metadata preview**, run `twenty app plan --remote local`. It requires an authenticated remote and previews creates, changes and deletions. For a new registration the CLI can return `PLAN_UNAVAILABLE`. If the request is preview-only, report that limit with the local manifest. When first installation is intended, run `twenty app apply --create --remote local` in the development workspace.
3. For an existing app, review the plan and run `twenty app apply --remote local` for a single sync. Normal apps can prune owned definitions missing from source, including fields and their data. For intentionally partial source, pass `--no-prune` to **both** plan and apply. The workspace Custom app defaults to additive sync on newer servers. Experimental `app pull` overwrites supported definitions and exports only part of the workspace. Preserve local changes before pulling.
4. For a **live UI preview**, run `twenty app dev --remote local` for continued sync as files change, or use the single apply above. Run `twenty open --remote local`, navigate to the surface that references the component and exercise it with a test record. Check that an edit appears after sync. A clean bundle alone cannot establish that a component works in the host's partial DOM.
5. For logic, open `twenty app logs --remote local` before triggering the event. To invoke a deployed function directly, use `twenty app exec --name FUNCTION_NAME --remote local` with browser sign-in. API keys cannot execute this command. Confirm the expected record change or response.

On a failed sync, locate the reported entity UUID in the manifest, check registration ownership and inspect the remote again before retrying. For stale record types use `twenty app generate-client --remote local`. Use `twenty doctor --offline` for toolchain issues and `twenty local logs --lines 100 --no-follow` for server startup issues. `twenty local stop` preserves the preview data.

## Test in isolation

Run `yarn test:unit` for scaffolded unit tests. The separate Vitest integration suite checks a real installation. Its global setup uninstalls an existing copy, applies the app, and uninstalls again in teardown. Uninstall deletes app-owned objects, fields and records. The scaffold can default to the preview URL on port 2020, so set the test target explicitly.

```sh
twenty local start --test
twenty local status --test
```

In that test workspace, create a key under **Settings → Developers → API** and set it as `TWENTY_TEST_API_KEY` in the invoking shell. Its role needs `APPLICATIONS` and `UPLOAD_FILE` for apply, plus the record permissions your tests exercise. Use the reported test URL if it differs from the default below.

```sh
(
  unset TWENTY_REMOTE
  export TWENTY_API_URL=http://localhost:2021
  export TWENTY_API_KEY="${TWENTY_TEST_API_KEY:?Set the API key for this test workspace}"
  yarn test
)
twenty local stop --test
```

The scaffold's CLI subprocess and Vitest workers need the same target. Assert both installation metadata and task behavior, such as creating an invoice and reading back its amount and company. Keep tests that install the same app serial. For CI, use the scaffold's ephemeral server workflow and pin the tested CLI and server versions.

## Deliver a version

For a private release, bump `package.json#version` above the last deployed version, check `engines.twenty`, run `twenty app publish --private --remote staging`, then `twenty app install --remote staging` in the intended workspace. Verify installed behavior there. Plain `twenty app publish` targets npm and is a separate public release operation.
