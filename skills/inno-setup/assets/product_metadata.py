"""Generate application VERSIONINFO/ICON resources or an Inno Setup include."""

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit


def load_product(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("expected a JSON product object")
    for key in ("name", "publisher", "homepage", "description", "executable", "license", "licenseFile"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"missing product field {key}")
    for key, value in data.items():
        if value is not None and (not isinstance(value, str) or not value.isprintable()):
            raise ValueError(f"{key} must be single-line text or null")
    home = urlsplit(data["homepage"])
    if home.scheme not in {"http", "https"} or not home.hostname:
        raise ValueError("homepage must be a full web URL")
    return data


def exe_name(value):
    if not value.isprintable() or not re.fullmatch(r'[^\\/:*?"<>|]+\.exe', value, re.IGNORECASE):
        raise ValueError("supply the executable basename including .exe")
    return value


def fixed_version(release, override):
    numeric = override or re.split(r"[-+]", release, maxsplit=1)[0]
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,3}", numeric):
        raise ValueError("set WINDOWS_FILE_VERSION to up to four numeric components")
    parts = [int(part) for part in numeric.split(".")]
    if max(parts) > 65535:
        raise ValueError("each Windows file version component must fit in 16 bits")
    return [*parts, *([0] * (4 - len(parts)))]


def asset_path(config, value):
    path = (config.parent / value).resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"expected a file at {path}")
    return path.as_posix()


def render_rc(data, release, numbers, exe, description, icon):
    def literal(value):
        return 'L"' + value.replace("\\", "\\\\").replace('"', '""') + '"'

    fields = {
        "CompanyName": data["publisher"], "ProductName": data["name"],
        "FileDescription": description or data["description"],
        "FileVersion": release, "ProductVersion": release,
        "InternalName": exe[:-4], "OriginalFilename": exe,
        "Comments": data["homepage"] + " | " + data["license"],
    }
    if data.get("copyright"):
        fields["LegalCopyright"] = data["copyright"]
    values = "\n".join(f'      VALUE "{key}", {literal(value)}' for key, value in fields.items())
    version = ",".join(map(str, numbers))
    icon_line = f'1 ICON "{icon}"\n' if icon else ""
    return f'''#pragma code_page(65001)
{icon_line}1 VERSIONINFO
FILEVERSION {version}
PRODUCTVERSION {version}
FILEOS 0x40004
FILETYPE 1
BEGIN
  BLOCK "StringFileInfo"
  BEGIN
    BLOCK "040904B0"
    BEGIN
{values}
    END
  END
  BLOCK "VarFileInfo"
  BEGIN
    VALUE "Translation", 0x0409, 1200
  END
END
'''


def render_include(config, data, numbers, exe, icon):
    directory = data.get("binaryDirectory") or ""
    parts = directory.replace("\\", "/").split("/") if directory else []
    if any(part in ("", ".", "..") or re.search(r'[<>:"|?*{}]', part) for part in parts):
        raise ValueError("binaryDirectory must be a relative installation subdirectory")
    fields = {
        "ProductName": data["name"], "ProductPublisher": data["publisher"],
        "ProductHomepage": data["homepage"], "ProductExe": exe,
        "ProductFixedVersion": ".".join(map(str, numbers)),
        "ProductLicenseFile": asset_path(config, data["licenseFile"]),
        "ProductBinSuffix": "".join("\\" + part for part in parts),
    }
    if icon:
        fields["ProductIcon"] = icon
    if data.get("wizardImage"):
        fields["ProductWizardImage"] = asset_path(config, data["wizardImage"])
    if data.get("welcomeCredit"):
        fields["ProductWelcomeCredit"] = data["welcomeCredit"]
    if data.get("guiExecutable"):
        fields["ProductGuiExe"] = exe_name(data["guiExecutable"])
        choice = data.get("silentShortcut")
        if choice not in ("create", "omit"):
            raise ValueError("set silentShortcut to create or omit for the GUI launcher")
        if choice == "create":
            fields["CreateSilentShortcut"] = "yes"
    if data.get("copyright"):
        fields["ProductCopyright"] = data["copyright"]
    lines = ["#pragma parseroption -p+"]
    for name, value in fields.items():
        quoted = value.replace('"', '""')
        lines.append(f'#define public {name} "{quoted}"')
    return "\n".join(lines) + "\n"


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("format", choices=("rc", "inno"))
    cli.add_argument("--product", type=Path, required=True)
    cli.add_argument("--version", required=True)
    cli.add_argument("--file-version", default=os.environ.get("WINDOWS_FILE_VERSION"))
    cli.add_argument("--exe", help="installed basename for a companion binary")
    cli.add_argument("--description", help="file description for a companion binary")
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    try:
        data = load_product(args.product)
        if not args.version.isprintable() or (args.description and not args.description.isprintable()):
            raise ValueError("version and description must be single-line text")
        numbers = fixed_version(args.version, args.file_version)
        exe = exe_name(args.exe or data["executable"])
        icon = asset_path(args.product, data["iconFile"]) if data.get("iconFile") else None
        if icon and not icon.lower().endswith(".ico"):
            raise ValueError("convert the supplied artwork to a Windows .ico first")
        if args.format == "rc":
            content = render_rc(data, args.version, numbers, exe, args.description, icon)
        else:
            content = render_include(args.product, data, numbers, exe, icon)
        encoded = content.encode("utf-8-sig" if args.format == "inno" else "utf-8")
        if args.output.is_file() and args.output.read_bytes() == encoded:
            return
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = tempfile.NamedTemporaryFile(dir=args.output.parent, delete=False)
        try:
            with tmp:
                tmp.write(encoded)
            os.replace(tmp.name, args.output)
        finally:
            Path(tmp.name).unlink(missing_ok=True)
    except (OSError, ValueError) as error:
        cli.exit(1, f"{cli.prog}: {error}\n")


if __name__ == "__main__":
    main()
