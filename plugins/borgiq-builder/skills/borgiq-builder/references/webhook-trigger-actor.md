# Webhook Trigger Actor Reference

The WebhookTriggerActor starts a flow when an HTTP request reaches its URL: third-party webhooks (GitHub, Stripe, Slack) and API endpoints. It covers the response to the caller, config, options, URL, emitted message and patterns. If the same flow must also run on a schedule, or code must run at trigger time (normalize, filter, respond from code), use [universal-trigger-actor.md](universal-trigger-actor.md).

## Contents

- [Responding to the caller](#responding-to-the-caller)
- [Configuration](#configuration)
- [Options reference](#options-reference)
- [URL and triggerKey](#url-and-triggerkey)
- [Emitted message](#emitted-message)
- [Reading the request](#reading-the-request)
- [Patterns](#patterns)

## Responding to the caller

- `respondImmediately` defaults to `false`: the request stays open until a downstream [WebhookResponseActor](webhook-response-actor.md) runs, or a DenoActor returns `signal: Signal.webhookRespond({ statusCode, headers, body })` (see [deno-actor.md](deno-actor.md)). Put one on every path, error paths included.
- Set `respondImmediately: true` when the caller needs no result: the trigger answers with `options.webhook.response`, then the flow runs on.

| Outcome | The caller gets | When |
|---|---|---|
| A WebhookResponseActor or `webhookRespond` signal runs | its `statusCode` (default `200`), `headers` and `body` | as soon as it runs; the flow continues |
| `respondImmediately: true` | `response.statusCode` (default `200`), `response.headers`, `response.body` | when the trigger runs, before any downstream actor |
| Nothing responds within `responseTimeout` (no response actor on the path, or it failed) | HTTP 400, `message: "webhook trigger timed out"` | at the timeout; the flow keeps running |
| Unknown actor or wrong `triggerKey` | HTTP 404 | at once; no flow starts |
| Missing or invalid credential for the `authorizationLevel` | HTTP 401 | at once; no flow starts |
| Method not in `allowedMethods` | HTTP 400 | at once; no flow starts |
| Request larger than the workspace limit (64 KB by default) | HTTP 413 | at once; no flow starts |

Only the first response of a run reaches the caller; a later response actor still emits but sends nothing. A response from the flow carries `x-borgiq-request-id` and `x-borgiq-flowrun-id` headers, so a caller can find its run.

## Configuration

```yaml
type: WebhookTriggerActor
version: 1
name: GitHub Push Webhook
msgVar: webhook_trigger
isActive: true
sourcePorts:
  - id: SPRTdefault
configuration:
  webhook:                    # static: literals only, never interpolated
    triggerKey: 01KD298E3VRBDAZN9X5ETV4R6G   # borgiq generate id webhooktriggerkey
    authorizationLevel: public
    allowedMethods:
      - post
    responseTimeout: 30
  options:
    webhook:                  # interpolated at request time: ${{ }} allowed
      respondImmediately: false
      emitRawBody: false
schemas: {}
```

The config is split along the interpolation boundary:
- **`configuration.webhook`**: static fields read when the request arrives; literals only (a `${{ }}` is rejected).
- **`configuration.options.webhook`**: the response behavior, interpolated with the request in scope, e.g. `respondImmediately: ${{ trigger.request.headers['x-sync'] == 'true' }}`.

## Options reference

| Option | In | Type | Default | Meaning |
|---|---|---|---|---|
| `triggerKey` | `webhook` | string | — (required) | Last URL segment. A trigger without it cannot be called. |
| `authorizationLevel` | `webhook` | `public` \| `apps` \| `apiKey` \| `appsAndApiKey` | `public` | `public`: anyone. `apps`: a valid app actor webhook token (`x-app-actor-token`). `apiKey`: a personal access token in `Authorization: Bearer` or `X-Api-Key` whose owner is a workspace member and whose scopes include `workspace:access`. `appsAndApiKey`: either; the app token wins when both are sent. |
| `allowedMethods` | `webhook` | list of `get`, `post`, `put`, `delete` (lowercase) | `[post]` | Methods accepted |
| `responseTimeout` | `webhook` | number, 1–60 | `30` | Seconds the request stays open waiting for a response |
| `respondImmediately` | `options.webhook` | boolean | `false` | `true`: answer with `response` at once |
| `emitRawBody` | `options.webhook` | boolean | `false` | Add the unparsed body as `rawBody` (for signature checks) |
| `response.statusCode` | `options.webhook` | number | `200` | Immediate response status |
| `response.headers` | `options.webhook` | object | — | Immediate response headers |
| `response.body` | `options.webhook` | any | — | Immediate response body |

Exact schemas: [typescript/actorSchemas/trigger/webhook.md](typescript/actorSchemas/trigger/webhook.md) (options and emitted message) and [typescript/actorSchemas/trigger/triggerConfig.md](typescript/actorSchemas/trigger/triggerConfig.md) (`configuration.webhook`).

## URL and triggerKey

```
https://<borgiq-api-host>/msg/<orgSlug>/<workspaceSlug>/<canvasId>/<actorId>/<triggerKey>
```

- Mint the key with `borgiq generate id webhooktriggerkey`; never invent one.
- Read the URL from `${{ ctx.canvas.webhookTriggers.<msgVar>.url }}` rather than building it.

## Emitted message

| Field | Meaning |
|---|---|
| `method` | `GET`, `POST`, `PUT` or `DELETE` |
| `headers` | Request headers, lowercase keys |
| `queryParams` | URL query parameters |
| `body` | Parsed body (JSON, form data, …) |
| `rawBody` | Raw body string; only with `emitRawBody: true` |
| `response` | The response sent; only with `respondImmediately: true` |
| `meta.requestId` | Id of this request (`WREQ…`) |
| `meta.ipAddress` | Caller IP, when it can be resolved |
| `meta.user` | `{ id, name?, email, appSessionId? }`: the caller, when it sent an app actor webhook token or an API key (then the key's owner). Absent on public calls. Same shape as InterfaceTriggerActor's `user`, so downstream templates can be shared. |
| `meta.auth` | `{ type: 'apiToken', keyId, keyName }`: the API key that authenticated the call; only on API-key calls. Never the secret: on those calls the `authorization` and `x-api-key` headers are stripped before the request is stored. Branch on `keyName` or `keyId` for per-caller behavior. |

## Reading the request

- Inside this actor's own `options.webhook` fields, read the request from `trigger.request` (`.body`, `.headers`, `.queryParams`). `msg.<thisActor>` does not exist until the trigger emits, which is after the response is built. `ctx`, `inputs` and `vars` are also in scope. See [context.md → trigger](context.md#trigger).
- Downstream actors read `msg.<msgVar>`, e.g. `${{ msg.webhook_trigger.headers['x-github-event'] }}` or `${{ msg.webhook_trigger.body.user.id }}`.
- A code actor gets the request through its `configuration.inputs`, e.g. `inputs: ${{ msg.webhook_trigger }}`, then reads `req.inputs.body`.

## Patterns

**Slack `url_verification`.** Slack sends a one-time request when you register the URL and expects the bare `challenge` value back:

```yaml
configuration:
  webhook:
    triggerKey: 01KD298E3VRBDAZN9X5ETV4R6G
    authorizationLevel: public    # Slack's check needs a public URL
    allowedMethods:
      - post
  options:
    webhook:
      respondImmediately: true
      response:
        statusCode: 200
        headers:
          content-type: text/plain; charset=utf-8
        body: ${{ trigger.request?.body?.challenge || 'OK' }}
```

Writing `${{ msg.receive_slack_event?.body?.challenge || 'OK' }}` here is the common mistake: that message does not exist yet, the template yields `'OK'`, and Slack rejects the URL.

**Computed response, no downstream actors.** Compute `response.body` from `trigger.request`, `ctx`, `inputs`, `vars` or static data (e.g. list `ctx.canvas.interfaceTriggers`). Work that needs I/O (fetch, external APIs) or imperative logic goes downstream, with a deferred response.

**Signed payloads (Stripe, GitHub, Slack).** Verify the signature before trusting the payload. Stripe needs the raw body: set `emitRawBody: true`, and in a DenoActor with `inputs: ${{ msg.webhook_trigger }}` verify `req.inputs.rawBody` against `req.inputs.headers['stripe-signature']` with the signing secret from `req.credentials`; throw when it does not match. Check the payload's shape before processing it, and mind downstream rate limits on high-volume webhooks.
