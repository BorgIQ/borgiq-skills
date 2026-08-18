# Complete Workflow Example

This example demonstrates a webhook-based workflow that receives an HTTP request, processes it with a router, and returns different responses based on conditions.

## Table of Contents

- [Workflow Diagram](#workflow-diagram)
- [Complete YAML](#complete-yaml)
- [Key Points](#key-points)
- [Advanced Example](#advanced-example)

## Workflow Diagram

```
          ┌──────────────────────┐
          │   Webhook Trigger    │  y: 0
          │   (POST /webhook)    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │       Router         │  y: 200
          │   (Route by Action)  │
          └────┬────────────┬────┘
               │            │
      Create   │            │  Update
               ▼            ▼
   ┌───────────────┐  ┌───────────────┐
   │Create Response│  │Update Response│  y: 400
   │ (201 Created) │  │   (200 OK)    │
   │   x: -300     │  │   x: 300      │
   └───────────────┘  └───────────────┘
```

## Complete YAML

```yaml
metadata:
  schemaVersion: v1.0
  source: BIQCanvas
actors:
  # 1. Webhook Trigger - receives incoming HTTP requests
  ACTR01kd6gqghj04j8765nnqyp09a3:
    type: WebhookTriggerActor
    version: 1
    name: Webhook Trigger
    msgVar: webhook_trigger
    description: Receives incoming webhook requests
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        allowedMethods:
          - post
        respondImmediately: false  # Wait for WebhookResponseActor
        emitRawBody: false
    schemas: {}
    id: ACTR01kd6gqghj04j8765nnqyp09a3
    position:
      x: 0
      'y': 0
    edges:
      EDGE01kd6gqx5k7tvzs86y40w8etms:
        id: EDGE01kd6gqx5k7tvzs86y40w8etms
        sourceActorId: ACTR01kd6gqghj04j8765nnqyp09a3
        sourcePortId: SPRTdefault
        targetActorId: ACTR01kd6gqx5k7tvzs86y40w8etmr
        targetPortId: TPRTdefault
        label: ''
        type: borgiqEdge

  # 2. Router - routes based on request body content
  ACTR01kd6gqx5k7tvzs86y40w8etmr:
    type: RouterActor
    version: 1
    name: Route by Action
    msgVar: route_by_action
    description: Routes requests based on the action field
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRT5d5gj2s
        name: Create
      - id: SPRTg5vsvui
        name: Update
      - id: SPRTdefault
        name: F
    configuration:
      options:
        emitType: singleRoute
        conditions:
          Create: ${{ msg.webhook_trigger.body?.action === 'create' }}
          Update: ${{ msg.webhook_trigger.body?.action === 'update' }}
    schemas: {}
    id: ACTR01kd6gqx5k7tvzs86y40w8etmr
    position:
      x: 0
      'y': 200
    edges:
      EDGE01kd6gr3vjxm2rs0k8s3fjq4nm:
        id: EDGE01kd6gr3vjxm2rs0k8s3fjq4nm
        sourceActorId: ACTR01kd6gqx5k7tvzs86y40w8etmr
        sourcePortId: SPRT5d5gj2s
        targetActorId: ACTR01kd6gr3vjxm2rs0k8s3fjq4nl
        targetPortId: TPRTdefault
        label: Create
        type: borgiqEdge
      EDGE01kd6gr8m6q9nzp2w4j7h5k6lp:
        id: EDGE01kd6gr8m6q9nzp2w4j7h5k6lp
        sourceActorId: ACTR01kd6gqx5k7tvzs86y40w8etmr
        sourcePortId: SPRTg5vsvui
        targetActorId: ACTR01kd6gr8m6q9nzp2w4j7h5k6lo
        targetPortId: TPRTdefault
        label: Update
        type: borgiqEdge

  # 3a. Create Response - responds to create actions
  ACTR01kd6gr3vjxm2rs0k8s3fjq4nl:
    type: WebhookResponseActor
    version: 1
    name: Create Response
    msgVar: create_response
    description: Returns response for create action
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        statusCode: 201
        body:
          success: true
          message: Resource created successfully
          data: ${{ msg.webhook_trigger.body }}
        headers:
          content-type: application/json
    schemas: {}
    id: ACTR01kd6gr3vjxm2rs0k8s3fjq4nl
    position:
      x: -300
      'y': 400
    edges: {}

  # 3b. Update Response - responds to update actions
  ACTR01kd6gr8m6q9nzp2w4j7h5k6lo:
    type: WebhookResponseActor
    version: 1
    name: Update Response
    msgVar: update_response
    description: Returns response for update action
    isActive: true
    continueOnError: false
    enableLTM: false
    enableSTM: false
    sourcePorts:
      - id: SPRTdefault
    configuration:
      options:
        statusCode: 200
        body:
          success: true
          message: Resource updated successfully
          data: ${{ msg.webhook_trigger.body }}
        headers:
          content-type: application/json
    schemas: {}
    id: ACTR01kd6gr8m6q9nzp2w4j7h5k6lo
    position:
      x: 300
      'y': 400
    edges: {}
```

## Key Points

1. **respondImmediately: false** - The WebhookTriggerActor waits for a WebhookResponseActor to send the response
2. **Multiple source ports** - RouterActor uses custom source ports (`SPRT5d5gj2s`, `SPRTg5vsvui`) for conditional routing
3. **Edge labels** - Labels like "Create" and "Update" match the router condition names for clarity
4. **Terminal actors** - WebhookResponseActor has `edges: {}` since it's the end of the workflow path

## Advanced Example

For a more complex example demonstrating callback tokens, sub-flows, data storage, LTM, and async event handling, see [email-reply-workflow-example.md](email-reply-workflow-example.md). This example shows:

- **Callback token pattern** for human-in-the-loop workflows (issueCallbackToken, waitForCallbackToken, notifyCallbackToken)
- **CallFlowActor and CallableResponseActor** for sub-flow invocation with multiple response points
- **CollectionActor** for cross-flow state management (storing tokens by thread ID)
- **DenoActor with LTM** for incremental Gmail polling across flowruns
- **Error handling with continueOnError** for graceful timeout handling
- **Multiple RouterActors** for complex branching logic
