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
