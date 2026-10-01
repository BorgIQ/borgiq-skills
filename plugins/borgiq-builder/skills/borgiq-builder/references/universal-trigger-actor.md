# UniversalTriggerActor Reference

A programmable trigger: your TypeScript runs on every fire (webhook request, cron schedule, lifecycle event or manual
Invoke) and branches on the delivered event. It runs on the DenoActor's runtime and contract: read
[code-actor-runtime.md](code-actor-runtime.md) for the contract, `codeDir`, memory and signals, and
[deno-actor.md](deno-actor.md) for options and imports. This file covers the trigger sources, the entry point and the
lifecycle events.

## Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [Code Files](#code-files)
- [Code Template](#code-template)
- [Emitted Message](#emitted-message)
- [Responding to Webhook Firings](#responding-to-webhook-firings)
- [Cleaning Up on Delete](#cleaning-up-on-delete)
- [Memory](#memory)
- [Common Mistakes](#common-mistakes)

## Overview

The entry point is `receive(req: TriggerRequest): Promise<Response>`: `TriggerRequest` is the DenoActor's `Request`
plus `req.trigger`, the firing event, discriminated by `type`. One actor can fire four ways:

| Firing mode | Enabled by | `req.trigger` |
|---|---|---|
| **Webhook** | `configuration.webhook.enabled: true` | `{ type: 'webhook', user?, request }`. `request` is the parsed inbound HTTP request (`meta`, `method`, `headers`, `body`, `queryParams`, `rawBody?`). `user` (`{ id, name?, email }`, also on `request.meta.user`) is the authenticated caller when the call carried an app token (a React app calling one of its declared endpoints) or an API key (the key's owner; `request.meta.auth = { type: 'apiToken', keyId, keyName }` names the key) |
| **Schedule** | `configuration.schedule.enabled: true` | `{ type: 'schedule', triggeredAt }`. The type also declares `lastTriggeredAt?`, but a universal trigger never receives it: keep the previous fire in LTM yourself ([Memory](#memory)) |
| **Lifecycle** | `configuration.lifecycle.events` lists the event | `{ type: 'lifecycle', event }`: `'on-delete'` (fired only by hand today; also carries `scope`, `subject` and, on a test fire, `manual: true`; see [Cleaning Up on Delete](#cleaning-up-on-delete)), or `'canvas-enabled'` / `'canvas-disabled'` (reserved, not delivered yet) |
| **Manual** | Always available (canvas Invoke) | `{ type: 'manual' }` |

With `webhook.enabled: false` the webhook URL returns 404 and no flowruns are created; with `schedule.enabled: false`
no cron job is registered. The actor receives a lifecycle event only when that event is listed in `lifecycle.events`:
an absent section, an absent `events` and an empty `events` all mean unsubscribed.

Choose it over a standalone trigger when one workflow must fire via webhook **and** schedule (and manual testing)
through one code path, when code must run at trigger time (normalize, filter, dedupe, enrich, or respond before
emitting), or when you need full control of what is emitted (a WebhookTriggerActor always emits the request shape). A
payload passed through with a static response is simpler with the standalone
[WebhookTriggerActor](webhook-trigger-actor.md) or [ScheduledTriggerActor](scheduled-trigger-actor.md).

## Configuration Structure

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
    enableLTM: true            # the schedule branch keeps a cursor in LTM
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      # STATIC source config — admission-consumed, never interpolated
      webhook:
        enabled: true
        triggerKey: 01KD298E3VRBDAZN9X5ETV4R7B
        authorizationLevel: public
        allowedMethods:
          - post
        responseTimeout: 30
      schedule:
        enabled: true
        cron: '0 * * * *'
        timezone: America/New_York
      lifecycle:
        events: []             # e.g. [on-delete]; canvas-enabled / canvas-disabled are reserved, not delivered yet
      options:
        # Deno runtime options (root) — identical to DenoActor
        allowNet: true
        allowFs: false
        emitArrayAsSingleMessage: true
        env: []
        # INTERPOLATABLE webhook response behavior (resolved at runtime)
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
              if (req.trigger.type === "webhook") {
                return { results: { event: req.trigger.request.headers["x-github-event"], payload: req.trigger.request.body } };
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

Generate the webhook `triggerKey` with the CLI (required whenever `webhook.enabled: true`):

```bash
borgiq generate id webhooktriggerkey
```

## Options Reference

The source configs are static: literals only, never interpolated, and queryable by the platform.

| Config | Fields (default) | Semantics |
|---|---|---|
| `configuration.webhook` | `enabled`; `triggerKey`, required when enabled; `authorizationLevel` (`public`), also `apps`, `apiKey` (a personal access token in `Authorization: Bearer` / `X-Api-Key`) or `appsAndApiKey` (either); `allowedMethods` (`["post"]`; get, post, put, delete); `responseTimeout` (`30` s, 1–60, used when `respondImmediately` is false) | [webhook-trigger-actor.md](webhook-trigger-actor.md#options-reference) |
| `configuration.schedule` | `enabled`; `cron`, a literal expression; `timezone`, the IANA zone it is evaluated in (no default: always set it, or the job runs on the scheduler's server clock) | [scheduled-trigger-actor.md](scheduled-trigger-actor.md) |

**`configuration.lifecycle`**: `events` (string[], default `[]`), the lifecycle events the actor receives: any of
`'on-delete'` ([Cleaning Up on Delete](#cleaning-up-on-delete)), `'canvas-enabled'` and `'canvas-disabled'` (reserved:
accepted in the list, not delivered yet). List only the events your code handles: the vocabulary grows, and an event
reaches the actor only once listed.

**`configuration.options`** is interpolated. The Deno runtime fields sit at its root, identical to DenoActor
([deno-actor.md → Options](deno-actor.md#options)): `emitArrayAsSingleMessage`, `allowNet`, `allowNetList`,
`denyNetList`, `allowFs`, `env`. The webhook response behavior, shared with the standalone WebhookTriggerActor
([webhook-trigger-actor.md](webhook-trigger-actor.md#options-reference)), is nested under `webhook:`:
`respondImmediately`, `emitRawBody`, `response.statusCode` / `response.headers` / `response.body`. These may use
`${{ }}` expressions, with `trigger` in scope ([context.md → trigger](context.md#trigger)).

Exact types: [typescript/actorSchemas/trigger/universalTrigger.md](typescript/actorSchemas/trigger/universalTrigger.md)
(options), [typescript/actorSchemas/trigger/triggerConfig.md](typescript/actorSchemas/trigger/triggerConfig.md) (static
webhook/schedule/lifecycle config), and [typescript/schemas/trigger.md](typescript/schemas/trigger.md) (the
`TriggerEvent` union).

## Code Files

`configuration.codeDir` follows the DenoActor's rules, with the entrypoint `main.ts` at the root: relative imports with
the extension, no import leaving the tree, never interpolated, and the Deno reserved names
([code-actor-runtime.md → Source files](code-actor-runtime.md#source-files-codedir)). `main_test.ts` is reserved because
the runtime owns that name for this trigger's test harness: name your own test helpers something else. Splitting per
trigger source is the common shape:

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

## Code Template

The entrypoint file, `main.ts`:

```typescript
import type { TriggerRequest, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";
// import { RetryableError, biqApi, mountFile, stashFile } from "@borgiq/actors";

export default async function receive(req: TriggerRequest): Promise<Response> {
  // req.trigger is the delivered event, discriminated by `type` (fields per type: see Overview).
  // Return `memory` only when you change it (omit it to leave memory unchanged).
  switch (req.trigger.type) {
    case "webhook":
      return {
        results: { source: "webhook", request: req.trigger.request },
        // Respond to the webhook request:
        // signal: Signal.webhookRespond({ statusCode: 200, body: { ok: true } }),
      };
    case "schedule": {
      // To remember the previous fire, set `enableLTM: true` on the actor and add to the return:
      //   memory: { ltm: { ...req.memory.ltm, lastTriggeredAt: req.trigger.triggeredAt } }
      // Returning a non-empty `ltm` while LTM is disabled fails the run.
      const prev = (req.memory.ltm.lastTriggeredAt as string) ?? null;
      return {
        results: { source: "schedule", triggeredAt: req.trigger.triggeredAt, lastTriggeredAt: prev },
      };
    }
    case "lifecycle":
      // On 'on-delete', unregister what this trigger registered externally, idempotently; a hand-run test fire
      // (req.trigger.manual) is a dry run. See "Cleaning Up on Delete" below.
      if (req.trigger.event === "on-delete") {
        const { scope, subject, manual } = req.trigger;
        return { results: { source: "lifecycle", event: req.trigger.event, scope, subject, dryRun: manual === true } };
      }
      return { results: { source: "lifecycle", event: req.trigger.event } };
    case "manual":
      return { results: { source: "manual" } };
    default:
      return { results: { source: req.trigger.type } };
  }
}
```

## Emitted Message

Downstream actors see whatever the code returns as `results`, under `msg.<msgVar>` (the result schema is `z.any()`),
with the DenoActor's emit rules ([What gets emitted](code-actor-runtime.md#what-gets-emitted)): an array is **one**
message unless `emitArrayAsSingleMessage: false`. `results: undefined` (or omitted) or an empty array emits
**nothing**, which suits respond-only webhook handling and filtering out uninteresting fires.

## Responding to Webhook Firings

Two ways to answer the HTTP caller, mirroring the standalone WebhookTriggerActor's response modes:

**1. Immediate interpolated response** — `options.webhook.respondImmediately: true` with a `response` template. The
response is built before the code runs; `trigger.request` is in scope:

```yaml
options:
  webhook:
    respondImmediately: true
    response:
      statusCode: 200
      body: ${{ trigger.request?.body?.challenge || 'OK' }}
```

**2. Respond from the trigger's own code** — `options.webhook.respondImmediately: false`, then return a
`Signal.webhookRespond` from `receive`:

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

## Cleaning Up on Delete

Subscribe to `on-delete` when the trigger registers something **outside** BorgIQ — a webhook at a third-party API, a push subscription, a watch channel. The event is the actor's chance to unregister it when the actor goes away, so the external service is not left calling a URL that no longer exists.

> **Automatic delivery is not available yet.** Today `on-delete` is delivered only when you fire it by hand from the editor to test the handler. Deleting a canvas, a workspace or an organization, or deploying a canvas without the actor, does **not** fire it yet; that comes with a later platform release. Write the handler now so it is ready, but until then remove external registrations yourself before deleting a canvas that created them.

```yaml
configuration:
  lifecycle:
    events:
      - on-delete
```

The event arrives as `{ type: 'lifecycle', event: 'on-delete', scope, subject, manual? }`:

| Field | Type | Meaning |
|---|---|---|
| `scope` | `'actor'` \| `'canvas'` \| `'workspace'` \| `'org'` | Which level was deleted. Always present. Only `'actor'` is sent today; the others are reserved for automatic delivery |
| `subject` | `{ id }` | The deleted resource: the id of the actor, canvas, workspace or organization that `scope` names. Always present |
| `manual` | `true` | Set only on a test fire run by hand in a development workspace, where nothing was actually deleted — treat it as a dry run. Absent on automatic deliveries |

**When it is delivered:**

| When | Available | `scope` / `subject` | `manual` |
|---|---|---|---|
| By hand — **Run onDelete** on the trigger's node in the canvas editor, in a development workspace | **Now** — the only delivery today | `'actor'` / `{ id: <this actor's id> }` | `true` |
| A deployed canvas, its workspace or its organization is deleted | Not yet — coming in a later platform release | `'canvas'`, `'workspace'` or `'org'` / that resource | absent |
| A deploy removes the actor from its canvas | Not yet — coming in a later platform release | `'actor'` / the removed actor | absent |

Only an **active** Universal Trigger that lists `on-delete` in `configuration.lifecycle.events` can be fired by hand. A deployed workspace refuses the hand fire: it would run the production handler for a delete that never happened.

**Writing the handler:**

- **Make it idempotent.** Delivery will be at-least-once, so the same event can arrive more than once — and a hand run can be repeated. Record what the handler has released, and treat "already gone" (e.g. a `404` from the remote API) as success.
- **Treat `manual: true` as a dry run, and decide that from `manual`, never from `scope`.** A hand-run test fire deleted nothing, so report what the handler would release and change nothing. `scope: 'actor'` does not mean "hand run": a deploy that removes the actor will send it too, without `manual`, and that removal is real.
- **Keep it short, and not the only safeguard.** Prefer external registrations that expire on their own where the API offers that.
- **It runs like any other fire.** Configuration, connections, secrets and long-term memory are available, so ids saved in LTM at registration time and the credentials for the remote API are there to use.

**Idempotent handler** — the registration id was saved to LTM when the webhook was created (requires `enableLTM: true`). A hand-run test fire only reports what it would release, so testing never unregisters a hook the development canvas still uses:

```typescript
import type { TriggerRequest, Response } from "@borgiq/actors";

export default async function receive(req: TriggerRequest): Promise<Response> {
  if (req.trigger.type !== "lifecycle" || req.trigger.event !== "on-delete") {
    return { results: undefined, memory: req.memory };
  }

  const { scope, subject } = req.trigger;
  const hookId = (req.memory.ltm.hookId as string) ?? null;

  // A hand-run test fire ("Run onDelete") deleted nothing — a dry run: report what WOULD be released and keep it.
  // Check `manual`, not `scope`: a deploy that removes the actor also sends scope 'actor'.
  if (req.trigger.manual) {
    return { results: { dryRun: true, scope, subject, wouldRelease: hookId }, memory: req.memory };
  }

  // Already released by an earlier delivery — nothing to do.
  if (!hookId) {
    return { results: { released: null, scope, subject }, memory: req.memory };
  }

  const res = await fetch(`https://api.example.com/hooks/${hookId}`, {
    method: "DELETE",
    headers: { authorization: `Bearer ${req.credentials.accessToken}` },
  });
  // 404 means an earlier delivery (or someone else) already removed it — success, not an error.
  if (!res.ok && res.status !== 404) {
    throw new Error(`Failed to remove hook ${hookId}: ${res.status}`);
  }

  return {
    results: { released: hookId, scope, subject },
    memory: { stm: req.memory.stm, ltm: { ...req.memory.ltm, hookId: null } },
  };
}
```

Once automatic delivery arrives, `scope` says which level was deleted. Branch on it only when the cleanup differs by level — for example, removing a single webhook when the actor or its canvas goes away but revoking an account-wide subscription when the whole organization is deleted. Handle `manual` first, and give the `switch` a `default:` that fails the run, so a scope added in a later release is never silently skipped:

```typescript
if (req.trigger.manual) {
  // hand-run test fire — nothing was deleted
  return { results: { dryRun: true, wouldRelease: hookId }, memory: req.memory };
}
switch (req.trigger.scope) {
  case "actor": // a deploy removed this actor from its canvas
  case "canvas":
  case "workspace":
    await removeWebhook(hookId);
    break;
  case "org":
    await revokeAllSubscriptions();
    break;
  default:
    // a scope this code predates: fail loudly rather than skip the cleanup
    throw new Error(`Unhandled on-delete scope: ${req.trigger.scope}`);
}
```

## Memory

Memory is **fully opt-in**: no infrastructure code reads or writes LTM/STM on your behalf. In particular the previous
schedule fire is **not** tracked: persist it yourself in `req.memory.ltm` (as in the [Code Template](#code-template))
after setting `enableLTM: true`. The merge contract, the `null` rule for clearing a key and the 1 KB / 4 KB caps are the
DenoActor's: [code-actor-runtime.md → Memory](code-actor-runtime.md#memory).

## Common Mistakes

1. **Static fields under `options`** — `triggerKey`, `authorizationLevel`, `allowedMethods`, `responseTimeout`, `cron`, `timezone`, `enabled`, `events` live in `configuration.webhook` / `configuration.schedule` / `configuration.lifecycle` (literals only), not in `configuration.options`.
2. **Reading `trigger.request` without a type guard** — on schedule/lifecycle/manual fires `req.trigger.request` does not exist. Branch on `req.trigger.type` (in code) or `${{ trigger.type === 'webhook' }}` / `${{ trigger?.request?.… }}` (in templates).
3. **Expecting the previous schedule fire automatically** — keep it in LTM yourself ([Memory](#memory)); to clear a memory key, return it as `null` (as the on-delete handler does with `hookId: null`), never leave it out.
4. **Typing the entry point as `Request`** — use `TriggerRequest`, otherwise `req.trigger` is not typed.
5. **Missing `triggerKey` with `webhook.enabled: true`** — the webhook URL will not work without it.
6. **A non-idempotent `on-delete` handler, or relying on `on-delete` today** — delivery will be at-least-once and a hand run can be repeated; nothing fires it automatically yet, so remove external registrations yourself before deleting ([Cleaning Up on Delete](#cleaning-up-on-delete)).
7. **Treating `scope: 'actor'` as a hand run** — check `manual`. A deploy that removes the actor will also send `scope: 'actor'`, without `manual`, and that removal is real.
