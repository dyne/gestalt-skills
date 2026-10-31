# Toolchains, modules and verification

## Establish the build scope

Read the module's `go` / `toolchain` directives and any `go.work` replacements
before selecting commands. Record `go version` and relevant `go env` settings:
`GOWORK`, `GOOS`, `GOARCH`, `CGO_ENABLED`, `GOTOOLCHAIN`, `GOFLAGS`. Workspace
replacements can hide a broken standalone module. `./...` covers packages under
the chosen root, not every nested module/workspace automatically; test the
intended modules and supported build tags/platforms. Cross-compilation does not
prove the target executable runs, and cgo may require a target C toolchain.

Respect the project's toolchain policy. `GOTOOLCHAIN=auto` can download a newer
toolchain; `GOTOOLCHAIN=local` refuses switching when an offline/local-only check
is needed. Do not change persistent `go env -w` settings, global services or
dependency versions just to run a check. Verify new APIs against the oldest
supported toolchain, not only the developer's installed release.

| Minimum version | Relevant additions/semantics |
| --- | --- |
| Go 1.22 | New loop-variable semantics under the package language version |
| Go 1.23 | Range-over-function iterators |
| Go 1.24 | `b.Loop`, `os.Root`, module `tool` directives |
| Go 1.25 | Stable `testing/synctest` (`Test`/`Wait`), `WaitGroup.Go` |
| Go 1.26 | `errors.AsType`, testing `ArtifactDir` |

These are gates, not a request to raise the module baseline. Experimental APIs
and `GODEBUG`-dependent behavior require the exact release's documentation.

## Run meaningful checks

```sh
gofmt -w changed.go changed_test.go
go test ./path/to/pkg -run '^TestTarget$' -count=1
go test ./...
go vet ./...
go test -race ./path/to/pkg
go test ./path/to/pkg -run '^$' -fuzz '^FuzzTarget$' -fuzztime=10s
```

Adapt paths, test names, time budgets and tags to the task. Run only existing
fuzz targets, and confirm intended tests actually execute. `go test` normally
reuses eligible passing test results; `-count=1` forces fresh test execution
without discarding the useful build cache. Do not clear caches as a routine
fix. The race detector needs a supported platform/toolchain and usually cgo;
it does not run on every cross target. Inspect findings as well as exit codes.

Use the repository's compatible `staticcheck`, `golangci-lint`, `govulncheck` or
other configured tools when they fit the change. Check how the project invokes
tools (including `go tool` on supported modules) before installing anything.
`go vet` is not a complete lint or vulnerability scan; a quiet vulnerability
scan covers known findings in the analyzed configuration, not general security.

## Keep dependency changes deliberate

Preserve module paths, major-version suffixes, sums, vendoring and private
proxy/auth policy. Scope an update to the requested modules/versions; avoid
routine `go get -u ./...`. Run `go mod tidy` when dependency graph changes justify
it and inspect `go.mod`/`go.sum` diffs. Module checksums verify downloaded content,
not whether a dependency is secure. Treat `go generate` as arbitrary configured
commands; run required trusted generators and inspect their outputs, rather than
assuming generation is a side-effect-free build step.

Sources: [modules](https://go.dev/ref/mod),
[toolchains](https://go.dev/doc/toolchain),
[go commands](https://pkg.go.dev/cmd/go),
[release notes](https://go.dev/doc/devel/release),
[govulncheck](https://go.dev/security/vuln).
