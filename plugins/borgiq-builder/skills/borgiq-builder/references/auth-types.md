# Authentication Types

The `auth: { type, values }` object an HttpRequestActor sends, and the connection auth types behind
`${{ connection.auth }}`. Read it when you write `auth` by hand instead of using a connection. Exact schemas:
[schemas/connection.md](typescript/schemas/connection.md) and [connection.md](typescript/connection.md).

## Rules

- Prefer `auth: ${{ connection.auth }}` with a workspace connection (`connection: { key, type }`); it renders the right
  `{ type, values }` and refreshes OAuth tokens. Typed connections: [http-request-actor.md](http-request-actor.md#typed-connections).
- Never hardcode a secret; write `${{ credentials.<name> }}`.
- An actor has one connection. A second auth source goes in `credentials` with `source: connection`.
- Check for auth failures (401, 403) in the `error` block ([error-handling.md](error-handling.md#the-error-block)).

## Types

| `type` | `values` | Notes |
|---|---|---|
| `bearer` | `token` | `Authorization: Bearer <token>` |
| `basic` | `userName`, `password` | Basic `Authorization` header |
| `apiKey` | `key`, `value`, `addToHeader` | Header when `addToHeader: true`, else a query parameter |
| `oauth2` | `token`, `prefix` (e.g. `Bearer`), `addToHeader` | What an OAuth2 connection renders |
| `oauth1` | `consumerKey`, `consumerSecret`; optional `token`, `tokenSecret`, `signatureMethod`, plus advanced signing fields in the schema | `signatureMethod`: `HMAC-SHA1` (default), `HMAC-SHA256`, `HMAC-SHA512`, `RSA-SHA1`, `RSA-SHA256`, `PLAINTEXT`; for RSA, `consumerSecret` holds the PEM private key |
| `awsKeyBased` | `accessKey`, `secretKey`; optional `sessionToken`, `signQuery` (sign the query instead of adding an `Authorization` header; default `false`), `awsRegion`, `serviceName` (both inferred from the host when omitted; region falls back to `us-east-1`) | AWS Signature V4 |
| `custom` | optional `headers`, `queryParams`, `body` | Each overrides the request's keys of the same name |
| `awsRoleBased` | — | Connection type only: BorgIQ assumes the customer's IAM role (role ARN plus a BorgIQ external ID), and `connection.auth` resolves to `awsKeyBased` with temporary credentials. Never write it as `options.auth.type` |
| `mcpOauth` | — | Connection type only (`type: mcp-server`): OAuth 2.1 to a remote MCP server. Resolves to `bearer` at request time |
| `none` | — | No authentication: omit `auth` |

**mcpOauth.** Supply only the MCP server URL: BorgIQ discovers the authorization server and registers itself (RFC 7591),
as servers such as Linear and Notion expect. The server must advertise a dynamic client registration endpoint; if it
doesn't, or the provider issued you a client ID and secret, use an `oauth2` connection. Tokens refresh automatically;
re-authorize only after changing the server URL or scope.

## Request signing (awsKeyBased, oauth1)

Signing works with Server-side credentials, the default exposure mode: when the auth values or the request carry BorgIQ
credential placeholders, the BorgIQ egress proxy resolves them and signs the request, for `https://` URLs only (a
placeholder-bearing `http://` request is refused, not sent). Literal credentials (Sent to runtime) are signed by the
runtime as the request is sent.

```yaml
options:
  auth:
    type: awsKeyBased
    values:
      accessKey: ${{ credentials.aws.accessKey }}
      secretKey: ${{ credentials.aws.secretKey }}
      awsRegion: us-east-1
      serviceName: execute-api
```
