# Modern JS and TS in application code

## Modules and data flow

- Follow the package's actual runtime contract. In Node, inspect `package.json` `type` and `exports`, extensions, entry points and consumers. For emitted Node ESM use the appropriate Node-aware TS resolution and runtime extensions in relative imports. For a bundler, use its resolution rules. Keep browser entry points free of eager Node imports. Test an actual consumer of the packed output, including declarations when published.
- Put transformation logic in functions whose inputs and outputs can be tested without I/O. Pass a clock, fetch function or guest adapter when it makes a real boundary replaceable. Iterate directly for tight binary loops. Use iterables or streams to keep large inputs bounded. `??` preserves meaningful zero, false and empty-string values. Object spread and typed-array views can still share nested storage.
- Give initialization an explicit owner. For shared immutable resources, cache an in-flight compilation promise, including concurrent callers, and choose whether a failed build is retried. Hold request-specific state outside that cache. If a promise is cleared on failure, ensure it still corresponds to the failed attempt.
- Sequence dependent awaits. Run independent work concurrently within the downstream capacity. `Promise.all` reports the first rejection while siblings may continue. Propagate an `AbortSignal` through supported I/O, release timers/listeners in cleanup, and choose `allSettled` when each outcome matters. Use backpressure or a bounded worker pool for unbounded input. An async function executing a synchronous Wasm export still occupies its calling thread.

## Types that express a contract

Parse external JSON, messages and configuration as `unknown`; validate with a schema or a narrow type guard at ingress. Type assertions and generated declarations cannot establish a binary's runtime ABI. Keep the validated internal representation small. Use a discriminated union when callers must handle distinct outcomes. An exhaustive switch with a `never` default makes an added variant visible to consumers.

Use inference for local code. Use generics for a relationship between values. For example this mapping preserves the result type for each requested operation:

```ts
type Results = { count: number; encode: Uint8Array };
type Operations = { [K in keyof Results]: (input: Uint8Array) => Results[K] };

function run<K extends keyof Results>(
    ops: Operations, kind: K, input: Uint8Array
): Results[K] {
    const operation = ops[kind];
    return operation(input);
}
```

Use `satisfies` to check a static registry while retaining its inferred keys and literals. Prefer built-in utility types such as `Pick` and `Awaited<ReturnType<...>>` to parallel declarations. Conditional types and `infer` earn their place when public return types truly depend on input. For unions, conditional types distribute over a naked type parameter. Wrap both sides in a tuple when the test concerns the union as a whole.

Check the public surface with the project's strict compiler. Exercise a valid inferred return and a deliberately invalid call guarded by `@ts-expect-error`. Run runtime tests separately for malformed input, rejected I/O and cleanup. For JS projects, JSDoc plus targeted `checkJs` can cover a boundary without migrating every caller.

## A Node service that calls a library

Validate request shape and size at the transport edge, authorize the operation, and pass typed data into an ordinary service function. Give the route and CLI access to the same adapter. Map domain errors to stable public responses at one boundary. Preserve an underlying error as `cause` for diagnosis. Log the operation, duration and request ID without copying payloads into logs.

Keep the request deadline and concurrency limit near the resource they protect. A single mutable guest heap needs exclusive ownership across each allocate/copy/call/release sequence. For long computations, isolate work in a worker and define cancellation and replacement on timeout. A DB transaction belongs to one checked-out connection through commit/rollback and release. On shutdown, stop admitting work, bound the drain, then release workers and pools. Test a failure and a subsequent successful request to detect leaked state.

[TypeScript handbook](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html) · [Node package resolution](https://nodejs.org/api/packages.html) · [Node streams](https://nodejs.org/api/stream.html) · [Node worker threads](https://nodejs.org/api/worker_threads.html)
