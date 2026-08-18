# API Tokens (Personal Access Tokens)

## Overview

BorgIQ API tokens provide programmatic access to the API. They work like GitHub Personal Access Tokens (PATs) — each token is tied to a user account, inherits the user's org/workspace memberships, and can be scoped to specific permissions.

## Token Model

- **User-associated**: a token automatically has access to any org/workspace its user belongs to. If the user loses a membership, the token stops working there — one token can serve pipelines that touch multiple workspaces.
- **Scopes are the ceiling**: the token can never exceed its configured scopes, even if the user gains broader permissions later. Grant the least privilege the integration needs — a token that only triggers flows doesn't need `DeleteCanvas`.
- **Shown once**: the raw token appears once at creation and cannot be recovered afterwards — only a hash is stored. Lost tokens must be re-created.
- **Revocation is immediate**: a revoked token is rejected on its next request.
- **Rate limits are per token**, so separate systems (CI/CD, monitoring, scripts) using their own tokens each get their own budget. Failed authentication attempts are additionally rate-limited per IP.
- Requests must authenticate with `Authorization: Bearer` — requests carrying neither a Bearer token nor a web-app session are rejected with 401.

---

## Authentication

### Making Authenticated Requests

Include your API token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer biq_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2" \
  https://api.borgiq.com/v1/orgs/my-org/workspaces/my-workspace/canvases
```

### Token Format

```
biq_<40 hex characters>
```

Example: `biq_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2`

- **Prefix**: `biq_` (always present, identifies it as a BorgIQ token)
- **Random part**: 40 hex characters (160 bits of entropy)
- **Total length**: 44 characters

### Authentication Flow

1. Client sends `Authorization: Bearer biq_...` header
2. Server hashes the token with SHA-256
3. Server looks up the hash in the database
4. Server verifies: not revoked, not expired, user not deleted
5. Server performs timing-safe comparison
6. Server checks per-token rate limit
7. Server sets `RateLimit-*` headers on the response
8. Request proceeds to the route handler

---

## Rate Limiting

### Per-Token Request Limits

Every API token response includes rate limit headers:

| Header | Description |
|--------|-------------|
| `RateLimit-Limit` | Maximum requests allowed per window |
| `RateLimit-Remaining` | Requests remaining in current window |
| `RateLimit-Reset` | Seconds until the window resets |

**Default limit**: 120 requests per minute per token (configurable via `API_TOKEN_RATE_LIMIT_PER_MINUTE` environment variable).

When the limit is exceeded, the API returns:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
RateLimit-Limit: 120
RateLimit-Remaining: 0
RateLimit-Reset: 45

{
  "status": 429,
  "message": "Too many requests. Please try again later.",
  "details": []
}
```

### Brute-Force Protection

Failed authentication attempts are rate-limited per IP address: **20 failures per 15 minutes**. After exceeding this, all Bearer token requests from that IP receive 429 until the window resets.

### Best Practices

- Check `RateLimit-Remaining` before making requests
- Respect `Retry-After` when you receive a 429
- Use exponential backoff for retries
- If you need higher limits, contact your administrator to adjust `API_TOKEN_RATE_LIMIT_PER_MINUTE`

---

## Token Management

### Creating a Token

**Via the UI**: Go to **User Settings > API Tokens > Create Token**. Select a name, scopes, and optional expiration. The raw token is shown **once** — copy it immediately.

**Via the API** (requires existing authentication):

```bash
POST /v1/apiTokens
Content-Type: application/json

{
  "name": "CI/CD Pipeline",
  "scopes": ["org:access", "workspace:access", "canvas:read", "flowrunJob:read"],
  "expiresAt": "2027-01-01T00:00:00.000Z"  // optional, max 365 days
}
```

**Response** (201 Created):

```json
{
  "id": "TOKN01j5a3b2c1d4e5f6g7h8i9j0",
  "name": "CI/CD Pipeline",
  "tokenPrefix": "biq_a1b2",
  "scopes": ["org:access", "workspace:access", "canvas:read", "flowrunJob:read"],
  "expiresAt": "2027-01-01T00:00:00.000Z",
  "lastUsedAt": null,
  "createdAt": "2026-03-20T12:00:00.000Z",
  "revokedAt": null,
  "rawToken": "biq_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
}
```

> **Important**: The `rawToken` field is only returned at creation time. Store it securely.

**Limits**:
- Maximum **50 active tokens** per user
- Token name: 1-255 characters
- At least 1 scope required
- Expiration (if set) must be in the future and within 365 days

### Listing Tokens

```bash
GET /v1/apiTokens?page=1&pageSize=25
```

**Response** (200 OK):

```json
{
  "total": 2,
  "data": [
    {
      "id": "TOKN01j5a3b2c1d4e5f6g7h8i9j0",
      "name": "CI/CD Pipeline",
      "tokenPrefix": "biq_a1b2",
      "scopes": ["org:access", "workspace:access", "canvas:read"],
      "expiresAt": "2027-01-01T00:00:00.000Z",
      "lastUsedAt": "2026-03-20T14:30:00.000Z",
      "createdAt": "2026-03-20T12:00:00.000Z",
      "revokedAt": null
    }
  ]
}
```

> The raw token value is **never** returned in listing responses. Only the `tokenPrefix` (first 8 characters) is shown for identification.

### Revoking a Token

```bash
DELETE /v1/apiTokens/TOKN01j5a3b2c1d4e5f6g7h8i9j0
```

**Response** (200 OK):

```json
{
  "message": "API token revoked successfully."
}
```

Revocation is immediate — the next request using that token will receive 401. Revoked tokens are soft-deleted (marked with `revokedAt` timestamp) and still appear in listings with a "Revoked" status.

---

## Scopes

Scopes control what a token can do. A token can only perform actions matching its configured scopes. Routes require specific scopes — if the token doesn't have them, the request is denied with 403.

### How Scopes Work

1. When you create a token, you select which scopes it should have.
2. On every request, the token's scopes are checked against the route's requirements.
3. The user's org/workspace **membership is also validated** — scopes alone aren't enough. The user must still be a member of the org/workspace being accessed.
4. Unlike web app sessions (which get all scopes for their role), **API token scopes are never expanded**. The token only ever has the scopes it was created with.

### Available Scopes

| Group | Scope | Description |
|-------|-------|-------------|
| **Organization** | `org:access` | Access organization endpoints |
| | `org:read` | Read organization details |
| | `org:write` | Update organization |
| | `org:delete` | Delete organization |
| **Workspace** | `workspace:access` | Access workspace endpoints |
| | `workspace:read` | Read workspace details |
| | `workspace:write` | Update workspace |
| | `workspace:delete` | Delete workspace |
| **Canvas** | `canvas:read` | Read canvases |
| | `canvas:write` | Create/update canvases |
| | `canvas:delete` | Delete canvases |
| **Flow Runs** | `flowrunJob:read` | Read flow run jobs |
| | `flowrunJob:reRun` | Re-run flow run jobs |
| | `flowrunJob:delete` | Delete flow run jobs |
| | `flowrunJobLog:read` | Read flow run logs |
| | `flowrunJobResult:read` | Read flow run results |
| | `flowrunMessage:read` | Read flow run messages |
| **Triggers** | `Trigger:manual:create` | Create manual triggers |
| **Secrets** | `secret:read` | Read secrets |
| | `secret:write` | Create/update secrets |
| | `secret:delete` | Delete secrets |
| **Connections** | `connection:read` | Read connections |
| | `connection:write` | Create/update connections |
| | `connection:delete` | Delete connections |
| **Assets** | `asset:read` | Read assets |
| | `asset:write` | Create/update assets |
| | `asset:delete` | Delete assets |
| **Templates** | `template:read` | Read templates |
| | `template:write` | Create/update templates |
| **Collections** | `collection:read` | Read collections |
| | `collection:write` | Create/update collections |
| | `collection:delete` | Delete collections |
| **Runtimes** | `runtime:read` | Read runtimes |
| | `runtime:write` | Create/update runtimes |
| | `runtime:delete` | Delete runtimes |
| **User** | `user.info:read` | Read authenticated user info |
| | `user.workspaces:read` | Read user's workspaces |
| **Actors** | `borgiqActor:read` | Read actor definitions |

### Common Scope Combinations

**Read-only monitoring** (view canvases and flow run results):
```json
["org:access", "workspace:access", "canvas:read", "flowrunJob:read", "flowrunJobResult:read", "flowrunMessage:read"]
```

**CI/CD pipeline** (trigger flows and read results):
```json
["org:access", "workspace:access", "canvas:read", "Trigger:manual:create", "flowrunJob:read", "flowrunJobResult:read"]
```

**Full workspace management**:
```json
["org:access", "workspace:access", "workspace:read", "workspace:write", "canvas:read", "canvas:write", "canvas:delete", "secret:read", "secret:write", "connection:read", "connection:write", "asset:read", "asset:write", "flowrunJob:read", "flowrunJob:reRun"]
```

---

## Error Responses

All error responses follow the format:

```json
{
  "status": <number>,
  "message": "<description>",
  "details": [{ "path": ["<field>"], "message": "<detail>" }]
}
```

| Status | Scenario |
|--------|----------|
| 201 | Token created successfully |
| 200 | Token listed or revoked successfully |
| 400 | Max tokens reached (50) / Invalid scopes / Invalid expiration |
| 401 | Missing or invalid token / Expired token / Revoked token |
| 403 | User lacks org/workspace membership / Missing required scopes |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Security

### Token Storage

- **Never log tokens** in application logs or error tracking.
- **Never commit tokens** to version control.
- **Use environment variables** or a secrets manager to store tokens in your applications.
- **Rotate tokens periodically** by creating a new token and revoking the old one.

### What Happens When...

| Event | Effect on Token |
|-------|----------------|
| User is deleted | Token immediately stops working (checked on every request) |
| User loses org membership | Token gets 403 on that org's endpoints |
| User loses workspace membership | Token gets 403 on that workspace's endpoints |
| Token is revoked | Token immediately returns 401 |
| Token expires | Token returns 401 after expiration time |
| Token scopes are insufficient | Token gets 403 on routes requiring missing scopes |

### Audit Trail

All token operations are logged:
- **Token created**: Records who created it, the token name, and timestamp
- **Token revoked**: Records who revoked it, the token name, and timestamp

Audit logs are accessible via the org audit log page.

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `API_TOKEN_RATE_LIMIT_PER_MINUTE` | `120` | Max API requests per minute per token |
