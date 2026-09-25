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

### `borgiq workspaces deployment`

Show or change whether the workspace is deployed. On a deployed workspace, every run of a canvas —
triggers and editor test runs alike — executes the canvas's active runtime build instead of its
current code. See [deployment.md](../deployment.md) for the full model.

```bash
borgiq workspaces deployment            # status table: per canvas, code actors / running / latest / state
borgiq workspaces deployment --enable   # deploy the workspace (then build each canvas)
borgiq workspaces deployment --disable  # undeploy: runs execute each canvas's current code again
borgiq workspaces deployment --json     # full detail, including per-actor build results
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--enable` | Deploy the workspace |
| `--disable` | Undeploy the workspace |

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
| `--readme-file <path>` | Replace the canvas README with a markdown file's contents (an empty file clears it). The README is the canvas's own documentation — `README.md` in a bundle, the README tab in the editor |

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
      "field": "configuration.codeDir",
      "message": "An entrypoint file named 'main.ts' is required for DenoActor"
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

### `borgiq canvases runtime-build`

Build one canvas of a **deployed** workspace: snapshot it, compile every code actor (React apps
included), install their dependencies. Synchronous — the command holds until the build finishes
(typically a minute or two) and prints the per-actor outcome; there is nothing to poll. Refuses on a
non-deployed workspace (exit 2 — nothing there would run the build). Exit 0 only when every actor
built; a `partially_ready` build exits non-zero because it serves nothing — the previous full build
keeps running. See [deployment.md](../deployment.md).

```bash
borgiq canvases runtime-build my-canvas --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--timeout <seconds>` | How long to wait for the build (default 900); the build itself finishes on the server either way |

### `borgiq canvases runtime-build-status`

Which build the canvas runs, whether the canvas has been edited since (`outdated`), and — with
`--history` — every build of the canvas.

```bash
borgiq canvases runtime-build-status my-canvas --json
borgiq canvases runtime-build-status my-canvas --history
```

### `borgiq canvases runtime-build-activate`

Make an earlier fully-successful (`ready`) build the one the canvas's runs execute — the rollback
path.

```bash
borgiq canvases runtime-build-activate my-canvas CRBD01…
```

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

### `borgiq canvas-actors app-url`

Print the URL an App / React App actor is served from — the page the web app frames, without the editor. Meant for screenshots with your own headless browser; the CLI runs none.

```bash
SRC=$(borgiq canvas-actors app-url my-canvas ACTR01kd6gqghj04j8765nnqyp09a3)
npx playwright screenshot --viewport-size=1280,800 --wait-for-timeout=3000 "$SRC" thumbnail.png
```

The URL's content token expires within minutes; stdout carries only the URL (a sensitivity note goes to stderr), and `--json` gives `{ actorId, src }`. Needs the **`app:use`** scope (`403` otherwise). A React app answers `409` until built.

### `borgiq canvas-actors thumbnail set|get|rm`

Manage an App / React App actor's thumbnail (the canvas node and apps-page image).

```bash
borgiq canvas-actors thumbnail set my-canvas ACTR01… thumbnail.png [--edit-version 3]
borgiq canvas-actors thumbnail get my-canvas ACTR01… [--out saved.png]
borgiq canvas-actors thumbnail rm  my-canvas ACTR01… [--edit-version 3]
```

- `set` sends the image inline (`{ thumbnail: { dataUrl } }`). The API stores it and answers with the stored `{ fileId }`. PNG/JPEG/WebP/GIF, ≤ 2 MiB, no SVG; the API's reason is shown if it refuses.
- `get` prints `{ actorId, fileId, mimeType, sizeInBytes }` (or `thumbnail: null`), never the base64. `--out` writes the image.
- `rm` sends `{ thumbnail: null }`.

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
StreamActor               task
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
  "code": { "supported": false, "language": null, "entrypoint": null, "multiFile": false },
  "supportsConnection": true,
  "enableLTM": false,
  "enableSTM": false
}
```

The `code` block describes how the type carries source. For an actor that runs code it names the
language and the entrypoint filename, and says whether the source is a file list:

```json
  "code": { "supported": true, "language": "typescript", "entrypoint": "main.ts", "multiFile": true }
```

`multiFile: true` means the actor's source belongs in `configuration.codeDir` — a list of
`{path, content}` files including one at `entrypoint`. `borgiq scaffold` reads these fields rather
than hardcoding per-type rules, so scaffolding stays correct as the platform adds types.

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

## Recipe Commands

Recipes are saved, unversioned starting points (a task actor, a trigger, a flow or a flow segment) that the API adds to a canvas whole. See [borgiq-cli.md — Start from a recipe](../borgiq-cli.md#start-from-a-recipe-a-multi-actor-starting-point) for when to use one. Requires `@borgiq/cli` >= 0.13.0.

### `borgiq recipes list`

Browse or search recipes for the current workspace. Searches name, description and tags server-side.

```bash
borgiq recipes list --json
borgiq recipes list --search slack --json
borgiq recipes list --kind FLOW --kind SEGMENT --json      # repeatable, any case: TASK, TRIGGER, FLOW, SEGMENT
borgiq recipes list --app-id TAPP01... --json
borgiq recipes list --has-entry --has-exit --json           # --no-has-entry / --no-has-exit for the opposite
```

Envelope `{ total, data }`; each item is metadata only — `id`, `kind`, `name`, `description`, `actorCount`, `apps` (a recipe can list under several), `settingsCount` (`connections`, `credentials`, `inputs`), `entry` and `exit` (each `null` when the recipe has none) and tags; the table shows them as a WIRING column (`in→out`, `in`, `out`, `—`). The kinds are checked by the API, which answers an unknown one with a `400`. Paginates with `--page` / `--page-size`.

### `borgiq recipes get`

The full recipe: `data.actors` (the `ExportedCanvasData` map), `entry`, `exit`, and `settings`.

```bash
borgiq recipes get RCPE01... --json | jq '{entry, exit, settings}'
```

`settings.connections[]` is `{ type, label?, actorIds, groupKey }`, `settings.credentials[]` is `{ key, type?, source, label?, actorIds, groupKey }`, `settings.inputs[]` is `{ key, label, type, required?, default?, targets }`. `groupKey` is the group's key in the `--settings` file; the `actorIds` are recipe-local — use them in a per-actor settings map. `entry` / `exit` are `null` when the recipe has none. On a terminal without `--json`, a short summary of those keys follows on stderr.

### `borgiq recipes apps`

The template apps that hold at least one recipe (an app holding only recipes appears here, not under `templates apps`).

```bash
borgiq recipes apps --search slack --json
```

### `borgiq recipes add`

Add a recipe to a canvas. The API instantiates it: fresh actor and edge ids (references inside code and configuration rewritten), the settings values applied, webhook-keyed triggers given fresh keys, message-variable collisions suffixed, and the recipe wired in at its declared entry and exit.

```bash
borgiq recipes add RCPE01... --canvas <slug-or-id> [--x <n> --y <n>] \
  [--after <actorId[:portId]> | --into-edge <edgeId>] [--settings <file|->] --json
```

| Flag | Meaning |
|---|---|
| `--canvas` | required; the canvas to add to |
| `--x` / `--y` | where the entry actor (or, with no entry, the top-left actor) lands, in flow coordinates; default: the whole recipe below the canvas's lowest actor |
| `--after` | wire that actor's source port — its first unless `:portId` names one — to the recipe's entry (a `TASK` or `SEGMENT` with an entry) |
| `--into-edge` | splice into an edge: its source feeds the entry, the exit feeds the edge's old target (a `TASK` or `SEGMENT` with an entry and an exit) |
| `--settings` | JSON/YAML object of values: groups by the `groupKey` `recipes get` prints, inputs by key (see below); `-` reads stdin |

```yaml
# settings.yaml
connections:
  slack-bearer|slack-oauth2: team-slack    # one key for the whole group
  # slack-bearer|slack-oauth2:             # or per recipe-local actor id
  #   ACTR01...: team-slack
credentials:
  apiKey||secret: my-api-key               # a recipe whose actors use configuration.credentials
inputs:
  channel: '#triage'
  model: claude-haiku-4-5
```

Response: `{ actorIds, entryActorId, exitActorId, edgeIds }` (the two ids `null` when the recipe has no entry or exit). Nothing is added unless every check passes. Errors: `400` with `details` when a settings key names no connection/secret in the workspace or a connection of the wrong type, a group or input is not part of the recipe, a per-actor map names an actor outside its group, a value does not read as its input's type, a required input has neither a value nor a default, `--after`/`--into-edge` names something not on the canvas, or the recipe cannot be wired that way (a `FLOW` or `TRIGGER` starts a flow; a recipe without an entry takes neither flag; `--into-edge` also needs an exit); `403` when the recipe holds an actor type the organization is not allowed (e.g. `PythonActor` outside a privileged organization); `409` when the actor it is wired to changed or was removed while it was being added — nothing was added, re-read and retry; `404` for an unknown recipe or canvas.

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

### `borgiq ai-providers list`

List the workspace AI providers: built-in provider credential links (`name` = provider) and custom providers (`provider: custom`, `name` = slug). Requires `@borgiq/cli` >= 0.12.0.

```bash
borgiq ai-providers list --json
borgiq ai-providers list --provider custom --json
```

**Output:**
```json
[
  { "id": "AIST01kd6gqghj04j8765nnqyp09", "name": "anthropic", "provider": "anthropic", "hasAuthenticationData": false,
    "connectionId": "CONN01…", "connectionMissing": false, "data": {}, "modelCount": 0,
    "createdAt": "2026-09-01T10:00:00.000Z", "updatedAt": null },
  { "id": "AIST01kd6gr3vjxm2rs0k8s3fjq4n", "name": "fireworks", "provider": "custom", "hasAuthenticationData": false,
    "connectionId": "CONN02…", "connectionMissing": false,
    "effectiveBaseUrl": "https://api.fireworks.ai/inference/v1", "derivedBaseUrl": "https://api.fireworks.ai/inference/v1", "baseUrlSource": "connectionType",
    "data": { "models": [{ "id": "accounts/fireworks/models/llama-v3p1-70b-instruct", "label": "Llama 70B" }] }, "modelCount": 1,
    "createdAt": "2026-09-01T10:05:00.000Z", "updatedAt": "2026-09-02T08:00:00.000Z" }
]
```

- `modelCount` — the number of entries in the provider's catalog (`data.models`); the table shows it as `MODELS`.
- `connectionMissing: true` — the provider points at a connection that no longer exists; its models cannot resolve until it is relinked (`borgiq ai-providers edit <name> --connection <key>`).
- Custom rows also carry `effectiveBaseUrl` (the setting's `data.baseURL` override, else `derivedBaseUrl`: the connection's own base URL, else the connection type's vendor default) and `baseUrlSource` (`setting` | `connection` | `connectionType`). `effectiveBaseUrl` is absent when nothing supplies one. The table shows it as `BASE URL`.

### `borgiq ai-providers models`

List every model reference usable in actor `model` options: the known models, then each custom provider's catalog as `<slug>/<model-id>`. Actors also accept `<provider>/<model-id>` for a built-in provider's unlisted models, which this list does not enumerate.

```bash
borgiq ai-providers models --json
borgiq ai-providers models --custom --json
borgiq ai-providers models --provider groq --json
```

**Output** (a top-level array):
```json
[
  { "ref": "claude-sonnet-5", "label": "Claude Sonnet 5", "provider": "anthropic", "group": "Anthropic", "custom": false, "agent": true },
  { "ref": "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct", "label": "Llama 70B", "provider": "fireworks", "group": "Custom Provider — fireworks", "custom": true, "agent": true },
  { "ref": "groq/whisper-large-v3", "label": "whisper-large-v3", "provider": "groq", "group": "Custom Provider — groq", "custom": true, "agent": false }
]
```

`agent` (the `AGENT` column in the table) says whether the model may drive an AI Agent actor: a known model when it is in the AI Agent's curated list, a custom catalog model unless its entry says `agent: false`.

**Flags:**

| Flag | Description |
|------|-------------|
| `--custom` | Only models from custom providers |
| `--provider <id-or-slug>` | Only one provider's models; prints `No provider named '<x>'` on stderr when no provider matches |

### `borgiq ai-providers create`

Add a custom provider (an OpenAI-compatible endpoint under a slug) or link a built-in provider's connection. A custom provider's connection is a vendor connection type (`groq-bearer`, `fireworks-bearer`, …, which carry the base URL), a generic bearer / API-key connection, or `custom-provider-apikey`; `--base-url` overrides the base URL the connection supplies.

```bash
borgiq ai-providers create --provider custom --name fireworks --connection fireworks \
  --models accounts/fireworks/models/llama-v3p1-70b-instruct --json
borgiq ai-providers create --provider custom --name my-gateway --connection gateway-key \
  --base-url https://llm.example.com/v1 --models qwen2.5-coder:7b --json
borgiq ai-providers create --provider openai --connection openai-main --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--provider <id>` | `custom`, or a built-in provider id (required when not interactive) |
| `--name <slug>` | Custom providers: **required** (no default) — lowercase letters, digits and dashes, starting with a letter or digit, at most 40 characters, not a built-in provider id. Built-in providers default to the provider id |
| `--connection <key-or-id>` | Connection providing the credential; a key is resolved to its id, and an unknown key is a usage error (`Connection '<x>' not found`) |
| `--base-url <url>` | Custom providers only: base URL override (absolute http(s) URL) |
| `--models <ids>` / `--models-file <path>` | Custom providers only: the catalog (ids, or `[{ id, label?, agent?, … }]` / `{ models: [...] }`); not both |
| `--data-file <path>` | Replace the whole non-secret `data` object; cannot be combined with `--models`, `--models-file` or `--base-url` |

A custom provider created non-interactively with no models prints a warning: actors cannot use it until its catalog is filled.

### `borgiq ai-providers edit`

Rename a custom provider, change its connection or base URL, or edit its catalog. The request is a full replacement, so unchanged parts are resent as they are.

```bash
borgiq ai-providers edit fireworks --add-model accounts/fireworks/models/deepseek-v3 --json
borgiq ai-providers edit fireworks --remove-model accounts/fireworks/models/qwen2p5-coder-32b-instruct --json
borgiq ai-providers edit fireworks --base-url https://gateway.example/fireworks/v1 --json
borgiq ai-providers edit fireworks --no-base-url --json
borgiq ai-providers edit fireworks --name fireworks-eu --connection fireworks-eu --json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--name <slug>` | New slug (custom providers; same rule as `create --name`). Warns first when canvases reference the provider |
| `--connection <key-or-id>` / `--no-connection` | Set or remove the connection (an unknown key is a usage error) |
| `--base-url <url>` / `--no-base-url` | Custom providers only: set or remove the base URL override |
| `--models <ids>` / `--models-file <path>` | Custom providers only: replace the catalog |
| `--add-model <id>` / `--remove-model <id>` | Custom providers only: adjust the catalog (repeatable, comma-separated allowed) |
| `--data-file <path>` | Replace the whole `data` object (warns when it replaces an existing catalog); cannot be combined with the model flags or `--base-url` |

With no flags, `edit` prints `Nothing to update.` and sends no request.

### `borgiq ai-providers delete`

```bash
borgiq ai-providers delete fireworks -y
```

Before the confirmation (or `-y` / `--force`) the command checks which canvases reference the provider's models and warns on stderr.

**Errors and warnings (all `ai-providers` subcommands):**

| Situation | Result |
|-----------|--------|
| `--base-url`, `--no-base-url`, `--models`, `--models-file`, `--add-model` or `--remove-model` on a built-in provider | Usage error, exit 2 (`<flag> applies to custom providers only …`) |
| `--provider custom` without `--name` (non-interactive) | Usage error, exit 2 (`--name is required for a custom provider.`) |
| `--base-url` together with `--no-base-url`, or `--connection` together with `--no-connection` | Usage error, exit 2 (`Use either --base-url <url> or --no-base-url, not both.`) |
| `--connection` names a key that does not exist | Usage error, exit 2 (`Connection '<x>' not found. Run \`borgiq connections list\` …`) |
| `edit` / `delete` names a provider that does not exist | Not found, exit 5 (`AI provider '<x>' not found in workspace. …`) |
| `edit --name` (rename) or `delete` of a provider referenced by canvases | Proceeds, after a stderr warning: `Warning: <n> canvas(es) reference this provider (<names>) — their "<slug>/<model-id>" models will stop resolving after the rename` (or `delete`). References are not rewritten |

See [custom-ai-providers.md](../custom-ai-providers.md) for the connection types, the catalog fields and the model reference rules.

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
