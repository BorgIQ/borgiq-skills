# Webhook Response Actor Reference

The WebhookResponseActor answers the HTTP caller of the WebhookTriggerActor (or webhook-fired UniversalTriggerActor) that started the run. Use it whenever the trigger has `respondImmediately: false`, the default, and put one on every path. What the caller receives, timeouts and errors: [webhook-trigger-actor.md → Responding to the caller](webhook-trigger-actor.md#responding-to-the-caller).

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `statusCode` | number | `200` | HTTP status |
| `headers` | object | — | Response headers |
| `body` | any | `Response to webhook from WebhookResponse Actor` | Response body (string, object, …) |

It emits what it sent, `{ statusCode, body, headers }`, on `SPRTdefault`, so the flow can continue after answering. Exact schema: [typescript/actorSchemas/task/webhookResponse.md](typescript/actorSchemas/task/webhookResponse.md).

## Example

```yaml
type: WebhookResponseActor
version: 1
name: Webhook Response
msgVar: webhook_response
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    statusCode: "${{ msg.api_call.statusCode < 300 ? 200 : 500 }}"   # quoted: a plain YAML value cannot contain ': '
    headers:
      content-type: application/json
      x-request-id: ${{ msg.webhook_trigger.headers['x-request-id'] }}
    body: ${{ msg.api_call.body }}
schemas: {}
```

The trigger it answers uses the current config shape: static fields under `configuration.webhook`, and `respondImmediately: false` under `configuration.options.webhook` (see [webhook-trigger-actor.md → Configuration](webhook-trigger-actor.md#configuration)).

## One response per path

Behind a [RouterActor](router-actor.md), give each route its own WebhookResponseActor, e.g. `200` with the result on a `Success` port and `500` with `{ error: true, message: … }` on an `Error` port. Only the first response of a run reaches the caller; a later one still emits but sends nothing.
