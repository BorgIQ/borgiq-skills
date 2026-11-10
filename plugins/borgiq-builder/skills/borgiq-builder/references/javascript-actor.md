# JavaScript Actor Reference

The JavaScriptActor (**beta**) runs the same TypeScript/JavaScript as a [DenoActor](deno-actor.md): the same
`main.ts` default-exporting `receive(req)`, the same `@borgiq/actors` SDK, inputs, results, memory, signals and
errors. Only the engine differs: it runs on workerd, the open-source JavaScript runtime, instead of Deno. This file
covers what differs from the DenoActor; the contract, emit rules, errors, source files, credentials, memory and
signals are in [code-actor-runtime.md](code-actor-runtime.md).

## Contents

- [When to use it](#when-to-use-it)
- [Configuration](#configuration)
- [Options](#options)
- [Imports](#imports)
- [What the code can use](#what-the-code-can-use)
- [Two rules the DenoActor does not have](#two-rules-the-denoactor-does-not-have)
- [Files](#files)
- [Network](#network)
- [Errors and limits](#errors-and-limits)
- [Moving a DenoActor](#moving-a-denoactor)
- [Example](#example)

## When to use it

Where a DenoActor would fit, when the code needs no `Deno.*` API, no shell, no raw TCP and no `eval`. It has no host
filesystem at all, a memory cap that stops only the actor (not the whole runtime), and its outbound network goes
through BorgIQ's egress proxy exactly as a DenoActor's does. It is not built ahead of time on deployed workspaces yet:
its packages resolve the first time it runs on a machine, as on an ordinary workspace.

## Configuration

```yaml
actors:
  ACTR01xxxxx:
    type: JavaScriptActor
    version: 1
    name: Normalize Orders
    msgVar: normalize_orders
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      inputs:
        orders: ${{ msg.fetch_orders }}
      options:
        allowNet: true
        allowNetList:
          - api.example.com
        env:
          - name: API_KEY
            value: ${{ credentials.apiKey }}
      codeDir:
        - path: main.ts
          content: |
            import type { Request, Response } from "@borgiq/actors";
            import { normalize } from "./lib/normalize.ts";

            export default async function receive(req: Request): Promise<Response> {
              return { results: normalize(req.inputs.orders) };
            }
        - path: lib/normalize.ts
          content: |
            export const normalize = (orders: unknown) => orders;
```

`codeDir` follows the DenoActor's rules: exactly one `main.ts`, relative imports with extensions. Reserved paths
differ: `package.json`, `tsconfig.json`, `jsconfig.json` and anything under `node_modules/` are refused; the Deno
bootstrap's names (`server.ts`, `handler.ts`, `shared/`) are free.

## Options

The DenoActor's options without `allowFs`: `emitArrayAsSingleMessage`, `allowNet`, `allowNetList`, `denyNetList` and
`env`, with the same meaning ([deno-actor.md](deno-actor.md#options)). `env` becomes `process.env`, set afresh for every
invocation: exactly the names listed, nothing a previous run set. Exact schema: the DenoActor's
([typescript/actorSchemas/task/deno.md](typescript/actorSchemas/task/deno.md)) minus `allowFs`.

## Imports

| Import | Rule |
|---|---|
| `./lib/x.ts`, `../shared/y.ts` | Your own files, with the extension. Nothing outside the actor's files: `..` past the root, absolute paths and symlinks out are refused |
| `@borgiq/actors` | The SDK, no version |
| `node:fs`, `node:crypto`, … | Node built-ins, always with `node:` (bare `fs` is refused) |
| `npm:name@1.2.3[/sub]` | Exact version only. Refused: no version, ranges (`^`, `~`), `latest` |
| `jsr:@scope/name@1.2.3[/sub]` | Exact version only, installed from JSR's npm mirror |
| `https://…` | **Refused.** Use the package from npm or JSR |
| `lodash` (bare) | **Refused.** Use `npm:lodash@4.17.21` |

Packages install without their install scripts, and a version published less than 7 days ago is refused, as for the
DenoActor. Code is bundled before it runs: a syntax error or a refused import fails the run with `main.ts:LINE:COL`
and the reason, before anything executes. Types are stripped, not checked.

## What the code can use

| Available | Not available |
|---|---|
| `fetch`, `Request`, `Response`, `URL`, streams, `TextEncoder` | `Deno` (any `Deno.*` call is a `ReferenceError`) |
| `crypto.subtle`, `crypto.randomUUID()`, `node:crypto` (hashes, HMAC, ciphers) | `node:child_process`, raw TCP (`node:net` connections), `node:worker_threads` |
| `node:buffer`, `node:events`, `node:stream`, `node:util`, `node:path`, `node:zlib`, `node:url` | Outbound WebSockets |
| `node:fs` on `/tmp` (see [Files](#files)) | `eval`, `new Function`, compiling WebAssembly from bytes (libraries that compile templates at run time fail) |
| `process.env` (from `options.env`), timers within the invocation | `process.exit`, `process.kill` (throw, as in a DenoActor) |

The time zone is UTC. `import.meta.url` is not a file path.

## Two rules the DenoActor does not have

1. **Await everything before returning.** Timers and promises still pending when `receive` returns are cancelled, so
   fire-and-forget work never happens.
2. **Do not keep open I/O across invocations.** Module-level state persists between runs (create clients and caches
   once, as usual), but a response stream or connection started in one invocation and used in the next hangs until
   the timeout. Keep configuration objects at module level; open requests inside `receive`.

## Files

`/tmp` is the only writable path. It is in memory, counts against the actor's memory cap, and **lasts one
invocation**: write and read within the same run; persist across runs with memory, a Collection or `stashFile`. There
is no `TMPDIR` and no other host file.

```typescript
import { readFileSync, writeFileSync } from "node:fs";
import { mountFile, stashFile } from "@borgiq/actors";

const path = await mountFile(req.inputs.inputFile);          // /tmp/borgiq_actor_<n>/<fileName>
writeFileSync("/tmp/out.csv", readFileSync(path, "utf8").toUpperCase());
const outputFile = await stashFile("/tmp/out.csv");           // a path string is read from /tmp
```

`mountFile` and `stashFile` need `allowNet: true`, as in a DenoActor.

## Network

- Without `allowNet`, every `fetch` throws: `outbound requests are not allowed from this actor`.
- With it, requests go through BorgIQ's egress proxy, so **Server-side** credential placeholders resolve as for a
  DenoActor ([credentials](code-actor-runtime.md#credentials-and-connections)). The BorgIQ API host is always allowed.
- A host outside `allowNetList`, or in `denyNetList`, is **not** an exception: `fetch` resolves with status `403` and
  the header `x-borgiq-egress-error: host-not-allowed` (or `host-denied`). Check `res.ok`. Link-local addresses
  (`169.254.*`) are always refused, and on the hosted runtime so is `localhost`.
- A target that cannot be reached resolves with `502` and `x-borgiq-egress-error: upstream-error`.

## Errors and limits

- Errors map exactly as for the DenoActor: `RetryableError` is retried, any other throw is not, and a returned
  `{ error: { message, retryable } }` is honoured ([errors](code-actor-runtime.md#errors-and-retries)). Stack frames
  name your files (`lib/x.ts:3:9`); frames in packages read `<dependency>`.
- **Timeout:** the same *Deno actor timeout* setting (workspace settings → Runtimes) applies; a run that exceeds it
  fails with `Request timed out` and the actor restarts.
- **Memory:** the actor's JavaScript heap is capped at 40% of the runtime's memory (at least 64 MB). Exceeding it fails
  the run with `The JavaScript actor ran out of memory (heap limit N MB)`, not retried; only this actor restarts.
- `console.log`/`info`/`debug` reach the run log as stdout, `console.warn`/`error` as stderr; one call is one entry,
  newlines included.

## Moving a DenoActor

Change `type: DenoActor` to `type: JavaScriptActor` and check:

- `Deno.*` calls → `node:fs` on `/tmp`, `process.env`, `fetch`;
- `https:` and `deno.land` imports → `npm:`/`jsr:` at an exact version;
- files that must survive the run → memory, a Collection or `stashFile`;
- unawaited promises, and clients that hold an open stream across runs;
- `allowFs` is ignored and may stay.

## Example

```typescript
import type { Request, Response } from "@borgiq/actors";
import { RetryableError } from "@borgiq/actors";
import { createHash } from "node:crypto";
import escapeHtml from "npm:escape-html@1.0.3";

export default async function receive(req: Request): Promise<Response> {
  const res = await fetch(`https://api.example.com/items/${encodeURIComponent(String(req.inputs.id))}`, {
    headers: { authorization: `Bearer ${process.env.API_KEY}` },
  });
  if (res.status === 429 || res.status >= 500) throw new RetryableError(`upstream ${res.status}`);
  if (!res.ok) return { error: { message: `lookup failed: ${res.status} ${res.headers.get("x-borgiq-egress-error") ?? ""}`.trim() } };
  const item = await res.json() as { title: string; body: string };
  return {
    results: {
      title: escapeHtml(item.title),
      checksum: createHash("sha256").update(item.body).digest("hex"),
    },
  };
}
```
