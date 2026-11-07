# Optional Unicode hygiene

Use the bundled standard-library helper only for an explicit cleanup request or
to inspect suspicious invisible characters. From this skill's directory:

```sh
python3 scripts/text_hygiene.py --scan < input.txt > unchanged.txt 2> report.json
python3 scripts/text_hygiene.py --remove-safe < input.txt > cleaned.txt 2> report.json
```

Never redirect output over the input file: the shell would truncate it first.
The default `--scan` and explicit `--safe` preserve input; JSON goes to stderr
and text to stdout. `--remove-safe` removes candidate format characters only
outside contexts the helper protects. `--nfc` separately requests canonical
composition where no protected context exists. It is not a spelling correction.

Candidates include U+200B, U+2060, U+FEFF, U+00AD, and Unicode tag characters.
The helper preserves bidi controls, ZWJ/ZWNJ, variation selectors, combining
marks, typographic spaces, and well-formed subdivision flag sequences. Its
heuristics protect quoted spans, code-like/fenced/indented lines, tabular lines,
and whole texts containing RTL characters. These heuristics are incomplete:
inline code, URLs, and unfamiliar quotation styles may need manual protection.
Soft hyphens and word joiners can also be intentional typography.

Inspect the report before choosing removal. Findings contain zero-based
`index`, `codepoint`, `name`, `class`, and `action`; actions are `removed`,
`mapped`, `preserved`, or `uncertain`. `--scan --nfc` can change text despite
the scan flag; omit `--nfc` for a strictly unchanged scan. Compare the output
and preserve any character that carries meaning or layout. The report concerns
characters, not authorship or statistical watermarks.
