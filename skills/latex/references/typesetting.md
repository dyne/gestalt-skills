# Typesetting and venues

## Displays and notation

Use the existing mathematical packages and macros. With `amsmath`, prefer
`equation` for a single numbered expression, `align` for aligned relations,
`gather` for unaligned lines, and `split`/`aligned` inside an appropriate outer
display. Avoid `$$` and `eqnarray` in new source. Do not add or change packages
in an official template merely to enforce this preference.

Break at mathematical structure, such as a relation or sum; keep coupled
products, integrands, and delimiters intelligible. Align relation signs and
number only expressions referenced later when compatible with the manuscript.
Do not nest display environments. Use upright operator names through established
macros or `\operatorname`, and punctuation appropriate to the surrounding
sentence. Keep displays in the reading flow; a font-size reduction that makes
one fit is rarely the best first repair.

Use stable semantic labels and the existing reference commands. Place a float
label after its caption when the caption establishes the counter. Renaming a
label requires updating its uses; changing a citation command requires
preserving narrative versus parenthetical meaning.

## Figures and tables

Give each figure a mathematical or explanatory job. Specify the idea and what
is exact, schematic, or simulated before drawing. Reuse paper notation, label
axes and units, and check every numeric value and bound against the source.
A schematic path cannot suggest a stronger bound than the paper proves.
Prefer editable TikZ or the project's existing vector source for mathematical
diagrams; use available plotting tools for measured data. Never fabricate data
to fill a figure.

Check text and line weights at the actual column width, color independence,
caption completeness, clipping, and nearby page breaks. In a two-column layout,
use `\linewidth` within the actual container; a page-wide float has different
constraints from a single-column float. Avoid forcing every float to `[H]`.

Preserve table cells, precision, missing-value markers, and units. Use consistent
alignment and rules under the template's conventions. Fix the source of an
oversized table before shrinking it beyond readability. Inspect multirow and
multicolumn structures visually after a change.

## Venue conversion

Establish venue, year, track/article type, and submission stage. Use the supplied
official kit or retrieve the matching official instructions; record their source
and check date. Verify page/word limits and exclusions, anonymity requirements,
required sections, and bibliography rules. If rules are inaccessible, retain the
existing format or identify the assumptions of a provisional conversion.
Do not invent a template filename by changing its year.

Follow the kit's example: `.cls` goes in `\documentclass`, `.sty` in
`\usepackage`; not every venue style is a class. Respect the prescribed
bibliography setup and author/caption interfaces. Remove conflicting overrides
through source changes rather than patching official `.cls`, `.sty`, or `.bst`
files. Never meet a limit through hidden margin, font, or spacing tricks.

For anonymous review, check the rebuilt main and supplementary PDFs, author
blocks, acknowledgments, funding, self-citations, links, and metadata against
the actual rules. Retain attribution required by those rules. A keyword search
alone cannot establish anonymity. Do not remove authors for a camera-ready or
preprint stage by default.

Measure the main-content boundary separately from references and appendices
when the rules exclude them. Report required items as pass, fail, or unverified
with their evidence. A successful build does not establish venue compliance.
