# Canvas Bundles

Canvas bundles are the preferred way to build and maintain BorgIQ canvases when shell access and a working directory are available. A bundle expands one canvas into ordinary YAML and source files, keeps the files git-friendly, and lets `borgiq bundle push` and `pull` synchronize only changed actors with three-way (content-hash + edit-version) conflict detection.

> **CLI capability gate:** Bundle commands require a build of `@borgiq/cli` that contains BorgIQ CLI PR #37. Until that change has a published release version, detect the command instead of guessing from `borgiq --version`:
>
> ```bash
> borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
> ```
>
> If `borgiq bundle` is unavailable, use the [direct document/batch workflow](../borgiq-cli.md#direct-document-and-batch-workflow) instead.

## Contents

- [Choose bundle or direct document](#choose-bundle-or-direct-document)
- [Folder layout and ownership](#folder-layout-and-ownership)
- [Worked webhook to Deno example](#worked-webhook-to-deno-example)
- [Add and remove actors: the three-edit rule](#add-and-remove-actors-the-three-edit-rule)
- [Edges and positions belong in canvas.yaml](#edges-and-positions-belong-in-canvasyaml)
- [External code and codeDir](#external-code-and-codedir)
- [Lifecycle commands](#lifecycle-commands)
- [Incremental sync and conflicts](#incremental-sync-and-conflicts)
- [Structured output](#structured-output)
- [Templates and the starter limitation](#templates-and-the-starter-limitation)
- [Troubleshooting](#troubleshooting)

## Choose bundle or direct document

**The bundle is the default way to build a canvas.** Like a `rails new` project, a canvas starts life as a bundle folder (`bundle init` or `bundle pull`), grows through file edits, and deploys with `bundle push` — building, editing, template adoption, code work, and iteration all happen in the bundle. Reach for a direct document or batch payload only in these cases:

| Exception | Use | Why |
|---|---|---|
| No shell or filesystem access | Direct document | Generate the document for manual deployment in the BorgIQ UI. |
| Installed CLI lacks `borgiq bundle` and cannot be upgraded | Direct document/batch | The bundle compiler ships in the CLI. |
| One-off patch to a canvas nobody maintains locally, not worth pulling | Direct batch | `canvas-actors batch` avoids creating a bundle for a throwaway change. |

Do not maintain both a bundle and out-of-band batch patches for the same canvas. Once a bundle exists locally, edit it and push it so git remains the source of truth.

## Folder layout and ownership

```text
<canvas-slug>.borgiq-canvas/
├── canvas.yaml
├── actors/
│   ├── triggers/
│   │   └── webhook/
│   │       └── ACTR.../
│   │           └── actor.yaml
│   ├── tasks/
│   │   └── deno/
│   │       └── ACTR.../
│   │           ├── actor.yaml
│   │           └── code/
│   │               ├── main.ts        # required entrypoint
│   │               └── lib/format.ts  # helper files are yours to arrange
│   └── other/
├── AGENTS.md
└── .gitignore
```

Actor paths are `actors/<category>/<type-folder>/<ACTOR_ID>/`. The CLI has an exhaustive registry of 32 types across `triggers/` (10), `tasks/` (20), and `other/` (2). Type folders are kebab-case, such as `HttpRequestActor` → `actors/tasks/http-request/` and `WebhookTriggerActor` → `actors/triggers/webhook/`. Never guess a path for an unknown type; upgrade the CLI.

| Category | Actor type → type folder |
|---|---|
| `triggers` | `AppTriggerActor` → `app`; `ButtonTriggerActor` → `button`; `CallableTriggerActor` → `callable`; `EmailTriggerActor` → `email`; `InterfaceTriggerActor` → `interface`; `McpServerActor` → `mcp-server`; `ReactAppTriggerActor` → `react-app`; `ScheduledTriggerActor` → `scheduled`; `UniversalTriggerActor` → `universal`; `WebhookTriggerActor` → `webhook` |
| `tasks` | `AgentHarnessActor` → `agent-harness`; `AiActor` → `ai`; `AiAgentActor` → `ai-agent`; `AiRouterActor` → `ai-router`; `CallFlowActor` → `call-flow`; `CallableResponseActor` → `callable-response`; `CollectionActor` → `collection`; `DataStoreActor` → `data-store`; `DenoActor` → `deno`; `DenoTestActor` → `deno-test`; `DeprecatedAiAgent` → `deprecated-ai-agent`; `HttpRequestActor` → `http-request`; `InterfaceActor` → `interface`; `InterfaceStatusActor` → `interface-status`; `MessageProcessorActor` → `message-processor`; `PythonActor` → `python`; `RouterActor` → `router`; `SendEmailActor` → `send-email`; `StreamActor` → `stream`; `WebhookResponseActor` → `webhook-response` |
| `other` | `CommentActor` → `comment`; `EchoActor` → `echo` |

`actor.yaml` uses the exported, parsed-object actor shape: `configuration.options`, `inputs`, `vars`, `outputs`, `error`, credentials, and schemas are YAML objects. The YAML-strings-in-JSON shape used by `canvas-actors batch` never appears on disk.

| Surface | Ownership | Editing rule |
|---|---|---|
| `actor.yaml` | Agent/user | Edit actor semantics, configuration, schemas, ports, names, and msgVars. Do not add position, edges, or externalized code. |
| `code/*` | Agent/user | Edit actor source here: the required entrypoint plus any helper files. |
| `canvas.yaml` `canvas`, `actors[]`, `graph.nodes`, `graph.edges` | Agent/user | Edit metadata, index entries, positions, and wiring. |
| `canvas.yaml` `dependencies`, `exportErrors`, `warnings`, `sync` | CLI-owned/informational | Read them, but do not hand-edit them; pack/pull/push regenerate or refresh them. |
| In-bundle `AGENTS.md` | CLI-owned companion | Read it first. It defines format/layout mechanics for the installed CLI version and is never overwritten by pull/unpack. |
| Skill references | Skill-owned guidance | Use them for actor semantics and platform knowledge: what values belong in the files. |

The two `AGENTS.md` surfaces are complementary: the generated file inside the bundle is authoritative for that installed CLI's filesystem contract; this skill is authoritative for actor behavior, schemas, expressions, and BorgIQ platform usage.

## Worked webhook to Deno example

This reduced example shows the generated object shape and graph ownership. IDs are valid BorgIQ IDs, but mint new IDs for a real canvas.

```text
webhook-processor.borgiq-canvas/
├── canvas.yaml
├── actors/triggers/webhook/ACTR01kx4amhthtq7e17vx2ab3q53z/actor.yaml
└── actors/tasks/deno/ACTR01kx4amhtje3y49waaevm7zsw7/
    ├── actor.yaml
    └── code/
        ├── main.ts
        └── lib/shape.ts
```

`canvas.yaml` owns the positions, edge, and actor index:

```yaml
format: borgiq.canvas.bundle
formatVersion: 1
canvas:
  slug: webhook-processor
  name: Webhook Processor
  description: ""
  tags: ""
  messageTTLInDays: 7
  runtimeSlug: ""
  schemaVersion: "1"
graph:
  nodes:
    - actorId: ACTR01kx4amhthtq7e17vx2ab3q53z
      position: { x: 0, y: 0 }
    - actorId: ACTR01kx4amhtje3y49waaevm7zsw7
      position: { x: 320, y: 0 }
  edges:
    - id: EDGE01kx4amhtje3y49waaevm7zsw9
      sourceActorId: ACTR01kx4amhthtq7e17vx2ab3q53z
      sourcePortId: SPRTdefault
      targetActorId: ACTR01kx4amhtje3y49waaevm7zsw7
      targetPortId: TPRTdefault
      type: borgiqEdge
dependencies:
  runtimes: []
  connections: []
  secrets: []
exportErrors: []
warnings: []
sync:
  actors:
    ACTR01kx4amhthtq7e17vx2ab3q53z:
      editVersion: 3
      contentHash: sha256:8e14…
    ACTR01kx4amhtje3y49waaevm7zsw7:
      editVersion: 7
      contentHash: sha256:2b90…
actors:
  - id: ACTR01kx4amhtje3y49waaevm7zsw7
    type: DenoActor
    name: Process event
    path: actors/tasks/deno/ACTR01kx4amhtje3y49waaevm7zsw7
  - id: ACTR01kx4amhthtq7e17vx2ab3q53z
    type: WebhookTriggerActor
    name: Incoming webhook
    path: actors/triggers/webhook/ACTR01kx4amhthtq7e17vx2ab3q53z
```

Webhook `actor.yaml` contains no position or edges:

```yaml
id: ACTR01kx4amhthtq7e17vx2ab3q53z
version: 1
type: WebhookTriggerActor
name: Incoming webhook
msgVar: incoming_webhook
description: Receives the event to process.
isActive: true
sourcePorts:
  - id: SPRTdefault
continueOnError: false
enableLTM: false
enableSTM: false
showInWorkspaceApps: true
runtimeSlug: ""
configuration:
  webhook:
    triggerKey: 01KX4AMHTJE3Y49WAAEVM7ZSWA
    authorizationLevel: public
    allowedMethods: [get, post]
    responseTimeout: 30
  options:
    webhook:
      respondImmediately: true
      emitRawBody: false
schemas: {}
```

Deno `actor.yaml` points to its code directory and keeps configuration objects parsed:

```yaml
id: ACTR01kx4amhtje3y49waaevm7zsw7
version: 1
type: DenoActor
name: Process event
msgVar: process_event
description: Processes the incoming webhook event.
isActive: true
sourcePorts:
  - id: SPRTdefault
continueOnError: false
enableLTM: true
enableSTM: true
configuration:
  codeDir: code
  inputs: {}
  options:
    allowNet: true
    allowFs: false
schemas:
  inputs:
    type: any
```

`code/main.ts` is native, byte-preserved source, and imports its siblings relatively:

```typescript
import type { Request, Response } from '@borgiq/actors';

import { shapeEvent } from './lib/shape.ts';

export default async function receive(req: Request): Promise<Response> {
  return { results: { event: shapeEvent(req.inputs) }, memory: req.memory };
}
```

```typescript
// code/lib/shape.ts
export const shapeEvent = (inputs: unknown) => ({ receivedAt: new Date().toISOString(), inputs });
```

## Add and remove actors: the three-edit rule

Mint IDs before adding an actor:

```bash
borgiq generate id actor
borgiq generate id edge
```

Adding an actor requires three structural edits, plus optional wiring:

1. Create `actors/<category>/<type-folder>/<newId>/actor.yaml` and, when the type carries code, its `code/` entrypoint (`main.ts` / `main.py`, or App's three fixed files).
2. Add the actor to `canvas.yaml` `actors[]`.
3. Add one position to `canvas.yaml` `graph.nodes`.
4. Add `graph.edges` entries to wire it.

Example for a new HTTP task:

```diff
+ actors/tasks/http-request/ACTR01kx4b00000000000000000001/actor.yaml
+ id: ACTR01kx4b00000000000000000001
+ version: 1
+ type: HttpRequestActor
+ name: Notify API
+ msgVar: notify_api
+ isActive: true
+ sourcePorts:
+   - id: SPRTdefault
+ continueOnError: false
+ configuration:
+   options:
+     url: https://example.com/events
+     method: POST
+     body: ${{ msg.process_event }}
+ schemas:
+   inputs:
+     type: any

 canvas.yaml
 actors:
+  - id: ACTR01kx4b00000000000000000001
+    type: HttpRequestActor
+    name: Notify API
+    path: actors/tasks/http-request/ACTR01kx4b00000000000000000001
 graph:
   nodes:
+    - actorId: ACTR01kx4b00000000000000000001
+      position: { x: 640, y: 0 }
   edges:
+    - id: EDGE01kx4b00000000000000000002
+      sourceActorId: ACTR01kx4amhtje3y49waaevm7zsw7
+      sourcePortId: SPRTdefault
+      targetActorId: ACTR01kx4b00000000000000000001
+      targetPortId: TPRTdefault
+      type: borgiqEdge
```

Removing an actor is the inverse: delete its actor folder, its `actors[]` entry, its `graph.nodes` entry, and every edge that targets or originates from it. Then search the whole bundle for its actor ID, msgVar, and `msg.<msgVar>` references before validating.

## Edges and positions belong in canvas.yaml

> **Bundle rule:** Edges live only in `canvas.yaml` `graph.edges`, and positions live only in `canvas.yaml` `graph.nodes`. Never put `edges` or `position` in an actor folder.

This intentionally differs from exported canvas documents and CanvasActor mutation payloads, where each source actor carries its own `edges` and `position`. The bundle compiler projects those fields into the root graph and restores them during pack/push.

For every edge:

- `sourceActorId` and `targetActorId` must name indexed actors.
- `sourcePortId` must exactly match an ID in the source actor's `sourcePorts`.
- `targetPortId` is normally `TPRTdefault`.
- Edge IDs are unique BorgIQ edge IDs minted with `borgiq generate id edge`.

## External code and codeDir

When code is externalized, `actor.yaml` carries the marker `configuration.codeDir: code` and the source lives in files under the actor's `code/` directory. That directory is either a **project tree** the actor owns freely, or a **fixed set of files** for the one type that still has one:

| Actor type | Shape of `code/` | Restored on pack |
|---|---|---|
| `DenoActor` | project tree; required entrypoint `main.ts` | `configuration.codeDir` — an array of `{path, content}` |
| `DenoTestActor` | project tree; required entrypoint `main.ts` | `configuration.codeDir` |
| `UniversalTriggerActor` | project tree; required entrypoint `main.ts` | `configuration.codeDir` |
| `PythonActor` | project tree; required entrypoint `main.py` | `configuration.codeDir` |
| `ReactAppTriggerActor` | a whole Vite project (no required entrypoint filename) | `configuration.codeDir` |
| `AppTriggerActor` | the three fixed files `index.html`, `styles.css`, `script.js` | `configuration.options.html`, `.css`, `.script` when those values are inline strings |

Rules:

- Edit code in `code/`, never inline in `actor.yaml`.
- `codeDir` in `actor.yaml` must be exactly the marker string `code`.
- Do not keep `configuration.code` and `code/` files together; that dual source is a hard error.
- App fields that are BorgIQ file-reference objects remain in `actor.yaml`; only inline string fields are externalized.

### Code actor project trees

Deno, Deno Test, Universal Trigger, and Python actors hold a small project, not one file: the entrypoint at the root of `code/`, plus any helper files and folders.

```text
actors/tasks/deno/ACTR.../
├── actor.yaml            # configuration.codeDir: code
└── code/
    ├── main.ts           # required — exports the default handler
    ├── lib/format.ts
    └── lib/nested/constants.ts
```

- **The entrypoint is required and matched exactly**: `code/main.ts` for Deno, Deno Test, and Universal Trigger actors, `code/main.py` for Python actors. `bundle validate` errors when it is absent; `Main.ts` is a different file, not a near-miss.
- **Import between your own files with ordinary relative imports** — `import { format } from './lib/format.ts'` in Deno (extension included), `from lib.format import format` in Python (a package directory needs `__init__.py`). Imports may not leave `code/`; reach anything else through registry specifiers (`npm:`, `jsr:`, `https`) in Deno, or `configuration.options.dependencies` in Python.
- **UTF-8 text only**, at most **200 files** and **1 MiB** of source in total across the tree.
- **Reserved filenames** — the BorgIQ runtime writes its own files into the same directory, so these names are rejected (case-insensitively) by `bundle validate` and by the API on save:

  | Family | Reserved |
  |---|---|
  | Deno, Deno Test, Universal Trigger | `server.ts`, `handler.ts`, `actor.ts`, `main_test.ts`, `deno.json`, `deno.jsonc`, `deno.lock`, `package.json`, anything under `shared/` or `node_modules/` |
  | Python | `server.py`, `handler.py`, `borgiq.py`, `pyproject.toml`, `.python-version`, `uv.lock`, anything under `.borgiq/`, `.venv/` or `borgiq/` |

  Python dependencies belong in `configuration.options.dependencies`, which is why a `pyproject.toml` of your own is reserved rather than merged.
- **Local tooling output is never synced.** `node_modules/`, `dist/`, `.vite/`, `.venv/`, `__pycache__/`, `.git/`, and lockfiles (`deno.lock`, `uv.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lock*`) under `code/` are left alone by pull, push, and `--replace`.
- **Two paths that differ only in letter case** cannot both exist on a case-insensitive filesystem, so the bundle rejects them.

### Multi-file requires a current CLI

Multi-file code needs a `@borgiq/cli` new enough to represent it. There is no separate probe for that — `borgiq bundle --help` only tells you the bundle commands exist at all. What you get instead is a clear failure at the moment it matters, so upgrade (`npm install -g @borgiq/cli`) when you see one:

- An **older CLI** pulling a canvas whose code actors are multi-file leaves the file list inline in `actor.yaml` and then refuses to pack or push it (`configuration.codeDir must be 'code'`). Upgrade; do not hand-edit around it. A CLI that supports multi-file never does that silently: when it meets a code shape it cannot represent it fails the operation with an explicit "upgrade `@borgiq/cli`" message rather than writing a bundle that would drop files on the next push.
- A **bundle pulled before multi-file support** has `code/mod.ts` (or `code/mod.py`). Rename it to `main.ts` (or `main.py`) — `bundle validate` says so in the error — and push. The old name is just another project file now.
- A canvas whose code actors the platform has **not converted yet** pulls into the same project layout, with the actor's source written to its entrypoint file; the first push afterwards converts the actor. Expect one pending update per such actor even before you edit anything.
- The bundle's generated `AGENTS.md` and `.gitignore` are only created when missing, so a bundle created before this release keeps its old copies. Update them by hand or delete them and re-pull.

## Lifecycle commands

Initialize git after `init` or `pull`, commit that baseline, and commit local edits before each push. After push, review and commit any refreshed actor/version metadata written by the implicit pull. Git is the recovery path when you accept server versions with `pull --replace` over colliding local edits.

### New canvas

```bash
borgiq bundle init ./my-flow.borgiq-canvas --name "My Flow" --slug my-flow
git init ./my-flow.borgiq-canvas
git -C ./my-flow.borgiq-canvas add .
git -C ./my-flow.borgiq-canvas commit -m "chore: initialize BorgIQ canvas bundle"
# Edit actor.yaml, code/*, and canvas.yaml.
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout
borgiq canvases validate my-flow --json
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
```

`bundle init` produces exactly one starter shape: webhook trigger → Deno task, plus an unconnected HTTP test-sender. It already passes `bundle validate --strict` and is immediately pushable.

### Existing canvas

```bash
borgiq bundle pull my-flow ./my-flow.borgiq-canvas
git init ./my-flow.borgiq-canvas
git -C ./my-flow.borgiq-canvas add .
git -C ./my-flow.borgiq-canvas commit -m "chore: pull BorgIQ canvas baseline"
# Edit files and commit the intended change.
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --dry-run
borgiq bundle push ./my-flow.borgiq-canvas   # add --auto-layout when actors were added, removed, or rewired
borgiq canvases validate my-flow --json
borgiq triggers run --canvas <canvasId> --actor-id <triggerActorId> --json
```

**On a deployed workspace, add `--runtime-build`.** Deployed workspaces run each canvas's last
runtime build rather than its current code, so a push alone does not change what triggers execute:

```bash
borgiq workspaces deployment --json                       # is this workspace deployed?
borgiq bundle push ./my-flow.borgiq-canvas --runtime-build  # push, then build, and wait
```

`--runtime-build` is ignored with `--dry-run` and `--mode`, and a build failure does not fail the
push — the canvas simply keeps running its previous build. See
[deployment.md](../deployment.md).

### Iterate and debug

```bash
# Edit files, then:
borgiq bundle validate ./my-flow.borgiq-canvas
git -C ./my-flow.borgiq-canvas add .
git -C ./my-flow.borgiq-canvas commit -m "fix: adjust actor configuration"
borgiq bundle push ./my-flow.borgiq-canvas
borgiq flowruns summary <flowrunId> --json
borgiq flowrun-jobs runtime-data <jobId> --root-path inputs --json
# Repeat edit -> validate -> commit -> push -> test.
```

Use `bundle pack <dir> -o export.yaml` to compile a bundle without deploying, and `bundle unpack <file|-> <dir>` to expand an existing export document.

## Incremental sync and conflicts

Bare `bundle push` and `bundle pull` use three-way incremental sync. `canvas.yaml` `sync.actors` records, per actor, the last-synced server `editVersion` and a `contentHash` baseline (not the actor's exported `version` field). Comparing local and server content against that baseline distinguishes local-only edits, server-only edits, concurrent edits, and edit-versus-delete cases:

| Case | How it is recognized | `push` | `pull` |
|---|---|---|---|
| Unchanged | Local and server content hashes match | Skip | Skip without touching file mtimes |
| Local edit | Local differs from baseline; server matches baseline | Update with `editVersion` | Keep local; push publishes it |
| Server edit | Local matches baseline; server differs | Abort; run `bundle pull` first | Rewrite that actor from server |
| Concurrent edit | Both sides differ from the baseline | Abort as a conflict | Abort as a conflict |
| New local | Actor exists only locally, no baseline entry | Add | Keep local and merge its graph slice |
| New server | Actor exists only on server, no baseline entry | Abort; run `bundle pull` first | Write it locally |
| Deleted locally | Absent locally; server matches baseline | Remove from server | Keep it deleted |
| Deleted on server | Absent on server; local matches baseline | Abort; run `bundle pull` first | Delete the local actor folder |
| Edit vs delete | One side edited and the other deleted, relative to baseline | Abort as a conflict | Abort as a conflict |
| Baseline missing | Content differs and no `sync.actors` entry exists | Abort as a conflict (fail closed) | Abort as a conflict |

Before applying a normal push, the CLI validates, fetches the server canvas and actor versions, computes the whole plan, and checks every actor. If any actor is conflicted **or carries a server-side change the bundle has not seen** (server edit, new server actor, deleted on server), the push applies **nothing** and reports every blocking actor with its verdict. Resolve deliberately:

- **First run bare `borgiq bundle pull <canvas> <dir>`.** It is the safe remedy: it applies server-only changes, keeps pure local edits and additions, and aborts (writing nothing) only when an actor has both local and server changes. If it completes, re-push.
- For actors that remain conflicted after a pull attempt: `borgiq bundle pull <canvas> <dir> --replace` for server wins (rewrites every managed path from the server — commit local state to git first and recover prior local versions with git), or `borgiq bundle push <dir> --force-local` for local wins (still carries `editVersion`, so an edit racing the apply can surface as a server conflict).
- Run `push --dry-run` or `pull --dry-run` to preview without writes/mutations.

Push also fails closed when the baseline itself is unusable: a bundle without `sync.actors` ("no content-hash sync baseline" warning — pull first to establish it), or a server export that reports actor errors ("the sync baseline is incomplete").

After a successful push, the CLI performs an implicit incremental pull to refresh local files and the `sync.actors` baseline. Avoid `--no-refresh` unless debugging a specific issue. Use `push --mode merge|insert|replace` only to opt into legacy whole-document import. `pull --replace` performs a full managed-path rewrite from the server — it is the server-wins conflict resolution.

## Structured output

Default push/pull output is compact and safe to inspect in an LLM context. Across plan, conflict, and applied-result paths it includes:

- mode, target, and summary counts;
- actor entries with `actorId`, `name`, verdict, bundle version, and server version on dry-run/conflict plans;
- conflict reports and compact operation summaries (`type`, `actorId`, `editVersion`);
- metadata delta, compact batch/layout results, and refresh write/delete paths when applicable.

It excludes actor bodies, code, prompts, schemas, app HTML/CSS/JS, generated mutation `data`, timestamps, API `actorData`, and merged conflict payloads. `--dry-run` uses the same compact contract.

Use `bundle push --raw` only when debugging operation or API payload generation. Do not dump raw output into model context without a specific need; it can contain every actor body and large code/prompt payloads.

## Templates and the starter limitation

`bundle init` has no `--template` flag and ships only the webhook → Deno + test-sender starter. Stay in the bundle to start from a different shape: run `bundle init`, then reshape it with the [three-edit rule](#add-and-remove-actors-the-three-edit-rule) — replace the starter actors with the ones the flow needs.

To seed an actor from the published template catalog:

1. Fetch the template with `borgiq templates get <templateId> --json`. Its `actor` payload is already in the ExportedCanvasActor object shape that `actor.yaml` uses.
2. Write that actor as the new folder's `actor.yaml`, then fix it up for the bundle:
   - Remove any `edges`/`position` fields — the graph lives in `canvas.yaml`.
   - Mint a fresh `id` with `borgiq generate id actor`.
   - Replace every trigger key in the payload — top-level `webhookTriggerKey` and `configuration.webhook.triggerKey` — with a fresh `borgiq generate id webhooktriggerkey` value. Never keep the template's key.
   - Keep or add the top-level `template: { id, version, appName }` provenance block using the values from the `templates get` payload; it drives the app-type badge and version check in the UI.
3. Complete the three-edit rule and wire the actor in `graph.edges`.

`borgiq scaffold actor-from-template` performs these same fixups but emits the CanvasActor YAML-string mutation shape — use it for the direct/batch path, not for bundle files.

## Troubleshooting

### Bundle command is missing

```bash
borgiq bundle --help >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"
```

Upgrade `@borgiq/cli`. If upgrading is not possible, fall back to direct documents/batch operations.

### Validation reports a file path

Bundle validation is offline and reports every finding against the responsible path. In JSON mode the shape is equivalent to:

```json
{
  "valid": false,
  "errors": [
    {
      "path": "actors/tasks/deno/ACTR.../code/main.ts",
      "message": "..."
    }
  ],
  "warnings": []
}
```

Fix the named file, not a packed export. Common misses are an indexed actor without `actor.yaml`, an actor without exactly one `graph.nodes` entry, a dangling edge, a source port not declared by the source actor, an invalid `codeDir` marker, a code actor whose `code/` tree has no entrypoint file, or a reserved filename under `code/`.

### Code actor code/ errors

| Message | Fix |
|---|---|
| `DenoActor needs an entrypoint file at code/main.ts` | Add it. If the message continues `- rename code/mod.ts to code/main.ts`, the bundle predates multi-file support: rename that file. |
| `'server.ts' is reserved by the BorgIQ runtime and may not appear in a bundle.` | Rename the file. The runtime owns that name — see the reserved table above. |
| `Both configuration.code and codeDir project files are present - remove one source.` | Delete the inline `configuration.code` from `actor.yaml`; the files under `code/` are the source of truth. |
| `Inline configuration.code is not supported for DenoActor - move the source into code/main.ts and set configuration.codeDir: code.` | Move the string into the entrypoint file and set the marker. |
| `Actor type DenoActor carries multi-file actor code, which this CLI version cannot represent - upgrade @borgiq/cli.` | Upgrade the CLI; this bundle was written by a newer one. |

### Unknown actor type

`Unknown actor type 'X' - this CLI version does not support it; upgrade @borgiq/cli` means the installed 32-type registry predates that platform actor type. Upgrade the CLI; do not invent a folder path.

### Push conflict report

A conflict resembles:

```text
Push aborted: 1 actor conflict(s). Re-pull, or re-run with --force-local for local wins.
  ACTR... (Process event): concurrent-edit; bundle editVersion 7 -> server editVersion 8
```

No actor operation is applied by the preflight-conflicted push. Read each actor's verdict:

- `server-edit`, `new-server`, `deleted-on-server` — the server moved ahead; bare `bundle pull` applies these safely, then re-push.
- `concurrent-edit`, `local-edit-server-delete`, `local-delete-server-edit`, `baseline-missing` — true conflicts; choose `bundle pull --replace` (server wins) or review git and re-run `bundle push --force-local` (local wins).

### Missing or incomplete sync baseline

`Warning: this bundle has no content-hash sync baseline` means `canvas.yaml` has no `sync.actors` block (e.g. a hand-built or pre-sync bundle); existing actors whose content differs from the server fail closed as conflicts. `Push aborted: the server export reported N actor error(s), so the sync baseline is incomplete` means the server could not export cleanly. In both cases run `bundle pull` first to establish a clean baseline, and never hand-edit `sync.actors`.

### Target directory is not empty

- `bundle init` always requires a fresh, empty directory; it has no `--force` flag.
- `bundle pull` can sync into an existing bundle containing `canvas.yaml` without `--force`, touching only managed paths (`canvas.yaml`, `actors/`).
- `bundle unpack` into an existing bundle always requires `--force` to replace its managed files.
- A non-empty target without `canvas.yaml` requires `--force` for pull and unpack. Even then, unmanaged files, `.git/`, `AGENTS.md`, and `.gitignore` are preserved; companion files are created only when missing.
