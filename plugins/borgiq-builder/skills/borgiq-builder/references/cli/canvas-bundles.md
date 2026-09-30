# Canvas Bundles

A canvas bundle expands one canvas into YAML and source files for git; `borgiq bundle push` and `pull` sync only the
changed actors, with three-way conflict detection. Read this to choose between a bundle and a direct document, to
start or pull a bundle, add actors, adapt templates, and resolve sync conflicts. Inside a bundle, read its `README.md`
(the canvas's own documentation) first, then its `AGENTS.md`: the CLI writes that file as the format contract of the
installed version, including the React App project, assets, thumbnails and what the CLI never touches.

Bundles need `@borgiq/cli` ≥ 0.8.0 (later floors: [CLI versions](../borgiq-cli.md#cli-versions)). Check with
`borgiq help bundle >/dev/null 2>&1 || echo "upgrade: npm install -g @borgiq/cli"`; without it, use the
[direct path](cli-data-formats.md).

## Contents

- [Choose bundle or direct document](#choose-bundle-or-direct-document)
- [Lifecycle commands](#lifecycle-commands)
- [Folder layout and ownership](#folder-layout-and-ownership)
- [Add and remove actors: the three-edit rule](#add-and-remove-actors-the-three-edit-rule)
- [Edges and positions belong in canvas.yaml](#edges-and-positions-belong-in-canvasyaml)
- [External code and codeDir](#external-code-and-codedir)
- [Templates and the starter limitation](#templates-and-the-starter-limitation)
- [Incremental sync and conflicts](#incremental-sync-and-conflicts)
- [Troubleshooting](#troubleshooting)

## Choose bundle or direct document

Build every canvas as a bundle: start it with `bundle init` or `bundle pull`, grow it by editing files, deploy it
with `bundle push`. The exceptions: with no shell or filesystem, write a direct document for the user to deploy in the
BorgIQ UI; with a CLI that lacks `borgiq bundle` (the bundle compiler ships in the CLI) and cannot be upgraded, use
direct documents or batch payloads; for a one-off patch to a canvas nobody maintains locally, `canvas-actors batch`
saves creating a bundle. Never also patch a canvas out of band once a bundle exists: edit and push it, so git stays
the source of truth.

## Lifecycle commands

```bash
borgiq bundle init ./my-flow.borgiq-canvas --name "My Flow" --slug my-flow   # new canvas, or:
borgiq bundle pull my-flow ./my-flow.borgiq-canvas                           # existing canvas
git init ./my-flow.borgiq-canvas   # then add and commit the baseline
# Edit actor.yaml, code/* and canvas.yaml; commit the intended change.
borgiq bundle validate ./my-flow.borgiq-canvas --strict
borgiq bundle push ./my-flow.borgiq-canvas --create --auto-layout   # first push of a new canvas
borgiq bundle push ./my-flow.borgiq-canvas --dry-run                # later: preview, then push without --dry-run
                                                                    # (--auto-layout when actors were added, removed or rewired)
borgiq canvases validate my-flow --json
```

Then run and debug the flow ([flowrun-job-states.md](../flowrun-job-states.md)) and repeat edit → validate → commit →
push → test.

- **Git is the recovery path.** Commit after `init` or `pull` and before each push. After a push, review and commit the
  actor and version metadata its implicit pull refreshed.
- **`bundle init`** needs an empty directory and has no `--force`. It writes one starter: a webhook trigger → Deno
  task, plus an unconnected HTTP test-sender. It passes `bundle validate --strict` and can be pushed as is.
- **Deployed workspace:** a push changes nothing that runs until the canvas is built. Use
  `bundle push --runtime-build`, or `bundle build`, which pushes and then runs the build this workspace needs
  ([deployment.md](../deployment.md)).
- **Pack and unpack.** `bundle pack <dir> -o export.yaml` compiles a bundle without deploying it;
  `bundle unpack <file|-> <dir>` expands an export document.
- **Duplicate a canvas:** `borgiq canvases export <canvas> --json | borgiq bundle unpack - ./copy.borgiq-canvas`, set a
  new `canvas.name` and `canvas.slug` in `canvas.yaml` (both unused in the workspace), then
  `borgiq bundle push ./copy.borgiq-canvas --create`. Actor IDs are kept; they only need to be unique within a canvas.
- **Output**, `--dry-run` included, is compact (counts, per-actor verdicts, conflicts, written paths; no actor bodies
  or code). `push --raw`
  prints full API payloads: only for debugging, and keep it out of model context.

## Folder layout and ownership

A bundle is `<canvas-slug>.borgiq-canvas/` holding `canvas.yaml`, one folder per actor at
`actors/<category>/<type-folder>/<ACTOR_ID>/` (`actor.yaml`, plus `code/` for code actors), `README.md`, and the
CLI's `AGENTS.md`, `CLAUDE.md` (`@AGENTS.md`) and `.gitignore`. Type folders come from the CLI's registry of 32 types;
never guess one for a type not listed, upgrade the CLI.

| Category | Actor type → type folder |
|---|---|
| `triggers` | `AppTriggerActor` → `app`; `ButtonTriggerActor` → `button`; `CallableTriggerActor` → `callable`; `EmailTriggerActor` → `email`; `InterfaceTriggerActor` → `interface`; `McpServerActor` → `mcp-server`; `ReactAppTriggerActor` → `react-app`; `ScheduledTriggerActor` → `scheduled`; `UniversalTriggerActor` → `universal`; `WebhookTriggerActor` → `webhook` |
| `tasks` | `AgentHarnessActor` → `agent-harness`; `AiActor` → `ai`; `AiAgentActor` → `ai-agent`; `AiRouterActor` → `ai-router`; `CallFlowActor` → `call-flow`; `CallableResponseActor` → `callable-response`; `CollectionActor` → `collection`; `DataStoreActor` → `data-store`; `DenoActor` → `deno`; `DenoTestActor` → `deno-test`; `DeprecatedAiAgent` → `deprecated-ai-agent`; `HttpRequestActor` → `http-request`; `InterfaceActor` → `interface`; `InterfaceStatusActor` → `interface-status`; `MessageProcessorActor` → `message-processor`; `PythonActor` → `python`; `RouterActor` → `router`; `SendEmailActor` → `send-email`; `StreamActor` → `stream`; `WebhookResponseActor` → `webhook-response` |
| `other` | `CommentActor` → `comment`; `EchoActor` → `echo` |

`canvas.yaml` holds `format: borgiq.canvas.bundle`, `formatVersion: 1`, the `canvas` metadata (`slug`, `name`,
`description`, `tags`, `messageTTLInDays`, `runtimeSlug`, `schemaVersion`), `graph.nodes` (`{ actorId, position }`),
`graph.edges`, the actor index `actors[]` (`{ id, type, name, path }`), and the CLI's `dependencies`, `exportErrors`,
`warnings` and `sync.actors`. `actor.yaml` uses the exported, parsed-object actor shape: `configuration.options`,
`inputs`, `vars`, `outputs`, `error`, credentials and schemas are YAML objects; the YAML-strings-in-JSON shape of
`canvas-actors batch` never appears on disk. The starter `bundle init` writes (a webhook trigger → Deno task) shows
every file shape, `code/main.ts` included.

**Yours to edit:** `actor.yaml` (semantics, configuration, schemas, ports, name, msgVar; never position, edges or
externalized code), `code/*`, and in `canvas.yaml` the `canvas` metadata, the `actors[]` index, `graph.nodes` and
`graph.edges`; also [`README.md`](#the-canvas-readme) and [app thumbnails](#app-thumbnails). **The CLI's:**
`canvas.yaml` `dependencies`, `exportErrors`, `warnings` and `sync` (read them; pack, pull and push regenerate them),
and `AGENTS.md`, `CLAUDE.md` and `.gitignore`, created only when missing and never overwritten (a bundle from an older
CLI keeps old copies: delete them and pull again). Actor behavior, schemas and expressions come from the skill
references.

### The canvas README

`README.md` is the canvas's `readme` metadata (the web editor's README tab) as a file: what *this canvas* is for and
the rules its author set. Read it before changing a canvas you did not build; keep it and its table of contents
current when you change what it describes. It is managed: push uploads it (last writer wins, like `description`),
pull overwrites it or deletes it when the canvas has none, so keep other notes in a file such as `NOTES.md`.
`bundle init` seeds one; a CLI older than 0.12.0 ignores it.

### App thumbnails

An App or React App actor's thumbnail is `thumbnail.<png|jpg|webp|gif>` beside its `actor.yaml`, which names it
(`thumbnail: thumbnail.webp`). Replace the file (and the name, if the extension changed) to change it; delete the file
**and** the line to remove it (push then sends `thumbnail: null`). An unnamed file is not pushed (validate warns); a name without its file is a validate
error. Type and size are only warned about locally: the API reads the type from the bytes and decides. The image
round-trips byte for byte. A CLI older than 0.12.0 keeps it inline (`thumbnail: { dataUrl: … }`), which still pushes.
Capture and limits: the `borgiq-react-app-builder` skill, *App thumbnail*.

## Add and remove actors: the three-edit rule

Mint IDs first: `borgiq generate id actor`, `borgiq generate id edge`. Adding an actor takes three edits, plus wiring:

1. Create `actors/<category>/<type-folder>/<newId>/actor.yaml` and, for a type that carries code, its `code/`
   entrypoint (`main.ts` / `main.py`, or an App actor's three fixed files).
2. Add the actor to `canvas.yaml` `actors[]`.
3. Add one position to `canvas.yaml` `graph.nodes`.
4. Wire it with `graph.edges` entries.

```diff
+ actors/tasks/http-request/ACTR01kx4b00000000000000000001/actor.yaml
+ id: ACTR01kx4b00000000000000000001
+ version: 1
+ type: HttpRequestActor
+ name: Notify API
+ msgVar: notify_api
+ isActive: true
+ sourcePorts: [{ id: SPRTdefault }]
+ continueOnError: false
+ configuration:
+   options: { url: https://example.com/events, method: POST, body: "${{ msg.process_event }}" }
+ schemas: { inputs: { type: any } }

 canvas.yaml
 actors:
+  - { id: ACTR01kx4b00000000000000000001, type: HttpRequestActor, name: Notify API, path: actors/tasks/http-request/ACTR01kx4b00000000000000000001 }
 graph:
   nodes:
+    - { actorId: ACTR01kx4b00000000000000000001, position: { x: 640, y: 0 } }
   edges:
+    - { id: EDGE01kx4b00000000000000000002, sourceActorId: ACTR01kx4amhtje3y49waaevm7zsw7, sourcePortId: SPRTdefault,
+        targetActorId: ACTR01kx4b00000000000000000001, targetPortId: TPRTdefault, type: borgiqEdge }
```

To remove an actor, delete its folder, its `actors[]` entry, its `graph.nodes` entry and every edge to or from it.
Then search the whole bundle for its actor ID, msgVar and `msg.<msgVar>` before validating.

## Edges and positions belong in canvas.yaml

> **Bundle rule:** edges live only in `canvas.yaml` `graph.edges`, positions only in `graph.nodes`. Never put `edges`
> or `position` in an actor folder.

Exported documents and CanvasActor payloads keep `edges` and `position` on each source actor instead; the bundle
compiler moves them into the root graph and restores them on pack and push. For every edge:

- `sourceActorId` and `targetActorId` name indexed actors;
- `sourcePortId` exactly matches an ID in the source actor's `sourcePorts`;
- `targetPortId` is normally `TPRTdefault`;
- the edge ID is minted with `borgiq generate id edge`.

## External code and codeDir

Externalized code leaves the marker `configuration.codeDir: code` in `actor.yaml` and the source in files under the
actor's `code/` directory:

| Actor type | Shape of `code/` | Restored on pack into |
|---|---|---|
| `DenoActor`, `DenoTestActor`, `UniversalTriggerActor` | project tree; required entrypoint `main.ts` | `configuration.codeDir`, an array of `{path, content}` |
| `PythonActor` | project tree; required entrypoint `main.py` | `configuration.codeDir` |
| `ReactAppTriggerActor` | a whole Vite project (no fixed entrypoint name; see the bundle's `AGENTS.md`) | `configuration.codeDir` |
| `AppTriggerActor` | the three fixed files `index.html`, `styles.css`, `script.js` | `configuration.options.html`, `.css`, `.script`, when those are inline strings |

- Edit code in `code/`, never inline in `actor.yaml`. The marker must be exactly `code`.
- Never keep `configuration.code` and `code/` files together: that is a hard error.
- App fields that are BorgIQ file-reference objects stay in `actor.yaml`; only inline strings are externalized.

### Code actor project trees

Deno, Deno Test, Universal Trigger and Python actors hold a small project under `code/`: the entrypoint at its root
(`main.ts` exporting the default handler, or `main.py`) plus any helper files and folders, imported relatively and
never from outside `code/` (`import { format } from './lib/format.ts'`, extension included; `from lib.format import
format`, where a package directory needs `__init__.py`). The runtime's rules apply unchanged: UTF-8 text, at most 200
files and 1 MiB, no reserved filenames (the runtime writes its own files beside yours). They are listed in
[code-actor-runtime.md → Source files](../code-actor-runtime.md#source-files-codedir). In a bundle:

- `bundle validate` rejects a missing entrypoint or a reserved name offline. The API only warns on save, but the
  runtime refuses to run such an actor, and `canvases validate` blocks a missing entrypoint. The entrypoint name is
  matched exactly: `Main.ts` is another file.
- Two paths that differ only in letter case are rejected: they cannot coexist on a case-insensitive filesystem.
- Local tooling output (`node_modules/`, `.venv/`, lockfiles, …) is never synced; the bundle's `AGENTS.md` lists it.

**Multi-file code needs CLI ≥ 0.10.0.** An older CLI leaves the file list inline in `actor.yaml` and refuses to push
it (`configuration.codeDir must be 'code'`): upgrade, do not edit around it. A current CLI fails with "upgrade
`@borgiq/cli`" on a code shape it cannot represent rather than drop files. A bundle pulled before multi-file support
has `code/mod.ts` (`mod.py`): rename it to `main.ts` (`main.py`). An actor whose only source is a legacy
`configuration.code` string is not converted for you: it stays in `actor.yaml`, and `bundle validate` names the
entrypoint file to move it into ([below](#code-actor-code-errors)).

## Templates and the starter limitation

`bundle init` has no `--template` flag. To start from another shape, run `bundle init` and replace the starter actors
using the [three-edit rule](#add-and-remove-actors-the-three-edit-rule). To seed an actor from the template catalog
([search](../borgiq-cli.md#start-from-a-template)):

1. `borgiq templates get <templateId> --json`: its `actor` is already in the object shape `actor.yaml` uses.
2. Write it as the new folder's `actor.yaml`, then:
   - remove `edges` and `position` (the graph lives in `canvas.yaml`);
   - mint a fresh `id` with `borgiq generate id actor`;
   - replace every trigger key, the top-level `webhookTriggerKey` and `configuration.webhook.triggerKey`, with a fresh
     `borgiq generate id webhooktriggerkey`; never keep the template's key;
   - keep or add the top-level `template: { id, version, appName }` block from the `templates get` payload: it drives
     the app badge and version check in the UI.
3. Finish the three-edit rule and wire the actor in `graph.edges`.

`borgiq scaffold actor-from-template` makes the ID and provenance fixups but emits the YAML-string CanvasActor shape
and replaces only a top-level `webhookTriggerKey`: use it for the direct path, not for bundle files.

## Incremental sync and conflicts

`canvas.yaml` `sync.actors` keeps, per actor, the last-synced server `editVersion` and a `contentHash` baseline (not
the actor's `version`). Bare `bundle push` and `pull` compare local and server content with it:

| Case | Recognized by | `push` | `pull` |
|---|---|---|---|
| Unchanged | Local and server hashes match | Skip | Skip (file mtimes untouched) |
| Local edit | Local differs from baseline; server matches it | Update with `editVersion` | Keep local |
| Server edit | Local matches baseline; server differs | Abort: pull first | Rewrite that actor from the server |
| Concurrent edit | Both differ from the baseline | Abort: conflict | Abort: conflict |
| New local | Only local, no baseline entry | Add | Keep local and merge its graph slice |
| New server | Only on the server, no baseline entry | Abort: pull first | Write it locally |
| Deleted locally | Absent locally; server matches baseline | Remove from the server | Keep it deleted |
| Deleted on server | Absent on the server; local matches baseline | Abort: pull first | Delete the local folder |
| Edit vs delete | One side edited, the other deleted | Abort: conflict | Abort: conflict |
| Baseline missing | Content differs and no `sync.actors` entry | Abort: conflict (fail closed) | Abort: conflict |

Push plans every actor first. If any is conflicted **or has a server change the bundle has not seen**, it applies
**nothing** and reports every blocking actor. Resolve deliberately:

1. **Run a bare `borgiq bundle pull <canvas> <dir>`.** It applies server-only changes, keeps pure local edits and
   additions, and aborts, writing nothing, only when an actor has both local and server changes. If it completes,
   push again.
2. For actors still conflicted: `borgiq bundle pull <canvas> <dir> --replace` for server wins (it rewrites every
   managed path from the server; commit first and recover local versions from git), or
   `borgiq bundle push <dir> --force-local` for local wins (it still sends `editVersion`, so an edit racing the apply
   can still conflict). Never pick either automatically.
3. `push --dry-run` and `pull --dry-run` preview without writing or mutating.

Push also fails closed without a usable baseline ([below](#missing-or-incomplete-sync-baseline)). After a successful
push the CLI pulls to refresh files and baseline (keep it: avoid `--no-refresh`). `push --mode merge|insert|replace`
opts into the legacy whole-document import.

## Troubleshooting

### Validation reports a file path

`bundle validate` is offline and reports each finding against the file responsible (`--json`:
`{ valid, errors: [{ path, message }], warnings }`). Fix the named file, not a packed export. Common misses: an indexed
actor without `actor.yaml`, an actor without exactly one `graph.nodes` entry, a dangling edge, a source port the
source actor does not declare, a bad `codeDir` marker, a code actor without its entrypoint, a reserved filename.

### Code actor code/ errors

| Message | Fix |
|---|---|
| `DenoActor needs an entrypoint file at code/main.ts` | Add it. If it continues `- rename code/mod.ts to code/main.ts`, the bundle predates multi-file support: rename that file |
| `'server.ts' is reserved by the BorgIQ runtime and may not appear in a bundle.` | Rename the file ([reserved names](#code-actor-project-trees)) |
| `Both configuration.code and codeDir project files are present - remove one source.` | Delete the inline `configuration.code`; the files under `code/` are the source |
| `Inline configuration.code is not supported for DenoActor - move the source into code/main.ts and set configuration.codeDir: code.` | Move the string into the entrypoint file and set the marker |
| `Actor type DenoActor carries multi-file actor code, which this CLI version cannot represent - upgrade @borgiq/cli.` | Upgrade: a newer CLI wrote this bundle |

### Unknown actor type

`Unknown actor type 'X' - this CLI version does not support it; upgrade @borgiq/cli`: the installed registry predates
that type. Upgrade; do not invent a folder.

### Push conflict report

```text
Push aborted: 1 actor conflict(s). Re-pull, or re-run with --force-local for local wins.
  ACTR... (Process event): concurrent-edit; bundle editVersion 7 -> server editVersion 8
```

Nothing was applied. `server-edit`, `new-server` and `deleted-on-server` mean the server moved ahead: a bare
`bundle pull` applies them safely, then push again. `concurrent-edit`, `local-edit-server-delete`,
`local-delete-server-edit` and `baseline-missing` are true conflicts: choose `bundle pull --replace` (server wins), or
review git and run `bundle push --force-local` (local wins).

### Missing or incomplete sync baseline

`Warning: this bundle has no content-hash sync baseline` means `canvas.yaml` has no `sync.actors` (a hand-built or
pre-sync bundle), so existing actors whose content differs from the server fail closed as conflicts.
`Push aborted: the server export reported N actor error(s), so the sync baseline is incomplete` means the server
could not export cleanly. Either way, run `bundle pull` to establish a clean baseline; never hand-edit `sync.actors`.

### Target directory is not empty

- `bundle pull` syncs into an existing bundle (one with `canvas.yaml`) without `--force`, touching only the managed
  paths `canvas.yaml`, `README.md` and `actors/`.
- `bundle unpack` into an existing bundle always needs `--force` to replace its managed files.
- A non-empty directory without `canvas.yaml` needs `--force` for pull and unpack. Unmanaged files, `.git/`,
  `AGENTS.md`, `CLAUDE.md` and `.gitignore` survive; a `README.md` there does not, since it is the canvas README and is
  replaced by the server's copy (or deleted when the canvas has none).
