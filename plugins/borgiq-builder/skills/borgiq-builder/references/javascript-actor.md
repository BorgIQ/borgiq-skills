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
through BorgIQ's egress proxy exactly as a DenoActor's does.

**When it is built.** On a deployed workspace it is built with the canvas, like the other code actors: its packages
are installed and its code bundled once, a bundle that throws while loading fails the build, and every run starts
from that bundle with nothing installed. Editing its code (`codeDir`) marks the canvas outdated until it is built
again; an options change does not, and applies from the next run. On an ordinary workspace it is bundled the first
time it runs on a machine, and again when its code or options change; `env` values do not count, so a value taken
from the message never rebuilds it.

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
invocation: exactly the names listed, nothing a previous run set. Each `allowNetList`/`denyNetList` entry is a host
name, an IP address or a URL (only its host counts). A wildcard such as `*.example.com` never matches: saving the actor
in the editor shows it as an options warning, and a run with one fails. Exact schema: [typescript/actorSchemas/task/javascript.md](typescript/actorSchemas/task/javascript.md).

## Imports

| Import | Rule |
|---|---|
| `./lib/x.ts`; `../y.ts` from a subfolder | Your own files, with the extension. Nothing outside the actor's files: `..` past the root, absolute paths and symlinks out are refused |
| `@borgiq/actors` | The SDK, no version |
| `node:fs`, `node:crypto`, … | Node built-ins, always with `node:` (bare `fs` is refused). The public built-ins workerd provides import (not Node's private `_`-prefixed modules, nor `node:sea` or `node:test/reporters`); several are stubs that throw when used (`node:child_process`, `node:worker_threads`, `node:cluster`) |
| `npm:name@1.2.3[/sub]` | Exact version only. Refused: no version, ranges (`^`, `~`), `latest` |
| `jsr:@scope/name@1.2.3[/sub]` | Exact version only, installed from JSR's npm mirror |
| `https://…` | **Refused.** Use the package from npm or JSR |
| `lodash` (bare) | **Refused.** Use `npm:lodash@4.17.21`; a subpath keeps the version on the name: `npm:lodash@4.17.21/chunk` |
| ``import(`./locale/${name}.ts`)`` | A path built from a variable is resolved when the code is bundled, against your own files: every match is bundled. One that reaches outside your files fails the build |

Packages install without their install scripts, and a version published less than 7 days ago is refused, as for the
DenoActor. Everything installed comes from the npm and JSR registries: a package whose own dependency is a tarball URL,
a git repository or a local path fails the install, naming it. An install that cannot reach the registry is retried. Code is bundled before it runs, packages included: a syntax error or a refused import fails the run (or
the canvas build) with `main.ts:LINE:COL` and the reason, before anything executes. Types are stripped, not checked,
and no `tsconfig.json` is read. Inside packages, `require("events")` and other bare built-ins work; a package that
requires a real npm package such as `ws` or `undici` gets that package.

## What the code can use

| Available | Not available |
|---|---|
| `fetch`, `Request`, `Response`, `URL`, streams, `TextEncoder` | `Deno` (any `Deno.*` call is a `ReferenceError`) |
| `crypto.subtle`, `crypto.randomUUID()`, `node:crypto` (hashes, HMAC, ciphers) | `node:child_process`, raw TCP (`node:net` connections), `node:worker_threads` |
| `node:buffer`, `node:events`, `node:stream`, `node:util`, `node:path`, `node:zlib`, `node:url` | Outbound WebSockets |
| `node:fs` on `/tmp` (see [Files](#files)) | `eval`, `new Function`, compiling WebAssembly from bytes, both in `receive` and while the module loads (libraries that compile templates at run time fail) |
| `process.env` (from `options.env`), timers within the invocation | `process.exit`, `process.kill` (throw, as in a DenoActor) |

The time zone is UTC. `import.meta.url` is `undefined`: `new URL("./x.json", import.meta.url)` throws; import the file
instead (`import data from "./x.json"`). The clock only moves inside `receive`: `new Date()` or `Date.now()` at module
level is the Unix epoch, so read the time in `receive`.

## Two rules the DenoActor does not have

1. **Await everything before returning.** Timers and promises still pending when `receive` returns are cancelled, so
   fire-and-forget work never happens. Work a library keeps alive past `receive` (`waitUntil`) cannot reach the
   network, not even while a later run of the actor is in progress: its requests are answered `403` with
   `x-borgiq-egress-error: outside-invocation`, and its console output reaches no run log.
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

`mountFile` and `stashFile` need `allowNet: true`, as in a DenoActor, and an empty `allowNetList`: the storage host
they download from and upload to is not on a list, so with one they fail naming the host and the reason. A failed
upload is an error from `stashFile`, never a file that was not stored.

## Network

- Without `allowNet`, every `fetch` throws: `outbound requests are not allowed from this actor`.
- With it, requests go through BorgIQ's egress proxy, so **Server-side** credential placeholders resolve as for a
  DenoActor ([credentials](code-actor-runtime.md#credentials-and-connections)). The BorgIQ API host is always allowed.
- A host outside `allowNetList`, or in `denyNetList`, is **not** an exception: `fetch` resolves with status `403` and
  the header `x-borgiq-egress-error: host-not-allowed` (or `host-denied`). Check `res.ok`. An IP address matches a list
  entry however it is written (`[::ffff:10.0.0.5]` is `10.0.0.5`). Link-local and instance-metadata addresses
  (`169.254.*`) are always refused (`link-local`), and on the hosted runtime so are `localhost` and `127.*`
  (`loopback`). Each refusal is also written to the run log with its reason.
- In local development without the egress proxy, a host name that resolves to a link-local address is refused with
  `resolved-address-denied`; on the hosted runtime the egress proxy resolves names.
- A target that cannot be reached resolves with `502` and `x-borgiq-egress-error: upstream-error`. One that does not
  answer resolves with `504` and `upstream-timeout` a little before the actor's own timeout (2 s before it, and at most
  80% of it), so the code can handle it rather than the run timing out.
- A `503` with `proxy-ca-unavailable` is the runtime's fault, not the code's: throw `RetryableError` on it.

## Errors and limits

- Errors map exactly as for the DenoActor: `RetryableError` is retried, any other throw is not, and a returned
  `{ error: { message, retryable } }` is honoured ([errors](code-actor-runtime.md#errors-and-retries)). Stack frames
  name your files (`lib/x.ts:3:9`); frames in packages read `<dependency>`. A thrown value that is not an `Error`
  (`throw "x"`) is its own message, with no stack.
- **Timeout:** the same *Deno and JavaScript actor timeout* setting (workspace settings → Runtimes) applies; a run
  that exceeds it fails with `Request timed out` and the actor restarts.
- **Memory:** the actor's JavaScript heap is capped at 40% of the runtime's memory (at least 64 MB). Exceeding it fails
  the run with `The JavaScript actor ran out of memory (heap limit N MB)`, not retried; only this actor restarts. The
  whole process, buffers (`Uint8Array`, `Buffer`) and `/tmp` files included, is capped at 60% of the runtime's memory
  (at least the heap cap plus 128 MB): `The JavaScript actor ran out of memory (it used more than N MB, …)`, not
  retried.
- **Load errors:** code that throws while `main.ts` or a module it imports loads fails with `The JavaScript actor's code
  threw while loading …` and the error, not retried; on a deployed workspace it fails the canvas build instead.
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
  if (!res.ok) return { error: { message: `lookup failed: ${res.status} ${res.headers.get("x-borgiq-egress-error") ?? ""}`.trim(), retryable: false } };
  const item = await res.json() as { title: string; body: string };
  return {
    results: {
      title: escapeHtml(item.title),
      checksum: createHash("sha256").update(item.body).digest("hex"),
    },
  };
}
```
