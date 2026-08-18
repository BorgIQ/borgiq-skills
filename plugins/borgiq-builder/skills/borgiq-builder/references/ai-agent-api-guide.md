# AI Agent API Guide

How to use the BorgIQ API to programmatically create, edit, test, and debug flows.

This guide is written for AI agents (like Claude Code) that interact with BorgIQ through HTTP API calls using a Personal Access Token (PAT). It covers the full lifecycle: authentication, discovery, flow creation, execution, monitoring, and debugging.

---

## Prerequisites

- A BorgIQ account with access to at least one organization and workspace
- A Personal Access Token (see [API Tokens documentation](api-tokens.md) for creation and management)

---

## Authentication

All API requests require a Bearer token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer biq_<your_token>" \
  https://your-api-host/v1/orgs
```

### Recommended Scopes for AI Agents

Create your token with these scopes for full flow management capabilities:

```json
[
  "org:access",
  "workspace:access",
  "canvas:read",
  "canvas:write",
  "canvas:delete",
  "flowrunJob:read",
  "flowrunJob:reRun",
  "flowrunJobResult:read",
  "flowrunMessage:read",
  "Trigger:manual:create",
  "connection:read",
  "connection:write",
  "secret:read",
  "secret:write",
  "asset:read",
  "asset:write",
  "borgiqActor:read"
]
```

For read-only monitoring, a minimal set is sufficient:

```json
[
  "org:access",
  "workspace:access",
  "canvas:read",
  "flowrunJob:read",
  "flowrunJobResult:read",
  "flowrunMessage:read"
]
```

### Rate Limits

API tokens are rate-limited to **120 requests per minute** by default. Check response headers:

| Header | Description |
|--------|-------------|
| `RateLimit-Limit` | Max requests per window |
| `RateLimit-Remaining` | Requests remaining |
| `RateLimit-Reset` | Seconds until window resets |

---

## ID Generation

BorgIQ uses prefixed ULIDs for all entity IDs. When creating actors, edges, and ports via the API, you must generate IDs client-side.

### ID Format Reference

| Entity | Prefix | Length | Character Set |
|--------|--------|--------|---------------|
| Actor | `ACTR` | 30 | ULID: `0-9, a-h, j-k, m-n, p, q, r-t, v-z` (excludes i, l, o, u) |
| Edge | `EDGE` | 30 | ULID (same as above) |
| Source Port | `SPRT` | 11 | Full lowercase alphanumeric: `a-z, 0-9` |

### ID Generation Script (Node.js)

```javascript
import { monotonicFactory } from 'ulidx';

const monotonicUlid = monotonicFactory();

function generateId(prefix) {
  // ULID-based IDs (actors, edges): 4-char prefix + 26-char lowercase ULID
  return `${prefix}${monotonicUlid().toLowerCase()}`;
}

function generateSourcePortId() {
  // Source ports: SPRT + 7 random lowercase alphanumeric chars
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = 'SPRT';
  for (let i = 0; i < 7; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

// Usage:
const actorId = generateId('ACTR');   // e.g., "ACTR01kmka7wqwan6fh6k5hgfpyv59"
const edgeId = generateId('EDGE');    // e.g., "EDGE01kmka7wr0j2g6mz540ezp0sts"
const portId = generateSourcePortId(); // e.g., "sprt3k9m2x7"
```

### ID Generation Script (Python)

```python
import ulid
import random
import string

def generate_id(prefix: str) -> str:
    """ULID-based IDs: 4-char prefix + 26-char lowercase ULID."""
    return f"{prefix}{ulid.new().str.lower()}"

def generate_source_port_id() -> str:
    """Source ports: SPRT + 7 random lowercase alphanumeric chars."""
    chars = string.ascii_lowercase + string.digits
    return "SPRT" + "".join(random.choices(chars, k=7))

# Usage:
actor_id = generate_id("ACTR")   # e.g., "ACTR01kmka7wqwan6fh6k5hgfpyv59"
edge_id = generate_id("EDGE")    # e.g., "EDGE01kmka7wr0j2g6mz540ezp0sts"
port_id = generate_source_port_id() # e.g., "sprt3k9m2x7"
```

### Validating IDs

Use `GET .../canvases/{id}/validate` to check if IDs in your canvas are correctly formatted. The endpoint returns detailed error messages with the expected format when IDs are malformed.

---

## URL Structure

All endpoints follow a nested resource pattern:

```
/v1/orgs/{orgSlugOrId}/workspaces/{workspaceSlugOrId}/{resource}
```

You can use either slugs or IDs interchangeably for `orgSlugOrId` and `workspaceSlugOrId`.

---

## Step 1: Discover Your Environment

Before creating flows, discover the orgs, workspaces, and existing canvases available to you.

### List Organizations

```bash
GET /v1/orgs
```

Returns all organizations your token's user belongs to.

### List Workspaces in an Organization

```bash
GET /v1/orgs/{orgSlugOrId}/workspaces
```

Returns all workspaces within the org.

### List Canvases (Flows) in a Workspace

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/
```

Returns canvas metadata: `id`, `name`, `slug`, `description`, `tags`, `createdAt`, `updatedAt`.

### Get a Canvas with Its Flow Data

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}?includeData=true
```

Returns canvas metadata plus `data: BIQCanvasData` — the full actor graph including actors, edges, positions, and configuration.

### Get Available Actor Types

```bash
GET /v1/actors
```

Returns the list of all actor types available for use in flows, with their default configurations and schemas.

### Get Actor Type Schema

```bash
GET /v1/actors/{actorType}/schema
```

Returns the options schema (BIQ JsonSchema), source port configuration, code support, default options, and capabilities for an actor type. For action-based actors (DataStoreActor, CollectionActor, MessageProcessorActor), returns the action selector but not per-action schemas — use the `?action` query param for those.

**Response (non-action actor):**

```json
{
  "actorType": "HttpRequestActor",
  "name": "HTTP Request",
  "description": "...",
  "category": "task",
  "optionsSchema": { "properties": { "url": { ... }, "method": { ... } }, "required": ["method", "url"] },
  "actions": null,
  "defaultOptions": { "url": "https://www.example.com", "method": "GET" },
  "sourcePorts": { "type": "singleDefault", "fixedPorts": [{ "id": "SPRTdefault" }], "canAddPorts": false },
  "code": { "supported": false, "language": null },
  "canReceiveMessage": true,
  "canEmitMessage": true,
  "supportsConnection": true,
  "enableLTM": false,
  "enableSTM": false
}
```

**Response (action-based actor):**

For actors with multiple actions, `optionsSchema` is `null` and `actions` contains the action selector schema:

```json
{
  "actorType": "DataStoreActor",
  "optionsSchema": null,
  "actions": {
    "selectorSchema": { "type": "string", "enum": ["get", "set", "delete", ...], "ui": { "component": "searchSelect", "options": { "enumLabels": { ... }, "enumGroups": { ... } } } }
  },
  "defaultOptions": { "scope": "canvas", "action": "set", "key": "myKey", "value": "myValue" },
  ...
}
```

### Get Per-Action Schema

```bash
GET /v1/actors/{actorType}/schema?action={action}
```

For action-based actors, returns the specific action's options schema and memory requirements:

```json
{
  "actorType": "MessageProcessorActor",
  "action": "dedupeByCount",
  "label": "Dedupe By Count",
  "group": "Dedupe",
  "optionsSchema": { "properties": { "action": { ... }, "scope": { ... }, "count": { ... } }, "required": ["action", "scope", "count"] },
  "memory": { "ltm": true }
}
```

The `memory` field indicates whether this action requires LTM (long-term memory) or STM (short-term memory) to be enabled on the actor.

---

## Step 2: Create a Flow

A flow is stored as a **canvas** containing **actors** connected by **edges**. There are two approaches to creating a flow:

### Option A: Create a Canvas with Full Data (Recommended)

Use this when building a complete flow in one shot:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/data
Content-Type: application/json

{
  "name": "My API Flow",
  "slug": "my-api-flow",
  "description": "A flow created via API",
  "tags": "api,automated",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01kmka7wqwan6fh6k5hgfpyv59": {
        "id": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
        "type": "ButtonTriggerActor",
        "name": "Manual Trigger",
        "msgVar": "manualTrigger",
        "isActive": true,
        "configuration": {
          "options": ""
        },
        "schemas": {},
        "position": { "x": 100, "y": 200 },
        "sourcePorts": [
          { "id": "SPRTa1b2c3d", "name": "output" }
        ],
        "edges": {
          "EDGE01kmka7wr0j2g6mz540ezp0sts": {
            "id": "EDGE01kmka7wr0j2g6mz540ezp0sts",
            "sourceActorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
            "sourcePortId": "SPRTa1b2c3d",
            "targetActorId": "ACTR01kmka7wr0j2g6mz540ezp0str",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        },
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "editVersion": 1,
        "version": 1
      },
      "ACTR01kmka7wr0j2g6mz540ezp0str": {
        "id": "ACTR01kmka7wr0j2g6mz540ezp0str",
        "type": "EchoActor",
        "name": "Echo",
        "msgVar": "echo",
        "isActive": true,
        "configuration": {
          "options": ""
        },
        "schemas": {},
        "position": { "x": 400, "y": 200 },
        "sourcePorts": [
          { "id": "SPRTe4f5g6h", "name": "output" }
        ],
        "edges": {},
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "editVersion": 1,
        "version": 1
      }
    }
  }
}
```

**Response** (200):

```json
{
  "id": "CANV01kmka7wr13pqkhbkz58rrpw0k",
  "name": "My API Flow",
  "slug": "my-api-flow",
  "version": 1,
  "createdAt": "2026-03-23T12:00:00.000Z",
  "updatedAt": "2026-03-23T12:00:00.000Z"
}
```

### Option B: Create Empty Canvas, Then Add Actors

Create the canvas first:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases
Content-Type: application/json

{
  "name": "My Flow",
  "slug": "my-flow",
  "description": "Built incrementally"
}
```

Then add actors incrementally using the batch actor operations endpoint:

```bash
PATCH /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors
Content-Type: application/json

{
  "operations": [
    {
      "type": "add",
      "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
      "data": {
        "id": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
        "type": "ButtonTriggerActor",
        "name": "Manual Trigger",
        "msgVar": "manualTrigger",
        "isActive": true,
        "configuration": { "options": "" },
        "schemas": {},
        "position": { "x": 100, "y": 200 },
        "sourcePorts": [{ "id": "SPRTa1b2c3d", "name": "output" }],
        "edges": {},
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "editVersion": 1,
        "version": 1
      }
    }
  ]
}
```

**Response** (200):

```json
{
  "appliedOperations": [
    { "type": "add", "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59", "status": "applied" }
  ],
  "conflicts": [],
  "updatedAt": "2026-03-23T12:00:00.000Z"
}
```

### Available Actor Types

**Triggers** (flow entry points):
| Type | Description |
|------|-------------|
| `ButtonTriggerActor` | Manual trigger via UI button or API |
| `WebhookTriggerActor` | HTTP webhook trigger |
| `ScheduledTriggerActor` | Cron-based scheduled trigger |
| `EmailTriggerActor` | Email-based trigger |
| `CallableTriggerActor` | Called by another flow via CallFlow actor |
| `InterfaceTriggerActor` | Triggered by user form submission |
| `AppTriggerActor` | Triggered by app interaction |

**Task Actors** (perform work):
| Type | Description |
|------|-------------|
| `HttpRequestActor` | Make HTTP requests |
| `MessageProcessorActor` | Process and transform messages |
| `DenoActor` | Run custom Deno/TypeScript code |
| `PythonActor` | Run custom Python code |
| `AiAgentActor` | LLM-powered agent with tool use |
| `AgentHarnessActor` | Multi-step agent execution harness |
| `DataStoreActor` | CRUD operations on data collections |
| `SendEmailActor` | Send emails |
| `EchoActor` | Pass through data (useful for testing) |

**Control Actors** (flow logic):
| Type | Description |
|------|-------------|
| `RouterActor` | Conditional routing based on rules |
| `AiRouterActor` | AI-powered routing decisions |
| `CallFlowActor` | Call another flow as a subflow |

**Response Actors:**
| Type | Description |
|------|-------------|
| `WebhookResponseActor` | Return HTTP response to webhook caller |
| `CallableResponseActor` | Return response to parent flow |

### Configuration Fields

Each actor's `configuration` object supports these fields (availability varies by actor type):

| Field | Type | Description |
|-------|------|-------------|
| `options` | YAML string | Actor-specific options (URL, method, model, etc.) |
| `code` | string | Custom code for Deno/Python actors |
| `inputs` | YAML string | Static input values |
| `vars` | YAML string | Variable definitions |
| `outputs` | YAML string | Output mapping configuration |
| `credentials` | YAML string | Credential references (e.g., `myCredential: ${{ credentials.API_KEY }}`) |
| `connection` | object | `{ type: "connectionType" \| ["typeA", "typeB"], key: "connectionKey" }` |
| `error` | YAML string | Error handling configuration |
| `webhookTriggerKey` | string | Unique key for webhook URL (WebhookTrigger only) |
| `aiAgentToolActorIds` | string[] | Actor IDs available as tools (AiAgent only) |

Use `GET /v1/actors/{actorType}/schema` to see which fields are required for a specific actor type.

### Edge Structure

Edges connect an actor's output port to another actor's input. They are stored on the **source** actor:

```json
{
  "edges": {
    "<edgeId>": {
      "id": "<edgeId (ULID)>",
      "sourceActorId": "<this actor's ID>",
      "sourcePortId": "<port ID from this actor's sourcePorts>",
      "targetActorId": "<destination actor's ID>",
      "targetPortId": "TPRTdefault",
      "type": "borgiqEdge"
    }
  }
}
```

Every actor has a single incoming `targetPortId` of `"TPRTdefault"` (the value of `DEFAULT_TARGET_PORT_ID` in `@borgiq/types`). Source ports are defined in the actor's `sourcePorts` array.

### Source Port Reference

Each actor type has specific source port requirements. The validation endpoint checks these automatically.

**Single port actors** — most actors have exactly one port with ID `SPRTdefault`:

All trigger actors (except AppTrigger), `HttpRequestActor`, `DenoActor`, `PythonActor`, `DenoTestActor`, `DataStoreActor`, `SendEmailActor`, `MessageProcessorActor`, `AiActor`, `CallFlowActor`, `WebhookResponseActor`, `CallableResponseActor`, `InterfaceStatusActor`, `CollectionActor`, `EchoActor`.

```json
"sourcePorts": [{ "id": "SPRTdefault", "name": "output" }]
```

**No ports** — `AppTriggerActor` and `CommentActor` have no source ports:

```json
"sourcePorts": []
```

**Fixed multi-port actors:**

| Actor Type | Ports |
|-----------|-------|
| `AgentHarnessActor` | `SPRTdone000` ("Done") + `SPRTdefault` ("Status") |
| `AiAgentActor` | `SPRTdone000` ("Done") + `SPRTdefault` ("Status") |
| `InterfaceActor` | `SPRTevent00` ("Event") + `SPRTdefault` ("Meta") |

**Dynamic port actors** — `RouterActor` and `AiRouterActor` have configurable routes. They must always include `SPRTdefault` (the fallback route) and at least one additional named route:

```json
"sourcePorts": [
  { "id": "SPRT5d5gj2s", "name": "True" },
  { "id": "SPRTdefault", "name": "False" }
]
```

Additional routes can be added with generated SPRT IDs (11 chars: `SPRT` + 7 random `a-z0-9`).

---

## Step 3: Validate and Layout

### Validate a Canvas

Before executing a flow, check for configuration errors:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/validate
```

**Response:**

```json
{
  "valid": false,
  "errors": [
    {
      "actorId": "ACTR01kmka7ws4xn8jrz3c7bq1d2y6",
      "actorName": "Transform Data",
      "field": "configuration.code",
      "message": "Code is required for DenoActor"
    },
    {
      "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
      "actorName": "My Actor",
      "field": "id",
      "message": "Invalid actor ID \"BAD_ID\". Actor IDs must be 30 characters: prefix \"ACTR\" + 26-character lowercase ULID (0-9, a-h, j-k, m-n, p, q, r-t, v-z — excludes i, l, o, u)."
    }
  ],
  "warnings": [
    { "message": "Canvas has no trigger actor — flow can only be started via manual trigger or test run" }
  ]
}
```

**What's validated:**
- **ID formats** — actor IDs, edge IDs, source port IDs (with format hints on error)
- **Duplicate `msgVar`** — each actor must have a unique `msgVar`
- **Graph structure** — edge references, self-referential edges, disconnected actors
- **Actor configuration** — code required for Deno/Python actors, webhook keys, AI agent tool references
- **Resource references** — connections exist in workspace

### Auto-Layout a Canvas

After creating a canvas programmatically (especially with arbitrary positions), use the layout endpoint to arrange actors visually:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/layout
```

This applies the same ELK-based layout algorithm the frontend uses — actors flow top-to-bottom following edge connections.

**Partial layout** — to layout only actors downstream of specific actors (keeping everything else in place), pass `sourceActorIds` in the request body:

```json
{
  "sourceActorIds": ["ACTR01kmka7wr0j2g6mz540ezp0str"]
}
```

A single source actor keeps its original position as the anchor. With multiple source actors, the top-leftmost actor is the anchor.

**Pinned actor positions** — to keep specific actors at fixed positions during layout, pass `pinnedActorPositions`. Omitted `x`/`y` values default to the actor's current canvas position:

```json
{
  "sourceActorIds": ["ACTR01flow1trigger", "ACTR01flow2trigger"],
  "pinnedActorPositions": {
    "ACTR01flow2trigger": { "x": 600, "y": 0 }
  }
}
```

**Response:**

```json
{
  "id": "CANV01kmka7wr13pqkhbkz58rrpw0k",
  "version": 5,
  "actors": {
    "ACTR01kmka7wqwan6fh6k5hgfpyv59": { "x": 227, "y": 0 },
    "ACTR01kmka7wr0j2g6mz540ezp0str": { "x": 227, "y": 200 },
    "ACTR01kmka7wrx9dp4mn2h3qfr8e4t": { "x": 0, "y": 400 }
  }
}
```

Returns only the repositioned actors with their new coordinates.

---

## Step 4: Edit a Flow

> **Bundle first:** with shell access, edit a deployed canvas through its [canvas bundle](cli/canvas-bundles.md) (`bundle pull` → edit files → `bundle push`) instead of calling these endpoints directly. Use the raw API below only when no bundle is possible, and never patch out of band a canvas that is maintained as a local bundle.

### Batch Actor Operations

The batch actor operations endpoint is the incremental, version-conflict-aware way to edit flows over the raw API:

```bash
PATCH /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors
Content-Type: application/json

{
  "operations": [
    {
      "type": "update",
      "actorId": "ACTR01kmka7wr0j2g6mz540ezp0str",
      "editVersion": 1,
      "data": {
        "name": "Renamed Echo Actor",
        "configuration": {
          "options": "someOption: newValue"
        }
      }
    },
    {
      "type": "remove",
      "actorId": "ACTR01kmka7wrx9dp4mn2h3qfr8e4t"
    }
  ]
}
```

**Operation types:**
- `add` — Add a new actor to the canvas
- `update` — Update an existing actor (requires `editVersion` for conflict detection)
- `remove` — Remove an actor from the canvas

If an `update` operation's `editVersion` doesn't match the current version, it's reported in the `conflicts` array instead of being applied.

### Import Canvas Data

Import actors into a canvas with 3 modes:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/import
Content-Type: application/json

{
  "canvas": {
    "schemaVersion": "1",
    "actors": { ... }
  },
  "mode": "merge"
}
```

**Modes:**

| Mode | Behavior |
|------|----------|
| `merge` (default) | Add new actors, update existing actors by ID. Actors not in the import are left untouched. |
| `insert` | Generate new actor IDs for all imported actors. Edges are remapped automatically. Existing actors are untouched. |
| `replace` | Replace the entire canvas with the imported data. Actors not in the import are deleted. Returns `409` if the canvas was modified concurrently. |

**Response:** Same as `PATCH .../actors` — returns `appliedOperations`, `conflicts`, and `processed` actor IDs.

**Conflict detection:** All modes use per-actor `editVersion` checking (same as the batch actor operations endpoint). Conflicts are reported in the `conflicts` array. Replace mode additionally uses canvas-level optimistic locking to prevent data loss from concurrent edits.

### Update Canvas Metadata

To update the canvas name, slug, description, or tags (without changing the flow data):

```bash
PUT /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "New description"
}
```

### Delete a Canvas

```bash
DELETE /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}
```

This is a soft delete — the canvas is marked as deleted but can potentially be recovered.

### Single Actor Operations

For fine-grained control over individual actors, use these dedicated endpoints instead of the batch actor operations endpoint.

#### List Actors in a Canvas

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors?page=1&pageSize=25&actorType=DenoActor&isActive=true&search=query
```

Returns a paginated, filterable list of actors in the canvas. Filter by `actorType`, `isActive`, and `search` (searches name and description).

**Response:**

```json
{
  "total": 3,
  "actors": [
    {
      "id": "ACTR01kmka7wr0j2g6mz540ezp0str",
      "name": "Process Data",
      "type": "DenoActor",
      "isActive": true,
      "msgVar": "processData",
      ...
    }
  ]
}
```

#### Get a Single Actor

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/{actorId}
```

Returns the full `BIQCanvasActor` object for the specified actor.

#### Get Actor Flow (Downstream Actors)

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/{actorId}/flow
```

Returns the specified actor plus all downstream actors reachable by following edges (BFS traversal). Useful for understanding what happens after a specific actor executes.

**Response:**

```json
{
  "sourceActorId": "ACTR01kmka7wr0j2g6mz540ezp0str",
  "actors": [ ... ],
  "actorCount": 5
}
```

#### Verify Actor Options

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/verify
Content-Type: application/json

{
  "actorType": "HttpRequestActor",
  "options": "method: GET\nurl: https://api.example.com/data"
}
```

Validates actor options (YAML string) against the actor type's schema before applying them. Returns validation results without modifying the canvas.

For `RouterActor` and `AiRouterActor`, include `sourcePorts` so route conditions can be validated:

```json
{
  "actorType": "RouterActor",
  "options": "conditions:\n  approved: \"${{ msg.Review.status === 'approved' }}\"",
  "sourcePorts": [
    { "id": "SPRTdefault" },
    { "id": "SPRTabc1234", "name": "approved" }
  ]
}
```

**Response:**

```json
{
  "valid": true,
  "errors": []
}
```

Or when invalid:

```json
{
  "valid": false,
  "errors": [
    { "path": ["url"], "message": "Invalid url" }
  ]
}
```

#### Create a Single Actor

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/{actorId}
Content-Type: application/json

{
  "name": "Fetch Data",
  "type": "HttpRequestActor",
  "version": 1,
  "msgVar": "fetchData",
  "description": "",
  "isActive": true,
  "continueOnError": false,
  "enableLTM": false,
  "enableSTM": false,
  "showInWorkspaceApps": true,
  "configuration": {
    "options": "method: GET\nurl: https://api.example.com"
  },
  "schemas": {},
  "sourcePorts": [{ "id": "SPRTdefault" }],
  "edges": {},
  "position": { "x": 0, "y": 0 }
}
```

The actor ID is specified in the URL path. Generate it client-side using the `ACTR` prefix format.

#### Update a Single Actor

```bash
PATCH /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/{actorId}?editVersion=1
Content-Type: application/json

{
  "name": "Updated Name",
  "configuration": {
    "options": "method: POST\nurl: https://api.example.com/submit"
  }
}
```

Partial update — only include the fields you want to change. The optional `editVersion` query parameter enables conflict detection.

#### Delete a Single Actor

```bash
DELETE /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/actors/{actorId}?editVersion=1
```

Removes the actor from the canvas. The optional `editVersion` query parameter enables conflict detection.

---

## Step 5: Execute a Flow

### Manual Trigger

The simplest way to run a flow. The canvas must contain a `ButtonTriggerActor`:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/triggers/manual
Content-Type: application/json

{
  "canvasId": "CANV01kmka7wr13pqkhbkz58rrpw0k",
  "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59"
}
```

**Response** (200):

```json
{
  "flowrun": {
    "id": "FLRN01kmka7wr13pqkhbkz58rrpw0m",
    "createdAt": 1711195200000
  },
  "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59"
}
```

Save the `flowrun.id` — you'll need it to monitor execution.

### Webhook Trigger

For `WebhookTriggerActor` flows, send data directly to the webhook URL:

```bash
POST /v1/msg/{org}/{workspace}/{canvasId}/{actorId}/{webhookKey}
Content-Type: application/json

{
  "any": "payload",
  "you": "want"
}
```

This endpoint is **unauthenticated** (public). The `webhookKey` is configured in the actor's `configuration.webhookTriggerKey`.

If the flow includes a `WebhookResponseActor`, the HTTP response will contain the flow's output. Otherwise, you'll get a simple acknowledgement.

The response includes an `X-BIQ-Flowrun-Id` header containing the flowrun ID, which you can use to monitor execution via the flowrun endpoints.

### Test Run a Single Actor

Test an individual actor using its most recent input data:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs/testRun
Content-Type: application/json

{
  "canvasId": "CANV01kmka7wr13pqkhbkz58rrpw0k",
  "actorId": "ACTR01kmka7wr0j2g6mz540ezp0str",
  "publishEmittedMessageToConnectedActors": false
}
```

Set `publishEmittedMessageToConnectedActors` to `true` if you want downstream actors to also execute. Set to `false` to test just this actor in isolation.

**Response** (200):

```json
{
  "flowrun": {
    "id": "FLRN01kmka7wr13pqkhbkz58rrpw0m",
    "createdAt": 1711195200000
  },
  "flowrunJob": {
    "id": "FJOB01kmka7wr13pqkhbkz58rrpw0n"
  },
  "actorId": "ACTR01kmka7wr0j2g6mz540ezp0str"
}
```

Use the returned `flowrunJob.id` to check results via `GET .../flowrunJobResults/summaries?flowrunJobId=X`, or the `flowrun.id` to monitor the broader execution.

### Re-Run a Previous Job

If a job failed and you've fixed the actor configuration, re-run it:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs/reRun
Content-Type: application/json

{
  "flowrunJobId": "FJOB01kmka7wr13pqkhbkz58rrpw0n",
  "publishEmittedMessagesToConnectedActors": true
}
```

This replays the same input message through the actor with the **latest** canvas configuration.

### Interrupt a Running Flow

Stop a flow that's currently executing:

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/flowruns/{flowrunId}/interrupt
```

Currently executing jobs will complete, but no new jobs will be created.

---

## Step 6: Monitor Flow Execution

After triggering a flow, you need to track its execution.

### Poll Flowrun Status (Recommended for Agents)

The most efficient way to wait for a flow to complete:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowruns/{flowrunId}/status
```

**Response:**

```json
{
  "id": "FLRN01kmka7wr13pqkhbkz58rrpw0m",
  "state": "Running",
  "actors": ["ACTR01kmka7wqwan6fh6k5hgfpyv59", "ACTR01kmka7wr0j2g6mz540ezp0str"],
  "counters": {
    "actorInboxMessagesCounter": 2,
    "postProcessingCounter": 0,
    "delayedCounter": 0,
    "callbackTokenWaitingCounter": 0,
    "interfaceSubmissionWaitingCounter": 0,
    "callableResponseWaitingCounter": 0,
    "aiAgentToolWaitingCounter": 0,
    "agentHarnessWaitingCounter": 0,
    "agentHarnessToolWaitingCounter": 0
  },
  "createdAt": "2026-03-23T12:00:00.000Z",
  "updatedAt": "2026-03-23T12:00:01.000Z"
}
```

**States:**
- `Running` — Flow is still executing (at least one counter > 0)
- `Completed` — All counters are zero, flow finished
- `UserInterrupted` — Flow was manually interrupted

**Poll every 2-3 seconds** until `state` is `Completed` or `UserInterrupted`. The `actors` array shows which actors have participated so far. The `counters` object tells you *why* a flow isn't done — e.g., `callbackTokenWaitingCounter > 0` means the flow is waiting for an external callback.

### Get Flowrun Summary (Recommended for Debugging)

Get a complete picture of what happened in a single call:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowruns/{flowrunId}/summary
```

**Response:**

```json
{
  "id": "FLRN01kmka7wr13pqkhbkz58rrpw0m",
  "state": "Completed",
  "triggerActor": { "id": "ACTR01kmka7wqwan6fh6k5hgfpyv59", "type": "ButtonTriggerActor", "name": "Manual Trigger" },
  "createdAt": "2026-03-23T12:00:00.000Z",
  "actors": [
    {
      "actorId": "ACTR01kmka7wqwan6fh6k5hgfpyv59",
      "actorName": "Manual Trigger",
      "actorType": "ButtonTriggerActor",
      "jobs": [
        {
          "jobId": "FJOB01kmka7wr13pqkhbkz58rrpw0n",
          "state": "Emitted",
          "resultId": "FJBR01kmka7wr13pqkhbkz58rrpw0p",
          "status": "success",
          "startedAt": "2026-03-23T12:00:00.500Z",
          "endedAt": "2026-03-23T12:00:01.200Z",
          "error": null,
          "emittedMessageCount": {}
        }
      ]
    }
  ],
  "errors": []
}
```

The `errors` array provides a quick scan of all failures across all actors. The `actors` array gives per-actor job details.

### List Flowruns for a Canvas

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowruns?canvasId={canvasId}
```

Returns flowruns in descending order (newest first).

### Get Flowrun Details

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowruns/{flowrunId}
```

Returns metadata and per-actor emitted message counts. Includes the full canvas data snapshot at execution time.

### Get Flowrun Jobs for an Actor

See the execution history for a specific actor within a flowrun:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs?canvasId={canvasId}&actorId={actorId}&flowrunId={flowrunId}
```

**Flowrun job states:**
| State | Meaning |
|-------|---------|
| `Queued` | Waiting to be processed |
| `PostProcessing` | Actor finished, results being processed |
| `Error` | Actor execution failed |
| `Delayed` | Waiting before emitting messages |
| `Waiting` | Waiting for external event (callback, interface input, etc.) |
| `Emitted` | Successfully completed and messages sent to downstream actors |
| `RenderedInterface` | Interface rendered for user interaction |
| `Unknown` | State could not be determined |

---

## Step 7: Debug Flow Execution

### Get Job Result Summaries

See execution results for a specific job:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobResults/summaries?flowrunJobId={jobId}
```

Returns: status (`success` or `error`), timing, error metadata, and message metadata.

### Get Full Job Result Data

Retrieve the complete output data from an actor execution:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobResults/{resultId}/data
```

Returns the full runtime response: messages emitted per port, error details, signal data, and memory updates.

### Get Runtime Data (What the Actor Received)

Inspect what data an actor had access to during execution:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs/{jobId}/runtimeData?rootPath=ctx
```

**Available root paths:**

| Path | Description |
|------|-------------|
| `ctx` | Actor context (flowrun metadata, actor metadata, etc.) |
| `msg` | Accumulated messages from source actors |
| `request` | HTTP request data (WebhookTrigger only) |
| `user` | User data (InterfaceTrigger / AppTrigger only) |
| `inputs` | AI agent tool inputs (AiAgent / AgentHarness only) |

### Get Flowrun Messages

View the data flowing between actors:

```bash
# List messages for a specific actor and port
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunMessages?canvasId={canvasId}&flowrunId={flowrunId}&actorId={actorId}&portId={portId}

# Get full message payload
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunMessages/{messageId}/emittedData
```

### Get AI Agent Timeline

For `AiAgentActor` jobs, view the full tool-use timeline:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs/{jobId}/aiAgentTimeline
```

Returns the sequence of LLM calls, tool invocations, and responses.

### Get Source Flowrun Message

See what triggered a specific job:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/flowrunJobs/{jobId}/sourceFlowrunMessage
```

---

## Step 8: Manage Supporting Resources

### Connections

Connections store credentials for external services (OAuth2, API keys, etc.):

```bash
# List connections
GET /v1/orgs/{org}/workspaces/{workspace}/connections

# Get available connection types
GET /v1/orgs/{org}/workspaces/{workspace}/connections/types

# Create a connection
POST /v1/orgs/{org}/workspaces/{workspace}/connections

# Delete a connection
DELETE /v1/orgs/{org}/workspaces/{workspace}/connections/{connectionId}
```

### Secrets

Secrets store sensitive values that can be referenced in actor configurations if defined in the actor credentials, and are available to the rest of the configuration via `${{ credentials.KEY }}`:

```bash
# Standard CRUD operations
GET    /v1/orgs/{org}/workspaces/{workspace}/secrets
POST   /v1/orgs/{org}/workspaces/{workspace}/secrets
PUT    /v1/orgs/{org}/workspaces/{workspace}/secrets/{id}
DELETE /v1/orgs/{org}/workspaces/{workspace}/secrets/{id}
```

### Assets

Assets are files (images, documents, etc.) accessible to actors:

```bash
# Standard CRUD with file upload
GET    /v1/orgs/{org}/workspaces/{workspace}/assets
POST   /v1/orgs/{org}/workspaces/{workspace}/assets
DELETE /v1/orgs/{org}/workspaces/{workspace}/assets/{id}
```

### Export / Import Canvases

Export a canvas for backup, transfer, or duplication:

```bash
GET /v1/orgs/{org}/workspaces/{workspace}/canvases/{canvasId}/exportData
```

Import by creating a new canvas with the exported data (the server regenerates all ULIDs via `importCanvas()`):

```bash
POST /v1/orgs/{org}/workspaces/{workspace}/canvases/data
```

This is the recommended way to **duplicate** a canvas — export then re-import. All actor IDs, edge IDs, and cross-references are regenerated automatically.

You can verify import data before creating:

```bash
PUT /v1/orgs/{org}/workspaces/{workspace}/canvases/verifyCanvasImportData
```

---

## Common Workflows

### Create, Validate, Layout, and Test a Flow

```
1. GET  /v1/actors                                 → List available actor types
2. GET  /v1/actors/{actorType}/schema              → Get config schema for a type
3. POST .../canvases/data                           → Create canvas with actors + edges
4. GET  .../canvases/{id}/validate                  → Check for errors before running
5. POST .../canvases/{id}/layout                    → Auto-arrange actors visually
6. POST .../triggers/manual                         → Trigger the flow
7. GET  .../flowruns/{flowrunId}/status             → Poll until Completed
8. GET  .../flowruns/{flowrunId}/summary            → Get full execution summary
```

### Debug a Failed Actor

```
1. GET  .../flowruns/{flowrunId}/summary             → Find actors with errors
2. GET  .../flowrunJobResults/summaries?flowrunJobId=J → See error details
3. GET  .../flowrunJobs/{jobId}/runtimeData?rootPath=ctx → See what config was used
4. GET  .../flowrunJobs/{jobId}/runtimeData?rootPath=msg → See what input data was received
5. PATCH .../canvases/{canvasId}/actors               → Fix the configuration
6. POST .../flowrunJobs/reRun                         → Re-run with fixed config
```

### Iterate on a Flow Design

```
1. GET  .../canvases/{id}?includeData=true    → Read current flow
2. PATCH .../canvases/{id}/actors              → Modify actors
3. GET  .../canvases/{id}/validate             → Check for errors
4. POST .../canvases/{id}/layout               → Re-layout if needed
5. POST .../triggers/manual                    → Test the change
6. GET  .../flowruns/{id}/status               → Poll until done
7. GET  .../flowruns/{id}/summary              → Check results
8. Repeat 2-7 until satisfied
```

### Duplicate a Flow

```
1. GET  .../canvases/{id}/exportData           → Export the canvas as YAML
2. POST .../canvases/data                      → Create new canvas with exported data
   (use a new name and slug; IDs are regenerated automatically)
```

---

## Error Handling

All error responses follow this format:

```json
{
  "status": 400,
  "message": "Description of the error",
  "details": [
    { "path": ["fieldName"], "message": "Specific field error" }
  ]
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input, missing fields) |
| 401 | Authentication failed (invalid/expired/revoked token) |
| 403 | Authorization failed (missing scopes or membership) |
| 404 | Resource not found |
| 409 | Version conflict (canvas was modified by someone else) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Handling Version Conflicts (409)

When updating canvas data, if you get a 409:

1. Re-read the canvas to get the latest `version`
2. Merge your changes with the current data
3. Retry the update with the new `currentVersion`

The `PATCH .../actors` endpoint handles conflicts more gracefully — conflicting operations are reported in the `conflicts` array rather than failing the entire request.

---

## Tips for AI Agents

1. **Use batch actor operations for edits** — The batch actor operations endpoint (`PATCH .../actors`) is designed for incremental changes and handles conflicts gracefully. Prefer it over replacing the full canvas data.

2. **Validate before executing** — Call `GET .../canvases/{id}/validate` to catch ID format errors, missing configuration, and broken references before triggering a flow.

3. **Use `/status` for polling** — Poll `GET .../flowruns/{id}/status` every 2-3 seconds to wait for completion. It's lightweight (one Redis hash read). Use `/summary` only after completion for the full picture.

4. **Use `publishEmittedMessageToConnectedActors: false`** for testing — When test-running an actor, set this to `false` to avoid triggering the entire downstream flow.

5. **Check job states, not just results** — A job in `Waiting` state isn't failed — it's waiting for an external event. Only `Error` state indicates failure.

6. **Read runtime data for debugging** — The `runtimeData` endpoint shows exactly what an actor received (context, messages, request data). This is the most useful debugging tool.

7. **Export before major changes** — Export the canvas data before making large modifications so you can restore if needed.

8. **Use auto-layout** — After creating or modifying a flow, call `POST .../canvases/{id}/layout` to arrange actors visually. Use `?sourceActorId=X` to layout only a subgraph.

9. **YAML strings in configuration** — Actor configuration fields like `options`, `inputs`, `vars`, and `outputs` are YAML strings (not JSON objects). Serialize your configuration as YAML before sending.

10. **Use the actor schema endpoint** — Call `GET /v1/actors/{actorType}/schema` before configuring an actor to understand its required fields, supported connections, and source ports.
