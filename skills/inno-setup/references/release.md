# Trace the release all the way to the download

Bitcoin Viz v0.8.1 illustrates the handoff. The version job computed a semantic version and prepared a candidate commit. The desktop workflow built that candidate. Its Windows CMake target ran `cmake --install` into a new staging directory and packaged the tree containing `bin/bitcoin-viz.exe`, `bin/bitcoin-viz-desktop.exe`, runtime dependencies, licenses, data and `MANIFEST.json`. The template retained its existing AppId across releases. Use a different GUID for tests. The Windows artifact `binaries-windows-x86_64` carried the Setup EXE and its JSON receipt to the publish job. The public release lists the direct versioned EXE, four Unix archives and `SHA256SUMS`. [Source at the released tag](https://github.com/LuganoPlanB/bitcoin-viz/tree/v0.8.1/ci/release) · [Desktop build and smoke job](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/.github/workflows/desktop.yml) · [Customer release assets](https://github.com/LuganoPlanB/bitcoin-viz/releases/tag/v0.8.1)

For the target project, inspect version files, tag selection, install rules, resource/link inputs, `.iss` and `AppId`, `sign-exe` or signing service, workflow outputs, receipt generation and published assets. Use `gh release view TAG --json assets,tagName,url` to identify the real URL and compare it to WinGet. Trace the candidate SHA through every dependent job. Preserve an existing identifier even when filenames or branding change.

## Transfer and publication

1. Once the fixture passes, build the release configuration from its actual dependencies. Install to a clean stage. Check the installed manifest, GUI and CLI paths, DLL load, real data and license inventory. Sign as required, generate Setup, verify its signature and write a receipt recording version, candidate commit, architecture, exact filename, signing state and SHA-256. Run the **actual Setup** from a clean user profile, exercise installed commands and the project's normal runtime smoke test outside the checkout, then uninstall. For Bitcoin Viz that includes the desktop graphics smoke with the Windows software GL setup and any supported redirected diagnostic paths.
2. Pass Setup **and** receipt via `actions/upload-artifact` using explicit paths and `if-no-files-found: error`. This ZIP is an internal transport. In the publish job download the artifacts into a fresh directory and verify their digests and candidate IDs against the receipts. Build a public allowlist from the expected platform matrix. Fail on missing or duplicate required assets and inspect an existing draft for stale asset names before making it public.
3. For a Windows-only project the authorized upload could use the following commands from the verified asset directory. For a multi-platform release explicitly append each expected Unix archive. Generate `SHA256SUMS` over public files only if the project distributes it. Keep receipts and old Windows ZIPs outside the upload argument list.

```sh
exe="bitcoin-viz-${tag}-windows-x86_64-setup.exe"
gh release upload "$tag" "$exe" SHA256SUMS --repo "$repo"
gh release view "$tag" --repo "$repo" --json assets --jq '.assets[] | [.name,.url] | @tsv'
curl --fail --location "https://github.com/$repo/releases/download/$tag/$exe" -o "$verify_dir/$exe"
# Compare with the retained digest from the signed-and-tested candidate.
(cd "$verify_dir" && printf '%s  %s\n' "$expected_sha256" "$exe" | sha256sum -c -)
```

For v0.8.1 the exact Windows name is `bitcoin-viz-v0.8.1-windows-x86_64-setup.exe`. Verify the final public asset set and direct URL after the draft is published. The App Installer/WinGet URL points to the EXE. [Release job](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/.github/workflows/release.yml) · [Direct v0.8.1 installer](https://github.com/LuganoPlanB/bitcoin-viz/releases/download/v0.8.1/bitcoin-viz-v0.8.1-windows-x86_64-setup.exe)

## Isolate a failing Windows job

Use the project's supported Windows-only workflow or matrix filter if it has one. Inspect available dispatch inputs first. For an existing run, `gh run view RUN_ID --json jobs --jq '.jobs[] | [.databaseId,.name,.conclusion]'` identifies the Windows job. `gh run rerun --job JOB_DATABASE_ID` reruns that job and eligible dependents under GitHub's rerun rules. Prefer a non-publishing test workflow when diagnosing an installer. A new workflow can expose `workflow_dispatch` for an isolated Windows fixture. Retain the normal version, desktop matrix and quality dependencies for publication. [GitHub job reruns](https://cli.github.com/manual/gh_run_rerun)
