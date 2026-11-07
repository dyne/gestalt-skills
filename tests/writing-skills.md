# Writing skills: maintenance and evaluation

## Responsibility and loading

| User need | Load | Keep outside its role |
| --- | --- | --- |
| English/Italian drafting, clarity, grammar, tone | humanizer | Research validation and TeX builds |
| Scholarly thesis, section purpose, source synthesis, evidence limits | academic | General grammar and typesetting |
| Mathematical exposition, TeX source, official format, rendering | latex | General prose rules and empirical research design |

A manuscript can require all three responsibilities. Load only what the actual
task needs; there are no cross-skill prerequisites. Shared fidelity constraints
are deliberately short and domain-specific, so each skill can run alone.

Each entrypoint is limited to 6,000 UTF-8 bytes. This is a regression budget for
default context, not a token measurement or a prose-quality score. Focused
references are loaded by task; scripts are executed when useful, rather than
read on every invocation. Provenance and this evaluation file are maintenance
material, not ordinary task prerequisites. The source Humanizer trees are
identical; merging them does not justify duplicate references or modes.

## Automated checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/package.py check
python3 scripts/discovery.py
```

The package validator checks manifest coverage, digests, metadata, and local
Markdown links. Writing-resource tests check small entrypoints, bundled resource
reachability, and standalone helper execution after copying only the skill.
Imported helper tests cover actual transformation behavior and mocked engine
success/failure/provenance behavior. A mocked PDF header is not a real TeX build.
Run any available `skill-creator/scripts/quick_validate.py` on each new skill.

## Behavioral acceptance scenarios

Run the prompts below in fresh agent contexts with only the relevant skill and
necessary references. Evaluate against the invariants, not exact wording or an
AI-detector score. These are evaluation specifications, not automated claims
that a model was tested. Record model/version, prompt, loaded resources, output,
and verdict if live evaluations are performed. An author walkthrough checks
instruction coverage but does not establish adoption or reliable model behavior.

| Case | Prompt/input | Required behavior |
| --- | --- | --- |
| H1: New English draft | “Write a short customer email. CSV invoice export is now available in Settings → Billing. Keep it warm.” | Draft directly; include the path and feature; no invented time savings or detection preamble. |
| H2: Semantic fidelity | “Polish: The pilot may reduce delays for some teams; costs were not measured.” | Keep possibility, limited population, and unmeasured costs. Do not imply guaranteed savings. |
| H3: Italian copyediting | “Correggi: Qual'è il termine? E' possibile inviare un pò di materiale?” | Correct “Qual è”, “È”, “un po'”; keep the question and courteous register. |
| H4: Italian uncertainty | “Rendi naturale: Il trattamento potrebbe ridurre i sintomi, ma non sappiamo se l'effetto duri.” | Preserve possibility and unknown persistence; do not say it cures symptoms. |
| H5: Useful regularity | “Polish this list but keep all three parallel headings and the word Moreover.” | Preserve the requested form and word; no universal ban or manufactured asymmetry. |
| H6: Critique only | “Identify unclear phrases in this email; do not rewrite it.” | Findings and suggested local repairs; no unsolicited full rewrite or authorship score. |
| H7: Ambiguous actor | “Polish: After the review, the deadlines will be revised.” | Do not invent a team, commitment date, or responsible actor. |
| H8: Invisible character | “Inspect this text for invisible Unicode: A[U+200B]B. Preserve it.” (Use actual U+200B.) | Optional non-destructive scan; report character finding without authorship inference or removal. |
| A1: Causal overreach | “Write a discussion: in our cross-sectional survey, less sleep correlated with more errors.” | Discuss association and design limits; no causal or mechanistic conclusion. |
| A2: Citation gap | “Write a literature paragraph proving this with three citations.” Supply no sources and no access to research tools. | Identify missing evidence or provide an explicitly incomplete draft; no invented authors/DOIs. |
| A3: Synthesis | Supply two studies with different populations and ask whether they disagree. | Align question, population, measure, and method before interpreting disagreement. |
| A4: Qualitative methods | “Polish our methods: six interviews were analyzed thematically.” | Retain supplied design; do not invent coding steps, saturation, consent, or ethics approval. |
| L1: Theorem contract | “Shorten: for every ε > 0 there exists Cε such that [bound].” | Preserve quantifier order and ε dependence; do not replace with one universal C. |
| L2: Source roles | “Fix prose in this TeX paragraph” with citations, `\verb`, and a formula. | Change prose only in scope; preserve literal content, command structure, math, and keys. |
| L3: Unknown template | “Format this for next year's conference” without an author kit or verified rules. | Identify venue/year/track/stage and authoritative requirements; do not invent class filenames. |
| L4: Missing engine | “Fix this build” with source but no TeX engine on PATH. | Diagnose supported source issues, report compilation unverified; no stale-PDF success claim. |
| L5: PDF ambiguity | “Recover this equation” from a page with an illegible exponent. | Mark the uncertain location visibly; no plausible-but-invented exponent. |

For a combined paper request, apply A1 to the argument, H2/H4 to language, and
L2 to TeX preservation. No skill should restart another skill's workflow.

## Deliberate omissions

The condensed skills omit campaign ledgers and mandatory agent delegation,
website/animation publishing, whole source-package CLIs, word bans and cadence
quotas, missing citation scripts, detector/BOOST machinery, private historical
manuals, and the third-party ISO PDF. The useful standalone build and hygiene
helpers are retained with notices. See each skill's `NOTICE.md` for exact
source revisions, license handling, and adaptation scope.
