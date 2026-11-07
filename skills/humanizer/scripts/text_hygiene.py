#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata

CANDIDATE_FORMATS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u2060": "WORD JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE/BOM",
    "\u00ad": "SOFT HYPHEN",
}
BIDI_RANGES = ((0x202A, 0x202E), (0x2066, 0x2069))
TAG_RANGE = (0xE0000, 0xE007F)
TAG_SPEC_RANGE = (0xE0020, 0xE007E)
TAG_CANCEL = "\U000e007f"
TAG_EMOJI_BASES = {"\U0001f3f4"}  # BLACK FLAG; base for subdivision flags
PRESERVE_CONTEXTUAL = {"\u200c", "\u200d"}  # ZWNJ / ZWJ
VARIATION_RANGES = ((0xFE00, 0xFE0F), (0xE0100, 0xE01EF))
TYPOGRAPHIC_SPACES = set("\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000")
CODE_LINE = re.compile(r"^\s*(?:```|~~~|(?:def|class|function|const|let|var|if|for|while)\b|[#/]{1,2})")
QUOTED_SPAN = re.compile(r'(["“‘])(?:[^"”’\\]|\\.)*(["”’])')

def in_ranges(cp, ranges):
    return any(lo <= cp <= hi for lo, hi in ranges)


def protected_indices(text):
    if any(unicodedata.bidirectional(ch) in {"R", "AL", "AN"} for ch in text):
        return set(range(len(text)))
    protected, offset, fenced = set(), 0, False
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        fence = content.lstrip().startswith(("```", "~~~"))
        if fence:
            fenced = not fenced
        if fenced or fence or "\t" in content or content.startswith("    ") or "|" in content or CODE_LINE.match(content):
            protected.update(range(offset, offset + len(content)))
        for match in QUOTED_SPAN.finditer(content):
            protected.update(range(offset + match.start(), offset + match.end()))
        offset += len(line)
    index = 0
    while index < len(text):
        if text[index] not in TAG_EMOJI_BASES:
            index += 1
            continue
        tag_start = index + 1
        tag_end = tag_start
        while tag_end < len(text) and TAG_SPEC_RANGE[0] <= ord(text[tag_end]) <= TAG_SPEC_RANGE[1]:
            tag_end += 1
        if tag_end > tag_start and tag_end < len(text) and text[tag_end] == TAG_CANCEL:
            protected.update(range(index, tag_end + 1))
            index = tag_end + 1
        else:
            index += 1
    return protected


def classify(ch):
    cp = ord(ch)
    if ch in CANDIDATE_FORMATS or TAG_RANGE[0] <= cp <= TAG_RANGE[1]:
        return "candidate-format"
    if in_ranges(cp, BIDI_RANGES):
        return "bidi-control"
    if ch in PRESERVE_CONTEXTUAL:
        return "contextual-shaping"
    if in_ranges(cp, VARIATION_RANGES):
        return "variation-selector"
    if unicodedata.combining(ch):
        return "combining-mark"
    if ch in TYPOGRAPHIC_SPACES or ch == "\t":
        return "typographic-spacing"
    return None


def make_finding(index, ch, kind, action):
    return {
        "index": index,
        "codepoint": f"U+{ord(ch):04X}",
        "name": unicodedata.name(ch, "UNNAMED"),
        "class": kind,
        "action": action,
    }


def sanitize(text: str, mode="scan", normalize=False):
    """Scan text and only remove plain-text candidate carriers on request."""
    if mode not in {"scan", "safe", "remove-safe"}:
        raise ValueError("mode must be scan, safe, or remove-safe")
    protected = protected_indices(text)
    findings, output, changed = [], [], False
    for index, ch in enumerate(text):
        kind = classify(ch)
        if kind is None:
            output.append(ch)
        elif mode == "remove-safe" and kind == "candidate-format" and index not in protected:
            findings.append(make_finding(index, ch, kind, "removed"))
            changed = True
        else:
            action = "uncertain" if kind == "candidate-format" and index not in protected else "preserved"
            findings.append(make_finding(index, ch, kind, action))
            output.append(ch)
    cleaned = "".join(output)
    if normalize and not protected:
        normalized = unicodedata.normalize("NFC", cleaned)
        if normalized != cleaned:
            cleaned, changed = normalized, True
            findings.append({
                "index": 0,
                "codepoint": "NFC",
                "name": "CANONICAL COMPOSITION",
                "class": "normalization",
                "action": "mapped",
            })
    return cleaned, {"mode": mode, "changed": changed, "count": len(findings), "findings": findings}

def main():
    ap = argparse.ArgumentParser(description="Conservative Unicode hygiene; scan is non-destructive.")
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument("--scan", action="store_const", const="scan", dest="mode", help="report only (default)")
    modes.add_argument("--safe", action="store_const", const="safe", dest="mode", help="explicit non-destructive mode")
    modes.add_argument("--remove-safe", action="store_const", const="remove-safe", dest="mode", help="remove candidate carriers from unprotected plain text")
    ap.set_defaults(mode="scan")
    ap.add_argument("--nfc", action="store_true", help="apply NFC only outside protected context")
    args = ap.parse_args()
    text = sys.stdin.read()
    cleaned, report = sanitize(text, args.mode, args.nfc)
    sys.stdout.write(cleaned)
    sys.stderr.write(json.dumps(report, ensure_ascii=False, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
