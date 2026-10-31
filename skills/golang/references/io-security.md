# I/O, protocol contracts and untrusted data

## HTTP and decoding

Reuse configured `http.Client` / `Transport` instances and connection pools;
choose deadlines and limits appropriate to short requests versus streaming.
Use request contexts and close successful responses' bodies. For connection
reuse, consume expected bounded bodies to EOF when appropriate; do not drain
an unlimited attacker-controlled body just to reuse a connection. A non-2xx
status is not automatically a `Client.Do` error. Check status and bound reads,
including error bodies, while preserving the protocol's status/error contract.

For servers, configure relevant header/body/idle limits and timeouts; a socket
write timeout is not a replacement for canceling application work. Use
`http.MaxBytesReader` to limit inbound bodies. JSON decoding must reject trailing
values when a single document is required; decide unknown-field handling from
compatibility needs. Preserve JSON nil/empty and numeric precision semantics.
Check scanner token limits, decode/write failures and errors after streaming
iteration. Once response bytes/status are committed, an error cannot simply
replace them with a fresh JSON error response.

## SQL and files

Use the driver's parameter placeholders and separate SQL values from syntax.
Identifiers such as sort columns require an allowlist/query builder, not value
placeholders. Set query contexts and pool bounds for the workload; do not fix
pool starvation merely by increasing limits while leaking rows/transactions.
Stream large transfers and bound accumulation instead of reading all rows or
request bytes into memory.

Treat filesystem paths and archive entry names as untrusted when they cross a
boundary. `Clean` plus a string prefix does not establish containment; lexical
checks alone do not prevent symlink races. Use Go 1.24+ `os.Root` operations when
applicable, or an established containment implementation for older targets.
Limit archive expansion, file counts and permissions. Understand special files
and platform restrictions; a rooted file API is not a complete process sandbox.
Use temporary files/atomic replacement only when the required filesystem and
durability semantics support that strategy.

## Secure the touched boundary

- Use separate executable arguments with `exec.CommandContext`; do not construct
  a shell program from user input. Arguments can still inject program-specific
  options, so validate/allowlist them and use `--` where the target supports it.
- Use `html/template` for context-aware HTML escaping; `text/template` does not
  provide that protection. Do not mark untrusted values as trusted HTML/JS.
  For outbound user-controlled URLs, account for redirects, address resolution
  and internal-network access in the existing SSRF policy.
- Use `crypto/rand` for secrets, vetted password hashing and authenticated
  encryption with correct nonce/key handling. Keep certificate verification on.
  Use `hmac.Equal` or appropriate constant-time comparison for secret comparison;
  do not invent cryptographic protocols or hardcode keys.
- Enforce authentication and resource/tenant authorization server-side. Preserve
  the application's CSRF, cookie (`Secure`, `HttpOnly`, `SameSite`) and trusted
  proxy policies. Do not trust forwarded/admin headers from arbitrary clients.
- Keep credentials, tokens and sensitive bodies out of errors, logs, metrics and
  profiles. For requested reviews, trace actual data flow and existing controls
  before reporting exploitability; do not assign severity from a snippet alone.

Sources: [net/http](https://pkg.go.dev/net/http),
[JSON](https://pkg.go.dev/encoding/json),
[SQL injection](https://go.dev/doc/database/sql-injection),
[rooted files](https://go.dev/blog/osroot),
[HTML templates](https://pkg.go.dev/html/template),
[security practices](https://go.dev/doc/security/best-practices).
