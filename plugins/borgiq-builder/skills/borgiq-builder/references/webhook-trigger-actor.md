# Webhook Trigger Actor Reference

The WebhookTriggerActor starts a workflow when it receives an HTTP request at its unique webhook URL.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Options Reference](#options-reference)
- [TypeScript Schema Definition](#typescript-schema-definition)
- [Emitted Message](#emitted-message)
- [Response Modes](#response-modes)
- [Common Patterns](#common-patterns)
- [Accessing in Downstream Actors](#accessing-in-downstream-actors)
- [Security Considerations](#security-considerations)
- [Quick Example](#quick-example)

## Overview

Webhook triggers allow external systems to initiate workflows by sending HTTP requests. Each webhook trigger has a unique URL that accepts incoming requests. Use webhook triggers for:

- Receiving notifications from third-party services (GitHub, Stripe, Slack, etc.)
- Building API endpoints that trigger workflows
- Integrating with external systems that support webhooks
- Real-time event processing from external sources

If the same workflow must also fire on a schedule, or you need code to run at trigger time (normalize, filter, respond programmatically), see [universal-trigger-actor.md](universal-trigger-actor.md).

> **Reading the inbound HTTP payload — `trigger.request` vs `msg.<this>`:** Inside this actor's own `options.webhook.response.*` config the trigger has not emitted yet, so `msg.<thisActor>` is **undefined**. Read the inbound payload via `trigger.request` (`trigger.request.body`, `trigger.request.headers`, `trigger.request.queryParams`). Downstream actors see the same payload via `msg.<triggerMsgVar>`. See [context.md → trigger](context.md#trigger) for the full rule and a Slack `url_verification` example.

## Configuration Structure

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01xxxxx:
    type: WebhookTriggerActor
    version: 1
    name: Webhook Trigger
    msgVar: webhook_trigger
    description: Receive HTTP requests to trigger the workflow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      # STATIC, admission-consumed settings — literals only (never interpolated), DB-queryable
      webhook:
        triggerKey: 01KDXXXXXXXXXXXXXXXXXX
        authorizationLevel: public
        allowedMethods:
          - get
          - post
        responseTimeout: 30
      options:
        # INTERPOLATABLE response behavior — resolved at runtime (supports ${{ }} expressions)
        webhook:
          respondImmediately: true
          emitRawBody: false
          response:
            statusCode: 200
            headers:
              content-type: text/plain; charset=utf-8
            body: OK
    schemas: {}
    id: ACTR01xxxxx
    position:
      x: 0
      'y': 0
    edges: {}
```

## Options Reference

| Option | Location | Type | Default | Description |
|--------|----------|------|---------|-------------|
| `triggerKey` | `configuration.webhook` | string | - | Unique key forming the webhook URL (static, literal only) |
| `authorizationLevel` | `configuration.webhook` | `public` \| `apps` | `public` | Who may call the webhook (static, literal only) |
| `allowedMethods` | `configuration.webhook` | string[] | `["post"]` | HTTP methods accepted (get, post, put, delete) — static, literal only |
| `responseTimeout` | `configuration.webhook` | number | `30` | Request timeout in seconds when `respondImmediately` is false (1-60) — static, literal only |
| `respondImmediately` | `configuration.options.webhook` | boolean | `true` | Respond immediately before workflow completes (interpolatable) |
| `emitRawBody` | `configuration.options.webhook` | boolean | `false` | Emit raw body bytes instead of parsed content (interpolatable) |
| `response` | `configuration.options.webhook` | object | - | Immediate response configuration (interpolatable) |
| `response.statusCode` | `configuration.options.webhook` | number | `200` | HTTP status code for immediate response |
| `response.headers` | `configuration.options.webhook` | object | - | Response headers |
| `response.body` | `configuration.options.webhook` | string | `"OK"` | Response body content |

## TypeScript Schema Definition

The complete TypeScript schema for WebhookTriggerActor options and results:

```typescript
import { z } from 'zod';

// STATIC, admission-consumed config — lives at `configuration.webhook` (never interpolated).
export const WebhookConfigSchema = z.object({
  triggerKey: z.string().optional(),
  authorizationLevel: z.enum(['public', 'apps']).optional(),
  allowedMethods: z.array(z.enum(['get', 'post', 'put', 'delete'])).optional(),
  responseTimeout: z.number().gte(1).lte(60).optional(),
  enabled: z.boolean().optional(), // UniversalTriggerActor only
});

// INTERPOLATABLE response behavior — lives at `configuration.options.webhook`.
export const WebhookBehaviorOptionsSchema = z.object({
  respondImmediately: z.union([z.boolean(), z.string()]).nullish(),
  emitRawBody: z.union([z.boolean(), z.string()]).nullish(),
  response: z.object({
    statusCode: z.union([z.number(), z.string()]),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.unknown(),
  }).nullish(),
});

/** The options schema for the WebhookTriggerActor (only the interpolatable behavior). */
export const WebhookTriggerActorOptionsSchema = z.object({
  webhook: WebhookBehaviorOptionsSchema.nullish(),
});

export type WebhookTriggerActorOptions = z.infer<typeof WebhookTriggerActorOptionsSchema>;

/** The response schema for the WebhookTriggerActor */
export const WebhookTriggerActorResultSchema = z.object({
  meta: z.object({
    requestId: z.string()
      .describe('The request id of the webhook request'),
  }),
  method: z.string().nullish()
    .describe('The method of the request. Valid methods are GET, POST, PUT, DELETE'),
  headers: z.record(z.string(), z.any()).nullish()
    .describe('The headers sent with the request'),
  body: z.any().nullish()
    .describe('The body sent with the request'),
  queryParams: z.any().nullish()
    .describe('The query parameters sent with the request'),
  rawBody: z.string().nullish()
    .describe('The raw body of the request if emitRawBody was set to true in the options'),
  response: z.object({
    statusCode: z.number(),
    headers: z.record(z.string(), z.unknown()).nullish(),
    body: z.any().nullish(),
  }).nullish()
    .describe('The response to the webhook request if respondImmediately was set to true'),
});

export type WebhookTriggerActorResult = z.infer<typeof WebhookTriggerActorResultSchema>;
```

### Config shape

Webhook config is split along the interpolation boundary:

- **`configuration.webhook`** — STATIC, admission-consumed fields (`triggerKey`, `authorizationLevel`, `allowedMethods`, `responseTimeout`, and `enabled` for the universal trigger). Never interpolated — must be literals; DB-queryable.
- **`configuration.options.webhook`** — INTERPOLATABLE response behavior (`respondImmediately`, `emitRawBody`, `response`). Resolved at runtime with the request in scope, so these may use `${{ }}` expressions (e.g. `respondImmediately: ${{ trigger.request.headers['x-sync'] == 'true' }}`).

### Validation Rules

- `responseTimeout` must be between 1 and 60 seconds
- `allowedMethods` values must be lowercase: `get`, `post`, `put`, `delete`
- static fields in `configuration.webhook` cannot contain `${{ }}` expressions

### triggerKey

The `triggerKey` (at `configuration.webhook.triggerKey`) is a unique identifier for each webhook trigger. It forms part of the webhook URL:

```
https://<borgiq-domain>/webhook/<triggerKey>
```

**Important:** You must generate and include a `triggerKey` for every WebhookTriggerActor. A webhook trigger without this key will not work.

**Generate using the CLI:**
```bash
borgiq generate id webhooktriggerkey
# Output: 01KD298E3VRBDAZN9X5ETV4R6G
```

Then add it to your configuration:
```yaml
configuration:
  webhook:
    triggerKey: 01KD298E3VRBDAZN9X5ETV4R6G  # Generated key
    authorizationLevel: public
    allowedMethods: [get, post]
  options:
    webhook:
      # ... interpolatable response behavior ...
```

## Emitted Message

The webhook trigger emits a message containing the HTTP request details:

```json
{
  "meta": {
    "requestId": "WREQ01kd...",
    "ipAddress": "203.0.113.42",
    "user": {
      "id": "USR01kd...",
      "name": "Jane Doe",
      "email": "jane@example.com"
    }
  },
  "method": "POST",
  "headers": {
    "content-type": "application/json",
    "user-agent": "GitHub-Hookshot/...",
    "x-github-event": "push"
  },
  "queryParams": {
    "param1": "value1"
  },
  "body": {
    "...parsed request body..."
  },
  "rawBody": "...",
  "response": {
    "statusCode": 200,
    "headers": { "content-type": "text/plain" },
    "body": "OK"
  }
}
```

| Field | Description |
|-------|-------------|
| `meta.requestId` | Unique identifier for this webhook request |
| `meta.ipAddress` | Caller IP address (optional — present when resolvable from the incoming request) |
| `meta.user` | Authenticated user info `{ id, name?, email }` — only populated when the webhook is **app-authorized** (`configuration.webhook.authorizationLevel: 'apps'`). Mirrors the `$.user` shape emitted by InterfaceTriggerActor so downstream actors can use the same templates. |
| `method` | HTTP method (GET, POST, PUT, DELETE) |
| `headers` | Request headers (lowercase keys) |
| `queryParams` | URL query parameters |
| `body` | Parsed request body (JSON, form data, etc.) |
| `rawBody` | Raw body string (only when `emitRawBody: true`) |
| `response` | The immediate response sent (only when `respondImmediately: true`) |

## Response Modes

### Immediate Response (Default)

With `respondImmediately: true`, the webhook responds instantly with the configured response, then the workflow runs asynchronously.

```yaml
configuration:
  options:
    webhook:
      respondImmediately: true
      response:
        statusCode: 200
        headers:
          content-type: application/json
        body: '{"status": "received"}'
```

**Use when:** You don't need to return workflow results to the caller.

### Deferred Response

With `respondImmediately: false`, the workflow must explicitly respond using a DenoActor with the `WebhookRespond` signal.

```yaml
configuration:
  options:
    webhook:
      respondImmediately: false
```

**Use when:** You need to return workflow results or computed data to the caller.

#### Responding from DenoActor

```typescript
import type { Request, Response } from "@borgiq/actors";
import { Signal } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  // Process data...
  const result = await processData(req.inputs);

  // Send response back to webhook caller via the returned signal
  return {
    results: result,
    signal: Signal.webhookRespond({
      statusCode: 200,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ result }),
    }),
  };
}
```

## Common Patterns

### Computed Immediate Response

Use `${{ }}` expressions in `response.body` to compute and return results directly from the trigger—no downstream actors needed. This is ideal for lightweight API endpoints that only need to read the request, context data, or transform inputs.

> **Scope reminder:** `response.*` templates run **before** the trigger emits, so `msg.<thisActor>` does **not** exist yet. To read the inbound HTTP request inside the trigger's own response config, use `trigger.request` (`trigger.request.body`, `trigger.request.headers`, `trigger.request.queryParams`) — **not** `msg.<thisActor>.body`. See [context.md → trigger](context.md#trigger) for the full rule. `ctx`, `inputs`, and `vars` are also in scope.

```yaml
configuration:
  webhook:
    allowedMethods:
      - get
  options:
    webhook:
      respondImmediately: true
      emitRawBody: false
      response:
        statusCode: 200
        body: >-
          ${{ { apps:
          Object.entries(ctx.canvas.interfaceTriggers).map(([msgVar, trigger])
          => ({
              id: trigger.id,
              name: trigger.name,
              description: trigger.description || '',
              url: trigger.url,
              msgVar: msgVar,
              isActive: trigger.isActive,
              type: trigger.type,
            }
          )) } }}
```

**When to use:** The response body only needs `trigger.request`, `ctx`, `inputs`, `vars`, or static data—no fetch calls, no external APIs, no complex imperative logic.

### Slack `url_verification` Challenge

Slack's Events API sends a one-time `url_verification` request when you register a webhook and expects the bare `challenge` value echoed back in the response body. Because the trigger has to answer immediately, the response template runs at response-build time — `msg.<thisActor>` is not yet populated, so you must read the inbound payload via `trigger.request`:

```yaml
configuration:
  webhook:
    authorizationLevel: public    # Slack's check needs a public URL
    allowedMethods:
      - post
  options:
    webhook:
      respondImmediately: true
      emitRawBody: false
      response:
        statusCode: 200
        headers:
          content-type: text/plain; charset=utf-8
        body: ${{ trigger.request?.body?.challenge || 'OK' }}    # ✅ uses `trigger.request` — not `msg.<thisActor>`
```

> **Common mistake:** writing `${{ msg.receive_slack_event?.body?.challenge || 'OK' }}` here. That references the **actor's own emitted message**, which doesn't exist until *after* the response goes out, so the template evaluates to `'OK'` and Slack rejects the URL. Always read the inbound payload from `trigger.request` inside the trigger's `response.*` fields.

### Accept Multiple Methods

```yaml
configuration:
  webhook:
    allowedMethods:
      - get
      - post
      - put
      - delete
```

### GitHub Webhook

```yaml
configuration:
  webhook:
    allowedMethods:
      - post
  options:
    webhook:
      respondImmediately: true
      response:
        statusCode: 200
        body: OK
```

Access GitHub event data in downstream actors:

```yaml
# In downstream actor
configuration:
  inputs:
    event: ${{ msg.webhook_trigger.headers['x-github-event'] }}
    payload: ${{ msg.webhook_trigger.body }}
```

### Stripe Webhook with Raw Body

Stripe requires the raw body for signature verification:

```yaml
configuration:
  webhook:
    allowedMethods:
      - post
  options:
    webhook:
      emitRawBody: true
      respondImmediately: true
      response:
        statusCode: 200
        body: OK
```

```typescript
// In DenoActor for Stripe signature verification
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const signature = req.inputs.headers['stripe-signature'];
  const rawBody = req.inputs.rawBody;
  const secret = req.credentials.STRIPE_WEBHOOK_SECRET;

  // Verify signature using raw body
  const isValid = verifyStripeSignature(rawBody, signature, secret);

  if (!isValid) {
    throw new Error('Invalid Stripe signature');
  }

  return { results: req.inputs.body };
}
```

### API Endpoint with Response

```yaml
configuration:
  webhook:
    allowedMethods:
      - post
  options:
    webhook:
      respondImmediately: false
```

The workflow processes the request and returns a computed response via `webhookRespond` signal.

## Accessing in Downstream Actors

```yaml
# In HttpRequestActor
configuration:
  inputs:
    userId: ${{ msg.webhook_trigger.body.user.id }}
    action: ${{ msg.webhook_trigger.body.action }}
```

```typescript
// In DenoActor
import type { Request, Response } from "@borgiq/actors";

export default async function receive(req: Request): Promise<Response> {
  const webhookData = req.inputs;
  const method = webhookData.method;
  const headers = webhookData.headers;
  const body = webhookData.body;

  console.log(`Received ${method} request`);
  return { results: { processed: body } };
}
```

## Security Considerations

1. **Validate signatures** - Many services (GitHub, Stripe, Slack) sign webhook payloads. Verify signatures to ensure authenticity.

2. **Use HTTPS** - BorgIQ webhook URLs use HTTPS by default.

3. **Validate payload structure** - Check that incoming payloads match expected structure before processing.

4. **Rate limiting** - Consider downstream rate limits when processing high-volume webhooks.

## Quick Example

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  ACTR01kd298e3vrbdazn9x5etv4r6f:
    type: WebhookTriggerActor
    version: 1
    name: GitHub Push Webhook
    msgVar: github_push_webhook
    description: Receive GitHub push events to trigger CI/CD workflow
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      webhook:
        triggerKey: 01KD298E3VRBDAZN9X5ETV4R6G
        allowedMethods:
          - post
      options:
        webhook:
          respondImmediately: true
          emitRawBody: false
          response:
            statusCode: 200
            headers:
              content-type: text/plain; charset=utf-8
            body: OK
    schemas: {}
    id: ACTR01kd298e3vrbdazn9x5etv4r6f
    position:
      x: 0
      'y': 0
    edges: {}
```
