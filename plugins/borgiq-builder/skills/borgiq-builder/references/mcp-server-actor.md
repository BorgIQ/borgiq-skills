# MCP Server Actor

**MCP spec versions served:** [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28) (current), [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25), 2025-06-18, 2025-03-26

The **MCP Server Actor** (`McpServerActor`) exposes its child tool actors as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
server endpoint. External AI agents (Claude Desktop, Cursor, custom agents, any MCP-compatible client) connect to the
endpoint, discover the tools and call them. It uses the same tool-actor pattern as the AI agents
([agent-tools.md](agent-tools.md)); the difference is that an **external MCP client** drives the tool calls instead of
an internal LLM loop. Read it to expose actors to a client, and for the protocol details a client implementer needs.

## Contents

- [1. Configuring the actor on a canvas](#1-configuring-the-actor-on-a-canvas)
- [2. Endpoint and authentication](#2-endpoint-and-authentication)
- [3. Transport and protocol eras](#3-transport-and-protocol-eras)
- [4. Tools](#4-tools)
- [5. Asking the caller for input (`input_required`)](#5-asking-the-caller-for-input-input_required)
- [6. Limits, errors, and edge cases](#6-limits-errors-and-edge-cases)

## 1. Configuring the actor on a canvas

It is a `trigger`-category actor with one **Status** port (`SPRTdefault`) where all its messages emit. It receives no
messages (`canReceiveMessage: false`): external MCP clients drive it, and it emits the real-time status of their
requests and tool calls.

**Tools.** List the tool actors in `configuration.aiAgentToolActorIds` and mark their client-supplied inputs with
`${{aiInput}}`, as in [agent-tools.md](agent-tools.md). A tool's MCP `name` is its `msgVar`, its `title` its display
name, its `description` its description: write the description for the *calling LLM*, since it is what external agents
see. Duplicate `msgVar`s fail canvas validation, and the endpoint refuses to serve `tools/list` with duplicates. To use
this server's tools from an AI agent inside BorgIQ, give the agent a `type: borgiq` MCP server entry.

**Options:**

```yaml
configuration:
  aiAgentToolActorIds: []
  options:
    responseTimeoutSeconds: 60   # 1–300; max time to wait for a tool call
    serverName: ''               # optional, ≤128 chars; defaults to the canvas name
    serverVersion: '1.0.0'       # ≤32 chars; reported to MCP clients
```

**Status port.** Every MCP request is recorded as a flowrun. The actor emits:

| Message type | When |
|---|---|
| `mcp-initialize` | A legacy-era `initialize` or a modern `server/discover` request is processed |
| `mcp-tool-list` | A `tools/list` request is processed |
| `mcp-tool-call` | A tool invocation is dispatched to the tool actor |
| `mcp-tool-result` | The tool result comes back (`isError: true` when the tool failed) |
| Errors | On any error |

`initialize` and `tools/list` are answered immediately and recorded fire-and-forget; `tools/call` is synchronous — the
HTTP response waits for the tool's result or error, up to `responseTimeoutSeconds` (see
[6.1](#61-tool-execution-timeout)).

## 2. Endpoint and authentication

### 2.1 URL pattern

```
POST /orgs/:orgSlugOrId/workspaces/:workspaceSlugOrId/mcp/:canvasId/:actorId
```

The full URL, with a copy button and a ready-to-paste client config, is in the actor's settings panel:

```json
{
  "mcpServers": {
    "<server-name>": {
      "url": "https://api.borgiq.com/orgs/my-org/workspaces/my-workspace/mcp/CNVS.../ACTR...",
      "headers": {
        "Authorization": "Bearer biq_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

### 2.2 Personal Access Tokens (PAT)

The simplest way to authenticate is a BorgIQ [API token](api-tokens.md), sent on **every** request, even within one
logical session, as `Authorization: Bearer <token>` (per OAuth 2.1, never in a URI query string), alongside
`Content-Type: application/json`, `Accept: application/json, text/event-stream` and `MCP-Protocol-Version`.

- The token must have the scopes **`org:access`**, **`workspace:access`**, **`canvas:read`** and
  **`Trigger:manual:create`**, and belong to a member of the org and workspace in the URL whose role grants them
  (member or admin; a viewer's role has no `Trigger:manual:create`). Create one with
  `borgiq tokens create --name <name> --scopes org:access,workspace:access,canvas:read,Trigger:manual:create --json`.

**Auth failures use HTTP status codes** (not JSON-RPC errors), with the API's `{ "status", "message", "details" }` error body:

| Status | When |
|---|---|
| `401` | No `Authorization` header — the response carries `WWW-Authenticate: Bearer resource_metadata="<protected-resource metadata URL>", scope="mcp:tools"` for OAuth discovery ([2.3](#23-oauth-21)) — or an invalid, expired or revoked token |
| `403` | The PAT lacks a required scope, or its user is not a member of the org or workspace (`You do not have the necessary privilege to access this resource!`) |
| `403` | An OAuth access token without the `mcp:tools` scope, with `WWW-Authenticate: Bearer resource_metadata="…", scope="mcp:tools", error="insufficient_scope"` |

### 2.3 OAuth 2.1

The endpoint also supports the [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
(OAuth 2.1): the `401` for a request with no credentials points (`resource_metadata`) at the Protected Resource Metadata
endpoint (RFC 9728), from which a client discovers the authorization server and runs the authorization-code + PKCE
flow. Use OAuth for clients that support it, and a PAT for header-based client configs.

### 2.4 Origin policy

A *present and invalid* `Origin` header is rejected with HTTP 403 (DNS-rebinding protection). An absent `Origin` is
allowed — only browsers attach one; non-browser MCP clients omit it.

## 3. Transport and protocol eras

The server uses **Streamable HTTP** on a single endpoint and serves both protocol eras from that one URL, with the same
credentials, so a client connects with whatever revision it speaks.

| | Modern (`2026-07-28`) | Legacy (`2025-11-25`, `2025-06-18`, `2025-03-26`) |
|---|---|---|
| Shape | Stateless: no handshake; every request carries its protocol version, client identity and capabilities in `_meta` | `initialize` handshake, negotiated once |
| Selected by | A `_meta` protocol version of `2026-07-28` or later; `server/discover` is always modern | No `_meta` protocol version |
| `Mcp-Method`, `Mcp-Name` headers | **Required**, validated against the body (`Mcp-Name` after decoding the `=?base64?…?=` sentinel); a mismatch returns `400` with `-32020` | — |
| `server/discover` | `200`: supported versions, capabilities, identity, cache hints | `-32601` |
| `initialize` | `-32601` (the handshake was removed) | `200`, echoing the client's requested revision when it is one we serve, else the newest legacy one |
| `ping` | `-32601` (removed) | `200` with `{}` |
| `tools/list` | `200`, tagged `resultType: "complete"` + `ttlMs` + `cacheScope: "private"` | `200`, `{ tools }` |
| `tools/call` | `200`, tagged `resultType`; may instead return `input_required` ([5](#5-asking-the-caller-for-input-input_required)) | `200`, untagged |
| Any notification | `202 Accepted`, no body | `202 Accepted`, no body |
| Unknown method | **`404`** + `-32601` | `200` + `-32601` |

- **`POST`** is the only method: a JSON-RPC *request* returns `application/json`, a *notification* `202 Accepted` with
  no body. **`GET`** and **`DELETE`** are always `405` (`2026-07-28` removed the standalone SSE stream and
  protocol-level sessions).
- `MCP-Protocol-Version` is validated against the supported set: an unsupported value returns `400` with `-32022` and a
  `supported` list, so the client can retry on a revision both sides speak. Absent means `2025-03-26`.
- `Accept: application/json, text/event-stream` is required of clients by the spec; a missing value is logged, not
  rejected. `Mcp-Session-Id` is never minted or read.
- Tools are returned sorted by name, so client and LLM prompt caches hit.
- On the modern era a client may call `tools/list` or `tools/call` directly; `server/discover` is optional. On the
  legacy era, `initialize` returns `serverInfo` (`name` = `BorgIQ - <canvas name>`, `title` = the actor's name,
  `version`), `capabilities: { tools: { listChanged: false } }` and the actor's `description` as `instructions`; the
  client then sends `notifications/initialized`.

## 4. Tools

### 4.1 `tools/list`

Each tool is listed with these fields:

| Field | Source | Required |
|---|---|---|
| `name` | Tool actor's `msgVar` | Yes |
| `title` | Tool actor's `name` (display name) | Optional |
| `description` | Tool actor's `description` | Optional (recommended) |
| `inputSchema` | Filtered `${{aiInput}}` properties from the actor input schema | Yes |
| `outputSchema` | Tool actor's output schema (`schemas.outputs`), if defined | Optional |
| `annotations` | Behavior hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), derived from actor type with safe defaults | Optional |

The `inputSchema` is JSON Schema 2020-12: the BIQ `ui` fields and the `${{aiInput}}` sentinel defaults are stripped,
property `title`s are kept, `const` fields are excluded, nested arrays and objects are kept, and a tool with no
`${{aiInput}}` parameters gets `{ "type": "object", "additionalProperties": false }`.

### 4.2 `tools/call`

The client sends `params: { name, arguments }`. The result maps the tool's output:

| Tool result type | `content` | `structuredContent` |
|---|---|---|
| `string` | `{ type: "text", text: <value> }` | — |
| `object` or `array` | JSON-stringified text | The value itself |
| Error | `{ type: "text", text: <error message> }` with `isError: true` | — |

`isError` is omitted on a successful result. Tool execution errors come back as tool results with `isError: true`,
actionable feedback the calling LLM can use to self-correct (e.g. `"Error: Connection to database timed out"`).
Protocol-level errors use JSON-RPC `error` objects instead: an unknown tool or bad arguments is `-32602`
(`Unknown tool: <name>`), a malformed request `-32600`.

Tool results use `text` content. A tool actor that fails answers at once, whatever its `continueOnError`: the client gets a tool result with `isError: true` whose text is the tool's error message (never its stack; an empty message becomes `The tool failed without an error message`). With `continueOnError: false` the tool's own job still ends in error state. The MCP Server Actor emits the result on its Status port with `isError` set.

## 5. Asking the caller for input (`input_required`)

`2026-07-28` removed server-initiated requests. A tool that needs input from the calling client (elicitation,
sampling, roots) asks for it **in the result**: the server answers `tools/call` with `resultType: "input_required"`,
and the client retries the original call with its answers and an opaque `requestState`. A tool actor opts in by
completing with a **reserved output shape**:

```js
// Deno / Python / AI tool actor
return { __mcpInputRequired: { github_login: {
  method: 'elicitation/create',
  params: {
    mode: 'form',
    message: 'GitHub username?',
    requestedSchema: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] },
  },
} } };
```

On retry the actor is re-invoked with the answers merged into its arguments under `mcpInputResponses`:

```js
{ ...originalArguments, mcpInputResponses: { github_login: { action: 'accept', content: { name: 'octocat' } } } }
```

- Supported request kinds are `elicitation/create`, `sampling/createMessage` and `roots/list`; anything else in the
  envelope is ignored.
- Only requests the client **declared it can answer** are sent. If it declared none of them, the call comes back as an
  error explaining that.
- `requestState` is single-use, expires after 5 minutes, and is bound to the caller, the tool and the exact arguments; a
  retry that changes any of those starts over.
- **Legacy clients cannot answer an input request.** A tool that returns the envelope to one gets an error result
  naming the problem; the envelope is never passed through as if it were the tool's real answer.

## 6. Limits, errors, and edge cases

### 6.1 Tool execution timeout

A call has one deadline, `responseTimeoutSeconds` after the API receives it. If the tool has not answered by then, the client receives a tool result with `isError: true` and the text `MCP tool call timed out after 60 seconds` (with the configured number), and the MCP Server Actor's job ends with a timeout error. The tool's own run is not cancelled; a result it produces after the deadline is discarded.

### 6.2 Canvas not active

If the canvas or the McpServerActor does not exist, or the actor is disabled (`isActive: false`), the endpoint answers
HTTP `404` with a `-32001` error whose message is `Canvas not found`, `MCP Server actor not found`, or
`MCP server is not active. Ensure the actor is enabled.`

### 6.3 Other behaviour

- Adding or removing tool actors is not pushed to connected clients; they must re-call `tools/list`.
- Clients may call several tools concurrently; each `tools/call` creates an independent run with no cross-call state.
- Request bodies are limited to 1 MB; tool names are 1–128 characters of letters, digits and `_-. `; tool results over
  10 MB are truncated with an error message.

### 6.4 Rate limiting

Three levels apply: **per token** (the API-token limit, default 120 requests/min), **per MCP server** (each McpServerActor
has its own sliding window, default 60 requests/min, covering all request types), and **per tool execution** (the
platform's standard actor invocation limits apply to `tools/call`). All responses carry `RateLimit-Limit`,
`RateLimit-Remaining` and `RateLimit-Reset` headers. Over a limit, the answer is `429 Too Many Requests` with
`Retry-After: <seconds>` and the JSON-RPC error `-32000`, `Rate limit exceeded. Retry after 45 seconds.`, with
`data.retryAfterSeconds`.

### 6.5 JSON-RPC error codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error (malformed JSON) |
| `-32600` | Invalid request (missing required fields) |
| `-32601` | Method not found (unsupported MCP method) |
| `-32602` | Invalid params (bad tool name or arguments) |
| `-32603` | Internal error |
| `-32000` | Server error (rate limit) |
| `-32001` | MCP server not active |
| `-32020` | Modern-era header/body mismatch (`Mcp-Method` / `Mcp-Name`) |
| `-32022` | Unsupported `MCP-Protocol-Version` (response lists supported revisions) |
