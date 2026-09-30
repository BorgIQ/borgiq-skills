# API Tokens (Personal Access Tokens)

A BorgIQ API token (a Personal Access Token, PAT) gives a script, a pipeline or an MCP client programmatic access to
the BorgIQ API as its user. Read it to mint a token with `borgiq tokens` and to choose its scopes; this is the scope
reference.

## Rules

- Grant the least privilege the integration needs: a token that only triggers flows does not need `canvas:delete`.
- Give each system (CI/CD, monitoring, a script) its own token: rate limits are per token.
- Send it as `Authorization: Bearer biq_…` on every request, never in a URL query string. A request with neither a
  Bearer token nor a web-app session gets 401.
- Never log a token or commit it to version control; keep it in an environment variable or a secrets manager. Rotate
  it by creating a new token and revoking the old one.

## Token model

- **User-associated**: a token reaches any org and workspace its user belongs to, and the membership is checked on every
  request, so one token can serve pipelines across workspaces. A user who loses a membership gets 403 there; a deleted
  user's tokens stop working at once.
- **Scopes are the ceiling**: a token's scopes are never expanded, even if the user gains permissions later, and each
  request is further capped by what the user's current role grants: a viewer's token cannot use
  `Trigger:manual:create` or any write scope, whatever it was created with.
- **Shown once**: the raw token appears only at creation; only a hash is stored, so a lost token must be re-created.
- **Format**: `biq_` plus 40 hex characters (160 bits), 44 characters in all, e.g.
  `biq_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2`.
- **Expiry and revocation**: an expiration is optional and must lie in the future, within 365 days. An expired or
  revoked token gets 401 on its next request. A revoked token stays in listings, marked revoked.
- **Limits**: 50 active tokens per user; a name of 1–255 characters; at least one scope.
- Creating and revoking a token is recorded in the org audit log (who, the token name, when).

## Create, List, Revoke

```bash
borgiq tokens create --name "CI/CD Pipeline" \
  --scopes org:access,workspace:access,canvas:read,Trigger:manual:create \
  --expires-at 2027-01-01T00:00:00.000Z --json   # --expires-at is optional
borgiq tokens list --json
borgiq tokens revoke <token-id> --yes           # the id from tokens list
```

`--scopes` is a comma-separated list of the scope strings below; on a terminal, a missing `--name` or `--scopes` is
prompted for. The `create` output includes `rawToken` (never shown again) and the token's `id`; listings show only
`tokenPrefix`, the first 8 characters. Run `borgiq auth login` first.

In the web app: **User Settings > API Tokens > Create Token**. Over the API, with existing authentication:
`POST /v1/apiTokens` with `{ "name", "scopes", "expiresAt" }` (201, returns `rawToken`),
`GET /v1/apiTokens?page=1&pageSize=25`, and `DELETE /v1/apiTokens/<token-id>`.

## Scopes

Every route requires specific scopes; a token without them gets 403. The user must also still be a member of the org
and workspace in the URL.

`:read` reads, `:write` creates and updates, `:delete` deletes. The complete list:

| Resource | Scopes |
|---|---|
| Organization | `org:access` (reach the org's endpoints), `org:read`, `org:write`, `org:delete` |
| Workspace | `workspace:access` (reach the workspace's endpoints), `workspace:read`, `workspace:write`, `workspace:delete` |
| Canvases | `canvas:read`, `canvas:write`, `canvas:delete` |
| Flow runs | `flowrunJob:read`, `flowrunJob:reRun`, `flowrunJob:delete`, `flowrunJobLog:read` (logs), `flowrunJobResult:read` (results), `flowrunMessage:read` (messages) |
| Triggers | `Trigger:manual:create` (run flows; call McpServerActor endpoints), `Trigger:lifecycle:create` (fire a lifecycle event such as `on-delete` by hand on a development workspace) |
| Apps | `app:use` (open and run published app and interface triggers; list the workspace's apps) |
| Secrets | `secret:read`, `secret:write`, `secret:delete` |
| Connections | `connection:read`, `connection:write`, `connection:delete` |
| Assets | `asset:read`, `asset:write`, `asset:delete` |
| Templates | `template:read`, `template:write` |
| Collections | `collection:read`, `collection:write`, `collection:delete` |
| Streams | `stream:read` (list, read, tail), `stream:write` (create, update, append records), `stream:delete` |
| Runtimes | `runtime:read`, `runtime:write`, `runtime:delete` |
| User | `user.info:read` (the authenticated user), `user.workspaces:read` (the user's workspaces) |
| Actors | `borgiqActor:read` (actor definitions) |
| Billing | `billing:read`, `billing:write` |
| Members | `member:read` (org and workspace members), `member:write` (change roles, remove members), `invitation:read`, `invitation:write` (send and manage invitations) |
| Audit | `auditLog:read` |

**Common sets:**

| Use | Scopes |
|---|---|
| Read-only monitoring | `org:access`, `workspace:access`, `canvas:read`, `flowrunJob:read`, `flowrunJobResult:read`, `flowrunMessage:read` |
| CI/CD: trigger flows, read results | `org:access`, `workspace:access`, `canvas:read`, `Trigger:manual:create`, `flowrunJob:read`, `flowrunJobResult:read` |
| MCP client calling an [McpServerActor](mcp-server-actor.md) endpoint | `org:access`, `workspace:access`, `canvas:read`, `Trigger:manual:create` |
| Full workspace management | `org:access`, `workspace:access`, `workspace:read`, `workspace:write`, `canvas:read`, `canvas:write`, `canvas:delete`, `secret:read`, `secret:write`, `connection:read`, `connection:write`, `asset:read`, `asset:write`, `flowrunJob:read`, `flowrunJob:reRun` |

## Rate Limits and Errors

- **120 requests per minute per token** by default (the deployment's `API_TOKEN_RATE_LIMIT_PER_MINUTE`; ask the
  administrator for more). Every response carries `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`
  (seconds until the window resets); watch `RateLimit-Remaining`. Over the limit: `429` with `Retry-After`. Respect it
  and back off exponentially.
- **Failed authentication** is limited per IP address: after 20 failures in 15 minutes, every Bearer request from that IP
  gets 429 until the window resets.
- Errors use the body `{ "status", "message", "details": [{ "path", "message" }] }`:

| Status | When |
|--------|------|
| 400 | 50 tokens reached, invalid scopes, invalid expiration |
| 401 | Missing, invalid, expired or revoked token |
| 403 | The user lacks the org/workspace membership, or the token lacks a required scope |
| 429 | Rate limit exceeded |
