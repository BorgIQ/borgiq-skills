# CLI Command Reference

Complete reference for every BorgIQ CLI command with examples, flags, and expected output.

All `--file` inputs must be valid JSON (not YAML). The `--json` flag controls **output** format (table vs JSON), not input. See [cli-data-formats.md](cli-data-formats.md) for detailed input schema documentation, required/optional field annotations, and common mistakes.

> **Two different JSON schemas exist for actor data:**
> - `canvases create-with-data` / `update-data` — config fields are **JSON objects** (ExportedCanvasData format)
> - `canvas-actors create` / `update` / `batch` — config fields are **YAML strings** within JSON (CanvasActor format)
>
> Mixing these up causes 400 errors. See the [Common Mistakes](cli-data-formats.md#common-mistakes) table.

---

## Auth Commands

### `borgiq auth login`

Authenticate the CLI with your BorgIQ account. Opens a browser for login or prompts for an API token.

```bash
borgiq auth login
```

The token is stored in `~/.config/borgiq/config.json` with owner-only permissions. The AI agent should never handle tokens directly.

### `borgiq auth status`

Check if the CLI is authenticated and show the current user.

```bash
borgiq auth status
```

**Output (success):**
```
Authenticated as john@example.com
Organization: acme-corp
Workspace: production
```

**Output (failure):**
```
Error: Not logged in. Run `borgiq auth login` to authenticate.
```

---

## Organization & Workspace Commands

### `borgiq orgs list`

List all organizations you have access to.

```bash
borgiq orgs list --json
```

**Output:**
```json
{
  "data": [
    { "id": "ORG01kd6gqghj04j8765nnqyp09a", "name": "Acme Corp", "slug": "acme-corp" },
    { "id": "ORG01kd6gr3vjxm2rs0k8s3fjq4n", "name": "Dev Team", "slug": "dev-team" }
  ]
}
```

### `borgiq workspaces list`

List workspaces in an organization.

```bash
borgiq workspaces list --org acme-corp --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--org <slug>` | Organization slug or ID (required) |

**Output:**
```json
{
  "total": 2,
  "data": [
    { "id": "WKSP01kd6gqghj04j8765nnqyp09", "name": "Production", "slug": "production", "description": "" },
    { "id": "WKSP01kd6gr3vjxm2rs0k8s3fjq4n", "name": "Staging", "slug": "staging", "description": "" }
  ]
}
```

---

## Canvas Commands

### `borgiq canvases list`

List all canvases in the current workspace.

```bash
borgiq canvases list --json
```

**Output:**
```json
{
  "total": 3,
  "data": [
    {
      "id": "CANV01kd6gqghj04j8765nnqyp09a3",
      "name": "Customer Onboarding",
      "slug": "customer-onboarding",
      "description": "Handles new customer signups",
      "createdAt": "2026-03-15T10:00:00.000Z",
      "updatedAt": "2026-04-01T14:30:00.000Z"
    }
  ]
}
```

### `borgiq canvases get`

Get a canvas by ID, optionally including the full actor graph.

```bash
# Metadata only
borgiq canvases get CANV01kd6gqghj04j8765nnqyp09a3 --json

# With full flow data (actors, edges, configuration)
borgiq canvases get CANV01kd6gqghj04j8765nnqyp09a3 --include-data --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--include-data` | Include the full actor graph in the response |

**Output (with `--include-data`):**
```json
{
  "id": "CANV01kd6gqghj04j8765nnqyp09a3",
  "name": "Customer Onboarding",
  "slug": "customer-onboarding",
  "data": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01kd6gqghj04j8765nnqyp09a3": {
        "id": "ACTR01kd6gqghj04j8765nnqyp09a3",
        "type": "ButtonTriggerActor",
        "name": "Manual Trigger",
        "msgVar": "manual_trigger",
        "configuration": {
          "options": ""
        },
        "...": "..."
      }
    }
  }
}
```

### `borgiq canvases create`

Create an empty canvas (no actors).

```bash
borgiq canvases create --name "Email Processor" --slug email-processor --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--name <name>` | Canvas name (2-255 chars) |
| `--slug <slug>` | URL slug (lowercase, numbers, hyphens) |
| `--description <desc>` | Optional description |

**Output:**
```json
{
  "id": "CANV01kd6gr3vjxm2rs0k8s3fjq4nl",
  "name": "Email Processor",
  "slug": "email-processor",
  "version": 1,
  "createdAt": "2026-04-07T12:00:00.000Z"
}
```

### `borgiq canvases create-with-data`

Create a canvas with a full actor graph in one shot.

**Input format:** JSON file in **ExportedCanvasData** format (config fields as JSON objects). See [cli-data-formats.md](cli-data-formats.md#exportedcanvasdata-format).

```bash
# From file
borgiq canvases create-with-data --file outputs/my-flow.json --json

# From stdin
cat outputs/my-flow.json | borgiq canvases create-with-data --json

# Using the scaffold script
./references/cli/scripts/scaffold-canvas.sh \
  --name "API Monitor" --slug api-monitor --template button-http \
  --output outputs/api-monitor.json
borgiq canvases create-with-data --file outputs/api-monitor.json --json
```

**Example input file (`outputs/my-flow.json`):**

Schema: `ExportedCanvasData` — config fields are **JSON objects** (not YAML strings).

```jsonc
{
  "name": "API Monitor",                   // REQUIRED
  "slug": "api-monitor",                   // REQUIRED
  "description": "Monitors API health",    // optional (defaults to "")
  "messageTTLInDays": 7,                   // REQUIRED (1-14)
  "data": {
    "schemaVersion": "1",                  // REQUIRED
    "actors": {
      "ACTR01kd6gqghj04j8765nnqyp09a3": {
        "id": "ACTR01kd6gqghj04j8765nnqyp09a3",
        "type": "ButtonTriggerActor",      // all base fields REQUIRED
        "version": 1,
        "name": "Manual Trigger",
        "msgVar": "manual_trigger",
        "description": "",
        "isActive": true,
        "continueOnError": false,
        "enableLTM": false,
        "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }],
        "configuration": { "options": {} },  // options is optional here (JSON object)
        "schemas": {},
        "position": { "x": 0, "y": 0 },
        "edges": {}
      }
    }
  }
}
```

**Output:**
```json
{
  "id": "CANV01kd6gr3vjxm2rs0k8s3fjq4nl",
  "name": "API Monitor",
  "slug": "api-monitor",
  "version": 1,
  "createdAt": "2026-04-07T12:00:00.000Z"
}
```

### `borgiq canvases update`

Update canvas metadata (not actors).

```bash
borgiq canvases update CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --name "API Health Monitor" \
  --description "Checks API endpoints every 5 minutes"
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--name <name>` | New canvas name |
| `--description <desc>` | New description |

### `borgiq canvases update-data`

Import actors into an existing canvas.

**Input format:** JSON file in **ExportedCanvasData** format (config fields as JSON objects), wrapped in `{ canvas, mode }`. See [cli-data-formats.md](cli-data-formats.md#update-data-body).

```bash
# Merge mode (default) — add/update imported actors, leave others
borgiq canvases update-data CANV01kd6gr3vjxm2rs0k8s3fjq4nl --file update.json --json

# Insert mode — generate new IDs for all imported actors
borgiq canvases update-data CANV01kd6gr3vjxm2rs0k8s3fjq4nl --file fragment.json --mode insert --json

# Replace mode — replace entire canvas
borgiq canvases update-data CANV01kd6gr3vjxm2rs0k8s3fjq4nl --file full.json --mode replace --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--file <path>` | JSON file with `{ canvas, mode }` |
| `--mode <mode>` | Import mode: `merge` (default), `insert`, `replace` |

**Output:**
```
Import complete (merge mode): 3 operations applied, 0 conflicts.
```

### `borgiq canvases export`

Export a canvas as JSON (always outputs JSON, ignores `--json` flag).

```bash
# Export to stdout
borgiq canvases export CANV01kd6gr3vjxm2rs0k8s3fjq4nl

# Export to file
borgiq canvases export CANV01kd6gr3vjxm2rs0k8s3fjq4nl > backup.json

# Duplicate a canvas (export then re-create)
borgiq canvases export CANV01kd6gr3vjxm2rs0k8s3fjq4nl | \
  jq '{name: "Copy of Flow", slug: "copy-of-flow", messageTTLInDays: 7, data: (.yaml | fromjson).data}' | \
  borgiq canvases create-with-data --json
```

**Output:**
```json
{
  "yaml": "metadata:\n  id: CANV01kd6gr3vjxm2rs0k8s3fjq4nl\n  slug: api-monitor\n  name: API Monitor\n  ...\ndata:\n  schemaVersion: '1'\n  actors:\n    ACTR01kd6gqghj04j8765nnqyp09a3:\n      ...",
  "errors": []
}
```

### `borgiq canvases verify-import`

Validate import data without actually importing.

**Input format:** JSON with `canvas` field as a YAML string.

```bash
borgiq canvases verify-import --file import-check.json --json
```

**Output (valid):**
```json
{
  "valid": true,
  "data": { "schemaVersion": "1", "actors": { "..." } }
}
```

**Output (invalid):**
```json
{
  "valid": false,
  "errors": ["Invalid actor ID format at actors.BAD_ID"]
}
```

### `borgiq canvases validate`

Validate a deployed canvas for configuration errors.

```bash
borgiq canvases validate CANV01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output (valid):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

**Output (with errors):**
```json
{
  "valid": false,
  "errors": [
    {
      "actorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
      "actorName": "Process Data",
      "field": "configuration.code",
      "message": "Code is required for DenoActor"
    }
  ],
  "warnings": [
    { "message": "Canvas has no trigger actor" }
  ]
}
```

### `borgiq canvases layout`

Auto-arrange actors visually using the ELK layout algorithm.

```bash
# Layout entire canvas
borgiq canvases layout CANV01kd6gr3vjxm2rs0k8s3fjq4nl --json

# Layout only actors downstream of a specific actor
borgiq canvases layout CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --source-actor-id ACTR01kd6gqghj04j8765nnqyp09a3 --json

# Layout downstream of multiple triggers
borgiq canvases layout CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --source-actor-id ACTR01kd6gqghj04j8765nnqyp09a3 \
  --source-actor-id ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--source-actor-id <id>` | Layout only downstream of this actor (repeatable) |

---

## Canvas Actor Commands

> **Format reminder:** All `canvas-actors` commands that accept `--file` use the **CanvasActor** schema where configuration fields (`options`, `inputs`, `vars`, `outputs`, `secrets`, `error`) must be **YAML strings** — not JSON objects. The `options` field is **required** (can be empty string `""`). This is different from `canvases create-with-data` which uses JSON objects for these fields.

### `borgiq canvas-actors list`

List actors in a canvas with optional filters.

```bash
# List all actors
borgiq canvas-actors list CANV01kd6gr3vjxm2rs0k8s3fjq4nl --json

# Filter by type
borgiq canvas-actors list CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --actor-type DenoActor --json

# Filter by active status
borgiq canvas-actors list CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --is-active true --json

# Search by name/description
borgiq canvas-actors list CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --search "fetch" --json

# Pagination
borgiq canvas-actors list CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --page 1 --page-size 10 --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--actor-type <type>` | Filter by actor type |
| `--is-active <bool>` | Filter by active status |
| `--search <query>` | Search name/description |
| `--page <n>` | Page number |
| `--page-size <n>` | Results per page |

**Output:**
```json
{
  "total": 5,
  "actors": [
    {
      "id": "ACTR01kd6gqghj04j8765nnqyp09a3",
      "type": "ButtonTriggerActor",
      "name": "Manual Trigger",
      "msgVar": "manual_trigger",
      "isActive": true,
      "configuration": { "options": "" },
      "..."
    }
  ]
}
```

### `borgiq canvas-actors get`

Get a single actor's full data.

```bash
borgiq canvas-actors get CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gqghj04j8765nnqyp09a3 --json
```

**Output:** Full `CanvasActor` object with YAML string configuration fields.

### `borgiq canvas-actors flow`

Get an actor and all its downstream actors (following edges).

```bash
borgiq canvas-actors flow CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gqghj04j8765nnqyp09a3 --json
```

**Output:**
```json
{
  "rootActor": { "id": "ACTR01kd6gqghj04j8765nnqyp09a3", "..." },
  "downstreamActors": [
    { "id": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl", "..." }
  ]
}
```

### `borgiq canvas-actors verify`

Validate actor options against the actor type's schema without modifying the canvas.

**Input format:** JSON with `actorType` and `options` (YAML string). Pipe via stdin or `--file`.

```bash
# Verify HttpRequestActor options
echo '{"actorType": "HttpRequestActor", "options": "method: GET\nurl: https://example.com"}' | \
  borgiq canvas-actors verify CANV01kd6gr3vjxm2rs0k8s3fjq4nl --json

# Verify RouterActor with sourcePorts
echo '{
  "actorType": "RouterActor",
  "options": "emitType: singleRoute\nconditions:\n  Active: ${{ msg.trigger.body.status === \"active\" }}",
  "sourcePorts": [
    { "id": "SPRTabcdefg", "name": "Active" },
    { "id": "SPRTdefault", "name": "F" }
  ]
}' | borgiq canvas-actors verify CANV01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output (valid):**
```json
{ "valid": true, "errors": [] }
```

**Output (invalid):**
```json
{
  "valid": false,
  "errors": [
    { "path": "url", "message": "Required" }
  ]
}
```

### `borgiq canvas-actors create`

Create a single actor in a canvas.

**Input format:** JSON in **CanvasActor** format (config fields as YAML strings). See [cli-data-formats.md](cli-data-formats.md#canvasactor-format).

```bash
# Generate the actor ID first
ACTOR_ID=$(borgiq generate id actor)
echo "Creating actor: $ACTOR_ID"

# Create from file
borgiq canvas-actors create CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  "$ACTOR_ID" --file actor.json --json

# Using the scaffold script
./references/cli/scripts/scaffold-actor.sh \
  --type HttpRequestActor --name "Fetch Users" --output actor.json
borgiq canvas-actors create CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  "$ACTOR_ID" --file actor.json --json
```

**Example input (`actor.json`):**

Schema: `CanvasActor` (without `id`) — config fields are **YAML strings** (not JSON objects).

```jsonc
{
  "type": "HttpRequestActor",              // REQUIRED
  "version": 1,                            // REQUIRED
  "name": "Fetch Users",                   // REQUIRED
  "msgVar": "fetch_users",                 // REQUIRED
  "description": "Fetches user list",      // REQUIRED (can be "")
  "isActive": true,                        // REQUIRED
  "continueOnError": false,                // REQUIRED
  "enableLTM": false,                      // REQUIRED
  "enableSTM": false,                      // REQUIRED
  "sourcePorts": [{ "id": "SPRTdefault" }], // REQUIRED
  "configuration": {
    "options": "method: GET\nurl: https://api.example.com/users",
                                            // REQUIRED — must be YAML string (not JSON object)
    "outputs": "${{ results.body }}"        // optional — YAML string
  },
  "schemas": {},                           // REQUIRED (can be {})
  "position": { "x": 0, "y": 200 },       // REQUIRED
  "edges": {}                              // REQUIRED (can be {})
}
```

**Output:**
```
Actor created: ACTR01kd6gr3vjxm2rs0k8s3fjq4nl
```

### `borgiq canvas-actors update`

Partial update of an actor — only include fields you want to change.

**Input format:** JSON in **CanvasActor** format (partial, config fields as YAML strings).

```bash
# Update actor options
borgiq canvas-actors update CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --file updates.json --json

# With conflict detection
borgiq canvas-actors update CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --file updates.json --edit-version 3 --json
```

**Example input (`updates.json`):**
```json
{
  "name": "Fetch Active Users",
  "msgVar": "fetch_active_users",
  "configuration": {
    "options": "method: GET\nurl: https://api.example.com/users?status=active"
  }
}
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--file <path>` | JSON file with partial actor data |
| `--edit-version <n>` | Expected edit version for conflict detection |

### `borgiq canvas-actors delete`

Delete an actor from a canvas.

```bash
# Simple delete
borgiq canvas-actors delete CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gr3vjxm2rs0k8s3fjq4nl

# With conflict detection
borgiq canvas-actors delete CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --edit-version 3
```

### `borgiq canvas-actors batch`

Execute multiple actor operations (add, update, remove) in a single request.

**Input format:** JSON with `operations` array in **CanvasActor** format (YAML strings). See [cli-data-formats.md](cli-data-formats.md#batch-operations-format).

```bash
# From file
borgiq canvas-actors batch CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --file batch-ops.json --json

# Using the scaffold script
./references/cli/scripts/scaffold-batch.sh \
  --add "HttpRequestActor:Fetch Data" \
  --add "DenoActor:Process" \
  --output batch-ops.json
borgiq canvas-actors batch CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --file batch-ops.json --json
```

**Output:**
```json
{
  "appliedOperations": [
    { "type": "add", "actorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl", "status": "applied" },
    { "type": "update", "actorId": "ACTR01kd6gqghj04j8765nnqyp09a3", "status": "applied" }
  ],
  "conflicts": [],
  "updatedAt": "2026-04-07T12:00:00.000Z"
}
```

---

## Actor Definition Commands

### `borgiq actors list`

List all available actor types.

```bash
borgiq actors list
```

**Output (table):**
```
Actor Type                Category
─────────────────────────────────
ButtonTriggerActor        trigger
WebhookTriggerActor       trigger
ScheduledTriggerActor     trigger
EmailTriggerActor         trigger
CallableTriggerActor      trigger
InterfaceTriggerActor     trigger
AppTriggerActor           trigger
HttpRequestActor          task
DenoActor                 task
PythonActor               task
AiActor                   task
AiAgentActor              task
AgentHarnessActor         task
DataStoreActor            task
CollectionActor           task
SendEmailActor            task
McpServerActor            task
MessageProcessorActor     task
RouterActor               control
AiRouterActor             control
CallFlowActor             control
WebhookResponseActor      response
CallableResponseActor     response
InterfaceActor            interface
InterfaceStatusActor      interface
CommentActor              other
EchoActor                 other
```

### `borgiq actors schema`

Get the configuration schema for an actor type.

```bash
# Standard actor
borgiq actors schema HttpRequestActor --json

# Action-based actor (shows action selector)
borgiq actors schema DataStoreActor --json

# Get per-action schema
borgiq actors schema DataStoreActor --action set --json
borgiq actors schema MessageProcessorActor --action dedupeByCount --json
```

**Output (HttpRequestActor):**
```json
{
  "actorType": "HttpRequestActor",
  "name": "HTTP Request",
  "description": "Make HTTP requests to external APIs",
  "category": "task",
  "optionsSchema": {
    "properties": {
      "url": { "type": "string", "title": "URL" },
      "method": { "type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"] }
    },
    "required": ["method", "url"]
  },
  "defaultOptions": { "url": "https://www.example.com", "method": "GET" },
  "sourcePorts": { "type": "singleDefault", "fixedPorts": [{ "id": "SPRTdefault" }] },
  "code": { "supported": false },
  "supportsConnection": true,
  "enableLTM": false,
  "enableSTM": false
}
```

---

## Template Commands

Templates are pre-built actor configurations published by BorgIQ or by your org/workspace. Use them as starting points when scaffolding actors instead of building from scratch — search the catalog, fetch the one you want, then drop its `actor` payload into a `canvas-actors create` or batch operation.

### `borgiq templates list`

Browse or search the template catalog for the current workspace. The list endpoint searches across name, description, and tags server-side.

```bash
# List the first page (default 25)
borgiq templates list --json

# Free-text search — matches name, description, tags
borgiq templates list --search slack --json

# Filter by template type (repeatable — pass both for either-or)
borgiq templates list --type TRIGGER --json
borgiq templates list --type TASK --type TRIGGER --json

# Filter by template app (discover ids with `templates apps`)
borgiq templates list --app-id TAPP01kd6gqghj04j8765nnqyp09a --json

# Combine filters with search
borgiq templates list --search "send email" --type TASK --json

# Pagination — paste back the same filters on each page
borgiq templates list --search slack --page 1 --page-size 50 --json
borgiq templates list --search slack --page 2 --page-size 50 --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--search <query>` | Server-side match on name, description, and tags |
| `--type <type>` | Filter by `TASK` or `TRIGGER` (repeatable) |
| `--app-id <id>` | Filter to one template app |
| `--page <n>` | Page number (1-indexed, default `1`) |
| `--page-size <n>` | Results per page (default `25`, max `100`) |

**Output (paginated envelope):**

```json
{
  "total": 137,
  "data": [
    {
      "id": "TMPL01kd6gqghj04j8765nnqyp09a",
      "name": "Send Slack message",
      "description": "Post a message to a Slack channel",
      "type": "TASK",
      "appName": "Slack",
      "appIcon": "logos:slack",
      "accessLevel": "PUBLIC",
      "isBorgiqTemplate": true,
      "tags": "slack,messaging,notification",
      "version": 3,
      "schemaVersion": 1,
      "color": "#4A154B"
    }
  ]
}
```

**Pagination idiom** — the envelope returns `total`, so you can compute pages in JSON mode:

```bash
borgiq --json templates list --search slack --page-size 25 \
  | jq '{total, pages: ((.total / 25) | ceil), got: (.data | length)}'
```

To pull every match across pages:

```bash
PAGE=1; PAGE_SIZE=100
while :; do
  RESP=$(borgiq --json templates list --search slack --page "$PAGE" --page-size "$PAGE_SIZE")
  echo "$RESP" | jq -c '.data[]'
  GOT=$(echo "$RESP" | jq '.data | length')
  TOTAL=$(echo "$RESP" | jq '.total')
  [[ $((PAGE * PAGE_SIZE)) -ge $TOTAL || $GOT -lt $PAGE_SIZE ]] && break
  PAGE=$((PAGE + 1))
done
```

> The `list` envelope is **metadata only** — the actor definition isn't included. Pipe the `id` into `templates get` to fetch the full payload before instantiating.

### `borgiq templates get`

Fetch a single template by id, **including the actor definition**. Designed to be piped after a search.

```bash
borgiq templates get TMPL01kd6gqghj04j8765nnqyp09a --json

# Search → pick first match → fetch full payload
borgiq --json templates list --search "send email" --type TASK \
  | jq -r '.data[0].id' \
  | xargs -I{} borgiq templates get {} --json > template.json
```

**Output:** Same fields as `list` plus an `actor` field carrying the `ExportedCanvasActor` payload.

> The payload's configuration is in **ExportedCanvasActor** shape (config fields are JSON objects) but `canvas-actors create` / `batch` expects **CanvasActor** (config fields are YAML strings inside JSON). Use `borgiq scaffold actor-from-template` to handle the conversion — it also generates a fresh actor id, a `webhookTriggerKey` for trigger types that need one, and stamps `template: { id, version, appName }` provenance. See [cli-setup-scripts.md#convert-a-template-to-an-actor-borgiq-scaffold-actor-from-template](cli-setup-scripts.md#convert-a-template-to-an-actor-borgiq-scaffold-actor-from-template) for the full reference. Example:
>
> ```bash
> ACTOR_ID=$(borgiq templates get TMPL01... --json \
>   | borgiq scaffold actor-from-template \
>       --name "My instance" --output actor.json --print-id 2>&1 >/dev/null)
> borgiq canvas-actors create CANV01... "$ACTOR_ID" --file actor.json --json
> ```

### `borgiq templates apps`

List the template apps available for the `--app-id` filter. Use this to discover app ids when you want to scope a search to a single integration.

```bash
borgiq templates apps --json

# Search apps by name
borgiq templates apps --search slack --json

# Filter to a specific category
borgiq templates apps --category-id TCAT01kd6gqghj04j8765nnqyp09a --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--search <query>` | Match on app name |
| `--category-id <id>` | Filter to one template category |
| `--page <n>` / `--page-size <n>` | Standard pagination |

**Output:**

```json
{
  "total": 42,
  "data": [
    { "id": "TAPP01kd6gqghj04j8765nnqyp09a", "name": "Slack", "color": "#4A154B", "icon": "logos:slack" },
    { "id": "TAPP01kd6gr3vjxm2rs0k8s3fjq4n", "name": "GitHub", "color": "#181717", "icon": "logos:github" }
  ]
}
```

---

## Resource Commands

### `borgiq connections list`

List workspace connections.

```bash
borgiq connections list --json
```

**Output:**
```json
{
  "total": 2,
  "data": [
    { "id": "CONN01kd6gqghj04j8765nnqyp09", "key": "gmail-oauth", "type": "gmail", "name": "Gmail" },
    { "id": "CONN01kd6gr3vjxm2rs0k8s3fjq4n", "key": "slack-bot", "type": "slack", "name": "Slack Bot" }
  ]
}
```

### `borgiq connections types`

List available connection types.

```bash
borgiq connections types --json
```

**Output:**
```json
{
  "data": [
    { "type": "gmail", "name": "Gmail", "authType": "oauth2" },
    { "type": "slack", "name": "Slack", "authType": "oauth2" },
    { "type": "api-key", "name": "API Key", "authType": "apiKey" }
  ]
}
```

### `borgiq secrets list`

List workspace secrets (keys only, not values).

```bash
borgiq secrets list --json
```

**Output:**
```json
{
  "total": 3,
  "data": [
    { "id": "SCRT01kd6gqghj04j8765nnqyp09", "key": "openai-key", "description": "OpenAI API Key" },
    { "id": "SCRT01kd6gr3vjxm2rs0k8s3fjq4n", "key": "stripe-key", "description": "Stripe Secret Key" }
  ]
}
```

### `borgiq assets list`

List workspace assets.

```bash
borgiq assets list --json
```

**Output:**
```json
{
  "total": 1,
  "data": [
    { "id": "ASST01kd6gqghj04j8765nnqyp09", "key": "prompt-template", "type": "plainText", "description": "System prompt" }
  ]
}
```

---

## Execution Commands

### `borgiq triggers run`

Manually trigger a flow. The canvas must contain a `ButtonTriggerActor`.

```bash
borgiq triggers run \
  --canvas CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --actor-id ACTR01kd6gqghj04j8765nnqyp09a3 --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--canvas <id>` | Canvas to trigger — ID/ULID, a slug is not accepted here (deprecated alias: `--canvas-id`) |
| `--actor-id <id>` | Trigger actor ID (must be ButtonTriggerActor) |

**Output:**
```json
{
  "flowrun": {
    "id": "FLRN01kd6gr3vjxm2rs0k8s3fjq4nl",
    "canvasId": "CANV01kd6gr3vjxm2rs0k8s3fjq4nl",
    "state": "Running",
    "createdAt": "2026-04-07T12:00:00.000Z"
  }
}
```

### `borgiq flowrun-jobs test-run`

Test a single actor using its most recent input data.

```bash
# Test in isolation
borgiq flowrun-jobs test-run \
  --canvas CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --actor-id ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --json

# Test and publish downstream
borgiq flowrun-jobs test-run \
  --canvas CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --actor-id ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --publish --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--canvas <id>` | Canvas containing the actor — ID/ULID, a slug is not accepted here (deprecated alias: `--canvas-id`) |
| `--actor-id <id>` | Actor to test |
| `--publish` | Also execute downstream actors |

### `borgiq flowrun-jobs re-run`

Re-run a failed job with the latest actor configuration.

```bash
borgiq flowrun-jobs re-run --job-id FRJB01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

---

## Monitoring Commands

### `borgiq flowruns status`

Poll the status of a running flow. Use this in a loop until `state` is `Completed` or `UserInterrupted`.

```bash
borgiq flowruns status FLRN01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output (running):**
```json
{
  "id": "FLRN01kd6gr3vjxm2rs0k8s3fjq4nl",
  "state": "Running",
  "counters": {
    "queued": 1,
    "running": 2,
    "completed": 3,
    "failed": 0
  }
}
```

**Output (completed):**
```json
{
  "id": "FLRN01kd6gr3vjxm2rs0k8s3fjq4nl",
  "state": "Completed",
  "counters": { "queued": 0, "running": 0, "completed": 5, "failed": 0 }
}
```

**States:**
- `Running` — at least one counter > 0
- `Completed` — all done
- `UserInterrupted` — manually interrupted

### `borgiq flowruns summary`

Get a complete execution summary after completion.

```bash
borgiq flowruns summary FLRN01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output:**
```json
{
  "id": "FLRN01kd6gr3vjxm2rs0k8s3fjq4nl",
  "state": "Completed",
  "jobs": [
    {
      "id": "FRJB01kd6gqghj04j8765nnqyp09a3",
      "actorId": "ACTR01kd6gqghj04j8765nnqyp09a3",
      "actorName": "Manual Trigger",
      "state": "Completed",
      "startedAt": "2026-04-07T12:00:00.000Z",
      "completedAt": "2026-04-07T12:00:01.000Z"
    },
    {
      "id": "FRJB01kd6gr3vjxm2rs0k8s3fjq4nl",
      "actorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
      "actorName": "Fetch Users",
      "state": "Completed",
      "startedAt": "2026-04-07T12:00:01.000Z",
      "completedAt": "2026-04-07T12:00:02.500Z"
    }
  ],
  "errors": []
}
```

### `borgiq flowruns interrupt`

Stop a running flow.

```bash
borgiq flowruns interrupt FLRN01kd6gr3vjxm2rs0k8s3fjq4nl
```

---

## Debugging Commands

### `borgiq flowrun-jobs runtime-data`

Inspect exactly what configuration and data an actor had at runtime.

```bash
# Actor context (configuration, secrets, connection data)
borgiq flowrun-jobs runtime-data FRJB01kd6gr3vjxm2rs0k8s3fjq4nl \
  --root-path ctx --json

# Trigger event for the firing (webhook request, schedule timestamps, …)
borgiq flowrun-jobs runtime-data FRJB01kd6gr3vjxm2rs0k8s3fjq4nl \
  --root-path trigger --json

# Interpolated actor inputs
borgiq flowrun-jobs runtime-data FRJB01kd6gr3vjxm2rs0k8s3fjq4nl \
  --root-path inputs --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--root-path <path>` | Data root path: `ctx`, `trigger`, or `inputs` |

**Output (`--root-path ctx`):**
```json
{
  "workspace": { "id": "WKSP01..." },
  "canvas": { "id": "CANV01..." },
  "actor": {
    "options": { "method": "GET", "url": "https://api.example.com/users" },
    "inputs": { "customerId": "cust_123" }
  }
}
```

**Output (`--root-path trigger`, webhook firing):**
```json
{
  "type": "webhook",
  "request": {
    "meta": { "requestId": "..." },
    "method": "POST",
    "headers": { "content-type": "application/json" },
    "body": { "id": "cust_123" },
    "queryParams": {}
  }
}
```

### `borgiq flowrun-jobs ai-timeline`

View the tool-use timeline for `AiAgentActor` jobs.

```bash
borgiq flowrun-jobs ai-timeline FRJB01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output:**
```json
{
  "timeline": [
    { "type": "message", "role": "user", "content": "Find customer data" },
    { "type": "tool_use", "name": "fetch_users", "input": { "query": "active" } },
    { "type": "tool_result", "content": "[{\"id\": 1, \"name\": \"Alice\"}]" },
    { "type": "message", "role": "assistant", "content": "Found 1 active customer: Alice" }
  ]
}
```

### `borgiq flowrun-jobs source-message`

See what triggered a specific job.

```bash
borgiq flowrun-jobs source-message FRJB01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

### `borgiq flowrun-results summaries`

Get result summaries for a job (shows success/error status and timing).

```bash
borgiq flowrun-results summaries --job-id FRJB01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

**Output:**
```json
[
  {
    "id": "FRRS01kd6gqghj04j8765nnqyp09a3",
    "status": "success",
    "startedAt": "2026-04-07T12:00:01.000Z",
    "completedAt": "2026-04-07T12:00:02.500Z"
  }
]
```

### `borgiq flowrun-results data`

Get the full runtime response: messages emitted per port, errors, signal data.

```bash
borgiq flowrun-results data FRRS01kd6gqghj04j8765nnqyp09a3 --json
```

**Output:**
```json
{
  "status": "success",
  "messages": {
    "SPRTdefault": [
      { "body": { "users": [{ "id": 1, "name": "Alice" }] } }
    ]
  }
}
```

### `borgiq flowrun-messages list`

List messages emitted by an actor in a flowrun.

```bash
borgiq flowrun-messages list \
  --canvas CANV01kd6gr3vjxm2rs0k8s3fjq4nl \
  --flowrun-id FLRN01kd6gr3vjxm2rs0k8s3fjq4nl \
  --actor-id ACTR01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

### `borgiq flowrun-messages data`

Get the full payload of a specific message.

```bash
borgiq flowrun-messages data MSG01kd6gr3vjxm2rs0k8s3fjq4nl --json
```

---

## Common Workflows

### Create, Validate, Layout, and Test

```bash
# 1. Generate canvas JSON
./references/cli/scripts/scaffold-canvas.sh \
  --name "My Flow" --slug my-flow --template button-http \
  --output outputs/my-flow.json

# 2. Deploy
RESULT=$(borgiq canvases create-with-data --file outputs/my-flow.json --json)
CANVAS_ID=$(echo "$RESULT" | jq -r '.id')
echo "Created canvas: $CANVAS_ID"

# 3. Validate
borgiq canvases validate "$CANVAS_ID" --json

# 4. Auto-layout
borgiq canvases layout "$CANVAS_ID" --json

# 5. Find the trigger actor
TRIGGER_ID=$(borgiq canvas-actors list "$CANVAS_ID" \
  --actor-type ButtonTriggerActor --json | jq -r '.actors[0].id')

# 6. Trigger the flow
FLOWRUN=$(borgiq triggers run --canvas "$CANVAS_ID" --actor-id "$TRIGGER_ID" --json)
FLOWRUN_ID=$(echo "$FLOWRUN" | jq -r '.flowrun.id')

# 7. Poll until complete (every 3 seconds)
while true; do
  STATUS=$(borgiq flowruns status "$FLOWRUN_ID" --json | jq -r '.state')
  echo "Status: $STATUS"
  [[ "$STATUS" == "Completed" || "$STATUS" == "UserInterrupted" ]] && break
  sleep 3
done

# 8. Check results
borgiq flowruns summary "$FLOWRUN_ID" --json
```

### Debug a Failed Actor

```bash
# 1. Find failures in the flowrun summary
borgiq flowruns summary "$FLOWRUN_ID" --json | jq '.errors'

# 2. Get the failed job ID from the summary
JOB_ID=$(borgiq flowruns summary "$FLOWRUN_ID" --json | \
  jq -r '.jobs[] | select(.state == "Error") | .id')

# 3. See what config was used
borgiq flowrun-jobs runtime-data "$JOB_ID" --root-path ctx --json

# 4. See what input data was received
borgiq flowrun-jobs runtime-data "$JOB_ID" --root-path inputs --json

# 5. Get detailed error
borgiq flowrun-results summaries --job-id "$JOB_ID" --json

# 6. Fix the actor
echo '{"configuration": {"options": "method: GET\nurl: https://correct-api.com"}}' > fix.json
borgiq canvas-actors update "$CANVAS_ID" "$ACTOR_ID" --file fix.json --json

# 7. Re-run the fixed job
borgiq flowrun-jobs re-run --job-id "$JOB_ID" --json
```

### Iterate on a Flow

> **Bundle first:** when the canvas has (or can have) a local bundle, iterate with `bundle pull` → edit files → `bundle validate` → `bundle push` instead — see [canvas-bundles.md](canvas-bundles.md#lifecycle-commands). The batch loop below is the fallback for a canvas nobody maintains locally.

```bash
# 1. Read current flow
borgiq canvases get "$CANVAS_ID" --include-data --json > current.json

# 2. Modify actors via batch
borgiq canvas-actors batch "$CANVAS_ID" --file changes.json --json

# 3. Validate
borgiq canvases validate "$CANVAS_ID" --json

# 4. Re-layout
borgiq canvases layout "$CANVAS_ID" --json

# 5. Test
borgiq triggers run --canvas "$CANVAS_ID" --actor-id "$TRIGGER_ID" --json

# 6. Monitor
borgiq flowruns status "$FLOWRUN_ID" --json
```
