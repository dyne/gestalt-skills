# PDF reconstruction

Clarify content recovery versus close visual approximation and identify the
requested pages. Preserve the input PDF and write new source/assets separately.
Use available text extraction and rendered-page inspection; scanned content
may need OCR. Do not install a converter just because source is unavailable.

A PDF does not reliably preserve its original class, engine, macros, bibliography
database, comments, or source boundaries. Treat those choices as inferred.
Sorted extraction can scramble columns, merge table cells, or lose subscripts;
compare the rendered pages before deciding the reading order or equation.

Recover the selected prose, mathematics, tables, captions, footnotes, and
references. Escape special characters in prose according to context, without
escaping actual TeX commands and math indiscriminately. Keep citation markers
unmatched when the evidence does not establish their bibliography mapping.
Do not replace an illegible symbol with a plausible mathematical guess.

Flag uncertain readings at their source locations and in a visible draft marker;
a TeX comment alone must not hide missing material from readers. Remove repeated
headers or join hyphenated lines only after verifying they are layout artifacts.
Retain meaningful hyphens and repeated scientific content.

Compile if the required tools/assets exist, then compare the reconstructed
pages with the original: content completeness, reading order, math signs and
indices, table cells, figures, and citation mappings. Matching page counts is
insufficient. Report selected-page coverage, extraction/OCR used, inferred
choices, compilation and visual status, and unresolved locations. Editable
reconstruction is not recovery of the exact original source.
