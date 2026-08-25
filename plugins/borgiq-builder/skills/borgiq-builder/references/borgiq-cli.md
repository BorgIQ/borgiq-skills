# BorgIQ CLI Reference

Use the `borgiq` CLI to deploy workflows to the platform, trigger flows, monitor execution, and debug failures — all from the command line.

> **Expanded documentation:** For detailed examples, data format specifications, scaffolding scripts, and troubleshooting, see the [CLI Documentation](cli/) directory:
> - [Canvas Bundles](cli/canvas-bundles.md) — preferred filesystem workflow, layout, sync/conflicts, and lifecycle commands
> - [Command Reference with Examples](cli/cli-command-reference.md) — every command with realistic examples and expected output
> - [Data Formats (JSON schemas, YAML strings)](cli/cli-data-formats.md) — which commands accept which JSON schema and field types
> - [Setup & Scaffolding Scripts](cli/cli-setup-scripts.md) — generate properly-structured JSON input files
> - [Troubleshooting Guide](cli/cli-troubleshooting.md) — common errors and fixes

> **Environment check:** This reference requires shell access (Claude Code, terminal). In environments without a terminal (Claude.ai projects, Claude API without shell tools), skip this reference — use the standard generate-only workflow and present YAML to the user for manual deployment via the BorgIQ web UI.
>
> To detect: run `borgiq auth status`. If it succeeds, use this CLI workflow. If the command is not found or fails, fall back to generate-only mode.

> **Canvas identifiers:** Commands shown with `<canvasSlugOrId>` accept either the canvas slug (e.g. `my-flow`) or its ULID (e.g. `CANV01…`). The two execution commands — `triggers run` and `flowrun-jobs test-run` — still require the ULID; a slug is not accepted there. The canonical flag is `--canvas`; the old `--canvas-id` keeps working as a deprecated alias.

## Canvas bundles

The canvas bundle is the default way to build and edit canvases: actor configuration lives in parsed-object `actor.yaml` files, code in native files under `code/` (a project tree, entrypoint plus helpers, for the actors that run code), the graph in `canvas.yaml`, and push/pull synchronize with three-way sync (a per-actor content-hash + edit-version baseline in `sync.actors`). Direct export documents and CanvasActor batch payloads are the fallback for environments without shell access or bundle support.

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
# New canvas: init -> edit -> validate -> create
borgiq bundle init ./my-flow.borgiq-canvas --name "My Flow" --slug my-flow
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout

# Existing canvas: pull -> edit -> validate -> preview -> push
borgiq bundle pull <canvasSlugOrId> ./my-flow.borgiq-canvas
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --dry-run
borgiq bundle push ./my-flow.borgiq-canvas   # add --auto-layout when actors were added, removed, or rewired
```

Read [Canvas Bundles](cli/canvas-bundles.md) before hand-editing the layout. It defines the three-edit rule, the `codeDir` contract — including the [project tree](cli/canvas-bundles.md#code-actor-project-trees) that Deno, Deno Test, Universal Trigger, and Python actors keep under `code/`, with its required `main.ts` / `main.py` entrypoint and reserved filenames — root graph ownership, incremental sync verdicts, and conflict recovery. Bundle commands require a CLI build containing BorgIQ CLI PR #37; until a release version is published, the capability check above is authoritative. If the command is unavailable, use the direct document/batch workflow below.

## Setup

**Install:**

```bash
npm install -g @borgiq/cli
```

**Authentication — user handles this, not the AI agent:**

The user must run `borgiq auth login` before starting the AI agent session. This stores the API token securely in `~/.config/borgiq/config.json` (owner-only permissions). The AI agent then uses `borgiq` commands without ever seeing or handling the token.

```bash
# User runs this before starting the AI agent session
borgiq auth login
```

**Important:**
- Do NOT ask the user for their API token — they authenticate via `borgiq auth login` themselves
- Do NOT read `~/.config/borgiq/config.json` or environment variables containing tokens
- Just run `borgiq` commands — authentication is handled transparently by the CLI
- If a command returns a 401 error, tell the user to run `borgiq auth login` to reconfigure

**Verify the CLI is authenticated:**

```bash
borgiq auth status
```

If this fails, instruct the user: "Please run `borgiq auth login` to authenticate before continuing."

---

## Step 1: Discover Environment

Before building a workflow, discover the orgs, workspaces, and resources available.

### List orgs and workspaces

```bash
borgiq orgs list
borgiq workspaces list --org my-org
```

### List existing canvases

```bash
borgiq canvases list
```

### Get a canvas with its full flow data

```bash
borgiq canvases get <canvasSlugOrId> --include-data --json
```

---

## Step 2: Discover Actor Types

### List all available actor types

```bash
borgiq actors list
```

### Get configuration schema for a specific actor type

```bash
borgiq actors schema HttpRequestActor --json
borgiq actors schema DenoActor --json
```

The schema response shows required fields, supported connections, source ports, and feature flags. Use this to understand what configuration an actor needs before generating YAML.

### Browse the template catalog (faster than building from scratch)

Templates are pre-built actor configurations published by BorgIQ (and optionally your org/workspace) — e.g. "Send Slack message", "GitHub: open issue", "OpenAI: chat completion". When a template matches what the user is asking for, prefer fetching and adapting it over hand-building an actor.

```bash
# Search by name, description, or tags
borgiq templates list --search slack --json
borgiq templates list --search "send email" --type TASK --json

# Filter by type (TASK or TRIGGER) — repeatable for either-or
borgiq templates list --type TRIGGER --json
borgiq templates list --type TASK --type TRIGGER --json

# Discover template app ids, then filter to one integration
borgiq templates apps --search slack --json
borgiq templates list --app-id TAPP01kd6gqghj04j8765nnqyp09a --json
```

**Pagination** — the list endpoint paginates the standard way (`--page` / `--page-size`, default `25`, max `100`). The JSON envelope is `{ total, data }`, so in `--json` mode you can detect more pages:

```bash
borgiq --json templates list --search slack --page-size 25 \
  | jq '{total, pages: ((.total / 25) | ceil)}'
```

To loop through every match:

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

The `list` envelope is **metadata only**. To get the actor definition, fetch the template by id:

```bash
borgiq templates get TMPL01kd6gqghj04j8765nnqyp09a --json
```

The returned object includes an `actor` field carrying the full `ExportedCanvasActor` payload — drop this into `canvas-actors create` / `batch` (remember to convert config fields to YAML strings per the [data formats reference](cli/cli-data-formats.md)) instead of writing the actor from scratch.

**End-to-end pattern — search, pick, instantiate:**

The YAML-string conversion is handled by `borgiq scaffold actor-from-template` (see [cli-setup-scripts.md#convert-a-template-to-an-actor-borgiq-scaffold-actor-from-template](cli/cli-setup-scripts.md#convert-a-template-to-an-actor-borgiq-scaffold-actor-from-template)), which mirrors the platform's `importActor()` and also generates a fresh actor id, a `webhookTriggerKey` for trigger types that need one, and the `template: { id, version, appName }` provenance:

```bash
# 1. Find a template
borgiq --json templates list --search "send slack" --type TASK \
  | jq '.data[] | {id, name, appName}'

# 2. Convert in one pipe and capture the generated actor id
ACTOR_ID=$(borgiq templates get TMPL01kd6gqghj04j8765nnqyp09a --json \
  | borgiq scaffold actor-from-template \
      --name "Notify #ops on deploy" \
      --output outputs/notify-ops-actor.json \
      --print-id 2>&1 >/dev/null)

# 3. Create the actor in the canvas
borgiq canvas-actors create "$CANVAS_ID" "$ACTOR_ID" \
  --file outputs/notify-ops-actor.json --json
```

For batch mode: pipe the converter through `--batch` to emit the operations envelope directly into `borgiq canvas-actors batch`. The command does **not** wire credentials, secrets, or `inputs` values — apply those via a follow-up `canvas-actors update`.

See [cli-command-reference.md#template-commands](cli/cli-command-reference.md#template-commands) for the full flag list and example outputs.

---

## Step 3: Discover Workspace Resources

Before building actor configurations, check what connections, credentials, and assets already exist in the workspace. This determines what `connection.key`, `credentials` keys, and asset references to use in the YAML.

### List connections

```bash
borgiq connections list --json
```

Check if the connection the actor needs already exists. If it does, use its `key` in the actor's `connection` config:

```yaml
configuration:
  connection:
    key: my-existing-connection
    type: gmail
```

`type` also accepts a non-empty array of connection-type names when several are acceptable (e.g. `[github-oauth2, github-pat]`) — see [Typed Connections](http-request-actor.md#typed-connections).

If the connection doesn't exist, instruct the user:

> You need to create a Gmail connection in the workspace with the key `my-gmail`. Go to **Workspace Settings > Connections > Add Connection** and select Gmail OAuth2.

### List connection types

```bash
borgiq connections types --json
```

Shows what connection types are available for the workspace (e.g., gmail, slack-oauth2, github-oauth2).

`configuration.connection.type` accepts either one exact connection-type name or a non-empty array of exact names.

### List secrets

```bash
borgiq secrets list --json
```

Check if a secret the actor needs exists. If it does, reference it in the actor config:

```yaml
configuration:
  credentials:
    apiKey:
      workspaceKey: my-openai-key
```

If the secret doesn't exist, instruct the user:

> You need to create a secret in the workspace with the key `my-openai-key`. Go to **Workspace Settings > Secrets > Add Secret** and add your OpenAI API key.

### List assets

```bash
borgiq assets list --json
```

Check if referenced assets (files, images, documents) exist. Assets are referenced by key in actor configurations.

---

## Step 4: Deploy a Workflow

After generating and locally validating YAML, deploy it to the platform.

### Preferred: deploy a canvas bundle

For a new bundle:

```bash
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout
```

For an existing canvas pulled into a bundle:

```bash
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --dry-run
borgiq bundle push ./my-flow.borgiq-canvas --auto-layout
```

`bundle push` is incremental by default and refreshes the local bundle after success. Use direct documents or batch operations only when a bundle is not possible: no shell/filesystem access, a CLI without bundle support, or a one-off patch to a canvas nobody maintains locally.

### Direct document and batch workflow

#### Create a new canvas with full flow data

```bash
borgiq canvases create-with-data --file outputs/my-workflow.yaml --json
```

Or pipe from stdin:

```bash
cat outputs/my-workflow.yaml | borgiq canvases create-with-data --json
```

The request body should include `name`, `slug`, `description`, and `data` (the full actor graph). See the [AI Agent API Guide](ai-agent-api-guide.md) for the expected JSON structure.

#### Create an empty canvas, then add actors incrementally

```bash
# Create empty canvas
borgiq canvases create --name "My Flow" --slug my-flow --json

# Add actors via patch
borgiq canvas-actors batch <canvasSlugOrId> --file actors-patch.yaml --json
```

The patch body uses operations: `add`, `update`, `remove`, with per-actor `editVersion` conflict detection. Use it only for a canvas that has no local bundle — once a bundle exists, edit the bundle and `bundle push` instead of patching out of band.

#### Import canvas data (merge, insert, or replace)

```bash
# Merge (default) — add/update actors from import, leave others untouched
borgiq canvases update-data <canvasSlugOrId> --file updated-flow.yaml --json

# Insert — generate new IDs for all imported actors, no conflicts
borgiq canvases update-data <canvasSlugOrId> --file flow-fragment.yaml --mode insert --json

# Replace — replace entire canvas with imported data
borgiq canvases update-data <canvasSlugOrId> --file full-canvas.yaml --mode replace --json
```

**Modes:**
- `merge` (default): Updates existing actors by ID, adds new ones. Other actors are left untouched.
- `insert`: Generates new actor/edge IDs for all imported actors. Safe for duplicating workflow fragments.
- `replace`: Full canvas replacement. Returns 409 if the canvas was modified concurrently — re-read and retry.

All modes use per-actor `editVersion` conflict detection and return the same response as `batch`.

#### Update canvas metadata only

```bash
borgiq canvases update <canvasSlugOrId> --name "New Name" --description "Updated"
```

---

## Step 4b: Manage Individual Actors

For fine-grained actor management without sending the full canvas data.

### List actors in a canvas

```bash
borgiq canvas-actors list <canvasSlugOrId> --json
borgiq canvas-actors list <canvasSlugOrId> --actor-type DenoActor --is-active true --json
borgiq canvas-actors list <canvasSlugOrId> --search "fetch" --json
```

Filter by `--actor-type`, `--is-active`, and `--search` (name/description). Supports pagination with `--page` and `--page-size`.

### Get a single actor

```bash
borgiq canvas-actors get <canvasSlugOrId> <actorId> --json
```

### Get downstream flow from an actor

```bash
borgiq canvas-actors flow <canvasSlugOrId> <actorId> --json
```

Returns the specified actor plus all downstream actors reachable by following edges. Useful for understanding what happens after a specific actor.

### Verify actor options

```bash
echo '{"actorType": "HttpRequestActor", "options": "method: GET\nurl: https://example.com"}' | borgiq canvas-actors verify <canvasSlugOrId> --json
```

Validates actor options (YAML string) against the type's schema without modifying the canvas. For `RouterActor`/`AiRouterActor`, include `sourcePorts` in the JSON body.

### Create a single actor

```bash
borgiq canvas-actors create <canvasSlugOrId> <actorId> --file actor-data.json --json
```

The actor ID is specified as an argument. Generate it client-side using the `ACTR` prefix format.

### Update a single actor

```bash
borgiq canvas-actors update <canvasSlugOrId> <actorId> --file updates.json --json
borgiq canvas-actors update <canvasSlugOrId> <actorId> --file updates.json --edit-version 3 --json
```

Partial update — only include the fields you want to change. Use `--edit-version` for conflict detection.

### Delete a single actor

```bash
borgiq canvas-actors delete <canvasSlugOrId> <actorId>
borgiq canvas-actors delete <canvasSlugOrId> <actorId> --edit-version 3
```

---

## Step 5: Validate on Server

After deploying, validate the canvas on the server to catch issues that local validation can't detect (missing connections, invalid resource references):

```bash
borgiq canvases validate <canvasSlugOrId> --json
```

**Response includes:**
- `valid: true/false`
- `errors` — ID format issues, missing config, broken references
- `warnings` — non-blocking issues (e.g., no trigger actor)

Fix any errors by patching actors and re-validating:

```bash
borgiq canvas-actors batch <canvasSlugOrId> --file fix-patch.json --json
borgiq canvases validate <canvasSlugOrId> --json
```

---

## Step 6: Auto-Layout

After creating or modifying a canvas programmatically, auto-arrange actors visually:

```bash
borgiq canvases layout <canvasSlugOrId> --json
```

To layout only actors downstream of specific actors (keeping everything else in place):

```bash
# Single flow
borgiq canvases layout <canvasSlugOrId> --source-actor-id ACTR01kmka7wqwan6fh6k5hgfpyv59 --json

# Multiple flows
borgiq canvases layout <canvasSlugOrId> --source-actor-id ACTR01flow1trigger --source-actor-id ACTR01flow2trigger --json
```

---

## Step 7: Execute a Flow

### Manual trigger

The canvas must contain a `ButtonTriggerActor`:

```bash
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
```

Save the returned `flowrun.id` for monitoring.

### Test run a single actor

Test an individual actor using its most recent input data:

```bash
borgiq flowrun-jobs test-run --canvas <canvasId> --actor-id <actorId> --json
```

Add `--publish` to also execute downstream actors. Without it, only this actor runs in isolation.

### Re-run a failed job

After fixing an actor's configuration, re-run it with the latest config:

```bash
borgiq flowrun-jobs re-run --job-id <flowrunJobId> --json
```

---

## Step 8: Monitor Execution

### Poll flowrun status (recommended for agents)

Poll every 2-3 seconds until `state` is `Completed` or `UserInterrupted`:

```bash
borgiq flowruns status <flowrunId> --json
```

**States:**
- `Running` — at least one counter > 0
- `Completed` — all done
- `UserInterrupted` — manually interrupted

### Get full execution summary

After completion, get a complete picture of what happened:

```bash
borgiq flowruns summary <flowrunId> --json
```

Returns per-actor job details, statuses, errors, and timing.

### Interrupt a running flow

```bash
borgiq flowruns interrupt <flowrunId>
```

---

## Step 9: Debug Failures

### Find which actors failed

```bash
borgiq flowruns summary <flowrunId> --json
# Look at the "errors" array for quick scan of all failures
```

### Get job result summaries

```bash
borgiq flowrun-results summaries --job-id <flowrunJobId> --json
```

Shows status (`success` or `error`), timing, and error metadata.

### Get full job result data

```bash
borgiq flowrun-results data <resultId> --json
```

Returns the complete runtime response: messages emitted per port, error details, signal data.

### Get runtime data (what the actor received)

This is the most useful debugging tool — see exactly what config and data an actor had:

```bash
# Actor context (configuration, secrets, connection data)
borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json

# Interpolated inputs the actor received
borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json

# Trigger event for the firing (webhook request, schedule timestamps, …)
borgiq flowrun-jobs runtime-data <jobId> --root-path trigger --json
```

### View messages between actors

```bash
# List messages for a specific actor and port
borgiq flowrun-messages list --canvas <id> --flowrun-id <id> --actor-id <id> --json

# Get full message payload
borgiq flowrun-messages data <messageId> --json
```

### AI agent timeline

For `AiAgentActor` jobs, view the full tool-use timeline:

```bash
borgiq flowrun-jobs ai-timeline <jobId> --json
```

### Get source message for a job

See what triggered a specific job:

```bash
borgiq flowrun-jobs source-message <jobId> --json
```

---

## Step 10: Export and Import

### Export a canvas

```bash
borgiq canvases export <canvasSlugOrId> > canvas-backup.json
```

### Duplicate a canvas

Export, then re-import (IDs are regenerated automatically):

```bash
borgiq canvases export <canvasSlugOrId> | borgiq canvases create-with-data --json
```

### Verify import data before creating

```bash
borgiq canvases verify-import --file import-data.json --json
```

---

## Common Workflows

### Create, Validate, Layout, and Test a Flow

```bash
# 1. Check available actor types
borgiq actors list

# 2. Check available connections and secrets
borgiq connections list --json
borgiq secrets list --json

# 3. Generate YAML locally (existing skill workflow)
# ... generate IDs, build YAML, validate locally ...

# 4. Deploy
borgiq canvases create-with-data --file outputs/my-flow.yaml --json
# Save the returned canvas ID

# 5. Validate on server
borgiq canvases validate <canvasSlugOrId> --json

# 6. Auto-layout
borgiq canvases layout <canvasSlugOrId>

# 7. Trigger
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
# Save the returned flowrun ID

# 8. Monitor (poll until Completed)
borgiq flowruns status <flowrunId> --json

# 9. Check results
borgiq flowruns summary <flowrunId> --json
```

### Debug a Failed Actor

```bash
# 1. Find failures
borgiq flowruns summary <flowrunId> --json

# 2. Get error details
borgiq flowrun-results summaries --job-id <jobId> --json

# 3. See what config was used
borgiq flowrun-jobs runtime-data <jobId> --root-path ctx --json

# 4. See what input data was received
borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json

# 5. Fix the actor configuration
borgiq canvas-actors batch <canvasSlugOrId> --file fix.json --json

# 6. Re-run with fixed config
borgiq flowrun-jobs re-run --job-id <jobId> --json
```

### Iterate on a Flow Design

The bundle loop is the default iteration workflow:

```bash
# 1. Pull once and commit the baseline
borgiq bundle pull <canvasSlugOrId> ./my-flow.borgiq-canvas

# 2. Edit actor.yaml, code/*, or canvas.yaml; then validate and preview
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --dry-run

# 3. Commit the intended local change and synchronize
borgiq bundle push ./my-flow.borgiq-canvas   # add --auto-layout when actors were added, removed, or rewired
borgiq canvases validate <canvasSlugOrId> --json

# 4. Test, inspect flowruns, edit the bundle, and repeat
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
borgiq flowruns summary <flowrunId> --json
```

When there is no local bundle, use the direct fallback:

```bash
# 1. Read current flow
borgiq canvases get <canvasSlugOrId> --include-data --json

# 2. Modify actors
borgiq canvas-actors batch <canvasSlugOrId> --file changes.json --json

# 3. Validate
borgiq canvases validate <canvasSlugOrId> --json

# 4. Re-layout if needed
borgiq canvases layout <canvasSlugOrId>

# 5. Test
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json

# 6. Monitor
borgiq flowruns status <flowrunId> --json

# 7. Check results
borgiq flowruns summary <flowrunId> --json

# Repeat 2-7 until satisfied
```

---

## Output Format

- **Interactive terminal:** Table output by default
- **Piped / `--json` flag:** JSON output (machine-readable)

Always use `--json` when parsing output programmatically:

```bash
borgiq canvases list --json | jq '.data[].id'
```
