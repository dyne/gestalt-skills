# Build and exercise both profiles

Save the starter assets as `build/installer.iss` and `build/build-installer.ps1`, alongside `product.json` and `product_metadata.py`. The PowerShell wrapper uses Python 3.10+ to generate an Inno include from the product record on each build. Fill the three remaining project markers for the application GUID, install folder and artifact slug. Keep an existing AppId verbatim. For a new GUID, run `[guid]::NewGuid().ToString()` once and substitute the bare value. The resulting directive looks like `AppId={{01234567-89ab-cdef-0123-456789abcdef}`. Keep it across releases. [AppId documentation](https://jrsoftware.org/ishelp/topic_setup_appid.htm)

**Classic wizard.** Build with `-InstallerProfile Classic`. Keep directory and ready pages, add the chosen license page, language or Start menu shortcut if appropriate. For example, a GUI app can have an `[Icons]` entry with `Name: "{group}\Product"; Filename: "{app}\product.exe"`. Verify by launching normally and walking through install and cancel.

**Silent install for WinGet.** Build with `-InstallerProfile Silent`. This suppresses wizard pages and produces a separate `-winget-setup.exe` artifact. Invoke it with `/SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART` and the appropriate scope switch for unattended installation. Ship the license file. Guard custom UI with `WizardSilent` and `UninstallSilent`, use `skipifsilent` on optional launches, and ensure child installers support unattended execution. [Setup parameters](https://jrsoftware.org/ishelp/topic_setupcmdline.htm) · [Uninstaller parameters](https://jrsoftware.org/ishelp/topic_uninstcmdline.htm)

**Scope and architecture.** The starter targets an x64 application with Inno 6.3+ and allows either install scope. A normal user can install with `/CURRENTUSER`. Use `/ALLUSERS` from an already elevated process for machine-wide unattended work. UAC still applies. For fixed user or machine installs remove the override, select `PrivilegesRequired=lowest` or `admin`, and omit scope overrides from the invocation. Use `{autopf}` and `HKA` for scope-aware locations. Change both architecture directives and all path/asset labels to match the payload. Arm64 uses `arm64`. For x86 payloads use the 32-bit install mode and `x86compatible` with a compatible Setup compiler target. Check the PE headers of shipped executables and native DLLs before packaging. [Scope overrides](https://jrsoftware.org/ishelp/topic_setup_privilegesrequiredoverridesallowed.htm) · [Architecture selection](https://jrsoftware.org/ishelp/topic_setup_architecturesallowed.htm)

## One packaging target

Map each `[Files]` source to the project's actual output. Relative source paths start at the script directory. Include the app-private DLLs, assets and redistribution notices the binary needs. Use explicit files or a clean, purpose-built staging directory. A missing required input should fail the build.

Add desktop integration only when the package needs it. For **Open With**, register an owned ProgID under `HKA\Software\Classes`, its icon, a quoted open command and a value under the extension's `OpenWithProgids`. Set `ChangesAssociations=yes`; uninstall only the registered ProgID and its value. For a CLI on **PATH**, update the matching user or machine environment, preserve other entries and expandable values, compare full entries case-insensitively and record whether setup added its directory. Preserve ownership on upgrade, remove only the owned entry on uninstall and set `ChangesEnvironment=yes`. Test from a new terminal, including a pre-existing entry and a directory with spaces.

For GNU Make, add the following **after the default goal** or in an included fragment. Connect the existing Windows release target(s) that produce the stamped binaries using the [application resource recipe](stamping.md). Set `VERSION` from the project's normal version source. Keep the command line as one recipe with a literal tab.

```make
.PHONY: win-installer
INSTALLER_PROFILE ?= Classic
win-installer: out/windows-x64/dial.exe
	pwsh -NoProfile -File build/build-installer.ps1 -Version "$(VERSION)" -InstallerProfile "$(INSTALLER_PROFILE)"
```

For CMake use `add_custom_target(win-installer ... DEPENDS <actual-target> VERBATIM)` and resolve configuration-specific paths such as `$<TARGET_FILE:...>` when staging. For Meson use a custom target with the executable as an input and the installer as an output. Preserve the same public target name and call it via the project's ordinary build tool. An installer target can run on Windows even if the rest of the project cross-compiles elsewhere.

## CI

Join the project's existing release-version and Windows build jobs. Provision or locate the selected Inno compiler and the project's native build tool on the runner. The wrapper accepts `ISCC` as a full executable path. Pass CI-derived values through environment variables. Here are GitHub Actions steps for a Windows GNU Make job with checkout, toolchain and `RELEASE_VERSION` already configured. Substitute the project's real artifact slug and use the action version policy of the repository.

```yaml
- name: Build Windows installer
  shell: pwsh
  run: |
    make win-installer "VERSION=$env:RELEASE_VERSION" INSTALLER_PROFILE=Silent
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
    $asset = "dist/dial-$env:RELEASE_VERSION-windows-x64-winget-setup.exe"
    if (!(Test-Path -LiteralPath $asset -PathType Leaf)) { throw "Missing $asset" }
- uses: actions/upload-artifact@v4
  with:
    name: windows-x64-installer
    path: dist/dial-${{ env.RELEASE_VERSION }}-windows-x64-winget-setup.exe
    if-no-files-found: error
```

Bind the version to both steps at job level, for example from an existing release job output. Give smoke jobs a timeout so an unexpected dialog fails visibly. Build the exact release asset once, apply the project's signing step if configured, exercise it, and pass those same bytes to the release job. Publish to a versioned public installer URL when releasing for WinGet. A CI artifact ZIP is for handoff within the pipeline. [Compiler invocation](https://jrsoftware.org/ishelp/topic_compilercmdline.htm)

## Windows acceptance

Use a fresh disposable Windows environment for each advertised scope. The example exercises a dual-scope CLI installer with a path containing spaces. Set `$installer` to the absolute release artifact path and adapt the app-specific probe. Run from outside the source checkout.

```powershell
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:TEMP ('Install smoke ' + [guid]::NewGuid())
$flags = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART'
function Run-Setup($exe, $arguments) {
    $p = Start-Process -FilePath $exe -ArgumentList $arguments -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw "$exe exited $($p.ExitCode)" }
}
Run-Setup $installer "/SP- /CURRENTUSER $flags /DIR=`"$dir`" /LOG=`"$dir-install.log`""
& (Join-Path $dir 'dial.exe') --version
if ($LASTEXITCODE) { throw 'Installed CLI failed' }
$uninstaller = @(Get-ChildItem -LiteralPath $dir -Filter 'unins*.exe')
if ($uninstaller.Count -ne 1) { throw 'Expected one registered installation' }
Run-Setup $uninstaller[0].FullName "$flags /LOG=`"$dir-uninstall.log`""
if (Test-Path (Join-Path $dir 'dial.exe')) { throw 'Executable survived uninstall' }
```

Also exercise the default destination without `/DIR`, and verify the Installed Apps entry's publisher, version, scope and uninstall command. Test the previous release followed by the candidate in the same scope. Check the new version, a single product entry, and preserved user data. Exercise companion binaries and any requested PATH, shortcut or Open With behavior from a fresh process. Uninstall and verify cleanup. Repeat machine scope elevated with `/ALLUSERS` when offered. Retain logs for failures. Report which profiles, architectures and scopes actually ran.
