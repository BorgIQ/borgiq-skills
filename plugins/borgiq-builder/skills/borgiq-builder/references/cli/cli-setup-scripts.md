# CLI Scaffolding Scripts

## Overview

Two paths produce the JSON files the BorgIQ CLI consumes:

- **Built-in CLI commands** — `borgiq scaffold canvas` and `borgiq scaffold actor-from-template` are part of the verified `@borgiq/cli`. Prefer these.
- **Shell helpers** — `scaffold-canvas.sh`, `scaffold-actor.sh`, and `scaffold-batch.sh` compose actors/operations the built-in commands don't yet cover (per-type actor scaffolding and multi-op batches). They mint IDs by calling `borgiq generate`, so they depend only on the same verified CLI.

They exist because:

1. The CLI only accepts JSON input (not YAML), and building correct JSON by hand is error-prone.
2. Two different JSON schemas exist -- ExportedCanvasData (config fields as JSON objects) and CanvasActor (config fields as YAML strings within JSON) -- and each helper produces the right format for its target command.
3. Actor IDs, edge IDs, and source port IDs must follow specific formats (ACTR + 26-char ULID, EDGE + 26-char ULID, SPRT + 7-char alphanumeric). The helpers call `borgiq generate id` to produce valid IDs.

| Helper | Output format | Target CLI command |
|--------|--------------|-------------------|
| `borgiq scaffold canvas` | ExportedCanvasData | `borgiq canvases create-with-data` |
| `scaffold-canvas.sh` | ExportedCanvasData | `borgiq canvases create-with-data` |
| `scaffold-actor.sh` | CanvasActor | `borgiq canvas-actors create` |
| `scaffold-batch.sh` | CanvasActor (in operations array) | `borgiq canvas-actors batch` |
| `borgiq scaffold actor-from-template` | CanvasActor (or batch envelope) | `borgiq canvas-actors create` / `batch` (from a `borgiq templates get` payload) |

---

## Prerequisites

The `@borgiq/cli` must be installed and on your `PATH`:

```bash
npm install -g @borgiq/cli
borgiq --version
```

That's the only dependency. `borgiq scaffold` and `borgiq generate` are **offline** commands — no API token and no `npm install` of script dependencies. The shell helpers shell out to `borgiq generate id` / `borgiq generate msgvar`, so they work as soon as the CLI is installed.

---

## scaffold-canvas.sh

Generates a complete canvas JSON file in **ExportedCanvasData** format (config fields are JSON objects). The output is ready for `borgiq canvases create-with-data --file`.

### Usage

```bash
./scripts/scaffold-canvas.sh --name <name> --slug <slug> [options]
```

### Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name <name>` | Yes | -- | Canvas display name |
| `--slug <slug>` | Yes | -- | URL-safe canvas slug (lowercase-hyphenated) |
| `--description <desc>` | No | `""` | Canvas description |
| `--template <template>` | No | `button-http` | Template to use (see below) |
| `--ttl <days>` | No | `7` | Message TTL in days (1-14) |
| `--output <path>` | No | stdout | Write JSON to file instead of stdout |

### Templates

**button-http** (default) -- ButtonTriggerActor -> HttpRequestActor

A manual trigger that fires an HTTP GET request.

**webhook-router** -- WebhookTriggerActor -> RouterActor -> 2x WebhookResponseActor

An incoming webhook that routes by condition to a 200 success or 400 error response. Generates a `webhookTriggerKey`, a custom source port for the "Success" route, and three edges.

**button-deno** -- ButtonTriggerActor -> DenoActor

A manual trigger that runs custom TypeScript code. The DenoActor includes a starter `configuration.codeDir` holding its `main.ts` entrypoint, with inputs/outputs wired up. Add further files to that array as the actor grows -- see [deno-actor.md](../deno-actor.md#code-files).

### Examples

Generate a button-http canvas to stdout:

```bash
./scripts/scaffold-canvas.sh --name "Customer Lookup" --slug customer-lookup
```

Generate a webhook-router canvas and save to file:

```bash
./scripts/scaffold-canvas.sh \
  --name "Webhook Handler" \
  --slug webhook-handler \
  --template webhook-router \
  --output outputs/webhook-handler.json
```

Deploy the generated file:

```bash
borgiq canvases create-with-data --file outputs/webhook-handler.json --json
```

Generate a button-deno canvas with a description:

```bash
./scripts/scaffold-canvas.sh \
  --name "Data Processor" \
  --slug data-processor \
  --template button-deno \
  --description "Processes incoming data with custom TypeScript"
```

Sample output (button-http, IDs will differ on each run):

```json
{
  "name": "Customer Lookup",
  "slug": "customer-lookup",
  "description": "",
  "messageTTLInDays": 7,
  "runtimeSlug": "",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01jt8r2xq5m3nk7vf0w9hb4p6c": {
        "id": "ACTR01jt8r2xq5m3nk7vf0w9hb4p6c",
        "type": "ButtonTriggerActor",
        "version": 1,
        "name": "Manual Trigger",
        "msgVar": "manual_trigger",
        "description": "Click to start the flow",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": { "options": {} },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {
          "EDGE01jt8r2xr7d9km4w1y5gc3s8ne": {
            "id": "EDGE01jt8r2xr7d9km4w1y5gc3s8ne",
            "sourceActorId": "ACTR01jt8r2xq5m3nk7vf0w9hb4p6c",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "ACTR01jt8r2xp4z6bh8jq2v3ek9n0f",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        }
      },
      "ACTR01jt8r2xp4z6bh8jq2v3ek9n0f": {
        "id": "ACTR01jt8r2xp4z6bh8jq2v3ek9n0f",
        "type": "HttpRequestActor",
        "version": 1,
        "name": "HTTP Request",
        "msgVar": "http_request",
        "description": "Makes an HTTP request",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": { "method": "GET", "url": "https://example.com" },
          "outputs": "${{ results.body }}"
        },
        "schemas": {},
        "position": { "x": 0, "y": 200 },
        "edges": {}
      }
    }
  }
}
```

---

## scaffold-actor.sh

Generates a single actor JSON file in **CanvasActor** format (config fields are YAML strings within JSON). The output is ready for `borgiq canvas-actors create`.

### Usage

```bash
./scripts/scaffold-actor.sh --type <ActorType> --name <name> [options]
```

### Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--type <type>` | Yes | -- | Actor type (e.g., `HttpRequestActor`, `DenoActor`) |
| `--name <name>` | Yes | -- | Actor display name |
| `--routes <routes>` | No | -- | Comma-separated route names (RouterActor/AiRouterActor only) |
| `--output <path>` | No | stdout | Write JSON to file instead of stdout |

The script prints the generated actor ID to stderr for use in the CLI command.

### Supported Actor Types

The script generates type-appropriate default configuration for these actor types:

| Actor type | Default options (YAML string) |
|-----------|-------------------------------|
| `HttpRequestActor` | `method: GET\nurl: https://example.com` |
| `DenoActor`, `DenoTestActor` | Empty options, plus a starter `configuration.codeDir` with the `main.ts` entrypoint |
| `UniversalTriggerActor` | Empty options, plus a starter `configuration.codeDir` with the `main.ts` entrypoint (typed `TriggerRequest`) |
| `PythonActor` | Empty options, plus a starter `configuration.codeDir` with the `main.py` entrypoint |
| `AiActor` | Model, maxTokens, systemPrompt, prompt |
| `AiAgentActor` | Model, systemPrompt, prompt (see [ai-agent-actor.md](../ai-agent-actor.md) for sessionId, timeoutInMinutes, tool filters, etc.) |
| `RouterActor` | emitType, conditions (from `--routes` or default) |
| `AiRouterActor` | Model, prompt |
| `WebhookTriggerActor` | allowedMethods, respondImmediately, emitRawBody + generated webhookTriggerKey |
| `WebhookResponseActor` | statusCode: 200, body, headers |
| `SendEmailActor` | Empty to, subject, body |
| `DataStoreActor` | scope: canvas, action: set |
| `CollectionActor` | action: putItem, collectionName |
| `StreamActor` | action: appendData, stream, one record |
| `CallFlowActor` | Empty canvasId, actorId |
| `ButtonTriggerActor`, `ScheduledTriggerActor`, `EmailTriggerActor`, `CallableTriggerActor`, `InterfaceTriggerActor`, `CallableResponseActor` | Empty options |

For any type not listed, the script produces empty options.

Source ports are set automatically:
- `RouterActor`/`AiRouterActor` -- custom ports from `--routes` + `SPRTdefault` (fallback "F")
- `AgentHarnessActor`/`AiAgentActor` -- `SPRTdone000` (Done) + `SPRTdefault` (Status)
- `InterfaceActor` -- `SPRTevent00` (Event) + `SPRTdefault` (Meta)
- `AppTriggerActor`/`CommentActor` -- empty array
- All others -- `SPRTdefault`

### Examples

Generate an HttpRequestActor:

```bash
./scripts/scaffold-actor.sh --type HttpRequestActor --name "Fetch Users"
```

Stderr output:

```
Actor ID: ACTR01jt8r3kp7m2nq5vz0w9hb4x6c
```

Stdout output:

```json
{
  "type": "HttpRequestActor",
  "version": 1,
  "name": "Fetch Users",
  "msgVar": "fetch_users",
  "description": "",
  "isActive": true,
  "continueOnError": false,
  "enableLTM": false,
  "enableSTM": false,
  "sourcePorts": [{ "id": "SPRTdefault" }],
  "configuration": {
    "options": "method: GET\nurl: https://example.com"
  },
  "schemas": {},
  "position": { "x": 0, "y": 0 },
  "edges": {}
}
```

Use the actor ID from stderr in the CLI command:

```bash
./scripts/scaffold-actor.sh --type HttpRequestActor --name "Fetch Users" --output actor.json
# Stderr: Actor ID: ACTR01jt8r3kp7m2nq5vz0w9hb4x6c

borgiq canvas-actors create CANV01mycanvasid ACTR01jt8r3kp7m2nq5vz0w9hb4x6c --file actor.json --json
```

Generate a RouterActor with named routes:

```bash
./scripts/scaffold-actor.sh --type RouterActor --name "Route by Status" --routes "Active,Inactive"
```

This generates custom source ports for each route plus the default fallback:

```json
{
  "type": "RouterActor",
  "version": 1,
  "name": "Route by Status",
  "msgVar": "route_by_status",
  "sourcePorts": [
    { "id": "SPRTa3k9m2x", "name": "Active" },
    { "id": "SPRTb7n4q5z", "name": "Inactive" },
    { "id": "SPRTdefault", "name": "F" }
  ],
  "configuration": {
    "options": "emitType: singleRoute\nconditions:\n  Active: ${{ true }}\n  Inactive: ${{ true }}"
  },
  "..."
}
```

Generate a WebhookTriggerActor (auto-generates webhookTriggerKey):

```bash
./scripts/scaffold-actor.sh --type WebhookTriggerActor --name "Incoming Webhook"
```

---

## scaffold-batch.sh

Generates a batch operations JSON file for `borgiq canvas-actors batch`. Supports `add`, `update`, and `remove` operations in a single file.

### Usage

```bash
./scripts/scaffold-batch.sh [operations...] [--output <path>]
```

### Flags

| Flag | Repeatable | Description |
|------|-----------|-------------|
| `--add <Type:Name>` | Yes | Add a new actor. Format: `ActorType:ActorName` |
| `--update <ActorId:field=value>` | Yes | Update a field on an existing actor. Format: `ACTR01...:fieldName=newValue` |
| `--remove <ActorId>` | Yes | Remove an existing actor by ID |
| `--output <path>` | No | Write JSON to file instead of stdout |

At least one operation is required. Operations are logged to stderr with their generated/referenced actor IDs.

### Operation Types

**add** -- Creates a new actor with a generated ID. Uses the CanvasActor format (YAML strings). Default options are generated based on actor type (HttpRequestActor gets `method: GET`, others get empty options). A timestamp is auto-generated.

**update** -- Partial update to an existing actor. Specify the actor ID and a single `field=value` pair. Sets `editVersion: 1` (update this in the output if the actor has been modified since creation).

**remove** -- Removes an actor by ID. Sets `editVersion: 1` (same caveat as update).

### Examples

Add two actors in one batch:

```bash
./scripts/scaffold-batch.sh \
  --add "HttpRequestActor:Fetch Users" \
  --add "DenoActor:Transform Data"
```

Stderr output:

```
Add: HttpRequestActor 'Fetch Users' -> ACTR01jt8r4np5m2qk7vz0w9hb3x6c
Add: DenoActor 'Transform Data' -> ACTR01jt8r4nq8d3bh4jq2v6ek9n0f
```

Stdout output:

```json
{
  "operations": [
    {
      "type": "add",
      "actorId": "ACTR01jt8r4np5m2qk7vz0w9hb3x6c",
      "data": {
        "type": "HttpRequestActor",
        "version": 1,
        "name": "Fetch Users",
        "msgVar": "fetch_users",
        "description": "",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": "method: GET\nurl: https://example.com"
        },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {}
      },
      "timestamp": 1712500000000
    },
    {
      "type": "add",
      "actorId": "ACTR01jt8r4nq8d3bh4jq2v6ek9n0f",
      "data": {
        "type": "DenoActor",
        "version": 1,
        "name": "Transform Data",
        "msgVar": "transform_data",
        "description": "",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": {
          "options": ""
        },
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {}
      },
      "timestamp": 1712500000001
    }
  ]
}
```

Mix add, update, and remove operations:

```bash
./scripts/scaffold-batch.sh \
  --add "HttpRequestActor:New Step" \
  --update "ACTR01existing00000000000000:name=Renamed Step" \
  --remove "ACTR01oldactor000000000000000" \
  --output batch.json

borgiq canvas-actors batch CANV01mycanvasid --file batch.json --json
```

---

## Scaffold a canvas (`borgiq scaffold canvas`)

The built-in CLI command. Produces the same **ExportedCanvasData** format as `scaffold-canvas.sh` but ships inside the verified `@borgiq/cli` and supports two additional templates. Prefer this over `scaffold-canvas.sh` for single-canvas scaffolding.

### Usage

```bash
borgiq scaffold canvas --name <name> --slug <slug> [options]
```

### Flags

Same as `scaffold-canvas.sh`:

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name <name>` | Yes | -- | Canvas display name |
| `--slug <slug>` | Yes | -- | URL-safe canvas slug |
| `--description <desc>` | No | `""` | Canvas description |
| `--template <template>` | No | `button-http` | Template to use |
| `--ttl <days>` | No | `7` | Message TTL in days |
| `--output <path>` | No | stdout | Write JSON to file instead of stdout |

### Templates

All three shell templates plus two additional ones:

| Template | Flow | Notes |
|----------|------|-------|
| `button-http` | ButtonTrigger -> HttpRequest | Same as shell version |
| `webhook-router` | WebhookTrigger -> Router -> 2x WebhookResponse | Same as shell version |
| `button-deno` | ButtonTrigger -> DenoActor | Same as shell version |
| `scheduled-http` | ScheduledTrigger -> HttpRequest | Cron-based health check pattern |
| `button-ai` | ButtonTrigger -> AiActor | Uses claude-sonnet-4-5-20250514, wires prompt input |

### Differences from scaffold-canvas.sh

1. **Two additional templates** -- `scheduled-http` and `button-ai` are only available via `borgiq scaffold canvas`.
2. **No shell wrapper needed** -- It's a first-class CLI command, so there's nothing to locate or `chmod`.
3. **Automatic router port resolution** -- Router source ports resolve to generated `SPRT` IDs at build time; the shell version wires these manually.
4. **Automatic webhookTriggerKey** -- WebhookTriggerActor templates get a generated key without explicit configuration.

### Examples

Generate a scheduled-http canvas:

```bash
borgiq scaffold canvas \
  --name "Health Check" \
  --slug health-check \
  --template scheduled-http \
  --output outputs/health-check.json
```

Generate a button-ai canvas and deploy it:

```bash
borgiq scaffold canvas \
  --name "AI Assistant" \
  --slug ai-assistant \
  --template button-ai \
  --output outputs/ai-assistant.json

borgiq canvases create-with-data --file outputs/ai-assistant.json --json
```

Sample output (button-ai):

```json
{
  "name": "AI Assistant",
  "slug": "ai-assistant",
  "description": "",
  "messageTTLInDays": 7,
  "runtimeSlug": "",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01jt8r5xq5m3nk7vf0w9hb4p6c": {
        "id": "ACTR01jt8r5xq5m3nk7vf0w9hb4p6c",
        "type": "ButtonTriggerActor",
        "name": "Manual Trigger",
        "msgVar": "manual_trigger",
        "configuration": { "options": {} },
        "edges": {
          "EDGE01jt8r5xr7d9km4w1y5gc3s8ne": {
            "sourceActorId": "ACTR01jt8r5xq5m3nk7vf0w9hb4p6c",
            "sourcePortId": "SPRTdefault",
            "targetActorId": "ACTR01jt8r5xp4z6bh8jq2v3ek9n0f",
            "targetPortId": "TPRTdefault",
            "type": "borgiqEdge"
          }
        },
        "..."
      },
      "ACTR01jt8r5xp4z6bh8jq2v3ek9n0f": {
        "id": "ACTR01jt8r5xp4z6bh8jq2v3ek9n0f",
        "type": "AiActor",
        "name": "AI Response",
        "msgVar": "ai_response",
        "configuration": {
          "options": {
            "model": "claude-sonnet-4-5-20250514",
            "maxTokens": 4096,
            "systemPrompt": "You are a helpful assistant.",
            "prompt": "${{ inputs.prompt }}"
          },
          "inputs": { "prompt": "${{ msg.manual_trigger.body.prompt }}" },
          "outputs": "${{ results.content }}"
        },
        "edges": {},
        "..."
      }
    }
  }
}
```

---

## Convert a template to an actor (`borgiq scaffold actor-from-template`)

Converts a published BorgIQ template (returned by `borgiq templates get`) into a CanvasActor body ready for `borgiq canvas-actors create` or `borgiq canvas-actors batch`. Use this instead of hand-building an actor when a template already does what you need — search the catalog, fetch the one you want, run it through this command, and create.

The conversion mirrors the platform's `importActor()` routine (the same conversion the web editor applies when a template is dragged onto a canvas). Specifically it:

- Stringifies `configuration.{credentials, inputs, vars, options, outputs, error}` and `schemas.{inputs, outputs}` from native objects (ExportedCanvasActor) to YAML strings inside JSON (CanvasActor).
- Generates a fresh actor id (the template's `actor.id` is the author's, not yours).
- Generates a `webhookTriggerKey` ULID for `WebhookTriggerActor` and `UniversalTriggerActor`.
- Stamps `template: { id, version, appName }` provenance so the UI can show the template badge and detect out-of-date instances.
- Clears the template's internal `edges` — the new canvas owns edges.

### Usage

```bash
# stdin → stdout (default)
borgiq templates get TMPL01... --json \
  | borgiq scaffold actor-from-template > actor.json

# Explicit file in/out
borgiq scaffold actor-from-template \
  --file template.json --output actor.json
```

### Flags

| Flag | Description |
|------|-------------|
| `--file <path>` | Read template JSON from path (default: stdin) |
| `--output <path>` | Write result to path (default: stdout) |
| `--actor-id <id>` | Use this id instead of generating a new one |
| `--name <name>` | Override actor name (default: template's `actor.name`) |
| `--msg-var <var>` | Override msgVar (default: derived from name) |
| `--description <text>` | Override description |
| `--position-x <n>` / `--position-y <n>` | Override canvas position (default: template's position or `0,0`) |
| `--batch` | Wrap as a single-op `canvas-actors batch` body (includes id in `data`) |
| `--include-id` | Include `id` in the actor body (useful when piping into custom tooling) |
| `--print-id` / `--no-print-id` | Echo the new actor id to stderr (default: on when `--output` is set) |

### End-to-end: search, fetch, convert, deploy

```bash
# 1. Find a template
borgiq --json templates list --search "send slack" --type TASK \
  | jq '.data[] | {id, name, appName}'

# 2. Pull the full payload and convert it in one pipe
ACTOR_ID=$(borgiq templates get TMPL01kd6gqghj04j8765nnqyp09a --json \
  | borgiq scaffold actor-from-template \
      --name "Notify #ops on deploy" \
      --output outputs/notify-ops-actor.json \
      --print-id 2>&1 >/dev/null)

# 3. Create the actor in the canvas
borgiq canvas-actors create CANV01... "$ACTOR_ID" \
  --file outputs/notify-ops-actor.json --json
```

### Batch mode

For a single template + batch endpoint:

```bash
borgiq templates get TMPL01... --json \
  | borgiq scaffold actor-from-template --batch \
  | borgiq canvas-actors batch CANV01... --file - --json
```

The batch envelope looks like:

```json
{
  "operations": [
    {
      "type": "add",
      "actorId": "ACTR01...",
      "timestamp": 1712500000000,
      "data": { "/* CanvasActor body with id and YAML-string config fields */": "" }
    }
  ]
}
```

For multi-template batches, run the command per template (with `--include-id`) and merge the operation entries with `jq`.

### What the command does **not** do

- Doesn't apply user-specific overrides like setting a real `credentials[*].workspaceKey`, picking a target channel, or filling `inputs` defaults. The output is a faithful instance of the template — you (or the caller) still need to wire it to workspace-specific connections, secrets, and `inputs` values via `canvas-actors update`.
- Doesn't create edges. The template ships as a single actor; connect it to upstream/downstream actors in a separate `canvas-actors batch` op or via the editor.
- Doesn't deduplicate `msgVar`. If you're inserting into a canvas that already has an actor with the same derived `msgVar`, pass `--msg-var` explicitly.

---

## Which Helper to Use

| I want to... | Helper | CLI command |
|--------------|--------|-------------|
| Create a new canvas with actors and edges | `borgiq scaffold canvas` (or `scaffold-canvas.sh`) | `borgiq canvases create-with-data --file <output> --json` |
| Create a canvas using scheduled-http or button-ai template | `borgiq scaffold canvas` | `borgiq canvases create-with-data --file <output> --json` |
| Add a single actor to an existing canvas | `scaffold-actor.sh` | `borgiq canvas-actors create <canvasSlugOrId> <actorId> --file <output> --json` |
| Add, update, or remove multiple actors at once | `scaffold-batch.sh` | `borgiq canvas-actors batch <canvasSlugOrId> --file <output> --json` |
| Instantiate a published template as a CanvasActor | `borgiq scaffold actor-from-template` | `borgiq canvas-actors create` (or `batch` with `--batch`) |
| Update an existing canvas's full data | `borgiq scaffold canvas` (edit the output) | `borgiq canvases update-data <canvasSlugOrId> --file <output> --json` |

Key distinction: `borgiq scaffold canvas` / `scaffold-canvas.sh` produce **ExportedCanvasData** format (config as JSON objects), while `scaffold-actor.sh`, `scaffold-batch.sh`, and `borgiq scaffold actor-from-template` produce **CanvasActor** format (config as YAML strings in JSON). These formats are not interchangeable -- see [cli-data-formats.md](cli-data-formats.md) for details.
