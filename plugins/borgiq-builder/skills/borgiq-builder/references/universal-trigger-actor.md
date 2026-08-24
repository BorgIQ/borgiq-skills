# UniversalTriggerActor Reference

The UniversalTriggerActor is a programmable trigger: user-supplied TypeScript runs on every fire — webhook request, cron schedule, canvas or actor lifecycle event, or manual canvas Invoke — and branches on the delivered trigger event.

> **API model:** the code runs on the same Deno runtime and value-in/value-out contract as the [DenoActor](deno-actor.md). The only difference is the entry point — `receive(req: TriggerRequest): Promise<Response>`, where `TriggerRequest` extends `Request` with `req.trigger` (the firing event, discriminated by `type`). Everything else — `req.inputs` / `req.ctx` / `req.connection` / `req.credentials` / `req.memory`, `biqApi`, `mountFile`, `stashFile`, `RetryableError`, `Signal`, the single `@borgiq/actors` import, network/fs permissions, dependency pinning — is identical to DenoActor.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Code Files](#code-files)
- [Code Template](#code-template)
- [Emitted Message](#emitted-message)
- [Responding to Webhook Firings](#responding-to-webhook-firings)
- [Memory](#memory)
- [Common Mistakes](#common-mistakes)
- [Quick Example](#quick-example)

## Overview

A single UniversalTriggerActor can fire four ways:

| Firing mode | Enabled by | `req.trigger` |
|---|---|---|
| **Webhook** | `configuration.webhook.enabled: true` | `{ type: 'webhook', user?, request }` — `request` is the parsed inbound HTTP request (`meta`, `method`, `headers`, `body`, `queryParams`, `rawBody?`); `user` is the authenticated caller (`{ id, name?, email }`) when the call carried an app token, e.g. a React app calling one of its declared endpoints |
| **Schedule** | `configuration.schedule.enabled: true` | `{ type: 'schedule', triggeredAt, lastTriggeredAt? }` |
| **Lifecycle** | `configuration.lifecycle.events` lists the event | `{ type: 'lifecycle', event }` — `event` is the lifecycle transition: `'canvas-enabled'` or `'canvas-disabled'` |
| **Manual** | Always available (canvas Invoke) | `{ type: 'manual' }` |

When `webhook.enabled` is false the webhook URL returns 404 and no flowruns are created; when `schedule.enabled` is false no cron job is registered; an actor receives a lifecycle event only when that event is listed in `lifecycle.events` — an absent section, an absent `events`, and an empty `events` all mean unsubscribed.

**Use a UniversalTriggerActor instead of a standalone WebhookTriggerActor / ScheduledTriggerActor when:**

- One workflow must fire via webhook **and** schedule (and manual testing) through a single code path
- Code must run at trigger time — normalize, filter, dedupe, enrich, or respond before emitting downstream
- You want full control over what the trigger emits (a plain WebhookTriggerActor always emits the request shape)

If the trigger just needs to pass the payload through with static response config, the standalone [WebhookTriggerActor](webhook-trigger-actor.md) or [ScheduledTriggerActor](scheduled-trigger-actor.md) is simpler.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: UniversalTriggerActor
    version: 1
    name: Universal Trigger
    msgVar: universal_trigger
    description: Programmable trigger for webhook, schedule, lifecycle, and manual fires
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      # STATIC webhook source config — admission-consumed, never interpolated
      webhook:
        enabled: true
        triggerKey: 01KDXXXXXXXXXXXXXXXXXX
        authorizationLevel: public
        allowedMethods:
          - get
          - post
        responseTimeout: 30
      # STATIC schedule source config — admission-consumed, never interpolated
      schedule:
        enabled: false
        cron: '0 * * * *'
        timezone: America/New_York
      # STATIC lifecycle source config — admission-consumed, never interpolated
      lifecycle:
        events:
          - canvas-enabled
          - canvas-disabled
      options:
        # --- Deno runtime options (root) — identical to DenoActor ---
        allowNet: true
        allowFs: false
        emitArrayAsSingleMessage: true
        env: []
        # --- INTERPOLATABLE webhook response behavior (resolved at runtime) ---
        webhook:
          respondImmediately: true
          emitRawBody: false
          response:
            statusCode: 200
            headers:
              content-type: text/plain; charset=utf-8
            body: OK
      # Source is a list of files, sibling of `options`, never interpolated.
      # Exactly one entry must have path `main.ts` — it is the entrypoint.
      codeDir:
        - path: main.ts
          content: |
            import type { TriggerRequest, Response } from "@borgiq/actors";

            export default async function receive(req: TriggerRequest): Promise<Response> {
              return { results: { firedBy: req.trigger.type }, memory: req.memory };
            }
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

Generate the webhook `triggerKey` with the CLI (required whenever `webhook.enabled: true`):

```bash
borgiq generate id webhooktriggerkey
```

## Options Reference

### Static source config (never interpolated — literals only, DB-queryable)

**`configuration.webhook`** (see [webhook-trigger-actor.md](webhook-trigger-actor.md#options-reference) for field semantics):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | - | When false the webhook URL returns 404 and no flowruns are created |
| `triggerKey` | string | - | Unique key forming the webhook URL — required when `enabled: true` |
| `authorizationLevel` | `public` \| `apps` | `public` | Who may call the webhook |
| `allowedMethods` | string[] | `["post"]` | HTTP methods accepted (get, post, put, delete) |
| `responseTimeout` | number | `30` | Timeout in seconds when `respondImmediately` is false (1-60) |

**`configuration.schedule`** (see [scheduled-trigger-actor.md](scheduled-trigger-actor.md)):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | - | When false no cron job is registered |
| `cron` | string | - | Cron expression (literal only, never interpolated) |
| `timezone` | string | `America/New_York` | Timezone used to evaluate the cron expression |

**`configuration.lifecycle`** — subscribes the trigger to individual lifecycle events. Absent ⇒ unsubscribed:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `events` | string[] | `[]` | The lifecycle events this actor is subscribed to — any of `'canvas-enabled'`, `'canvas-disabled'`. The actor receives `{ type: 'lifecycle', event }` only for events in this list; an empty or absent list means it receives none. |

Subscription is per event rather than a single on/off flag because the event vocabulary grows over time — a flag would silently opt an existing trigger into events its code was never written to handle.

### Interpolatable options (`configuration.options`)

Deno runtime fields live at the root — identical to DenoActor (see [deno-actor.md → Options Reference](deno-actor.md#options-reference)): `emitArrayAsSingleMessage`, `allowNet`, `allowNetList`, `denyNetList`, `allowFs`, `env`.

Webhook response behavior is nested under `webhook:` — shared with the standalone WebhookTriggerActor (see [webhook-trigger-actor.md](webhook-trigger-actor.md#options-reference)): `respondImmediately`, `emitRawBody`, `response.statusCode` / `response.headers` / `response.body`. These may use `${{ }}` expressions; `trigger` is in scope (see [context.md → trigger](context.md#trigger)).

## TypeScript Schema Definition

```typescript
/** The options for the UniversalTriggerActor (the interpolated `options` blob). */
export const UniversalTriggerActorOptionsSchema = z.object({
  // --- deno runtime options (root) — identical to DenoActorOptionsSchema ---
  emitArrayAsSingleMessage: z.boolean().nullish().default(true),
  allowNet: z.boolean().nullish().default(false),
  allowNetList: z.array(z.string()).nullish().default([]),
  denyNetList: z.array(z.string()).nullish().default([]),
  allowFs: z.boolean().nullish().default(false),
  env: z.array(z.object({ name: z.string(), value: z.string().nullish() })).nullish().default([]),
  // --- interpolatable webhook behavior (shared with WebhookTriggerActor) ---
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

/**
 * The UniversalTriggerActor's `configuration.codeDir`: at most 200 files and 1 MiB of content in
 * total, exactly one of them at `main.ts`, none using a filename the runtime reserves.
 */
export const UniversalTriggerActorCodeDirSchema = makeCodeDirSchema({
  requiredEntrypoint: 'main.ts',
  reservedPaths: DENO_RESERVED_PATHS,
});
```

Full definitions: [typescript/actor-schemas-triggers.md → universalTrigger](typescript/actor-schemas-triggers.md#actorschemastriggeruniversaltrigger) (options), [typescript/actor-schemas-triggers.md → triggerConfig](typescript/actor-schemas-triggers.md#actorschemastriggertriggerconfig) (static webhook/schedule/lifecycle config), and [typescript/schemas.md → schemas/trigger](typescript/schemas.md#schemastrigger) (the `TriggerEvent` union).

## Code Files

The trigger's source is a project tree in `configuration.codeDir` — a list of `{path, content}` files with the required entrypoint `main.ts` at its root, plus any helper files you add. The rules are the DenoActor's, which this trigger shares: relative imports between your own files (extension included), no imports leaving the tree, no interpolation of `codeDir`, and the reserved filenames `server.ts`, `handler.ts`, `actor.ts`, `main_test.ts`, `deno.json`, `deno.jsonc`, `deno.lock`, `package.json`, `shared/…`, `node_modules/…`. See [deno-actor.md → Code Files](deno-actor.md#code-files) for the full contract, limits, and editing surfaces.

Splitting per trigger source is the common shape:

```yaml
configuration:
  codeDir:
    - path: main.ts
      content: |
        import type { TriggerRequest, Response } from "@borgiq/actors";

        import { onWebhook } from "./handlers/webhook.ts";
        import { onSchedule } from "./handlers/schedule.ts";

        export default async function receive(req: TriggerRequest): Promise<Response> {
          if (req.trigger.type === "webhook") return onWebhook(req);
          if (req.trigger.type === "schedule") return onSchedule(req);
          return { results: undefined };
        }
    - path: handlers/webhook.ts
      content: |
        …
    - path: handlers/schedule.ts
      content: |
        …
```

Note the reserved `main_test.ts`: the runtime owns that name for this trigger's variant, so name your own test helpers something else.

## Code Template

The entrypoint file, `main.ts`:

```typescript
import type { TriggerRequest, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";
// import { RetryableError, biqApi, mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: TriggerRequest): Promise<Response> {
  // req.trigger is the delivered event, discriminated by `type`:
  // - webhook:  req.trigger.request carries the HTTP request (meta, method, headers, body, queryParams);
  //             req.trigger.user is the authenticated caller when the call carried an app token
  // - schedule: req.trigger.triggeredAt is this fire; req.trigger.lastTriggeredAt is the previous fire (if tracked)
  // - lifecycle: req.trigger.event is the lifecycle transition ('canvas-enabled' | 'canvas-disabled')
  // - manual:   no extra fields
  switch (req.trigger.type) {
    case "webhook":
      return {
        results: { source: "webhook", request: req.trigger.request },
        memory: req.memory,
        // Respond to the webhook request:
        // signal: Signal.webhookRespond({ statusCode: 200, body: { ok: true } }),
      };
    case "schedule": {
      // Enable LTM in advanced settings if you want to remember the previous fire.
      const prev = (req.memory.ltm.lastTriggeredAt as string) ?? null;
      return {
        results: { source: "schedule", triggeredAt: req.trigger.triggeredAt, lastTriggeredAt: prev },
        memory: { stm: req.memory.stm, ltm: { ...req.memory.ltm, lastTriggeredAt: req.trigger.triggeredAt } },
      };
    }
    case "lifecycle":
      // req.trigger.event is 'canvas-enabled' | 'canvas-disabled'
      return { results: { source: "lifecycle", event: req.trigger.event }, memory: req.memory };
    case "manual":
      return { results: { source: "manual" }, memory: req.memory };
    default:
      return { results: { source: req.trigger.type }, memory: req.memory };
  }
}
```

## Emitted Message

The result schema is `z.any()` — downstream actors see whatever the code returns as `results`, under `msg.<msgVar>`. The DenoActor emit semantics apply (see [deno-actor.md → Return Values](deno-actor.md#return-values)):

- An array emits one message per item unless `emitArrayAsSingleMessage: true` (the default)
- `results: undefined` (or omitted) emits **nothing** — useful for respond-only webhook handling or filtering out uninteresting fires

## Responding to Webhook Firings

Two ways to answer the HTTP caller, mirroring the standalone WebhookTriggerActor's response modes:

**1. Immediate interpolated response** — `options.webhook.respondImmediately: true` with a `response` template. The response is built before the code runs; `trigger.request` is in scope:

```yaml
options:
  webhook:
    respondImmediately: true
    response:
      statusCode: 200
      body: ${{ trigger.request?.body?.challenge || 'OK' }}
```

**2. Respond from the trigger's own code** — `options.webhook.respondImmediately: false`, then return a `Signal.webhookRespond` from `receive`:

```typescript
return {
  results: payload,
  signal: Signal.webhookRespond({
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ok: true }),
  }),
};
```

Guard signal use by firing type — `Signal.webhookRespond` only makes sense when `req.trigger.type === 'webhook'`.

## Memory

Memory is **fully opt-in** — no infrastructure code reads or writes LTM/STM on the user's behalf. Notably, `lastTriggeredAt` is **not** tracked automatically: persist it yourself via `req.memory.ltm` → `Response.memory` (as in the [Code Template](#code-template)) after enabling LTM in advanced settings. The value-in/value-out rules are the DenoActor's (see [deno-actor.md → Memory Types](deno-actor.md#memory-types)): the returned `memory` **replaces** the stored value, so spread the previous object to avoid dropping keys.

## Common Mistakes

1. **Static fields under `options`** — `triggerKey`, `authorizationLevel`, `allowedMethods`, `responseTimeout`, `cron`, `timezone`, `enabled`, `events` live in `configuration.webhook` / `configuration.schedule` / `configuration.lifecycle` (literals only), not in `configuration.options`.
2. **Reading `trigger.request` without a type guard** — on schedule/lifecycle/manual fires `req.trigger.request` does not exist. Branch on `req.trigger.type` (in code) or `${{ trigger.type === 'webhook' }}` / `${{ trigger?.request?.… }}` (in templates).
3. **Expecting `lastTriggeredAt` automatically** — it's only present if your code persisted it to LTM on a previous fire.
4. **Typing the entry point as `Request`** — use `TriggerRequest`, otherwise `req.trigger` is not typed.
5. **Missing `triggerKey` with `webhook.enabled: true`** — the webhook URL will not work without it.
6. **Returning partial `memory`** — `Response.memory` replaces the stored value; spread `req.memory.stm` / `req.memory.ltm` to keep existing keys.

## Quick Example

A trigger that accepts GitHub webhooks and also runs hourly to catch missed events:

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd298e3vrbdazn9x5etv4r7a:
    type: UniversalTriggerActor
    version: 1
    name: GitHub Events
    msgVar: github_events
    description: Receive GitHub push webhooks and poll hourly as a fallback
    isActive: true
    continueOnError: false
    enableLTM: true
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      webhook:
        enabled: true
        triggerKey: 01KD298E3VRBDAZN9X5ETV4R7B
        authorizationLevel: public
        allowedMethods:
          - post
      schedule:
        enabled: true
        cron: '0 * * * *'
        timezone: America/New_York
      options:
        allowNet: true
        webhook:
          respondImmediately: true
          response:
            statusCode: 200
            body: OK
      codeDir:
        - path: main.ts
          content: |
            import type { TriggerRequest, Response } from "@borgiq/actors";

            export default async function receive(req: TriggerRequest): Promise<Response> {
              if (req.trigger.type === "webhook") {
                return { results: { event: req.trigger.request.headers["x-github-event"], payload: req.trigger.request.body }, memory: req.memory };
              }
              if (req.trigger.type === "schedule") {
                const since = (req.memory.ltm.lastPolledAt as string) ?? null;
                return {
                  results: { event: "poll", since },
                  memory: { stm: req.memory.stm, ltm: { ...req.memory.ltm, lastPolledAt: req.trigger.triggeredAt } },
                };
              }
              return { results: undefined };  // manual fire: emit nothing
            }
    schemas: {}
    id: ACTR01kd298e3vrbdazn9x5etv4r7a
    position:
      x: 0
      'y': 0
    edges: {}
```
