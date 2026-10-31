# Measure before changing performance

Define the target metric and representative input/concurrency/load. Establish
whether latency comes from CPU, allocation/GC, lock contention, connection pools
or external I/O. A CPU profile cannot explain time spent blocked by itself;
correlate CPU/heap, goroutine/block/mutex profiles, traces and upstream timings.
Keep diagnostic endpoints/profiles within the application's access policy.

## Benchmark comparably

Use representative nonconstant data and ensure the result is consumed so the
compiler cannot delete the work. Use `b.Loop` for suitable Go 1.24+ benchmarks;
keep a correct `b.N` loop when supporting older targets or preserving an
established benchmark. Exclude setup where it is not part of the metric,
report allocations and use `RunParallel` only to model real concurrent access.
Record Go version, CPU, build flags, workload and concurrency. Benchmark one
variant at a time on comparable idle hardware; race instrumentation and active
profiling can perturb timings. Compare repeated before/after samples with an
available compatible `benchstat`, not one favorable run.

```sh
go test ./path/to/pkg -run '^$' -bench '^BenchmarkTarget$' -benchmem -count=6
go test ./path/to/pkg -run '^$' -bench '^BenchmarkTarget$' -cpuprofile cpu.out -memprofile mem.out
go tool pprof -top cpu.out
go test -gcflags='-m=2' ./path/to/pkg
```

Replace the illustrative package/benchmark names. Separate profiling runs from
comparison runs and retain the matching binary. Escape-analysis messages are
compiler diagnostics, not a measured allocation budget. CPU profiles, retained
heap (`inuse_space`) and allocation traffic (`alloc_space`) answer different
questions. Do not attribute all blocked goroutines to an external bottleneck;
locks or internal channel flow can also stall work.

## Optimize the observed cause

- Fix unsuitable algorithms, repeated queries and unnecessary round trips before
  micro-optimizing syntax. Stream large I/O and reuse bounded connection pools.
- Reduce copying/conversions and preallocate from credible size information.
  Use `strings.Builder`, `strconv` or compiled reusable regexes where the hot
  path benefits; conversions are not guaranteed to allocate in every context.
- Use `sync.Pool` only for disposable temporary objects with clear ownership.
  Entries may disappear at any time; it is not a bounded application cache.
  Reset retained references and cap oversized buffers rather than increasing
  memory retention. Never use an object after returning it to a pool.
- Application caches need bounds, key correctness (including tenant scope),
  invalidation/expiry, stampede control and error/cancellation semantics. Check
  whether stale results are allowed before introducing a cache.
- Change `GOGC`, `GOMEMLIMIT` or `GOMAXPROCS` only with workload evidence and
  knowledge of the target runtime/container behavior. `GOMEMLIMIT` is a soft
  runtime limit, not a cap on total process RSS. Prefer supported defaults before
  adding manual GC calls, forced scheduler settings, `unsafe` or assembly.

Rerun behavioral tests alongside benchmarks. Report both regressions and gains,
including memory/latency tradeoffs, and keep a non-obvious optimization's reason
near the code rather than embedding machine-specific timings as a universal rule.

Sources: [diagnostics](https://go.dev/doc/diagnostics),
[benchmark loop](https://go.dev/blog/testing-b-loop),
[GC guide](https://go.dev/doc/gc-guide),
[sync.Pool](https://pkg.go.dev/sync#Pool).
