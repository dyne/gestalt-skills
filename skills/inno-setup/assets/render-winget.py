"""Render project-owned WinGet templates for a single final installer asset."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from product_metadata import load_product


def render(templates, version, installer, url, output, product=None):
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._+-]*", version) or version.endswith("."):
        raise ValueError("expected a release version usable as a Windows directory name")
    if urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
        raise ValueError("supply the public HTTPS URL of the versioned installer")
    installer_templates = list(templates.glob("*.installer.yaml.in"))
    if len(installer_templates) != 1:
        raise ValueError("expected one *.installer.yaml.in template")
    identifier = installer_templates[0].name.removesuffix(".installer.yaml.in")
    parts = identifier.split(".")
    if (not 2 <= len(parts) <= 8 or len(identifier) > 128 or
            any(not re.fullmatch(r'[^.\s\\/:*?"<>|\x00-\x1f]{1,32}', part) for part in parts)):
        raise ValueError("expected a WinGet package identifier with 2 to 8 path components")
    digest = hashlib.sha256()
    with installer.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    values = {"@VERSION@": version, "@URL@": url, "@SHA256@": digest.hexdigest().upper()}
    product_keys = ("publisher", "name", "homepage", "license", "description")
    if product is not None:
        metadata = load_product(product)
        values.update({f"@{key.upper()}@": metadata[key] for key in product_keys})
    tokens = re.compile(r"@[A-Z][A-Z0-9_]*@")
    files = {}
    for template in sorted(templates.glob("*.yaml.in")):
        if not template.name.startswith(identifier + "."):
            raise ValueError(f"unexpected package template {template.name}")
        content = template.read_text(encoding="utf-8-sig")
        required = ("@VERSION@", "@URL@", "@SHA256@") if template == installer_templates[0] else ["@VERSION@"]
        if any(token not in content for token in required):
            raise ValueError(f"{template} is missing a release token")
        unknown = set(tokens.findall(content)) - values.keys()
        if unknown:
            raise ValueError(f"unresolved tokens in {template}: {sorted(unknown)}; check --product")
        files[template.stem] = tokens.sub(lambda m: json.dumps(values[m[0]]), content)
    if f"{identifier}.yaml" not in files or not any(
        name.startswith(f"{identifier}.locale.") for name in files
    ):
        raise ValueError("expected version and default-locale templates")

    parent = output / identifier[0].lower() / Path(*parts)
    target = parent / version
    parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if set(files) == {item.name for item in target.iterdir()} and all(
            (target / name).read_text(encoding="utf-8") == content for name, content in files.items()
        ):
            return target
        raise ValueError(f"{target} already contains different manifests; use a fresh output directory")
    with tempfile.TemporaryDirectory(dir=parent) as scratch:
        staged = Path(scratch) / "manifests"
        staged.mkdir()
        for name, content in files.items():
            (staged / name).write_text(content, encoding="utf-8", newline="\n")
        staged.rename(target)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--installer", required=True, type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", default=Path("manifests"), type=Path)
    parser.add_argument("--product", type=Path, help="shared product.json for product tokens")
    args = parser.parse_args()
    try:
        print(render(args.templates, args.version, args.installer, args.url, args.output, args.product))
    except (OSError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
