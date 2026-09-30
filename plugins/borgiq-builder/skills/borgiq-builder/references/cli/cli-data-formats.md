# Direct documents and batch payloads

The payload shapes for the direct path, which bypasses canvas bundles: `canvases create-with-data` / `update-data`
documents and `canvas-actors create` / `update` / `batch` bodies. Use it only when a bundle is not possible: a CLI
without `borgiq bundle` that cannot be upgraded, a one-off patch to a canvas nobody maintains locally, or a document
for manual deployment when there is no shell. Once a canvas has a local bundle, edit and push the bundle instead
([canvas-bundles.md](canvas-bundles.md)).

## Contents

- [Which command takes which shape](#which-command-takes-which-shape)
- [Field types](#field-types)
- [Actor fields](#actor-fields)
- [create-with-data body](#create-with-data-body)
- [update-data](#update-data)
- [canvas-actors bodies](#canvas-actors-bodies)
- [Verify bodies](#verify-bodies)
- [Export and duplicate](#export-and-duplicate)
- [Common mistakes](#common-mistakes)

## Which command takes which shape

`--file` reads JSON, or YAML when the name ends in `.yaml`/`.yml`; stdin is read as YAML. The CLI always sends JSON to
the API. The same configuration fields take **two different shapes**, and mixing them up is a `400`:

| Command | Body | `options`, `inputs`, `vars`, `outputs`, `credentials`, `error`, `schemas.*` |
|---|---|---|
| `canvases create-with-data` | ExportedCanvasData envelope | objects (the parsed shape) |
| `canvases update-data <canvas>` | ExportedCanvasData canvas data `{ schemaVersion, actors }` | objects |
| `canvas-actors create <canvas> <actorId>` | CanvasActor, without `id` | **YAML strings** |
| `canvas-actors update <canvas> <actorId>` | partial CanvasActor | **YAML strings** |
| `canvas-actors batch <canvas>` | `{ operations: [...] }` | **YAML strings** |
| `canvas-actors verify <canvas>` | `{ actorType, options, sourcePorts? }` | `options` is a YAML string |
| `canvases verify-import` | `{ canvas: "<YAML string>" }` | the whole export as one YAML string |

The API turns ExportedCanvasData objects into YAML strings before storing them, and stores CanvasActor YAML strings as
they are (its schemas: `CanvasCreateWithDataInputSchema` with `ExportedCanvasDataSchema`; `CanvasActorSchema`, without
`id` for create; `CanvasActorsBatchInputSchema` with `ActorOperationSchema`). `borgiq scaffold actor|actor-from-template|canvas|batch` builds correctly shaped payloads
([borgiq-cli.md](../borgiq-cli.md#command-map)).

## Field types

| Field | ExportedCanvasData | CanvasActor |
|---|---|---|
| `configuration.options` | object, optional (omit or `{}`) | YAML string, **required** (`""` allowed) |
| `configuration.inputs`, `outputs`, `error`, `credentials` | object | YAML string |
| `configuration.vars` | array | YAML string |
| `schemas.inputs`, `schemas.outputs` | object (JSON Schema) | YAML string (JSON Schema as YAML) |
| `configuration.codeDir` | array of `{ path, content }` | the same array, **never** a YAML string |
| `configuration.connection` | `{ type?: string \| string[], key? }` | the same object |
| `configuration.webhook` | `{ triggerKey?, authorizationLevel?, allowedMethods?, responseTimeout?, enabled? }`; `authorizationLevel` is `public`, `apps`, `apiKey` or `appsAndApiKey` | the same object |
| `configuration.aiAgentToolActorIds` | string array | string array |
| `configuration.code` | legacy single string: never write it | legacy single string: never write it |

`codeDir` carries the source of Deno, Deno Test, Universal Trigger, Python and React App actors. For the four code
actors exactly one entry is the entrypoint (`main.ts`, or `main.py` for Python); see
[code-actor-runtime.md → Source files](../code-actor-runtime.md#source-files-codedir).
`configuration.code` is the pre-multi-file shape, and the runtime no longer reads it: an actor with `code` and no
`codeDir` entrypoint cannot run, and `canvases validate` reports the missing entrypoint. Write `codeDir`, and never
send both for one actor.

## Actor fields

Every actor carries `type` (a type name), `version` (usually `1`), `name`, `msgVar` (a JSON-safe identifier),
`description` (`""` allowed), `isActive` (whether it receives and emits messages), `continueOnError` (emit an error
message instead of stopping: [error-handling.md](../error-handling.md)), `enableLTM` and `enableSTM` (long-term memory,
canvas-scoped, and short-term memory, flowrun-scoped; each one run at a time), `sourcePorts`
([ports per type](../edges-and-positioning.md#port-ids)), `configuration`, `schemas` (`{}` allowed), `position`
(`{ x, y }`, the UI coordinates) and `edges` (outgoing edges keyed by ID, `{}` allowed); all are required. `id` is required too, except in
a `canvas-actors create` body, where the ID is the command's argument. Optional:

| Field | Meaning |
|---|---|
| `showInWorkspaceApps` | List the actor in the workspace apps (default `true`) |
| `template` | `{ id, version, appName }`: the template it came from |
| `runtimeSlug` | A runtime other than the canvas's |
| `icon` | `{ type: "borgiq", value, category: "logos" \| "icons", color?, colorable? }`, `{ type: "svg", value: "<svg…>" }` or `{ type: "url", value: "https://…" }` |

A `borgiq` icon's `value` is a slug from `https://icons.borgiqassets.com/v1/manifest.json`: `logos` are brand logos
(`…/v1/logos/{slug}/icon-{light|dark}.svg`), `icons` monochrome UI icons (`…/v1/icons/{slug}.svg`). `color` is a hex
override without `#` (e.g. `"504C97"`, sent as the CDN's `?color=`) for an icon marked `colorable: true`, e.g.
`{ "type": "borgiq", "value": "arrow-right", "category": "icons", "colorable": true }`.

## create-with-data body

The envelope: `name` (2–255 characters), `slug` (lowercase letters, numbers, hyphens), `messageTTLInDays` (1–14) are
required; `description`, `tags` and `runtimeSlug` default to `""`. `data` holds `schemaVersion` and `actors`, keyed
by actor ID, with objects for the configuration fields:

```json
{
  "name": "My API Flow",
  "slug": "my-api-flow",
  "messageTTLInDays": 7,
  "data": {
    "schemaVersion": "1",
    "actors": {
      "ACTR01kd6gqghj04j8765nnqyp09a3": {
        "id": "ACTR01kd6gqghj04j8765nnqyp09a3", "type": "ButtonTriggerActor", "version": 1,
        "name": "Manual Trigger", "msgVar": "manual_trigger", "description": "",
        "isActive": true, "continueOnError": false, "enableLTM": false, "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }], "schemas": {}, "position": { "x": 0, "y": 0 },
        "edges": {
          "EDGE01kd6gqx5k7tvzs86y40w8etms": {
            "id": "EDGE01kd6gqx5k7tvzs86y40w8etms", "sourceActorId": "ACTR01kd6gqghj04j8765nnqyp09a3",
            "sourcePortId": "SPRTdefault", "targetActorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl",
            "targetPortId": "TPRTdefault", "type": "borgiqEdge"
          }
        },
        "configuration": { "options": {} }
      },
      "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl": {
        "id": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl", "type": "HttpRequestActor", "version": 1,
        "name": "Fetch Customer Data", "msgVar": "fetch_customer_data", "description": "",
        "isActive": true, "continueOnError": false, "enableLTM": false, "enableSTM": false,
        "sourcePorts": [{ "id": "SPRTdefault" }], "position": { "x": 0, "y": 200 }, "edges": {},
        "schemas": { "inputs": { "type": "object", "properties": { "customerId": { "type": "string" } } } },
        "configuration": {
          "inputs": { "customerId": "${{ msg.manual_trigger.body.id }}" },
          "options": { "method": "GET", "url": "https://api.example.com/customers/${{ inputs.customerId }}" },
          "outputs": "${{ results.body }}",
          "connection": { "type": ["api-key", "bearer-token"], "key": "example-api" }
        }
      }
    }
  }
}
```

A generated `metadata` + `actors` document becomes this envelope: validate it with `borgiq validate` first, move
`metadata.schemaVersion` to `data.schemaVersion`, nest `actors` under `data`, drop `metadata`, and add `name`, `slug`
and `messageTTLInDays`. `create-with-data --auto-layout` lays the canvas out after creating it. The name and the slug
must both be unused in the workspace (`400`, "already in use!"), so never run `create-with-data` against an existing
canvas.

## update-data

`canvases update-data <canvas> --file <path> [--mode merge|insert|replace]` imports actors into an existing canvas.
The file holds only the canvas data, `{ schemaVersion, actors }`; the CLI wraps it as `{ canvas, mode }` itself, so a
file you wrap is wrapped twice.

| Mode | Effect |
|---|---|
| `merge` (default) | Updates actors by ID and adds new ones; other actors are untouched |
| `insert` | New actor and edge IDs for everything imported: safe for duplicating a fragment |
| `replace` | Replaces the whole canvas data; `409` if the canvas changed meanwhile (re-read and retry) |

Every mode checks each actor's `editVersion` and answers like `batch`.

## canvas-actors bodies

`canvas-actors create <canvas> <actorId> --file actor.json`: a full CanvasActor without `id` (an `id` in the body is
ignored). Mint the ID with `borgiq generate id actor`. `canvas-actors get` returns actors in this shape, and a canvas
made empty with `canvases create --name --slug` is filled with `batch`.

```json
{
  "type": "HttpRequestActor", "version": 1, "name": "Fetch Customer Data", "msgVar": "fetch_customer_data",
  "description": "", "isActive": true, "continueOnError": false, "enableLTM": false, "enableSTM": false,
  "sourcePorts": [{ "id": "SPRTdefault" }], "position": { "x": 0, "y": 200 }, "edges": {},
  "configuration": {
    "options": "method: GET\nurl: https://api.example.com/customers/${{ inputs.customerId }}",
    "inputs": "customerId: ${{ msg.manual_trigger.body.id }}",
    "outputs": "${{ results.body }}",
    "connection": { "type": ["api-key", "bearer-token"], "key": "example-api" }
  },
  "schemas": { "inputs": "type: object\nproperties:\n  customerId:\n    type: string" }
}
```

`canvas-actors update <canvas> <actorId> --file updates.json [--edit-version <n>]` takes only the fields that change,
e.g. `{ "configuration": { "options": "method: POST\nurl: https://api.example.com/customers" } }`.
`canvas-actors delete <canvas> <actorId> [--edit-version <n>]` removes one. `--edit-version` is the conflict check:
a stale value answers `409`.

`canvas-actors batch <canvas> --file ops.json` applies several operations in one request. Each needs `type` (`add`,
`update` or `remove`), `actorId` and `timestamp` (epoch milliseconds; omitting it is a `400`). `add` takes a full
CanvasActor in `data`, `update` a partial one; `editVersion` is optional on `update` and `remove`. The answer is
`{ processed, appliedOperations: [{ type, actorId, newEditVersion }], conflicts, warnings?, updatedAt }`.

```jsonc
{
  "operations": [
    { "type": "add", "actorId": "ACTR01kd6gr3vjxm2rs0k8s3fjq4nl", "timestamp": 1712500000000,
      "data": { /* a full CanvasActor, as in the create body */ } },
    { "type": "update", "actorId": "ACTR01kd6gqghj04j8765nnqyp09a3", "editVersion": 3, "timestamp": 1712500000001,
      "data": { "name": "Updated Actor Name", "msgVar": "updated_actor_name" } },
    { "type": "remove", "actorId": "ACTR01kd6gr8m6q9nzp2w4j7h5k6ln", "editVersion": 2, "timestamp": 1712500000002 }
  ]
}
```

## Verify bodies

`canvas-actors verify <canvas>` (file or stdin) checks one actor's options against its type's schema without saving
anything. Router and AI Router actors also need `sourcePorts`:

```json
{
  "actorType": "RouterActor",
  "options": "emitType: singleRoute\nconditions:\n  Active: ${{ msg.trigger.body.status === 'active' }}",
  "sourcePorts": [{ "id": "SPRTabcdefg", "name": "Active" }, { "id": "SPRTdefault", "name": "F" }]
}
```

`canvases verify-import --file <path>` checks import data without importing it; its `canvas` field is the whole export
as one YAML string (`"metadata:\n  schemaVersion: v1.0\n  source: BIQCanvas\nactors:\n  …"`).

## Export and duplicate

`canvases export <canvas>` prints `{ yaml, errors }`. `yaml` is the whole canvas as one YAML string in the
ExportedCanvasData shape: a `metadata` block (`id`, `slug`, `name`, `description`, `tags`, `imagePath`,
`messageTTLInDays`, `runtimeSlug`) and a `data` block with the actor graph. `create-with-data` does not accept it, and
`yaml` is YAML, not JSON, so `jq fromjson` fails on it. To copy a canvas, unpack the export into a bundle:
[canvas-bundles.md → Lifecycle commands](canvas-bundles.md#lifecycle-commands).

## Common mistakes

| Mistake | Result | Fix |
|---|---|---|
| An object for `options` in a `canvas-actors create`/`update`/`batch` body | `400`: a YAML string is expected | `"options": "method: GET"` |
| A YAML string for `options` in `create-with-data` | Accepted, but the actor's options become that string, not an object | `"options": { "method": "GET" }` |
| No `options` in a CanvasActor body | `400`: required | `"options": ""` at least |
| No `description` | `400`: required | `"description": ""` |
| No `timestamp` in a batch operation | `400`: required | `"timestamp": <epoch ms>` |
| `codeDir` as a YAML string | Rejected | An array of `{ path, content }` in both shapes |
| An `id` in a `canvas-actors create` body | Ignored | Pass the ID as the command's argument |
| A `{ canvas, mode }` wrapper in the `update-data` file | Wrapped twice | The file holds `{ schemaVersion, actors }` only |
