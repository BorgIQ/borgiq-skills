# CLI Data Formats Reference

This document specifies the exact input and output formats for every BorgIQ CLI command that accepts data.

## Input Formats

The CLI accepts both **JSON** and **YAML** files via `--file`. It auto-detects the format by file extension (`.yaml`/`.yml` for YAML, everything else parsed as JSON). Internally, the CLI always sends `Content-Type: application/json` to the API — YAML files are parsed and converted to JSON before sending.

The `--json` flag controls **output format only** — without it the CLI renders tables for interactive use; with it the CLI outputs machine-readable JSON. It does not affect input parsing.

---

## Master Format Table

### Commands that accept file input

| Command | `--file` | JSON Schema | Config fields format |
|---------|----------|-------------|---------------------|
| `borgiq canvases create-with-data` | Yes | `ExportedCanvasData` envelope | **JSON objects** |
| `borgiq canvases update-data` | Yes | `ExportedCanvasData` in `{ canvas, mode }` wrapper | **JSON objects** |
| `borgiq canvas-actors create` | Yes | `CanvasActorSchema` (without `id`) | **YAML strings** |
| `borgiq canvas-actors update` | Yes | `CanvasActorSchema` partial (without `id`) | **YAML strings** |
| `borgiq canvas-actors batch` | Yes | `{ operations: ActorOperation[] }` | **YAML strings** |
| `borgiq canvas-actors verify` | Yes or stdin | `{ actorType, options, sourcePorts? }` | **YAML string** (`options` only) |
| `borgiq canvases verify-import` | Yes | `{ canvas: "<YAML string>" }` | **YAML string** (entire export) |

### Commands with no file input

| Command | Input | Notes |
|---------|-------|-------|
| `borgiq auth login` | Interactive prompt | User handles authentication |
| `borgiq auth status` | None | |
| `borgiq orgs list` | None | |
| `borgiq workspaces list` | `--org` flag | |
| `borgiq canvases list` | None | |
| `borgiq canvases get` | `<canvasSlugOrId>`, `--include-data` flag | |
| `borgiq canvases create` | `--name`, `--slug`, `--description` flags | |
| `borgiq canvases update` | `<canvasSlugOrId>`, `--name`, `--description` flags | |
| `borgiq canvases export` | `<canvasSlugOrId>` | Returns `{ yaml, errors }` |
| `borgiq canvases validate` | `<canvasSlugOrId>` | |
| `borgiq canvases layout` | `<canvasSlugOrId>`, `--source-actor-id` flag(s) | |
| `borgiq actors list` | None | |
| `borgiq actors schema` | `<actorType>` | |
| `borgiq connections list` | None | |
| `borgiq connections types` | None | |
| `borgiq secrets list` | None | |
| `borgiq assets list` | None | |
| `borgiq templates list` | `--search`, `--type` (repeatable), `--app-id`, `--page`, `--page-size` flags | Returns `{ total, data }` (metadata only — no `actor` payload) |
| `borgiq templates get` | `<templateId>` | Returns full template including `actor` (ExportedCanvasActor) |
| `borgiq templates apps` | `--search`, `--category-id`, `--page`, `--page-size` flags | Use to discover ids for `templates list --app-id` |
| `borgiq canvas-actors list` | `<canvasSlugOrId>`, filter flags | |
| `borgiq canvas-actors get` | `<canvasSlugOrId> <actorId>` | |
| `borgiq canvas-actors flow` | `<canvasSlugOrId> <actorId>` | |
| `borgiq canvas-actors delete` | `<canvasSlugOrId> <actorId>`, `--edit-version` | |
| `borgiq triggers run` | `--canvas`, `--actor-id` flags | |
| `borgiq flowruns status` | `<flowrunId>` | |
| `borgiq flowruns summary` | `<flowrunId>` | |
| `borgiq flowruns interrupt` | `<flowrunId>` | |
| `borgiq flowrun-jobs test-run` | `--canvas`, `--actor-id`, `--publish` flags | |
| `borgiq flowrun-jobs re-run` | `--job-id` flag | |
| `borgiq flowrun-jobs runtime-data` | `<jobId>`, `--root-path` flag | |
| `borgiq flowrun-jobs ai-timeline` | `<jobId>` | |
| `borgiq flowrun-jobs source-message` | `<jobId>` | |
| `borgiq flowrun-results summaries` | `--job-id` flag | |
| `borgiq flowrun-results data` | `<resultId>` | |
| `borgiq flowrun-messages list` | `--canvas`, `--flowrun-id`, `--actor-id` flags | |
| `borgiq flowrun-messages data` | `<messageId>` | |

---

## Common Mistakes

> **CRITICAL: Two JSON schemas, different field types.** The same configuration fields (`options`, `inputs`, `vars`, `outputs`, `credentials`, `error`, `schemas.inputs`, `schemas.outputs`) have **different types** depending on which CLI command you use. Mixing them up causes 400 errors.

| Mistake | What happens | Fix |
|---------|-------------|-----|
| Sending `"options": {"method": "GET"}` (JSON object) to `canvas-actors create` | 400 — expects YAML string | Use `"options": "method: GET"` |
| Sending `"options": "method: GET"` (YAML string) to `canvases create-with-data` | 400 — expects JSON object | Use `"options": {"method": "GET"}` |
| Omitting `options` in `canvas-actors create` body | 400 — `options` is required | Always include `"options": "..."` (can be empty string `""`) |
| Omitting `options` in `create-with-data` body | OK — `options` is optional in ExportedCanvasData | Both `{}` and omitting are valid |
| Omitting `description` | 400 — `description` is required | Always include `"description": "..."` (can be empty string `""`) |
| Omitting `timestamp` in batch operations | 400 — `timestamp` is required | Always include `"timestamp": <epoch_ms>` |
| Using `"id"` in `canvas-actors create` body | Ignored — ID comes from CLI argument | Pass actor ID as CLI arg, omit from JSON body |

---

## Field Type Summary

The same actor configuration fields exist in two different representations depending on which CLI command (and underlying API endpoint) you use.

| Field path | `ExportedCanvasData` format | Required? | `CanvasActor` format | Required? |
|-----------|----------------------------|-----------|---------------------|-----------|
| `configuration.options` | `any` — JSON object | **No** | `string` — YAML string | **Yes** |
| `configuration.inputs` | `any` — JSON object | No | `string` — YAML string | No |
| `configuration.vars` | `any[]` — JSON array | No | `string` — YAML string | No |
| `configuration.outputs` | `any` — JSON object | No | `string` — YAML string | No |
| `configuration.credentials` | `Record<string, { type?, workspaceKey?, source? }>` — JSON object | No | `string` — YAML string | No |
| `configuration.error` | `any` — JSON object | No | `string` — YAML string | No |
| `configuration.code` | `string` — plain string | No | `string` — plain string | No |
| `configuration.connection` | `{ type?: string \| string[], key? }` — JSON object | No | `{ type?: string \| string[], key? }` — JSON object | No |
| `configuration.webhookTriggerKey` | `string` — plain string | No | `string` — plain string | No |
| `configuration.webhookAuthorizationLevel` | `"public"` or `"apps"` | No | `"public"` or `"apps"` | No |
| `configuration.aiAgentToolActorIds` | `string[]` — string array | No | `string[]` — string array | No |
| `schemas.inputs` | `any` — JSON object | No | `string` — YAML string | No |
| `schemas.outputs` | `any` — JSON object | No | `string` — YAML string | No |

**Key difference:** `configuration.options` is **required** in `CanvasActor` format (must be a YAML string, can be `""`) but **optional** in `ExportedCanvasData` format (can be omitted or `{}`).

**When to use which format:**

- **ExportedCanvasData** (config as JSON objects) — used by `canvases create-with-data` and `canvases update-data`. The API converts these JSON objects to YAML strings via `yamlDump()` before storing.
- **CanvasActor** (config as YAML strings) — used by `canvas-actors create`, `canvas-actors update`, and `canvas-actors batch`. The API stores these YAML strings as-is.

---

## ExportedCanvasData Format

Used by: `borgiq canvases create-with-data --file <path>`, `borgiq canvases update-data <id> --file <path>`

Configuration fields are **JSON objects** (the parsed representation).

### create-with-data body

Zod schema: `CanvasCreateWithDataInputSchema` with `ExportedCanvasDataSchema` for actor data.

```jsonc
{
  // --- Canvas metadata ---
  "name": "My API Flow",                    // REQUIRED  string (2-255 chars)
  "slug": "my-api-flow",                    // REQUIRED  string (lowercase, numbers, hyphens)
  "description": "A flow created via CLI",  // optional  string (defaults to "")
  "tags": "api,automated",                  // optional  string (defaults to "")
  "messageTTLInDays": 7,                    // REQUIRED  number (1-14)
  "runtimeSlug": "",                        // optional  string (defaults to "")

  // --- Canvas data ---
  "data": {
    "schemaVersion": "1",                   // REQUIRED  string
    "actors": {

      // ---- Actor 1: ButtonTriggerActor ----
      "ACTR01kd6gqghj04j8765nnqyp09a3": {
        "id": "ACTR01kd6gqghj04j8765nnqyp09a3",  // REQUIRED  ACTR + 26-char ULID
        "type": "ButtonTriggerActor",       // REQUIRED  BIQActorType enum value
        "version": 1,                       // REQUIRED  number
        "name": "Manual Trigger",           // REQUIRED  string
        "msgVar": "manual_trigger",         // REQUIRED  string (JSON-safe identifier)
        "description": "Starts the flow",   // REQUIRED  string (can be "")
        "isActive": true,                   // REQUIRED  boolean
        "continueOnError": false,           // REQUIRED  boolean
        "enableLTM": false,                 // REQUIRED  boolean
        "enableSTM": false,                 // REQUIRED  boolean
        "sourcePorts": [{ "id": "SPRTdefault" }], // REQUIRED  array
        "schemas": {},                      // REQUIRED  object (can be {})
        "position": { "x": 0, "y": 0 },    // REQUIRED  { x: number, y: number }
        "edges": {                          // REQUIRED  object (can be {})
          "EDGE01kd6gqx5k7tvzs86y40w8etms": {
            "id": "EDGE01kd6gqx5k7tvzs86y40w8etms",
            "sourceActorId": "ACTR01kd6gqghj04j8765nnqyp09a3",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        },
        // --- ExportedCanvasData: config fields are JSON OBJECTS ---
        "configuration": {                  // REQUIRED  object
          "options": {}                     // optional  JSON object (can omit entirely)
        }
        // optional fields (omitted = use defaults):
        // "showInWorkspaceApps": true       // defaults to true
        // "template": { "id": "...", "version": 1, "appName": "..." }
        // "icon": { "type": "borgiq", "value": "slack", "category": "logos" }
        // "icon": { "type": "borgiq", "value": "arrow-right", "category": "icons", "colorable": true }
        // "icon": { "type": "svg", "value": "<svg>...</svg>" }
        // "icon": { "type": "url", "value": "https://example.com/icon.svg" }
        // "runtimeSlug": "..."
      },

      // ---- Actor 2: HttpRequestActor ----
      "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl": {
        "id": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
        "type": "HttpRequestActor",
        "version": 1,
        "name": "Fetch Customer Data",
        "msgVar": "fetch_customer_data",
        "description": "Fetches customer data from the API",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "schemas": {
          "inputs": {                       // optional  JSON Schema object
            "type": "object",
            "properties": { "customerId": { "type": "string" } },
            "required": ["customerId"]
          }
        },
        "position": { "x": 0, "y": 200 },
        "edges": {},
        // --- ExportedCanvasData: config fields are JSON OBJECTS ---
        "configuration": {
          "options": {                      // optional  JSON object (actor-type-specific)
            "method": "GET",
            "url": "https://api.example.com/customers/${{ inputs.customerId }}"
          },
          "inputs": {                       // optional  JSON object
            "customerId": "${{ msg.manual_trigger.body.id }}"
          },
          "outputs": "${{ results.body }}", // optional  expression string or JSON object
          "connection": {                   // optional  { type?: string | string[], key? }
            "type": ["api-key", "bearer-token"],
            "key": "example-api"
          }
          // other optional config fields:
          // "vars": [{ "myVar": "${{ ... }}" }]   // JSON array
          // "credentials": { "key": { "workspaceKey": "..." } }
          // "error": { "if": false }
          // "code": "..."                   // for DenoActor/PythonActor
          // "webhookTriggerKey": "..."       // for WebhookTriggerActor
          // "webhookAuthorizationLevel": "public"  // for WebhookTriggerActor
          // "aiAgentToolActorIds": ["ACTR..."]     // for AiAgentActor
        }
      }
    }
  }
}
```

### update-data body

Wraps the canvas data in a `{ canvas, mode }` envelope:

```json
{
  "canvas": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl": {
        "...same ExportedCanvasActor structure as above..."
      }
    }
  },
  "mode": "merge"
}
```

**Import modes:**
- `merge` (default) — add/update actors from import, leave others untouched
- `insert` — generate new IDs for all imported actors (no conflicts possible)
- `replace` — replace entire canvas data with import

---

## CanvasActor Format

Used by: `borgiq canvas-actors create`, `borgiq canvas-actors update`, `borgiq canvas-actors batch`

Configuration fields are **YAML strings within JSON**.

### canvas-actors create body

Zod schema: `CanvasActorSchema.omit({ id: true })` — the actor ID is passed as a CLI argument, not in the body.

```bash
borgiq canvas-actors create <canvasSlugOrId> ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --file actor.json --json
```

```jsonc
{
  // --- Actor base fields (all REQUIRED for create) ---
  "type": "HttpRequestActor",              // REQUIRED  BIQActorType enum value
  "version": 1,                            // REQUIRED  number
  "name": "Fetch Customer Data",           // REQUIRED  string
  "msgVar": "fetch_customer_data",         // REQUIRED  string (JSON-safe identifier)
  "description": "Fetches customer data",  // REQUIRED  string (can be "")
  "isActive": true,                        // REQUIRED  boolean
  "continueOnError": false,                // REQUIRED  boolean
  "enableLTM": false,                      // REQUIRED  boolean
  "enableSTM": false,                      // REQUIRED  boolean
  "sourcePorts": [{ "id": "SPRTdefault" }], // REQUIRED  array
  "schemas": {},                           // REQUIRED  object (can be {})
  "position": { "x": 0, "y": 200 },       // REQUIRED  { x: number, y: number }
  "edges": {},                             // REQUIRED  object (can be {})
  // "showInWorkspaceApps": true,           // optional  defaults to true
  // "template": { ... },                   // optional
  // "icon": { "type": "borgiq", "value": "slack", "category": "logos" },  // optional
  // "runtimeSlug": "...",                   // optional

  // --- CanvasActor: config fields are YAML STRINGS ---
  "configuration": {                       // REQUIRED  object
    "options": "method: GET\nurl: https://api.example.com/customers/${{ inputs.customerId }}",
                                            // REQUIRED  YAML string (can be "")
    "inputs": "customerId: ${{ msg.manual_trigger.body.id }}",
                                            // optional  YAML string
    "outputs": "${{ results.body }}",       // optional  YAML string
    "connection": {                         // optional  { type?: string | string[], key? } (NOT a YAML string)
      "type": ["api-key", "bearer-token"],
      "key": "example-api"
    }
    // other optional config fields:
    // "vars": "- myVar: ${{ ... }}"         // YAML string
    // "credentials": "key:\n  workspaceKey: ..."  // YAML string
    // "error": "if: false"                  // YAML string
    // "code": "const x = 1; ..."            // plain string (DenoActor/PythonActor)
    // "webhookTriggerKey": "01KD298..."      // plain string (WebhookTriggerActor)
    // "webhookAuthorizationLevel": "public"  // enum (WebhookTriggerActor)
    // "aiAgentToolActorIds": ["ACTR..."]     // string array (AiAgentActor)
  },
  "schemas": {                             // REQUIRED  object (can be {})
    "inputs": "type: object\nproperties:\n  customerId:\n    type: string\nrequired:\n  - customerId"
                                            // optional  YAML string (JSON Schema as YAML)
  }
}
```

### canvas-actors update body

Partial update — only include fields you want to change:

```json
{
  "configuration": {
    "options": "method: POST\nurl: https://api.example.com/customers\nbody:\n  name: ${{ inputs.name }}"
  }
}
```

### canvas-actors batch body

Zod schema: `CanvasActorsBatchInputSchema` with `ActorOperationSchema` per operation.

```jsonc
{
  "operations": [
    {
      // --- "add" operation: requires full CanvasActorSchema in data ---
      "type": "add",                       // REQUIRED  "add" | "update" | "remove"
      "actorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl", // REQUIRED  ACTR + 26-char ULID
      "data": {                            // REQUIRED for add  (full CanvasActorSchema)
        "type": "HttpRequestActor",
        "version": 1,
        "name": "Fetch Data",
        "msgVar": "fetch_data",
        "description": "Makes an HTTP request",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": "method: GET\nurl: https://example.com"  // REQUIRED YAML string
        },
        "schemas": {},
        "position": { "x": 0, "y": 200 },
        "edges": {}
      },
      "timestamp": 1712500000000           // REQUIRED  number (epoch milliseconds)
    },
    {
      // --- "update" operation: partial CanvasActorSchema in data ---
      "type": "update",
      "actorId": "ACTR01kd6gqghj04j8765nnqyp09a3",
      "data": {                            // REQUIRED for update  (partial — only changed fields)
        "name": "Updated Actor Name",
        "msgVar": "updated_actor_name",
        "configuration": {
          "options": "method: POST\nurl: https://example.com/update"
        }
      },
      "editVersion": 3,                    // optional  for conflict detection
      "timestamp": 1712500000001           // REQUIRED
    },
    {
      // --- "remove" operation: no data needed ---
      "type": "remove",
      "actorId": "ACTR01kd6gr8m6q9nzp2w4j7h5k6lo",
      "editVersion": 2,                    // optional  for conflict detection
      "timestamp": 1712500000002           // REQUIRED
    }
  ]
}
```

---

## Verify Format

Used by: `borgiq canvas-actors verify <canvasSlugOrId>`

The `options` field is a YAML string:

```json
{
  "actorType": "HttpRequestActor",
  "options": "method: GET\nurl: https://example.com"
}
```

For `RouterActor` and `AiRouterActor`, include `sourcePorts`:

```json
{
  "actorType": "RouterActor",
  "options": "emitType: singleRoute\nconditions:\n  Active: ${{ msg.trigger.body.status === 'active' }}",
  "sourcePorts": [
    { "id": "SPRTabcdefg", "name": "Active" },
    { "id": "SPRTdefault", "name": "F" }
  ]
}
```

---

## Verify-Import Format

Used by: `borgiq canvases verify-import --file <path>`

The `canvas` field is a single YAML string containing the entire canvas export:

```json
{
  "canvas": "metadata:\n  schemaVersion: v1.0\n  source: BIQCanvas\nactors:\n  ACTR01kd6gqghj04j8765nnqyp09a3:\n    type: ButtonTriggerActor\n    ..."
}
```

---

## Export Format

The `borgiq canvases export <canvasSlugOrId>` command returns JSON with a `yaml` field containing the entire canvas as a YAML string, and an `errors` array:

```json
{
  "yaml": "metadata:\n  id: CANV01abc123def456ghi789jkl012\n  slug: my-flow\n  name: My Flow\n  description: ''\n  tags: ''\n  imagePath: null\n  messageTTLInDays: 7\n  runtimeSlug: ''\ndata:\n  schemaVersion: '1'\n  actors:\n    ACTR01kd6gqghj04j8765nnqyp09a3:\n      type: ButtonTriggerActor\n      ...",
  "errors": []
}
```

The YAML inside the `yaml` field uses the **ExportedCanvasData** format — configuration fields are parsed objects (not YAML strings). The `metadata` section includes canvas metadata (`id`, `slug`, `name`, etc.) and the `data` section contains the actor graph.

To re-import an exported canvas:

```bash
# Export and pipe directly to create a duplicate
borgiq canvases export CANV01abc123def456ghi789jkl012 | \
  jq '{ name: "Copy of Flow", slug: "copy-of-flow", messageTTLInDays: 7, data: (.yaml | fromjson).data }' | \
  borgiq canvases create-with-data --json
```

---

## Actor Common Fields Reference

Every actor (in both formats) has these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes (except in `canvas-actors create` — passed as CLI arg) | `ACTR` + 26-char ULID |
| `type` | string | Yes | Actor type enum (e.g., `HttpRequestActor`) |
| `version` | number | Yes | Runtime version (typically `1`) |
| `name` | string | Yes | Display name |
| `msgVar` | string | Yes | JSON-safe variable name for message references |
| `description` | string | Yes | UI description (can be `""`) |
| `isActive` | boolean | Yes | Whether the actor receives/emits messages |
| `continueOnError` | boolean | Yes | Emit error message on failure instead of stopping |
| `enableLTM` | boolean | Yes | Long-term memory (canvas-scoped, one-at-a-time across flowruns) |
| `enableSTM` | boolean | Yes | Short-term memory (flowrun-scoped, one-at-a-time within flowrun) |
| `sourcePorts` | array | Yes | Output ports (see below) |
| `configuration` | object | Yes | Actor-specific configuration (format varies by endpoint — see above) |
| `schemas` | object | Yes | Custom JSON schemas for inputs/outputs (can be `{}`) |
| `position` | `{ x, y }` | Yes | UI coordinates |
| `edges` | object | Yes | Outgoing connections (can be `{}`) |
| `showInWorkspaceApps` | boolean | No (defaults to `true`) | Whether actor appears in workspace apps listing |
| `template` | object | No | Template reference: `{ id, version, appName }` |
| `icon` | object | No | Custom icon: `{ type: "borgiq"\|"svg"\|"url", value, category?, color?, colorable? }`. See [Icon Configuration](#icon-configuration) below. |
| `runtimeSlug` | string | No | Override runtime for this actor |

### Icon Configuration

The `icon` field supports three types:

**1. CDN-hosted icon (`type: "borgiq"`)** — Recommended for standard brand/UI icons:

```json
{ "type": "borgiq", "value": "slack", "category": "logos" }
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"borgiq"` |
| `value` | Yes | Icon slug from the CDN manifest |
| `category` | Yes for borgiq | `"logos"` (brand logos, 4 variants) or `"icons"` (monochrome UI icons, single file) |
| `color` | No | Hex color override without `#` (e.g., `"FF5733"`). Applied via CDN `?color=` param. |
| `colorable` | No | `true` if the icon supports color rewriting (monochrome SVGs) |

CDN URL structure:
- Logos: `https://icons.borgiqassets.com/v1/logos/{slug}/icon-{light|dark}.svg`
- Icons: `https://icons.borgiqassets.com/v1/icons/{slug}.svg`
- Manifest: `https://icons.borgiqassets.com/v1/manifest.json`

Examples:
```json
{ "type": "borgiq", "value": "slack", "category": "logos" }
{ "type": "borgiq", "value": "arrow-right", "category": "icons", "colorable": true }
{ "type": "borgiq", "value": "brand-github", "category": "logos", "colorable": true }
{ "type": "borgiq", "value": "AiActor", "category": "icons", "colorable": true, "color": "504C97" }
```

**2. Raw SVG (`type: "svg"`)** — For custom inline SVGs:

```json
{ "type": "svg", "value": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\">...</svg>" }
```

**3. External URL (`type: "url"`)** — For externally hosted images:

```json
{ "type": "url", "value": "https://example.com/my-icon.svg" }
```

### Source Ports

Most actors use a single default port:

```json
"sourcePorts": [{ "id": "SPRTdefault" }]
```

Actors with multiple ports:

| Actor Type | Ports |
|-----------|-------|
| `RouterActor`, `AiRouterActor` | Custom `SPRTxxxxxxx` ports + `SPRTdefault` (fallback) |
| `AgentHarnessActor`, `AiAgentActor` | `SPRTdone000` (Done) + `SPRTdefault` (Status) |
| `InterfaceActor` | `SPRTevent00` (Event) + `SPRTdefault` (Meta) |
| `AppTriggerActor`, `CommentActor` | No ports (`[]`) |

### Edge Structure

```json
{
  "EDGE01kd6gqx5k7tvzs86y40w8etms": {
    "id": "EDGE01kd6gqx5k7tvzs86y40w8etms",
    "sourceActorId": "ACTR01kd6gqghj04j8765nnqyp09a3",
    "sourcePortId": "SPRTdefault",
    "targetActorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
    "targetPortId": "TPRTdefault",
    "type": "borgiqEdge"
  }
}
```

### ID Format Reference

| Entity | Prefix | Total Length | Character Set |
|--------|--------|-------------|---------------|
| Actor | `ACTR` | 30 | `0-9, a-h, j-k, m-n, p, q, r-t, v-z` (ULID, excludes i, l, o, u) |
| Edge | `EDGE` | 30 | Same ULID charset |
| Source Port | `SPRT` | 11 | Full `a-z, 0-9` |
| Canvas | `CANV` | 30 | Same ULID charset |

Generate IDs using the `borgiq generate` command:

```bash
borgiq generate id actor       # ACTR01kcsnjnkqa69w50qr60dcd06e
borgiq generate id edge        # EDGE01kd6gqx5k7tvzs86y40w8etms
borgiq generate id sourceport  # SPRTabcdefg
borgiq generate msgvar "Fetch user profile"  # fetch_user_profile
```
