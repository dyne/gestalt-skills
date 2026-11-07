# Mathematical exposition

## Statements and dependencies

Put the mathematical contract in a theorem-like environment. Keep motivation,
provenance, strategy, and interpretation around it. State the kind of each object
before using it; declare parameters and constant dependencies where a reader
needs them. A global convention does not replace a result's exceptional
assumptions. Preserve the author's meaningful notation rather than normalizing
it for cosmetic consistency.

For a substantial rewrite, record each original conclusion, its revised
location, and its downstream uses. Reordering conclusions by use must not lose
an intermediate estimate that another proof needs. A formalization is useful
evidence only at the actual mapped revision; its API names are not automatically
good theorem names or paper structure.

## Proofs

- Give a long proof a brief route map: reduction, construction, decisive
  estimate, conclusion. Do not require a roadmap for a two-line proof.
- Make each paragraph discharge one mathematical obligation. Begin with the
  action it performs; explain an obstruction before the device that resolves it.
- Introduce an object near its sustained use and explain its mathematical job.
  Keep its identity visible through coordinate changes, differentiation,
  normalization, or decomposition. Define an abbreviation when it reveals
  structure or saves repeated effort, not merely to shorten a formula.
- At a theorem application, give the precise source/result and establish the
  hypotheses, setting, and normalization. A superficially similar theorem is
  not an interchangeable proof step.
- Show a load-bearing argument instead of calling it “standard” or “clear.”
  Replacing proof by citation requires checking the cited statement and its
  transport to the present setting. Do not invent the source or locator.
- Explain the consequence after a decisive display. Track remaining errors,
  preserved properties, and the cost of a step rather than declaring progress
  without a bound. Stop once the asserted conclusion follows.

For a deferred proof, state the usable result, its role, and exact proof location
in matching notation. A summary cannot quietly omit a condition that later
users need. If the supplied argument has a genuine gap, mark the precise missing
implication and ask for a mathematical decision instead of hiding it in prose.

## Paper architecture

For a new manuscript, begin from the principal claim and a dependency outline.
Draft a representative statement/proof before scaling its exposition. Distinguish
checked statements, draft arguments, and open obligations in working notes.
Those notes do not belong in the finished paper as claims of certainty.

For a checked manuscript, first read the relevant proof and its consequences.
Reduce repetition, verify source substitutions, order dependencies for the
reader, and then rewrite. Settle the introduction and abstract once the main
statement surface is stable. Explain the mathematical mechanism before a dense
parameter list, while keeping every essential condition explicit somewhere the
reader can find it. Separate a new improvement from a property merely preserved.

## Acceptance check

Compare every revised statement and decisive proof step with its authority.
Can a reader identify the objects, the goal of each step, the estimate that
closes it, and the result being invoked without consulting the author's working
history? Record unresolved proof status separately from successful typesetting.
Do not describe an editorial review or a compiler run as independent proof
verification.
