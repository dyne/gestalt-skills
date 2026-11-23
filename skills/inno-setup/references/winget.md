# Prepare a WinGet submission

## Identify the release

Search the community source with `winget search --name "Display Name" --source winget`. For an existing entry, inspect `winget show --id Publisher.Product --exact --source winget` and its latest accepted manifests. Preserve the identifier, casing, locales and useful metadata. For a first listing, agree on a stable identifier with the maker. The dotted ID, display publisher, package display name and Inno AppId serve different purposes. Match the latter three against what Windows actually registers. Check for an open PR for the same version.

Use the publisher's version-specific HTTPS release URL that downloads the installer without login or visiting an HTML page. Record the SHA-256 of the final signed or unsigned installer. Download the public asset and compare its hash with the local one before submitting. Use a distinct asset URL and digest for each distinct payload. Keep public release assets byte-stable. Check the repository's current requirements, especially the submission rights and unattended-install requirements. [WinGet manifest guide](https://learn.microsoft.com/en-us/windows/package-manager/package/manifest) · [Repository policies](https://learn.microsoft.com/en-us/windows/package-manager/package/windows-package-manager-policies)

## Generate the files

For a release with one installer asset, copy the three templates and renderer into the target repository. Rename each `Example.Dial` prefix to the exact package ID and update every `PackageIdentifier`. The renderer reads the app name, publisher, homepage, description and license from the same product record used to stamp the executable. Keep these tokens in the default-locale template. Preserve translations when adding other locales. Match the default locale across filenames and manifests. Keep variable tokens as **unquoted whole scalars**. The renderer quotes them as YAML strings. Keep existing package metadata such as `AppsAndFeaturesEntries` when needed for detection.

The starter uses schema 1.28.0 from the community repository's submission checklist. At submission time check the current checklist and align all three schema comments and `ManifestVersion` values. Use a WinGet client that supports the selected schema. [PR checklist](https://github.com/microsoft/winget-pkgs/blob/master/.github/PULL_REQUEST_TEMPLATE.md) · [Validation failure guide](https://github.com/microsoft/winget-pkgs/blob/master/doc/ValidationFailureGuide.md)

| Project destination | Skill asset |
| --- | --- |
| `build/winget/<ID>.yaml.in` | `assets/winget/Example.Dial.yaml.in` |
| `build/winget/<ID>.installer.yaml.in` | `assets/winget/Example.Dial.installer.yaml.in` |
| `build/winget/<ID>.locale.en-US.yaml.in` | `assets/winget/Example.Dial.locale.en-US.yaml.in` |
| `build/render-winget.py` | `assets/render-winget.py` (Python 3.10+) |
| `build/product.json`, `build/product_metadata.py` | Same adopted files used for the executable and installer |

Set `InstallerType: inno` and the payload architecture on the installer entries. List only verified scopes. If both entries use a common EXE, give each its matching `Custom` scope switch. A single fixed-scope installer needs just one entry and no scope switch. Use `Silent` for no UI and `SilentWithProgress` for progress without confirmation. Supply optional product codes or display-version overrides only from observed install registration. For different installer assets per architecture, extend the templates and renderer to bind each row to its own verified URL/hash pair, or use WinGetCreate's multiple-URL support.

Example release step in PowerShell, after compiling and any signing:

```powershell
$version = $env:RELEASE_VERSION
$file = "dial-$version-windows-x64-winget-setup.exe"
$url = "https://github.com/OWNER/REPO/releases/download/v$version/$file"
python -B build/render-winget.py --product build/product.json --templates build/winget --version $version --installer "dist/$file" --url $url
if ($LASTEXITCODE) { throw 'Manifest generation failed' }
```

Replace the release URL pattern with the real project's. For `Example.Dial` version `1.2.3`, the output is `manifests/e/Example/Dial/1.2.3/` with the three final `.yaml` files. Include that folder as a CI artifact when submission runs later. An identical rerun succeeds. If the same version has different content, inspect the release and use a fresh output root for the corrected draft.

**WinGetCreate route.** Install the official utility on the Windows packaging host if needed (`winget install --id Microsoft.WingetCreate --exact`). For a first listing run `wingetcreate new "$url"`, fill the prompts and choose local output at the submission prompt. For an accepted package, `wingetcreate update Example.Dial --version $version --urls "$url" --out .\draft` updates the existing metadata. Review the emitted folder and every installer selection, scope, URL and hash. The CLI's `--submit` option opens a PR when used with update. [New command](https://github.com/microsoft/winget-create/blob/main/doc/new.md) · [Update command](https://github.com/microsoft/winget-create/blob/main/doc/update.md)

## Validate, exercise, submit

On Windows, point WinGet at the directory containing the complete rendered manifest set:

```powershell
$manifest = ".\manifests\e\Example\Dial\$version"
winget validate --manifest "$manifest"
if ($LASTEXITCODE) { throw 'Manifest validation failed' }
winget install --manifest "$manifest" --scope user --silent --disable-interactivity --accept-source-agreements --accept-package-agreements
if ($LASTEXITCODE) { throw 'WinGet install failed' }
```

Local manifest installation may require enabling `LocalManifestFiles` in the disposable test environment with elevated `winget settings --enable LocalManifestFiles`. Use a test host on which that setting is permitted. Test machine scope separately from an elevated session if advertised. Exercise the installed program, check `winget list --id Example.Dial --exact` for version recognition (also inspect Installed Apps for a first listing), and exercise silent uninstall. Fix and rerun on hash mismatch, a hung dialog, an architecture mismatch or a detection failure. For a hash mismatch check the download target, signing order and published bytes. For a dialog check scope elevation, optional launches and custom installer code. [Local manifest installs](https://learn.microsoft.com/en-us/windows/package-manager/winget/install) · [WinGet validate](https://learn.microsoft.com/en-us/windows/package-manager/winget/validate)

As an alternative for a Windows host with Sandbox enabled, run `.\Tools\SandboxTest.ps1 <manifest-directory>` from a checkout of `microsoft/winget-pkgs`. Inspect the installed app and the before/after registration output.

For an authorized submission, authenticate WinGetCreate to GitHub and run `wingetcreate submit "$manifest"`. Alternatively, put just the version folder in the correct path in a fork of `microsoft/winget-pkgs` and open a PR to the upstream default branch. Review bot checks and any contributor agreement prompt. Address reported findings in the same PR. After merge and catalog propagation, verify with `winget show --id Example.Dial --exact --source winget` and install from the catalog on a clean host. A local validation, an open PR, and a discoverable release are separate milestones. [Submit command and authentication](https://github.com/microsoft/winget-create/blob/main/doc/submit.md) · [Community submission and validation](https://learn.microsoft.com/en-us/windows/package-manager/package/repository)
