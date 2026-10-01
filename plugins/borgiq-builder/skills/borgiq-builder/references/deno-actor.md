# Deno Actor Reference

The DenoActor runs TypeScript/JavaScript in a sandboxed Deno runtime. This file covers what is Deno-only:
configuration, options, imports and pinning, files, the no-shell rule, the entrypoint template and examples. The
contract, emit rules, errors, source files, credentials, memory, signals and the runtime API are shared with Python and
the [UniversalTriggerActor](universal-trigger-actor.md): read [code-actor-runtime.md](code-actor-runtime.md) with it.

## Contents

- [Configuration](#configuration)
- [Options](#options)
- [Imports and pinning](#imports-and-pinning)
- [Files and temporary storage](#files-and-temporary-storage)
- [No shell](#no-shell)
- [Runtime API helper](#runtime-api-helper)
- [Template](#template)
- [Examples](#examples)
- [Best practices](#best-practices)

## Configuration

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

The `codeDir` rules and `schemas.inputs` are in [code-actor-runtime.md](code-actor-runtime.md#source-files-codedir).

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `emitArrayAsSingleMessage` | boolean | `true` | An array under `results` is one message; `false` emits one message per item |
| `allowNet` | boolean | `false` | Network access; required for `fetch`, `biqApi`, `mountFile` and `stashFile` |
| `allowNetList` | string[] | `[]` | With `allowNet`, allow only these hosts (the BorgIQ API host is added automatically); empty allows all |
| `denyNetList` | string[] | `[]` | With `allowNet`, hosts to block |
| `allowFs` | boolean | `false` | Read and write the actor's temporary directory |
| `env` | `{ name, value }[]` | `[]` | Environment variables for the runtime. Names match `[A-Z0-9_]+`; `TMPDIR` and `DENO_NO_UPDATE_CHECK` are reserved. Values may use expressions, e.g. `${{ credentials.apiKey }}` |

Exact schema: [typescript/actorSchemas/task/deno.md](typescript/actorSchemas/task/deno.md).

## Imports and pinning

- **Your own files:** import them relatively, **with the extension**, resolved against the importing file:
  `./lib/normalize.ts` from `main.ts`, `./constants.ts` from inside `lib/`.
- **npm and JSR:** `npm:name@x.y.z` and `jsr:@scope/name@x.y.z`, always an exact version, never a bare name or a
  floating range ([why](code-actor-runtime.md#dependencies-and-deployed-workspaces)). The runtime refuses a version
  published less than 7 days ago: pin one at least a week old. Do not use `deno.land` URLs: use `jsr:`.
- **`https:` modules** load only from `deno.land`, `jsr.io`, `esm.sh`, `raw.esm.sh`, `cdn.jsdelivr.net`,
  `raw.githubusercontent.com` and `gist.githubusercontent.com`, and skip the 7-day check.
- **BorgIQ:** import everything from the single `@borgiq/actors` specifier: `Request`, `Response`, `TriggerRequest`,
  `Signal`, `RetryableError`, `biqApi`, `mountFile`, `stashFile`. It and `node:*` built-ins need no version.
- **Imports may not leave the actor's own files.** An import that resolves outside the tree (an absolute path, a `..`
  escape, a symlink out) is refused when the actor loads: "This actor imports a module outside its own code directory,
  and the runtime refused to load it." On a deployed workspace the build rejects it first and names the specifier.

```typescript
import _ from "npm:lodash@4.17.21";
import { encodeHex } from "jsr:@std/encoding@1.0.5/hex";
import type { Request, Response } from "@borgiq/actors";
import { normalize } from "./lib/normalize.ts";      // in lib/normalize.ts: import { LIMIT } from "./constants.ts";
```

## Files and temporary storage

With `allowFs: true` the actor can read and write its temporary directory, `TMPDIR`
([where it lives and how long files last](code-actor-runtime.md#temporary-files)). Never hardcode `/tmp/...` paths.

- `Deno.makeTempDir({ prefix })` creates a new, unique directory there; remove it when done.
- `tmpdir()` from `node:os` returns the directory itself. With LTM enabled it is the same path for every flowrun, so a
  file written there can serve a later flowrun in the same warm container.
- `node:sqlite` (`DatabaseSync`) gives an embedded database with no dependency: open the file under `tmpdir()`, not a
  relative path (the working directory is the read-only code tree).
- `mountFile(file)` and `stashFile(file: File | Blob | ArrayBuffer | ReadableStream<BlobPart> | string, filename?,
  mimeType?): Promise<BIQFile>` also need `allowNet: true`; a string `file` is a path.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const inputPath = await mountFile(req.inputs.inputFile);           // a BIQFile input → local path
  const processed = (await Deno.readTextFile(inputPath)).toUpperCase();

  const tempDir = await Deno.makeTempDir({ prefix: "process_" });
  const outputPath = `${tempDir}/processed.txt`;
  await Deno.writeTextFile(outputPath, processed);
  const outputFile = await stashFile(await Deno.readFile(outputPath), "processed.txt", "text/plain");
  await Deno.remove(tempDir, { recursive: true });

  return { results: { outputFile } };                                 // a BIQFile for downstream actors
}
```

## No shell

A Deno actor cannot run commands: there is no `zip`, `unzip`, `curl`, `wget`, `jq`, `git`, `base64`, `shasum` or any
other CLI, and `new Deno.Command(...)` is refused. Use a library. When a CLI tool is truly needed, use a PythonActor.

| Operation | Use | Not |
|---|---|---|
| Zip/unzip | `jsr:@peterblockman/zip` or `npm:jszip` | `unzip`, `zip` |
| JSON processing | `JSON.parse` / `JSON.stringify` | `jq` |
| HTTP requests | `fetch()` | `curl`, `wget` |
| Base64 | `btoa()` / `atob()` or `jsr:@std/encoding` | `base64` |
| Hashing | `crypto.subtle.digest()` | `shasum`, `md5` |
| File operations | `Deno.readFile`, `Deno.writeFile` | `cat`, `cp`, `mv` |

## Runtime API helper

`biqApi(path, init?)` takes `fetch` options. Unwrap the `{ ok, value, error? }` envelope of `/collections` and
`/streams` once ([endpoints](code-actor-runtime.md#runtime-api)):

```typescript
import { biqApi } from "@borgiq/actors";

async function runtimeAction<T = unknown>(path: "/collections" | "/streams", body: Record<string, unknown>): Promise<T> {
  const res = await biqApi(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const json = (await res.json()) as { ok: boolean; value: T; error?: { code: string; message: string } };
  if (!json.ok) {
    const err = new Error(json.error?.message || "Action failed");
    (err as any).code = json.error?.code;
    throw err;
  }
  return json.value;
}

const item = await runtimeAction("/collections", { action: "getItem", collection: "my-col", key: "k1" }); // null if missing
const page = await runtimeAction<{ records: { cursor: string; payload: string }[]; nextCursor: string; hasMore: boolean }>(
  "/streams", { action: "readStream", stream: "order-events", from: cursor ?? "start", maxRecords: 500 },
);
```

Every action, its fields and its errors: [collection-actor.md](collection-actor.md), [stream-api.md](stream-api.md).

## Template

The entrypoint, `main.ts`:

```typescript
import type { Request, Response } from "@borgiq/actors";
import { RetryableError, Signal, biqApi, mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // req.inputs                       — interpolated inputs for this invocation
  // req.ctx                          — RuntimeContext (org / workspace / canvas / flowrun / actor)
  // req.connection                   — the single connection's resolved config (read-only)
  // req.credentials.XXXX             — secret values; placeholders when Server-side (read-only)
  // req.memory.stm / req.memory.ltm  — short / long term memory (value-in)
  // throw new RetryableError() to be re-invoked with the same message; other errors are permanent.

  console.log("Processing started");   // captured with the flowrun

  return {
    // `results` is emitted as msg.<msgVar> downstream (an array is ONE message unless
    // options.emitArrayAsSingleMessage is false).
    results: { result: "data" },
    // To persist memory, return the half you changed; it is shallow-merged into the stored
    // half: memory: { ltm: { ...req.memory?.ltm, key } }. Clear a key with `key: null`.
    // Omit `memory` to leave both halves unchanged. (ltm/stm need enableLTM / enableSTM.)
    // signal: Signal.webhookRespond({ statusCode: 200, body: { ok: true } }),
  };
}
```

## Examples

### Two dependent API calls

Several HTTP requests that depend on each other belong in one code actor, not a chain of HttpRequestActors. This one
looks up a Gmail label by name, then applies it to a message:

```typescript
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const token = req.connection?.auth?.values?.token;
  if (!token) throw new Error("Missing OAuth token");
  const headers = { Authorization: `Bearer ${token}` };

  // Step 1: fetch the label id by name
  const labelsRes = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/labels", { headers });
  const labels = await labelsRes.json();
  const label = labels.labels.find((l: any) => l.name === req.inputs.labelName);
  if (!label) throw new Error(`Label not found: ${req.inputs.labelName}`);

  // Step 2: apply it to the message
  const applyRes = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${req.inputs.messageId}/modify`,
    { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ addLabelIds: [label.id] }) },
  );
  return { results: await applyRes.json() };
}
```

### Incremental poll that dedupes in LTM

Emits Google Calendar events starting within 15 minutes, skipping ones already emitted. Needs `enableLTM: true` and
`allowNet: true`. LTM is capped at 1 KB by default, so it keeps only the 15 most recent IDs.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { RetryableError } from "@borgiq/actors";

const MAX_PROCESSED_EVENTS = 15;

export default async function receive(req: Request): Promise<Response> {
  const token = req.connection.auth.values.token;
  if (!token) throw new Error("No OAuth2 token found in connection");

  const now = Date.now();
  const params = new URLSearchParams({
    timeMin: new Date(now - 15 * 60 * 1000).toISOString(),
    timeMax: new Date(now + 15 * 60 * 1000).toISOString(),
    singleEvents: "true",
    orderBy: "startTime",
  });
  const response = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(req.inputs.calendarId)}/events?${params}`,
    { headers: { Authorization: `Bearer ${token}`, Accept: "application/json" } },
  );
  if (!response.ok) {
    if (response.status === 401) throw new RetryableError("Authentication failed");
    throw new Error(`Failed to fetch events: ${response.statusText}`);
  }
  const data = await response.json();

  const seen = new Map(Object.entries(req.memory?.ltm?.processedEventIds ?? {}));
  const eventsToEmit = [];
  for (const event of data.items ?? []) {
    if (seen.has(event.id)) continue;
    eventsToEmit.push({ id: event.id, summary: event.summary, start: event.start, end: event.end });
    seen.set(event.id, true);
  }
  const processedEventIds = Object.fromEntries([...seen.entries()].slice(-MAX_PROCESSED_EVENTS));

  return { results: eventsToEmit, memory: { ltm: { ...req.memory?.ltm, processedEventIds } } };
}
```

### Checkpoint a large dataset in a stashed file

For a working set too large for memory: stash it, keep the `BIQFile` in the LTM checkpoint, mount it on resume. Needs
`enableLTM`, `allowNet` and `allowFs`; `maxRunTimeMs` is an input set below the runtime's timeout.

```typescript
import type { Request, Response } from "@borgiq/actors";
import { mountFile, stashFile } from "@borgiq/actors";

interface Checkpoint { lastProcessedIndex: number; dataFile: any }   // dataFile: a BIQFile

export default async function receive(req: Request): Promise<Response> {
  const checkpoint = req.memory.ltm.checkpoint as Checkpoint | null | undefined;   // null once cleared
  let workingData: any[] = [];
  let startIndex = 0;

  if (checkpoint?.dataFile) {
    // Resume: mount the stashed file and load the data
    workingData = JSON.parse(await Deno.readTextFile(await mountFile(checkpoint.dataFile)));
    startIndex = checkpoint.lastProcessedIndex;
    console.log(`Resuming from index ${startIndex}, loaded ${workingData.length} items`);
  } else {
    workingData = await fetchLargeDataset();   // first run
  }

  const startTime = Date.now();
  const BUFFER_TIME_MS = 30000;
  const maxRunTimeMs = req.inputs.maxRunTimeMs;

  for (let i = startIndex; i < workingData.length; i++) {
    if (Date.now() - startTime > maxRunTimeMs - BUFFER_TIME_MS) {
      // Running low on time: stash the data, checkpoint, and exit
      const tempDir = await Deno.makeTempDir({ prefix: "checkpoint_" });
      await Deno.writeTextFile(`${tempDir}/data.json`, JSON.stringify(workingData));
      const dataFile = await stashFile(await Deno.readFile(`${tempDir}/data.json`), "checkpoint-data.json", "application/json");
      await Deno.remove(tempDir, { recursive: true });
      return {
        results: { status: "in_progress", processedSoFar: i },
        memory: { ltm: { ...req.memory.ltm, checkpoint: { lastProcessedIndex: i, dataFile } } },
      };
    }
    await processItem(workingData[i]);
  }

  // Complete: clear the checkpoint with null; omitting it would keep it (the returned ltm is merged).
  return { results: { status: "complete", totalProcessed: workingData.length }, memory: { ltm: { ...req.memory.ltm, checkpoint: null } } };
}
```

## Best practices

- **Prefer native `fetch()` to SDK libraries**: no dependency to pin, full control of the request, easy to debug, always
  available. Use an `npm:`/`jsr:` SDK only when the user asks for one (e.g. "use the OpenAI SDK") or the API's
  authentication is impractical to implement by hand.
- **Create clients once at module level** (a database or SDK client), and reuse them across invocations while the
  container stays warm.
- **Use the Deno file APIs** (`Deno.makeTempDir()`), never hardcoded paths.
- The shared rules (validation, retries, memory, checkpoints, pinning) are in
  [code-actor-runtime.md](code-actor-runtime.md#rules).
