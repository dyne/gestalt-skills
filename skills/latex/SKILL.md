---
name: latex
description: "Write, format, refactor, or repair LaTeX papers and mathematical exposition. Use for .tex manuscripts, theorem/proof structure, notation, equations, figures/tables, bibliography wiring, venue templates, PDF reconstruction, build errors, and rendered-page checks. Excludes general prose style and empirical argument design."
---

# LaTeX papers

Produce readable manuscript source whose mathematical meaning and rendered
pages agree. Follow the author's and venue's requirements; no house preamble,
font, package, or companion skill is mandatory.

## Workflow

1. Identify the requested deliverable and scope. For a project, inspect the
   actual root document, included files, macros, bibliography, build configuration,
   and surrounding mathematics. A file called `main.tex` is only a candidate.
   Establish the engine, bibliography backend, and any generated inputs before
   changing them. For pasted text, work from the supplied context and state
   any verification that requires the project.
2. Establish the source of mathematical authority: supplied statements, proofs,
   notes, or a checked revision. Preserve hypotheses, quantifier order, domains,
   boundary conditions, normalizations, signs, exponents, exceptional sets,
   constant dependencies, and uniformity. Keep labels, citation keys, macros,
   comments, and uncertainty markers unless the task requires a justified change.
   If an ambiguity or gap changes a result, stop that part and identify it;
   continue independent work without writing around the gap.
3. Load only the applicable reference below. For whole-paper work, map the
   principal statements and dependencies, then finish one coherent statement
   and proof at a time. Keep mathematical status separate from editorial and
   build status. For a local repair, stay within its dependency context.
4. Edit source according to its role. Prose arguments can be revised in scope;
   command names, keys, paths, math, and verbatim material require separate
   treatment. Reuse established notation and environments. Avoid blanket regex
   replacements across TeX. Keep official class/style files intact and make a
   reviewable diff that preserves unrelated author changes.
5. Build using the configured command when available. For a conventional project
   without custom build steps, the optional bundled checker records fresh logs
   and output; see the build reference. Diagnose the first causal error in its
   source context, repair the smallest cause, and rebuild. Missing tools leave
   compilation unverified; a stale PDF is never fresh build evidence.
6. Read final logs for errors, unresolved references/citations, duplicate labels,
   rerun requests, and new layout warnings. Inspect affected PDF pages at
   readable size, including neighboring page breaks, floats, captions, and
   displays. Reread the changed mathematics linearly. Successful compilation
   establishes neither proof correctness nor submission compliance.

## Focused references

| Need | Read |
| --- | --- |
| Statements, proofs, definitions, mathematical notation | [Mathematical exposition](references/mathematics.md) |
| Equations, floats, tables, official venue formats | [Typesetting and venues](references/typesetting.md) |
| Engine/backend selection, build failure, fresh-output evidence | [Build and repair](references/build-and-repair.md) |
| Recover editable source from PDF pages | [PDF reconstruction](references/pdf-reconstruction.md) |

For a small TeX edit, this entrypoint is sufficient. Scripts are optional and
run from this skill's own directory or their absolute installed path.

## Deliver

Return the requested source or file changes. For project work, summarize the
changed files, actual build command and result, evidence/PDF locations, visual
check coverage, remaining warnings, and unresolved mathematical or author
decisions. Distinguish a proposed fix from an executed build and an inspected
PDF. Do not submit or publish a manuscript merely because it was formatted.

Source adaptations and license notices: [NOTICE](NOTICE.md).
