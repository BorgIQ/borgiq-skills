# Complete Workflow Example

A webhook endpoint that routes a request by its `action` field and answers with a WebhookResponseActor, written as a
canvas bundle. Read it as the model for a multi-actor bundle; the format is in [canvas-bundles.md](cli/canvas-bundles.md).

```
POST → webhook_trigger → route_by_action ─ Create  → create_response (201)
                                          ├ Update  → update_response (200)
                                          └ Unknown → unknown_action  (400, the default port)
```

## canvas.yaml

The actor index (each actor lives at its `path`), positions and edges. `bundle init` and `bundle pull` also write the CLI-owned keys; leave those alone.

```yaml
format: borgiq.canvas.bundle
formatVersion: 1
canvas:
  slug: webhook-router
  name: Webhook Router
actors:
  - { id: ACTR01m3snwbtbgxwvsg38jghyy0wb, type: WebhookTriggerActor, path: actors/triggers/webhook/ACTR01m3snwbtbgxwvsg38jghyy0wb }
  - { id: ACTR01m3snwc33nqnc3dexjga60bsw, type: RouterActor, path: actors/tasks/router/ACTR01m3snwc33nqnc3dexjga60bsw }
  - { id: ACTR01m3snwcbxnpyyzp68kf90n10s, type: WebhookResponseActor, path: actors/tasks/webhook-response/ACTR01m3snwcbxnpyyzp68kf90n10s }
  - { id: ACTR01m3snwcmeyekx97tw83v1nxz4, type: WebhookResponseActor, path: actors/tasks/webhook-response/ACTR01m3snwcmeyekx97tw83v1nxz4 }
  - { id: ACTR01m3snwsmnxk91h1ggc4zxshb8, type: WebhookResponseActor, path: actors/tasks/webhook-response/ACTR01m3snwsmnxk91h1ggc4zxshb8 }
graph:
  nodes:
    - { actorId: ACTR01m3snwbtbgxwvsg38jghyy0wb, position: { x: 0, y: 0 } }
    - { actorId: ACTR01m3snwc33nqnc3dexjga60bsw, position: { x: 0, y: 200 } }
    - { actorId: ACTR01m3snwcbxnpyyzp68kf90n10s, position: { x: -300, y: 400 } }
    - { actorId: ACTR01m3snwcmeyekx97tw83v1nxz4, position: { x: 0, y: 400 } }
    - { actorId: ACTR01m3snwsmnxk91h1ggc4zxshb8, position: { x: 300, y: 400 } }
  edges:
    - { id: EDGE01m3snwcx1tcajm6ze3h5bqng5, sourceActorId: ACTR01m3snwbtbgxwvsg38jghyy0wb, sourcePortId: SPRTdefault, targetActorId: ACTR01m3snwc33nqnc3dexjga60bsw, targetPortId: TPRTdefault, type: borgiqEdge }
    - { id: EDGE01m3snwd5m0dqfk258brj0f92x, sourceActorId: ACTR01m3snwc33nqnc3dexjga60bsw, sourcePortId: SPRTfqxv4ld, targetActorId: ACTR01m3snwcbxnpyyzp68kf90n10s, targetPortId: TPRTdefault, type: borgiqEdge }
    - { id: EDGE01m3snwdecny2anqat1fmbf1tq, sourceActorId: ACTR01m3snwc33nqnc3dexjga60bsw, sourcePortId: SPRTgc1tf89, targetActorId: ACTR01m3snwcmeyekx97tw83v1nxz4, targetPortId: TPRTdefault, type: borgiqEdge }
    - { id: EDGE01m3snwsxeyqa963q46nvxf00v, sourceActorId: ACTR01m3snwc33nqnc3dexjga60bsw, sourcePortId: SPRTdefault, targetActorId: ACTR01m3snwsmnxk91h1ggc4zxshb8, targetPortId: TPRTdefault, type: borgiqEdge }
```

## actor.yaml files

```yaml
# actors/triggers/webhook/ACTR01m3snwbtbgxwvsg38jghyy0wb/actor.yaml
id: ACTR01m3snwbtbgxwvsg38jghyy0wb
version: 1
type: WebhookTriggerActor
name: Webhook Trigger
msgVar: webhook_trigger
description: Receives the request to route.
isActive: true
continueOnError: false
sourcePorts:
  - id: SPRTdefault
configuration:
  webhook:                       # static literals
    triggerKey: 01M3SNWE8DDSVT1ARR12MFVSRZ   # borgiq generate id webhooktriggerkey
    authorizationLevel: public
    allowedMethods: [post]
    responseTimeout: 30
  options:
    webhook:
      respondImmediately: false  # a WebhookResponseActor answers
      emitRawBody: false
schemas: {}
```

```yaml
# actors/tasks/router/ACTR01m3snwc33nqnc3dexjga60bsw/actor.yaml
id: ACTR01m3snwc33nqnc3dexjga60bsw
version: 1
type: RouterActor
name: Route by Action
msgVar: route_by_action
description: Routes the request by its action field.
isActive: true
continueOnError: false
sourcePorts:
  - { id: SPRTfqxv4ld, name: Create, description: action is create }
  - { id: SPRTgc1tf89, name: Update, description: action is update }
  - { id: SPRTdefault, name: Unknown, description: any other action }
configuration:
  options:
    emitType: singleRoute
    conditions:
      Create: ${{ msg.webhook_trigger.body?.action === 'create' }}
      Update: ${{ msg.webhook_trigger.body?.action === 'update' }}
schemas: {}
```

```yaml
# actors/tasks/webhook-response/ACTR01m3snwcbxnpyyzp68kf90n10s/actor.yaml
id: ACTR01m3snwcbxnpyyzp68kf90n10s
version: 1
type: WebhookResponseActor
name: Create Response
msgVar: create_response
description: Answers a create request.
isActive: true
continueOnError: false
sourcePorts:
  - id: SPRTdefault
configuration:
  options:
    statusCode: 201
    headers:
      content-type: application/json
    body:
      message: Resource created
      data: ${{ msg.webhook_trigger.body }}
schemas: {}
```

`update_response` and `unknown_action` are the same with their own `id`, `name`, `msgVar` and `description`, and
`statusCode: 200` / `message: Resource updated`, and `statusCode: 400` / `message: Unknown action`.

## Key points

- `respondImmediately: false` makes the caller wait for a WebhookResponseActor. Every router port needs a path to a
  response: a request that reaches none waits `responseTimeout` seconds (default 30) and then gets a timeout error.
- The router's custom ports (`SPRT` + 7 characters, from `borgiq generate id sourceport`) are named like its
  `conditions` keys; the default port catches everything else and takes no condition.
- WebhookResponseActors end the flow, so no edge leaves them.
- Mint fresh IDs and a fresh `triggerKey` for a real canvas, then `borgiq bundle validate <dir> --strict` and
  `borgiq bundle push <dir> --create --auto-layout`.
