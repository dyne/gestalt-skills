# Behavioral testing

Test observable contracts and important failure paths with the existing stack.
Standard `testing`, table-driven subtests, `httptest`, small fakes and executable
examples often suffice; preserve established assertion/mock libraries rather
than requiring a new framework, generator or leak detector for every change.
Choose black-box `_test` packages for public contracts and same-package tests
when internal access is justified. Organize `_test.go` files by the repository's
conventions; Go does not require one test file per source file.

## Isolate each case

Use meaningful `t.Run` names for distinct table cases. Bind assertions and
helpers to the subtest's own `t`, call `t.Helper()` in helpers, and fail in the
test goroutine after collecting worker results. `Fatal` / `FailNow` in a worker
does not stop the parent test. Independent tests may use `t.Parallel`, but
shared environment, working directory, ports and singleton fixtures must not
race. `t.Setenv` / `t.Chdir` cannot be used in parallel tests or parallel ancestors.
Check loop capture semantics for older package language versions.

Use `t.TempDir` / `t.Cleanup` to scope resources, and unique integration data with
explicit cleanup. Use the project's build tags, short-mode or separate-package
policy for external dependencies; do not silently add mandatory services to
`go test ./...`. Report unavailable integrations as untested rather than passing.
Use `httptest.NewRecorder` for handler contracts and a local test server when
transport behavior matters. Check response status, headers and decoded body;
avoid tests that only assert "not nil" or reproduce implementation arithmetic.

```go
func TestClassify(t *testing.T) {
	for _, tc := range []struct {
		name string
		err  error
		want bool
	}{
		{"wrapped", fmt.Errorf("lookup: %w", fs.ErrNotExist), true},
		{"other", errors.New("unavailable"), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if got := errors.Is(tc.err, fs.ErrNotExist); got != tc.want {
				t.Fatalf("errors.Is(%v, ErrNotExist) = %v; want %v", tc.err, got, tc.want)
			}
		})
	}
}
```

The fragment illustrates error-chain assertions; in application tests, pass
the actual operation's returned error to the assertion instead of testing the
standard library in isolation. Its imports are `errors`, `fmt`, `io/fs`, `testing`.

## Concurrent, fuzz and regression tests

Establish worker readiness with a handshake, trigger the event, then await
completion. Prefer fake clocks or supported `synctest.Test` (Go 1.25+) for
appropriate time-dependent concurrent code; do not replace synchronization with
`time.Sleep`. Exercise cancellation and check cleanup on failing paths as well
as success. Race and leak checks answer different questions. Blanket leak
ignores can conceal the defect; scope justified exceptions narrowly.

Seed fuzz targets with real edge cases, keep them deterministic and bound their
work. Pick properties that match the valid domain (for example bytes versus
Unicode), and preserve failing inputs as regression cases. An ordinary `go test`
runs seed cases, not an active fuzz campaign. Use a specific package and a
bounded `-fuzztime` for fuzzing. Coverage identifies unexecuted code, not the
strength of assertions. Retained artifacts may use `ArtifactDir` on Go 1.26+
with the runner's artifact settings; use portable temporary/output conventions
on earlier targets.

Sources: [testing](https://pkg.go.dev/testing),
[subtests](https://go.dev/blog/subtests),
[httptest](https://pkg.go.dev/net/http/httptest),
[fuzzing](https://go.dev/doc/security/fuzz),
[Go 1.25](https://go.dev/doc/go1.25), [Go 1.26](https://go.dev/doc/go1.26).
