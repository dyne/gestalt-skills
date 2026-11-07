---
name: humanizer
description: "Write or edit clear, idiomatic English or Italian prose: emails, documentation, reports, explanations, public copy, and manuscript language. Use for drafting, rewriting, translation polishing, grammar, tone, concision, or removing AI slop. Owns prose quality; excludes scholarly evidence design and TeX formatting."
---

# Humanizer

Write something a particular reader can understand and use. Naturalness comes
from a clear purpose, precise language, and an identifiable voice. Apply this
workflow to new drafts as well as supplied text; no detection pass is required.

## Write from meaning

1. Establish the reader, purpose, language, genre, and requested form from the
   request and context. Preserve the author's English variant, Italian register,
   and voice where evident. Ask only if missing information changes the meaning
   or makes the requested result unusable; otherwise use a reasonable default.
2. Identify what the reader needs to know, feel, decide, or do. For a new draft,
   work from the supplied facts; for an edit, silently map the existing meaning.
   Preserve names, numbers, attribution, negation, uncertainty, conditions,
   comparisons, causal direction, and intentional ambiguity. Keep quotations,
   technical terms, citations, code, markup, and requested structure intact.
   If ambiguity changes the claim, retain it or ask; do not guess it away.
3. Lead with the useful point. Arrange the rest in the order the reader needs:
   context before an unfamiliar concept, explanation beside its claim, and an
   action beside the information needed to take it. Give each paragraph a job.
   Use headings or lists when they help navigation or comparison.
4. Draft with concrete subjects and verbs. Name the actor when known and
   relevant; use passive voice when the actor is unknown or the object deserves
   emphasis. Keep the main clause easy to find. Carry a familiar idea into the
   next sentence, then add new information. Choose idiomatic phrasing over
   impressive synonyms. Retain necessary complexity and domain terminology.
5. Revise what obstructs the reader. Cut empty setup, generic praise, repeated
   conclusions, and abstractions that conceal the point. Explain an actual
   contrast or cause when a transition is needed. Let sentence length and
   paragraph shape follow the thought; preserve useful parallelism. Keep
   warmth, wit, or formality when the situation calls for it.
6. Compare the result with the facts or original. Reject edits that strengthen
   a claim, erase a caveat, fabricate specificity, or replace the author's voice
   with generic polish. Check grammar, idiom, pronoun references, punctuation,
   and formatting. Stop when the text works; further synonym churn adds cost
   and risks drift.

## Avoid manufactured voice

Do not add anecdotes, personal experience, enthusiasm, deliberate mistakes,
slang, or rhetorical flourishes merely to sound human. Replace phrases such as
“a transformative solution” with an evidenced description, or remove them if
none exists. Words such as “moreover,” necessary hedges, em dashes, and regular
sentence patterns are contextual choices, never forbidden tokens or quotas.
Do not infer authorship, assign AI scores, or optimize for detector evasion.

## Load only the needed detail

| Need | Reference |
| --- | --- |
| Reshape a draft, remove formulaic prose, preserve voice | [Prose craft](references/prose-craft.md) |
| English idiom or mechanics | [English](references/english.md) |
| Italian idiom, grammar, or register | [Italiano](references/italian.md) |
| Explicit Unicode cleanup or suspicious invisible characters | [Text hygiene](references/text-hygiene.md) |

An ordinary draft needs only this entrypoint. For mixed-language work, apply
the appropriate language guidance to each passage; translate only when asked.

## Deliver

For drafting or rewriting, return the requested text without an unsolicited
diagnostic preamble. For files, make the edit and give a brief change summary.
For critique-only requests, give specific findings and suggested repairs without
rewriting the whole text. Include comparisons or explanations when requested.
If essential facts are missing, identify the gap or use a clearly marked draft
placeholder; never manufacture details to make prose vivid.

Sources and adapted-material terms: [NOTICE](NOTICE.md).
