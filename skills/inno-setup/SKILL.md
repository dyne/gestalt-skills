---
name: inno-setup
description: "Build and verify classic Inno Setup wizards, unattended installations and WinGet installers. Integrate Windows executable metadata, release signing, CMake or GNU Make, CI and public release assets."
---

# Inno Setup releases

1. Trace a single version from source/tag → shipped GUI, CLI and dependencies → clean stage → Setup → CI artifact → public download. Search source, workflow, release history and installed registration for the existing installer, AppId, signing command or service, receipts and customer asset names. Preserve upgrade identity. [Worked release trace](references/release.md)
2. Present repository candidates in **one intake**. Confirm app name, publisher, license and text file, exact welcome credit and homepage, supplied icon and wizard logos, scope, fresh interactive and silent shortcut defaults, finish-page launch target and trusted-signing requirement. Ask only for unresolved choices affecting identity, installation or signing access. Continue fixture and staging work while waiting. Publisher strings and icons identify the product in its metadata. Windows verifies publisher identity through Authenticode. [Signing decision](references/signing.md)
3. Reuse the [product record](assets/product.json) for [PE resources](references/stamping.md), installer and locale. Select the classic wizard, the same EXE with unattended switches, or the separate WinGet profile. Wire the [installer template](assets/installer.iss.in) and [build wrapper](assets/build-installer.ps1) into the project's normal `win-installer` target. [CMake and GNU Make](references/build.md)
4. Start with the [disposable Windows fixture](references/fixture.md). Exercise the real wizard, artwork, shortcut and upgrade behavior before building the application. Preserve keyboard access and GUI/CLI diagnostics. [Wizard and artwork](references/wizard.md) · [Windows subsystems](references/subsystems.md)
5. Build the release binaries, apply the signing decision, compile Setup and verify its final bytes. Smoke-test the installed **release payload**, transfer the receipt internally and verify the direct public EXE after authorized publication. For catalog distribution, render and validate the [WinGet manifests](references/winget.md) against that EXE. Report the versions, asset digest, signing state and checks actually run.
