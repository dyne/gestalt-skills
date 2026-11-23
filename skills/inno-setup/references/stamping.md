# Stamp the application during its Windows build

Put the confirmed fields in `build/product.json` and copy `assets/product_metadata.py` alongside it. When the package already owns these fields in project metadata, generate the record from that source. Resolve asset paths relative to the JSON file. Keep the human-readable product name separate from the executable basename, WinGet identifier and stable Inno AppId.

| Input | Where it goes |
| --- | --- |
| Name and publisher | Application VERSIONINFO, installer file properties, Installed Apps, WinGet default locale |
| Homepage, description and license | Executable description and Comments, installer publisher link and bundled license text, WinGet PackageUrl, ShortDescription and License |
| Release version | File and product version text, Inno AppVersion and WinGet PackageVersion |
| Optional `copyright` | LegalCopyright on the application and installer. Use the supplied notice verbatim. |
| Optional `iconFile` | Application icon group, Setup icon, installed application/shortcut icon and Installed Apps display icon |

Use the license name or SPDX expression the project supplies and the corresponding distributable license text. Include any other required notices in the installer's file list. For a classic wizard, enable `LicenseFile={#ProductLicenseFile}` if a license page is wanted and the file is in an Inno-supported display format. The silent profile ships the text without adding a confirmation page.

Prefer the project's multi-resolution Windows ICO. If the maker supplies PNG/SVG artwork, use their source artwork and an available image converter to create the ICO once. For example, from a square, transparent PNG run `magick logo.png -define icon:auto-resize=256,64,48,32,16 app.ico`. Inspect small sizes and transparency. A wide logo can also supply separate wizard artwork via `WizardImageFile` or `WizardSmallImageFile` in a format supported by the selected compiler. With no supplied artwork leave `iconFile` null and preserve any existing icon resources. In the public WinGet catalog, icon metadata is populated during validation. [SetupIconFile](https://jrsoftware.org/ishelp/topic_setup_setupiconfile.htm) · [WinGet locale and icon fields](https://github.com/microsoft/winget-pkgs/blob/master/doc/manifest/schema/1.28.0/locale.md)

## Compile and link

Generate one resource script per project-owned Windows executable before linking. The helper preserves Unicode strings and encodes the release's numeric core in the four 16-bit file/product version components. For instance, `2.4.7-beta.2` becomes `2,4,7,0` while the full release remains visible in the version strings. If the project uses another numbering scheme, pass the release's explicit numeric mapping through `WINDOWS_FILE_VERSION` to both the application build and installer job.

For GNU Make with MinGW, adapt these rules to the project's existing Windows binary target. Replace `WIN_OBJECTS`, `WIN_LDLIBS` and tool names with its existing link inputs. Use a separate intermediate directory per target architecture/configuration. For builds running simultaneously with different versions, use a separate build directory per release.

```make
WIN_OUT := out/windows-x64
WINDRES := x86_64-w64-mingw32-windres
WIN_CC := x86_64-w64-mingw32-gcc
PYTHON ?= python
.PHONY: FORCE
FORCE:

$(WIN_OUT)/dial.rc: FORCE build/product.json build/product_metadata.py
	$(PYTHON) -B build/product_metadata.py rc --product build/product.json --version "$(VERSION)" --output "$@"

# Add the actual ICO as a prerequisite here when iconFile is supplied.
$(WIN_OUT)/dial-resource.o: $(WIN_OUT)/dial.rc
	$(WINDRES) --codepage=65001 -i "$<" -O coff -o "$@"

$(WIN_OUT)/dial.exe: $(WIN_OBJECTS) $(WIN_OUT)/dial-resource.o
	$(WIN_CC) $(WIN_LDFLAGS) -o "$@" $^ $(WIN_LDLIBS)
```

Keep the package's default goal ahead of these rules. The helper leaves an identical `.rc` untouched so a version check alone need not relink the application. A change to an ICO's bytes must recompile the resource even when its path stays the same. For a companion EXE add `--exe dial-tool.exe --description "Dial helper"` and link a separate resource object. Leave third-party or previously signed payloads with their original identity.

With MSVC, generate the same UTF-8 `.rc`, run `rc.exe /c 65001 /fo dial.res dial.rc`, and add `dial.res` to the actual EXE link inputs. In CMake with RC enabled, the generated `.rc` can be a source of the executable target. A Go build can consume a correctly targeted COFF `.syso` in the Windows main package. For an SDK-style .NET build use its native Company, Product, FileVersion, InformationalVersion and ApplicationIcon properties from the shared metadata. Merge with an existing version resource or icon when present so each EXE carries one effective version record. Avoid modifying signed bytes. [Windows VERSIONINFO](https://learn.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource) · [GNU windres formats](https://sourceware.org/binutils/docs/binutils/windres.html)

For CMake, make the generated resource a linker input on each Windows executable. For example, with an existing `dial` target:

```cmake
if(WIN32)
  enable_language(RC)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  set(meta "${PROJECT_SOURCE_DIR}/build")
  set(rc "${CMAKE_CURRENT_BINARY_DIR}/dial-version.rc")
  file(GENERATE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/win-version.txt" CONTENT "${PROJECT_VERSION}")
  add_custom_command(OUTPUT "${rc}"
    COMMAND Python3::Interpreter "${meta}/product_metadata.py" rc --product "${meta}/product.json"
            --version "${PROJECT_VERSION}" --exe dial.exe --output "${rc}"
    DEPENDS "${meta}/product_metadata.py" "${meta}/product.json"
            "${CMAKE_CURRENT_BINARY_DIR}/win-version.txt" VERBATIM)
  target_sources(dial PRIVATE "${rc}")
  # With Ninja/Makefiles, when iconFile is supplied:
  # set_property(SOURCE "${rc}" APPEND PROPERTY OBJECT_DEPENDS "${meta}/app.ico")
endif()
```

Use a distinct output for each binary. For a Visual Studio generator use its native resource dependencies and verify an icon-only rebuild. If the display version has a prerelease suffix, pass the pipeline's full version string in place of CMake's numeric project version.

## Inspect the linked EXE

On Windows, run the following immediately after linking and repeat on the installed copy. Adapt the path for each binary. Also inspect the setup EXE's CompanyName, ProductName and version after ISCC.

```powershell
$product = Get-Content -Raw build/product.json | ConvertFrom-Json
$v = (Get-Item "out/windows-x64/$($product.executable)").VersionInfo
if ($v.CompanyName -cne $product.publisher -or $v.ProductName -cne $product.name -or
    $v.OriginalFilename -cne $product.executable -or $v.ProductVersion -cne $env:RELEASE_VERSION) {
    throw "Unexpected executable metadata: $($v | Out-String)"
}
```

On a cross-build host, `llvm-readobj --coff-resources app.exe` identifies VERSIONINFO and, when configured, ICON/GROUP_ICON resources. Decode the linked version strings and check the displayed icon in Explorer on Windows. Then sign project executables if configured, compile the installer with those bytes, sign the installer if configured, and hash that final installer for WinGet.
