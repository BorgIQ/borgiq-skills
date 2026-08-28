# Deno Actor Reference

The DenoActor executes custom TypeScript/JavaScript code in a sandboxed Deno runtime within BorgIQ workflows.

> **API model (important):** A Deno Actor is a **pure function** — `receive(req: Request): Promise<Response>`. There is **no `actor` object**. Read everything you need from `req` (`req.inputs`, `req.ctx`, `req.connection`, `req.credentials`, `req.memory`) and return a `Response`. Memory is **value-in / value-out**: read it from `req.memory`, and **return `memory` in the `Response` to persist it**. Emitted messages go under `Response.results`. Signals are returned via `Response.signal` (built with `Signal.*`), not set imperatively. Everything — the `Request`/`Response` types, the `Signal` constructors, `RetryableError`, and the `biqApi`/`mountFile`/`stashFile` helpers — is imported from the single `@borgiq/actors` specifier.

> **Building a trigger in Deno?** The [UniversalTriggerActor](universal-trigger-actor.md) runs this same runtime and contract — the only difference is the entry point `receive(req: TriggerRequest)`, where `req.trigger` carries the firing event (webhook / schedule / manual).

## Table of Contents

- [Execution Environment](#execution-environment)
- [Configuration Structure](#configuration-structure)
- [Input Schemas](#input-schemas)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Code Files](#code-files)
- [Code Template](#code-template)
- [Logging](#logging)
- [Request and Response](#request-and-response)
- [Memory Types](#memory-types)
- [Importing Libraries](#importing-libraries)
- [File Operations](#file-operations)
- [BIQ Runtime API](#biq-runtime-api)
  - [Available API Endpoints](#available-api-endpoints)
  - [When to Use biqApi vs Standard Actors](#when-to-use-biqapi-vs-standard-actors)
  - [Collection API (Recommended)](#collection-api-recommended)
  - [Callback Token API](#callback-token-api)
  - [File Download URL API](#file-download-url-api)
- [Error Handling](#error-handling)
- [Credentials and Connections](#credentials-and-connections)
- [Signals](#signals)
- [Network Access](#network-access)
- [Runtime Context](#runtime-context)
- [Return Values](#return-values)
- [Examples](#examples)
- [Checkpointing for Resumable Operations](#checkpointing-for-resumable-operations)
- [Best Practices](#best-practices)

## Execution Environment

Deno Actors run inside **AWS Lambda** with the following constraints:

| Constraint | Value | Notes |
|------------|-------|-------|
| Maximum timeout | 15 minutes | Absolute limit, cannot be exceeded |
| Configurable timeout | Varies | Set per workspace via `denoActorTimeoutInSeconds` |
| Memory | Configurable | Set in Lambda configuration |
| Ephemeral storage | Temp directory | Limited, cleared between invocations |
| Shell commands | **Not available** | No access to `zip`, `unzip`, `curl`, `jq`, `git`, etc. |

**Critical Implication:** All long-running operations must be designed as **pausable and resumable**. Never assume an operation will complete in a single invocation.

**No Shell Access:** Deno Actors do not have access to shell commands or CLI tools. Operations like zip/unzip, HTTP requests, JSON processing, and hashing must be implemented using JavaScript/TypeScript libraries (e.g., `npm:jszip`, native `fetch()`, `JSON.parse()`, `crypto.subtle`).

### Design for Interruption

Since Lambda can timeout at any point, your code must:

1. **Track progress** - Know where you stopped
2. **Save state** - Persist progress before timeout (return it in `Response.memory`)
3. **Resume gracefully** - Pick up where you left off (read it from `req.memory`)
4. **Set safe time limits** - Stop processing before Lambda kills the function

### Temporary File Storage

When file system access is enabled (`allowFs: true`), you have two options for working with temporary files:

**Option 1: Create a new temporary directory** using `Deno.makeTempDir()`:

```typescript
// ✅ Create a new temporary directory
const tempDir = await Deno.makeTempDir({ prefix: "myactor_" });
const tempFile = `${tempDir}/output.json`;
await Deno.writeTextFile(tempFile, JSON.stringify(data));

// Clean up when done
await Deno.remove(tempDir, { recursive: true });
```

**Option 2: Access the existing temp directory root** using `tmpdir()` from `node:os`:

```typescript
import { tmpdir } from "node:os";
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Access the existing temp directory root
  const tempRoot = tmpdir();

  // Use it to persist data that might be reused in future invocations
  const dataFile = `${tempRoot}/persistent-data.json`;
  await Deno.writeTextFile(dataFile, JSON.stringify(data));

  return { results: { tempRoot } };
}
```

**Key differences:**
- `Deno.makeTempDir()` - Creates a **new unique directory** each time (e.g., `/tmp/myactor_abc123`)
- `tmpdir()` - Returns the **existing temp directory root** (e.g., `/tmp`), where data could be persisted across invocations during the same Lambda container lifecycle

**Never hardcode paths:**
```typescript
// ❌ Wrong - never hardcode paths
const badPath = "/tmp/myfile.json";  // Don't do this
```

#### LTM and File Persistence

**When LTM (Long Term Memory) is enabled for an actor, the data directory path no longer includes the `flowrunId`.** This allows temp files and data to persist across flowrun executions.

The `TMPDIR` environment variable is automatically set to the data directory path:

| LTM Setting | Data Directory Path |
|-------------|---------------------|
| Disabled (default) | `/tmp/borgiq/data/{workspaceId}/{flowrunId}/{actorId}/` |
| Enabled | `/tmp/borgiq/data/{workspaceId}/{actorId}/` |

**Key implications:**

- **LTM disabled**: Each flowrun gets its own isolated directory (includes `flowrunId`). Files are cleared after the flowrun completes.
- **LTM enabled**: All flowruns for the same actor share the same directory (no `flowrunId`). Files persist across flowrun executions within the same Lambda container lifecycle.

```yaml
# Enable LTM to persist temp files across flowruns
enableLTM: true
```

```typescript
import { tmpdir } from "node:os";
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // When LTM is enabled, tmpdir() returns:
  // /tmp/borgiq/data/{workspaceId}/{actorId}/
  // Files here persist across flowruns (within the same Lambda container)

  const dataDir = tmpdir();
  const persistentFile = `${dataDir}/cache.json`;

  // Check if cached data exists from a previous flowrun
  try {
    const cached = await Deno.readTextFile(persistentFile);
    console.log('Found cached data from previous flowrun');
    return { results: JSON.parse(cached) };
  } catch {
    // No cache, fetch and store for next flowrun
    const data = await fetchData();
    await Deno.writeTextFile(persistentFile, JSON.stringify(data));
    return { results: data };
  }
}
```

**Important:**
- Temp files are cleared between Lambda cold starts (container restarts)
- Even with LTM enabled, do not rely on temp storage for critical persistence—use LTM (returned in `Response.memory`) or external storage (Collections, databases, etc.)
- Always clean up temp files when done to avoid storage limits

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: DenoActor
    version: 1
    name: Actor Name Here
    msgVar: actor_name_here
    description: What this actor does
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        key: value
      options:
        emitArrayAsSingleMessage: false
        allowNet: false
        allowNetList:
          - api.example.com
        denyNetList:
          - blocked.example.com
        allowFs: false
        env:
          - name: ENV_VAR
            value: some_value
      # Source is a list of files, sibling of `options`, never interpolated.
      # Exactly one entry must have path `main.ts` — it is the entrypoint.
      codeDir:
        - path: main.ts
          content: |
            import type { Request, Response } from "@borgiq/actors";

            import { shape } from "./lib/shape.ts";

            export default async function receive(req: Request): Promise<Response> {
              return { results: shape("success") };
            }
        - path: lib/shape.ts
          content: |
            export const shape = (result: string) => ({ result });
    schemas:
      inputs:
        type: object
        properties:
          key:
            type: string
            title: Key
            description: Description of the key input
        required:
          - key
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Input Schemas

**Important:** If your code accesses `req.inputs` properties, you MUST configure both:
1. `configuration.inputs` - The actual input values (can reference `msg`, `ctx`, `secrets`)
2. `schemas.inputs` - A JSON Schema defining the input structure for validation and UI generation

### Schema Format

Input schemas use JSON Schema with BorgIQ UI extensions:

```yaml
schemas:
  inputs:
    type: object
    properties:
      apiKey:
        type: string
        title: API Key
        description: The API key for authentication
        ui:
          order: 0
          component: password
      timeout:
        type: number
        title: Timeout (seconds)
        description: Request timeout in seconds
        default: 30
        ui:
          order: 1
      debugMode:
        type: boolean
        title: Debug Mode
        description: Enable verbose logging
        default: false
        ui:
          order: 2
    required:
      - apiKey
```

### UI Extensions

The `ui` property provides hints for form rendering:

| Property | Description |
|----------|-------------|
| `order` | Display order in forms (0 = first) |
| `component` | Override default component (`password`, `textarea`, `code`, etc.) |

### Complete Example

```yaml
actors:
  ACTR01example:
    type: DenoActor
    version: 1
    name: Process Data
    msgVar: process_data
    configuration:
      inputs:
        apiKey: ${{ credentials.API_KEY }}
        timeout: 30
        data: ${{ msg.upstream_actor.body }}
      options:
        allowNet: true
      codeDir:
        - path: main.ts
          content: |
            import type { Request, Response } from "@borgiq/actors";

            export default async function receive(req: Request): Promise<Response> {
              const { apiKey, timeout, data } = req.inputs;

              const response = await fetch('https://api.example.com/process', {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${apiKey}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                signal: AbortSignal.timeout(timeout * 1000),
              });

              return { results: await response.json() };
            }
    schemas:
      inputs:
        type: object
        properties:
          apiKey:
            type: string
            title: API Key
            description: API key for the external service
            ui:
              order: 0
              component: password
          timeout:
            type: number
            title: Timeout
            description: Request timeout in seconds
            default: 30
            ui:
              order: 1
          data:
            type: object
            title: Data
            description: Data to process
            ui:
              order: 2
        required:
          - apiKey
          - data
```

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `emitArrayAsSingleMessage` | boolean | true | Emit array as single message instead of multiple messages |
| `allowNet` | boolean | false | Allow network access |
| `allowNetList` | string[] | [] | URLs allowed when `allowNet` is true |
| `denyNetList` | string[] | [] | URLs blocked when `allowNet` is true |
| `allowFs` | boolean | false | Allow file system access to temp directory |
| `env` | object[] | [] | Environment variables for the runtime |

## TypeScript Schema Definition

The complete TypeScript schema for DenoActor options:

```typescript
import { z } from 'zod';

/** One source file of the actor's project tree. */
export const CodeFileSchema = z.object({
  /** path relative to the project root; '/' separates nested folders, e.g. 'lib/util.ts' */
  path: z.string().min(1).max(255),
  /** raw file content, UTF-8 text */
  content: z.string(),
});

/**
 * The DenoActor's `configuration.codeDir`: at most 200 files and 1 MiB of content in total,
 * exactly one of them at `main.ts`, none of them using a filename the runtime reserves.
 */
export const DenoActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: 'main.ts',
  reservedPaths: DENO_RESERVED_PATHS,
});

/** The options for the DenoActor */
export const DenoActorOptionsSchema = z.object({
  emitArrayAsSingleMessage: z.boolean().nullish()
    .describe('Emit the array as a single message instead of an array of messages, defaults to true')
    .default(true),
  allowNet: z.boolean().nullish()
    .describe('Allow network access. By default when this is true, all network call is allowed but if allowNetList is provided then only that subset of URLs are allowed')
    .default(false),
  allowNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are allowed to be accessed when allowNet is true. This is ignored if allowNet is false')
    .default([]),
  denyNetList: z.array(z.string()).nullish()
    .describe('List of URLs that are denied to be accessed when allowNet is true. This is ignored if allowNet is false')
    .default([]),
  allowFs: z.boolean().nullish()
    .describe('Allow file system access to the temporary directory. By default when this is true, all file system access is allowed within the temporary directory')
    .default(false),
  env: z.array(z.object({
    name: z.string()
      .regex(/^[A-Z0-9_]+$/, 'Environment variable name must contain only uppercase letters, numbers and underscores')
      .regex(/^(?!TMPDIR$)/, 'Environment variable name cannot be TMPDIR')
      .regex(/^(?!DENO_NO_UPDATE_CHECK$)/, 'Environment variable name cannot be DENO_NO_UPDATE_CHECK')
      .describe('Environment variable name (must contain only uppercase letters, numbers and underscores)'),
    value: z.string().nullish()
      .describe('Environment variable value')
  })).nullish().default([])
    .describe('List of environment variables to pass to the Deno runtime'),
});

/** The response schema for the DenoActor */
export const DenoActorResultSchema = z.any();
```

### Environment Variables

Environment variable names must:
- Contain only uppercase letters, numbers, and underscores (`[A-Z0-9_]+`)
- Not be reserved names: `TMPDIR`, `DENO_NO_UPDATE_CHECK`

```yaml
options:
  env:
    - name: API_KEY
      value: ${{ credentials.apiKey }}
    - name: DEBUG_MODE
      value: "true"
```

## Code Files

A Deno Actor's source is a small project, held in `configuration.codeDir` as a list of `{path, content}` files:

```yaml
configuration:
  codeDir:
    - path: main.ts            # required entrypoint — exports the default handler
      content: |
        import type { Request, Response } from "@borgiq/actors";

        import { normalize } from "./lib/normalize.ts";
        import { LIMIT } from "./lib/constants.ts";

        export default async function receive(req: Request): Promise<Response> {
          return { results: normalize(req.inputs, LIMIT) };
        }
    - path: lib/normalize.ts
      content: |
        export const normalize = (input: unknown, limit: number) => ({ input, limit });
    - path: lib/constants.ts
      content: |
        export const LIMIT = 50;
```

Rules:

- **`main.ts` is required** and must be at the root of the tree — exactly one entry may have that path. The runtime imports it; a tree without it is rejected on save.
- **Import your own files relatively, with the extension**, resolved against the importing file: `./lib/normalize.ts` from `main.ts`, `./constants.ts` from inside `lib/`. An import that resolves outside the actor's own files is rejected before the code runs. Everything else comes from registry specifiers (`npm:`, `jsr:`, `https`) or `@borgiq/actors`, exactly as before.
- **`codeDir` is never interpolated.** `${{ }}` in your source is literal text, not an expression — pass runtime values through `configuration.inputs` and read them from `req.inputs`. A `${{ credentials.* }}` written into source is therefore never resolved, and source that happens to look like an expression survives verbatim.
- **Removing an entry removes the file.** The runtime rebuilds the actor's directory from the list on every code change, so a deleted helper stops being importable immediately.
- **Reserved filenames** — the runtime writes its own files into the same directory, so these are rejected on save: `server.ts`, `handler.ts`, `actor.ts`, `main_test.ts`, `deno.json`, `deno.jsonc`, `deno.lock`, `package.json`, and anything under `shared/` or `node_modules/`. Comparison is case-insensitive (`Server.ts` collides with `server.ts`). There is no user-managed dependency manifest: pin versions in the import specifiers instead.
- **Limits:** UTF-8 text only, at most 200 files, 1 MiB of content across the whole tree. Paths are relative, `/`-separated, and may not contain `.` or `..` segments.

Editing surfaces:

- **Bundle:** real files under the actor folder's `code/` directory — see [Canvas Bundles → Code actor project trees](cli/canvas-bundles.md#code-actor-project-trees).
- **Direct document / batch payload:** the `configuration.codeDir` list itself, as shown above. It is a structured array in both formats, not a YAML string.
- **Web editor:** the actor's Code page shows a file tree beside the editor; the right-hand panel on the canvas edits the entrypoint inline. The **AI code assist works on the selected file only** — it cannot see sibling files, so prompt it per file and wire the pieces together yourself.

An actor written before multi-file support carries a single `configuration.code` string. It keeps running, and saving it from the editor (or pushing it from a bundle) converts it to a one-entry `codeDir`. Never set both fields.

## Code Template

The entrypoint file, `main.ts`:

```typescript
import { concat, indexOfNeedle, endsWith } from "jsr:@std/bytes@1.0.4";
import { assertEquals } from "jsr:@std/assert@1.0.8";

import type { Request, Response } from "@borgiq/actors";
import { RetryableError, Signal, biqApi, mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // req.inputs                       — interpolated inputs for this invocation
  // req.ctx                          — RuntimeContext (org / workspace / canvas / flowrun / actor)
  // req.connection                   — the single connection's resolved config (read-only)
  // req.credentials.XXXX             — resolved secret values (read-only)
  // req.memory.stm / req.memory.ltm  — short / long term memory (value-in)
  // biqApi(url, options?)            — fetch wrapper for the BIQ Runtime API
  // mountFile(file) / stashFile(file, filename?, mimeType?)
  // throw new RetryableError() to be re-invoked with the same message; other errors are permanent.

  // Console logs are captured and stored with the flowrun
  console.log('Processing started');

  return {
    // `results` is emitted as msg.ActorName downstream (array => one message per item).
    results: { result: "data" },
    // To persist memory, return the half you changed — what you return REPLACES that
    // stored half, so spread the prior state: memory: { ltm: { ...req.memory?.ltm, key } }.
    // Omit `memory` to leave both halves unchanged. (ltm/stm need enableLTM / enableSTM.)
    // Any actor may respond to a pending request in the flow. Allowed signals:
    // Signal.webhookRespond | Signal.callableResponse | Signal.delayUntil
    // signal: Signal.webhookRespond({ statusCode: 200, body: { ok: true } }),
  };
}
```

**Return-value notes:**
- `results: undefined` (or omitting `results`) emits **no** message downstream.
- `results: null` emits a `null` message (valid JSON).
- `results: [a, b]` emits one message per item (unless `emitArrayAsSingleMessage: true`).
- `throw new RetryableError()` re-invokes the actor with the same message; all other thrown errors are permanent.

## Logging

**Always use `console.log()` for logging in Deno Actors.** All console output is captured and stored with the flowrun for debugging and visibility in the BorgIQ UI.

```typescript
// ✅ Use console.log for all logging needs
console.log('Processing item:', item.id);
console.log('Rate limit approaching');
console.log('Failed to process:', error.message);

// You can also use other console methods - they're all captured
console.warn('Rate limit approaching');
console.error('Failed to process:', error.message);
```

**Important:**
- All console output (`console.log`, `console.warn`, `console.error`) is captured and stored with the flowrun
- Logs are visible in the flowrun details in the BorgIQ UI
- Use `console.log()` liberally to aid in debugging and monitoring your workflows

## Request and Response

User code is the pure function `receive(req: Request): Promise<Response>`. There is no `actor` object — read everything from `req`, and return a `Response`.

```typescript
interface Request {
  /** interpolated inputs for this invocation (read-only) */
  inputs: { [key: string]: any };
  /** RuntimeContext (org / workspace / canvas / flowrun / actor) */
  ctx: RuntimeContext;
  /** the single connection's resolved config (read-only) */
  connection: { [key: string]: any };
  /** resolved secret values, keyed by name (read-only) */
  credentials: { [key: string]: string };
  /** short / long term memory (value-in) */
  memory: Memory;
}

interface Memory {
  /** short term memory — persists within one flowrun */
  stm: { [key: string]: any };
  /** long term memory — persists across flowruns */
  ltm: { [key: string]: any };
}

interface Response {
  /** emitted as msg.ActorName downstream (array => one message per item) */
  results?: any;
  /** return memory to persist it; omit to leave it unchanged */
  memory?: Memory;
  /** a value-typed signal built with Signal.* (webhookRespond | callableResponse | delayUntil) */
  signal?: UserSignal;
  /** fail explicitly */
  error?: { message: string; retryable?: boolean };
}
```

**Migration note (from the old `actor` object):**

| Old (removed) | New |
|---------------|-----|
| `{ inputs, actor }` parameters | `req` parameter |
| `inputs.x` | `req.inputs.x` |
| `actor.ctx` | `req.ctx` |
| `actor.connection` | `req.connection` |
| `actor.credentials` | `req.credentials` |
| `actor.stm` / `actor.ltm` (mutated in place) | `req.memory.stm` / `req.memory.ltm` (read), returned in `Response.memory` (write) |
| `actor.setSignal({ type, value })` | `return { signal: Signal.<type>(value) }` |
| `actor.assets` | Removed — manage assets via the `/assets` `biqApi` endpoints |
| `return { data }` | `return { results: { data } }` |

## Memory Types

Memory is **value-in / value-out**. Read the incoming state from `req.memory`, and **return `memory` in your `Response` to persist it**. If you omit `memory` from the response, the stored memory is left unchanged.

`req.memory` always has **both** halves present — `stm` (reclaimed when the flowrun completes) and `ltm` (survives across flowruns). The API is identical; they differ only in lifetime. The split exists so STM can be garbage-collected promptly per-flowrun — **default to `stm` for run-local state**, and use `ltm` only for values that must outlive the run.

**What you return for a half replaces that stored half — it does not merge.** Each half is persisted independently of the other, but *within* a half the returned object becomes the new stored value wholesale. So always return the complete state you want to keep:

1. **Return the full half — spread the prior state, then set your keys.** `memory: { ltm }` replaces LTM and leaves STM untouched (you don't echo back the other half — and *shouldn't*; see *Enabling* below). Returning a bare `{ cursor: nextCursor }` would drop every other LTM key.
   ```typescript
   // ✅ spread the prior LTM so existing keys survive, then set the one you changed.
   return { results, memory: { ltm: { ...req.memory?.ltm, cursor: nextCursor } } };

   // multiple keys at once (spread is undefined-safe — no `?? {}` guard):
   const ltm = { ...req.memory?.ltm, cursor: nextCursor, lastRunAt };
   return { results, memory: { ltm } };
   ```
2. **To clear a key, omit it from the snapshot you return** (it's a replace, so omission drops it). To clear a whole half, return it empty: `{ ltm: {} }`.
3. **Omit `memory` to leave everything unchanged** — only return it when you mutated something.
4. **Read with optional chaining + default** — `req.memory?.ltm?.cursor ?? 0`; each store is empty on first use.
5. **Match the store to the lifetime** — run-local scratch → `stm` (auto-reclaimed); must-outlive-the-run → `ltm`.

**Enabling is required, and you only return what's enabled.** Writing `req.memory.stm` requires `enableSTM: true`; `req.memory.ltm` requires `enableLTM: true`. Returning a **non-empty** half for a store that isn't enabled is a runtime error (`STM is not enabled for the actor` / `LTM is not enabled...`) — the other reason to return only the half you actually use. Enabling a store also **serializes** this actor's message processing — one message at a time within a flowrun (STM) or across all flowruns (LTM) — so read-modify-write is race-free.

### Short-Term Memory (STM)

Run-local state within a single flowrun; reclaimed when the flowrun completes. Read with optional chaining, and return the full STM snapshot you want stored — what you return replaces the stored STM.

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const count = (req.memory?.stm?.counter ?? 0) + 1;   // 0 on first use within the run

  // Spread the prior STM so other keys survive, then set the one you changed.
  return { results: { count }, memory: { stm: { ...req.memory?.stm, counter: count } } };
}
```

Requires `enableSTM: true` in the actor config.

### Long-Term Memory (LTM)

State that survives across flowruns — a cursor, checkpoint, or registered external ID. Same idiom as STM:

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const lastCheckedAt = req.memory?.ltm?.lastInvokedAt ?? 0;   // 0 on the very first run

  // Return the full LTM snapshot (spread the prior state). STM is left untouched —
  // echoing it back when STM is disabled would be a runtime error.
  return { results: { lastCheckedAt }, memory: { ltm: { ...req.memory?.ltm, lastInvokedAt: Date.now() } } };
}
```

**Important:** Using LTM requires `enableLTM: true` in the actor configuration:
```yaml
enableLTM: true
```

This mirrors a real incremental-poll trigger: read a `historyId`/cursor from `ltm`, fetch only what changed since, write the new cursor back via `memory: { ltm }`, and return the new items as `results`.

## Importing Libraries

> **Security rule — always pin an exact version.** Every third-party `npm:` and
> `jsr:` import MUST specify an exact version (`npm:name@x.y.z`), never a bare
> name and never a floating range (`^`, `~`, `>=`). A bare specifier like
> `npm:lodash` resolves to whatever is **latest** at the moment it is resolved —
> so a newly-published malicious or breaking release is pulled automatically.
> That is a supply-chain risk and makes deploys non-deterministic. An exact pin
> (`npm:lodash@4.17.21`) is immune to both. BorgIQ-internal specifiers
> (`@borgiq/actors`, `node:*`) are exempt — they are provided by the runtime.
>
> **When resolution happens depends on whether the workspace is deployed.** On an
> ordinary workspace, dependencies are resolved the first time the actor runs on a
> given machine. On a **deployed** workspace they are resolved once, when the
> canvas is built, and written into a lockfile that ships with the actor — every
> run from that build uses exactly those versions and resolves nothing. Either
> way an unpinned specifier means what you get depends on *when* resolution
> happened, which is the whole reason to pin. See
> [deployment.md](deployment.md).

**Imports may not leave the actor's own files.** An import that reaches outside
the actor's tree is refused when the actor loads; on a deployed workspace the
build catches it first and names the offending specifier. Relative imports
between your own files, `@borgiq/actors`, `npm:`/`jsr:`/`node:` packages and
approved `https:` hosts are all fine.

### Your Own Files

Files in the same actor (see [Code Files](#code-files)) are imported relatively, **with the file extension**, the way Deno resolves any module:

```typescript
// in main.ts
import { normalize } from "./lib/normalize.ts";
// in lib/normalize.ts
import { LIMIT } from "./constants.ts";      // relative to lib/, not to the root
```

Imports must stay inside the actor's own files. An import that resolves outside them — an absolute path, a `..` escape, a symlink out of the tree — is rejected before the code runs, with an error naming the offending specifier. Reach anything external through `npm:` / `jsr:` / `https` specifiers below.

### NPM Libraries

Use the `npm:` prefix with an exact version:

```typescript
import _ from "npm:lodash@4.17.21";
import { MongoClient } from "npm:mongodb@6.12.0";
```

### JSR/Deno Libraries

Use the `jsr:` prefix with an exact version:

```typescript
import { concat, indexOfNeedle } from "jsr:@std/bytes@1.0.4";
import { encodeHex } from "jsr:@std/encoding@1.0.5/hex";
```

**Important:** Do NOT use `deno.land` URLs. Always use `jsr:` syntax, and always pin a version.

### BorgIQ Library

Everything BorgIQ-specific is imported from the single `@borgiq/actors` specifier — types, the `Signal` constructors, `RetryableError`, and the file/API helpers:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { RetryableError, Signal, biqApi, mountFile, stashFile } from "@borgiq/actors";
```

> **Migration:** the old `@borgiq/actor` (singular) and `@borgiq/errors` specifiers are gone. Import `Request`/`Response`/`Signal`/`RetryableError`/`biqApi`/`mountFile`/`stashFile` from `@borgiq/actors`.

### Recommended Libraries

These are the recommended libraries for common tasks in Deno actors:

#### SQLite Database

Use `node:sqlite` for embedded SQLite databases:

```typescript
import { DatabaseSync } from "node:sqlite";
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Create or open a database file
  const db = new DatabaseSync('database.db');

  // Create a table
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL
    )
  `);

  // Insert data
  const insert = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
  insert.run('Alice', 'alice@example.com');

  // Query data
  const query = db.prepare('SELECT * FROM users WHERE name = ?');
  const users = query.all('Alice');

  // Close the database
  db.close();

  return { results: { users } };
}
```

**Key features:**
- Native Node.js SQLite module (no external dependencies)
- Synchronous API for simple operations
- Works well with `allowFs: true` for persistent storage
- Can be combined with LTM-enabled temp directory for cross-flowrun persistence

## File Operations

BorgIQ provides utilities for working with files in Deno actors.

**Important:** `mountFile` and `stashFile` require network access to communicate with BorgIQ APIs. You must enable `allowNet: true` in your actor's configuration options when using these functions.

```yaml
options:
  allowNet: true  # Required for mountFile/stashFile
```

### mountFile

Mounts a BIQFile to the local filesystem and returns the path. Use this to access files passed as inputs.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { mountFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Mount the input file to local filesystem
  const filePath = await mountFile(req.inputs.uploadedFile);

  // Now you can read it with Deno APIs
  const content = await Deno.readTextFile(filePath);

  return { results: { content } };
}
```

### stashFile

Uploads a file to BorgIQ storage and returns a BIQFile object that can be passed to downstream actors.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { stashFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Create some content
  const csvContent = "name,age\nAlice,30\nBob,25";
  const encoder = new TextEncoder();
  const buffer = encoder.encode(csvContent);

  // Upload to BorgIQ storage
  const biqFile = await stashFile(buffer, 'output.csv', 'text/csv');

  // Return the file reference for downstream actors
  return { results: { file: biqFile } };
}
```

**Signature:** `stashFile(file: File | Blob | ArrayBuffer | ReadableStream<BlobPart> | string, filename?: string, mimeType?: string): Promise<BIQFile>` — the `file` can be raw binary, a stream, or a path string.

### File Processing Example

```typescript
import type { Request, Response } from "@borgiq/actors";
import { mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Mount input file
  const inputPath = await mountFile(req.inputs.inputFile);

  // Process the file
  const content = await Deno.readTextFile(inputPath);
  const processed = content.toUpperCase();

  // Create temp directory for output
  const tempDir = await Deno.makeTempDir({ prefix: "process_" });
  const outputPath = `${tempDir}/processed.txt`;
  await Deno.writeTextFile(outputPath, processed);

  // Read and stash the output
  const outputBuffer = await Deno.readFile(outputPath);
  const outputFile = await stashFile(outputBuffer, 'processed.txt', 'text/plain');

  // Clean up
  await Deno.remove(tempDir, { recursive: true });

  return { results: { outputFile } };
}
```

## BIQ Runtime API

The `biqApi` function provides authenticated access to BorgIQ Runtime APIs from within Deno actors. This enables advanced workflows that require direct API access beyond what standard actors provide.

```typescript
import { biqApi } from "@borgiq/actors";

const response = await biqApi('/endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: 'value' }),
});

const result = await response.json();
```

### Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/collections` | POST | All Collection API operations (action in request body) |
| `/issueCallbackToken` | POST | Issue a callback token for async workflows |
| `/files/{fileId}/downloadUrl` | GET | Get a signed download URL for a file (supports `?expiresInMinutes=N&downloadAsAttachment=true`) |
| `/files/upload` | POST | Upload multiple files (multipart) |
| `/files/upload` | PUT | Stream a single file directly to S3 |
| `/files/download` | GET | Stream file content from S3 |
| `/files/updateUploads` | POST | Update file status after presigned URL upload |

> **File operations:** Prefer `mountFile` and `stashFile` from `@borgiq/actors` instead of calling the `/files/*` endpoints directly. These helpers handle download, upload, temp file management, and cleanup automatically. The raw endpoints above are what `mountFile`/`stashFile` use under the hood — only call them directly if you need advanced control (e.g., custom expiration, presigned URL workflows).

| `/assets` | GET | List workspace assets |
| `/assets` | POST | Create a new asset |
| `/assets/{key}` | PUT | Update an asset |
| `/assets/{key}` | DELETE | Delete an asset |
| `/secrets` | GET | Get decrypted secrets |
| `/connections/{key}` | GET | Get decrypted connection credentials |
| `/publicKey` | GET | Get workspace public key (for encrypting sensitive data) |
| `/sendEmail` | POST | Send an email |
| `/interfaces/status` | PUT | Update interface status display |
| `/toolkit/chatCompletion` | POST | AI chat completion (internal) |
| `/dataStore/*` | Various | Legacy data store operations (deprecated — use `/collections` instead) |

> **Assets:** the old `actor.assets` field no longer exists in the `Request`. To read or manage workspace assets from actor code, use the `/assets` `biqApi` endpoints above.

### When to Use `biqApi` vs Standard Actors

| Scenario | Use |
|----------|-----|
| Structured persistent storage | **CollectionActor** |
| Queue operations (enqueue/dequeue) | **CollectionActor** (queue-via-Collections pattern) |
| Multiple storage operations in sequence | **`biqApi`** (reduces actor count) |
| Conditional storage based on complex logic | **`biqApi`** (full code control) |
| Issue callback token with custom logic | **`biqApi`** |
| Standard callback token workflow | **MessageProcessorActor** (`issueCallbackToken` action) |

### Collection API (Recommended)

The Collection API provides structured, persistent storage organized into named collections, backed by DynamoDB. All operations use a single `POST /collections` endpoint with the `action` field in the request body.

**For full documentation** of all 13 actions, parameters, conditions, concurrent update patterns, DynamoDB behavior, batch operations, transactions, and error codes, see [collection-api.md](collection-api.md).

**Response format:** All Collection API calls return `{ ok: boolean, value: T, error?: { code, message } }`, where `T` varies by action (e.g. `getItem` → `{ key, value } | null`, `query` → `{ items[], count, lastKey? }`, `listCollections` → `{ collections[], lastKey? }`, `deleteItem` → `{ deleted: number }`). See [collection-api.md](collection-api.md) for the complete return type table.

#### Helper Pattern

Use a typed helper to unwrap the response envelope and handle errors:

```typescript
import { biqApi } from "@borgiq/actors";

async function collectionsApi<T = unknown>(body: Record<string, unknown>): Promise<T> {
  const res = await biqApi("/collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const json = (await res.json()) as { ok: boolean; value: T; error?: { code: string; message: string } };
  if (!json.ok) {
    const err = new Error(json.error?.message || "Action failed");
    (err as any).code = json.error?.code;
    throw err;
  }
  return json.value;
}
```

**Quick reference — common actions:**

```typescript
// putItem — full replace
await collectionsApi({ action: "putItem", collection: "my-col", key: "k1", value: { name: "Alice" } });

// getItem — eventually consistent read (returns null if missing)
const item = await collectionsApi({ action: "getItem", collection: "my-col", key: "k1" });

// updateItem — shallow field merge (only listed fields change, others preserved)
await collectionsApi({ action: "updateItem", collection: "my-col", key: "k1", value: { email: "new@email.com" } });

// updateItem with atomic counter
await collectionsApi({ action: "updateItem", collection: "my-col", key: "k1", atomicCounters: { visits: 1 } });

// query — prefix search
const results = await collectionsApi({ action: "query", collection: "my-col", key: "user:*" });

// deleteItem
await collectionsApi({ action: "deleteItem", collection: "my-col", key: "k1" });
```

See [collection-api.md](collection-api.md) for `batchGetItem`, `batchWriteItem`, `transactWrite`, `transactGet`, conditions, concurrent update patterns, and DynamoDB mapping details.



### Callback Token API

Issue callback tokens for async workflows where you need to pause execution and wait for an external event (like an email reply or approval).

```typescript
import type { Request, Response } from "@borgiq/actors";
import { biqApi } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const response = await biqApi('/issueCallbackToken', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      expiresAfterInSeconds: req.inputs.expiresAfterInSeconds ?? 3600, // Default 1 hour
    }),
  });

  return { results: await response.json() };
}
```

**Response:**
```json
{
  "token": "cbt_01HQXYZ...",
  "url": "https://api.borgiq.com/callback/cbt_01HQXYZ...",
  "expiresAt": "2024-01-15T12:00:00Z"
}
```

**Key fields:**
- `token` - The callback token identifier
- `url` - The URL that external systems use to trigger the callback (POST to this URL to notify the waiting workflow)
- `expiresAt` - When the token expires

**Use case:** Issue a callback token, store it in a Collection keyed by a correlation ID (like email thread ID) using `putItem`, then use `waitForCallbackToken` in another actor to pause until an external system POSTs to the callback URL.

### File Download URL API

Get a signed download URL for a BIQFile. Useful when you need to download file content within your Deno code or pass the URL to an external service.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { biqApi } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Extract file ID from string or BIQFile object
  const fileId = typeof req.inputs.file === 'string'
    ? req.inputs.file
    : req.inputs.file?.id;

  if (!fileId) {
    throw new Error('File ID is required');
  }

  const expiresAfterInMinutes = req.inputs.expiresAfterInMinutes ?? 60;

  const queryParams = new URLSearchParams({
    expiresAfterInMinutes: String(expiresAfterInMinutes),
  });

  const response = await biqApi(`/files/${fileId}/downloadUrl?${queryParams.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return { results: await response.json() };
}
```

**Response:**
```json
{
  "url": "https://storage.borgiq.com/files/...",
  "expiresAt": "2024-01-15T13:00:00Z"
}
```

**Use case:** Get a download URL to pass to an external API, or to download and process file content within the same actor.

### Network Configuration for biqApi

When using `biqApi`, ensure network access is enabled:

```yaml
options:
  allowNet: true
  allowNetList:
    - api.borgiq.com
```

## Error Handling

You can fail an actor in two ways: throw, or return an `error` on the `Response`.

### Retryable Errors

Throw `RetryableError` for transient failures that should be retried:

```typescript
import { RetryableError } from "@borgiq/actors";

if (response.status === 401) {
  throw new RetryableError('Authentication failed, token might need refresh');
}
```

### Permanent Errors

Regular errors are treated as permanent failures:

```typescript
if (!req.inputs.required_field) {
  throw new Error('Required field is missing');
}
```

### Explicit Error via Response

You may also return an explicit error instead of throwing:

```typescript
return {
  error: { message: 'Upstream service unavailable', retryable: true },
};
```

## Credentials and Connections

**Key rule:** An actor can have **only ONE connection**, but **multiple secrets (credentials)**. Use `req.connection` for the single app/auth source; use `req.credentials` for individual secret values.

- `req.connection` — the single connection's resolved config object (e.g. OAuth tokens at `req.connection.auth.values.token`).
- `req.credentials` — a map of secret name → resolved string value (`req.credentials.MY_SECRET`).

### Accessing Connection Auth

For OAuth and other connection-based auth (single connection):

```typescript
const token = req.connection.auth.values.token;

const response = await fetch(url, {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

### Accessing Credentials (Secrets)

Credentials are resolved secret values, keyed by name:

```typescript
const apiKey = req.credentials.OPENAI_API_KEY;
const mongoUser = req.credentials.MONGO_USERNAME;
const mongoPass = req.credentials.MONGO_PASSWORD;
```

Reference them in the actor configuration with `${{ credentials.NAME }}`:

```yaml
configuration:
  inputs:
    apiKey: ${{ credentials.OPENAI_API_KEY }}
```

## Signals

Signals communicate with the Orchestrator for special operations. In the new model, a signal is a **value** returned on the `Response` and built with a `Signal.*` constructor — there is no `actor.setSignal()`.

### User-Settable Signals

An actor returns at most one signal via `Response.signal`. The constructors available to actor code are:

| Constructor | Purpose | Value shape |
|-------------|---------|-------------|
| `Signal.webhookRespond(value)` | Respond to a pending webhook request | `{ statusCode: number, headers?: object, body?: any }` |
| `Signal.callableResponse(value)` | Respond to a pending callable/subflow request | `{ payload: object, throwError?: boolean }` |
| `Signal.delayUntil(value)` | Delay message emission until a time | `{ delayUntil: string }` (ISO 8601) |

> Other orchestrator signal types (`callFlow`, `waitForCallbackToken`, `notifyCallbackToken`, the `interface*` family, `ai`, `aiAgent`) are driven by their dedicated actors / the MessageProcessorActor, not set from Deno code.

### Using Signals

```typescript
import type { Request, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Delay until a specific time
  return {
    results: { queued: true },
    signal: Signal.delayUntil({ delayUntil: new Date(Date.now() + 60000).toISOString() }),
  };
}
```

### WebhookRespond Signal

Use the `webhookRespond` signal to return an HTTP response directly from a Deno Actor instead of using a separate WebhookResponseActor. This saves ~300ms per request by eliminating the extra actor hop.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const result = { success: true, data: req.inputs.payload };

  // Respond directly to the webhook caller, and still emit downstream
  return {
    results: result,
    signal: Signal.webhookRespond({
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: result,
    }),
  };
}
```

**Why use `webhookRespond` instead of WebhookResponseActor:**

| Approach | Latency | Actor count |
|----------|---------|-------------|
| WebhookResponseActor | +~300ms | Extra actor in flow |
| `webhookRespond` signal | Immediate | Handled in same actor |

**Note:** The signal sends the response back to the webhook caller as soon as the actor completes. The actor's `results` still propagate downstream as normal.

## Network Access

Enable network access in options:

```yaml
options:
  allowNet: true
  allowNetList:
    - api.openai.com
    - www.googleapis.com
```

### Making HTTP Requests

```typescript
const response = await fetch('https://api.openai.com/v1/embeddings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${req.credentials.OPENAI_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'text-embedding-3-small',
    input: texts,
  }),
});

if (!response.ok) {
  throw new Error(`API error: ${response.status}`);
}

const data = await response.json();
```

## Runtime Context

Access runtime information via `req.ctx`:

```typescript
interface RuntimeContext {
  org: { id: string; name: string };
  workspace: {
    id: string;
    slug: string;
    name: string;
    denoActorTimeoutInSeconds: number;
  };
  canvas: { id: string; slug: string; name: string; /* webhookTriggers, interfaceTriggers, appTriggers */ };
  actor: { id: string; type: string; name: string; msgVar: string; description: string; isActive: boolean; continueOnError: boolean };
  flowrun: { id: string; createdAt: string };
  triggerActor: { id: string; type: string; name: string; msgVar: string };
  sourceActor?: { id: string; type: string; name: string; msgVar: string };
  sourceMsgId?: string;
  parentFlowrun?: { workspace: any; canvas: any; flowrunId: string; actorId: string; flowrunJobId: string };
}
```

Usage:
```typescript
console.log(`Running in workspace: ${req.ctx.workspace.name}`);
console.log(`Flowrun ID: ${req.ctx.flowrun.id}`);
```

## Return Values

The `results` field of the returned `Response` becomes available as `msg.actor_msgvar` in downstream actors, where `actor_msgvar` is the actor's `msgVar` property.

| Return | Behavior |
|--------|----------|
| `return { results: { data } }` | Emit object as message |
| `return { results: [item1, item2] }` | Emit multiple messages (one per item) |
| `return { results: null }` | Emit null message (valid JSON) |
| `return { results: undefined }` or `return {}` | Do NOT emit any message |
| `return { results, memory }` | Emit message AND persist memory |

### Emitting Arrays

By default, returning an array under `results` emits multiple messages. To emit as single message:

```yaml
options:
  emitArrayAsSingleMessage: true
```

## Examples

### Basic Example: Return Deno Info

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  return {
    results: {
      version: Deno.version,
      mainModule: Deno.mainModule,
    },
  };
}
```

### LTM Example: Track Last Invocation

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const ltm = req.memory.ltm ?? {};
  const lastCheckedAt = ltm.lastInvokedAt ?? 0;

  ltm.lastInvokedAt = Date.now();

  // Return the full ltm snapshot; stm is omitted, so it's left untouched.
  return { results: { lastCheckedAt }, memory: { ltm } };
}
```

### API Example: Google Calendar Events

```typescript
import { RetryableError } from "@borgiq/actors";
import type { Request, Response } from "@borgiq/actors";
import _ from "npm:lodash@4.17.21";

const MAX_PROCESSED_EVENTS = 300;

export default async function receive(req: Request): Promise<Response> {
  const token = req.connection.auth.values.token;

  if (!token) {
    throw new Error('No OAuth2 token found in connection');
  }

  const calendarId = req.inputs.calendarId;
  const now = new Date();
  const timeMin = new Date(now.getTime() - 15 * 60 * 1000);
  const timeMax = new Date(now.getTime() + 15 * 60 * 1000);

  const encodedCalendarId = encodeURIComponent(calendarId);
  const params = new URLSearchParams({
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
    singleEvents: 'true',
    orderBy: 'startTime',
  });

  const response = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/${encodedCalendarId}/events?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      throw new RetryableError('Authentication failed');
    }
    throw new Error(`Failed to fetch events: ${response.statusText}`);
  }

  const data = await response.json();

  // Track processed events in LTM (read from req.memory.ltm)
  const processedEventIds = new Map(
    Object.entries(_.get(req.memory.ltm, "processedEventIds", {}))
  );

  const eventsToEmit = [];

  for (const event of data.items || []) {
    if (processedEventIds.has(event.id)) continue;

    eventsToEmit.push({
      id: event.id,
      summary: event.summary,
      start: event.start,
      end: event.end,
    });

    processedEventIds.set(event.id, true);
  }

  // Trim and persist LTM via Response.memory
  const trimmed = processedEventIds.size > MAX_PROCESSED_EVENTS
    ? Object.fromEntries(Array.from(processedEventIds.entries()).slice(-MAX_PROCESSED_EVENTS))
    : Object.fromEntries(processedEventIds);

  const ltm = req.memory.ltm ?? {};
  ltm.processedEventIds = trimmed;

  return {
    results: eventsToEmit,
    memory: { ltm },
  };
}
```

### Database Example: MongoDB Ping

```typescript
import { MongoClient, ServerApiVersion } from 'npm:mongodb@6.12.0';
import type { Request, Response } from "@borgiq/actors";

let client = null;

export default async function receive(req: Request): Promise<Response> {
  // Initialize client once, reuse across invocations
  if (client === null) {
    const uri = `mongodb+srv://${req.credentials.MONGO_USERNAME}:${req.credentials.MONGO_PASSWORD}@${req.inputs.cluster}/?retryWrites=true&w=majority`;
    client = new MongoClient(uri, {
      serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
      }
    });
    await client.connect();
  }

  const ping = await client.db("admin").command({ ping: 1 });
  return { results: ping };
}
```

## Checkpointing for Resumable Operations

Since Deno Actors run in AWS Lambda (max 15 minutes), long-running operations must implement checkpointing. There are two approaches:

| Approach | How It Works | Best For |
|----------|--------------|----------|
| **LTM-based** | Actor stores checkpoint in `req.memory.ltm` (returned in `Response.memory`) | Self-contained actors, simple flows |
| **Input-based** | Checkpoint passed via `req.inputs`, emitted in `Response.results` | Complex flows, external orchestration |

**Important:** When implementing checkpointing, ask the user which approach they prefer.

### Checkpointing Large Datasets with Stashed Files

When working with large datasets that cannot fit in LTM or would be expensive to serialize repeatedly, use `stashFile` to persist intermediate data between invocations:

1. Write the working dataset to a temporary file
2. Stash the file to BorgIQ storage
3. Include the BIQFile reference in your checkpoint/cursor
4. On resume, mount the file and continue processing

```typescript
import type { Request, Response } from "@borgiq/actors";
import { mountFile, stashFile } from "@borgiq/actors";

interface Checkpoint {
  lastProcessedIndex: number;
  dataFile: any;  // BIQFile reference
}

export default async function receive(req: Request): Promise<Response> {
  const checkpoint = req.memory.ltm.checkpoint as Checkpoint | undefined;
  let workingData: any[] = [];
  let startIndex = 0;

  if (checkpoint?.dataFile) {
    // Resume: mount the stashed file and load data
    const dataPath = await mountFile(checkpoint.dataFile);
    const content = await Deno.readTextFile(dataPath);
    workingData = JSON.parse(content);
    startIndex = checkpoint.lastProcessedIndex;
    console.log(`Resuming from index ${startIndex}, loaded ${workingData.length} items`);
  } else {
    // First run: fetch initial dataset
    workingData = await fetchLargeDataset();
  }

  // Process items with time budget
  const startTime = Date.now();
  const BUFFER_TIME_MS = 30000;
  const maxRunTimeMs = req.inputs.maxRunTimeMs || 240000;

  for (let i = startIndex; i < workingData.length; i++) {
    if ((Date.now() - startTime) > (maxRunTimeMs - BUFFER_TIME_MS)) {
      // Running low on time - checkpoint and exit
      const tempDir = await Deno.makeTempDir({ prefix: "checkpoint_" });
      const tempPath = `${tempDir}/data.json`;
      await Deno.writeTextFile(tempPath, JSON.stringify(workingData));
      const stashedFile = await stashFile(await Deno.readFile(tempPath), 'checkpoint-data.json', 'application/json');
      await Deno.remove(tempDir, { recursive: true });

      const ltm = req.memory.ltm ?? {};
      ltm.checkpoint = { lastProcessedIndex: i, dataFile: stashedFile };

      return { results: { status: 'in_progress', processedSoFar: i }, memory: { ltm } };
    }

    await processItem(workingData[i]);
  }

  // Complete - clear the checkpoint. Persistence REPLACES the ltm half, so spread
  // the prior ltm and drop `checkpoint` from the snapshot; other keys are preserved.
  const { checkpoint: _done, ...ltm } = req.memory.ltm ?? {};
  return { results: { status: 'complete', totalProcessed: workingData.length }, memory: { ltm } };
}
```

**Benefits:**
- Avoids LTM size limits for large datasets
- Reduces serialization overhead on each checkpoint
- Data persists reliably in BorgIQ storage
- Works with both LTM-based and input-based checkpointing

### Time Budget Management

Always reserve buffer time before Lambda timeout:

```typescript
const startTime = Date.now();
const maxRunTimeMs = req.inputs.maxRunTimeMs || 240000; // 4 minutes default
const BUFFER_TIME_MS = 30000; // 30 seconds buffer

function hasTimeRemaining(): boolean {
  return (Date.now() - startTime) < (maxRunTimeMs - BUFFER_TIME_MS);
}
```

### Approach 1: LTM-Based Checkpointing

The actor manages its own checkpoint state using Long-Term Memory — read from `req.memory.ltm`, persist via `Response.memory`.

```typescript
import type { Request, Response } from "@borgiq/actors";

interface Checkpoint {
  lastProcessedId: string | null;
  processedCount: number;
  timestamp: string;
}

export default async function receive(req: Request): Promise<Response> {
  const startTime = Date.now();
  const maxRunTimeMs = req.inputs.maxRunTimeMs || 240000;
  const BUFFER_TIME_MS = 30000;

  // Resume from LTM checkpoint if exists (null/undefined when none)
  const checkpoint = req.memory?.ltm?.checkpoint as Checkpoint | null | undefined;
  let lastProcessedId = checkpoint?.lastProcessedId || null;

  if (checkpoint) {
    console.log(`Resuming from checkpoint: ${checkpoint.processedCount} items processed`);
  }

  const results = {
    processed: checkpoint?.processedCount || 0,
    hasMore: true,
  };

  const ltm = req.memory.ltm ?? {};

  while (results.hasMore && (Date.now() - startTime) < (maxRunTimeMs - BUFFER_TIME_MS)) {
    const batch = await fetchBatch(lastProcessedId, req.inputs.batchSize || 50);

    if (batch.length === 0) {
      results.hasMore = false;
      break;
    }

    for (const item of batch) {
      await processItem(item);
      results.processed++;
      lastProcessedId = item._id;
    }

    // Update checkpoint after each batch
    ltm.checkpoint = {
      lastProcessedId,
      processedCount: results.processed,
      timestamp: new Date().toISOString(),
    };
  }

  // Clear checkpoint on completion. `ltm` holds the full prior memory (read from
  // req.memory.ltm above), and persistence REPLACES the stored half with what we
  // return, so just delete the key — other ltm keys survive because they're still in `ltm`.
  if (!results.hasMore) {
    delete ltm.checkpoint;
    console.log('Processing complete, checkpoint cleared');
  }

  // Return the full ltm snapshot; stm is omitted, so it's left untouched.
  return { results, memory: { ltm } };
}
```

### Approach 2: Input-Based Checkpointing

Checkpoint cursor is passed in via `req.inputs` and emitted in `Response.results` for external management.

```typescript
import type { Request, Response } from "@borgiq/actors";

interface CursorData {
  lastProcessedId: string | null;
  processedCount: number;
}

export default async function receive(req: Request): Promise<Response> {
  const startTime = Date.now();
  const maxRunTimeMs = req.inputs.maxRunTimeMs || 240000;
  const BUFFER_TIME_MS = 30000;

  // Resume from cursor provided in inputs (if any)
  const cursor = req.inputs.cursor as CursorData | undefined;
  let lastProcessedId = cursor?.lastProcessedId || null;

  if (cursor) {
    console.log(`Resuming from cursor: ${cursor.processedCount} items previously processed`);
  }

  const results = {
    processed: cursor?.processedCount || 0,
    hasMore: true,
    cursor: null as CursorData | null,  // Emit cursor for next invocation
  };

  while (results.hasMore && (Date.now() - startTime) < (maxRunTimeMs - BUFFER_TIME_MS)) {
    const batch = await fetchBatch(lastProcessedId, req.inputs.batchSize || 50);

    if (batch.length === 0) {
      results.hasMore = false;
      break;
    }

    for (const item of batch) {
      await processItem(item);
      results.processed++;
      lastProcessedId = item._id;
    }
  }

  // Emit cursor if there's more to process
  // The caller is responsible for passing this back in the next invocation
  if (results.hasMore) {
    results.cursor = {
      lastProcessedId,
      processedCount: results.processed,
    };
    console.log('Emitting cursor for continuation');
  }

  return { results };
}
```

**Usage:** The downstream flow or orchestrator receives `results.cursor` and passes it back as `req.inputs.cursor` on the next invocation.

### Hash-Based Change Detection

For idempotent operations, detect when source data has changed:

```typescript
import { encodeHex } from 'jsr:@std/encoding@1.0.5/hex';

async function calculateHash(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return encodeHex(new Uint8Array(hashBuffer));
}

// Skip unchanged items
const contentHash = await calculateHash(item.content);
if (item.processedHash === contentHash) {
  results.skipped++;
  continue;
}
```

### Handling Rate Limits

Use `RetryableError` for transient failures:

```typescript
import { RetryableError } from "@borgiq/actors";

if (response.status === 429) {
  throw new RetryableError('Rate limit reached, will retry');
}
```

## Best Practices

1. **Initialize clients once** - Store clients at module level, reuse across invocations
2. **Use LTM for state tracking** - Read from `req.memory.ltm`, persist via `Response.memory`
3. **Handle timeouts gracefully** - Save state before timeout, resume on next invocation
4. **Use RetryableError** - For transient failures (rate limits, auth refresh)
5. **Log progress** - Use `console.log()` for debugging (captured in flowrun logs)
6. **Validate inputs early** - Check required fields, secrets, and connections at the start; fail fast with clear errors
7. **Keep actors focused** - Split complex logic into multiple actors
8. **Prefer `fetch()` over SDK libraries** - Use native `fetch()` for API calls unless the user explicitly requests a library
9. **Prefer native code over CLI tools** - Use libraries for operations like zip/unzip; only use CLI if no native facility exists
10. **Use Deno APIs for file operations** - Use `Deno.makeTempDir()`, not hardcoded paths like `/tmp`
11. **Pin dependency versions** - Always import third-party `npm:`/`jsr:` libraries with an exact version (`npm:jszip@3.10.1`), never a bare name or floating range — prevents supply-chain attacks and non-deterministic deploys. See [Importing Libraries](#importing-libraries)

### Prefer `fetch()` Over Pre-Built Libraries

Always prefer using the native `fetch()` API for HTTP requests to external services instead of pre-built SDK libraries. This keeps the code lightweight, reduces dependencies, and provides more control.

**Only use pre-built libraries** (via `npm:xxx` or `jsr:xxx`) when the user explicitly requests them.

```typescript
// ✅ Correct - use native fetch for API calls
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${req.credentials.OPENAI_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello' }],
  }),
});

const data = await response.json();

// ❌ Avoid - don't use SDK libraries unless explicitly requested
import OpenAI from 'npm:openai@4.77.0';  // Only use if user specifically asks for it
const openai = new OpenAI({ apiKey: req.credentials.OPENAI_API_KEY });
```

**Why prefer `fetch()`:**

| Aspect | `fetch()` | SDK Libraries |
|--------|-----------|---------------|
| Dependencies | None (built-in) | Adds external dependency |
| Bundle size | Minimal | Can be large |
| Control | Full control over requests | Abstracted away |
| Debugging | Easy to inspect requests/responses | May hide details |
| Compatibility | Always available in Deno | May have compatibility issues |

**When to use libraries:** Only when the user explicitly asks for a specific library (e.g., "use the OpenAI SDK" or "use `npm:axios`"), or when the API requires complex authentication flows that would be impractical to implement manually.

### Validate Credentials and Connections

Always validate that required credentials and connections are present before using them. Throw descriptive errors if missing.

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // ✅ Validate credentials upfront
  if (!req.credentials.OPENAI_API_KEY) {
    throw new Error('Missing required credential: OPENAI_API_KEY. Configure it in workspace credentials.');
  }

  if (!req.credentials.MONGO_USERNAME || !req.credentials.MONGO_PASSWORD) {
    throw new Error('Missing required credentials: MONGO_USERNAME and MONGO_PASSWORD');
  }

  // ✅ Validate connection auth
  if (!req.connection?.auth?.values?.token) {
    throw new Error('Missing OAuth token. Ensure connection is configured and authorized.');
  }

  // ✅ Validate required inputs
  if (!req.inputs.database || !req.inputs.collection) {
    throw new Error('Missing required inputs: database and collection');
  }

  // Now safe to proceed...
  return { results: {} };
}
```

### Prefer Native Code Over CLI Tools

Use JavaScript/TypeScript libraries instead of CLI tools. **Shell commands are not available** in the Deno Actor Lambda environment — there is no access to tools like `zip`, `unzip`, `curl`, `wget`, `jq`, `git`, `base64`, `shasum`, etc.

```typescript
// ✅ Correct - use native libraries
import { ZipReader, ZipWriter } from 'jsr:@peterblockman/zip@1.0.0';
import { Buffer } from 'node:buffer';

// Unzip using library
const zipData = await Deno.readFile('archive.zip');
const reader = new ZipReader(new Blob([zipData]).stream());
const entries = await reader.getEntries();

// ❌ Wrong - don't shell out to CLI tools
const process = new Deno.Command('unzip', { args: ['archive.zip'] });  // Don't do this
```

**Common operations with native alternatives:**

| Operation | Use This | Not This |
|-----------|----------|----------|
| Zip/Unzip | `jsr:@peterblockman/zip` or `npm:jszip` | `unzip`, `zip` CLI |
| JSON processing | Native `JSON.parse/stringify` | `jq` CLI |
| HTTP requests | Native `fetch()` | `curl`, `wget` CLI |
| Base64 encoding | `btoa()`/`atob()` or `jsr:@std/encoding` | `base64` CLI |
| Hashing | `crypto.subtle.digest()` | `shasum`, `md5` CLI |
| File operations | `Deno.readFile`, `Deno.writeFile` | `cat`, `cp`, `mv` CLI |
