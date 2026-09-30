# Code Actor Runtime

What DenoActor, PythonActor and UniversalTriggerActor share: the `receive(req)` → `Response` contract, emit rules,
errors, source files (`codeDir`), inputs, credentials, memory, temporary files, signals, the runtime API, long-running
work and dependencies. Read it with the language file ([deno-actor.md](deno-actor.md) or
[python-actor.md](python-actor.md)); trigger events are in [universal-trigger-actor.md](universal-trigger-actor.md).

## Contents

- [Rules](#rules)
- [Execution environment](#execution-environment)
- [Request and response](#request-and-response)
- [What gets emitted](#what-gets-emitted)
- [Errors and retries](#errors-and-retries)
- [Source files (codeDir)](#source-files-codedir)
- [Inputs](#inputs)
- [Credentials and connections](#credentials-and-connections)
- [Memory](#memory)
- [Temporary files](#temporary-files)
- [Signals](#signals)
- [Runtime API](#runtime-api)
- [Long-running work and checkpoints](#long-running-work-and-checkpoints)
- [Dependencies and deployed workspaces](#dependencies-and-deployed-workspaces)
- [Runtime context](#runtime-context)

## Rules

1. Write `receive(req)` as a pure function: read everything from `req`, return a `Response`.
2. Pass runtime values through `configuration.inputs`; `${{ }}` in source is literal text.
3. Read tokens from `req.connection` and secrets from `req.credentials`; never pass a secret through `inputs`.
4. Validate required inputs, credentials and the connection first; fail with a message naming what is missing.
5. Return `memory` only for the half you changed: spread the prior state, set keys, clear a key with `null`.
6. Make long work pausable and resumable: the runtime can stop a run at any point, at the latest at its timeout.
7. Pin every third-party dependency to an exact version.
8. Keep each actor focused; split complex logic across actors.
9. Create clients (database, SDK) once at module level: they are reused while the container stays warm.

## Execution environment

Code actors run on AWS Lambda, in a container that can stay warm between invocations.

| | |
|---|---|
| Timeout | The runtime's *Deno actor timeout* (workspace settings → Runtimes, 3–780 s), used by PythonActor too; code cannot read it from `req.ctx`. Lambda's absolute limit is 15 minutes |
| Memory, ephemeral storage | Set on the runtime (the Lambda configuration) |
| Deno | TypeScript/JavaScript; no shell or CLI tools ([No shell](deno-actor.md#no-shell)) |
| Python | Exactly 3.11, dependencies installed by UV; CLI tools such as `git`, `aws`, `jq`, ImageMagick and `tar` via `subprocess` ([CLI tools](python-actor.md#cli-tools)) |

## Request and response

The entrypoint exports `export default async function receive(req: Request): Promise<Response>` (`main.ts`) or
`def receive(req: Request) -> Response:` (`main.py`). There is no `actor` object. Import everything from
`@borgiq/actors` (TypeScript) or `borgiq` (Python). A UniversalTriggerActor receives a `TriggerRequest`: the same
fields plus `req.trigger`, the firing event.

| Field | Meaning |
|---|---|
| `req.inputs` | The interpolated `configuration.inputs` for this invocation |
| `req.ctx` | Org, workspace, canvas, flowrun and actor ([Runtime context](#runtime-context)) |
| `req.connection` | The single connection's resolved config (read-only) |
| `req.credentials` | Secret values by name; proxy placeholders when Server-side (read-only) |
| `req.memory` | `{ stm, ltm }`, value-in ([Memory](#memory)) |
| `Response.results` | Emitted as `msg.<msgVar>` downstream ([What gets emitted](#what-gets-emitted)) |
| `Response.memory` | The halves to persist; omit to leave memory unchanged |
| `Response.signal` | One signal built with `Signal.*` / `signal.*` ([Signals](#signals)) |
| `Response.error` | `{ message, retryable }`, to fail explicitly ([Errors](#errors-and-retries)) |

In Python the fields hold dicts (`req.inputs.get('x')`, `req.memory['ltm']`); return
`Response(results=..., memory=..., signal=..., error=...)`. A bare return value is treated as `results`.

Console output (`console.log` / `warn` / `error` in Deno, `print` in Python) is captured and stored with the flowrun,
visible in its details in the BorgIQ UI: log progress liberally. The request has no `assets` field: manage workspace
assets through the `/assets` [runtime API](#runtime-api) routes.

## What gets emitted

| You return | Downstream gets |
|---|---|
| An object or other value | One message, `msg.<msgVar>` |
| An array (Python: list) | **One** message holding it; one message per item only with `options.emitArrayAsSingleMessage: false` (default `true`) |
| An empty array `[]` | Nothing |
| TypeScript `results: undefined`, no `results`, or `{}` | Nothing |
| TypeScript `results: null` | A `null` message (valid JSON) |
| Python `results=None`, no `results`, or `Response()` | A `null` message; return `results=[]` to emit nothing |

Returning `memory` alongside `results` emits the message and persists the memory.

## Errors and retries

| To | TypeScript | Python |
|---|---|---|
| Fail and be re-invoked with the same message | `throw new RetryableError("…")` | `raise RetryableError("…")` |
| Fail permanently | Throw any other error | Raise any other exception |
| Fail without throwing | `return { error: { message, retryable: true } }` | `return Response(error={'message': ..., 'retryable': True})` |

Use `RetryableError` for transient failures: a 429 rate limit, or a 401 when a token may need a refresh. The
TypeScript type requires `retryable`: set `false` for a permanent failure (omitted, it counts as `false`).

## Source files (codeDir)

DenoActor, DenoTestActor, UniversalTriggerActor and PythonActor hold their source in `configuration.codeDir`: a list
of `{ path, content }` files forming a small project, a sibling of `options` (examples in
[deno-actor.md](deno-actor.md#configuration) and [python-actor.md](python-actor.md#configuration)).

- **Exactly one entrypoint, at the root:** `main.ts` for the Deno family, `main.py` for PythonActor; the runtime
  imports it. Arrange the rest in folders as you like.
- **Your own files:** Deno imports them relatively, with the extension ([imports](deno-actor.md#imports-and-pinning));
  Python imports modules from the tree root, packages need `__init__.py` ([modules](python-actor.md#modules-and-packages)).
- **`codeDir` is never interpolated.** `${{ }}` in source is literal text: pass runtime values through
  `configuration.inputs` and read `req.inputs`. A `${{ credentials.* }}` in source is never resolved, and source that
  looks like an expression survives verbatim.
- **Removing an entry removes the file:** the runtime rebuilds the actor's directory from the list on every code
  change, so a deleted file stops being importable immediately.
- **Limits:** UTF-8 text only, at most 200 files and 1 MiB of content in total. Paths are up to 255 characters,
  relative and `/`-separated, with no `.` or `..` segments, backslashes or leading `/`.
- **Reserved paths**, compared case-insensitively (the runtime writes its own files beside yours; in Python a root
  file would shadow the runtime's module):

  | Family | Reserved |
  |---|---|
  | Deno, Deno Test, Universal Trigger | `server.ts`, `handler.ts`, `actor.ts`, `main_test.ts`, `deno.json`, `deno.jsonc`, `deno.lock`, `package.json`, anything under `shared/`, `node_modules/` or `.borgiq-deno-dir/` |
  | Python | `server.py`, `handler.py`, `borgiq.py`, `pyproject.toml`, `.python-version`, `uv.lock`, anything under `.borgiq/`, `.venv/` or `borgiq/` |

  There is no user-managed dependency manifest: Deno pins versions in the import specifiers; Python lists them in
  `options.dependencies`, which is why a `pyproject.toml` of your own is reserved rather than merged.
- **Enforcement:** a save through the editor or API lands with a `code_dir` warning; `canvases validate` blocks a
  missing entrypoint; `bundle validate` checks the tree locally; the runtime refuses a missing entrypoint or a
  reserved path when the actor runs.
- **Never write `configuration.code`** (legacy single-string source): the runtime reads only `codeDir`, an actor with
  `code` and no entrypoint in `codeDir` cannot run, and `canvases validate` reports the missing entrypoint.

Editing surfaces: in a **bundle**, real files under the actor's `code/` directory
([canvas-bundles.md](cli/canvas-bundles.md#code-actor-project-trees)); in a **direct document or batch payload**, the
`codeDir` list itself, a structured array in both formats, never a YAML string; in the **web editor**, the Code page's
file tree (the canvas side panel edits only the entrypoint). The AI code assist sees only the selected file: prompt it
per file and wire the pieces together yourself. Exact rules:
[typescript/actorSchemas/codeDir.md](typescript/actorSchemas/codeDir.md).

## Inputs

If the code reads `req.inputs`, configure both `configuration.inputs` (the values, interpolated per invocation from
`msg`, `ctx` and the other [context variables](context.md)) and `schemas.inputs` (a JSON Schema for validation and the
editor form). In the schema, `ui.order` sets the display order (0 first) and `ui.component` overrides the widget
(`password`, `textarea`, `code`, …).

```yaml
configuration:
  inputs:
    data: ${{ msg.upstream_actor.body }}
    timeout: 30
schemas:
  inputs:
    type: object
    properties:
      data: { type: object, title: Data, description: Data to process, ui: { order: 0 } }
      timeout: { type: number, title: Timeout (seconds), default: 30, ui: { order: 1 } }
    required: [data]
```

## Credentials and connections

An actor has **only one connection**, but **any number of credentials** (secrets). All are read-only.

| Source | Declare | Read |
|---|---|---|
| The connection | `connection: { key: <workspace connection key> }` | `req.connection`; an OAuth2 token is at `req.connection.auth.values.token` (Python `req.connection.get('auth', {}).get('values', {}).get('token')`) |
| A secret | `credentials: { NAME: { workspaceKey: <workspace secret key> } }` | `req.credentials.NAME` (Python `req.credentials.get('NAME')`), a string |
| Another connection | `credentials: { NAME: { workspaceKey: <workspace connection key>, source: connection } }` | `req.credentials.NAME`, shaped like `req.connection`: `.auth.values.token` |

In configuration fields such as `options.env`, `${{ credentials.NAME }}` and `${{ connection.auth }}` resolve the same
values ([context.md](context.md)).

### Server-side vs Sent to runtime

Every secret and connection has an **exposure mode**. The UI names it one way and the API and CLI another:

| UI label | `exposureMode` (API / CLI) | What the code receives |
|---|---|---|
| **Server-side** (recommended, the default) | `httpOnly` | A placeholder such as `BORGIQ_CREDENTIAL_OPENAI_API_KEY_<hash>`, never the real value |
| **Sent to runtime** | `exposed` | The decrypted value |

A Server-side placeholder works only inside an outbound **HTTPS** request: the BorgIQ proxy swaps in the real value
where the placeholder appears in the URL, a header or a text body. It is not substituted in a plain `http://` request
or a binary body, and anything else the code does with it — hashing, signing, a database driver, a non-HTTP SDK — gets
the placeholder string. The same holds for a connection's sensitive fields under `req.connection.auth.values`. A
Server-side credential can also be limited to a list of URLs (`allowedUrls`); the proxy refuses a request that uses it
anywhere else.

Choose **Sent to runtime** only when the code needs the raw value (signing or encrypting with a key, a database
password, a non-HTTP protocol). Set it in the *Exposure mode* field in the UI, or with `--exposure-mode exposed` on
`borgiq secrets create` / `borgiq connections create`.

### More than one connection

Prefer splitting the work across actors, one connection each. When the logic must stay in one actor, declare each
extra connection as a credential with `source: connection` (`workspaceKey` is its key in the workspace). The runtime
API's `/connections/{key}` returns only the actor's own connection and refuses any other key with 403.

```yaml
configuration:
  connection:
    key: my-gmail-connection
  credentials:
    calendar:
      workspaceKey: my-calendar-connection
      source: connection
```

```typescript
const gmailToken = req.connection.auth.values.token;                   // the actor's own connection
const calendarToken = (req.credentials["calendar"] as any).auth.values.token;   // the second connection (typed as a string)
```

### Consolidating a flow into one actor

To turn a flow of connected actors into one actor, **use a DenoActor**. If the flow used one connection, make it the
DenoActor's `connection`; if it used several, declare each as a `source: connection` credential.

| Scenario | Consolidate? |
|---|---|
| Sequential API calls with data dependencies, or an API call plus data processing | Yes |
| Parallel API calls whose results must be combined | A code actor, or fork/forkJoin |
| Simple linear flow of independent actors | Optional |
| Branching or routing logic | No: keep separate actors |
| AI actors needing different models | Case by case |
| The user explicitly asks | Yes |

## Memory

Every code actor has two key-value stores, always present on `req.memory`, with an identical API:

| Store | Lifetime | Use for | Enable |
|---|---|---|---|
| `stm` (the default choice) | One flowrun; garbage-collected when it completes | Run-local state: counters, running totals, fork/join bookkeeping, dedup sets | `enableSTM: true` |
| `ltm` | Every flowrun of the actor, until overwritten | Only values that must outlive the run: a cursor, a checkpoint, a registered external ID | `enableLTM: true` |

Memory is **value-in / value-out**. Read the incoming state from `req.memory`, and **return `memory` in your `Response`
to persist it**; there is no other way to write it. If you omit `memory`, the stored memory is left unchanged.

**The runtime shallow-merges each half you return into the stored half.** Each half is persisted independently of the
other. *Within* a half, every top-level key you return replaces that key's whole value (nested objects are not merged),
and every key you leave out keeps its stored value:

1. **Return the half you changed: spread the prior state, then set your keys.** `memory: { ltm }` merges into LTM and
   leaves STM untouched. The spread is undefined-safe, so no `?? {}` guard is needed.
2. **To clear a key, return it as `null`** (Python `None`): `memory: { ltm: { checkpoint: null } }`. Omitting a key,
   `delete`-ing it (Python `pop`/`del`), or setting it to `undefined` (dropped in transit) all leave the stored value in
   place, and `{ ltm: {} }` changes nothing.
3. **Omit `memory` to leave everything unchanged**; return it only when you changed something.
4. **Read with optional chaining and a default:** `req.memory?.ltm?.cursor ?? 0`. Each store is empty on first use, and
   a cleared key reads as `null` (Python `.get('key', default)` then returns `None`, not `default`).
5. **Match the store to the lifetime:** run-local scratch in `stm`, must-outlive-the-run in `ltm`.
6. **Stay under the size caps:** LTM **1 KB** and STM **4 KB** per actor by default, measured as JSON after the merge
   (workspace settings → Actors → *Max LTM (KB)* / *Max STM (KB)*). Over a cap, the run fails with
   `MemoryExceedAllowedSize` (not retried) and no memory change is saved. Keep IDs and cursors in memory; put bulk
   state in a Collection or a stashed file.

**Enabling is required, and you only return what is enabled.** Returning a **non-empty** half for a store that is not
enabled is a runtime error (`STM is not enabled for the actor` / `LTM is not enabled for the actor`). A store that is
not enabled arrives as `{}`, so echoing it back is harmless. Enabling a store also **serializes** the actor's message
processing, one message at a time within a flowrun (STM) or across all flowruns (LTM), so read-modify-write is
race-free. LTM also moves the actor's [temporary directory](#temporary-files) to an actor-scoped path.

The incremental poll reads a cursor from `ltm`, fetches only what changed since, writes the new cursor back and emits
the new items:

```typescript
export default async function receive(req: Request): Promise<Response> {
  const cursor = req.memory?.ltm?.cursor ?? 0;                    // 0 on the very first run
  const { items, nextCursor } = await fetchSince(cursor);
  return { results: items, memory: { ltm: { ...req.memory?.ltm, cursor: nextCursor } } };
}
```

STM is the same idiom (`memory: { stm: { ...req.memory?.stm, counter } }`). In Python, set the key on the dict and
return it: `req.memory['ltm']['cursor'] = next_cursor`, then `Response(results=items, memory=req.memory)`.

The TypeScript `Memory` type declares both halves, so an editor that type-checks flags `memory: { ltm }`. It runs
(actor code is not type-checked, and the omitted half is unchanged); add `stm: req.memory.stm` to satisfy the type.

## Temporary files

`TMPDIR` is the actor's data directory, so `tmpdir()`, `Deno.makeTempDir()` and Python's `tempfile` write there. A Deno
actor reaches it only with `allowFs: true`.

| LTM | Data directory |
|---|---|
| Disabled (default) | `/tmp/borgiq/data/{workspaceId}/{flowrunId}/{actorId}/`, one per flowrun |
| Enabled | `/tmp/borgiq/data/{workspaceId}/{actorId}/`, shared by every flowrun of the actor |

- It lives in the container's `/tmp`: files persist between invocations only within the same warm container, a cold
  start begins empty, and a finished flowrun's directory is removed some time after the run.
- With LTM enabled, a later flowrun in the same warm container can read what an earlier one wrote: a cache, never the
  only copy. For anything that must persist, use memory, a Collection or a stashed file.
- Never hardcode `/tmp/...` paths; clean up what you write, to stay within the runtime's ephemeral storage.

## Signals

Return at most one signal in `Response.signal`. Any actor may answer a pending request in its flow.

**Signals take effect only for DenoActor and UniversalTriggerActor.** The Python SDK builds them, but the platform ignores a PythonActor's signal: its `results` emit as if no signal was set. From Python, answer a webhook with a downstream WebhookResponseActor, a sub-flow with a CallableResponseActor, and delay with a MessageProcessorActor.

| Purpose | TypeScript `Signal.*` | Python `signal.*` |
|---|---|---|
| Respond to a pending webhook request | `webhookRespond({ statusCode, headers?, body? })` | `webhook_respond(status_code, headers=None, body=None)` |
| Respond to a pending callable (sub-flow) request | `callableResponse({ payload, throwError? })` | `callable_response(payload, throw_error=None)` |
| Delay emitting the message until a time | `delayUntil(when)`: an ISO 8601 string or a `Date`, passed directly (not wrapped in an object) | `delay_until(when)`: an ISO 8601 string, positional |

`webhookRespond` answers the webhook caller as soon as the actor completes, without a WebhookResponseActor; `results`
still propagate downstream. The other orchestrator signals (`callFlow`, `waitForCallbackToken`, `notifyCallbackToken`, the `interface*` family,
`ai`, `aiAgent`) belong to their dedicated actors and the MessageProcessorActor, not to code.

## Runtime API

`biqApi(path, init?)` (TypeScript, a `fetch` wrapper) and `biq_api(path, **kwargs)` (Python, a `requests` wrapper) call
the BorgIQ Runtime API as the running actor. In Deno they and the file helpers need `allowNet: true`; with an
`allowNetList`, the BorgIQ API host is added to it automatically.

| Endpoint | Method | Purpose |
|---|---|---|
| `/collections` | POST | Every Collection action (`action` in the body) |
| `/streams` | POST | Every Stream action (`action` in the body) |
| `/streams/{streamIdOrSlug}/tail` | GET | Tail a stream over SSE for a bounded window (`?from=&maxSeconds=&maxRecords=`) |
| `/issueCallbackToken` | POST | Issue a callback token for an async workflow |
| `/files/{fileId}/downloadUrl` | GET | Signed download URL (`?expiresInMinutes=N&downloadAsAttachment=true`) |
| `/files/upload` | POST / PUT | Upload files (multipart) / stream one file directly to storage |
| `/files/download` | GET | Stream file content from storage |
| `/files/updateUploads` | POST | Update file status after a presigned-URL upload |
| `/assets`, `/assets/{key}` | GET, POST / PUT, DELETE | List and create workspace assets / update and delete one |
| `/secrets` | GET | Secrets: decrypted when Sent to runtime, a proxy placeholder when Server-side |
| `/connections/{key}` | GET | The actor's own connection (`configuration.connection.key`; other keys get 403), sensitive fields as placeholders when Server-side |
| `/publicKey` | GET | Workspace public key, for encrypting sensitive data |
| `/sendEmail` | POST | Send an email |
| `/interfaces/status` | PUT | Update an interface status display |
| `/toolkit/chatCompletion` | POST | AI chat completion (internal) |
| `/dataStore/*` | Various | Legacy data store (deprecated: use `/collections`) |

**Files.** Prefer `mountFile(file)` (downloads a `BIQFile`, returns its local path) and
`stashFile(file, filename?, mimeType?)` (uploads bytes, a stream or a local path, returns a `BIQFile` for downstream
actors) to the `/files/*` routes they use underneath: they handle download, upload, temp files and cleanup. Call the
routes only for advanced control (custom expiry, presigned uploads). `GET /files/{fileId}/downloadUrl` returns
`{ downloadUrl }`, valid for 1 minute unless you pass `expiresInMinutes`: use it to hand a file to an external API.

**Callback tokens.** `POST /issueCallbackToken` with `{ expiresAfterInSeconds }` returns `{ token, url, expiresAt }`;
an external system POSTs to `url` to notify the waiting workflow. Typically you store the token in a Collection under
a correlation ID (an email thread ID) with `putItem`, and another actor pauses on `waitForCallbackToken`.

**Collections and streams** answer `{ ok, value, error?: { code, message } }`: unwrap it in one helper
([Deno](deno-actor.md#runtime-api-helper), [Python](python-actor.md#template-and-sdk)). Actions, semantics and error
codes: [collection-actor.md](collection-actor.md) (`putItem` is create-only) and [stream-api.md](stream-api.md).
Streams must be created before use and expire unless persistent ([stream-actor.md](stream-actor.md)).

| Scenario | Use |
|---|---|
| Structured persistent storage; queue operations (queue-via-Collections) | CollectionActor |
| Several storage operations in sequence, or storage decided by complex logic | `biqApi` (fewer actors, full control) |
| A callback token issued by custom logic | `biqApi` |
| The standard callback token workflow | MessageProcessorActor `issueCallbackToken` |

## Long-running work and checkpoints

A run is stopped at the runtime timeout, which code cannot read. **Track progress**, **save state before the
deadline** (in `Response.memory`, or emitted), **resume** from it on the next invocation, and **stop early**: take the
time budget as an input set below the runtime's timeout, and stop with a buffer (30 s) to spare.

| Approach | How it works | Best for |
|---|---|---|
| **LTM-based** | The checkpoint lives in `req.memory.ltm`, returned in `Response.memory` | Self-contained actors, simple flows |
| **Input-based** | The checkpoint arrives in `req.inputs` and leaves in `Response.results`; the flow passes it back | Complex flows, external orchestration |

Ask the user which approach they prefer. Examples: [Deno](deno-actor.md#checkpoint-a-large-dataset-in-a-stashed-file),
[Python](python-actor.md#checkpoint-a-batch-loop-in-ltm).

- **LTM-based:** process in batches while `Date.now() - start < budget - buffer`; after each batch keep
  `{ lastProcessedId, processedCount, timestamp }` as `ltm.checkpoint`, and on completion return `checkpoint: null`
  (an omitted or deleted key would survive the merge and the next run would resume from it).
- **Input-based:** read `req.inputs.cursor`; while there is more, emit `results.cursor`
  (`{ lastProcessedId, processedCount }`), which the caller passes back as `inputs.cursor`.
- **Large working sets:** write the dataset to a temp file, stash it, and keep the `BIQFile` in the checkpoint; on
  resume, mount it and continue. This avoids the memory caps and re-serializing at every checkpoint, persists reliably
  in BorgIQ storage, and works with either approach (examples in both language files).
- **Idempotent reprocessing:** keep a SHA-256 of each item's content (`crypto.subtle.digest` / `hashlib.sha256`) and
  skip items whose hash is unchanged.
- **Rate limits:** throw `RetryableError` on a 429.

## Dependencies and deployed workspaces

- **Pin every third-party dependency exactly:** Deno `npm:name@x.y.z` / `jsr:@scope/name@x.y.z`, Python
  `name==x.y.z`. A bare name or a floating range (`^`, `~`, `>=`, `~=`, `*`) resolves to whatever is latest at
  resolution time: a newly published malicious or breaking release is pulled automatically (a supply-chain risk), and
  deploys become non-deterministic. Runtime-provided specifiers (`@borgiq/actors`, `node:*`) are exempt.
- **Deno refuses `npm:`/`jsr:` versions published less than 7 days ago** (`minimumDependencyAge: "P7D"`): pin a
  release at least a week old, or it fails to resolve.
- **When resolution happens depends on the workspace.** On an ordinary workspace, dependencies are resolved (Python:
  installed) the first time the actor runs on a given machine. On a **deployed** workspace they are resolved once,
  when the canvas is built, into a lockfile (Python: a locked environment) that ships with the actor; every run from
  that build uses exactly those versions and resolves nothing. A Python actor that needs a package its build did not
  install fails immediately rather than installing it.
- **On a deployed workspace every run executes the canvas's active runtime build,** so an edit takes effect only after
  the next build ([deployment.md](deployment.md)).

## Runtime context

`req.ctx` holds the org, the workspace (`{ id, slug, name }`), the canvas with its trigger URL maps, the current actor
(including `upstreamActorCount`), the flowrun (`{ id, createdAt }`), the trigger actor, the optional source actor and
`sourceMsgId`, and `parentFlowrun` in a sub-flow; not the runtime timeout. Exact shape:
[typescript/schemas/ctx.md](typescript/schemas/ctx.md); in expressions: [context.md → ctx](context.md#ctx).
