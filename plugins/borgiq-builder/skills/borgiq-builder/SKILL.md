---
name: borgiq-builder
description: Build BorgIQ workflows (actors, triggers, wiring, expressions, storage) and deploy, run and debug them with the borgiq CLI. Covers HttpRequestActor, DenoActor, PythonActor, AiActor, AiAgentActor, AgentHarnessActor, CollectionActor, StreamActor, WebhookTriggerActor, InterfaceTriggerActor, ReactAppTriggerActor. Triggers on "create an actor", "build HTTP request", "write Deno/Python code", "use AI to process", "build an AI agent", "agent harness", "run Claude Code in sandbox", "store data", "collection", "stream", "append-only log", "set up webhook", "build a web app", "theme an app", or workflow tasks.
---

# BorgIQ Builder

Routing, core rules and where to read more. Read only what a task needs.

## Load map

Paths are under `references/`.

| Task | Read |
|---|---|
| Choose an actor or trigger type | `choosing-actors.md` |
| Webhook endpoint that routes and responds | `webhook-trigger-actor.md`, `router-actor.md`, `webhook-response-actor.md`, `workflow-example.md` |
| Scheduled job, fan-out and join | `scheduled-trigger-actor.md`, `message-processor-actor.md`, `error-handling.md` |
| Approval by emailed link, any recipient | `message-processor-actor.md` → Human approval pattern (the token `url` takes only POST, so the link opens a GET webhook flow that calls `notifyCallbackToken`), `router-actor.md`, `send-email-actor.md` |
| Approval page for a signed-in workspace member | InterfaceActor, via the form spoke |
| Deno or Python code, state across runs | `code-actor-runtime.md` + `deno-actor.md` or `python-actor.md` |
| Collection-backed CRUD API | `universal-trigger-actor.md`, `collection-design.md`, `collection-sdk.md`, `collection-migrations.md` |
| Record events, process them later | `stream-actor.md`, `collection-migrations.md` |
| Forms, apps, AI agents, schemas | [Spokes](#spokes) |
| Start from a template or recipe | `borgiq-cli.md`, `cli/canvas-bundles.md` → Templates |
| Build and push a bundle; deployed workspace | `cli/canvas-bundles.md`; `deployment.md` |
| Run, monitor, debug a flowrun | `flowrun-job-states.md`, `error-handling.md` |
| Edit an existing canvas | `editing-workflows.md` |
| No shell | `validation.md` |
| Exact option and result types | [typescript/index.md](references/typescript/index.md) |

## Non-negotiables

1. **Search [templates](references/borgiq-cli.md#start-from-a-template)** (`borgiq templates apps --search <vendor>`)
   **and, for a multi-actor flow, [recipes](references/borgiq-cli.md#start-from-a-recipe)** (`borgiq recipes list`,
   CLI ≥ 0.13.0) before hand-building.
2. **With a shell, build in a canvas bundle.** Edges and positions live only in `canvas.yaml`; adding an actor follows
   the [three-edit rule](references/cli/canvas-bundles.md#add-and-remove-actors-the-three-edit-rule).
3. **Mint IDs with `borgiq generate`** (`id actor|edge|sourceport|webhooktriggerkey`, `msgvar "<name>"`); never
   invent them. Most port IDs are fixed per type ([ports](references/edges-and-positioning.md#port-ids)). With no
   shell, use the formats in [validation.md](references/validation.md).
4. **An actor's output is `msg.<msgVar>`.** With `continueOnError: true`, a failure lands in `err.<msgVar>`.
5. **Fan-out is automatic:** N incoming edges mean N runs. [`fork`/`forkJoin`](references/message-processor-actor.md#fork-actions)
   are only for joining; `forkJoin` needs `enableSTM` and `size: ${{ ctx.actor.upstreamActorCount }}` after N
   parallel actors, or a number when a connected path can drop or reroute its message.
6. **Inputs are the wire; `vars` are local scratch.** Code actors never interpolate `vars`/`outputs`; `codeDir` is
   never interpolated.
7. **`${{ }}` goes only in YAML values and must be pure** (no I/O). Escape it as `\${{` (`"\\${{"` in double quotes):
   it stays unevaluated, backslash included.
8. **One connection per actor;** more go through credentials `source: connection`. Never put secrets in inputs.
   [Server-side](references/code-actor-runtime.md#server-side-vs-sent-to-runtime) credentials (the default) are
   placeholders that work only inside outbound HTTPS requests.
9. **Code-actor memory merges:** return only the half you change, spread the prior state, `null` clears a key; set
   the enable flags; defaults are 1 KB LTM and 4 KB STM ([memory](references/code-actor-runtime.md#memory)).
10. **Collections and streams must exist before use.** Ship an idempotent, manual-invoke migration runner
    ([below](#collection-migrations-and-provisioning)); `putItem` is create-only.
11. **On a deployed workspace, runs execute the active build:** push, then build ([deployment.md](references/deployment.md)).
12. **Validate before presenting or pushing:** `borgiq bundle validate <dir> --strict`, or `borgiq validate <file>`
    for a document.
13. **Web apps are ReactAppTriggerActor** (React spoke). **Forms are interface pages** (form spoke), which require
    signed-in viewers.
14. **Run states are lowercase, and `completed` does not mean success:** read the summary's `errors`.

## Platform model

A workspace holds canvases, connections, secrets and assets. A canvas holds workflows, each started by exactly one
trigger actor (a run is a flowrun); task actors do the work, passing messages along edges.

## Spokes

A flow across domains (form → agent → Slack) uses this hub plus each spoke it touches.

- Use the `borgiq-form-builder` skill (or read [its SKILL.md](../borgiq-form-builder/SKILL.md)) for interface
  pages: signups, surveys, data entry, approval pages.
- Use the `borgiq-react-app-builder` skill (or read [its SKILL.md](../borgiq-react-app-builder/SKILL.md)) for any
  app UI (dashboards, SPAs, `useEndpoint`, `useStreamTail`, app themes) and legacy AppTriggerActor apps.
- Use the `borgiq-agent-builder` skill (or read [its SKILL.md](../borgiq-agent-builder/SKILL.md)) to choose and
  configure AiAgentActor, AgentHarnessActor or McpServerActor.
- Use the `borgiq-json-schema-builder` skill (or read [its SKILL.md](../borgiq-json-schema-builder/SKILL.md)) for
  non-trivial schemas: `outputSchema`, tool inputs, collection items, sub-flow contracts.

## Actor catalog

Scenarios: [choosing-actors.md](references/choosing-actors.md).

### Task Actor Types

| Type | Use for |
|---|---|
| [HttpRequestActor](references/http-request-actor.md) | One REST call, when no template fits |
| [DenoActor](references/deno-actor.md) | TypeScript: dependent API calls, npm packages, I/O, loops |
| [PythonActor](references/python-actor.md) | Python 3.11 packages, data science, shell tools (`git`, `jq`) |
| [MessageProcessorActor](references/message-processor-actor.md) | Transforms (`inject`, the default), filter, delay, split/collect, fork/join, dedupe, callbacks |
| [RouterActor](references/router-actor.md) | Branch on conditions, one port per route |
| [AiActor](references/ai-actor.md) | One LLM call: generate, classify, extract, structured output |
| [AiRouterActor](references/ai-router-actor.md) | Route by AI classification |
| [AiAgentActor](references/ai-agent-actor.md) | Agent loop: workspace, bash, sessions, actors as tools |
| [AgentHarnessActor](references/agent-harness-actor.md) | Claude Code, Codex, OpenCode or pi in a sandbox VM |
| [CollectionActor](references/collection-actor.md) | Current state: CRUD, queries, labels, TTL, transactions, queues |
| [StreamActor](references/stream-actor.md) | Append-only ordered logs read by cursor |
| [CallFlowActor](references/call-flow-actor.md) | Call a sub-flow and wait, or fire and forget |
| [CallableResponseActor](references/callable-response-actor.md) | Return a sub-flow's result to a waiting CallFlowActor; otherwise it just emits |
| [WebhookResponseActor](references/webhook-response-actor.md) | Answer a WebhookTriggerActor's caller |
| [InterfaceActor](references/interface-actor.md) | A form page mid-flow; `timeoutInMinutes` bounds the wait |
| [SendEmailActor](references/send-email-actor.md) | Text or HTML email with attachments |
| [CommentActor](references/comment-actor.md) | A canvas note; never runs |

Legacy, never create: [DeprecatedAiAgent](references/ai-agent-actor.md#legacy-deprecatedaiagent);
[DataStoreActor](references/typescript/legacy/actorSchemas/task/dataStore/index.md) (use CollectionActor).

### Trigger Actor Types

| Type | Starts a flow on |
|---|---|
| [ButtonTriggerActor](references/button-trigger-actor.md) | A click in the UI; emits its `options` |
| [WebhookTriggerActor](references/webhook-trigger-actor.md) | An HTTP request that feeds a multi-actor flow |
| [UniversalTriggerActor](references/universal-trigger-actor.md) | Webhook, schedule, lifecycle or manual Invoke, handled in its `receive(req)` code |
| [ScheduledTriggerActor](references/scheduled-trigger-actor.md) | A cron schedule |
| [EmailTriggerActor](references/email-trigger-actor.md) | An email to its address |
| [InterfaceTriggerActor](references/interface-trigger-actor.md) | A form submission (form spoke) |
| [CallableTriggerActor](references/callable-trigger-actor.md) | A CallFlowActor call; its `schemas.inputs` is the contract |
| [McpServerActor](references/mcp-server-actor.md) | External MCP clients calling its tool actors |
| [ReactAppTriggerActor](../borgiq-react-app-builder/SKILL.md) | Nothing: hosts a React app; emits no messages |
| [AppTriggerActor](references/app-trigger-actor.md) | Nothing: legacy raw-HTML app, maintain only; emits no messages |

### Universal Trigger vs Webhook Trigger (HTTP endpoints)

- **Self-contained route** (parse, auth, collection reads and writes, validation, response) → a webhook-enabled
  UniversalTriggerActor replying with `Signal.webhookRespond` under `options.webhook.respondImmediately: false`.
- **Orchestration** (AI, integrations, routing, a fork) → a WebhookTriggerActor feeding task actors and a
  WebhookResponseActor.
- **Several endpoints** → one trigger each, mixing both; never merge routes to save actors.

URLs: `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}`, `${{ ctx.canvas.universalTriggers.<msgVar>.url }}` (only
with `configuration.webhook.enabled: true`). Apps call triggers by URL, never edges
([backend wiring](references/app-trigger-actor.md#backend-wiring)). [Matrix](references/choosing-actors.md#universal-trigger-vs-webhook-trigger).

## Common Actor Structure

A `metadata` + `actors` document keys actors by ID. In a bundle, `actor.yaml` holds one actor without `position` and
`edges` ([edges-and-positioning.md](references/edges-and-positioning.md)).

```yaml
metadata: { schemaVersion: v1.0, source: BIQCanvas }
actors:
  ACTR01kx4b00000000000000000001:
    id: ACTR01kx4b00000000000000000001
    type: HttpRequestActor
    version: 1
    name: Fetch user profile from Gmail
    msgVar: fetch_user_profile_from_gmail
    description: Fetches the sender's Gmail profile
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts: [{ id: SPRTdefault }]
    configuration:
      inputs:
        userId: ${{ msg.webhook_trigger.body.userId }}
      options: {}               # the type's options, reading ${{ inputs.* }}
      connection: { key: gmail-connection }
    schemas:
      inputs: { type: object, properties: { userId: { type: string, title: User ID } }, required: [userId] }
    position: { x: 0, 'y': 0 }
    edges: {}
```

- `schemas.inputs`/`outputs` are the actor's interface (editor form, templates, validation);
  `configuration.options.inputSchema`/`outputSchema` are type options (AiActor's tells the model what to return).
- **Names:** verb, object, context, proper nouns capitalized ("Fetch user profile from Gmail", "Create Issue in
  GitHub").
- A type's options and defaults: `borgiq actors schema <Type> --json`, its reference, or the generated types.

## Configuration and expressions

Order: `inputs` → `vars` → `options` → run (`results`) → `error` → `outputs` (only without an error)
([scope per step](references/context.md#scope-and-interpolation-order)). Map every upstream value into `inputs` and
declare it in `schemas.inputs`; add `vars` only for a value reused inside the actor:

```yaml
# Wrong: upstream data in vars, declared inputs left empty
vars: [{ name: '${{ msg.normalize_lead.name }}' }]
inputs: { name: '' }
options: { prompt: 'Research ${{ vars.name }}' }
# Right
inputs: { name: '${{ msg.normalize_lead.name }}' }
options: { prompt: 'Research ${{ inputs.name }}' }
```

Expressions are JavaScript over [`Q` helpers](references/q-lib.md) (`Q.toJSON`, `Q.lo`, `Q.dateFns`, …) and
standard globals (`JSON`, `Math`, `btoa`). Double-quote a value containing `: `: `a: "${{ x ? 1 : 2 }}"`.
Variables ([context.md](references/context.md)): `msg`, `err`, `ctx` (org, workspace, canvas with trigger URL maps,
actor, flowrun), `inputs`, `vars`, `credentials`, `connection`, `assets`; `trigger` only in a trigger's own
configuration; `results` only in `error` and `outputs`. Auth: `auth: ${{ connection.auth }}` with
`connection: { key, type }` ([auth-types.md](references/auth-types.md)).

## Wiring

- Edges run from a `sourcePortId` to `TPRTdefault`; ports per type and hand placement:
  [edges-and-positioning.md](references/edges-and-positioning.md). `bundle push --auto-layout` arranges the canvas.
- Failures and the `error` block (`if`, `retryIf`, `message`, `includeResult`): [error-handling.md](references/error-handling.md).
  Every actor between a split or fork and its join needs `continueOnError: true`, or the join waits forever.
- A sub-flow's `schemas.inputs` is not enforced: keep the caller's `payload`, that schema and downstream reads in
  step ([contract](references/callable-trigger-actor.md#input-schema--the-sub-flow-contract)).
- Flow shapes: [workflow-patterns.md](references/workflow-patterns.md); a whole bundle: [workflow-example.md](references/workflow-example.md).

## Code actors

DenoActor, PythonActor and UniversalTriggerActor export `receive(req)` and return a `Response`
([code-actor-runtime.md](references/code-actor-runtime.md), with the language file).

- **Source:** `configuration.codeDir`, `{ path, content }` files with one root entrypoint (`main.ts`/`main.py`), at
  most 200 files and 1 MiB, some paths reserved ([source files](references/code-actor-runtime.md#source-files-codedir));
  in a bundle, files under `code/`. Never write `configuration.code`. Deno imports stay in the actor's tree. Pin
  dependencies exactly (Deno: versions at least 7 days old).
- **Data:** values arrive as `req.inputs` from `configuration.inputs`; `results` becomes `msg.<msgVar>`; secrets are
  `req.credentials.<name>`, the connection `req.connection` ([credentials](references/code-actor-runtime.md#credentials-and-connections)).
- **Memory:** `stm` lasts one flowrun, `ltm` every flowrun; default to STM. Writing a store that is not enabled is an
  error; enabling one serializes the actor's messages; over a cap the run fails (`MemoryExceedAllowedSize`).
- **Whole flow in one actor:** a DenoActor, extra connections as `source: connection` credentials
  ([consolidating](references/code-actor-runtime.md#consolidating-a-flow-into-one-actor)).

## Storage

- **Collections hold current state:** one per app, entity key prefixes (`ticket:<id>`, `comment:<ticketId>:<at>`) and
  a `$meta` manifest row; split only for a security boundary, on request, or near the ~1,000 WCU/s partition limit.
  Keep items small, label only what you query, use what a write emits (reads are eventually consistent)
  ([design](references/collection-design.md), [actions](references/collection-actor.md), [code](references/collection-sdk.md)).
- **Streams hold what happened, in order**, never `event:<timestamp>` items. Unless created `persistent: true`, a
  stream is deleted `idleTtlSeconds` (default one hour) after its last append. `readStream` returns one page: loop
  `nextCursor` while `hasMore`, persist the cursor in a collection. Nothing fires on arrival: poll `getStreamInfo` on a
  schedule, or tail over SSE ([stream-actor.md](references/stream-actor.md)).

### Collection migrations and provisioning

Missing storage fails with `COLLECTION_NOT_FOUND`/`STREAM_NOT_FOUND`: the app works where it was hand-made and 404s
elsewhere. The [migration runner](references/collection-migrations.md) is a UniversalTriggerActor fired only by manual
invoke (`webhook.enabled: false`, `schedule.enabled: false`). It creates the collection (swallowing
`COLLECTION_ALREADY_EXISTS`) and each stream `persistent: true`, runs migrations missing from its `$migration:<id>`
ledger, seeds with `putItem` (swallowing `ITEM_ALREADY_EXISTS`, never `overwrite: true`) and rewrites `$meta`. Run it
(canvas Invoke or `borgiq triggers run`) after deploying to a new workspace or adding a migration.

## Build, deploy and debug

**Mode check.** No shell: see [Generation Instructions](#generation-instructions). Otherwise run `borgiq auth status`
(on failure the user runs `borgiq auth login`; never ask for or read the token) and `borgiq --version`. Check a
command with `borgiq help <cmd>` (`<cmd> --help` exits 0 even for unknown commands): bundles need ≥ 0.8.0, recipes
≥ 0.13.0 ([versions](references/borgiq-cli.md#cli-versions)); upgrade with `npm install -g @borgiq/cli`.

```bash
borgiq connections list --json; borgiq secrets list --json    # keys to use; ask the user for missing ones
borgiq bundle init ./my-flow.borgiq-canvas --name "My Flow" --slug my-flow   # or: bundle pull <canvas> <dir>
git init ./my-flow.borgiq-canvas     # commit the baseline, and before every push
# read README.md and AGENTS.md; edit actor.yaml, code/*, canvas.yaml
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout  # first push; later --dry-run, then push
borgiq canvases validate my-flow --json
```

- A push applies only changed actors, and nothing if one conflicts or changed on the server ([sync](references/cli/canvas-bundles.md#incremental-sync-and-conflicts)).
- Deployed workspace (`isDeployed` in `borgiq workspaces deployment --json`): `bundle push --runtime-build` or
  `bundle build`.
- Run: `borgiq triggers run --canvas <canvasId> --actor-id <triggerId> --json` (canvas ULID, no payload), then
  `flowruns status` and `flowruns summary`; payloads, test runs and debugging: [flowrun-job-states.md](references/flowrun-job-states.md).
- No bundle possible (no shell, a CLI without `bundle` that cannot upgrade, a one-off patch):
  [cli-data-formats.md](references/cli/cli-data-formats.md). Never patch out of band once a bundle exists.
- Renaming an actor: new msgVar, update every `msg.<old>` ([editing-workflows.md](references/editing-workflows.md)).
  Porting from another platform: [migration-from-automation-platforms.md](references/migration-from-automation-platforms.md).

## Generation Instructions

- **Shell:** write bundle files and validate them (rule 12). **No shell:** return one `metadata` + `actors` YAML
  document, IDs composed per [validation.md](references/validation.md), and say it is unvalidated.
- Build what was asked: one actor, or a flow planned first (a flowchart) and built one actor at a time. Keep actors
  single-purpose; suggest variants for other options.
- Keep input schemas simple; an object without defined properties is `type: any`, not `type: object`.
- Map each input from upstream; leave one empty only when nothing upstream supplies it.
- Assume values may be missing (`${{ inputs?.field }}` is then `undefined`); pass an empty array on as `undefined`:
  `"${{ inputs.items?.length > 0 ? inputs.items : undefined }}"`.
- Add `outputs` only when the user asks for custom output formatting.
- Indent with 2 spaces; use `|` for multi-line strings with special characters.
- Setup steps and prerequisites go in the bundle's `README.md`. A setup CommentActor goes above a new workflow only
  when the user wants notes on the canvas or you return a document without a bundle; never on a single-actor addition
  ([comment-actor.md](references/comment-actor.md)).
