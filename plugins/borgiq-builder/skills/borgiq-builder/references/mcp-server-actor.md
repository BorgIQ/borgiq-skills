# MCP Server Actor

**MCP spec versions served:** [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28) (current), [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25), 2025-06-18, 2025-03-26

The **MCP Server Actor** (`McpServerActor`) exposes its child tool actors as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server endpoint. External AI agents (Claude Desktop, Cursor, custom agents, any MCP-compatible client) connect to the endpoint, discover the available tools, and invoke them using the MCP standard.

**Key principle:** the MCP Server Actor reuses the **exact same tool-actor pattern** as the AI Agent actor — `aiAgentToolActorIds`, `${{aiInput}}` schema filtering, tool actors as child nodes. The difference: instead of an internal LLM loop driving tool calls, an **external MCP client** drives them.

---

## 1. Configuring the actor on a canvas

| Property | Value |
|---|---|
| Type | `McpServerActor` |
| Category | `task` |
| Source ports | Single **Status** port (`SPRTdefault`) — all messages emit here |
| Receives messages | No (`canReceiveMessage: false`) — it is driven by external MCP clients, not upstream actors |
| Emits messages | Yes — real-time status of MCP requests and tool calls |

### 1.1 Tools

Tool actors are attached exactly like AI Agent tools:

- `configuration.aiAgentToolActorIds` lists the child tool actor IDs (max 10).
- Each tool actor's inputs marked with the `${{aiInput}}` default become that tool's MCP `inputSchema`. Secrets, connection data, and non-`${{aiInput}}` properties are **never** exposed to MCP clients.
- The tool's MCP `name` comes from the actor's `msgVar`, `title` from its display name, and `description` from its description field. Write tool descriptions for the *calling LLM* — they are what external agents see.
- Duplicate tool names (`msgVar`) fail canvas validation, and the endpoint refuses to serve `tools/list` with duplicates.
- An MCP Server Actor cannot itself be a tool of an AI Agent actor (and vice versa).

### 1.2 Options

```yaml
configuration:
  aiAgentToolActorIds: []
  options:
    responseTimeoutSeconds: 60   # 1–300; max time to wait for a tool call
    serverName: ''               # optional, ≤128 chars; defaults to the canvas name
    serverVersion: '1.0.0'       # ≤32 chars; reported to MCP clients
```

### 1.3 Status port messages

Every MCP request is recorded as a flowrun for full observability. The actor emits on its **Status** port:

| Message type | When |
|---|---|
| `mcp-initialize` | A legacy-era `initialize` request is processed |
| `mcp-tool-list` | A `tools/list` request is processed |
| `mcp-tool-call` | A tool invocation is dispatched to the tool actor |
| `mcp-tool-result` | The tool result comes back |
| Errors | On any error |

`initialize` and `tools/list` are answered immediately and recorded fire-and-forget; `tools/call` is synchronous — the HTTP response waits for the tool result (up to `responseTimeoutSeconds`).

---

## 2. Endpoint and authentication

### 2.1 URL pattern

```
POST /orgs/:orgSlugOrId/workspaces/:workspaceSlugOrId/mcp/:canvasId/:actorId
```

The full URL (with copy button and a ready-to-paste client config snippet) is shown in the actor's settings panel. Example client configuration:

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

The simplest way to authenticate is a BorgIQ Personal Access Token sent as a Bearer token:

```http
POST /orgs/my-org/workspaces/my-workspace/mcp/CNVS.../ACTR...
Authorization: Bearer biq_abc123...
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2025-11-25
```

- Token format: `biq_<40 hex chars>`; sent as `Authorization: Bearer <token>` per OAuth 2.1 — never in a URI query string.
- The token must have the scopes **`AccessWorkspace`**, **`AccessCanvases`**, and **`CreateFlowrun`**, and belong to a member of the workspace in the URL.
- Auth must be included on **every** request, even within one logical session.

**Auth failures use HTTP status codes** (not JSON-RPC errors):

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
```

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope", scope="workspace:read canvas:read flowrun:create"
```

### 2.3 OAuth 2.1

The endpoint also supports the [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) (OAuth 2.1). On a `401`, the `WWW-Authenticate` header carries a `resource_metadata` pointer to the Protected Resource Metadata endpoint (RFC 9728) so MCP clients can discover the authorization server and run the standard authorization-code + PKCE flow. Use OAuth for clients that support it; PATs remain the pragmatic path for header-based client configs.

### 2.4 Origin policy

A *present and invalid* `Origin` header is rejected with HTTP 403 (DNS-rebinding protection). An absent `Origin` is allowed — only browsers attach one; non-browser MCP clients omit it.

---

## 3. Transport and protocol eras

The server uses **Streamable HTTP** on a single endpoint and serves **two protocol eras from that one URL**:

| Era | Revisions | Shape |
|---|---|---|
| **Modern** | `2026-07-28` | Stateless. No handshake; every request carries its protocol version, client identity and capabilities in `_meta`. `server/discover` replaces `initialize`. |
| **Legacy** | `2025-11-25`, `2025-06-18`, `2025-03-26` | `initialize` handshake, negotiated once. |

`2026-07-28` is a breaking revision, and most MCP clients were still on the older ones when it shipped. Serving both means a client connects with whatever it speaks, at the same URL, with the same credentials — nothing to configure either way.

**Era selection.** The request body decides: a `_meta` protocol version of `2026-07-28` or later is modern; its absence is legacy. `server/discover` always classifies as modern — it exists in no earlier revision.

- **`POST`**: the only method. A JSON-RPC *request* returns `application/json`; a *notification* returns `202 Accepted` with no body.
- **`GET`** and **`DELETE`**: permanently `405`. `2026-07-28` removed the standalone SSE stream and protocol-level sessions outright.

**Headers.**

- `MCP-Protocol-Version` — validated against the supported set. An unsupported value returns `400` with `-32022` and a `supported` list, so a client can retry on a revision both sides speak. Absent ⇒ `2025-03-26`, since revisions before `2025-06-18` never defined the header.
- `Mcp-Method`, `Mcp-Name` — **required on modern requests** and validated against the body (`Mcp-Name` after decoding the `=?base64?…?=` sentinel). A mismatch returns `400` with `-32020`.
- `Accept: application/json, text/event-stream` — required of clients by the spec; a missing value is logged rather than rejected.
- `Mcp-Session-Id` — no longer part of the protocol. Never minted, never read.

### 3.1 Supported methods, by era

| JSON-RPC method | Modern (`2026-07-28`) | Legacy (`2025-11-25` and earlier) |
|---|---|---|
| `server/discover` | `200` — supported versions, capabilities, identity, cache hints | `-32601` |
| `initialize` | `-32601` — the handshake was removed | `200` — echoes the client's requested revision when it is one we serve |
| `ping` | `-32601` — removed | `200` with `{}` |
| `tools/list` | `200`, tagged `resultType: "complete"` + `ttlMs` + `cacheScope: "private"` | `200`, `{ tools }` |
| `tools/call` | `200`, tagged `resultType`; may instead return `input_required` (see §5) | `200`, untagged |
| any notification | `202 Accepted`, no body | `202 Accepted`, no body |
| unknown | **`404`** + `-32601` | `200` + `-32601` |

Tools are returned in a deterministic (name-sorted) order, which the modern spec asks for so client and LLM prompt caches hit.

### 3.2 `initialize` (legacy era only)

> On the modern era there is no handshake. A client that wants this information calls `server/discover` instead — and even that is optional, since a client may simply invoke `tools/list` or `tools/call` directly.

**Request** (from the MCP client):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": { "roots": { "listChanged": true }, "sampling": {} },
    "clientInfo": { "name": "claude-desktop", "version": "1.0.0" }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": { "tools": { "listChanged": false } },
    "serverInfo": {
      "name": "BorgIQ - <canvas name>",
      "title": "<MCP Server Actor name>",
      "version": "1.0.0"
    },
    "instructions": "This MCP server exposes BorgIQ workflow tools. Use tools/list to discover available tools."
  }
}
```

The actor's `description` field is exposed to clients as the `instructions` string. Version negotiation echoes the client's requested revision whenever it is one we serve; otherwise the newest *legacy* revision is offered — never the stateless one, which a handshake client could not follow us into.

After initialization the client sends `notifications/initialized`; the server answers `202 Accepted` with no body.

---

## 4. Tools

### 4.1 `tools/list`

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_database",
        "title": "Search Database",
        "description": "Search the customer database by query",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": { "type": "string", "description": "The search query" },
            "limit": { "type": "integer", "description": "Max results to return" }
          },
          "required": ["query"]
        },
        "annotations": { "readOnlyHint": true, "openWorldHint": false }
      }
    ]
  }
}
```

**Tool definition fields:**

| Field | Source | Required |
|---|---|---|
| `name` | Tool actor's `msgVar` | Yes |
| `title` | Tool actor's `name` (display name) | Optional |
| `description` | Tool actor's `description` | Optional (recommended) |
| `inputSchema` | Filtered `${{aiInput}}` properties from the actor input schema | Yes |
| `outputSchema` | Tool actor's output schema (`schemas.outputs`), if defined | Optional |
| `annotations` | Behavior hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), derived from actor type with safe defaults | Optional |

**Schema conversion notes:**

- BIQ JSON Schema `ui` fields are stripped (not relevant to MCP clients).
- `${{aiInput}}` sentinel values are removed from defaults.
- `title` on schema properties is preserved; `const` fields are excluded (fixed values, not caller-configurable).
- Array and object types are preserved with their nested schemas; the dialect is JSON Schema 2020-12 per the MCP spec.
- A tool with no `${{aiInput}}` parameters gets `{ "type": "object", "additionalProperties": false }`.

### 4.2 `tools/call`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_database",
    "arguments": { "query": "Acme Corp", "limit": 10 }
  }
}
```

**Success response** (with structured content when the tool has an `outputSchema`):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      { "type": "text", "text": "{\"results\": [{\"name\": \"Acme Corp\", \"id\": \"cust_123\"}], \"count\": 1}" }
    ],
    "structuredContent": {
      "results": [{ "name": "Acme Corp", "id": "cust_123" }],
      "count": 1
    },
    "isError": false
  }
}
```

**Result mapping:**

| Tool result type | `content` | `structuredContent` |
|---|---|---|
| `string` | `{ type: "text", text: <value> }` | `{ "value": <value> }` |
| `object` | JSON-stringified text | The object directly (validated against `outputSchema` if present) |
| `array` | JSON-stringified text | `{ "items": [...] }` |
| Error | `{ type: "text", text: <error message> }` with `isError: true` | — |

**Tool execution errors** are returned as tool results with `isError: true` — actionable feedback the calling LLM can use to self-correct:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [{ "type": "text", "text": "Error: Connection to database timed out" }],
    "isError": true
  }
}
```

**Protocol-level errors** (invalid tool name, malformed request) use JSON-RPC `error` objects instead:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": { "code": -32602, "message": "Unknown tool: invalid_tool_name" }
}
```

Tool results currently use `text` content. If a tool actor has `continueOnError: true` and produces an error output, the error is returned as a tool result with `isError: true`; with `continueOnError: false`, the run enters error state and the MCP response carries the error message.

---

## 5. Asking the caller for input (`input_required`)

`2026-07-28` removed server-initiated requests. A tool that needs input from the calling client — elicitation, sampling, roots — asks for it **in the result**: the server answers `tools/call` with `resultType: "input_required"`, and the client retries the original call with its answers and an opaque `requestState`.

A tool actor opts in by completing with a **reserved output shape**:

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

Notes:

- Supported request kinds are `elicitation/create`, `sampling/createMessage` and `roots/list`. Anything else in the envelope is ignored.
- Only requests the client **declared it can answer** are sent. If the client declared none of them, the call comes back as an error explaining that, rather than as an input request it could not act on.
- `requestState` is single-use, expires after 5 minutes, and is bound to the caller, the tool and the exact arguments. A retry that changes any of those starts over.
- **Legacy clients cannot answer an input request.** A tool that returns the envelope to one gets an error result naming the problem; the envelope is never passed through as if it were the tool's real answer.

---

## 6. Limits, errors, and edge cases

### 6.1 Unknown tool

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": { "code": -32602, "message": "Tool 'unknown_tool' not found. Use tools/list to discover available tools." }
}
```

### 6.2 Tool execution timeout

If the tool doesn't complete within `responseTimeoutSeconds`, the client receives a tool result with `isError: true` ("Tool execution timed out after 60 seconds"). The underlying run continues to execute — it is not cancelled.

### 6.3 Canvas not active

If the canvas is in draft state or the actor is disabled:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32001, "message": "MCP server is not active. Ensure the canvas is deployed and the actor is enabled." }
}
```

### 6.4 Tool configuration changes

Adding or removing tool actors is not pushed to connected clients — clients must re-call `tools/list` to see the updated set.

### 6.5 Concurrency

Clients may call multiple tools concurrently; each `tools/call` creates an independent run with no cross-call state.

### 6.6 Rate limiting

Three levels apply:

1. **Per token** — the standard API-token limit (default 120 requests/min).
2. **Per MCP server** — each MCP Server Actor instance has its own sliding-window budget (default 60 requests/min) covering all request types.
3. **Per tool execution** — the platform's standard actor invocation limits apply to `tools/call`.

All responses carry `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` headers. When exceeded:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
```

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Rate limit exceeded. Retry after 45 seconds.",
    "data": { "retryAfterSeconds": 45 }
  }
}
```

### 6.7 Request and response size

- Request bodies are limited to 1 MB.
- Tool names: 1–128 chars, alphanumeric plus `_-. `.
- Very large tool results are capped at 10 MB and truncated with an error message beyond that.

### 6.8 JSON-RPC error codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error (malformed JSON) |
| `-32600` | Invalid request (missing required fields) |
| `-32601` | Method not found (unsupported MCP method) |
| `-32602` | Invalid params (bad tool name or arguments) |
| `-32603` | Internal error |
| `-32000` | Server error (rate limit, workspace access denied) |
| `-32001` | MCP server not active |
| `-32020` | Modern-era header/body mismatch (`Mcp-Method` / `Mcp-Name`) |
| `-32022` | Unsupported `MCP-Protocol-Version` (response lists supported revisions) |

### 6.9 Workspace access

The PAT must belong to a member of the workspace in the URL; otherwise the call fails with HTTP `403` and a `-32000` "Access denied to workspace" error.
