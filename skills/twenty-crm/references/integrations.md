# Workspace APIs

Discover the schema on the target workspace first. Custom objects and fields become API names immediately. Inspect **Settings → Developers → API** or use a saved CLI remote. These read-only examples take a small sample and work outside an app directory.

```sh
twenty metadata object list --remote dev
twenty metadata field list companies --remote dev
twenty api rest '/rest/companies?fields=id,name&limit=2' --remote dev
twenty api graphql --query '{ companies(first: 2) { edges { node { id name } } } }' --remote dev
```

| Surface | REST | GraphQL | Use for |
| --- | --- | --- | --- |
| Core | `/rest/` | `/graphql` | Records, filters and relations in the workspace |
| Metadata | `/rest/metadata/` | `/metadata` | Object and field definitions, schema and application metadata |

Use the API base shown for the workspace. For a service accessing one workspace, create a role-scoped API key under **Settings → Developers → API** and send it as a Bearer token. For an integration acting on behalf of different users, discover the workspace's OAuth endpoints at `/.well-known/oauth-authorization-server`, use the authorization code flow with PKCE S256, and verify callback state. Keep credentials and refresh tokens server-side.

Page through results using the cursor returned by the chosen API. Request only the fields needed, including a composite field as a whole (for example `name`). Use GraphQL to traverse relations or batch upsert. Respect the instance's batch and rate limits and back off on HTTP 429. If a custom field is missing, check the object API name, the key's role and the schema on that exact workspace.

## Notifications

Use an outbound webhook to send record changes to a service. A workflow webhook trigger accepts incoming events into Twenty. Choose one direction before configuring the endpoint.

For outbound delivery, register the receiving URL and event types under **Settings → Developers → Webhooks**. Configure a signing secret. Verify `X-Twenty-Webhook-Signature` against the hex HMAC-SHA256 of the timestamp header, a colon and the exact serialized JSON payload, keyed with that secret. Check `X-Twenty-Webhook-Timestamp` (epoch milliseconds) for freshness and use a length-checked constant-time comparison. Make downstream writes idempotent and acknowledge accepted work promptly with a 2xx. To verify delivery, perform one subscribed change on a test record and match its ID and event to the receiver's observation.
