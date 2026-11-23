# Fast Windows fixture

Run on a disposable Windows desktop or hosted Windows VM. Use Python 3.10+, Go and the official 6.4.3 compiler. The collection's Windows CI workflow downloads `innosetup-6.4.3.exe` by version and checks SHA-256 `f3c42116542c4cc57263c5ba6c4feabfc49fe771f2f98a79d2f7628b8762723b` before installing it into a private runner directory. The compiler log records the actual engine version. [Pinned compiler](https://github.com/jrsoftware/issrc/releases/tag/is-6_4_3)

From the skill directory:

```powershell
python -B fixture/run.py 'C:\Inno643\ISCC.exe' "$env:TEMP\fixture-$([guid]::NewGuid())"
if ($LASTEXITCODE) { throw 'Installer fixture failed' }
```

The fixture uses the production template and product metadata generator, two small Windows binaries, real hash-pinned release art, license, data and a staged manifest. The installed destination has spaces and a Unicode character. Each run creates its own AppId, title, Start menu group and evidence directory. The same AppId is used for both fixture versions. A Windows Job Object contains the worker and its descendants; closing it terminates leftover Setup loaders, child Setup processes and uninstallers even after timeout.

The interactive test manipulates the actual visible controls. It checks the welcome link's tab stop, license acceptance, destination and Install caption, logged page sequence, independent launch/shortcut choices, creation, removal and an initially unchecked shortcut. It captures the rendered welcome page. The silent test verifies exit status, payload hashes, installed manifest, shortcut default and absence of auto-launch. The separate WinGet build upgrades the first installation and preserves user-created data. Uninstall checks owned-file and shortcut cleanup. Keep the compiler, install and uninstall logs and PNG on failure.

The probe exercises Windows subsystem selection and redirected IO. It cannot exercise the real application's graphics driver, redistributables, data compatibility, performance, signing credentials or SmartScreen reputation. Once the fixture passes, build and smoke-test the actual release asset using the [release handoff](release.md); compare the hash again after publication.
