# Components, templates and DOM integration

## Events and bindings

Use Svelte 5 event attributes such as `onclick` and typed callback props for
new runes components. Preserve forwarded callbacks when spreading props; decide
the spread/override order deliberately. Translate legacy event modifiers into
explicit handler behavior rather than appending modifiers to event attributes.
Use `<svelte:window>` / `<svelte:document>` for their declarative listeners;
do not recreate those listeners in lifecycle hooks without a specific need.

Prefer semantic buttons, links and labeled inputs with their keyboard and focus
behavior intact. Investigate compiler accessibility warnings rather than
suppressing them to make validation quiet. Preserve an explicit button type
when a component can live inside a form.

Use bindings for intentional two-way values. On Svelte 5.9+, function bindings
can provide a getter/setter for normalization or validation; a read-only binding
uses `null` for the getter. Expose component binding through `$bindable`, with a
consistent parent/child fallback contract. Keep an assignable item/property in
each blocks when binding to it; avoid destructuring that disconnects the write
from its owner.

## Snippets, lists and compatibility

- Declare `{#snippet name(...)}` in template scope and instantiate it with
  `{@render name(...)}`. Type public snippet props with `Snippet<[...]>`.
  Handle optional snippets with optional rendering or an explicit fallback.
  Respect lexical scope; exported snippets must not capture instance state,
  directly or through other snippets. Preserve the `children` snippet contract
  when wrapping components.
- Use stable, unique item identifiers as keys when list identity matters,
  especially for reordering, local component state and form controls. An index
  is not a stable identity for a changing list. Verify insertion/removal/reorder
  behavior; keys do not make every list inherently faster.
- In runes mode, prefer snippets to slots and render a changing component
  directly as `<Component />`. Use explicit self-imports for recursive
  components. Migrate legacy `export let`, `$:`, `on:`, slots and dynamic
  component APIs only within the agreed scope; some combinations across legacy
  and snippet interfaces require adapting callers.

## Apply design feedback to a Svelte screen

Consider a settings form where someone edits a value and saves it. Shape the screen around that task, then apply the requested change at the component that owns it.

| Design direction | Example in the settings form |
| --- | --- |
| **Critique** the visual hierarchy | Can someone find the field, tell what changed, and identify how to save? Follow the same path with the keyboard and check where focus lands after an error. |
| Make the form **quieter** or the primary action **bolder** | Use the project's color and spacing tokens in scoped CSS. Give Save the strongest emphasis and reduce competing accents on secondary actions. Keep focus rings and error messages visible. |
| **Distill** the form or **clarify** the action | Remove a heading that repeats the fieldset legend, or rename “Apply” to “Save preferences” if that is what the handler does. Keep each input's associated label. |
| **Adapt** the layout | Stack the label, field and actions at narrow widths using CSS grid or flex. Keep one mounted input and a logical DOM order. Type a draft, resize while the input is focused, then tab to Save and check the submitted value. |
| **Polish** or **harden** the save flow | For polish, align labels and controls across field groups. For hardening, exercise a slow or failed save, preserve the draft and make the error and retry action discoverable. |

## Styling and element lifetimes

Keep component CSS scoped. Pass dynamic values with style directives/custom
properties, and use custom properties as a child's public styling interface.
When a third-party component requires a global override, scope `:global(...)`
under a deliberate wrapper to avoid affecting unrelated instances. Use
supported class arrays/objects for new class composition; do not churn working
`class:` directives just to restyle a component.

For element-bound libraries on Svelte 5.29+, prefer `{@attach ...}` with a cleanup
function. Reactive values read during setup can destroy and recreate the
attachment; isolate cheap updates from expensive initialization where needed.
Retain supported actions on older versions or when a library contract requires
them. Do not duplicate library instances/listeners across rerenders, and avoid
browser-only imports during server module evaluation.

Sources: [events and markup](https://svelte.dev/docs/svelte/basic-markup),
[bindings](https://svelte.dev/docs/svelte/bind),
[snippets](https://svelte.dev/docs/svelte/snippet),
[each blocks](https://svelte.dev/docs/svelte/each),
[custom properties](https://svelte.dev/docs/svelte/custom-properties),
[attachments](https://svelte.dev/docs/svelte/@attach),
[migration](https://svelte.dev/docs/svelte/v5-migration-guide).
